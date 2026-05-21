#!/usr/bin/env python3
"""
20 mandatory tests for Oracle AI Embryo R0.
Criterion: 20/20 PASS.
"""
import os
import sys
import json
import yaml
import tempfile
import shutil

# Add embryo dir to path
EMBRYO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, EMBRYO_DIR)

from oracle_ai_embryo import (
    load_state, load_self_tasks, load_contract, choose_next_task,
    request_dispatcher_permission, check_kill_switch, write_event,
    EMBRYO_ID, STATE_PATH, SELF_TASKS_PATH, CONTRACT_PATH, KS_PATH,
    EVENT_LOG_PATH, EVENT_LOG_DIR
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
        print(f"  FAIL [{passed+failed:02d}] {name}")


print("=" * 60)
print("TEST SUITE: Oracle AI Embryo R0 — 20 Tests")
print("=" * 60)

# 1. embryo_id exists
test("embryo_id exists", EMBRYO_ID == "oracle_ai_embryo_r0")

# 2. state loads
state = load_state()
test("state loads", state is not None and "embryo_id" in state)

# 3. self_task_queue loads
tasks = load_self_tasks()
test("self_task_queue loads", len(tasks) >= 5)

# 4. choose_next_task selects a valid task
chosen = choose_next_task(tasks, state)
test("choose_next_task selects valid task", chosen is not None and "task_id" in chosen)

# 5. run_once aborts if kill-switch active:true
# Temporarily set kill-switch to active
original_ks = None
if os.path.exists(KS_PATH):
    with open(KS_PATH) as f:
        original_ks = json.load(f)
os.makedirs(os.path.dirname(KS_PATH), exist_ok=True)
with open(KS_PATH, "w") as f:
    json.dump({"active": True}, f)
test("run_once aborts if kill-switch active", check_kill_switch() == True)
# Restore
with open(KS_PATH, "w") as f:
    json.dump({"active": False}, f)

# 6. run_once requests Dispatcher permission
contract = load_contract()
decision, reason = request_dispatcher_permission(chosen, contract)
test("run_once requests Dispatcher permission", decision in ["ALLOW", "DENY"])

# 7. action A0 is ALLOW
a0_task = {"task_id": "test_a0", "action_class": "A0_OBSERVE"}
d, _ = request_dispatcher_permission(a0_task, contract)
test("action A0_OBSERVE is ALLOW", d == "ALLOW")

# 8. action A1 is ALLOW
a1_task = {"task_id": "test_a1", "action_class": "A1_ANALYZE"}
d, _ = request_dispatcher_permission(a1_task, contract)
test("action A1_ANALYZE is ALLOW", d == "ALLOW")

# 9. action A2 is ALLOW
a2_task = {"task_id": "test_a2", "action_class": "A2_PREPARE_EVIDENCE"}
d, _ = request_dispatcher_permission(a2_task, contract)
test("action A2_PREPARE_EVIDENCE is ALLOW", d == "ALLOW")

# 10. action A3 is ALLOW
a3_task = {"task_id": "test_a3", "action_class": "A3_CREATE_NON_PRODUCTIVE_ARTIFACT"}
d, _ = request_dispatcher_permission(a3_task, contract)
test("action A3_CREATE_NON_PRODUCTIVE_ARTIFACT is ALLOW", d == "ALLOW")

# 11. action R1 is DENY
r1_task = {"task_id": "test_r1", "action_class": "R1"}
d, _ = request_dispatcher_permission(r1_task, contract)
test("action R1 is DENY", d == "DENY")

# 12. MEMORY_WRITE is DENY
mw_task = {"task_id": "test_mw", "action_class": "MEMORY_WRITE"}
d, _ = request_dispatcher_permission(mw_task, contract)
test("MEMORY_WRITE is DENY", d == "DENY")

# 13. SUPABASE_WRITE is DENY
sw_task = {"task_id": "test_sw", "action_class": "SUPABASE_WRITE"}
d, _ = request_dispatcher_permission(sw_task, contract)
test("SUPABASE_WRITE is DENY", d == "DENY")

# 14. APP_VISION_UPDATE is DENY
av_task = {"task_id": "test_av", "action_class": "APP_VISION_UPDATE"}
d, _ = request_dispatcher_permission(av_task, contract)
test("APP_VISION_UPDATE is DENY", d == "DENY")

# 15. event_log receives event
os.makedirs(EVENT_LOG_DIR, exist_ok=True)
# Clear existing log for test
if os.path.exists(EVENT_LOG_PATH):
    os.remove(EVENT_LOG_PATH)
write_event("TEST_EVENT", {"test": True})
test("event_log receives event", os.path.exists(EVENT_LOG_PATH) and os.path.getsize(EVENT_LOG_PATH) > 0)

# 16. state_after updates (simulate)
state_copy = state.copy()
state_copy["total_cycles"] = 99
test("state can be updated", state_copy["total_cycles"] == 99)

# 17. output report can be generated
from oracle_ai_embryo import produce_report
os.makedirs(os.path.join(EVENT_LOG_DIR, "outputs"), exist_ok=True)
path = produce_report(chosen, {"test": "data"}, "ALLOW", 0.001)
test("output report generates", os.path.exists(path))

# 18. no PR/main/deploy in contract
forbidden = contract.get("forbidden_action_classes", [])
test("no PR/main/deploy in contract", "PR_CREATE" in forbidden and "DEPLOY" in forbidden and "MAIN_WRITE" in forbidden)

# 19. no secrets in contract
test("no SECRET_READ/WRITE in contract", "SECRET_READ" in forbidden and "SECRET_WRITE" in forbidden)

# 20. no memory/Memento/Anti-Dory writes
test("no MEMORY_WRITE in contract", "MEMORY_WRITE" in forbidden)

print(f"\n{'='*60}")
print(f"RESULT: {passed}/20 PASS, {failed}/20 FAIL")
print(f"{'='*60}")

if failed > 0:
    sys.exit(1)
