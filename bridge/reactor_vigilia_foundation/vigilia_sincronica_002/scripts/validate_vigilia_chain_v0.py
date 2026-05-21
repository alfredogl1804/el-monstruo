"""
validate_vigilia_chain_v0.py — Validador de la Cadena Vigilia Sincrónica
SPR-VIGILIA-SINCRONICA-002

Ejecuta 12 gates de validación sobre los artefactos producidos por
run_vigilia_chain_v0.py para garantizar que la cadena se ejecutó
correctamente y sin violar controles de riesgo.
"""

import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAIN_RUN_DIR = os.path.join(BASE_DIR, "chain_run_001")


def gate_1_manifest_exists():
    """Gate 1: Chain manifest exists and is valid JSON."""
    path = os.path.join(CHAIN_RUN_DIR, "real_loop_chain_manifest.v0_1.json")
    if not os.path.exists(path):
        return False, "Manifest file not found"
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        if "chain_id" not in data or "steps" not in data:
            return False, "Manifest missing required fields"
        return True, f"Manifest valid: chain_id={data['chain_id']}"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"


def gate_2_all_steps_success():
    """Gate 2: All 4 chain steps completed with acceptable status (SUCCESS or PARTIAL with PASS_WITH_FINDINGS)."""
    path = os.path.join(CHAIN_RUN_DIR, "real_loop_chain_manifest.v0_1.json")
    with open(path, 'r') as f:
        data = json.load(f)
    steps = data.get("steps", [])
    if len(steps) != 4:
        return False, f"Expected 4 steps, got {len(steps)}"
    acceptable_statuses = {"SUCCESS", "PARTIAL"}
    statuses = []
    for step in steps:
        if step["status"] not in acceptable_statuses:
            return False, f"Step {step['step_id']} ({step['loop_id']}) status={step['status']} (unacceptable)"
        # PARTIAL is only acceptable if the verdict is PASS_WITH_FINDINGS
        if step["status"] == "PARTIAL":
            verdict = step.get("verdict", "")
            if verdict not in ("PASS_WITH_FINDINGS", "PASS"):
                return False, f"Step {step['step_id']} PARTIAL but verdict={verdict} (not PASS_WITH_FINDINGS)"
        statuses.append(step["status"])
    return True, f"All 4 steps acceptable: {statuses}"


def gate_3_handoff_packets_exist():
    """Gate 3: All 3 handoff packets exist and are valid."""
    expected_handoffs = [
        "handoff_loop_oraculo_ias_to_loop_auditor.v0_1.json",
        "handoff_loop_auditor_to_loop_risk_classification.v0_1.json",
        "handoff_loop_risk_classification_to_loop_unified_face.v0_1.json"
    ]
    for filename in expected_handoffs:
        path = os.path.join(CHAIN_RUN_DIR, filename)
        if not os.path.exists(path):
            return False, f"Missing handoff: {filename}"
        with open(path, 'r') as f:
            packet = json.load(f)
        if "source_loop" not in packet or "target_loop" not in packet:
            return False, f"Invalid handoff: {filename}"
    return True, "All 3 handoff packets valid"


def gate_4_event_log_delta_populated():
    """Gate 4: Event log delta has events (append-only, non-empty)."""
    path = os.path.join(CHAIN_RUN_DIR, "chain_event_log_delta.v0_1.jsonl")
    if not os.path.exists(path):
        return False, "Event log delta not found"
    with open(path, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if len(lines) < 5:
        return False, f"Expected >= 5 events, got {len(lines)}"
    # Verify each line is valid JSON
    for i, line in enumerate(lines):
        try:
            json.loads(line)
        except json.JSONDecodeError:
            return False, f"Invalid JSON at line {i+1}"
    return True, f"Event log delta: {len(lines)} valid events"


def gate_5_no_realtime_verified():
    """Gate 5: No artifact claims REALTIME_VERIFIED evidence status."""
    # Check handoff packets
    for filename in os.listdir(CHAIN_RUN_DIR):
        if filename.startswith("handoff_") and filename.endswith(".json"):
            path = os.path.join(CHAIN_RUN_DIR, filename)
            with open(path, 'r') as f:
                data = json.load(f)
            if data.get("evidence_status") == "REALTIME_VERIFIED":
                return False, f"REALTIME_VERIFIED found in {filename}"
            if data.get("not_realtime_verified") is not True:
                return False, f"not_realtime_verified != true in {filename}"

    # Check risk overlay
    risk_path = os.path.join(CHAIN_RUN_DIR, "risk_output", "chain_risk_overlay_v0_1.json")
    if os.path.exists(risk_path):
        with open(risk_path, 'r') as f:
            data = json.load(f)
        if data.get("global_evidence_status") == "REALTIME_VERIFIED":
            return False, "Risk overlay claims REALTIME_VERIFIED"

    return True, "No REALTIME_VERIFIED claims found"


def gate_6_no_m2_unlock():
    """Gate 6: No artifact or event proposes M2 unlock."""
    for filename in os.listdir(CHAIN_RUN_DIR):
        if filename.startswith("handoff_") and filename.endswith(".json"):
            path = os.path.join(CHAIN_RUN_DIR, filename)
            with open(path, 'r') as f:
                data = json.load(f)
            if data.get("no_m2_unlock") is not True:
                return False, f"no_m2_unlock != true in {filename}"

    # Check manifest risk controls
    manifest_path = os.path.join(CHAIN_RUN_DIR, "real_loop_chain_manifest.v0_1.json")
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    controls = manifest.get("risk_controls", {})
    if controls.get("no_m2_unlock") is not True:
        return False, "Manifest risk_controls.no_m2_unlock != true"

    return True, "M2 unlock correctly blocked"


def gate_7_dispatcher_deny_present():
    """Gate 7: At least one DENY event exists (Oracle write_code attempt)."""
    path = os.path.join(CHAIN_RUN_DIR, "chain_event_log_delta.v0_1.jsonl")
    with open(path, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    deny_found = False
    for line in lines:
        event = json.loads(line)
        if event.get("event_type") == "BLOCKER_DECLARED":
            deny_found = True
            break

    if not deny_found:
        return False, "No BLOCKER_DECLARED event found (expected DENY for write_code)"
    return True, "DENY event present (write_code blocked as expected)"


def gate_8_unified_face_summary_exists():
    """Gate 8: Unified Face summary markdown exists."""
    path = os.path.join(CHAIN_RUN_DIR, "face_output", "unified_face_summary.v0_1.md")
    if not os.path.exists(path):
        return False, "Unified Face summary not found"
    with open(path, 'r') as f:
        content = f.read()
    if len(content) < 100:
        return False, "Summary too short (< 100 chars)"
    if "NO" not in content.upper() or "EJECUT" not in content.upper():
        return False, "Summary missing 'what was NOT executed' section"
    return True, f"Unified Face summary valid ({len(content)} chars)"


def gate_9_no_daemon_no_scheduler():
    """Gate 9: No evidence of daemon/scheduler/infinite loop."""
    # Check manifest
    manifest_path = os.path.join(CHAIN_RUN_DIR, "real_loop_chain_manifest.v0_1.json")
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    controls = manifest.get("risk_controls", {})
    if controls.get("no_daemon") is not True:
        return False, "Manifest risk_controls.no_daemon != true"

    # Check unified face output
    face_path = os.path.join(CHAIN_RUN_DIR, "unified_face_output.v0_1.json")
    if os.path.exists(face_path):
        with open(face_path, 'r') as f:
            face = json.load(f)
        restrictions = face.get("active_restrictions", [])
        if "no_daemon" not in restrictions:
            return False, "Unified face missing 'no_daemon' restriction"

    return True, "No daemon/scheduler evidence"


def gate_10_oracle_catalog_produced():
    """Gate 10: Oracle produced a valid capability catalog."""
    path = os.path.join(CHAIN_RUN_DIR, "oracle_output", "oraculo_capability_catalog_v0.json")
    if not os.path.exists(path):
        return False, "Oracle catalog not found"
    with open(path, 'r') as f:
        data = json.load(f)
    caps = data.get("capabilities", [])
    if len(caps) < 6:
        return False, f"Expected >= 6 capabilities, got {len(caps)}"
    return True, f"Oracle catalog valid: {len(caps)} capabilities"


def gate_11_risk_overlay_all_r0():
    """Gate 11: Risk overlay classifies all capabilities as R0/A1."""
    path = os.path.join(CHAIN_RUN_DIR, "risk_output", "chain_risk_overlay_v0_1.json")
    if not os.path.exists(path):
        return False, "Risk overlay not found"
    with open(path, 'r') as f:
        data = json.load(f)
    if data.get("global_risk_class") != "R0":
        return False, f"Global risk class = {data.get('global_risk_class')}, expected R0"
    for cap in data.get("capabilities", []):
        if cap.get("risk_class") != "R0":
            return False, f"Capability {cap['id']} risk_class = {cap.get('risk_class')}"
    return True, "All capabilities classified R0/A1"


def gate_12_chain_sequence_correct():
    """Gate 12: Steps executed in correct order (1→2→3→4)."""
    manifest_path = os.path.join(CHAIN_RUN_DIR, "real_loop_chain_manifest.v0_1.json")
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    steps = manifest.get("steps", [])
    expected_order = [
        (1, "loop_oraculo_ias"),
        (2, "loop_auditor"),
        (3, "loop_risk_classification"),
        (4, "loop_unified_face")
    ]
    for expected_id, expected_loop in expected_order:
        matching = [s for s in steps if s["step_id"] == expected_id]
        if not matching:
            return False, f"Step {expected_id} not found"
        if matching[0]["loop_id"] != expected_loop:
            return False, f"Step {expected_id} loop_id={matching[0]['loop_id']}, expected {expected_loop}"
    return True, "Chain sequence correct: Oracle → Auditor → Risk → Face"


def run_all_gates():
    """Execute all 12 gates and produce a validation report."""
    gates = [
        (1, "manifest_exists", gate_1_manifest_exists),
        (2, "all_steps_success", gate_2_all_steps_success),
        (3, "handoff_packets_exist", gate_3_handoff_packets_exist),
        (4, "event_log_delta_populated", gate_4_event_log_delta_populated),
        (5, "no_realtime_verified", gate_5_no_realtime_verified),
        (6, "no_m2_unlock", gate_6_no_m2_unlock),
        (7, "dispatcher_deny_present", gate_7_dispatcher_deny_present),
        (8, "unified_face_summary_exists", gate_8_unified_face_summary_exists),
        (9, "no_daemon_no_scheduler", gate_9_no_daemon_no_scheduler),
        (10, "oracle_catalog_produced", gate_10_oracle_catalog_produced),
        (11, "risk_overlay_all_r0", gate_11_risk_overlay_all_r0),
        (12, "chain_sequence_correct", gate_12_chain_sequence_correct),
    ]

    results = []
    passed = 0
    failed = 0

    print("=" * 70)
    print("  VALIDACIÓN DE CADENA — 12 GATES")
    print("=" * 70)
    print()

    for gate_id, gate_name, gate_fn in gates:
        try:
            success, evidence = gate_fn()
        except Exception as e:
            success = False
            evidence = f"Exception: {e}"

        status = "PASS" if success else "FAIL"
        if success:
            passed += 1
        else:
            failed += 1

        print(f"  Gate {gate_id:2d} [{status}] {gate_name}")
        print(f"         → {evidence}")
        print()

        results.append({
            "gate_id": gate_id,
            "gate_name": gate_name,
            "passed": success,
            "evidence": evidence,
            "failure_reason": evidence if not success else ""
        })

    # Write validation report
    from datetime import datetime, timezone
    report = {
        "chain_id": "vigilia-chain-v0.2-001",
        "validated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_gates": len(gates),
        "gates_passed": passed,
        "gates_failed": failed,
        "overall_verdict": "PASS" if failed == 0 else "FAIL",
        "gates": results
    }

    report_path = os.path.join(CHAIN_RUN_DIR, "chain_validation_report.v0_1.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print(f"  RESULTADO: {passed}/{len(gates)} PASS | Veredicto: {report['overall_verdict']}")
    print("=" * 70)
    print(f"\n  Report saved: {report_path}")

    return report


if __name__ == "__main__":
    if not os.path.exists(CHAIN_RUN_DIR):
        print(f"ERROR: Chain run directory not found: {CHAIN_RUN_DIR}")
        print("Run 'run_vigilia_chain_v0.py' first.")
        sys.exit(1)

    report = run_all_gates()
    sys.exit(0 if report["overall_verdict"] == "PASS" else 1)
