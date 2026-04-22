"""
Honcho Bridge — HTTP-Only Dialectic User Modeling for El Monstruo
Sprint 25 | v0.18.0-sprint25

Architecture:
  - Honcho provides persistent user profiles + preference learning
  - Self-hosted on Railway: honcho-railway.railway.internal:8000
  - API: Honcho v3.0.6 (validated via /openapi.json 2026-04-22)
  - Auth: disabled (AUTH_USE_AUTH=false on Railway)

Sprint 25 Migration (CRITICAL):
  - BEFORE: honcho-ai==2.1.1 SDK (old v1 API: /v1/apps/{app_id}/users/...)
    → SDK used AGPL-3.0 server code patterns, contamination risk
    → v1 endpoints returned 404 on our v3 server
  - AFTER: Pure httpx against Honcho v3 REST API
    → No SDK dependency, no AGPL contamination
    → Validated endpoints from /openapi.json

Honcho v3 API mapping (validated 2026-04-22):
  - Apps → Workspaces: POST /v3/workspaces {id: "el-monstruo"}
  - Users → Peers: POST /v3/workspaces/{ws_id}/peers {id: "user_xxx"}
  - Sessions: POST /v3/workspaces/{ws_id}/sessions {id: "session_xxx"}
  - Messages: POST /v3/workspaces/{ws_id}/sessions/{sess_id}/messages
    Body: {messages: [{content: "...", peer_id: "..."}]}
  - Peer context: GET /v3/workspaces/{ws_id}/peers/{peer_id}/context
  - Session context: GET /v3/workspaces/{ws_id}/sessions/{sess_id}/context

Integration points:
    intake node       → get_user_context() → inject into system prompt
    memory_write node → update_user_model() → send interaction summary

Principio: Honcho es un servicio externo. Falla silenciosamente, nunca bloquea.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

import httpx

logger = logging.getLogger("monstruo.memory.honcho")

# ── Configuration ─────────────────────────────────────────────────────

_BASE_URL: str = os.getenv(
    "HONCHO_BASE_URL",
    "http://honcho-railway.railway.internal:8000",
)
_WORKSPACE_ID: str = os.getenv("HONCHO_WORKSPACE_ID", "el-monstruo")
_TIMEOUT: float = float(os.getenv("HONCHO_TIMEOUT", "10"))

# ── Lazy client ───────────────────────────────────────────────────────

_client: httpx.AsyncClient | None = None
_workspace_ready: bool = False
_init_error: str | None = None


def _get_client() -> httpx.AsyncClient:
    """Get or create the shared httpx async client."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=_BASE_URL,
            timeout=_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )
    return _client


# ── Workspace (was "App") ─────────────────────────────────────────────


async def ensure_workspace() -> bool:
    """
    Ensure the workspace exists in Honcho. Creates it if needed.
    Called during kernel lifespan startup.

    Honcho v3: POST /v3/workspaces with {id: workspace_name}
    This is a "get or create" endpoint — idempotent.
    """
    global _workspace_ready, _init_error

    try:
        client = _get_client()
        resp = await client.post(
            "/v3/workspaces",
            json={"id": _WORKSPACE_ID},
        )

        if resp.status_code in (200, 201):
            _workspace_ready = True
            _init_error = None
            data = resp.json()
            logger.info(
                "honcho_workspace_ready",
                extra={
                    "workspace_id": _WORKSPACE_ID,
                    "created_at": data.get("created_at"),
                },
            )
            return True
        else:
            _init_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
            logger.warning(
                "honcho_workspace_failed",
                extra={"status": resp.status_code, "body": resp.text[:200]},
            )
            return False

    except Exception as exc:
        _init_error = f"{type(exc).__name__}: {exc}"
        logger.warning("honcho_workspace_error", extra={"error": str(exc)})
        return False


# ── Peers (was "Users") ───────────────────────────────────────────────


async def _ensure_peer(peer_id: str, metadata: Optional[dict] = None) -> dict | None:
    """
    Get or create a peer (user) in the workspace.

    Honcho v3: POST /v3/workspaces/{ws_id}/peers {id: peer_id, metadata: {...}}
    """
    if not _workspace_ready:
        await ensure_workspace()
        if not _workspace_ready:
            return None

    try:
        client = _get_client()
        body: dict[str, Any] = {"id": peer_id}
        if metadata:
            body["metadata"] = metadata

        resp = await client.post(
            f"/v3/workspaces/{_WORKSPACE_ID}/peers",
            json=body,
        )

        if resp.status_code in (200, 201):
            return resp.json()
        else:
            logger.warning(
                "honcho_peer_failed",
                extra={"peer_id": peer_id, "status": resp.status_code},
            )
            return None

    except Exception as exc:
        logger.warning("honcho_peer_error", extra={"error": str(exc)})
        return None


# ── Public API (backward-compatible signatures) ───────────────────────


async def get_user_context(user_id: str = "alfredo") -> dict[str, Any]:
    """
    Retrieve user context from Honcho for System Prompt injection.

    Called by intake node at the start of each conversation.
    Returns a dict with user preferences, interaction patterns, etc.

    Sprint 25: Uses Honcho v3 peer context endpoint.
    NEVER blocks the main flow — returns empty dict on failure.
    """
    try:
        # Ensure peer exists
        peer = await _ensure_peer(user_id)
        if not peer:
            return {"honcho_active": False}

        # Get peer context (dialectic user model)
        client = _get_client()
        resp = await client.get(
            f"/v3/workspaces/{_WORKSPACE_ID}/peers/{user_id}/context",
        )

        context_text = ""
        if resp.status_code == 200:
            data = resp.json()
            context_text = data.get("context", "") if isinstance(data, dict) else str(data)

        # Get peer card (structured profile)
        card = {}
        try:
            card_resp = await client.get(
                f"/v3/workspaces/{_WORKSPACE_ID}/peers/{user_id}/card",
            )
            if card_resp.status_code == 200:
                card = card_resp.json()
        except Exception:
            pass  # Card is optional

        logger.info(
            "honcho_context_retrieved",
            extra={
                "user_id": user_id,
                "has_context": bool(context_text),
                "has_card": bool(card),
            },
        )

        return {
            "honcho_active": True,
            "user_id": user_id,
            "context": context_text,
            "card": card,
            "profile": card.get("metadata", {}).get("profile", {}),
            "preferences": card.get("metadata", {}).get("preferences", {}),
        }

    except Exception as e:
        logger.warning("honcho_get_context_failed", extra={"user_id": user_id, "error": str(e)})
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
    Sends interaction summary as a message in a Honcho session.

    Sprint 25: Uses Honcho v3 sessions + messages endpoints.
    NEVER blocks the main flow — returns status dict on failure.
    """
    try:
        # Ensure peer exists
        peer = await _ensure_peer(user_id)
        if not peer:
            return {"updated": False, "reason": "honcho_disabled"}

        client = _get_client()

        # Create a session for this interaction
        session_id = thread_id or f"interaction-{user_id}"
        sess_resp = await client.post(
            f"/v3/workspaces/{_WORKSPACE_ID}/sessions",
            json={
                "id": session_id,
                "peers": [user_id],
                "metadata": {
                    "thread_id": thread_id,
                    "source": "el-monstruo-kernel",
                },
            },
        )

        if sess_resp.status_code not in (200, 201):
            return {
                "updated": False,
                "reason": f"session_create_failed: {sess_resp.status_code}",
            }

        session = sess_resp.json()
        actual_session_id = session.get("id", session_id)

        # Store the interaction summary as a message
        if interaction_summary:
            msg_resp = await client.post(
                f"/v3/workspaces/{_WORKSPACE_ID}/sessions/{actual_session_id}/messages",
                json={
                    "messages": [{
                        "content": interaction_summary,
                        "peer_id": user_id,
                        "metadata": {"type": "interaction_summary"},
                    }],
                },
            )

            if msg_resp.status_code not in (200, 201):
                logger.warning(
                    "honcho_message_failed",
                    extra={"status": msg_resp.status_code},
                )

        # Update peer metadata with preferences if provided
        if preferences_update:
            await client.put(
                f"/v3/workspaces/{_WORKSPACE_ID}/peers/{user_id}",
                json={"metadata": {"preferences": preferences_update}},
            )

        logger.info(
            "honcho_user_updated",
            extra={
                "user_id": user_id,
                "thread_id": thread_id,
                "has_summary": bool(interaction_summary),
                "has_prefs": bool(preferences_update),
            },
        )

        return {
            "updated": True,
            "session_id": actual_session_id,
            "user_id": user_id,
        }

    except Exception as e:
        logger.warning(
            "honcho_update_failed",
            extra={"user_id": user_id, "error": str(e)},
        )
        return {"updated": False, "error": str(e)}


# ── Health / Stats ────────────────────────────────────────────────────


async def get_stats() -> dict[str, Any]:
    """Return Honcho bridge status for health checks."""
    return await get_honcho_status()


async def get_honcho_status() -> dict[str, Any]:
    """Return Honcho connection status for health checks."""
    try:
        client = _get_client()
        resp = await client.get("/health")

        if resp.status_code == 200:
            server_health = resp.json()
            return {
                "active": _workspace_ready,
                "workspace": _WORKSPACE_ID,
                "workspace_ready": _workspace_ready,
                "server_health": server_health,
                "base_url": _BASE_URL,
                "transport": "httpx",
                "api_version": "v3",
            }
        else:
            return {
                "active": False,
                "reason": f"health returned {resp.status_code}",
            }

    except Exception as e:
        return {
            "active": False,
            "error": str(e),
            "init_error": _init_error,
        }


async def close():
    """Close the httpx client. Called during kernel shutdown."""
    global _client, _workspace_ready
    if _client:
        await _client.aclose()
        _client = None
    _workspace_ready = False
