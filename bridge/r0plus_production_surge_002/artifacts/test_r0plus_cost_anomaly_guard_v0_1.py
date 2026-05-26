"""
Tests for R0+ Cost Anomaly Guard v0.1
Minimum 12 tests required.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import r0plus_cost_anomaly_guard_v0_1 as guard

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
print("R0+ Cost Anomaly Guard v0.1 Tests")
print("=" * 60)

# Test 01: Happy path - run_guard returns valid structure
result = guard.run_guard()
test(
    "happy path returns valid structure",
    "artifact" in result and "severity" in result and "recommended_action" in result,
)

# Test 02: Statistics calculation with normal data
costs = [{"cost_usd": 0.001, "epoch": "e1"}, {"cost_usd": 0.001, "epoch": "e2"}, {"cost_usd": 0.001, "epoch": "e3"}]
stats = guard.calculate_statistics(costs)
test("statistics calculation normal data", stats["mean"] == 0.001 and stats["std"] == 0.0)

# Test 03: Statistics with empty data
stats_empty = guard.calculate_statistics([])
test("statistics with empty data", stats_empty["mean"] == 0 and stats_empty["count"] == 0)

# Test 04: Anomaly detection with clear spike
costs_spike = [
    {"cost_usd": 0.001, "epoch": "e1"},
    {"cost_usd": 0.001, "epoch": "e2"},
    {"cost_usd": 0.001, "epoch": "e3"},
    {"cost_usd": 0.001, "epoch": "e4"},
    {"cost_usd": 0.010, "epoch": "e5"},  # 10x spike
]
stats_spike = guard.calculate_statistics(costs_spike)
anomalies = guard.detect_anomalies(stats_spike)
test("anomaly detection with clear spike", len(anomalies) > 0 and anomalies[0]["direction"] == "SPIKE")

# Test 05: No anomalies in uniform data
costs_uniform = [{"cost_usd": 0.001, "epoch": f"e{i}"} for i in range(10)]
stats_uniform = guard.calculate_statistics(costs_uniform)
anomalies_uniform = guard.detect_anomalies(stats_uniform)
test("no anomalies in uniform data", len(anomalies_uniform) == 0)

# Test 06: Cost spike detection
spikes = guard.detect_cost_spike(costs_spike)
test("cost spike detection", len(spikes) > 0 and spikes[0]["epoch"] == "e5")

# Test 07: Cost per run calculation
cpr = guard.calculate_cost_per_run(costs_spike)
test("cost per run calculation", cpr > 0 and cpr < 0.01)

# Test 08: Cost per artifact calculation
cpa = guard.calculate_cost_per_artifact(0.027, 11)
test("cost per artifact calculation", cpa > 0 and abs(cpa - 0.002455) < 0.001)

# Test 09: Severity HIGH for extreme spike
extreme_costs = [{"cost_usd": 0.001, "epoch": f"e{i}"} for i in range(10)]
extreme_costs.append({"cost_usd": 0.050, "epoch": "e_extreme"})
extreme_stats = guard.calculate_statistics(extreme_costs)
extreme_anomalies = guard.detect_anomalies(extreme_stats)
extreme_severity = guard.determine_severity(extreme_anomalies, [])
test("severity HIGH for extreme spike", extreme_severity == "HIGH")

# Test 10: Severity LOW for no issues
low_severity = guard.determine_severity([], [])
test("severity LOW for no issues", low_severity == "LOW")

# Test 11: Recommend FREEZE_CANDIDATE for HIGH
action_high = guard.recommend_action("HIGH", [{"z_score": 4.0}], [])
test("recommend FREEZE_CANDIDATE for HIGH", action_high == "FREEZE_CANDIDATE")

# Test 12: Recommend TRACK for LOW
action_low = guard.recommend_action("LOW", [], [])
test("recommend TRACK for LOW", action_low == "TRACK")

# Test 13: No external API calls in output
test("no external API calls", result["external_api_calls"] == 0)

# Test 14: No secrets in output
test("no secrets", result["secrets_used"] == 0 and "sk-" not in json.dumps(result))

# Test 15: Output JSON valid
try:
    json_str = json.dumps(result, default=str)
    parsed = json.loads(json_str)
    test("output JSON valid", parsed["artifact"] == "r0plus_cost_anomaly_guard_v0_1")
except (json.JSONDecodeError, TypeError):
    test("output JSON valid", False)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

if failed > 0:
    sys.exit(1)
