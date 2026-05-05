"""
Sprint 87 — Tests sintéticos del pipeline E2E.

Cubren:
- Repository CRUD básico (create_run, get_run, update_run, append_step_log)
- Orchestrator lifecycle (start_run dispara pipeline, dashboard agrega)
- Catastro client (selección + fallback)
- Pipeline 12 pasos (con DBClient mock + CatastroRuntimeClient mock)
- Routes (autenticación, 404, 202)

Sin red. Sin dependencias productivas.
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pytest

from kernel.e2e.catastro_client import CatastroRuntimeClient, STEP_FALLBACK_MODEL
from kernel.e2e.orchestrator import E2EOrchestrator
from kernel.e2e.pipeline import run_e2e_pipeline
from kernel.e2e.repository import E2ERepository, generate_run_id
from kernel.e2e.schema import (
    EstadoRun,
    PIPELINE_STEPS,
    StepName,
    StepStatus,
    Veredicto,
)


# ---------------- DB Mock ----------------


class FakeDBClient:
    """Mock in-memory de SupabaseClient suficiente para repository.py."""

    def __init__(self) -> None:
        self._rows: Dict[str, List[dict]] = {"e2e_runs": [], "e2e_step_log": []}
        self._connected = True
        self._step_id_seq = 0

    @property
    def connected(self) -> bool:
        return self._connected

    async def insert(self, table: str, data: dict) -> Optional[dict]:
        if table == "e2e_step_log":
            self._step_id_seq += 1
            data = {**data, "id": self._step_id_seq, "ts": datetime.now(timezone.utc).isoformat()}
        self._rows[table].append(data)
        return data

    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[dict] = None,
        order_by: Optional[str] = None,
        order_desc: bool = True,
        limit: Optional[int] = None,
    ) -> List[dict]:
        rows = list(self._rows.get(table, []))
        if filters:
            for k, v in filters.items():
                rows = [r for r in rows if r.get(k) == v]
        if order_by:
            rows.sort(key=lambda r: (r.get(order_by) or ""), reverse=order_desc)
        if limit is not None:
            rows = rows[:limit]
        return rows

    async def update(
        self,
        table: str,
        data: dict,
        filters: dict,
    ) -> Optional[dict]:
        for r in self._rows.get(table, []):
            if all(r.get(k) == v for k, v in filters.items()):
                r.update(data)
                return r
        return None


# ---------------- Schema / IDs ----------------


def test_pipeline_steps_consistency():
    assert len(PIPELINE_STEPS) == 12
    numbers = [n for n, _ in PIPELINE_STEPS]
    names = [s for _, s in PIPELINE_STEPS]
    assert numbers == list(range(1, 13))
    assert names[0] == StepName.INTAKE
    assert names[-1] == StepName.VEREDICTO
    # No duplicados
    assert len(set(names)) == 12


def test_generate_run_id_format():
    rid = generate_run_id("test landing")
    assert rid.startswith("e2e_")
    parts = rid.split("_")
    assert len(parts) == 3
    assert parts[1].isdigit()
    assert len(parts[2]) == 6


# ---------------- Repository ----------------


@pytest.mark.asyncio
async def test_repository_create_and_get_run():
    db = FakeDBClient()
    repo = E2ERepository(db)
    run = await repo.create_run("hacé una landing premium para pintura al óleo", {"src": "test"})
    assert run.estado == EstadoRun.IN_PROGRESS
    assert run.pipeline_step == 0
    fetched = await repo.get_run(run.id)
    assert fetched is not None
    assert fetched.frase_input.startswith("hacé una landing")


@pytest.mark.asyncio
async def test_repository_update_run_partial():
    db = FakeDBClient()
    repo = E2ERepository(db)
    run = await repo.create_run("frase", {})
    updated = await repo.update_run(run.id, pipeline_step=3, deploy_url="https://example.com")
    assert updated is not None
    assert updated.pipeline_step == 3
    assert updated.deploy_url == "https://example.com"
    # Otros campos no se tocaron
    assert updated.estado == EstadoRun.IN_PROGRESS


@pytest.mark.asyncio
async def test_repository_metadata_merge():
    db = FakeDBClient()
    repo = E2ERepository(db)
    run = await repo.create_run("frase", {"a": 1})
    updated = await repo.update_run(run.id, metadata_patch={"b": 2})
    assert updated is not None
    assert updated.metadata == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_repository_append_step_log():
    db = FakeDBClient()
    repo = E2ERepository(db)
    run = await repo.create_run("frase", {})
    log = await repo.append_step_log(
        run.id,
        step_number=1,
        step_name=StepName.INTAKE,
        status=StepStatus.OK,
        duration_ms=42,
    )
    assert log is not None
    assert log.step_number == 1
    assert log.status == StepStatus.OK
    listed = await repo.list_steps_for_run(run.id)
    assert len(listed) == 1


# ---------------- Catastro Client (fallback) ----------------


@pytest.mark.asyncio
async def test_catastro_client_fallback_on_missing_url(monkeypatch):
    monkeypatch.setenv("E2E_CATASTRO_BASE_URL", "http://invalid-host.local:1")
    client = CatastroRuntimeClient(timeout_seconds=0.5)
    selection = await client.select_model_for_step("INVESTIGAR")
    assert selection["source"] == "fallback"
    assert selection["model_id"] == STEP_FALLBACK_MODEL["INVESTIGAR"]


@pytest.mark.asyncio
async def test_catastro_client_no_use_case_fallback():
    client = CatastroRuntimeClient(timeout_seconds=0.5)
    selection = await client.select_model_for_step("INTAKE")  # no está en STEP_USE_CASE_MAP
    assert selection["source"] == "fallback"
    assert selection["fallback_reason"] == "no_use_case_mapped"


# ---------------- Orchestrator ----------------


@pytest.mark.asyncio
async def test_orchestrator_start_run_inyecta_runner_fake():
    db = FakeDBClient()
    runner_calls: List[str] = []

    async def fake_runner(run_id: str, repo: E2ERepository) -> None:
        runner_calls.append(run_id)

    orch = E2EOrchestrator(db, pipeline_runner=fake_runner)
    run = await orch.start_run("frase test", {})
    # El runner se dispara en task → esperamos un tick
    await asyncio.sleep(0.05)
    assert run.id in runner_calls


@pytest.mark.asyncio
async def test_orchestrator_emit_judgment():
    db = FakeDBClient()
    orch = E2EOrchestrator(db, pipeline_runner=_no_op_runner)
    run = await orch.start_run("frase", {})
    updated = await orch.emit_judgment(run.id, Veredicto.COMERCIALIZABLE, "Excelente")
    assert updated is not None
    assert updated.veredicto_alfredo == Veredicto.COMERCIALIZABLE
    assert updated.estado == EstadoRun.COMPLETED
    assert updated.completed_at is not None


@pytest.mark.asyncio
async def test_orchestrator_dashboard_snapshot():
    db = FakeDBClient()
    orch = E2EOrchestrator(db, pipeline_runner=_no_op_runner)
    r1 = await orch.start_run("frase 1", {})
    r2 = await orch.start_run("frase 2", {})
    await orch.emit_judgment(r1.id, Veredicto.COMERCIALIZABLE, None)
    snap = await orch.dashboard_snapshot()
    assert snap.runs_total == 2
    assert snap.runs_completed == 1
    assert snap.veredictos_breakdown.get("comercializable") == 1


async def _no_op_runner(run_id: str, repo: E2ERepository) -> None:  # noqa: ANN001
    return None


# ---------------- Pipeline ----------------


@pytest.mark.asyncio
async def test_pipeline_full_12_steps_with_fake_catastro(monkeypatch):
    """Integra repo + pipeline real, con CatastroRuntimeClient siempre en fallback."""
    monkeypatch.setenv("E2E_CATASTRO_BASE_URL", "http://invalid-host.local:1")
    db = FakeDBClient()
    repo = E2ERepository(db)
    run = await repo.create_run("hacé una landing para café de Mérida", {})

    await run_e2e_pipeline(run.id, repo)

    final = await repo.get_run(run.id)
    assert final is not None
    assert final.pipeline_step == 12
    # Como critic_visual_score=60 < 80 → awaiting_judgment
    assert final.estado == EstadoRun.AWAITING_JUDGMENT
    assert final.deploy_url is not None
    assert final.critic_visual_score == 60.0

    steps = await repo.list_steps_for_run(run.id)
    assert len(steps) == 12
    assert all(s.status == StepStatus.OK for s in steps)
    # Steps con LLM deben tener modelo_consultado loggeado
    steps_with_model = [s for s in steps if s.modelo_consultado]
    assert len(steps_with_model) >= 7  # INVESTIGAR..TECNICO + CRITIC


@pytest.mark.asyncio
async def test_pipeline_stack_decision_persisted(monkeypatch):
    monkeypatch.setenv("E2E_CATASTRO_BASE_URL", "http://invalid-host.local:1")
    db = FakeDBClient()
    repo = E2ERepository(db)
    run = await repo.create_run("frase test", {})
    await run_e2e_pipeline(run.id, repo)
    final = await repo.get_run(run.id)
    assert final is not None
    assert final.stack_decision is not None
    assert final.brief is not None


# ---------------- Routes (FastAPI TestClient) ----------------


@pytest.fixture
def app_with_e2e(monkeypatch):
    """FastAPI app aislada con E2EOrchestrator inyectado y FakeDBClient."""
    from fastapi import FastAPI
    from kernel.e2e.routes import e2e_router

    monkeypatch.setenv("MONSTRUO_API_KEY", "test-key-87")
    monkeypatch.setenv("E2E_CATASTRO_BASE_URL", "http://invalid-host.local:1")

    app = FastAPI()
    db = FakeDBClient()
    orch = E2EOrchestrator(db, pipeline_runner=_no_op_runner)
    app.state.e2e_orchestrator = orch
    app.include_router(e2e_router)
    return app


def test_routes_post_run_requires_auth(app_with_e2e):
    from fastapi.testclient import TestClient

    client = TestClient(app_with_e2e)
    response = client.post("/v1/e2e/run", json={"frase_input": "frase test"})
    assert response.status_code == 401
    detail = response.json()["detail"]
    assert detail == "e2e_auth_invalid_api_key"


def test_routes_post_run_accepted(app_with_e2e):
    from fastapi.testclient import TestClient

    client = TestClient(app_with_e2e)
    response = client.post(
        "/v1/e2e/run",
        json={"frase_input": "frase canónica de Alfredo"},
        headers={"X-API-Key": "test-key-87"},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["estado"] == "in_progress"
    assert body["run_id"].startswith("e2e_")


def test_routes_get_run_404(app_with_e2e):
    from fastapi.testclient import TestClient

    client = TestClient(app_with_e2e)
    response = client.get(
        "/v1/e2e/runs/inexistente",
        headers={"X-API-Key": "test-key-87"},
    )
    assert response.status_code == 404


def test_routes_dashboard(app_with_e2e):
    from fastapi.testclient import TestClient

    client = TestClient(app_with_e2e)
    response = client.get(
        "/v1/e2e/dashboard",
        headers={"X-API-Key": "test-key-87"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "runs_total" in body
    assert "veredictos_breakdown" in body
