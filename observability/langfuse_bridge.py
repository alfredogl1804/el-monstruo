"""
El Monstruo — Langfuse Bridge
===============================
Mirrors sovereign EventStore events to Langfuse v4 for visualization.

Langfuse is a COMMODITY — our EventStore is the source of truth.
This bridge sends a copy to Langfuse for its UI/analytics.

Usage:
    bridge = LangfuseBridge()
    await bridge.initialize()

    # Mirror a complete run
    await bridge.trace_run(run_output, events)

    # Mirror a single LLM call
    await bridge.trace_generation(model, prompt, response, usage)
"""

from __future__ import annotations

import os
from typing import Any, Optional
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger("observability.langfuse")


class LangfuseBridge:
    """
    Bridges the sovereign EventStore to Langfuse v4 for observability.

    Langfuse v4 SDK is imported lazily — if not installed or not configured,
    the bridge silently degrades to no-op mode. This ensures the kernel
    never depends on Langfuse being available.
    """

    def __init__(self) -> None:
        self._client: Any = None
        self._enabled: bool = False

    async def initialize(self) -> bool:
        """
        Initialize the Langfuse client.
        Returns True if Langfuse is available and configured.
        """
        public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
        secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
        host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if not public_key or not secret_key:
            logger.info("langfuse_disabled", reason="missing credentials")
            return False

        try:
            from langfuse import Langfuse

            self._client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host,
            )
            self._enabled = True
            logger.info("langfuse_connected", host=host)
            return True
        except ImportError:
            logger.warning("langfuse_not_installed", hint="pip install langfuse")
            return False
        except Exception as e:
            logger.error("langfuse_init_failed", error=str(e))
            return False

    def trace_run_start(
        self,
        run_id: str,
        user_id: str,
        channel: str,
        message: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Start a Langfuse trace for a new run.
        Returns the trace object (or None if disabled).
        """
        if not self._enabled or not self._client:
            return None

        try:
            trace = self._client.trace(
                id=run_id,
                name="monstruo.run",
                user_id=user_id,
                input={"message": message, "channel": channel},
                metadata={
                    "channel": channel,
                    "system": "el-monstruo",
                    "version": "0.2.0-sprint1",
                    **(metadata or {}),
                },
            )
            logger.debug("langfuse_trace_started", run_id=run_id)
            return trace
        except Exception as e:
            logger.warning("langfuse_trace_error", error=str(e))
            return None

    def trace_span(
        self,
        trace: Any,
        name: str,
        input: Optional[dict[str, Any]] = None,
        output: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
        level: str = "DEFAULT",
    ) -> Any:
        """
        Add a span to an existing trace (e.g., for a node execution).
        """
        if not trace:
            return None

        try:
            span = trace.span(
                name=name,
                input=input,
                output=output,
                metadata=metadata,
                level=level,
            )
            return span
        except Exception as e:
            logger.warning("langfuse_span_error", name=name, error=str(e))
            return None

    def trace_generation(
        self,
        trace: Any,
        name: str,
        model: str,
        input_messages: list[dict[str, str]],
        output: str,
        usage: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Record an LLM generation (model call) in Langfuse.
        This is the most valuable trace type — it shows model usage,
        tokens, cost, and latency per call.
        """
        if not trace:
            return None

        try:
            generation = trace.generation(
                name=name,
                model=model,
                input=input_messages,
                output=output,
                usage=usage,
                metadata=metadata,
            )
            return generation
        except Exception as e:
            logger.warning("langfuse_generation_error", name=name, error=str(e))
            return None

    def trace_run_end(
        self,
        trace: Any,
        output: str,
        status: str = "completed",
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        End a Langfuse trace for a completed run.
        """
        if not trace:
            return

        try:
            level = "DEFAULT" if status == "completed" else "ERROR"
            trace.update(
                output={"response": output},
                metadata={
                    "status": status,
                    **(metadata or {}),
                },
                level=level,
            )
        except Exception as e:
            logger.warning("langfuse_end_error", error=str(e))

    def trace_event(
        self,
        trace: Any,
        name: str,
        input: Optional[dict[str, Any]] = None,
        output: Optional[dict[str, Any]] = None,
        level: str = "DEFAULT",
    ) -> None:
        """
        Add a discrete event to a trace (for policy checks, memory ops, etc.).
        """
        if not trace:
            return

        try:
            trace.event(
                name=name,
                input=input,
                output=output,
                level=level,
            )
        except Exception as e:
            logger.warning("langfuse_event_error", name=name, error=str(e))

    def score_run(
        self,
        trace: Any,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ) -> None:
        """
        Add a score to a trace (for quality metrics, user feedback, etc.).
        """
        if not trace:
            return

        try:
            trace.score(
                name=name,
                value=value,
                comment=comment,
            )
        except Exception as e:
            logger.warning("langfuse_score_error", name=name, error=str(e))

    async def flush(self) -> None:
        """Flush any pending events to Langfuse."""
        if self._enabled and self._client:
            try:
                self._client.flush()
            except Exception as e:
                logger.warning("langfuse_flush_error", error=str(e))

    async def shutdown(self) -> None:
        """Shutdown the Langfuse client gracefully."""
        if self._enabled and self._client:
            try:
                self._client.flush()
                self._client.shutdown()
                logger.info("langfuse_shutdown")
            except Exception as e:
                logger.warning("langfuse_shutdown_error", error=str(e))

    @property
    def enabled(self) -> bool:
        return self._enabled
