"""
Provider Fallback Verifier v0.1

Reads provider registry, detects models with risk flags or reported EOL,
validates NO auto-replacement, constructs fallback candidates,
requires T1 for any change, blocks Perplexity/DeepSeek/unknown providers,
and produces a decision pack.

No external API calls. No secrets read. No state modification.
No provider calls. No scheduler/kill-switch changes.

Usage:
    python3 provider_fallback_verifier_v0_1.py [--base-dir /path]
"""
import json
import sys
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Optional


# Blocked providers (cannot be used as fallback)
BLOCKED_PROVIDERS = {"perplexity", "deepseek"}

# Allowed providers for fallback consideration
ALLOWED_FALLBACK_PROVIDERS = {"openai", "google", "xai"}


def load_provider_registry(base_dir: Path) -> dict:
    """Load the provider registry from disk."""
    path = base_dir / "bridge" / "provider_ops" / "provider_registry.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def detect_risk_candidates(registry: dict, eol_overrides: Optional[dict] = None) -> list:
    """Detect providers with risk flags (EOL reported, deprecated, blocked)."""
    candidates = []
    providers = registry.get("providers", {})
    if eol_overrides is None:
        eol_overrides = {}

    for name, config in providers.items():
        risk_flags = []

        # Check if EOL is reported
        if name in eol_overrides:
            eol_date_str = eol_overrides[name]
            try:
                eol_date = date.fromisoformat(eol_date_str)
                days_remaining = (eol_date - date.today()).days
                risk_flags.append(f"EOL_REPORTED:{eol_date_str} ({days_remaining}d)")
            except (ValueError, TypeError):
                risk_flags.append(f"EOL_INVALID:{eol_date_str}")

        # Check if status is not ALLOWED
        if config.get("status") not in ("ALLOWED",):
            risk_flags.append(f"STATUS:{config.get('status')}")

        if risk_flags:
            candidates.append({
                "provider": name,
                "model": config.get("model"),
                "status": config.get("status"),
                "risk_flags": risk_flags,
                "is_blocked": name in BLOCKED_PROVIDERS,
            })

    return candidates


def validate_no_auto_replacement(registry: dict) -> dict:
    """Validate that auto-replacement is disabled in policies."""
    policies = registry.get("policies", {})
    auto_fallback = policies.get("auto_fallback", False)
    auto_replacement = policies.get("auto_replacement", False)

    return {
        "auto_fallback_disabled": not auto_fallback,
        "auto_replacement_disabled": not auto_replacement,
        "safe": not auto_fallback and not auto_replacement,
    }


def construct_fallback_candidates(registry: dict, risk_provider: str) -> list:
    """Construct list of fallback candidates from allowed providers."""
    candidates = []
    providers = registry.get("providers", {})

    for name, config in providers.items():
        if name == risk_provider:
            continue
        if name in BLOCKED_PROVIDERS:
            continue
        if config.get("status") != "ALLOWED":
            continue
        if config.get("model") is None:
            continue

        candidates.append({
            "provider": name,
            "model": config["model"],
            "status": "FALLBACK_CANDIDATE",
            "requires_t1_approval": True,
        })

    return candidates


def is_provider_blocked(provider_name: str) -> bool:
    """Check if a provider is blocked."""
    return provider_name.lower() in BLOCKED_PROVIDERS


def is_unknown_provider(provider_name: str, registry: dict) -> bool:
    """Check if a provider is unknown (not in registry)."""
    return provider_name.lower() not in registry.get("providers", {})


def requires_t1_for_change() -> bool:
    """Always returns True — any model change requires T1 approval."""
    return True


def produce_decision_pack(
    risk_candidates: list,
    fallback_candidates: list,
    auto_replacement_status: dict,
    eol_verification_status: str,
) -> dict:
    """Produce the T1 decision pack for provider fallback."""
    # Determine recommended action
    if eol_verification_status == "VERIFIED_EOL":
        recommended_action = "MIGRATE_NOW"
    elif eol_verification_status == "VERIFIED_SAFE":
        recommended_action = "KEEP_CURRENT_MONITOR"
    elif eol_verification_status == "UNVERIFIED_RISK":
        recommended_action = "WAIT_FOR_EXTERNAL_VERIFICATION"
    else:
        recommended_action = "WAIT_FOR_EXTERNAL_VERIFICATION"

    return {
        "risk_candidates": risk_candidates,
        "fallback_candidates": fallback_candidates,
        "auto_replacement_status": auto_replacement_status,
        "eol_verification_status": eol_verification_status,
        "recommended_action": recommended_action,
        "requires_t1": True,
        "auto_replacement_attempted": False,
        "provider_calls_made": 0,
        "secrets_read": 0,
        "scheduler_modified": False,
        "kill_switch_modified": False,
    }


def run_verifier(base_dir: Optional[Path] = None) -> dict:
    """Main entry point: run the full provider fallback verifier."""
    if base_dir is None:
        base_dir = Path(__file__).parents[2]

    registry = load_provider_registry(base_dir)

    # Known EOL overrides (from migration guard — unverified)
    eol_overrides = {"anthropic": "2026-06-15"}

    risk_candidates = detect_risk_candidates(registry, eol_overrides)
    auto_replacement_status = validate_no_auto_replacement(registry)
    fallback_candidates = construct_fallback_candidates(registry, "anthropic")

    # EOL verification status — we cannot verify externally in this sprint
    eol_verification_status = "UNVERIFIED_RISK"

    decision_pack = produce_decision_pack(
        risk_candidates, fallback_candidates, auto_replacement_status, eol_verification_status
    )

    return {
        "artifact": "provider_fallback_verifier_v0_1",
        "version": "0.1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "registry_loaded": bool(registry),
        "risk_candidates": risk_candidates,
        "fallback_candidates": fallback_candidates,
        "auto_replacement_status": auto_replacement_status,
        "eol_verification_status": eol_verification_status,
        "decision_pack": decision_pack,
        "blocked_providers": list(BLOCKED_PROVIDERS),
        "external_api_calls": 0,
        "secrets_used": 0,
        "state_modified": False,
        "provider_calls": 0,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Provider Fallback Verifier v0.1")
    parser.add_argument("--base-dir", default=None)
    args = parser.parse_args()
    base = Path(args.base_dir) if args.base_dir else None
    result = run_verifier(base)
    print(json.dumps(result, indent=2, default=str))
