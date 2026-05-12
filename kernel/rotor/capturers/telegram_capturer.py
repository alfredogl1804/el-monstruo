"""
Telegram capturer — extiende telegram_webhook para INSERT en rotor_activity_log.

Sprint: ROTOR-001 (T2.3)
Trigger: extensión del webhook Telegram existente que ya popula embrion_inbox.
"""

from __future__ import annotations

import os
from typing import Any, Mapping, Optional

from kernel.rotor.capturers import BaseCapturer
from kernel.rotor.energy_calculator import RotorActivity, RotorSource


def _get_authorized_chat_ids() -> frozenset[str]:
    """
    Lee env var TELEGRAM_AUTHORIZED_CHAT_IDS (comma-separated) o cae a TELEGRAM_CHAT_ID.
    Mensajes de chats no autorizados se capturan pero su energy_units = 0.
    """
    explicit = os.environ.get("TELEGRAM_AUTHORIZED_CHAT_IDS", "")
    if explicit.strip():
        return frozenset(s.strip() for s in explicit.split(",") if s.strip())
    fallback = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    return frozenset({fallback}) if fallback else frozenset()


class TelegramCapturer(BaseCapturer):
    """Captura un mensaje de Telegram y produce RotorActivity."""

    SOURCE: str = RotorSource.TELEGRAM_MESSAGE.value
    DEFAULT_ACTOR: str = "telegram_unknown"

    def __init__(
        self,
        persist_fn=None,
        authorized_chat_ids: Optional[frozenset[str]] = None,
    ) -> None:
        super().__init__(persist_fn=persist_fn)
        # Permite inyección explícita para tests
        self._authorized = (
            authorized_chat_ids
            if authorized_chat_ids is not None
            else _get_authorized_chat_ids()
        )

    def capture(self, raw_event: Mapping[str, Any]) -> RotorActivity:
        """
        raw_event esperado (subset Telegram Update.message):
          {
            "chat_id": "123456",
            "message_id": 42,
            "text": "Hola monstruo",
            "from_username": "alfredogl1804"
          }
        """
        chat_id = str(raw_event.get("chat_id", ""))
        username = str(raw_event.get("from_username", ""))
        actor = username if username else self.DEFAULT_ACTOR
        text = str(raw_event.get("text", ""))

        authorized = chat_id in self._authorized if self._authorized else False

        payload = {
            "chat_id": chat_id,
            "message_id": int(raw_event.get("message_id", 0)),
            "text_length": len(text),
            "sender": username,
            "authorized": authorized,
        }

        return RotorActivity(source=self.SOURCE, actor=actor, payload=payload)


__all__ = ["TelegramCapturer"]
