"""
El Monstruo — Deployments Routes (Sprint 85)
================================================
REST API para consultar deploys generados por el ciclo
Product Architect → Executor → Critic Visual.

Endpoints:
    GET  /v1/deployments              → Lista deploys (filtros + paginación)
    GET  /v1/deployments/{id}         → Detalle de un deploy específico
    POST /v1/deployments              → Crear deploy (consumido por Executor)
    PATCH /v1/deployments/{id}        → Actualizar score, status o veredicto
    GET  /v1/deployments/stats        → Estadísticas agregadas (Command Center)

Patrón de credenciales: lectura via os.environ.get(...) en cada uso del cliente
Supabase. Cumple decisión de Cowork de no cachear credenciales al boot — las
keys rotadas por el Hilo Credenciales se aplican sin reinicio.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = structlog.get_logger("deployments_routes")
router = APIRouter(prefix="/v1/deployments", tags=["deployments"])

# ── Module-level dependency (injected at startup) ─────────────────
_db = None  # SupabaseClient instance from kernel/main.py lifespan


def set_dependencies(db=None):
    """Inject Supabase client from lifespan."""
    global _db
    _db = db


def _db_available() -> bool:
    """Verificación defensiva del cliente DB."""
    return _db is not None and getattr(_db, "_connected", False)


# ── Schemas ────────────────────────────────────────────────────────
class DeploymentCreate(BaseModel):
    """Payload para crear un deploy nuevo (lo emite el Executor)."""

    project_name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1)
    deploy_type: str = Field(
        ...,
        pattern=r"^(github_pages|railway|vercel|cloudflare_pages|manual)$",
    )
    brief_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DeploymentUpdate(BaseModel):
    """Payload para actualizar un deploy (lo emite Critic Visual o el usuario)."""

    critic_score: Optional[int] = Field(None, ge=0, le=100)
    quality_passed: Optional[bool] = None
    retry_count: Optional[int] = Field(None, ge=0)
    screenshot_url: Optional[str] = None
    screenshot_mobile_url: Optional[str] = None
    critic_findings: Optional[list[dict[str, Any]]] = None
    critic_breakdown: Optional[dict[str, Any]] = None
    status: Optional[str] = Field(
        None,
        pattern=r"^(building|active|rejected_by_critic|failed|archived)$",
    )
    user_verdict: Optional[str] = Field(
        None,
        pattern=r"^(commercializable|not_commercializable)$",
    )


class DeploymentResponse(BaseModel):
    """Respuesta serializada de un deployment."""

    id: str
    project_name: str
    url: str
    deploy_type: str
    brief_id: Optional[str] = None
    critic_score: Optional[int] = None
    quality_passed: bool = False
    retry_count: int = 0
    screenshot_url: Optional[str] = None
    screenshot_mobile_url: Optional[str] = None
    critic_findings: list[dict[str, Any]] = Field(default_factory=list)
    critic_breakdown: dict[str, Any] = Field(default_factory=dict)
    status: str
    user_verdict: Optional[str] = None
    user_verdict_at: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


# ── Endpoints ──────────────────────────────────────────────────────
@router.get("", summary="Listar deploys", response_model=list[DeploymentResponse])
async def list_deployments(
    project_name: Optional[str] = Query(None, description="Filtrar por nombre de proyecto"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    quality_passed: Optional[bool] = Query(None, description="Filtrar por quality_passed"),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Score mínimo"),
    limit: int = Query(50, ge=1, le=500, description="Cantidad máxima de resultados"),
    offset: int = Query(0, ge=0, description="Offset de paginación"),
):
    """
    Lista deploys con filtros opcionales.

    Por defecto retorna los 50 más recientes. El Command Center usa este
    endpoint para mostrar la cola de proyectos generados.
    """
    if not _db_available():
        logger.warning("deployments_db_unavailable")
        raise HTTPException(status_code=503, detail="deployments_store_unavailable")

    filters: dict[str, Any] = {}
    if project_name:
        filters["project_name"] = project_name
    if status:
        filters["status"] = status
    if quality_passed is not None:
        filters["quality_passed"] = quality_passed

    try:
        rows = await _db.select(
            "deployments",
            filters=filters,
            order_by="created_at",
            order_desc=True,
            limit=limit,
            offset=offset,
        )
    except Exception as exc:
        logger.error("deployments_list_failed", error=str(exc))
        raise HTTPException(status_code=500, detail="deployments_list_failed") from exc

    if min_score is not None:
        rows = [r for r in rows if (r.get("critic_score") or 0) >= min_score]

    return [_row_to_response(r) for r in rows]


@router.get("/stats", summary="Estadísticas agregadas")
async def deployments_stats():
    """
    Métricas agregadas para el Command Center.

    Retorna:
        - total: total de deploys registrados
        - by_status: conteo por status
        - by_quality: conteo por quality_passed (true/false/null)
        - avg_critic_score: promedio del score del Critic
        - last_24h: deploys creados en las últimas 24h
    """
    if not _db_available():
        raise HTTPException(status_code=503, detail="deployments_store_unavailable")

    try:
        rows = await _db.select("deployments", limit=10_000)
    except Exception as exc:
        logger.error("deployments_stats_failed", error=str(exc))
        raise HTTPException(status_code=500, detail="deployments_stats_failed") from exc

    total = len(rows)
    by_status: dict[str, int] = {}
    by_quality = {"passed": 0, "failed": 0, "pending": 0}
    score_sum = 0
    score_n = 0
    last_24h_cutoff = datetime.now(timezone.utc).timestamp() - 86400
    last_24h = 0

    for r in rows:
        status = r.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1

        if r.get("quality_passed") is True:
            by_quality["passed"] += 1
        elif r.get("quality_passed") is False and r.get("critic_score") is not None:
            by_quality["failed"] += 1
        else:
            by_quality["pending"] += 1

        score = r.get("critic_score")
        if score is not None:
            score_sum += score
            score_n += 1

        created_at = r.get("created_at")
        if created_at:
            try:
                ts = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
                if ts >= last_24h_cutoff:
                    last_24h += 1
            except (ValueError, AttributeError):
                pass

    return {
        "total": total,
        "by_status": by_status,
        "by_quality": by_quality,
        "avg_critic_score": round(score_sum / score_n, 2) if score_n else None,
        "last_24h": last_24h,
    }


@router.get("/{deployment_id}", summary="Detalle de un deploy", response_model=DeploymentResponse)
async def get_deployment(deployment_id: str):
    """Retorna un deploy específico por ID."""
    if not _db_available():
        raise HTTPException(status_code=503, detail="deployments_store_unavailable")

    try:
        rows = await _db.select("deployments", filters={"id": deployment_id}, limit=1)
    except Exception as exc:
        logger.error("deployments_get_failed", error=str(exc), deployment_id=deployment_id)
        raise HTTPException(status_code=500, detail="deployments_get_failed") from exc

    if not rows:
        raise HTTPException(status_code=404, detail="deployment_not_found")

    return _row_to_response(rows[0])


@router.post("", summary="Crear deploy", response_model=DeploymentResponse, status_code=201)
async def create_deployment(payload: DeploymentCreate):
    """
    Registra un nuevo deploy. Llamado por el Executor cuando termina un build.

    El score y los findings los completa el Critic Visual via PATCH después.
    """
    if not _db_available():
        raise HTTPException(status_code=503, detail="deployments_store_unavailable")

    row = {
        "project_name": payload.project_name,
        "url": payload.url,
        "deploy_type": payload.deploy_type,
        "brief_id": payload.brief_id,
        "metadata": payload.metadata,
        "status": "building",
    }

    try:
        created = await _db.insert("deployments", row)
    except Exception as exc:
        logger.error("deployments_create_failed", error=str(exc), project=payload.project_name)
        raise HTTPException(status_code=500, detail="deployments_create_failed") from exc

    if not created:
        raise HTTPException(status_code=500, detail="deployments_create_no_data")

    logger.info(
        "deployment_created",
        deployment_id=created.get("id"),
        project_name=payload.project_name,
        deploy_type=payload.deploy_type,
    )
    return _row_to_response(created)


@router.patch("/{deployment_id}", summary="Actualizar deploy", response_model=DeploymentResponse)
async def update_deployment(deployment_id: str, payload: DeploymentUpdate):
    """
    Actualiza un deploy. Usado por:
      - Critic Visual: para registrar score, findings y breakdown
      - Usuario (Test 3): para emitir veredicto comercializable / no
    """
    if not _db_available():
        raise HTTPException(status_code=503, detail="deployments_store_unavailable")

    update_data: dict[str, Any] = {}
    for field, value in payload.model_dump(exclude_none=True).items():
        update_data[field] = value

    if "user_verdict" in update_data:
        update_data["user_verdict_at"] = datetime.now(timezone.utc).isoformat()

    if not update_data:
        raise HTTPException(status_code=400, detail="no_fields_to_update")

    try:
        updated = await _db.update(
            "deployments",
            data=update_data,
            filters={"id": deployment_id},
        )
    except Exception as exc:
        logger.error("deployments_update_failed", error=str(exc), deployment_id=deployment_id)
        raise HTTPException(status_code=500, detail="deployments_update_failed") from exc

    if not updated:
        raise HTTPException(status_code=404, detail="deployment_not_found")

    logger.info(
        "deployment_updated",
        deployment_id=deployment_id,
        fields=list(update_data.keys()),
    )

    # Recargar para retornar el estado completo
    rows = await _db.select("deployments", filters={"id": deployment_id}, limit=1)
    return _row_to_response(rows[0]) if rows else updated


# ── Helpers ────────────────────────────────────────────────────────
def _row_to_response(row: dict[str, Any]) -> DeploymentResponse:
    """Normaliza una fila de DB al schema de respuesta."""
    return DeploymentResponse(
        id=str(row.get("id", "")),
        project_name=row.get("project_name", ""),
        url=row.get("url", ""),
        deploy_type=row.get("deploy_type", ""),
        brief_id=str(row["brief_id"]) if row.get("brief_id") else None,
        critic_score=row.get("critic_score"),
        quality_passed=bool(row.get("quality_passed", False)),
        retry_count=int(row.get("retry_count", 0)),
        screenshot_url=row.get("screenshot_url"),
        screenshot_mobile_url=row.get("screenshot_mobile_url"),
        critic_findings=row.get("critic_findings") or [],
        critic_breakdown=row.get("critic_breakdown") or {},
        status=row.get("status", "unknown"),
        user_verdict=row.get("user_verdict"),
        user_verdict_at=row.get("user_verdict_at"),
        metadata=row.get("metadata") or {},
        created_at=str(row.get("created_at", "")),
        updated_at=str(row.get("updated_at", "")),
    )
