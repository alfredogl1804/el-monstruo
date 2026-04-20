"""
El Monstruo — FinOps Soberano (Sprint 15)
==========================================
Per-run cost tracking with budget hard stop.
Integrates with UsageTracker for persistent cost data
and SovereignAlerts for real-time Telegram notifications.

Features:
    - Per-run cost accumulation (run_costs table)
    - Budget hard stop: blocks new runs when daily budget exceeded
    - Burn rate calculation (cost/hour, projected daily)
    - Cost anomaly detection (spike alerts)
    - Integration with Langfuse cost data

Sprint 15 — 2026-04-20
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.finops")

# ── Configuration ──────────────────────────────────────────────
DAILY_HARD_LIMIT_USD = float(os.environ.get("DAILY_HARD_LIMIT_USD", "15.0"))
MONTHLY_HARD_LIMIT_USD = float(os.environ.get("MONTHLY_HARD_LIMIT_USD", "300.0"))
COST_SPIKE_MULTIPLIER = float(os.environ.get("COST_SPIKE_MULTIPLIER", "3.0"))
BUDGET_HARD_STOP_ENABLED = os.environ.get("BUDGET_HARD_STOP", "true").lower() == "true"


class FinOpsController:
    """
    Sovereign FinOps controller.
    Enforces budget limits and tracks per-run costs.
    """

    RUN_COSTS_TABLE = "run_costs"

    def __init__(self, db: Any = None, usage_tracker: Any = None, alerts: Any = None) -> None:
        self._db = db
        self._usage_tracker = usage_tracker
        self._alerts = alerts
        self._daily_cost: float = 0.0
        self._daily_date: str = ""
        self._run_costs: dict[str, float] = {}  # run_id -> accumulated cost
        self._hourly_costs: list[tuple[float, float]] = []  # (timestamp, cost)

    async def initialize(self) -> bool:
        """Load today's accumulated cost from run_costs table."""
        if not self._db or not self._db.connected:
            logger.warning("finops_no_db")
            return False

        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            self._daily_date = today

            # Sum today's run costs
            rows = await self._db.select(
                self.RUN_COSTS_TABLE,
                columns="total_cost_usd",
                limit=500,
            )
            if rows:
                # Filter by today (created_at starts with today's date)
                self._daily_cost = sum(
                    float(r.get("total_cost_usd", 0))
                    for r in rows
                    if str(r.get("created_at", "")).startswith(today)
                )

            logger.info(
                "finops_initialized",
                daily_cost=f"${self._daily_cost:.4f}",
                hard_limit=f"${DAILY_HARD_LIMIT_USD:.2f}",
                hard_stop=BUDGET_HARD_STOP_ENABLED,
            )
            return True
        except Exception as e:
            logger.error("finops_init_failed", error=str(e))
            return False

    def check_budget(self) -> dict:
        """
        Check if the current budget allows a new run.
        Returns dict with 'allowed' bool and reason.
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today != self._daily_date:
            self._daily_date = today
            self._daily_cost = 0.0
            self._hourly_costs.clear()

        if not BUDGET_HARD_STOP_ENABLED:
            return {"allowed": True, "reason": "hard_stop_disabled"}

        if self._daily_cost >= DAILY_HARD_LIMIT_USD:
            logger.warning(
                "budget_hard_stop_triggered",
                daily_cost=f"${self._daily_cost:.4f}",
                limit=f"${DAILY_HARD_LIMIT_USD:.2f}",
            )
            return {
                "allowed": False,
                "reason": f"Daily budget exceeded: ${self._daily_cost:.2f} / ${DAILY_HARD_LIMIT_USD:.2f}",
                "daily_cost": self._daily_cost,
                "daily_limit": DAILY_HARD_LIMIT_USD,
            }

        return {
            "allowed": True,
            "reason": "within_budget",
            "daily_cost": self._daily_cost,
            "daily_limit": DAILY_HARD_LIMIT_USD,
            "remaining": round(DAILY_HARD_LIMIT_USD - self._daily_cost, 4),
        }

    async def record_run_cost(
        self,
        *,
        run_id: str,
        model_used: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost_usd: float = 0.0,
        latency_ms: int = 0,
        tool_count: int = 0,
        status: str = "completed",
    ) -> Optional[dict]:
        """
        Record the cost of a completed run to run_costs table.
        Also updates daily accumulator and checks for cost spikes.
        """
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")

        # Reset daily if day changed
        if today != self._daily_date:
            self._daily_date = today
            self._daily_cost = 0.0
            self._hourly_costs.clear()

        # Update accumulators
        self._daily_cost += cost_usd
        self._run_costs[run_id] = cost_usd
        self._hourly_costs.append((now.timestamp(), cost_usd))

        # Prune hourly costs older than 1 hour
        cutoff = now.timestamp() - 3600
        self._hourly_costs = [(t, c) for t, c in self._hourly_costs if t > cutoff]

        # Check for cost spike
        await self._check_cost_spike(cost_usd, model_used)

        # Persist to Supabase
        if not self._db or not self._db.connected:
            return None

        try:
            row = {
                "run_id": run_id,
                "model_used": model_used,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "total_cost_usd": cost_usd,
                "latency_ms": latency_ms,
                "tool_count": tool_count,
                "status": status,
            }
            result = await self._db.insert(self.RUN_COSTS_TABLE, row)
            logger.info(
                "run_cost_recorded",
                run_id=run_id,
                cost=f"${cost_usd:.6f}",
                daily_total=f"${self._daily_cost:.4f}",
            )
            return result
        except Exception as e:
            logger.error("run_cost_record_failed", run_id=run_id, error=str(e))
            return None

    async def _check_cost_spike(self, current_cost: float, model: str) -> None:
        """Detect cost spikes and send alert."""
        if len(self._hourly_costs) < 3:
            return  # Not enough data

        # Calculate average cost per run (excluding current)
        past_costs = [c for _, c in self._hourly_costs[:-1]]
        avg_cost = sum(past_costs) / len(past_costs) if past_costs else 0

        if avg_cost > 0 and current_cost > avg_cost * COST_SPIKE_MULTIPLIER:
            logger.warning(
                "cost_spike_detected",
                current=f"${current_cost:.6f}",
                average=f"${avg_cost:.6f}",
                multiplier=f"{current_cost / avg_cost:.1f}x",
            )
            if self._alerts:
                try:
                    await self._alerts.send_alert(
                        alert_type="cost_spike",
                        value=current_cost,
                        threshold=avg_cost * COST_SPIKE_MULTIPLIER,
                        details=f"Model: {model}, {current_cost / avg_cost:.1f}x average",
                    )
                except Exception:
                    pass

    def get_burn_rate(self) -> dict:
        """Calculate current burn rate (cost/hour, projected daily)."""
        if not self._hourly_costs:
            return {
                "cost_per_hour": 0.0,
                "projected_daily": 0.0,
                "runs_last_hour": 0,
            }

        total_cost_hour = sum(c for _, c in self._hourly_costs)
        runs_hour = len(self._hourly_costs)

        # Time span of the hourly window
        if len(self._hourly_costs) > 1:
            time_span_hours = (self._hourly_costs[-1][0] - self._hourly_costs[0][0]) / 3600
        else:
            time_span_hours = 1.0

        cost_per_hour = total_cost_hour / max(time_span_hours, 0.01)
        projected_daily = cost_per_hour * 24

        return {
            "cost_per_hour": round(cost_per_hour, 6),
            "projected_daily": round(projected_daily, 4),
            "runs_last_hour": runs_hour,
            "daily_cost": round(self._daily_cost, 6),
            "daily_limit": DAILY_HARD_LIMIT_USD,
            "budget_used_pct": round(self._daily_cost / DAILY_HARD_LIMIT_USD * 100, 1),
        }

    def get_status(self) -> dict:
        """Get full FinOps status."""
        budget = self.check_budget()
        burn = self.get_burn_rate()
        return {
            "budget": budget,
            "burn_rate": burn,
            "hard_stop_enabled": BUDGET_HARD_STOP_ENABLED,
            "daily_hard_limit_usd": DAILY_HARD_LIMIT_USD,
            "monthly_hard_limit_usd": MONTHLY_HARD_LIMIT_USD,
            "runs_tracked": len(self._run_costs),
        }
