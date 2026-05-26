"""
B4 Memento Integration — Anti-Dory FORGE v3.0

Integrates with Protocolo Memento for persistent memory validation.
Provides read/validate path — no production writes.

Architecture:
1. Read memories from Memento store (Supabase semantic_memories).
2. Validate memory integrity (hash, TTL, source).
3. Provide memory context to B2 (Claim VG) and B9 (Authority Matrix).
4. Detect memory drift (stale/contradictory memories).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Protocol


class MementoStoreReader(Protocol):
    """Protocol for reading from Memento store."""

    def fetch_memories(self, query: str, limit: int = 10) -> list[dict]: ...
    def get_memory_by_id(self, memory_id: str) -> dict: ...


class MemoryStatus(Enum):
    VALID = "VALID"
    STALE = "STALE"
    CORRUPTED = "CORRUPTED"
    EXPIRED = "EXPIRED"
    MISSING = "MISSING"


@dataclass
class Memory:
    """A single memory from the Memento store."""

    id: str
    content: str
    content_hash: str
    source: str
    created_at: datetime
    ttl_hours: Optional[int]
    metadata: dict


@dataclass
class MemoryValidation:
    """Result of validating a single memory."""

    memory_id: str
    status: MemoryStatus
    reason: str
    is_valid: bool


@dataclass
class MementoContext:
    """Context provided by Memento to other Anti-Dory modules."""

    memories: list[Memory]
    validations: list[MemoryValidation]
    valid_count: int
    stale_count: int
    corrupted_count: int

    @property
    def health_ratio(self) -> float:
        total = len(self.validations)
        if total == 0:
            return 1.0
        return self.valid_count / total


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of memory content for integrity check."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class MementoIntegration:
    """
    B4 Memento Integration.

    Provides:
    - fetch_context(query) → MementoContext
    - validate_memory(memory) → MemoryValidation
    - check_drift(memories) → list[MemoryValidation]
    - is_memory_expired(memory) → bool
    """

    DEFAULT_TTL_HOURS = 720  # 30 days

    def __init__(self, store: Optional[MementoStoreReader] = None):
        self._store = store

    def fetch_context(self, query: str, limit: int = 10) -> MementoContext:
        """
        Fetch and validate memories relevant to a query.

        Args:
            query: Search query for semantic memory retrieval.
            limit: Maximum memories to fetch.

        Returns:
            MementoContext with validated memories.
        """
        if self._store is None:
            return MementoContext(memories=[], validations=[], valid_count=0, stale_count=0, corrupted_count=0)

        raw_memories = self._store.fetch_memories(query, limit=limit)
        memories = [self._dict_to_memory(m) for m in raw_memories]
        validations = [self.validate_memory(m) for m in memories]

        valid_count = sum(1 for v in validations if v.is_valid)
        stale_count = sum(1 for v in validations if v.status == MemoryStatus.STALE)
        corrupted_count = sum(1 for v in validations if v.status == MemoryStatus.CORRUPTED)

        return MementoContext(
            memories=memories,
            validations=validations,
            valid_count=valid_count,
            stale_count=stale_count,
            corrupted_count=corrupted_count,
        )

    def validate_memory(self, memory: Memory) -> MemoryValidation:
        """
        Validate a single memory's integrity.

        Checks:
        1. Content hash matches stored hash.
        2. Memory is not expired (TTL).
        3. Content is not empty.
        """
        # Check empty content
        if not memory.content or not memory.content.strip():
            return MemoryValidation(
                memory_id=memory.id,
                status=MemoryStatus.CORRUPTED,
                reason="Empty content",
                is_valid=False,
            )

        # Check hash integrity
        computed_hash = compute_content_hash(memory.content)
        if memory.content_hash and computed_hash != memory.content_hash:
            return MemoryValidation(
                memory_id=memory.id,
                status=MemoryStatus.CORRUPTED,
                reason=f"Hash mismatch: expected {memory.content_hash[:8]}..., got {computed_hash[:8]}...",
                is_valid=False,
            )

        # Check TTL expiration (only if explicit TTL is set)
        if memory.ttl_hours is not None and self.is_memory_expired(memory):
            return MemoryValidation(
                memory_id=memory.id,
                status=MemoryStatus.EXPIRED,
                reason=f"Memory expired (TTL: {memory.ttl_hours}h)",
                is_valid=False,
            )

        # Check staleness (older than 90 days without TTL)
        if self._is_stale(memory):
            return MemoryValidation(
                memory_id=memory.id,
                status=MemoryStatus.STALE,
                reason="Memory older than 90 days without explicit TTL",
                is_valid=False,
            )

        return MemoryValidation(
            memory_id=memory.id,
            status=MemoryStatus.VALID,
            reason="All checks passed",
            is_valid=True,
        )

    def is_memory_expired(self, memory: Memory) -> bool:
        """Check if a memory has exceeded its TTL."""
        ttl = memory.ttl_hours or self.DEFAULT_TTL_HOURS
        expiry = memory.created_at + timedelta(hours=ttl)
        return datetime.utcnow() > expiry

    def check_drift(self, memories: list[Memory]) -> list[MemoryValidation]:
        """
        Check a batch of memories for drift/corruption.

        Returns list of validations, highlighting issues.
        """
        return [self.validate_memory(m) for m in memories]

    def _is_stale(self, memory: Memory) -> bool:
        """Check if memory is stale (>90 days without explicit TTL)."""
        if memory.ttl_hours is not None:
            return False  # Has explicit TTL, use that instead
        age = datetime.utcnow() - memory.created_at
        return age > timedelta(days=90)

    @staticmethod
    def _dict_to_memory(data: dict) -> Memory:
        """Convert a raw dict from store to Memory dataclass."""
        return Memory(
            id=data.get("id", "unknown"),
            content=data.get("content", ""),
            content_hash=data.get("content_hash", ""),
            source=data.get("source", "unknown"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            ttl_hours=data.get("ttl_hours"),
            metadata=data.get("metadata", {}),
        )
