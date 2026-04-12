"""
El Monstruo — FastAPI Application (Día 1)
============================================
API principal que conecta Kernel + Router + EventStore.
Endpoints para: chat, stream, status, replay, health, cancel.

Principio: Un mensaje entra, se routea, se ejecuta, se responde,
y todo queda registrado.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from contracts.kernel_interface import IntentType, RunInput, RunStatus
from kernel.engine import KernelEngine
from router.engine import RouterEngine
from memory.event_store import EventStore
from contracts.event_envelope import EventBuilder, EventCategory

# ── Structured Logging ──────────────────────────────────────────────

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
)

logger = structlog.get_logger("monstruo")


# ── Global Instances ────────────────────────────────────────────────

event_store = EventStore(
    supabase_url=os.environ.get("SUPABASE_URL"),
    supabase_key=os.environ.get("SUPABASE_SERVICE_KEY"),
)

router_engine = RouterEngine(
    litellm_url=os.environ.get("LITELLM_URL", "http://localhost:4000"),
    litellm_key=os.environ.get("LITELLM_MASTER_KEY", "sk-monstruo-dev"),
)

kernel = KernelEngine(
    router=router_engine,
    event_store=event_store,
)

BOOT_TIME = datetime.now(timezone.utc)


# ── Lifespan ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("monstruo_starting", version="0.1.0-sprint1")

    await event_store.initialize()

    await event_store.append(
        EventBuilder()
        .category(EventCategory.SYSTEM_STARTUP)
        .actor("system")
        .action("El Monstruo started")
        .with_payload({
            "version": "0.1.0-sprint1",
            "litellm_url": os.environ.get("LITELLM_URL", "http://localhost:4000"),
            "supabase_configured": bool(os.environ.get("SUPABASE_URL")),
        })
        .build()
    )

    logger.info("monstruo_ready")
    yield

    await router_engine.close()
    await event_store.append(
        EventBuilder()
        .category(EventCategory.SYSTEM_SHUTDOWN)
        .actor("system")
        .action("El Monstruo shutting down")
        .build()
    )
    logger.info("monstruo_shutdown")


# ── FastAPI App ─────────────────────────────────────────────────────

app = FastAPI(
    title="El Monstruo",
    description="Sistema de Inteligencia Artificial Soberana",
    version="0.1.0-sprint1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response Models ─────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32000)
    user_id: str = Field(default="anonymous")
    channel: str = Field(default="api")
    context: dict[str, Any] = Field(default_factory=dict)
    force_model: Optional[str] = None

class ChatResponse(BaseModel):
    run_id: str
    status: str
    intent: str
    model_used: str
    response: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: float

class StepRequest(BaseModel):
    run_id: str
    message: str = ""
    data: dict[str, Any] = Field(default_factory=dict)

class CancelRequest(BaseModel):
    run_id: str
    reason: str = ""


# ── Endpoints ───────────────────────────────────────────────────────

@app.get("/", tags=["system"])
async def root():
    return {
        "name": "El Monstruo",
        "version": "0.1.0-sprint1",
        "status": "alive",
        "description": "Sistema de Inteligencia Artificial Soberana",
    }


@app.post("/v1/chat", response_model=ChatResponse, tags=["core"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Message in → intent → model routing → execution → response.
    Everything logged in event store.
    """
    context = request.context.copy()
    if request.force_model:
        context["force_model"] = request.force_model

    run_input = RunInput(
        run_id=uuid4(),
        user_id=request.user_id,
        channel=request.channel,
        message=request.message,
        context=context,
    )

    output = await kernel.start_run(run_input)

    return ChatResponse(
        run_id=str(output.run_id),
        status=output.status.value,
        intent=output.intent.value,
        model_used=output.model_used,
        response=output.response,
        tokens_in=output.tokens_in,
        tokens_out=output.tokens_out,
        cost_usd=output.cost_usd,
        latency_ms=round(output.latency_ms, 2),
    )


@app.post("/v1/chat/stream", tags=["core"])
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint with Server-Sent Events."""
    context = request.context.copy()
    if request.force_model:
        context["force_model"] = request.force_model

    run_input = RunInput(
        run_id=uuid4(),
        user_id=request.user_id,
        channel=request.channel,
        message=request.message,
        context=context,
    )

    async def event_generator():
        async for chunk in kernel.stream(run_input):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/v1/step", response_model=ChatResponse, tags=["core"])
async def step(request: StepRequest):
    """Continue a multi-step run."""
    try:
        run_id = UUID(request.run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run_id format")

    try:
        output = await kernel.step(run_id, {"message": request.message, **request.data})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ChatResponse(
        run_id=str(output.run_id),
        status=output.status.value,
        intent=output.intent.value,
        model_used=output.model_used,
        response=output.response,
        tokens_in=output.tokens_in,
        tokens_out=output.tokens_out,
        cost_usd=output.cost_usd,
        latency_ms=round(output.latency_ms, 2),
    )


@app.post("/v1/cancel", tags=["core"])
async def cancel(request: CancelRequest):
    """Kill switch: cancel a running execution."""
    try:
        run_id = UUID(request.run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run_id format")

    success = await kernel.cancel(run_id, request.reason)
    return {"run_id": request.run_id, "cancelled": success}


@app.get("/v1/status/{run_id}", tags=["core"])
async def get_status(run_id: str):
    """Get current status of a run."""
    try:
        rid = UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run_id format")

    try:
        status = await kernel.get_status(rid)
        return {"run_id": run_id, "status": status.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/v1/replay/{run_id}", tags=["observability"])
async def replay(run_id: str):
    """Replay a run: see every event in chronological order."""
    try:
        rid = UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run_id format")

    events = await event_store.replay(rid)
    if not events:
        raise HTTPException(status_code=404, detail=f"No events found for run {run_id}")

    return {"run_id": run_id, "event_count": len(events), "events": events}


@app.get("/v1/events/recent", tags=["observability"])
async def recent_events(limit: int = 50):
    """Get the most recent events."""
    events = await event_store.get_recent(limit)
    return {
        "count": len(events),
        "events": [
            {
                "event_id": str(e.event_id),
                "category": e.category.value,
                "severity": e.severity.value,
                "actor": e.actor,
                "action": e.action,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in events
        ],
    }


@app.get("/v1/events/errors", tags=["observability"])
async def error_events(limit: int = 20):
    """Get recent error events."""
    errors = await event_store.get_errors(limit)
    return {
        "count": len(errors),
        "errors": [
            {
                "event_id": str(e.event_id),
                "category": e.category.value,
                "severity": e.severity.value,
                "actor": e.actor,
                "action": e.action,
                "payload": e.payload,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in errors
        ],
    }


@app.get("/v1/stats", tags=["observability"])
async def stats():
    """Get event store and system statistics."""
    store_stats = await event_store.get_stats()
    now = datetime.now(timezone.utc)
    return {
        "system": {
            "name": "El Monstruo",
            "version": "0.1.0-sprint1",
            "uptime_seconds": (now - BOOT_TIME).total_seconds(),
        },
        "event_store": store_stats,
    }


@app.get("/health", tags=["system"])
async def health():
    """Health check endpoint."""
    litellm_health = await router_engine.health_check()
    store_stats = await event_store.get_stats()
    now = datetime.now(timezone.utc)

    overall = "ok" if litellm_health.get("status") == "ok" else "degraded"

    return {
        "status": overall,
        "version": "0.1.0-sprint1",
        "uptime_seconds": (now - BOOT_TIME).total_seconds(),
        "litellm": litellm_health,
        "event_store": store_stats,
    }
