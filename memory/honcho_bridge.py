"""
El Monstruo — Honcho Bridge (Sprint 17 → 18)
========================================
Dialectic User Modeling via honcho-ai SDK.

Honcho provides persistent user profiles with preference learning.
We use it to:
  1. Store user interaction summaries after each conversation (memory_write)
  2. Retrieve user profile + preferences at conversation start (intake)
  3. Build a richer System Prompt with user context

License: SDK is Apache-2.0 (safe). Server is AGPL-3.0 (we don't run it).
Pattern: Same as MongoDB (server SSPL, driver Apache-2.0).

Validated against: honcho-ai==2.1.1 (PyPI latest 2026-04-20)
Reference: https://github.com/plastic-labs/honcho

Integration points:
    intake node       → get_user_context() → inject into system prompt
    memory_write node → update_user_model() → send interaction summary

Principio: Honcho es un servicio externo. Falla silenciosamente, nunca bloquea.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import structlog

logger = structlog.get_logger("memory.honcho")

# ── Honcho Client Singleton ────────────────────────────────────────────

_honcho_client = None
_honcho_app_id = None


async def _get_client():
    """Lazy-initialize the Honcho client."""
    global _honcho_client, _honcho_app_id

    if _honcho_client is not None:
        return _honcho_client, _honcho_app_id

    api_key = os.environ.get("HONCHO_API_KEY")
    base_url = os.environ.get("HONCHO_BASE_URL", "https://api.honcho.dev")
    app_name = os.environ.get("HONCHO_APP_NAME", "el-monstruo")

    if not api_key:
        logger.debug("honcho_disabled", reason="HONCHO_API_KEY not set")
        return None, None

    try:
        from honcho import Honcho

        client = Honcho(api_key=api_key, base_url=base_url)

        # Get or create the app
        apps = client.apps.list(name=app_name)
        app = None
        for a in apps:
            if a.name == app_name:
                app = a
                break

        if not app:
            app = client.apps.create(name=app_name)
            logger.info("honcho_app_created", app_name=app_name, app_id=str(app.id))
        else:
            logger.info("honcho_app_found", app_name=app_name, app_id=str(app.id))

        _honcho_client = client
        _honcho_app_id = str(app.id)
        return client, _honcho_app_id

    except Exception as e:
        logger.warning("honcho_init_failed", error=str(e))
        return None, None


# ── Public API ──────────────────────────────────────────────────────────

async def get_user_context(user_id: str = "alfredo") -> dict[str, Any]:
    """
    Retrieve user context from Honcho for System Prompt injection.

    Called by intake node at the start of each conversation.
    Returns a dict with user preferences, interaction patterns, etc.

    NEVER blocks the main flow — returns empty dict on failure.
    """
    try:
        client, app_id = await _get_client()
        if not client or not app_id:
            return {"honcho_active": False}

        # Get or create user
        users = client.apps.users.list(app_id=app_id, filter={"name": user_id})
        user = None
        for u in users:
            if u.name == user_id:
                user = u
                break

        if not user:
            user = client.apps.users.create(app_id=app_id, name=user_id)
            logger.info("honcho_user_created", user_id=user_id)
            return {
                "honcho_active": True,
                "user_id": user_id,
                "profile": {},
                "preferences": {},
                "interaction_count": 0,
            }

        # Get user metadata (preferences, patterns)
        metadata = user.metadata if hasattr(user, "metadata") and user.metadata else {}

        # Get recent sessions for context
        sessions = client.apps.users.sessions.list(
            app_id=app_id,
            user_id=str(user.id),
        )
        session_count = 0
        for _ in sessions:
            session_count += 1
            if session_count >= 100:
                break

        logger.info(
            "honcho_context_retrieved",
            user_id=user_id,
            has_metadata=bool(metadata),
            session_count=session_count,
        )

        return {
            "honcho_active": True,
            "user_id": user_id,
            "profile": metadata.get("profile", {}),
            "preferences": metadata.get("preferences", {}),
            "interaction_count": session_count,
            "communication_style": metadata.get("communication_style", ""),
            "expertise_areas": metadata.get("expertise_areas", []),
        }

    except Exception as e:
        logger.warning("honcho_get_context_failed", user_id=user_id, error=str(e))
        return {"honcho_active": False, "error": str(e)}


async def update_user_model(
    user_id: str = "alfredo",
    interaction_summary: str = "",
    preferences_update: Optional[dict[str, Any]] = None,
    thread_id: str = "",
) -> dict[str, Any]:
    """
    Update user model in Honcho after a conversation.

    Called by memory_write node at the end of each conversation.
    Sends interaction summary for Honcho to learn from.

    NEVER blocks the main flow — returns status dict on failure.
    """
    try:
        client, app_id = await _get_client()
        if not client or not app_id:
            return {"updated": False, "reason": "honcho_disabled"}

        # Get or create user
        users = client.apps.users.list(app_id=app_id, filter={"name": user_id})
        user = None
        for u in users:
            if u.name == user_id:
                user = u
                break

        if not user:
            user = client.apps.users.create(app_id=app_id, name=user_id)

        # Create a new session for this interaction
        session = client.apps.users.sessions.create(
            app_id=app_id,
            user_id=str(user.id),
            metadata={
                "thread_id": thread_id,
                "source": "el-monstruo-kernel",
            },
        )

        # Add the interaction as messages
        if interaction_summary:
            client.apps.users.sessions.messages.create(
                app_id=app_id,
                user_id=str(user.id),
                session_id=str(session.id),
                content=interaction_summary,
                is_user=False,  # This is the assistant's summary
            )

        # Update user metadata with preferences if provided
        if preferences_update:
            existing_metadata = user.metadata if hasattr(user, "metadata") and user.metadata else {}
            existing_prefs = existing_metadata.get("preferences", {})
            existing_prefs.update(preferences_update)
            existing_metadata["preferences"] = existing_prefs

            client.apps.users.update(
                app_id=app_id,
                user_id=str(user.id),
                metadata=existing_metadata,
            )

        logger.info(
            "honcho_user_updated",
            user_id=user_id,
            thread_id=thread_id,
            has_summary=bool(interaction_summary),
            has_prefs=bool(preferences_update),
        )

        return {
            "updated": True,
            "session_id": str(session.id),
            "user_id": user_id,
        }

    except Exception as e:
        logger.warning(
            "honcho_update_failed",
            user_id=user_id,
            error=str(e),
        )
        return {"updated": False, "error": str(e)}


async def get_stats() -> dict[str, Any]:
    """Alias for get_honcho_status (used by /v1/memory/status)."""
    return await get_honcho_status()


async def get_honcho_status() -> dict[str, Any]:
    """Return Honcho connection status for health checks."""
    try:
        client, app_id = await _get_client()
        if not client:
            return {"active": False, "reason": "not_configured"}

        return {
            "active": True,
            "app_id": app_id,
            "sdk_version": "2.1.1",
        }
    except Exception as e:
        return {"active": False, "error": str(e)}
