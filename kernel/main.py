"""
El Monstruo — FastAPI Application (LangGraph Rewrite)
======================================================
HTTP API that connects the LangGraph Kernel with Memory,
Knowledge Graph, and Event Store.

Endpoints:
    POST /v1/chat          → Main chat (message → response)
    POST /v1/chat/stream   → Streaming via SSE
    POST /v1/step          → Continue HITL-paused run
    POST /v1/cancel        → Kill switch
    GET  /v1/status/{id}   → Run status
    GET  /v1/replay/{id}   → Full run replay
    GET  /v1/events/recent → Recent events
    GET  /v1/events/errors → Recent errors
    GET  /v1/stats         → System statistics
    GET  /v1/graph         → Execution graph visualization
    GET  /health           → Health check
    GET  /                 → Root
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
from contracts.event_envelope import EventBuilder, EventCategory, Severity
from kernel.engine import LangGraphKernel
from memory.event_store import EventStore
from memory.conversation import ConversationMemory
from memory.knowledge_graph import KnowledgeGraph
from observability.manager import ObservabilityManager

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

kernel: Optional[LangGraphKernel] = None
event_store: Optional[EventStore] = None
conversation_memory: Optional[ConversationMemory] = None
knowledge_graph: Optional[KnowledgeGraph] = None
observability: Optional[ObservabilityManager] = None
BOOT_TIME = datetime.now(timezone.utc)


# ── Lifespan ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all sovereign components on startup."""
    global kernel, event_store, conversation_memory, knowledge_graph, observability, BOOT_TIME

    BOOT_TIME = datetime.now(timezone.utc)
    logger.info("monstruo_starting", version="0.2.0-sprint1", motor="langgraph")

    # Initialize sovereign components
    event_store = EventStore()
    conversation_memory = ConversationMemory()
    knowledge_graph = KnowledgeGraph()

    # Initialize router if LiteLLM is available
    router = None
    litellm_url = os.environ.get("LITELLM_URL", os.environ.get("LITELLM_BASE_URL"))
    if litellm_url:
        try:
            from router.engine import RouterEngine
            router = RouterEngine(
                litellm_url=litellm_url,
                litellm_key=os.environ.get("LITELLM_MASTER_KEY", "sk-monstruo-dev"),
            )
            logger.info("router_connected", url=litellm_url)
        except Exception as e:
            logger.warning("router_init_failed", error=str(e))

    # Initialize observability (Langfuse v4 + OpenTelemetry)
    observability = ObservabilityManager()
    obs_status = await observability.initialize()
    logger.info("observability_status", **obs_status)

    # Initialize the LangGraph Kernel with all dependencies
    kernel = LangGraphKernel(
        router=router,
        event_store=event_store,
        memory=conversation_memory,
        knowledge=knowledge_graph,
        observability=observability,
    )

    # Emit startup event
    await event_store.append(
        EventBuilder()
        .category(EventCategory.SYSTEM_STARTUP)
        .actor("system")
        .action("El Monstruo started")
        .with_payload({
            "version": "0.2.0-sprint1",
            "motor": "langgraph",
            "router": "connected" if router else "stub",
            "memory": "active",
            "knowledge": "active",
        })
        .build()
    )

    logger.info(
        "monstruo_ready",
        motor="langgraph",
        router="connected" if router else "stub",
    )

    yield

    # Shutdown
    if router:
        try:
            await router.close()
        except Exception:
            pass

    # Shutdown observability
    if observability:
        await observability.shutdown()

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
    description="Sistema de Inteligencia Artificial Soberana — LangGraph Kernel",
    version="0.2.0-sprint1",
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
    user_id: str = Field(default="alfredo")
    channel: str = Field(default="api")
    context: dict[str, Any] = Field(default_factory=dict)
    force_model: Optional[str] = None
    run_id: Optional[str] = None

class ChatResponse(BaseModel):
    run_id: str
    status: str
    intent: str
    model_used: str
    response: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    enriched: bool = False
    memory_written: bool = False
    events_count: int = 0

class StepRequest(BaseModel):
    run_id: str
    response: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict)

class CancelRequest(BaseModel):
    run_id: str
    reason: str = ""


# ── Endpoints ───────────────────────────────────────────────────────

@app.get("/", tags=["system"])
async def root():
    return {
        "name": "El Monstruo",
        "version": "0.2.0-sprint1",
        "motor": "langgraph",
        "status": "alive",
        "description": "Sistema de Inteligencia Artificial Soberana",
    }


@app.post("/v1/chat", response_model=ChatResponse, tags=["core"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Message enters → routes through 7-node LangGraph → response exits.
    """
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")

    context = request.context.copy()
    if request.force_model:
        context["force_model"] = request.force_model

    run_id = UUID(request.run_id) if request.run_id else uuid4()

    # Start observability trace
    trace_ctx = None
    if observability:
        trace_ctx = observability.start_trace(
            run_id=str(run_id),
            user_id=request.user_id,
            channel=request.channel,
            message=request.message,
            metadata={"force_model": request.force_model} if request.force_model else None,
        )

    run_input = RunInput(
        run_id=run_id,
        user_id=request.user_id,
        channel=request.channel,
        message=request.message,
        context=context,
    )

    output = await kernel.start_run(run_input)

    # End observability trace
    if observability and trace_ctx:
        observability.end_trace(
            ctx=trace_ctx,
            output=output.response,
            status=output.status.value,
            metadata={
                "model_used": output.model_used,
                "tokens_in": output.tokens_in,
                "tokens_out": output.tokens_out,
                "cost_usd": output.cost_usd,
                "latency_ms": output.latency_ms,
            },
        )
        await observability.flush()

    metadata = output.metadata or {}
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
        enriched=metadata.get("enriched", False),
        memory_written=metadata.get("memory_written", False),
        events_count=metadata.get("events_count", 0),
    )


@app.post("/v1/chat/stream", tags=["core"])
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint with Server-Sent Events."""
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")

    context = request.context.copy()
    if request.force_model:
        context["force_model"] = request.force_model

    run_id = UUID(request.run_id) if request.run_id else uuid4()

    run_input = RunInput(
        run_id=run_id,
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
    """Continue a HITL-paused run with human input."""
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")

    try:
        run_id = UUID(request.run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run_id format")

    input_data = {"response": request.response, **request.data} if request.response else request.data or None

    try:
        output = await kernel.step(run_id, input_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    metadata = output.metadata or {}
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
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")

    try:
        run_id = UUID(request.run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run_id format")

    success = await kernel.cancel(run_id, request.reason)
    if not success:
        raise HTTPException(status_code=404, detail="Run not found or already terminal")

    return {"run_id": request.run_id, "cancelled": True, "reason": request.reason}


@app.get("/v1/status/{run_id}", tags=["core"])
async def get_status(run_id: str):
    """Get current status of a run."""
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")

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
    if not event_store:
        raise HTTPException(status_code=503, detail="Event store not initialized")

    try:
        rid = UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run_id format")

    events = await event_store.replay(rid)
    # replay returns dicts, convert for consistent output
    return {
        "run_id": run_id,
        "events_count": len(events),
        "events": events,
    }



@app.get("/v1/events/recent", tags=["observability"])
async def recent_events(limit: int = 50):
    """Get the most recent events."""
    if not event_store:
        raise HTTPException(status_code=503, detail="Event store not initialized")

    events = await event_store.get_recent(limit=limit)
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
                "run_id": str(e.run_id) if e.run_id else None,
            }
            for e in events
        ],
    }


@app.get("/v1/events/errors", tags=["observability"])
async def error_events(limit: int = 20):
    """Get recent error events."""
    if not event_store:
        raise HTTPException(status_code=503, detail="Event store not initialized")

    events = await event_store.get_errors(limit=limit)
    return {
        "count": len(events),
        "events": [
            {
                "event_id": str(e.event_id),
                "category": e.category.value,
                "actor": e.actor,
                "action": e.action,
                "timestamp": e.timestamp.isoformat(),
                "payload": e.payload,
            }
            for e in events
        ],
    }


@app.get("/v1/stats", tags=["observability"])
async def stats():
    """System statistics."""
    if not event_store:
        return {"status": "no_event_store"}

    all_events = await event_store.get_recent(limit=10000)
    categories: dict[str, int] = {}
    for e in all_events:
        cat = e.category.value
        categories[cat] = categories.get(cat, 0) + 1

    now = datetime.now(timezone.utc)
    return {
        "system": {
            "name": "El Monstruo",
            "version": "0.2.0-sprint1",
            "motor": "langgraph",
            "uptime_seconds": (now - BOOT_TIME).total_seconds(),
        },
        "event_store": {
            "total_events": len(all_events),
            "categories": categories,
        },
        "memory": {
            "conversations": await conversation_memory.count() if conversation_memory else 0,
        },
        "knowledge": {
            "entities": knowledge_graph.entity_count if knowledge_graph else 0,
            "relations": knowledge_graph.relation_count if knowledge_graph else 0,
        },
    }


@app.get("/v1/graph", tags=["observability"])
async def graph_visualization():
    """Get the execution graph as Mermaid diagram."""
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")

    return {
        "mermaid": kernel.get_graph_mermaid(),
        "ascii": kernel.get_graph_ascii(),
    }


@app.get("/health", tags=["system"])
async def health():
    """Health check endpoint."""
    now = datetime.now(timezone.utc)
    return {
        "status": "healthy" if kernel else "degraded",
        "version": "0.2.0-sprint1",
        "motor": "langgraph",
        "uptime_seconds": (now - BOOT_TIME).total_seconds(),
        "components": {
            "kernel": "active" if kernel else "inactive",
            "event_store": "active" if event_store else "inactive",
            "memory": "active" if conversation_memory else "inactive",
            "knowledge": "active" if knowledge_graph else "inactive",
            "langfuse": "active" if (observability and observability.langfuse_enabled) else "inactive",
            "opentelemetry": "active" if (observability and observability.otel_enabled) else "inactive",
        },
    }
