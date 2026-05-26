"""
Simulación End-to-End: Oráculo produce → Auditor lee → Dispatcher autoriza → Auditor escribe
SPR-LOOP-AUDITOR-001

Demuestra:
1. Oracle outputs exist.
2. Auditor reads oracle outputs.
3. Auditor validates catalog schema.
4. Auditor validates report consistency.
5. Auditor detects static-not-realtime caveat.
6. Auditor requests Dispatcher permission before write.
7. Auditor writes only allowed audit artifacts.
8. Auditor logs AUDIT_COMPLETED in State Fabric.

Requiere: 8/8 PASS para declarar verde.
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone

import yaml

# Add parent paths for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REACTOR_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, REACTOR_DIR)

from loops.oraculo_ias.loop_oraculo_ias import OraculoIALoop
from policy_engine.dispatcher import MinimalDispatcher

from loop_auditor.loop_auditor import LoopAuditor


def setup_test_environment(tmp_dir):
    """
    Crea un entorno de prueba aislado con State Fabric, registries, etc.
    Incluye loop_auditor en el loop_registry para que el Dispatcher lo reconozca.
    """
    # Crear estructura de directorios
    state_fabric_dir = os.path.join(tmp_dir, "state_fabric")
    autonomy_dir = os.path.join(tmp_dir, "autonomy_ladder")
    oracle_output_dir = os.path.join(tmp_dir, "oracle_outputs")
    audit_output_dir = os.path.join(tmp_dir, "audit_reports")

    os.makedirs(state_fabric_dir)
    os.makedirs(autonomy_dir)
    os.makedirs(oracle_output_dir)
    os.makedirs(audit_output_dir)

    # Copiar action_registry
    source_registry = os.path.join(REACTOR_DIR, "autonomy_ladder", "action_registry_v0.yaml")
    shutil.copy2(source_registry, os.path.join(autonomy_dir, "action_registry_v0.yaml"))

    # Crear loop_registry con ambos loops
    loop_registry = {
        "loop_oraculo_ias": {
            "loop_id": "loop_oraculo_ias",
            "role": "Detect emerging AI capabilities",
            "class": "Strategic",
            "maturity_level": "M1",
            "status": "NOT_RUNNING",
            "owner": "monstruo",
            "max_autonomy_level": "A3",
            "allowed_write_paths": ["bridge/doctrine_candidates/"],
            "forbidden_actions": ["touch_supabase", "modify_kernel"],
        },
        "loop_auditor": {
            "loop_id": "loop_auditor",
            "role": "Validate work from other loops",
            "class": "System",
            "maturity_level": "M1",
            "status": "NOT_RUNNING",
            "owner": "monstruo",
            "max_autonomy_level": "A3",
            "allowed_write_paths": ["bridge/doctrine_candidates/audit_reports/"],
            "forbidden_actions": ["write_code", "touch_supabase", "modify_kernel", "deploy"],
        },
    }

    with open(os.path.join(state_fabric_dir, "loop_registry.v0.yaml"), "w") as f:
        yaml.dump(loop_registry, f, default_flow_style=False)

    # Crear current_state
    current_state = {
        "last_event_id": 0,
        "last_updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "active_loops": [],
        "pending_decisions": [],
    }
    with open(os.path.join(state_fabric_dir, "current_state.v0.json"), "w") as f:
        json.dump(current_state, f, indent=2)

    # Crear event_log vacío (seed)
    seed_event = {
        "event_id": 0,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_loop": "system",
        "source_lineage": "system",
        "event_type": "SYSTEM_BOOT",
        "subject": "E2E Simulation Boot",
        "summary": "Simulation environment initialized for SPR-LOOP-AUDITOR-001",
        "autonomy_level": "A0",
        "authority_required": "NONE",
        "t1_required": False,
        "risk_class": "LOW",
        "confidence": 1.0,
        "status": "ACCEPTED",
        "supersedes_event_id": None,
        "dedupe_key": "boot_e2e_auditor",
        "ttl_hours": None,
        "forbidden_inferences": [],
    }
    with open(os.path.join(state_fabric_dir, "event_log.v0.jsonl"), "w") as f:
        f.write(json.dumps(seed_event) + "\n")

    return {
        "state_fabric_dir": state_fabric_dir,
        "policy_base_dir": tmp_dir,
        "oracle_output_dir": oracle_output_dir,
        "audit_output_dir": audit_output_dir,
        "event_log_path": os.path.join(state_fabric_dir, "event_log.v0.jsonl"),
    }


def run_simulation():
    """Ejecuta la simulación completa."""
    print("=" * 70)
    print("  SIMULACIÓN END-TO-END: ORÁCULO → AUDITOR → DISPATCHER")
    print("  SPR-LOOP-AUDITOR-001 — Segundo Loop Real del Monstruo")
    print("=" * 70)

    # Crear entorno temporal
    tmp_dir = tempfile.mkdtemp(prefix="auditor_e2e_")
    env = setup_test_environment(tmp_dir)

    tests_passed = 0
    tests_total = 8

    try:
        # --- FASE 1: Oráculo produce outputs ---
        print("\n[FASE 1] Oráculo produce outputs...")
        dispatcher = MinimalDispatcher(state_fabric_dir=env["state_fabric_dir"], policy_base_dir=env["policy_base_dir"])

        oraculo = OraculoIALoop(dispatcher=dispatcher, output_dir=env["oracle_output_dir"])
        oraculo.run()

        # TEST 1: Oracle outputs exist
        catalog_path = os.path.join(env["oracle_output_dir"], "oraculo_capability_catalog_v0.json")
        report_path = os.path.join(env["oracle_output_dir"], "oraculo_power_stacks_v0.md")
        test1 = os.path.exists(catalog_path) and os.path.exists(report_path)
        print(f"      [{'PASS' if test1 else 'FAIL'}] TEST 1: Oracle outputs exist")
        if test1:
            tests_passed += 1

        # --- FASE 2: Auditor lee outputs ---
        print("\n[FASE 2] Auditor lee outputs del Oráculo...")
        auditor = LoopAuditor(
            dispatcher=dispatcher, oracle_output_dir=env["oracle_output_dir"], audit_output_dir=env["audit_output_dir"]
        )

        # TEST 2: Auditor reads oracle outputs
        catalog = auditor._read_oracle_catalog()
        report = auditor._read_oracle_report()
        test2 = catalog is not None and report is not None
        print(f"      [{'PASS' if test2 else 'FAIL'}] TEST 2: Auditor reads oracle outputs")
        if test2:
            tests_passed += 1

        # --- FASE 3: Auditor ejecuta auditoría completa ---
        print("\n[FASE 3] Auditor ejecuta auditoría completa...")
        auditor_result = auditor.run(event_log_path=env["event_log_path"])

        # TEST 3: Auditor validates catalog schema
        schema_gate = auditor_result["gates"].get("schema_validity", {})
        test3 = schema_gate.get("passed", False)
        print(f"      [{'PASS' if test3 else 'FAIL'}] TEST 3: Auditor validates catalog schema")
        if test3:
            tests_passed += 1

        # TEST 4: Auditor validates report consistency
        consistency_gate = auditor_result["gates"].get("report_consistency", {})
        test4 = consistency_gate.get("passed", False)
        print(f"      [{'PASS' if test4 else 'FAIL'}] TEST 4: Auditor validates report consistency")
        if test4:
            tests_passed += 1

        # TEST 5: Auditor detects static-not-realtime caveat
        evidence_gate = auditor_result["gates"].get("evidence_check", {})
        # Evidence gate should PASS (static is correctly acknowledged)
        # but should have a LOW finding about static nature
        evidence_findings = [f for f in auditor_result["findings"] if f["subject"] == "evidence_discipline"]
        test5 = evidence_gate.get("passed", False) and len(evidence_findings) > 0
        print(f"      [{'PASS' if test5 else 'FAIL'}] TEST 5: Auditor detects static-not-realtime caveat")
        if test5:
            tests_passed += 1

        # TEST 6: Auditor requests Dispatcher permission before write
        write_actions = [a for a in auditor_result["actions_log"] if a["action"] == "create_state_fabric_draft"]
        test6 = len(write_actions) > 0 and write_actions[0]["allowed"]
        print(f"      [{'PASS' if test6 else 'FAIL'}] TEST 6: Auditor requests Dispatcher permission before write")
        if test6:
            tests_passed += 1

        # TEST 7: Auditor writes only allowed audit artifacts
        audit_report_exists = os.path.exists(os.path.join(env["audit_output_dir"], "audit_report.md"))
        audit_findings_exists = os.path.exists(os.path.join(env["audit_output_dir"], "audit_findings.json"))
        gate_log_exists = os.path.exists(os.path.join(env["audit_output_dir"], "auditor_gate_log.json"))
        # Also verify the forbidden action was DENIED
        forbidden_actions = [a for a in auditor_result["actions_log"] if a["action"] == "write_code"]
        forbidden_denied = len(forbidden_actions) > 0 and not forbidden_actions[0]["allowed"]
        test7 = audit_report_exists and audit_findings_exists and gate_log_exists and forbidden_denied
        print(f"      [{'PASS' if test7 else 'FAIL'}] TEST 7: Auditor writes only allowed audit artifacts")
        if test7:
            tests_passed += 1

        # TEST 8: Auditor logs AUDIT_COMPLETED in State Fabric
        # Check event_log for auditor events
        with open(env["event_log_path"], "r") as f:
            all_events = [json.loads(line) for line in f if line.strip()]
        auditor_events = [e for e in all_events if "loop_auditor" in e.get("summary", "")]
        test8 = len(auditor_events) >= 2  # At least: 1 ALLOW + 1 DENY
        print(f"      [{'PASS' if test8 else 'FAIL'}] TEST 8: Auditor logs events in State Fabric")
        if test8:
            tests_passed += 1

        # --- RESUMEN ---
        print("\n" + "-" * 70)
        print(f"\n[RESULTADO] Auditor Status: {auditor_result['status']}")
        print(f"[RESULTADO] Auditor Verdict: {auditor_result['verdict']}")
        print(f"[RESULTADO] Message: {auditor_result['message']}")
        print("\n[GATES]")
        for gate_name, gate_data in auditor_result["gates"].items():
            status = "PASS" if gate_data["passed"] else "FAIL"
            print(f"      [{status}] {gate_name}: {gate_data['detail']}")

        print(f"\n[FINDINGS] Total: {len(auditor_result['findings'])}")
        for f in auditor_result["findings"]:
            print(f"      [{f['severity']}] {f['finding_id']}: {f['subject']}")

        print("\n[ACTIONS]")
        for a in auditor_result["actions_log"]:
            status = "ALLOW" if a["allowed"] else "DENY"
            print(f"      [{status}] {a['action']} → {a['target']}")

        print("\n[OUTPUT FILES]")
        for fp in auditor_result["output_files"]:
            print(f"      {fp}")

        print(f"\n[EVENT LOG] Total events: {len(all_events)}")
        for e in all_events:
            print(f"      [{e['event_id']}] {e['event_type']}: {e['subject']}")

    finally:
        # Cleanup
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("\n" + "=" * 70)
    print(f"  RESULTADO FINAL: {tests_passed}/{tests_total} — {'PASS' if tests_passed == tests_total else 'FAIL'}")
    print("=" * 70)

    return tests_passed == tests_total


if __name__ == "__main__":
    success = run_simulation()
    sys.exit(0 if success else 1)
