"""
Provider Registry Guard v1.0
Prevents provider drift, deprecated models, and unauthorized access during M2 cycles.
"""

import json
import os

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "provider_registry.json")


def load_provider_registry(path=None):
    """Load the provider registry from JSON file."""
    p = path or REGISTRY_PATH
    with open(p, "r") as f:
        return json.load(f)


def validate_provider_allowed(provider_id, model_id, registry=None):
    """Validate that a provider+model combination is allowed. Returns (bool, reason)."""
    reg = registry or load_provider_registry()
    providers = reg.get("providers", {})

    if provider_id not in providers:
        return False, f"DENY: Unknown provider '{provider_id}'. Policy: {reg['policies']['unknown_provider_default']}"

    entry = providers[provider_id]

    if entry["status"] not in ("ALLOWED",):
        return (
            False,
            f"DENY: Provider '{provider_id}' status is '{entry['status']}'. Reason: {entry.get('reason', 'N/A')}",
        )

    if model_id != entry["model"]:
        if model_id in entry.get("deprecated_models", []):
            return False, f"DENY: Model '{model_id}' is deprecated for provider '{provider_id}'."
        return (
            False,
            f"DENY: Model '{model_id}' is not the registered model for '{provider_id}'. Expected: '{entry['model']}'.",
        )

    return True, "ALLOWED"


def reject_blocked_provider(provider_id, registry=None):
    """Check if a provider is blocked. Returns True if blocked."""
    reg = registry or load_provider_registry()
    providers = reg.get("providers", {})

    if provider_id not in providers:
        return True  # Unknown = blocked

    entry = providers[provider_id]
    return entry["status"] != "ALLOWED"


def reject_deprecated_model(model_id, registry=None):
    """Check if a model is deprecated across any provider. Returns (bool, provider_id or None)."""
    reg = registry or load_provider_registry()
    providers = reg.get("providers", {})

    for pid, entry in providers.items():
        if model_id in entry.get("deprecated_models", []):
            return True, pid

    return False, None


def get_allowed_m2_providers(registry=None):
    """Return list of providers allowed for M2 cycles."""
    reg = registry or load_provider_registry()
    providers = reg.get("providers", {})
    return [
        {"provider_id": pid, "model": entry["model"], "endpoint": entry["endpoint"], "key_env": entry["key_env"]}
        for pid, entry in providers.items()
        if entry["status"] == "ALLOWED"
    ]


def assert_no_provider_auto_replacement(registry=None):
    """Assert that auto-replacement and auto-fallback are disabled."""
    reg = registry or load_provider_registry()
    policies = reg.get("policies", {})
    assert policies.get("auto_fallback") is False, "VIOLATION: auto_fallback must be False"
    assert policies.get("auto_replacement") is False, "VIOLATION: auto_replacement must be False"
    return True


def estimate_budget_for_cycle(registry=None):
    """Estimate max budget for a single cycle based on registry constraints."""
    reg = registry or load_provider_registry()
    budget = reg.get("budget", {})
    allowed = get_allowed_m2_providers(reg)
    num_providers = len(allowed)
    max_calls = budget.get("max_calls_per_provider_per_cycle", 1)
    max_per_cycle = budget.get("max_usd_per_cycle", 0.03)
    return {
        "max_usd_per_cycle": max_per_cycle,
        "max_usd_per_day": budget.get("max_usd_per_day", 0.05),
        "providers_count": num_providers,
        "max_calls_per_provider": max_calls,
        "retries": budget.get("retries", 0),
        "estimated_max_cost": max_per_cycle,
    }
