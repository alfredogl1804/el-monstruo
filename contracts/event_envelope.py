"""
El Monstruo — Contrato Soberano #3: EventEnvelope
===================================================
Define el formato canónico de eventos para TODO el sistema.
Cada acción, decisión, error y resultado se envuelve en un
EventEnvelope antes de persistirse.

Principio: Si no puedes reconstruir qué pasó, no tienes control.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4


class EventCategory(enum.Enum):
    """Categorías de eventos del sistema."""

    # Kernel events
    RUN_STARTED = "run.started"
    RUN_STEP = "run.step"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"
    RUN_CANCELLED = "run.cancelled"

    # Router events
    INTENT_CLASSIFIED = "route.intent_classified"
    ROUTE_DECIDED = "route.decided"
    ROUTE_FALLBACK = "route.fallback"

    # Enrichment events
    CONTEXT_ENRICHED = "enrich.context_enriched"

    # Model events
    MODEL_CALLED = "model.called"

    # Memory events
    MEMORY_STORED = "memory.stored"
    MEMORY_UPDATED = "memory.updated"
    MEMORY_SEARCHED = "memory.searched"
    ENTITY_CREATED = "memory.entity.created"
    RELATION_CREATED = "memory.relation.created"
    EPISODE_STARTED = "memory.episode.started"
    EPISODE_ENDED = "memory.episode.ended"

    # Tool events
    TOOL_CALLED = "tool.called"
    TOOL_SUCCEEDED = "tool.succeeded"
    TOOL_FAILED = "tool.failed"

    # Policy events
    POLICY_EVALUATED = "policy.evaluated"
    POLICY_BLOCKED = "policy.blocked"
    POLICY_OVERRIDDEN = "policy.overridden"

    # Checkpoint events
    CHECKPOINT_CREATED = "checkpoint.created"
    CHECKPOINT_RESTORED = "checkpoint.restored"

    # Observability events
    COST_RECORDED = "observability.cost"
    LATENCY_RECORDED = "observability.latency"
    ERROR_RECORDED = "observability.error"

    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_HEALTH = "system.health"

    # Human-in-the-loop events
    HUMAN_FEEDBACK = "hitl.feedback"
    HUMAN_APPROVED = "hitl.approved"
    HUMAN_REJECTED = "hitl.rejected"
    HUMAN_REVIEWED = "hitl.reviewed"

    # Channel events
    MESSAGE_RECEIVED = "channel.message.received"
    MESSAGE_SENT = "channel.message.sent"


class Severity(enum.Enum):
    """Severidad del evento para filtrado y alertas."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class EventEnvelope:
    """
    Sobre canónico para TODOS los eventos del sistema.

    Inmutable una vez creado. Append-only al event store.
    Contiene toda la información necesaria para:
    - Auditoría: quién, qué, cuándo, por qué
    - Replay: reconstruir cualquier estado
    - Observabilidad: métricas, costos, latencia
    - Debugging: trazar cualquier problema

    Campos:
        event_id    → Identificador único del evento
        category    → Tipo de evento (ver EventCategory)
        severity    → Nivel de severidad
        run_id      → Ejecución asociada (si aplica)
        user_id     → Usuario que originó la acción
        channel     → Canal de origen (telegram, console, api)
        actor       → Componente que generó el evento
        action      → Descripción de la acción
        payload     → Datos específicos del evento
        parent_id   → Evento padre (para cadenas causales)
        trace_id    → ID de traza distribuida (OpenTelemetry)
        span_id     → ID de span (OpenTelemetry)
        timestamp   → Momento exacto del evento (UTC)
        version     → Versión del schema del evento
    """

    event_id: UUID = field(default_factory=uuid4)
    category: EventCategory = EventCategory.RUN_STARTED
    severity: Severity = Severity.INFO
    run_id: Optional[UUID] = None
    user_id: str = ""
    channel: str = ""
    actor: str = ""  # "kernel", "router", "memory", "bot", etc.
    action: str = ""  # Human-readable description
    payload: dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[UUID] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"


# ── Event Builder ───────────────────────────────────────────────────


class EventBuilder:
    """
    Builder pattern para crear EventEnvelopes de forma legible.

    Uso:
        event = (EventBuilder()
            .category(EventCategory.RUN_STARTED)
            .actor("kernel")
            .action("Started new run")
            .for_run(run_id)
            .for_user(user_id)
            .with_payload({"model": "gpt-5.4", "intent": "chat"})
            .build())
    """

    def __init__(self) -> None:
        self._kwargs: dict[str, Any] = {}

    def category(self, cat: EventCategory) -> EventBuilder:
        self._kwargs["category"] = cat
        return self

    def severity(self, sev: Severity) -> EventBuilder:
        self._kwargs["severity"] = sev
        return self

    def actor(self, actor: str) -> EventBuilder:
        self._kwargs["actor"] = actor
        return self

    def action(self, action: str) -> EventBuilder:
        self._kwargs["action"] = action
        return self

    def for_run(self, run_id: UUID) -> EventBuilder:
        self._kwargs["run_id"] = run_id
        return self

    def for_run_str(self, run_id: str) -> EventBuilder:
        """Accept run_id as string (from LangGraph state serialization)."""
        if run_id:
            from uuid import UUID as UUIDType

            try:
                self._kwargs["run_id"] = UUIDType(run_id)
            except (ValueError, AttributeError):
                pass
        return self

    def for_user(self, user_id: str) -> EventBuilder:
        self._kwargs["user_id"] = user_id
        return self

    def on_channel(self, channel: str) -> EventBuilder:
        self._kwargs["channel"] = channel
        return self

    def with_payload(self, payload: dict[str, Any]) -> EventBuilder:
        self._kwargs["payload"] = payload
        return self

    def caused_by(self, parent_id: UUID) -> EventBuilder:
        self._kwargs["parent_id"] = parent_id
        return self

    def with_trace(self, trace_id: str, span_id: str) -> EventBuilder:
        self._kwargs["trace_id"] = trace_id
        self._kwargs["span_id"] = span_id
        return self

    def build(self) -> EventEnvelope:
        return EventEnvelope(**self._kwargs)
