"""
El Monstruo — Checkpoint Store (Día 2)
========================================
Full implementation of CheckpointStore contract.
Persistent checkpoints with in-memory + Supabase dual mode.
System state tracking for health monitoring.

Principio: Si no puedes reconstruir tu estado, no puedes sobrevivir.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

import structlog

from contracts.checkpoint_model import (
    CheckpointData,
    CheckpointStore,
    CheckpointType,
    SystemHealth,
    SystemState,
)
from memory.supabase_client import SupabaseClient

logger = structlog.get_logger("checkpoint_store")


class SovereignCheckpointStore(CheckpointStore):
    """
    Sovereign checkpoint store implementation.

    Dual mode:
    - In-memory: always active, fast access
    - Supabase: persistent, survives restarts

    Features:
    - Save/load checkpoints with full state snapshots
    - TTL-based automatic expiration
    - System state tracking
    - Audit trail for all checkpoint operations
    """

    def __init__(self, db: Optional[SupabaseClient] = None) -> None:
        self._checkpoints: dict[UUID, CheckpointData] = {}
        self._by_run: dict[UUID, list[UUID]] = {}
        self._system_states: list[SystemState] = []
        self._db = db

    async def initialize(self) -> None:
        """Load recent checkpoints from Supabase if available."""
        if self._db and self._db.connected:
            try:
                rows = await self._db.select(
                    "checkpoints",
                    order_by="created_at",
                    order_desc=True,
                    limit=100,
                )
                for row in rows:
                    cp = self._row_to_checkpoint(row)
                    if cp and not self._is_expired(cp):
                        self._checkpoints[cp.checkpoint_id] = cp
                        if cp.run_id:
                            self._by_run.setdefault(cp.run_id, []).append(cp.checkpoint_id)

                logger.info(
                    "checkpoint_store_initialized",
                    loaded=len(self._checkpoints),
                    persistence="supabase",
                )
            except Exception as e:
                logger.warning("checkpoint_load_failed", error=str(e))
        else:
            logger.info("checkpoint_store_initialized", persistence="in-memory")

    # ── Core Operations ────────────────────────────────────────────

    async def save(self, checkpoint: CheckpointData) -> UUID:
        """Save a checkpoint. Returns the checkpoint_id."""
        # In-memory
        self._checkpoints[checkpoint.checkpoint_id] = checkpoint
        if checkpoint.run_id:
            self._by_run.setdefault(checkpoint.run_id, []).append(
                checkpoint.checkpoint_id
            )

        # Persist to Supabase
        if self._db and self._db.connected:
            await self._db.insert("checkpoints", self._checkpoint_to_row(checkpoint))

        logger.info(
            "checkpoint_saved",
            checkpoint_id=str(checkpoint.checkpoint_id),
            checkpoint_type=checkpoint.checkpoint_type.value,
            run_id=str(checkpoint.run_id) if checkpoint.run_id else None,
            step=checkpoint.step,
        )
        return checkpoint.checkpoint_id

    async def load(self, checkpoint_id: UUID) -> Optional[CheckpointData]:
        """Load a checkpoint by ID. Returns None if not found or expired."""
        # Try in-memory first
        cp = self._checkpoints.get(checkpoint_id)
        if cp:
            if self._is_expired(cp):
                del self._checkpoints[checkpoint_id]
                return None
            return cp

        # Try Supabase
        if self._db and self._db.connected:
            rows = await self._db.select(
                "checkpoints",
                filters={"checkpoint_id": str(checkpoint_id)},
                limit=1,
            )
            if rows:
                cp = self._row_to_checkpoint(rows[0])
                if cp and not self._is_expired(cp):
                    self._checkpoints[cp.checkpoint_id] = cp
                    return cp

        return None

    async def load_latest(
        self,
        run_id: Optional[UUID] = None,
    ) -> Optional[CheckpointData]:
        """Load the most recent checkpoint, optionally for a specific run."""
        if run_id:
            # Get checkpoints for this run
            cp_ids = self._by_run.get(run_id, [])
            if cp_ids:
                # Get the most recent
                candidates = [
                    self._checkpoints[cid]
                    for cid in cp_ids
                    if cid in self._checkpoints and not self._is_expired(self._checkpoints[cid])
                ]
                if candidates:
                    return max(candidates, key=lambda c: c.created_at)

        # Get the most recent overall
        valid = [
            cp for cp in self._checkpoints.values()
            if not self._is_expired(cp)
            and (run_id is None or cp.run_id == run_id)
        ]
        if valid:
            return max(valid, key=lambda c: c.created_at)

        # Try Supabase
        if self._db and self._db.connected:
            filters = {}
            if run_id:
                filters["run_id"] = str(run_id)
            rows = await self._db.select(
                "checkpoints",
                filters=filters,
                order_by="created_at",
                order_desc=True,
                limit=1,
            )
            if rows:
                cp = self._row_to_checkpoint(rows[0])
                if cp and not self._is_expired(cp):
                    self._checkpoints[cp.checkpoint_id] = cp
                    return cp

        return None

    async def list_checkpoints(
        self,
        run_id: Optional[UUID] = None,
        checkpoint_type: Optional[CheckpointType] = None,
        limit: int = 20,
    ) -> list[CheckpointData]:
        """List checkpoints with optional filters."""
        candidates = list(self._checkpoints.values())

        if run_id:
            candidates = [c for c in candidates if c.run_id == run_id]
        if checkpoint_type:
            candidates = [c for c in candidates if c.checkpoint_type == checkpoint_type]

        # Filter expired
        candidates = [c for c in candidates if not self._is_expired(c)]

        # Sort by created_at descending
        candidates.sort(key=lambda c: c.created_at, reverse=True)
        return candidates[:limit]

    async def delete(self, checkpoint_id: UUID) -> bool:
        """Delete a specific checkpoint."""
        if checkpoint_id in self._checkpoints:
            cp = self._checkpoints.pop(checkpoint_id)
            # Remove from run index
            if cp.run_id and cp.run_id in self._by_run:
                self._by_run[cp.run_id] = [
                    cid for cid in self._by_run[cp.run_id]
                    if cid != checkpoint_id
                ]

        # Delete from Supabase
        if self._db and self._db.connected:
            await self._db.delete("checkpoints", {"checkpoint_id": str(checkpoint_id)})

        logger.info("checkpoint_deleted", checkpoint_id=str(checkpoint_id))
        return True

    async def cleanup_expired(self) -> int:
        """Delete expired checkpoints. Returns count deleted."""
        expired_ids = [
            cp.checkpoint_id
            for cp in self._checkpoints.values()
            if self._is_expired(cp)
        ]

        for cid in expired_ids:
            await self.delete(cid)

        if expired_ids:
            logger.info("checkpoints_cleaned", count=len(expired_ids))

        return len(expired_ids)

    # ── System State ───────────────────────────────────────────────

    async def save_system_state(self, state: SystemState) -> None:
        """Save the current system state."""
        self._system_states.append(state)

        # Keep only last 100 states in memory
        if len(self._system_states) > 100:
            self._system_states = self._system_states[-100:]

        # Persist to Supabase
        if self._db and self._db.connected:
            await self._db.insert("system_state", {
                "state_id": str(state.state_id),
                "health": state.health.value,
                "active_runs": state.active_runs,
                "total_runs_today": state.total_runs_today,
                "total_cost_today_usd": state.total_cost_today_usd,
                "total_tokens_today": state.total_tokens_today,
                "models_available": state.models_available,
                "models_degraded": state.models_degraded,
                "last_error": state.last_error,
                "uptime_seconds": state.uptime_seconds,
                "checked_at": state.checked_at.isoformat()
                if hasattr(state.checked_at, 'isoformat')
                else str(state.checked_at),
            })

        logger.debug(
            "system_state_saved",
            health=state.health.value,
            active_runs=state.active_runs,
        )

    async def get_system_state(self) -> SystemState:
        """Get the most recent system state."""
        if self._system_states:
            return self._system_states[-1]

        # Try Supabase
        if self._db and self._db.connected:
            rows = await self._db.select(
                "system_state",
                order_by="checked_at",
                order_desc=True,
                limit=1,
            )
            if rows:
                return self._row_to_system_state(rows[0])

        # Return default healthy state
        return SystemState()

    async def get_system_health(self) -> SystemHealth:
        """Shortcut: get just the health status."""
        state = await self.get_system_state()
        return state.health

    # ── Stats ──────────────────────────────────────────────────────

    async def get_stats(self) -> dict[str, Any]:
        """Get checkpoint store statistics."""
        valid = [c for c in self._checkpoints.values() if not self._is_expired(c)]
        expired = len(self._checkpoints) - len(valid)

        type_counts = {}
        for cp in valid:
            t = cp.checkpoint_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "total_checkpoints": len(valid),
            "expired_pending_cleanup": expired,
            "unique_runs": len(self._by_run),
            "by_type": type_counts,
            "system_states_in_memory": len(self._system_states),
            "persistence": "supabase" if (self._db and self._db.connected) else "in-memory",
        }

    # ── Private Helpers ────────────────────────────────────────────

    @staticmethod
    def _is_expired(cp: CheckpointData) -> bool:
        """Check if a checkpoint has expired based on TTL."""
        now = datetime.now(timezone.utc)
        created = cp.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        expiry = created + timedelta(hours=cp.ttl_hours)
        return now > expiry

    @staticmethod
    def _checkpoint_to_row(cp: CheckpointData) -> dict[str, Any]:
        """Convert CheckpointData to Supabase row."""
        return {
            "checkpoint_id": str(cp.checkpoint_id),
            "checkpoint_type": cp.checkpoint_type.value,
            "run_id": str(cp.run_id) if cp.run_id else None,
            "step": cp.step,
            "kernel_state": cp.kernel_state,
            "memory_state": cp.memory_state,
            "router_state": cp.router_state,
            "policy_state": cp.policy_state,
            "active_tools": cp.active_tools,
            "pending_actions": cp.pending_actions,
            "conversation_context": cp.conversation_context,
            "reason": cp.reason,
            "ttl_hours": cp.ttl_hours,
            "created_at": cp.created_at.isoformat()
            if hasattr(cp.created_at, 'isoformat')
            else str(cp.created_at),
        }

    @staticmethod
    def _row_to_checkpoint(row: dict) -> Optional[CheckpointData]:
        """Convert Supabase row to CheckpointData."""
        try:
            from uuid import UUID as _UUID
            return CheckpointData(
                checkpoint_id=_UUID(row["checkpoint_id"]),
                checkpoint_type=CheckpointType(row.get("checkpoint_type", "auto")),
                run_id=_UUID(row["run_id"]) if row.get("run_id") else None,
                step=row.get("step", 0),
                kernel_state=row.get("kernel_state", {}),
                memory_state=row.get("memory_state", {}),
                router_state=row.get("router_state", {}),
                policy_state=row.get("policy_state", {}),
                active_tools=row.get("active_tools", []),
                pending_actions=row.get("pending_actions", []),
                conversation_context=row.get("conversation_context", {}),
                reason=row.get("reason", ""),
                ttl_hours=row.get("ttl_hours", 168),
                created_at=datetime.fromisoformat(row["created_at"])
                if isinstance(row.get("created_at"), str)
                else row.get("created_at", datetime.now(timezone.utc)),
            )
        except Exception:
            return None

    @staticmethod
    def _row_to_system_state(row: dict) -> SystemState:
        """Convert Supabase row to SystemState."""
        from uuid import UUID as _UUID
        return SystemState(
            state_id=_UUID(row.get("state_id", str(uuid4()))),
            health=SystemHealth(row.get("health", "healthy")),
            active_runs=row.get("active_runs", 0),
            total_runs_today=row.get("total_runs_today", 0),
            total_cost_today_usd=row.get("total_cost_today_usd", 0.0),
            total_tokens_today=row.get("total_tokens_today", 0),
            models_available=row.get("models_available", []),
            models_degraded=row.get("models_degraded", []),
            last_error=row.get("last_error"),
            uptime_seconds=row.get("uptime_seconds", 0.0),
            checked_at=datetime.fromisoformat(row["checked_at"])
            if isinstance(row.get("checked_at"), str)
            else datetime.now(timezone.utc),
        )
