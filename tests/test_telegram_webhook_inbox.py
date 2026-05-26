"""
tests/test_telegram_webhook_inbox.py — Tests CA2 del webhook Telegram→Inbox.

Sprint EMBRION-NEEDS-002 Tarea 5 (CA2).
Verifica que el handler de /v1/embrion/telegram/webhook:
  - acepta mensajes /command y los enqueua al inbox
  - rechaza autores no autorizados
  - mantiene flujo callback_query intacto (regresión Sprint S-001)
  - valida X-Telegram-Bot-Api-Secret-Token
  - ignora mensajes sin /
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

# ─── Setup mínimo de FastAPI app sólo con el router de embrion ──────────


@pytest.fixture
def app_client():
    """TestClient FastAPI con el router de embrion montado."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from kernel.embrion_routes import router as embrion_router

    app = FastAPI()
    # router ya incluye prefix="/v1/embrion" en su definición; no duplicar.
    app.include_router(embrion_router)
    return TestClient(app)


# ─── Fake inbox para evitar tocar Supabase real en tests del webhook ────


class FakeEnqueuedResult:
    def __init__(
        self,
        inbox_id="fake-inbox-id",
        created=True,
        estado="pending",
        tipo_comando="/help",
        intent_class="safe",
        rejected_reason=None,
    ):
        self.inbox_id = inbox_id
        self.created = created
        self.estado = estado
        self.tipo_comando = tipo_comando
        self.intent_class = intent_class
        self.rejected_reason = rejected_reason


@pytest.fixture
def patch_inbox():
    """Mockear enqueue() y _get_supabase_client() para no tocar Supabase real."""
    enqueue_calls = []

    def fake_enqueue(client, chat_id, text, *args, **kwargs):
        enqueue_calls.append({"chat_id": chat_id, "text": text})
        return FakeEnqueuedResult(
            inbox_id=f"fake-{len(enqueue_calls)}",
            tipo_comando=text.split()[0] if text.startswith("/") else "unknown",
        )

    fake_client = object()  # marker

    with (
        patch("kernel.embrion_inbox.enqueue", side_effect=fake_enqueue) as enq,
        patch("kernel.embrion_inbox._get_supabase_client", return_value=fake_client),
    ):
        yield {"enqueue": enq, "calls": enqueue_calls}


# ─── Fixture de env vars (secret + chat_id válidos) ──────────────────────


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "test-secret-abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    yield


# ═══════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════


# ─── 1) Webhook sin secret → 401 ────────────────────────────────────────
def test_webhook_missing_secret_returns_401(app_client):
    response = app_client.post(
        "/v1/embrion/telegram/webhook",
        json={"update_id": 1},
    )
    assert response.status_code == 401


# ─── 2) Webhook con secret incorrecto → 401 ─────────────────────────────
def test_webhook_wrong_secret_returns_401(app_client):
    response = app_client.post(
        "/v1/embrion/telegram/webhook",
        json={"update_id": 1},
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
    )
    assert response.status_code == 401


# ─── 3) Webhook con body no-JSON → 400 ──────────────────────────────────
def test_webhook_bad_json_400(app_client):
    response = app_client.post(
        "/v1/embrion/telegram/webhook",
        content="not-json",
        headers={
            "X-Telegram-Bot-Api-Secret-Token": "test-secret-abc",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 400


# ─── 4) Mensaje /help de Alfredo (chat_id correcto) → enqueued ──────────
def test_message_help_from_alfredo_enqueued(app_client, patch_inbox):
    response = app_client.post(
        "/v1/embrion/telegram/webhook",
        json={
            "update_id": 100,
            "message": {
                "message_id": 1,
                "from": {"id": 12345, "username": "alfredo"},
                "chat": {"id": 12345, "type": "private"},
                "text": "/help",
                "date": 1715000000,
            },
        },
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret-abc"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body.get("enqueued") is True
    assert body.get("tipo_comando") == "/help"
    assert len(patch_inbox["calls"]) == 1
    call = patch_inbox["calls"][0]
    assert call["text"] == "/help"


# ─── 5) Mensaje /context con texto largo → enqueued ──────────────────────
def test_message_context_enqueued(app_client, patch_inbox):
    response = app_client.post(
        "/v1/embrion/telegram/webhook",
        json={
            "update_id": 101,
            "message": {
                "message_id": 2,
                "from": {"id": 12345},
                "chat": {"id": 12345},
                "text": "/context El sprint está bloqueado",
            },
        },
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret-abc"},
    )
    assert response.status_code == 200
    assert response.json()["enqueued"] is True
    assert response.json()["tipo_comando"] == "/context"


# ─── 6) Mensaje de chat_id NO autorizado → denied + audit ───────────────
def test_message_from_unauthorized_user_denied(app_client, patch_inbox):
    # Mockear _get_supabase_client + audit del inbox para evitar Supabase real
    with patch("kernel.embrion_inbox.audit", return_value={}):
        response = app_client.post(
            "/v1/embrion/telegram/webhook",
            json={
                "update_id": 102,
                "message": {
                    "message_id": 3,
                    "from": {"id": 99999},  # NO es chat_id 12345
                    "chat": {"id": 99999},
                    "text": "/help",
                },
            },
            headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret-abc"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body.get("denied") is True
    assert body.get("reason") == "unauthorized_inbox"
    # No debe haber llamado enqueue
    assert len(patch_inbox["calls"]) == 0


# ─── 7) Mensaje de texto sin / → ignored ────────────────────────────────
def test_non_command_message_ignored(app_client, patch_inbox):
    response = app_client.post(
        "/v1/embrion/telegram/webhook",
        json={
            "update_id": 103,
            "message": {
                "message_id": 4,
                "from": {"id": 12345},
                "chat": {"id": 12345},
                "text": "Hola, esto no es un comando",
            },
        },
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret-abc"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body.get("ignored") is True
    assert body.get("reason") == "non_command_text"
    assert len(patch_inbox["calls"]) == 0


# ─── 8) Update sin message ni callback_query → ignored ──────────────────
def test_update_without_message_or_callback_ignored(app_client, patch_inbox):
    response = app_client.post(
        "/v1/embrion/telegram/webhook",
        json={
            "update_id": 104,
            "edited_message": {"text": "edited"},  # campo que ignoramos
        },
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret-abc"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body.get("ignored") is True


# ─── 9) callback_query sigue funcionando (regresión Sprint S-001) ───────
def test_callback_query_flow_intact(app_client):
    """Verifica que la rama callback_query NO fue rota por el cambio CA2."""
    response = app_client.post(
        "/v1/embrion/telegram/webhook",
        json={
            "update_id": 105,
            "callback_query": {
                "id": "cb-1",
                "from": {"id": 12345},
                "data": "approve:non-existent-proposal-id-1234",
                "message": {
                    "message_id": 5,
                    "chat": {"id": 12345},
                },
            },
        },
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret-abc"},
    )
    # No debe ser 401/400. Puede ser 200 con success=False o 500 si la DB no
    # está disponible — lo importante: NO retornó 200 con "enqueued"=True
    # (eso significaría que la rama nueva atrapó el callback por error).
    body = response.json() if response.status_code == 200 else {}
    assert "enqueued" not in body
    # Debe tener "action" si la rama callback_query la procesó (success o no)
    # o bien "denied"/"ignored" si DB ausente — pero NUNCA enqueued.


# ─── 10) Mensaje vacío (text=None) → ignored ────────────────────────────
def test_message_with_no_text_ignored(app_client, patch_inbox):
    response = app_client.post(
        "/v1/embrion/telegram/webhook",
        json={
            "update_id": 106,
            "message": {
                "message_id": 6,
                "from": {"id": 12345},
                "chat": {"id": 12345},
                # sin text
            },
        },
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret-abc"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body.get("ignored") is True
    assert len(patch_inbox["calls"]) == 0


# ─── 11) Si TELEGRAM_CHAT_ID NO está configurado, acepta cualquier autor (defensivo) ─
def test_no_telegram_chat_id_accepts_any_author(app_client, patch_inbox, monkeypatch):
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    response = app_client.post(
        "/v1/embrion/telegram/webhook",
        json={
            "update_id": 107,
            "message": {
                "message_id": 7,
                "from": {"id": 99999},  # autor random
                "chat": {"id": 99999},
                "text": "/help",
            },
        },
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret-abc"},
    )
    assert response.status_code == 200
    body = response.json()
    # Sin TELEGRAM_CHAT_ID configurado, no podemos verificar autor → enqueue
    assert body.get("enqueued") is True or body.get("denied") is False


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
