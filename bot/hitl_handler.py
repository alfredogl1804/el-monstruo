"""
El Monstruo — Telegram HITL Handler v1.0
==========================================
Connects LangGraph interrupt() with Telegram inline keyboards.

When the kernel pauses for HITL review, this handler:
1. Receives the interrupt payload from the kernel
2. Formats it as a Telegram message with inline keyboard
3. Sends it to Alfredo's Telegram chat
4. Waits for callback_query (button press)
5. Calls POST /v1/feedback to resume the graph via Command(resume=...)

Architecture:
  Kernel interrupt() → hitl_handler.send_review() → Telegram inline keyboard
  Telegram callback → hitl_handler.process_callback() → POST /v1/feedback → Command(resume=...)

Dependencies: aiogram>=3.27.0, httpx
Validated: 14 abril 2026
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any, Optional

import structlog
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

logger = structlog.get_logger("bot.hitl")

# ── Configuration ──────────────────────────────────────────────────

KERNEL_API_URL = os.getenv("KERNEL_API_URL", "http://localhost:8000")
ADMIN_CHAT_ID = int(os.getenv("TELEGRAM_ADMIN_CHAT_ID", "0"))

# Timeout for HITL review (seconds). After this, auto-reject.
HITL_TIMEOUT_SECONDS = int(os.getenv("HITL_TIMEOUT_SECONDS", "300"))  # 5 min default

# ── Router ─────────────────────────────────────────────────────────

hitl_router = Router(name="hitl")

# In-memory store of pending reviews (run_id → review_data)
# In production, this should be in Redis or Supabase
_pending_reviews: dict[str, dict[str, Any]] = {}


# ── Risk Level Formatting ──────────────────────────────────────────

RISK_EMOJI = {
    "L1_SAFE": "🟢",
    "L2_CAUTION": "🟡",
    "L3_SENSITIVE": "🟠",
    "L4_CRITICAL": "🔴",
    "L5_FORBIDDEN": "⛔",
}

RISK_LABEL = {
    "L1_SAFE": "Safe",
    "L2_CAUTION": "Caution",
    "L3_SENSITIVE": "Sensitive",
    "L4_CRITICAL": "Critical",
    "L5_FORBIDDEN": "Forbidden",
}


# ── Send Review to Telegram ───────────────────────────────────────

async def send_hitl_review(
    bot: Any,
    chat_id: int,
    review_payload: dict[str, Any],
) -> Optional[Message]:
    """Send a HITL review request to Telegram with inline keyboard.

    Args:
        bot: aiogram Bot instance
        chat_id: Telegram chat ID to send the review to
        review_payload: The interrupt payload from LangGraph hitl_review node

    Returns:
        The sent Message, or None if sending failed
    """
    run_id = review_payload.get("run_id", "unknown")
    risk_level = review_payload.get("risk_level", "L2_CAUTION")
    reason = review_payload.get("reason", "Policy requires approval")
    intent = review_payload.get("intent", "unknown")
    message_preview = review_payload.get("message_preview", "")
    response_preview = review_payload.get("proposed_response_preview", "")
    envelope_summary = review_payload.get("action_envelope_summary")
    timestamp = review_payload.get("timestamp", datetime.now(timezone.utc).isoformat())

    risk_emoji = RISK_EMOJI.get(risk_level, "❓")
    risk_label = RISK_LABEL.get(risk_level, risk_level)

    # Build the review message
    lines = [
        f"{risk_emoji} <b>HITL Review Required</b> {risk_emoji}",
        "",
        f"<b>Risk:</b> {risk_label} ({risk_level})",
        f"<b>Intent:</b> {intent}",
        f"<b>Reason:</b> {reason}",
        "",
        f"<b>User message:</b>",
        f"<code>{_escape_html(message_preview[:300])}</code>",
    ]

    if response_preview:
        lines.extend([
            "",
            f"<b>Proposed response:</b>",
            f"<code>{_escape_html(response_preview[:500])}</code>",
        ])

    if envelope_summary:
        action_type = envelope_summary.get("action_type", "unknown")
        target = envelope_summary.get("target", {})
        resource = target.get("resource_kind", "unknown")
        resource_id = target.get("resource_id", "")
        operation = envelope_summary.get("operation", "unknown")
        lines.extend([
            "",
            f"<b>Action:</b> {action_type}",
            f"<b>Target:</b> {resource} ({resource_id})",
            f"<b>Operation:</b> {operation}",
        ])

    lines.extend([
        "",
        f"<i>Run: {run_id[:8]}... | {timestamp[:19]}</i>",
        f"<i>Auto-reject in {HITL_TIMEOUT_SECONDS // 60} min</i>",
    ])

    text = "\n".join(lines)

    # Build inline keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Approve",
                callback_data=f"hitl:approve:{run_id}",
            ),
            InlineKeyboardButton(
                text="❌ Reject",
                callback_data=f"hitl:reject:{run_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="✏️ Modify",
                callback_data=f"hitl:modify:{run_id}",
            ),
            InlineKeyboardButton(
                text="📋 Details",
                callback_data=f"hitl:details:{run_id}",
            ),
        ],
    ])

    try:
        msg = await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

        # Store pending review
        _pending_reviews[run_id] = {
            "message_id": msg.message_id,
            "chat_id": chat_id,
            "payload": review_payload,
            "sent_at": datetime.now(timezone.utc),
            "status": "pending",
        }

        # Schedule auto-reject timeout
        asyncio.create_task(_auto_reject_timeout(bot, run_id))

        logger.info(
            "hitl_review_sent",
            run_id=run_id,
            chat_id=chat_id,
            risk_level=risk_level,
        )

        return msg

    except Exception as e:
        logger.error("hitl_review_send_failed", run_id=run_id, error=str(e))
        return None


# ── Callback Query Handlers ────────────────────────────────────────

@hitl_router.callback_query(F.data.startswith("hitl:approve:"))
async def on_approve(callback: CallbackQuery):
    """Handle Approve button press."""
    run_id = callback.data.split(":", 2)[2]
    await _process_decision(callback, run_id, "approve")


@hitl_router.callback_query(F.data.startswith("hitl:reject:"))
async def on_reject(callback: CallbackQuery):
    """Handle Reject button press."""
    run_id = callback.data.split(":", 2)[2]
    await _process_decision(callback, run_id, "reject")


@hitl_router.callback_query(F.data.startswith("hitl:modify:"))
async def on_modify(callback: CallbackQuery):
    """Handle Modify button press — asks user to type modification."""
    run_id = callback.data.split(":", 2)[2]

    if run_id not in _pending_reviews:
        await callback.answer("Review expired or already processed", show_alert=True)
        return

    _pending_reviews[run_id]["status"] = "awaiting_modification"

    await callback.message.reply(
        f"✏️ <b>Send your modified response for run {run_id[:8]}...</b>\n\n"
        f"Type your modification and send it. It will replace the AI's response.",
        parse_mode="HTML",
    )
    await callback.answer("Type your modification below")


@hitl_router.callback_query(F.data.startswith("hitl:details:"))
async def on_details(callback: CallbackQuery):
    """Handle Details button press — show full review payload."""
    run_id = callback.data.split(":", 2)[2]

    review = _pending_reviews.get(run_id)
    if not review:
        await callback.answer("Review not found", show_alert=True)
        return

    payload = review["payload"]
    import json
    details_text = f"<b>Full Review Payload:</b>\n<pre>{_escape_html(json.dumps(payload, indent=2, default=str)[:3000])}</pre>"

    await callback.message.reply(details_text, parse_mode="HTML")
    await callback.answer("Details shown below")


@hitl_router.message(F.reply_to_message)
async def on_modification_text(message: Message):
    """Handle modification text sent as a reply to the modify prompt."""
    # Find pending review awaiting modification
    target_run_id = None
    for run_id, review in _pending_reviews.items():
        if review.get("status") == "awaiting_modification" and review.get("chat_id") == message.chat.id:
            target_run_id = run_id
            break

    if not target_run_id:
        return  # Not a modification reply, ignore

    modification_text = message.text
    await _process_decision(
        message,
        target_run_id,
        "modify",
        modification=modification_text,
        is_message=True,
    )


# ── Core Decision Processing ──────────────────────────────────────

async def _process_decision(
    event: CallbackQuery | Message,
    run_id: str,
    decision: str,
    modification: str | None = None,
    is_message: bool = False,
):
    """Process a HITL decision and send it to the kernel API."""
    import httpx

    review = _pending_reviews.get(run_id)
    if not review or review.get("status") == "processed":
        if isinstance(event, CallbackQuery):
            await event.answer("Review already processed", show_alert=True)
        return

    # Mark as processed
    review["status"] = "processed"
    review["decision"] = decision
    review["decided_at"] = datetime.now(timezone.utc)

    # Send feedback to kernel API
    feedback_payload = {
        "run_id": run_id,
        "action": decision,
        "user_id": "alfredo",
        "comment": f"Telegram HITL: {decision}",
    }
    if modification:
        feedback_payload["edited_response"] = modification

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{KERNEL_API_URL}/v1/feedback",
                json=feedback_payload,
            )
            result = resp.json()
            logger.info(
                "hitl_feedback_sent",
                run_id=run_id,
                decision=decision,
                api_status=resp.status_code,
                result=result,
            )
    except Exception as e:
        logger.error("hitl_feedback_failed", run_id=run_id, error=str(e))
        result = {"error": str(e)}

    # Update the original message to show the decision
    decision_emoji = {"approve": "✅", "reject": "❌", "modify": "✏️"}.get(decision, "❓")
    decision_text = f"\n\n{decision_emoji} <b>Decision: {decision.upper()}</b>"
    if modification:
        decision_text += f"\n<i>Modified response provided</i>"

    try:
        if isinstance(event, CallbackQuery):
            original_text = event.message.text or event.message.html_text or ""
            # Remove inline keyboard and append decision
            await event.message.edit_text(
                original_text + decision_text,
                parse_mode="HTML",
                reply_markup=None,  # Remove keyboard
            )
            await event.answer(f"Decision: {decision.upper()}")
        elif is_message:
            await event.reply(
                f"{decision_emoji} Modification applied for run {run_id[:8]}...",
                parse_mode="HTML",
            )
    except Exception as e:
        logger.warning("hitl_message_update_failed", error=str(e))

    # Clean up
    _pending_reviews.pop(run_id, None)


# ── Auto-Reject Timeout ───────────────────────────────────────────

async def _auto_reject_timeout(bot: Any, run_id: str):
    """Auto-reject a review after HITL_TIMEOUT_SECONDS if no response."""
    await asyncio.sleep(HITL_TIMEOUT_SECONDS)

    review = _pending_reviews.get(run_id)
    if not review or review.get("status") != "pending":
        return  # Already processed

    logger.warning("hitl_auto_reject", run_id=run_id, timeout=HITL_TIMEOUT_SECONDS)

    # Auto-reject via API
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"{KERNEL_API_URL}/v1/feedback",
                json={
                    "run_id": run_id,
                    "action": "reject",
                    "user_id": "system",
                    "comment": f"Auto-rejected after {HITL_TIMEOUT_SECONDS}s timeout",
                },
            )
    except Exception as e:
        logger.error("hitl_auto_reject_failed", run_id=run_id, error=str(e))

    # Update Telegram message
    review["status"] = "auto_rejected"
    try:
        await bot.edit_message_text(
            chat_id=review["chat_id"],
            message_id=review["message_id"],
            text=f"⏰ <b>Auto-rejected</b> (timeout: {HITL_TIMEOUT_SECONDS // 60} min)\n\n"
                 f"Run: {run_id[:8]}...",
            parse_mode="HTML",
        )
    except Exception:
        pass

    _pending_reviews.pop(run_id, None)


# ── Helpers ────────────────────────────────────────────────────────

def _escape_html(text: str) -> str:
    """Escape HTML special characters for Telegram HTML parse mode."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def get_pending_reviews() -> dict[str, dict[str, Any]]:
    """Get all pending HITL reviews (for API/debugging)."""
    return {
        run_id: {
            "status": review["status"],
            "sent_at": review["sent_at"].isoformat(),
            "risk_level": review["payload"].get("risk_level", "unknown"),
        }
        for run_id, review in _pending_reviews.items()
    }
