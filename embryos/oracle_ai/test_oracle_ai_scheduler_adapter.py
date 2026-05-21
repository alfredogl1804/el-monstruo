#!/usr/bin/env python3
"""Tests for Oracle AI Scheduler Adapter."""
import os
import sys
import json
import tempfile
import shutil

ADAPTER_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ADAPTER_DIR)

import oracle_ai_scheduler_adapter as adapter

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
# TEST 1: check_kill_switch returns True when active
# ============================================================
def test_ks_active():
    original = adapter.KS_PATH
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump({"active": True}, tmp)
    tmp.close()
    adapter.KS_PATH = tmp.name
    result = adapter.check_kill_switch()
    adapter.KS_PATH = original
    os.unlink(tmp.name)
    test("kill_switch_active_returns_true", result is True)


# ============================================================
# TEST 2: check_kill_switch returns False when inactive
# ============================================================
def test_ks_inactive():
    original = adapter.KS_PATH
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump({"active": False}, tmp)
    tmp.close()
    adapter.KS_PATH = tmp.name
    result = adapter.check_kill_switch()
    adapter.KS_PATH = original
    os.unlink(tmp.name)
    test("kill_switch_inactive_returns_false", result is False)


# ============================================================
# TEST 3: check_kill_switch returns False when file missing
# ============================================================
def test_ks_missing():
    original = adapter.KS_PATH
    adapter.KS_PATH = "/tmp/nonexistent_ks_12345.json"
    result = adapter.check_kill_switch()
    adapter.KS_PATH = original
    test("kill_switch_missing_returns_false", result is False)


# ============================================================
# TEST 4: check_dispatcher_available returns True with valid contract
# ============================================================
def test_dispatcher_available():
    ok, msg = adapter.check_dispatcher_available()
    test("dispatcher_available_with_real_contract", ok is True)


# ============================================================
# TEST 5: check_dispatcher_available returns False with missing file
# ============================================================
def test_dispatcher_missing():
    original = adapter.CONTRACT_PATH
    adapter.CONTRACT_PATH = "/tmp/nonexistent_contract_12345.yaml"
    ok, msg = adapter.check_dispatcher_available()
    adapter.CONTRACT_PATH = original
    test("dispatcher_unavailable_missing_file", ok is False)


# ============================================================
# TEST 6: check_budget_headroom returns True when under cap
# ============================================================
def test_budget_ok():
    original = adapter.STATE_PATH
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump({"total_cost_usd": 0.001}, tmp)
    tmp.close()
    adapter.STATE_PATH = tmp.name
    ok, spent = adapter.check_budget_headroom()
    adapter.STATE_PATH = original
    os.unlink(tmp.name)
    test("budget_under_cap_returns_true", ok is True)


# ============================================================
# TEST 7: check_budget_headroom returns False when over cap
# ============================================================
def test_budget_exceeded():
    original = adapter.STATE_PATH
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump({"total_cost_usd": 0.02}, tmp)
    tmp.close()
    adapter.STATE_PATH = tmp.name
    ok, spent = adapter.check_budget_headroom()
    adapter.STATE_PATH = original
    os.unlink(tmp.name)
    test("budget_exceeded_returns_false", ok is False)


# ============================================================
# TEST 8: invoke_embryo aborts on kill-switch active
# ============================================================
def test_invoke_aborts_ks():
    original = adapter.KS_PATH
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump({"active": True}, tmp)
    tmp.close()
    adapter.KS_PATH = tmp.name
    result = adapter.invoke_embryo()
    adapter.KS_PATH = original
    os.unlink(tmp.name)
    test("invoke_aborts_on_kill_switch", result["verdict"] == "ABORTED" and result["abort_reason"] == "kill_switch_active")


# ============================================================
# TEST 9: invoke_embryo aborts on dispatcher unavailable
# ============================================================
def test_invoke_aborts_dispatcher():
    original_ks = adapter.KS_PATH
    original_contract = adapter.CONTRACT_PATH
    # KS inactive
    tmp_ks = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump({"active": False}, tmp_ks)
    tmp_ks.close()
    adapter.KS_PATH = tmp_ks.name
    # Contract missing
    adapter.CONTRACT_PATH = "/tmp/nonexistent_contract_99999.yaml"
    result = adapter.invoke_embryo()
    adapter.KS_PATH = original_ks
    adapter.CONTRACT_PATH = original_contract
    os.unlink(tmp_ks.name)
    test("invoke_aborts_on_dispatcher_unavailable", result["verdict"] == "ABORTED" and "dispatcher_unavailable" in result["abort_reason"])


# ============================================================
# TEST 10: invoke_embryo aborts on budget exceeded
# ============================================================
def test_invoke_aborts_budget():
    original_state = adapter.STATE_PATH
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump({"total_cost_usd": 0.02}, tmp)
    tmp.close()
    adapter.STATE_PATH = tmp.name
    result = adapter.invoke_embryo()
    adapter.STATE_PATH = original_state
    os.unlink(tmp.name)
    test("invoke_aborts_on_budget_exceeded", result["verdict"] == "ABORTED" and result["abort_reason"] == "budget_exceeded")


# ============================================================
# TEST 11: ADAPTER_ID is correct
# ============================================================
def test_adapter_id():
    test("adapter_id_correct", adapter.ADAPTER_ID == "oracle_ai_scheduler_adapter_r0")


# ============================================================
# TEST 12: INTEGRATION_BUDGET_CAP is $0.01
# ============================================================
def test_budget_cap():
    test("budget_cap_is_001", adapter.INTEGRATION_BUDGET_CAP == 0.01)


if __name__ == "__main__":
    print("=" * 60)
    print("TEST SUITE: oracle_ai_scheduler_adapter")
    print("=" * 60)
    test_ks_active()
    test_ks_inactive()
    test_ks_missing()
    test_dispatcher_available()
    test_dispatcher_missing()
    test_budget_ok()
    test_budget_exceeded()
    test_invoke_aborts_ks()
    test_invoke_aborts_dispatcher()
    test_invoke_aborts_budget()
    test_adapter_id()
    test_budget_cap()
    print(f"\n{'='*60}")
    print(f"RESULT: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL")
    print(f"{'='*60}")
    sys.exit(0 if FAIL == 0 else 1)
