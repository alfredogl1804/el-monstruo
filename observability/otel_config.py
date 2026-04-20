"""
El Monstruo — OpenTelemetry Configuration (Sprint 16)
=====================================================
Configures OTel tracing and metrics export.
Dual export: Langfuse (primary) + OTLP (optional secondary).

The kernel uses Langfuse as the primary observability backend,
but OTel provides a vendor-neutral escape hatch.

Usage:
    Called during ObservabilityManager.initialize() if
    OTEL_ENABLED=true is set in environment.
"""

from __future__ import annotations

import os
from typing import Optional

import structlog

logger = structlog.get_logger("observability.otel")

OTEL_ENABLED = os.environ.get("OTEL_ENABLED", "false").lower() == "true"
OTEL_ENDPOINT = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
OTEL_SERVICE_NAME = os.environ.get("OTEL_SERVICE_NAME", "el-monstruo-kernel")


def configure_otel() -> Optional[dict]:
    """
    Configure OpenTelemetry if enabled.
    Returns status dict or None if disabled.

    Note: This is a lightweight config that sets up the OTel SDK
    for trace context propagation. The actual trace data goes to
    Langfuse via CallbackHandler; OTel provides the W3C trace
    context headers for distributed tracing across services.
    """
    if not OTEL_ENABLED:
        logger.debug("otel_disabled")
        return None

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider

        resource = Resource.create(
            {
                "service.name": OTEL_SERVICE_NAME,
                "service.version": "0.9.0-sprint15",
                "deployment.environment": os.environ.get("RAILWAY_ENVIRONMENT", "development"),
            }
        )

        provider = TracerProvider(resource=resource)

        # Add OTLP exporter if endpoint configured
        if OTEL_ENDPOINT:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            exporter = OTLPSpanExporter(endpoint=OTEL_ENDPOINT)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            logger.info("otel_otlp_exporter_configured", endpoint=OTEL_ENDPOINT)

        trace.set_tracer_provider(provider)

        logger.info(
            "otel_configured",
            service=OTEL_SERVICE_NAME,
            endpoint=OTEL_ENDPOINT or "none",
        )

        return {
            "enabled": True,
            "service_name": OTEL_SERVICE_NAME,
            "endpoint": OTEL_ENDPOINT or "none",
        }

    except ImportError as e:
        logger.warning(
            "otel_import_failed",
            error=str(e),
            hint="pip install opentelemetry-sdk opentelemetry-exporter-otlp",
        )
        return {"enabled": False, "error": "missing_dependencies"}
    except Exception as e:
        logger.error("otel_config_failed", error=str(e))
        return {"enabled": False, "error": str(e)}
