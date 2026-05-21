"""
Test Suite: Embryo Task Diversity Balancer v0.1
Sprint: SPR-R0PLUS-PRODUCTION-SURGE-002

12 tests covering:
- Empty history handling
- Distribution computation
- Entropy calculation (uniform, skewed, single)
- Gini coefficient
- Overspecialization detection (HIGH, MEDIUM, LOW, NONE)
- Recommendations generation
- Full analyze() integration
- Custom config

Constraints: No network, no Supabase, no secrets, no DB.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embryo_task_diversity_balancer_v0_1 import TaskDiversityBalancer, run

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
print("TEST SUITE: Embryo Task Diversity Balancer v0.1 — 12 Tests")
print("=" * 60)

# 1. Empty history returns GREEN
result = run([])
test("01. empty history returns GREEN balancer_status",
     result["balancer_status"] == "GREEN")

# 2. Uniform distribution has high entropy
uniform_history = [
    {"category": "A"}, {"category": "B"}, {"category": "C"},
    {"category": "D"}, {"category": "A"}, {"category": "B"},
    {"category": "C"}, {"category": "D"},
]
result_uniform = run(uniform_history)
test("02. uniform distribution has normalized entropy > 0.9",
     result_uniform["entropy"]["normalized"] > 0.9)

# 3. Single category has zero entropy
single_history = [{"category": "TESTING"} for _ in range(10)]
result_single = run(single_history)
test("03. single category has normalized entropy == 0.0",
     result_single["entropy"]["normalized"] == 0.0)

# 4. Overspecialization detected on single category
test("04. single category triggers overspecialization HIGH",
     result_single["overspecialization"]["detected"] is True and
     result_single["overspecialization"]["severity"] == "HIGH")

# 5. Dominant category detected
dominant_history = [{"category": "TESTING"}] * 8 + [{"category": "OTHER"}] * 2
balancer = TaskDiversityBalancer(dominant_history)
overspec = balancer.detect_overspecialization()
test("05. dominant category detected when > 60%",
     overspec["dominant_category"] == "TESTING" and overspec["dominant_pct"] == 0.8)

# 6. Gini coefficient for uniform = 0
uniform_gini = TaskDiversityBalancer(uniform_history).compute_gini()
test("06. Gini coefficient near 0 for uniform distribution",
     uniform_gini < 0.1)

# 7. Gini coefficient for skewed > 0
skewed_history = [{"category": "A"}] * 9 + [{"category": "B"}]
skewed_gini = TaskDiversityBalancer(skewed_history).compute_gini()
test("07. Gini coefficient > 0 for skewed distribution",
     skewed_gini > 0.3)

# 8. Distribution counts correct
dist = TaskDiversityBalancer(dominant_history).compute_distribution()
test("08. distribution counts are correct",
     dist["categories"]["TESTING"]["count"] == 8 and dist["total"] == 10)

# 9. Healthy diversity not flagged
healthy_history = (
    [{"category": "TESTING"}] * 3 +
    [{"category": "INFRASTRUCTURE"}] * 3 +
    [{"category": "PRODUCTION"}] * 3 +
    [{"category": "ANALYSIS"}] * 3
)
result_healthy = run(healthy_history)
test("09. healthy diversity returns GREEN and not detected",
     result_healthy["balancer_status"] == "GREEN" and
     result_healthy["overspecialization"]["detected"] is False)

# 10. Recommendations include diversification for HIGH
recs = result_single["recommendations"]
test("10. HIGH overspec generates IMMEDIATE_DIVERSIFICATION recommendation",
     any(r["action"] == "IMMEDIATE_DIVERSIFICATION" for r in recs))

# 11. Full analyze has all required keys
required_keys = ["version", "generated_at", "balancer_status", "distribution",
                 "entropy", "gini_coefficient", "overspecialization", "recommendations", "config"]
test("11. analyze() returns all required keys",
     all(k in result_single for k in required_keys))

# 12. Custom config thresholds respected
custom_config = {"entropy_healthy": 0.9, "dominance_threshold": 0.5}
balancer_custom = TaskDiversityBalancer(dominant_history, config=custom_config)
test("12. custom config thresholds applied",
     balancer_custom.entropy_healthy == 0.9 and balancer_custom.dominance_threshold == 0.5)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
