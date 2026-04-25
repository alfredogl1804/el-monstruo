"""
Honcho Bridge — DISABLED (Sprint 26)

Sprint 26 Decision (Veredicto Cruzado Hilo B/C):
  - Honcho service DELETED from Railway (was exposing Swagger UI publicly)
  - AGPL-3.0 license contamination risk eliminated
  - All functions return disabled/empty status — no network calls
  - Bridge preserved as stub for backward compatibility with nodes.py

Timeline:
  - Sprint 25: Migrated from SDK to httpx (v0.18.0)
  - Sprint 26: Service deleted, bridge disabled (v0.19.0)
  - Future: Evaluate replacement (MemPalace + LightRAG cover user modeling)
"""

from __future__ import annotations

import logging
import warnings
from typing import Any, Optional

warnings.warn(
    "honcho_bridge deprecated since Sprint 26. Removal: Sprint 30.",
    DeprecationWarning,
    stacklevel=2,
)

logger = logging.getLogger("monstruo.memory.honcho")

_DISABLED_REASON = "honcho_service_deleted_sprint26"


async def ensure_workspace() -> bool:
    """No-op. Honcho service was deleted in Sprint 26."""
    logger.info("honcho_disabled", extra={"reason": _DISABLED_REASON})
    return False


async def get_user_context(user_id: str = "alfredo") -> dict[str, Any]:
    """Return empty context. Honcho service was deleted in Sprint 26."""
    return {"honcho_active": False, "reason": _DISABLED_REASON}


async def update_user_model(
    user_id: str = "alfredo",
    interaction_summary: str = "",
    preferences_update: Optional[dict[str, Any]] = None,
    thread_id: str = "",
) -> dict[str, Any]:
    """No-op. Honcho service was deleted in Sprint 26."""
    return {"updated": False, "reason": _DISABLED_REASON}


async def get_stats() -> dict[str, Any]:
    """Return disabled status for health checks."""
    return await get_honcho_status()


async def get_honcho_status() -> dict[str, Any]:
    """Return disabled status for health checks."""
    return {
        "active": False,
        "reason": _DISABLED_REASON,
        "note": "Service deleted from Railway. AGPL-3.0 contamination risk eliminated.",
    }


async def close():
    """No-op. No client to close."""
    pass
