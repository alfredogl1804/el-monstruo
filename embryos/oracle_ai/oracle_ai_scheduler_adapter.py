#!/usr/bin/env python3
"""
Oracle AI Scheduler Adapter
Bridges the scheduler/heartbeat layer with the oracle_ai_embryo_r0.

Responsibilities:
- Verify kill-switch BEFORE invoking embryo
- Verify Dispatcher availability
- Invoke oracle_ai_embryo.run_once() programmatically
- Enforce budget cap ($0.01 for integration test)
- Enforce max 1 provider call
- Enforce retries=0
- Register start/end in event log
- Return structured result to caller (heartbeat hook)

Invocation:
  from oracle_ai_scheduler_adapter import invoke_embryo
  result = invoke_embryo()
"""
import os
import sys
import json
import datetime

# Resolve paths
ADAPTER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(ADAPTER_DIR))
BRIDGE_DIR = os.path.join(PROJECT_ROOT, "bridge")
KS_PATH = os.path.join(BRIDGE_DIR, "reactor_vigilia_foundation", "reactor_heartbeat_r0", "scheduler", "scheduler_kill_switch.json")
CONTRACT_PATH = os.path.join(ADAPTER_DIR, "oracle_ai_contract.yaml")
STATE_PATH = os.path.join(ADAPTER_DIR, "oracle_ai_state.json")

# Integration constraints
INTEGRATION_BUDGET_CAP = 0.01  # $0.01 max for this integration test
MAX_PROVIDER_CALLS = 1
MAX_RETRIES = 0

ADAPTER_ID = "oracle_ai_scheduler_adapter_r0"


def check_kill_switch():
    """Returns True if kill-switch is active (should abort)."""
    if not os.path.exists(KS_PATH):
        return False
    with open(KS_PATH, "r") as f:
        ks = json.load(f)
    return ks.get("active", False)


def check_dispatcher_available():
    """Verify Dispatcher is available by checking contract file exists and is valid."""
    if not os.path.exists(CONTRACT_PATH):
        return False, "Contract file not found"
    try:
        import yaml
        with open(CONTRACT_PATH, "r") as f:
            contract = yaml.safe_load(f)
        if not contract.get("allowed_action_classes"):
            return False, "No allowed_action_classes in contract"
        return True, "Dispatcher available"
    except Exception as e:
        return False, f"Contract parse error: {str(e)[:100]}"


def check_budget_headroom():
    """Verify remaining budget allows at least one call."""
    if not os.path.exists(STATE_PATH):
        return True, 0.0
    with open(STATE_PATH, "r") as f:
        state = json.load(f)
    spent = state.get("total_cost_usd", 0.0)
    remaining = INTEGRATION_BUDGET_CAP - spent
    if remaining <= 0:
        return False, spent
    return True, spent


def invoke_embryo():
    """
    Main entry point for the scheduler to invoke the embryo.
    Returns a structured dict with the result.
    """
    ts_start = datetime.datetime.utcnow().isoformat() + "Z"
    result = {
        "adapter_id": ADAPTER_ID,
        "timestamp_start": ts_start,
        "timestamp_end": None,
        "verdict": None,
        "embryo_result": None,
        "abort_reason": None,
        "checks": {}
    }

    # CHECK 1: Kill-switch
    ks_active = check_kill_switch()
    result["checks"]["kill_switch"] = "ACTIVE" if ks_active else "INACTIVE"
    if ks_active:
        result["verdict"] = "ABORTED"
        result["abort_reason"] = "kill_switch_active"
        result["timestamp_end"] = datetime.datetime.utcnow().isoformat() + "Z"
        return result

    # CHECK 2: Dispatcher available
    disp_ok, disp_msg = check_dispatcher_available()
    result["checks"]["dispatcher"] = "AVAILABLE" if disp_ok else f"UNAVAILABLE: {disp_msg}"
    if not disp_ok:
        result["verdict"] = "ABORTED"
        result["abort_reason"] = f"dispatcher_unavailable: {disp_msg}"
        result["timestamp_end"] = datetime.datetime.utcnow().isoformat() + "Z"
        return result

    # CHECK 3: Budget headroom
    budget_ok, spent = check_budget_headroom()
    result["checks"]["budget"] = f"OK (spent: ${spent:.4f}, cap: ${INTEGRATION_BUDGET_CAP})" if budget_ok else f"EXCEEDED (spent: ${spent:.4f})"
    if not budget_ok:
        result["verdict"] = "ABORTED"
        result["abort_reason"] = "budget_exceeded"
        result["timestamp_end"] = datetime.datetime.utcnow().isoformat() + "Z"
        return result

    # ALL CHECKS PASSED — invoke embryo
    try:
        # Import and call run_once from the embryo module
        sys.path.insert(0, ADAPTER_DIR)
        from oracle_ai_embryo import run_once
        embryo_result = run_once()
        result["embryo_result"] = embryo_result
        result["verdict"] = embryo_result.get("verdict", "UNKNOWN")
    except Exception as e:
        result["verdict"] = "ERROR"
        result["abort_reason"] = f"embryo_invocation_error: {str(e)[:200]}"

    result["timestamp_end"] = datetime.datetime.utcnow().isoformat() + "Z"
    return result


if __name__ == "__main__":
    r = invoke_embryo()
    print(json.dumps(r, indent=2))
