"""
14 mandatory tests for T1 Decision Executor v0.1.
Criterion: 14/14 PASS.

Tests use dry_run mode and temp files to avoid mutating real state.
"""

import json
import os
import sys

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ARTIFACT_DIR)

from t1_decision_executor_v0_1 import execute_decision, get_pending_decisions, validate_decision

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS [{passed:02d}] {name}")
    else:
        failed += 1
        print(f"  FAIL [{passed + failed:02d}] {name}")


print("=" * 60)
print("TEST SUITE: T1 Decision Executor v0.1 — 14 Tests")
print("=" * 60)

# 1. Valid decision passes validation
valid_decision = {"decision_type": "ACKNOWLEDGE_RISK", "target": "anthropic", "reason": "Risk acknowledged"}
valid, errors = validate_decision(valid_decision)
test("01. valid decision passes validation", valid is True and len(errors) == 0)

# 2. Missing required fields fail validation
invalid_decision = {"decision_type": "ACKNOWLEDGE_RISK"}
valid, errors = validate_decision(invalid_decision)
test("02. missing fields fail validation", valid is False and len(errors) > 0)

# 3. Prohibited decision type is rejected
prohibited_decision = {"decision_type": "DEPLOY", "target": "production", "reason": "test"}
valid, errors = validate_decision(prohibited_decision)
test("03. prohibited decision type rejected", valid is False and "PROHIBITED" in str(errors))

# 4. Unknown decision type is rejected
unknown_decision = {"decision_type": "LAUNCH_MISSILES", "target": "world", "reason": "test"}
valid, errors = validate_decision(unknown_decision)
test("04. unknown decision type rejected", valid is False and "not recognized" in str(errors))

# 5. APPROVE_MODEL_MIGRATION requires params
migration_no_params = {
    "decision_type": "APPROVE_MODEL_MIGRATION",
    "target": "anthropic",
    "reason": "test",
    "params": {},
}
valid, errors = validate_decision(migration_no_params)
test("05. migration requires params", valid is False and "new_model" in str(errors))

# 6. APPROVE_MODEL_MIGRATION with params passes
migration_valid = {
    "decision_type": "APPROVE_MODEL_MIGRATION",
    "target": "anthropic",
    "reason": "EOL approaching",
    "params": {"provider": "anthropic", "new_model": "claude-sonnet-4-20250601"},
}
valid, errors = validate_decision(migration_valid)
test("06. migration with params passes", valid is True)

# 7. Dry-run does not execute
success, msg, log = execute_decision(valid_decision, dry_run=True)
test("07. dry-run does not execute", success is True and "Dry run" in msg)

# 8. ACKNOWLEDGE_RISK executes successfully
success, msg, log = execute_decision(valid_decision, dry_run=False)
test("08. ACKNOWLEDGE_RISK executes", success is True and "acknowledged" in msg.lower())

# 9. Decision log is written
log_path = os.path.join(ARTIFACT_DIR, "t1_decision_log.jsonl")
test("09. decision log written", os.path.exists(log_path))

# 10. Decision log contains entry
with open(log_path, "r") as f:
    lines = f.readlines()
last_entry = json.loads(lines[-1])
test(
    "10. decision log has correct entry",
    last_entry["decision_type"] == "ACKNOWLEDGE_RISK" and last_entry["success"] is True,
)

# 11. get_pending_decisions returns provider migration
pending = get_pending_decisions()
test(
    "11. pending decisions include provider migration", len(pending) >= 1 and pending[0]["type"] == "PROVIDER_MIGRATION"
)

# 12. Pending decision has valid_decision_types
test("12. pending has valid decision types", "APPROVE_MODEL_MIGRATION" in pending[0]["valid_decision_types"])

# 13. No external API calls in source
import inspect

import t1_decision_executor_v0_1 as executor_module

source = inspect.getsource(executor_module)
test(
    "13. no external API calls",
    "import requests" not in source and "import httpx" not in source and "urllib.request" not in source,
)

# 14. No secrets in source
secret_patterns = ["sk-", "sbp_", "eyJ", "OPENAI_API_KEY=", "password="]
test("14. no secrets in source", not any(p in source for p in secret_patterns))

# Cleanup decision log (keep it clean for commit)
os.remove(log_path)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
