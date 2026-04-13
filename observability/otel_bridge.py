"""
El Monstruo — OpenTelemetry Bridge
====================================
Exports sovereign traces to any OTLP-compatible backend.

This is a thin wrapper around the OpenTelemetry SDK that creates
spans for kernel nodes, model calls, and memory operations.

Architecture:
    OTelBridge → TracerProvider → OTLPSpanExporter → Any OTLP backend
                                                    (Langfuse, Jaeger, etc.)

Principle: OpenTelemetry is the industry standard for distributed tracing.
We use it as a transport layer — our EventStore remains the source of truth.
"""

from __future__ import annotations

import os
from typing import Any, Optional
from contextlib import contextmanager

import structlog

logger = structlog.get_logger("observability.otel")


class OTelBridge:
    """
    OpenTelemetry bridge for El Monstruo.

    Lazily imports OTel SDK — if not installed, degrades to no-op.
    Supports OTLP export to any compatible backend.
    """

    def __init__(self) -> None:
        self._tracer: Any = None
        self._provider: Any = None
        self._enabled: bool = False

    async def initialize(self) -> bool:
        """
        Initialize the OpenTelemetry tracer with OTLP exporter.
        Reads OTEL_EXPORTER_OTLP_ENDPOINT from environment.
        """
        endpoint = os.environ.get(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            os.environ.get("LANGFUSE_HOST", ""),
        )

        if not endpoint:
            logger.info("otel_disabled", reason="no OTLP endpoint configured")
            return False

        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )

            resource = Resource.create(
                {
                    "service.name": "el-monstruo",
                    "service.version": "0.2.0-sprint1",
                    "deployment.environment": os.environ.get("ENV", "development"),
                }
            )

            self._provider = TracerProvider(resource=resource)
            exporter = OTLPSpanExporter(endpoint=endpoint)
            self._provider.add_span_processor(BatchSpanProcessor(exporter))

            trace.set_tracer_provider(self._provider)
            self._tracer = trace.get_tracer("el-monstruo", "0.2.0")
            self._enabled = True

            logger.info("otel_connected", endpoint=endpoint)
            return True

        except ImportError:
            logger.warning(
                "otel_not_installed",
                hint="pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp",
            )
            return False
        except Exception as e:
            logger.error("otel_init_failed", error=str(e))
            return False

    @contextmanager
    def span(
        self,
        name: str,
        attributes: Optional[dict[str, Any]] = None,
    ):
        """
        Create an OpenTelemetry span as a context manager.

        Usage:
            with otel.span("think_node", {"model": "gpt-5.4"}) as span:
                result = await think(state)
                span.set_attribute("tokens", result.tokens)
        """
        if not self._enabled or not self._tracer:
            yield _NoOpSpan()
            return

        try:
            with self._tracer.start_as_current_span(name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, str(value))
                yield span
        except Exception as e:
            logger.warning("otel_span_error", name=name, error=str(e))
            yield _NoOpSpan()

    def record_exception(self, span: Any, exception: Exception) -> None:
        """Record an exception on a span."""
        if not self._enabled:
            return
        try:
            if hasattr(span, "record_exception"):
                span.record_exception(exception)
                span.set_status(
                    _get_error_status()
                )
        except Exception:
            pass

    async def shutdown(self) -> None:
        """Shutdown the tracer provider."""
        if self._provider:
            try:
                self._provider.shutdown()
                logger.info("otel_shutdown")
            except Exception as e:
                logger.warning("otel_shutdown_error", error=str(e))

    @property
    def enabled(self) -> bool:
        return self._enabled


class _NoOpSpan:
    """No-op span for when OTel is disabled."""

    def set_attribute(self, key: str, value: Any) -> None:
        pass

    def record_exception(self, exception: Exception) -> None:
        pass

    def set_status(self, status: Any) -> None:
        pass

    def add_event(self, name: str, attributes: Optional[dict] = None) -> None:
        pass


def _get_error_status():
    """Get OTel error status, handling import gracefully."""
    try:
        from opentelemetry.trace import StatusCode, Status
        return Status(StatusCode.ERROR)
    except ImportError:
        return None
