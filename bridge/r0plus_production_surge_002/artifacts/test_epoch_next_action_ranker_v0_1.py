"""
Tests for Epoch Next Action Ranker v0.1
Minimum 12 tests required.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import epoch_next_action_ranker_v0_1 as ranker

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
print("Epoch Next Action Ranker v0.1 Tests")
print("=" * 60)

# Test 01: Happy path - run_ranker returns valid structure
result = ranker.run_ranker()
test("happy path returns valid structure",
     "artifact" in result and "top_5_next_actions" in result and "next_recommended_sprint" in result)

# Test 02: Top 5 actions limited to 5
test("top 5 actions limited", len(result["top_5_next_actions"]) <= 5)

# Test 03: Blocked actions detected
test("blocked actions detected", len(result["blocked_actions"]) > 0)

# Test 04: MERGE_TO_MAIN is blocked
merge_actions = [a for a in result["top_5_next_actions"] if a["action_id"] == "MERGE_TO_MAIN"]
if merge_actions:
    test("MERGE_TO_MAIN is blocked", merge_actions[0]["classification"] == "BLOCKED")
else:
    # It might not be in top 5 since blocked goes last
    all_candidates = ranker.generate_candidate_actions({}, {}, {"entries": [], "count": 0})
    merge = [a for a in all_candidates if a["action_id"] == "MERGE_TO_MAIN"][0]
    test("MERGE_TO_MAIN is blocked", ranker.is_blocked(merge))

# Test 05: DEPLOY_PRODUCTION is blocked
deploy = {"action_id": "DEPLOY_PRODUCTION", "category": "R1", "value": 95, "risk_reduction": 5}
test("DEPLOY_PRODUCTION is blocked", ranker.is_blocked(deploy))

# Test 06: SUPABASE_INTEGRATION is blocked
supa = {"action_id": "SUPABASE_INTEGRATION", "category": "R1", "value": 80, "risk_reduction": 50}
test("SUPABASE_INTEGRATION is blocked", ranker.is_blocked(supa))

# Test 07: R0PLUS actions not blocked
r0_action = {"action_id": "PRODUCE_NEXT_SURGE", "category": "R0PLUS", "value": 85, "risk_reduction": 60}
test("R0PLUS actions not blocked", not ranker.is_blocked(r0_action))

# Test 08: Classification EXECUTE_NOW for high value + high risk reduction
classification = ranker.classify_action(r0_action)
test("classify EXECUTE_NOW for high scores", classification == "EXECUTE_NOW")

# Test 09: Classification BLOCKED for R1
classification_blocked = ranker.classify_action(deploy)
test("classify BLOCKED for R1", classification_blocked == "BLOCKED")

# Test 10: Classification TRACK for low value
low_action = {"action_id": "LOW_PRIORITY", "category": "R0PLUS", "value": 50, "risk_reduction": 20}
classification_low = ranker.classify_action(low_action)
test("classify TRACK for low value", classification_low == "TRACK")

# Test 11: Next sprint recommendation exists
test("next sprint recommendation exists", result["next_recommended_sprint"].startswith("SPR-"))

# Test 12: No external API calls
test("no external API calls", result["external_api_calls"] == 0)

# Test 13: No secrets in output
test("no secrets", result["secrets_used"] == 0 and "sk-" not in json.dumps(result))

# Test 14: State not modified
test("state not modified", result["state_modified"] is False)

# Test 15: Output JSON valid
try:
    json_str = json.dumps(result, default=str)
    parsed = json.loads(json_str)
    test("output JSON valid", parsed["artifact"] == "epoch_next_action_ranker_v0_1")
except (json.JSONDecodeError, TypeError):
    test("output JSON valid", False)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

if failed > 0:
    sys.exit(1)
