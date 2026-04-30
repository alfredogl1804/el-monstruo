"""
El Monstruo — Autonomous Runner (Sprint 37: MOC Integration)
=============================================================
Background asyncio task que:
  1. Polls Supabase every POLL_INTERVAL_S for due scheduled_jobs
  2. Sprint 37: Pasa los jobs al MOC para priorización dinámica
  3. Para cada job (en orden de prioridad), re-entra al kernel
  4. Sprint 37: Feedback loop — actualiza success_rate tras cada ejecución
  5. Registra ejecución en job_executions con cost_usd real
  6. Envía notificación via Telegram (u otro canal)
  7. Maneja recurrencia (reschedule daily/weekly jobs)

Guardrails:
  - Max concurrent executions: 3
  - Anti-recursión: source="scheduled_job" bloquea schedule_task tool
  - TTL: jobs older than 30 days auto-cancel
  - Error handling: retry up to max_retries, then mark failed

Architecture (Sprint 37):
  lifespan(startup) → asyncio.create_task(runner.start())
  runner.start() → poll loop → MOC.priorizar_jobs() → _execute_job() → feedback → notify
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
    Background runner que ejecuta scheduled jobs de forma autónoma.

    Sprint 37: Integrado con MOC para priorización dinámica.
    El MOC reordena los jobs antes de ejecutarlos según:
      - Urgencia temporal (40%)
      - Impacto de la tarea (30%)
      - Presupuesto disponible (20%)
      - Historial de éxito (10%)

    Dependencias (inyectadas):
        - db: SupabaseClient para leer/escribir jobs
        - kernel: LangGraphKernel para re-entry execution
        - notifier: TelegramNotifier para enviar resultados al usuario
        - moc: MOC (Motor de Orquestación Central) — opcional, inyectado post-init
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
        self._moc: Optional[Any] = None  # Sprint 37: inyectado post-init por main.py
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self._jobs_executed = 0
        self._jobs_failed = 0
        # Sprint 37: métricas de priorización
        self._jobs_prioritized = 0
        self._moc_reorders = 0  # Cuántas veces el MOC cambió el orden FIFO

    def set_moc(self, moc: Any) -> None:
        """Sprint 37: Inyectar el MOC después de la construcción (evita circular deps)."""
        self._moc = moc
        logger.info("runner_moc_injected")

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "poll_interval_s": POLL_INTERVAL_S,
            "max_concurrent": MAX_CONCURRENT,
            "jobs_executed": self._jobs_executed,
            "jobs_failed": self._jobs_failed,
            # Sprint 37
            "moc_enabled": self._moc is not None,
            "jobs_prioritized": self._jobs_prioritized,
            "moc_reorders": self._moc_reorders,
        }

    async def start(self) -> None:
        """Iniciar el polling loop como background task."""
        if self._running:
            logger.warning("runner_already_running")
            return
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(
            "autonomous_runner_started",
            poll_interval=POLL_INTERVAL_S,
            moc_enabled=self._moc is not None,
        )

    async def stop(self) -> None:
        """Detener el runner gracefully."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("autonomous_runner_stopped")

    async def _poll_loop(self) -> None:
        """Main polling loop — corre cada POLL_INTERVAL_S segundos."""
        while self._running:
            try:
                await self._poll_once()
            except Exception as e:
                logger.error("poll_loop_error", error=str(e))
            await asyncio.sleep(POLL_INTERVAL_S)

    async def _poll_once(self) -> None:
        """
        Single poll iteration: encuentra jobs pendientes y los ejecuta.

        Sprint 37: Después del claim atómico, pasa los jobs al MOC para
        reordenarlos por prioridad antes de ejecutar.
        """
        if not self._db or not self._db.connected:
            return

        # Claim jobs atómicamente (RPC get_due_jobs marca status='running')
        try:
            due_jobs = await self._db.rpc("get_due_jobs", {"max_jobs": MAX_CONCURRENT})
        except Exception as e:
            # Fallback: select manual si el RPC no está disponible
            logger.warning("rpc_get_due_jobs_failed", error=str(e), fallback="manual_select")
            due_jobs = await self._db.select(
                "scheduled_jobs",
                filters={"status": "scheduled"},
                order_by="run_at",
                order_desc=False,
                limit=MAX_CONCURRENT,
            )
            # Filtrar solo los que ya vencieron
            now = datetime.now(timezone.utc)
            due_jobs = [
                j
                for j in due_jobs
                if j.get("run_at") and datetime.fromisoformat(j["run_at"].replace("Z", "+00:00")) <= now
            ]
            # Reclamar actualizando status
            for job in due_jobs:
                await self._db.update(
                    "scheduled_jobs",
                    {"status": "running"},
                    {"id": job["id"]},
                )

        if not due_jobs:
            return

        logger.info("due_jobs_found", count=len(due_jobs))

        # ── Sprint 37: MOC Prioritization ─────────────────────────────
        # El MOC reordena los jobs por score dinámico antes de ejecutar.
        # Si el MOC no está disponible, se ejecutan en orden FIFO (run_at).
        if self._moc is not None and len(due_jobs) > 1:
            try:
                original_order = [j.get("id") for j in due_jobs]
                due_jobs = await self._moc.priorizar_jobs(due_jobs)
                new_order = [j.get("id") for j in due_jobs]

                self._jobs_prioritized += len(due_jobs)

                # Detectar si el MOC cambió el orden
                if original_order != new_order:
                    self._moc_reorders += 1
                    logger.info(
                        "moc_reordered_jobs",
                        original_order=original_order,
                        new_order=new_order,
                        top_score=due_jobs[0].get("moc_priority_score", 0),
                    )

                # Persistir el score calculado en cada job
                for job in due_jobs:
                    score = job.get("moc_priority_score")
                    if score is not None:
                        try:
                            await self._db.update(
                                "scheduled_jobs",
                                {
                                    "moc_priority_score": score,
                                    "last_prioritized_at": datetime.now(timezone.utc).isoformat(),
                                },
                                {"id": job["id"]},
                            )
                        except Exception:
                            pass  # No bloquear ejecución por error de persistencia

            except Exception as e:
                logger.warning("moc_prioritization_failed", error=str(e), fallback="fifo")
                # Continuar con orden FIFO en caso de error del MOC
        elif self._moc is not None and len(due_jobs) == 1:
            # Un solo job — priorizar igual para actualizar el score
            try:
                due_jobs = await self._moc.priorizar_jobs(due_jobs)
                self._jobs_prioritized += 1
                score = due_jobs[0].get("moc_priority_score")
                if score is not None:
                    await self._db.update(
                        "scheduled_jobs",
                        {
                            "moc_priority_score": score,
                            "last_prioritized_at": datetime.now(timezone.utc).isoformat(),
                        },
                        {"id": due_jobs[0]["id"]},
                    )
            except Exception as e:
                logger.warning("moc_single_job_prioritization_failed", error=str(e))

        # Ejecutar jobs en orden de prioridad (concurrentemente hasta MAX_CONCURRENT)
        tasks = [self._execute_job(job) for job in due_jobs]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_job(self, job: dict[str, Any]) -> None:
        """
        Ejecutar un único scheduled job via kernel re-entry.

        Sprint 37: Después de la ejecución, actualiza success_rate en
        scheduled_jobs basándose en el historial de job_executions.
        """
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
                moc_score=job.get("moc_priority_score", "N/A"),
            )

            # Registrar inicio de ejecución
            await self._db.insert(
                "job_executions",
                {
                    "id": execution_id,
                    "scheduled_job_id": job_id,
                    "started_at": started_at.isoformat(),
                    "status": "running",
                },
            )

            try:
                # Re-entrar al kernel con la instrucción del job
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
                result_summary = result.get("response", "")[:2000]
                tokens_used = result.get("tokens_used", 0)
                # Sprint 37: calcular costo real (aprox $0.000002/token)
                cost_usd = round(tokens_used * 0.000002, 6)

                # Actualizar registro de ejecución con costo real
                await self._db.update(
                    "job_executions",
                    {
                        "finished_at": finished_at.isoformat(),
                        "status": "completed",
                        "result_summary": result_summary,
                        "tokens_used": tokens_used,
                        "cost_usd": cost_usd,
                    },
                    {"id": execution_id},
                )

                # Actualizar estado del job
                await self._db.update(
                    "scheduled_jobs",
                    {"status": "completed"},
                    {"id": job_id},
                )

                self._jobs_executed += 1
                duration_s = (finished_at - started_at).total_seconds()
                logger.info(
                    "job_execution_completed",
                    job_id=job_id,
                    execution_id=execution_id,
                    duration_s=duration_s,
                    tokens_used=tokens_used,
                    cost_usd=cost_usd,
                )

                # Sprint 37: Feedback loop — actualizar success_rate
                await self._update_success_rate(job_id)

                # Enviar notificación
                await self._notify(
                    user_id=user_id,
                    channel=channel,
                    title=title,
                    status="completed",
                    result=result_summary,
                )

                # Manejar recurrencia
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

    async def _update_success_rate(self, job_id: str) -> None:
        """
        Sprint 37: Feedback loop — calcula y persiste el success_rate del job.

        Lee las últimas 20 ejecuciones del job y calcula el ratio de éxito.
        Este valor alimenta al Priorizador del MOC en el próximo ciclo.
        """
        try:
            # Obtener historial de ejecuciones del job
            executions = await self._db.select(
                "job_executions",
                filters={"scheduled_job_id": job_id},
                order_by="started_at",
                order_desc=True,
                limit=20,
            )

            if not executions:
                return

            total = len(executions)
            completed = sum(1 for e in executions if e.get("status") == "completed")
            success_rate = round(completed / total, 3) if total > 0 else 1.0

            # Persistir success_rate en scheduled_jobs
            await self._db.update(
                "scheduled_jobs",
                {"success_rate": success_rate},
                {"id": job_id},
            )

            logger.info(
                "job_success_rate_updated",
                job_id=job_id,
                success_rate=success_rate,
                total_executions=total,
                completed=completed,
            )

        except Exception as e:
            logger.warning("success_rate_update_failed", job_id=job_id, error=str(e))

    async def _kernel_execute(
        self,
        instruction: str,
        user_id: str,
        source: str,
        job_id: str,
    ) -> dict[str, Any]:
        """
        Re-entrar al kernel para ejecutar la instrucción del job.
        Usa kernel.start_run() con un RunInput sintético.
        """
        from contracts.kernel_interface import RunInput

        run_input = RunInput(
            message=instruction,
            user_id=user_id,
            channel="autonomous",
            context={
                "source": source,
                "scheduled_job_id": job_id,
                "autonomous": True,
            },
        )

        try:
            result = await self._kernel.start_run(run_input)
            return {
                "response": result.response if hasattr(result, "response") else str(result),
                "tokens_used": getattr(result, "tokens_used", 0),
                "status": "completed",
            }
        except Exception as e:
            logger.error("kernel_reentry_failed", job_id=job_id, error=str(e))
            return {
                "response": f"Error durante ejecución: {str(e)}",
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
        """Manejar un job fallido con lógica de retry."""
        finished_at = datetime.now(timezone.utc)
        retry_count = job.get("retry_count", 0) + 1
        max_retries = job.get("max_retries", 1)

        # Actualizar registro de ejecución
        await self._db.update(
            "job_executions",
            {
                "finished_at": finished_at.isoformat(),
                "status": "failed",
                "error": error[:2000],
                "cost_usd": 0.0,
            },
            {"id": execution_id},
        )

        if retry_count < max_retries:
            # Reprogramar para retry (5 min de delay)
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
            # Marcar como fallido permanentemente
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

        # Sprint 37: Feedback loop incluso en fallo
        await self._update_success_rate(job_id)

        # Notificar al usuario
        await self._notify(
            user_id=user_id,
            channel=channel,
            title=title,
            status="failed",
            result=f"Error: {error[:500]}",
        )

    async def _handle_recurrence(self, job: dict) -> None:
        """Si el job es recurrente, programar la próxima ejecución."""
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

        # Verificar TTL
        if (next_run - datetime.now(timezone.utc)).days > MAX_TTL_DAYS:
            logger.info("recurrence_ttl_exceeded", job_id=job_id)
            return

        # Crear nuevo job para la próxima ocurrencia
        # Sprint 37: heredar task_type y estimated_cost_usd del job original
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
            # Sprint 37: heredar metadatos de priorización
            "task_type": job.get("task_type", "default"),
            "estimated_cost_usd": job.get("estimated_cost_usd", 0.0),
            "success_rate": job.get("success_rate", 1.0),  # Heredar historial
        }
        await self._db.insert("scheduled_jobs", new_job)
        logger.info(
            "recurrence_scheduled",
            original_job_id=job_id,
            new_job_id=new_job["id"],
            next_run=next_run.isoformat(),
            task_type=new_job["task_type"],
        )

    async def _notify(
        self,
        user_id: str,
        channel: str,
        title: str,
        status: str,
        result: str,
    ) -> None:
        """Enviar notificación sobre completado/fallo del job."""
        if channel == "telegram" and self._notifier:
            try:
                emoji = "\u2705" if status == "completed" else "\u274c"
                message = f"{emoji} **Tarea Autónoma: {title}**\n\nEstado: {status}\n\n{result[:1500]}"
                await self._notifier.send_message(user_id, message)
            except Exception as e:
                logger.error("notification_failed", channel=channel, error=str(e))
        elif channel == "webhook":
            logger.info("webhook_notification_skipped", msg="Not implemented yet")
        else:
            logger.info("notification_channel_unknown", channel=channel)
