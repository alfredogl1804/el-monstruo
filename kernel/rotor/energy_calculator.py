"""
Energy Calculator — convierte actividad humana + hilos Manus en energy_units.

Sprint: ROTOR-001 (T3) — pieza diferencial Reloj Suizo
DSC enforzado: DSC-MO-010 (Reloj Suizo), DSC-G-017 (DSC-as-Contract)
Owner: Hilo Ejecutor 2 (manus_hilo_b)
Fecha: 2026-05-12

Defaults firmados por Alfredo T1 el 2026-05-11 (spec §3 Tarea T3 tabla):

    | Source                              | Energy units (USD-equivalent) |
    |-------------------------------------|-------------------------------|
    | github_commit (cualquiera)          | $0.05                         |
    | github_commit mergeado a main       | bonus +$0.10 (= $0.15 total)  |
    | supabase_query MCP de Cowork        | $0.02                         |
    | telegram_message chat autorizado    | $0.05                         |
    | cowork_session > 2h                 | $0.50                         |
    | manus_session con PR mergeado       | $0.30                         |
    | embrion_latido exitoso              | $0.01                         |
    | embrion_latido aborted              | -$0.05 (penalización)         |

    Cap diario por source: $5 (anti-farming) — firmado T1.
    Cap superior recharge: $30/día (2× daily cap original) — firmado T1.

Esta función es PURA: no toca DB, no llama red, no tiene side effects.
Es testeable con ≥20 casos sin fixtures externas.

DSC-G-008 v2 anti-Goodhart: defaults son numéricos, no producidos por LLM.
La validación humana magna (record_validation post-deploy 7d) puede ajustar
los defaults via PR retroactivo si la calibración resulta incorrecta.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping, Optional

# ---------------------------------------------------------------------------
# Versionado del calculador (se persiste en rotor_activity_log.energy_calculator_version)
# ---------------------------------------------------------------------------
ENERGY_CALCULATOR_VERSION = "1.0.0-defaults-T1-2026-05-11"


# ---------------------------------------------------------------------------
# Sources canónicos (deben coincidir con CHECK constraint de migración 0023)
# ---------------------------------------------------------------------------
class RotorSource(str, Enum):
    GITHUB_COMMIT = "github_commit"
    SUPABASE_QUERY = "supabase_query"
    TELEGRAM_MESSAGE = "telegram_message"
    COWORK_SESSION = "cowork_session"
    MANUS_SESSION = "manus_session"
    EMBRION_LATIDO = "embrion_latido"


VALID_SOURCES: frozenset[str] = frozenset(s.value for s in RotorSource)


# ---------------------------------------------------------------------------
# Defaults firmados T1 — NO MODIFICAR sin firma humana magna
# ---------------------------------------------------------------------------
DEFAULTS_T1_SIGNED: Mapping[str, Decimal] = {
    "github_commit_base": Decimal("0.05"),
    "github_commit_merged_main_bonus": Decimal("0.10"),
    "supabase_query_base": Decimal("0.02"),
    "telegram_message_base": Decimal("0.05"),
    "cowork_session_base": Decimal("0.50"),
    "manus_session_base": Decimal("0.30"),
    "embrion_latido_success": Decimal("0.01"),
    "embrion_latido_aborted_penalty": Decimal("-0.05"),
}

# Caps anti-farming (firmados T1)
CAP_DIARIO_POR_SOURCE_USD: Decimal = Decimal("5.00")
CAP_SUPERIOR_RECHARGE_USD: Decimal = Decimal("30.00")

# Pre-condiciones por source
COWORK_SESSION_MIN_DURATION_SECONDS: int = 2 * 3600  # 2 horas firmadas


# ---------------------------------------------------------------------------
# Dataclass: actividad capturada
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RotorActivity:
    """
    Representa una actividad capturada por un capturer del Rotor.

    Campos canónicos coinciden con columnas de rotor_activity_log:
      - source: uno de los 6 canónicos
      - actor: quién generó la actividad (alfredo, cowork, manus_hilo_X, embrion)
      - payload: dict arbitrario con metadatos (estructura por source documentada
                 en migración 0023 nota operativa #2)
    """

    source: str
    actor: str
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.source not in VALID_SOURCES:
            raise ValueError(
                f"RotorActivity.source invalido: {self.source!r}. "
                f"Validos: {sorted(VALID_SOURCES)}"
            )
        if not isinstance(self.actor, str) or not self.actor.strip():
            raise ValueError("RotorActivity.actor debe ser un string no vacio")


# ---------------------------------------------------------------------------
# Función principal — PURA, sin side effects
# ---------------------------------------------------------------------------
def compute_energy_units(activity: RotorActivity) -> Decimal:
    """
    Calcula energy_units (USD-equivalent) para una actividad capturada.

    Determinística: misma actividad → mismo resultado. Sin acceso a red ni DB.

    Returns:
        Decimal con 4 decimales de precisión (coincide con NUMERIC(8,4) de la
        columna energy_units en rotor_activity_log).

    Raises:
        ValueError: si source no es válido (ya validado en RotorActivity.__post_init__).
    """
    source = activity.source
    payload = activity.payload

    if source == RotorSource.GITHUB_COMMIT.value:
        base = DEFAULTS_T1_SIGNED["github_commit_base"]
        # Bonus si el commit fue mergeado a main (recompensa cierre — spec T3)
        if bool(payload.get("merged_to_main", False)):
            base += DEFAULTS_T1_SIGNED["github_commit_merged_main_bonus"]
        return _quantize(base)

    if source == RotorSource.SUPABASE_QUERY.value:
        # Solo queries no-triviales suman energía. Triviales = SELECT 1, health checks, etc.
        if bool(payload.get("trivial", False)):
            return _quantize(Decimal("0"))
        return _quantize(DEFAULTS_T1_SIGNED["supabase_query_base"])

    if source == RotorSource.TELEGRAM_MESSAGE.value:
        # Solo mensajes de chat autorizado suman (atención humana es magna)
        if not bool(payload.get("authorized", True)):
            return _quantize(Decimal("0"))
        return _quantize(DEFAULTS_T1_SIGNED["telegram_message_base"])

    if source == RotorSource.COWORK_SESSION.value:
        # Solo sesiones >2h cuentan (sesión productiva real, firmado T1)
        duration_seconds = int(payload.get("duration_seconds", 0))
        if duration_seconds < COWORK_SESSION_MIN_DURATION_SECONDS:
            return _quantize(Decimal("0"))
        return _quantize(DEFAULTS_T1_SIGNED["cowork_session_base"])

    if source == RotorSource.MANUS_SESSION.value:
        # Solo sesiones que cerraron con PR mergeado cuentan
        if not bool(payload.get("pr_merged", False)):
            return _quantize(Decimal("0"))
        return _quantize(DEFAULTS_T1_SIGNED["manus_session_base"])

    if source == RotorSource.EMBRION_LATIDO.value:
        # Latido exitoso recarga lento; aborted penaliza
        status = str(payload.get("status", "")).lower()
        if status == "success":
            return _quantize(DEFAULTS_T1_SIGNED["embrion_latido_success"])
        if status == "aborted":
            return _quantize(DEFAULTS_T1_SIGNED["embrion_latido_aborted_penalty"])
        # Status desconocido → cero energía (no penaliza pero tampoco recarga)
        return _quantize(Decimal("0"))

    # Defensa adicional (no debería ocurrir por validación en RotorActivity)
    raise ValueError(f"compute_energy_units: source no manejado: {source!r}")


# ---------------------------------------------------------------------------
# Cap diario por source — anti-farming
# ---------------------------------------------------------------------------
def apply_daily_source_cap(
    raw_units: Decimal,
    accumulated_today_for_source: Decimal,
) -> Decimal:
    """
    Aplica cap diario por source ($5/día por source firmado T1).

    Si la suma acumulada del día para ese source ya superó el cap, retorna 0.
    Si la nueva actividad cabe parcialmente dentro del cap, retorna lo que cabe.

    Args:
        raw_units: energía calculada por compute_energy_units (puede ser negativa).
        accumulated_today_for_source: suma de energy_units del día para este source.

    Returns:
        Decimal energy_units que efectivamente entran al budget (post-cap).
        Las penalizaciones (negativas) NO son afectadas por el cap.
    """
    # Las penalizaciones (negativos) siempre aplican, no se capean
    if raw_units < Decimal("0"):
        return _quantize(raw_units)

    cap = CAP_DIARIO_POR_SOURCE_USD
    if accumulated_today_for_source >= cap:
        return _quantize(Decimal("0"))

    headroom = cap - accumulated_today_for_source
    if raw_units > headroom:
        return _quantize(headroom)

    return _quantize(raw_units)


# ---------------------------------------------------------------------------
# Cap superior recharge — máximo $30/día agregado al budget
# ---------------------------------------------------------------------------
def apply_total_recharge_cap(
    pending_units: Decimal,
    already_recharged_today: Decimal,
) -> tuple[Decimal, Decimal]:
    """
    Aplica cap superior de recharge ($30/día firmado T1).

    Si Rotor genera más de $30 en un día, $30 entran al budget y el excedente
    se registra como "energía perdida — capacidad excedida" para análisis post-hoc.

    Returns:
        (units_to_recharge, units_lost_capacity_exceeded)
    """
    cap = CAP_SUPERIOR_RECHARGE_USD

    if already_recharged_today >= cap:
        # Ya está al máximo — toda la energía pendiente se pierde
        return (_quantize(Decimal("0")), _quantize(pending_units))

    headroom = cap - already_recharged_today
    if pending_units <= headroom:
        return (_quantize(pending_units), _quantize(Decimal("0")))

    units_to_recharge = headroom
    units_lost = pending_units - headroom
    return (_quantize(units_to_recharge), _quantize(units_lost))


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------
def _quantize(value: Decimal) -> Decimal:
    """Redondea a 4 decimales (precisión de NUMERIC(8,4))."""
    return value.quantize(Decimal("0.0001"))


# ---------------------------------------------------------------------------
# Inspección — útil para diagnostics y dashboard
# ---------------------------------------------------------------------------
def get_signed_defaults() -> Mapping[str, str]:
    """Retorna los defaults firmados T1 como string (serializable a JSON)."""
    return {k: str(v) for k, v in DEFAULTS_T1_SIGNED.items()}


def get_calculator_metadata() -> Mapping[str, Any]:
    """Metadata canónica del calculador (para reportes y dashboard)."""
    return {
        "version": ENERGY_CALCULATOR_VERSION,
        "defaults_signed_T1_2026_05_11": get_signed_defaults(),
        "cap_diario_por_source_usd": str(CAP_DIARIO_POR_SOURCE_USD),
        "cap_superior_recharge_usd": str(CAP_SUPERIOR_RECHARGE_USD),
        "cowork_session_min_duration_seconds": COWORK_SESSION_MIN_DURATION_SECONDS,
        "valid_sources": sorted(VALID_SOURCES),
    }


__all__ = [
    "ENERGY_CALCULATOR_VERSION",
    "RotorSource",
    "VALID_SOURCES",
    "DEFAULTS_T1_SIGNED",
    "CAP_DIARIO_POR_SOURCE_USD",
    "CAP_SUPERIOR_RECHARGE_USD",
    "COWORK_SESSION_MIN_DURATION_SECONDS",
    "RotorActivity",
    "compute_energy_units",
    "apply_daily_source_cap",
    "apply_total_recharge_cap",
    "get_signed_defaults",
    "get_calculator_metadata",
]
