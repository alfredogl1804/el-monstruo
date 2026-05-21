#!/usr/bin/env python3
"""Tests for Oracle Auditor Embryo R0 — 20 Tests."""
import os
import sys
import json
import yaml
import tempfile

EMBRYO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, EMBRYO_DIR)

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
        print(f"  FAIL [{PASS+FAIL:02d}] {name}")


# ============================================================
print("=" * 60)
print("TEST SUITE: Oracle Auditor Embryo R0 — 20 Tests")
print("=" * 60)

# 01. embryo_id exists
test("embryo_id exists", auditor.EMBRYO_ID == "oracle_auditor_embryo_r0")

# 02. state loads
state = auditor.load_state()
test("state loads", state is not None and "embryo_id" in state)

# 03. self_task_queue loads
tasks = auditor.load_self_tasks()
test("self_task_queue loads", len(tasks) >= 3)

# 04. run_once exists
test("run_once exists", callable(getattr(auditor, "run_once", None)))

# 05. kill-switch active:true aborts
original_ks = auditor.KS_PATH
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
json.dump({"active": True}, tmp)
tmp.close()
auditor.KS_PATH = tmp.name
result = auditor.run_once()
auditor.KS_PATH = original_ks
os.unlink(tmp.name)
test("kill-switch active aborts", result["verdict"] == "ABORTED")

# 06. Dispatcher requerido
contract = auditor.load_contract()
test("Dispatcher requerido", "allowed_action_classes" in contract and "forbidden_action_classes" in contract)

# 07. A0_OBSERVE allowed
task_a0 = {"task_id": "test", "action_class": "A0_OBSERVE"}
d, _ = auditor.request_dispatcher_permission(task_a0, contract)
test("A0_OBSERVE allowed", d == "ALLOW")

# 08. A1_ANALYZE allowed
task_a1 = {"task_id": "test", "action_class": "A1_ANALYZE"}
d, _ = auditor.request_dispatcher_permission(task_a1, contract)
test("A1_ANALYZE allowed", d == "ALLOW")

# 09. A2_PREPARE_EVIDENCE allowed
task_a2 = {"task_id": "test", "action_class": "A2_PREPARE_EVIDENCE"}
d, _ = auditor.request_dispatcher_permission(task_a2, contract)
test("A2_PREPARE_EVIDENCE allowed", d == "ALLOW")

# 10. A3_CREATE_NON_PRODUCTIVE_ARTIFACT allowed
task_a3 = {"task_id": "test", "action_class": "A3_CREATE_NON_PRODUCTIVE_ARTIFACT"}
d, _ = auditor.request_dispatcher_permission(task_a3, contract)
test("A3_CREATE_NON_PRODUCTIVE_ARTIFACT allowed", d == "ALLOW")

# 11. R1 DENY
task_r1 = {"task_id": "test", "action_class": "R1"}
d, _ = auditor.request_dispatcher_permission(task_r1, contract)
test("R1 DENY", d == "DENY")

# 12. MEMORY_WRITE DENY
task_mw = {"task_id": "test", "action_class": "MEMORY_WRITE"}
d, _ = auditor.request_dispatcher_permission(task_mw, contract)
test("MEMORY_WRITE DENY", d == "DENY")

# 13. SUPABASE_WRITE DENY
task_sb = {"task_id": "test", "action_class": "SUPABASE_WRITE"}
d, _ = auditor.request_dispatcher_permission(task_sb, contract)
test("SUPABASE_WRITE DENY", d == "DENY")

# 14. APP_VISION_UPDATE DENY
task_av = {"task_id": "test", "action_class": "APP_VISION_UPDATE"}
d, _ = auditor.request_dispatcher_permission(task_av, contract)
test("APP_VISION_UPDATE DENY", d == "DENY")

# 15. no self-audit (contract says self_audit: false)
test("no self-audit", contract.get("constraints", {}).get("self_audit") is False)

# 16. audit_target is oracle_ai_embryo_r0
test("audit_target is oracle", contract.get("constraints", {}).get("audit_target") == "oracle_ai_embryo_r0")

# 17. no secrets in contract
forbidden = contract.get("forbidden_action_classes", [])
test("no secrets", "SECRET_READ" in forbidden and "SECRET_WRITE" in forbidden)

# 18. no main/PR/deploy in contract
test("no main/PR/deploy", "PR_CREATE" in forbidden and "DEPLOY" in forbidden and "MAIN_MODIFY" in forbidden)

# 19. can be invoked with 0 args (run_once takes no required params)
import inspect
sig = inspect.signature(auditor.run_once)
test("invocable with 0 args", len([p for p in sig.parameters.values() if p.default is inspect.Parameter.empty]) == 0)

# 20. hard rules PASS (contract enforces all forbidden classes)
required_forbidden = ["R1", "MEMORY_WRITE", "SUPABASE_WRITE", "DB_WRITE", "SECRET_READ", "SECRET_WRITE", "APP_VISION_UPDATE", "CANON_UPDATE", "PRE_IA_CLOSE", "PR_CREATE", "DEPLOY", "MAIN_MODIFY"]
all_forbidden = all(f in forbidden for f in required_forbidden)
test("hard rules PASS (all forbidden enforced)", all_forbidden)

print(f"\n{'='*60}")
print(f"RESULT: {PASS}/{PASS+FAIL} PASS, {FAIL}/{PASS+FAIL} FAIL")
print(f"{'='*60}")
sys.exit(0 if FAIL == 0 else 1)
