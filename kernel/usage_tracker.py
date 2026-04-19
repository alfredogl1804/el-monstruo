"""
El Monstruo — Usage Tracker (Sprint 10)
=========================================
Persistent usage tracking backed by Supabase.
Logs every kernel request with token counts, cost, model, and latency.
Provides aggregation queries for the cost dashboard.

Features:
    - Log each request to usage_log table
    - Aggregate daily stats (on-demand or scheduled)
    - Query cost by period (today, week, month, all-time)
    - Per-model breakdown
    - Budget alerts (configurable daily cap)

Sprint 10 — 2026-04-18
Sprint 10b (ADR) — 2026-04-18: Added tool-level metrics integration with ToolBroker
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.usage_tracker")

# ── Configuration ──────────────────────────────────────────────
DAILY_BUDGET_USD = float(os.environ.get("DAILY_BUDGET_USD", "10.0"))
MONTHLY_BUDGET_USD = float(os.environ.get("MONTHLY_BUDGET_USD", "200.0"))


class UsageTracker:
    """
    Persistent usage tracker backed by Supabase.
    Logs token usage, cost, and latency for every kernel request.
    """

    LOG_TABLE = "usage_log"
    DAILY_TABLE = "usage_daily"
    TOOL_METRICS_TABLE = "tool_usage_metrics"

    def __init__(self, db: Any = None) -> None:
        self._db = db
        self._initialized = False
        # In-memory accumulator for the current day (fast reads)
        self._today_cost: float = 0.0
        self._today_date: str = ""
        self._today_requests: int = 0
        # Tool-level in-memory tracking
        self._tool_calls: dict[str, dict] = {}  # tool_name -> {calls, errors, total_ms}

    async def initialize(self) -> bool:
        """Load today's accumulated cost from Supabase."""
        if not self._db or not self._db.connected:
            logger.warning("usage_tracker_no_db")
            return False

        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            self._today_date = today

            # Load today's aggregates from usage_daily
            rows = await self._db.select(
                self.DAILY_TABLE,
                columns="total_cost_usd, request_count",
                filters={"date": today},
            )
            if rows:
                self._today_cost = sum(float(r.get("total_cost_usd", 0)) for r in rows)
                self._today_requests = sum(int(r.get("request_count", 0)) for r in rows)

            self._initialized = True
            logger.info(
                "usage_tracker_initialized",
                today_cost=f"${self._today_cost:.4f}",
                today_requests=self._today_requests,
            )
            return True
        except Exception as e:
            logger.error("usage_tracker_init_failed", error=str(e))
            return False

    @property
    def initialized(self) -> bool:
        return self._initialized

    async def log_request(
        self,
        *,
        thread_id: str = "",
        model_used: str,
        provider: str = "",
        role_used: str = "",
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost_usd: float = 0.0,
        latency_ms: int = 0,
        tool_calls: list[str] = None,
        status: str = "completed",
        error_message: str = "",
    ) -> Optional[dict]:
        """
        Log a single kernel request to usage_log.
        Also updates the in-memory daily accumulator.
        """
        if not self._db or not self._db.connected:
            return None

        # Reset daily accumulator if day changed
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today != self._today_date:
            self._today_date = today
            self._today_cost = 0.0
            self._today_requests = 0

        # Update in-memory
        self._today_cost += cost_usd
        self._today_requests += 1

        # Persist to Supabase
        try:
            row = {
                "thread_id": thread_id,
                "model_used": model_used,
                "provider": provider,
                "role_used": role_used,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost_usd": cost_usd,
                "latency_ms": latency_ms,
                "tool_calls": tool_calls or [],
                "status": status,
                "error_message": error_message,
            }
            result = await self._db.insert(self.LOG_TABLE, row)

            # Check budget alerts
            if self._today_cost >= DAILY_BUDGET_USD:
                logger.warning(
                    "daily_budget_exceeded",
                    today_cost=f"${self._today_cost:.4f}",
                    budget=f"${DAILY_BUDGET_USD:.2f}",
                )

            return result
        except Exception as e:
            logger.error("usage_log_failed", model=model_used, error=str(e))
            return None

    async def aggregate_today(self) -> None:
        """Trigger daily aggregation RPC for today."""
        if not self._db or not self._db.connected:
            return
        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            await self._db.rpc("aggregate_daily_usage", {"target_date": today})
            logger.info("usage_daily_aggregated", date=today)
        except Exception as e:
            logger.error("usage_aggregate_failed", error=str(e))

    async def get_today_summary(self) -> dict:
        """Get today's usage summary."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Try from daily table first (aggregated)
        if self._db and self._db.connected:
            rows = await self._db.select(
                self.DAILY_TABLE,
                columns="*",
                filters={"date": today},
                order_by="total_cost_usd",
                order_desc=True,
            )
            if rows:
                return {
                    "date": today,
                    "total_requests": sum(r.get("request_count", 0) for r in rows),
                    "total_tokens_in": sum(r.get("total_tokens_in", 0) for r in rows),
                    "total_tokens_out": sum(r.get("total_tokens_out", 0) for r in rows),
                    "total_cost_usd": float(sum(float(r.get("total_cost_usd", 0)) for r in rows)),
                    "avg_latency_ms": (
                        sum(r.get("avg_latency_ms", 0) * r.get("request_count", 1) for r in rows)
                        // max(sum(r.get("request_count", 1) for r in rows), 1)
                    ),
                    "models": [
                        {
                            "model": r["model"],
                            "requests": r["request_count"],
                            "tokens_in": r["total_tokens_in"],
                            "tokens_out": r["total_tokens_out"],
                            "cost_usd": float(r["total_cost_usd"]),
                            "errors": r.get("error_count", 0),
                        }
                        for r in rows
                    ],
                    "budget": {
                        "daily_limit": DAILY_BUDGET_USD,
                        "used_pct": round(
                            float(sum(float(r.get("total_cost_usd", 0)) for r in rows))
                            / DAILY_BUDGET_USD * 100, 1
                        ) if DAILY_BUDGET_USD > 0 else 0,
                    },
                }

        # Fallback to in-memory
        return {
            "date": today,
            "total_requests": self._today_requests,
            "total_cost_usd": self._today_cost,
            "budget": {
                "daily_limit": DAILY_BUDGET_USD,
                "used_pct": round(self._today_cost / DAILY_BUDGET_USD * 100, 1) if DAILY_BUDGET_USD > 0 else 0,
            },
            "source": "in_memory",
        }

    async def get_period_summary(self, days: int = 7) -> dict:
        """Get usage summary for the last N days."""
        if not self._db or not self._db.connected:
            return {"error": "DB not available"}

        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
            # Use select with manual filter since SupabaseClient doesn't support gte
            # We'll get all daily rows and filter in Python
            rows = await self._db.select(
                self.DAILY_TABLE,
                columns="*",
                order_by="date",
                order_desc=True,
                limit=days * 15,  # max ~15 models per day
            )

            # Filter by date
            filtered = [r for r in rows if r.get("date", "") >= cutoff]

            if not filtered:
                return {
                    "period_days": days,
                    "total_requests": 0,
                    "total_cost_usd": 0.0,
                    "total_tokens": 0,
                    "daily_breakdown": [],
                }

            # Aggregate by date
            daily: dict[str, dict] = {}
            for r in filtered:
                d = r["date"]
                if d not in daily:
                    daily[d] = {"date": d, "requests": 0, "cost_usd": 0.0, "tokens": 0}
                daily[d]["requests"] += r.get("request_count", 0)
                daily[d]["cost_usd"] += float(r.get("total_cost_usd", 0))
                daily[d]["tokens"] += r.get("total_tokens_in", 0) + r.get("total_tokens_out", 0)

            # Aggregate by model
            models: dict[str, dict] = {}
            for r in filtered:
                m = r["model"]
                if m not in models:
                    models[m] = {"model": m, "requests": 0, "cost_usd": 0.0, "tokens": 0}
                models[m]["requests"] += r.get("request_count", 0)
                models[m]["cost_usd"] += float(r.get("total_cost_usd", 0))
                models[m]["tokens"] += r.get("total_tokens_in", 0) + r.get("total_tokens_out", 0)

            total_cost = sum(d["cost_usd"] for d in daily.values())

            return {
                "period_days": days,
                "total_requests": sum(d["requests"] for d in daily.values()),
                "total_cost_usd": round(total_cost, 6),
                "total_tokens": sum(d["tokens"] for d in daily.values()),
                "avg_daily_cost": round(total_cost / max(len(daily), 1), 6),
                "budget": {
                    "monthly_limit": MONTHLY_BUDGET_USD,
                    "projected_monthly": round(total_cost / max(days, 1) * 30, 2),
                },
                "daily_breakdown": sorted(daily.values(), key=lambda x: x["date"], reverse=True),
                "model_breakdown": sorted(models.values(), key=lambda x: x["cost_usd"], reverse=True),
            }
        except Exception as e:
            logger.error("usage_period_query_failed", error=str(e))
            return {"error": str(e)}

    async def get_recent_requests(self, limit: int = 20) -> list[dict]:
        """Get the most recent usage log entries."""
        if not self._db or not self._db.connected:
            return []

        try:
            rows = await self._db.select(
                self.LOG_TABLE,
                columns="id, model_used, provider, role_used, tokens_in, tokens_out, cost_usd, latency_ms, tool_calls, status, created_at",
                order_by="created_at",
                order_desc=True,
                limit=limit,
            )
            return rows
        except Exception as e:
            logger.error("usage_recent_query_failed", error=str(e))
            return []

    # ── Tool-Level Metrics ──────────────────────────────────────────

    async def log_tool_execution(
        self,
        *,
        tool_name: str,
        run_id: str = "",
        status: str = "success",
        wall_ms: int = 0,
        api_calls: int = 1,
        cost_usd: float = 0.0,
    ) -> None:
        """Log a tool execution for tool-level metrics."""
        # Update in-memory
        if tool_name not in self._tool_calls:
            self._tool_calls[tool_name] = {"calls": 0, "errors": 0, "total_ms": 0}
        self._tool_calls[tool_name]["calls"] += 1
        if status == "failed":
            self._tool_calls[tool_name]["errors"] += 1
        self._tool_calls[tool_name]["total_ms"] += wall_ms

        # Persist to Supabase
        if not self._db or not self._db.connected:
            return

        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            await self._db.insert(self.TOOL_METRICS_TABLE, {
                "date": today,
                "tool_name": tool_name,
                "invocation_count": 1,
                "success_count": 1 if status == "success" else 0,
                "error_count": 1 if status == "failed" else 0,
                "total_wall_ms": wall_ms,
                "avg_wall_ms": wall_ms,
                "total_api_calls": api_calls,
                "total_cost_usd": cost_usd,
            })
        except Exception as e:
            logger.error("tool_metrics_log_failed", tool=tool_name, error=str(e))

    async def get_tool_metrics(self, days: int = 7) -> list[dict]:
        """Get tool-level usage metrics for the last N days."""
        if not self._db or not self._db.connected:
            # Return in-memory data
            return [
                {
                    "tool_name": name,
                    "calls": stats["calls"],
                    "errors": stats["errors"],
                    "avg_ms": stats["total_ms"] // max(stats["calls"], 1),
                    "source": "in_memory",
                }
                for name, stats in self._tool_calls.items()
            ]

        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
            rows = await self._db.select(
                self.TOOL_METRICS_TABLE,
                columns="*",
                order_by="date",
                order_desc=True,
                limit=days * 20,
            )

            filtered = [r for r in (rows or []) if r.get("date", "") >= cutoff]

            # Aggregate by tool
            tools: dict[str, dict] = {}
            for r in filtered:
                t = r["tool_name"]
                if t not in tools:
                    tools[t] = {
                        "tool_name": t,
                        "invocations": 0,
                        "successes": 0,
                        "errors": 0,
                        "total_wall_ms": 0,
                        "total_cost_usd": 0.0,
                    }
                tools[t]["invocations"] += r.get("invocation_count", 0)
                tools[t]["successes"] += r.get("success_count", 0)
                tools[t]["errors"] += r.get("error_count", 0)
                tools[t]["total_wall_ms"] += r.get("total_wall_ms", 0)
                tools[t]["total_cost_usd"] += float(r.get("total_cost_usd", 0))

            result = []
            for t in tools.values():
                t["avg_wall_ms"] = t["total_wall_ms"] // max(t["invocations"], 1)
                t["success_rate"] = round(
                    t["successes"] / max(t["invocations"], 1) * 100, 1
                )
                result.append(t)

            return sorted(result, key=lambda x: x["invocations"], reverse=True)
        except Exception as e:
            logger.error("tool_metrics_query_failed", error=str(e))
            return []

    def get_stats(self) -> dict:
        """Get current tracker statistics (in-memory)."""
        return {
            "initialized": self._initialized,
            "today_date": self._today_date,
            "today_cost_usd": round(self._today_cost, 6),
            "today_requests": self._today_requests,
            "daily_budget_usd": DAILY_BUDGET_USD,
            "monthly_budget_usd": MONTHLY_BUDGET_USD,
            "budget_used_pct": round(
                self._today_cost / DAILY_BUDGET_USD * 100, 1
            ) if DAILY_BUDGET_USD > 0 else 0,
            "tool_calls_session": dict(self._tool_calls),
        }
