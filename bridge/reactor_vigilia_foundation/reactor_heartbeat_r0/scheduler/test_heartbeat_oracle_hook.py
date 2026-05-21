#!/usr/bin/env python3
"""Tests for Heartbeat Oracle Hook."""
import os
import sys
import json
import tempfile

HOOK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HOOK_DIR)

import heartbeat_oracle_hook as hook

PASS = 0
FAIL = 0


def test(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")


# ============================================================
# TEST 1: HOOK_ID is correct
# ============================================================
def test_hook_id():
    test("hook_id_correct", hook.HOOK_ID == "heartbeat_oracle_hook_r0")


# ============================================================
# TEST 2: check_kill_switch returns True when active
# ============================================================
def test_ks_active():
    original = hook.KS_PATH
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump({"active": True}, tmp)
    tmp.close()
    hook.KS_PATH = tmp.name
    result = hook.check_kill_switch()
    hook.KS_PATH = original
    os.unlink(tmp.name)
    test("ks_active_returns_true", result is True)


# ============================================================
# TEST 3: check_kill_switch returns False when inactive
# ============================================================
def test_ks_inactive():
    original = hook.KS_PATH
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump({"active": False}, tmp)
    tmp.close()
    hook.KS_PATH = tmp.name
    result = hook.check_kill_switch()
    hook.KS_PATH = original
    os.unlink(tmp.name)
    test("ks_inactive_returns_false", result is False)


# ============================================================
# TEST 4: run_once aborts on kill-switch active
# ============================================================
def test_run_once_aborts_ks():
    original = hook.KS_PATH
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump({"active": True}, tmp)
    tmp.close()
    hook.KS_PATH = tmp.name
    result = hook.run_once()
    hook.KS_PATH = original
    os.unlink(tmp.name)
    test("run_once_aborts_on_ks", result["verdict"] == "ABORTED" and result["reason"] == "kill_switch_active")


# ============================================================
# TEST 5: run_once returns structured result with required fields
# ============================================================
def test_run_once_structure():
    original = hook.KS_PATH
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump({"active": True}, tmp)
    tmp.close()
    hook.KS_PATH = tmp.name
    result = hook.run_once()
    hook.KS_PATH = original
    os.unlink(tmp.name)
    has_fields = all(k in result for k in ["hook_id", "verdict", "timestamp_start", "timestamp_end"])
    test("run_once_has_required_fields", has_fields)


# ============================================================
# TEST 6: EVENT_LOG_PATH is in the correct location
# ============================================================
def test_event_log_path():
    test("event_log_path_in_bridge", "bridge/embryos/oracle_ai_r0" in hook.EVENT_LOG_PATH)


# ============================================================
# TEST 7: write_event produces valid JSONL
# ============================================================
def test_write_event():
    original = hook.EVENT_LOG_PATH
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
    tmp.close()
    hook.EVENT_LOG_PATH = tmp.name
    hook.write_event("TEST_EVENT", {"test": True})
    with open(tmp.name, "r") as f:
        line = f.readline()
    event = json.loads(line)
    hook.EVENT_LOG_PATH = original
    os.unlink(tmp.name)
    test("write_event_valid_jsonl", event["event_type"] == "TEST_EVENT" and event["source"] == "heartbeat_oracle_hook_r0")


# ============================================================
# TEST 8: KS_PATH points to scheduler directory
# ============================================================
def test_ks_path_location():
    test("ks_path_in_scheduler_dir", "scheduler" in hook.KS_PATH)


if __name__ == "__main__":
    print("=" * 60)
    print("TEST SUITE: heartbeat_oracle_hook")
    print("=" * 60)
    test_hook_id()
    test_ks_active()
    test_ks_inactive()
    test_run_once_aborts_ks()
    test_run_once_structure()
    test_event_log_path()
    test_write_event()
    test_ks_path_location()
    print(f"\n{'='*60}")
    print(f"RESULT: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL")
    print(f"{'='*60}")
    sys.exit(0 if FAIL == 0 else 1)
