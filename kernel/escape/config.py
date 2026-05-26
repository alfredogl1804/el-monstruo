"""kernel.escape.config — Defaults firmados T1 Alfredo 2026-05-12 ~07:55 UTC.

Configuración canónica del Escapement (Throttler Determinístico).

Doctrina Reloj Suizo §2.1 fila 2 — Escape dosifica el consumo del Resorte
(embrion_budget) en pulsos discretos por consumer. Sin Escape, una sola llamada
LLM agresiva puede agotar el budget en minutos. Con Escape, el gasto se
distribuye en pulsos predecibles, haciendo autonomía perpetua viable.

6 consumers canónicos firmados por T1:

| Consumer                | Interval | Justificación operativa                          |
|-------------------------|----------|--------------------------------------------------|
| embrion_loop_latido     | 60s      | 1 ciclo Volante/min (doctrina §3.1)              |
| guardian_daily_audit    | 86400s   | 1 audit/día (sprint GUARDIAN-AUTONOMO-001)       |
| rotor_recharge          | 300s     | Mismo intervalo que recharge_mainspring          |
| self_verifier_call      | 30s      | Max 2 Self-Verifier/min (anti-spam)              |
| embrion_specialization  | 120s     | Especializaciones cada 2min (sprint posterior)   |
| external_llm_call       | 10s      | Llamadas LLM agresivas dosificadas (cap superior)|

Override por env var: ESCAPE_PULSE_INTERVAL_<CONSUMER_UPPER> = <seconds>
Ej: ESCAPE_PULSE_INTERVAL_EMBRION_LOOP_LATIDO=120 (override a 2min)

DSC enforzado:
- DSC-MO-010 (Reloj Suizo §2.1 fila 2)
- DSC-G-008 v2 (anti-Goodhart): blocked_count tracking obligatorio
- DSC-S-006 v1.1 (RLS): escape_pulse_log con service_role only
"""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Final

# ═══════════════════════════════════════════════════════════════════════════════
# Versionado del config (DSC-G-017 DSC-as-Contract)
# ═══════════════════════════════════════════════════════════════════════════════
CONFIG_VERSION: Final[str] = "1.0.0"
SIGNED_AT_UTC: Final[str] = "2026-05-12T07:55:00Z"
SIGNED_BY: Final[str] = "Alfredo T1 (Gate (a) spec ESCAPE-001 FIRME)"
SPEC_COMMIT: Final[str] = "ff8716f"  # commit con firma T1

# ═══════════════════════════════════════════════════════════════════════════════
# Defaults canónicos firmados — 6 consumers
# ═══════════════════════════════════════════════════════════════════════════════
DEFAULT_PULSE_INTERVALS_SECONDS: Final[dict[str, int]] = {
    "embrion_loop_latido": 60,
    "guardian_daily_audit": 86400,
    "rotor_recharge": 300,
    "self_verifier_call": 30,
    "embrion_specialization": 120,
    "external_llm_call": 10,
}

# Registry canónico — única fuente de verdad de consumers válidos
REGISTRY_CONSUMERS: Final[frozenset[str]] = frozenset(DEFAULT_PULSE_INTERVALS_SECONDS.keys())

# Default energy_consumed por pulso — doctrina §4 paso 2
DEFAULT_ENERGY_CONSUMED_PER_PULSE: Final[Decimal] = Decimal("1.000000")

# Cap superior absoluto: ningún consumer puede tener intervalo < 1s (anti-spam)
MIN_PULSE_INTERVAL_SECONDS: Final[int] = 1
# Cap superior absoluto: ningún consumer puede tener intervalo > 7 días (anti-stale)
MAX_PULSE_INTERVAL_SECONDS: Final[int] = 7 * 86400


# ═══════════════════════════════════════════════════════════════════════════════
# Resolución por consumer (con override env var opcional)
# ═══════════════════════════════════════════════════════════════════════════════
def get_pulse_interval_seconds(consumer: str) -> int:
    """Retorna pulse_interval_seconds para <consumer>.

    Resolución en orden:
    1. Env var `ESCAPE_PULSE_INTERVAL_<CONSUMER_UPPER>` si está seteada y es int válido
    2. DEFAULT_PULSE_INTERVALS_SECONDS[<consumer>] si está en REGISTRY_CONSUMERS
    3. 60 (fallback genérico — log warning)

    Aplica clamping a [MIN_PULSE_INTERVAL_SECONDS, MAX_PULSE_INTERVAL_SECONDS].

    Args:
        consumer: nombre canónico del consumer (case-sensitive).

    Returns:
        int — segundos del intervalo entre pulsos.
    """
    env_key = f"ESCAPE_PULSE_INTERVAL_{consumer.upper()}"
    env_value = os.environ.get(env_key)
    if env_value is not None:
        try:
            parsed = int(env_value)
            return max(MIN_PULSE_INTERVAL_SECONDS, min(MAX_PULSE_INTERVAL_SECONDS, parsed))
        except (ValueError, TypeError):
            pass  # Fall through al default

    if consumer in DEFAULT_PULSE_INTERVALS_SECONDS:
        return DEFAULT_PULSE_INTERVALS_SECONDS[consumer]

    # Consumer desconocido — usa 60s genérico
    return 60


def is_registered_consumer(consumer: str) -> bool:
    """Retorna True si <consumer> está en REGISTRY_CONSUMERS canónico.

    Útil para validar a nivel app antes de insertar en escape_pulse_log
    (la tabla no tiene CHECK constraint a propósito; ver migration 0024).
    """
    return consumer in REGISTRY_CONSUMERS


def list_registered_consumers() -> tuple[str, ...]:
    """Lista ordenada (estable) de los 6 consumers canónicos."""
    return tuple(sorted(REGISTRY_CONSUMERS))


# ═══════════════════════════════════════════════════════════════════════════════
# Self-introspection (útil para dashboards y testing)
# ═══════════════════════════════════════════════════════════════════════════════
def snapshot() -> dict:
    """Retorna snapshot del config actual (con overrides env aplicados)."""
    return {
        "config_version": CONFIG_VERSION,
        "signed_at_utc": SIGNED_AT_UTC,
        "signed_by": SIGNED_BY,
        "spec_commit": SPEC_COMMIT,
        "registry_consumers": list_registered_consumers(),
        "effective_intervals_seconds": {c: get_pulse_interval_seconds(c) for c in list_registered_consumers()},
        "default_energy_per_pulse": str(DEFAULT_ENERGY_CONSUMED_PER_PULSE),
        "bounds_seconds": {
            "min": MIN_PULSE_INTERVAL_SECONDS,
            "max": MAX_PULSE_INTERVAL_SECONDS,
        },
    }
