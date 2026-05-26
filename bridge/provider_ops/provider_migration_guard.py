"""
Provider Migration Guard v0.1
Epoch 008 — Carril A.

Detects provider model EOL risks, marks migration candidates,
blocks auto-replacement, and requires T1 for any model change.

Zero external API calls. Zero secrets. Pure local logic.
"""

import datetime
import json
import os

GUARD_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(GUARD_DIR, "provider_registry.json")

# Default EOL risk threshold: 30 days
DEFAULT_EOL_THRESHOLD_DAYS = 30


def load_provider_registry(registry_path=None):
    """Load the provider registry JSON. Returns dict or raises."""
    path = registry_path or REGISTRY_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Provider registry not found: {path}")
    with open(path, "r") as f:
        return json.load(f)


def detect_provider_eol_risk(registry=None, eol_overrides=None, reference_date=None, threshold_days=None):
    """
    Detect providers with EOL risk based on known EOL dates.

    Args:
        registry: Provider registry dict (loaded if None)
        eol_overrides: Dict of {provider: eol_date_str} for known EOL dates
        reference_date: Date to compare against (defaults to today)
        threshold_days: Days before EOL to flag as risk

    Returns:
        List of risk dicts with provider, model, eol_date, risk_level, days_remaining
    """
    if registry is None:
        registry = load_provider_registry()

    if eol_overrides is None:
        eol_overrides = {}

    if reference_date is None:
        reference_date = datetime.date.today()
    elif isinstance(reference_date, str):
        reference_date = datetime.date.fromisoformat(reference_date)

    if threshold_days is None:
        threshold_days = DEFAULT_EOL_THRESHOLD_DAYS

    risks = []
    providers = registry.get("providers", {})

    for provider_name, provider_data in providers.items():
        if provider_data.get("status") not in ("ALLOWED",):
            continue

        model = provider_data.get("model")
        if not model:
            continue

        eol_date_str = eol_overrides.get(provider_name)
        if not eol_date_str:
            continue

        eol_date = datetime.date.fromisoformat(eol_date_str)
        days_remaining = (eol_date - reference_date).days

        if days_remaining <= 0:
            risk_level = "CRITICAL"
        elif days_remaining <= 7:
            risk_level = "CRITICAL"
        elif days_remaining <= threshold_days:
            risk_level = "HIGH"
        elif days_remaining <= threshold_days * 2:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        risks.append(
            {
                "provider": provider_name,
                "model": model,
                "eol_date": eol_date_str,
                "risk_level": risk_level,
                "days_remaining": days_remaining,
            }
        )

    return risks


def mark_model_migration_candidate(provider_name, current_model, eol_date, suggested_replacements=None, notes=""):
    """
    Create a migration candidate record. Does NOT replace the model.

    Returns:
        Migration candidate dict with status=MIGRATION_CANDIDATE, requires_t1=True
    """
    return {
        "provider": provider_name,
        "current_model": current_model,
        "eol_date": eol_date,
        "risk_level": "HIGH",
        "status": "MIGRATION_CANDIDATE",
        "requires_t1": True,
        "suggested_replacements": suggested_replacements or [],
        "notes": notes,
        "detected_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "decided_at": None,
        "t1_decision": None,
    }


def block_auto_replacement(registry=None):
    """
    Verify and enforce that auto_replacement is blocked in the registry.

    Returns:
        (is_blocked: bool, policy: dict)
    """
    if registry is None:
        registry = load_provider_registry()

    policies = registry.get("policies", {})
    auto_replacement = policies.get("auto_replacement", True)
    auto_fallback = policies.get("auto_fallback", True)

    is_blocked = (auto_replacement is False) and (auto_fallback is False)

    return is_blocked, {
        "auto_replacement": auto_replacement,
        "auto_fallback": auto_fallback,
        "enforcement": "BLOCKED" if is_blocked else "VIOLATION",
    }


def require_t1_for_model_change(requested_model, current_model, provider_name, t1_decision=None):
    """
    Enforce that any model change requires explicit T1 decision.

    Args:
        requested_model: The model someone wants to switch to
        current_model: The currently active model
        provider_name: The provider name
        t1_decision: T1's explicit decision (None = no decision yet)

    Returns:
        (allowed: bool, reason: str)
    """
    if requested_model == current_model:
        return True, "No change requested — current model maintained."

    if t1_decision is None:
        return (
            False,
            f"Model change from '{current_model}' to '{requested_model}' for {provider_name} BLOCKED: requires explicit T1 decision.",
        )

    if t1_decision == "APPROVE":
        return True, f"T1 approved model change to '{requested_model}' for {provider_name}."

    return False, f"T1 decision is '{t1_decision}' — model change denied."


def produce_migration_options(provider_name, current_model, eol_date):
    """
    Produce a set of migration options for T1 to choose from.
    Does NOT execute any option — only presents them.

    Returns:
        List of option dicts
    """
    options = [
        {
            "option_id": "KEEP_CURRENT_UNTIL_DATE",
            "description": f"Keep {current_model} until EOL date ({eol_date}). Monitor for issues.",
            "risk": "Model may stop working on EOL date.",
            "requires_t1": True,
            "auto_executable": False,
        },
        {
            "option_id": "MIGRATE_NOW",
            "description": f"Migrate {provider_name} to a new model immediately.",
            "risk": "New model may behave differently. Requires testing.",
            "requires_t1": True,
            "auto_executable": False,
        },
        {
            "option_id": "BLOCK_PROVIDER_UNTIL_VERIFIED",
            "description": f"Block {provider_name} entirely until new model is verified.",
            "risk": "Reduces available providers. May affect cycle diversity.",
            "requires_t1": True,
            "auto_executable": False,
        },
        {
            "option_id": "REQUIRE_EXTERNAL_VERIFICATION",
            "description": f"Keep {current_model} but require external verification of EOL claim before acting.",
            "risk": "May delay necessary migration if EOL is real.",
            "requires_t1": True,
            "auto_executable": False,
        },
    ]
    return options


def validate_current_model_allowed_until_t1_decision(provider_name, registry=None):
    """
    Validate that the current model for a provider is still allowed
    (i.e., not BLOCKED) pending T1 decision.

    Returns:
        (allowed: bool, model: str, status: str)
    """
    if registry is None:
        registry = load_provider_registry()

    providers = registry.get("providers", {})
    provider = providers.get(provider_name)

    if not provider:
        return False, None, "UNKNOWN_PROVIDER"

    status = provider.get("status", "UNKNOWN")
    model = provider.get("model")

    if status == "ALLOWED":
        return True, model, "ALLOWED"
    elif status == "BLOCKED":
        return False, model, "BLOCKED"
    else:
        return False, model, status


def export_provider_migration_snapshot(risks, candidates, registry=None):
    """
    Export a complete migration snapshot for persistence/reporting.

    Returns:
        Snapshot dict conforming to provider_migration_guard_schema.json
    """
    if registry is None:
        registry = load_provider_registry()

    is_blocked, policy_status = block_auto_replacement(registry)

    # Collect blocked models from registry
    blocked_models = []
    for pname, pdata in registry.get("providers", {}).items():
        for dep_model in pdata.get("deprecated_models", []):
            blocked_models.append(
                {
                    "provider": pname,
                    "model": dep_model,
                    "reason": "Listed in deprecated_models",
                    "blocked_at": "2026-05-21T00:00:00Z",
                }
            )

    snapshot = {
        "version": "0.1.0",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "migration_candidates": candidates,
        "blocked_models": blocked_models,
        "risks_detected": risks,
        "policy": {
            "auto_replacement_allowed": False,
            "t1_required_for_model_change": True,
            "unknown_provider_default": "DENY",
            "eol_risk_threshold_days": DEFAULT_EOL_THRESHOLD_DAYS,
        },
    }

    return snapshot


# ============================================================
# CLI ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("PROVIDER MIGRATION GUARD v0.1")
    print("=" * 60)

    registry = load_provider_registry()

    # Known EOL dates (reported by system, not verified externally)
    # NOTE: anthropic EOL removed after T1-approved migration to claude-sonnet-4-6
    # (SPR-R0PLUS-ANTHROPIC-MIGRATION-PATCH-001, 2026-05-21)
    eol_overrides = {}

    risks = detect_provider_eol_risk(registry, eol_overrides)
    print(f"\n  Risks detected: {len(risks)}")
    for r in risks:
        print(f"    - {r['provider']}/{r['model']}: {r['risk_level']} ({r['days_remaining']}d remaining)")

    candidates = []
    for r in risks:
        if r["risk_level"] in ("HIGH", "CRITICAL"):
            c = mark_model_migration_candidate(
                r["provider"],
                r["model"],
                r["eol_date"],
                notes=f"EOL risk detected: {r['days_remaining']} days remaining",
            )
            candidates.append(c)
            print(f"\n  Migration candidate: {r['provider']}/{r['model']}")
            print(f"    Status: {c['status']}")
            print(f"    Requires T1: {c['requires_t1']}")

    is_blocked, policy = block_auto_replacement(registry)
    print(f"\n  Auto-replacement blocked: {is_blocked}")

    snapshot = export_provider_migration_snapshot(risks, candidates, registry)
    out_path = os.path.join(GUARD_DIR, "provider_migration_snapshot.json")
    with open(out_path, "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"\n  Snapshot exported: {out_path}")
    print("=" * 60)
