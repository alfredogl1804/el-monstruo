"""
El Monstruo — Supabase Client (Día 2)
========================================
Shared async-compatible Supabase client wrapper.
All memory modules use this single client for persistence.

Principio: Un solo punto de conexión, control total.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import structlog

logger = structlog.get_logger("supabase_client")


class SupabaseClient:
    """
    Thin wrapper around the Supabase Python client.
    Provides async-compatible methods for CRUD operations.

    Uses the sync supabase-py client internally but wraps
    it for consistent async interface across the codebase.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
    ) -> None:
        self._url = url or os.environ.get("SUPABASE_URL", "")
        self._key = key or os.environ.get("SUPABASE_SERVICE_KEY", "")
        self._client = None
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> bool:
        """Initialize the Supabase connection."""
        if not self._url or not self._key:
            logger.warning(
                "supabase_not_configured",
                hint="Set SUPABASE_URL and SUPABASE_SERVICE_KEY",
            )
            return False

        try:
            from supabase import create_client

            self._client = create_client(self._url, self._key)
            self._connected = True
            logger.info("supabase_connected", url=self._url[:50])
            return True
        except ImportError:
            logger.warning("supabase_sdk_not_installed", hint="pip install supabase")
            return False
        except Exception as e:
            logger.error("supabase_connection_failed", error=str(e))
            return False

    async def insert(self, table: str, data: dict[str, Any]) -> Optional[dict]:
        """Insert a row into a table."""
        if not self._connected:
            return None
        try:
            result = self._client.table(table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("supabase_insert_failed", table=table, error=str(e))
            return None

    async def insert_batch(self, table: str, rows: list[dict[str, Any]]) -> list[dict]:
        """Insert multiple rows in a single transaction."""
        if not self._connected or not rows:
            return []
        try:
            result = self._client.table(table).insert(rows).execute()
            return result.data or []
        except Exception as e:
            logger.error(
                "supabase_batch_insert_failed",
                table=table,
                count=len(rows),
                error=str(e),
            )
            return []

    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = True,
        limit: Optional[int] = None,
    ) -> list[dict]:
        """Select rows from a table with optional filters."""
        if not self._connected:
            return []
        try:
            query = self._client.table(table).select(columns)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)

            if order_by:
                query = query.order(order_by, desc=order_desc)

            if limit:
                query = query.limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error("supabase_select_failed", table=table, error=str(e))
            return []

    async def upsert(self, table: str, data: dict[str, Any], on_conflict: str = "") -> Optional[dict]:
        """Upsert (insert or update) a row."""
        if not self._connected:
            return None
        try:
            result = self._client.table(table).upsert(data, on_conflict=on_conflict).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("supabase_upsert_failed", table=table, error=str(e))
            return None

    async def update(
        self,
        table: str,
        data: dict[str, Any],
        filters: dict[str, Any],
    ) -> Optional[dict]:
        """Update rows matching filters."""
        if not self._connected:
            return None
        try:
            query = self._client.table(table).update(data)
            for key, value in filters.items():
                query = query.eq(key, value)
            result = query.execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("supabase_update_failed", table=table, error=str(e))
            return None

    async def delete(self, table: str, filters: dict[str, Any]) -> bool:
        """Delete rows matching filters."""
        if not self._connected:
            return False
        try:
            query = self._client.table(table).delete()
            for key, value in filters.items():
                query = query.eq(key, value)
            query.execute()
            return True
        except Exception as e:
            logger.error("supabase_delete_failed", table=table, error=str(e))
            return False

    async def rpc(self, function_name: str, params: dict[str, Any] = None) -> Any:
        """Call a Postgres function via RPC."""
        if not self._connected:
            return None
        try:
            result = self._client.rpc(function_name, params or {}).execute()
            return result.data
        except Exception as e:
            logger.error("supabase_rpc_failed", function=function_name, error=str(e))
            return None

    async def count(self, table: str, filters: Optional[dict[str, Any]] = None) -> int:
        """Count rows in a table."""
        if not self._connected:
            return 0
        try:
            query = self._client.table(table).select("*", count="exact")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            result = query.limit(0).execute()
            return result.count or 0
        except Exception as e:
            logger.error("supabase_count_failed", table=table, error=str(e))
            return 0
