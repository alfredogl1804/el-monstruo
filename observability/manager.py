"""
El Monstruo — Observability Manager
=====================================
Unified facade that coordinates Langfuse + OpenTelemetry bridges.

This is the ONLY class the kernel should interact with.
It delegates to the appropriate bridge(s) based on configuration.

Usage in kernel/main.py:
    from observability.manager import ObservabilityManager

    obs = ObservabilityManager()
    await obs.initialize()

    # In start_run:
    ctx = obs.start_trace(run_id, user_id, channel, message)

    # In each node:
    obs.record_span(ctx, "think_node", input={...}, output={...})

    # For LLM calls:
    obs.record_generation(ctx, "execute", model, messages, response, usage)

    # End:
    obs.end_trace(ctx, response, status)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

from observability.langfuse_bridge import LangfuseBridge
from observability.otel_bridge import OTelBridge

logger = structlog.get_logger("observability.manager")


@dataclass
class TraceContext:
    """
    Holds references to active trace objects across both bridges.
    Passed through the kernel run as a lightweight context carrier.
    """

    run_id: str
    langfuse_trace: Any = None
    otel_spans: dict[str, Any] = field(default_factory=dict)


class ObservabilityManager:
    """
    Unified observability facade for El Monstruo.

    Coordinates:
    - LangfuseBridge: For Langfuse UI visualization and LLM analytics
    - OTelBridge: For distributed tracing to any OTLP backend

    Both are optional — the kernel works fine without either.
    """

    def __init__(self) -> None:
        self._langfuse = LangfuseBridge()
        self._otel = OTelBridge()

    async def initialize(self) -> dict[str, bool]:
        """
        Initialize all observability bridges.
        Returns a dict showing which bridges are active.
        """
        langfuse_ok = await self._langfuse.initialize()
        otel_ok = await self._otel.initialize()

        status = {
            "langfuse": langfuse_ok,
            "opentelemetry": otel_ok,
        }

        logger.info("observability_initialized", **status)
        return status

    def start_trace(
        self,
        run_id: str,
        user_id: str,
        channel: str,
        message: str,
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> TraceContext:
        """
        Start a new trace for a kernel run.
        Creates trace objects in both Langfuse and OTel.

        Sprint 13: Added session_id for Langfuse session grouping.
        """
        ctx = TraceContext(run_id=run_id)

        # Langfuse trace (Sprint 13: with session_id)
        ctx.langfuse_trace = self._langfuse.trace_run_start(
            run_id=run_id,
            user_id=user_id,
            channel=channel,
            message=message,
            metadata=metadata,
            session_id=session_id,
        )

        logger.debug("trace_started", run_id=run_id, session_id=session_id or "none")
        return ctx

    def record_span(
        self,
        ctx: TraceContext,
        name: str,
        input: Optional[dict[str, Any]] = None,
        output: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
        level: str = "DEFAULT",
    ) -> None:
        """
        Record a span (node execution) in both bridges.
        """
        # Langfuse span
        self._langfuse.trace_span(
            trace=ctx.langfuse_trace,
            name=name,
            input=input,
            output=output,
            metadata=metadata,
            level=level,
        )

        logger.debug("span_recorded", run_id=ctx.run_id, name=name)

    def record_generation(
        self,
        ctx: TraceContext,
        name: str,
        model: str,
        input_messages: list[dict[str, str]],
        output: str,
        usage: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Record an LLM generation (model call) in Langfuse.
        This is the most valuable observability data point.
        """
        self._langfuse.trace_generation(
            trace=ctx.langfuse_trace,
            name=name,
            model=model,
            input_messages=input_messages,
            output=output,
            usage=usage,
            metadata=metadata,
        )

        logger.debug(
            "generation_recorded",
            run_id=ctx.run_id,
            name=name,
            model=model,
        )

    def record_event(
        self,
        ctx: TraceContext,
        name: str,
        input: Optional[dict[str, Any]] = None,
        output: Optional[dict[str, Any]] = None,
        level: str = "DEFAULT",
    ) -> None:
        """
        Record a discrete event (policy check, memory op, etc.).
        """
        self._langfuse.trace_event(
            trace=ctx.langfuse_trace,
            name=name,
            input=input,
            output=output,
            level=level,
        )

    def score(
        self,
        ctx: TraceContext,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ) -> None:
        """
        Score a trace (for quality metrics, user feedback).
        """
        self._langfuse.score_run(
            trace=ctx.langfuse_trace,
            name=name,
            value=value,
            comment=comment,
        )

    def end_trace(
        self,
        ctx: TraceContext,
        output: str,
        status: str = "completed",
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        End a trace for a completed run.
        """
        self._langfuse.trace_run_end(
            trace=ctx.langfuse_trace,
            output=output,
            status=status,
            metadata=metadata,
        )

        logger.debug("trace_ended", run_id=ctx.run_id, status=status)

    async def flush(self) -> None:
        """Flush pending events to all backends."""
        await self._langfuse.flush()

    def get_callback_handler(self) -> Any:
        """
        Sprint 13: Get a Langfuse CallbackHandler for LangGraph deep tracing.

        Returns a langfuse.langchain.CallbackHandler that automatically captures
        all LangGraph node executions, LLM calls, and tool invocations when
        passed to LangGraph via config["callbacks"].

        Returns None if Langfuse is not enabled.
        """
        return self._langfuse.get_callback_handler()

    async def shutdown(self) -> None:
        """Shutdown all observability bridges."""
        await self._langfuse.shutdown()
        await self._otel.shutdown()
        logger.info("observability_shutdown")

    @property
    def langfuse_enabled(self) -> bool:
        return self._langfuse.enabled

    @property
    def otel_enabled(self) -> bool:
        return self._otel.enabled
