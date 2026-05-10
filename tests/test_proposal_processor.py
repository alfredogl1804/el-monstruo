"""Tests para Sprint EMBRION-NEEDS-002 — proposal_processor + executor_registry.

Cubre:
  - executor_registry: dispatch, noop default, opt-in real, fallback
  - executors: db_write, external_api_call, code_commit (deferred)
  - proposal_processor: expire_loop, execute_loop, notify post-execute
  - Resilience: errores transitorios no rompen el worker
"""
from __future__ import annotations

import asyncio
import os
from typing import Any
from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from kernel.embrion_write_policy import ExecutionResult
from kernel.runner.executor_registry import (
    ExecutorRegistry,
    _exec_code_commit,
    _exec_db_write,
    _exec_external_api_call,
    _exec_noop,
    _is_real,
)
from kernel.runner.proposal_processor import (
    _format_execution_message,
    _notify_post_execute,
    execute_loop,
    expire_loop,
)


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------
def make_proposal(
    *,
    proposal_id: str = "11111111-1111-1111-1111-111111111111",
    proposal_type: str = "other",
    payload: dict | None = None,
    approval_status: str = "approved",
) -> dict:
    return {
        "id": proposal_id,
        "proposal_type": proposal_type,
        "approval_status": approval_status,
        "payload_json": payload or {},
        "result_json": None,
    }


# -----------------------------------------------------------------------------
# 1. ExecutorRegistry — defaults y dispatch
# -----------------------------------------------------------------------------
def test_registry_default_types_registered():
    """Registry tiene los 4 types: code_commit, db_write, external_api_call, other."""
    reg = ExecutorRegistry()
    assert set(reg._executors.keys()) == {"code_commit", "db_write", "external_api_call", "other"}


def test_registry_dispatch_other_returns_noop_success():
    """proposal_type='other' → noop success."""
    reg = ExecutorRegistry()
    result = reg.dispatch(make_proposal(proposal_type="other"))
    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.result["noop"] is True


def test_registry_unknown_type_falls_back_to_noop():
    """proposal_type desconocido → noop fallback (no excepción)."""
    reg = ExecutorRegistry()
    result = reg.dispatch(make_proposal(proposal_type="nonexistent_type"))
    assert result.success is True
    assert result.result["noop"] is True


def test_registry_dispatch_unhandled_exception_returns_failed():
    """Si executor lanza excepción inesperada, dispatch retorna failed (no propaga)."""
    def buggy_executor(p):
        raise RuntimeError("boom")

    reg = ExecutorRegistry()
    reg.register("test", buggy_executor)
    result = reg.dispatch(make_proposal(proposal_type="test"))
    assert result.success is False
    assert "RuntimeError: boom" in result.error


def test_registry_register_overrides_existing():
    """register() puede reemplazar un executor existente."""
    reg = ExecutorRegistry()

    def custom(p):
        return ExecutionResult(proposal_id=str(p["id"]), success=True, result={"custom": True})

    reg.register("other", custom)
    result = reg.dispatch(make_proposal(proposal_type="other"))
    assert result.result == {"custom": True}


# -----------------------------------------------------------------------------
# 2. _is_real opt-in
# -----------------------------------------------------------------------------
def test_is_real_default_false():
    assert _is_real(make_proposal()) is False


def test_is_real_with_executor_real_true():
    assert _is_real(make_proposal(payload={"executor": "real"})) is True


def test_is_real_with_invalid_payload_false():
    """Si payload_json no es dict, retorna False sin crashear."""
    assert _is_real({"id": "x", "payload_json": None}) is False
    assert _is_real({"id": "x", "payload_json": "not a dict"}) is False


# -----------------------------------------------------------------------------
# 3. external_api_call executor
# -----------------------------------------------------------------------------
def test_external_api_noop_when_not_real():
    """Sin executor='real', external_api_call retorna noop."""
    result = _exec_external_api_call(make_proposal(
        proposal_type="external_api_call",
        payload={"url": "https://example.com"},
    ))
    assert result.success is True
    assert result.result["noop"] is True


def test_external_api_missing_url_fails():
    result = _exec_external_api_call(make_proposal(
        proposal_type="external_api_call",
        payload={"executor": "real"},
    ))
    assert result.success is False
    assert "missing payload.url" in result.error


def test_external_api_http_200_success():
    """HTTP 200 → success con status_code en result."""
    proposal = make_proposal(
        proposal_type="external_api_call",
        payload={"executor": "real", "method": "GET", "url": "https://example.com"},
    )
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "ok"

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=None)
    mock_client.request = MagicMock(return_value=mock_response)

    with patch("kernel.runner.executor_registry.httpx.Client", return_value=mock_client):
        result = _exec_external_api_call(proposal)

    assert result.success is True
    assert result.result["status_code"] == 200


def test_external_api_http_500_marks_failed():
    """HTTP 500 → success=False con status_code 500."""
    proposal = make_proposal(
        proposal_type="external_api_call",
        payload={"executor": "real", "method": "POST", "url": "https://example.com"},
    )
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "internal error"

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=None)
    mock_client.request = MagicMock(return_value=mock_response)

    with patch("kernel.runner.executor_registry.httpx.Client", return_value=mock_client):
        result = _exec_external_api_call(proposal)

    assert result.success is False
    assert "HTTP 500" in result.error


# -----------------------------------------------------------------------------
# 4. db_write executor
# -----------------------------------------------------------------------------
def test_db_write_noop_when_not_real():
    """Sin executor='real', db_write es noop (CRÍTICO: protección por defecto)."""
    result = _exec_db_write(make_proposal(
        proposal_type="db_write",
        payload={"sql": "DELETE FROM users"},  # peligroso, pero noop sin opt-in
    ))
    assert result.success is True
    assert result.result["noop"] is True


def test_db_write_missing_sql_fails():
    result = _exec_db_write(make_proposal(
        proposal_type="db_write",
        payload={"executor": "real"},
    ))
    assert result.success is False
    assert "missing or invalid payload.sql" in result.error


def test_db_write_no_db_url_fails():
    """Si SUPABASE_DB_URL/DATABASE_URL no está, falla con error claro."""
    with patch.dict(os.environ, {}, clear=False):
        # Limpiar las dos vars
        for var in ("SUPABASE_DB_URL", "DATABASE_URL"):
            os.environ.pop(var, None)
        result = _exec_db_write(make_proposal(
            proposal_type="db_write",
            payload={"executor": "real", "sql": "SELECT 1"},
        ))
    assert result.success is False
    assert "DB_URL" in result.error or "DATABASE_URL" in result.error


# -----------------------------------------------------------------------------
# 5. code_commit deferred
# -----------------------------------------------------------------------------
def test_code_commit_always_noop_for_now():
    """code_commit es noop hasta Sprint futuro (incluso con executor=real)."""
    result = _exec_code_commit(make_proposal(
        proposal_type="code_commit",
        payload={"executor": "real"},
    ))
    assert result.success is True
    assert result.result["noop"] is True
    assert "diferido" in result.result["reason"].lower()
    assert "deferred_to_sprint" in result.result


# -----------------------------------------------------------------------------
# 6. _format_execution_message
# -----------------------------------------------------------------------------
def test_format_message_executed_success():
    proposal = {
        "id": "abc-123",
        "proposal_type": "other",
        "approval_status": "executed",
        "result_json": {"duration_ms": 42, "result": {"ok": True}},
    }
    msg = _format_execution_message(proposal)
    assert "✅" in msg
    assert "executed" in msg
    assert "abc-123" in msg
    assert "42ms" in msg


def test_format_message_failed_includes_error():
    proposal = {
        "id": "abc-456",
        "proposal_type": "external_api_call",
        "approval_status": "failed",
        "result_json": {"duration_ms": 10, "error": "HTTP 500", "result": None},
    }
    msg = _format_execution_message(proposal)
    assert "❌" in msg
    assert "failed" in msg
    assert "HTTP 500" in msg


# -----------------------------------------------------------------------------
# 7. _notify_post_execute (best-effort, no rompe el loop)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_notify_post_execute_telegram_disabled_does_not_fail():
    """Si TelegramNotifier.enabled=False, no debe llamar a send_message ni fallar."""
    db_client = MagicMock()
    db_client.insert = MagicMock(return_value=None)
    notifier = MagicMock()
    notifier.enabled = False  # disabled
    notifier.send_message = AsyncMock()

    proposal = {
        "id": "abc-789",
        "proposal_type": "other",
        "approval_status": "executed",
        "result_json": {"duration_ms": 1, "result": {"ok": True}},
    }

    # NOTIFY_ENABLED por default es true
    await _notify_post_execute(db_client, notifier, proposal)

    notifier.send_message.assert_not_called()
    # cowork_bridge SÍ debe haberse llamado
    db_client.insert.assert_called_once()


@pytest.mark.asyncio
async def test_notify_post_execute_telegram_failure_does_not_break():
    """Si Telegram lanza excepción, cowork_bridge igual recibe el log."""
    db_client = MagicMock()
    db_client.insert = MagicMock(return_value=None)
    notifier = MagicMock()
    notifier.enabled = True
    notifier.send_message = AsyncMock(side_effect=RuntimeError("network down"))

    proposal = {
        "id": "abc-aaa",
        "proposal_type": "other",
        "approval_status": "executed",
        "result_json": {"duration_ms": 1, "result": {}},
    }

    # No debe propagar la excepción
    await _notify_post_execute(db_client, notifier, proposal)

    db_client.insert.assert_called_once()


# -----------------------------------------------------------------------------
# 8. expire_loop / execute_loop — resilience
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_expire_loop_stops_on_event():
    """expire_loop termina cuando se setea stop_event."""
    db_client = MagicMock()
    stop_event = asyncio.Event()

    with patch("kernel.runner.proposal_processor.expire_old", return_value=0), \
         patch("kernel.runner.proposal_processor.EXPIRE_INTERVAL_SEC", 0.01):
        task = asyncio.create_task(expire_loop(db_client, stop_event))
        await asyncio.sleep(0.05)
        stop_event.set()
        await asyncio.wait_for(task, timeout=1.0)

    assert task.done()


@pytest.mark.asyncio
async def test_expire_loop_swallows_errors():
    """Si expire_old falla, el loop loguea pero no se rompe."""
    db_client = MagicMock()
    stop_event = asyncio.Event()
    call_count = {"n": 0}

    def buggy(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise RuntimeError("transient error")
        return 0

    with patch("kernel.runner.proposal_processor.expire_old", side_effect=buggy), \
         patch("kernel.runner.proposal_processor.EXPIRE_INTERVAL_SEC", 0.001):
        task = asyncio.create_task(expire_loop(db_client, stop_event))
        # Ceder control suficientes veces para garantizar >=2 iteraciones
        for _ in range(20):
            await asyncio.sleep(0.01)
            if call_count["n"] >= 2:
                break
        stop_event.set()
        await asyncio.wait_for(task, timeout=1.0)

    # El loop NO debe haber muerto por la excepción transitoria
    assert task.done()
    assert task.exception() is None, f"loop crashed: {task.exception()}"
    # CRITICAL: el loop debe haber sobrevivido al RuntimeError y seguir ejecutando
    assert call_count["n"] >= 2, (
        f"expected loop to swallow error and re-run, got call_count={call_count['n']}"
    )


@pytest.mark.asyncio
async def test_execute_loop_calls_notify_when_executed():
    """Cuando execute_next retorna proposal, execute_loop llama notify."""
    db_client = MagicMock()
    db_client.insert = MagicMock(return_value=None)
    registry = MagicMock()
    notifier = MagicMock()
    notifier.enabled = False  # silencia telegram
    stop_event = asyncio.Event()

    executed = {
        "id": "exec-xxx",
        "proposal_type": "other",
        "approval_status": "executed",
        "result_json": {"duration_ms": 1, "result": {}},
    }
    call_count = {"n": 0}

    def fake_execute_next(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return executed
        return None  # subsequent calls return None

    with patch("kernel.runner.proposal_processor.execute_next", side_effect=fake_execute_next), \
         patch("kernel.runner.proposal_processor.EXECUTE_INTERVAL_SEC", 0.01):
        task = asyncio.create_task(
            execute_loop(db_client, registry, notifier, stop_event)
        )
        await asyncio.sleep(0.05)
        stop_event.set()
        await asyncio.wait_for(task, timeout=1.0)

    # cowork_bridge insert debe haberse llamado al menos 1 vez (notify post-execute)
    assert db_client.insert.called
