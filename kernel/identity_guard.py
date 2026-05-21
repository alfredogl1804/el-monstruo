"""
OPP-NB-023 R1 — Identity Guard: Anonymous User Context Resolution

This module provides a minimal guard that prevents `user_id="anonymous"` from
being silently treated as a valid runtime identity. It does NOT implement a
full identity/auth system — it only ensures that anonymous is explicitly
marked as UNRESOLVED and that downstream code can detect and handle it.

Scope:
  - Defines ANONYMOUS_SENTINEL and UNRESOLVED_USER_CONTEXT constants.
  - Provides `resolve_user_id()` to normalize and classify user_id values.
  - Provides `is_anonymous_blocked()` to check if a user_id is blocked.
  - Provides `require_resolved_user()` to raise if user_id is unresolved.

Does NOT:
  - Access Supabase, DB, memory, Memento, Anti-Dory, secrets, or runtime_events.
  - Implement auth, RLS, or user model.
  - Canonize anonymous or any identity.
  - Deploy, merge, or modify CI/gates.

Sprint: OPP-NB-023 R1
Branch: r1/opp-nb-023-anonymous-guard
Status: R1 DRAFT — NOT CANON — NOT RUNTIME until T1 approval
"""

from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────

ANONYMOUS_SENTINEL = "anonymous"
"""The string value that Sprint 29 DT-8 introduced as a replacement for
hardcoded 'alfredo'. This value is NOT a valid runtime identity."""

UNRESOLVED_USER_CONTEXT = "UNRESOLVED_USER_CONTEXT"
"""Explicit marker for user_id values that have not been resolved to a
real identity. Downstream code should treat this as 'no identity available'."""

BLOCKED_USER_IDS = frozenset({
    "anonymous",
    "",
    "null",
    "undefined",
    "none",
    "default",
})
"""Set of user_id values that are BLOCKED from being treated as valid
runtime identities. These are drift artifacts, not real users."""


# ─── Enums ────────────────────────────────────────────────────────────────────

class UserIdStatus(str, Enum):
    """Classification of a user_id value."""
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    BLOCKED = "BLOCKED"


# ─── Core Functions ───────────────────────────────────────────────────────────

def resolve_user_id(user_id: Optional[str]) -> tuple[str, UserIdStatus]:
    """
    Normalize and classify a user_id value.

    Returns:
        Tuple of (normalized_user_id, status)

    Examples:
        >>> resolve_user_id("alfredo")
        ("alfredo", UserIdStatus.RESOLVED)
        >>> resolve_user_id("anonymous")
        ("UNRESOLVED_USER_CONTEXT", UserIdStatus.BLOCKED)
        >>> resolve_user_id(None)
        ("UNRESOLVED_USER_CONTEXT", UserIdStatus.UNRESOLVED)
        >>> resolve_user_id("")
        ("UNRESOLVED_USER_CONTEXT", UserIdStatus.BLOCKED)
    """
    if user_id is None:
        logger.debug("identity_guard: user_id is None → UNRESOLVED")
        return UNRESOLVED_USER_CONTEXT, UserIdStatus.UNRESOLVED

    normalized = user_id.strip().lower()

    if normalized in BLOCKED_USER_IDS:
        logger.warning(
            "identity_guard: blocked user_id detected",
            extra={"original_value": user_id, "normalized": normalized}
        )
        return UNRESOLVED_USER_CONTEXT, UserIdStatus.BLOCKED

    # Valid user_id — return as-is (preserving original case)
    return user_id, UserIdStatus.RESOLVED


def is_anonymous_blocked(user_id: Optional[str]) -> bool:
    """
    Quick check: is this user_id in the blocked set?

    This is the minimal guard. Use it at decision points where anonymous
    should not be silently accepted.
    """
    if user_id is None:
        return True
    return user_id.strip().lower() in BLOCKED_USER_IDS


def require_resolved_user(user_id: Optional[str], context: str = "") -> str:
    """
    Assert that user_id is resolved. Raises ValueError if blocked/unresolved.

    Use this at critical paths where anonymous MUST NOT proceed.

    Args:
        user_id: The user_id to validate.
        context: Optional description of where this check is happening.

    Returns:
        The validated user_id if resolved.

    Raises:
        ValueError: If user_id is blocked or unresolved.
    """
    resolved_id, status = resolve_user_id(user_id)

    if status != UserIdStatus.RESOLVED:
        msg = (
            f"identity_guard: BLOCKED — user_id='{user_id}' is {status.value}. "
            f"Context: {context or 'unspecified'}. "
            f"This path requires a resolved user identity."
        )
        logger.error(msg)
        raise ValueError(msg)

    return resolved_id


# ─── Annotation Helper ────────────────────────────────────────────────────────

def annotate_user_id(user_id: Optional[str]) -> dict:
    """
    Produce a structured annotation for logging/observability.

    Returns a dict suitable for inclusion in event envelopes or logs.
    """
    resolved_id, status = resolve_user_id(user_id)
    return {
        "user_id_original": user_id,
        "user_id_resolved": resolved_id,
        "user_id_status": status.value,
        "is_blocked": status != UserIdStatus.RESOLVED,
        "guard_version": "OPP-NB-023-R1",
    }
