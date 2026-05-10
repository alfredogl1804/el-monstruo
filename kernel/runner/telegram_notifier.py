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

    async def send_with_keyboard(
        self,
        text: str,
        inline_keyboard: list,
        chat_id: Optional[str] = None,
        parse_mode: str = "Markdown",
    ) -> Optional[dict]:
        """
        Send a message with an inline keyboard attached (HITL approval flow).

        Args:
            text: Message body (Markdown supported, auto-escaped).
            inline_keyboard: List of button rows. Each row is a list of dicts:
                [{"text": "✅ Aprobar", "callback_data": "approve:abc-123"}]
            chat_id: Override chat ID (defaults to TELEGRAM_CHAT_ID).
            parse_mode: "Markdown" or "HTML". "Markdown" auto-escapes.

        Returns:
            Telegram API result dict on success (contains message_id, chat, etc),
            or None on failure. Caller can persist message_id for later editMessageText.
        """
        if not self._enabled:
            logger.info("hitl_notification_skipped", reason="notifier_disabled")
            return None

        target_chat_id = chat_id or self._default_chat_id
        if not target_chat_id:
            logger.warning("no_chat_id", flow="hitl")
            return None

        url = f"{TELEGRAM_API_BASE}{self._bot_token}/sendMessage"
        safe_text = _escape_telegram_markdown(text) if parse_mode == "Markdown" else text

        payload = {
            "chat_id": target_chat_id,
            "text": safe_text[:4096],
            "parse_mode": parse_mode,
            "reply_markup": {"inline_keyboard": inline_keyboard},
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(url, json=payload)
            data = response.json() if response.status_code == 200 else {}
            if response.status_code == 200 and data.get("ok"):
                logger.info(
                    "telegram_hitl_sent",
                    chat_id=target_chat_id,
                    message_id=data["result"].get("message_id"),
                )
                return data["result"]
            # Markdown fallback for keyboard messages
            if (
                response.status_code == 200
                and "can't parse" in data.get("description", "").lower()
                and parse_mode == "Markdown"
            ):
                payload.pop("parse_mode", None)
                payload["text"] = text[:4096]
                async with httpx.AsyncClient(timeout=15) as client:
                    response = await client.post(url, json=payload)
                data = response.json() if response.status_code == 200 else {}
                if response.status_code == 200 and data.get("ok"):
                    return data["result"]
            logger.error(
                "telegram_hitl_failed",
                status=response.status_code,
                description=data.get("description", ""),
            )
            return None
        except Exception as e:
            logger.error("telegram_hitl_exception", error=str(e))
            return None

    async def answer_callback(
        self,
        callback_query_id: str,
        text: str = "",
        show_alert: bool = False,
    ) -> bool:
        """Acknowledge a callback_query (removes loading spinner). MUST be called within ~10s."""
        if not self._enabled:
            return False
        url = f"{TELEGRAM_API_BASE}{self._bot_token}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text[:200]
        if show_alert:
            payload["show_alert"] = True
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=payload)
            return response.status_code == 200 and response.json().get("ok", False)
        except Exception as e:
            logger.error("telegram_answer_callback_failed", error=str(e))
            return False

    async def edit_message_text(
        self,
        chat_id: str,
        message_id: int,
        text: str,
        parse_mode: str = "Markdown",
        remove_keyboard: bool = True,
    ) -> bool:
        """Edit an existing message (typically to replace HITL prompt with resolution)."""
        if not self._enabled:
            return False
        url = f"{TELEGRAM_API_BASE}{self._bot_token}/editMessageText"
        safe_text = _escape_telegram_markdown(text) if parse_mode == "Markdown" else text
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": safe_text[:4096],
            "parse_mode": parse_mode,
        }
        if remove_keyboard:
            payload["reply_markup"] = {"inline_keyboard": []}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(url, json=payload)
            data = response.json() if response.status_code == 200 else {}
            if response.status_code == 200 and data.get("ok"):
                return True
            if (
                response.status_code == 200
                and "can't parse" in data.get("description", "").lower()
                and parse_mode == "Markdown"
            ):
                payload.pop("parse_mode", None)
                payload["text"] = text[:4096]
                async with httpx.AsyncClient(timeout=15) as client:
                    response = await client.post(url, json=payload)
                return response.status_code == 200 and response.json().get("ok", False)
            logger.error("telegram_edit_failed", status=response.status_code, description=data.get("description", ""))
            return False
        except Exception as e:
            logger.error("telegram_edit_exception", error=str(e))
            return False

    async def send_proposal_for_hitl(
        self,
        proposal_id: str,
        action_type: str,
        risk_level: str,
        target: str,
        reason: str,
        cost_estimate_usd: float = 0.0,
        expires_at: str = "",
        chat_id: Optional[str] = None,
    ) -> Optional[dict]:
        """High-level HITL: send a write proposal to Alfredo with Aprobar/Rechazar buttons."""
        risk_emoji = {
            "low": "\u26aa",
            "medium": "\U0001f7e1",
            "high": "\U0001f7e0",
            "critical": "\U0001f534",
        }.get(risk_level.lower(), "\u2753")

        action_emoji = {
            "db_write": "\U0001f4be",
            "code_commit": "\U0001f4dd",
            "external_api_call": "\U0001f310",
        }.get(action_type, "\u2699\ufe0f")

        text_parts = [
            f"{action_emoji} *Propuesta de escritura del Embri\u00f3n*",
            "",
            f"{risk_emoji} *Riesgo:* {risk_level}",
            f"*Tipo:* `{action_type}`",
            f"*Target:* `{target[:120]}`",
            f"*Razon:* {reason[:600]}",
        ]
        if cost_estimate_usd > 0:
            text_parts.append(f"*Costo estimado:* ${cost_estimate_usd:.4f} USD")
        if expires_at:
            text_parts.append(f"*Expira:* {expires_at}")
        text_parts.append("")
        text_parts.append(f"`ID: {proposal_id}`")

        text = "\n".join(text_parts)

        keyboard = [
            [
                {"text": "\u2705 Aprobar", "callback_data": f"approve:{proposal_id}"},
                {"text": "\u274c Rechazar", "callback_data": f"reject:{proposal_id}"},
            ]
        ]

        return await self.send_with_keyboard(
            text=text,
            inline_keyboard=keyboard,
            chat_id=chat_id,
            parse_mode="Markdown",
        )

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
