"""
B3 Plan Ledger Adapter — Anti-Dory FORGE v3.0

Append-only immutable ledger of plans and delegations.
Status transitions are the ONLY allowed mutations.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Protocol


class SupabaseClient(Protocol):
    """Protocol for Supabase client dependency injection."""

    def table(self, name: str): ...


class PlanStatus(Enum):
    CREATED = "CREATED"
    DELEGATED = "DELEGATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# Valid state transitions
VALID_TRANSITIONS = {
    PlanStatus.CREATED: {PlanStatus.DELEGATED, PlanStatus.IN_PROGRESS, PlanStatus.CANCELLED},
    PlanStatus.DELEGATED: {PlanStatus.IN_PROGRESS, PlanStatus.CANCELLED},
    PlanStatus.IN_PROGRESS: {PlanStatus.COMPLETED, PlanStatus.FAILED, PlanStatus.CANCELLED},
    PlanStatus.COMPLETED: set(),  # Terminal
    PlanStatus.FAILED: set(),  # Terminal
    PlanStatus.CANCELLED: set(),  # Terminal
}


@dataclass
class PlanEntry:
    """Represents a single plan in the ledger."""

    id: str
    plan_hash: str
    plan_summary: str
    status: PlanStatus
    delegated_to: Optional[str]
    delegated_at: Optional[datetime]
    parent_plan_id: Optional[str]
    metadata: dict
    created_at: datetime
    completed_at: Optional[datetime]


@dataclass
class PlanCreateRequest:
    """Request to create a new plan entry."""

    plan_summary: str
    delegated_to: Optional[str] = None
    parent_plan_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class PlanLedgerError(Exception):
    pass


class PlanNotFoundError(PlanLedgerError):
    pass


class InvalidTransitionError(PlanLedgerError):
    pass


class PlanDuplicateError(PlanLedgerError):
    pass


def compute_plan_hash(summary: str, metadata: dict) -> str:
    """Compute deterministic hash for a plan."""
    payload = json.dumps({"summary": summary, "metadata": metadata}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


class PlanLedgerAdapter:
    """
    Adapter for B3 Plan Ledger (Supabase).

    Provides:
    - create_plan(request) → PlanEntry
    - get_plan(plan_id) → PlanEntry
    - transition_status(plan_id, new_status) → PlanEntry
    - list_plans(status_filter, delegated_to) → list[PlanEntry]
    - get_plan_tree(root_id) → list[PlanEntry]
    """

    TABLE_NAME = "anti_dory_plan_ledger"

    def __init__(self, client: Optional[SupabaseClient] = None):
        self._client = client

    @property
    def client(self) -> SupabaseClient:
        if self._client is None:
            raise PlanLedgerError("Supabase client not initialized.")
        return self._client

    def create_plan(self, request: PlanCreateRequest) -> PlanEntry:
        """Create a new plan entry in the ledger."""
        plan_hash = compute_plan_hash(request.plan_summary, request.metadata)
        status = PlanStatus.DELEGATED if request.delegated_to else PlanStatus.CREATED

        data = {
            "plan_hash": plan_hash,
            "plan_summary": request.plan_summary,
            "status": status.value,
            "delegated_to": request.delegated_to,
            "delegated_at": datetime.utcnow().isoformat() if request.delegated_to else None,
            "parent_plan_id": request.parent_plan_id,
            "metadata": request.metadata,
        }

        try:
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                raise PlanDuplicateError(f"Plan with hash '{plan_hash}' already exists")
            raise PlanLedgerError(f"Insert failed: {e}")

        if not response.data:
            raise PlanLedgerError("Insert returned no data")

        return self._row_to_plan(response.data[0])

    def get_plan(self, plan_id: str) -> PlanEntry:
        """Retrieve a plan by ID."""
        response = self.client.table(self.TABLE_NAME).select("*").eq("id", plan_id).limit(1).execute()
        if not response.data:
            raise PlanNotFoundError(f"Plan '{plan_id}' not found")
        return self._row_to_plan(response.data[0])

    def transition_status(self, plan_id: str, new_status: PlanStatus) -> PlanEntry:
        """
        Transition a plan to a new status.
        Validates the transition is allowed.
        """
        current = self.get_plan(plan_id)
        allowed = VALID_TRANSITIONS.get(current.status, set())

        if new_status not in allowed:
            raise InvalidTransitionError(
                f"Cannot transition from {current.status.value} to {new_status.value}. "
                f"Allowed: {[s.value for s in allowed]}"
            )

        update_data = {"status": new_status.value}
        if new_status in (PlanStatus.COMPLETED, PlanStatus.FAILED, PlanStatus.CANCELLED):
            update_data["completed_at"] = datetime.utcnow().isoformat()

        response = self.client.table(self.TABLE_NAME).update(update_data).eq("id", plan_id).execute()

        if not response.data:
            raise PlanLedgerError("Update returned no data")

        return self._row_to_plan(response.data[0])

    def list_plans(
        self,
        status_filter: Optional[PlanStatus] = None,
        delegated_to: Optional[str] = None,
        limit: int = 50,
    ) -> list[PlanEntry]:
        """List plans with optional filters."""
        query = self.client.table(self.TABLE_NAME).select("*")

        if status_filter:
            query = query.eq("status", status_filter.value)
        if delegated_to:
            query = query.eq("delegated_to", delegated_to)

        response = query.order("created_at", desc=True).limit(limit).execute()
        return [self._row_to_plan(row) for row in (response.data or [])]

    @staticmethod
    def _row_to_plan(row: dict) -> PlanEntry:
        """Convert a database row to PlanEntry."""
        return PlanEntry(
            id=row["id"],
            plan_hash=row["plan_hash"],
            plan_summary=row["plan_summary"],
            status=PlanStatus(row["status"]),
            delegated_to=row.get("delegated_to"),
            delegated_at=datetime.fromisoformat(row["delegated_at"]) if row.get("delegated_at") else None,
            parent_plan_id=row.get("parent_plan_id"),
            metadata=row.get("metadata", {}),
            created_at=datetime.fromisoformat(row["created_at"]),
            completed_at=datetime.fromisoformat(row["completed_at"]) if row.get("completed_at") else None,
        )
