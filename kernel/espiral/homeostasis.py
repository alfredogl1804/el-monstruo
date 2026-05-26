"""kernel.espiral.homeostasis — Hairspring class (Pieza #5 Reloj Suizo).

Sprint ESPIRAL-001 T2 — clase principal del feedback loop dinámico.

API canónica spec firmado T1:
    Hairspring(consumer, canonical_interval, sensitivity=0.5)
        .sense_deviation(window_minutes=15) → SensorReading
        .apply_correction(reading) → int (nuevo pulse_interval aplicado)
        .return_to_canonical() → None

DSC enforzado: DSC-MO-006 v1.1, DSC-MO-010, DSC-G-008 v3, DSC-S-006 v1.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

import structlog

from kernel.escape.config import get_pulse_interval_seconds, is_registered_consumer
from kernel.espiral.controller import (
    DEFAULT_SENSITIVITY,
    THRESHOLD_CORRECTION_DEVIATION,
    THRESHOLD_RETURN_DEVIATION,
    CorrectionAction,
    ProportionalController,
)
from kernel.espiral.sensor import DBQueryFn, PulseRateSensor, SensorReading

logger = structlog.get_logger("espiral.homeostasis")


# Tipo del logger function — inyectable para tests sin DB.
# Recibe (consumer, reading, decision) y persiste en embrion_homeostasis_log.
HomeostasisLoggerFn = Callable[[str, SensorReading, "AppliedCorrection"], Awaitable[None]]

# Tipo del registry override applier — inyectable.
# Recibe (consumer, new_interval_seconds, ttl_seconds) y aplica el override en el Escape registry.
RegistryOverrideFn = Callable[[str, int, int], Awaitable[None]]

# Tipo del registry restore — restaura el canonical de un consumer.
RegistryRestoreFn = Callable[[str], Awaitable[None]]

# TTL default del override aplicado por la Espiral (segundos)
# 30 min: ventana de estabilización razonable, evita oscillation con re-correcciones rápidas
DEFAULT_OVERRIDE_TTL_SECONDS: int = 30 * 60


@dataclass(frozen=True)
class AppliedCorrection:
    """Resultado de apply_correction."""

    action: CorrectionAction
    new_pulse_interval_seconds: int
    canonical_pulse_interval_seconds: int
    deviation_ratio: float
    rationale: str
    persisted: bool  # True si se logueó en embrion_homeostasis_log


class Hairspring:
    """Pieza Espiral del Reloj Suizo.

    Detecta deviation del pulse_rate observado vs baseline en ventana móvil
    y aplica feedback negativo dinámico sobre el Escape:
    - spike (deviation_ratio > 1.30) → dampening (aumenta interval)
    - undershoot (deviation_ratio < 0.70) → acceleration (reduce interval)
    - estable (|deviation - 1| < 0.10) → return_to_canonical

    Inyecta dependencias para tests sin DB ni red:
    - db_query_fn: cuenta pulses de escape_pulse_log
    - homeostasis_logger_fn: persiste correcciones en embrion_homeostasis_log
    - registry_override_fn: aplica override temporal al Escape
    - registry_restore_fn: restaura canonical del Escape
    """

    def __init__(
        self,
        consumer: str,
        canonical_interval: Optional[int] = None,
        sensitivity: float = DEFAULT_SENSITIVITY,
        window_minutes: int = 15,
        override_ttl_seconds: int = DEFAULT_OVERRIDE_TTL_SECONDS,
        db_query_fn: Optional[DBQueryFn] = None,
        homeostasis_logger_fn: Optional[HomeostasisLoggerFn] = None,
        registry_override_fn: Optional[RegistryOverrideFn] = None,
        registry_restore_fn: Optional[RegistryRestoreFn] = None,
    ):
        if not consumer or not isinstance(consumer, str):
            raise ValueError("consumer must be non-empty string")
        if window_minutes <= 0:
            raise ValueError(f"window_minutes must be positive, got {window_minutes}")
        if override_ttl_seconds <= 0:
            raise ValueError(f"override_ttl_seconds must be positive, got {override_ttl_seconds}")

        self.consumer = consumer
        # Si no se pasa canonical, lo deriva del registry canónico del Escape
        self.canonical_interval = (
            canonical_interval if canonical_interval is not None else get_pulse_interval_seconds(consumer)
        )
        self.window_minutes = window_minutes
        self.override_ttl_seconds = override_ttl_seconds

        self._sensor = PulseRateSensor(
            consumer=consumer,
            window_minutes=window_minutes,
            db_query_fn=db_query_fn,
        )
        self._controller = ProportionalController(sensitivity=sensitivity)
        self._homeostasis_logger_fn = homeostasis_logger_fn
        self._registry_override_fn = registry_override_fn
        self._registry_restore_fn = registry_restore_fn

        # Estado in-memory: ¿este Hairspring tiene actualmente override activo?
        # Se resetea al reiniciar el proceso (degradación segura).
        self._currently_overridden: bool = False

        # Doctrina honesta: si consumer no está en REGISTRY canónico, log warning
        if not is_registered_consumer(consumer):
            logger.warning(
                "hairspring_consumer_not_in_canonical_registry",
                consumer=consumer,
                canonical_interval=self.canonical_interval,
            )

    async def sense_deviation(
        self,
        window_minutes: Optional[int] = None,
    ) -> SensorReading:
        """Lee pulse_rate observed vs baseline en ventana móvil.

        Permite override del window_minutes para análisis ad-hoc.
        """
        if window_minutes is not None and window_minutes != self.window_minutes:
            # Crea sensor temporal con ventana custom (no muta el sensor base)
            tmp_sensor = PulseRateSensor(
                consumer=self.consumer,
                window_minutes=window_minutes,
                db_query_fn=self._sensor._db_query_fn,
            )
            return await tmp_sensor.sense()
        return await self._sensor.sense()

    async def apply_correction(self, sense_result: SensorReading) -> AppliedCorrection:
        """Aplica corrección al Escape registry según deviation observada.

        Si la decisión es NONE, no hace nada (no log, no override).
        Si es RETURN_TO_CANONICAL, restaura canonical en Escape.
        Si es SPIKE_DAMPENING o UNDERSHOOT_ACCELERATION, aplica override.
        Siempre intenta loguear en embrion_homeostasis_log si hay action != NONE.
        """
        decision = self._controller.decide(
            deviation_ratio=sense_result.deviation_ratio,
            canonical_interval_seconds=self.canonical_interval,
            currently_overridden=self._currently_overridden,
        )

        action = decision.action
        applied = AppliedCorrection(
            action=action,
            new_pulse_interval_seconds=decision.new_pulse_interval_seconds,
            canonical_pulse_interval_seconds=decision.canonical_pulse_interval_seconds,
            deviation_ratio=sense_result.deviation_ratio,
            rationale=decision.rationale,
            persisted=False,
        )

        # NONE: no hacer nada, no loguear
        if action == CorrectionAction.NONE:
            return applied

        # Aplicar al registry según action
        try:
            if action in (CorrectionAction.SPIKE_DAMPENING, CorrectionAction.UNDERSHOOT_ACCELERATION):
                if self._registry_override_fn is not None:
                    await self._registry_override_fn(
                        self.consumer,
                        decision.new_pulse_interval_seconds,
                        self.override_ttl_seconds,
                    )
                self._currently_overridden = True
            elif action == CorrectionAction.RETURN_TO_CANONICAL:
                if self._registry_restore_fn is not None:
                    await self._registry_restore_fn(self.consumer)
                self._currently_overridden = False
        except Exception as e:  # noqa: BLE001
            # Fail-soft: el registry puede fallar (config corrupto, etc.). Log y seguir.
            logger.warning(
                "hairspring_registry_apply_failed",
                consumer=self.consumer,
                action=action.value,
                error=str(e),
            )

        # Persistir en embrion_homeostasis_log
        persisted = False
        if self._homeostasis_logger_fn is not None:
            try:
                await self._homeostasis_logger_fn(self.consumer, sense_result, applied)
                persisted = True
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    "hairspring_log_persist_failed",
                    consumer=self.consumer,
                    action=action.value,
                    error=str(e),
                )

        # Estructurado log para observabilidad
        logger.info(
            "hairspring_correction_applied",
            consumer=self.consumer,
            action=action.value,
            deviation_ratio=sense_result.deviation_ratio,
            new_interval=decision.new_pulse_interval_seconds,
            canonical_interval=decision.canonical_pulse_interval_seconds,
            persisted=persisted,
            rationale=decision.rationale,
        )

        # Retornar AppliedCorrection con persisted real
        return AppliedCorrection(
            action=action,
            new_pulse_interval_seconds=decision.new_pulse_interval_seconds,
            canonical_pulse_interval_seconds=decision.canonical_pulse_interval_seconds,
            deviation_ratio=sense_result.deviation_ratio,
            rationale=decision.rationale,
            persisted=persisted,
        )

    async def return_to_canonical(self) -> None:
        """Restaura el pulse_interval canonical del consumer en el Escape.

        Útil para hotpaths/forzado externo (e.g., apagado de feature flag).
        """
        if not self._currently_overridden:
            return
        try:
            if self._registry_restore_fn is not None:
                await self._registry_restore_fn(self.consumer)
            self._currently_overridden = False
            logger.info(
                "hairspring_return_to_canonical_forced",
                consumer=self.consumer,
                canonical_interval=self.canonical_interval,
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "hairspring_force_restore_failed",
                consumer=self.consumer,
                error=str(e),
            )

    @property
    def currently_overridden(self) -> bool:
        """True si esta Hairspring tiene un override activo en el registry."""
        return self._currently_overridden


# ─── Constantes públicas (re-export para acceso desde tests/dashboard) ─────
__all__ = [
    "Hairspring",
    "AppliedCorrection",
    "DEFAULT_OVERRIDE_TTL_SECONDS",
    "THRESHOLD_CORRECTION_DEVIATION",
    "THRESHOLD_RETURN_DEVIATION",
]
