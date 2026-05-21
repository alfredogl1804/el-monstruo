"""
Test Suite: Regression False Positive Filter v0.1
Sprint: SPR-R0PLUS-PRODUCTION-SURGE-003
13 tests.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regression_false_positive_filter_v0_1 import RegressionFalsePositiveFilter

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
print("TEST SUITE: Regression False Positive Filter v0.1 — 13 Tests")
print("=" * 60)

# Setup
f = RegressionFalsePositiveFilter()

# Create run history with ceiling values
run_history = [
    {"cost_usd": 0.001, "run_index": 0},
    {"cost_usd": 0.0003, "run_index": 1},
    {"cost_usd": 0.001, "run_index": 2},
    {"cost_usd": 0.0002, "run_index": 3},
    {"cost_usd": 0.0004, "run_index": 4},
    {"cost_usd": 0.001, "run_index": 5},
    {"cost_usd": 0.0003, "run_index": 6},
    {"cost_usd": 0.0002, "run_index": 7},
    {"cost_usd": 0.0003, "run_index": 8},
    {"cost_usd": 0.0003, "run_index": 9},
]

# 1. Empty flags produces empty report
result = f.filter([], run_history)
test("01. empty flags produces valid report", result["total_flags_input"] == 0)

# 2. Detects fixture ceiling value
ceiling_flag = {"type": "COST_SPIKE", "current_value": 0.001, "run_index": 5}
result = f.filter([ceiling_flag], run_history)
test("02. detects fixture ceiling value", result["false_positives_filtered"] == 1)

# 3. Ceiling filter reason is FIXTURE_CEILING
test("03. filter reason is FIXTURE_CEILING", result["classifications"][0]["filter_reason"] == "FIXTURE_CEILING")

# 4. Ceiling confidence is 0.95
test("04. ceiling confidence is 0.95", result["classifications"][0]["confidence"] == 0.95)

# 5. Detects recovered spike
recovered_flag = {"type": "COST_SPIKE", "current_value": 0.005, "run_index": 3}
# Add a spike at index 3 and recovery after
spike_history = [
    {"cost_usd": 0.0003, "run_index": 0},
    {"cost_usd": 0.0003, "run_index": 1},
    {"cost_usd": 0.0003, "run_index": 2},
    {"cost_usd": 0.005, "run_index": 3},
    {"cost_usd": 0.0003, "run_index": 4},
    {"cost_usd": 0.0003, "run_index": 5},
    {"cost_usd": 0.0003, "run_index": 6},
]
result2 = f.filter([recovered_flag], spike_history)
test("05. detects recovered spike", result2["false_positives_filtered"] == 1)

# 6. Recovered spike reason
test("06. recovered spike reason is RECOVERED_SPIKE", result2["classifications"][0]["filter_reason"] == "RECOVERED_SPIKE")

# 7. Insufficient baseline detection
short_history = [{"cost_usd": 0.001, "run_index": 0}, {"cost_usd": 0.002, "run_index": 1}]
flag3 = {"type": "COST_SPIKE", "current_value": 0.005, "run_index": 1}
result3 = f.filter([flag3], short_history)
test("07. detects insufficient baseline", result3["classifications"][0]["filter_reason"] == "INSUFFICIENT_BASELINE")

# 8. Real regression passes through
real_flag = {"type": "COST_SPIKE", "current_value": 0.05, "run_index": 5}
# History with no ceiling, no recovery
stable_history = [
    {"cost_usd": 0.0003, "run_index": 0},
    {"cost_usd": 0.0003, "run_index": 1},
    {"cost_usd": 0.0003, "run_index": 2},
    {"cost_usd": 0.0003, "run_index": 3},
    {"cost_usd": 0.0003, "run_index": 4},
    {"cost_usd": 0.05, "run_index": 5},
]
result4 = f.filter([real_flag], stable_history)
test("08. real regression passes through", result4["real_regressions"] == 1)

# 9. Real regression is_false_positive = False
test("09. real regression is_false_positive is False", result4["classifications"][0]["is_false_positive"] is False)

# 10. Filter rate calculation
mixed_flags = [
    {"type": "COST_SPIKE", "current_value": 0.001, "run_index": 2},
    {"type": "COST_SPIKE", "current_value": 0.05, "run_index": 5},
]
result5 = f.filter(mixed_flags, run_history)
test("10. filter rate calculation correct", result5["filter_rate_pct"] == 50.0)

# 11. Custom config thresholds applied
custom_filter = RegressionFalsePositiveFilter({"ceiling_values": [0.002], "ceiling_occurrence_threshold": 1, "min_baseline_runs": 3})
custom_history = [{"cost_usd": 0.002, "run_index": 0}, {"cost_usd": 0.0003, "run_index": 1}, {"cost_usd": 0.0003, "run_index": 2}, {"cost_usd": 0.0003, "run_index": 3}]
custom_flag = {"type": "COST_SPIKE", "current_value": 0.002, "run_index": 0}
result6 = custom_filter.filter([custom_flag], custom_history)
test("11. custom config thresholds applied", result6["false_positives_filtered"] == 1)

# 12. No external API calls
test("12. no external API calls", result["external_api_calls"] == 0)

# 13. No secrets used
test("13. no secrets used", result["secrets_used"] == 0)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
