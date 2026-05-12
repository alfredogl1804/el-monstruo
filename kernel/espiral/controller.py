"""kernel.espiral.controller — Proportional controller para feedback negativo.

v1: Sólo P (proportional). v2 candidato: PID completo (DSC-MO-015 candidato).

DSC-G-008 v2 anti-Goodhart: lógica pura Python, cero LLM. Determinístico.
DSC-G-008 v3: lazos canonizados firmados T1 en kernel.espiral.config (este módulo).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# ─── Lazos canonizados firmados T1 (spec §2 lazos) ─────────────────────────
# threshold_correction: ±30% deviation antes de corregir
THRESHOLD_CORRECTION_DEVIATION: float = 0.30

# threshold_return: ±10% deviation sostenida para volver a canonical
THRESHOLD_RETURN_DEVIATION: float = 0.10

# max_correction_factor: no aumentar interval >2x ni reducirlo a <0.5x
MAX_CORRECTION_FACTOR_UP: float = 2.0
MAX_CORRECTION_FACTOR_DOWN: float = 0.5

# sensitivity default — controla agresividad de la corrección (0.0=inerte, 1.0=agresivo)
DEFAULT_SENSITIVITY: float = 0.5


class CorrectionAction(str, Enum):
    """Acciones posibles del controlador."""

    SPIKE_DAMPENING = "spike_dampening"
    UNDERSHOOT_ACCELERATION = "undershoot_acceleration"
    RETURN_TO_CANONICAL = "return_to_canonical"
    NONE = "none"  # estado base, deviation < threshold_correction y > threshold_return


@dataclass(frozen=True)
class ControllerDecision:
    """Decisión del controlador a partir de una deviation observada."""

    action: CorrectionAction
    new_pulse_interval_seconds: int
    canonical_pulse_interval_seconds: int
    correction_factor: float  # ratio aplicado al canonical
    rationale: str


class ProportionalController:
    """Controlador proportional-only (v1).

    Lógica:
    - deviation_ratio > 1 + threshold_correction → spike_dampening (aumenta interval)
    - deviation_ratio < 1 - threshold_correction → undershoot_acceleration (reduce interval)
    - |deviation_ratio - 1| < threshold_return → return_to_canonical
    - else → NONE (estado neutral, no acción)

    sensitivity controla cuánto se desvía del canonical (factor lineal).
    """

    def __init__(self, sensitivity: float = DEFAULT_SENSITIVITY):
        if not (0.0 <= sensitivity <= 1.0):
            raise ValueError(f"sensitivity must be in [0.0, 1.0], got {sensitivity}")
        self.sensitivity = sensitivity

    def decide(
        self,
        deviation_ratio: float,
        canonical_interval_seconds: int,
        currently_overridden: bool,
    ) -> ControllerDecision:
        """Decide qué acción tomar dado deviation observada.

        Args:
            deviation_ratio: observed_rate / baseline_rate (1.0 = on target).
            canonical_interval_seconds: el canonical original del consumer.
            currently_overridden: True si el consumer ya tiene un override activo.

        Returns:
            ControllerDecision con action + new_interval (clampeado).
        """
        # Caso: deviation_ratio == 0 (sensor fail-soft o sin actividad observada)
        # No corregir; tampoco retornar agresivamente. Mantener canonical neutral.
        if deviation_ratio <= 0:
            return ControllerDecision(
                action=CorrectionAction.NONE,
                new_pulse_interval_seconds=canonical_interval_seconds,
                canonical_pulse_interval_seconds=canonical_interval_seconds,
                correction_factor=1.0,
                rationale="deviation_ratio<=0 (no observación o fail-soft) — mantener canonical sin override",
            )

        deviation_from_target = deviation_ratio - 1.0  # >0 spike, <0 undershoot
        abs_deviation = abs(deviation_from_target)

        # Caso: deviation pequeña y consumer ya overrideado → return to canonical
        if currently_overridden and abs_deviation < THRESHOLD_RETURN_DEVIATION:
            return ControllerDecision(
                action=CorrectionAction.RETURN_TO_CANONICAL,
                new_pulse_interval_seconds=canonical_interval_seconds,
                canonical_pulse_interval_seconds=canonical_interval_seconds,
                correction_factor=1.0,
                rationale=(
                    f"abs_deviation={abs_deviation:.3f} < return_threshold={THRESHOLD_RETURN_DEVIATION} "
                    "y consumer overrideado — restaurar canonical"
                ),
            )

        # Caso: deviation chica y NO overrideado → no acción
        if abs_deviation < THRESHOLD_CORRECTION_DEVIATION:
            return ControllerDecision(
                action=CorrectionAction.NONE,
                new_pulse_interval_seconds=canonical_interval_seconds,
                canonical_pulse_interval_seconds=canonical_interval_seconds,
                correction_factor=1.0,
                rationale=(
                    f"abs_deviation={abs_deviation:.3f} < correction_threshold={THRESHOLD_CORRECTION_DEVIATION} "
                    "— estado base, no corregir"
                ),
            )

        # Aplicar corrección proportional con sensitivity y clamp
        # Si spike (deviation_ratio > 1): aumentar interval (deviation_ratio veces, atenuado por sensitivity)
        # Si undershoot (deviation_ratio < 1): reducir interval (1/deviation_ratio veces, atenuado)
        if deviation_from_target > 0:
            # Spike: factor = 1 + sensitivity * deviation_from_target
            raw_factor = 1.0 + self.sensitivity * deviation_from_target
            clamped_factor = min(raw_factor, MAX_CORRECTION_FACTOR_UP)
            new_interval = max(1, int(round(canonical_interval_seconds * clamped_factor)))
            return ControllerDecision(
                action=CorrectionAction.SPIKE_DAMPENING,
                new_pulse_interval_seconds=new_interval,
                canonical_pulse_interval_seconds=canonical_interval_seconds,
                correction_factor=clamped_factor,
                rationale=(
                    f"spike deviation_ratio={deviation_ratio:.3f} → factor={clamped_factor:.3f} "
                    f"(raw={raw_factor:.3f}, capped@{MAX_CORRECTION_FACTOR_UP})"
                ),
            )

        # Undershoot
        # factor = 1 - sensitivity * abs_deviation, clamped to MAX_CORRECTION_FACTOR_DOWN
        raw_factor = 1.0 - self.sensitivity * abs_deviation
        clamped_factor = max(raw_factor, MAX_CORRECTION_FACTOR_DOWN)
        new_interval = max(1, int(round(canonical_interval_seconds * clamped_factor)))
        return ControllerDecision(
            action=CorrectionAction.UNDERSHOOT_ACCELERATION,
            new_pulse_interval_seconds=new_interval,
            canonical_pulse_interval_seconds=canonical_interval_seconds,
            correction_factor=clamped_factor,
            rationale=(
                f"undershoot deviation_ratio={deviation_ratio:.3f} → factor={clamped_factor:.3f} "
                f"(raw={raw_factor:.3f}, capped@{MAX_CORRECTION_FACTOR_DOWN})"
            ),
        )
