"""
Memento Routes — Sprint Memento Bloque 3 (Capa Memoria Soberana v1.0)
=====================================================================

Router FastAPI que expone el endpoint POST /v1/memento/validate.

Diseño y decisiones (alineadas con spec_sprint_memento.md y green light Cowork):

1.  Auth idéntico al patrón existente (/v1/error-memory/seed, /v1/browser/*):
    header X-API-Key validado contra os.environ["MONSTRUO_API_KEY"] leído
    FRESH en cada request (no se cachea al boot — disciplina anti-Dory).
    El helper se exporta como `require_memento_admin_key` para reuso.

2.  El validador (MementoValidator) se instancia UNA vez al startup en el
    lifespan del kernel y se expone via `app.state.memento_validator`.
    El SourceCache vive en esa instancia, así los hits entre requests
    se aprovechan correctamente.

3.  Persistencia no-bloqueante: si Supabase falla al insertar, loggeamos
    `memento_persistence_failed` pero NO hacemos fail al cliente. La
    validación ya ocurrió y es lo importante; el log es secundario
    (Capa 7: Resiliencia Agéntica). La respuesta lleva el flag
    `persistence_failed=true` para que el llamador lo sepa.

4.  Logging estructurado con `structlog` (mismo patrón que el resto del
    kernel) en cada paso del pipeline.

5.  Rate limiting NO se implementa en v1.0 (lo dijo Cowork explícitamente).

6.  El endpoint es un APIRouter independiente, registrado en main.py via
    `app.include_router(memento_router, prefix="/v1/memento")`.

Refs:
    - bridge/sprint_memento_preinvestigation/spec_sprint_memento.md
    - kernel/memento/validator.py (lógica)
    - scripts/017_sprint_memento_schema.sql (tabla memento_validations)
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import structlog
from fastapi import APIRouter, HTTPException, Request, status

from kernel.memento.models import MementoValidationRequest, ValidationResult
from kernel.memento.validator import MementoValidator

logger = structlog.get_logger(__name__)

# Tabla en Supabase (espejo del bootstrap del Bloque 1, migration 017).
MEMENTO_VALIDATIONS_TABLE = "memento_validations"


# ===========================================================================
# Auth helper (reusable + testeable)
# ===========================================================================

def require_memento_admin_key(request: Request) -> None:
    """
    Valida el header X-API-Key contra MONSTRUO_API_KEY (lectura fresh).

    Raises:
        HTTPException(503): si MONSTRUO_API_KEY no está configurada en el env.
        HTTPException(401): si el header es válido pero la key no matchea
            (alineado con el patrón existente en error_memory_seed; aunque
            semánticamente sería 403, mantenemos consistencia con el resto
            del kernel).
        HTTPException(401): si falta el header.
    """
    admin_key = os.environ.get("MONSTRUO_API_KEY", "")
    if not admin_key:
        raise HTTPException(
            status_code=503,
            detail="memento_api_key_no_configurada",
        )
    provided = request.headers.get("X-API-Key", "") or request.headers.get(
        "Authorization", ""
    ).replace("Bearer ", "").strip()
    if not provided:
        raise HTTPException(
            status_code=401,
            detail="memento_api_key_missing",
        )
    if provided != admin_key:
        raise HTTPException(
            status_code=401,
            detail="memento_api_key_invalid",
        )


# ===========================================================================
# Persistencia (no-bloqueante)
# ===========================================================================

async def _persist_validation(
    *,
    db: Any,
    hilo_id: str,
    operation: str,
    context_used: Dict[str, Any],
    result: ValidationResult,
    intent_summary: Optional[str],
) -> bool:
    """
    Inserta la validación en `memento_validations`.

    Returns:
        True si la inserción fue exitosa, False si falló (no propaga excepción).
    """
    if db is None:
        logger.warning(
            "memento_persistence_skipped",
            reason="db_not_available",
            validation_id=result.validation_id,
        )
        return False

    try:
        row = {
            "validation_id": result.validation_id,
            "hilo_id": hilo_id,
            "operation": operation,
            "context_used": context_used,
            "intent_summary": intent_summary,
            "validation_status": result.validation_status.value,
            "discrepancy": result.discrepancy.model_dump(mode="json") if result.discrepancy else None,
            "proceed": result.proceed,
            "context_freshness_seconds": result.context_freshness_seconds,
            "remediation": result.remediation,
            "source_consulted": result.source_consulted,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        await db.insert(MEMENTO_VALIDATIONS_TABLE, data=row)
        return True
    except Exception as exc:
        logger.warning(
            "memento_persistence_failed",
            error=str(exc),
            validation_id=result.validation_id,
            hilo_id=hilo_id,
            operation=operation,
        )
        return False


# ===========================================================================
# Router
# ===========================================================================

memento_router = APIRouter(tags=["memento"])


@memento_router.post(
    "/validate",
    summary="Validar contexto operativo contra fuentes de verdad",
    response_model=None,  # devolvemos un dict plano por compatibilidad con el spec
    status_code=status.HTTP_200_OK,
)
async def memento_validate(request: Request):
    """
    POST /v1/memento/validate

    Body (JSON):
        {
          "hilo_id": "hilo_manus_ticketlike",
          "operation": "sql_against_production",
          "context_used": {
            "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
            "user": "37Hy7adB53QmFW4.root",
            "credential_hash_first_8": "4N6caSwp"
          },
          "intent_summary": "Run E2E test post Stripe rotation"
        }

    Response (JSON, status 200):
        {
          "validation_id": "mv_2026-05-04T22:30:15_a1b2c3",
          "validation_status": "ok" | "discrepancy_detected" | "unknown_operation" | "source_unavailable",
          "proceed": true | false,
          "context_freshness_seconds": 12,
          "discrepancy": null | { ... },
          "remediation": null | "context_stale_or_contaminated: ...",
          "source_consulted": "ticketlike_credentials",
          "persistence_failed": false  // true si Supabase falló (no bloqueante)
        }

    Errors:
        - 401 unauthorized: API key missing or invalid
        - 422 validation error: malformed body (missing hilo_id, operation, context_used)
        - 503 service unavailable: MONSTRUO_API_KEY not configured OR validator not initialized
    """
    require_memento_admin_key(request)

    # Validator singleton (instanciado al startup del kernel)
    validator: Optional[MementoValidator] = getattr(
        request.app.state, "memento_validator", None
    )
    if validator is None:
        raise HTTPException(
            status_code=503,
            detail="memento_validator_not_initialized",
        )

    # Parse + valida body
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="memento_body_not_json",
        )

    try:
        req = MementoValidationRequest(**body)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"memento_body_invalid: {str(exc)[:300]}",
        )

    logger.info(
        "memento_validate_request",
        hilo_id=req.hilo_id,
        operation=req.operation,
        context_keys=list(req.context_used.keys()),
        intent_summary=req.intent_summary,
    )

    # Ejecutar validación
    try:
        result: ValidationResult = await validator.validate(
            operation=req.operation,
            context_used=req.context_used,
            hilo_id=req.hilo_id,
            intent_summary=req.intent_summary,
        )
    except Exception as exc:
        logger.error(
            "memento_validate_failed",
            error=str(exc),
            hilo_id=req.hilo_id,
            operation=req.operation,
        )
        raise HTTPException(
            status_code=500,
            detail=f"memento_validate_internal_error: {str(exc)[:300]}",
        )

    logger.info(
        "memento_validate_result",
        validation_id=result.validation_id,
        validation_status=result.validation_status.value,
        proceed=result.proceed,
        freshness=result.context_freshness_seconds,
        discrepancy_field=(result.discrepancy.field if result.discrepancy else None),
    )

    # Persistencia no-bloqueante
    db = getattr(request.app.state, "db", None)
    persisted = await _persist_validation(
        db=db,
        hilo_id=req.hilo_id,
        operation=req.operation,
        context_used=req.context_used,
        result=result,
        intent_summary=req.intent_summary,
    )

    # Shape de respuesta — espejo del spec
    return {
        "validation_id": result.validation_id,
        "validation_status": result.validation_status.value,
        "proceed": result.proceed,
        "context_freshness_seconds": result.context_freshness_seconds,
        "discrepancy": result.discrepancy.model_dump(mode="json") if result.discrepancy else None,
        "remediation": result.remediation,
        "source_consulted": result.source_consulted,
        "persistence_failed": not persisted,
    }


__all__ = [
    "memento_router",
    "require_memento_admin_key",
    "MEMENTO_VALIDATIONS_TABLE",
]
