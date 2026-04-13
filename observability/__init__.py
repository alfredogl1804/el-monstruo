"""
El Monstruo — Observability Layer
==================================
Langfuse v4 SDK + OpenTelemetry bridge for sovereign tracing.

Architecture:
    EventStore (sovereign) → ObservabilityBridge → Langfuse (mirror)
                                                → OpenTelemetry (export)

Principle: Our EventStore is the source of truth.
Langfuse is a mirror — useful but replaceable.
"""
