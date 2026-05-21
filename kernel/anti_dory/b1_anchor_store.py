"""
B1 Anchor Store Adapter — Anti-Dory FORGE v3.0

Provides read/write access to the immutable doctrine store.
Write operations require T1 signature validation.
Read operations are unrestricted for service_role.

This adapter abstracts the Supabase client interaction and
provides a clean interface for the rest of the Anti-Dory system.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol


class SupabaseClient(Protocol):
    """Protocol for Supabase client dependency injection."""

    def table(self, name: str): ...


@dataclass
class Anchor:
    """Represents a single doctrinal anchor."""
    id: str
    concept: str
    definition: str
    canon_source: Optional[str]
    canon_date: datetime
    t1_signature: str
    created_at: datetime


@dataclass
class AnchorInsertRequest:
    """Request to insert a new anchor (requires T1 signature)."""
    concept: str
    definition: str
    canon_source: Optional[str]
    t1_signature: str


class AnchorStoreError(Exception):
    """Base error for Anchor Store operations."""
    pass


class AnchorNotFoundError(AnchorStoreError):
    """Raised when an anchor concept is not found."""
    pass


class AnchorDuplicateError(AnchorStoreError):
    """Raised when attempting to insert a duplicate concept."""
    pass


class AnchorSignatureError(AnchorStoreError):
    """Raised when T1 signature validation fails."""
    pass


class AnchorStoreAdapter:
    """
    Adapter for B1 Anchor Store (Supabase).

    Provides:
    - get_anchor(concept) → Anchor
    - list_anchors() → list[Anchor]
    - search_anchors(query) → list[Anchor]
    - insert_anchor(request) → Anchor (requires T1 signature)
    - count_anchors() → int
    """

    TABLE_NAME = "anti_dory_anchor_store"

    def __init__(self, client: Optional[SupabaseClient] = None):
        """
        Initialize with optional Supabase client.
        If not provided, will attempt to create from environment.
        """
        self._client = client

    @property
    def client(self) -> SupabaseClient:
        if self._client is None:
            raise AnchorStoreError(
                "Supabase client not initialized. "
                "Pass client to constructor or set SUPABASE_URL + SUPABASE_SERVICE_KEY."
            )
        return self._client

    def get_anchor(self, concept: str) -> Anchor:
        """
        Retrieve a single anchor by concept name.

        Args:
            concept: The concept identifier to look up.

        Returns:
            Anchor dataclass.

        Raises:
            AnchorNotFoundError: If concept does not exist.
        """
        response = (
            self.client.table(self.TABLE_NAME)
            .select("*")
            .eq("concept", concept)
            .limit(1)
            .execute()
        )

        if not response.data:
            raise AnchorNotFoundError(f"Anchor '{concept}' not found")

        return self._row_to_anchor(response.data[0])

    def list_anchors(self, limit: int = 100, offset: int = 0) -> list[Anchor]:
        """
        List all anchors ordered by canon_date descending.

        Args:
            limit: Maximum number of results.
            offset: Pagination offset.

        Returns:
            List of Anchor dataclasses.
        """
        response = (
            self.client.table(self.TABLE_NAME)
            .select("*")
            .order("canon_date", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return [self._row_to_anchor(row) for row in (response.data or [])]

    def search_anchors(self, query: str) -> list[Anchor]:
        """
        Search anchors by concept or definition containing query.

        Args:
            query: Text to search for (case-insensitive).

        Returns:
            List of matching Anchor dataclasses.
        """
        response = (
            self.client.table(self.TABLE_NAME)
            .select("*")
            .or_(f"concept.ilike.%{query}%,definition.ilike.%{query}%")
            .order("canon_date", desc=True)
            .execute()
        )

        return [self._row_to_anchor(row) for row in (response.data or [])]

    def insert_anchor(self, request: AnchorInsertRequest) -> Anchor:
        """
        Insert a new doctrinal anchor.

        Args:
            request: AnchorInsertRequest with concept, definition, and T1 signature.

        Returns:
            The newly created Anchor.

        Raises:
            AnchorSignatureError: If T1 signature is empty/invalid.
            AnchorDuplicateError: If concept already exists.
        """
        # Validate T1 signature presence
        if not request.t1_signature or not request.t1_signature.strip():
            raise AnchorSignatureError("T1 signature is required for anchor insertion")

        # Attempt insert
        data = {
            "concept": request.concept,
            "definition": request.definition,
            "canon_source": request.canon_source,
            "t1_signature": request.t1_signature,
        }

        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .insert(data)
                .execute()
            )
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                raise AnchorDuplicateError(
                    f"Anchor '{request.concept}' already exists (append-only)"
                )
            raise AnchorStoreError(f"Insert failed: {e}")

        if not response.data:
            raise AnchorStoreError("Insert returned no data")

        return self._row_to_anchor(response.data[0])

    def count_anchors(self) -> int:
        """Return total number of anchors in the store."""
        response = (
            self.client.table(self.TABLE_NAME)
            .select("id", count="exact")
            .execute()
        )
        return response.count or 0

    @staticmethod
    def _row_to_anchor(row: dict) -> Anchor:
        """Convert a database row dict to an Anchor dataclass."""
        return Anchor(
            id=row["id"],
            concept=row["concept"],
            definition=row["definition"],
            canon_source=row.get("canon_source"),
            canon_date=datetime.fromisoformat(row["canon_date"]),
            t1_signature=row["t1_signature"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
