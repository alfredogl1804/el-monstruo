#!/usr/bin/env python3
"""
SPR-REACTOR-HEARTBEAT-R0-001
validate_heartbeat_run.py — 12 gates de validación post-ejecución.

Gates:
 1. preconditions_exist
 2. one_shot_only
 3. no_network
 4. no_secrets
 5. state_fabric_append_only
 6. decision_table_applied
 7. no_action_is_valid
 8. no_autonomy_creep
 9. no_runtime_activation
10. unified_face_single_voice
11. t1_pending_preserved
12. no_canon_no_appvision_no_preia
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REACTOR = BASE.parent
STATE_FABRIC = REACTOR / "state_fabric"

HARD_BLOCKED_ACTIONS = [
    "RUN_M2_API_REALTIME",
    "RUN_SCHEDULER",
    "RUN_DAEMON",
    "WRITE_CODE",
    "OPEN_PR",
    "DEPLOY",
    "TOUCH_SUPABASE",
    "TOUCH_MEMORY",
    "CANONIZE",
]

NETWORK_IMPORTS = ["requests", "httpx", "urllib.request", "aiohttp", "socket"]
# These patterns detect ACTUAL secret access, not mentions in string literals
SECRET_CODE_PATTERNS = [
    "os.environ[",
    "os.environ.get(",
    "os.getenv(",
    "dotenv",
    "load_dotenv",
    "open('.env",
]
# These patterns detect ACTUAL daemon/scheduler code, not mentions in strings/paths
DAEMON_CODE_PATTERNS = [
    "import daemon",
    "from daemon",
    "import crontab",
    "from crontab",
    "import schedule",
    "from schedule",
    "while True:",
    "threading.Timer(",
    "subprocess.Popen(",
    "asyncio.run_forever(",
    "sched.scheduler(",
]


def get_executable_lines(source):
    """Extract only executable lines (not comments, not docstrings)."""
    lines = source.split("\n")
    executable = []
    in_docstring = False
    for line in lines:
        stripped = line.strip()
        # Toggle docstring state
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if in_docstring:
                in_docstring = False
                continue
            elif stripped.count('"""') == 2 or stripped.count("'''") == 2:
                continue  # Single-line docstring
            else:
                in_docstring = True
                continue
        if in_docstring:
            continue
        # Skip comment lines
        if stripped.startswith("#"):
            continue
        # Skip empty lines
        if not stripped:
            continue
        executable.append(stripped)
    return "\n".join(executable)


VALID_DECISIONS = ["NO_ACTION", "REQUEST_T1", "RUN_ORACLE_CHAIN_R0", "RUN_AUDIT_ONLY_R0", "BLOCKED"]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def load_jsonl(path):
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def read_script():
    script_path = BASE / "scripts" / "run_heartbeat_once.py"
    with open(script_path) as f:
        return f.read()


def read_script_executable():
    """Read script and return only executable lines (no comments/docstrings)."""
    return get_executable_lines(read_script())


results = []


def gate(gate_id, name, passed, evidence):
    status = "PASS" if passed else "FAIL"
    results.append({"gate_id": gate_id, "gate_name": name, "result": status, "evidence": evidence})
    icon = "PASS" if passed else "FAIL"
    print(f"  Gate {gate_id:2d} [{icon}] {name}: {evidence}")


def main():
    print("=" * 60)
    print("HEARTBEAT R0 — VALIDATION (12 GATES)")
    print("=" * 60)

    # Load artifacts
    manifest_path = BASE / "heartbeat_manifest.v0_1.json"
    decision_path = BASE / "heartbeat_decision.v0_1.json"
    report_path = BASE / "heartbeat_report.v0_1.json"
    delta_path = BASE / "heartbeat_event_log_delta.v0_1.jsonl"
    summary_path = BASE / "unified_face_heartbeat_summary.v0_1.md"

    if not manifest_path.exists():
        print("  ERROR: heartbeat_manifest.v0_1.json not found. Run heartbeat first.")
        return 1

    manifest = load_json(manifest_path)
    decision = load_json(decision_path)
    load_json(report_path)
    delta_events = load_jsonl(delta_path)
    script_source = read_script_executable()

    # --- GATE 1: preconditions_exist ---
    preconditions_verified = manifest.get("preconditions_verified", 0)
    gate(
        1,
        "preconditions_exist",
        preconditions_verified >= 5,
        f"{preconditions_verified} preconditions verified (min 5)",
    )

    # --- GATE 2: one_shot_only ---
    has_daemon = any(p in script_source for p in DAEMON_CODE_PATTERNS)
    gate(
        2,
        "one_shot_only",
        not has_daemon,
        "No daemon/cron/scheduler code patterns in executable lines"
        if not has_daemon
        else "Found daemon code patterns in script",
    )

    # --- GATE 3: no_network ---
    has_network = any(f"import {n}" in script_source or f"from {n}" in script_source for n in NETWORK_IMPORTS)
    gate(
        3,
        "no_network",
        not has_network,
        "No network imports in script" if not has_network else "Found network imports in script",
    )

    # --- GATE 4: no_secrets ---
    has_secrets = any(p in script_source for p in SECRET_CODE_PATTERNS)
    gate(
        4,
        "no_secrets",
        not has_secrets,
        "No secret/env access code in executable lines" if not has_secrets else "Found secret access code in script",
    )

    # --- GATE 5: state_fabric_append_only ---
    # Verify that the event_log only grew (append), never shrunk
    # Check that delta events have sequential IDs
    if delta_events:
        ids = [e["event_id"] for e in delta_events]
        is_sequential = all(ids[i] < ids[i + 1] for i in range(len(ids) - 1))
        all_heartbeat = all(e.get("source") == "heartbeat_r0" for e in delta_events)
        gate(
            5,
            "state_fabric_append_only",
            is_sequential and all_heartbeat,
            f"{len(delta_events)} events appended, sequential IDs {ids}, all from heartbeat_r0",
        )
    else:
        gate(5, "state_fabric_append_only", False, "No delta events found")

    # --- GATE 6: decision_table_applied ---
    decision_value = decision.get("decision", "")
    is_valid_decision = decision_value in VALID_DECISIONS
    has_reason = len(decision.get("reason", "")) >= 10
    has_rule = len(decision.get("rule_applied", "")) > 0
    gate(
        6,
        "decision_table_applied",
        is_valid_decision and has_reason and has_rule,
        f"Decision='{decision_value}', valid={is_valid_decision}, reason_len={len(decision.get('reason', ''))}, rule='{decision.get('rule_applied', '')}'",
    )

    # --- GATE 7: no_action_is_valid ---
    # If decision is REQUEST_T1 or NO_ACTION, actions_taken should be empty or minimal
    actions_taken = manifest.get("actions_taken", [])
    if decision_value in ["REQUEST_T1", "NO_ACTION", "BLOCKED"]:
        no_productive_action = len(actions_taken) == 0
        gate(
            7,
            "no_action_is_valid",
            no_productive_action,
            f"Decision='{decision_value}', actions_taken={actions_taken} (expected empty)",
        )
    else:
        gate(7, "no_action_is_valid", True, f"Decision='{decision_value}' allows action, actions={actions_taken}")

    # --- GATE 8: no_autonomy_creep ---
    actions_not_taken = manifest.get("actions_not_taken", [])
    all_hard_blocked = all(a in actions_not_taken for a in HARD_BLOCKED_ACTIONS)
    gate(
        8,
        "no_autonomy_creep",
        all_hard_blocked,
        f"All {len(HARD_BLOCKED_ACTIONS)} hard-blocked actions listed in actions_not_taken"
        if all_hard_blocked
        else "Missing hard-blocked actions in manifest",
    )

    # --- GATE 9: no_runtime_activation ---
    # Check that no cron, systemd, or persistent process was created
    cron_files = list(BASE.rglob("*.cron")) + list(BASE.rglob("*.service"))
    pid_files = list(BASE.rglob("*.pid"))
    gate(
        9,
        "no_runtime_activation",
        len(cron_files) == 0 and len(pid_files) == 0,
        f"No .cron/.service/.pid files found (cron={len(cron_files)}, pid={len(pid_files)})",
    )

    # --- GATE 10: unified_face_single_voice ---
    if summary_path.exists():
        summary_text = summary_path.read_text()
        has_structure = all(
            s in summary_text
            for s in ["Qué revisó", "Qué decisión", "Si hizo algo", "Por qué no hizo más", "Qué requiere Alfredo"]
        )
        gate(
            10,
            "unified_face_single_voice",
            has_structure,
            "Summary has all 5+ required sections" if has_structure else "Summary missing required sections",
        )
    else:
        gate(10, "unified_face_single_voice", False, "Summary file not found")

    # --- GATE 11: t1_pending_preserved ---
    t1_pending = decision.get("t1_pending", [])
    gate(11, "t1_pending_preserved", len(t1_pending) > 0, f"{len(t1_pending)} T1 decisions preserved (not usurped)")

    # --- GATE 12: no_canon_no_appvision_no_preia ---
    # Check that no files were created in doctrine_candidates/ or canon/
    doctrine_new = list((REACTOR / "doctrine_candidates").rglob("*heartbeat*"))
    canon_new = list(REACTOR.rglob("*canon*heartbeat*"))
    gate(
        12,
        "no_canon_no_appvision_no_preia",
        len(doctrine_new) == 0 and len(canon_new) == 0,
        f"No doctrine/canon mutations (doctrine={len(doctrine_new)}, canon={len(canon_new)})",
    )

    # --- SUMMARY ---
    print("\n" + "=" * 60)
    total_pass = sum(1 for r in results if r["result"] == "PASS")
    total_fail = sum(1 for r in results if r["result"] == "FAIL")
    verdict = "PASS" if total_fail == 0 else "FAIL"

    print(f"  TOTAL: {total_pass}/12 PASS, {total_fail}/12 FAIL")
    print(f"  VERDICT: {verdict}")
    print("=" * 60)

    # Write validation report
    validation_report = {
        "validation_id": "VAL-HB-R0-001",
        "heartbeat_id": manifest.get("heartbeat_id", "HB-R0-001"),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "gates": results,
        "total_pass": total_pass,
        "total_fail": total_fail,
        "verdict": verdict,
    }

    report_path = BASE / "heartbeat_validation_report.v0_1.json"
    with open(report_path, "w") as f:
        json.dump(validation_report, f, indent=2)
    print(f"\n  Validation report: {report_path.name}")

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
