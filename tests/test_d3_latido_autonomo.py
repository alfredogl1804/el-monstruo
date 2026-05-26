"""
Sprint D-3 (2026-05-11) — Hilo Ejecutor 2.

Tests para el sistema de latido autónomo proactivo:
  - `EmbrionLoop.trigger_reflexion_autonoma()` (entry-point público)
  - Singleton accessors `set_embrion_loop_singleton` / `get_embrion_loop_singleton`
  - `_handler_latido_autonomo` del scheduler
  - Extensión `_stub_handler_health_check` alerta latido stale > 12h
  - `register_default_tasks` incluye `latido_autonomo` con interval 6h
"""

from __future__ import annotations

import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from kernel.embrion_loop import (
    EmbrionLoop,
    get_embrion_loop_singleton,
    set_embrion_loop_singleton,
)
from kernel.embrion_scheduler import (
    EmbrionScheduler,
    _handler_latido_autonomo,
    _stub_handler_health_check,
    register_default_tasks,
)

# ── 1. EmbrionLoop.trigger_reflexion_autonoma ────────────────────────────────


@pytest.mark.asyncio
async def test_trigger_reflexion_autonoma_running_loop():
    """trigger_reflexion_autonoma() con loop running dispara _think con trigger correcto."""
    db_mock = MagicMock()
    kernel_mock = MagicMock()
    loop = EmbrionLoop(db=db_mock, kernel=kernel_mock, notifier=None)
    loop._running = True
    loop._cycle_count = 7

    # Mock _think para no ejecutar el pipeline completo
    fake_think_result = {"content": "ok-test-response", "tokens": 10}
    loop._think = AsyncMock(return_value=fake_think_result)

    result = await loop.trigger_reflexion_autonoma(source="scheduler", cycle_id="exec-abc-123")

    assert result["triggered"] is True
    assert result["source"] == "scheduler"
    assert result["cycle_id"] == "exec-abc-123"
    assert result["internal_cycle"] == 7
    assert result["result_chars"] == len("ok-test-response")

    # Verificar trigger dispatchado
    loop._think.assert_awaited_once()
    call_arg = loop._think.await_args.args[0]
    assert call_arg["type"] == "reflexion_autonoma"
    assert "latido_autonomo source=scheduler" in call_arg["detail"]
    assert "exec-abc-123" in call_arg["detail"]
    assert call_arg["priority"] == 3
    assert call_arg["source"] == "scheduler"
    assert call_arg["scheduler_cycle_id"] == "exec-abc-123"


@pytest.mark.asyncio
async def test_trigger_reflexion_autonoma_skips_when_not_running():
    """Si el loop no está running, retorna triggered=False sin tocar _think."""
    db_mock = MagicMock()
    kernel_mock = MagicMock()
    loop = EmbrionLoop(db=db_mock, kernel=kernel_mock, notifier=None)
    loop._running = False
    loop._think = AsyncMock()  # no debe ser llamado

    result = await loop.trigger_reflexion_autonoma(source="manual", cycle_id="test-skip")

    assert result["triggered"] is False
    assert result["reason"] == "embrion_loop_not_running"
    assert result["source"] == "manual"
    assert result["cycle_id"] == "test-skip"
    loop._think.assert_not_called()


@pytest.mark.asyncio
async def test_trigger_reflexion_autonoma_handles_think_exception():
    """Si _think levanta excepción, captura y retorna triggered=False con error."""
    db_mock = MagicMock()
    kernel_mock = MagicMock()
    loop = EmbrionLoop(db=db_mock, kernel=kernel_mock, notifier=None)
    loop._running = True
    loop._think = AsyncMock(side_effect=ValueError("boom-test"))

    result = await loop.trigger_reflexion_autonoma(source="scheduler", cycle_id="x")

    assert result["triggered"] is False
    assert result["reason"] == "exception:ValueError"
    assert "boom-test" in result["error"]


# ── 2. Singleton accessors ───────────────────────────────────────────────────


def test_singleton_set_and_get():
    """set_embrion_loop_singleton + get_embrion_loop_singleton funcionan."""
    db_mock = MagicMock()
    kernel_mock = MagicMock()
    loop = EmbrionLoop(db=db_mock, kernel=kernel_mock, notifier=None)

    set_embrion_loop_singleton(loop)
    got = get_embrion_loop_singleton()

    assert got is loop


def test_singleton_overwritable():
    """La última llamada a set_embrion_loop_singleton gana (útil para tests)."""
    db_mock = MagicMock()
    kernel_mock = MagicMock()
    loop_a = EmbrionLoop(db=db_mock, kernel=kernel_mock, notifier=None)
    loop_b = EmbrionLoop(db=db_mock, kernel=kernel_mock, notifier=None)

    set_embrion_loop_singleton(loop_a)
    set_embrion_loop_singleton(loop_b)
    assert get_embrion_loop_singleton() is loop_b


# ── 3. _handler_latido_autonomo del scheduler ────────────────────────────────


@pytest.mark.asyncio
async def test_handler_latido_autonomo_invokes_singleton():
    """Handler obtiene singleton y llama trigger_reflexion_autonoma."""
    db_mock = MagicMock()
    kernel_mock = MagicMock()
    loop = EmbrionLoop(db=db_mock, kernel=kernel_mock, notifier=None)
    loop._running = True
    loop.trigger_reflexion_autonoma = AsyncMock(return_value={"triggered": True, "result_chars": 42, "reason": None})

    set_embrion_loop_singleton(loop)
    os.environ.pop("EMBRION_LATIDO_AUTONOMO_ENABLED", None)

    await _handler_latido_autonomo(task_id="exec-test-1", task_name="latido_autonomo")

    loop.trigger_reflexion_autonoma.assert_awaited_once()
    call_kwargs = loop.trigger_reflexion_autonoma.await_args.kwargs
    assert call_kwargs["source"] == "scheduler"
    assert call_kwargs["cycle_id"] == "exec-test-1"


@pytest.mark.asyncio
async def test_handler_latido_autonomo_respects_env_disabled():
    """Si EMBRION_LATIDO_AUTONOMO_ENABLED=false, handler skip sin tocar singleton."""
    db_mock = MagicMock()
    kernel_mock = MagicMock()
    loop = EmbrionLoop(db=db_mock, kernel=kernel_mock, notifier=None)
    loop.trigger_reflexion_autonoma = AsyncMock()
    set_embrion_loop_singleton(loop)

    with patch.dict(os.environ, {"EMBRION_LATIDO_AUTONOMO_ENABLED": "false"}):
        await _handler_latido_autonomo(task_id="exec-skip", task_name="latido_autonomo")

    loop.trigger_reflexion_autonoma.assert_not_called()


@pytest.mark.asyncio
async def test_handler_latido_autonomo_no_singleton_graceful():
    """Si singleton no está registrado, handler no propaga excepción."""
    set_embrion_loop_singleton(None)  # explícito
    os.environ.pop("EMBRION_LATIDO_AUTONOMO_ENABLED", None)

    # No debe levantar
    await _handler_latido_autonomo(task_id="exec-no-singleton")


# ── 4. Health check con alerta latido stale > 12h ────────────────────────────


@pytest.mark.asyncio
async def test_health_check_alerts_on_stale_latido():
    """Si último latido > 12h, dispara notificación Telegram via notifier."""
    db_mock = MagicMock()
    kernel_mock = MagicMock()
    notifier_mock = MagicMock()
    notifier_mock.send_message = AsyncMock()
    loop = EmbrionLoop(db=db_mock, kernel=kernel_mock, notifier=notifier_mock)
    # 13 horas atrás
    loop._last_thought_at = time.time() - (13 * 3600)
    set_embrion_loop_singleton(loop)

    await _stub_handler_health_check()

    notifier_mock.send_message.assert_awaited_once()
    call_kwargs = notifier_mock.send_message.await_args.kwargs
    assert "Latido Stale" in call_kwargs["text"]
    assert "13.0h" in call_kwargs["text"]


@pytest.mark.asyncio
async def test_health_check_no_alert_if_recent():
    """Si último latido reciente (< 12h), no envía alerta."""
    db_mock = MagicMock()
    kernel_mock = MagicMock()
    notifier_mock = MagicMock()
    notifier_mock.send_message = AsyncMock()
    loop = EmbrionLoop(db=db_mock, kernel=kernel_mock, notifier=notifier_mock)
    loop._last_thought_at = time.time() - (3 * 3600)  # 3h atrás
    set_embrion_loop_singleton(loop)

    await _stub_handler_health_check()

    notifier_mock.send_message.assert_not_called()


# ── 5. register_default_tasks incluye latido_autonomo ────────────────────────


def test_register_default_tasks_includes_latido_autonomo():
    """register_default_tasks añade la 6ta task latido_autonomo correctamente."""
    db_mock = MagicMock()
    scheduler = EmbrionScheduler(db=db_mock)
    register_default_tasks(scheduler)

    task_names = [t.name for t in scheduler._tasks.values()]
    assert "latido_autonomo" in task_names

    latido = next(t for t in scheduler._tasks.values() if t.name == "latido_autonomo")
    assert latido.schedule_type == "periodic"
    assert latido.interval_hours == 6.0
    assert latido.max_cost_usd == 0.30
    assert latido.handler == "run_latido_autonomo"
    assert latido.embrion_id == "embrion-0"
