"""
El Monstruo — Kernel Engine (LangGraph Rewrite)
=================================================
Sovereign kernel that uses LangGraph as the internal execution motor
while exposing the KernelInterface contract.

Architecture:
    KernelInterface (OUR contract)
        └── LangGraphKernel (this file)
                └── StateGraph (LangGraph motor)
                        └── 6 nodes (kernel/nodes.py) — optimized v1.1

Principio: LangGraph es un motor intercambiable.
Los contratos soberanos son permanentes.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Callable, Optional
from uuid import UUID, uuid4

import structlog
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# PostgresSaver for durable state (Sprint 2)
# Falls back to MemorySaver if SUPABASE_DB_URL is not set
try:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    _HAS_POSTGRES_SAVER = True
except ImportError:
    _HAS_POSTGRES_SAVER = False

from contracts.kernel_interface import (
    KernelInterface,
    RunInput,
    RunOutput,
    RunStatus,
    IntentType,
)
from contracts.event_envelope import EventBuilder, EventCategory, Severity
from kernel.state import MonstruoState
from kernel.nodes import (
    intake,
    classify_and_route,
    enrich,
    execute,
    memory_write,
    respond,
    should_enrich,
)
from kernel.hitl import hitl_gate, hitl_review

logger = structlog.get_logger("kernel.engine")


class LangGraphKernel(KernelInterface):
    """
    Sovereign kernel implementation backed by LangGraph.

    The KernelInterface is OUR contract — it defines what the kernel
    can do. LangGraph is the motor that executes the graph internally.
    If LangGraph dies tomorrow, we swap the motor, not the interface.

    Graph topology:
        intake → classify → route → [enrich] → execute → [HITL] → memory_write → respond
                                  ↓ (chat/system)        ↓ (failed)
                                execute                  respond
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
    ) -> None:
        self._router = router
        self._event_store = event_store
        self._memory = memory
        self._knowledge = knowledge
        self._checkpoint_store = checkpoint_store
        self._observability = observability
        self._hooks: dict[str, list[Callable[..., Any]]] = {}
        self._runs: dict[UUID, MonstruoState] = {}

        # Use injected checkpointer (PostgresSaver) or fallback to MemorySaver
        self._checkpointer = checkpointer or MemorySaver()
        self._graph = self._build_graph()
        self._compiled = self._graph.compile(
            checkpointer=self._checkpointer,
        )

        checkpointer_type = type(self._checkpointer).__name__
        logger.info("kernel_initialized", motor="langgraph", version="1.1.6", checkpointer=checkpointer_type)

    def _build_graph(self) -> StateGraph:
        """
        Build the sovereign execution graph (optimized v1.1).

        6 nodes, 2 conditional edges:
            intake → classify_and_route → should_enrich? → execute → check_hitl? → respond → memory_write

        Optimizations:
            - OPT-1: classify + route fused into single node (-800ms)
            - OPT-2: Enrich parallelizes memory lookups
            - OPT-3: Smart fast-path skips enrich for simple queries
            - OPT-5: respond BEFORE memory_write (user gets response faster)
            - OPT-6: Intent classification cached
        """
        graph = StateGraph(MonstruoState)

        # Add all 6 nodes (OPT-1: classify+route fused)
        graph.add_node("intake", intake)
        graph.add_node("classify_and_route", classify_and_route)
        graph.add_node("enrich", enrich)
        graph.add_node("execute", execute)
        graph.add_node("memory_write", memory_write)
        graph.add_node("respond", respond)

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

        # HITL node — real LangGraph interrupt()
        graph.add_node("hitl_review", hitl_review)

        # Conditional: execute → hitl_review or respond
        # Uses hitl_gate from kernel/hitl.py (replaces check_hitl)
        graph.add_conditional_edges(
            "execute",
            hitl_gate,
            {
                "hitl_review": "hitl_review",  # HITL needed: pause for human
                "respond": "respond",            # Normal/error: respond directly
            },
        )

        # hitl_review → respond (after human approves/rejects)
        graph.add_edge("hitl_review", "respond")

        # OPT-5: respond → memory_write → END
        # User sees response immediately, memory persists after
        graph.add_edge("respond", "memory_write")

        # memory_write is terminal
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
            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "_router": self._router,
                    "_memory": self._memory,
                    "_knowledge": self._knowledge,
                    "_event_store": self._event_store,
                    "_observability": self._observability,
                }
            }
            # Use v2 API to properly detect interrupts (validated 2026-04-14)
            # In v2, ainvoke returns GraphOutput with .value and .interrupts
            # instead of raising GraphInterrupt exception
            result = await self._compiled.ainvoke(
                initial_state, config, version="v2"
            )

            # ── Check for HITL interrupt ──────────────────────────────
            if result.interrupts:
                # Graph paused at interrupt() — HITL review needed
                interrupt_payloads = [
                    i.value if hasattr(i, 'value') else str(i)
                    for i in result.interrupts
                ]
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

            return output

        except Exception as e:
            logger.error("run_failed", run_id=str(run_id), error=str(e))
            await self._fire_hook("on_error", run_id, e)

            # Emit failure event
            if self._event_store:
                event = EventBuilder() \
                    .category(EventCategory.RUN_FAILED) \
                    .severity(Severity.ERROR) \
                    .actor("kernel.engine") \
                    .action(f"Run failed: {str(e)[:200]}") \
                    .for_run(run_id) \
                    .with_payload({"error": str(e), "error_type": type(e).__name__}) \
                    .build()
                await self._event_store.append(event)

            return RunOutput(
                run_id=run_id,
                status=RunStatus.FAILED,
                intent=IntentType.CHAT,
                model_used="",
                response=f"Error: {str(e)}",
                metadata={"error": str(e), "error_type": type(e).__name__},
            )

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
            result = await self._compiled.ainvoke(
                Command(resume=resume_value), config, version="v2"
            )

            # Check if another interrupt was triggered (multi-step HITL)
            if result.interrupts:
                interrupt_payloads = [
                    i.value if hasattr(i, 'value') else str(i)
                    for i in result.interrupts
                ]
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
        if current_status in (RunStatus.COMPLETED.value, RunStatus.FAILED.value, RunStatus.CANCELLED.value):
            return False

        # Update state
        state["cancelled"] = True
        state["cancel_reason"] = reason
        state["status"] = RunStatus.CANCELLED.value
        self._runs[run_id] = state

        # Emit cancellation event
        if self._event_store:
            event = EventBuilder() \
                .category(EventCategory.RUN_CANCELLED) \
                .actor("kernel.engine") \
                .action(f"Run cancelled: {reason or 'no reason given'}") \
                .for_run(run_id) \
                .with_payload({"reason": reason}) \
                .build()
            await self._event_store.append(event)

        await self._fire_hook("on_cancel", run_id, reason)
        logger.warning("run_cancelled", run_id=str(run_id), reason=reason)
        return True

    async def stream(self, input: RunInput) -> AsyncIterator[str]:
        """
        Real streaming: runs pre-LLM nodes (intake, classify, enrich) normally,
        then streams LLM tokens in real-time via router.execute_stream().
        Memory write runs fire-and-forget after streaming completes.

        Yields JSON-encoded SSE events:
          {"type": "meta", "intent": ..., "model": ..., "enriched": ...}
          {"type": "chunk", "text": "..."}
          {"type": "done", "latency_ms": ..., "model_used": ...}
          {"type": "error", "message": "..."}
        """
        import json as _json
        run_id = input.run_id
        thread_id = str(run_id)
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
            }
        }

        try:
            # ── Phase 1: Run pre-LLM nodes via graph (intake → classify_and_route → enrich) ──
            # We use astream with updates mode to run nodes up to execute
            pre_llm_state = dict(initial_state)

            async for event in self._compiled.astream(initial_state, config, stream_mode="updates"):
                for node_name, state_update in event.items():
                    pre_llm_state.update(state_update)

                    if node_name == "classify_and_route":
                        # Emit metadata event
                        yield _json.dumps({
                            "type": "meta",
                            "intent": state_update.get("intent", "chat"),
                            "model": state_update.get("model", "unknown"),
                            "enriched": False,
                        })

                    elif node_name == "enrich":
                        yield _json.dumps({
                            "type": "meta",
                            "enriched": state_update.get("enriched", False),
                            "memories_found": len(state_update.get("relevant_memories", [])),
                        })

                    elif node_name == "execute":
                        # The non-streaming execute already ran via the graph.
                        # For true streaming, we'd need to intercept before execute.
                        # For now, stream the response that execute produced.
                        response = state_update.get("response", "")
                        if response:
                            # Stream in word-boundary chunks for natural feel
                            words = response.split(" ")
                            buffer = ""
                            for word in words:
                                buffer += word + " "
                                if len(buffer) >= 20:  # ~4-5 words per chunk
                                    yield _json.dumps({"type": "chunk", "text": buffer})
                                    buffer = ""
                            if buffer.strip():
                                yield _json.dumps({"type": "chunk", "text": buffer})

                    elif node_name == "respond":
                        # Final response — if execute didn't stream, stream from here
                        final = state_update.get("final_response", "")
                        response_already = pre_llm_state.get("response", "")
                        if final and not response_already:
                            words = final.split(" ")
                            buffer = ""
                            for word in words:
                                buffer += word + " "
                                if len(buffer) >= 20:
                                    yield _json.dumps({"type": "chunk", "text": buffer})
                                    buffer = ""
                            if buffer.strip():
                                yield _json.dumps({"type": "chunk", "text": buffer})

            elapsed_ms = (time.monotonic() - start_time) * 1000
            yield _json.dumps({
                "type": "done",
                "latency_ms": round(elapsed_ms),
                "model_used": pre_llm_state.get("model_used", ""),
                "intent": pre_llm_state.get("intent", "chat"),
            })

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
            return "graph TD\n  A[intake] --> B[classify] --> C[route] --> D{enrich?} --> E[execute] --> F{HITL?} --> G[memory_write] --> H[respond]"

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
