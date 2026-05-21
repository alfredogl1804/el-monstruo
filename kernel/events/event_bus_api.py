"""
El Monstruo — Event Bus API
============================
Endpoints para emitir, consultar y cristalizar eventos del stream inmutable.

Principio: La Operación ES el Registro.
El Event Bus es el fundamento del Reactor de Coherencia.

Endpoints:
    POST /events/emit              → Emitir un evento al stream
    POST /events/crystallize       → Cristalizar eventos pendientes al SMS
    GET  /events/stream            → Consultar el stream con filtros
    GET  /events/stats             → Estadísticas del stream

Auth: SMS_API_KEY (Bearer o X-Api-Key header)
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field

logger = structlog.get_logger("monstruo.event_bus")

router = APIRouter(prefix="/v1/events", tags=["event-bus"])

# ── Auth ───────────────────────────────────────────────────────────────

SMS_API_KEY = os.environ.get("SMS_API_KEY", "")


async def verify_auth(
    authorization: str = Header(None),
    x_api_key: str = Header(None, alias="X-Api-Key"),
):
    """Verify Bearer token or X-Api-Key header."""
    if not SMS_API_KEY:
        return  # No auth configured = open (dev mode)
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    elif x_api_key:
        token = x_api_key
    if token != SMS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


# ── Supabase Client ───────────────────────────────────────────────────

_supabase_client = None


def _get_supabase():
    """Lazy-init Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        try:
            from supabase import create_client

            url = os.environ.get("SUPABASE_URL", "")
            key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get(
                "SUPABASE_SERVICE_ROLE_KEY", ""
            )
            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY required")
            _supabase_client = create_client(url, key)
        except Exception as e:
            logger.error("supabase_init_failed", error=str(e))
            raise HTTPException(status_code=503, detail="Event Bus unavailable")
    return _supabase_client


# ── Request/Response Models ───────────────────────────────────────────


class EmitEventRequest(BaseModel):
    """Request body for emitting an event."""

    event_type: str = Field(
        ...,
        description="Type of event",
        pattern="^(decision|discovery|error|concept|build|destroy|emotion|proposal|validation|connection)$",
    )
    source: str = Field(..., description="Source identifier (thread ID, agent name, etc.)")
    source_type: str = Field(
        ...,
        description="Type of source",
        pattern="^(manus_thread|chatgpt|claude|sabio|embrion|human|webhook|system)$",
    )
    title: str = Field(..., description="Short title of the event", max_length=500)
    content: str = Field(..., description="Full content/description of the event")
    context: Optional[str] = Field(None, description="Additional context")
    value_signal: str = Field(
        "medium",
        description="Value signal",
        pattern="^(critical|high|medium|low)$",
    )
    related_entities: list[str] = Field(default_factory=list, description="Related entity names")
    related_events: list[str] = Field(default_factory=list, description="Related event UUIDs")
    personal_layer: Optional[dict[str, Any]] = Field(
        None, description="Personal layer data (emotions, inspirations)"
    )


class EmitEventResponse(BaseModel):
    """Response after emitting an event."""

    event_id: str
    status: str
    auto_classification: dict[str, Any]
    crystallization_pending: bool


class CrystallizeRequest(BaseModel):
    """Request body for crystallization."""

    limit: int = Field(50, description="Max events to crystallize", ge=1, le=200)


class CrystallizeResponse(BaseModel):
    """Response after crystallization."""

    crystallized_count: int
    events: list[dict[str, Any]]


class EventStreamQuery(BaseModel):
    """Query parameters for event stream."""

    event_type: Optional[str] = None
    source_type: Optional[str] = None
    value_signal: Optional[str] = None
    since: Optional[str] = None
    entity: Optional[str] = None
    limit: int = 50


# ── Endpoints ─────────────────────────────────────────────────────────


@router.post("/emit", dependencies=[Depends(verify_auth)], response_model=EmitEventResponse)
async def emit_event(req: EmitEventRequest):
    """
    Emitir un evento al stream inmutable del Monstruo.

    El evento se registra en monstruo_event_stream y se auto-clasifica.
    Eventos con value_signal 'critical' o 'high' quedan pendientes de cristalización.
    """
    sb = _get_supabase()

    try:
        # Call the emit_event RPC
        result = sb.rpc(
            "emit_event",
            {
                "p_event_type": req.event_type,
                "p_source": req.source,
                "p_source_type": req.source_type,
                "p_title": req.title,
                "p_content": req.content,
                "p_context": req.context,
                "p_value_signal": req.value_signal,
                "p_related_entities": req.related_entities,
                "p_related_events": [str(e) for e in req.related_events] if req.related_events else [],
                "p_personal_layer": req.personal_layer,
            },
        ).execute()

        if result.data:
            data = result.data
            logger.info(
                "event_emitted",
                event_id=data.get("event_id"),
                event_type=req.event_type,
                value_signal=req.value_signal,
                title=req.title[:80],
            )
            return EmitEventResponse(
                event_id=str(data["event_id"]),
                status=data["status"],
                auto_classification=data.get("auto_classification", {}),
                crystallization_pending=data.get("crystallization_pending", False),
            )
        else:
            raise HTTPException(status_code=500, detail="emit_event RPC returned no data")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("emit_event_failed", error=str(e), event_type=req.event_type)
        raise HTTPException(status_code=500, detail=f"Failed to emit event: {str(e)}")


@router.post(
    "/crystallize", dependencies=[Depends(verify_auth)], response_model=CrystallizeResponse
)
async def crystallize_events(req: CrystallizeRequest = CrystallizeRequest()):
    """
    Cristalizar eventos pendientes (critical/high) al SMS como sovereign_memories.

    Este proceso convierte eventos efímeros en memoria permanente del Monstruo.
    """
    sb = _get_supabase()

    try:
        result = sb.rpc("crystallize_pending_events", {"p_limit": req.limit}).execute()

        if result.data:
            data = result.data
            logger.info(
                "events_crystallized",
                count=data.get("crystallized_count", 0),
            )
            return CrystallizeResponse(
                crystallized_count=data.get("crystallized_count", 0),
                events=data.get("events", []),
            )
        else:
            return CrystallizeResponse(crystallized_count=0, events=[])

    except Exception as e:
        logger.error("crystallize_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Crystallization failed: {str(e)}")


@router.get("/stream", dependencies=[Depends(verify_auth)])
async def query_stream(
    event_type: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    value_signal: Optional[str] = Query(None),
    since: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """
    Consultar el stream de eventos con filtros opcionales.

    Retorna eventos ordenados por emitted_at DESC.
    """
    sb = _get_supabase()

    try:
        result = sb.rpc(
            "query_event_stream",
            {
                "p_event_type": event_type,
                "p_source_type": source_type,
                "p_value_signal": value_signal,
                "p_since": since,
                "p_entity": entity,
                "p_limit": limit,
            },
        ).execute()

        events = result.data if result.data else []
        return {"events": events, "count": len(events) if isinstance(events, list) else 0}

    except Exception as e:
        logger.error("query_stream_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/stats", dependencies=[Depends(verify_auth)])
async def get_stats():
    """
    Obtener estadísticas del Event Stream.

    Incluye conteos por tipo, valor, fuente, y estado de cristalización.
    """
    sb = _get_supabase()

    try:
        result = sb.rpc("get_event_stream_stats", {}).execute()

        stats = result.data if result.data else {}
        return {"stats": stats, "status": "healthy"}

    except Exception as e:
        logger.error("get_stats_failed", error=str(e))
        # Return empty stats instead of failing — the bus might just be empty
        return {
            "stats": {"total_events": 0, "note": "Stats unavailable or stream empty"},
            "status": "degraded",
            "error": str(e),
        }
