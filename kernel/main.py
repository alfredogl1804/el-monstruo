"""
El Monstruo — FastAPI Application (LangGraph Rewrite)
======================================================
HTTP API that connects the LangGraph Kernel with Memory,
Knowledge Graph, and Event Store.

Endpoints:
    POST /v1/chat          → Main chat (message → response)
    POST /v1/chat/stream   → Streaming via SSE
    POST /v1/step          → Continue HITL-paused run
    POST /v1/feedback      → HITL feedback (approve/reject/edit)
    POST /v1/cancel        → Kill switch
    GET  /v1/history       → Conversation history
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

    # Initialize Supabase client for persistence
    from memory.supabase_client import SupabaseClient
    db = SupabaseClient()
    db_connected = await db.connect()
    if db_connected:
        logger.info("supabase_connected", url=db._url[:50])
    else:
        logger.warning("supabase_not_connected", msg="Memory will be in-memory only")

    # Initialize sovereign components with Supabase persistence
    event_store = EventStore()
    conversation_memory = ConversationMemory(db=db if db_connected else None)
    await conversation_memory.initialize()
    knowledge_graph = KnowledgeGraph()

    # Initialize sovereign router (native SDKs, no LiteLLM proxy)
    router = None
    try:
        from router.engine import RouterEngine
        router = RouterEngine()
        logger.info("router_connected", mode="native_sdks")
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
    # Thin-client fields (Telegram bot convergence)
    session_id: Optional[str] = None
    brain: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

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
    # Thin-client contract fields (Telegram bot convergence)
    brain_used: str = ""
    tokens: dict[str, int] = Field(default_factory=dict)
    policy_decisions: list[dict[str, Any]] = Field(default_factory=list)
    requires_approval: bool = False
    duration_ms: int = 0

class StepRequest(BaseModel):
    run_id: str
    response: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict)

class CancelRequest(BaseModel):
    run_id: str
    reason: str = ""

class FeedbackRequest(BaseModel):
    """HITL feedback from Telegram or other channels."""
    run_id: str
    action: str = Field(..., description="approve | reject | edit | escalate")
    user_id: str = Field(default="alfredo")
    comment: Optional[str] = None
    edited_response: Optional[str] = None


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
    Supports both direct API calls and thin-client (Telegram bot) calls.
    """
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")

    context = request.context.copy()
    if request.force_model:
        context["force_model"] = request.force_model
    # Pass thin-client fields into context for kernel processing
    if request.brain:
        context["brain"] = request.brain
    if request.metadata:
        context["metadata"] = request.metadata
    if request.session_id:
        context["session_id"] = request.session_id

    run_id = UUID(request.run_id) if request.run_id else uuid4()

    # Start observability trace
    trace_ctx = None
    obs_metadata = {}
    if request.force_model:
        obs_metadata["force_model"] = request.force_model
    if request.brain:
        obs_metadata["brain"] = request.brain
    if request.channel:
        obs_metadata["channel"] = request.channel
    if observability:
        trace_ctx = observability.start_trace(
            run_id=str(run_id),
            user_id=request.user_id,
            channel=request.channel,
            message=request.message,
            metadata=obs_metadata or None,
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
        # Thin-client contract fields
        brain_used=metadata.get("brain_used", context.get("brain", "auto")),
        tokens={"input": output.tokens_in, "output": output.tokens_out},
        policy_decisions=metadata.get("policy_decisions", []),
        requires_approval=output.status == RunStatus.AWAITING_HUMAN,
        duration_ms=int(output.latency_ms),
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


@app.post("/v1/feedback", tags=["core"])
async def feedback(request: FeedbackRequest):
    """
    HITL feedback endpoint.
    The bot sends approval/rejection/edits here after user reviews a response.
    """
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")

    try:
        run_id = UUID(request.run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run_id format")

    # Record feedback event
    if event_store:
        await event_store.append(
            EventBuilder()
            .category(EventCategory.HUMAN_FEEDBACK)
            .actor(request.user_id)
            .action(f"feedback:{request.action}")
            .for_run(run_id)
            .with_payload({
                "action": request.action,
                "comment": request.comment,
                "edited_response": request.edited_response,
            })
            .build()
        )

    # If action is "approve" and run is paused, continue it
    result = {"run_id": request.run_id, "action": request.action, "processed": True}

    if request.action == "approve":
        try:
            status = await kernel.get_status(run_id)
            if status == RunStatus.AWAITING_HUMAN:
                output = await kernel.step(run_id, {"response": "approved", "comment": request.comment})
                result["continued"] = True
                result["new_status"] = output.status.value
        except ValueError:
            result["continued"] = False
            result["note"] = "Run not found or not in AWAITING_HUMAN state"

    elif request.action == "reject":
        try:
            await kernel.cancel(run_id, reason=request.comment or "Rejected by user")
            result["cancelled"] = True
        except Exception:
            result["cancelled"] = False

    elif request.action == "edit" and request.edited_response:
        # Store the edited response as an override
        result["edited"] = True
        result["note"] = "Edited response recorded in event store"

    return result


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


@app.get("/v1/history", tags=["core"])
async def history(user_id: Optional[str] = None, limit: int = 20):
    """Get conversation history. Used by thin client and consola PWA."""
    if not event_store:
        return []

    all_events = await event_store.get_recent(limit=limit * 3)  # Get more to filter

    # Filter for chat-related events
    chat_events = [
        {
            "event_id": str(e.event_id),
            "run_id": str(e.run_id) if e.run_id else None,
            "actor": e.actor,
            "action": e.action,
            "category": e.category.value,
            "timestamp": e.timestamp.isoformat(),
            "payload": e.payload,
        }
        for e in all_events
        if (not user_id or e.actor == user_id)
        and e.category.value in ("llm_call", "run_started", "run_completed", "human_feedback")
    ][:limit]

    return chat_events


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
    """Health check endpoint. Compatible with thin-client contract."""
    now = datetime.now(timezone.utc)
    # Build models_available from model catalog if available
    models_available = []
    try:
        from config.model_catalog import MODEL_CATALOG
        models_available = list(MODEL_CATALOG.keys())
    except ImportError:
        models_available = ["gpt-5", "claude-sonnet", "sonar-pro"]

    obs_status = "active" if (observability and (observability.langfuse_enabled or observability.otel_enabled)) else "inactive"

    return {
        "status": "healthy" if kernel else "degraded",
        "version": "0.3.0-sprint1",
        "motor": "langgraph",
        "uptime_seconds": int((now - BOOT_TIME).total_seconds()),
        # Thin-client contract fields
        "models_available": models_available,
        "observability": obs_status,
        # Detailed components (for consola PWA)
        "components": {
            "kernel": "active" if kernel else "inactive",
            "event_store": "active" if event_store else "inactive",
            "memory": "active" if conversation_memory else "inactive",
            "knowledge": "active" if knowledge_graph else "inactive",
            "langfuse": "active" if (observability and observability.langfuse_enabled) else "inactive",
            "opentelemetry": "active" if (observability and observability.otel_enabled) else "inactive",
        },
    }
