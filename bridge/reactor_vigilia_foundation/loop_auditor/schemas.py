"""
Schemas (Mock) para validación del Loop Auditor.
En una implementación real, estos serían archivos JSON Schema o Pydantic models.
Aquí los definimos como diccionarios base para usarlos en el código de simulación.
"""

# loop_auditor_contract.yaml equivalente (ya existe en loop_registry.v0.yaml)

ORACLE_AUDIT_RESULT_SCHEMA = {
    "type": "object",
    "required": ["audit_id", "target_loop", "verdict", "timestamp", "findings_summary"],
    "properties": {
        "audit_id": {"type": "string"},
        "target_loop": {"type": "string"},
        "verdict": {"type": "string", "enum": ["PASS", "PASS_WITH_FINDINGS", "FAIL"]},
        "timestamp": {"type": "string"},
        "findings_summary": {
            "type": "object",
            "properties": {
                "total": {"type": "integer"},
                "high": {"type": "integer"},
                "medium": {"type": "integer"},
                "low": {"type": "integer"}
            }
        }
    }
}

ORACLE_AUDIT_FINDINGS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["finding_id", "severity", "subject", "status"],
        "properties": {
            "finding_id": {"type": "string"},
            "severity": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
            "subject": {"type": "string"},
            "evidence_ref": {"type": "string"},
            "status": {"type": "string", "enum": ["OPEN", "RESOLVED", "ACCEPTED_RISK"]},
            "recommended_next_action": {"type": "string"},
            "t1_required": {"type": "boolean"}
        }
    }
}

AUDITOR_GATE_LOG_SCHEMA = {
    "type": "object",
    "properties": {
        "schema_validity": {"type": "boolean"},
        "report_consistency": {"type": "boolean"},
        "authority_check": {"type": "boolean"},
        "evidence_check": {"type": "boolean"},
        "policy_check": {"type": "boolean"},
        "f16_check": {"type": "boolean"},
        "no_autonomy_creep": {"type": "boolean"},
        "no_external_api": {"type": "boolean"},
        "no_canon": {"type": "boolean"},
        "no_runtime_side_effects": {"type": "boolean"}
    }
}
