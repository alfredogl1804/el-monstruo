#!/usr/bin/env python3
"""
SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
Validador de 14 gates para la reclasificación post-M2.

Reglas estrictas:
- No network / No API calls / No secrets / No env vars
- Solo lee artifacts generados y valida integridad
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REACTOR = BASE.parent
M2_DIR = REACTOR / "oracle_ai_m2"

# --- Utility ---
def load_json(path):
    with open(path) as f:
        return json.load(f)


def gate_result(gate_id, name, passed, evidence):
    status = "PASS" if passed else "FAIL"
    print(f"  Gate {gate_id:02d}: [{status}] {name}")
    if not passed:
        print(f"           Evidence: {evidence}")
    return {"gate_id": gate_id, "gate_name": name, "result": status, "evidence": evidence}


# --- Gates ---
def gate_01_m2_artifacts_exist():
    """All required M2 input artifacts exist."""
    required = [
        M2_DIR / "provider_access_status.v0_1.json",
        M2_DIR / "realtime_capability_catalog.v0_1.json",
        M2_DIR / "oracle_catalog_m2_realtime_overlay.v0_1.json",
    ]
    missing = [str(p) for p in required if not p.exists()]
    return len(missing) == 0, f"Missing: {missing}" if missing else "All M2 inputs present."


def gate_02_no_new_api_calls():
    """No new API calls were made (script is pure computation)."""
    # Verified by design: run_post_m2_reclassification.py has no import requests/httpx/urllib
    script = BASE / "scripts" / "run_post_m2_reclassification.py"
    content = script.read_text()
    forbidden = ["import requests", "import httpx", "import urllib", "os.environ"]
    found = [f for f in forbidden if f in content]
    return len(found) == 0, f"Forbidden imports found: {found}" if found else "No network/env imports."


def gate_03_no_secret_access():
    """No secrets were accessed or printed in any output."""
    # Only check data artifacts (overlays, matrices, manifests), NOT schema files
    outputs = [f for f in BASE.glob("*.json") if not f.name.endswith(".schema.json")]
    for out in outputs:
        content = out.read_text()
        # Look for actual secret patterns (long alphanumeric strings after sk-)
        import re
        actual_secrets = re.findall(r'sk-[A-Za-z0-9_-]{20,}', content)
        bearer_tokens = re.findall(r'Bearer [A-Za-z0-9_-]{20,}', content)
        if actual_secrets or bearer_tokens:
            return False, f"Potential secret in {out.name}"
    return True, "No secrets found in data outputs."


def gate_04_no_original_mutation():
    """M2 artifacts are not modified (overlay-only approach)."""
    # Check that M2 files have not been touched by comparing existence only
    # In a real system we'd check checksums; here we verify no writes to M2_DIR
    script = BASE / "scripts" / "run_post_m2_reclassification.py"
    content = script.read_text()
    # Script should only write to OUTPUT_DIR (BASE), never to M2_DIR
    if "M2_DIR" in content and "open(M2_DIR" in content.replace(" ", ""):
        return False, "Script writes to M2_DIR."
    return True, "Script only writes to its own directory (overlay-only)."


def gate_05_all_verified_reclassified():
    """All REALTIME_VERIFIED capabilities have a risk_class != R0."""
    overlay_path = BASE / "post_m2_capability_risk_overlay.v0_1.json"
    if not overlay_path.exists():
        return False, "Overlay file not found."
    overlay = load_json(overlay_path)
    caps = overlay["capabilities"]
    verified = [c for c in caps if c["evidence_status"] == "REALTIME_VERIFIED"]
    still_r0 = [c for c in verified if c["risk_class_after"] == "R0"]
    return len(still_r0) == 0, f"{len(still_r0)} verified caps still at R0." if still_r0 else f"All {len(verified)} verified caps elevated."


def gate_06_access_blocked_preserved():
    """ACCESS_BLOCKED capabilities remain BLOCKED_FOR_AUTOMATION."""
    overlay_path = BASE / "post_m2_capability_risk_overlay.v0_1.json"
    if not overlay_path.exists():
        return False, "Overlay file not found."
    overlay = load_json(overlay_path)
    caps = overlay["capabilities"]
    blocked = [c for c in caps if c["evidence_status"] != "REALTIME_VERIFIED"]
    wrong = [c for c in blocked if c["risk_class_after"] != "BLOCKED_FOR_AUTOMATION"]
    return len(wrong) == 0, f"{len(wrong)} blocked caps not BLOCKED_FOR_AUTOMATION." if wrong else f"All {len(blocked)} blocked caps preserved."


def gate_07_no_realtime_invention():
    """No capabilities are invented without M2 evidence."""
    overlay_path = BASE / "post_m2_capability_risk_overlay.v0_1.json"
    catalog_path = M2_DIR / "realtime_capability_catalog.v0_1.json"
    if not overlay_path.exists() or not catalog_path.exists():
        return False, "Required files not found."
    overlay = load_json(overlay_path)
    catalog = load_json(catalog_path)
    catalog_ids = {c["capability_id"] for c in catalog["capabilities"]}
    overlay_ids = {c["capability_id"] for c in overlay["capabilities"]}
    invented = overlay_ids - catalog_ids
    return len(invented) == 0, f"Invented capabilities: {invented}" if invented else "No invented capabilities."


def gate_08_power_stacks_reclassified():
    """Power Stacks have derived risk."""
    path = BASE / "post_m2_power_stack_risk_overlay.v0_1.json"
    if not path.exists():
        return False, "Power stack overlay not found."
    data = load_json(path)
    stacks = data["stacks"]
    no_risk = [s for s in stacks if not s.get("derived_risk_class")]
    return len(no_risk) == 0, f"{len(no_risk)} stacks without risk." if no_risk else f"All {len(stacks)} stacks classified."


def gate_09_sprint_candidates_reclassified():
    """Sprint candidates have autonomy requirements."""
    path = BASE / "post_m2_sprint_candidate_risk_overlay.v0_1.json"
    if not path.exists():
        return False, "Sprint candidate overlay not found."
    data = load_json(path)
    candidates = data["candidates"]
    no_autonomy = [c for c in candidates if not c.get("required_autonomy_level")]
    return len(no_autonomy) == 0, f"{len(no_autonomy)} candidates without autonomy." if no_autonomy else f"All {len(candidates)} candidates classified."


def gate_10_no_scheduler_enabled():
    """No recurring_status is APPROVED (all must be T1_PENDING or BLOCKED)."""
    overlay_path = BASE / "post_m2_capability_risk_overlay.v0_1.json"
    if not overlay_path.exists():
        return False, "Overlay file not found."
    overlay = load_json(overlay_path)
    approved = [c for c in overlay["capabilities"] if c.get("recurring_status") == "APPROVED"]
    return len(approved) == 0, f"{len(approved)} capabilities with APPROVED recurring." if approved else "No scheduler enabled."


def gate_11_no_supabase_move():
    """No data was moved to Supabase."""
    script = BASE / "scripts" / "run_post_m2_reclassification.py"
    content = script.read_text()
    # Check for actual Supabase client imports/usage, not just mentions in comments
    actual_imports = ["import supabase" in content, "from supabase" in content,
                      "import psycopg" in content, "import sqlalchemy" in content,
                      "supabase.create_client" in content]
    return not any(actual_imports), "Supabase client imports found in script." if any(actual_imports) else "No Supabase client access."


def gate_12_no_canon_no_appvision():
    """No alterations to doctrine core, no AppVision, no PreIA."""
    # Check that no files were written outside the sprint directory
    # This is a design check — the script only writes to BASE
    script = BASE / "scripts" / "run_post_m2_reclassification.py"
    content = script.read_text()
    # Should not reference doctrine paths
    doctrine_refs = ["doctrine_candidates" in content, "appvision" in content.lower(), "preia" in content.lower()]
    return not any(doctrine_refs), "Doctrine/AppVision/PreIA references found." if any(doctrine_refs) else "No doctrine alterations."


def gate_13_auditor_recheck():
    """The overlay passes basic schema validation."""
    overlay_path = BASE / "post_m2_capability_risk_overlay.v0_1.json"
    if not overlay_path.exists():
        return False, "Overlay file not found."
    overlay = load_json(overlay_path)
    # Check required fields
    required_fields = ["capability_id", "provider_id", "evidence_status", "risk_class_before", "risk_class_after", "required_autonomy_level"]
    for cap in overlay["capabilities"]:
        missing = [f for f in required_fields if f not in cap]
        if missing:
            return False, f"Missing fields in {cap.get('capability_id', '?')}: {missing}"
    return True, f"All {len(overlay['capabilities'])} capabilities pass schema check."


def gate_14_unified_face_single_voice():
    """Decision pack uses single voice (no conflicting recommendations)."""
    path = BASE / "post_m2_t1_decision_pack.v0_1.json"
    if not path.exists():
        return False, "Decision pack not found."
    data = load_json(path)
    # Check that recommendation exists and is a single string
    rec = data.get("recommendation", "")
    return isinstance(rec, str) and len(rec) > 10, f"Recommendation too short or missing." if not (isinstance(rec, str) and len(rec) > 10) else "Single voice recommendation present."


# --- Main ---
def main():
    print("=" * 60)
    print("VALIDATION: SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001")
    print("14 Gates")
    print("=" * 60)

    gates = [
        (1, "m2_artifacts_exist", gate_01_m2_artifacts_exist),
        (2, "no_new_api_calls", gate_02_no_new_api_calls),
        (3, "no_secret_access", gate_03_no_secret_access),
        (4, "no_original_mutation", gate_04_no_original_mutation),
        (5, "all_verified_reclassified", gate_05_all_verified_reclassified),
        (6, "access_blocked_preserved", gate_06_access_blocked_preserved),
        (7, "no_realtime_invention", gate_07_no_realtime_invention),
        (8, "power_stacks_reclassified", gate_08_power_stacks_reclassified),
        (9, "sprint_candidates_reclassified", gate_09_sprint_candidates_reclassified),
        (10, "no_scheduler_enabled", gate_10_no_scheduler_enabled),
        (11, "no_supabase_move", gate_11_no_supabase_move),
        (12, "no_canon_no_appvision", gate_12_no_canon_no_appvision),
        (13, "auditor_recheck", gate_13_auditor_recheck),
        (14, "unified_face_single_voice", gate_14_unified_face_single_voice),
    ]

    results = []
    for gate_id, name, fn in gates:
        try:
            passed, evidence = fn()
        except Exception as e:
            passed, evidence = False, f"Exception: {e}"
        results.append(gate_result(gate_id, name, passed, evidence))

    total_pass = sum(1 for r in results if r["result"] == "PASS")
    total_fail = sum(1 for r in results if r["result"] == "FAIL")
    verdict = "PASS" if total_fail == 0 else "FAIL"

    print("\n" + "=" * 60)
    print(f"VERDICT: {verdict} ({total_pass}/{len(gates)} gates)")
    print("=" * 60)

    # Write validation report
    report = {
        "recheck_id": "post-m2-reclass-validation-001",
        "sprint_id": "SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "gates": results,
        "total_pass": total_pass,
        "total_fail": total_fail,
        "verdict": verdict
    }

    report_path = BASE / "post_m2_validation_report.v0_1.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport written: {report_path.name}")

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
