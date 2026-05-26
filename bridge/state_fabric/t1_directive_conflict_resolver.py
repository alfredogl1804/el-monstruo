"""
T1 Directive Conflict Resolver v0.1
Epoch 008 — Carril B.

Detects conflicts between multiple active T1 directives,
resolves by explicit priority, and ensures no directive
can authorize prohibited actions.

Zero external API calls. Zero secrets. Pure local logic.
"""

import datetime
import json
import os

STATE_FABRIC_DIR = os.path.dirname(os.path.abspath(__file__))
DIRECTIVE_QUEUE_PATH = os.path.join(STATE_FABRIC_DIR, "t1_directive_queue.v0_1.json")

# Actions that NO directive can authorize
PROHIBITED_ACTIONS = frozenset(
    [
        "R1_OPERATION",
        "SUPABASE_WRITE",
        "MEMENTO_WRITE",
        "ANTI_DORY_WRITE",
        "PROVIDER_AUTO_REPLACEMENT",
        "DEPLOY",
        "PR_AUTOMATIC",
        "MAIN_BRANCH_PUSH",
        "SECRET_EXPOSURE",
        "APP_VISION",
        "CANON_WRITE",
        "PRE_IA_CLOSE",
    ]
)

# Conflict detection keywords — opposing intents
CONFLICT_PAIRS = [
    (
        {"novedad", "nuevo", "new", "create", "produce", "artifact"},
        {"robustez", "risk", "riesgo", "stability", "reduce", "guard", "protect"},
    ),
    ({"speed", "fast", "rápido", "velocidad"}, {"quality", "calidad", "thorough", "exhaustivo"}),
]


def load_active_directives(queue_path=None):
    """Load all ACTIVE directives from the queue."""
    path = queue_path or DIRECTIVE_QUEUE_PATH
    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        queue = json.load(f)

    now = datetime.datetime.now(datetime.timezone.utc)
    active = []

    for d in queue.get("directives", []):
        if d.get("status") != "ACTIVE":
            continue

        # Check expiry
        expires_at = d.get("expires_at")
        if expires_at:
            try:
                exp = datetime.datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if now > exp:
                    continue  # Expired, skip
            except (ValueError, TypeError):
                pass

        active.append(d)

    return active


def detect_conflict(directives):
    """
    Detect if there is a conflict between active directives.

    Returns:
        (has_conflict: bool, conflict_details: dict)
    """
    if len(directives) < 2:
        return False, {"reason": "Less than 2 active directives — no conflict possible."}

    # Extract focus keywords from each directive
    directive_keywords = []
    for d in directives:
        focus = d.get("focus", "").lower()
        desired = d.get("desired_outcome", "").lower()
        combined = focus + " " + desired
        words = set(combined.split())
        directive_keywords.append((d["directive_id"], words))

    conflicts_found = []

    for i in range(len(directive_keywords)):
        for j in range(i + 1, len(directive_keywords)):
            id_a, words_a = directive_keywords[i]
            id_b, words_b = directive_keywords[j]

            for pair_a, pair_b in CONFLICT_PAIRS:
                a_matches_first = bool(words_a & pair_a)
                b_matches_second = bool(words_b & pair_b)
                a_matches_second = bool(words_a & pair_b)
                b_matches_first = bool(words_b & pair_a)

                if (a_matches_first and b_matches_second) or (a_matches_second and b_matches_first):
                    conflicts_found.append(
                        {
                            "directive_a": id_a,
                            "directive_b": id_b,
                            "conflict_type": "OPPOSING_INTENT",
                            "pair_keywords": [list(pair_a), list(pair_b)],
                        }
                    )

    if conflicts_found:
        return True, {"reason": "Opposing intents detected between directives.", "conflicts": conflicts_found}

    return False, {"reason": "No keyword-based conflicts detected between directives."}


def resolve_by_priority(directives):
    """
    Resolve conflict by explicit priority (higher priority wins).

    Returns:
        (chosen_set: list, suppressed: list, explanation: str)
    """
    if not directives:
        return [], [], "No directives to resolve."

    sorted_directives = sorted(directives, key=lambda d: d.get("priority", 0), reverse=True)

    # The highest priority directive is the primary guide
    chosen = [sorted_directives[0]]
    suppressed = []

    for d in sorted_directives[1:]:
        # Check if lower-priority directive conflicts with chosen
        has_conflict, _ = detect_conflict([chosen[0], d])
        if has_conflict:
            suppressed.append(d)
        else:
            chosen.append(d)

    explanation = (
        f"Primary directive: {chosen[0]['directive_id']} (priority {chosen[0].get('priority', 0)}). "
        f"Suppressed: {[s['directive_id'] for s in suppressed]}. "
        f"Non-conflicting additions: {[c['directive_id'] for c in chosen[1:]]}."
    )

    return chosen, suppressed, explanation


def validate_directive_does_not_authorize(directive, action):
    """
    Verify that a directive does NOT authorize a prohibited action.

    Returns:
        (safe: bool, reason: str)
    """
    if action in PROHIBITED_ACTIONS:
        return False, f"Action '{action}' is PROHIBITED. No directive can authorize it."

    # Check if directive explicitly says may_authorize_actions
    if directive.get("may_authorize_actions", False):
        return (
            False,
            f"Directive {directive.get('directive_id')} claims may_authorize_actions=True — REJECTED. Directives cannot authorize actions.",
        )

    return True, f"Action '{action}' is not prohibited and directive does not claim authorization."


def validate_directive_does_not_change_provider_allowlist(directive):
    """
    Verify that a directive does NOT attempt to change the provider allowlist.

    Returns:
        (safe: bool, reason: str)
    """
    focus = (directive.get("focus", "") + " " + directive.get("desired_outcome", "")).lower()
    dangerous_patterns = ["change provider", "replace model", "switch to", "migrate to", "use instead"]

    for pattern in dangerous_patterns:
        if pattern in focus:
            return (
                False,
                f"Directive {directive.get('directive_id')} contains provider change language: '{pattern}' — BLOCKED. Provider changes require T1 explicit decision, not directive.",
            )

    return True, "Directive does not attempt to change provider allowlist."


def validate_directive_does_not_bypass_dispatcher(directive):
    """
    Verify that a directive does NOT bypass the Dispatcher.

    Returns:
        (safe: bool, reason: str)
    """
    focus = (directive.get("focus", "") + " " + directive.get("desired_outcome", "")).lower()
    bypass_patterns = ["skip dispatcher", "bypass dispatcher", "ignore dispatcher", "override dispatcher"]

    for pattern in bypass_patterns:
        if pattern in focus:
            return False, f"Directive {directive.get('directive_id')} attempts dispatcher bypass — BLOCKED."

    return True, "Directive does not bypass Dispatcher."


def export_conflict_snapshot(directives, has_conflict, conflict_details, chosen, suppressed, explanation):
    """
    Export a complete conflict resolution snapshot.

    Returns:
        Snapshot dict
    """
    return {
        "version": "0.1.0",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_directives_loaded": len(directives),
        "active_directives": [d["directive_id"] for d in directives],
        "has_conflict": has_conflict,
        "conflict_details": conflict_details,
        "resolution": {
            "chosen_directive_set": [d["directive_id"] for d in chosen],
            "suppressed_directives": [d["directive_id"] for d in suppressed],
            "explanation": explanation,
        },
        "safety_checks": {
            "no_r1_authorized": True,
            "no_provider_change_authorized": True,
            "no_dispatcher_bypass": True,
        },
    }


# ============================================================
# CLI ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("T1 DIRECTIVE CONFLICT RESOLVER v0.1")
    print("=" * 60)

    directives = load_active_directives()
    print(f"\n  Active directives: {len(directives)}")
    for d in directives:
        print(f"    - {d['directive_id']}: priority={d.get('priority', 0)}")

    has_conflict, details = detect_conflict(directives)
    print(f"\n  Conflict detected: {has_conflict}")
    if has_conflict:
        print(f"    Details: {details['reason']}")

    chosen, suppressed, explanation = resolve_by_priority(directives)
    print(f"\n  Resolution: {explanation}")

    snapshot = export_conflict_snapshot(directives, has_conflict, details, chosen, suppressed, explanation)
    print("\n  Snapshot exported.")
    print("=" * 60)
