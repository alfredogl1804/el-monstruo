"""
El Monstruo — Composite Risk Calculator v1.0
==============================================
Calcula riesgo compuesto sobre cadenas de acciones en ventana temporal.
Diseñado por el Consejo de 6 Sabios (Ciclo 3, 14 abril 2026).

Fórmula: Densidad multiplicativa (DeepSeek) + correcciones (Claude)
  composite = risk_actual × (1 + min(MAX_DENSITY_FACTOR, similar_count × 0.1))

Principios:
  1. Determinista: mismo input temporal = mismo output
  2. Latencia < 0.5ms (solo aritmética, sin LLM calls)
  3. Memoria bounded (deque con maxlen)
  4. Backward compatible con ActionEnvelope v2.0
  5. Solo escala acciones MEDIUM+ (anti false-positive)

Dependencias: Solo stdlib Python 3.11+ (time, collections, typing)
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any

from core.action_envelope import RiskLevel

# ── Configuration ────────────────────────────────────────────────────

WINDOW_SECONDS: int = 10
MAX_DENSITY_FACTOR: float = 0.5  # Max 5 similar actions = +50%
MAX_WINDOW_SIZE: int = 200  # Prevents memory leak (Claude falla #3)

# Map RiskLevel enum to numeric value for arithmetic
RISK_NUMERIC: dict[str, float] = {
    RiskLevel.L1_SAFE.value: 0.1,
    RiskLevel.L2_CAUTION.value: 0.5,
    RiskLevel.L3_SENSITIVE.value: 0.9,
}

# Threshold for "similar" actions to count toward density
# Only L2_CAUTION and above count (anti false-positive per Claude)
DENSITY_THRESHOLD: float = 0.5  # L2_CAUTION


# ── Composite Risk Calculator ────────────────────────────────────────


class CompositeRiskCalculator:
    """Calcula riesgo compuesto sobre cadenas de acciones en ventana temporal.

    Thread-safety: Not needed — LangGraph processes actions sequentially.
    Memory: Bounded by MAX_WINDOW_SIZE per session.
    Latency: < 0.5ms (2 loops: window cleanup + density count).

    Usage:
        calculator = CompositeRiskCalculator()
        result = calculator.calculate(session_id, action_type, resource_kind, risk_level)
        # result = {"composite_risk": "L2_CAUTION", "composite_value": 0.55,
        #           "density_count": 1, "pattern": None}
    """

    def __init__(self) -> None:
        # session_id -> deque[(timestamp, action_type_str, resource_kind_str, risk_level_str)]
        self._history: dict[str, deque] = {}

    def calculate(
        self,
        session_id: str,
        action_type: str,
        resource_kind: str,
        risk_level: str,
    ) -> dict[str, Any]:
        """Calculate composite risk for an action in context of its chain.

        Args:
            session_id: Session identifier (same session = same chain)
            action_type: ActionType value (READ, WRITE, DELETE, EXECUTE)
            resource_kind: ResourceKind value (FILE, DB, API, TOOL, etc.)
            risk_level: RiskLevel value (L1_SAFE, L2_CAUTION, L3_SENSITIVE)

        Returns:
            Dict with:
              - composite_risk: str (RiskLevel value)
              - composite_value: float (0.0 - 1.0)
              - density_count: int (similar actions in window)
              - pattern: str | None (reserved for Sprint 2)
        """
        now = time.time()

        # Initialize history with absolute limit (Claude falla #3)
        if session_id not in self._history:
            self._history[session_id] = deque(maxlen=MAX_WINDOW_SIZE)

        window = self._history[session_id]

        # Clean actions outside temporal window
        while window and now - window[0][0] > WINDOW_SECONDS:
            window.popleft()

        # Current action risk as numeric value
        current_risk_val = RISK_NUMERIC.get(risk_level, 0.1)

        # Count similar actions with risk >= DENSITY_THRESHOLD (Claude falla #2)
        similar_count = 0
        for _, a_type, r_kind, r_level in window:
            if (
                a_type == action_type
                and r_kind == resource_kind
                and RISK_NUMERIC.get(r_level, 0.0) >= DENSITY_THRESHOLD
            ):
                similar_count += 1

        # Formula: density multiplicative (DeepSeek)
        density_factor = min(MAX_DENSITY_FACTOR, similar_count * 0.1)
        composite_value = min(1.0, current_risk_val * (1 + density_factor))

        # Dominant risk rule (Grok attack #7):
        # If current action is L3_SENSITIVE, composite stays at max
        if risk_level == RiskLevel.L3_SENSITIVE.value:
            composite_value = max(composite_value, 0.9)

        # Record action in history
        window.append((now, action_type, resource_kind, risk_level))

        # Convert value back to RiskLevel
        composite_risk = self._value_to_level(composite_value)

        return {
            "composite_risk": composite_risk,
            "composite_value": round(composite_value, 3),
            "density_count": similar_count,
            "pattern": None,  # Sprint 2: pattern matching
        }

    def cleanup_session(self, session_id: str) -> None:
        """Clean up history for a terminated session."""
        self._history.pop(session_id, None)

    def get_window_size(self, session_id: str) -> int:
        """Get current window size for a session (for observability)."""
        return len(self._history.get(session_id, []))

    @staticmethod
    def _value_to_level(value: float) -> str:
        """Convert numeric composite value to RiskLevel string."""
        if value >= 0.7:
            return RiskLevel.L3_SENSITIVE.value
        if value >= 0.3:
            return RiskLevel.L2_CAUTION.value
        return RiskLevel.L1_SAFE.value


# ── Module-level singleton ───────────────────────────────────────────
# One calculator per kernel process. Shared across all requests.
_calculator: CompositeRiskCalculator | None = None


def get_composite_calculator() -> CompositeRiskCalculator:
    """Get or create the module-level CompositeRiskCalculator singleton."""
    global _calculator
    if _calculator is None:
        _calculator = CompositeRiskCalculator()
    return _calculator
