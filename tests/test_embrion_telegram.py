"""
Tests for Sprint EMBRION-NEEDS-001 — Tarea 4 (Telegram HITL bidireccional).

Coverage:
1. TelegramNotifier extension (send_with_keyboard, answer_callback, edit_message_text, send_proposal_for_hitl)
2. embrion_write_policy.notify_hitl() multi-channel (cowork_bridge,telegram)
3. embrion_routes /v1/embrion/telegram/webhook endpoint (security + dispatch)

All HTTP I/O to api.telegram.org is mocked. All DB I/O is mocked via FakeClient.
Zero network calls. Should run in < 1 second total.
"""
from __future__ import annotations

import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from kernel import embrion_routes
from kernel import embrion_write_policy
from kernel.runner.telegram_notifier import TelegramNotifier


# ════════════════════════════════════════════════════════════════════
# FakeClient — same pattern as test_embrion_write_policy.py
# ════════════════════════════════════════════════════════════════════


class FakeClient:
    """Minimal in-memory client emulating the _SupabaseRest API."""

    def __init__(self):
        self.tables: dict[str, list[dict]] = {}

    def select(self, table: str, params: dict | None = None) -> list[dict]:
        return list(self.tables.get(table, []))

    def insert(self, table: str, payload: dict) -> dict:
        self.tables.setdefault(table, []).append(payload)
        return payload

    def update(self, table: str, filters: dict, payload: dict) -> list[dict]:
        rows = self.tables.get(table, [])
        # filters like {"id": "eq.<uuid>"} → match id == <uuid>
        f_id = filters.get("id", "").removeprefix("eq.")
        matched = [r for r in rows if str(r.get("id")) == f_id]
        for r in matched:
            r.update(payload)
        return matched


# ════════════════════════════════════════════════════════════════════
# Section 1 — TelegramNotifier extension
# ════════════════════════════════════════════════════════════════════


def _mock_httpx_response(status_code: int = 200, json_payload: dict | None = None):
    """Build a MagicMock that mimics httpx.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_payload or {"ok": True, "result": {"message_id": 42}}
    return resp


@pytest.mark.asyncio
async def test_send_with_keyboard_disabled_returns_none():
    """When notifier is disabled (no token), send_with_keyboard returns None."""
    notifier = TelegramNotifier(bot_token=None, default_chat_id=None)
    assert notifier.enabled is False
    result = await notifier.send_with_keyboard(
        text="hi",
        inline_keyboard=[[{"text": "OK", "callback_data": "ok:x"}]],
    )
    assert result is None


@pytest.mark.asyncio
async def test_send_with_keyboard_success_returns_message_dict():
    """Successful send returns the result dict with message_id."""
    notifier = TelegramNotifier(bot_token="t" * 20, default_chat_id="123")
    fake_resp = _mock_httpx_response(
        200, {"ok": True, "result": {"message_id": 999, "chat": {"id": 123}}}
    )

    fake_client = MagicMock()
    fake_client.__aenter__ = AsyncMock(return_value=fake_client)
    fake_client.__aexit__ = AsyncMock(return_value=None)
    fake_client.post = AsyncMock(return_value=fake_resp)

    with patch("kernel.runner.telegram_notifier.httpx.AsyncClient", return_value=fake_client):
        result = await notifier.send_with_keyboard(
            text="HITL test",
            inline_keyboard=[
                [{"text": "Yes", "callback_data": "yes:1"}, {"text": "No", "callback_data": "no:1"}]
            ],
        )

    assert result is not None
    assert result["message_id"] == 999
    # Verify the payload included reply_markup with inline_keyboard
    call_kwargs = fake_client.post.call_args.kwargs
    payload = call_kwargs["json"]
    assert "reply_markup" in payload
    assert payload["reply_markup"]["inline_keyboard"][0][0]["callback_data"] == "yes:1"


@pytest.mark.asyncio
async def test_answer_callback_calls_correct_endpoint():
    """answer_callback POSTs to answerCallbackQuery with the callback_query_id."""
    notifier = TelegramNotifier(bot_token="t" * 20, default_chat_id="123")
    fake_resp = _mock_httpx_response(200, {"ok": True, "result": True})

    fake_client = MagicMock()
    fake_client.__aenter__ = AsyncMock(return_value=fake_client)
    fake_client.__aexit__ = AsyncMock(return_value=None)
    fake_client.post = AsyncMock(return_value=fake_resp)

    with patch("kernel.runner.telegram_notifier.httpx.AsyncClient", return_value=fake_client):
        ok = await notifier.answer_callback("cb-id-123", text="Aprobada", show_alert=False)

    assert ok is True
    url = fake_client.post.call_args.args[0]
    assert "answerCallbackQuery" in url
    payload = fake_client.post.call_args.kwargs["json"]
    assert payload["callback_query_id"] == "cb-id-123"
    assert payload["text"] == "Aprobada"


@pytest.mark.asyncio
async def test_edit_message_text_removes_keyboard_by_default():
    """edit_message_text sends empty inline_keyboard when remove_keyboard=True."""
    notifier = TelegramNotifier(bot_token="t" * 20, default_chat_id="123")
    fake_resp = _mock_httpx_response(200, {"ok": True})

    fake_client = MagicMock()
    fake_client.__aenter__ = AsyncMock(return_value=fake_client)
    fake_client.__aexit__ = AsyncMock(return_value=None)
    fake_client.post = AsyncMock(return_value=fake_resp)

    with patch("kernel.runner.telegram_notifier.httpx.AsyncClient", return_value=fake_client):
        ok = await notifier.edit_message_text(
            chat_id="123",
            message_id=42,
            text="Resolved!",
            remove_keyboard=True,
        )

    assert ok is True
    payload = fake_client.post.call_args.kwargs["json"]
    assert payload["reply_markup"] == {"inline_keyboard": []}


@pytest.mark.asyncio
async def test_send_proposal_for_hitl_builds_correct_callback_data():
    """send_proposal_for_hitl generates callback_data with format 'approve:<id>' and 'reject:<id>'."""
    notifier = TelegramNotifier(bot_token="t" * 20, default_chat_id="123")
    fake_resp = _mock_httpx_response(200, {"ok": True, "result": {"message_id": 100}})

    fake_client = MagicMock()
    fake_client.__aenter__ = AsyncMock(return_value=fake_client)
    fake_client.__aexit__ = AsyncMock(return_value=None)
    fake_client.post = AsyncMock(return_value=fake_resp)

    with patch("kernel.runner.telegram_notifier.httpx.AsyncClient", return_value=fake_client):
        result = await notifier.send_proposal_for_hitl(
            proposal_id="abc-12345-def",
            action_type="db_write",
            risk_level="high",
            target="embrion_memoria",
            reason="Insert reflection",
            cost_estimate_usd=0.0,
            expires_at="2026-05-11T00:00:00Z",
        )

    assert result is not None
    payload = fake_client.post.call_args.kwargs["json"]
    keyboard = payload["reply_markup"]["inline_keyboard"]
    assert len(keyboard) == 1  # one row
    assert len(keyboard[0]) == 2  # two buttons
    cb_approve = keyboard[0][0]["callback_data"]
    cb_reject = keyboard[0][1]["callback_data"]
    assert cb_approve == "approve:abc-12345-def"
    assert cb_reject == "reject:abc-12345-def"
    # Text should mention the proposal_id and risk
    assert "abc-12345-def" in payload["text"]


# ════════════════════════════════════════════════════════════════════
# Section 2 — embrion_write_policy.notify_hitl multi-channel
# ════════════════════════════════════════════════════════════════════


def test_notify_hitl_parse_channels_csv():
    """_parse_channels handles CSV string with whitespace."""
    parsed = embrion_write_policy._parse_channels("cowork_bridge, telegram")
    assert parsed == ["cowork_bridge", "telegram"]


def test_notify_hitl_parse_channels_invalid_raises():
    """_parse_channels raises ValueError on unknown channel."""
    with pytest.raises(ValueError, match="invál"):
        embrion_write_policy._parse_channels("cowork_bridge,invalid_channel")


def test_notify_hitl_parse_channels_empty_raises():
    """_parse_channels raises on empty input."""
    with pytest.raises(ValueError, match="vac"):
        embrion_write_policy._parse_channels("")


def test_notify_hitl_telegram_disabled_falls_back_gracefully(monkeypatch):
    """When telegram is unconfigured, notify_hitl(channel='telegram') returns False non-fatally."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    client = FakeClient()
    proposal = {
        "id": "test-uuid-123",
        "proposal_type": "db_write",
        "summary": "test",
        "risk_level": "low",
    }
    result = embrion_write_policy.notify_hitl(client, proposal, channel="telegram")
    # Telegram notifier disabled → returns False (no channels succeeded)
    assert result is False


def test_notify_hitl_multi_channel_succeeds_if_any_succeeds(monkeypatch):
    """When channel='cowork_bridge,telegram' and only cowork succeeds, overall returns True."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    client = FakeClient()
    proposal = {
        "id": "test-uuid-456",
        "proposal_type": "db_write",
        "summary": "test multi",
        "risk_level": "medium",
        "expires_at": "2026-05-11T00:00:00Z",
    }
    # Insert a row in proposals so update doesn't fail silently
    client.insert(embrion_write_policy.TABLE_PROPOSALS, {"id": "test-uuid-456", "approval_status": "pending"})

    result = embrion_write_policy.notify_hitl(
        client, proposal, channel="cowork_bridge,telegram"
    )
    assert result is True
    # cowork inserted to embrion_memoria
    memos = client.tables.get(embrion_write_policy.TABLE_MEMORIA, [])
    assert len(memos) == 1
    assert memos[0]["importancia"] == 10
    # notified_via should be only "cowork_bridge" (telegram failed)
    proposals = client.tables.get(embrion_write_policy.TABLE_PROPOSALS, [])
    assert proposals[0].get("notified_via") == "cowork_bridge"


# ════════════════════════════════════════════════════════════════════
# Section 3 — Telegram webhook endpoint
# ════════════════════════════════════════════════════════════════════


def _build_test_client(fake_db) -> TestClient:
    """Mount embrion_routes router into a fresh FastAPI app with mocked DB."""
    app = FastAPI()
    app.include_router(embrion_routes.router)
    embrion_routes.set_dependencies(db=fake_db, notifier=None)
    return TestClient(app)


class FakeDB:
    """Async DB mock matching the routes-side adapter (kwargs-based API)."""

    connected = True  # _ensure_db() checks this attribute

    def __init__(self):
        self.proposals: list[dict] = []

    async def select(self, table: str, columns: str = "*", filters: dict | None = None,
                     order_by: str | None = None, order_desc: bool = False, limit: int = 100):
        rows = list(self.proposals)
        if filters:
            for k, v in filters.items():
                rows = [r for r in rows if r.get(k) == v]
        return rows

    async def insert(self, table: str, payload: dict):
        self.proposals.append(payload)
        return payload

    async def update(self, table: str, data: dict, filters: dict):
        rows = self.proposals
        matched = []
        for r in rows:
            if all(r.get(k) == v for k, v in filters.items()):
                r.update(data)
                matched.append(r)
        return matched


def test_webhook_disabled_when_secret_unset(monkeypatch):
    """Without TELEGRAM_WEBHOOK_SECRET, webhook returns 503."""
    monkeypatch.delenv("TELEGRAM_WEBHOOK_SECRET", raising=False)

    client = _build_test_client(FakeDB())
    resp = client.post("/v1/embrion/telegram/webhook", json={"update_id": 1})
    assert resp.status_code == 503
    assert "disabled" in resp.json()["detail"].lower()


def test_webhook_rejects_wrong_secret(monkeypatch):
    """Wrong X-Telegram-Bot-Api-Secret-Token returns 401."""
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "correct-secret")

    client = _build_test_client(FakeDB())
    resp = client.post(
        "/v1/embrion/telegram/webhook",
        json={"update_id": 1},
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
    )
    assert resp.status_code == 401


def test_webhook_ignores_non_callback_update(monkeypatch):
    """A regular message update is ignored gracefully (200 with ignored=True)."""
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "s3cret")

    client = _build_test_client(FakeDB())
    resp = client.post(
        "/v1/embrion/telegram/webhook",
        json={"update_id": 5, "message": {"text": "hello", "from": {"id": 1}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cret"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body.get("ignored") is True


def test_webhook_rejects_unauthorized_user(monkeypatch):
    """Callback from non-authorized user_id is denied (200 with denied=True for graceful no-retry)."""
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "s3cret")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "777")  # Alfredo's chat_id
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x" * 20)

    client = _build_test_client(FakeDB())
    update = {
        "update_id": 10,
        "callback_query": {
            "id": "cb-1",
            "data": "approve:test-uuid-1",
            "from": {"id": 999},  # ← NOT Alfredo
            "message": {"chat": {"id": 999}, "message_id": 50},
        },
    }
    # Patch httpx so the answer_callback inside doesn't actually call Telegram
    fake_client = MagicMock()
    fake_client.__aenter__ = AsyncMock(return_value=fake_client)
    fake_client.__aexit__ = AsyncMock(return_value=None)
    fake_client.post = AsyncMock(return_value=_mock_httpx_response(200, {"ok": True, "result": True}))
    with patch("kernel.runner.telegram_notifier.httpx.AsyncClient", return_value=fake_client):
        resp = client.post(
            "/v1/embrion/telegram/webhook",
            json=update,
            headers={"X-Telegram-Bot-Api-Secret-Token": "s3cret"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("denied") is True
    assert body.get("reason") == "unauthorized"


def test_webhook_approve_flow_marks_proposal_approved(monkeypatch):
    """Full happy path: authorized user clicks approve → proposal becomes approved."""
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "s3cret")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "777")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x" * 20)

    db = FakeDB()
    proposal_id = "prop-uuid-aaaa-bbbb-cccc-dddd-eeee"
    db.proposals.append({
        "id": proposal_id,
        "approval_status": "pending",
        "proposal_type": "db_write",
        "summary": "test approve flow",
        "risk_level": "low",
        "expires_at": "2099-01-01T00:00:00+00:00",
    })

    client = _build_test_client(db)

    update = {
        "update_id": 20,
        "callback_query": {
            "id": "cb-2",
            "data": f"approve:{proposal_id}",
            "from": {"id": 777},
            "message": {"chat": {"id": 777}, "message_id": 60},
        },
    }

    fake_client = MagicMock()
    fake_client.__aenter__ = AsyncMock(return_value=fake_client)
    fake_client.__aexit__ = AsyncMock(return_value=None)
    fake_client.post = AsyncMock(return_value=_mock_httpx_response(200, {"ok": True, "result": True}))
    with patch("kernel.runner.telegram_notifier.httpx.AsyncClient", return_value=fake_client):
        resp = client.post(
            "/v1/embrion/telegram/webhook",
            json=update,
            headers={"X-Telegram-Bot-Api-Secret-Token": "s3cret"},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["action"] == "approve"
    assert body["success"] is True
    assert db.proposals[0]["approval_status"] == "approved"
    assert db.proposals[0]["approved_by"] == "telegram:777"


def test_webhook_reject_flow_marks_proposal_rejected(monkeypatch):
    """Full happy path: authorized user clicks reject → proposal becomes rejected."""
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "s3cret")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "777")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x" * 20)

    db = FakeDB()
    proposal_id = "prop-uuid-rej-1234-5678-9abc-def0"
    db.proposals.append({
        "id": proposal_id,
        "approval_status": "pending",
        "proposal_type": "code_commit",
        "summary": "test reject flow",
        "risk_level": "high",
        "expires_at": "2099-01-01T00:00:00+00:00",
    })

    client = _build_test_client(db)
    update = {
        "update_id": 30,
        "callback_query": {
            "id": "cb-3",
            "data": f"reject:{proposal_id}",
            "from": {"id": 777},
            "message": {"chat": {"id": 777}, "message_id": 70},
        },
    }

    fake_client = MagicMock()
    fake_client.__aenter__ = AsyncMock(return_value=fake_client)
    fake_client.__aexit__ = AsyncMock(return_value=None)
    fake_client.post = AsyncMock(return_value=_mock_httpx_response(200, {"ok": True, "result": True}))
    with patch("kernel.runner.telegram_notifier.httpx.AsyncClient", return_value=fake_client):
        resp = client.post(
            "/v1/embrion/telegram/webhook",
            json=update,
            headers={"X-Telegram-Bot-Api-Secret-Token": "s3cret"},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["action"] == "reject"
    assert body["success"] is True
    assert db.proposals[0]["approval_status"] == "rejected"
    assert "rejection_reason" in db.proposals[0]


def test_webhook_idempotent_on_already_approved(monkeypatch):
    """If proposal is already approved, second click does NOT change state but returns 200."""
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "s3cret")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "777")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x" * 20)

    db = FakeDB()
    proposal_id = "prop-uuid-idempotent"
    db.proposals.append({
        "id": proposal_id,
        "approval_status": "approved",  # ← already approved
        "proposal_type": "db_write",
        "summary": "test",
        "risk_level": "low",
        "approved_by": "telegram:777",
        "expires_at": "2099-01-01T00:00:00+00:00",
    })

    client = _build_test_client(db)
    update = {
        "update_id": 40,
        "callback_query": {
            "id": "cb-4",
            "data": f"approve:{proposal_id}",
            "from": {"id": 777},
            "message": {"chat": {"id": 777}, "message_id": 80},
        },
    }

    fake_client = MagicMock()
    fake_client.__aenter__ = AsyncMock(return_value=fake_client)
    fake_client.__aexit__ = AsyncMock(return_value=None)
    fake_client.post = AsyncMock(return_value=_mock_httpx_response(200, {"ok": True, "result": True}))
    with patch("kernel.runner.telegram_notifier.httpx.AsyncClient", return_value=fake_client):
        resp = client.post(
            "/v1/embrion/telegram/webhook",
            json=update,
            headers={"X-Telegram-Bot-Api-Secret-Token": "s3cret"},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["success"] is False  # didn't change state
    # Proposal still 'approved' (no regression)
    assert db.proposals[0]["approval_status"] == "approved"


def test_webhook_handles_bad_callback_data(monkeypatch):
    """Malformed callback_data is ignored gracefully with 200."""
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "s3cret")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "777")

    client = _build_test_client(FakeDB())
    update = {
        "update_id": 50,
        "callback_query": {
            "id": "cb-5",
            "data": "no_colon_here",
            "from": {"id": 777},
            "message": {"chat": {"id": 777}, "message_id": 90},
        },
    }
    resp = client.post(
        "/v1/embrion/telegram/webhook",
        json=update,
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cret"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("ignored") is True
    assert body.get("reason") == "bad_callback_data"



# ============================================================================
# Defensive tests for the message_id validation contract (post-fix Tarea 4)
# ============================================================================
#
# Contexto del fix:
#   `TelegramNotifier.send_with_keyboard()` retorna directamente el `result` de
#   la Bot API (un dict como {"message_id": 1915, "chat": {...}, "text": "..."}),
#   NO el envoltorio {"ok": true, "result": {...}}.
#
#   Antes del fix, `embrion_routes._propose_write` validaba `tg_result.get("ok")`,
#   que siempre era None porque el dict no tenía esa key. Resultado: el flag
#   `notified_via` caía a 'cowork_bridge' aunque el mensaje SÍ llegara.
#
#   El fix valida `tg_result.get("message_id")` — Telegram solo asigna message_id
#   cuando entrega el mensaje al chat exitosamente.
#
# Estos 3 tests previenen regresión si alguien refactoriza send_with_keyboard
# y vuelve al envoltorio o devuelve dicts incompletos.


class _SuccessNotifier:
    """Fake notifier que simula respuesta exitosa de la Bot API (con message_id)."""
    enabled = True

    async def send_proposal_for_hitl(self, **kwargs):  # noqa: ARG002
        # Simula respuesta exitosa real de Telegram: dict con message_id directo
        return {
            "message_id": 1915,
            "chat": {"id": 7712993094, "type": "private"},
            "date": 1778412027,
            "text": "⚙️ *Propuesta de escritura del Embrión*\n...",
        }


class _EnvelopeOkFalseNotifier:
    """Fake notifier que devuelve un envelope-style dict con ok=False (caso defensivo)."""
    enabled = True

    async def send_proposal_for_hitl(self, **kwargs):  # noqa: ARG002
        # Simula que algún día alguien envuelve la respuesta o que la API falla
        # devolviendo un objeto-envelope. NO debe contar como entregado porque
        # NO hay message_id (Telegram solo lo asigna en éxito real).
        return {"ok": False, "description": "Bad Request: chat not found"}


class _EmptyDictNotifier:
    """Fake notifier que devuelve un dict vacío (degenerate case)."""
    enabled = True

    async def send_proposal_for_hitl(self, **kwargs):  # noqa: ARG002
        return {}


class _FakeDBWithIdGen:
    """FakeDB que genera UUID en insert (para el helper /propose)."""
    connected = True

    def __init__(self):
        self.rows: list[dict] = []

    async def select(self, table, columns="*", filters=None, order_by=None,
                     order_desc=False, limit=100):  # noqa: ARG002
        rows = list(self.rows)
        if filters:
            for k, v in filters.items():
                rows = [r for r in rows if r.get(k) == v]
        return rows[:limit]

    async def insert(self, table, payload):  # noqa: ARG002
        import uuid
        new_row = dict(payload)
        if "id" not in new_row:
            new_row["id"] = str(uuid.uuid4())
        self.rows.append(new_row)
        return new_row

    async def update(self, table, data, filters):  # noqa: ARG002
        matched = []
        for r in self.rows:
            if all(r.get(k) == v for k, v in filters.items()):
                r.update(data)
                matched.append(r)
        return matched

    def find_by_id(self, proposal_id):
        for r in self.rows:
            if r.get("id") == proposal_id:
                return r
        return None


def _post_propose(monkeypatch, fake_notifier_cls):
    """
    Helper: parchea TelegramNotifier para devolver el fake, posta una proposal,
    y retorna (db, proposal_id) para inspeccionar `notified_via`.
    """
    # Parchea ambos import paths del TelegramNotifier:
    import kernel.runner.telegram_notifier as tn_mod
    monkeypatch.setattr(tn_mod, "TelegramNotifier", fake_notifier_cls)
    # Env vars seguros para que enabled=True en el sitio que importa
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:fake")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "7712993094")

    db = _FakeDBWithIdGen()
    client = _build_test_client(db)
    resp = client.post(
        "/v1/embrion/propose",
        json={
            "proposal_type": "external_api_call",
            "risk_level": "low",
            "summary": "test message_id validation",
            "payload": {"target": "test_endpoint"},
            "notification_channels": ["cowork_bridge", "telegram"],
        },
        headers={"X-API-Key": "test-key"},
    )
    assert resp.status_code == 200, resp.text
    proposal_id = resp.json()["proposal_id"]
    return db, proposal_id


def test_notify_returns_true_when_telegram_returns_message_id(monkeypatch):
    """
    HAPPY PATH: notifier devuelve dict con message_id → notified_via debe
    incluir 'telegram'.
    """
    db, proposal_id = _post_propose(monkeypatch, _SuccessNotifier)
    row = db.find_by_id(proposal_id)
    assert row is not None, "Proposal not persisted in fake DB"
    notified_via = row.get("notified_via") or ""
    assert "telegram" in notified_via, (
        f"Expected 'telegram' in notified_via, got: {notified_via!r}"
    )


def test_notify_returns_false_when_telegram_returns_envelope_with_ok_false(monkeypatch):
    """
    DEFENSIVE: si alguien refactoriza send_with_keyboard y vuelve al envoltorio
    estilo {ok:false}, NO debe contar como telegram entregado (sin message_id).
    """
    db, proposal_id = _post_propose(monkeypatch, _EnvelopeOkFalseNotifier)
    row = db.find_by_id(proposal_id)
    assert row is not None
    notified_via = row.get("notified_via") or ""
    assert "telegram" not in notified_via, (
        f"Envelope con ok=false NO debe contar como telegram entregado. "
        f"notified_via={notified_via!r}"
    )


def test_notify_returns_false_when_telegram_returns_empty_dict(monkeypatch):
    """
    DEGENERATE: si la Bot API devuelve un dict vacío (sin message_id), tampoco
    debe contar como entregado.
    """
    db, proposal_id = _post_propose(monkeypatch, _EmptyDictNotifier)
    row = db.find_by_id(proposal_id)
    assert row is not None
    notified_via = row.get("notified_via") or ""
    assert "telegram" not in notified_via, (
        f"Dict vacío NO debe contar como telegram entregado. "
        f"notified_via={notified_via!r}"
    )
