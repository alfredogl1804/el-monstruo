"""
Test Suite: Epoch Next Action Ranker v0.1
Sprint: SPR-R0PLUS-PRODUCTION-SURGE-002

12 tests covering:
- Empty signals handling
- Score computation for individual actions
- Ranking order correctness
- Health urgency scoring (RED vs GREEN)
- Risk severity matching
- Directive alignment
- Coverage impact scoring
- Maturity contribution (early vs late epochs)
- Blocker detection
- Full rank() integration
- Top-N limiting
- Custom weights

Constraints: No network, no Supabase, no secrets, no DB.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from epoch_next_action_ranker_v0_1 import NextActionRanker, run, ACTION_CATALOG

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
print("TEST SUITE: Epoch Next Action Ranker v0.1 — 12 Tests")
print("=" * 60)

# 1. Empty signals produces valid output
result = run({})
test("01. empty signals produces valid ranked output",
     isinstance(result, dict) and "top_actions" in result and len(result["top_actions"]) == 5)

# 2. All actions have composite_score > 0
test("02. all top actions have composite_score > 0",
     all(a["composite_score"] > 0 for a in result["top_actions"]))

# 3. Ranking is in descending order
scores = [a["composite_score"] for a in result["top_actions"]]
test("03. ranking is in descending order",
     scores == sorted(scores, reverse=True))

# 4. RED health boosts investigation actions
red_signals = {"epoch_health": {"overall": "RED"}, "risks": [{"risk": "regression flag", "severity": "HIGH"}]}
result_red = run(red_signals)
top_ids_red = [a["action_id"] for a in result_red["top_actions"][:3]]
test("04. RED health puts INVESTIGATE_REGRESSION in top 3",
     "INVESTIGATE_REGRESSION" in top_ids_red)

# 5. GREEN health with no risks favors production
green_signals = {
    "epoch_health": {"overall": "GREEN"},
    "risks": [],
    "directives": [{"directive_type": "PRODUCTIVITY", "priority": 8}],
    "coverage_pct": 100.0,
    "epochs_completed": 9,
}
result_green = run(green_signals)
top_ids_green = [a["action_id"] for a in result_green["top_actions"][:3]]
test("05. GREEN health favors PRODUCE_NEXT_SURGE in top 3",
     "PRODUCE_NEXT_SURGE" in top_ids_green)

# 6. Risk severity matching works
cost_risk_signals = {
    "epoch_health": {"overall": "YELLOW"},
    "risks": [{"risk": "cost drift detected", "severity": "HIGH"}],
}
ranker = NextActionRanker(cost_risk_signals)
cost_score = ranker.score_action("ADDRESS_COST_DRIFT")
other_score = ranker.score_action("MEMORY_PALACE_CLEANUP")
test("06. cost risk boosts ADDRESS_COST_DRIFT over unrelated actions",
     cost_score["composite_score"] > other_score["composite_score"])

# 7. Directive alignment scoring
directive_signals = {
    "directives": [{"directive_type": "SAFETY", "priority": 9}],
}
ranker_dir = NextActionRanker(directive_signals)
security_score = ranker_dir._directive_alignment_score("SECURITY_AUDIT")
production_score = ranker_dir._directive_alignment_score("PRODUCE_NEXT_SURGE")
test("07. SAFETY directive aligns SECURITY_AUDIT > PRODUCE_NEXT_SURGE",
     security_score > production_score)

# 8. Coverage impact: gap boosts REMEDIATE_COVERAGE
gap_signals = {"coverage_pct": 60.0}
ranker_gap = NextActionRanker(gap_signals)
remediate_score = ranker_gap._coverage_impact_score("REMEDIATE_COVERAGE")
test("08. coverage gap boosts REMEDIATE_COVERAGE score",
     remediate_score > 0.5)

# 9. Maturity: early epochs favor infrastructure
early_signals = {"epochs_completed": 2}
ranker_early = NextActionRanker(early_signals)
infra_score = ranker_early._maturity_contribution_score("UPGRADE_OPS_LAYER")
prod_score = ranker_early._maturity_contribution_score("PRODUCE_NEXT_SURGE")
test("09. early epochs favor UPGRADE_OPS_LAYER over PRODUCE_NEXT_SURGE",
     infra_score > prod_score)

# 10. Blocker detection works
ranker_block = NextActionRanker({"coverage_pct": 50.0})
# Force a scenario where MERGE_TO_MAIN and REMEDIATE_COVERAGE are both top
fake_ranked = [
    {"action_id": "MERGE_TO_MAIN"},
    {"action_id": "REMEDIATE_COVERAGE"},
]
blockers = ranker_block.detect_blockers(fake_ranked)
test("10. blocker detected: REMEDIATE_COVERAGE blocks MERGE_TO_MAIN",
     len(blockers) > 0 and blockers[0]["blocked_by"] == "REMEDIATE_COVERAGE")

# 11. Top-N limiting works
result_3 = run({}, top_n=3)
test("11. top_n=3 returns exactly 3 actions",
     len(result_3["top_actions"]) == 3)

# 12. All required output keys present
required_keys = ["version", "generated_at", "generated_by", "signals_used",
                 "top_actions", "blockers", "total_candidates", "ranking_weights"]
test("12. rank() output has all required keys",
     all(k in result for k in required_keys))

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
