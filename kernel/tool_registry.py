"""
El Monstruo — Tool Registry (Sprint 10)
=========================================
Dynamic tool registry backed by Supabase.
Replaces hardcoded tool metadata with queryable, trackable data.

Features:
    - Load tool metadata from Supabase on startup
    - Track invocation counts and last-invoked timestamps
    - Enable/disable tools dynamically
    - Provide tool catalog to LLM system prompts
    - Sync with tool_dispatch.py ToolSpecs

Sprint 10 — 2026-04-18
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.tool_registry")


class ToolRegistry:
    """
    Dynamic tool registry backed by Supabase.
    Loads tool metadata from the tool_registry table and provides
    methods to query, update, and track tool usage.
    """

    TABLE = "tool_registry"

    def __init__(self, db: Any = None) -> None:
        self._db = db
        self._cache: dict[str, dict] = {}  # tool_name -> row
        self._initialized = False

    async def initialize(self) -> bool:
        """Load all tools from Supabase into local cache."""
        if not self._db or not self._db.connected:
            logger.warning("tool_registry_no_db", hint="DB not available, registry disabled")
            return False

        try:
            rows = await self._db.select(
                self.TABLE,
                columns="*",
                order_by="tool_name",
                order_desc=False,
            )
            self._cache = {row["tool_name"]: row for row in rows}
            self._initialized = True
            logger.info(
                "tool_registry_loaded",
                tool_count=len(self._cache),
                active=sum(1 for r in self._cache.values() if r.get("is_active")),
            )
            return True
        except Exception as e:
            logger.error("tool_registry_init_failed", error=str(e))
            return False

    @property
    def initialized(self) -> bool:
        return self._initialized

    def get_tool(self, tool_name: str) -> Optional[dict]:
        """Get metadata for a specific tool."""
        return self._cache.get(tool_name)

    def get_active_tools(self) -> list[dict]:
        """Get all active tools."""
        return [t for t in self._cache.values() if t.get("is_active", True)]

    def get_tools_by_category(self, category: str) -> list[dict]:
        """Get tools filtered by category."""
        return [
            t for t in self._cache.values()
            if t.get("category") == category and t.get("is_active", True)
        ]

    def list_all(self) -> list[dict]:
        """Get all tools regardless of status."""
        return list(self._cache.values())

    async def record_invocation(self, tool_name: str) -> None:
        """Increment invocation count and update last_invoked_at."""
        if not self._db or not self._db.connected:
            return

        now = datetime.now(timezone.utc).isoformat()

        # Update cache
        if tool_name in self._cache:
            self._cache[tool_name]["invocation_count"] = (
                self._cache[tool_name].get("invocation_count", 0) + 1
            )
            self._cache[tool_name]["last_invoked_at"] = now

        # Update Supabase (fire-and-forget, don't block the request)
        try:
            current = self._cache.get(tool_name, {})
            await self._db.update(
                self.TABLE,
                data={
                    "invocation_count": current.get("invocation_count", 1),
                    "last_invoked_at": now,
                },
                filters={"tool_name": tool_name},
            )
        except Exception as e:
            logger.warning("tool_registry_update_failed", tool=tool_name, error=str(e))

    async def set_active(self, tool_name: str, active: bool) -> bool:
        """Enable or disable a tool."""
        if not self._db or not self._db.connected:
            return False

        try:
            result = await self._db.update(
                self.TABLE,
                data={"is_active": active},
                filters={"tool_name": tool_name},
            )
            if result and tool_name in self._cache:
                self._cache[tool_name]["is_active"] = active
            logger.info("tool_registry_toggled", tool=tool_name, active=active)
            return True
        except Exception as e:
            logger.error("tool_registry_toggle_failed", tool=tool_name, error=str(e))
            return False

    async def register_tool(self, tool_data: dict) -> Optional[dict]:
        """Register a new tool in the registry."""
        if not self._db or not self._db.connected:
            return None

        try:
            result = await self._db.upsert(
                self.TABLE,
                data=tool_data,
                on_conflict="tool_name",
            )
            if result:
                self._cache[result["tool_name"]] = result
            return result
        except Exception as e:
            logger.error("tool_registry_register_failed", error=str(e))
            return None

    def get_catalog_summary(self) -> str:
        """
        Generate a human-readable tool catalog for injection into system prompts.
        This lets the LLM know what tools are available and their capabilities.
        """
        if not self._cache:
            return "No tools registered."

        active = self.get_active_tools()
        if not active:
            return "No active tools."

        lines = [f"## Tool Catalog ({len(active)} active tools)\n"]

        # Group by category
        categories: dict[str, list[dict]] = {}
        for tool in active:
            cat = tool.get("category", "general")
            categories.setdefault(cat, []).append(tool)

        category_order = ["read", "write", "orchestration", "autonomy", "awareness", "general"]
        for cat in category_order:
            tools = categories.get(cat, [])
            if not tools:
                continue
            lines.append(f"\n### {cat.upper()}")
            for t in sorted(tools, key=lambda x: x["tool_name"]):
                risk = t.get("risk_level", "LOW")
                hitl = " [HITL]" if t.get("requires_hitl") else ""
                count = t.get("invocation_count", 0)
                lines.append(
                    f"- **{t['display_name']}** (`{t['tool_name']}`): "
                    f"{t.get('description', 'No description')} "
                    f"[Risk: {risk}{hitl}] (used {count}x)"
                )

        return "\n".join(lines)

    def get_stats(self) -> dict:
        """Get registry statistics."""
        active = self.get_active_tools()
        total_invocations = sum(t.get("invocation_count", 0) for t in self._cache.values())
        return {
            "total_tools": len(self._cache),
            "active_tools": len(active),
            "total_invocations": total_invocations,
            "categories": list(set(t.get("category", "general") for t in active)),
            "most_used": sorted(
                [{"name": t["tool_name"], "count": t.get("invocation_count", 0)}
                 for t in self._cache.values()],
                key=lambda x: x["count"],
                reverse=True,
            )[:5],
        }
