#!/usr/bin/env python3
"""Tests for Oracle Auditor Embryo R0 v0.3 (Memory-Guided + Grounding Enforcement) — 20 Tests."""

import json
import os
import sys

EMBRYO_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(EMBRYO_DIR))
sys.path.insert(0, EMBRYO_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "embryos", "memory_palace"))

import oracle_auditor_embryo as auditor

PASS = 0
FAIL = 0


def test(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS [{PASS:02d}] {name}")
    else:
        FAIL += 1
        print(f"  FAIL [{PASS + FAIL:02d}] {name}")


# ============================================================
print("=" * 60)
print("TEST SUITE: Oracle Auditor Embryo R0 v0.3 — 20 Tests")
print("=" * 60)

# 01. embryo_id exists
test("embryo_id exists", auditor.EMBRYO_ID == "oracle_auditor_embryo_r0")

# 02. state loads
state = auditor.load_state()
test("state loads", state is not None and "embryo_id" in state)

# 03. contract has grounding_enforcement v0.2
contract = auditor.load_contract()
test(
    "contract has grounding_enforcement v0.2",
    "grounding_enforcement" in contract and contract["grounding_enforcement"]["version"] == "0.2.0",
)

# 04. grounding_enforcement has 4 scoring dimensions
dims = contract["grounding_enforcement"]["scoring_dimensions"]
test("4 scoring dimensions", len(dims) == 4)

# 05. grounding_enforcement has thresholds
thresholds = contract["grounding_enforcement"]["thresholds"]
test("thresholds PASS=8 PARTIAL=5", thresholds["PASS"] == 8.0 and thresholds["PARTIAL"] == 5.0)

# 06. enforce_grounding: well-grounded → PASS
well_grounded = {
    "output": {
        "claims": [
            {
                "claim_id": "c1",
                "claim_text": "Better orchestration",
                "claim_type": "analytical",
                "evidence_status": "VERIFIED_LOCAL",
                "source_ref": "local",
                "freshness_required": False,
                "confidence": 0.9,
            },
            {
                "claim_id": "c2",
                "claim_text": "Improved latency",
                "claim_type": "factual",
                "evidence_status": "VERIFIED_PROVIDER",
                "source_ref": "provider",
                "freshness_required": False,
                "confidence": 0.85,
            },
        ]
    }
}
score, penalties, verdict, details = auditor.enforce_grounding(well_grounded, contract)
test("enforce_grounding: well-grounded → PASS", verdict == "PASS" and score >= 8.0)

# 07. enforce_grounding: no claims → penalty
no_claims = {"output": {"response_raw": "text", "cost": 0.001}}
score2, penalties2, verdict2, details2 = auditor.enforce_grounding(no_claims, contract)
test("enforce_grounding: no claims → penalty", any("no_claims_field" in p[0] for p in penalties2))

# 08. enforce_grounding: NO_SOURCE high confidence → penalty
bad = {
    "output": {
        "claims": [
            {
                "claim_id": "c1",
                "claim_text": "GPT-6 released",
                "claim_type": "factual",
                "evidence_status": "NO_SOURCE",
                "source_ref": "none",
                "freshness_required": False,
                "confidence": 0.95,
            }
        ]
    }
}
score3, penalties3, verdict3, _ = auditor.enforce_grounding(bad, contract)
test("enforce_grounding: NO_SOURCE high conf → penalty", any("no_source_as_fact" in p[0] for p in penalties3))

# 09. enforce_grounding: date without NEEDS_RTC → penalty
date_bad = {
    "output": {
        "claims": [
            {
                "claim_id": "c1",
                "claim_text": "Released 2026-05-15",
                "claim_type": "factual",
                "evidence_status": "HYPOTHESIS",
                "source_ref": "none",
                "freshness_required": False,
                "confidence": 0.5,
            }
        ]
    }
}
_, penalties4, _, _ = auditor.enforce_grounding(date_bad, contract)
test("enforce_grounding: date without RTC → penalty", any("missing_freshness_on_date" in p[0] for p in penalties4))

# 10. enforce_grounding: date with NEEDS_RTC → no freshness penalty
date_good = {
    "output": {
        "claims": [
            {
                "claim_id": "c1",
                "claim_text": "Released 2026-05-15",
                "claim_type": "factual",
                "evidence_status": "NEEDS_REAL_TIME_CHECK",
                "source_ref": "none",
                "freshness_required": True,
                "confidence": 0.5,
            }
        ]
    }
}
_, penalties5, _, _ = auditor.enforce_grounding(date_good, contract)
test("enforce_grounding: date with RTC → no penalty", not any("missing_freshness_on_date" in p[0] for p in penalties5))

# 11. enforce_grounding: disabled → PASS 10
contract_off = dict(contract)
contract_off["grounding_enforcement"] = {"enabled": False}
score6, _, verdict6, _ = auditor.enforce_grounding(no_claims, contract_off)
test("enforce_grounding: disabled → PASS 10", verdict6 == "PASS" and score6 == 10.0)

# 12. A1_ANALYZE allowed
d, _ = auditor.request_dispatcher_permission({"task_id": "t", "action_class": "A1_ANALYZE"}, contract)
test("A1_ANALYZE allowed", d == "ALLOW")

# 13. R1 DENY
d, _ = auditor.request_dispatcher_permission({"task_id": "t", "action_class": "R1"}, contract)
test("R1 DENY", d == "DENY")

# 14. kill-switch active aborts
os.makedirs(os.path.dirname(auditor.KS_PATH), exist_ok=True)
with open(auditor.KS_PATH, "w") as f:
    json.dump({"active": True}, f)
test("kill-switch active detected", auditor.check_kill_switch())
with open(auditor.KS_PATH, "w") as f:
    json.dump({"active": False}, f)

# 15. Memory Palace loads
memory = auditor.load_memory()
test("memory palace loads", memory["available"] is True)

# 16. choose_next_task returns tuple (task, memory_influenced)
tasks = auditor.load_self_tasks()
chosen, mem_inf = auditor.choose_next_task(tasks, state, None)
test("choose_next_task returns tuple", chosen is not None and isinstance(mem_inf, bool))

# 17. build_auditor_memory_entry has required fields
fake_task = {"task_id": "test_task", "action_class": "A1_ANALYZE"}
entry = auditor.build_auditor_memory_entry(fake_task, "/fake/path.json", 8.5, "PASS", 0.001)
required_fields = [
    "memory_id",
    "timestamp",
    "source_embryo_id",
    "task_id",
    "lessons",
    "avoid_next_time",
    "grounding_score",
]
test("memory entry has required fields", all(f in entry for f in required_fields))

# 18. memory entry for FAIL has avoid patterns
entry_fail = auditor.build_auditor_memory_entry(fake_task, "/fake/path.json", 3.0, "FAIL", 0.001)
test("memory entry FAIL has avoid", len(entry_fail["avoid_next_time"]) > 0)

# 19. memory entry source is auditor
test("memory entry source is auditor", entry["source_embryo_id"] == "oracle_auditor_embryo_r0")

# 20. forbidden actions complete
forbidden = contract.get("forbidden_action_classes", [])
required = [
    "R1",
    "MEMORY_WRITE",
    "SUPABASE_WRITE",
    "DB_WRITE",
    "SECRET_READ",
    "SECRET_WRITE",
    "APP_VISION_UPDATE",
    "CANON_UPDATE",
    "PRE_IA_CLOSE",
    "PR_CREATE",
    "DEPLOY",
    "MAIN_MODIFY",
]
test("all forbidden enforced", all(f in forbidden for f in required))

print(f"\n{'=' * 60}")
print(f"RESULT: {PASS}/{PASS + FAIL} PASS, {FAIL}/{PASS + FAIL} FAIL")
print(f"{'=' * 60}")
sys.exit(0 if FAIL == 0 else 1)
