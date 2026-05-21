"""
12 mandatory tests for Provider Migration Guard v0.1.
Criterion: 12/12 PASS.
"""
import os
import sys
import json
import datetime

GUARD_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GUARD_DIR)

from provider_migration_guard import (
    load_provider_registry,
    detect_provider_eol_risk,
    mark_model_migration_candidate,
    block_auto_replacement,
    require_t1_for_model_change,
    produce_migration_options,
    validate_current_model_allowed_until_t1_decision,
    export_provider_migration_snapshot
)

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS [{passed:02d}] {name}")
    else:
        failed += 1
        print(f"  FAIL [{passed+failed:02d}] {name}")


print("=" * 60)
print("TEST SUITE: Provider Migration Guard v0.1 — 12 Tests")
print("=" * 60)

# Load registry once
registry = load_provider_registry()

# 1. Detects model with reported EOL
eol_overrides = {"anthropic": "2026-06-15"}
risks = detect_provider_eol_risk(registry, eol_overrides, reference_date="2026-05-21")
test("01. detects model with EOL reported",
     len(risks) == 1 and risks[0]["provider"] == "anthropic" and risks[0]["days_remaining"] == 25)

# 2. Marks migration candidate
candidate = mark_model_migration_candidate(
    "anthropic", "claude-sonnet-4-20250514", "2026-06-15",
    suggested_replacements=["claude-sonnet-4-20250601"],
    notes="EOL risk"
)
test("02. marks migration_candidate",
     candidate["status"] == "MIGRATION_CANDIDATE" and candidate["requires_t1"] is True)

# 3. Does NOT replace model automatically
allowed, reason = require_t1_for_model_change(
    "claude-sonnet-4-20250601", "claude-sonnet-4-20250514", "anthropic", t1_decision=None
)
test("03. NO auto-replacement (T1 required)",
     allowed is False and "BLOCKED" in reason)

# 4. Requires T1 for model change
allowed_approve, _ = require_t1_for_model_change(
    "claude-sonnet-4-20250601", "claude-sonnet-4-20250514", "anthropic", t1_decision="APPROVE"
)
allowed_deny, _ = require_t1_for_model_change(
    "claude-sonnet-4-20250601", "claude-sonnet-4-20250514", "anthropic", t1_decision="DENY"
)
test("04. T1 APPROVE allows, T1 DENY blocks",
     allowed_approve is True and allowed_deny is False)

# 5. Current model stays allowed until T1 decision (if not blocked)
allowed_now, model, status = validate_current_model_allowed_until_t1_decision("anthropic", registry)
test("05. current model allowed until T1 decision",
     allowed_now is True and model == "claude-sonnet-4-20250514" and status == "ALLOWED")

# 6. Blocks unknown provider
allowed_unknown, _, status_unknown = validate_current_model_allowed_until_t1_decision("unknown_provider_xyz", registry)
test("06. blocks unknown provider",
     allowed_unknown is False and status_unknown == "UNKNOWN_PROVIDER")

# 7. Blocks model if status=BLOCKED
# Create a modified registry with anthropic BLOCKED
blocked_registry = json.loads(json.dumps(registry))
blocked_registry["providers"]["anthropic"]["status"] = "BLOCKED"
allowed_blocked, _, status_blocked = validate_current_model_allowed_until_t1_decision("anthropic", blocked_registry)
test("07. blocks deprecated model if status=BLOCKED",
     allowed_blocked is False and status_blocked == "BLOCKED")

# 8. Exports snapshot
snapshot = export_provider_migration_snapshot(risks, [candidate], registry)
test("08. exports snapshot with required fields",
     snapshot["version"] == "0.1.0" and
     len(snapshot["migration_candidates"]) == 1 and
     snapshot["policy"]["auto_replacement_allowed"] is False and
     snapshot["policy"]["t1_required_for_model_change"] is True)

# 9. No secrets in snapshot
snapshot_str = json.dumps(snapshot)
secret_patterns = ["sk-", "sbp_", "eyJ", "password"]
test("09. no secrets in snapshot",
     not any(p in snapshot_str for p in secret_patterns))

# 10. No env vars printed in snapshot
env_patterns = ["OPENAI_API_KEY=", "ANTHROPIC_API_KEY=", "GEMINI_API_KEY=", "XAI_API_KEY="]
test("10. no env var values in snapshot",
     not any(p in snapshot_str for p in env_patterns))

# 11. No external API calls (verify by checking function signatures — all are pure logic)
import inspect
guard_module = sys.modules["provider_migration_guard"]
source = inspect.getsource(guard_module)
test("11. no external API calls (no requests/httpx/urllib in source)",
     "import requests" not in source and "import httpx" not in source and "urllib.request" not in source)

# 12. Provider registry remains valid after guard operations
registry_after = load_provider_registry()
test("12. provider registry still valid after operations",
     registry_after["version"] == "1.0.0" and
     len(registry_after["providers"]) >= 4 and
     registry_after["policies"]["auto_replacement"] is False)

print("=" * 60)
print(f"RESULT: {passed}/{passed+failed} PASS, {failed}/{passed+failed} FAIL")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
