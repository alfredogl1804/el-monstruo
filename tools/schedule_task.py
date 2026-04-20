"""
El Monstruo — Schedule Task Tool (Sprint 8: Autonomía Temporal)
================================================================
Allows the LLM to schedule tasks for future autonomous execution.
The kernel's autonomous runner will pick up and execute these jobs.

Usage by LLM:
    schedule_task(title="...", instruction="...", run_at="...", timezone="...")

Guardrails:
    - Max TTL: 30 days
    - No recursive scheduling (depth check)
    - Rate limit: 20 jobs per user per day
    - HITL required for high-risk instructions (delegated to Policy Engine at execution time)
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from datetime import timezone as tz
from typing import Any, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("tool.schedule_task")

# ── Constants ───────────────────────────────────────────────────────
MAX_TTL_DAYS = 30
MAX_JOBS_PER_USER_PER_DAY = 20
VALID_CHANNELS = {"telegram", "api", "webhook"}
VALID_RECURRENCES = {None, "daily", "weekly"}

# Common timezone aliases for Mexico
TZ_ALIASES = {
    "cdmx": "America/Mexico_City",
    "mexico": "America/Mexico_City",
    "cst": "America/Mexico_City",
    "est": "America/New_York",
    "pst": "America/Los_Angeles",
    "utc": "UTC",
}


def _parse_run_at(run_at_str: str, user_tz: str) -> Optional[datetime]:
    """
    Parse a run_at string into a timezone-aware UTC datetime.
    Supports:
        - ISO 8601: "2026-04-19T08:00:00"
        - Natural relative: "in 3 hours", "in 30 minutes", "tomorrow 8am"
        - Date + time: "2026-04-19 08:00"
    """
    now = datetime.now(tz.utc)

    # Try ISO 8601 first
    for fmt in [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ]:
        try:
            dt = datetime.strptime(run_at_str.strip(), fmt)
            # Assume user's timezone if no tz info
            try:
                from zoneinfo import ZoneInfo

                user_zone = ZoneInfo(user_tz)
                dt = dt.replace(tzinfo=user_zone)
            except Exception:
                dt = dt.replace(tzinfo=tz.utc)
            return dt.astimezone(tz.utc)
        except ValueError:
            continue

    # Try relative formats
    s = run_at_str.strip().lower()

    # "in X hours/minutes"
    m = re.match(r"in\s+(\d+)\s+(hour|hours|minute|minutes|min|mins|day|days)", s)
    if m:
        amount = int(m.group(1))
        unit = m.group(2)
        if "hour" in unit:
            return now + timedelta(hours=amount)
        elif "min" in unit:
            return now + timedelta(minutes=amount)
        elif "day" in unit:
            return now + timedelta(days=amount)

    # "tomorrow Xam/Xpm" or "tomorrow at X:XX"
    m = re.match(r"tomorrow\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", s)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2) or 0)
        ampm = m.group(3)
        if ampm == "pm" and hour < 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0
        try:
            from zoneinfo import ZoneInfo

            user_zone = ZoneInfo(user_tz)
            tomorrow_local = (datetime.now(user_zone) + timedelta(days=1)).replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            return tomorrow_local.astimezone(tz.utc)
        except Exception:
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)

    return None


async def execute_schedule_task(
    params: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a scheduled job in Supabase.

    Params:
        title: str — Short description of the task
        instruction: str — Full instruction for the kernel to execute
        run_at: str — When to execute (ISO 8601, relative, or natural language)
        timezone: str — User's timezone (default: America/Mexico_City)
        channel: str — Notification channel (default: telegram)
        recurrence: str|None — None for one-shot, "daily" for daily repeat

    Context (injected by kernel):
        user_id: str
        thread_id: str
        db: SupabaseClient
        source: str — If "scheduled_job", block recursive scheduling
    """
    # ── Extract params ──────────────────────────────────────────────
    title = params.get("title", "").strip()
    instruction = params.get("instruction", "").strip()
    run_at_str = params.get("run_at", "").strip()
    user_tz = params.get("timezone", "America/Mexico_City").strip()
    channel = params.get("channel", "telegram").strip().lower()
    recurrence = params.get("recurrence")

    user_id = context.get("user_id", "unknown")
    thread_id = context.get("thread_id", "")
    db = context.get("db")
    source = context.get("source", "user")

    # ── Validate ────────────────────────────────────────────────────
    if not title:
        return {"error": "title is required", "success": False}
    if not instruction:
        return {"error": "instruction is required", "success": False}
    if not run_at_str:
        return {
            "error": "run_at is required (e.g., 'tomorrow 8am', 'in 3 hours', '2026-04-19T08:00')",
            "success": False,
        }

    # Anti-recursion: block scheduling from within a scheduled job
    if source == "scheduled_job":
        return {
            "error": "Recursive scheduling blocked: a scheduled job cannot create new scheduled jobs.",
            "success": False,
        }

    # Resolve timezone alias
    user_tz = TZ_ALIASES.get(user_tz.lower(), user_tz)

    # Validate channel
    if channel not in VALID_CHANNELS:
        return {
            "error": f"Invalid channel '{channel}'. Valid: {VALID_CHANNELS}",
            "success": False,
        }

    # Validate recurrence
    if recurrence and recurrence not in VALID_RECURRENCES:
        return {
            "error": f"Invalid recurrence '{recurrence}'. Valid: {VALID_RECURRENCES}",
            "success": False,
        }

    # Parse run_at
    run_at_utc = _parse_run_at(run_at_str, user_tz)
    if not run_at_utc:
        return {
            "error": f"Could not parse run_at: '{run_at_str}'. Use ISO 8601, 'tomorrow 8am', or 'in 3 hours'.",
            "success": False,
        }

    # Validate TTL (max 30 days)
    now = datetime.now(tz.utc)
    if run_at_utc < now:
        return {
            "error": "run_at is in the past. Please specify a future time.",
            "success": False,
        }
    if (run_at_utc - now).days > MAX_TTL_DAYS:
        return {
            "error": f"run_at is too far in the future. Maximum: {MAX_TTL_DAYS} days.",
            "success": False,
        }

    # Rate limit: check existing jobs for this user today
    if db:
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        existing = await db.select(
            "scheduled_jobs",
            columns="id",
            filters={"user_id": user_id},
        )
        today_jobs = [j for j in existing if j.get("created_at", "") >= today_start.isoformat()]
        if len(today_jobs) >= MAX_JOBS_PER_USER_PER_DAY:
            return {
                "error": f"Rate limit: max {MAX_JOBS_PER_USER_PER_DAY} jobs per day. You have {len(today_jobs)}.",
                "success": False,
            }

    # ── Create job ──────────────────────────────────────────────────
    job_id = str(uuid4())
    job_data = {
        "id": job_id,
        "user_id": user_id,
        "thread_id": thread_id,
        "title": title,
        "instruction": instruction,
        "run_at": run_at_utc.isoformat(),
        "timezone": user_tz,
        "channel": channel,
        "status": "scheduled",
        "recurrence": recurrence,
        "max_retries": 1,
        "retry_count": 0,
    }

    if db:
        result = await db.insert("scheduled_jobs", job_data)
        if not result:
            return {"error": "Failed to save job to database", "success": False}
        logger.info("job_scheduled", job_id=job_id, title=title, run_at=run_at_utc.isoformat())
    else:
        logger.warning(
            "job_scheduled_no_db",
            job_id=job_id,
            msg="No database — job will not persist across restarts",
        )

    # Format human-readable time in user's timezone
    try:
        from zoneinfo import ZoneInfo

        user_zone = ZoneInfo(user_tz)
        run_at_local = run_at_utc.astimezone(user_zone)
        human_time = run_at_local.strftime("%A %d de %B, %Y a las %H:%M %Z")
    except Exception:
        human_time = run_at_utc.strftime("%Y-%m-%d %H:%M UTC")

    return {
        "success": True,
        "job_id": job_id,
        "title": title,
        "run_at_utc": run_at_utc.isoformat(),
        "run_at_local": human_time,
        "timezone": user_tz,
        "channel": channel,
        "recurrence": recurrence or "one-shot",
        "message": f"Tarea programada: '{title}' se ejecutará el {human_time}.",
    }
