"""
El Monstruo — Event Store (Día 1)
====================================
Append-only event log. Source of truth for auditoría y replay.
Dual mode: in-memory (always) + Supabase (when configured).

Principio: Todo lo que pasa se registra. Si no está en el log, no pasó.
"""

from __future__ import annotations

import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

import structlog

from contracts.event_envelope import EventEnvelope, EventCategory, Severity

logger = structlog.get_logger("event_store")


class EventStore:
    """
    Sovereign event store.

    Always keeps events in memory for fast access.
    Optionally persists to Supabase for durability.

    Thread-safe for single-process async usage.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        buffer_size: int = 1000,
    ) -> None:
        self._events: list[EventEnvelope] = []
        self._by_run: dict[UUID, list[EventEnvelope]] = defaultdict(list)
        self._by_category: dict[EventCategory, list[EventEnvelope]] = defaultdict(list)
        self._buffer_size = buffer_size
        self._supabase_url = supabase_url or os.environ.get("SUPABASE_URL")
        self._supabase_key = supabase_key or os.environ.get("SUPABASE_SERVICE_KEY")
        self._supabase_client = None
        self._persist_enabled = False

    async def initialize(self) -> None:
        """Initialize Supabase connection if configured."""
        if self._supabase_url and self._supabase_key:
            try:
                from supabase import create_client
                self._supabase_client = create_client(
                    self._supabase_url, self._supabase_key
                )
                self._persist_enabled = True
                logger.info("event_store_initialized", persistence="supabase")
            except Exception as e:
                logger.warning(
                    "supabase_init_failed",
                    error=str(e),
                    fallback="in-memory only",
                )
        else:
            logger.info("event_store_initialized", persistence="in-memory")

    # ── Core Operations ─────────────────────────────────────────────

    async def append(self, event: EventEnvelope) -> UUID:
        """
        Append an event to the store. Never modifies, never deletes.
        Returns the event_id.
        """
        # In-memory storage (always)
        self._events.append(event)

        if event.run_id:
            self._by_run[event.run_id].append(event)

        self._by_category[event.category].append(event)

        # Persist to Supabase (if enabled)
        if self._persist_enabled:
            await self._persist_event(event)

        # Trim in-memory buffer if needed
        if len(self._events) > self._buffer_size * 2:
            self._events = self._events[-self._buffer_size:]

        logger.debug(
            "event_appended",
            event_id=str(event.event_id),
            category=event.category.value,
            actor=event.actor,
        )

        return event.event_id

    async def append_batch(self, events: list[EventEnvelope]) -> list[UUID]:
        """Append multiple events atomically."""
        ids = []
        for event in events:
            eid = await self.append(event)
            ids.append(eid)
        return ids

    # ── Query Operations ────────────────────────────────────────────

    async def get_by_run(self, run_id: UUID) -> list[EventEnvelope]:
        """Get all events for a specific run (replay)."""
        return list(self._by_run.get(run_id, []))

    async def get_by_category(
        self,
        category: EventCategory,
        limit: int = 50,
    ) -> list[EventEnvelope]:
        """Get recent events of a specific category."""
        events = self._by_category.get(category, [])
        return events[-limit:]

    async def get_recent(self, limit: int = 50) -> list[EventEnvelope]:
        """Get the most recent events."""
        return self._events[-limit:]

    async def get_errors(self, limit: int = 20) -> list[EventEnvelope]:
        """Get recent error events."""
        errors = [
            e for e in self._events
            if e.severity in {Severity.ERROR, Severity.CRITICAL}
        ]
        return errors[-limit:]

    async def replay(self, run_id: UUID) -> list[dict[str, Any]]:
        """
        Replay a run: return all events in chronological order
        with human-readable format for debugging.
        """
        events = await self.get_by_run(run_id)
        return [
            {
                "step": i + 1,
                "timestamp": e.timestamp.isoformat(),
                "category": e.category.value,
                "severity": e.severity.value,
                "actor": e.actor,
                "action": e.action,
                "payload": e.payload,
            }
            for i, e in enumerate(sorted(events, key=lambda x: x.timestamp))
        ]

    async def count(
        self,
        category: Optional[EventCategory] = None,
    ) -> int:
        """Count events, optionally filtered by category."""
        if category:
            return len(self._by_category.get(category, []))
        return len(self._events)

    # ── Stats ───────────────────────────────────────────────────────

    async def get_stats(self) -> dict[str, Any]:
        """Get event store statistics."""
        now = datetime.now(timezone.utc)

        # Count events by category
        category_counts = {
            cat.value: len(events)
            for cat, events in self._by_category.items()
        }

        # Count active runs
        active_runs = set()
        completed_runs = set()
        for event in self._events:
            if event.run_id:
                if event.category in {
                    EventCategory.RUN_COMPLETED,
                    EventCategory.RUN_FAILED,
                    EventCategory.RUN_CANCELLED,
                }:
                    completed_runs.add(event.run_id)
                else:
                    active_runs.add(event.run_id)

        active_runs -= completed_runs

        return {
            "total_events": len(self._events),
            "unique_runs": len(self._by_run),
            "active_runs": len(active_runs),
            "completed_runs": len(completed_runs),
            "events_by_category": category_counts,
            "error_count": len([
                e for e in self._events
                if e.severity in {Severity.ERROR, Severity.CRITICAL}
            ]),
            "persistence": "supabase" if self._persist_enabled else "in-memory",
            "buffer_size": self._buffer_size,
            "checked_at": now.isoformat(),
        }

    # ── Supabase Persistence ────────────────────────────────────────

    async def _persist_event(self, event: EventEnvelope) -> None:
        """Persist a single event to Supabase."""
        if not self._supabase_client:
            return

        try:
            row = {
                "event_id": str(event.event_id),
                "category": event.category.value,
                "severity": event.severity.value,
                "run_id": str(event.run_id) if event.run_id else None,
                "user_id": event.user_id or None,
                "channel": event.channel or None,
                "actor": event.actor,
                "action": event.action,
                "payload": event.payload,
                "parent_id": str(event.parent_id) if event.parent_id else None,
                "trace_id": event.trace_id,
                "span_id": event.span_id,
                "version": event.version,
                "created_at": event.timestamp.isoformat(),
            }

            self._supabase_client.table("events").insert(row).execute()

        except Exception as e:
            logger.error(
                "persist_failed",
                event_id=str(event.event_id),
                error=str(e),
            )
