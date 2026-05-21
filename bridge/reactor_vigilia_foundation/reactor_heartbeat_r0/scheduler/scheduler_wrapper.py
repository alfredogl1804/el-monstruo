#!/usr/bin/env python3
"""
SPR-REACTOR-SCHEDULER-R0-001
scheduler_wrapper.py — Wrapper que ejecuta Heartbeat R0 de forma controlada.

Este script NO es un daemon. Es invocado por un mecanismo externo (GitHub Actions
cron o Manus scheduled task) cada 12 horas. Cada invocación:

1. Verifica kill-switch (si activo, aborta inmediatamente).
2. Verifica anti-loop (si ya se ejecutó en esta ventana de 12h, aborta).
3. Verifica consecutive failures (si 2+ fallos seguidos, pausa y pide T1).
4. Ejecuta run_heartbeat_once.py como subprocess.
5. Registra resultado en scheduler_state.json (contador, timestamps, resultado).
6. Genera scheduler_report.md para lectura humana.
7. Muere. No persiste. No loop. No daemon.

Reglas estrictas:
- No network / No API calls / No secrets / No env vars (salvo PATH)
- No daemon / No persistent process / No background job
- No Supabase / No DB / No deploy / No PR / No main
- Budget: $0 por ciclo (R0 es 100% local)
- Máximo 1 ejecución por ventana de 12h
- Si falla 2 veces seguidas → PAUSED, requiere T1
- Kill-switch: scheduler_kill_switch.json con {"active": true}
"""

import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# --- Paths ---
SCHEDULER_DIR = Path(__file__).resolve().parent
HEARTBEAT_DIR = SCHEDULER_DIR.parent
SCRIPTS_DIR = HEARTBEAT_DIR / "scripts"
HEARTBEAT_SCRIPT = SCRIPTS_DIR / "run_heartbeat_once.py"

# State files
STATE_FILE = SCHEDULER_DIR / "scheduler_state.json"
KILL_SWITCH_FILE = SCHEDULER_DIR / "scheduler_kill_switch.json"
REPORT_FILE = SCHEDULER_DIR / "scheduler_report.md"

# Configuration
WINDOW_HOURS = 12
MAX_CONSECUTIVE_FAILURES = 2


def now_utc():
    return datetime.now(timezone.utc)


def now_iso():
    return now_utc().isoformat()


def load_state() -> dict:
    """Load scheduler state or create default."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "total_cycles": 0,
        "successful_cycles": 0,
        "failed_cycles": 0,
        "consecutive_failures": 0,
        "last_run_at": None,
        "last_result": None,
        "last_decision": None,
        "status": "ACTIVE",
        "history": [],
    }


def save_state(state: dict):
    """Persist scheduler state."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def is_kill_switch_active() -> bool:
    """Check if kill-switch is engaged."""
    if not KILL_SWITCH_FILE.exists():
        return False
    with open(KILL_SWITCH_FILE) as f:
        data = json.load(f)
    return data.get("active", False)


def is_within_window(state: dict) -> bool:
    """Check if a run already happened within the current 12h window."""
    last_run = state.get("last_run_at")
    if not last_run:
        return False  # Never ran, not within window
    last_dt = datetime.fromisoformat(last_run)
    window_start = now_utc() - timedelta(hours=WINDOW_HOURS)
    return last_dt > window_start


def run_heartbeat() -> tuple[int, str]:
    """Execute run_heartbeat_once.py as subprocess. Returns (exit_code, output)."""
    try:
        result = subprocess.run(
            [sys.executable, str(HEARTBEAT_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout — heartbeat is local-only
            cwd=str(SCRIPTS_DIR),
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 99, "TIMEOUT: Heartbeat exceeded 120s limit."
    except Exception as e:
        return 98, f"EXCEPTION: {type(e).__name__}: {e}"


def extract_decision_from_output(output: str) -> str:
    """Parse heartbeat output to find the decision."""
    for line in output.split("\n"):
        if "Decision:" in line and "HEARTBEAT" not in line:
            parts = line.split("Decision:")
            if len(parts) > 1:
                return parts[1].strip()
    return "UNKNOWN"


def generate_report(state: dict, run_result: dict):
    """Generate human-readable scheduler report."""
    report = f"""# Scheduler Report — SPR-REACTOR-SCHEDULER-R0-001

**Generated:** {now_iso()}
**Status:** {state['status']}

## Current State

| Metric | Value |
|--------|-------|
| Total cycles | {state['total_cycles']} |
| Successful | {state['successful_cycles']} |
| Failed | {state['failed_cycles']} |
| Consecutive failures | {state['consecutive_failures']} |
| Last run | {state['last_run_at'] or 'Never'} |
| Last result | {state['last_result'] or 'N/A'} |
| Last decision | {state['last_decision'] or 'N/A'} |

## Last Run Details

| Field | Value |
|-------|-------|
| Timestamp | {run_result.get('timestamp', 'N/A')} |
| Exit code | {run_result.get('exit_code', 'N/A')} |
| Duration | {run_result.get('duration_seconds', 'N/A')}s |
| Decision | {run_result.get('decision', 'N/A')} |
| Outcome | {run_result.get('outcome', 'N/A')} |

## Configuration

| Setting | Value |
|---------|-------|
| Frequency | Every {WINDOW_HOURS}h |
| Mode | audit-only / report-only |
| Budget per cycle | $0 (R0 local) |
| Max consecutive failures | {MAX_CONSECUTIVE_FAILURES} |
| Kill-switch | {'ACTIVE' if is_kill_switch_active() else 'INACTIVE'} |

## Anti-Loop Protection

- Window: {WINDOW_HOURS}h
- Max 1 execution per window
- If {MAX_CONSECUTIVE_FAILURES} consecutive failures → PAUSED (requires T1)

## Kill-Switch

To stop the scheduler immediately, create or edit:
`scheduler/scheduler_kill_switch.json` with `{{"active": true}}`

To resume: set `{{"active": false}}` and reset `scheduler_state.json` status to "ACTIVE".
"""
    with open(REPORT_FILE, "w") as f:
        f.write(report)


def main():
    print("=" * 60)
    print("SPR-REACTOR-SCHEDULER-R0-001 — SCHEDULER WRAPPER")
    print("=" * 60)
    print(f"  Timestamp: {now_iso()}")

    # --- CHECK 1: Kill-switch ---
    if is_kill_switch_active():
        print("  [ABORT] Kill-switch is ACTIVE. Exiting immediately.")
        print("  To resume: set scheduler_kill_switch.json active=false")
        return 0  # Clean exit, not a failure

    # --- LOAD STATE ---
    state = load_state()
    print(f"  Total cycles so far: {state['total_cycles']}")
    print(f"  Status: {state['status']}")

    # --- CHECK 2: Paused state ---
    if state["status"] == "PAUSED":
        print(f"  [ABORT] Scheduler is PAUSED after {MAX_CONSECUTIVE_FAILURES} consecutive failures.")
        print("  Requires T1 decision to resume.")
        print("  To resume: set scheduler_state.json status to 'ACTIVE' and consecutive_failures to 0.")
        return 0

    # --- CHECK 3: Anti-loop (window check) ---
    if is_within_window(state):
        print(f"  [ABORT] Already executed within the last {WINDOW_HOURS}h window.")
        print(f"  Last run: {state['last_run_at']}")
        print("  Anti-loop protection active. Skipping.")
        return 0

    # --- EXECUTE HEARTBEAT ---
    print("\n  Executing Heartbeat R0...")
    start_time = now_utc()
    exit_code, output = run_heartbeat()
    end_time = now_utc()
    duration = (end_time - start_time).total_seconds()

    decision = extract_decision_from_output(output)
    print(f"  Exit code: {exit_code}")
    print(f"  Duration: {duration:.1f}s")
    print(f"  Decision: {decision}")

    # --- UPDATE STATE ---
    run_result = {
        "timestamp": now_iso(),
        "exit_code": exit_code,
        "duration_seconds": round(duration, 2),
        "decision": decision,
        "outcome": "SUCCESS" if exit_code == 0 else "FAILURE",
    }

    state["total_cycles"] += 1
    state["last_run_at"] = now_iso()
    state["last_result"] = run_result["outcome"]
    state["last_decision"] = decision

    if exit_code == 0:
        state["successful_cycles"] += 1
        state["consecutive_failures"] = 0
        print("  [OK] Heartbeat completed successfully.")
    else:
        state["failed_cycles"] += 1
        state["consecutive_failures"] += 1
        print(f"  [FAIL] Heartbeat failed (exit={exit_code}).")
        if state["consecutive_failures"] >= MAX_CONSECUTIVE_FAILURES:
            state["status"] = "PAUSED"
            print(f"  [PAUSED] {MAX_CONSECUTIVE_FAILURES} consecutive failures. Scheduler paused.")
            print("  Requires T1 decision to resume.")

    # Keep last 20 runs in history
    state["history"].append(run_result)
    state["history"] = state["history"][-20:]

    save_state(state)
    generate_report(state, run_result)

    print(f"\n  State saved: {STATE_FILE.name}")
    print(f"  Report saved: {REPORT_FILE.name}")
    print("\n  Scheduler wrapper dying. No daemon. No loop. No persistent process.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
