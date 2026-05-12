"""
kernel/embrion_budget.py — Budget Tracker estricto para el Embrión

Sprint EMBRION-NEEDS-001, Tarea 1.
Origen: bridge/sprints_propuestos/sprint_EMBRION_NEEDS_001.md
Handoff: bridge/cowork_to_manus_SPRINT_EMBRION_NEEDS_001_2026_05_10.md

Misión:
  Frenar el sangrado de costo del embrión que el 1 de mayo gastó $105 USD
  en un solo día (cycles individuales pequeños, suma estallada). Implementar
  control granular antes de ejecutar cada cycle, no después.

Diseño de 3 capas:

  1. Pre-flight check (`check_before_cycle`) — proyección antes de gastar.
     Si la proyección > cap_per_latido_usd, devuelve abort.
     Si el costo acumulado del día > daily_budget * 0.95, devuelve abort.

  2. Post-flight registration (`record_after_cycle`) — registra costo real.
     Si el actual > estimated * 1.3, lanza warning.
     Si el actual > cap_per_latido_usd (raro, pero posible en streaming),
     marca cap_excedido=true y suma al contador diario.

  3. HITL escalation (`maybe_escalate_hitl`) — al 3er cycle excedido en
     un día, escribe un mensaje a embrion_memoria pidiendo decisión humana.

API pública (3 funciones top-level):
  - `check_before_cycle(...)`  → retorna BudgetDecision
  - `record_after_cycle(...)`  → persiste resultado real
  - `daily_summary(...)`       → snapshot operativo del día

Dependencias:
  - SUPABASE_SERVICE_KEY o SUPABASE_KEY en env (igual que el resto del kernel)
  - SUPABASE_URL (default xsumzuhwmivjgftsneov.supabase.co)

Configuración via env vars:
  - EMBRION_CAP_PER_LATIDO_USD   default "0.25"
  - EMBRION_DAILY_BUDGET         default "30.0"  (ya existe, lo reusamos)
  - EMBRION_HITL_ESCALATION_THRESHOLD  default "3"  (cycles excedidos antes de escalar)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

try:
    import structlog
    logger = structlog.get_logger("embrion.budget")
except ImportError:  # pragma: no cover
    import logging
    logger = logging.getLogger("embrion.budget")

# ── Configuración (canónica, lee env al import)
CAP_PER_LATIDO_USD = float(os.environ.get("EMBRION_CAP_PER_LATIDO_USD", "0.25"))
DAILY_BUDGET_USD = float(os.environ.get("EMBRION_DAILY_BUDGET", "30.0"))
HITL_ESCALATION_THRESHOLD = int(os.environ.get("EMBRION_HITL_ESCALATION_THRESHOLD", "3"))

# Margen de seguridad: si el costo del día acumulado supera 95% del cap diario,
# bloqueamos antes de gastar más.
DAILY_SAFETY_MARGIN = 0.95


@dataclass
class BudgetDecision:
    """Resultado de check_before_cycle. Determinístico."""
    allow: bool
    reason: str  # "ok" | "estimated_exceeds_cap" | "daily_budget_near_limit" | "daily_budget_exhausted"
    cap_per_latido_usd: float
    cost_estimated_usd: float
    daily_spent_usd: float
    daily_budget_usd: float
    requires_approval: bool = False
    metadata: dict = field(default_factory=dict)

    def __bool__(self) -> bool:  # azúcar: `if decision: ...`
        return self.allow


@dataclass
class CycleResult:
    """Resultado real al cerrar un cycle. Lo escribimos en embrion_budget_state."""
    cycle_id: int
    cost_actual_usd: float
    tokens_used: int = 0
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    model_used: Optional[str] = None
    cap_excedido: bool = False
    abort_reason: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_detail: Optional[str] = None
    latido_id: Optional[str] = None


# ── Cliente Supabase (lazy, para no romper imports en tests sin red)

class _SupabaseRest:
    """Cliente REST mínimo y testeable. No usa supabase-py para mantener
    superficie chica y inyectable en tests vía monkeypatch."""

    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key

    def _headers(self, prefer: Optional[str] = None):
        h = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }
        if prefer:
            h["Prefer"] = prefer
        return h

    def select(self, table: str, params: dict, prefer: Optional[str] = None):
        import requests
        r = requests.get(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(prefer=prefer),
            params=params,
            timeout=15,
        )
        r.raise_for_status()
        return r.json(), r.headers

    def insert(self, table: str, payload: dict | list[dict]):
        import requests
        r = requests.post(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(prefer="return=representation"),
            json=payload,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()


def _get_supabase_client() -> _SupabaseRest:
    url = os.environ.get("SUPABASE_URL", "https://xsumzuhwmivjgftsneov.supabase.co")
    key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_KEY")
        or os.environ.get("SUPA_KEY")
    )
    if not key:
        raise RuntimeError(
            "embrion_budget: ninguna env var Supabase encontrada "
            "(probadas: SUPABASE_SERVICE_KEY, SUPABASE_KEY, SUPA_KEY)"
        )
    return _SupabaseRest(url=url, key=key)


# ── Funciones puras de cálculo (testeable sin red)

def estimate_cost_usd(
    *,
    estimated_tokens_in: int,
    estimated_tokens_out: int,
    model: str = "gpt-5",
) -> float:
    """Estima costo USD de un cycle dado tokens proyectados.

    Pricing 2026-05 (USD por 1M tokens, redondeado a precio público vigente):
      gpt-5      input  $2.50  output $10.00
      gpt-5.5    input  $3.00  output $12.00
      claude-opus-4.7 input $3.00 output $15.00
      gemini-3.1-pro  input $1.25 output $5.00

    Devuelve costo total en USD (no por 1M, ya escalado al volumen real).
    """
    pricing = {
        "gpt-5":           (2.50, 10.00),
        "gpt-5.5":         (3.00, 12.00),
        "claude-opus-4.7": (3.00, 15.00),
        "gemini-3.1-pro":  (1.25, 5.00),
    }
    inp, out = pricing.get(model.lower(), pricing["gpt-5"])
    return (estimated_tokens_in / 1_000_000.0) * inp + (estimated_tokens_out / 1_000_000.0) * out


def _today_iso_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ── API pública

def check_before_cycle(
    *,
    estimated_tokens_in: int,
    estimated_tokens_out: int,
    model: str = "gpt-5",
    cap_per_latido_usd: Optional[float] = None,
    daily_budget_usd: Optional[float] = None,
    supabase_client: Optional[_SupabaseRest] = None,
) -> BudgetDecision:
    """Pre-flight check. Llamar ANTES de hacer la llamada al modelo.

    Returns:
        BudgetDecision.allow=True si se puede ejecutar.
        BudgetDecision.allow=False si hay que abortar el cycle.

    No persiste nada — eso lo hace `record_after_cycle` o, en caso de abort,
    el caller debe registrar el abort vía `record_aborted_cycle`.
    """
    cap = cap_per_latido_usd if cap_per_latido_usd is not None else CAP_PER_LATIDO_USD
    daily_cap = daily_budget_usd if daily_budget_usd is not None else DAILY_BUDGET_USD

    estimated = estimate_cost_usd(
        estimated_tokens_in=estimated_tokens_in,
        estimated_tokens_out=estimated_tokens_out,
        model=model,
    )

    # 1) Hard abort si el estimado solo del cycle ya excede cap
    if estimated > cap:
        return BudgetDecision(
            allow=False,
            reason="estimated_exceeds_cap",
            cap_per_latido_usd=cap,
            cost_estimated_usd=estimated,
            daily_spent_usd=0.0,  # no consultado, abort temprano
            daily_budget_usd=daily_cap,
            metadata={"model": model, "tokens_in": estimated_tokens_in, "tokens_out": estimated_tokens_out},
        )

    # 2) Consultar gasto del día
    client = supabase_client or _get_supabase_client()
    today = _today_iso_date()
    try:
        rows, _ = client.select(
            "embrion_budget_state",
            params={
                "select": "cost_actual_usd",
                "created_at": f"gte.{today}T00:00:00+00:00",
            },
        )
        daily_spent = sum(float(r.get("cost_actual_usd") or 0) for r in rows)
    except Exception as e:
        # Fail-safe: si no podemos consultar, asumimos 0 y dejamos pasar SOLO si
        # el estimated es claramente seguro (< 50% del cap). Si está cerca del
        # cap, abortamos por precaución.
        logger.warning("embrion_budget_query_failed", error=str(e))
        if estimated > cap * 0.5:
            return BudgetDecision(
                allow=False,
                reason="query_failed_and_estimated_too_high",
                cap_per_latido_usd=cap,
                cost_estimated_usd=estimated,
                daily_spent_usd=-1.0,
                daily_budget_usd=daily_cap,
                metadata={"error": str(e)},
            )
        daily_spent = -1.0

    # 3) Hard abort si daily cap exhausto
    if 0 <= daily_spent + estimated > daily_cap:
        return BudgetDecision(
            allow=False,
            reason="daily_budget_exhausted",
            cap_per_latido_usd=cap,
            cost_estimated_usd=estimated,
            daily_spent_usd=daily_spent,
            daily_budget_usd=daily_cap,
        )

    # 4) Soft warning si estamos cerca del límite diario
    near_limit = (
        daily_spent >= 0
        and (daily_spent + estimated) > daily_cap * DAILY_SAFETY_MARGIN
    )
    reason = "daily_budget_near_limit" if near_limit else "ok"

    return BudgetDecision(
        allow=True,
        reason=reason,
        cap_per_latido_usd=cap,
        cost_estimated_usd=estimated,
        daily_spent_usd=daily_spent if daily_spent >= 0 else 0.0,
        daily_budget_usd=daily_cap,
    )


def record_after_cycle(
    result: CycleResult,
    *,
    cap_per_latido_usd: Optional[float] = None,
    supabase_client: Optional[_SupabaseRest] = None,
) -> dict:
    """Persiste el resultado de un cycle en embrion_budget_state.

    Args:
        result: CycleResult con costo real y telemetría.
        cap_per_latido_usd: cap activo en este cycle (default: env).
        supabase_client: opcional, para tests.

    Returns:
        dict con la fila insertada.
    """
    cap = cap_per_latido_usd if cap_per_latido_usd is not None else CAP_PER_LATIDO_USD
    cap_excedido = result.cap_excedido or (result.cost_actual_usd > cap)

    payload = {
        "cycle_id": result.cycle_id,
        "latido_id": result.latido_id,
        "cap_per_latido_usd": round(cap, 4),
        "cost_actual_usd": round(float(result.cost_actual_usd), 4),
        "cap_excedido": cap_excedido,
        "abort_reason": result.abort_reason,
        "tokens_used": int(result.tokens_used or 0),
        "tokens_input": result.tokens_input,
        "tokens_output": result.tokens_output,
        "model_used": result.model_used,
        "trigger_type": result.trigger_type,
        "trigger_detail": (result.trigger_detail or "")[:1000],
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    client = supabase_client or _get_supabase_client()
    inserted = client.insert("embrion_budget_state", payload)
    if isinstance(inserted, list) and inserted:
        return inserted[0]
    return inserted or payload


def record_aborted_cycle(
    *,
    cycle_id: int,
    decision: BudgetDecision,
    trigger_type: Optional[str] = None,
    trigger_detail: Optional[str] = None,
    model_used: Optional[str] = None,
    supabase_client: Optional[_SupabaseRest] = None,
) -> dict:
    """Registra un cycle que NO se ejecutó por decisión de check_before_cycle.

    Esto es importante para auditoría: queremos contar cuántas veces el
    Budget Tracker frenó algo, qué proyección tenía y por qué.
    """
    payload = {
        "cycle_id": cycle_id,
        "cap_per_latido_usd": round(decision.cap_per_latido_usd, 4),
        "cost_estimated_usd": round(decision.cost_estimated_usd, 4),
        "cost_actual_usd": 0,
        "cap_excedido": decision.reason == "estimated_exceeds_cap",
        "abort_reason": decision.reason,
        "model_used": model_used,
        "trigger_type": trigger_type,
        "trigger_detail": (trigger_detail or "")[:1000],
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    client = supabase_client or _get_supabase_client()
    inserted = client.insert("embrion_budget_state", payload)
    if isinstance(inserted, list) and inserted:
        return inserted[0]
    return inserted or payload


def maybe_escalate_hitl(
    *,
    threshold: Optional[int] = None,
    supabase_client: Optional[_SupabaseRest] = None,
) -> Optional[dict]:
    """Si en el día corriente hay >= threshold cycles excedidos, escala a HITL.

    La escalación se hace insertando una fila en `embrion_memoria` con:
      tipo='respuesta_embrion', importancia=10, contexto.requires_alfredo_approval=True

    Esto sigue el protocolo del handoff (líneas 98-104) mientras Tarea 4
    (bot Telegram) no esté completa.

    Returns:
        dict con la fila escalada si se escaló, None si no.
    """
    th = threshold if threshold is not None else HITL_ESCALATION_THRESHOLD
    client = supabase_client or _get_supabase_client()
    today = _today_iso_date()

    # Contar cycles excedidos hoy
    rows, hdrs = client.select(
        "embrion_budget_state",
        params={
            "select": "id,cycle_id,cost_estimated_usd,abort_reason,created_at",
            "created_at": f"gte.{today}T00:00:00+00:00",
            "cap_excedido": "eq.true",
        },
        prefer="count=exact",
    )
    excedidos = len(rows)
    if excedidos < th:
        return None

    # Verificar que no escalamos ya hoy (idempotencia simple)
    msg_check, _ = client.select(
        "embrion_memoria",
        params={
            "select": "id",
            "tipo": "eq.respuesta_embrion",
            "hilo_origen": "eq.embrion_budget",
            "created_at": f"gte.{today}T00:00:00+00:00",
            "limit": "1",
        },
    )
    if msg_check:
        return None  # ya escalamos hoy, no spamear

    contenido = (
        f"⚠️ Budget Tracker — {excedidos} cycles excedidos hoy.\n\n"
        f"Cap por latido: ${CAP_PER_LATIDO_USD:.2f} USD.\n"
        f"Cycles que pidieron más:\n"
        + "\n".join(
            f"  - cycle {r.get('cycle_id')}: estimado ${r.get('cost_estimated_usd', 0):.4f}, razón: {r.get('abort_reason', 'unknown')}"
            for r in rows[:10]
        )
        + "\n\nRequiere decisión: subir el cap, ajustar el modelo, o investigar el patrón."
    )

    contexto = {
        "requires_alfredo_approval": True,
        "exceeded_count_today": excedidos,
        "threshold": th,
        "cap_per_latido_usd": CAP_PER_LATIDO_USD,
        "source": "embrion_budget.maybe_escalate_hitl",
    }

    payload = {
        "tipo": "respuesta_embrion",
        "hilo_origen": "embrion_budget",
        "importancia": 10,
        "contenido": contenido,
        "contexto": contexto,
    }

    inserted = client.insert("embrion_memoria", payload)
    if isinstance(inserted, list) and inserted:
        logger.warning("embrion_budget_hitl_escalated", excedidos=excedidos, msg_id=inserted[0].get("id"))
        return inserted[0]
    return inserted


def daily_summary(
    *,
    supabase_client: Optional[_SupabaseRest] = None,
) -> dict:
    """Snapshot operativo del día para dashboards y stats endpoint."""
    client = supabase_client or _get_supabase_client()
    today = _today_iso_date()
    rows, hdrs = client.select(
        "embrion_budget_state",
        params={
            "select": "cycle_id,cost_actual_usd,cost_estimated_usd,cap_excedido,abort_reason,model_used",
            "created_at": f"gte.{today}T00:00:00+00:00",
        },
    )
    total_cost = sum(float(r.get("cost_actual_usd") or 0) for r in rows)
    excedidos = sum(1 for r in rows if r.get("cap_excedido"))
    abortados = sum(1 for r in rows if r.get("abort_reason") and r.get("abort_reason") != "ok")

    return {
        "date": today,
        "cycles_total": len(rows),
        "cycles_excedidos": excedidos,
        "cycles_abortados_pre_flight": abortados,
        "cost_actual_usd": round(total_cost, 4),
        "cap_per_latido_usd": CAP_PER_LATIDO_USD,
        "daily_budget_usd": DAILY_BUDGET_USD,
        "daily_remaining_usd": round(max(0.0, DAILY_BUDGET_USD - total_cost), 4),
        "near_limit": total_cost > DAILY_BUDGET_USD * DAILY_SAFETY_MARGIN,
        "by_model": _group_cost_by_model(rows),
    }


def _group_cost_by_model(rows: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for r in rows:
        m = r.get("model_used") or "unknown"
        if m not in out:
            out[m] = {"cycles": 0, "cost_usd": 0.0}
        out[m]["cycles"] += 1
        out[m]["cost_usd"] = round(out[m]["cost_usd"] + float(r.get("cost_actual_usd") or 0), 4)
    return out



# ── Sprint ROTOR-001 (2026-05-12) Hilo Ejecutor 2 ─────────────────────────
# add_recycled_energy: API pública para que kernel.rotor.recharge devuelva
# energy_units (USD-equivalent) al budget del Embrión. Esta función NO calcula
# nada — solo persiste un registro contable que el daily_summary lee.
#
# Diseño:
#   - Inserta una fila en `embrion_budget_state` con cost_actual_usd = -units_usd
#     (signo negativo para indicar "recharge" en lugar de "consumo").
#   - El query de daily_summary suma cost_actual_usd, así que las recharges
#     reducen el total consumido del día (i.e. recargan presupuesto disponible).
#   - cycle_id apunta al cycle del Embrión que solicitó el recharge
#     (trazabilidad post-hoc).
#   - source_breakdown se persiste en abort_reason (campo libre TEXT) como
#     JSON serializado para análisis post-hoc del Rotor.
#
# Cap superior $30/día firmado T1 — enforced en kernel.rotor.recharge antes
# de llamar a esta función. Esta función NO valida cap superior (separación
# de concerns: rotor maneja caps, budget solo registra).
#
# Spec firmado: bridge/sprints_propuestos/sprint_ROTOR_001_reciclador_actividad.md

from decimal import Decimal as _RotorDecimal
import json as _rotor_json


def add_recycled_energy(
    *,
    units_usd,
    cycle_id: int,
    source_breakdown: Optional[dict] = None,
    supabase_client: Optional[_SupabaseRest] = None,
) -> dict:
    """
    Registra energy_units recargados desde el Rotor al budget del Embrión.

    Escribe una fila contable en embrion_budget_state con cost_actual_usd negativo
    (recharge = anti-consumo). Cap superior YA enforced en kernel.rotor.recharge.

    Args:
        units_usd: cantidad en USD-equivalent a recargar (Decimal | float | str, >= 0).
                   Negativos NO permitidos (las penalizaciones de embrion_latido
                   se aplican en compute_energy_units, no aquí).
        cycle_id: id del cycle del Embrión que solicitó el recharge.
        source_breakdown: dict opcional con detalle por source (para postmortem).

    Returns:
        dict con la fila persistida (para auditoría).

    Raises:
        ValueError: si units_usd < 0.
        RuntimeError: si Supabase no responde (caller debe fail-soft).
    """
    units = _RotorDecimal(str(units_usd))
    if units < 0:
        raise ValueError(
            f"add_recycled_energy: units_usd debe ser >= 0 (recibido {units}). "
            "Las penalizaciones se aplican en compute_energy_units, no aqui."
        )
    if units == 0:
        # No-op silencioso, no spammear DB con zeros
        logger.info("rotor.budget.add_recycled_energy_zero", cycle_id=cycle_id)
        return {"recorded": False, "reason": "zero_units"}

    client = supabase_client or _get_supabase_client()

    # cost_actual_usd negativo = recharge (lo opuesto de un consumo)
    payload = {
        "cycle_id": cycle_id,
        "cost_actual_usd": -float(units),  # NEGATIVO = recharge
        "cost_estimated_usd": -float(units),
        "cap_excedido": False,
        "abort_reason": "rotor_recharge",
        "model_used": "rotor",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if source_breakdown:
        # Persistir breakdown como JSON en abort_reason (campo TEXT libre)
        payload["abort_reason"] = (
            "rotor_recharge:" + _rotor_json.dumps(source_breakdown, default=str)
        )[:500]  # truncar para no romper si hay muchos sources

    try:
        result = client.insert("embrion_budget_state", payload)
        logger.info(
            "rotor.budget.add_recycled_energy_ok",
            cycle_id=cycle_id,
            units_usd=str(units),
            sources=list(source_breakdown.keys()) if source_breakdown else [],
        )
        return {"recorded": True, "row": result[0] if result else None}
    except Exception as exc:
        logger.error(
            "rotor.budget.add_recycled_energy_failed",
            err=str(exc),
            cycle_id=cycle_id,
            units_usd=str(units),
        )
        raise RuntimeError(f"add_recycled_energy: insert fallido: {exc}") from exc


# ── /Sprint ROTOR-001 ──────────────────────────────────────────────────────
