"""
Cowork Routes — Sprint COWORK-RUNTIME-001 Tarea 8 (PREMIUM 2)
==============================================================

Router FastAPI que expone el endpoint POST /v1/cowork/memento/validate.

M8 (auditoria): "endpoint POST /v1/cowork/memento/validate que cualquier hilo
Manus puede llamar para verificar que Cowork esta operando con contexto fresco
antes de aceptar specs de Cowork. Mismo patron que /v1/memento/validate pero
specifico a Cowork. Resultado: Manus puede rechazar specs de Cowork que no
tengan firma de Pre-flight ejecutado."

Decisiones de diseño:
  1. Auth identico a /v1/memento/validate: header X-API-Key validado contra
     MONSTRUO_API_KEY (lectura fresh, no se cachea — disciplina anti-Dory).
  2. La logica de validacion vive en kernel/cowork_runtime/session_memory.py
     (read_recent + Pre-flight Memento check). El endpoint solo orquesta.
  3. Respuesta binaria + structured: cowork_fresco / razon / metricas /
     ultima_sesion. Si cowork_fresco=False, el llamador (Manus) DEBE rechazar
     specs de Cowork hasta que vuelva a estar fresco.
  4. Drift detector T7 invocado para evaluar salud actual; resultado embedded
     en respuesta (action recomendada).
  5. Sin rate limiting en v1.0 (mismo patron que memento).
  6. APIRouter independiente, registrado en main.py via:
       from kernel.cowork_routes import cowork_router
       app.include_router(cowork_router, prefix="/v1/cowork")

Refs:
  - M8 de AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md
  - kernel/memento_routes.py (patron clonado)
  - kernel/cowork_runtime/session_memory.py (T3)
  - kernel/cowork_runtime/drift_detector.py (T7)
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from kernel.cowork_runtime.session_memory import SessionMemoryStore
from kernel.cowork_runtime.drift_detector import (
    DriftDetector,
    DriftAction,
    SessionDriftState,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# Auth helper (reusa MONSTRUO_API_KEY, mismo patron que memento)
# =============================================================================

def require_cowork_admin_key(request: Request) -> None:
    """
    Valida X-API-Key contra MONSTRUO_API_KEY (fresh).

    Raises:
        HTTPException(503): si MONSTRUO_API_KEY no esta configurada
        HTTPException(401): si key falta o no matchea
    """
    expected = os.environ.get("MONSTRUO_API_KEY")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MONSTRUO_API_KEY not configured",
        )
    provided = request.headers.get("X-API-Key")
    if not provided:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )
    if provided != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-API-Key",
        )


# =============================================================================
# Modelos Pydantic
# =============================================================================

class CoworkValidateRequest(BaseModel):
    """Request body para POST /v1/cowork/memento/validate."""
    hilo_solicitante: str = Field(
        ...,
        description="Identificador del hilo Manus que valida (ej: 'hilo_ejecutor_t1').",
    )
    razon: Optional[str] = Field(
        None,
        description="Razon de la validacion (ej: 'Antes de aceptar spec X de Cowork').",
        max_length=500,
    )


class CoworkValidateResponse(BaseModel):
    """Respuesta del endpoint."""
    cowork_fresco: bool = Field(..., description="Si Cowork esta operando con contexto fresco.")
    razon: str = Field(..., description="Explicacion humano-leible.")
    drift_action: str = Field(..., description="Accion recomendada: no_op|reinject|force_preflight|hard_halt.")
    drift_severidad: int = Field(..., ge=0, le=3, description="0=info,1=warn,2=error,3=halt.")
    metricas: dict = Field(default_factory=dict, description="Metricas de la ultima sesion.")
    ultima_sesion: Optional[dict] = Field(None, description="Snapshot de la ultima sesion Cowork.")
    validado_en: str = Field(..., description="Timestamp ISO de la validacion.")


# =============================================================================
# Router
# =============================================================================

cowork_router = APIRouter(tags=["cowork"])


@cowork_router.post(
    "/memento/validate",
    response_model=CoworkValidateResponse,
    summary="Validar que Cowork opera con contexto fresco antes de aceptar specs",
)
async def validate_cowork_memento(
    payload: CoworkValidateRequest,
    request: Request,
) -> CoworkValidateResponse:
    """
    Hilos Manus llaman este endpoint antes de aceptar specs de Cowork.

    Returns:
        cowork_fresco=True: ultima sesion Cowork tiene Pre-flight ejecutado y
        no hay drift severo. Manus puede aceptar el spec.

        cowork_fresco=False: Cowork no esta fresco (no Pre-flight, drift severo,
        muchas violaciones). Manus DEBE rechazar el spec hasta que Cowork
        re-valide.
    """
    require_cowork_admin_key(request)

    store = SessionMemoryStore()
    sesiones = store.read_recent(limit=10)

    if not sesiones:
        logger.warning("cowork_validate_no_sessions", hilo=payload.hilo_solicitante)
        return CoworkValidateResponse(
            cowork_fresco=False,
            razon="No hay sesiones Cowork registradas. Cowork debe iniciar sesion con Pre-flight Memento.",
            drift_action=DriftAction.FORCE_PREFLIGHT.value,
            drift_severidad=2,
            metricas={"sesiones_totales": 0},
            ultima_sesion=None,
            validado_en=datetime.now(timezone.utc).isoformat(),
        )

    ultima = sesiones[0]
    pre_flight_ok = bool(ultima.get("pre_flight_ejecutado"))
    violaciones = ultima.get("violaciones_detectadas") or []
    if isinstance(violaciones, str):
        try:
            import json
            violaciones = json.loads(violaciones)
        except Exception:
            violaciones = []
    n_violaciones = len(violaciones) if isinstance(violaciones, list) else 0

    # Drift detector con enabled=True forzado (este endpoint es el llamado explicito)
    detector = DriftDetector(enabled=True)
    state = SessionDriftState(
        turnos=int(ultima.get("turnos_totales") or 0),
        pre_flight_ejecutado=pre_flight_ok,
        violaciones_acumuladas=n_violaciones,
    )
    signal = detector.evaluate(state)

    # Determinar fresco binario
    cowork_fresco = (
        pre_flight_ok
        and signal.action in (DriftAction.NO_OP,)
        and n_violaciones < 3
    )

    razon_partes = []
    if pre_flight_ok:
        razon_partes.append("Pre-flight Memento ejecutado")
    else:
        razon_partes.append("Pre-flight Memento NO ejecutado")
    razon_partes.append(f"violaciones_acumuladas={n_violaciones}")
    razon_partes.append(f"drift_action={signal.action.value}")

    metricas = {
        "sesion_id": ultima.get("id"),
        "fecha_inicio": ultima.get("fecha_inicio"),
        "turnos_totales": ultima.get("turnos_totales") or 0,
        "commits_productivos": ultima.get("commits_productivos") or 0,
        "violaciones_acumuladas": n_violaciones,
        "pre_flight_ejecutado": pre_flight_ok,
        "sprint_activo": ultima.get("sprint_activo"),
        "kernel_version": ultima.get("kernel_version"),
        "embrion_ultimo_latido": ultima.get("embrion_ultimo_latido"),
        "drift_severidad": signal.severidad,
    }

    # Ultima sesion: dict slim para no enviar todo el payload
    ultima_slim = {
        k: ultima.get(k) for k in (
            "id", "fecha_inicio", "fecha_fin", "duracion_minutos",
            "sprint_activo", "pre_flight_ejecutado", "commits_productivos",
            "turnos_totales", "kernel_version", "embrion_ultimo_latido",
        )
    }

    logger.info(
        "cowork_validate_done",
        hilo=payload.hilo_solicitante,
        cowork_fresco=cowork_fresco,
        razon=" · ".join(razon_partes),
        drift_action=signal.action.value,
    )

    return CoworkValidateResponse(
        cowork_fresco=cowork_fresco,
        razon=" · ".join(razon_partes),
        drift_action=signal.action.value,
        drift_severidad=signal.severidad,
        metricas=metricas,
        ultima_sesion=ultima_slim,
        validado_en=datetime.now(timezone.utc).isoformat(),
    )


@cowork_router.get(
    "/health",
    summary="Healthcheck del subsistema cowork-runtime",
)
async def cowork_health() -> dict:
    """Healthcheck publico (sin auth) del subsistema cowork-runtime."""
    return {
        "status": "ok",
        "modulo": "cowork-runtime",
        "version": "1.0.0",
        "endpoints": [
            "POST /v1/cowork/memento/validate (auth)",
            "GET  /v1/cowork/health",
        ],
    }
