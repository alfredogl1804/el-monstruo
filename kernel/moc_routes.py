"""
El Monstruo — MOC Routes (Sprint 36)
=====================================
Endpoints de observabilidad y control del Motor de Orquestación Central.

Endpoints:
    GET  /v1/moc/status          → Estado del MOC (stats, último insight)
    GET  /v1/moc/insights        → Lista de insights recientes
    POST /v1/moc/sintetizar      → Trigger manual de síntesis
    POST /v1/moc/priorizar       → Priorizar lista de jobs manualmente
"""

from __future__ import annotations

from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = structlog.get_logger("kernel.moc_routes")

router = APIRouter(prefix="/v1/moc", tags=["moc"])

# ── Dependency injection ─────────────────────────────────────────────

_moc: Optional[Any] = None


def set_dependencies(moc: Any) -> None:
    global _moc
    _moc = moc


def _ensure_moc():
    if not _moc:
        raise HTTPException(status_code=503, detail="MOC not initialized")
    return _moc


# ── Models ───────────────────────────────────────────────────────────


class SintetizarRequest(BaseModel):
    window_hours: int = Field(default=24, ge=1, le=168, description="Ventana de análisis en horas")
    user_id: str = Field(default="anonymous")


class PriorizarRequest(BaseModel):
    jobs: list[dict[str, Any]] = Field(..., description="Lista de jobs a priorizar")
    gasto_hoy_usd: float = Field(default=0.0, ge=0.0)


# ── Endpoints ────────────────────────────────────────────────────────


@router.get("/status")
async def moc_status(request: Request):
    """Estado del MOC: stats, último insight generado."""
    moc = _ensure_moc()
    return JSONResponse({"status": "active", "stats": moc.stats})


@router.get("/insights")
async def moc_insights(request: Request, limit: int = 10):
    """Lista de insights recientes generados por el Sintetizador."""
    moc = _ensure_moc()
    try:
        db = moc._db
        if not db or not db.connected:
            return JSONResponse({"insights": [], "message": "DB not connected"})

        rows = await db.select(
            "moc_insights",
            order_by="created_at",
            order_desc=True,
            limit=min(limit, 50),
        )
        return JSONResponse({"insights": rows, "total": len(rows)})
    except Exception as e:
        logger.error("moc_insights_endpoint_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sintetizar")
async def moc_sintetizar(request: Request, body: SintetizarRequest):
    """Trigger manual de síntesis de ciclos."""
    moc = _ensure_moc()
    try:
        insight = await moc.sintetizar_ciclos(
            window_hours=body.window_hours,
            user_id=body.user_id,
        )
        return JSONResponse({"status": "ok", "insight": insight})
    except Exception as e:
        logger.error("moc_sintetizar_endpoint_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/priorizar")
async def moc_priorizar(request: Request, body: PriorizarRequest):
    """Prioriza una lista de jobs y retorna el orden sugerido."""
    moc = _ensure_moc()
    try:
        priorizados = await moc.priorizar_jobs(body.jobs)
        return JSONResponse({"status": "ok", "jobs": priorizados})
    except Exception as e:
        logger.error("moc_priorizar_endpoint_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ── Sprint 39: Cache stats endpoint ──────────────────────────────────────────

@router.get("/v1/cache/stats")
async def get_cache_stats(request: Request):
    """Estadísticas del response cache y dossier cache (Sprint 39)."""
    _require_api_key(request)
    from kernel import response_cache, dossier_cache
    return {
        "response_cache": response_cache.stats(),
        "dossier_cache": dossier_cache.stats(),
    }


@router.delete("/v1/cache")
async def clear_cache(request: Request, intent: str = None):
    """Invalida el response cache. Útil tras cambios de prompt."""
    _require_api_key(request)
    from kernel import response_cache, dossier_cache
    rc_cleared = response_cache.invalidate(intent)
    dc_cleared = dossier_cache.invalidate()
    return {
        "response_cache_cleared": rc_cleared,
        "dossier_cache_cleared": dc_cleared,
    }
