"""Test del fix Sprint D-4 (2026-05-12 Hilo Ejecutor 1).

Verifica que `_persist_task` invoca `db.upsert` con
``on_conflict='name,embrion_id'`` para que el UPSERT use el UNIQUE constraint
``scheduled_tasks_name_embrion_unique`` (creado por migration 0019, Sprint D-2,
DSC-S-013) como conflict target en lugar de la PK ``id``.

Sin este parametro, las re-ejecuciones de ``add_task`` post-restore generan
un INSERT que viola el UNIQUE constraint con Postgres error 23505 y deja a
las tasks zombie con ``next_run`` antiguo en DB y ``next_run`` futuro en
memoria que el loop nunca dispara antes del proximo redeploy.

Bug original observado:
- Logs Railway 2026-05-12 02:55:44 UTC: 6x ``supabase_upsert_failed`` con
  ``duplicate key value violates unique constraint
  "scheduled_tasks_name_embrion_unique"``.
- 3 tasks zombie con ``total_runs=1`` y ``last_run`` de hace 1-6 dias:
  ``causal_seeding`` (last_run 11-may), ``vanguard_scan`` (9-may),
  ``prediction_validation`` (6-may).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from kernel.embrion_scheduler import EmbrionScheduler, ScheduledTask


@pytest.mark.asyncio
async def test_persist_task_uses_on_conflict_name_embrion():
    """`_persist_task` debe pasar ``on_conflict='name,embrion_id'`` al cliente DB.

    Esto fuerza al cliente Supabase a usar el UNIQUE constraint
    ``scheduled_tasks_name_embrion_unique`` como conflict target, evitando
    el error 23505 cuando el ``task_id`` reusado por el guard idempotente
    (DSC-S-013) no coincide con el ``id`` ya existente en DB para la misma
    combinacion ``(name, embrion_id)``.
    """
    db_mock = MagicMock()
    db_mock.upsert = AsyncMock(return_value={"id": "stub"})

    scheduler = EmbrionScheduler(db=db_mock)
    task = ScheduledTask(
        name="latido_autonomo",
        description="test",
        embrion_id="embrion-0",
        schedule_type="periodic",
        interval_hours=6.0,
        max_cost_usd=0.30,
        handler="run_latido_autonomo",
    )

    await scheduler._persist_task(task)

    assert db_mock.upsert.await_count == 1, "upsert debe invocarse exactamente 1x"
    args, kwargs = db_mock.upsert.await_args

    # Posicional: (table, row); on_conflict puede venir como kw o posicional
    assert args[0] == "scheduled_tasks", "tabla destino incorrecta"

    on_conflict_value = kwargs.get("on_conflict")
    if on_conflict_value is None and len(args) >= 3:
        on_conflict_value = args[2]

    assert on_conflict_value == "name,embrion_id", (
        f"_persist_task debe pasar on_conflict='name,embrion_id' "
        f"para usar el UNIQUE constraint scheduled_tasks_name_embrion_unique. "
        f"Recibido: on_conflict={on_conflict_value!r}"
    )


@pytest.mark.asyncio
async def test_persist_task_no_op_if_db_none():
    """Si `_db is None`, `_persist_task` no debe levantar — modo degraded."""
    scheduler = EmbrionScheduler(db=None)
    task = ScheduledTask(
        name="x",
        description="t",
        embrion_id="e0",
        schedule_type="periodic",
        interval_hours=1.0,
        max_cost_usd=0.01,
        handler="h",
    )
    # No assertion — solo que no levante
    await scheduler._persist_task(task)


@pytest.mark.asyncio
async def test_persist_task_swallows_db_errors():
    """Si `db.upsert` levanta (p.ej. timeout), el caller no debe romperse.

    El warning `scheduler_persist_failed` se loguea pero no propaga, para no
    matar el scheduler loop en errores transitorios de DB.
    """
    db_mock = MagicMock()
    db_mock.upsert = AsyncMock(side_effect=Exception("simulated db timeout"))

    scheduler = EmbrionScheduler(db=db_mock)
    task = ScheduledTask(
        name="latido_autonomo",
        description="test",
        embrion_id="embrion-0",
        schedule_type="periodic",
        interval_hours=6.0,
        max_cost_usd=0.30,
        handler="run_latido_autonomo",
    )

    # No debe levantar
    await scheduler._persist_task(task)

    assert db_mock.upsert.await_count == 1


@pytest.mark.asyncio
async def test_persist_task_row_includes_handler_args_json():
    """El row enviado a upsert debe contener ``handler_args`` como JSON string."""
    db_mock = MagicMock()
    db_mock.upsert = AsyncMock(return_value={"id": "stub"})

    scheduler = EmbrionScheduler(db=db_mock)
    task = ScheduledTask(
        name="x",
        description="t",
        embrion_id="e0",
        schedule_type="periodic",
        interval_hours=1.0,
        max_cost_usd=0.01,
        handler="h",
        handler_args={"key": "value", "num": 42},
    )

    await scheduler._persist_task(task)

    args, kwargs = db_mock.upsert.await_args
    row = args[1]
    assert isinstance(row["handler_args"], str), "handler_args debe ser JSON serializado"
    assert "key" in row["handler_args"]
    assert "value" in row["handler_args"]

    # No debe haber 'task_id' en row — solo 'id'
    assert "task_id" not in row, "task_id debe ser renombrado a id"
    assert row["id"] == task.task_id
