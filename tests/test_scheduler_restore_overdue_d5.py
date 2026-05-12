"""
Sprint D-5 fix (2026-05-12 Hilo Ejecutor 1) — Restore overdue tasks execute immediately.

Verifica que tras `_restore_from_supabase` con `next_run` en pasado:
  1. `next_run` NO se recalcula al futuro (permanece en pasado)
  2. `_check_and_execute_due_tasks` dispara la task inmediatamente (proximo ciclo loop)
  3. Se loguea `scheduler_task_overdue_at_restore` con `seconds_overdue` calculado correctamente

Bug original (D-2 a D-4):
- `_restore_from_supabase` linea 211 hacia `task.next_run = self._calculate_next_run(task)`
  cuando detectaba `next_run` en pasado.
- Resultado: tasks vencidas tras downtime > interval (e.g. 6h+ caido) eran empujadas
  al futuro en cada restart, y nunca ejecutaban.
- Combinado con bug de upsert sin on_conflict (D-4), las 3 daily tasks zombies
  acumularon 1-6 dias sin ejecutar.

Fix D-5: NO recalcular `next_run` al futuro; loguear `seconds_overdue` y dejar que
el loop dispare en proximo ciclo (<=60s).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from kernel.embrion_scheduler import EmbrionScheduler, ScheduledTask


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_db_with_overdue_row(name: str, hours_overdue: float, embrion_id: str = "embrion-causal") -> MagicMock:
    """Crea un mock de db cuyo `select` devuelve 1 task con next_run en pasado."""
    overdue_iso = (datetime.now(timezone.utc) - timedelta(hours=hours_overdue)).isoformat()
    last_run_iso = (datetime.now(timezone.utc) - timedelta(hours=hours_overdue + 24)).isoformat()

    row = {
        "task_id": "11111111-1111-1111-1111-111111111111",
        "name": name,
        "description": f"test overdue {name}",
        "embrion_id": embrion_id,
        "schedule_type": "daily",
        "interval_hours": 24.0,
        "daily_hour": 3,
        "max_cost_usd": 0.50,
        "max_retries": 3,
        "consecutive_failures": 0,
        "paused": False,
        "status": "active",
        "last_run": last_run_iso,
        "next_run": overdue_iso,
        "total_runs": 1,
        "total_cost_usd": 0.0,
        "handler": "h_test",
        "handler_args": {},
    }
    db = MagicMock()
    db.select = AsyncMock(return_value=[row])
    db.upsert = AsyncMock(return_value={"id": row["task_id"]})
    return db, overdue_iso


# ── Test 1: next_run NO se recalcula al futuro ───────────────────────────────


@pytest.mark.asyncio
async def test_restore_keeps_overdue_next_run_in_past():
    """Tras restore, next_run de task vencida permanece en pasado (NO recalculado al futuro)."""
    db, overdue_iso = _build_db_with_overdue_row("prediction_validation", hours_overdue=144.2)

    scheduler = EmbrionScheduler(db=db)
    await scheduler._restore_from_supabase()

    assert len(scheduler._tasks) == 1, "esperado 1 task restaurada"
    task = next(iter(scheduler._tasks.values()))

    # CRITICO: next_run debe seguir siendo el ISO original (pasado), NO recalculado
    assert task.next_run == overdue_iso, (
        f"FALLO Sprint D-5: next_run fue recalculado al futuro.\n"
        f"  esperado (pasado): {overdue_iso}\n"
        f"  recibido:          {task.next_run}\n"
        f"El fix de D-5 requiere que next_run vencido permanezca en pasado "
        f"para que el loop la dispare inmediatamente en el proximo ciclo."
    )

    # Y debe estar efectivamente en el pasado vs ahora
    now_iso = _now_utc_iso()
    assert task.next_run < now_iso, (
        f"next_run debe ser < now: next_run={task.next_run} now={now_iso}"
    )


# ── Test 2: loop dispara la task overdue inmediatamente ──────────────────────


@pytest.mark.asyncio
async def test_overdue_task_executes_within_one_loop_cycle():
    """Tras restore con next_run en pasado, _check_and_execute_due_tasks dispara la task."""
    db, _ = _build_db_with_overdue_row("vanguard_scan", hours_overdue=69.2, embrion_id="embrion-0")

    scheduler = EmbrionScheduler(db=db)
    await scheduler._restore_from_supabase()

    # Mock del handler para verificar que se invoca
    handler_called = AsyncMock(return_value=None)
    task = next(iter(scheduler._tasks.values()))
    scheduler.register_handler(task.handler, handler_called)

    # Llamar al checker (simula 1 iteracion del loop)
    await scheduler._check_and_execute_due_tasks()

    # asyncio.create_task se uso dentro de _check_and_execute_due_tasks; dejar
    # tiempo a que se schedulee y se ejecute el handler
    import asyncio
    await asyncio.sleep(0.05)

    assert handler_called.await_count >= 1, (
        f"FALLO Sprint D-5: el handler NO fue invocado.\n"
        f"  await_count={handler_called.await_count}\n"
        f"  task.next_run={task.next_run}\n"
        f"  Pre-D-5 esto pasaba porque next_run quedaba en futuro tras restore."
    )


# ── Test 3: seconds_overdue se loguea correctamente ──────────────────────────


@pytest.mark.asyncio
async def test_log_seconds_overdue_calculated_correctly(caplog):
    """El log scheduler_task_overdue_at_restore incluye seconds_overdue >= esperado."""
    hours_overdue = 27.1  # causal_seeding caso real
    db, overdue_iso = _build_db_with_overdue_row("causal_seeding", hours_overdue=hours_overdue)

    # structlog escribe via logging stdlib; capturar todo a nivel INFO
    import structlog
    structlog.configure(
        processors=[structlog.stdlib.render_to_log_kwargs],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    scheduler = EmbrionScheduler(db=db)
    with caplog.at_level(logging.INFO, logger="kernel.embrion_scheduler"):
        await scheduler._restore_from_supabase()

    # Buscar el log estructurado de overdue
    overdue_logs = [
        rec for rec in caplog.records
        if rec.name == "kernel.embrion_scheduler"
        and (
            "scheduler_task_overdue_at_restore" in (rec.getMessage() or "")
            or getattr(rec, "event", "") == "scheduler_task_overdue_at_restore"
        )
    ]
    assert len(overdue_logs) >= 1, (
        f"FALLO Sprint D-5: NO se logueo scheduler_task_overdue_at_restore.\n"
        f"  Logs capturados (kernel.embrion_scheduler): "
        f"{[r.getMessage() for r in caplog.records if r.name == 'kernel.embrion_scheduler']}"
    )

    # Verificar que seconds_overdue es razonable (>= 27h * 3600 = 97_200s, con margen)
    expected_seconds = int(hours_overdue * 3600)
    rec = overdue_logs[0]
    seconds_in_record = getattr(rec, "seconds_overdue", None)
    if seconds_in_record is None:
        # structlog puede serializar todo en el mensaje; buscar substring
        msg = rec.getMessage()
        assert "seconds_overdue" in msg, f"seconds_overdue ausente del log: {msg}"
    else:
        # Margen de tolerancia 60s por overhead de test
        assert abs(seconds_in_record - expected_seconds) < 60, (
            f"seconds_overdue impreciso: esperado~{expected_seconds}, recibido {seconds_in_record}"
        )


# ── Test 4 (regresion D-2/D-3): tasks no vencidas NO se tocan ────────────────


@pytest.mark.asyncio
async def test_restore_does_not_modify_future_next_run():
    """Tasks con next_run en futuro NO deben modificarse durante restore."""
    future_iso = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    row = {
        "task_id": "22222222-2222-2222-2222-222222222222",
        "name": "system_health_check",
        "description": "test future task",
        "embrion_id": "embrion-0",
        "schedule_type": "periodic",
        "interval_hours": 2.0,
        "daily_hour": 3,
        "max_cost_usd": 0.10,
        "max_retries": 3,
        "consecutive_failures": 0,
        "paused": False,
        "status": "active",
        "last_run": _now_utc_iso(),
        "next_run": future_iso,
        "total_runs": 5,
        "total_cost_usd": 0.0,
        "handler": "h_health",
        "handler_args": {},
    }
    db = MagicMock()
    db.select = AsyncMock(return_value=[row])
    db.upsert = AsyncMock()

    scheduler = EmbrionScheduler(db=db)
    await scheduler._restore_from_supabase()

    task = next(iter(scheduler._tasks.values()))
    assert task.next_run == future_iso, (
        f"REGRESION: next_run en futuro fue modificado.\n"
        f"  esperado: {future_iso}\n"
        f"  recibido: {task.next_run}"
    )
