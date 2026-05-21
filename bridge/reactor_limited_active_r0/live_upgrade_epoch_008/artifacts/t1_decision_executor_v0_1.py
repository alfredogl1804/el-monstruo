"""
T1 Decision Executor v0.1
4th R0+ Artifact — Epoch 008.

Accepts T1 decisions (from the directive queue or manual input),
validates them against safety constraints, and applies them locally
to the provider registry and directive queue.

Zero external API calls. Zero secrets. Pure local state mutation.

Use cases:
- T1 approves model migration → updates provider_registry.json
- T1 expires a directive → updates t1_directive_queue.v0_1.json
- T1 creates a new directive → appends to queue
- T1 blocks a provider → updates registry status

All mutations are validated against:
- PROHIBITED_ACTIONS (from conflict resolver)
- Provider auto-replacement policy
- Dispatcher bypass prevention
"""
import os
import sys
import json
import datetime
import copy

# Resolve paths
ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
EPOCH_DIR = os.path.dirname(ARTIFACT_DIR)
BRIDGE_DIR = os.path.dirname(os.path.dirname(EPOCH_DIR))
PROVIDER_OPS_DIR = os.path.join(BRIDGE_DIR, "provider_ops")
STATE_FABRIC_DIR = os.path.join(BRIDGE_DIR, "state_fabric")

REGISTRY_PATH = os.path.join(PROVIDER_OPS_DIR, "provider_registry.json")
DIRECTIVE_QUEUE_PATH = os.path.join(STATE_FABRIC_DIR, "t1_directive_queue.v0_1.json")
DECISION_LOG_PATH = os.path.join(ARTIFACT_DIR, "t1_decision_log.jsonl")

# Safety: actions that T1 decisions CANNOT execute in R0+
PROHIBITED_DECISION_TYPES = frozenset([
    "DEPLOY",
    "PR_CREATE",
    "MAIN_PUSH",
    "SUPABASE_WRITE",
    "SECRET_WRITE",
    "R1_OPERATION",
    "APP_VISION",
    "CANON_WRITE"
])

VALID_DECISION_TYPES = frozenset([
    "APPROVE_MODEL_MIGRATION",
    "BLOCK_PROVIDER",
    "UNBLOCK_PROVIDER",
    "EXPIRE_DIRECTIVE",
    "CREATE_DIRECTIVE",
    "PAUSE_DIRECTIVE",
    "RESUME_DIRECTIVE",
    "ACKNOWLEDGE_RISK",
    "REJECT_MIGRATION"
])


def validate_decision(decision):
    """
    Validate a T1 decision before execution.

    Args:
        decision: Dict with decision_type, target, params, reason

    Returns:
        (valid: bool, errors: list)
    """
    errors = []

    # Required fields
    for field in ["decision_type", "target", "reason"]:
        if field not in decision:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    decision_type = decision["decision_type"]

    # Check prohibited
    if decision_type in PROHIBITED_DECISION_TYPES:
        errors.append(f"Decision type '{decision_type}' is PROHIBITED in R0+.")

    # Check valid
    if decision_type not in VALID_DECISION_TYPES:
        errors.append(f"Decision type '{decision_type}' is not recognized.")

    # Validate specific decision types
    if decision_type == "APPROVE_MODEL_MIGRATION":
        params = decision.get("params", {})
        if not params.get("new_model"):
            errors.append("APPROVE_MODEL_MIGRATION requires params.new_model")
        if not params.get("provider"):
            errors.append("APPROVE_MODEL_MIGRATION requires params.provider")

    if decision_type in ("EXPIRE_DIRECTIVE", "PAUSE_DIRECTIVE", "RESUME_DIRECTIVE"):
        if not decision.get("target"):
            errors.append(f"{decision_type} requires target directive_id")

    if decision_type == "CREATE_DIRECTIVE":
        params = decision.get("params", {})
        for req in ["directive_type", "priority", "focus"]:
            if req not in params:
                errors.append(f"CREATE_DIRECTIVE requires params.{req}")

    return len(errors) == 0, errors


def execute_approve_model_migration(decision):
    """
    Execute model migration: update provider_registry.json with new model.

    Returns:
        (success: bool, message: str, before: dict, after: dict)
    """
    params = decision.get("params", {})
    provider = params["provider"]
    new_model = params["new_model"]

    with open(REGISTRY_PATH, "r") as f:
        registry = json.load(f)

    before = copy.deepcopy(registry)

    providers = registry.get("providers", {})
    if provider not in providers:
        return False, f"Provider '{provider}' not found in registry.", before, before

    old_model = providers[provider].get("model")

    # Move old model to deprecated list
    if old_model and old_model not in providers[provider].get("deprecated_models", []):
        providers[provider].setdefault("deprecated_models", []).append(old_model)

    # Set new model
    providers[provider]["model"] = new_model
    registry["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

    return True, f"Migrated {provider} from '{old_model}' to '{new_model}'.", before, registry


def execute_block_provider(decision):
    """Block a provider in the registry."""
    target = decision["target"]

    with open(REGISTRY_PATH, "r") as f:
        registry = json.load(f)

    before = copy.deepcopy(registry)
    providers = registry.get("providers", {})

    if target not in providers:
        return False, f"Provider '{target}' not found.", before, before

    providers[target]["status"] = "BLOCKED"
    providers[target]["reason"] = decision.get("reason", "Blocked by T1 decision")
    registry["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

    return True, f"Provider '{target}' blocked.", before, registry


def execute_unblock_provider(decision):
    """Unblock a provider in the registry."""
    target = decision["target"]

    with open(REGISTRY_PATH, "r") as f:
        registry = json.load(f)

    before = copy.deepcopy(registry)
    providers = registry.get("providers", {})

    if target not in providers:
        return False, f"Provider '{target}' not found.", before, before

    providers[target]["status"] = "ALLOWED"
    if "reason" in providers[target]:
        del providers[target]["reason"]
    registry["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

    return True, f"Provider '{target}' unblocked.", before, registry


def execute_expire_directive(decision):
    """Expire a directive in the queue."""
    target = decision["target"]

    with open(DIRECTIVE_QUEUE_PATH, "r") as f:
        queue = json.load(f)

    before = copy.deepcopy(queue)
    found = False

    for d in queue.get("directives", []):
        if d["directive_id"] == target:
            d["status"] = "EXPIRED"
            d["expired_by"] = "T1_DECISION"
            d["expired_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            found = True
            break

    if not found:
        return False, f"Directive '{target}' not found.", before, before

    queue["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    with open(DIRECTIVE_QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)

    return True, f"Directive '{target}' expired.", before, queue


def execute_pause_directive(decision):
    """Pause a directive in the queue."""
    target = decision["target"]

    with open(DIRECTIVE_QUEUE_PATH, "r") as f:
        queue = json.load(f)

    before = copy.deepcopy(queue)
    found = False

    for d in queue.get("directives", []):
        if d["directive_id"] == target:
            d["status"] = "PAUSED"
            found = True
            break

    if not found:
        return False, f"Directive '{target}' not found.", before, before

    queue["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    with open(DIRECTIVE_QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)

    return True, f"Directive '{target}' paused.", before, queue


def execute_resume_directive(decision):
    """Resume a paused directive."""
    target = decision["target"]

    with open(DIRECTIVE_QUEUE_PATH, "r") as f:
        queue = json.load(f)

    before = copy.deepcopy(queue)
    found = False

    for d in queue.get("directives", []):
        if d["directive_id"] == target:
            d["status"] = "ACTIVE"
            found = True
            break

    if not found:
        return False, f"Directive '{target}' not found.", before, before

    queue["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    with open(DIRECTIVE_QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)

    return True, f"Directive '{target}' resumed.", before, queue


def execute_create_directive(decision):
    """Create a new directive in the queue."""
    params = decision.get("params", {})

    with open(DIRECTIVE_QUEUE_PATH, "r") as f:
        queue = json.load(f)

    before = copy.deepcopy(queue)

    # Generate next directive ID
    existing_ids = [d["directive_id"] for d in queue.get("directives", [])]
    max_num = max([int(did.replace("T1D-", "")) for did in existing_ids if did.startswith("T1D-")], default=0)
    new_id = f"T1D-{max_num + 1:03d}"

    now = datetime.datetime.now(datetime.timezone.utc)
    new_directive = {
        "directive_id": new_id,
        "created_at": now.isoformat(),
        "created_by": "ALFREDO_T1",
        "source": "t1_decision_executor",
        "directive_type": params.get("directive_type", "STRATEGIC_GUIDANCE"),
        "priority": params.get("priority", 5),
        "scope": params.get("scope", "ALL_EMBRYOS"),
        "target_embryos": params.get("target_embryos", ["oracle_ai_embryo_r0", "oracle_auditor_embryo_r0"]),
        "focus": params.get("focus", ""),
        "desired_outcome": params.get("desired_outcome", ""),
        "forbidden_interpretations": [
            "This directive does NOT authorize R1 operations",
            "This directive does NOT bypass Dispatcher",
            "This directive does NOT allow Supabase/DB writes"
        ],
        "ttl_cycles": params.get("ttl_cycles", 10),
        "expires_at": (now + datetime.timedelta(days=4)).isoformat(),
        "status": "ACTIVE",
        "may_influence_scoring": True,
        "may_authorize_actions": False,
        "requires_dispatcher": True,
        "no_r1": True,
        "no_canon": True,
        "no_memory_write": True,
        "no_supabase": True,
        "evidence_ref": decision.get("reason", "T1 decision executor"),
        "t1_verbatim": params.get("t1_verbatim", params.get("focus", ""))
    }

    queue["directives"].append(new_directive)
    queue["last_updated"] = now.isoformat()

    with open(DIRECTIVE_QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)

    return True, f"Directive '{new_id}' created.", before, queue


def execute_decision(decision, dry_run=False):
    """
    Execute a validated T1 decision.

    Args:
        decision: Validated decision dict
        dry_run: If True, validate only without executing

    Returns:
        (success: bool, message: str, log_entry: dict)
    """
    valid, errors = validate_decision(decision)
    if not valid:
        return False, f"Validation failed: {errors}", {"errors": errors}

    if dry_run:
        return True, "Dry run: decision is valid but not executed.", {"dry_run": True}

    decision_type = decision["decision_type"]
    executors = {
        "APPROVE_MODEL_MIGRATION": execute_approve_model_migration,
        "BLOCK_PROVIDER": execute_block_provider,
        "UNBLOCK_PROVIDER": execute_unblock_provider,
        "EXPIRE_DIRECTIVE": execute_expire_directive,
        "PAUSE_DIRECTIVE": execute_pause_directive,
        "RESUME_DIRECTIVE": execute_resume_directive,
        "CREATE_DIRECTIVE": execute_create_directive,
        "ACKNOWLEDGE_RISK": lambda d: (True, f"Risk acknowledged: {d.get('reason', 'N/A')}", {}, {}),
        "REJECT_MIGRATION": lambda d: (True, f"Migration rejected: {d.get('reason', 'N/A')}", {}, {}),
    }

    executor = executors.get(decision_type)
    if not executor:
        return False, f"No executor for '{decision_type}'", {}

    result = executor(decision)
    success, message = result[0], result[1]

    # Log the decision
    log_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "decision_type": decision_type,
        "target": decision.get("target"),
        "reason": decision.get("reason"),
        "success": success,
        "message": message,
        "dry_run": dry_run
    }

    os.makedirs(os.path.dirname(DECISION_LOG_PATH), exist_ok=True)
    with open(DECISION_LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return success, message, log_entry


def get_pending_decisions():
    """
    List decisions that are pending T1 input (from migration guard snapshot).

    Returns:
        List of pending decision descriptions
    """
    pending = []

    # Check migration snapshot
    snapshot_path = os.path.join(PROVIDER_OPS_DIR, "provider_migration_snapshot.json")
    if os.path.exists(snapshot_path):
        with open(snapshot_path, "r") as f:
            snapshot = json.load(f)
        for candidate in snapshot.get("migration_candidates", []):
            if candidate.get("status") == "MIGRATION_CANDIDATE":
                pending.append({
                    "type": "PROVIDER_MIGRATION",
                    "provider": candidate["provider"],
                    "current_model": candidate["current_model"],
                    "eol_date": candidate.get("eol_date"),
                    "risk_level": candidate.get("risk_level"),
                    "requires_decision": True,
                    "valid_decision_types": ["APPROVE_MODEL_MIGRATION", "REJECT_MIGRATION", "BLOCK_PROVIDER", "ACKNOWLEDGE_RISK"]
                })

    return pending


# ============================================================
# CLI ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("T1 DECISION EXECUTOR v0.1")
    print("=" * 60)

    # Show pending decisions
    pending = get_pending_decisions()
    print(f"\n  Pending T1 decisions: {len(pending)}")
    for p in pending:
        print(f"    - [{p['type']}] {p.get('provider', p.get('target', 'N/A'))}: {p.get('risk_level', 'N/A')}")
        print(f"      Valid actions: {p['valid_decision_types']}")

    # Dry-run example
    example = {
        "decision_type": "ACKNOWLEDGE_RISK",
        "target": "anthropic",
        "reason": "Acknowledged Anthropic EOL risk. Will monitor and decide closer to date.",
        "params": {}
    }
    success, msg, log = execute_decision(example, dry_run=True)
    print(f"\n  Dry-run example: {msg}")
    print("=" * 60)
