"""
El Catastro · APIRouter REST (Sprint 86 Bloque 5).

Expone los 4 endpoints REST del Catastro bajo `/v1/catastro/*`:
  · POST /v1/catastro/recommend      → Top N modelos para un caso de uso.
  · GET  /v1/catastro/modelos/{id}   → Ficha detallada del modelo.
  · GET  /v1/catastro/dominios       → Macroáreas + dominios + conteos.
  · GET  /v1/catastro/status         → Snapshot de salud del Catastro.

Diseño (alineado con green light Cowork Bloque 5):
  · Auth idéntico a /v1/memento/validate: header X-API-Key o
    Authorization: Bearer <key> contra os.environ['MONSTRUO_API_KEY']
    leído FRESH en cada request (anti-Dory).
  · El RecommendationEngine vive en app.state.catastro_engine, instanciado
    UNA vez en el lifespan (cache compartido entre requests).
  · Modo degraded NUNCA fallar: si Supabase cae, devolvemos 200 con
    `degraded: true` en el payload (Capa 7 Resiliencia Agéntica).
  · Errores con identidad de marca: detail siempre con prefijo
    `catastro_recommend_*` o `catastro_routes_*`.
  · `set_dependencies(engine)` permite a los tests inyectar mock sin tocar
    el global de FastAPI (mismo patrón que magna_routes/memento_routes).

[Hilo Manus Catastro] · Sprint 86 Bloque 5 · 2026-05-04 · v0.86.5
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException, Path, Query, Request, status
from pydantic import BaseModel, Field

from kernel.catastro.recommendation import (
    CatastroRecommendInvalidArgs,
    DEFAULT_TOP_N,
    MAX_TOP_N,
    ListDominiosResponse,
    ModeloDetallado,
    RecommendationEngine,
    RecommendationResponse,
    StatusSnapshot,
)

logger = structlog.get_logger("kernel.catastro.routes")

router = APIRouter(tags=["catastro"])

# Engine inyectable por tests/lifespan
_engine_singleton: Optional[RecommendationEngine] = None


def set_dependencies(engine: RecommendationEngine) -> None:
    """Inyecta el RecommendationEngine. Llamar una sola vez en lifespan."""
    global _engine_singleton
    _engine_singleton = engine


def _get_engine(request: Request) -> RecommendationEngine:
    """Resuelve el engine: app.state primero, singleton de tests fallback."""
    eng = getattr(request.app.state, "catastro_engine", None)
    if eng is not None:
        return eng
    if _engine_singleton is not None:
        return _engine_singleton
    raise HTTPException(
        status_code=503,
        detail="catastro_routes_engine_not_initialized",
    )


# ============================================================================
# Auth — patrón idéntico a /v1/memento/validate
# ============================================================================


def require_catastro_admin_key(request: Request) -> None:
    """
    Valida el header X-API-Key (o Authorization: Bearer) contra
    MONSTRUO_API_KEY (lectura fresh, anti-Dory).

    Raises:
        HTTPException(503): MONSTRUO_API_KEY no configurada.
        HTTPException(401): falta o inválido.
    """
    admin_key = os.environ.get("MONSTRUO_API_KEY", "")
    if not admin_key:
        raise HTTPException(
            status_code=503,
            detail="catastro_api_key_no_configurada",
        )
    provided = request.headers.get("X-API-Key", "") or request.headers.get(
        "Authorization", ""
    ).replace("Bearer ", "").strip()
    if not provided:
        raise HTTPException(
            status_code=401,
            detail="catastro_api_key_missing",
        )
    if provided != admin_key:
        raise HTTPException(
            status_code=401,
            detail="catastro_api_key_invalid",
        )


# ============================================================================
# Schemas de request
# ============================================================================


class RecommendRequest(BaseModel):
    """Cuerpo de POST /v1/catastro/recommend."""

    use_case: str = Field(..., min_length=1, description="Descripción libre del caso de uso")
    dominio: Optional[str] = Field(None, description="Filtro por dominio del Catastro")
    macroarea: Optional[str] = Field(None, description="Filtro por macroárea (Inteligencia/Visión/Agentes)")
    top_n: int = Field(DEFAULT_TOP_N, ge=1, le=MAX_TOP_N)
    estado: str = Field("production", description="Estado del modelo (default 'production')")
    only_quorum: bool = Field(False, description="Si True, solo modelos con quorum_alcanzado")


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    summary="Top N modelos recomendados para un caso de uso",
)
async def recommend(request: Request, body: RecommendRequest) -> RecommendationResponse:
    """
    Devuelve los Top N modelos del Catastro ordenados por trono_global desc,
    filtrados opcionalmente por dominio/macroárea. Auth obligatoria.
    """
    require_catastro_admin_key(request)
    engine = _get_engine(request)
    try:
        resp = engine.recommend(
            use_case=body.use_case,
            dominio=body.dominio,
            macroarea=body.macroarea,
            top_n=body.top_n,
            estado=body.estado,
            only_quorum=body.only_quorum,
        )
    except CatastroRecommendInvalidArgs as exc:
        raise HTTPException(status_code=400, detail=exc.code) from exc
    except Exception as exc:
        logger.warning("catastro_recommend_error", error=str(exc))
        raise HTTPException(
            status_code=500,
            detail="catastro_recommend_unexpected_error",
        ) from exc
    if resp.degraded:
        logger.info(
            "catastro_recommend_degraded",
            reason=resp.degraded_reason,
            use_case=body.use_case[:60],
        )
    return resp


@router.get(
    "/modelos/{modelo_id}",
    response_model=ModeloDetallado,
    summary="Ficha detallada de un modelo del Catastro",
)
async def get_modelo(
    request: Request,
    modelo_id: str = Path(..., min_length=2, description="Identificador canónico del modelo"),
) -> ModeloDetallado:
    """
    Devuelve la ficha completa del modelo (incluye subcapacidades, sovereignty,
    velocity, estado). Auth obligatoria.
    """
    require_catastro_admin_key(request)
    engine = _get_engine(request)
    try:
        modelo = engine.get_modelo(modelo_id)
    except CatastroRecommendInvalidArgs as exc:
        raise HTTPException(status_code=400, detail=exc.code) from exc
    if modelo is None:
        raise HTTPException(
            status_code=404,
            detail="catastro_recommend_modelo_not_found",
        )
    return modelo


@router.get(
    "/dominios",
    response_model=ListDominiosResponse,
    summary="Lista de macroáreas y dominios del Catastro con conteos",
)
async def list_dominios(request: Request) -> ListDominiosResponse:
    """Lista todos los dominios agrupados por macroárea. Auth obligatoria."""
    require_catastro_admin_key(request)
    engine = _get_engine(request)
    return engine.list_dominios()


@router.get(
    "/status",
    response_model=StatusSnapshot,
    summary="Snapshot de salud del Catastro",
)
async def status_endpoint(request: Request) -> StatusSnapshot:
    """
    Snapshot operativo: trust_level, last_update, modelos_count, dominios_count,
    macroareas, cache_entries, degraded flag. Auth obligatoria.
    """
    require_catastro_admin_key(request)
    engine = _get_engine(request)
    return engine.status()
