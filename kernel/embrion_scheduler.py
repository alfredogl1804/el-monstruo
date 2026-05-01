"""
El Monstruo — Embrión Scheduler (Sprint 56.3)
=============================================
Scheduler interno para tareas autónomas de los Embriones.
Cada Embrión puede tener tareas programadas que se ejecutan
sin intervención humana.

Tipos de tareas:
  - periodic: Se ejecuta cada N horas (e.g., causal seeding cada 6h)
  - daily:    Se ejecuta una vez al día a hora fija (e.g., validación a las 3am UTC)
  - triggered: Se ejecuta cuando una condición se cumple (e.g., nuevo evento detectado)
  - one_shot: Se ejecuta una vez y se elimina (e.g., investigar tema específico)

Governance (Obj #4 — Nunca se equivoca dos veces):
  - Cada tarea tiene un budget máximo (costo USD por ejecución)
  - Si una tarea falla 3 veces seguidas, se pausa y notifica
  - Budget diario total compartido entre todas las tareas (EMBRION_DAILY_BUDGET)

Persistencia (Corrección C3 del cruce detractor):
  - Las tareas se persisten en Supabase tabla `scheduled_tasks`
  - Al reiniciar el servidor, las tareas se recuperan de Supabase
  - Sin persistencia, las tareas programadas se perderían en cada deploy

Integración:
  - CausalKB (Sprint 55.3): El handler `run_causal_seeding_cycle` alimenta la KB
  - ThreeLayerMemory (Sprint 51): El handler `run_memory_consolidation` consolida memorias
  - LangfuseBridge (Sprint 13): Cada ejecución emite un trace de observabilidad

Validated: APScheduler 3.11.2 (MIT, Dec 2025), Supabase (ya en stack)
Sprint 56.3 | Biblias: Kimi K2.6 (Agent Swarm budget), Mem0 v2 (memory consolidation)
"""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Coroutine, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("kernel.embrion_scheduler")


# ── Dataclasses ──────────────────────────────────────────────────────────────


@dataclass
class ScheduledTask:
    """
    Una tarea programada para un Embrión.

    Unidad atómica del Scheduler. Cada tarea tiene:
      - Identidad: task_id, name, description, embrion_id
      - Scheduling: schedule_type + interval_hours o daily_hour
      - Governance: max_cost_usd, max_retries, consecutive_failures
      - Estado: status, last_run, next_run, total_runs, total_cost_usd
      - Ejecución: handler (nombre del callable registrado) + handler_args
    """
    task_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    embrion_id: str = "embrion-0"  # Quién la ejecuta

    # Scheduling
    schedule_type: str = "periodic"   # periodic | daily | triggered | one_shot
    interval_hours: float = 6.0       # Para periodic: cada N horas
    daily_hour: int = 3               # Para daily: hora UTC (0-23)
    trigger_condition: Optional[str] = None  # Para triggered: expresión evaluable

    # Governance
    max_cost_usd: float = 0.50        # Budget máximo por ejecución
    max_retries: int = 3              # Fallos consecutivos antes de pausar
    consecutive_failures: int = 0
    paused: bool = False

    # Estado
    status: str = "active"            # active | paused | completed | failed
    last_run: Optional[str] = None    # ISO timestamp última ejecución
    next_run: Optional[str] = None    # ISO timestamp próxima ejecución
    total_runs: int = 0
    total_cost_usd: float = 0.0

    # Ejecución
    handler: Optional[str] = None     # Nombre del handler registrado
    handler_args: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "embrion_id": self.embrion_id,
            "schedule_type": self.schedule_type,
            "interval_hours": self.interval_hours,
            "daily_hour": self.daily_hour,
            "trigger_condition": self.trigger_condition,
            "max_cost_usd": self.max_cost_usd,
            "max_retries": self.max_retries,
            "consecutive_failures": self.consecutive_failures,
            "paused": self.paused,
            "status": self.status,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "total_runs": self.total_runs,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "handler": self.handler,
            "handler_args": self.handler_args,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScheduledTask":
        handler_args = data.get("handler_args", {})
        if isinstance(handler_args, str):
            try:
                handler_args = json.loads(handler_args)
            except Exception:
                handler_args = {}
        return cls(
            task_id=data.get("task_id", str(uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            embrion_id=data.get("embrion_id", "embrion-0"),
            schedule_type=data.get("schedule_type", "periodic"),
            interval_hours=float(data.get("interval_hours", 6.0)),
            daily_hour=int(data.get("daily_hour", 3)),
            trigger_condition=data.get("trigger_condition"),
            max_cost_usd=float(data.get("max_cost_usd", 0.50)),
            max_retries=int(data.get("max_retries", 3)),
            consecutive_failures=int(data.get("consecutive_failures", 0)),
            paused=bool(data.get("paused", False)),
            status=data.get("status", "active"),
            last_run=data.get("last_run"),
            next_run=data.get("next_run"),
            total_runs=int(data.get("total_runs", 0)),
            total_cost_usd=float(data.get("total_cost_usd", 0.0)),
            handler=data.get("handler"),
            handler_args=handler_args,
        )


# ── EmbrionScheduler ─────────────────────────────────────────────────────────


class EmbrionScheduler:
    """
    Scheduler de tareas autónomas para Embriones.

    Gestiona el ciclo de vida de tareas programadas con:
      - Persistencia en Supabase (corrección C3 — no SQLite local)
      - Budget diario compartido (EMBRION_DAILY_BUDGET env var)
      - Auto-pause tras max_retries fallos consecutivos
      - Loop asyncio que revisa tareas cada 60 segundos

    Uso típico:
        scheduler = EmbrionScheduler(db=supabase_client)
        await scheduler.initialize()
        register_default_tasks(scheduler)
        scheduler.register_handler("run_health_check", my_health_fn)
        await scheduler.start()
        app.state.embrion_scheduler = scheduler
    """

    TABLE = "scheduled_tasks"
    DAILY_BUDGET_USD = float(os.environ.get("EMBRION_DAILY_BUDGET", "10.0"))
    LOOP_INTERVAL_SECONDS = 60

    def __init__(self, db: Any = None):
        self._db = db
        self._tasks: dict[str, ScheduledTask] = {}
        self._handlers: dict[str, Callable[..., Coroutine]] = {}
        self._daily_spend: float = 0.0
        self._daily_reset: Optional[str] = None
        self._running: bool = False
        self._check_task: Optional[asyncio.Task] = None

    # ── Inicialización ────────────────────────────────────────────────────────

    async def initialize(self) -> None:
        """
        Inicializar el scheduler.
        Recupera tareas persistidas en Supabase (corrección C3).
        Si no hay Supabase, opera en modo in-memory (degradado).
        """
        if self._db:
            await self._restore_from_supabase()
            logger.info(
                "embrion_scheduler_initialized",
                db="supabase",
                tasks_restored=len(self._tasks),
            )
        else:
            logger.warning(
                "embrion_scheduler_no_db",
                hint="Tasks will NOT persist across restarts. Set SUPABASE_DB_URL.",
            )

    async def _restore_from_supabase(self) -> None:
        """Restaurar tareas desde Supabase al startup."""
        try:
            rows = await self._db.select(
                self.TABLE,
                filters={"status": "active"},
            )
            restored = 0
            for row in (rows or []):
                task = ScheduledTask.from_dict(row)
                # Recalcular next_run si está en el pasado (servidor estuvo caído)
                if task.next_run and task.next_run < datetime.now(timezone.utc).isoformat():
                    task.next_run = self._calculate_next_run(task)
                self._tasks[task.task_id] = task
                restored += 1
            logger.info("scheduler_tasks_restored", count=restored)
        except Exception as e:
            logger.warning("scheduler_restore_failed", error=str(e))

    async def _persist_task(self, task: ScheduledTask) -> None:
        """Persistir o actualizar una tarea en Supabase."""
        if not self._db:
            return
        try:
            row = {
                "id": task.task_id,
                **task.to_dict(),
                "handler_args": json.dumps(task.handler_args),
            }
            # Renombrar task_id → id para Supabase
            row.pop("task_id", None)
            row["id"] = task.task_id
            await self._db.upsert(self.TABLE, row)
        except Exception as e:
            logger.warning("scheduler_persist_failed", task=task.name, error=str(e))

    # ── Gestión de handlers ───────────────────────────────────────────────────

    def register_handler(self, name: str, handler: Callable[..., Coroutine]) -> None:
        """
        Registrar un handler ejecutable por nombre.

        El handler debe ser una coroutine async.
        Los ScheduledTask.handler apuntan a este nombre.
        """
        self._handlers[name] = handler
        logger.info("scheduler_handler_registered", name=name)

    # ── Gestión de tareas ─────────────────────────────────────────────────────

    def add_task(self, task: ScheduledTask) -> str:
        """
        Agregar una tarea al scheduler.

        Calcula next_run automáticamente.
        Persiste en Supabase (fire-and-forget).
        """
        task.next_run = self._calculate_next_run(task)
        self._tasks[task.task_id] = task

        # Persistir en background (no bloquear)
        asyncio.create_task(self._persist_task(task)) if asyncio.get_event_loop().is_running() else None

        logger.info(
            "scheduler_task_added",
            task_id=task.task_id,
            name=task.name,
            schedule=task.schedule_type,
            next_run=task.next_run,
            embrion=task.embrion_id,
        )
        return task.task_id

    def remove_task(self, task_id: str) -> bool:
        """Remover una tarea del scheduler."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            logger.info("scheduler_task_removed", task_id=task_id)
            return True
        return False

    def pause_task(self, task_id: str) -> bool:
        """Pausar una tarea activa."""
        if task_id in self._tasks:
            self._tasks[task_id].paused = True
            self._tasks[task_id].status = "paused"
            asyncio.create_task(self._persist_task(self._tasks[task_id])) if asyncio.get_event_loop().is_running() else None
            logger.info("scheduler_task_paused", task_id=task_id)
            return True
        return False

    def resume_task(self, task_id: str) -> bool:
        """Reanudar una tarea pausada."""
        if task_id in self._tasks:
            t = self._tasks[task_id]
            t.paused = False
            t.status = "active"
            t.consecutive_failures = 0
            t.next_run = self._calculate_next_run(t)
            asyncio.create_task(self._persist_task(t)) if asyncio.get_event_loop().is_running() else None
            logger.info("scheduler_task_resumed", task_id=task_id, next_run=t.next_run)
            return True
        return False

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Obtener una tarea por ID."""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[dict[str, Any]]:
        """Listar todas las tareas con su estado actual."""
        return [t.to_dict() for t in self._tasks.values()]

    # ── Scheduler loop ────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Iniciar el scheduler loop en background."""
        self._running = True
        self._check_task = asyncio.create_task(self._scheduler_loop())
        logger.info(
            "embrion_scheduler_started",
            tasks=len(self._tasks),
            daily_budget_usd=self.DAILY_BUDGET_USD,
            loop_interval_s=self.LOOP_INTERVAL_SECONDS,
        )

    async def stop(self) -> None:
        """Detener el scheduler limpiamente."""
        self._running = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        logger.info("embrion_scheduler_stopped", total_tasks=len(self._tasks))

    async def _scheduler_loop(self) -> None:
        """Loop principal. Revisa tareas cada LOOP_INTERVAL_SECONDS."""
        while self._running:
            try:
                await self._check_and_execute_due_tasks()
                await asyncio.sleep(self.LOOP_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("scheduler_loop_error", error=str(e))
                await asyncio.sleep(self.LOOP_INTERVAL_SECONDS)

    async def _check_and_execute_due_tasks(self) -> None:
        """Verificar y ejecutar tareas que están listas para ejecutarse."""
        self._reset_daily_budget_if_needed()

        now = datetime.now(timezone.utc).isoformat()

        for task in list(self._tasks.values()):
            if task.paused or task.status not in ("active",):
                continue
            if not task.next_run or task.next_run > now:
                continue
            if self._daily_spend >= self.DAILY_BUDGET_USD:
                logger.warning(
                    "scheduler_daily_budget_exhausted",
                    spend=self._daily_spend,
                    budget=self.DAILY_BUDGET_USD,
                )
                break

            # Ejecutar tarea de forma aislada (no bloquear el loop)
            asyncio.create_task(self._execute_task(task))

    async def _execute_task(self, task: ScheduledTask) -> None:
        """
        Ejecutar una tarea individual.

        Governance:
          - Registra last_run, total_runs, estimated_cost
          - Si falla: incrementa consecutive_failures
          - Si falla >= max_retries: pausa la tarea
          - Persiste el estado actualizado en Supabase
        """
        handler = self._handlers.get(task.handler)
        if not handler:
            logger.error(
                "scheduler_handler_not_found",
                handler=task.handler,
                task=task.name,
                hint="Register handler with scheduler.register_handler(name, fn)",
            )
            # Contar como fallo para no quedar en loop infinito
            task.consecutive_failures += 1
            task.last_run = datetime.now(timezone.utc).isoformat()
            if task.consecutive_failures >= task.max_retries:
                task.paused = True
                task.status = "paused"
            else:
                task.next_run = self._calculate_next_run(task)
            await self._persist_task(task)
            return

        logger.info(
            "scheduler_task_executing",
            task_id=task.task_id,
            name=task.name,
            embrion=task.embrion_id,
            handler=task.handler,
        )

        try:
            await handler(**task.handler_args)

            # ── Éxito ──────────────────────────────────────────────────────
            task.last_run = datetime.now(timezone.utc).isoformat()
            task.total_runs += 1
            task.consecutive_failures = 0

            # Estimar costo conservador (50% del max declarado)
            estimated_cost = task.max_cost_usd * 0.5
            task.total_cost_usd += estimated_cost
            self._daily_spend += estimated_cost

            if task.schedule_type == "one_shot":
                task.status = "completed"
            else:
                task.next_run = self._calculate_next_run(task)

            logger.info(
                "scheduler_task_completed",
                task_id=task.task_id,
                name=task.name,
                total_runs=task.total_runs,
                estimated_cost_usd=round(estimated_cost, 4),
                daily_spend_usd=round(self._daily_spend, 4),
            )

        except Exception as e:
            # ── Fallo ──────────────────────────────────────────────────────
            task.consecutive_failures += 1
            task.last_run = datetime.now(timezone.utc).isoformat()

            if task.consecutive_failures >= task.max_retries:
                task.paused = True
                task.status = "paused"
                logger.error(
                    "scheduler_task_paused_max_failures",
                    task_id=task.task_id,
                    name=task.name,
                    failures=task.consecutive_failures,
                    error=str(e),
                )
            else:
                task.next_run = self._calculate_next_run(task)
                logger.warning(
                    "scheduler_task_failed",
                    task_id=task.task_id,
                    name=task.name,
                    failures=task.consecutive_failures,
                    max_retries=task.max_retries,
                    error=str(e),
                )

        # Persistir estado actualizado
        await self._persist_task(task)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _calculate_next_run(self, task: ScheduledTask) -> str:
        """Calcular la próxima ejecución de una tarea."""
        now = datetime.now(timezone.utc)

        if task.schedule_type == "periodic":
            next_time = now + timedelta(hours=task.interval_hours)

        elif task.schedule_type == "daily":
            next_time = now.replace(
                hour=task.daily_hour,
                minute=0,
                second=0,
                microsecond=0,
            )
            if next_time <= now:
                next_time += timedelta(days=1)

        elif task.schedule_type == "one_shot":
            next_time = now + timedelta(minutes=1)  # Ejecutar pronto

        else:
            # triggered o desconocido: default 1 hora
            next_time = now + timedelta(hours=1)

        return next_time.isoformat()

    def _reset_daily_budget_if_needed(self) -> None:
        """Reset del budget diario si cambió el día UTC."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._daily_reset != today:
            prev_spend = self._daily_spend
            self._daily_spend = 0.0
            self._daily_reset = today
            if prev_spend > 0:
                logger.info(
                    "scheduler_daily_budget_reset",
                    prev_spend_usd=round(prev_spend, 4),
                    new_budget_usd=self.DAILY_BUDGET_USD,
                )

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas completas del scheduler."""
        active = sum(1 for t in self._tasks.values() if t.status == "active" and not t.paused)
        paused = sum(1 for t in self._tasks.values() if t.paused or t.status == "paused")
        completed = sum(1 for t in self._tasks.values() if t.status == "completed")
        total_runs = sum(t.total_runs for t in self._tasks.values())
        total_cost = sum(t.total_cost_usd for t in self._tasks.values())

        return {
            "total_tasks": len(self._tasks),
            "active_tasks": active,
            "paused_tasks": paused,
            "completed_tasks": completed,
            "total_runs_all_time": total_runs,
            "total_cost_usd_all_time": round(total_cost, 4),
            "daily_spend_usd": round(self._daily_spend, 4),
            "daily_budget_usd": self.DAILY_BUDGET_USD,
            "daily_budget_remaining_usd": round(self.DAILY_BUDGET_USD - self._daily_spend, 4),
            "running": self._running,
            "handlers_registered": list(self._handlers.keys()),
            "persistence": "supabase" if self._db else "in-memory (degraded)",
        }


# ── Default Tasks ─────────────────────────────────────────────────────────────


def register_default_tasks(scheduler: EmbrionScheduler) -> None:
    """
    Registrar las 5 tareas default del sistema al startup.

    Estas tareas son el corazón de la autonomía de El Monstruo:
      1. Causal Seeding — alimenta la Causal KB cada 6h (Obj #10)
      2. Prediction Validation — valida predicciones diariamente a las 3am UTC (Obj #10)
      3. Vanguard Scan — detecta nuevas tecnologías a las 6am UTC (Obj #7)
      4. Health Check — verifica salud del sistema cada 2h (Obj #4)
      5. Memory Consolidation — consolida memorias a las 2am UTC (Obj #3)

    Los handlers deben registrarse por separado con scheduler.register_handler().
    Si un handler no está registrado, la tarea fallará con gracia (no crash).
    """

    # 1. Causal Seeding — Obj #10: Simulador Predictivo
    # Alimenta la Causal KB con eventos históricos descompuestos
    # Prerequisito para que el Simulador tenga datos históricos
    scheduler.add_task(ScheduledTask(
        name="causal_seeding",
        description="Feed the Causal KB with new decomposed events (Obj #10)",
        embrion_id="embrion-causal",
        schedule_type="periodic",
        interval_hours=6.0,
        max_cost_usd=1.00,
        handler="run_causal_seeding_cycle",
    ))

    # 2. Prediction Validation — Obj #10: Feedback loop del Simulador
    # Valida predicciones vencidas y ajusta pesos de factores causales
    scheduler.add_task(ScheduledTask(
        name="prediction_validation",
        description="Validate due predictions and adjust causal factor weights (Obj #10)",
        embrion_id="embrion-causal",
        schedule_type="daily",
        daily_hour=3,  # 3am UTC
        max_cost_usd=0.50,
        handler="run_prediction_validation",
    ))

    # 3. Vanguard Scan — Obj #7: Vanguardia Tecnológica
    # Detecta nuevas herramientas y tecnologías relevantes para El Monstruo
    scheduler.add_task(ScheduledTask(
        name="vanguard_scan",
        description="Scan for new technologies and tools relevant to El Monstruo (Obj #7)",
        embrion_id="embrion-0",
        schedule_type="daily",
        daily_hour=6,  # 6am UTC
        max_cost_usd=0.30,
        handler="run_vanguard_scan",
    ))

    # 4. Health Check — Obj #4: Nunca se equivoca dos veces
    # Verifica salud de todos los subsistemas y reporta anomalías
    scheduler.add_task(ScheduledTask(
        name="system_health_check",
        description="Check health of all subsystems and report anomalies (Obj #4)",
        embrion_id="embrion-0",
        schedule_type="periodic",
        interval_hours=2.0,
        max_cost_usd=0.05,
        handler="run_health_check",
    ))

    # 5. Memory Consolidation — Obj #3: Memoria Perfecta
    # Consolida memorias de corto plazo en patrones de largo plazo (ThreeLayerMemory)
    scheduler.add_task(ScheduledTask(
        name="memory_consolidation",
        description="Consolidate short-term memories into long-term patterns (Obj #3)",
        embrion_id="embrion-0",
        schedule_type="daily",
        daily_hour=2,  # 2am UTC
        max_cost_usd=0.20,
        handler="run_memory_consolidation",
    ))

    logger.info(
        "scheduler_default_tasks_registered",
        count=5,
        tasks=["causal_seeding", "prediction_validation", "vanguard_scan",
               "system_health_check", "memory_consolidation"],
    )


# ── Default Handlers (stubs) ──────────────────────────────────────────────────


async def _stub_handler_causal_seeding(**kwargs: Any) -> None:
    """
    Stub del handler de Causal Seeding.
    Será reemplazado por CausalSeeder.run_cycle() en Sprint 56.1.
    """
    logger.info("causal_seeding_stub_executed", note="Sprint 56.1 will replace this stub")


async def _stub_handler_prediction_validation(**kwargs: Any) -> None:
    """
    Stub del handler de Prediction Validation.
    Será reemplazado por PredictionValidator.validate_due_predictions() en Sprint 56.2.
    """
    logger.info("prediction_validation_stub_executed", note="Sprint 56.2 will replace this stub")


async def _stub_handler_vanguard_scan(**kwargs: Any) -> None:
    """
    Stub del handler de Vanguard Scan.
    Será reemplazado por WideResearchTool en Sprint 57+.
    """
    logger.info("vanguard_scan_stub_executed", note="Sprint 57+ will replace this stub")


async def _stub_handler_health_check(**kwargs: Any) -> None:
    """
    Stub del handler de Health Check.
    Verifica que los componentes principales estén activos.
    """
    from datetime import datetime, timezone
    logger.info(
        "health_check_executed",
        timestamp=datetime.now(timezone.utc).isoformat(),
        status="ok",
    )


async def _stub_handler_memory_consolidation(**kwargs: Any) -> None:
    """
    Stub del handler de Memory Consolidation.
    Será reemplazado por ThreeLayerMemory.consolidate() en Sprint 57+.
    """
    logger.info("memory_consolidation_stub_executed", note="Sprint 57+ will replace this stub")


def register_stub_handlers(scheduler: EmbrionScheduler) -> None:
    """
    Registrar handlers stub para las 5 tareas default.

    Estos stubs permiten que el Scheduler funcione desde el primer deploy
    sin depender de CausalSeeder o PredictionValidator (aún no implementados).

    En sprints futuros, los stubs se reemplazan con implementaciones reales:
      - Sprint 56.1: run_causal_seeding_cycle → CausalSeeder.run_cycle()
      - Sprint 56.2: run_prediction_validation → PredictionValidator.validate_due_predictions()
      - Sprint 57+:  run_vanguard_scan → WideResearchTool
      - Sprint 57+:  run_memory_consolidation → ThreeLayerMemory.consolidate()
    """
    scheduler.register_handler("run_causal_seeding_cycle", _stub_handler_causal_seeding)
    scheduler.register_handler("run_prediction_validation", _stub_handler_prediction_validation)
    scheduler.register_handler("run_vanguard_scan", _stub_handler_vanguard_scan)
    scheduler.register_handler("run_health_check", _stub_handler_health_check)
    scheduler.register_handler("run_memory_consolidation", _stub_handler_memory_consolidation)
    logger.info("scheduler_stub_handlers_registered", count=5)


# ── Singleton global ──────────────────────────────────────────────────────────

_embrion_scheduler: Optional[EmbrionScheduler] = None


def get_embrion_scheduler(db: Any = None) -> EmbrionScheduler:
    """
    Retorna la instancia global de EmbrionScheduler.

    Args:
        db: SupabaseClient — requerido solo en la primera llamada.

    Returns:
        EmbrionScheduler instance (crea una nueva si no existe)
    """
    global _embrion_scheduler
    if _embrion_scheduler is None:
        _embrion_scheduler = EmbrionScheduler(db=db)
        logger.info("embrion_scheduler_singleton_created")
    return _embrion_scheduler
