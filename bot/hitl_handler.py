"""
El Monstruo — HITL Handler for Bot Integration (Sprint 21)
==========================================================
Provides get_pending_reviews() for the /v1/hitl/pending endpoint.

Previously this module was dead code (aiogram-based, incompatible).
Sprint 21 rewrites it as a thin bridge that queries the LangGraph
checkpointer for runs stuck in AWAITING_HUMAN status.

The real HITL logic lives in kernel/hitl.py (interrupt/Command).
This module only provides the pending-reviews query for the API.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("monstruo.bot.hitl_handler")

# ── In-memory pending reviews store ────────────────────────────────
# Populated by the kernel when a run hits AWAITING_HUMAN status.
# Cleared when the run is resumed via /v1/feedback or /v1/step.
_pending_reviews: dict[str, dict[str, Any]] = {}


def add_pending_review(run_id: str, payload: dict[str, Any]) -> None:
    """Register a run as pending HITL review."""
    _pending_reviews[run_id] = payload
    logger.info("hitl_pending_added", extra={"run_id": run_id})


def remove_pending_review(run_id: str) -> None:
    """Remove a run from pending reviews (after approval/rejection)."""
    _pending_reviews.pop(run_id, None)
    logger.info("hitl_pending_removed", extra={"run_id": run_id})


def get_pending_reviews() -> dict[str, dict[str, Any]]:
    """
    Return all pending HITL reviews.
    Used by /v1/hitl/pending endpoint and Telegram bot polling.
    """
    return dict(_pending_reviews)


def get_pending_count() -> int:
    """Return count of pending reviews."""
    return len(_pending_reviews)
