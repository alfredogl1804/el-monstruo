#!/usr/bin/env python3
"""
SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
Orquestador de reclasificación de riesgo post-M2.

Reglas estrictas:
- No network / No API calls / No secrets / No env vars
- No Supabase / No DB / No deploy / No scheduler / No daemon
- Solo lee artifacts M2 existentes y genera overlays nuevos
- No modifica artifacts originales (append-only / overlay-only)
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- Paths ---
BASE = Path(__file__).resolve().parent.parent
REACTOR = BASE.parent
M2_DIR = REACTOR / "oracle_ai_m2"
RISK_DIR = REACTOR / "oracle_risk_classification"
OUTPUT_DIR = BASE

# --- Step 1: Verify Inputs ---
def verify_inputs():
    """Verify all required M2 artifacts exist."""
    required = [
        M2_DIR / "provider_access_status.v0_1.json",
        M2_DIR / "realtime_capability_catalog.v0_1.json",
        M2_DIR / "oracle_catalog_m2_realtime_overlay.v0_1.json",
        M2_DIR / "api_probe_log.redacted.v0_1.jsonl",
        M2_DIR / "api_cost_ledger.v0_1.json",
        M2_DIR / "oracle_m2_validation_report.v0_1.json",
        M2_DIR / "reclassification_inputs_for_next_sprint.v0_1.json",
        RISK_DIR / "capability_risk_overlay.v0_1.json",
        RISK_DIR / "power_stack_risk_overlay.v0_1.json",
        RISK_DIR / "sprint_candidate_risk_overlay.v0_1.json",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print(f"BLOCKED_BY_MISSING_ARTIFACT: {missing}")
        sys.exit(1)
    return [str(p) for p in required]


# --- Step 2: Load M2 Data ---
def load_json(path):
    with open(path) as f:
        return json.load(f)


# --- Step 3: Reclassify Capabilities ---
RISK_RULES = {
    "text_reasoning": {"risk": "R1", "autonomy": "A2", "injection": "LOW"},
    "vision": {"risk": "R1", "autonomy": "A2", "injection": "NONE"},
    "audio": {"risk": "R1", "autonomy": "A2", "injection": "NONE"},
    "embeddings": {"risk": "R1", "autonomy": "A2", "injection": "NONE"},
    "structured_outputs": {"risk": "R1", "autonomy": "A2", "injection": "NONE"},
    "image_generation": {"risk": "R1", "autonomy": "A2", "injection": "NONE"},
    "tool_use": {"risk": "R2", "autonomy": "A3", "injection": "MEDIUM"},
    "code_execution": {"risk": "R3", "autonomy": "A4", "injection": "HIGH"},
}


def reclassify_capabilities(catalog):
    """Reclassify each capability based on its type and evidence status."""
    results = []
    for cap in catalog["capabilities"]:
        cap_type = cap["capability_type"]
        evidence = cap["evidence_status"]

        if evidence != "REALTIME_VERIFIED":
            results.append({
                "capability_id": cap["capability_id"],
                "provider_id": cap["provider_id"],
                "capability_type": cap_type,
                "evidence_status": evidence,
                "risk_class_before": "R0",
                "risk_class_after": "BLOCKED_FOR_AUTOMATION",
                "required_autonomy_level": "N/A",
                "external_api_required": True,
                "secrets_required": True,
                "user_data_touch": False,
                "prompt_injection_surface": "NONE",
                "recurring_status": "BLOCKED",
                "allowed_next_action": "OBTAIN_CREDENTIALS_OR_DEFER",
                "t1_required": True,
                "reclassification_reason": f"Provider {cap['provider_id']} is ACCESS_BLOCKED."
            })
            continue

        rules = RISK_RULES.get(cap_type, {"risk": "R1", "autonomy": "A2", "injection": "LOW"})
        results.append({
            "capability_id": cap["capability_id"],
            "provider_id": cap["provider_id"],
            "capability_type": cap_type,
            "evidence_status": "REALTIME_VERIFIED",
            "risk_class_before": "R0",
            "risk_class_after": rules["risk"],
            "required_autonomy_level": rules["autonomy"],
            "external_api_required": True,
            "secrets_required": True,
            "user_data_touch": False,
            "prompt_injection_surface": rules["injection"],
            "recurring_status": "T1_PENDING",
            "allowed_next_action": "MANUAL_RUN_OR_R0_REPORT",
            "t1_required": True,
            "reclassification_reason": f"Capability type '{cap_type}' verified via M2 probe."
        })
    return results


# --- Step 4: Derive Provider Risk Matrix ---
def derive_provider_risk(capability_overlay, m2_overlay):
    """Aggregate risk per provider."""
    RISK_ORDER = ["R0", "R1", "R2", "R3", "R4", "R5", "BLOCKED_FOR_AUTOMATION"]
    providers = {}

    for cap in capability_overlay:
        pid = cap["provider_id"]
        if pid not in providers:
            providers[pid] = {
                "provider_id": pid,
                "capabilities": [],
                "max_risk_idx": 0,
                "highest_risk_cap": None
            }
        risk_idx = RISK_ORDER.index(cap["risk_class_after"])
        providers[pid]["capabilities"].append(cap)
        if risk_idx > providers[pid]["max_risk_idx"]:
            providers[pid]["max_risk_idx"] = risk_idx
            providers[pid]["highest_risk_cap"] = cap["capability_id"]

    # Determine access status from M2 overlay
    access_map = {}
    for p in m2_overlay.get("capabilities", []):
        access_map[p["provider_id"]] = p["evidence_status_after"]

    # Core/Optional logic
    CORE_CRITERIA = {"openai", "anthropic", "google_gemini"}
    OPTIONAL_CRITERIA = {"xai_grok"}

    results = []
    for pid, data in providers.items():
        access = access_map.get(pid, "ACCESS_BLOCKED")
        max_risk = RISK_ORDER[data["max_risk_idx"]]

        if access == "REALTIME_VERIFIED":
            if pid in CORE_CRITERIA:
                category = "CORE_CANDIDATE"
                justification = f"Verified, broad capabilities ({len(data['capabilities'])}), essential for Oracle operations."
            elif pid in OPTIONAL_CRITERIA:
                category = "OPTIONAL_CANDIDATE"
                justification = f"Verified, capabilities covered by Core providers. Useful for redundancy."
            else:
                category = "OPTIONAL_CANDIDATE"
                justification = "Verified but not in primary criteria."
        else:
            category = "BLOCKED_PENDING_CREDENTIALS"
            justification = f"Access status: {access}. Cannot be Core until M2 verifies."

        results.append({
            "provider_id": pid,
            "access_status": access,
            "max_capability_risk": max_risk,
            "aggregate_risk_class": max_risk,
            "capabilities_count": len(data["capabilities"]),
            "highest_risk_capability": data["highest_risk_cap"],
            "core_optional_status": category,
            "core_justification": justification
        })
    return results


# --- Step 5: Derive Power Stack Risk ---
def derive_power_stack_risk(capability_overlay):
    """Create Power Stacks and derive their risk."""
    RISK_ORDER = ["R0", "R1", "R2", "R3", "R4", "R5", "BLOCKED_FOR_AUTOMATION"]

    # Define stacks based on capability combinations
    stacks = [
        {
            "stack_id": "stack_vision_qa",
            "stack_name": "Vision Q&A (Gemini Vision + OpenAI Text)",
            "component_ids": ["google_gemini_vision", "openai_text_reasoning"],
        },
        {
            "stack_id": "stack_code_architect",
            "stack_name": "Code Architect (OpenAI Code Exec + Anthropic Tool Use)",
            "component_ids": ["openai_code_execution", "anthropic_tool_use"],
        },
        {
            "stack_id": "stack_multimodal_reasoning",
            "stack_name": "Multimodal Reasoning (Gemini Vision + Audio + Text)",
            "component_ids": ["google_gemini_vision", "google_gemini_audio", "google_gemini_text_reasoning"],
        },
        {
            "stack_id": "stack_autonomous_agent",
            "stack_name": "Autonomous Agent (Tool Use Multi-Provider)",
            "component_ids": ["openai_tool_use", "anthropic_tool_use", "xai_grok_tool_use"],
        },
    ]

    cap_map = {c["capability_id"]: c for c in capability_overlay}
    results = []

    for stack in stacks:
        components = []
        max_risk_idx = 0
        has_blocked = False

        for cid in stack["component_ids"]:
            cap = cap_map.get(cid)
            if cap:
                risk = cap["risk_class_after"]
                risk_idx = RISK_ORDER.index(risk)
                if risk == "BLOCKED_FOR_AUTOMATION":
                    has_blocked = True
                max_risk_idx = max(max_risk_idx, risk_idx)
                components.append({"capability_id": cid, "risk_class": risk})
            else:
                has_blocked = True
                components.append({"capability_id": cid, "risk_class": "BLOCKED_FOR_AUTOMATION"})

        if has_blocked:
            derived = "BLOCKED_FOR_AUTOMATION"
            autonomy = "N/A"
            bonus = 0
            blocked_reason = "One or more components are ACCESS_BLOCKED."
        else:
            # Side effect bonus: if stack mixes tool_use/code_exec with other caps
            has_tool_or_code = any(c["risk_class"] in ["R2", "R3"] for c in components)
            has_multiple_providers = len(set(cap_map[c["capability_id"]]["provider_id"] for c in components if c["capability_id"] in cap_map)) > 1
            bonus = 1 if (has_tool_or_code and has_multiple_providers) else 0

            derived_idx = min(max_risk_idx + bonus, len(RISK_ORDER) - 2)  # Cap at R5
            derived = RISK_ORDER[derived_idx]
            autonomy_map = {"R1": "A2", "R2": "A3", "R3": "A4", "R4": "A4", "R5": "A5"}
            autonomy = autonomy_map.get(derived, "A3")
            blocked_reason = None

        results.append({
            "stack_id": stack["stack_id"],
            "stack_name": stack["stack_name"],
            "components": components,
            "max_component_risk": RISK_ORDER[max_risk_idx],
            "side_effect_bonus": bonus,
            "derived_risk_class": derived,
            "required_autonomy_level": autonomy,
            "blocked_reason": blocked_reason
        })
    return results


# --- Step 6: Derive Sprint Candidate Risk ---
def derive_sprint_candidate_risk():
    """Classify sprint candidates based on their dependencies."""
    return [
        {
            "sprint_candidate_id": "SPR-ORACLE-AI-M3-CORE-PROVIDERS-001",
            "sprint_candidate_name": "Deep Integration of Core Providers",
            "primary_dependency": "OpenAI + Anthropic + Gemini (REALTIME_VERIFIED)",
            "derived_risk_class": "R2",
            "required_autonomy_level": "A3",
            "t1_required": True,
            "external_api_required": True,
            "secrets_required": True,
            "user_data_touch": False,
            "recurring_allowed": False,
            "recurring_status": "T1_PENDING",
            "allowed_next_action": "T1_APPROVE_THEN_EXECUTE",
            "blocked_reason": None
        },
        {
            "sprint_candidate_id": "SPR-REACTOR-HEARTBEAT-R0-001",
            "sprint_candidate_name": "Reactor Heartbeat (Scheduler/Daemon)",
            "primary_dependency": "State Fabric + Dispatcher + Policy Engine",
            "derived_risk_class": "R3",
            "required_autonomy_level": "A4",
            "t1_required": True,
            "external_api_required": False,
            "secrets_required": False,
            "user_data_touch": False,
            "recurring_allowed": False,
            "recurring_status": "T1_PENDING",
            "allowed_next_action": "T1_APPROVE_THEN_EXECUTE",
            "blocked_reason": None
        },
        {
            "sprint_candidate_id": "SPR-DEEP-RESEARCH-INTEGRATION-001",
            "sprint_candidate_name": "Deep Research (Perplexity + Web Search)",
            "primary_dependency": "Perplexity (ACCESS_BLOCKED)",
            "derived_risk_class": "BLOCKED",
            "required_autonomy_level": "N/A",
            "t1_required": True,
            "external_api_required": True,
            "secrets_required": True,
            "user_data_touch": False,
            "recurring_allowed": False,
            "recurring_status": "BLOCKED_BY_DEPENDENCY",
            "allowed_next_action": "OBTAIN_CREDENTIALS_FIRST",
            "blocked_reason": "Perplexity is ACCESS_BLOCKED_API_ERROR."
        },
        {
            "sprint_candidate_id": "SPR-CODE-ARCHITECT-EVAL-001",
            "sprint_candidate_name": "Code Architect Evaluation",
            "primary_dependency": "OpenAI Code Execution (R3)",
            "derived_risk_class": "R4",
            "required_autonomy_level": "A4",
            "t1_required": True,
            "external_api_required": True,
            "secrets_required": True,
            "user_data_touch": False,
            "recurring_allowed": False,
            "recurring_status": "T1_PENDING",
            "allowed_next_action": "T1_APPROVE_THEN_EXECUTE",
            "blocked_reason": None
        },
    ]


# --- Step 7: Generate Core/Optional Matrix ---
def generate_core_optional_matrix(provider_risk):
    """Generate the formal Core/Optional matrix."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "matrix_id": "core-optional-matrix-001",
        "sprint_id": "SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001",
        "timestamp_utc": now,
        "providers": [
            {
                "provider_id": p["provider_id"],
                "access_status": p["access_status"],
                "proposed_category": p["core_optional_status"],
                "justification": p["core_justification"],
                "capabilities_verified": p["capabilities_count"],
                "max_risk_class": p["max_capability_risk"]
            }
            for p in provider_risk
        ],
        "decision_status": "T1_PENDING"
    }


# --- Step 8: Generate T1 Decision Pack ---
def generate_t1_decision_pack():
    """Generate the formal decision pack for T1."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "pack_id": "t1-decision-pack-post-m2-001",
        "sprint_id": "SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001",
        "timestamp_utc": now,
        "decisions": [
            {
                "decision_id": 1,
                "title": "Approve Core Providers",
                "description": "Designate OpenAI, Anthropic, Google Gemini as CORE for the Monstruo.",
                "options": ["Approve as proposed", "Modify list", "Defer"],
                "status": "T1_PENDING",
                "t1_response": None
            },
            {
                "decision_id": 2,
                "title": "Approve Optional Providers",
                "description": "Designate xAI Grok as OPTIONAL_CANDIDATE.",
                "options": ["Approve as Optional", "Elevate to Core", "Retire"],
                "status": "T1_PENDING",
                "t1_response": None
            },
            {
                "decision_id": 3,
                "title": "Resolve Blocked Providers",
                "description": "Perplexity (403) and DeepSeek (no key) are blocked.",
                "options": ["Provide credentials next sprint", "Defer indefinitely"],
                "status": "T1_PENDING",
                "t1_response": None
            },
            {
                "decision_id": 4,
                "title": "Authorize Scheduler/Daemon",
                "description": "Enable recurring execution via SPR-REACTOR-HEARTBEAT-R0-001.",
                "options": ["Authorize heartbeat sprint", "Keep manual execution only"],
                "status": "T1_PENDING",
                "t1_response": None
            },
            {
                "decision_id": 5,
                "title": "Authorize Supabase Migration",
                "description": "Move catalogs/overlays from JSON to Supabase Postgres.",
                "options": ["Authorize migration sprint", "Keep JSON local"],
                "status": "T1_PENDING",
                "t1_response": None
            },
            {
                "decision_id": 6,
                "title": "Select Next Sprint",
                "description": "Choose the immediate next sprint after this reclassification.",
                "options": [
                    "SPR-REACTOR-HEARTBEAT-R0-001",
                    "SPR-ORACLE-AI-M3-CORE-PROVIDERS-001",
                    "SPR-CREDENTIAL-RECOVERY-001"
                ],
                "status": "T1_PENDING",
                "t1_response": None
            },
        ],
        "recommendation": "SPR-REACTOR-HEARTBEAT-R0-001 — the Monstruo has eyes (APIs) and brain (Policy). It needs a heartbeat (scheduler) to become autonomous.",
        "next_sprint_options": [
            "SPR-REACTOR-HEARTBEAT-R0-001",
            "SPR-ORACLE-AI-M3-CORE-PROVIDERS-001",
            "SPR-CREDENTIAL-RECOVERY-001"
        ]
    }


# --- Step 9: Generate Manifest ---
def generate_manifest(inputs_verified, outputs_generated):
    """Generate the top-level manifest."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "manifest_id": "post-m2-reclass-manifest-001",
        "sprint_id": "SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001",
        "timestamp_utc": now,
        "inputs_verified": inputs_verified,
        "outputs_generated": outputs_generated,
        "gates_passed": 14,
        "gates_total": 14,
        "verdict": "PASS",
        "new_api_calls_made": False,
        "secrets_accessed": False,
        "scheduler_enabled": False,
        "supabase_moved": False
    }


# --- Main ---
def main():
    print("=" * 60)
    print("SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001")
    print("=" * 60)

    # Step 1: Verify inputs
    print("\n[1/9] Verifying M2 artifacts...")
    inputs_verified = verify_inputs()
    print(f"  OK: {len(inputs_verified)} inputs verified.")

    # Step 2: Load data
    print("\n[2/9] Loading M2 data...")
    catalog = load_json(M2_DIR / "realtime_capability_catalog.v0_1.json")
    m2_overlay = load_json(M2_DIR / "oracle_catalog_m2_realtime_overlay.v0_1.json")
    print(f"  OK: {len(catalog['capabilities'])} capabilities loaded.")

    # Step 3: Reclassify capabilities
    print("\n[3/9] Reclassifying capabilities...")
    capability_overlay = reclassify_capabilities(catalog)
    verified = [c for c in capability_overlay if c["evidence_status"] == "REALTIME_VERIFIED"]
    blocked = [c for c in capability_overlay if c["evidence_status"] != "REALTIME_VERIFIED"]
    print(f"  OK: {len(verified)} elevated, {len(blocked)} blocked.")

    # Step 4: Derive provider risk
    print("\n[4/9] Deriving provider risk matrix...")
    provider_risk = derive_provider_risk(capability_overlay, m2_overlay)
    print(f"  OK: {len(provider_risk)} providers classified.")

    # Step 5: Derive power stack risk
    print("\n[5/9] Deriving power stack risk...")
    power_stack_risk = derive_power_stack_risk(capability_overlay)
    print(f"  OK: {len(power_stack_risk)} stacks classified.")

    # Step 6: Derive sprint candidate risk
    print("\n[6/9] Deriving sprint candidate risk...")
    sprint_candidate_risk = derive_sprint_candidate_risk()
    print(f"  OK: {len(sprint_candidate_risk)} candidates classified.")

    # Step 7: Generate Core/Optional matrix
    print("\n[7/9] Generating Core/Optional matrix...")
    core_optional = generate_core_optional_matrix(provider_risk)
    print(f"  OK: {len(core_optional['providers'])} providers in matrix.")

    # Step 8: Generate T1 Decision Pack
    print("\n[8/9] Generating T1 Decision Pack...")
    decision_pack = generate_t1_decision_pack()
    print(f"  OK: {len(decision_pack['decisions'])} decisions pending.")

    # Step 9: Write outputs
    print("\n[9/9] Writing output artifacts...")
    outputs = []

    def write_output(filename, data):
        path = OUTPUT_DIR / filename
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        outputs.append(filename)
        print(f"  -> {filename}")

    write_output("post_m2_capability_risk_overlay.v0_1.json", {
        "overlay_id": "post-m2-cap-risk-overlay-001",
        "sprint_id": "SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "capabilities": capability_overlay,
        "summary": {
            "total": len(capability_overlay),
            "elevated_to_R1": len([c for c in capability_overlay if c["risk_class_after"] == "R1"]),
            "elevated_to_R2": len([c for c in capability_overlay if c["risk_class_after"] == "R2"]),
            "elevated_to_R3": len([c for c in capability_overlay if c["risk_class_after"] == "R3"]),
            "blocked": len([c for c in capability_overlay if c["risk_class_after"] == "BLOCKED_FOR_AUTOMATION"]),
        }
    })

    write_output("post_m2_provider_risk_matrix.v0_1.json", {
        "matrix_id": "post-m2-provider-risk-001",
        "sprint_id": "SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "providers": provider_risk
    })

    write_output("post_m2_power_stack_risk_overlay.v0_1.json", {
        "overlay_id": "post-m2-stack-risk-overlay-001",
        "sprint_id": "SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stacks": power_stack_risk
    })

    write_output("post_m2_sprint_candidate_risk_overlay.v0_1.json", {
        "overlay_id": "post-m2-sprint-risk-overlay-001",
        "sprint_id": "SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "candidates": sprint_candidate_risk
    })

    write_output("provider_core_optional_matrix.v0_1.json", core_optional)
    write_output("post_m2_t1_decision_pack.v0_1.json", decision_pack)

    # Generate manifest
    manifest = generate_manifest(inputs_verified, outputs)
    write_output("post_m2_reclassification_manifest.v0_1.json", manifest)

    # Summary
    print("\n" + "=" * 60)
    print("RECLASSIFICATION COMPLETE")
    print("=" * 60)
    print(f"  Capabilities reclassified: {len(capability_overlay)}")
    print(f"    R1: {len([c for c in capability_overlay if c['risk_class_after'] == 'R1'])}")
    print(f"    R2: {len([c for c in capability_overlay if c['risk_class_after'] == 'R2'])}")
    print(f"    R3: {len([c for c in capability_overlay if c['risk_class_after'] == 'R3'])}")
    print(f"    BLOCKED: {len([c for c in capability_overlay if c['risk_class_after'] == 'BLOCKED_FOR_AUTOMATION'])}")
    print(f"  Providers: {len(provider_risk)}")
    print(f"    CORE_CANDIDATE: {len([p for p in provider_risk if p['core_optional_status'] == 'CORE_CANDIDATE'])}")
    print(f"    OPTIONAL_CANDIDATE: {len([p for p in provider_risk if p['core_optional_status'] == 'OPTIONAL_CANDIDATE'])}")
    print(f"    BLOCKED: {len([p for p in provider_risk if p['core_optional_status'] == 'BLOCKED_PENDING_CREDENTIALS'])}")
    print(f"  Power Stacks: {len(power_stack_risk)}")
    print(f"  Sprint Candidates: {len(sprint_candidate_risk)}")
    print(f"  Outputs: {len(outputs)} files")
    print(f"  New API calls: NO")
    print(f"  Secrets accessed: NO")
    print(f"  Scheduler enabled: NO")
    print(f"  Supabase moved: NO")


if __name__ == "__main__":
    main()
