"""Storage Supabase para validation_log (DSC-V-001)."""
from __future__ import annotations

from typing import Any, Optional

from kernel.validation.perplexity_decorator import ClaimRecord


class SupabaseStorage:
    """Persiste a tabla `validation_log` de Supabase via cliente injectado."""

    TABLE_NAME = "validation_log"

    def __init__(self, supabase_client: Any) -> None:
        self._client = supabase_client

    def find_latest(self, claim_type: str) -> Optional[ClaimRecord]:
        result = (
            self._client
            .table(self.TABLE_NAME)
            .select("*")
            .eq("claim_type", claim_type)
            .order("timestamp_unix", desc=True)
            .limit(1)
            .execute()
        )
        rows = result.data or []
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def find_latest_by_fingerprint(self, fingerprint: str) -> Optional[ClaimRecord]:
        result = (
            self._client
            .table(self.TABLE_NAME)
            .select("*")
            .eq("claim_fingerprint", fingerprint)
            .order("timestamp_unix", desc=True)
            .limit(1)
            .execute()
        )
        rows = result.data or []
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def insert(self, record: ClaimRecord) -> None:
        from dataclasses import asdict
        data = asdict(record)
        self._client.table(self.TABLE_NAME).insert(data).execute()

    @staticmethod
    def _row_to_record(row: dict[str, Any]) -> ClaimRecord:
        return ClaimRecord(
            claim_type=row["claim_type"],
            claim_fingerprint=row["claim_fingerprint"],
            claim_value=row["claim_value"],
            validator=row["validator"],
            evidence_url=row.get("evidence_url"),
            timestamp_unix=float(row["timestamp_unix"]),
            ttl_seconds=int(row["ttl_seconds"]),
            metadata=row.get("metadata") or {},
        )


__all__ = ["SupabaseStorage"]
