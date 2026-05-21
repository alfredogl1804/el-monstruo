#!/usr/bin/env python3
"""
Heartbeat Oracle Hook
Connects the Heartbeat R0 scheduler to the Oracle AI Embryo R0 via the adapter.

Chain:
  Heartbeat R0 → heartbeat_oracle_hook → adapter.invoke_embryo() → embryo.run_once()

Invocation:
  python3 scheduler/heartbeat_oracle_hook.py --run-once

Constraints:
- Uses existing LIMITED_ACTIVE_R0 window (no new cron)
- Budget max $0.01
- Max 1 provider call
- Retries 0
- No provider auto-replacement
"""
import os
import sys
import json
import datetime

# Resolve paths
HOOK_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HOOK_DIR))))
EMBRYO_DIR = os.path.join(PROJECT_ROOT, "embryos", "oracle_ai")
BRIDGE_DIR = os.path.join(PROJECT_ROOT, "bridge")
KS_PATH = os.path.join(HOOK_DIR, "scheduler_kill_switch.json")
EVENT_LOG_PATH = os.path.join(BRIDGE_DIR, "embryos", "oracle_ai_r0", "event_log.jsonl")

HOOK_ID = "heartbeat_oracle_hook_r0"


def write_event(event_type, payload):
    """Write event to the embryo's event log."""
    os.makedirs(os.path.dirname(EVENT_LOG_PATH), exist_ok=True)
    event = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "source": HOOK_ID,
        "event_type": event_type,
        "payload": payload
    }
    with open(EVENT_LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")
    return event


def check_kill_switch():
    """Returns True if kill-switch is active."""
    if not os.path.exists(KS_PATH):
        return False
    with open(KS_PATH, "r") as f:
        ks = json.load(f)
    return ks.get("active", False)


def run_once():
    """
    Single heartbeat cycle that invokes the Oracle AI Embryo via adapter.
    """
    ts_start = datetime.datetime.utcnow().isoformat() + "Z"
    print(f"{'='*60}")
    print(f"HOOK: {HOOK_ID} — run_once()")
    print(f"{'='*60}")

    # Pre-check: kill-switch at hook level
    if check_kill_switch():
        print("  [ABORT] Kill-switch is ACTIVE at hook level.")
        write_event("HOOK_ABORTED", {"reason": "kill_switch_active"})
        return {
            "hook_id": HOOK_ID,
            "verdict": "ABORTED",
            "reason": "kill_switch_active",
            "timestamp_start": ts_start,
            "timestamp_end": datetime.datetime.utcnow().isoformat() + "Z"
        }

    # Register hook start
    write_event("HOOK_STARTED", {"hook_id": HOOK_ID})
    print(f"  Hook started at {ts_start}")

    # Import and invoke the adapter
    sys.path.insert(0, EMBRYO_DIR)
    try:
        from oracle_ai_scheduler_adapter import invoke_embryo
        print("  Invoking adapter...")
        adapter_result = invoke_embryo()
    except Exception as e:
        error_msg = f"adapter_import_error: {str(e)[:200]}"
        print(f"  [ERROR] {error_msg}")
        write_event("HOOK_ERROR", {"error": error_msg})
        return {
            "hook_id": HOOK_ID,
            "verdict": "ERROR",
            "reason": error_msg,
            "timestamp_start": ts_start,
            "timestamp_end": datetime.datetime.utcnow().isoformat() + "Z"
        }

    # Register hook completion
    ts_end = datetime.datetime.utcnow().isoformat() + "Z"
    verdict = adapter_result.get("verdict", "UNKNOWN")
    embryo_result = adapter_result.get("embryo_result", {})

    write_event("HOOK_COMPLETED", {
        "hook_id": HOOK_ID,
        "adapter_verdict": verdict,
        "embryo_task": embryo_result.get("task") if embryo_result else None,
        "embryo_cost": embryo_result.get("cost") if embryo_result else None
    })

    print(f"  Adapter verdict: {verdict}")
    if embryo_result:
        print(f"  Embryo task: {embryo_result.get('task', 'N/A')}")
        print(f"  Embryo cost: ${embryo_result.get('cost', 0):.6f}")
    print(f"{'='*60}")

    return {
        "hook_id": HOOK_ID,
        "verdict": verdict,
        "adapter_result": adapter_result,
        "timestamp_start": ts_start,
        "timestamp_end": ts_end
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Heartbeat Oracle Hook R0")
    parser.add_argument("--run-once", action="store_true", help="Execute a single hook cycle")
    args = parser.parse_args()

    if args.run_once:
        result = run_once()
        print(f"\nHook Result: {json.dumps(result, indent=2)}")
    else:
        print("Usage: python3 heartbeat_oracle_hook.py --run-once")
        sys.exit(1)
