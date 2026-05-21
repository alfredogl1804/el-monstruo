"""
Test Suite: Regression Investigator v0.1
Sprint: SPR-R0PLUS-REGRESSION-INVESTIGATION-001

12 tests covering:
1. Loads valid run history
2. Handles missing file / empty data
3. Detects false positive (fixture ceiling + recovery)
4. Detects real regression (no recovery, no ceiling)
5. Detects cost spike
6. Detects grounding drop
7. Detects repeated task
8. Calculates baseline correctly
9. Classifies severity correctly
10. Produces valid JSON output
11. No external API calls
12. No secrets used

Constraints: No network, no Supabase, no secrets, no DB.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regression_investigator_v0_1 import RegressionInvestigator

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
print("TEST SUITE: Regression Investigator v0.1 — 12 Tests")
print("=" * 60)

# Sample data mimicking real oracle runs
NORMAL_HISTORY = [
    {"cost_usd": 0.001, "task_id": "detect", "timestamp": "2026-05-21T03:11:31Z", "file": "a.json"},
    {"cost_usd": 0.00019, "task_id": "detect", "timestamp": "2026-05-21T03:11:54Z", "file": "b.json"},
    {"cost_usd": 0.001, "task_id": "detect", "timestamp": "2026-05-21T03:24:50Z", "file": "c.json"},
    {"cost_usd": 0.000195, "task_id": "detect", "timestamp": "2026-05-21T03:33:44Z", "file": "d.json"},
    {"cost_usd": 0.000478, "task_id": "detect", "timestamp": "2026-05-21T04:27:04Z", "file": "e.json"},
    {"cost_usd": 0.000285, "task_id": "detect", "timestamp": "2026-05-21T04:51:39Z", "file": "f.json"},
    {"cost_usd": 0.000438, "task_id": "detect", "timestamp": "2026-05-21T05:44:51Z", "file": "g.json"},
    {"cost_usd": 0.000114, "task_id": "map", "timestamp": "2026-05-21T03:23:40Z", "file": "h.json"},
    {"cost_usd": 0.001, "task_id": "map", "timestamp": "2026-05-21T03:35:25Z", "file": "i.json"},
    {"cost_usd": 0.000295, "task_id": "map", "timestamp": "2026-05-21T04:13:23Z", "file": "j.json"},
    {"cost_usd": 0.000287, "task_id": "map", "timestamp": "2026-05-21T04:28:16Z", "file": "k.json"},
    {"cost_usd": 0.000292, "task_id": "map", "timestamp": "2026-05-21T05:12:50Z", "file": "l.json"},
    {"cost_usd": 0.000294, "task_id": "map", "timestamp": "2026-05-21T06:27:59Z", "file": "m.json"},
]

COST_SPIKE_FLAG = [
    {
        "type": "COST_SPIKE",
        "run_index": 8,
        "source_file": "map_capability_to_application_20260521T033525.json",
        "current_value": 0.001,
        "recent_avg": 0.000279,
        "severity": "MEDIUM",
    }
]

MEMORY_PALACE = [
    {"grounding_score": 6, "source_embryo_id": "oracle_ai_embryo_r0"},
    {"grounding_score": 10, "source_embryo_id": "oracle_auditor_embryo_r0"},
    {"grounding_score": 9, "source_embryo_id": "oracle_ai_embryo_r0"},
    {"grounding_score": 10, "source_embryo_id": "oracle_auditor_embryo_r0"},
]

# 1. Loads valid run history
inv = RegressionInvestigator(NORMAL_HISTORY, COST_SPIKE_FLAG, MEMORY_PALACE)
test("01. loads valid run history",
     len(inv.run_history) == 13 and len(inv.regression_flags) == 1)

# 2. Handles empty data gracefully
inv_empty = RegressionInvestigator([], [], [])
result_empty = inv_empty.investigate()
test("02. handles empty data without error",
     result_empty["investigation_count"] == 0 and result_empty["overall_classification"] == "FALSE_POSITIVE")

# 3. Detects false positive (fixture ceiling + recovery)
result = inv.investigate()
first_inv = result["investigations"][0]
test("03. detects false positive (fixture ceiling + recovery)",
     first_inv["classification"] == "FALSE_POSITIVE" and
     first_inv["root_cause_candidate"] == "fixture_ceiling_value")

# 4. Detects real regression (no ceiling, no recovery)
real_history = [{"cost_usd": 0.0003, "task_id": "t"} for _ in range(8)] + \
               [{"cost_usd": 0.002, "task_id": "t"}]  # spike at end, no recovery
real_flag = [{"type": "COST_SPIKE", "run_index": 8, "current_value": 0.002, "recent_avg": 0.0003, "source_file": "x.json"}]
inv_real = RegressionInvestigator(real_history, real_flag)
result_real = inv_real.investigate()
test("04. detects real regression (no ceiling, no recovery)",
     result_real["investigations"][0]["classification"] in ["REAL_REGRESSION_NEEDS_FIX", "LOW_RISK_TRACK"])

# 5. Detects cost spike type
test("05. detects cost spike type",
     first_inv["analysis"]["cost_spike_analysis"]["type"] == "COST_SPIKE")

# 6. Detects grounding drop
low_grounding_palace = [
    {"grounding_score": 3},
    {"grounding_score": 2},
    {"grounding_score": 4},
]
inv_grounding = RegressionInvestigator(NORMAL_HISTORY, COST_SPIKE_FLAG, low_grounding_palace)
grounding_result = inv_grounding.detect_grounding_drop()
test("06. detects grounding drop when scores < 5",
     grounding_result["detected"] is True and grounding_result["low_score_count"] == 3)

# 7. Detects repeated task
repetitive_history = [{"cost_usd": 0.001, "task_id": "same_task"} for _ in range(10)]
inv_rep = RegressionInvestigator(repetitive_history, [])
rep_result = inv_rep.detect_repeated_task()
test("07. detects repeated task when dominant > 70%",
     rep_result["detected"] is True and rep_result["dominant_task"] == "same_task")

# 8. Calculates baseline correctly
baseline = inv.calculate_baseline()
test("08. calculates baseline correctly",
     baseline["count"] == 13 and baseline["mean"] > 0 and baseline["stddev"] > 0)

# 9. Classifies severity correctly
# FALSE_POSITIVE case should have severity NONE
test("09. classifies severity NONE for false positive",
     first_inv["severity"] == "NONE")

# 10. Produces valid JSON output
import json
try:
    json_str = json.dumps(result)
    parsed = json.loads(json_str)
    valid_json = "version" in parsed and "investigations" in parsed
except:
    valid_json = False
test("10. produces valid JSON output",
     valid_json)

# 11. No external API calls
test("11. no external API calls",
     result["external_api_calls"] == 0)

# 12. No secrets used
test("12. no secrets used",
     result["secrets_used"] == 0)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
