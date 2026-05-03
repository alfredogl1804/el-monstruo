"""
El Monstruo — Supabase Client (Día 2 / Sprint 83 fix)
========================================================
Shared async-compatible Supabase client wrapper.
All memory modules use this single client for persistence.

Sprint 83 FIX: All DB operations now run in asyncio.to_thread()
to prevent blocking the event loop. This was the root cause of
embrion_loop cycle_count=1 — the sync supabase-py calls blocked
the entire asyncio loop, preventing subsequent cycles.

Principio: Un solo punto de conexión, control total.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Optional

import structlog

logger = structlog.get_logger("supabase_client")

# Timeout for individual DB operations (seconds)
_DB_OP_TIMEOUT = 15


class SupabaseClient:
    """
    Thin wrapper around the Supabase Python client.
    Provides async-compatible methods for CRUD operations.

    Sprint 83: All sync supabase-py calls are wrapped in
    asyncio.to_thread() with a timeout to prevent event loop blocking.
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

    # ── Internal sync helpers (run inside to_thread) ─────────────

    def _insert_sync(self, table: str, data: dict[str, Any]) -> Optional[dict]:
        result = self._client.table(table).insert(data).execute()
        return result.data[0] if result.data else None

    def _insert_batch_sync(self, table: str, rows: list[dict[str, Any]]) -> list[dict]:
        result = self._client.table(table).insert(rows).execute()
        return result.data or []

    def _select_sync(
        self,
        table: str,
        columns: str,
        filters: Optional[dict[str, Any]],
        order_by: Optional[str],
        order_desc: bool,
        limit: Optional[int],
    ) -> list[dict]:
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

    def _upsert_sync(self, table: str, data: dict[str, Any], on_conflict: str) -> Optional[dict]:
        result = self._client.table(table).upsert(data, on_conflict=on_conflict).execute()
        return result.data[0] if result.data else None

    def _update_sync(self, table: str, data: dict[str, Any], filters: dict[str, Any]) -> Optional[dict]:
        query = self._client.table(table).update(data)
        for key, value in filters.items():
            query = query.eq(key, value)
        result = query.execute()
        return result.data[0] if result.data else None

    def _delete_sync(self, table: str, filters: dict[str, Any]) -> bool:
        query = self._client.table(table).delete()
        for key, value in filters.items():
            query = query.eq(key, value)
        query.execute()
        return True

    def _rpc_sync(self, function_name: str, params: dict[str, Any]) -> Any:
        result = self._client.rpc(function_name, params).execute()
        return result.data

    def _count_sync(self, table: str, filters: Optional[dict[str, Any]]) -> int:
        query = self._client.table(table).select("*", count="exact")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        result = query.limit(0).execute()
        return result.count or 0

    # ── Public async methods (non-blocking) ──────────────────────

    async def insert(self, table: str, data: dict[str, Any]) -> Optional[dict]:
        """Insert a row into a table."""
        if not self._connected:
            return None
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._insert_sync, table, data),
                timeout=_DB_OP_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error("supabase_insert_timeout", table=table)
            return None
        except Exception as e:
            logger.error("supabase_insert_failed", table=table, error=str(e))
            return None

    async def insert_batch(self, table: str, rows: list[dict[str, Any]]) -> list[dict]:
        """Insert multiple rows in a single transaction."""
        if not self._connected or not rows:
            return []
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._insert_batch_sync, table, rows),
                timeout=_DB_OP_TIMEOUT * 2,  # batch gets double timeout
            )
        except asyncio.TimeoutError:
            logger.error("supabase_batch_insert_timeout", table=table, count=len(rows))
            return []
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
            return await asyncio.wait_for(
                asyncio.to_thread(
                    self._select_sync, table, columns, filters, order_by, order_desc, limit
                ),
                timeout=_DB_OP_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error("supabase_select_timeout", table=table)
            return []
        except Exception as e:
            logger.error("supabase_select_failed", table=table, error=str(e))
            return []

    async def upsert(self, table: str, data: dict[str, Any], on_conflict: str = "") -> Optional[dict]:
        """Upsert (insert or update) a row."""
        if not self._connected:
            return None
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._upsert_sync, table, data, on_conflict),
                timeout=_DB_OP_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error("supabase_upsert_timeout", table=table)
            return None
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
            return await asyncio.wait_for(
                asyncio.to_thread(self._update_sync, table, data, filters),
                timeout=_DB_OP_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error("supabase_update_timeout", table=table)
            return None
        except Exception as e:
            logger.error("supabase_update_failed", table=table, error=str(e))
            return None

    async def delete(self, table: str, filters: dict[str, Any]) -> bool:
        """Delete rows matching filters."""
        if not self._connected:
            return False
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._delete_sync, table, filters),
                timeout=_DB_OP_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error("supabase_delete_timeout", table=table)
            return False
        except Exception as e:
            logger.error("supabase_delete_failed", table=table, error=str(e))
            return False

    async def rpc(self, function_name: str, params: dict[str, Any] = None) -> Any:
        """Call a Postgres function via RPC."""
        if not self._connected:
            return None
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._rpc_sync, function_name, params or {}),
                timeout=_DB_OP_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error("supabase_rpc_timeout", function=function_name)
            return None
        except Exception as e:
            logger.error("supabase_rpc_failed", function=function_name, error=str(e))
            return None

    async def count(self, table: str, filters: Optional[dict[str, Any]] = None) -> int:
        """Count rows in a table."""
        if not self._connected:
            return 0
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._count_sync, table, filters),
                timeout=_DB_OP_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error("supabase_count_timeout", table=table)
            return 0
        except Exception as e:
            logger.error("supabase_count_failed", table=table, error=str(e))
            return 0
