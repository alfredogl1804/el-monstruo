"""
Simulación End-to-End — Risk Classification Process
SPR-RISK-CLASSIFICATION-001

Valida que:
1. El overlay de clasificación de riesgo es consistente con el catálogo base.
2. Todas las capabilities tienen risk_class y required_autonomy_level.
3. Todos los power stacks tienen derivación correcta.
4. Todos los sprint candidates tienen autonomía derivada.
5. La regla de evidence_status=STATIC_CATALOG -> R0 se cumple.
6. No hay claims de REALTIME_VERIFIED sin API real.
7. El auditor recheck gate log pasa 10/10 gates.
8. El finding FND-031 está marcado como RESOLVED.
9. No hay autonomy creep (ningún item permite auto-ejecución).
10. Los schemas JSON son válidos.

10 tests = 10 gates.
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_json(filename):
    """Carga un archivo JSON del directorio del sprint."""
    path = os.path.join(BASE_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_json_schema(data, schema):
    """Validación simplificada de schema (sin jsonschema library)."""
    required = schema.get("required", [])
    for field in required:
        if field not in data:
            return False, f"Missing required field: {field}"
    return True, "OK"


def main():
    print("=" * 70)
    print("SIMULACIÓN E2E — SPR-RISK-CLASSIFICATION-001")
    print("Risk Classification Process Validation")
    print("=" * 70)
    print()

    tests_passed = 0
    tests_total = 10
    results = []

    # === Load artifacts ===
    try:
        cap_overlay = load_json("capability_risk_overlay.v0_1.json")
        ps_overlay = load_json("power_stack_risk_overlay.v0_1.json")
        sc_overlay = load_json("sprint_candidate_risk_overlay.v0_1.json")
        annotated = load_json("oracle_catalog_risk_annotated.v0_1.json")
        recheck = load_json("auditor_recheck_gate_log.json")
        cap_schema = load_json("capability_risk.schema.json")
        ps_schema = load_json("power_stack_risk.schema.json")
        sc_schema = load_json("sprint_candidate_risk.schema.json")
        overlay_schema = load_json("risk_classification_overlay.schema.json")
    except Exception as e:
        print(f"FATAL: Cannot load artifacts: {e}")
        sys.exit(1)

    # === TEST 1: All capabilities have risk_class and required_autonomy_level ===
    print("TEST 01: All capabilities have risk_class + required_autonomy_level")
    all_have_risk = all(
        "risk_class" in cap and "required_autonomy_level" in cap
        for cap in cap_overlay["capabilities"]
    )
    count = len(cap_overlay["capabilities"])
    if all_have_risk and count == 6:
        print(f"  PASS — {count}/6 capabilities classified")
        tests_passed += 1
        results.append(("TEST_01", "PASS", f"{count}/6 capabilities classified"))
    else:
        print(f"  FAIL — Missing risk_class in some capabilities")
        results.append(("TEST_01", "FAIL", "Missing fields"))

    # === TEST 2: All power stacks have derived_risk_class ===
    print("TEST 02: All power stacks have derived_risk_class")
    all_ps_risk = all(
        "derived_risk_class" in ps and "required_autonomy_level" in ps
        for ps in ps_overlay["power_stacks"]
    )
    ps_count = len(ps_overlay["power_stacks"])
    if all_ps_risk and ps_count == 6:
        print(f"  PASS — {ps_count}/6 power stacks classified")
        tests_passed += 1
        results.append(("TEST_02", "PASS", f"{ps_count}/6 power stacks classified"))
    else:
        print(f"  FAIL — Missing derived_risk_class in some power stacks")
        results.append(("TEST_02", "FAIL", "Missing fields"))

    # === TEST 3: All sprint candidates have required_autonomy_level ===
    print("TEST 03: All sprint candidates have required_autonomy_level")
    all_sc_risk = all(
        "derived_risk_class" in sc and "required_autonomy_level" in sc
        for sc in sc_overlay["sprint_candidates"]
    )
    sc_count = len(sc_overlay["sprint_candidates"])
    if all_sc_risk and sc_count == 6:
        print(f"  PASS — {sc_count}/6 sprint candidates classified")
        tests_passed += 1
        results.append(("TEST_03", "PASS", f"{sc_count}/6 sprint candidates classified"))
    else:
        print(f"  FAIL — Missing fields in sprint candidates")
        results.append(("TEST_03", "FAIL", "Missing fields"))

    # === TEST 4: STATIC_CATALOG -> R0 rule enforced ===
    print("TEST 04: STATIC_CATALOG evidence -> R0 risk_class enforced")
    all_static_r0 = all(
        cap["evidence_status"] == "STATIC_CATALOG" and cap["risk_class"] == "R0"
        for cap in cap_overlay["capabilities"]
    )
    if all_static_r0:
        print(f"  PASS — All STATIC_CATALOG capabilities are R0")
        tests_passed += 1
        results.append(("TEST_04", "PASS", "All STATIC_CATALOG -> R0"))
    else:
        print(f"  FAIL — Some STATIC_CATALOG capabilities are not R0")
        results.append(("TEST_04", "FAIL", "Rule violation"))

    # === TEST 5: No false REALTIME_VERIFIED claims ===
    print("TEST 05: No false REALTIME_VERIFIED claims")
    any_realtime = any(
        cap["evidence_status"] == "REALTIME_VERIFIED"
        for cap in cap_overlay["capabilities"]
    )
    if not any_realtime:
        print(f"  PASS — No REALTIME_VERIFIED claims (correct for v0)")
        tests_passed += 1
        results.append(("TEST_05", "PASS", "No false REALTIME claims"))
    else:
        print(f"  FAIL — Found REALTIME_VERIFIED without API connection")
        results.append(("TEST_05", "FAIL", "False REALTIME claim"))

    # === TEST 6: Auditor recheck gate log passes 10/10 ===
    print("TEST 06: Auditor recheck gate log = 10/10 PASS")
    gates = recheck["gates_rechecked"]
    gates_passed = sum(1 for g in gates if g["recheck_result"] == "PASS")
    if gates_passed == 10 and len(gates) == 10:
        print(f"  PASS — {gates_passed}/10 gates PASS")
        tests_passed += 1
        results.append(("TEST_06", "PASS", f"{gates_passed}/10 gates"))
    else:
        print(f"  FAIL — {gates_passed}/{len(gates)} gates PASS")
        results.append(("TEST_06", "FAIL", f"{gates_passed}/{len(gates)}"))

    # === TEST 7: FND-031 is RESOLVED ===
    print("TEST 07: Finding FND-031 status = RESOLVED")
    fnd_status = recheck["finding_status_update"]["new_status"]
    if fnd_status == "RESOLVED":
        print(f"  PASS — FND-031 is RESOLVED")
        tests_passed += 1
        results.append(("TEST_07", "PASS", "FND-031 RESOLVED"))
    else:
        print(f"  FAIL — FND-031 status is {fnd_status}")
        results.append(("TEST_07", "FAIL", f"Status: {fnd_status}"))

    # === TEST 8: No autonomy creep (no self-execution allowed) ===
    print("TEST 08: No autonomy creep — all allowed_next_action blocks execution")
    allowed_actions = set()
    for cap in cap_overlay["capabilities"]:
        allowed_actions.add(cap["allowed_next_action"])
    for sc in sc_overlay["sprint_candidates"]:
        allowed_actions.add(sc["allowed_next_action"])
    
    forbidden_self_execute = {"EXECUTE", "AUTO_RUN", "DEPLOY"}
    creep_detected = allowed_actions & forbidden_self_execute
    if not creep_detected:
        print(f"  PASS — allowed_next_actions: {allowed_actions} (no self-execute)")
        tests_passed += 1
        results.append(("TEST_08", "PASS", f"Actions: {allowed_actions}"))
    else:
        print(f"  FAIL — Autonomy creep detected: {creep_detected}")
        results.append(("TEST_08", "FAIL", f"Creep: {creep_detected}"))

    # === TEST 9: Annotated catalog is consistent with overlays ===
    print("TEST 09: Annotated catalog consistent with overlays")
    annotated_caps = {c["id"]: c for c in annotated["capabilities"]}
    overlay_caps = {c["capability_id"]: c for c in cap_overlay["capabilities"]}
    
    consistent = True
    for cap_id, ann in annotated_caps.items():
        ov = overlay_caps.get(cap_id)
        if not ov:
            consistent = False
            break
        if ann["risk_class"] != ov["risk_class"]:
            consistent = False
            break
        if ann["required_autonomy_level"] != ov["required_autonomy_level"]:
            consistent = False
            break
    
    if consistent and len(annotated_caps) == 6:
        print(f"  PASS — Annotated catalog matches overlay (6/6)")
        tests_passed += 1
        results.append(("TEST_09", "PASS", "Consistent 6/6"))
    else:
        print(f"  FAIL — Inconsistency between annotated catalog and overlay")
        results.append(("TEST_09", "FAIL", "Inconsistent"))

    # === TEST 10: Schema validation (simplified) ===
    print("TEST 10: Schema validation — all overlays have required fields")
    schema_valid = True
    errors = []
    
    # Check capability overlay has required top-level fields
    for field in ["overlay_version", "base_catalog_version", "generated_by", "generated_at", "capabilities"]:
        if field not in cap_overlay:
            schema_valid = False
            errors.append(f"cap_overlay missing {field}")
    
    # Check each capability has required fields from schema
    cap_required = cap_schema.get("required", [])
    for cap in cap_overlay["capabilities"]:
        for field in cap_required:
            if field not in cap:
                schema_valid = False
                errors.append(f"Capability {cap.get('capability_id', '?')} missing {field}")
    
    # Check power stack overlay
    ps_required = ps_schema.get("required", [])
    for ps in ps_overlay["power_stacks"]:
        for field in ps_required:
            if field not in ps:
                schema_valid = False
                errors.append(f"PS {ps.get('power_stack_id', '?')} missing {field}")
    
    # Check sprint candidate overlay
    sc_required = sc_schema.get("required", [])
    for sc in sc_overlay["sprint_candidates"]:
        for field in sc_required:
            if field not in sc:
                schema_valid = False
                errors.append(f"SC {sc.get('sprint_candidate_id', '?')} missing {field}")
    
    if schema_valid:
        print(f"  PASS — All schemas valid")
        tests_passed += 1
        results.append(("TEST_10", "PASS", "All schemas valid"))
    else:
        print(f"  FAIL — Schema errors: {errors[:3]}")
        results.append(("TEST_10", "FAIL", f"Errors: {errors[:3]}"))

    # === SUMMARY ===
    print()
    print("=" * 70)
    print(f"RESULTADO: {tests_passed}/{tests_total} PASS")
    
    if tests_passed == tests_total:
        verdict = "PASS"
    elif tests_passed >= 8:
        verdict = "PASS_WITH_FINDINGS"
    else:
        verdict = "FAIL"
    
    print(f"VERDICT: {verdict}")
    print("=" * 70)

    # === Save manifest ===
    manifest = {
        "simulation": "SPR-RISK-CLASSIFICATION-001 E2E",
        "tests_passed": tests_passed,
        "tests_total": tests_total,
        "verdict": verdict,
        "results": [{"test": r[0], "result": r[1], "detail": r[2]} for r in results],
        "artifacts_validated": [
            "capability_risk_overlay.v0_1.json",
            "power_stack_risk_overlay.v0_1.json",
            "sprint_candidate_risk_overlay.v0_1.json",
            "oracle_catalog_risk_annotated.v0_1.json",
            "auditor_recheck_gate_log.json"
        ]
    }
    
    manifest_path = os.path.join(BASE_DIR, "e2e_simulation_manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\nManifest guardado en: {manifest_path}")
    
    return tests_passed == tests_total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
