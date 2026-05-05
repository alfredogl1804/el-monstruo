"""
Sprint 87.2 Bloque 4 — Endpoints FastAPI para Traffic Soberano.

Mounted en main.py via app.include_router(traffic_router).
NO requiere API key (es público para que monstruo-tracking.js pueda hacer ingest
desde cualquier landing deployada). Anti-abuso: límite de tamaño body + rate
limit a futuro (Sprint 87.3).

Endpoints:
- POST /v1/traffic/ingest                — recibe evento desde tracking script
- GET  /v1/traffic/summary/{run_id}      — métricas agregadas para un run
"""
from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from kernel.e2e.traffic.repository import (
    TrafficEvent,
    TrafficIngestFailed,
    TrafficRepository,
    TrafficSummary,
)

traffic_router = APIRouter(prefix="/v1/traffic", tags=["traffic"])

# Límite anti-abuso para el body del ingest endpoint
MAX_BODY_BYTES = 4096


def _get_repo(request: Request) -> TrafficRepository:
    repo = getattr(request.app.state, "traffic_repository", None)
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="traffic_repository_not_initialized",
        )
    return repo


@traffic_router.post(
    "/ingest",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def post_ingest(request: Request) -> JSONResponse:
    """Recibe evento de monstruo-tracking.js. Privacy-first, sin auth."""
    body_bytes = await request.body()
    if len(body_bytes) > MAX_BODY_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="traffic_ingest_validation_failed:body_too_large",
        )
    if not body_bytes:
        # sendBeacon vacío → 204 silencioso
        return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"traffic_ingest_validation_failed:json_parse:{e!s}",
        )

    try:
        event = TrafficEvent(**payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"traffic_ingest_validation_failed:schema:{e!s}",
        )

    repo = _get_repo(request)
    try:
        await repo.ingest_event(event)
    except TrafficIngestFailed as e:
        # No exponer detalles internos a navegadores anónimos
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.code,
        )

    # 204 No Content, no leak de internals
    return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)


@traffic_router.get(
    "/summary/{run_id}",
    response_model=TrafficSummary,
)
async def get_summary(run_id: str, request: Request) -> TrafficSummary:
    """Retorna métricas agregadas de tráfico para un run específico."""
    repo = _get_repo(request)
    return await repo.summarize_run(run_id)
