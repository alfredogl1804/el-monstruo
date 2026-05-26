"""
tests/test_embrion_loop_inbox_integration.py — Tests CA5+CA6+CA7-stub.

Sprint EMBRION-NEEDS-002 Tarea 5.
Verifica que la integración del inbox en `embrion_loop._detect_trigger` y
`_check_and_think` funciona sin alucinar:
  - inbox row pending → trigger tipo "inbox_command" prioridad 9
  - mensaje_alfredo (10) sigue ganando contra inbox (9)
  - comando alto-riesgo /override → requires_mfa stub, NO ejecuta
  - mark_processed se llama al cierre del ciclo
  - excepción del inbox NO bloquea el resto de triggers
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ─── Fixture: cargar embrion_loop con stubs mínimos ─────────────────────


@pytest.fixture
def loop_module():
    """Importar el módulo embrion_loop después de mockear deps pesadas."""
    import kernel.embrion_loop as mod

    return mod


@pytest.fixture
def mock_db():
    """DB stub: select() async que devuelve listas vacías por default."""
    db = MagicMock()
    db.connected = True
    db.select = AsyncMock(return_value=[])
    return db


@pytest.fixture
def loop_instance(loop_module, mock_db):
    """Instancia del loop con DB stubeado."""
    EmbrionLoop = loop_module.EmbrionLoop
    inst = EmbrionLoop.__new__(EmbrionLoop)
    inst._db = mock_db
    inst._kernel = MagicMock()
    inst._cycle_count = 1
    inst._last_thought_at = None
    inst._thoughts_today = 0
    inst._cost_today_usd = 0.0
    inst._messages_sent_today = 0
    inst._silenced_thoughts = []
    inst._last_trigger = None
    inst._last_result = None
    inst._judge_consecutive_failures = 0
    inst._judge_circuit_open = False
    inst._last_judge_failure_at = 0
    return inst


# ═══════════════════════════════════════════════════════════════════════
# Tests de _detect_trigger
# ═══════════════════════════════════════════════════════════════════════


# ─── 1) Si NO hay mensaje_alfredo y SÍ hay inbox row → trigger inbox ────
@pytest.mark.asyncio
async def test_inbox_row_becomes_trigger_priority_9(loop_instance):
    """Sin mensaje_alfredo, un row pending del inbox se convierte en trigger."""
    inbox_row = {
        "id": "abc-123",
        "tipo_comando": "/help",
        "intent_class": "safe",
        "chat_id_origen": "12345",
        "raw_text": "/help",
        "sanitized_payload": "/help",
    }
    with (
        patch("kernel.embrion_inbox.consume_next", return_value=[inbox_row]),
        patch("kernel.embrion_inbox._get_supabase_client", return_value=object()),
    ):
        trigger = await loop_instance._detect_trigger()

    assert trigger is not None
    assert trigger["type"] == "inbox_command"
    assert trigger["priority"] == 9
    assert trigger["inbox_id"] == "abc-123"
    assert trigger["command_type"] == "/help"
    assert trigger["requires_mfa"] is False  # /help no es alto-riesgo


# ─── 2) Comando /override → requires_mfa=True ──────────────────────────
@pytest.mark.asyncio
async def test_inbox_override_marks_requires_mfa(loop_instance):
    inbox_row = {
        "id": "abc-456",
        "tipo_comando": "/override",
        "intent_class": "safe",
        "chat_id_origen": "12345",
        "raw_text": "/override hash=xxx",
        "sanitized_payload": "/override hash=xxx",
    }
    with (
        patch("kernel.embrion_inbox.consume_next", return_value=[inbox_row]),
        patch("kernel.embrion_inbox._get_supabase_client", return_value=object()),
    ):
        trigger = await loop_instance._detect_trigger()

    assert trigger["requires_mfa"] is True
    assert trigger["command_type"] == "/override"


# ─── 3) Mensaje_alfredo (priority 10) gana contra inbox (priority 9) ────
@pytest.mark.asyncio
async def test_alfredo_message_beats_inbox(loop_instance, mock_db):
    """Si hay tanto mensaje_alfredo NUEVO como inbox_row, gana mensaje_alfredo."""
    mock_db.select = AsyncMock(
        side_effect=[
            # 1ra llamada: mensajes (mensaje_alfredo)
            [{"id": "msg-1", "contenido": "Test directiva", "created_at": "2026-05-11T20:00:00Z"}],
            # 2da llamada: respuestas (vacío → no hemos respondido)
            [],
        ]
    )
    inbox_row = {
        "id": "abc-789",
        "tipo_comando": "/help",
        "raw_text": "/help",
        "sanitized_payload": "/help",
    }
    with (
        patch("kernel.embrion_inbox.consume_next", return_value=[inbox_row]),
        patch("kernel.embrion_inbox._get_supabase_client", return_value=object()),
    ):
        trigger = await loop_instance._detect_trigger()

    # Debe ganar mensaje_alfredo (priority 10), NO el inbox
    assert trigger["type"] == "mensaje_alfredo"
    assert trigger["priority"] == 10


# ─── 4) Excepción del inbox NO bloquea el resto de triggers ─────────────
@pytest.mark.asyncio
async def test_inbox_exception_does_not_block_other_triggers(loop_instance, mock_db):
    """Si consume_next() lanza, el flujo continúa a Sabios y reflexión."""
    # Mock contribuciones vacías y reflexion = trigger
    mock_db.select = AsyncMock(
        side_effect=[
            [],  # mensajes
            [],  # contribuciones (paso 2)
        ]
    )
    loop_instance._last_thought_at = None  # forzar trigger reflexion (paso 3)

    with (
        patch("kernel.embrion_inbox.consume_next", side_effect=RuntimeError("boom")),
        patch("kernel.embrion_inbox._get_supabase_client", return_value=object()),
    ):
        trigger = await loop_instance._detect_trigger()

    # Debe caer al trigger de reflexión autónoma (priority 3)
    assert trigger is not None
    assert trigger["type"] == "reflexion_autonoma"


# ─── 5) Inbox vacío → no crea trigger inbox ────────────────────────────
@pytest.mark.asyncio
async def test_empty_inbox_does_not_create_trigger(loop_instance, mock_db):
    mock_db.select = AsyncMock(
        side_effect=[
            [],  # mensajes
            [],  # contribuciones
        ]
    )
    loop_instance._last_thought_at = 99999999999  # cooldown infinito → no reflexion

    with (
        patch("kernel.embrion_inbox.consume_next", return_value=[]),
        patch("kernel.embrion_inbox._get_supabase_client", return_value=object()),
    ):
        trigger = await loop_instance._detect_trigger()

    assert trigger is None


# ═══════════════════════════════════════════════════════════════════════
# Tests del flujo MFA stub en _check_and_think
# ═══════════════════════════════════════════════════════════════════════


# ─── 6) Trigger inbox_command requires_mfa → mark_requires_mfa, NO _think ─
@pytest.mark.asyncio
async def test_high_risk_inbox_command_skips_think_and_marks_mfa(loop_instance):
    """Un /override no debe llamar _judge_before ni _think — solo mfa stub."""
    trigger_mfa = {
        "type": "inbox_command",
        "inbox_id": "mfa-1",
        "command_type": "/override",
        "requires_mfa": True,
        "detail": "/override hash=xxx",
        "priority": 9,
    }
    loop_instance._detect_trigger = AsyncMock(return_value=trigger_mfa)
    loop_instance._judge_before = AsyncMock(return_value=True)
    loop_instance._think = AsyncMock(return_value={"response": "should not happen"})

    mfa_calls = []

    def fake_mfa(client, **kwargs):
        mfa_calls.append(kwargs)
        return {"id": kwargs.get("inbox_id")}

    with (
        patch("kernel.embrion_inbox.mark_requires_mfa", side_effect=fake_mfa) as mfa_mock,
        patch("kernel.embrion_inbox._get_supabase_client", return_value=object()),
    ):
        await loop_instance._check_and_think()

    assert mfa_mock.called
    assert len(mfa_calls) == 1
    assert mfa_calls[0]["inbox_id"] == "mfa-1"
    assert "mfa_pin_hash" in mfa_calls[0]
    assert "mfa_expires_at" in mfa_calls[0]
    # Verifica que NO llamó _think ni _judge_before
    loop_instance._think.assert_not_called()
    loop_instance._judge_before.assert_not_called()


# ─── 7) Trigger inbox_command (no MFA) → flujo normal + mark_processed ──
@pytest.mark.asyncio
async def test_safe_inbox_command_completes_with_mark_processed(loop_instance):
    trigger_safe = {
        "type": "inbox_command",
        "inbox_id": "safe-1",
        "command_type": "/help",
        "requires_mfa": False,
        "detail": "/help",
        "priority": 9,
    }
    loop_instance._detect_trigger = AsyncMock(return_value=trigger_safe)
    loop_instance._judge_before = AsyncMock(return_value=True)
    loop_instance._think = AsyncMock(return_value={"response": "Lista de comandos: /help /status..."})
    loop_instance._judge_after = AsyncMock(return_value={"useful": True})
    loop_instance._should_speak = MagicMock(return_value=(True, 80, "mensaje"))
    loop_instance._report = AsyncMock(return_value=None)

    processed_calls = []

    def fake_processed(client, inbox_id, **kwargs):
        processed_calls.append({"inbox_id": inbox_id, **kwargs})
        return {"id": inbox_id}

    with (
        patch("kernel.embrion_inbox.mark_processed", side_effect=fake_processed) as proc_mock,
        patch("kernel.embrion_inbox._get_supabase_client", return_value=object()),
    ):
        await loop_instance._check_and_think()

    assert proc_mock.called
    assert len(processed_calls) == 1
    assert processed_calls[0]["inbox_id"] == "safe-1"
    assert "cycle_id" in processed_calls[0]
    # _think SÍ se llamó esta vez
    loop_instance._think.assert_called_once()


# ─── 8) Si excepción en mark_processed → no rompe el flujo ──────────────
@pytest.mark.asyncio
async def test_mark_processed_exception_swallowed(loop_instance):
    trigger_safe = {
        "type": "inbox_command",
        "inbox_id": "boom-1",
        "command_type": "/help",
        "requires_mfa": False,
        "detail": "/help",
        "priority": 9,
    }
    loop_instance._detect_trigger = AsyncMock(return_value=trigger_safe)
    loop_instance._judge_before = AsyncMock(return_value=True)
    loop_instance._think = AsyncMock(return_value={"response": "ok"})
    loop_instance._judge_after = AsyncMock(return_value={"useful": True})
    loop_instance._should_speak = MagicMock(return_value=(False, 30, "silencioso"))

    with (
        patch("kernel.embrion_inbox.mark_processed", side_effect=RuntimeError("db down")),
        patch("kernel.embrion_inbox._get_supabase_client", return_value=object()),
    ):
        # NO debe propagar la excepción
        await loop_instance._check_and_think()

    # Pero los counters siguen actualizándose
    assert loop_instance._thoughts_today == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
