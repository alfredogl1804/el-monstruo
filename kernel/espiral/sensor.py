"""kernel.espiral.sensor — Observador de pulse_rate en ventana móvil.

Lee `escape_pulse_log` (Pieza #2 del Reloj Suizo) y calcula el pulse_rate
observado por consumer en una ventana temporal móvil. Calcula también el
baseline canónico esperado a partir de `kernel.escape.config`.

Sin DB ni red en tests: el sensor es inyectable con un `db_query_fn` callable
que retorna lista de pulses. En producción se inyecta una función real que
consulta Supabase REST. En tests se mockea.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

from kernel.escape.config import get_pulse_interval_seconds


@dataclass(frozen=True)
class SensorReading:
    """Lectura instantánea del PulseRateSensor."""

    consumer: str
    window_minutes: int
    pulses_observed: int
    pulse_rate_observed: float  # pulses/min
    pulse_rate_baseline: float  # pulses/min según canonical_interval
    deviation_ratio: float  # observed/baseline (1.0 = on target)


# Tipo del query function — inyectable.
# Recibe (consumer, window_minutes) y retorna count de pulses observados.
DBQueryFn = Callable[[str, int], Awaitable[int]]


class PulseRateSensor:
    """Sensor del pulse_rate en ventana móvil para un consumer.

    DSC-G-008 v3 anti-Goodhart: el baseline NO se deriva del histórico (eso
    crearía un bucle Goodhart donde el target se ajusta a sí mismo). El
    baseline se deriva del canonical_interval firmado T1 en kernel.escape.config.
    """

    def __init__(
        self,
        consumer: str,
        window_minutes: int = 15,
        db_query_fn: Optional[DBQueryFn] = None,
    ):
        if window_minutes <= 0:
            raise ValueError(f"window_minutes must be positive, got {window_minutes}")
        self.consumer = consumer
        self.window_minutes = window_minutes
        self._db_query_fn = db_query_fn

    @property
    def baseline_rate_per_minute(self) -> float:
        """pulse_rate_baseline = 60 / canonical_interval_seconds.

        Ej: consumer con canonical_interval=60s → baseline = 1.0 pulses/min
        Ej: consumer con canonical_interval=300s → baseline = 0.2 pulses/min
        """
        canonical_interval_s = get_pulse_interval_seconds(self.consumer)
        if canonical_interval_s <= 0:
            return 0.0
        return 60.0 / canonical_interval_s

    async def sense(self) -> SensorReading:
        """Lee pulses en ventana móvil + calcula deviation_ratio.

        Si db_query_fn no está inyectado o falla, retorna lectura con
        pulses_observed=0 y deviation_ratio=0.0 (fail-soft).
        """
        baseline = self.baseline_rate_per_minute
        pulses_observed = 0

        if self._db_query_fn is not None:
            try:
                pulses_observed = await self._db_query_fn(self.consumer, self.window_minutes)
            except Exception:
                # Fail-soft: si la query falla, asumimos 0 pulsos (no provoca correcciones).
                pulses_observed = 0

        if self.window_minutes > 0:
            observed_rate = pulses_observed / self.window_minutes
        else:
            observed_rate = 0.0

        if baseline > 0:
            deviation_ratio = observed_rate / baseline
        else:
            deviation_ratio = 0.0

        return SensorReading(
            consumer=self.consumer,
            window_minutes=self.window_minutes,
            pulses_observed=pulses_observed,
            pulse_rate_observed=observed_rate,
            pulse_rate_baseline=baseline,
            deviation_ratio=deviation_ratio,
        )
