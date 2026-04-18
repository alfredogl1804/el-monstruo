"""
El Monstruo — Autonomous Runner (Sprint 8: Autonomía Temporal)
===============================================================
Background asyncio task that:
  1. Polls Supabase every POLL_INTERVAL_S for due scheduled_jobs
  2. For each due job, re-enters the kernel with the job's instruction
  3. Records execution in job_executions
  4. Sends notification via Telegram (or other channel)
  5. Handles recurrence (reschedule daily jobs)

Guardrails:
  - Max concurrent executions: 3
  - Anti-recursion: source="scheduled_job" blocks schedule_task tool
  - TTL: jobs older than 30 days auto-cancel
  - Error handling: retry up to max_retries, then mark failed

Architecture:
  lifespan(startup) → asyncio.create_task(runner.start())
  runner.start() → poll loop → _execute_job() → kernel.run() → notify
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("runner.autonomous")

# ── Configuration ───────────────────────────────────────────────────
POLL_INTERVAL_S = int(os.environ.get("AUTONOMY_POLL_INTERVAL", "60"))
MAX_CONCURRENT = int(os.environ.get("AUTONOMY_MAX_CONCURRENT", "3"))
MAX_TTL_DAYS = 30
JOB_TIMEOUT_S = int(os.environ.get("AUTONOMY_JOB_TIMEOUT", "300"))  # 5 min per job


class AutonomousRunner:
    """
    Background runner that executes scheduled jobs autonomously.
    
    Dependencies (injected at init):
        - db: SupabaseClient for reading/writing jobs
        - kernel: LangGraphKernel for re-entry execution
        - notifier: TelegramNotifier for sending results to user
    """

    def __init__(
        self,
        db: Any,
        kernel: Any,
        notifier: Optional[Any] = None,
    ):
        self._db = db
        self._kernel = kernel
        self._notifier = notifier
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self._jobs_executed = 0
        self._jobs_failed = 0

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "poll_interval_s": POLL_INTERVAL_S,
            "max_concurrent": MAX_CONCURRENT,
            "jobs_executed": self._jobs_executed,
            "jobs_failed": self._jobs_failed,
        }

    async def start(self) -> None:
        """Start the polling loop as a background task."""
        if self._running:
            logger.warning("runner_already_running")
            return
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("autonomous_runner_started", poll_interval=POLL_INTERVAL_S)

    async def stop(self) -> None:
        """Gracefully stop the runner."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("autonomous_runner_stopped")

    async def _poll_loop(self) -> None:
        """Main polling loop — runs every POLL_INTERVAL_S."""
        while self._running:
            try:
                await self._poll_once()
            except Exception as e:
                logger.error("poll_loop_error", error=str(e))
            await asyncio.sleep(POLL_INTERVAL_S)

    async def _poll_once(self) -> None:
        """Single poll iteration: find due jobs and execute them."""
        if not self._db or not self._db.connected:
            return

        # Use the RPC function get_due_jobs for atomic claim
        try:
            due_jobs = await self._db.rpc("get_due_jobs", {"max_jobs": MAX_CONCURRENT})
        except Exception as e:
            # Fallback: manual select + update if RPC not available
            logger.warning("rpc_get_due_jobs_failed", error=str(e), fallback="manual_select")
            due_jobs = await self._db.select(
                "scheduled_jobs",
                filters={"status": "scheduled"},
                order_by="run_at",
                order_desc=False,
                limit=MAX_CONCURRENT,
            )
            # Filter to only due jobs
            now = datetime.now(timezone.utc)
            due_jobs = [
                j for j in due_jobs
                if j.get("run_at") and datetime.fromisoformat(j["run_at"].replace("Z", "+00:00")) <= now
            ]
            # Claim them by updating status
            for job in due_jobs:
                await self._db.update(
                    "scheduled_jobs",
                    {"status": "running"},
                    {"id": job["id"]},
                )

        if not due_jobs:
            return

        logger.info("due_jobs_found", count=len(due_jobs))

        # Execute jobs concurrently (up to MAX_CONCURRENT)
        tasks = [self._execute_job(job) for job in due_jobs]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_job(self, job: dict[str, Any]) -> None:
        """Execute a single scheduled job via kernel re-entry."""
        job_id = job.get("id", "unknown")
        title = job.get("title", "")
        instruction = job.get("instruction", "")
        user_id = job.get("user_id", "unknown")
        channel = job.get("channel", "telegram")

        async with self._semaphore:
            execution_id = str(uuid4())
            started_at = datetime.now(timezone.utc)

            logger.info(
                "job_execution_start",
                job_id=job_id,
                execution_id=execution_id,
                title=title,
            )

            # Record execution start
            await self._db.insert("job_executions", {
                "id": execution_id,
                "scheduled_job_id": job_id,
                "started_at": started_at.isoformat(),
                "status": "running",
            })

            try:
                # Re-enter the kernel with the job's instruction
                # The source="scheduled_job" flag prevents recursive scheduling
                result = await asyncio.wait_for(
                    self._kernel_execute(
                        instruction=instruction,
                        user_id=user_id,
                        source="scheduled_job",
                        job_id=job_id,
                    ),
                    timeout=JOB_TIMEOUT_S,
                )

                finished_at = datetime.now(timezone.utc)
                result_summary = result.get("response", "")[:2000]  # Truncate

                # Update execution record
                await self._db.update(
                    "job_executions",
                    {
                        "finished_at": finished_at.isoformat(),
                        "status": "completed",
                        "result_summary": result_summary,
                        "tokens_used": result.get("tokens_used", 0),
                    },
                    {"id": execution_id},
                )

                # Update job status
                await self._db.update(
                    "scheduled_jobs",
                    {"status": "completed"},
                    {"id": job_id},
                )

                self._jobs_executed += 1
                logger.info(
                    "job_execution_completed",
                    job_id=job_id,
                    execution_id=execution_id,
                    duration_s=(finished_at - started_at).total_seconds(),
                )

                # Send notification
                await self._notify(
                    user_id=user_id,
                    channel=channel,
                    title=title,
                    status="completed",
                    result=result_summary,
                )

                # Handle recurrence
                await self._handle_recurrence(job)

            except asyncio.TimeoutError:
                await self._handle_failure(
                    job_id=job_id,
                    execution_id=execution_id,
                    error=f"Job timed out after {JOB_TIMEOUT_S}s",
                    job=job,
                    user_id=user_id,
                    channel=channel,
                    title=title,
                )

            except Exception as e:
                await self._handle_failure(
                    job_id=job_id,
                    execution_id=execution_id,
                    error=str(e),
                    job=job,
                    user_id=user_id,
                    channel=channel,
                    title=title,
                )

    async def _kernel_execute(
        self,
        instruction: str,
        user_id: str,
        source: str,
        job_id: str,
    ) -> dict[str, Any]:
        """
        Re-enter the kernel to execute the job's instruction.
        Uses the kernel's run() method with a synthetic RunInput.
        """
        from contracts.kernel_interface import RunInput, IntentType

        run_input = RunInput(
            message=instruction,
            user_id=user_id,
            intent=IntentType.EXECUTE,
            metadata={
                "source": source,
                "scheduled_job_id": job_id,
                "autonomous": True,
            },
        )

        try:
            result = await self._kernel.run(run_input)
            return {
                "response": result.response if hasattr(result, "response") else str(result),
                "tokens_used": getattr(result, "tokens_used", 0),
                "status": "completed",
            }
        except Exception as e:
            logger.error("kernel_reentry_failed", job_id=job_id, error=str(e))
            return {
                "response": f"Error during execution: {str(e)}",
                "tokens_used": 0,
                "status": "failed",
            }

    async def _handle_failure(
        self,
        job_id: str,
        execution_id: str,
        error: str,
        job: dict,
        user_id: str,
        channel: str,
        title: str,
    ) -> None:
        """Handle a failed job execution with retry logic."""
        finished_at = datetime.now(timezone.utc)
        retry_count = job.get("retry_count", 0) + 1
        max_retries = job.get("max_retries", 1)

        # Update execution record
        await self._db.update(
            "job_executions",
            {
                "finished_at": finished_at.isoformat(),
                "status": "failed",
                "error": error[:2000],
            },
            {"id": execution_id},
        )

        if retry_count < max_retries:
            # Reschedule for retry (5 min delay)
            retry_at = finished_at + timedelta(minutes=5)
            await self._db.update(
                "scheduled_jobs",
                {
                    "status": "scheduled",
                    "retry_count": retry_count,
                    "last_error": error[:500],
                    "run_at": retry_at.isoformat(),
                },
                {"id": job_id},
            )
            logger.warning(
                "job_retry_scheduled",
                job_id=job_id,
                retry_count=retry_count,
                retry_at=retry_at.isoformat(),
            )
        else:
            # Mark as permanently failed
            await self._db.update(
                "scheduled_jobs",
                {
                    "status": "failed",
                    "retry_count": retry_count,
                    "last_error": error[:500],
                },
                {"id": job_id},
            )
            self._jobs_failed += 1
            logger.error(
                "job_permanently_failed",
                job_id=job_id,
                error=error[:200],
            )

        # Notify user of failure
        await self._notify(
            user_id=user_id,
            channel=channel,
            title=title,
            status="failed",
            result=f"Error: {error[:500]}",
        )

    async def _handle_recurrence(self, job: dict) -> None:
        """If the job is recurring, schedule the next execution."""
        recurrence = job.get("recurrence")
        if not recurrence:
            return

        job_id = job.get("id")
        run_at_str = job.get("run_at", "")
        user_tz = job.get("timezone", "America/Mexico_City")

        try:
            run_at = datetime.fromisoformat(run_at_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            run_at = datetime.now(timezone.utc)

        if recurrence == "daily":
            next_run = run_at + timedelta(days=1)
        elif recurrence == "weekly":
            next_run = run_at + timedelta(weeks=1)
        else:
            return

        # Check TTL
        if (next_run - datetime.now(timezone.utc)).days > MAX_TTL_DAYS:
            logger.info("recurrence_ttl_exceeded", job_id=job_id)
            return

        # Create new job for next occurrence
        new_job = {
            "id": str(uuid4()),
            "user_id": job.get("user_id"),
            "thread_id": job.get("thread_id"),
            "title": job.get("title"),
            "instruction": job.get("instruction"),
            "run_at": next_run.isoformat(),
            "timezone": user_tz,
            "channel": job.get("channel", "telegram"),
            "status": "scheduled",
            "recurrence": recurrence,
            "max_retries": job.get("max_retries", 1),
            "retry_count": 0,
        }
        await self._db.insert("scheduled_jobs", new_job)
        logger.info(
            "recurrence_scheduled",
            original_job_id=job_id,
            new_job_id=new_job["id"],
            next_run=next_run.isoformat(),
        )

    async def _notify(
        self,
        user_id: str,
        channel: str,
        title: str,
        status: str,
        result: str,
    ) -> None:
        """Send notification about job completion/failure."""
        if channel == "telegram" and self._notifier:
            try:
                emoji = "\u2705" if status == "completed" else "\u274c"
                message = (
                    f"{emoji} **Tarea Autónoma: {title}**\n\n"
                    f"Estado: {status}\n\n"
                    f"{result[:1500]}"
                )
                await self._notifier.send_message(user_id, message)
            except Exception as e:
                logger.error("notification_failed", channel=channel, error=str(e))
        elif channel == "webhook":
            # Future: call webhook with result
            logger.info("webhook_notification_skipped", msg="Not implemented yet")
        else:
            logger.info("notification_channel_unknown", channel=channel)
