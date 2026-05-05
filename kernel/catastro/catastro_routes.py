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

from fastapi.responses import HTMLResponse

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
from kernel.catastro.dashboard import (
    CatastroDashboardInvalidArgs,
    CuradorsResponse,
    DEFAULT_TIMELINE_DAYS,
    DashboardEngine,
    MAX_TIMELINE_DAYS,
    SummarySnapshot as DashboardSummarySnapshot,
    TimelineResponse,
    dashboard_requires_auth,
    render_html_dashboard,
)

logger = structlog.get_logger("kernel.catastro.routes")

router = APIRouter(tags=["catastro"])

# Engine inyectable por tests/lifespan
_engine_singleton: Optional[RecommendationEngine] = None
_dashboard_engine_singleton: Optional[DashboardEngine] = None


def set_dependencies(
    engine: RecommendationEngine,
    dashboard_engine: Optional[DashboardEngine] = None,
) -> None:
    """Inyecta engines. Llamar una sola vez en lifespan.

    Args:
        engine: RecommendationEngine para los endpoints de recomendación.
        dashboard_engine: opcional. Si es None, el dashboard se inicializa
            on-demand con un DashboardEngine sin db (modo degraded).
    """
    global _engine_singleton, _dashboard_engine_singleton
    _engine_singleton = engine
    if dashboard_engine is not None:
        _dashboard_engine_singleton = dashboard_engine


def _get_dashboard_engine(request: Request) -> DashboardEngine:
    """Resuelve el dashboard engine: app.state primero, singleton fallback."""
    eng = getattr(request.app.state, "catastro_dashboard_engine", None)
    if eng is not None:
        return eng
    if _dashboard_engine_singleton is not None:
        return _dashboard_engine_singleton
    # Modo degraded automático: dashboard sin db_factory
    return DashboardEngine(db_factory=None)


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


# ============================================================================
# Dashboard endpoints (Sprint 86 Bloque 7)
#
# Diseño: público read-only POR DEFECTO. Auth obligatoria solo si
# CATASTRO_DASHBOARD_REQUIRE_AUTH=true (lectura fresh, anti-Dory).
# Esto permite a Alfredo + Cowork inspeccionar el sistema sin pasar
# auth en MVP, y endurecer con un env var sin redeploy de código.
# ============================================================================


def _maybe_require_dashboard_auth(request: Request) -> None:
    """Aplica auth solo si CATASTRO_DASHBOARD_REQUIRE_AUTH=true."""
    if dashboard_requires_auth():
        require_catastro_admin_key(request)


@router.get(
    "/dashboard/summary",
    response_model=DashboardSummarySnapshot,
    summary="Snapshot resumido del Catastro (dashboard)",
)
async def dashboard_summary(request: Request) -> DashboardSummarySnapshot:
    """
    Snapshot operativo: trust_level, modelos_total/production, dominios,
    macroareas, last_run, fuentes, drift_detected, cache_entries.
    Auth opcional (default público).
    """
    _maybe_require_dashboard_auth(request)
    engine = _get_dashboard_engine(request)
    try:
        return engine.summary()
    except Exception as exc:
        logger.warning("catastro_dashboard_summary_error", error=str(exc))
        raise HTTPException(
            status_code=500,
            detail="catastro_dashboard_summary_unexpected_error",
        ) from exc


@router.get(
    "/dashboard/timeline",
    response_model=TimelineResponse,
    summary="Histórico últimos N días (default 14)",
)
async def dashboard_timeline(
    request: Request,
    days: int = Query(
        DEFAULT_TIMELINE_DAYS,
        ge=1,
        le=MAX_TIMELINE_DAYS,
        description=f"Días a mostrar (1-{MAX_TIMELINE_DAYS})",
    ),
) -> TimelineResponse:
    """
    Timeline de runs/eventos/drift por día. failure_rate por día +
    avg_failure_rate del rango. Auth opcional.
    """
    _maybe_require_dashboard_auth(request)
    engine = _get_dashboard_engine(request)
    try:
        return engine.timeline(days=days)
    except CatastroDashboardInvalidArgs as exc:
        raise HTTPException(status_code=400, detail=exc.code) from exc
    except Exception as exc:
        logger.warning("catastro_dashboard_timeline_error", error=str(exc))
        raise HTTPException(
            status_code=500,
            detail="catastro_dashboard_timeline_unexpected_error",
        ) from exc


@router.get(
    "/dashboard/curators",
    response_model=CuradorsResponse,
    summary="Trust scores + tendencia de los curadores",
)
async def dashboard_curators(request: Request) -> CuradorsResponse:
    """Lista curadores con trust_score actual, delta 7d, invocaciones."""
    _maybe_require_dashboard_auth(request)
    engine = _get_dashboard_engine(request)
    try:
        return engine.curators()
    except Exception as exc:
        logger.warning("catastro_dashboard_curators_error", error=str(exc))
        raise HTTPException(
            status_code=500,
            detail="catastro_dashboard_curators_unexpected_error",
        ) from exc


@router.get(
    "/dashboard/",
    response_class=HTMLResponse,
    summary="HTML render del dashboard de salud",
    include_in_schema=False,  # No contamina /docs OpenAPI
)
async def dashboard_html(request: Request) -> HTMLResponse:
    """
    Render HTML vanilla del dashboard. Consume los 3 JSON via fetch+Chart.js.
    Auth obligatoria si CATASTRO_DASHBOARD_REQUIRE_AUTH=true.
    """
    _maybe_require_dashboard_auth(request)
    return HTMLResponse(content=render_html_dashboard(), status_code=200)
