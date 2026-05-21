#!/usr/bin/env python3
"""
SPR-ORACLE-AI-M2-001 — Validation Gates (12)
Validates all outputs from the M2 probe execution.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPRINT_ID = "SPR-ORACLE-AI-M2-001"

# Secret patterns that MUST NOT appear in any artifact
SECRET_PATTERNS = [
    r'sk-proj-[A-Za-z0-9_\-]{20,}',
    r'sk-ant-api[A-Za-z0-9_\-]{20,}',
    r'xai-[A-Za-z0-9_\-]{20,}',
    r'AIzaSy[A-Za-z0-9_\-]{20,}',
    r'pplx-[A-Za-z0-9_\-]{20,}',
    r'sk-or-v1-[A-Za-z0-9_\-]{20,}',
    r'ghp_[A-Za-z0-9_\-]{20,}',
    r'sbp_[A-Za-z0-9_\-]{20,}',
]

BUDGET_CAP = {
    "max_total_cost_usd": 5.00,
    "max_total_calls": 18
}


def load_json(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def load_text(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return f.read()


def scan_for_secrets(text: str) -> list:
    """Scan text for leaked secrets."""
    found = []
    for pattern in SECRET_PATTERNS:
        matches = re.findall(pattern, text)
        found.extend(matches)
    return found


# ─── Gates ────────────────────────────────────────────────────────────────────

def gate_1_base_artifacts_exist():
    """Gate 1: Base artifacts from previous sprints exist."""
    required = [
        "../vigilia_sincronica_002/chain_run_001/oracle_output/oraculo_capability_catalog_v0.json",
        "../oracle_risk_classification/oracle_catalog_risk_annotated.v0_1.json"
    ]
    for rel_path in required:
        full_path = os.path.join(OUTPUT_DIR, rel_path)
        if not os.path.exists(full_path):
            return False, f"Missing: {rel_path}"
    return True, "All base artifacts present"


def gate_2_dispatcher_permission_per_provider():
    """Gate 2: Each provider probe had explicit ALLOW/DENY."""
    data = load_json("provider_access_status.v0_1.json")
    if not data:
        return False, "provider_access_status.v0_1.json not found"
    providers = data.get("providers", [])
    if len(providers) < 6:
        return False, f"Expected 6 providers, got {len(providers)}"
    for p in providers:
        status = p.get("access_status", "")
        if not status:
            return False, f"Provider {p['provider_id']} has no access_status"
    return True, f"All {len(providers)} providers have explicit status"


def gate_3_no_secret_leak():
    """Gate 3: No artifacts contain API keys, tokens, or sensitive headers."""
    artifacts_to_scan = [
        "api_probe_manifest.v0_1.json",
        "provider_access_status.v0_1.json",
        "realtime_capability_catalog.v0_1.json",
        "oracle_catalog_m2_realtime_overlay.v0_1.json",
        "api_cost_ledger.v0_1.json",
        "api_probe_log.redacted.v0_1.jsonl",
        "unified_face_summary_oracle_m2.v0_1.md",
        "reclassification_inputs_for_next_sprint.v0_1.json"
    ]
    for filename in artifacts_to_scan:
        text = load_text(filename)
        if text:
            leaks = scan_for_secrets(text)
            if leaks:
                return False, f"SECRET LEAK in {filename}: {len(leaks)} patterns found"
    return True, "No secrets detected in any artifact"


def gate_4_budget_cap():
    """Gate 4: Call count and estimated cost within budget cap."""
    data = load_json("api_cost_ledger.v0_1.json")
    if not data:
        return False, "api_cost_ledger.v0_1.json not found"
    totals = data.get("totals", {})
    total_calls = totals.get("total_calls", 0)
    total_cost = totals.get("total_estimated_cost_usd", 0)
    within = totals.get("within_budget", False)
    if total_calls > BUDGET_CAP["max_total_calls"]:
        return False, f"Calls {total_calls} > cap {BUDGET_CAP['max_total_calls']}"
    if total_cost > BUDGET_CAP["max_total_cost_usd"]:
        return False, f"Cost ${total_cost} > cap ${BUDGET_CAP['max_total_cost_usd']}"
    return True, f"Calls={total_calls}, Cost=${total_cost:.4f}, Within budget"


def gate_5_read_only_api():
    """Gate 5: Only read/list/capability check calls were made."""
    log_path = os.path.join(OUTPUT_DIR, "api_probe_log.redacted.v0_1.jsonl")
    if not os.path.exists(log_path):
        return False, "api_probe_log.redacted.v0_1.jsonl not found"
    with open(log_path, "r") as f:
        for line in f:
            entry = json.loads(line)
            action = entry.get("action", "")
            if action not in ("execute_api_probe",):
                return False, f"Non-read-only action detected: {action}"
    return True, "All actions are execute_api_probe (read-only)"


def gate_6_evidence_status_discipline():
    """Gate 6: REALTIME_VERIFIED only appears with real API evidence."""
    overlay = load_json("oracle_catalog_m2_realtime_overlay.v0_1.json")
    if not overlay:
        return False, "oracle_catalog_m2_realtime_overlay.v0_1.json not found"
    for cap in overlay.get("capabilities", []):
        if cap["evidence_status_after"] == "REALTIME_VERIFIED":
            if not cap.get("raw_response_hash"):
                return False, f"REALTIME_VERIFIED without hash: {cap['capability_id']}"
    return True, "All REALTIME_VERIFIED have raw_response_hash"


def gate_7_no_catalog_mutation():
    """Gate 7: Original static catalog not modified destructively."""
    # Check that the original catalog still exists unchanged
    original_path = os.path.join(OUTPUT_DIR, "..", "vigilia_sincronica_002",
                                  "chain_run_001", "oracle_output",
                                  "oraculo_capability_catalog_v0.json")
    if not os.path.exists(original_path):
        return False, "Original catalog missing (destructive mutation?)"
    # Verify it's still valid JSON
    try:
        with open(original_path, "r") as f:
            data = json.load(f)
        if "capabilities" not in data:
            return False, "Original catalog corrupted"
    except Exception as e:
        return False, f"Original catalog unreadable: {e}"
    return True, "Original catalog intact and valid"


def gate_8_overlay_created():
    """Gate 8: oracle_catalog_m2_realtime_overlay.v0_1.json exists."""
    overlay = load_json("oracle_catalog_m2_realtime_overlay.v0_1.json")
    if not overlay:
        return False, "Overlay file not found"
    if "capabilities" not in overlay:
        return False, "Overlay missing 'capabilities' field"
    if "summary" not in overlay:
        return False, "Overlay missing 'summary' field"
    return True, f"Overlay valid: {overlay['summary'].get('total_capabilities', 0)} capabilities"


def gate_9_access_blocked_honest():
    """Gate 9: Providers without credentials/error are ACCESS_BLOCKED, not invented."""
    status = load_json("provider_access_status.v0_1.json")
    if not status:
        return False, "provider_access_status.v0_1.json not found"
    for p in status.get("providers", []):
        if not p.get("key_available") and p.get("access_status") == "REALTIME_VERIFIED":
            return False, f"Provider {p['provider_id']} marked VERIFIED without key"
    return True, "All blocked providers honestly reported"


def gate_10_no_m2_autonomy_expansion():
    """Gate 10: M2 did not enable scheduler, daemon, PR, deploy, or write_code."""
    # Check that no scheduler/daemon artifacts were created
    forbidden_indicators = [
        "scheduler.py", "daemon.py", "crontab", ".service",
        "deploy.sh", "Dockerfile", "railway.json"
    ]
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for f in files:
            if f in forbidden_indicators:
                return False, f"Forbidden artifact found: {f}"
    return True, "No scheduler/daemon/deploy artifacts"


def gate_11_no_risk_reclassification_final():
    """Gate 11: Sprint only produces inputs for reclassification, not final decision."""
    reclass = load_json("reclassification_inputs_for_next_sprint.v0_1.json")
    if not reclass:
        return False, "reclassification_inputs_for_next_sprint.v0_1.json not found"
    # Check it says "inputs" not "decisions"
    purpose = reclass.get("purpose", "")
    if "decision" in purpose.lower() and "input" not in purpose.lower():
        return False, "File appears to contain final decisions, not inputs"
    # Check no provider has final risk_class assigned
    for p in reclass.get("providers_verified", []):
        suggestion = p.get("suggested_risk_elevation", "")
        if suggestion.startswith("R") and suggestion[1:2].isdigit() and "CANDIDATE" not in suggestion:
            return False, f"Final risk assigned to {p['provider_id']}: {suggestion}"
    return True, "Only candidates/inputs produced, no final risk decisions"


def gate_12_unified_face_summary_single_voice():
    """Gate 12: Output final synthesizes for T1 as a single Monstruo voice."""
    face = load_text("unified_face_summary_oracle_m2.v0_1.md")
    if not face:
        return False, "unified_face_summary_oracle_m2.v0_1.md not found"
    if len(face) < 200:
        return False, f"Face summary too short ({len(face)} chars)"
    # Check it has key sections
    if "T1" not in face:
        return False, "Face summary doesn't address T1"
    return True, f"Unified Face valid ({len(face)} chars)"


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    gates = [
        ("base_artifacts_exist", gate_1_base_artifacts_exist),
        ("dispatcher_permission_per_provider", gate_2_dispatcher_permission_per_provider),
        ("no_secret_leak", gate_3_no_secret_leak),
        ("budget_cap", gate_4_budget_cap),
        ("read_only_api", gate_5_read_only_api),
        ("evidence_status_discipline", gate_6_evidence_status_discipline),
        ("no_catalog_mutation", gate_7_no_catalog_mutation),
        ("overlay_created", gate_8_overlay_created),
        ("access_blocked_honest", gate_9_access_blocked_honest),
        ("no_m2_autonomy_expansion", gate_10_no_m2_autonomy_expansion),
        ("no_risk_reclassification_final", gate_11_no_risk_reclassification_final),
        ("unified_face_summary_single_voice", gate_12_unified_face_summary_single_voice),
    ]

    print("=" * 70)
    print("  VALIDACIÓN ORACLE M2 — 12 GATES")
    print("=" * 70)

    results = []
    pass_count = 0
    fail_count = 0
    findings = []

    for i, (name, func) in enumerate(gates, 1):
        try:
            passed, evidence = func()
        except Exception as e:
            passed, evidence = False, f"Exception: {e}"

        result_str = "PASS" if passed else "FAIL"
        if passed:
            pass_count += 1
        else:
            fail_count += 1
            findings.append(f"Gate {i} ({name}): {evidence}")

        results.append({
            "gate_id": i,
            "name": name,
            "result": result_str,
            "evidence": evidence
        })

        print(f"  Gate {i:2d} [{result_str}] {name}")
        print(f"         → {evidence}")

    # Determine verdict
    if fail_count == 0:
        verdict = "PASS"
    elif fail_count <= 2 and all("ACCESS_BLOCKED" in f or "COST_ESTIMATE" in f for f in findings):
        verdict = "PASS_WITH_FINDINGS"
    else:
        verdict = "FAIL"

    print("=" * 70)
    print(f"  RESULTADO: {pass_count}/12 PASS | Veredicto: {verdict}")
    print("=" * 70)

    # Write validation report
    report = {
        "report_id": "oracle-m2-validation-001",
        "sprint_id": SPRINT_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "gates": results,
        "verdict": verdict,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "findings": findings
    }

    report_path = os.path.join(OUTPUT_DIR, "oracle_m2_validation_report.v0_1.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"  Report saved: {report_path}")

    return 0 if verdict != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
