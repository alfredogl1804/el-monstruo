"""
Tests for Artifact Ops Epoch Adapter v0.1
16 tests required: all must PASS.
"""

import json
import sys
from pathlib import Path

# Add adapter to path
sys.path.insert(0, str(Path(__file__).parent))

import artifact_ops_epoch_adapter_v0_1 as adapter

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS [{passed + failed:02d}] {name}")
    else:
        failed += 1
        print(f"  FAIL [{passed + failed:02d}] {name}")


print("=" * 60)
print("Artifact Ops Epoch Adapter v0.1 Tests")
print("=" * 60)

# --- Test 01: loads config ---
config = adapter.load_config("EPOCH_009")
test("loads config", config["epoch_id"] == "EPOCH_009" and config["adapter_version"] == "0.1")

# --- Test 02: invokes runner ---
runner_output = adapter.invoke_runner(config)
test("invokes runner", runner_output.get("status") == "SUCCESS")

# --- Test 03: reads kill-switch without modifying ---
ks = adapter.read_kill_switch(config)
test("reads kill-switch without modifying", ks["read_only"] is True and ks["exists"] is True)

# --- Test 04: generates snapshot ---
directive_summary = adapter.read_directive_summary(config)
snapshot = adapter.generate_epoch_ops_snapshot(config, runner_output, ks, directive_summary)
test("generates snapshot", snapshot["epoch_id"] == "EPOCH_009" and "artifact_ops_health" in snapshot)

# --- Test 05: includes epoch_id ---
test("includes epoch_id", snapshot["epoch_id"] == "EPOCH_009")

# --- Test 06: includes artifact coverage ---
test("includes artifact coverage", "artifact_test_coverage" in snapshot and snapshot["artifact_test_coverage"] >= 0)

# --- Test 07: includes embryo health ---
test("includes embryo health", "embryo_health" in snapshot)

# --- Test 08: includes memory health ---
test("includes memory_palace_health", "memory_palace_health" in snapshot)

# --- Test 09: includes directive summary ---
test("includes directive summary", "directive_summary" in snapshot and snapshot["directive_summary"]["exists"] is True)

# --- Test 10: includes cost summary ---
test("includes cost summary", "cost_summary" in snapshot and snapshot["cost_summary"]["provider_calls"] == 0)

# --- Test 11: detects top risks ---
risks = adapter.detect_top_risks(runner_output)
test("detects top risks", isinstance(risks, list) and len(risks) <= 3)

# --- Test 12: produces next action ---
action = adapter.detect_next_action(runner_output, ks)
test("produces next action", isinstance(action, str) and len(action) > 0)

# --- Test 13: no external API calls ---
test("no external API calls", snapshot["external_api_calls"] == 0)

# --- Test 14: no secrets ---
snapshot_str = json.dumps(snapshot)
secret_patterns = ["sk-", "sbp_", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "password=", "token="]
no_secrets = not any(p in snapshot_str for p in secret_patterns)
test("no secrets", no_secrets and snapshot["secrets_used"] == 0)

# --- Test 15: output JSON valid ---
try:
    json_str = json.dumps(snapshot, default=str)
    parsed = json.loads(json_str)
    test("output JSON valid", parsed["epoch_id"] == "EPOCH_009")
except (json.JSONDecodeError, TypeError):
    test("output JSON valid", False)

# --- Test 16: error handling if runner missing ---
bad_config = adapter.load_config("EPOCH_009")
bad_config["runner_path"] = "/nonexistent/path/runner.py"
error_output = adapter.invoke_runner(bad_config)
test("error handling if runner missing", error_output["status"] == "ERROR")

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

if failed > 0:
    sys.exit(1)
