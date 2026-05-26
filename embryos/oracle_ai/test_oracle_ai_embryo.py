#!/usr/bin/env python3
"""
20 mandatory tests for Oracle AI Embryo R0 v0.2 (Grounding-Aware).
Criterion: 20/20 PASS.
"""

import json
import os
import sys

# Add embryo dir to path
EMBRYO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, EMBRYO_DIR)

from oracle_ai_embryo import (
    EMBRYO_ID,
    KS_PATH,
    _build_prompt_for_task,
    _calculate_grounding_level,
    _normalize_claim,
    _parse_grounded_response,
    check_kill_switch,
    choose_next_task,
    load_contract,
    load_self_tasks,
    load_state,
    request_dispatcher_permission,
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
print("TEST SUITE: Oracle AI Embryo R0 v0.2 — 20 Tests")
print("=" * 60)

# 1. embryo_id exists
test("embryo_id exists", EMBRYO_ID == "oracle_ai_embryo_r0")

# 2. state loads
state = load_state()
test("state loads", state is not None and "embryo_id" in state)

# 3. self_task_queue loads
tasks = load_self_tasks()
test("self_task_queue loads", len(tasks) >= 4)

# 4. contract loads and has grounding section
contract = load_contract()
test("contract has grounding v0.2", "grounding" in contract and contract["grounding"]["version"] == "0.2.0")

# 5. grounding mandatory_claim_fields present
fields = contract["grounding"]["mandatory_claim_fields"]
test(
    "mandatory_claim_fields complete",
    all(
        f in fields
        for f in [
            "claim_id",
            "claim_text",
            "claim_type",
            "evidence_status",
            "source_ref",
            "freshness_required",
            "confidence",
        ]
    ),
)

# 6. evidence_statuses complete
statuses = contract["grounding"]["evidence_statuses"]
test(
    "evidence_statuses complete",
    all(
        s in statuses
        for s in [
            "VERIFIED_LOCAL",
            "VERIFIED_PROVIDER",
            "NEEDS_REAL_TIME_CHECK",
            "NO_SOURCE",
            "HYPOTHESIS",
            "CANDIDATE_ONLY",
        ]
    ),
)

# 7. choose_next_task selects a valid task
chosen, mem_influenced, mem_info = choose_next_task(tasks, state)
test("choose_next_task selects valid task", chosen is not None and "task_id" in chosen)

# 8. action A0_OBSERVE is ALLOW
d, _ = request_dispatcher_permission({"task_id": "t", "action_class": "A0_OBSERVE"}, contract)
test("action A0_OBSERVE is ALLOW", d == "ALLOW")

# 9. action R1 is DENY
d, _ = request_dispatcher_permission({"task_id": "t", "action_class": "R1"}, contract)
test("action R1 is DENY", d == "DENY")

# 10. kill-switch detection
os.makedirs(os.path.dirname(KS_PATH), exist_ok=True)
with open(KS_PATH, "w") as f:
    json.dump({"active": True}, f)
test("kill-switch active detected", check_kill_switch())
with open(KS_PATH, "w") as f:
    json.dump({"active": False}, f)

# 11. prompt includes grounding instructions
prompt = _build_prompt_for_task({"task_id": "detect_new_ai_capability_candidates"})
test("prompt has grounding rules", "evidence_status" in prompt and "NEEDS_REAL_TIME_CHECK" in prompt)

# 12. _normalize_claim produces all mandatory fields
raw = {"capability_name": "GPT-5 released 2026-05-01", "provider": "OpenAI"}
claim = _normalize_claim(raw, 0)
test(
    "normalize_claim has all fields",
    all(
        k in claim
        for k in [
            "claim_id",
            "claim_text",
            "claim_type",
            "evidence_status",
            "source_ref",
            "freshness_required",
            "confidence",
        ]
    ),
)

# 13. _normalize_claim auto-detects NEEDS_REAL_TIME_CHECK for dates
test("auto-detect NEEDS_RTC for dates", claim["evidence_status"] == "NEEDS_REAL_TIME_CHECK")

# 14. _normalize_claim marks freshness_required for RTC
test("freshness_required true for RTC", claim["freshness_required"] is True)

# 15. _normalize_claim without date indicators → HYPOTHESIS
raw2 = {"capability_name": "Better orchestration logic"}
claim2 = _normalize_claim(raw2, 1)
test("no-date claim → HYPOTHESIS", claim2["evidence_status"] == "HYPOTHESIS")

# 16. _calculate_grounding_level: all VERIFIED = 10
claims_v = [{"evidence_status": "VERIFIED_LOCAL"}, {"evidence_status": "VERIFIED_PROVIDER"}]
test("grounding all verified = 10", _calculate_grounding_level(claims_v) == 10)

# 17. _calculate_grounding_level: all NO_SOURCE = 2
claims_ns = [{"evidence_status": "NO_SOURCE"}, {"evidence_status": "NO_SOURCE"}]
test("grounding all NO_SOURCE = 2", _calculate_grounding_level(claims_ns) == 2)

# 18. _parse_grounded_response handles JSON array
json_text = json.dumps(
    [
        {
            "claim_text": "Test",
            "claim_type": "factual",
            "evidence_status": "HYPOTHESIS",
            "source_ref": "none",
            "confidence": 0.5,
        },
        {
            "claim_text": "Test2",
            "claim_type": "analytical",
            "evidence_status": "VERIFIED_LOCAL",
            "source_ref": "local",
            "confidence": 0.9,
        },
    ]
)
parsed = _parse_grounded_response(json_text, {"task_id": "test"})
test("parse JSON array → claims", len(parsed["claims"]) == 2 and "grounding_level" in parsed)

# 19. _parse_grounded_response handles non-JSON fallback
fallback = _parse_grounded_response("Not JSON at all", {"task_id": "test"})
test(
    "parse fallback → NEEDS_RTC",
    len(fallback["claims"]) == 1 and fallback["claims"][0]["evidence_status"] == "NEEDS_REAL_TIME_CHECK",
)

# 20. forbidden actions in contract
forbidden = contract.get("forbidden_action_classes", [])
test(
    "forbidden: PR/DEPLOY/MAIN/SECRET/MEMORY",
    all(a in forbidden for a in ["PR_CREATE", "DEPLOY", "MAIN_WRITE", "SECRET_READ", "MEMORY_WRITE"]),
)

print(f"\n{'=' * 60}")
print(f"RESULT: {passed}/20 PASS, {failed}/20 FAIL")
print(f"{'=' * 60}")

if failed > 0:
    sys.exit(1)
