"""
El Monstruo — Kernel Engine (LangGraph Rewrite)
=================================================
Sovereign kernel that uses LangGraph as the internal execution motor
while exposing the KernelInterface contract.

Architecture:
    KernelInterface (OUR contract)
        └── LangGraphKernel (this file)
                └── StateGraph (LangGraph motor)
                        └── 7 nodes (kernel/nodes.py)

Principio: LangGraph es un motor intercambiable.
Los contratos soberanos son permanentes.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Callable, Optional
from uuid import UUID, uuid4

import structlog
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

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
    classify,
    route,
    enrich,
    execute,
    memory_write,
    respond,
    should_enrich,
    check_hitl,
)

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
    ) -> None:
        self._router = router
        self._event_store = event_store
        self._memory = memory
        self._knowledge = knowledge
        self._checkpoint_store = checkpoint_store
        self._hooks: dict[str, list[Callable[..., Any]]] = {}
        self._runs: dict[UUID, MonstruoState] = {}

        # Build the LangGraph graph
        self._checkpointer = MemorySaver()
        self._graph = self._build_graph()
        self._compiled = self._graph.compile(
            checkpointer=self._checkpointer,
        )

        logger.info("kernel_initialized", motor="langgraph", version="1.1.6")

    def _build_graph(self) -> StateGraph:
        """
        Build the sovereign execution graph.

        7 nodes, 2 conditional edges:
            intake → classify → route → should_enrich? → execute → check_hitl? → memory_write → respond
        """
        graph = StateGraph(MonstruoState)

        # Add all 7 nodes
        graph.add_node("intake", intake)
        graph.add_node("classify", classify)
        graph.add_node("route", route)
        graph.add_node("enrich", enrich)
        graph.add_node("execute", execute)
        graph.add_node("memory_write", memory_write)
        graph.add_node("respond", respond)

        # Set entry point
        graph.set_entry_point("intake")

        # Linear edges
        graph.add_edge("intake", "classify")
        graph.add_edge("classify", "route")

        # Conditional: route → enrich or execute (skip enrichment for chat/system)
        graph.add_conditional_edges(
            "route",
            should_enrich,
            {
                "enrich": "enrich",
                "execute": "execute",
            },
        )

        # enrich always goes to execute
        graph.add_edge("enrich", "execute")

        # Conditional: execute → memory_write or respond (on failure)
        graph.add_conditional_edges(
            "execute",
            check_hitl,
            {
                "memory_write": "memory_write",
                "respond": "respond",
            },
        )

        # memory_write always goes to respond
        graph.add_edge("memory_write", "respond")

        # respond is terminal
        graph.add_edge("respond", END)

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
                }
            }
            final_state = await self._compiled.ainvoke(initial_state, config)

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
        Sends the human response and resumes the graph.
        """
        thread_id = str(run_id)
        config = {"configurable": {"thread_id": thread_id}}

        # If there's human input, update the state
        update = {}
        if input:
            update["human_response"] = input.get("response", "")
            update["needs_human_approval"] = False

        try:
            final_state = await self._compiled.ainvoke(update or None, config)
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
        LangGraph handles this internally via MemorySaver.
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
        Stream tokens from model execution.
        Uses LangGraph's astream_events for real-time token streaming.
        """
        run_id = input.run_id
        thread_id = str(run_id)

        initial_state: MonstruoState = {
            "run_id": str(run_id),
            "user_id": input.user_id,
            "channel": input.channel,
            "message": input.message,
            "attachments": input.attachments or [],
            "context": {
                **(input.context or {}),
                "_router": self._router,
                "_memory": self._memory,
                "_knowledge": self._knowledge,
                "_event_store": self._event_store,
            },
        }

        config = {"configurable": {"thread_id": thread_id}}

        try:
            async for event in self._compiled.astream(initial_state, config, stream_mode="updates"):
                # Each event is a dict with node_name: state_update
                for node_name, state_update in event.items():
                    if node_name == "respond" and "final_response" in state_update:
                        # Stream the final response in chunks
                        response = state_update["final_response"]
                        chunk_size = 50
                        for i in range(0, len(response), chunk_size):
                            yield response[i:i + chunk_size]
                    elif node_name == "execute" and "response" in state_update:
                        # Stream intermediate execution response
                        yield f"[{node_name}] Processing..."
        except Exception as e:
            logger.error("stream_failed", run_id=str(run_id), error=str(e))
            yield f"[error] {str(e)}"

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
