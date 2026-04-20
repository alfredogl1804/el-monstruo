"""
El Monstruo — Autonomy Guardrails (Sprint 8)
==============================================
Safety rules for autonomous job execution:

1. Anti-recursion: scheduled jobs cannot create new scheduled jobs
2. Tool restrictions: certain tools are blocked in autonomous mode
3. Cost cap: max tokens per autonomous execution
4. Rate limiting: max jobs per user per day
5. TTL enforcement: auto-cancel jobs older than 30 days
6. Content filtering: block dangerous instructions

These rules are checked BEFORE the autonomous runner executes a job.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

import structlog

logger = structlog.get_logger("policy.autonomy")

# ── Constants ───────────────────────────────────────────────────────
MAX_TOKENS_PER_JOB = 50_000  # ~$0.50 at GPT-5.4 rates
MAX_JOBS_PER_USER_PER_DAY = 20
MAX_TTL_DAYS = 30
BLOCKED_TOOLS_IN_AUTONOMOUS = {"schedule_task"}  # Anti-recursion
HITL_REQUIRED_TOOLS_IN_AUTONOMOUS = {"email", "call_webhook"}  # Need approval

# Dangerous patterns in instructions (regex)
DANGEROUS_PATTERNS = [
    r"(?i)(delete|drop|truncate)\s+(all|table|database|everything)",
    r"(?i)rm\s+-rf",
    r"(?i)(transfer|send)\s+\$?\d+.*money",
    r"(?i)(password|secret|token|key)\s*(=|:)",
]


class AutonomyGuardrails:
    """
    Validates scheduled jobs before execution.
    Returns (allowed: bool, reason: str).
    """

    @staticmethod
    async def validate_job(
        job: dict[str, Any],
        db: Any = None,
    ) -> tuple[bool, str]:
        """
        Run all guardrail checks on a job before execution.
        Returns (True, "ok") if allowed, (False, reason) if blocked.
        """
        instruction = job.get("instruction", "")
        user_id = job.get("user_id", "unknown")
        job.get("run_at", "")
        created_at_str = job.get("created_at", "")

        # 1. Check for empty instruction
        if not instruction.strip():
            return False, "Empty instruction"

        # 2. Check TTL (auto-cancel if too old)
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                age = datetime.now(timezone.utc) - created_at
                if age.days > MAX_TTL_DAYS:
                    return (
                        False,
                        f"Job expired: created {age.days} days ago (max {MAX_TTL_DAYS})",
                    )
            except (ValueError, TypeError):
                pass

        # 3. Check dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, instruction):
                return (
                    False,
                    f"Dangerous instruction detected: matches pattern '{pattern}'",
                )

        # 4. Check instruction length (sanity)
        if len(instruction) > 10_000:
            return False, f"Instruction too long: {len(instruction)} chars (max 10,000)"

        # 5. Rate limit check
        if db and db.connected:
            try:
                today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                all_jobs = await db.select(
                    "scheduled_jobs",
                    filters={"user_id": user_id},
                    order_by="created_at",
                    order_desc=True,
                    limit=100,
                )
                today_count = sum(1 for j in all_jobs if j.get("created_at", "") >= today_start.isoformat())
                if today_count > MAX_JOBS_PER_USER_PER_DAY * 2:  # 2x for execution (more lenient)
                    return False, f"Rate limit: user has {today_count} jobs today"
            except Exception as e:
                logger.warning("rate_limit_check_failed", error=str(e))

        return True, "ok"

    @staticmethod
    def get_tool_restrictions(source: str) -> dict[str, Any]:
        """
        Return tool restrictions for autonomous execution.
        Used by tool_dispatch to filter available tools.
        """
        if source == "scheduled_job":
            return {
                "blocked_tools": BLOCKED_TOOLS_IN_AUTONOMOUS,
                "hitl_required_tools": HITL_REQUIRED_TOOLS_IN_AUTONOMOUS,
                "max_tokens": MAX_TOKENS_PER_JOB,
            }
        return {
            "blocked_tools": set(),
            "hitl_required_tools": set(),
            "max_tokens": None,
        }

    @staticmethod
    async def cleanup_expired_jobs(db: Any) -> int:
        """
        Cancel jobs that have exceeded their TTL.
        Called periodically by the autonomous runner.
        Returns count of cancelled jobs.
        """
        if not db or not db.connected:
            return 0

        cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_TTL_DAYS)
        expired = await db.select(
            "scheduled_jobs",
            filters={"status": "scheduled"},
            order_by="created_at",
            order_desc=False,
            limit=100,
        )

        cancelled = 0
        for job in expired:
            created = job.get("created_at", "")
            if created and created < cutoff.isoformat():
                await db.update(
                    "scheduled_jobs",
                    {"status": "cancelled", "last_error": "TTL expired"},
                    {"id": job["id"]},
                )
                cancelled += 1

        if cancelled:
            logger.info("expired_jobs_cancelled", count=cancelled)
        return cancelled
