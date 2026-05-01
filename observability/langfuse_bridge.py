"""\nEl Monstruo — Langfuse Bridge (Sprint 13: Observabilidad Total)\n================================================================\nMirrors sovereign EventStore events to Langfuse v4 for visualization.\n\nSprint 13 additions:\n  - get_callback_handler() → returns langfuse.langchain.CallbackHandler\n    for automatic LangGraph node-level tracing\n  - session_id propagation from JWT claims into trace metadata\n  - Version string updated to 0.8.0-sprint13\n\nLangfuse is a COMMODITY — our EventStore is the source of truth.\nThis bridge sends a copy to Langfuse for its UI/analytics.\n"""  # noqa: E501

from __future__ import annotations

import os
from typing import Any, Optional

import structlog

logger = structlog.get_logger("observability.langfuse")

# Sprint 13: Lazy import of CallbackHandler to avoid hard dependency
_CallbackHandler = None


def _get_callback_handler_class():
    """Lazy import of langfuse.langchain.CallbackHandler (v4 SDK path)."""
    global _CallbackHandler
    if _CallbackHandler is None:
        try:
            from langfuse.langchain import CallbackHandler

            _CallbackHandler = CallbackHandler
        except ImportError:
            logger.warning("langfuse_callback_handler_not_available", hint="pip install langfuse")
            _CallbackHandler = False  # sentinel: tried and failed
    return _CallbackHandler if _CallbackHandler is not False else None


class LangfuseBridge:
    """
    Bridges the sovereign EventStore to Langfuse v4 for observability.

    Langfuse v4 SDK is imported lazily — if not installed or not configured,
    the bridge silently degrades to no-op mode. This ensures the kernel
    never depends on Langfuse being available.

    Sprint 13: Added get_callback_handler() for LangGraph deep tracing.
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
        session_id: Optional[str] = None,
    ) -> Any:
        """
        Start a Langfuse trace for a new run.
        Returns the trace object (or None if disabled).

        Sprint 13: Added session_id parameter for session grouping in Langfuse.
        """
        if not self._enabled or not self._client:
            return None

        try:
            trace_kwargs: dict[str, Any] = {
                "id": run_id,
                "name": "monstruo.run",
                "user_id": user_id,
                "input": {"message": message, "channel": channel},
                "metadata": {
                    "channel": channel,
                    "system": "el-monstruo",
                    "version": "0.8.0-sprint13",
                    **(metadata or {}),
                },
            }
            # Sprint 13: Propagate session_id for Langfuse session grouping
            if session_id:
                trace_kwargs["session_id"] = session_id

            trace = self._client.trace(**trace_kwargs)
            logger.debug("langfuse_trace_started", run_id=run_id, session_id=session_id or "none")
            return trace
        except Exception as e:
            logger.warning("langfuse_trace_error", error=str(e))
            return None

    def get_callback_handler(self) -> Any:
        """
        Sprint 13: Create a Langfuse CallbackHandler for LangGraph deep tracing.

        Returns a langfuse.langchain.CallbackHandler instance that automatically
        captures all LangGraph node executions, LLM calls, and tool invocations.

        The handler is passed to LangGraph via config["callbacks"].
        Session/user attribution is done via config["metadata"] at invocation time.

        Returns None if Langfuse is not enabled or CallbackHandler is not available.
        """
        if not self._enabled:
            return None

        handler_cls = _get_callback_handler_class()
        if handler_cls is None:
            return None

        try:
            handler = handler_cls()
            logger.debug("langfuse_callback_handler_created")
            return handler
        except Exception as e:
            logger.warning("langfuse_callback_handler_error", error=str(e))
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

    # ── Sprint 56.4: Embrión Observability ────────────────────────────────

    def trace_embrion_action(
        self,
        embrion_id: str,
        action_name: str,
        action_type: str = "task",  # task, thinking, seeding, validation
        metadata: Optional[dict] = None,
    ) -> Optional[Any]:
        """
        Crear un trace para una acción de Embrión.
        T1: Cada acción de Embrión genera un trace en Langfuse con embrion_id.
        """
        if not self._enabled or not self._client:
            return None

        try:
            trace = self._client.trace(
                name=f"embrion:{embrion_id}:{action_name}",
                user_id=embrion_id,
                session_id=f"embrion-session-{embrion_id}",
                metadata={
                    "embrion_id": embrion_id,
                    "action_type": action_type,
                    "sprint": "56",
                    **(metadata or {}),
                },
                tags=[f"embrion:{embrion_id}", f"type:{action_type}"],
            )
            return trace
        except Exception as e:
            logger.warning("langfuse_trace_embrion_failed", error=str(e))
            return None

    def score_embrion_action(
        self,
        trace_id: str,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ) -> None:
        """
        Registrar un score para una acción de Embrión.
        T4: Quality scores del judge se registran en Langfuse.
        """
        if not self._enabled or not self._client:
            return

        try:
            self._client.score(
                trace_id=trace_id,
                name=name,
                value=value,
                comment=comment,
            )
        except Exception as e:
            logger.warning("langfuse_score_embrion_failed", error=str(e))

    def track_embrion_cost(
        self,
        embrion_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
    ) -> None:
        """
        Trackear costo de un LLM call de un Embrión.
        T2: Costos se trackean por Embrión y por acción.
        """
        if not self._enabled or not self._client:
            return

        try:
            self._client.trace(
                name=f"embrion:{embrion_id}:llm_cost",
                metadata={
                    "embrion_id": embrion_id,
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost_usd": cost_usd,
                },
                tags=[f"embrion:{embrion_id}", "cost_tracking"],
            )
        except Exception as e:
            logger.warning("langfuse_cost_tracking_failed", error=str(e))

    # ── /Sprint 56.4 ──────────────────────────────────────────────────────────

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
