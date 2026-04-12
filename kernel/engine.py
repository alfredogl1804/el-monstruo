"""
El Monstruo — Kernel Engine (Día 1)
=====================================
Implementación soberana del KernelInterface.
State machine propia — sin frameworks externos para el flujo.

Flujo:
    message_in → classify_intent → route_model → execute → emit_events → respond
"""

from __future__ import annotations

import time
from typing import Any, AsyncIterator, Callable, Optional
from uuid import UUID, uuid4

import structlog

from contracts.kernel_interface import (
    Checkpoint,
    IntentType,
    KernelInterface,
    RunInput,
    RunOutput,
    RunStatus,
)
from contracts.event_envelope import EventBuilder, EventCategory, Severity

logger = structlog.get_logger("kernel")


# ── Valid State Transitions ─────────────────────────────────────────

VALID_TRANSITIONS: dict[RunStatus, set[RunStatus]] = {
    RunStatus.PENDING: {RunStatus.ROUTING, RunStatus.CANCELLED, RunStatus.FAILED},
    RunStatus.ROUTING: {RunStatus.EXECUTING, RunStatus.FAILED, RunStatus.CANCELLED},
    RunStatus.EXECUTING: {
        RunStatus.STREAMING,
        RunStatus.AWAITING_TOOL,
        RunStatus.AWAITING_HUMAN,
        RunStatus.COMPLETED,
        RunStatus.FAILED,
        RunStatus.CANCELLED,
    },
    RunStatus.STREAMING: {RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED},
    RunStatus.AWAITING_TOOL: {RunStatus.EXECUTING, RunStatus.FAILED, RunStatus.CANCELLED},
    RunStatus.AWAITING_HUMAN: {RunStatus.EXECUTING, RunStatus.CANCELLED},
    RunStatus.CHECKPOINTED: {RunStatus.EXECUTING, RunStatus.CANCELLED},
    RunStatus.COMPLETED: set(),  # Terminal
    RunStatus.FAILED: set(),     # Terminal
    RunStatus.CANCELLED: set(),  # Terminal
}


class KernelEngine(KernelInterface):
    """
    Implementación soberana del Kernel.

    Responsabilidades:
        - Mantener el estado de cada run
        - Validar transiciones de estado
        - Coordinar router + ejecución + event emission
        - Hooks para extensibilidad
    """

    def __init__(
        self,
        router: Any = None,       # RouterInterface (Phase 2)
        event_store: Any = None,   # EventStoreInterface (Phase 3)
    ) -> None:
        self._runs: dict[UUID, _RunState] = {}
        self._hooks: dict[str, list[Callable]] = {}
        self._router = router
        self._event_store = event_store

    # ── KernelInterface Implementation ──────────────────────────────

    async def start_run(self, input: RunInput) -> RunOutput:
        """
        Full execution pipeline:
        1. Create run state (PENDING)
        2. Emit RUN_STARTED event
        3. Classify intent (ROUTING)
        4. Route to model (ROUTING → EXECUTING)
        5. Execute with model (EXECUTING)
        6. Emit RUN_COMPLETED event
        7. Return RunOutput
        """
        run_id = input.run_id
        start_time = time.monotonic()

        # 1. Create run state
        run_state = _RunState(
            run_id=run_id,
            status=RunStatus.PENDING,
            input=input,
        )
        self._runs[run_id] = run_state

        # 2. Emit RUN_STARTED
        await self._emit_event(
            EventBuilder()
            .category(EventCategory.RUN_STARTED)
            .actor("kernel")
            .action(f"Run started for user {input.user_id} on {input.channel}")
            .for_run(run_id)
            .for_user(input.user_id)
            .on_channel(input.channel)
            .with_payload({"message": input.message[:200]})
            .build()
        )

        try:
            # 3. Classify intent
            await self._transition(run_id, RunStatus.ROUTING)
            await self._fire_hook("pre_route", run_id, input)

            intent, model = await self._route(input)
            run_state.intent = intent
            run_state.model = model

            await self._emit_event(
                EventBuilder()
                .category(EventCategory.ROUTE_DECIDED)
                .actor("kernel")
                .action(f"Routed to {model} with intent {intent.value}")
                .for_run(run_id)
                .for_user(input.user_id)
                .with_payload({"intent": intent.value, "model": model})
                .build()
            )
            await self._fire_hook("post_route", run_id, intent, model)

            # 4. Execute
            await self._transition(run_id, RunStatus.EXECUTING)
            await self._fire_hook("pre_execute", run_id, input, model)

            response, usage = await self._execute(input, model, intent)
            run_state.response = response
            run_state.usage = usage

            await self._fire_hook("post_execute", run_id, response, usage)

            # 5. Complete
            await self._transition(run_id, RunStatus.COMPLETED)
            elapsed_ms = (time.monotonic() - start_time) * 1000

            output = RunOutput(
                run_id=run_id,
                status=RunStatus.COMPLETED,
                intent=intent,
                model_used=model,
                response=response,
                tokens_in=usage.get("prompt_tokens", 0),
                tokens_out=usage.get("completion_tokens", 0),
                cost_usd=usage.get("cost_usd", 0.0),
                latency_ms=elapsed_ms,
            )

            # 6. Emit RUN_COMPLETED
            await self._emit_event(
                EventBuilder()
                .category(EventCategory.RUN_COMPLETED)
                .actor("kernel")
                .action(f"Run completed in {elapsed_ms:.0f}ms using {model}")
                .for_run(run_id)
                .for_user(input.user_id)
                .with_payload({
                    "model": model,
                    "intent": intent.value,
                    "tokens_in": output.tokens_in,
                    "tokens_out": output.tokens_out,
                    "cost_usd": output.cost_usd,
                    "latency_ms": elapsed_ms,
                    "response_preview": response[:200],
                })
                .build()
            )

            logger.info(
                "run_completed",
                run_id=str(run_id),
                model=model,
                intent=intent.value,
                latency_ms=f"{elapsed_ms:.0f}",
            )
            return output

        except Exception as e:
            # Handle failure
            await self._transition(run_id, RunStatus.FAILED)
            elapsed_ms = (time.monotonic() - start_time) * 1000

            await self._emit_event(
                EventBuilder()
                .category(EventCategory.RUN_FAILED)
                .severity(Severity.ERROR)
                .actor("kernel")
                .action(f"Run failed: {str(e)}")
                .for_run(run_id)
                .for_user(input.user_id)
                .with_payload({"error": str(e), "error_type": type(e).__name__})
                .build()
            )
            await self._fire_hook("on_error", run_id, e)

            logger.error("run_failed", run_id=str(run_id), error=str(e))

            return RunOutput(
                run_id=run_id,
                status=RunStatus.FAILED,
                response=f"Error: {str(e)}",
                latency_ms=elapsed_ms,
            )

    async def step(self, run_id: UUID, input: dict[str, Any]) -> RunOutput:
        """Advance a multi-step run (tool results, human input, etc.)."""
        run_state = self._runs.get(run_id)
        if not run_state:
            raise ValueError(f"Run {run_id} not found")

        await self._emit_event(
            EventBuilder()
            .category(EventCategory.RUN_STEP)
            .actor("kernel")
            .action(f"Step received for run {run_id}")
            .for_run(run_id)
            .with_payload(input)
            .build()
        )

        # For now, re-execute with the additional input as context
        run_state.step_count += 1
        original_input = run_state.input

        # Create new input with step context
        step_input = RunInput(
            run_id=run_id,
            user_id=original_input.user_id,
            channel=original_input.channel,
            message=input.get("message", ""),
            context={**original_input.context, "step": run_state.step_count, **input},
        )

        await self._transition(run_id, RunStatus.EXECUTING)
        response, usage = await self._execute(
            step_input, run_state.model, run_state.intent
        )

        await self._transition(run_id, RunStatus.COMPLETED)
        return RunOutput(
            run_id=run_id,
            status=RunStatus.COMPLETED,
            intent=run_state.intent,
            model_used=run_state.model,
            response=response,
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
            cost_usd=usage.get("cost_usd", 0.0),
        )

    async def checkpoint(self, run_id: UUID) -> Checkpoint:
        """Save current run state for replay/recovery."""
        run_state = self._runs.get(run_id)
        if not run_state:
            raise ValueError(f"Run {run_id} not found")

        cp = Checkpoint(
            run_id=run_id,
            step=run_state.step_count,
            status=RunStatus.CHECKPOINTED,
            state={
                "intent": run_state.intent.value if run_state.intent else None,
                "model": run_state.model,
                "response": run_state.response,
                "usage": run_state.usage,
            },
        )

        await self._emit_event(
            EventBuilder()
            .category(EventCategory.CHECKPOINT_CREATED)
            .actor("kernel")
            .action(f"Checkpoint created at step {run_state.step_count}")
            .for_run(run_id)
            .with_payload({"step": run_state.step_count})
            .build()
        )

        return cp

    async def resume(self, checkpoint: Checkpoint) -> RunOutput:
        """Resume execution from a checkpoint."""
        run_id = checkpoint.run_id
        run_state = self._runs.get(run_id)
        if not run_state:
            raise ValueError(f"Run {run_id} not found for resume")

        await self._emit_event(
            EventBuilder()
            .category(EventCategory.CHECKPOINT_RESTORED)
            .actor("kernel")
            .action(f"Resuming from checkpoint step {checkpoint.step}")
            .for_run(run_id)
            .build()
        )

        await self._transition(run_id, RunStatus.EXECUTING)
        response, usage = await self._execute(
            run_state.input, run_state.model, run_state.intent
        )

        await self._transition(run_id, RunStatus.COMPLETED)
        return RunOutput(
            run_id=run_id,
            status=RunStatus.COMPLETED,
            intent=run_state.intent,
            model_used=run_state.model,
            response=response,
        )

    async def cancel(self, run_id: UUID, reason: str = "") -> bool:
        """Kill switch: cancel a run immediately."""
        run_state = self._runs.get(run_id)
        if not run_state:
            return False

        if run_state.status in {RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED}:
            return False

        await self._transition(run_id, RunStatus.CANCELLED)
        await self._emit_event(
            EventBuilder()
            .category(EventCategory.RUN_CANCELLED)
            .actor("kernel")
            .action(f"Run cancelled: {reason or 'no reason given'}")
            .for_run(run_id)
            .with_payload({"reason": reason})
            .build()
        )
        await self._fire_hook("on_cancel", run_id, reason)

        logger.warning("run_cancelled", run_id=str(run_id), reason=reason)
        return True

    async def stream(self, input: RunInput) -> AsyncIterator[str]:
        """Stream tokens from model execution."""
        run_id = input.run_id
        run_state = _RunState(run_id=run_id, status=RunStatus.PENDING, input=input)
        self._runs[run_id] = run_state

        await self._transition(run_id, RunStatus.ROUTING)
        intent, model = await self._route(input)
        run_state.intent = intent
        run_state.model = model

        await self._transition(run_id, RunStatus.STREAMING)

        if self._router:
            async for chunk in self._router.stream(input.message, model, intent):
                yield chunk
        else:
            yield f"[stream-stub] Would stream from {model} for: {input.message}"

        await self._transition(run_id, RunStatus.COMPLETED)

    async def get_status(self, run_id: UUID) -> RunStatus:
        """Get current status of a run."""
        run_state = self._runs.get(run_id)
        if not run_state:
            raise ValueError(f"Run {run_id} not found")
        return run_state.status

    async def register_hook(self, event: str, callback: Callable[..., Any]) -> None:
        """Register a lifecycle hook."""
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)
        logger.debug("hook_registered", hook_event=event)

    # ── Internal Methods ────────────────────────────────────────────

    async def _route(self, input: RunInput) -> tuple[IntentType, str]:
        """Classify intent and select model via router."""
        if self._router:
            return await self._router.route(input.message, input.channel, input.context)
        # Fallback: basic intent classification without router
        return _basic_intent_classify(input.message), "gpt-5"

    async def _execute(
        self,
        input: RunInput,
        model: str,
        intent: IntentType,
    ) -> tuple[str, dict[str, Any]]:
        """Execute the request against the selected model."""
        if self._router:
            return await self._router.execute(input.message, model, intent, input.context)
        # Fallback stub
        return (
            f"[stub] Model {model} would respond to: {input.message[:100]}",
            {"prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0},
        )

    async def _transition(self, run_id: UUID, new_status: RunStatus) -> None:
        """Validate and execute a state transition."""
        run_state = self._runs.get(run_id)
        if not run_state:
            raise ValueError(f"Run {run_id} not found")

        current = run_state.status
        allowed = VALID_TRANSITIONS.get(current, set())

        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition: {current.value} → {new_status.value}. "
                f"Allowed: {[s.value for s in allowed]}"
            )

        run_state.status = new_status
        logger.debug(
            "state_transition",
            run_id=str(run_id),
            from_state=current.value,
            to_state=new_status.value,
        )

    async def _emit_event(self, event: Any) -> None:
        """Emit an event to the event store."""
        if self._event_store:
            await self._event_store.append(event)
        else:
            logger.debug("event_emitted", category=event.category.value, action=event.action)

    async def _fire_hook(self, event: str, *args: Any) -> None:
        """Fire all registered hooks for an event."""
        for callback in self._hooks.get(event, []):
            try:
                result = callback(*args)
                if hasattr(result, "__await__"):
                    await result
            except Exception as e:
                logger.warning("hook_error", event=event, error=str(e))


# ── Internal Run State ──────────────────────────────────────────────

class _RunState:
    """Mutable internal state for a run. Not exposed outside the kernel."""

    __slots__ = (
        "run_id", "status", "input", "intent", "model",
        "response", "usage", "step_count",
    )

    def __init__(
        self,
        run_id: UUID,
        status: RunStatus,
        input: RunInput,
    ) -> None:
        self.run_id = run_id
        self.status = status
        self.input = input
        self.intent: Optional[IntentType] = None
        self.model: str = ""
        self.response: str = ""
        self.usage: dict[str, Any] = {}
        self.step_count: int = 0


# ── Basic Intent Classification (no router fallback) ────────────────

def _basic_intent_classify(message: str) -> IntentType:
    """
    Simple keyword-based intent classification.
    Used only when no router is available.
    """
    msg = message.lower().strip()

    deep_keywords = {"analiza", "piensa", "razona", "explica", "compara", "evalúa",
                     "analyze", "think", "reason", "explain", "compare", "evaluate"}
    exec_keywords = {"haz", "ejecuta", "crea", "genera", "envía", "publica",
                     "do", "execute", "create", "generate", "send", "publish"}
    system_keywords = {"status", "health", "estado", "salud", "/start", "/help"}

    words = set(msg.split())

    if words & system_keywords or msg.startswith("/"):
        return IntentType.SYSTEM
    if words & exec_keywords:
        return IntentType.EXECUTE
    if words & deep_keywords or len(msg) > 500:
        return IntentType.DEEP_THINK
    return IntentType.CHAT
