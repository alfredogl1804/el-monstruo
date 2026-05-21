"""
12 mandatory tests for Provider Migration Guard v0.1.
Updated for SPR-R0PLUS-ANTHROPIC-MIGRATION-PATCH-001.
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
print("TEST SUITE: Provider Migration Guard v0.1 — 12 Tests (post-migration)")
print("=" * 60)

# Load registry once
registry = load_provider_registry()

# 1. No EOL risks detected after migration (eol_overrides empty for anthropic now)
eol_overrides_empty = {}
risks_empty = detect_provider_eol_risk(registry, eol_overrides_empty, reference_date="2026-05-21")
test("01. no EOL risks after migration (overrides cleared)",
     len(risks_empty) == 0)

# 2. EOL detection still works if a new override is added (hypothetical future risk)
eol_overrides_future = {"openai": "2026-08-01"}
risks_future = detect_provider_eol_risk(registry, eol_overrides_future, reference_date="2026-05-21")
test("02. EOL detection still works for future risks",
     len(risks_future) == 1 and risks_future[0]["provider"] == "openai")

# 3. Marks migration candidate correctly
candidate = mark_model_migration_candidate(
    "anthropic", "claude-sonnet-4-20250514", "2026-06-15",
    suggested_replacements=["claude-sonnet-4-6"],
    notes="Historical: already migrated"
)
test("03. marks migration_candidate",
     candidate["status"] == "MIGRATION_CANDIDATE" and candidate["requires_t1"] is True)

# 4. Does NOT replace model automatically (T1 required)
allowed, reason = require_t1_for_model_change(
    "claude-sonnet-4-6", "claude-sonnet-4-20250514", "anthropic", t1_decision=None
)
test("04. NO auto-replacement (T1 required)",
     allowed is False and "BLOCKED" in reason)

# 5. T1 APPROVE allows, T1 DENY blocks
allowed_approve, _ = require_t1_for_model_change(
    "claude-sonnet-4-6", "claude-sonnet-4-20250514", "anthropic", t1_decision="APPROVE"
)
allowed_deny, _ = require_t1_for_model_change(
    "claude-sonnet-4-6", "claude-sonnet-4-20250514", "anthropic", t1_decision="DENY"
)
test("05. T1 APPROVE allows, T1 DENY blocks",
     allowed_approve is True and allowed_deny is False)

# 6. Current model (claude-sonnet-4-6) is allowed
allowed_now, model, status = validate_current_model_allowed_until_t1_decision("anthropic", registry)
test("06. current model claude-sonnet-4-6 allowed",
     allowed_now is True and model == "claude-sonnet-4-6" and status == "ALLOWED")

# 7. Blocks unknown provider
allowed_unknown, _, status_unknown = validate_current_model_allowed_until_t1_decision("unknown_provider_xyz", registry)
test("07. blocks unknown provider",
     allowed_unknown is False and status_unknown == "UNKNOWN_PROVIDER")

# 8. Blocks model if status=BLOCKED
blocked_registry = json.loads(json.dumps(registry))
blocked_registry["providers"]["anthropic"]["status"] = "BLOCKED"
allowed_blocked, _, status_blocked = validate_current_model_allowed_until_t1_decision("anthropic", blocked_registry)
test("08. blocks deprecated model if status=BLOCKED",
     allowed_blocked is False and status_blocked == "BLOCKED")

# 9. Exports snapshot with required fields
snapshot = export_provider_migration_snapshot(risks_empty, [candidate], registry)
test("09. exports snapshot with required fields",
     snapshot["version"] == "0.1.0" and
     len(snapshot["migration_candidates"]) == 1 and
     snapshot["policy"]["auto_replacement_allowed"] is False and
     snapshot["policy"]["t1_required_for_model_change"] is True)

# 10. No secrets in snapshot
snapshot_str = json.dumps(snapshot)
secret_patterns = ["sk-", "sbp_", "eyJ", "password"]
test("10. no secrets in snapshot",
     not any(p in snapshot_str for p in secret_patterns))

# 11. No external API calls (no requests/httpx/urllib in source)
import inspect
guard_module = sys.modules["provider_migration_guard"]
source = inspect.getsource(guard_module)
test("11. no external API calls (no requests/httpx/urllib in source)",
     "import requests" not in source and "import httpx" not in source and "urllib.request" not in source)

# 12. Provider registry remains valid after guard operations (version 1.1.0 post-migration)
registry_after = load_provider_registry()
test("12. provider registry still valid after operations",
     registry_after["version"] == "1.1.0" and
     len(registry_after["providers"]) >= 4 and
     registry_after["policies"]["auto_replacement"] is False)

print("=" * 60)
print(f"RESULT: {passed}/{passed+failed} PASS, {failed}/{passed+failed} FAIL")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
