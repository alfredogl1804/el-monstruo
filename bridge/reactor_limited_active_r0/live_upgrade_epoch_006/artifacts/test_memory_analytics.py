#!/usr/bin/env python3
"""Tests for Memory Analytics v0.1 — 12 Tests."""
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory_analytics_v0_1 as ma

PASS = 0
FAIL = 0


def test(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS [{PASS:02d}] {name}")
    else:
        FAIL += 1
        print(f"  FAIL [{PASS+FAIL:02d}] {name}")


print("=" * 60)
print("TEST SUITE: Memory Analytics v0.1 — 12 Tests")
print("=" * 60)

# 01. Module loads
test("module loads", hasattr(ma, "run_analytics"))

# 02. analyze_learning_velocity empty
result = ma.analyze_learning_velocity([])
test("learning_velocity empty → 0", result["lessons_per_cycle"] == 0)

# 03. analyze_learning_velocity with data
entries = [
    {"lessons": ["lesson1", "lesson2"]},
    {"lessons": ["lesson3"]}
]
result = ma.analyze_learning_velocity(entries)
test("learning_velocity 3 lessons / 2 cycles = 1.5", result["lessons_per_cycle"] == 1.5)

# 04. analyze_cost_efficiency empty
result = ma.analyze_cost_efficiency([])
test("cost_efficiency empty → 0", result["avg_cost"] == 0)

# 05. analyze_cost_efficiency with data
entries = [{"cost_usd": 0.001}, {"cost_usd": 0.002}]
result = ma.analyze_cost_efficiency(entries)
test("cost_efficiency avg = 0.0015", result["avg_cost"] == 0.0015)

# 06. analyze_grounding_progression empty
result = ma.analyze_grounding_progression([])
test("grounding empty → NO_DATA", result["trend"] == "NO_DATA")

# 07. analyze_grounding_progression with data
entries = [{"grounding_score": 6}, {"grounding_score": 8}, {"grounding_score": 9}, {"grounding_score": 10}]
result = ma.analyze_grounding_progression(entries)
test("grounding improving", result["trend"] == "IMPROVING" and result["avg_grounding"] == 8.2)

# 08. analyze_cross_embryo_patterns independent
entries = [
    {"source_embryo_id": "oracle", "artifact_refs": ["a.json"]},
    {"source_embryo_id": "auditor", "artifact_refs": ["b.json"]}
]
result = ma.analyze_cross_embryo_patterns(entries)
test("cross_embryo independent", result["interaction_type"] == "INDEPENDENT")

# 09. analyze_cross_embryo_patterns collaborative
entries = [
    {"source_embryo_id": "oracle", "artifact_refs": ["shared.json"]},
    {"source_embryo_id": "auditor", "artifact_refs": ["shared.json"]}
]
result = ma.analyze_cross_embryo_patterns(entries)
test("cross_embryo collaborative", result["interaction_type"] == "COLLABORATIVE")

# 10. generate_recommendations healthy
learning = {"lessons_per_cycle": 2, "total_lessons": 4, "unique_lessons": 3}
cost = {"avg_cost": 0.001, "total_cost": 0.002, "cost_trend": "STABLE"}
grounding = {"avg_grounding": 9.0, "trend": "IMPROVING"}
patterns = {"interaction_type": "COLLABORATIVE"}
recs = ma.generate_recommendations(learning, cost, grounding, patterns)
test("healthy → HEALTHY rec", any("HEALTHY" in r for r in recs))

# 11. generate_recommendations low grounding
grounding_low = {"avg_grounding": 5.0, "trend": "STABLE"}
recs = ma.generate_recommendations(learning, cost, grounding_low, patterns)
test("low grounding → IMPROVE rec", any("IMPROVE_GROUNDING" in r for r in recs))

# 12. kill-switch check function exists
test("check_kill_switch exists", callable(ma.check_kill_switch))

print(f"\n{'='*60}")
print(f"RESULT: {PASS}/{PASS+FAIL} PASS, {FAIL}/{PASS+FAIL} FAIL")
print(f"{'='*60}")
sys.exit(0 if FAIL == 0 else 1)
