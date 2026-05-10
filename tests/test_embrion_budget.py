"""
tests/test_embrion_budget.py

Sprint EMBRION-NEEDS-001, Tarea 1.

Cubre los casos requeridos por el spec:
  - Latido proyectado a $0.30 → abortado antes de gastar.
  - 3er latido excedido en un día → escalación HITL disparada.

Plus:
  - Estimación de costo determinística por modelo.
  - Pre-flight passes cuando estimated < cap.
  - Pre-flight aborta cuando daily budget exhausto.
  - record_after_cycle marca cap_excedido si actual > cap.
  - daily_summary agrupa correctamente.
  - maybe_escalate_hitl idempotente (no escala 2 veces el mismo día).

Estrategia: usamos un FakeSupabaseClient que cumple la interfaz mínima
(_SupabaseRest.select/insert) sin hacer red.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import pytest

# El módulo lee env al importar; seteamos antes del import.
os.environ.setdefault("EMBRION_CAP_PER_LATIDO_USD", "0.25")
os.environ.setdefault("EMBRION_DAILY_BUDGET", "30.0")
os.environ.setdefault("EMBRION_HITL_ESCALATION_THRESHOLD", "3")

from kernel import embrion_budget as eb


class FakeClient:
    """Cliente Supabase mockeado: store en memoria por tabla."""

    def __init__(self, prefilled: dict[str, list[dict]] | None = None):
        self.tables: dict[str, list[dict]] = prefilled or {}
        self.calls: list[tuple] = []

    def select(self, table: str, params: dict, prefer: str | None = None):
        self.calls.append(("select", table, params, prefer))
        rows = list(self.tables.get(table, []))

        # Filtro por created_at gte (parser muy básico, suficiente para tests)
        ca = params.get("created_at", "")
        if ca.startswith("gte."):
            cutoff = ca[len("gte."):]
            rows = [r for r in rows if (r.get("created_at") or "") >= cutoff]

        # Filtros de igualdad: cap_excedido=eq.true, tipo=eq.X, hilo_origen=eq.X
        for k, v in params.items():
            if k in ("created_at", "select", "limit", "order"):
                continue
            if isinstance(v, str) and v.startswith("eq."):
                expected = v[len("eq."):]
                if expected == "true":
                    rows = [r for r in rows if r.get(k) is True]
                elif expected == "false":
                    rows = [r for r in rows if r.get(k) is False]
                else:
                    rows = [r for r in rows if str(r.get(k)) == expected]

        # Limit
        lim = params.get("limit")
        if lim:
            rows = rows[: int(lim)]

        return rows, {"Content-Range": f"0-{max(0, len(rows)-1)}/{len(rows)}"}

    def insert(self, table: str, payload: Any):
        self.calls.append(("insert", table, payload))
        if isinstance(payload, dict):
            payload = [payload]
        for p in payload:
            row = dict(p)
            row.setdefault("id", str(uuid4()))
            row.setdefault("created_at", datetime.now(timezone.utc).isoformat())
            self.tables.setdefault(table, []).append(row)
        return payload


# ── 1) Estimación de costo

def test_estimate_cost_gpt5():
    # gpt-5 input $2.50 / 1M, output $10 / 1M
    # 1000 tok in + 500 tok out
    # = 1000/1e6 * 2.5  + 500/1e6 * 10
    # = 0.0025 + 0.005 = 0.0075
    cost = eb.estimate_cost_usd(estimated_tokens_in=1000, estimated_tokens_out=500, model="gpt-5")
    assert abs(cost - 0.0075) < 1e-9


def test_estimate_cost_unknown_model_falls_back_to_gpt5():
    cost1 = eb.estimate_cost_usd(estimated_tokens_in=1000, estimated_tokens_out=500, model="UNKNOWN")
    cost2 = eb.estimate_cost_usd(estimated_tokens_in=1000, estimated_tokens_out=500, model="gpt-5")
    assert cost1 == cost2


def test_estimate_cost_gpt55_more_expensive():
    cost_5 = eb.estimate_cost_usd(estimated_tokens_in=10000, estimated_tokens_out=5000, model="gpt-5")
    cost_55 = eb.estimate_cost_usd(estimated_tokens_in=10000, estimated_tokens_out=5000, model="gpt-5.5")
    assert cost_55 > cost_5


# ── 2) Pre-flight aborta cuando estimated > cap (REQUERIDO POR SPEC)

def test_check_before_cycle_aborts_when_estimated_exceeds_cap():
    """Spec: 'latido proyectado a $0.30 se aborta antes de gastar'."""
    fake = FakeClient()
    # Forzamos un cycle con tokens enormes que dan ~$0.30 con gpt-5
    # gpt-5: 0.30 = (in_tok/1e6)*2.5 + (out_tok/1e6)*10
    # Con out=20000, costo = 20000/1e6 * 10 = 0.20. Falta 0.10 con input.
    # Con in=40000, costo = 40000/1e6 * 2.5 = 0.10. Total 0.30.
    decision = eb.check_before_cycle(
        estimated_tokens_in=40000,
        estimated_tokens_out=20000,
        model="gpt-5",
        supabase_client=fake,
    )
    assert decision.allow is False
    assert decision.reason == "estimated_exceeds_cap"
    assert abs(decision.cost_estimated_usd - 0.30) < 1e-6
    assert decision.cap_per_latido_usd == 0.25


def test_check_before_cycle_passes_when_estimated_under_cap():
    fake = FakeClient()
    decision = eb.check_before_cycle(
        estimated_tokens_in=10000,
        estimated_tokens_out=5000,
        model="gpt-5",
        supabase_client=fake,
    )
    assert decision.allow is True
    assert decision.reason == "ok"


def test_check_before_cycle_aborts_when_daily_exhausted():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:01+00:00")
    fake = FakeClient(prefilled={
        "embrion_budget_state": [
            {"cost_actual_usd": 29.95, "created_at": today, "cap_excedido": False},
        ],
    })
    decision = eb.check_before_cycle(
        estimated_tokens_in=20000,
        estimated_tokens_out=10000,
        model="gpt-5",
        supabase_client=fake,
        daily_budget_usd=30.0,
    )
    # 0.15 estimado + 29.95 acumulado = 30.10 > 30.0 → abort
    assert decision.allow is False
    assert decision.reason == "daily_budget_exhausted"


def test_check_before_cycle_warns_near_daily_limit():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:01+00:00")
    fake = FakeClient(prefilled={
        "embrion_budget_state": [
            {"cost_actual_usd": 28.7, "created_at": today, "cap_excedido": False},
        ],
    })
    # Estimado pequeño, pasa, pero >= 95% del cap diario
    decision = eb.check_before_cycle(
        estimated_tokens_in=10000,
        estimated_tokens_out=5000,
        model="gpt-5",
        supabase_client=fake,
    )
    assert decision.allow is True
    assert decision.reason == "daily_budget_near_limit"


# ── 3) record_after_cycle

def test_record_after_cycle_marks_cap_excedido_when_actual_exceeds():
    fake = FakeClient()
    result = eb.CycleResult(
        cycle_id=42,
        cost_actual_usd=0.40,  # > cap 0.25
        tokens_used=12345,
        model_used="gpt-5.5",
    )
    inserted = eb.record_after_cycle(result, supabase_client=fake)
    assert inserted["cap_excedido"] is True
    assert inserted["cost_actual_usd"] == 0.40
    assert inserted["cycle_id"] == 42
    assert "embrion_budget_state" in fake.tables


def test_record_after_cycle_no_excedido_when_under_cap():
    fake = FakeClient()
    result = eb.CycleResult(
        cycle_id=43,
        cost_actual_usd=0.10,
        tokens_used=5000,
        model_used="gpt-5",
    )
    inserted = eb.record_after_cycle(result, supabase_client=fake)
    assert inserted["cap_excedido"] is False


# ── 4) HITL escalation (REQUERIDO POR SPEC)

def test_maybe_escalate_hitl_no_escala_si_pocos_excedidos():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:01:00+00:00")
    fake = FakeClient(prefilled={
        "embrion_budget_state": [
            {"cycle_id": 1, "cap_excedido": True, "created_at": today, "cost_estimated_usd": 0.30, "abort_reason": "estimated_exceeds_cap"},
            {"cycle_id": 2, "cap_excedido": True, "created_at": today, "cost_estimated_usd": 0.32, "abort_reason": "estimated_exceeds_cap"},
        ],
    })
    out = eb.maybe_escalate_hitl(supabase_client=fake)
    assert out is None


def test_maybe_escalate_hitl_escala_al_3er_excedido():
    """Spec: 'escalación HITL se dispara al 3er latido excedido'."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:01:00+00:00")
    fake = FakeClient(prefilled={
        "embrion_budget_state": [
            {"cycle_id": 1, "cap_excedido": True, "created_at": today, "cost_estimated_usd": 0.30, "abort_reason": "estimated_exceeds_cap"},
            {"cycle_id": 2, "cap_excedido": True, "created_at": today, "cost_estimated_usd": 0.32, "abort_reason": "estimated_exceeds_cap"},
            {"cycle_id": 3, "cap_excedido": True, "created_at": today, "cost_estimated_usd": 0.45, "abort_reason": "estimated_exceeds_cap"},
        ],
    })
    out = eb.maybe_escalate_hitl(supabase_client=fake)
    assert out is not None
    assert out["tipo"] == "respuesta_embrion"
    assert out["hilo_origen"] == "embrion_budget"
    assert out["importancia"] == 10
    assert out["contexto"]["requires_alfredo_approval"] is True
    assert out["contexto"]["exceeded_count_today"] == 3
    assert "$0.25" in out["contenido"] or "0.25" in out["contenido"]


def test_maybe_escalate_hitl_idempotente():
    """Si ya escalamos hoy, no spameamos."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:01:00+00:00")
    fake = FakeClient(prefilled={
        "embrion_budget_state": [
            {"cycle_id": i, "cap_excedido": True, "created_at": today, "cost_estimated_usd": 0.30, "abort_reason": "estimated_exceeds_cap"}
            for i in range(5)
        ],
        "embrion_memoria": [
            {"id": "abc", "tipo": "respuesta_embrion", "hilo_origen": "embrion_budget", "created_at": today},
        ],
    })
    out = eb.maybe_escalate_hitl(supabase_client=fake)
    assert out is None


# ── 5) record_aborted_cycle

def test_record_aborted_cycle_persiste_telemetria():
    fake = FakeClient()
    decision = eb.BudgetDecision(
        allow=False,
        reason="estimated_exceeds_cap",
        cap_per_latido_usd=0.25,
        cost_estimated_usd=0.45,
        daily_spent_usd=0.0,
        daily_budget_usd=30.0,
    )
    inserted = eb.record_aborted_cycle(
        cycle_id=99,
        decision=decision,
        trigger_type="reflexion",
        trigger_detail="reflexion sobre auto-mejora",
        model_used="gpt-5.5",
        supabase_client=fake,
    )
    assert inserted["cycle_id"] == 99
    assert inserted["abort_reason"] == "estimated_exceeds_cap"
    assert inserted["cap_excedido"] is True
    assert inserted["cost_actual_usd"] == 0


# ── 6) daily_summary

def test_daily_summary_agrupa_por_modelo():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:01:00+00:00")
    fake = FakeClient(prefilled={
        "embrion_budget_state": [
            {"cycle_id": 1, "cost_actual_usd": 0.10, "model_used": "gpt-5",   "cap_excedido": False, "created_at": today},
            {"cycle_id": 2, "cost_actual_usd": 0.20, "model_used": "gpt-5",   "cap_excedido": False, "created_at": today},
            {"cycle_id": 3, "cost_actual_usd": 0.30, "model_used": "gpt-5.5", "cap_excedido": True,  "created_at": today, "abort_reason": "actual_exceeds_cap"},
        ],
    })
    s = eb.daily_summary(supabase_client=fake)
    assert s["cycles_total"] == 3
    assert s["cycles_excedidos"] == 1
    assert s["cost_actual_usd"] == 0.60
    assert s["by_model"]["gpt-5"]["cycles"] == 2
    assert s["by_model"]["gpt-5"]["cost_usd"] == 0.30
    assert s["by_model"]["gpt-5.5"]["cycles"] == 1


# ── 7) integración: el bucle del 1 de mayo se hubiera frenado

def test_caso_real_bucle_1_mayo_se_hubiera_frenado():
    """
    El 1 de mayo el embrión gastó $105 USD en 98 respuestas. Promedio ~$1.07
    por respuesta. Con cap $0.25, cada una hubiera sido abortada en pre-flight.

    Simulamos: 98 cycles, cada uno proyectado a $1.07, todos deberían abortarse.
    """
    fake = FakeClient()
    aborts = 0
    for i in range(98):
        # tokens que producen ~$1.07 con gpt-5.5
        # gpt-5.5 out $12/1M → 1.07 ≈ 80000 tokens output + 30000 input
        d = eb.check_before_cycle(
            estimated_tokens_in=30000,
            estimated_tokens_out=80000,
            model="gpt-5.5",
            supabase_client=fake,
        )
        if not d.allow:
            aborts += 1
            eb.record_aborted_cycle(
                cycle_id=i, decision=d,
                trigger_type="reflexion",
                supabase_client=fake,
            )

    assert aborts == 98, "TODOS los cycles del 1 de mayo deberían haber sido abortados con el cap activo"
    # Y al 3er abort, escalación HITL se hubiera disparado
    out = eb.maybe_escalate_hitl(supabase_client=fake)
    assert out is not None
    assert out["contexto"]["exceeded_count_today"] >= 3
