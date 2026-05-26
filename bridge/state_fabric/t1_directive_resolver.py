"""
T1 Directive Resolver v0.1
Resolves T1 directives into scoring modifiers for embryo task selection.

Principle: Directives influence scoring. Directives NEVER authorize actions.
"""

import datetime
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
QUEUE_PATH = os.path.join(DIR, "t1_directive_queue.v0_1.json")
SCHEMA_PATH = os.path.join(DIR, "t1_directive_queue_schema.v0_1.json")


def load_t1_directives():
    """Load all directives from the queue file."""
    with open(QUEUE_PATH, "r") as f:
        data = json.load(f)
    return data.get("directives", [])


def validate_directive(directive):
    """
    Validate a directive against hard constraints.
    Returns (is_valid, errors).
    """
    errors = []

    # t1_verbatim must not be empty
    if not directive.get("t1_verbatim"):
        errors.append("MISSING_T1_VERBATIM")

    # may_authorize_actions must be false
    if directive.get("may_authorize_actions") is not False:
        errors.append("MAY_AUTHORIZE_ACTIONS_NOT_FALSE")

    # no_r1 must be true
    if directive.get("no_r1") is not True:
        errors.append("NO_R1_NOT_TRUE")

    # no_canon must be true
    if directive.get("no_canon") is not True:
        errors.append("NO_CANON_NOT_TRUE")

    # no_memory_write must be true
    if directive.get("no_memory_write") is not True:
        errors.append("NO_MEMORY_WRITE_NOT_TRUE")

    # no_supabase must be true
    if directive.get("no_supabase") is not True:
        errors.append("NO_SUPABASE_NOT_TRUE")

    # requires_dispatcher must be true
    if directive.get("requires_dispatcher") is not True:
        errors.append("REQUIRES_DISPATCHER_NOT_TRUE")

    # forbidden_interpretations must be non-empty array
    fi = directive.get("forbidden_interpretations")
    if not isinstance(fi, list) or len(fi) == 0:
        errors.append("MISSING_FORBIDDEN_INTERPRETATIONS")

    # target_embryos must be non-empty array
    te = directive.get("target_embryos")
    if not isinstance(te, list) or len(te) == 0:
        errors.append("MISSING_TARGET_EMBRYOS")

    # No secrets
    d_str = json.dumps(directive)
    secret_patterns = ["sk-", "sbp_", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "password=", "token="]
    for p in secret_patterns:
        if p in d_str:
            errors.append(f"SECRET_DETECTED: {p}")

    return (len(errors) == 0, errors)


def get_active_directives():
    """Return only ACTIVE directives that pass validation."""
    directives = load_t1_directives()
    active = []
    for d in directives:
        if d.get("status") != "ACTIVE":
            continue
        is_valid, _ = validate_directive(d)
        if not is_valid:
            continue
        # Check TTL/expiry
        expires = d.get("expires_at")
        if expires:
            try:
                exp_dt = datetime.datetime.fromisoformat(expires.replace("Z", "+00:00"))
                now = datetime.datetime.now(datetime.timezone.utc)
                if now > exp_dt:
                    continue
            except (ValueError, TypeError):
                pass
        active.append(d)
    return active


def resolve_directives_for_embryo(embryo_id):
    """Get active directives that target a specific embryo.

    Logic: scope=ALL_EMBRYOS means 'all embryos listed in target_embryos'.
    An embryo_id NOT in target_embryos never receives the directive,
    regardless of scope. This prevents unknown/unregistered embryos
    from receiving directives meant for the registered set.
    """
    active = get_active_directives()
    resolved = []
    for d in active:
        targets = d.get("target_embryos", [])
        if embryo_id in targets:
            resolved.append(d)
    return resolved


def compute_directive_weight(directive):
    """
    Compute the scoring weight of a directive.
    Higher priority = higher weight.
    Range: 1-10 maps to weight 0.5-5.0.
    """
    priority = directive.get("priority", 5)
    weight = priority * 0.5
    return weight


def apply_directive_to_task_scores(tasks, directives):
    """
    Apply directive influence to task scores.
    Returns list of (task, score_modifier, directive_id) tuples.

    Rules:
    - Directive can boost tasks aligned with focus/desired_outcome.
    - Directive can suppress tasks misaligned with focus.
    - Directive CANNOT convert DENY to ALLOW.
    - Directive CANNOT bypass Dispatcher.
    - Directive CANNOT change budget or provider allowlist.
    """
    modifiers = []

    for task in tasks:
        total_modifier = 0.0
        applied_directives = []

        for d in directives:
            weight = compute_directive_weight(d)
            d_type = d.get("directive_type", "")
            focus = d.get("focus", "").lower()
            desired = d.get("desired_outcome", "").lower()
            task_id = task.get("task_id", "").lower()
            task_purpose = task.get("purpose", "").lower()

            # STRATEGIC_GUIDANCE / FOCUS_SHIFT: boost tasks aligned with focus
            if d_type in ("STRATEGIC_GUIDANCE", "FOCUS_SHIFT", "PRIORITY_BOOST"):
                # Check alignment: task purpose contains keywords from focus/desired
                focus_keywords = [w for w in focus.split() if len(w) > 4]
                desired_keywords = [w for w in desired.split() if len(w) > 4]
                alignment = sum(1 for k in focus_keywords if k in task_purpose or k in task_id)
                alignment += sum(1 for k in desired_keywords if k in task_purpose or k in task_id)
                if alignment > 0:
                    total_modifier += weight * min(alignment, 3)
                    applied_directives.append(d["directive_id"])

            # PRIORITY_SUPPRESS / WHAT_NOT_TO_DO: penalize misaligned tasks
            elif d_type in ("PRIORITY_SUPPRESS", "WHAT_NOT_TO_DO"):
                # Check if task matches what NOT to do
                focus_keywords = [w for w in focus.split() if len(w) > 4]
                misalignment = sum(1 for k in focus_keywords if k in task_purpose or k in task_id)
                if misalignment > 0:
                    total_modifier -= weight * min(misalignment, 3)
                    applied_directives.append(d["directive_id"])

        modifiers.append(
            {"task_id": task.get("task_id"), "score_modifier": total_modifier, "applied_directives": applied_directives}
        )

    return modifiers


def detect_conflicting_directives(directives):
    """
    Detect directives that conflict with each other.
    Conflict = same target_embryos + opposing directive_types.
    """
    conflicts = []
    boost_types = {"FOCUS_SHIFT", "PRIORITY_BOOST", "STRATEGIC_GUIDANCE"}
    suppress_types = {"PRIORITY_SUPPRESS", "WHAT_NOT_TO_DO"}

    for i, d1 in enumerate(directives):
        for j, d2 in enumerate(directives):
            if i >= j:
                continue
            # Check if they target same embryos
            t1 = set(d1.get("target_embryos", []))
            t2 = set(d2.get("target_embryos", []))
            if not t1.intersection(t2):
                continue
            # Check if opposing types
            if (d1["directive_type"] in boost_types and d2["directive_type"] in suppress_types) or (
                d1["directive_type"] in suppress_types and d2["directive_type"] in boost_types
            ):
                conflicts.append((d1["directive_id"], d2["directive_id"]))

    return conflicts


def expire_old_directives():
    """
    Mark expired directives (past expires_at or exceeded ttl_cycles).
    Returns count of newly expired.
    """
    with open(QUEUE_PATH, "r") as f:
        data = json.load(f)

    now = datetime.datetime.now(datetime.timezone.utc)
    expired_count = 0

    for d in data["directives"]:
        if d["status"] != "ACTIVE":
            continue
        expires = d.get("expires_at")
        if expires:
            try:
                exp_dt = datetime.datetime.fromisoformat(expires.replace("Z", "+00:00"))
                if now > exp_dt:
                    d["status"] = "EXPIRED"
                    expired_count += 1
            except (ValueError, TypeError):
                pass

    if expired_count > 0:
        data["last_updated"] = now.isoformat()
        with open(QUEUE_PATH, "w") as f:
            json.dump(data, f, indent=2)

    return expired_count


def export_directive_snapshot():
    """Export a snapshot of the current directive queue state."""
    directives = load_t1_directives()
    active = [d for d in directives if d["status"] == "ACTIVE"]
    return {
        "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_directives": len(directives),
        "active_count": len(active),
        "expired_count": sum(1 for d in directives if d["status"] == "EXPIRED"),
        "paused_count": sum(1 for d in directives if d["status"] == "PAUSED"),
        "active_directive_ids": [d["directive_id"] for d in active],
        "total_priority_weight": sum(compute_directive_weight(d) for d in active),
    }
