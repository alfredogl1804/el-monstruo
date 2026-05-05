"""
Sprint 87 — Endpoints FastAPI para el pipeline E2E.

Mounted en main.py via app.include_router(e2e_router).
Auth: MONSTRUO_API_KEY (header X-API-Key).

Endpoints:
- POST /v1/e2e/run                          — arranca pipeline en background
- GET  /v1/e2e/runs                         — lista runs (con filtro de estado)
- GET  /v1/e2e/runs/{run_id}                — detalle de un run + steps
- POST /v1/e2e/runs/{run_id}/judgment       — Alfredo emite veredicto
- GET  /v1/e2e/dashboard                    — snapshot agregado JSON
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from kernel.e2e.orchestrator import E2EOrchestrator
from kernel.e2e.schema import (
    DashboardSnapshot,
    EstadoRun,
    JudgmentRequest,
    RunRequest,
    RunResponse,
    Veredicto,
)


e2e_router = APIRouter(prefix="/v1/e2e", tags=["e2e"])


def _expected_api_key() -> str:
    return os.environ.get("MONSTRUO_API_KEY", "")


def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> None:
    expected = _expected_api_key()
    if not expected:
        # Si no hay key configurada en el ambiente, permitimos el request (dev local).
        return
    if not x_api_key or x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="e2e_auth_invalid_api_key",
        )


def _get_orchestrator(request: Request) -> E2EOrchestrator:
    orch = getattr(request.app.state, "e2e_orchestrator", None)
    if orch is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="e2e_orchestrator_not_initialized",
        )
    return orch


@e2e_router.post(
    "/run",
    response_model=RunResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_api_key)],
)
async def post_run(
    body: RunRequest,
    request: Request,
) -> RunResponse:
    orch = _get_orchestrator(request)
    run = await orch.start_run(body.frase_input, body.metadata)
    return RunResponse(
        run_id=run.id,
        estado=run.estado,
        accepted_at=datetime.now(timezone.utc),
    )


@e2e_router.get(
    "/runs",
    dependencies=[Depends(require_api_key)],
)
async def list_runs(
    request: Request,
    estado: Optional[EstadoRun] = None,
    limit: int = 50,
):
    orch = _get_orchestrator(request)
    runs = await orch.list_runs(estado=estado, limit=limit)
    return {
        "count": len(runs),
        "runs": [r.model_dump(mode="json") for r in runs],
    }


@e2e_router.get(
    "/runs/{run_id}",
    dependencies=[Depends(require_api_key)],
)
async def get_run_detail(run_id: str, request: Request):
    orch = _get_orchestrator(request)
    run = await orch.get_run(run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"e2e_run_not_found:{run_id}",
        )
    steps = await orch.repository.list_steps_for_run(run_id)
    return {
        "run": run.model_dump(mode="json"),
        "steps": [s.model_dump(mode="json") for s in steps],
    }


@e2e_router.post(
    "/runs/{run_id}/judgment",
    dependencies=[Depends(require_api_key)],
)
async def post_judgment(
    run_id: str,
    body: JudgmentRequest,
    request: Request,
):
    orch = _get_orchestrator(request)
    updated = await orch.emit_judgment(run_id, body.veredicto, body.nota)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"e2e_run_not_found:{run_id}",
        )
    return {"run": updated.model_dump(mode="json")}


@e2e_router.get(
    "/dashboard",
    response_model=DashboardSnapshot,
    dependencies=[Depends(require_api_key)],
)
async def get_dashboard(request: Request) -> DashboardSnapshot:
    orch = _get_orchestrator(request)
    return await orch.dashboard_snapshot()
