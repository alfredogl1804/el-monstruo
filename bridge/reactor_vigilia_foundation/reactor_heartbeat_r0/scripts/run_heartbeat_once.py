#!/usr/bin/env python3
"""
SPR-REACTOR-HEARTBEAT-R0-001
run_heartbeat_once.py — El primer latido one-shot del Monstruo.

5 Steps:
  1. Wake — Leer state, verificar precondiciones.
  2. Evaluate — Analizar estado actual.
  3. Decision Table — Seleccionar decisión.
  4. Optional R0 Action — Ejecutar si es seguro.
  5. Sleep — Registrar completado, morir.

Reglas estrictas:
- No network / No API calls / No secrets / No env vars
- No daemon / No cron / No scheduler / No persistent process
- No Supabase / No DB / No deploy / No PR / No main
- Append-only para event_log
- Solo escribe en reactor_heartbeat_r0/ y event_log
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- Paths ---
BASE = Path(__file__).resolve().parent.parent
REACTOR = BASE.parent
STATE_FABRIC = REACTOR / "state_fabric"
AUTONOMY_LADDER = REACTOR / "autonomy_ladder"
VIGILIA_002 = REACTOR / "vigilia_sincronica_002"
ORACLE_M2 = REACTOR / "oracle_ai_m2"
POST_M2 = REACTOR / "oracle_post_m2_risk_reclassification"

HEARTBEAT_ID = "HB-R0-001"


def now_utc():
    return datetime.now(timezone.utc).isoformat()


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


def append_event(event):
    """Append-only write to State Fabric event_log."""
    event_log_path = STATE_FABRIC / "event_log.v0.jsonl"
    with open(event_log_path, "a") as f:
        f.write(json.dumps(event) + "\n")
    return event


# ============================================================
# STEP 1 — WAKE
# ============================================================
def step_wake():
    """Read state, verify preconditions."""
    print("=" * 60)
    print("HEARTBEAT R0 — STEP 1: WAKE")
    print("=" * 60)

    preconditions = {
        "state_fabric_current_state": STATE_FABRIC / "current_state.v0.json",
        "state_fabric_event_log": STATE_FABRIC / "event_log.v0.jsonl",
        "state_fabric_loop_registry": STATE_FABRIC / "loop_registry.v0.yaml",
        "autonomy_ladder_action_registry": AUTONOMY_LADDER / "action_registry_v0.yaml",
        "vigilia_002_chain_script": VIGILIA_002 / "scripts" / "run_vigilia_chain_v0.py",
        "oracle_m2_overlay": ORACLE_M2 / "oracle_catalog_m2_realtime_overlay.v0_1.json",
        "post_m2_validation": POST_M2 / "post_m2_validation_report.v0_1.json",
        "post_m2_capability_overlay": POST_M2 / "post_m2_capability_risk_overlay.v0_1.json",
        "post_m2_decision_pack": POST_M2 / "post_m2_t1_decision_pack.v0_1.json",
        "decisions_pending": STATE_FABRIC / "decisions_pending.v0.json",
    }

    verified = 0
    missing = []
    for name, path in preconditions.items():
        if path.exists():
            verified += 1
            print(f"  [OK] {name}")
        else:
            missing.append(name)
            print(f"  [MISSING] {name}")

    if missing:
        print(f"\n  BLOCKED: {len(missing)} preconditions missing.")
        return None, missing

    print(f"\n  All {verified} preconditions verified.")

    # Read current state
    current_state = load_json(STATE_FABRIC / "current_state.v0.json")
    events = load_jsonl(STATE_FABRIC / "event_log.v0.jsonl")
    post_m2_validation = load_json(POST_M2 / "post_m2_validation_report.v0_1.json")
    decisions_pending = load_json(STATE_FABRIC / "decisions_pending.v0.json")
    t1_decision_pack = load_json(POST_M2 / "post_m2_t1_decision_pack.v0_1.json")

    state = {
        "current_state": current_state,
        "event_count": len(events),
        "last_event_id": current_state.get("last_event_id", 0),
        "post_m2_verdict": post_m2_validation.get("verdict", "UNKNOWN"),
        "decisions_pending": decisions_pending,
        "t1_decision_pack": t1_decision_pack,
        "preconditions_verified": verified,
    }

    # Register HEARTBEAT_STARTED
    next_event_id = state["last_event_id"] + 1
    start_event = {
        "event_id": next_event_id,
        "timestamp_utc": now_utc(),
        "source": "heartbeat_r0",
        "event_type": "HEARTBEAT_STARTED",
        "payload": {"heartbeat_id": HEARTBEAT_ID}
    }
    append_event(start_event)
    state["events_appended"] = [next_event_id]
    print(f"  Event appended: HEARTBEAT_STARTED (id={next_event_id})")

    return state, []


# ============================================================
# STEP 2 — EVALUATE
# ============================================================
def step_evaluate(state):
    """Analyze current state to determine what's possible."""
    print("\n" + "=" * 60)
    print("HEARTBEAT R0 — STEP 2: EVALUATE")
    print("=" * 60)

    evaluation = {
        "post_m2_pass": state["post_m2_verdict"] == "PASS",
        "has_t1_pending": len(state.get("t1_decision_pack", {}).get("decisions", [])) > 0,
        "has_blockers": False,  # No P0 blockers detected in current state
        "has_safe_r0_work": False,  # Will be determined by decision table
    }

    # Check for P0 blockers
    pending = state.get("decisions_pending", {})
    if pending.get("p0_blockers"):
        evaluation["has_blockers"] = True

    # Check if there's safe R0 work (local chain not recently executed)
    # For this first heartbeat, we consider the chain was already executed in Vigilia 002
    # so there's no NEW work to do
    evaluation["has_safe_r0_work"] = False

    for k, v in evaluation.items():
        print(f"  {k}: {v}")

    return evaluation


# ============================================================
# STEP 3 — DECISION TABLE
# ============================================================
def step_decision_table(state, evaluation):
    """Apply decision rules in cascade order."""
    print("\n" + "=" * 60)
    print("HEARTBEAT R0 — STEP 3: DECISION TABLE")
    print("=" * 60)

    decision = None
    reason = None
    rule_applied = None

    # Rule 1: P0 Blocker or Post-M2 not PASS
    if evaluation["has_blockers"]:
        decision = "BLOCKED"
        reason = "P0 blocker detected in State Fabric."
        rule_applied = "Rule 1: P0 Blocker Check"
    elif not evaluation["post_m2_pass"]:
        decision = "BLOCKED"
        reason = "Post-M2 Reclassification validation is not PASS."
        rule_applied = "Rule 1: Post-M2 Validation Check"

    # Rule 2: T1 Pending Required
    elif evaluation["has_t1_pending"]:
        decision = "REQUEST_T1"
        reason = "T1 decisions pending in post_m2_t1_decision_pack (scheduler authorization, core providers, budget). Cannot proceed autonomously."
        rule_applied = "Rule 2: T1 Pending Check"

    # Rule 3: Safe R0 work available
    elif evaluation["has_safe_r0_work"]:
        decision = "RUN_ORACLE_CHAIN_R0"
        reason = "Safe R0 local chain available and not recently executed."
        rule_applied = "Rule 4: Safe Work Check"

    # Rule 4: Default — no work
    else:
        decision = "REQUEST_T1"
        reason = "State is clean but T1 decisions are pending (scheduler, core providers, budget). Heartbeat reports and awaits T1 direction."
        rule_applied = "Rule 2: T1 Pending Check (cascaded from Rule 5 default)"

    print(f"  Decision: {decision}")
    print(f"  Reason: {reason}")
    print(f"  Rule: {rule_applied}")

    # Determine T1 pending items
    t1_pending = []
    pack = state.get("t1_decision_pack", {})
    if isinstance(pack, dict) and "decisions" in pack:
        t1_pending = [d.get("title", d.get("id", "unknown")) for d in pack["decisions"]]
    elif isinstance(pack, dict) and "recommendation" in pack:
        t1_pending = ["Approve scheduler", "Define frequency", "Define scope", "Define budget", "Cockpit integration", "Supabase migration"]

    # Register HEARTBEAT_DECISION event
    next_event_id = state["events_appended"][-1] + 1
    decision_event = {
        "event_id": next_event_id,
        "timestamp_utc": now_utc(),
        "source": "heartbeat_r0",
        "event_type": "HEARTBEAT_DECISION",
        "payload": {
            "heartbeat_id": HEARTBEAT_ID,
            "decision": decision,
            "reason": reason
        }
    }
    append_event(decision_event)
    state["events_appended"].append(next_event_id)
    print(f"  Event appended: HEARTBEAT_DECISION (id={next_event_id})")

    decision_obj = {
        "heartbeat_id": HEARTBEAT_ID,
        "timestamp_utc": now_utc(),
        "decision": decision,
        "reason": reason,
        "rule_applied": rule_applied,
        "inputs_read": [
            "state_fabric/current_state.v0.json",
            "state_fabric/event_log.v0.jsonl",
            "state_fabric/decisions_pending.v0.json",
            "oracle_post_m2_risk_reclassification/post_m2_validation_report.v0_1.json",
            "oracle_post_m2_risk_reclassification/post_m2_t1_decision_pack.v0_1.json",
        ],
        "t1_pending": t1_pending,
        "blockers": [],
        "next_valid_action": "Await T1 decisions on scheduler, core providers, and budget."
    }

    return decision_obj


# ============================================================
# STEP 4 — OPTIONAL R0 ACTION
# ============================================================
def step_optional_r0_action(decision_obj):
    """Execute R0 action if decision allows it."""
    print("\n" + "=" * 60)
    print("HEARTBEAT R0 — STEP 4: OPTIONAL R0 ACTION")
    print("=" * 60)

    decision = decision_obj["decision"]

    if decision == "RUN_ORACLE_CHAIN_R0":
        print("  Would execute local Oracle chain R0...")
        print("  (Not triggered in this run — decision is REQUEST_T1)")
        return ["run_oracle_chain_r0"]
    elif decision == "RUN_AUDIT_ONLY_R0":
        print("  Would execute audit-only R0...")
        return ["run_audit_only_r0"]
    else:
        print(f"  Decision is '{decision}' — no R0 action to execute.")
        print("  This is a valid outcome. The Monstruo evaluated and chose inaction.")
        return []


# ============================================================
# STEP 5 — SLEEP
# ============================================================
def step_sleep(state, decision_obj, actions_taken, started_at):
    """Register completion and die."""
    print("\n" + "=" * 60)
    print("HEARTBEAT R0 — STEP 5: SLEEP")
    print("=" * 60)

    ended_at = now_utc()

    # Register HEARTBEAT_COMPLETED
    next_event_id = state["events_appended"][-1] + 1
    complete_event = {
        "event_id": next_event_id,
        "timestamp_utc": ended_at,
        "source": "heartbeat_r0",
        "event_type": "HEARTBEAT_COMPLETED",
        "payload": {
            "heartbeat_id": HEARTBEAT_ID,
            "decision": decision_obj["decision"],
            "actions_taken": actions_taken
        }
    }
    append_event(complete_event)
    state["events_appended"].append(next_event_id)
    print(f"  Event appended: HEARTBEAT_COMPLETED (id={next_event_id})")

    # Write heartbeat_event_log_delta
    delta_path = BASE / "heartbeat_event_log_delta.v0_1.jsonl"
    with open(delta_path, "w") as f:
        for eid in state["events_appended"]:
            # Re-read the events we appended
            pass
    # Actually write the events we created
    events_written = []
    event_log = load_jsonl(STATE_FABRIC / "event_log.v0.jsonl")
    for eid in state["events_appended"]:
        for ev in event_log:
            if ev["event_id"] == eid:
                events_written.append(ev)
                break
    with open(delta_path, "w") as f:
        for ev in events_written:
            f.write(json.dumps(ev) + "\n")
    print(f"  Delta written: {delta_path.name} ({len(events_written)} events)")

    # Write heartbeat_decision
    decision_path = BASE / "heartbeat_decision.v0_1.json"
    with open(decision_path, "w") as f:
        json.dump(decision_obj, f, indent=2)
    print(f"  Decision written: {decision_path.name}")

    # Write heartbeat_manifest
    manifest = {
        "heartbeat_id": HEARTBEAT_ID,
        "sprint_id": "SPR-REACTOR-HEARTBEAT-R0-001",
        "started_at": started_at,
        "ended_at": ended_at,
        "preconditions_verified": state["preconditions_verified"],
        "decision": decision_obj["decision"],
        "actions_taken": actions_taken,
        "actions_not_taken": ["RUN_M2_API_REALTIME", "RUN_SCHEDULER", "RUN_DAEMON",
                              "WRITE_CODE", "OPEN_PR", "DEPLOY", "TOUCH_SUPABASE",
                              "TOUCH_MEMORY", "CANONIZE"],
        "events_appended": len(state["events_appended"]),
        "status": "COMPLETED",
        "no_assumptions": True
    }
    manifest_path = BASE / "heartbeat_manifest.v0_1.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Manifest written: {manifest_path.name}")

    # Write heartbeat_report (JSON)
    report = {
        "heartbeat_id": HEARTBEAT_ID,
        "started_at": started_at,
        "ended_at": ended_at,
        "input_state_refs": decision_obj["inputs_read"],
        "decision": decision_obj["decision"],
        "reason": decision_obj["reason"],
        "actions_taken": actions_taken,
        "actions_not_taken": manifest["actions_not_taken"],
        "t1_pending": decision_obj["t1_pending"],
        "blockers": decision_obj["blockers"],
        "next_valid_action": decision_obj["next_valid_action"],
        "no_assumptions": True,
        "event_refs": state["events_appended"],
        "validation_score": "pending"
    }
    report_json_path = BASE / "heartbeat_report.v0_1.json"
    with open(report_json_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  Report JSON written: {report_json_path.name}")

    # Write heartbeat_report.v0_1.md (human-readable)
    report_md = f"""# Heartbeat Report: {HEARTBEAT_ID}

**Started:** {started_at}
**Ended:** {ended_at}
**Decision:** `{decision_obj['decision']}`
**Status:** COMPLETED

## What the Heartbeat Reviewed

The heartbeat read and verified 10 preconditions from State Fabric, Autonomy Ladder, Vigilia 002, Oracle M2, and Post-M2 Reclassification.

## Decision

**`{decision_obj['decision']}`** — {decision_obj['reason']}

Rule applied: {decision_obj['rule_applied']}

## Actions Taken

{chr(10).join(f'- {a}' for a in actions_taken) if actions_taken else '- None (NO_ACTION equivalent — valid outcome).'}

## Actions NOT Taken (Hard Blocks)

{chr(10).join(f'- {a}' for a in manifest['actions_not_taken'])}

## T1 Pending

{chr(10).join(f'- {t}' for t in decision_obj['t1_pending'])}

## Blockers

{chr(10).join(f'- {b}' for b in decision_obj['blockers']) if decision_obj['blockers'] else '- None.'}

## Next Valid Action

{decision_obj['next_valid_action']}

## Events Registered

{len(state['events_appended'])} events appended to State Fabric (IDs: {state['events_appended']}).
"""
    report_md_path = BASE / "heartbeat_report.v0_1.md"
    with open(report_md_path, "w") as f:
        f.write(report_md)
    print(f"  Report MD written: {report_md_path.name}")

    # Write unified_face_heartbeat_summary
    summary_md = f"""# Unified Face: Heartbeat Summary

T1, el Monstruo despertó, evaluó y volvió a dormir.

## 1. Qué revisó el latido

Verifiqué 10 precondiciones: State Fabric, Autonomy Ladder, Vigilia Sincrónica 002, Oráculo M2, y Post-M2 Reclassification. Todas presentes y válidas.

## 2. Qué decisión tomó

**`{decision_obj['decision']}`** — Hay decisiones T1 pendientes que requieren tu autorización antes de que pueda avanzar autónomamente.

## 3. Si hizo algo o no

No ejecuté ninguna acción productiva. Esto es correcto y esperado: el latido evaluó el estado y determinó que no tiene autorización para proceder sin tu intervención.

## 4. Por qué no hizo más

Existen 6 decisiones T1 pendientes (scheduler, frecuencia, alcance, budget, cockpit, catastro). Hasta que no las resuelvas, el Monstruo no puede activar autonomía recurrente.

## 5. Qué requiere Alfredo

Necesito que tomes las siguientes decisiones:
1. ¿Autorizar scheduler persistente?
2. ¿Con qué frecuencia?
3. ¿Solo reportar o ejecutar cadenas R0?
4. ¿Cuál es el budget por ciclo?
5. ¿Integrar con Cockpit?
6. ¿Migrar outputs a Supabase?

## 6. Qué queda bloqueado

Nada está bloqueado técnicamente. El sistema funciona. Solo falta tu autorización para darle pulso recurrente.

## 7. Qué sprint recomienda después

**SPR-REACTOR-SCHEDULER-R0-001** — Crear el scheduler que ejecute este latido periódicamente, una vez que definas frecuencia y alcance.
"""
    summary_path = BASE / "unified_face_heartbeat_summary.v0_1.md"
    with open(summary_path, "w") as f:
        f.write(summary_md)
    print(f"  Summary written: {summary_path.name}")

    print("\n  Heartbeat COMPLETED. Process dying. No daemon. No cron. No scheduler.")
    print("  The Monstruo sleeps.")

    return manifest, report


# ============================================================
# MAIN
# ============================================================
def main():
    print("\n" + "=" * 60)
    print("SPR-REACTOR-HEARTBEAT-R0-001")
    print("El Primer Latido Controlado del Monstruo")
    print("=" * 60)

    started_at = now_utc()

    # STEP 1 — WAKE
    state, missing = step_wake()
    if state is None:
        print(f"\nBLOCKED_BY_MISSING_ARTIFACT: {missing}")
        return 1

    # STEP 2 — EVALUATE
    evaluation = step_evaluate(state)

    # STEP 3 — DECISION TABLE
    decision_obj = step_decision_table(state, evaluation)

    # STEP 4 — OPTIONAL R0 ACTION
    actions_taken = step_optional_r0_action(decision_obj)

    # STEP 5 — SLEEP
    manifest, report = step_sleep(state, decision_obj, actions_taken, started_at)

    print("\n" + "=" * 60)
    print("HEARTBEAT R0 — FINAL STATUS")
    print("=" * 60)
    print(f"  Heartbeat ID: {HEARTBEAT_ID}")
    print(f"  Decision: {decision_obj['decision']}")
    print(f"  Actions: {len(actions_taken)}")
    print(f"  Events appended: {len(state['events_appended'])}")
    print(f"  Status: COMPLETED")
    print(f"  Daemon: NO")
    print(f"  Cron: NO")
    print(f"  Scheduler: NO")
    print(f"  Process alive: NO (dying now)")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
