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

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

import structlog
from fastapi import FastAPI, HTTPException, Request
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

# ── Background Jobs Store ──────────────────────────────────────────
background_jobs: dict[str, dict[str, Any]] = {}
_MAX_JOBS = 100


# ── Lifespan ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all sovereign components on startup."""
    global kernel, event_store, conversation_memory, knowledge_graph, observability, BOOT_TIME

    BOOT_TIME = datetime.now(timezone.utc)
    logger.info("monstruo_starting", version="0.4.0-sprint8", motor="langgraph")

    # Initialize Supabase client for persistence
    from memory.supabase_client import SupabaseClient
    db = SupabaseClient()
    db_connected = await db.connect()
    if db_connected:
        logger.info("supabase_connected", url=db._url[:50])
    else:
        logger.warning("supabase_not_connected", msg="Memory will be in-memory only")

    # Initialize sovereign components with Supabase persistence
    event_store = EventStore(db=db if db_connected else None)
    await event_store.initialize()
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

    # Initialize durable checkpointer (PostgresSaver → Supabase PostgreSQL)
    # Falls back to MemorySaver if SUPABASE_DB_URL is not set or connection fails
    # IMPORTANT: from_conn_string is an @asynccontextmanager — must enter manually
    checkpointer = None
    _checkpointer_cm = None  # context manager handle for cleanup
    supabase_db_url = os.environ.get("SUPABASE_DB_URL")
    if supabase_db_url:
        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
            # from_conn_string is an async context manager, enter it manually
            _checkpointer_cm = AsyncPostgresSaver.from_conn_string(supabase_db_url)
            checkpointer = await _checkpointer_cm.__aenter__()
            await checkpointer.setup()
            logger.info("checkpointer_initialized", type="AsyncPostgresSaver", backend="supabase_postgresql")
        except Exception as e:
            logger.warning("postgres_checkpointer_failed", error=str(e), fallback="MemorySaver")
            checkpointer = None
            _checkpointer_cm = None
    else:
        logger.warning("no_supabase_db_url", msg="Using MemorySaver (volatile). Set SUPABASE_DB_URL for durable state.")

    # Initialize the LangGraph Kernel with all dependencies
    kernel = LangGraphKernel(
        router=router,
        event_store=event_store,
        memory=conversation_memory,
        knowledge=knowledge_graph,
        observability=observability,
        checkpointer=checkpointer,
    )

    # Emit startup event
    await event_store.append(
        EventBuilder()
        .category(EventCategory.SYSTEM_STARTUP)
        .actor("system")
        .action("El Monstruo started")
        .with_payload({
            "version": "0.3.0-sprint2",
            "motor": "langgraph",
            "router": "connected" if router else "stub",
            "memory": "active",
            "knowledge": "active",
            "checkpointer": "PostgresSaver" if checkpointer else "MemorySaver",
        })
        .build()
    )

    # ── Sprint 8: Autonomous Runner ──────────────────────────────────
    autonomous_runner = None
    try:
        from kernel.runner.telegram_notifier import TelegramNotifier
        from kernel.runner.autonomous_runner import AutonomousRunner

        notifier = TelegramNotifier()
        autonomous_runner = AutonomousRunner(
            db=db if db_connected else None,
            kernel=kernel,
            notifier=notifier if notifier.enabled else None,
        )
        await autonomous_runner.start()
        logger.info("autonomous_runner_started", notifier="telegram" if notifier.enabled else "disabled")
    except Exception as e:
        logger.warning("autonomous_runner_init_failed", error=str(e))

    # Wire autonomy routes
    try:
        from kernel.autonomy_routes import router as autonomy_router, set_dependencies as set_autonomy_deps
        set_autonomy_deps(db=db if db_connected else None, runner=autonomous_runner)
        app.include_router(autonomy_router)
        logger.info("autonomy_routes_registered")
    except Exception as e:
        logger.warning("autonomy_routes_failed", error=str(e))

    logger.info(
        "monstruo_ready",
        motor="langgraph",
        router="connected" if router else "stub",
        autonomy="active" if autonomous_runner else "inactive",
    )

    # Warm-up: pre-heat LLM connections to eliminate cold start on first request
    if router:
        import asyncio
        async def _warmup():
            try:
                logger.info("warmup_starting")
                health = await router.health_check()
                logger.info("warmup_completed", result=health.get("status", "unknown"))
            except Exception as e:
                logger.warning("warmup_failed", error=str(e))
        asyncio.create_task(_warmup())

    yield

    # Shutdown checkpointer (close PostgreSQL connection)
    if _checkpointer_cm:
        try:
            await _checkpointer_cm.__aexit__(None, None, None)
            logger.info("checkpointer_shutdown", type="AsyncPostgresSaver")
        except Exception:
            pass

    # Shutdown autonomous runner
    if autonomous_runner:
        try:
            await autonomous_runner.stop()
            logger.info("autonomous_runner_shutdown")
        except Exception:
            pass

    # Shutdown router
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
    version="0.4.0-sprint8",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key authentication (Sprint 2)
# If MONSTRUO_API_KEY env var is set, all /v1/* endpoints require it
from kernel.auth import APIKeyAuthMiddleware
app.add_middleware(APIKeyAuthMiddleware)

# Rate limiting & cost caps (Sprint 3)
# Protects against API key leaks and runaway LLM costs
# Config: RATE_LIMIT_RPM, RATE_LIMIT_RPH, DAILY_COST_CAP_USD env vars
from kernel.rate_limiter import RateLimiterMiddleware
app.add_middleware(RateLimiterMiddleware)

# ── OpenAI-Compatible Adapter (Open WebUI integration) ────────────────
from kernel.openai_adapter import router as openai_router
app.include_router(openai_router)


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
    interrupt_payload: Optional[dict[str, Any]] = None  # HITL review details for bot
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
        interrupt_payload=metadata.get("interrupt_payload") if output.status == RunStatus.AWAITING_HUMAN else None,
        duration_ms=int(output.latency_ms),
    )


# ── Background Job Endpoints ───────────────────────────────────────

class BackgroundJobRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32000)
    user_id: str = Field(default="alfredo")
    channel: str = Field(default="api")
    brain: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    webhook_url: Optional[str] = None

class BackgroundJobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class BackgroundJobStatus(BaseModel):
    job_id: str
    status: str  # queued | running | completed | failed
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None


async def _run_background_job(job_id: str, request: BackgroundJobRequest):
    """Execute a kernel run in background and store the result."""
    global background_jobs
    try:
        background_jobs[job_id]["status"] = "running"
        logger.info("background_job_started", job_id=job_id, message=request.message[:80])

        context: dict[str, Any] = {}
        if request.brain:
            context["brain"] = request.brain
        if request.metadata:
            context["metadata"] = request.metadata
        if request.session_id:
            context["session_id"] = request.session_id

        run_id = uuid4()
        run_input = RunInput(
            run_id=run_id,
            user_id=request.user_id,
            channel=request.channel,
            message=request.message,
            context=context,
        )

        output = await kernel.start_run(run_input)

        result_data = {
            "run_id": str(output.run_id),
            "status": output.status.value,
            "intent": output.intent.value,
            "model_used": output.model_used,
            "response": output.response,
            "tokens_in": output.tokens_in,
            "tokens_out": output.tokens_out,
            "cost_usd": output.cost_usd,
            "latency_ms": round(output.latency_ms, 2),
        }

        background_jobs[job_id]["status"] = "completed"
        background_jobs[job_id]["result"] = result_data
        background_jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("background_job_completed", job_id=job_id, latency_ms=output.latency_ms)

        # Webhook notification if configured
        if request.webhook_url:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(request.webhook_url, json={
                        "job_id": job_id,
                        "status": "completed",
                        "result": result_data,
                    })
            except Exception as wh_err:
                logger.warning("background_webhook_failed", job_id=job_id, error=str(wh_err))

    except Exception as e:
        background_jobs[job_id]["status"] = "failed"
        background_jobs[job_id]["error"] = str(e)
        background_jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        logger.error("background_job_failed", job_id=job_id, error=str(e))


@app.post("/v1/background", response_model=BackgroundJobResponse, tags=["core"])
async def create_background_job(request: BackgroundJobRequest):
    """
    Submit a task for background processing.
    Returns immediately with a job_id. Poll /v1/background/{job_id} for results.
    Optionally set webhook_url to receive a POST when the job completes.
    """
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")

    if len(background_jobs) >= _MAX_JOBS:
        oldest_key = next(iter(background_jobs))
        del background_jobs[oldest_key]

    job_id = str(uuid4())
    background_jobs[job_id] = {
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "result": None,
        "error": None,
    }

    asyncio.create_task(_run_background_job(job_id, request))

    return BackgroundJobResponse(
        job_id=job_id,
        status="queued",
        message="Job submitted. Poll /v1/background/{job_id} for status.",
    )


@app.get("/v1/background/{job_id}", response_model=BackgroundJobStatus, tags=["core"])
async def get_background_job(job_id: str):
    """Get the status and result of a background job."""
    job = background_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return BackgroundJobStatus(
        job_id=job_id,
        status=job["status"],
        created_at=job["created_at"],
        completed_at=job.get("completed_at"),
        result=job.get("result"),
        error=job.get("error"),
    )


@app.get("/v1/background", tags=["core"])
async def list_background_jobs(limit: int = 20):
    """List recent background jobs."""
    jobs = []
    for jid, jdata in list(background_jobs.items())[-limit:]:
        jobs.append({
            "job_id": jid,
            "status": jdata["status"],
            "created_at": jdata["created_at"],
            "completed_at": jdata.get("completed_at"),
        })
    return jobs


# ── Backup Endpoint ───────────────────────────────────────────

class BackupRequest(BaseModel):
    tables: Optional[list[str]] = None
    include_env: bool = True
    upload_to_dropbox: bool = True

@app.post("/v1/backup", tags=["admin"])
async def trigger_backup(request: BackupRequest = BackupRequest()):
    """
    Trigger a manual backup of Supabase data and environment.
    Backs up to Dropbox (if configured) and local filesystem.
    """
    try:
        from scripts.backup import run_backup
        result = await run_backup(
            tables=request.tables,
            include_env=request.include_env,
            upload=request.upload_to_dropbox,
        )
        return result
    except ImportError:
        raise HTTPException(status_code=500, detail="Backup module not found")
    except Exception as e:
        logger.error("backup_endpoint_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


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

    # Resume the HITL-paused graph with the human's decision
    # All actions (approve/reject/edit) go through step() with Command(resume=...)
    # This ensures hitl_review node processes the decision correctly
    # Fix validated 2026-04-14: previous code used cancel() for reject (wrong)
    # and didn't resume for edit (graph stayed paused forever)
    result = {"run_id": request.run_id, "action": request.action, "processed": True}

    try:
        status = await kernel.get_status(run_id)
    except ValueError:
        result["processed"] = False
        result["note"] = "Run not found"
        return result

    if status != RunStatus.AWAITING_HUMAN:
        result["processed"] = False
        result["note"] = f"Run is not awaiting human review (status: {status.value})"
        return result

    # Map feedback action to hitl_review decision contract
    # hitl_review expects: {"decision": "approve"|"reject"|"modify", "modification": str|None}
    if request.action == "approve":
        step_input = {"decision": "approve"}
    elif request.action == "reject":
        step_input = {"decision": "reject"}
    elif request.action in ("edit", "modify") and request.edited_response:
        step_input = {
            "decision": "modify",
            "modification": request.edited_response,
        }
    elif request.action == "escalate":
        # Escalate = reject with reason for now
        step_input = {"decision": "reject"}
    else:
        result["processed"] = False
        result["note"] = f"Unknown action: {request.action}"
        return result

    try:
        output = await kernel.step(run_id, step_input)
        result["continued"] = True
        result["new_status"] = output.status.value
        result["response"] = output.response
    except Exception as e:
        logger.error("feedback_step_failed", run_id=request.run_id, error=str(e))
        result["continued"] = False
        result["error"] = str(e)

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


def _get_fallback_metrics() -> dict:
    """Lazy import to avoid circular dependency."""
    try:
        from router.engine import get_fallback_metrics
        return get_fallback_metrics()
    except ImportError:
        return {}


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
        "version": "0.4.0-sprint8",
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
        "router": {
            "fallback_metrics": _get_fallback_metrics(),
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


@app.get("/v1/hitl/pending", tags=["core"])
async def hitl_pending():
    """Get pending HITL reviews (for Telegram bot and consola PWA)."""
    try:
        from bot.hitl_handler import get_pending_reviews
        return {"pending": get_pending_reviews()}
    except ImportError:
        return {"pending": {}, "note": "HITL handler not loaded"}


# ── Sprint 2: Tool Endpoints (Las Manos) ──────────────────────────────


@app.post("/v1/tools/web_search", tags=["tools"])
async def tool_web_search(request: Request):
    """Search the web using Perplexity Sonar API."""
    body = await request.json()
    query = body.get("query", "")
    context = body.get("context", "")
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    from tools.web_search import web_search
    result = await web_search(query=query, context=context)
    return result


@app.post("/v1/tools/consult_sabios", tags=["tools"])
async def tool_consult_sabios(request: Request):
    """Consult the 6 Sabios (multi-model AI consultation)."""
    body = await request.json()
    prompt = body.get("prompt", "")
    context = body.get("context", "")
    sabios = body.get("sabios", None)  # Optional: list of sabio IDs
    parallel = body.get("parallel", True)
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    from tools.consult_sabios import consult_sabios
    result = await consult_sabios(prompt=prompt, context=context, sabios=sabios, parallel=parallel)
    return result


@app.post("/v1/tools/email", tags=["tools"])
async def tool_email(request: Request):
    """Send an email via Gmail SMTP."""
    body = await request.json()
    to = body.get("to", "")
    subject = body.get("subject", "")
    body_text = body.get("body", "")
    html_body = body.get("html_body", None)
    cc = body.get("cc", None)
    if not to or not subject or not body_text:
        raise HTTPException(status_code=400, detail="to, subject, and body are required")

    from tools.email_sender import send_email
    result = await send_email(to=to, subject=subject, body=body_text, html_body=html_body, cc=cc)
    return result


@app.get("/v1/tools", tags=["tools"])
async def list_tools():
    """List available tools and their status."""
    import os
    return {
        "tools": [
            {
                "name": "web_search",
                "endpoint": "/v1/tools/web_search",
                "status": "active" if os.environ.get("SONAR_API_KEY") else "no_api_key",
                "description": "Search the web using Perplexity Sonar API",
            },
            {
                "name": "consult_sabios",
                "endpoint": "/v1/tools/consult_sabios",
                "status": "active",
                "description": "Consult the 6 Sabios (multi-model AI consultation)",
            },
            {
                "name": "email",
                "endpoint": "/v1/tools/email",
                "status": "active" if os.environ.get("GMAIL_APP_PASSWORD") else "no_credentials",
                "description": "Send email via Gmail SMTP",
            },
        ]
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
        "version": "0.4.0-sprint8",
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
            "checkpointer": type(kernel._checkpointer).__name__ if kernel else "unknown",
        },
    }


# ── DEBUG ENDPOINTS (only active when DEBUG=true) ─────────────────────

_DEBUG_MODE = os.environ.get("DEBUG", "").lower() in ("true", "1", "yes")


def _register_debug_endpoints(application: FastAPI) -> None:
    """Register debug endpoints only when DEBUG mode is active."""

    @application.get("/v1/debug/tool_calling", tags=["debug"])
    async def debug_tool_calling(request: Request):
        """Test each LLM provider directly with tools and report results."""
        import traceback
        from router.llm_client import LLMClient, ToolSpec

        results = {}
        test_tool = ToolSpec(
            name="web_search",
            description="Search the web for real-time information.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
            risk="low",
        )
        test_messages = [
            {"role": "system", "content": "You are an assistant. Use web_search for current data."},
            {"role": "user", "content": "What is the USD/MXN exchange rate today?"},
        ]
        providers = {
            "gemini": ("gemini-3.1-flash-lite-preview", "GEMINI_API_KEY", "google"),
            "openai": ("gpt-5.4-mini", "OPENAI_API_KEY", "openai"),
            "anthropic": ("claude-sonnet-4-6", "ANTHROPIC_API_KEY", "anthropic"),
            "xai": ("grok-4.20-0309-non-reasoning", "XAI_API_KEY", "openai_compat"),
        }
        client = LLMClient()
        for name, (model_id, env_key, provider) in providers.items():
            api_key = os.environ.get(env_key, "")
            if not api_key:
                results[name] = {"status": "SKIP", "reason": f"{env_key} not set"}
                continue
            try:
                call_method = {
                    "google": lambda: client._call_google(model_id=model_id, api_key=api_key, messages=test_messages, temperature=0.1, max_tokens=200, tools=[test_tool], tool_choice="auto"),
                    "openai": lambda: client._call_openai(model_id=model_id, api_key=api_key, messages=test_messages, temperature=0.1, max_tokens=200, tools=[test_tool], tool_choice="auto"),
                    "anthropic": lambda: client._call_anthropic(model_id=model_id, api_key=api_key, messages=test_messages, temperature=0.1, max_tokens=200, tools=[test_tool], tool_choice="auto"),
                    "openai_compat": lambda: client._call_openai_compat(model_id=model_id, api_key=api_key, base_url="https://api.x.ai/v1", messages=test_messages, temperature=0.1, max_tokens=200, tools=[test_tool], tool_choice="auto"),
                }[provider]
                resp = await call_method()
                results[name] = {
                    "status": "OK", "model": model_id,
                    "finish_reason": resp.finish_reason,
                    "has_tool_calls": len(resp.tool_calls) > 0,
                    "tool_calls": [{"name": tc.name, "args": tc.arguments} for tc in resp.tool_calls],
                    "content_preview": resp.content[:100] if resp.content else "",
                    "usage": resp.usage,
                }
            except Exception as e:
                results[name] = {"status": "ERROR", "model": model_id, "error": str(e), "traceback": traceback.format_exc()[-500:]}
        return {"debug_tool_calling": results}

    @application.get("/v1/debug/error_log", tags=["debug"])
    async def debug_error_log(request: Request):
        """Return the in-memory error log from the fallback chain."""
        from router.engine import _TOOL_ERROR_LOG
        return {"error_count": len(_TOOL_ERROR_LOG), "errors": list(_TOOL_ERROR_LOG)}


if _DEBUG_MODE:
    _register_debug_endpoints(app)
    structlog.get_logger("monstruo").info("debug_endpoints_registered", mode="DEBUG")
