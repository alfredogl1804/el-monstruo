"""Test unitario del guard idempotente en EmbrionScheduler.add_task.

Sprint D-2 (Hilo Ejecutor 2). Valida que llamar add_task dos veces con la misma
combinacion (name, embrion_id) NO crea una segunda entrada en self._tasks y
que preserva el task_id original.
"""
import os
import sys
from pathlib import Path

# Ensure project root is in path (patrón estándar del repo)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.embrion_scheduler import EmbrionScheduler, ScheduledTask


def test_idempotency():
    scheduler = EmbrionScheduler(db=None)

    # 1ra adicion — limpia
    t1 = ScheduledTask(
        name="causal_seeding",
        embrion_id="embrion-causal",
        schedule_type="periodic",
        interval_hours=6.0,
        handler="run_causal_seeding_cycle",
    )
    scheduler.add_task(t1)
    original_task_id = t1.task_id
    assert len(scheduler._tasks) == 1, f"expected 1 task, got {len(scheduler._tasks)}"

    # Simular que la 1ra tiene historial de ejecucion
    scheduler._tasks[original_task_id].last_run = "2026-05-11T20:00:00+00:00"
    scheduler._tasks[original_task_id].total_runs = 42
    scheduler._tasks[original_task_id].total_cost_usd = 3.50

    # 2da adicion con MISMO (name, embrion_id) pero distinta config — simula restart
    t2 = ScheduledTask(
        name="causal_seeding",
        embrion_id="embrion-causal",
        schedule_type="periodic",
        interval_hours=12.0,  # CAMBIO de schedule
        handler="run_causal_seeding_cycle",
    )
    scheduler.add_task(t2)

    # ASSERT 1: solo hay 1 tarea (no se duplicó)
    assert len(scheduler._tasks) == 1, f"DUPLICATION BUG: expected 1 task, got {len(scheduler._tasks)}"

    # ASSERT 2: el task_id se reusó (no se creó nuevo)
    assert t2.task_id == original_task_id, f"task_id no reusado: {t2.task_id} != {original_task_id}"

    # ASSERT 3: estado de ejecución preservado
    final = scheduler._tasks[original_task_id]
    assert final.last_run == "2026-05-11T20:00:00+00:00", "last_run no preservado"
    assert final.total_runs == 42, f"total_runs no preservado: {final.total_runs}"
    assert final.total_cost_usd == 3.50, f"total_cost_usd no preservado: {final.total_cost_usd}"

    # ASSERT 4: definicion se refrescó (interval_hours nuevo)
    assert final.interval_hours == 12.0, f"interval_hours no refrescado: {final.interval_hours}"

    print("OK: add_task es idempotente por (name, embrion_id)")
    print(f"  - tasks count: {len(scheduler._tasks)} (esperado 1)")
    print(f"  - task_id reusado: {original_task_id}")
    print(f"  - last_run preservado: {final.last_run}")
    print(f"  - total_runs preservado: {final.total_runs}")
    print(f"  - interval_hours refrescado: {final.interval_hours}")


def test_different_embrion_ids_not_collapsed():
    """Tareas con mismo name pero distinto embrion_id NO deben colapsarse."""
    scheduler = EmbrionScheduler(db=None)
    t1 = ScheduledTask(name="health_check", embrion_id="embrion-0")
    t2 = ScheduledTask(name="health_check", embrion_id="embrion-causal")
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    assert len(scheduler._tasks) == 2, f"FALSE-POSITIVE: collapsed across embrions, got {len(scheduler._tasks)}"
    assert t1.task_id != t2.task_id
    print("OK: tareas con distinto embrion_id no colapsan")


def test_register_default_tasks_double_call():
    """register_default_tasks llamado 2 veces (simula restart) NO duplica."""
    from kernel.embrion_scheduler import register_default_tasks
    scheduler = EmbrionScheduler(db=None)

    register_default_tasks(scheduler)
    count_after_first = len(scheduler._tasks)
    # Sprint D-3 (2026-05-11) agregó latido_autonomo → 6 tasks.
    # Sprint GUARDIAN-AUTONOMO-001 (2026-05-12) agregó daily_guardian_audit → 7 tasks default.
    assert count_after_first == 7, f"primera corrida: esperado 7 tasks, got {count_after_first}"

    # Simula restart del kernel (sin _restore_from_supabase porque no hay DB)
    register_default_tasks(scheduler)
    count_after_second = len(scheduler._tasks)
    assert count_after_second == 7, f"BUG: segunda corrida creó duplicados, got {count_after_second}"

    print(f"OK: register_default_tasks llamado 2x -> {count_after_second} tasks (no duplicación)")


if __name__ == "__main__":
    test_idempotency()
    test_different_embrion_ids_not_collapsed()
    test_register_default_tasks_double_call()
    print()
    print("=== TODOS LOS TESTS PASARON ===")
