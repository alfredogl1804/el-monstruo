"""
El Monstruo — Opik Cloud Bridge (Sprint 29 — Épica 2)
======================================================
Dual observability: Langfuse + Opik Cloud.

Opik provides:
  - LLM trace visualization in Opik Cloud dashboard
  - Cost tracking per model
  - Latency percentiles
  - Evaluation scoring

Gate Épica 2: Each request generates a trace in Opik Cloud dashboard.

Integration:
  - OpikBridge initializes the Opik client
  - Records traces, spans, and generations
  - Works alongside LangfuseBridge (not a replacement)

Requires:
  - OPIK_API_KEY env var (Opik Cloud)
  - OPIK_WORKSPACE env var (optional, defaults to "el-monstruo")
  - opik==2.0.14

Sprint 29 | 0.22.0-sprint29 | 25 abril 2026
"""

from __future__ import annotations

import os
import time
from typing import Any, Optional

import structlog

logger = structlog.get_logger("observability.opik_bridge")


class OpikBridge:
    """Bridge to Opik Cloud for LLM observability."""

    def __init__(self) -> None:
        self._client = None
        self._enabled = False
        self._workspace = os.environ.get("OPIK_WORKSPACE", "el-monstruo")
        self._project = os.environ.get("OPIK_PROJECT", "monstruo-kernel")

    async def initialize(self) -> bool:
        """Initialize Opik client. Returns True if successful."""
        api_key = os.environ.get("OPIK_API_KEY", "")
        if not api_key:
            logger.info("opik_disabled", reason="no OPIK_API_KEY")
            return False

        try:
            import opik

            # Configure Opik with API key
            opik.configure(
                api_key=api_key,
                workspace=self._workspace,
                use_local=False,
            )

            self._client = opik.Opik(
                project_name=self._project,
            )
            self._enabled = True
            logger.info(
                "opik_initialized",
                workspace=self._workspace,
                project=self._project,
                version="2.0.14",
            )
            return True

        except ImportError:
            logger.warning("opik_not_installed", hint="pip install opik==2.0.14")
            return False
        except Exception as e:
            logger.warning("opik_init_failed", error=str(e))
            return False

    def trace_start(
        self,
        run_id: str,
        user_id: str,
        channel: str,
        message: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Start a new Opik trace for a kernel run."""
        if not self._enabled or not self._client:
            return None

        try:
            trace = self._client.trace(
                name=f"kernel_run_{run_id[:8]}",
                input={"message": message[:500], "channel": channel},
                metadata={
                    "user_id": user_id,
                    "channel": channel,
                    "run_id": run_id,
                    **(metadata or {}),
                },
            )
            logger.debug("opik_trace_started", run_id=run_id)
            return trace
        except Exception as e:
            logger.warning("opik_trace_start_failed", error=str(e))
            return None

    def record_span(
        self,
        trace: Any,
        name: str,
        input_data: Optional[dict[str, Any]] = None,
        output_data: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Record a span within an Opik trace."""
        if not self._enabled or trace is None:
            return None

        try:
            span = trace.span(
                name=name,
                input=input_data,
                output=output_data,
                metadata=metadata,
            )
            return span
        except Exception as e:
            logger.warning("opik_span_failed", name=name, error=str(e))
            return None

    def record_generation(
        self,
        trace: Any,
        name: str,
        model: str,
        input_messages: list[dict[str, str]],
        output: str,
        usage: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Record an LLM generation in Opik."""
        if not self._enabled or trace is None:
            return

        try:
            trace.span(
                name=f"llm_{name}",
                type="llm",
                input={"messages": input_messages},
                output={"content": output[:1000]},
                metadata={
                    "model": model,
                    "tokens_in": usage.get("input", 0) if usage else 0,
                    "tokens_out": usage.get("output", 0) if usage else 0,
                    "cost_usd": usage.get("cost_usd", 0.0) if usage else 0.0,
                    **(metadata or {}),
                },
            )
        except Exception as e:
            logger.warning("opik_generation_failed", name=name, error=str(e))

    def trace_end(
        self,
        trace: Any,
        output: str,
        status: str = "completed",
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """End an Opik trace."""
        if not self._enabled or trace is None:
            return

        try:
            trace.end(
                output={"response": output[:1000], "status": status},
                metadata=metadata,
            )
        except Exception as e:
            logger.warning("opik_trace_end_failed", error=str(e))

    def flush(self) -> None:
        """Flush pending Opik events."""
        if self._enabled and self._client:
            try:
                self._client.flush()
            except Exception as e:
                logger.warning("opik_flush_failed", error=str(e))

    async def shutdown(self) -> None:
        """Shutdown Opik client."""
        if self._enabled and self._client:
            try:
                self._client.end()
            except Exception:
                pass
            self._enabled = False
            logger.info("opik_shutdown")

    @property
    def enabled(self) -> bool:
        return self._enabled

    def get_status(self) -> dict[str, Any]:
        """Return Opik status for /health endpoint."""
        return {
            "active": self._enabled,
            "workspace": self._workspace if self._enabled else None,
            "project": self._project if self._enabled else None,
            "version": "2.0.14" if self._enabled else None,
        }
