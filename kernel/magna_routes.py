"""
El Monstruo — Magna Classifier Routes (Sprint 51, Capa 0.2)
============================================================
Endpoints REST para el Magna Classifier, consumibles desde el Command Center.

Endpoints:
    POST /v1/magna/classify  → Clasificar un texto y obtener ruta recomendada
    GET  /v1/magna/stats     → Estadísticas del clasificador
    POST /v1/magna/cleanup   → Limpiar cache expirado

Patrón: Router modular con dependencia inyectada en startup.
Referencia: kernel/embrion_routes.py, kernel/finops_routes.py
"""

from __future__ import annotations

from typing import Optional

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = structlog.get_logger("magna_routes")

router = APIRouter(prefix="/v1/magna", tags=["magna"])

# ── Module-level dependency (injected at startup) ───────────────────
_classifier = None  # MagnaClassifier


def set_dependencies(classifier=None):
    """Inject MagnaClassifier from lifespan.

    Called from kernel/main.py during startup bootstrap.
    """
    global _classifier
    _classifier = classifier


def _ensure_classifier():
    """Validate that the classifier is available."""
    if _classifier is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "magna_classifier_no_disponible",
                "causa": "El clasificador no fue inicializado en el bootstrap del kernel",
                "sugerencia": "Verificar que MagnaClassifier se instancia en main.py lifespan",
            },
        )
    return _classifier


# ── Request/Response Models ─────────────────────────────────────────

class ClassifyRequest(BaseModel):
    """Payload para clasificar un texto."""
    text: str = Field(..., min_length=1, max_length=10000, description="Texto a clasificar")
    context: Optional[dict] = Field(default=None, description="Contexto adicional (trigger_type, cycle, etc.)")


class ClassifyResponse(BaseModel):
    """Resultado de clasificación."""
    route: str = Field(..., description="Ruta recomendada: graph | router | tool_specific")
    score: float = Field(..., description="Confianza de la clasificación (0.0 a 1.0)")
    category: str = Field(..., description="Categoría: tech | action | reflection | query_realtime | unknown")
    suggested_tool: Optional[str] = Field(None, description="Tool específica si route == tool_specific")
    reasoning: str = Field("", description="Explicación de la decisión")
    cached: bool = Field(False, description="Si el resultado vino del cache")


# ── Endpoints ───────────────────────────────────────────────────────

@router.post("/classify", response_model=ClassifyResponse)
async def classify_text(request: ClassifyRequest):
    """Clasificar un texto y obtener la ruta recomendada.

    El clasificador analiza el contenido y decide si el Embrión
    debería usar el grafo completo (con tools) o el router barato.

    Returns:
        ClassifyResponse con route, score, category, suggested_tool.
    """
    classifier = _ensure_classifier()

    try:
        result = classifier.classify(
            text=request.text,
            context=request.context,
        )

        # Persistir en cache DB (async, no bloquea respuesta)
        cache_key = classifier._make_cache_key(request.text.lower().strip())
        await classifier.store_cache_db(cache_key, result, request.text)

        logger.info(
            "magna_route_decided",
            route=result.route.value,
            score=result.score,
            category=result.category.value,
            tool=result.suggested_tool,
        )

        return ClassifyResponse(
            route=result.route.value,
            score=result.score,
            category=result.category.value,
            suggested_tool=result.suggested_tool,
            reasoning=result.reasoning,
            cached=result.cached,
        )

    except Exception as e:
        logger.error("magna_classify_endpoint_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "magna_clasificacion_fallida",
                "causa": str(e),
                "sugerencia": "Verificar input y reintentar",
            },
        )


@router.get("/stats")
async def get_stats():
    """Estadísticas del clasificador para el Command Center.

    Returns:
        Dict con contadores, tasas de cache, estado del cap diario.
    """
    classifier = _ensure_classifier()

    return {
        "status": "active",
        "module": "magna_classifier",
        "sprint": "51",
        **classifier.get_stats(),
    }


@router.post("/cleanup")
async def cleanup_cache():
    """Limpiar entradas expiradas del cache.

    Útil para mantenimiento manual o cron job.

    Returns:
        Dict con número de entradas limpiadas.
    """
    classifier = _ensure_classifier()

    try:
        cleaned = await classifier.cleanup_expired_cache()
        return {
            "status": "ok",
            "expired_entries_cleaned": cleaned,
        }
    except Exception as e:
        logger.error("magna_cleanup_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "magna_cache_limpieza_fallida",
                "causa": str(e),
            },
        )
