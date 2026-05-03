"""
El Monstruo — Telegram Notifier (Sprint 8: Autonomía Temporal)
===============================================================
Sends notifications to the user via Telegram Bot API when:
  - A scheduled job starts executing
  - A scheduled job completes successfully
  - A scheduled job fails

Uses the Telegram Bot HTTP API directly (no python-telegram-bot dependency).
The bot token and chat ID are read from environment variables.

Architecture:
  AutonomousRunner → TelegramNotifier.send_message() → Telegram Bot API
"""

from __future__ import annotations

import os
from typing import Optional

import httpx
import structlog

logger = structlog.get_logger("notifier.telegram")

# ── Configuration ───────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")  # Alfredo's chat ID
TELEGRAM_API_BASE = "https://api.telegram.org/bot"


def _escape_telegram_markdown(text: str) -> str:
    """
    Escape special Markdown characters for Telegram's MarkdownV1 parser.

    Telegram's Markdown parser chokes on unmatched `_`, `*`, `` ` ``, `[`.
    This escapes them so the message arrives intact without falling back
    to the plain-text retry (which produces log noise).
    """
    # Order matters: backslash first to avoid double-escaping
    for char in ("_", "*", "`", "["):
        text = text.replace(char, f"\\{char}")
    return text


class TelegramNotifier:
    """
    Sends messages to a Telegram user via the Bot API.

    Uses httpx for async HTTP calls. No external Telegram SDK needed.
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        default_chat_id: Optional[str] = None,
    ):
        self._bot_token = bot_token or TELEGRAM_BOT_TOKEN
        self._default_chat_id = default_chat_id or TELEGRAM_CHAT_ID
        self._enabled = bool(self._bot_token and self._default_chat_id)

        if not self._enabled:
            logger.warning(
                "telegram_notifier_disabled",
                has_token=bool(self._bot_token),
                has_chat_id=bool(self._default_chat_id),
                hint="Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars",
            )

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def send_message(
        self,
        user_id: str,
        text: str,
        chat_id: Optional[str] = None,
        parse_mode: str = "Markdown",
    ) -> bool:
        """
        Send a text message to a Telegram chat.

        Args:
            user_id: User identifier (used for logging, not for routing)
            text: Message text (supports Markdown)
            chat_id: Override chat ID (defaults to TELEGRAM_CHAT_ID)
            parse_mode: "Markdown" or "HTML"

        Returns:
            True if sent successfully, False otherwise
        """
        if not self._enabled:
            logger.info("notification_skipped", reason="notifier_disabled", user_id=user_id)
            return False

        target_chat_id = chat_id or self._default_chat_id
        if not target_chat_id:
            logger.warning("no_chat_id", user_id=user_id)
            return False

        url = f"{TELEGRAM_API_BASE}{self._bot_token}/sendMessage"
        # Escape Markdown special chars to prevent parse errors (Sprint 81.6)
        safe_text = _escape_telegram_markdown(text) if parse_mode == "Markdown" else text

        payload = {
            "chat_id": target_chat_id,
            "text": safe_text[:4096],  # Telegram limit
            "parse_mode": parse_mode,
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    logger.info(
                        "telegram_message_sent",
                        user_id=user_id,
                        chat_id=target_chat_id,
                        text_length=len(text),
                    )
                    return True
                else:
                    logger.error(
                        "telegram_api_error",
                        description=data.get("description", "unknown"),
                    )
                    # Retry without parse_mode if Markdown fails
                    if "can't parse" in data.get("description", "").lower():
                        return await self._send_plain(target_chat_id, text)
                    return False
            else:
                logger.error(
                    "telegram_http_error",
                    status=response.status_code,
                    body=response.text[:200],
                )
                return False

        except Exception as e:
            logger.error("telegram_send_failed", error=str(e))
            return False

    async def _send_plain(self, chat_id: str, text: str) -> bool:
        """Fallback: send without parse_mode if Markdown fails."""
        url = f"{TELEGRAM_API_BASE}{self._bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text[:4096],
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(url, json=payload)
            return response.status_code == 200 and response.json().get("ok", False)
        except Exception:
            return False

    async def send_job_notification(
        self,
        title: str,
        status: str,
        result: str,
        job_id: str = "",
        chat_id: Optional[str] = None,
    ) -> bool:
        """
        Send a formatted job notification.

        Args:
            title: Job title
            status: "started", "completed", or "failed"
            result: Result summary or error message
            job_id: Job UUID for reference
            chat_id: Override chat ID
        """
        emoji_map = {
            "started": "\u23f3",  # hourglass
            "completed": "\u2705",  # green check
            "failed": "\u274c",  # red X
        }
        emoji = emoji_map.get(status, "\u2139\ufe0f")

        message = f"{emoji} *Tarea Autónoma*\n\n*{title}*\nEstado: {status}\n"

        if result:
            # Truncate result for Telegram
            truncated = result[:1200]
            if len(result) > 1200:
                truncated += "\n\n_(resultado truncado)_"
            message += f"\n{truncated}"

        if job_id:
            message += f"\n\n`ID: {job_id[:8]}...`"

        return await self.send_message(
            user_id="system",
            text=message,
            chat_id=chat_id,
        )
