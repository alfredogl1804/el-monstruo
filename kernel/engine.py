"""
El Monstruo — Kernel Engine (LangGraph Rewrite)
=================================================
Sovereign kernel that uses LangGraph as the internal execution motor
while exposing the KernelInterface contract.

Architecture:
    KernelInterface (OUR contract)
        └── LangGraphKernel (this file)
                └── StateGraph (LangGraph motor)
                        └── 8 nodes (kernel/nodes.py) — Sprint 19
                        └── Multi-Agent Dispatcher (kernel/multi_agent.py)
                        └── MemPalace Bridge (memory/mempalace_bridge.py)

Principio: LangGraph es un motor intercambiable.
Los contratos soberanos son permanentes.
"""

from __future__ import annotations

import time
from typing import Any, AsyncIterator, Callable
from uuid import UUID

import structlog
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

# PostgresSaver for durable state (Sprint 2)
# Falls back to MemorySaver if SUPABASE_DB_URL is not set
try:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver  # noqa: F401

    _HAS_POSTGRES_SAVER = True
except ImportError:
    _HAS_POSTGRES_SAVER = False

from contracts.event_envelope import EventBuilder, EventCategory, Severity
from contracts.kernel_interface import (
    IntentType,
    KernelInterface,
    RunInput,
    RunOutput,
    RunStatus,
)
from kernel.hitl import hitl_review
from kernel.nodes import (
    classify_and_route,
    enrich,
    execute,
    intake,
    memory_write,
    respond,
    should_enrich,
)
from kernel.state import MonstruoState
from kernel.tool_dispatch import tool_dispatch

logger = structlog.get_logger("kernel.engine")


class LangGraphKernel(KernelInterface):
    """
    Sovereign kernel implementation backed by LangGraph.

    The KernelInterface is OUR contract — it defines what the kernel
    can do. LangGraph is the motor that executes the graph internally.
    If LangGraph dies tomorrow, we swap the motor, not the interface.

    Graph topology (Sprint 2 — Las Manos):
        intake → classify_and_route → [enrich] → execute
        → [tool_dispatch → execute]* → [hitl_review] → respond → memory_write
        * = tool calling loop (max 3 iterations)
    """

    def __init__(
        self,
        router: Any = None,
        event_store: Any = None,
        memory: Any = None,
        knowledge: Any = None,
        checkpoint_store: Any = None,
        observability: Any = None,
        checkpointer: Any = None,
        db: Any = None,
    ) -> None:
        self._router = router
        self._event_store = event_store
        self._memory = memory
        self._knowledge = knowledge
        self._checkpoint_store = checkpoint_store
        self._observability = observability
        self._db = db  # Sprint 9: SupabaseClient for dossier injection
        self._usage_tracker = None  # Sprint 10: injected post-init
        self._tool_registry = None  # Sprint 10: injected post-init
        self._finops = None  # Sprint 15: FinOps controller
        self._hooks: dict[str, list[Callable[..., Any]]] = {}
        self._runs: dict[UUID, MonstruoState] = {}

        # Use injected checkpointer (PostgresSaver) or fallback to MemorySaver
        self._checkpointer = checkpointer or MemorySaver()
        self._graph = self._build_graph()
        self._compiled = self._graph.compile(
            checkpointer=self._checkpointer,
        )

        # Sprint 15: Apply recursion_limit to prevent runaway graphs
        self._compiled.recursion_limit = 25

        # Sprint 4: Streaming graph — interrupts before execute for real LLM streaming
        self._compiled_streaming = self._graph.compile(
            checkpointer=self._checkpointer,
            interrupt_before=["execute"],
        )

        checkpointer_type = type(self._checkpointer).__name__
        logger.info(
            "kernel_initialized",
            motor="langgraph",
            version="1.1.8",
            checkpointer=checkpointer_type,
        )

    @staticmethod
    def _should_dispatch_tools_fn(state: MonstruoState) -> str:
        """Unified conditional edge after execute (merges tool loop + HITL gate).

        Returns:
            "tool_dispatch" — LLM wants tools and we haven't exceeded max loops
            "hitl_review"  — HITL approval required
            "respond"      — normal flow, go to respond
        """
        from contracts.kernel_interface import RunStatus

        # 1. Check for tools first (tool loop takes priority)
        pending = state.get("pending_tool_calls", [])
        loop_count = state.get("tool_loop_count", 0)

        if pending and loop_count < 5:  # MAX_TOOL_LOOPS = 5 (Sprint 15: raised from 3)
            return "tool_dispatch"

        # 2. Error flow: skip HITL, go to respond
        status = state.get("status", "")
        if status == RunStatus.FAILED.value:
            return "respond"

        # 3. Check HITL gate
        policy_decision = state.get("policy_decision")
        needs_approval = state.get("needs_human_approval", False)

        if policy_decision == "HITL" or needs_approval:
            return "hitl_review"

        # 4. Normal flow
        return "respond"

    def _build_graph(self) -> StateGraph:
        """
        Build the sovereign execution graph (Sprint 2 — Las Manos).

        8 nodes, 2 conditional edges:
            intake → classify_and_route → should_enrich? → execute
            execute → should_dispatch? → tool_dispatch → execute  (loop, max 3)
            execute → should_dispatch? → hitl_review → respond  (HITL path)
            execute → should_dispatch? → respond → memory_write  (normal path)

        Sprint 2 additions:
            - tool_dispatch node executes tools the LLM requested
            - should_loop_tools conditional edge creates the tool calling loop
            - Max 3 loops to prevent runaway chains

        Optimizations:
            - OPT-1: classify + route fused into single node (-800ms)
            - OPT-2: Enrich parallelizes memory lookups
            - OPT-3: Smart fast-path skips enrich for simple queries
            - OPT-5: respond BEFORE memory_write (user gets response faster)
            - OPT-6: Intent classification cached
        """
        graph = StateGraph(MonstruoState)

        # Add all 8 nodes
        graph.add_node("intake", intake)
        graph.add_node("classify_and_route", classify_and_route)
        graph.add_node("enrich", enrich)
        graph.add_node("execute", execute)
        graph.add_node("tool_dispatch", tool_dispatch)  # Sprint 2: Las Manos
        graph.add_node("hitl_review", hitl_review)  # HITL — real LangGraph interrupt()
        graph.add_node("respond", respond)
        graph.add_node("memory_write", memory_write)

        # Set entry point
        graph.set_entry_point("intake")

        # Linear edge: intake → classify_and_route (OPT-1: single node)
        graph.add_edge("intake", "classify_and_route")

        # Conditional: classify_and_route → enrich or execute (OPT-3: fast-path)
        graph.add_conditional_edges(
            "classify_and_route",
            should_enrich,
            {
                "enrich": "enrich",
                "execute": "execute",
            },
        )

        # enrich always goes to execute
        graph.add_edge("enrich", "execute")

        # ── Sprint 2: Tool Calling Loop ──────────────────────────────
        # Canonical ReAct pattern (validated against langchain-ai/react-agent
        # and ai.google.dev/gemini-api/docs/langgraph-example, 2026-04-16):
        #   execute → should_dispatch_tools? → tool_dispatch → execute (loop)
        #   execute → should_dispatch_tools? → hitl_review → respond (HITL path)
        #   execute → should_dispatch_tools? → respond (normal path)
        graph.add_conditional_edges(
            "execute",
            LangGraphKernel._should_dispatch_tools_fn,
            {
                "tool_dispatch": "tool_dispatch",  # LLM wants tools → dispatch
                "hitl_review": "hitl_review",  # HITL needed → review
                "respond": "respond",  # Normal → respond
            },
        )

        # tool_dispatch always loops back to execute (canonical: tools → llm)
        graph.add_edge("tool_dispatch", "execute")

        # hitl_review always goes to respond (after human approves/rejects)
        graph.add_edge("hitl_review", "respond")

        # OPT-5: respond → memory_write → END
        graph.add_edge("respond", "memory_write")
        graph.add_edge("memory_write", END)

        return graph

    # ── KernelInterface Implementation ─────────────────────────────

    async def start_run(self, input: RunInput) -> RunOutput:
        """
        Execute a complete run through the LangGraph graph.
        This is the main entry point — message in, response out.
        """
        run_id = input.run_id
        thread_id = str(run_id)

        # Sprint 15: Budget hard stop — block run if daily budget exceeded
        if self._finops:
            budget_check = self._finops.check_budget()
            if not budget_check.get("allowed", True):
                logger.warning(
                    "run_blocked_budget",
                    run_id=str(run_id),
                    reason=budget_check["reason"],
                )
                return RunOutput(
                    run_id=run_id,
                    status=RunStatus.FAILED,
                    intent=IntentType.CHAT,
                    model_used="",
                    response=f"Run blocked: {budget_check['reason']}. Contact admin.",
                    metadata={"budget_block": True, **budget_check},
                )

        # Sprint 33D: Reset circuit breaker at start of each new run
        # Without this, input_hashes accumulate across runs and the
        # circuit breaker blocks legitimate tool calls after 2-3 attempts.
        from kernel.tool_dispatch import get_tool_broker
        broker = get_tool_broker()
        if broker:
            broker.reset_run_state()

        # Fire pre-hooks
        await self._fire_hook("pre_route", run_id, input)

        # Build initial state — NO non-serializable objects here
        initial_state: MonstruoState = {
            "run_id": str(run_id),
            "user_id": input.user_id,
            "channel": input.channel,
            "message": input.message,
            "attachments": input.attachments or [],
            "context": input.context or {},
            "parent_run_id": str(input.parent_run_id) if input.parent_run_id else None,
        }

        # Store run reference
        self._runs[run_id] = initial_state

        try:
            # Dependencies go in config["configurable"], NOT in state
            # LangGraph never serializes config, only state
            config: dict[str, Any] = {
                "configurable": {
                    "thread_id": thread_id,
                    "_router": self._router,
                    "_memory": self._memory,
                    "_knowledge": self._knowledge,
                    "_event_store": self._event_store,
                    "_observability": self._observability,
                    "_db": self._db,  # Sprint 9: for dossier injection
                }
            }

            # ── Sprint 13: Langfuse CallbackHandler for deep tracing ──────
            # Injects langfuse.langchain.CallbackHandler into LangGraph config
            # so every node execution, LLM call, and tool invocation is
            # automatically traced in Langfuse with full nesting.
            if self._observability:
                langfuse_handler = self._observability.get_callback_handler()
                if langfuse_handler:
                    config["callbacks"] = [langfuse_handler]
                    # Propagate session_id and user_id via metadata
                    # (Langfuse v4 pattern: metadata.langfuse_session_id)
                    session_id = input.context.get("session_id", "") if input.context else ""
                    config["metadata"] = {
                        "langfuse_session_id": session_id or str(run_id),
                        "langfuse_user_id": input.user_id,
                    }
                    logger.debug("langfuse_callback_injected", run_id=str(run_id))

            # Use v2 API to properly detect interrupts (validated 2026-04-14)
            # In v2, ainvoke returns GraphOutput with .value and .interrupts
            # instead of raising GraphInterrupt exception
            result = await self._compiled.ainvoke(initial_state, config, version="v2")

            # ── Check for HITL interrupt ──────────────────────────────
            if result.interrupts:
                # Graph paused at interrupt() — HITL review needed
                interrupt_payloads = [i.value if hasattr(i, "value") else str(i) for i in result.interrupts]
                final_state = result.value
                self._runs[run_id] = final_state

                # Update state to reflect AWAITING_HUMAN
                final_state["status"] = RunStatus.AWAITING_HUMAN.value
                self._runs[run_id] = final_state

                intent_str = final_state.get("intent", IntentType.CHAT.value)
                try:
                    intent = IntentType(intent_str)
                except ValueError:
                    intent = IntentType.CHAT

                logger.info(
                    "run_awaiting_human",
                    run_id=str(run_id),
                    intent=intent.value,
                    interrupt_count=len(result.interrupts),
                )

                return RunOutput(
                    run_id=run_id,
                    status=RunStatus.AWAITING_HUMAN,
                    intent=intent,
                    model_used=final_state.get("model_used", ""),
                    response=final_state.get("response", ""),
                    tokens_in=final_state.get("tokens_in", 0),
                    tokens_out=final_state.get("tokens_out", 0),
                    cost_usd=final_state.get("cost_usd", 0.0),
                    latency_ms=final_state.get("latency_ms", 0.0),
                    metadata={
                        "interrupt_payload": interrupt_payloads[0] if interrupt_payloads else {},
                        "interrupt_count": len(interrupt_payloads),
                        "enriched": final_state.get("enriched", False),
                        "route_reason": final_state.get("route_reason", ""),
                    },
                )

            # ── Normal completion (no interrupt) ─────────────────────
            final_state = result.value

            # Update stored state
            self._runs[run_id] = final_state

            # Fire post-hooks
            await self._fire_hook("post_execute", run_id, final_state)

            # Build output
            status_str = final_state.get("status", RunStatus.COMPLETED.value)
            try:
                status = RunStatus(status_str)
            except ValueError:
                status = RunStatus.COMPLETED

            intent_str = final_state.get("intent", IntentType.CHAT.value)
            try:
                intent = IntentType(intent_str)
            except ValueError:
                intent = IntentType.CHAT

            output = RunOutput(
                run_id=run_id,
                status=status,
                intent=intent,
                model_used=final_state.get("model_used", ""),
                response=final_state.get("final_response", ""),
                tokens_in=final_state.get("tokens_in", 0),
                tokens_out=final_state.get("tokens_out", 0),
                cost_usd=final_state.get("cost_usd", 0.0),
                latency_ms=final_state.get("latency_ms", 0.0),
                tool_calls=final_state.get("tool_calls", []),
                metadata={
                    "enriched": final_state.get("enriched", False),
                    "memory_written": final_state.get("memory_written", False),
                    "execution_attempts": final_state.get("execution_attempts", 0),
                    "route_reason": final_state.get("route_reason", ""),
                    "events_count": len(final_state.get("events", [])),
                },
            )

            logger.info(
                "run_completed",
                run_id=str(run_id),
                status=status.value,
                intent=intent.value,
                model=output.model_used,
                latency_ms=f"{output.latency_ms:.0f}",
            )

            # Sprint 10: Log usage to persistent tracker
            await self._log_usage(output, final_state)

            # Sprint 15: Record per-run cost in FinOps
            if self._finops:
                await self._finops.record_run_cost(
                    run_id=str(run_id),
                    model_used=output.model_used or "unknown",
                    tokens_in=output.tokens_in,
                    tokens_out=output.tokens_out,
                    cost_usd=output.cost_usd,
                    latency_ms=int(output.latency_ms),
                    tool_count=len(output.tool_calls or []),
                    status="completed",
                )

            return output

        except Exception as e:
            logger.error("run_failed", run_id=str(run_id), error=str(e))
            await self._fire_hook("on_error", run_id, e)

            # Emit failure event
            if self._event_store:
                event = (
                    EventBuilder()
                    .category(EventCategory.RUN_FAILED)
                    .severity(Severity.ERROR)
                    .actor("kernel.engine")
                    .action(f"Run failed: {str(e)[:200]}")
                    .for_run(run_id)
                    .with_payload({"error": str(e), "error_type": type(e).__name__})
                    .build()
                )
                await self._event_store.append(event)

            error_output = RunOutput(
                run_id=run_id,
                status=RunStatus.FAILED,
                intent=IntentType.CHAT,
                model_used="",
                response=f"Error: {str(e)}",
                metadata={"error": str(e), "error_type": type(e).__name__},
            )
            # Sprint 10: Log failed request too
            await self._log_usage(error_output, {}, status="failed", error_message=str(e))
            return error_output

    async def _log_usage(
        self,
        output: RunOutput,
        state: dict,
        status: str = "completed",
        error_message: str = "",
    ) -> None:
        """Sprint 10: Log request to UsageTracker and record tool invocations."""
        try:
            if self._usage_tracker:
                # Determine provider from model_catalog
                provider = ""
                try:
                    from config.model_catalog import MODELS

                    model_info = MODELS.get(output.model_used, {})
                    provider = model_info.get("provider", "")
                except Exception:
                    pass

                await self._usage_tracker.log_request(
                    thread_id=state.get("thread_id", ""),
                    model_used=output.model_used or "unknown",
                    provider=provider,
                    role_used=state.get("role_used", ""),
                    tokens_in=output.tokens_in,
                    tokens_out=output.tokens_out,
                    cost_usd=output.cost_usd,
                    latency_ms=int(output.latency_ms),
                    tool_calls=[
                        tc.get("name", "") if isinstance(tc, dict) else str(tc) for tc in (output.tool_calls or [])
                    ],
                    status=status,
                    error_message=error_message,
                )

            # Record tool invocations in registry
            if self._tool_registry and output.tool_calls:
                for tc in output.tool_calls:
                    tool_name = tc.get("name", "") if isinstance(tc, dict) else str(tc)
                    if tool_name:
                        await self._tool_registry.record_invocation(tool_name)
        except Exception as e:
            logger.warning("usage_tracking_failed", error=str(e))

    async def step(self, run_id: UUID, input: dict[str, Any] | None = None) -> RunOutput:
        """
        Continue a paused run (after HITL interrupt).
        Uses LangGraph Command(resume=...) to resume from interrupt().
        """
        from langgraph.types import Command

        thread_id = str(run_id)
        config = {
            "configurable": {
                "thread_id": thread_id,
                "_router": self._router,
                "_memory": self._memory,
                "_knowledge": self._knowledge,
                "_event_store": self._event_store,
                "_observability": self._observability,
                "_db": self._db,
            }
        }

        # Build resume payload for Command
        resume_value = {"decision": "approve"}  # default
        if input:
            resume_value = {
                "decision": input.get("decision", input.get("response", "approve")),
                "modification": input.get("modification"),
            }

        try:
            # Resume the graph using LangGraph Command(resume=...) with v2 API
            # validated 2026-04-14 against LangGraph 1.1.6 docs
            result = await self._compiled.ainvoke(Command(resume=resume_value), config, version="v2")

            # Check if another interrupt was triggered (multi-step HITL)
            if result.interrupts:
                interrupt_payloads = [i.value if hasattr(i, "value") else str(i) for i in result.interrupts]
                final_state = result.value
                final_state["status"] = RunStatus.AWAITING_HUMAN.value
                self._runs[run_id] = final_state

                return RunOutput(
                    run_id=run_id,
                    status=RunStatus.AWAITING_HUMAN,
                    intent=IntentType(final_state.get("intent", IntentType.CHAT.value)),
                    model_used=final_state.get("model_used", ""),
                    response=final_state.get("response", ""),
                    metadata={"interrupt_payload": interrupt_payloads[0] if interrupt_payloads else {}},
                )

            final_state = result.value
            self._runs[run_id] = final_state

            status_str = final_state.get("status", RunStatus.COMPLETED.value)
            try:
                status = RunStatus(status_str)
            except ValueError:
                status = RunStatus.COMPLETED

            intent_str = final_state.get("intent", IntentType.CHAT.value)
            try:
                intent = IntentType(intent_str)
            except ValueError:
                intent = IntentType.CHAT

            return RunOutput(
                run_id=run_id,
                status=status,
                intent=intent,
                model_used=final_state.get("model_used", ""),
                response=final_state.get("final_response", ""),
            )
        except Exception as e:
            logger.error("step_failed", run_id=str(run_id), error=str(e))
            return RunOutput(
                run_id=run_id,
                status=RunStatus.FAILED,
                intent=IntentType.CHAT,
                model_used="",
                response=f"Step error: {str(e)}",
            )

    async def checkpoint(self, run_id: UUID) -> Any:
        """
        Create a checkpoint of the current run state.
        LangGraph handles this internally via PostgresSaver (or MemorySaver fallback).
        We also persist to our sovereign CheckpointStore.
        """
        state = self._runs.get(run_id)
        if not state:
            raise ValueError(f"Run {run_id} not found")

        if self._checkpoint_store:
            from contracts.checkpoint_model import Checkpoint, CheckpointType

            cp = Checkpoint(
                run_id=run_id,
                checkpoint_type=CheckpointType.MANUAL,
                state=dict(state),
                step=state.get("step_count", 0),
            )
            await self._checkpoint_store.save(cp)
            logger.info("checkpoint_saved", run_id=str(run_id))
            return cp

        return state

    async def resume(self, run_id: UUID) -> RunOutput:
        """Resume a run from its last checkpoint."""
        return await self.step(run_id)

    async def cancel(self, run_id: UUID, reason: str = "") -> bool:
        """Kill switch: cancel a run immediately."""
        state = self._runs.get(run_id)
        if not state:
            return False

        current_status = state.get("status", "")
        if current_status in (
            RunStatus.COMPLETED.value,
            RunStatus.FAILED.value,
            RunStatus.CANCELLED.value,
        ):
            return False

        # Update state
        state["cancelled"] = True
        state["cancel_reason"] = reason
        state["status"] = RunStatus.CANCELLED.value
        self._runs[run_id] = state

        # Emit cancellation event
        if self._event_store:
            event = (
                EventBuilder()
                .category(EventCategory.RUN_CANCELLED)
                .actor("kernel.engine")
                .action(f"Run cancelled: {reason or 'no reason given'}")
                .for_run(run_id)
                .with_payload({"reason": reason})
                .build()
            )
            await self._event_store.append(event)

        await self._fire_hook("on_cancel", run_id, reason)
        logger.warning("run_cancelled", run_id=str(run_id), reason=reason)
        return True

    async def stream(self, input: RunInput) -> AsyncIterator[str]:
        """
        Sprint 4 → Sprint 42: REAL streaming via interrupt_before=["execute"].

        Strategy (validated by 6 Sabios consensus + Sprint 42 streaming fix):
          Phase 1: Run pre-LLM nodes (intake → classify → enrich) via streaming graph
          Phase 2: Graph interrupts before execute → extract enriched state
          Phase 3: Call router.execute_stream() directly → yield real LLM tokens
          Phase 4: Inject response into state via update_state() → resume for post-LLM
          Phase 5: Post-LLM nodes (respond → memory_write) run to completion

        Sprint 42 Fix: Yield progress events between phases to prevent
        Railway proxy buffering. The adapter layer (agui_adapter.py) also
        sends heartbeat comments every 3s during gaps.

        Fallback policy: only before first token. After first token, fail gracefully.
        Memory write: blocked if stream fails (no partial contamination).

        Yields JSON-encoded SSE events:
          {"type": "meta", "intent": ..., "model": ..., "enriched": ...}
          {"type": "progress", "phase": ..., "detail": ...}
          {"type": "chunk", "text": "..."}
          {"type": "done", "latency_ms": ..., "model_used": ..., "tokens_in": ..., "tokens_out": ...}
          {"type": "error", "message": "..."}
        """
        import json as _json

        run_id = input.run_id
        # Use a unique thread_id for streaming to avoid checkpoint conflicts
        thread_id = f"stream-{run_id}"
        start_time = time.monotonic()

        initial_state: MonstruoState = {
            "run_id": str(run_id),
            "user_id": input.user_id,
            "channel": input.channel,
            "message": input.message,
            "attachments": input.attachments or [],
            "context": input.context or {},
        }

        config = {
            "configurable": {
                "thread_id": thread_id,
                "_router": self._router,
                "_memory": self._memory,
                "_knowledge": self._knowledge,
                "_event_store": self._event_store,
                "_observability": self._observability,
                "_db": self._db,
            }
        }

        try:
            # ══ Phase 0: Immediate step event ═══════════════════════════════
            # Sprint 42+43: Structured step events for thinking indicator
            yield _json.dumps({"type": "step", "id": "classify", "status": "in_progress", "label": "Analizando solicitud...", "icon": "brain"})

            # ══ Phase 1: Run pre-LLM nodes ══════════════════════════════════════════
            # Graph runs intake → classify_and_route → enrich, then STOPS before execute
            logger.info("stream_phase1_start", run_id=str(run_id))

            pre_llm_state = dict(initial_state)
            async for event in self._compiled_streaming.astream(initial_state, config, stream_mode="updates"):
                for node_name, state_update in event.items():
                    pre_llm_state.update(state_update)

                    if node_name == "classify_and_route":
                        # Step: classify completed
                        yield _json.dumps({"type": "step", "id": "classify", "status": "completed", "label": "Solicitud analizada", "icon": "brain"})
                        # Meta event for model/intent (backward compat)
                        yield _json.dumps(
                            {
                                "type": "meta",
                                "intent": state_update.get("intent", "chat"),
                                "model": state_update.get("model", "unknown"),
                                "enriched": False,
                            }
                        )
                        # Step: enrich starting
                        yield _json.dumps({"type": "step", "id": "enrich", "status": "in_progress", "label": "Buscando en tu memoria...", "icon": "memory"})

                    elif node_name == "enrich":
                        # Step: enrich completed
                        yield _json.dumps({"type": "step", "id": "enrich", "status": "completed", "label": "Contexto preparado", "icon": "memory"})
                        # Meta event (backward compat)
                        yield _json.dumps(
                            {
                                "type": "meta",
                                "enriched": state_update.get("enriched", False),
                                "memories_found": len(state_update.get("relevant_memories", [])),
                            }
                        )

            # Sprint 42+43: Step event — context extraction phase
            # (no separate step needed — enrich already completed above)

            # ══ Phase 2: Extract enriched state from checkpoint ════════════════════
            # Graph is now paused before execute. Read the full state.
            graph_state = await self._compiled_streaming.aget_state(config)
            current_state = graph_state.values if graph_state else pre_llm_state

            model = current_state.get("model", "gpt-5.5")
            intent = current_state.get("intent", "chat")
            system_prompt = current_state.get("system_prompt", "")
            conversation_context = current_state.get("conversation_context", [])
            message = current_state.get("message", input.message)

            logger.info(
                "stream_phase2_state_extracted",
                run_id=str(run_id),
                model=model,
                intent=intent,
                has_system_prompt=bool(system_prompt),
                history_len=len(conversation_context),
            )

            # Build enriched context for the router
            enriched_context = dict(current_state.get("context", {}))
            if conversation_context:
                enriched_context["history"] = conversation_context
            if system_prompt:
                enriched_context["system_prompt"] = system_prompt

            # ══ Sprint 46.1 + Sprint 48 Fix: Task Planner Bifurcation ════════════
            # If intent is EXECUTE and the task is complex, delegate to Task Planner
            # which will plan, execute tools, and stream step/tool/chunk events.
            # Sprint 48: Fixed — no longer falls through silently on error.
            if intent == "execute":
                try:
                    from kernel.task_planner import TaskPlanner
                    _planner = TaskPlanner(kernel=self, db=self._db)
                    if _planner.is_complex_objective(message):
                        logger.info(
                            "stream_bifurcate_to_planner",
                            run_id=str(run_id),
                            message_preview=message[:80],
                        )
                        yield _json.dumps({"type": "step", "id": "generate", "status": "in_progress", "label": "Ejecutando tarea autónoma...", "icon": "build"})

                        async for event in _planner.stream_plan_and_execute(
                            objective=message,
                            context=enriched_context,
                            user_id=input.user_id,
                            enriched_context=enriched_context,
                        ):
                            # Parse to check if it's a done event
                            try:
                                parsed = _json.loads(event)
                                if parsed.get("type") == "done":
                                    # Inject additional metadata
                                    parsed["intent"] = intent
                                    parsed["streaming"] = True
                                    yield _json.dumps(parsed)
                                else:
                                    yield event
                            except (ValueError, KeyError):
                                yield event

                        # Write memory after task planner completes
                        try:
                            await self._compiled_streaming.aupdate_state(
                                config,
                                {
                                    "response": "[Task Planner executed autonomously]",
                                    "model_used": model,
                                    "status": RunStatus.DONE.value,
                                },
                                as_node="execute",
                            )
                            async for event in self._compiled_streaming.astream(None, config, stream_mode="updates"):
                                pass  # Let memory_write run silently
                        except Exception as mem_err:
                            logger.warning("stream_planner_memory_write_failed", error=str(mem_err))

                        return  # Task Planner handled everything
                except ImportError as ie:
                    logger.error("stream_planner_import_failed", error=str(ie))
                    # ImportError is fatal — report to user, don't fall through
                    yield _json.dumps({"type": "chunk", "text": f"Error interno: módulo del Task Planner no disponible ({ie}). Contacta al desarrollador."})
                    yield _json.dumps({"type": "done", "error": str(ie), "intent": intent})
                    return
                except Exception as planner_err:
                    import traceback
                    tb = traceback.format_exc()
                    logger.error(
                        "stream_planner_bifurcation_failed",
                        error=str(planner_err),
                        traceback=tb,
                        run_id=str(run_id),
                    )
                    # Sprint 48: Report error to user instead of silent fallback
                    yield _json.dumps({"type": "chunk", "text": f"Error en el Task Planner: {str(planner_err)[:200]}. Reintentando con flujo directo..."})
                    # Still fall through to normal LLM as graceful degradation,
                    # but now with full logging and user notification

            # Sprint 42+43: Step event — LLM generation starting
            yield _json.dumps({"type": "step", "id": "generate", "status": "in_progress", "label": f"Pensando con {model}...", "icon": "sparkles"})

            # ══ Phase 3: REAL LLM Streaming ═════════════════════════════════════
            # Call router.execute_stream() directly — yields real LLM tokens
            logger.info("stream_phase3_llm_start", run_id=str(run_id), model=model)
            llm_start = time.monotonic()

            accumulated_response = ""
            first_token_emitted = False
            stream_failed = False

            try:
                if self._router and hasattr(self._router, "execute_stream"):
                    async for chunk in self._router.execute_stream(
                        message=message,
                        model=model,
                        intent=IntentType(intent),
                        context=enriched_context,
                    ):
                        accumulated_response += chunk
                        first_token_emitted = True
                        yield _json.dumps({"type": "chunk", "text": chunk})
                elif self._router:
                    # Fallback: non-streaming execute, then fake-stream
                    logger.warning("stream_fallback_to_sync", run_id=str(run_id))
                    response, usage = await self._router.execute(message, model, IntentType(intent), enriched_context)
                    accumulated_response = response
                    # Emit in one chunk
                    yield _json.dumps({"type": "chunk", "text": response})
                    first_token_emitted = True
                else:
                    # Sprint 38: router no disponible — error real en lugar de stub silencioso
                    logger.error("stream_no_router", run_id=str(run_id), model=model)
                    yield _json.dumps({
                        "type": "error",
                        "message": "Router no disponible. El sistema no puede procesar la solicitud en este momento.",
                    })
                    return

            except Exception as llm_err:
                stream_failed = True
                logger.error(
                    "stream_llm_failed",
                    run_id=str(run_id),
                    model=model,
                    error=str(llm_err),
                    first_token_emitted=first_token_emitted,
                )
                if not first_token_emitted:
                    # Fallback policy: before first token, we can retry or error
                    yield _json.dumps(
                        {
                            "type": "error",
                            "message": f"LLM streaming failed: {type(llm_err).__name__}",
                        }
                    )
                    return
                else:
                    # After first token: graceful termination
                    yield _json.dumps(
                        {
                            "type": "error",
                            "message": "Stream interrupted. Partial response delivered.",
                        }
                    )

            llm_elapsed_ms = (time.monotonic() - llm_start) * 1000
            logger.info(
                "stream_phase3_llm_done",
                run_id=str(run_id),
                response_len=len(accumulated_response),
                llm_latency_ms=round(llm_elapsed_ms),
                stream_failed=stream_failed,
            )

            # ══ Phase 4: Inject response and resume graph ═════════════════════
            # Update state with the streamed response, then let post-LLM nodes run
            if not stream_failed and accumulated_response:
                try:
                    await self._compiled_streaming.aupdate_state(
                        config,
                        {
                            "response": accumulated_response,
                            "model_used": model,
                            "status": RunStatus.EXECUTING.value,
                            "latency_ms": llm_elapsed_ms,
                            # Note: token counts from streaming are estimated;
                            # exact counts come from provider callbacks
                            "tokens_in": 0,
                            "tokens_out": 0,
                            "cost_usd": 0.0,
                        },
                        as_node="execute",  # Pretend this update came from execute node
                    )

                    # ══ Phase 5: Run post-LLM nodes (respond → memory_write) ══════
                    # Resume the graph — it will run respond → memory_write → END
                    logger.info("stream_phase5_post_llm", run_id=str(run_id))
                    async for event in self._compiled_streaming.astream(None, config, stream_mode="updates"):
                        # Post-LLM nodes run silently; we don't yield their output
                        for node_name, state_update in event.items():
                            if node_name == "respond":
                                # Capture final state for done event
                                pre_llm_state.update(state_update)
                            elif node_name == "memory_write":
                                pre_llm_state.update(state_update)

                except Exception as post_err:
                    # Post-LLM failure shouldn't affect the user's response
                    logger.error(
                        "stream_post_llm_failed",
                        run_id=str(run_id),
                        error=str(post_err),
                    )
            elif stream_failed:
                logger.warning(
                    "stream_memory_write_blocked",
                    run_id=str(run_id),
                    reason="stream_failed_no_contamination",
                )

            # ══ Emit done event ════════════════════════════════════════════════
            elapsed_ms = (time.monotonic() - start_time) * 1000
            yield _json.dumps(
                {
                    "type": "done",
                    "latency_ms": round(elapsed_ms),
                    "model_used": model,
                    "intent": intent,
                    "tokens_in": pre_llm_state.get("tokens_in", 0),
                    "tokens_out": pre_llm_state.get("tokens_out", 0),
                    "cost_usd": pre_llm_state.get("cost_usd", 0.0),
                    "streaming": True,
                }
            )

        except Exception as e:
            logger.error("stream_failed", run_id=str(run_id), error=str(e))
            yield _json.dumps({"type": "error", "message": str(e)})

    async def get_status(self, run_id: UUID) -> RunStatus:
        """Get current status of a run."""
        state = self._runs.get(run_id)
        if not state:
            raise ValueError(f"Run {run_id} not found")

        status_str = state.get("status", RunStatus.PENDING.value)
        try:
            return RunStatus(status_str)
        except ValueError:
            return RunStatus.PENDING

    async def register_hook(self, event: str, callback: Callable[..., Any]) -> None:
        """Register a lifecycle hook."""
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)
        logger.debug("hook_registered", hook_event=event)

    # ── Graph Visualization ────────────────────────────────────────

    def get_graph_mermaid(self) -> str:
        """Export the graph as Mermaid diagram for debugging."""
        try:
            return self._compiled.get_graph().draw_mermaid()
        except Exception:
            return "graph TD\n  A[intake] --> B[classify] --> C[route] --> D{enrich?} --> E[execute] --> F{HITL?} --> G[memory_write] --> H[respond]"  # noqa: E501

    def get_graph_ascii(self) -> str:
        """Export the graph as ASCII art."""
        try:
            return self._compiled.get_graph().draw_ascii()
        except Exception:
            return "intake → classify → route → enrich? → execute → HITL? → memory_write → respond"

    # ── Internal Methods ───────────────────────────────────────────

    async def _fire_hook(self, event: str, *args: Any) -> None:
        """Fire all registered hooks for an event."""
        for callback in self._hooks.get(event, []):
            try:
                result = callback(*args)
                if hasattr(result, "__await__"):
                    await result
            except Exception as e:
                logger.warning("hook_error", event=event, error=str(e))
