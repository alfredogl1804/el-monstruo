"""
Tests for Embryo Task Diversity Balancer v0.1
Minimum 12 tests required.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import embryo_task_diversity_balancer_v0_1 as balancer

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
print("Embryo Task Diversity Balancer v0.1 Tests")
print("=" * 60)

# Test 01: Happy path - run_balancer returns valid structure
result = balancer.run_balancer()
test("happy path returns valid structure",
     "artifact" in result and "overall_diversity_score" in result and "recommendation" in result)

# Test 02: Count diversity with varied tasks
runs_varied = [{"task": f"task_{i}"} for i in range(8)]
div = balancer.count_task_diversity(runs_varied)
test("count diversity varied tasks", div["unique_tasks"] == 8 and div["total_runs"] == 8)

# Test 03: Count diversity with repetitive tasks
runs_repetitive = [{"task": "same_task"} for _ in range(8)]
div_rep = balancer.count_task_diversity(runs_repetitive)
test("count diversity repetitive tasks", div_rep["unique_tasks"] == 1 and div_rep["total_runs"] == 8)

# Test 04: Count diversity with empty input
div_empty = balancer.count_task_diversity([])
test("count diversity empty input", div_empty["unique_tasks"] == 0 and div_empty["total_runs"] == 0)

# Test 05: Detect excessive repetition - positive case
rep_detected = balancer.detect_excessive_repetition(div_rep)
test("detect excessive repetition positive", rep_detected["detected"] is True and rep_detected["ratio"] == 1.0)

# Test 06: Detect excessive repetition - negative case
rep_not_detected = balancer.detect_excessive_repetition(div)
test("detect excessive repetition negative", rep_not_detected["detected"] is False)

# Test 07: Diversity score high for varied tasks
score_high = balancer.calculate_diversity_score(div)
test("diversity score high for varied tasks", score_high >= 80)

# Test 08: Diversity score low for repetitive tasks
score_low = balancer.calculate_diversity_score(div_rep)
test("diversity score low for repetitive tasks", score_low <= 60)

# Test 09: Propose adjustment when repetition detected
adj = balancer.propose_scoring_adjustment(div_rep, rep_detected)
test("propose adjustment when repetition detected", adj["adjustment_needed"] is True and len(adj["modifiers"]) > 0)

# Test 10: No adjustment when diverse
adj_none = balancer.propose_scoring_adjustment(div, rep_not_detected)
test("no adjustment when diverse", adj_none["adjustment_needed"] is False)

# Test 11: Never forces task
test("never forces task", result["forces_task"] is False)

# Test 12: Never skips dispatcher
test("never skips dispatcher", result["skips_dispatcher"] is False)

# Test 13: No external API calls
test("no external API calls", result["external_api_calls"] == 0)

# Test 14: No secrets in output
test("no secrets", result["secrets_used"] == 0 and "sk-" not in json.dumps(result))

# Test 15: Output JSON valid
try:
    json_str = json.dumps(result, default=str)
    parsed = json.loads(json_str)
    test("output JSON valid", parsed["artifact"] == "embryo_task_diversity_balancer_v0_1")
except (json.JSONDecodeError, TypeError):
    test("output JSON valid", False)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

if failed > 0:
    sys.exit(1)
