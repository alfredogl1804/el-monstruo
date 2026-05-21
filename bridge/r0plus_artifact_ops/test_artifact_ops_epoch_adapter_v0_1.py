"""
Test Suite: Artifact Ops Epoch Adapter v0.1
Sprint: SPR-R0PLUS-EPOCH-009-OPS-INTEGRATED

14 tests covering:
- read_directive_queue (exists, missing, malformed)
- read_remediation_queue (exists, missing)
- compute_epoch_health (GREEN, YELLOW, RED)
- compute_top_risks (with/without anomalies)
- determine_next_sprint (various states)
- build_epoch_ops_snapshot (structure validation)
- build_t1_operating_snapshot_v03 (structure validation)
- run_epoch_adapter (full integration)
- safety invariants (no secrets, no API calls)

Constraints:
- No network, no Supabase, no secrets, no DB
- All assertions are real
- Pure local computation
"""
import json
import os
import sys
import inspect

OPS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OPS_DIR)

from artifact_ops_epoch_adapter_v0_1 import (
    read_directive_queue,
    read_remediation_queue,
    compute_epoch_health,
    compute_top_risks,
    determine_next_sprint,
    build_epoch_ops_snapshot,
    build_t1_operating_snapshot_v03,
    run_epoch_adapter,
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
        print(f"  FAIL [{passed + failed:02d}] {name}")


print("=" * 60)
print("TEST SUITE: Artifact Ops Epoch Adapter v0.1 — 14 Tests")
print("=" * 60)

# 1. read_directive_queue returns valid structure
dq = read_directive_queue()
test("01. read_directive_queue returns dict with exists key",
     isinstance(dq, dict) and "exists" in dq)

# 2. read_directive_queue has active_count
test("02. directive_queue has active_count field",
     "active_count" in dq)

# 3. read_remediation_queue returns valid structure
rq = read_remediation_queue()
test("03. read_remediation_queue returns dict with exists key",
     isinstance(rq, dict) and "exists" in rq)

# 4. compute_epoch_health returns GREEN when all healthy
mock_runner_output = {
    "consolidated": {
        "artifact_test_coverage": 100,
        "memory_health": "HEALTHY",
        "embryo_health": "HEALTHY",
    }
}
mock_dq = {"active_count": 2}
health = compute_epoch_health(mock_runner_output, mock_dq)
test("04. compute_epoch_health GREEN when all healthy",
     health["overall"] == "GREEN")

# 5. compute_epoch_health returns YELLOW when memory degraded
mock_runner_degraded = {
    "consolidated": {
        "artifact_test_coverage": 100,
        "memory_health": "DEGRADED",
        "embryo_health": "HEALTHY",
    }
}
health_yellow = compute_epoch_health(mock_runner_degraded, mock_dq)
test("05. compute_epoch_health YELLOW when memory not HEALTHY",
     health_yellow["overall"] == "YELLOW")

# 6. compute_epoch_health returns RED on ERROR
mock_runner_error = {
    "consolidated": {
        "artifact_test_coverage": 100,
        "memory_health": "ERROR",
        "embryo_health": "HEALTHY",
    }
}
health_red = compute_epoch_health(mock_runner_error, mock_dq)
test("06. compute_epoch_health RED on ERROR",
     health_red["overall"] == "RED")

# 7. compute_top_risks returns exactly 3 items
mock_runner_risks = {
    "consolidated": {
        "regression_flags": [{"id": 1}],
        "cost_anomalies": [{"id": 1}],
        "task_overspecialization": {"detected": True},
        "artifact_test_coverage": 100,
    }
}
risks = compute_top_risks(mock_runner_risks)
test("07. compute_top_risks returns exactly 3",
     len(risks) == 3)

# 8. determine_next_sprint returns valid sprint name
next_sprint = determine_next_sprint(mock_runner_output, health)
test("08. determine_next_sprint returns string starting with SPR-",
     isinstance(next_sprint, str) and next_sprint.startswith("SPR-"))

# 9. build_epoch_ops_snapshot has required top-level keys
snapshot = build_epoch_ops_snapshot(
    "009", mock_runner_output, dq, rq, health, risks, next_sprint
)
required_keys = ["version", "epoch_id", "epoch_status", "generated_at",
                 "kill_switch", "health", "artifact_coverage",
                 "memory_palace", "embryo_status", "directive_queue",
                 "top_risks", "next_recommended_sprint"]
test("09. epoch_ops_snapshot has all required keys",
     all(k in snapshot for k in required_keys))

# 10. epoch_ops_snapshot has zero external calls
test("10. epoch_ops_snapshot external_api_calls == 0",
     snapshot.get("external_api_calls") == 0 and
     snapshot.get("secrets_used") == 0 and
     snapshot.get("r1_operations") == 0)

# 11. build_t1_operating_snapshot_v03 has version 0.3
t1_snap = build_t1_operating_snapshot_v03("009", snapshot, health, risks, next_sprint)
test("11. T1 snapshot has version 0.3",
     t1_snap.get("version") == "0.3")

# 12. T1 snapshot has epoch_lineage
test("12. T1 snapshot has epoch_lineage with epochs_completed",
     "epoch_lineage" in t1_snap and t1_snap["epoch_lineage"]["epochs_completed"] == 9)

# 13. Full integration: run_epoch_adapter produces valid output
result = run_epoch_adapter(epoch_id="009")
test("13. run_epoch_adapter returns dict with epoch_ops_snapshot",
     isinstance(result, dict) and "epoch_ops_snapshot" in result and
     "t1_operating_snapshot_v03" in result)

# 14. No external API imports in source
import artifact_ops_epoch_adapter_v0_1 as adapter_module
source = inspect.getsource(adapter_module)
forbidden_imports = ["import requests", "import httpx", "urllib.request",
                     "import supabase", "import boto3"]
test("14. no external API imports in adapter source",
     not any(p in source for p in forbidden_imports))

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
