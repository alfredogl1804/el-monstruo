"""
Tests de integración para Sprint EMBRION-NEEDS-001 — PR de integración.

Valida el cableado de embrion_budget.check_before_cycle() y
embrion_self_verifier.verify() dentro de embrion_loop._think():

  1. Flags OFF → comportamiento previo intacto
  2. Flags ON + budget allow + verifier pass → flujo normal
  3. Flags ON + budget abort → return None, no se llama modelo, persiste abort
  4. Flags ON + verifier abort → return None, memoria como silencio_verificador
  5. Bucle activo simulado → cycles repetidos abortados por verifier

Estos tests son de **cableado** (integración). Los tests unitarios de cada
módulo ya están verdes en PR #38 (15/15) y PR #39 (24/24).
"""
from __future__ import annotations

import asyncio
import os
import sys
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ─── Configurar ambiente ANTES de importar embrion_loop ────────────────
os.environ.setdefault("EMBRION_BUDGET_TRACKER_ENABLED", "true")
os.environ.setdefault("EMBRION_SELF_VERIFIER_ENABLED", "true")


@pytest.fixture
def loop_module():
    """Carga embrion_loop con mocks de dependencias problemáticas."""
    # Mock de embrion_budget y embrion_self_verifier antes del import
    mock_budget = types.ModuleType("kernel.embrion_budget")
    mock_verifier = types.ModuleType("kernel.embrion_self_verifier")

    sys.modules.setdefault("kernel.embrion_budget", mock_budget)
    sys.modules.setdefault("kernel.embrion_self_verifier", mock_verifier)

    from kernel import embrion_loop
    return embrion_loop


def _make_loop(loop_module, *, kernel=None, db=None):
    """Construye un EmbrionLoop con mocks mínimos para invocar _think."""
    L = loop_module.EmbrionLoop(
        kernel=kernel or MagicMock(),
        db=db or MagicMock(),
    )
    # Mocks de métodos auxiliares que _think llama
    L._get_relevant_lessons = AsyncMock(return_value="")
    L._save_memory = AsyncMock(return_value=None)
    L._think_with_graph = AsyncMock(return_value=("Respuesta de prueba", 100, 0.05, []))
    L._think_with_router = AsyncMock(return_value=("Respuesta de prueba", 100, 0.05, []))
    L._cycle_count = 1
    L._cost_today_usd = 0.0
    L._thoughts_today = 0
    L._fcs_tool_calls_total = 0
    return L


# ────────────────────────────────────────────────────────────────────────
# Test 1: Ambas flags OFF → comportamiento previo intacto
# ────────────────────────────────────────────────────────────────────────

def test_flags_off_no_invocan_budget_ni_verifier(loop_module, monkeypatch):
    """Con ambas flags en False, no debe llamar a check_before_cycle ni a verify."""
    monkeypatch.setattr(loop_module, "EMBRION_BUDGET_TRACKER_ENABLED", False)
    monkeypatch.setattr(loop_module, "EMBRION_SELF_VERIFIER_ENABLED", False)

    L = _make_loop(loop_module)

    check_mock = MagicMock()
    verify_mock = MagicMock()
    monkeypatch.setattr(loop_module._embrion_budget, "check_before_cycle", check_mock, raising=False)
    monkeypatch.setattr(loop_module._embrion_self_verifier, "verify", verify_mock, raising=False)

    trigger = {"type": "reflexion_autonoma", "detail": "tick", "priority": 5}
    result = asyncio.run(L._think(trigger))

    assert result is not None
    assert result["response"] == "Respuesta de prueba"
    check_mock.assert_not_called()
    verify_mock.assert_not_called()


# ────────────────────────────────────────────────────────────────────────
# Test 2: Flags ON, budget allow + verifier pass → flujo normal
# ────────────────────────────────────────────────────────────────────────

def test_flags_on_flujo_normal_pasa(loop_module, monkeypatch):
    """Con flags ON, si budget allow y verifier pass, retorna response normal."""
    monkeypatch.setattr(loop_module, "EMBRION_BUDGET_TRACKER_ENABLED", True)
    monkeypatch.setattr(loop_module, "EMBRION_SELF_VERIFIER_ENABLED", True)

    L = _make_loop(loop_module)

    # Budget allow
    fake_decision = MagicMock()
    fake_decision.allow = True
    fake_decision.reason = "ok"
    check_mock = MagicMock(return_value=fake_decision)
    record_mock = MagicMock()
    monkeypatch.setattr(loop_module._embrion_budget, "check_before_cycle", check_mock, raising=False)
    monkeypatch.setattr(loop_module._embrion_budget, "record_after_cycle", record_mock, raising=False)
    monkeypatch.setattr(loop_module._embrion_budget, "CycleResult", MagicMock(), raising=False)

    # Verifier pass
    fake_sv = MagicMock()
    fake_sv.abort = False
    fake_sv.reasons = ["D1 purpose=True", "D2 novelty=True", "D3 verifiable=True"]
    fake_sv.votes_no = 0
    fake_sv.decision_purpose = True
    fake_sv.decision_novelty = True
    fake_sv.decision_verifiable = True
    fake_sv.similarity_score = 0.1
    verify_mock = MagicMock(return_value=fake_sv)
    monkeypatch.setattr(loop_module._embrion_self_verifier, "verify", verify_mock, raising=False)

    trigger = {"type": "reflexion_autonoma", "detail": "tick", "priority": 5}
    result = asyncio.run(L._think(trigger))

    assert result is not None
    assert result["response"] == "Respuesta de prueba"
    check_mock.assert_called_once()
    verify_mock.assert_called_once()
    record_mock.assert_called_once()
    # Memoria guardada como tipo normal (latido), no como silencio_verificador
    save_call = L._save_memory.await_args
    assert save_call.kwargs["tipo"] == "latido"


# ────────────────────────────────────────────────────────────────────────
# Test 3: Budget abort → return None, NO llama al modelo
# ────────────────────────────────────────────────────────────────────────

def test_budget_abort_retorna_none_sin_llamar_modelo(loop_module, monkeypatch):
    """Si check_before_cycle dice abort, no se llama al modelo y retorna None."""
    monkeypatch.setattr(loop_module, "EMBRION_BUDGET_TRACKER_ENABLED", True)
    monkeypatch.setattr(loop_module, "EMBRION_SELF_VERIFIER_ENABLED", True)

    L = _make_loop(loop_module)

    # Budget abort
    fake_decision = MagicMock()
    fake_decision.allow = False
    fake_decision.reason = "estimated_exceeds_cap"
    fake_decision.cost_estimated_usd = 0.30
    fake_decision.cap_per_latido_usd = 0.25
    fake_decision.daily_spent_usd = 5.0
    fake_decision.daily_budget_usd = 30.0
    check_mock = MagicMock(return_value=fake_decision)
    record_aborted_mock = MagicMock()
    escalate_mock = MagicMock()
    monkeypatch.setattr(loop_module._embrion_budget, "check_before_cycle", check_mock, raising=False)
    monkeypatch.setattr(loop_module._embrion_budget, "record_aborted_cycle", record_aborted_mock, raising=False)
    monkeypatch.setattr(loop_module._embrion_budget, "maybe_escalate_hitl", escalate_mock, raising=False)

    verify_mock = MagicMock()
    monkeypatch.setattr(loop_module._embrion_self_verifier, "verify", verify_mock, raising=False)

    trigger = {"type": "reflexion_autonoma", "detail": "tick", "priority": 5}
    result = asyncio.run(L._think(trigger))

    assert result is None, "Si budget abort, _think debe retornar None"
    check_mock.assert_called_once()
    record_aborted_mock.assert_called_once()
    escalate_mock.assert_called_once()
    # NO se llamó al modelo
    L._think_with_graph.assert_not_called()
    L._think_with_router.assert_not_called()
    # NO se llamó al verifier (porque ni siquiera generamos respuesta)
    verify_mock.assert_not_called()


# ────────────────────────────────────────────────────────────────────────
# Test 4: Verifier abort → return None, memoria como silencio_verificador
# ────────────────────────────────────────────────────────────────────────

def test_verifier_abort_marca_memoria_silencio(loop_module, monkeypatch):
    """Si verifier abort=True, la memoria se guarda como silencio_verificador."""
    monkeypatch.setattr(loop_module, "EMBRION_BUDGET_TRACKER_ENABLED", True)
    monkeypatch.setattr(loop_module, "EMBRION_SELF_VERIFIER_ENABLED", True)

    L = _make_loop(loop_module)

    # Budget allow
    fake_decision = MagicMock()
    fake_decision.allow = True
    fake_decision.reason = "ok"
    monkeypatch.setattr(loop_module._embrion_budget, "check_before_cycle", MagicMock(return_value=fake_decision), raising=False)
    monkeypatch.setattr(loop_module._embrion_budget, "record_after_cycle", MagicMock(), raising=False)
    monkeypatch.setattr(loop_module._embrion_budget, "CycleResult", MagicMock(), raising=False)

    # Verifier abort
    fake_sv = MagicMock()
    fake_sv.abort = True
    fake_sv.reasons = ["D1 purpose=False: anti-purpose phrase 'recibido y entendido'", "D2 novelty=False: jaccard=0.92"]
    fake_sv.votes_no = 2
    fake_sv.decision_purpose = False
    fake_sv.decision_novelty = False
    fake_sv.decision_verifiable = True
    fake_sv.similarity_score = 0.92
    monkeypatch.setattr(loop_module._embrion_self_verifier, "verify", MagicMock(return_value=fake_sv), raising=False)

    trigger = {"type": "reflexion_autonoma", "detail": "tick", "priority": 5}
    result = asyncio.run(L._think(trigger))

    assert result is None, "Si verifier abort, _think debe retornar None"
    # Memoria SI guardada (para auditoría) pero como silencio_verificador
    save_call = L._save_memory.await_args
    assert save_call.kwargs["tipo"] == "silencio_verificador"
    assert save_call.kwargs["importancia"] == 1, "Importancia bajada porque fue eco"
    assert save_call.kwargs["contexto"]["verifier_aborted"] is True
    assert "verifier_reasons" in save_call.kwargs["contexto"]


# ────────────────────────────────────────────────────────────────────────
# Test 5: Bucle activo simulado — 5 cycles del bucle abortados
# ────────────────────────────────────────────────────────────────────────

def test_bucle_activo_simulado_aborta_repetidos(loop_module, monkeypatch):
    """Simula el bucle real del 10-may donde 30+ respuestas idénticas
    aparecen. El verifier debe abortar todas a partir de la 2da."""
    monkeypatch.setattr(loop_module, "EMBRION_BUDGET_TRACKER_ENABLED", True)
    monkeypatch.setattr(loop_module, "EMBRION_SELF_VERIFIER_ENABLED", True)

    # Budget siempre allow (queremos probar que verifier es quien frena)
    fake_decision = MagicMock()
    fake_decision.allow = True
    fake_decision.reason = "ok"
    monkeypatch.setattr(loop_module._embrion_budget, "check_before_cycle", MagicMock(return_value=fake_decision), raising=False)
    monkeypatch.setattr(loop_module._embrion_budget, "record_after_cycle", MagicMock(), raising=False)
    monkeypatch.setattr(loop_module._embrion_budget, "CycleResult", MagicMock(), raising=False)

    # Verifier: primer cycle pasa, los siguientes abortan (simulando duplicados)
    call_count = {"n": 0}
    def _fake_verify(thought, *, trigger_type, cycle_id, supabase_client=None, persist=True):
        call_count["n"] += 1
        sv = MagicMock()
        if call_count["n"] == 1:
            sv.abort = False
            sv.votes_no = 0
            sv.decision_purpose = True
            sv.decision_novelty = True
            sv.decision_verifiable = True
        else:
            sv.abort = True
            sv.votes_no = 2
            sv.decision_purpose = False
            sv.decision_novelty = False
            sv.decision_verifiable = True
        sv.reasons = [f"call {call_count['n']}"]
        sv.similarity_score = 0.9 if call_count["n"] > 1 else 0.1
        return sv
    monkeypatch.setattr(loop_module._embrion_self_verifier, "verify", _fake_verify, raising=False)

    L = _make_loop(loop_module)
    # Modelo siempre devuelve la misma respuesta (simula eco)
    L._think_with_router = AsyncMock(
        return_value=("Recibido y entendido. Procedo con análisis.", 800, 0.04, [])
    )

    results = []
    for i in range(5):
        L._cycle_count = 76 + i
        trigger = {"type": "reflexion_autonoma", "detail": f"tick_{i}", "priority": 5}
        results.append(asyncio.run(L._think(trigger)))

    # Cycle 76 → response normal
    assert results[0] is not None, "Primer cycle debe pasar"
    # Cycles 77-80 → abortados por verifier (return None)
    assert all(r is None for r in results[1:]), "Cycles repetidos deben abortar"
    # save_memory llamado 5 veces (todos guardados, pero 4 como silencio)
    assert L._save_memory.await_count == 5
