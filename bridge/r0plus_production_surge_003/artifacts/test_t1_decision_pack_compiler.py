"""
Test Suite: T1 Decision Pack Compiler v0.1
Sprint: SPR-R0PLUS-PRODUCTION-SURGE-003
13 tests.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t1_decision_pack_compiler_v0_1 import T1DecisionPackCompiler

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
print("TEST SUITE: T1 Decision Pack Compiler v0.1 — 13 Tests")
print("=" * 60)

# Setup
compiler = T1DecisionPackCompiler()

# 1. Empty compile produces valid JSON
result = compiler.compile()
test("01. empty compile produces valid JSON", json.dumps(result) is not None)

# 2. Ingest snapshot
compiler.ingest_snapshot({"pilot_health": "HEALTHY", "artifact_count": 15, "artifact_test_coverage": 100.0, "epoch_current": 9})
test("02. ingest snapshot stores data", compiler.signals["snapshot"]["pilot_health"] == "HEALTHY")

# 3. Ingest regression
compiler.ingest_regression({"overall_classification": "FALSE_POSITIVE", "overall_severity": "NONE", "investigations": [{"classification": "FALSE_POSITIVE"}]})
test("03. ingest regression stores classification", compiler.signals["regression"]["overall_classification"] == "FALSE_POSITIVE")

# 4. Ingest cost guard
compiler.ingest_cost_guard({"guard_status": "GREEN", "anomaly_count": 0, "total_cost_usd": 0.0, "drift_detected": False})
test("04. ingest cost guard stores status", compiler.signals["cost"]["guard_status"] == "GREEN")

# 5. Ingest diversity
compiler.ingest_diversity({"status": "YELLOW", "entropy_normalized": 0.65, "overspecialized": False, "dominant_task": "testing"})
test("05. ingest diversity stores status", compiler.signals["diversity"]["status"] == "YELLOW")

# 6. Ingest ranker
compiler.ingest_ranker({"top_actions": [{"action_id": "PRODUCE_NEXT_SURGE", "composite_score": 0.42}], "blockers": [], "total_candidates": 10})
test("06. ingest ranker stores actions", len(compiler.signals["ranker"]["top_actions"]) == 1)

# 7. Ingest audit ledger
compiler.ingest_audit_ledger({"p0_open": 0, "p1_blocking": 0, "track_items": 6})
test("07. ingest audit ledger stores state", compiler.signals["audit_ledger"]["r0plus_can_continue"] is True)

# 8. Ingest provider risk
compiler.ingest_provider_risk({"anthropic_risk": "VERIFIED_REAL", "local_only_mode": True, "migration_required": True, "provider_calls_allowed": False})
test("08. ingest provider risk stores constraint", compiler.signals["provider_risk"]["local_only_mode"] is True)

# 9. Full compile produces all required keys
full_result = compiler.compile()
required_keys = ["pilot_health", "regression_status", "cost_status", "diversity_status", "provider_risk", "top_actions", "blocked_actions", "audit_ledger", "recommended_sprint"]
test("09. full compile has all required keys", all(k in full_result for k in required_keys))

# 10. Recommended sprint is correct
test("10. recommended sprint is EXECUTE_NEXT_PRODUCTION_SURGE", full_result["recommended_sprint"] == "EXECUTE_NEXT_PRODUCTION_SURGE")

# 11. Blocked actions include provider-blocked items
test("11. blocked actions populated", len(full_result["blocked_actions"]) > 0)

# 12. No external API calls
test("12. no external API calls", full_result["external_api_calls"] == 0)

# 13. No secrets used
test("13. no secrets used", full_result["secrets_used"] == 0)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
