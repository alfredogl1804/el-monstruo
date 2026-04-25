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

from contracts.event_envelope import EventBuilder, EventCategory
from contracts.kernel_interface import RunInput, RunStatus
from kernel.engine import LangGraphKernel
from memory.conversation import ConversationMemory
from memory.event_store import EventStore
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
    logger.info("monstruo_starting", version="0.20.0-sprint27", motor="langgraph")

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
            logger.info(
                "checkpointer_initialized",
                type="AsyncPostgresSaver",
                backend="supabase_postgresql",
            )
        except Exception as e:
            logger.warning("postgres_checkpointer_failed", error=str(e), fallback="MemorySaver")
            checkpointer = None
            _checkpointer_cm = None
    else:
        logger.warning(
            "no_supabase_db_url",
            msg="Using MemorySaver (volatile). Set SUPABASE_DB_URL for durable state.",
        )

    # Initialize the LangGraph Kernel with all dependencies
    kernel = LangGraphKernel(
        router=router,
        event_store=event_store,
        memory=conversation_memory,
        knowledge=knowledge_graph,
        observability=observability,
        checkpointer=checkpointer,
        db=db if db_connected else None,  # Sprint 9: for dossier injection
    )

    # Emit startup event
    await event_store.append(
        EventBuilder()
        .category(EventCategory.SYSTEM_STARTUP)
        .actor("system")
        .action("El Monstruo started")
        .with_payload(
            {
                "version": "0.20.0-sprint27",
                "motor": "langgraph",
                "router": "connected" if router else "stub",
                "memory": "active",
                "knowledge": "active",
                "checkpointer": "PostgresSaver" if checkpointer else "MemorySaver",
            }
        )
        .build()
    )

    # ── Inject DB into tool_dispatch for schedule_task ─────────────
    try:
        from kernel.tool_dispatch import set_tool_db

        if db_connected:
            set_tool_db(db)
            logger.info("tool_db_injected")
    except Exception as e:
        logger.warning("tool_db_injection_failed", error=str(e))

    # ── Sprint 8: Autonomous Runner ──────────────────────────────────
    autonomous_runner = None
    try:
        from kernel.runner.autonomous_runner import AutonomousRunner
        from kernel.runner.telegram_notifier import TelegramNotifier

        notifier = TelegramNotifier()
        autonomous_runner = AutonomousRunner(
            db=db if db_connected else None,
            kernel=kernel,
            notifier=notifier if notifier.enabled else None,
        )
        await autonomous_runner.start()
        logger.info(
            "autonomous_runner_started",
            notifier="telegram" if notifier.enabled else "disabled",
        )
    except Exception as e:
        logger.warning("autonomous_runner_init_failed", error=str(e))

    # Wire autonomy routes
    try:
        from kernel.autonomy_routes import router as autonomy_router
        from kernel.autonomy_routes import set_dependencies as set_autonomy_deps

        set_autonomy_deps(db=db if db_connected else None, runner=autonomous_runner)
        app.include_router(autonomy_router)
        logger.info("autonomy_routes_registered")
    except Exception as e:
        logger.warning("autonomy_routes_failed", error=str(e))

    # Sprint 9: Wire mission control and dossier routes
    try:
        from kernel.mission_routes import (
            dossier_router,
        )
        from kernel.mission_routes import (
            router as mission_router,
        )
        from kernel.mission_routes import (
            set_dependencies as set_mission_deps,
        )

        set_mission_deps(db=db if db_connected else None)
        app.include_router(mission_router)
        app.include_router(dossier_router)
        logger.info("mission_dossier_routes_registered")
    except Exception as e:
        logger.warning("mission_dossier_routes_failed", error=str(e))

    # ── Sprint 10: Tool Registry + Usage Tracker ──────────────────
    tool_registry = None
    usage_tracker = None
    try:
        from kernel.tool_registry import ToolRegistry
        from kernel.usage_tracker import UsageTracker

        tool_registry = ToolRegistry(db=db if db_connected else None)
        await tool_registry.initialize()
        app.state.tool_registry = tool_registry

        usage_tracker = UsageTracker(db=db if db_connected else None)
        await usage_tracker.initialize()
        app.state.usage_tracker = usage_tracker

        # Inject into kernel for automatic tracking
        if kernel:
            kernel._usage_tracker = usage_tracker
            kernel._tool_registry = tool_registry

        logger.info(
            "sprint10_initialized",
            registry_tools=tool_registry.get_stats().get("total_tools", 0),
            tracker_today_cost=usage_tracker.get_stats().get("today_cost_usd", 0),
        )
    except Exception as e:
        logger.warning("sprint10_init_failed", error=str(e))

    # Wire usage & registry routes
    try:
        from kernel.usage_routes import router as usage_router

        app.include_router(usage_router)
        logger.info("usage_registry_routes_registered")
    except Exception as e:
        logger.warning("usage_registry_routes_failed", error=str(e))

    # ── Sprint 15: FinOps Soberano ────────────────────────────────
    finops = None
    try:
        from kernel.alerts.sovereign_alerts import SovereignAlertMonitor
        from kernel.finops import FinOpsController
        from kernel.runner.telegram_notifier import TelegramNotifier as _TN

        # Reuse existing notifier or create one for FinOps alerts
        _finops_notifier = _TN()
        alert_monitor_finops = SovereignAlertMonitor(notifier=_finops_notifier)

        finops = FinOpsController(
            db=db if db_connected else None,
            usage_tracker=usage_tracker,
            alerts=alert_monitor_finops,
        )
        await finops.initialize()
        app.state.finops = finops

        # Inject into kernel for budget hard stop
        if kernel:
            kernel._finops = finops

        logger.info(
            "finops_initialized",
            daily_limit=finops.get_status()["daily_hard_limit_usd"],
            hard_stop=finops.get_status()["hard_stop_enabled"],
        )
    except Exception as e:
        logger.warning("finops_init_failed", error=str(e))

    # ── Sprint 10b (ADR): Tool Broker ────────────────────────────
    tool_broker = None
    try:
        from kernel.tool_broker import ToolBroker
        from kernel.tool_dispatch import set_tool_broker

        tool_broker = ToolBroker(db=db if db_connected else None)
        await tool_broker.initialize(tenant_id="alfredo")
        set_tool_broker(tool_broker)
        app.state.tool_broker = tool_broker

        logger.info(
            "tool_broker_initialized",
            bindings=tool_broker.get_stats().get("bindings_loaded", 0),
        )
    except Exception as e:
        logger.warning("tool_broker_init_failed", error=str(e))

    # ── Sprint 12: Persistent Memory (ThoughtsStore) ────────────────
    thoughts_store = None
    try:
        from memory.thoughts import ThoughtsStore

        thoughts_store = ThoughtsStore(db=db if db_connected else None)
        await thoughts_store.initialize()
        app.state.thoughts_store = thoughts_store
        logger.info("thoughts_store_initialized")
    except Exception as e:
        logger.warning("thoughts_store_init_failed", error=str(e))

    # Wire memory routes
    try:
        from kernel.memory_routes import router as memory_router
        from kernel.memory_routes import set_dependencies as set_memory_deps

        set_memory_deps(thoughts_store=thoughts_store)
        app.include_router(memory_router)
        logger.info("memory_routes_registered")
    except Exception as e:
        logger.warning("memory_routes_failed", error=str(e))

    # Wire AG-UI adapter
    try:
        from kernel.agui_adapter import router as agui_router
        from kernel.agui_adapter import set_dependencies as set_agui_deps

        set_agui_deps(kernel=kernel, thoughts_store=thoughts_store)
        app.include_router(agui_router)
        logger.info("agui_adapter_registered")
    except Exception as e:
        logger.warning("agui_adapter_failed", error=str(e))

    # ── Sprint 14: Sovereign Alert System ────────────────────────────
    try:
        from kernel.alerts.routes import router as alerts_router

        app.include_router(alerts_router)
        logger.info("sovereign_alerts_registered")
    except Exception as e:
        logger.warning("sovereign_alerts_failed", error=str(e))

    # ── Sprint 24: MemPalace Warm-up (pgvector) ────────────────────
    mempalace_ready = False
    try:
        from memory.mempalace_bridge import _ensure_initialized

        if _ensure_initialized():
            mempalace_ready = True
            app.state._mempalace_ready = True
            logger.info("mempalace_warmed_up", backend="pgvector")
        else:
            logger.warning("mempalace_warmup_skipped", reason="init_returned_false")
    except Exception as e:
        logger.warning("mempalace_warmup_failed", error=str(e))
    # ── Sprint 24: LightRAG Warm-up ──────────────────────────────────
    try:
        from memory.lightrag_bridge import get_stats as lightrag_stats

        lr_status = await lightrag_stats()
        if lr_status.get("status") == "active":
            app.state._lightrag_ready = True
            logger.info("lightrag_warmed_up", model=lr_status.get("model", "unknown"))
        else:
            logger.info("lightrag_warmup_deferred", reason=lr_status.get("reason", "not_initialized"))
    except Exception as e:
        logger.warning("lightrag_warmup_failed", error=str(e))

    # ── Sprint 17: MCP Client Manager ──────────────────────────────────
    mcp_manager = None
    try:
        from kernel.mcp_client import MCPClientManager, build_mcp_configs
        from kernel.tool_dispatch import set_mcp_manager

        # Sprint 18: build_mcp_configs() = presets (github, filesystem, supabase) + env custom
        mcp_configs = build_mcp_configs()
        if mcp_configs:
            mcp_manager = MCPClientManager(mcp_configs)
            mcp_status = await mcp_manager.initialize()
            set_mcp_manager(mcp_manager)
            app.state.mcp_manager = mcp_manager
            logger.info(
                "mcp_manager_initialized",
                servers=len(mcp_configs),
                tools=len(mcp_manager.tools),
                status=mcp_status,
            )
        else:
            logger.info("mcp_manager_skipped", reason="no MCP servers configured")
    except Exception as e:
        logger.warning("mcp_manager_init_failed", error=str(e))

    # ── Sprint 26: Honcho DISABLED (service deleted from Railway) ──────
    _ = False  # honcho_active removed Sprint 27.5
    logger.info("honcho_disabled", reason="replaced_by_mem0_sprint27")

    # ── Sprint 27: Mem0 2.0.0 — Episodic Memory (replaces Honcho) ──────
    mem0_active = False
    try:
        from memory.mem0_bridge import get_stats as mem0_stats

        _mem0_check = await mem0_stats()
        mem0_active = _mem0_check.get("status") == "active"
        if mem0_active:
            logger.info("mem0_initialized", provider="pgvector", version="2.0.0")
        else:
            logger.warning("mem0_init_inactive", detail=_mem0_check)
    except Exception as e:
        logger.warning("mem0_init_failed", error=str(e))
    app.state._mem0_active = mem0_active

    # ── Sprint 26: FastMCP Server (internal tool exposure via MCP) ──────
    fastmcp_server = None
    try:
        from kernel.fastmcp_server import create_fastmcp_server

        fastmcp_server = create_fastmcp_server()
        if fastmcp_server:
            # Mount FastMCP SSE endpoint on the FastAPI app
            # FastMCP 3.2.4: http_app(transport='sse') returns a Starlette ASGI app
            app.mount("/mcp", fastmcp_server.http_app(transport="sse"))
            app.state.fastmcp_server = fastmcp_server
            logger.info("fastmcp_mounted", path="/mcp", transport="sse", tools=3)
    except Exception as e:
        logger.warning("fastmcp_init_failed", error=str(e))

    logger.info(
        "monstruo_ready",
        version="0.20.0-sprint27",
        motor="langgraph",
        router="connected" if router else "stub",
        autonomy="active" if autonomous_runner else "inactive",
        registry="active" if tool_registry and tool_registry.initialized else "inactive",
        tracker="active" if usage_tracker and usage_tracker.initialized else "inactive",
        broker="active" if tool_broker else "inactive",
        thoughts="active" if thoughts_store else "inactive",
        finops="active" if finops else "inactive",
        agui="active",
        alerts="registered",
        mcp="active" if mcp_manager else "inactive",
        fastmcp="active" if fastmcp_server else "inactive",
        mem0="active" if mem0_active else "inactive",
        mempalace="active" if mempalace_ready else "inactive",
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
    version="0.20.0-sprint27",
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
        "version": "0.20.0-sprint27",
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
            session_id=request.session_id,  # Sprint 13: propagate session_id
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
                    await client.post(
                        request.webhook_url,
                        json={
                            "job_id": job_id,
                            "status": "completed",
                            "result": result_data,
                        },
                    )
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
        jobs.append(
            {
                "job_id": jid,
                "status": jdata["status"],
                "created_at": jdata["created_at"],
                "completed_at": jdata.get("completed_at"),
            }
        )
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
            .with_payload(
                {
                    "action": request.action,
                    "comment": request.comment,
                    "edited_response": request.edited_response,
                }
            )
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
            "version": "0.20.0-sprint27",
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
    """Get conversation history. Used by thin client and consola PWA.

    Sprint 21 fix: expanded category filter to include all relevant event types
    that the kernel actually emits (run.started, model.called, memory.updated,
    intent.classified, context.enriched, human.reviewed, human.feedback).
    Previous filter only matched 'llm_call' etc. which didn't match the actual
    EventCategory enum values.
    """
    if not event_store:
        return []

    all_events = await event_store.get_recent(limit=limit * 5)  # Get more to filter

    # Sprint 21: Expanded filter to match actual EventCategory enum values
    # The kernel emits: run.started, intent.classified, context.enriched,
    # model.called, run.completed, run.failed, memory.updated, human.reviewed, human.feedback
    history_categories = {
        "run.started",
        "run.completed",
        "run.failed",
        "model.called",
        "memory.updated",
        "human.reviewed",
        "human.feedback",
        "intent.classified",
        # Legacy names (in case any old events use them)
        "llm_call",
        "human_feedback",
    }

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
        if (not user_id or e.actor == user_id or e.user_id == user_id) and e.category.value in history_categories
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
    """Get pending HITL reviews (for Telegram bot and consola PWA).

    Sprint 21: Now uses bot.hitl_handler with in-memory pending store.
    """
    try:
        from bot.hitl_handler import get_pending_count, get_pending_reviews

        reviews = get_pending_reviews()
        return {"pending": reviews, "count": get_pending_count()}
    except ImportError:
        return {"pending": {}, "count": 0, "note": "HITL handler not loaded"}


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
        from config.model_catalog import MODELS as MODEL_CATALOG

        # Show flagship model_ids (not catalog keys) for external consumers
        flagship_keys = ["gpt-5.4", "claude-opus-4-7", "gemini-3.1-pro", "sonar-reasoning-pro"]
        models_available = [MODEL_CATALOG[k]["model_id"] for k in flagship_keys if k in MODEL_CATALOG]
    except ImportError:
        models_available = ["gpt-5.4-pro-2026-03-05", "claude-opus-4-7", "sonar-reasoning-pro"]

    obs_status = (
        "active" if (observability and (observability.langfuse_enabled or observability.otel_enabled)) else "inactive"
    )

    return {
        "status": "healthy" if kernel else "degraded",
        "version": "0.20.0-sprint27",
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
            "checkpointer": "active (AsyncPostgresSaver)"
            if (kernel and type(kernel._checkpointer).__name__ == "AsyncPostgresSaver")
            else "inactive (MemorySaver)"
            if kernel
            else "unknown",  # noqa: E501
            "mempalace": "active" if getattr(app.state, "_mempalace_ready", False) else "inactive",
            "lightrag": "active" if getattr(app.state, "_lightrag_ready", False) else "inactive",
            "multi_agent": "active",  # Sprint 21: always available (keyword-based, no external deps)
            "finops": "active" if getattr(app.state, "finops", None) else "inactive",
            "mcp": "active" if getattr(app.state, "mcp_manager", None) else "inactive",
            "fastmcp": "active" if getattr(app.state, "fastmcp_server", None) else "inactive",
            "mem0": "active" if getattr(app.state, "_mem0_active", False) else "inactive",
        },
    }


# ── Sprint 22: Auth Health Check ──────────────────────────────────


@app.get("/health/auth", tags=["system"])
async def auth_health():
    """Auth configuration health check. Sprint 22 — monitoring endpoint."""
    api_key = os.environ.get("MONSTRUO_API_KEY")
    key_configured = bool(api_key)
    key_length = len(api_key) if api_key else 0
    expected_length = 36  # UUID format
    return {
        "auth_configured": key_configured,
        "key_length": key_length,
        "key_format_valid": key_length == expected_length,
        "status": "healthy" if key_configured and key_length == expected_length else "degraded",
        "mode": "fail-closed" if not key_configured else "enforcing",
    }


# ── Sprint 18: MCP Status Endpoint ─────────────────────────────


@app.get("/v1/mcp/status", tags=["mcp"])
async def mcp_status():
    """Return MCP server connection status and available tools."""
    mcp_mgr = getattr(app.state, "mcp_manager", None)
    if mcp_mgr:
        return {
            "status": "active",
            "servers": mcp_mgr.get_status(),
        }
    return {
        "status": "inactive",
        "reason": "No MCP servers configured. Set env vars to enable presets.",
        "available_presets": [
            {
                "name": "github",
                "env": "GITHUB_PERSONAL_ACCESS_TOKEN",
                "pkg": "@modelcontextprotocol/server-github@2025.4.8",
            },  # noqa: E501
            {
                "name": "filesystem",
                "env": "MCP_FILESYSTEM_PATHS",
                "pkg": "@modelcontextprotocol/server-filesystem@2026.1.14",
            },  # noqa: E501
            {
                "name": "supabase",
                "env": "SUPABASE_URL + SUPABASE_SERVICE_KEY (or SUPABASE_SERVICE_ROLE_KEY)",
                "pkg": "@supabase/mcp-server-supabase@0.7.0",
            },  # noqa: E501
        ],
    }


@app.get("/v1/memory/status", tags=["memory"])
async def memory_status():
    """Return MemPalace + Mem0 + LightRAG memory system status. Sprint 27."""
    result = {"layers": {}}

    # MemPalace (episodic + semantic)
    try:
        from memory.mempalace_bridge import get_stats

        result["layers"]["mempalace"] = await get_stats()
    except Exception as e:
        result["layers"]["mempalace"] = {"status": "error", "error": str(e)}

    # Mem0 (episodic memory — replaces Honcho, Sprint 27)
    try:
        from memory.mem0_bridge import get_stats as mem0_stats

        result["layers"]["mem0"] = await mem0_stats()
    except Exception as e:
        result["layers"]["mem0"] = {"status": "not_configured", "error": str(e)}

    # Sprint 23: LightRAG (knowledge graph RAG)
    try:
        from memory.lightrag_bridge import get_stats as lightrag_stats

        result["layers"]["lightrag"] = await lightrag_stats()
    except Exception:
        result["layers"]["lightrag"] = {"status": "not_configured"}

    # PostgresSaver (checkpoints)
    _cp_type = type(kernel._checkpointer).__name__ if kernel else "none"
    _cp_is_postgres = _cp_type == "AsyncPostgresSaver"
    result["layers"]["checkpointer"] = {
        "status": "active" if _cp_is_postgres else "fallback",
        "type": _cp_type,
        "durable": _cp_is_postgres,
    }

    result["total_layers"] = len(result["layers"])
    active = sum(1 for v in result["layers"].values() if v.get("status") in ("active", "not_configured"))
    result["active_layers"] = active
    return result


# ── Sprint 23: Knowledge Ingest + Query Endpoints ────────────────


class IngestRequest(BaseModel):
    """Request body for document ingestion."""

    content: str = Field(..., min_length=10, description="Document text to ingest")
    source: Optional[str] = Field(None, description="Source identifier (filename, URL, etc.)")
    doc_type: Optional[str] = Field(None, description="Document type (pdf, markdown, text, etc.)")


class KnowledgeQueryRequest(BaseModel):
    """Request body for knowledge graph query."""

    query: str = Field(..., min_length=3, description="Natural language query")
    mode: str = Field("hybrid", description="Retrieval mode: local, global, hybrid, naive")
    top_k: int = Field(5, ge=1, le=20, description="Max results")


@app.post("/v1/knowledge/ingest", tags=["knowledge"])
async def knowledge_ingest(req: IngestRequest, request: Request):
    """Ingest a document into the LightRAG knowledge graph. Sprint 23."""
    try:
        from memory.lightrag_bridge import ingest_document

        result = await ingest_document(
            content=req.content,
            metadata={"source": req.source, "doc_type": req.doc_type},
        )
        if result.get("ingested"):
            return {"status": "ok", **result}
        return {"status": "error", **result}
    except Exception as e:
        logger.error("knowledge_ingest_endpoint_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/knowledge/query", tags=["knowledge"])
async def knowledge_query(req: KnowledgeQueryRequest, request: Request):
    """Query the LightRAG knowledge graph. Sprint 23."""
    try:
        from memory.lightrag_bridge import query_knowledge

        result = await query_knowledge(
            query=req.query,
            mode=req.mode,
            top_k=req.top_k,
        )
        return {"status": "ok", **result}
    except Exception as e:
        logger.error("knowledge_query_endpoint_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/agents/status", tags=["agents"])
async def agents_status():
    """Return Multi-Agent Dispatcher registry status. Sprint 19."""
    try:
        from kernel.multi_agent import get_registry_status

        return get_registry_status()
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ── Sprint 21: FinOps Status Endpoint ──────────────────────────


@app.get("/v1/finops/status", tags=["finops"])
async def finops_status(request: Request):
    """Return FinOps controller status: daily spend, limits, alerts.

    Sprint 21: Registered route. Previously returned 404.
    Requires valid auth (same as other /v1/* endpoints).
    """
    finops = getattr(app.state, "finops", None)
    if not finops:
        return {
            "status": "unavailable",
            "reason": "FinOps controller not initialized",
            "hint": "Ensure FINOPS_DAILY_LIMIT_USD is set in environment",
        }
    try:
        status = finops.get_status()
        return {"status": "active", **status}
    except Exception as e:
        return {"status": "error", "error": str(e)}


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
            {
                "role": "system",
                "content": "You are an assistant. Use web_search for current data.",
            },
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
                    "google": lambda: client._call_google(
                        model_id=model_id,
                        api_key=api_key,
                        messages=test_messages,
                        temperature=0.1,
                        max_tokens=200,
                        tools=[test_tool],
                        tool_choice="auto",
                    ),
                    "openai": lambda: client._call_openai(
                        model_id=model_id,
                        api_key=api_key,
                        messages=test_messages,
                        temperature=0.1,
                        max_tokens=200,
                        tools=[test_tool],
                        tool_choice="auto",
                    ),
                    "anthropic": lambda: client._call_anthropic(
                        model_id=model_id,
                        api_key=api_key,
                        messages=test_messages,
                        temperature=0.1,
                        max_tokens=200,
                        tools=[test_tool],
                        tool_choice="auto",
                    ),
                    "openai_compat": lambda: client._call_openai_compat(
                        model_id=model_id,
                        api_key=api_key,
                        base_url="https://api.x.ai/v1",
                        messages=test_messages,
                        temperature=0.1,
                        max_tokens=200,
                        tools=[test_tool],
                        tool_choice="auto",
                    ),
                }[provider]
                resp = await call_method()
                results[name] = {
                    "status": "OK",
                    "model": model_id,
                    "finish_reason": resp.finish_reason,
                    "has_tool_calls": len(resp.tool_calls) > 0,
                    "tool_calls": [{"name": tc.name, "args": tc.arguments} for tc in resp.tool_calls],
                    "content_preview": resp.content[:100] if resp.content else "",
                    "usage": resp.usage,
                }
            except Exception as e:
                results[name] = {
                    "status": "ERROR",
                    "model": model_id,
                    "error": str(e),
                    "traceback": traceback.format_exc()[-500:],
                }
        return {"debug_tool_calling": results}

    @application.get("/v1/debug/error_log", tags=["debug"])
    async def debug_error_log(request: Request):
        """Return the in-memory error log from the fallback chain."""
        from router.engine import _TOOL_ERROR_LOG

        return {"error_count": len(_TOOL_ERROR_LOG), "errors": list(_TOOL_ERROR_LOG)}


if _DEBUG_MODE:
    _register_debug_endpoints(app)
    structlog.get_logger("monstruo").info("debug_endpoints_registered", mode="DEBUG")
