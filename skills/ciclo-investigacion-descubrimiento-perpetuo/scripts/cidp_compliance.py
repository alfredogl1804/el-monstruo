#!/usr/bin/env python3.11
"""
cidp_compliance.py — Policy Engine: Gates regulatorios.

Evalúa cumplimiento regulatorio por obligación y fecha.
NO es un checkbox genérico — es un motor de políticas con timeline.
"""

from datetime import datetime
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).parent.parent


def load_compliance_rules():
    """Load compliance rules from config."""
    path = SKILL_DIR / "config" / "compliance_rules.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_compliance_gate(stage: str, context: dict = None) -> dict:
    """
    Check compliance gate for a specific stage.

    Args:
        stage: The current stage (intake, research, build, deploy)
        context: Additional context about the project

    Returns:
        Dict with compliance check results
    """
    rules = load_compliance_rules()
    gates = rules.get("compliance_gates", [])
    now = datetime.now()

    results = {
        "stage": stage,
        "timestamp": now.isoformat(),
        "passed": True,
        "checks": [],
        "warnings": [],
        "blockers": [],
    }

    # Find applicable gate
    applicable_gate = None
    for gate in gates:
        if gate.get("stage") == stage:
            applicable_gate = gate
            break

    if not applicable_gate:
        results["checks"].append({"check": "No compliance gate defined for this stage", "status": "skip"})
        return results

    # Run checks
    for check in applicable_gate.get("checks", []):
        check_result = {
            "check": check,
            "status": "pending",
            "notes": "",
        }

        # Auto-evaluate what we can
        if "ToS" in check:
            check_result["status"] = "manual_review"
            check_result["notes"] = "Requires manual review of target software's Terms of Service"
            results["warnings"].append(check)

        elif "datos personales" in check.lower() or "privacy" in check.lower():
            check_result["status"] = "check"
            check_result["notes"] = "Verify if personal data is being processed"

        elif "código protegido" in check.lower() or "copiar" in check.lower():
            check_result["status"] = "check"
            check_result["notes"] = "Ensure no protected code is copied"

        else:
            check_result["status"] = "pending"
            check_result["notes"] = "Requires evaluation"

        results["checks"].append(check_result)

    # Check AI Act timeline
    ai_act = rules.get("frameworks", {}).get("ai_act", {})
    timeline = ai_act.get("timeline", [])
    for entry in timeline:
        entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
        if entry.get("status") == "active" and now >= entry_date:
            results["warnings"].append(f"AI Act obligation active since {entry['date']}: {entry['description']}")
        elif entry.get("status") == "upcoming":
            days_until = (entry_date - now).days
            if days_until <= 180:
                results["warnings"].append(f"AI Act obligation upcoming in {days_until} days: {entry['description']}")

    # Check reverse engineering rules
    re_rules = rules.get("frameworks", {}).get("reverse_engineering", {})
    if stage == "research":
        for rule in re_rules.get("rules", []):
            results["warnings"].append(f"RE Legal: {rule}")

    return results


def generate_compliance_report(stages_checked: list) -> dict:
    """Generate a comprehensive compliance report."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "stages": stages_checked,
        "overall_status": "pass",
        "total_warnings": 0,
        "total_blockers": 0,
    }

    for stage in stages_checked:
        report["total_warnings"] += len(stage.get("warnings", []))
        report["total_blockers"] += len(stage.get("blockers", []))
        if stage.get("blockers"):
            report["overall_status"] = "blocked"
        elif stage.get("warnings") and report["overall_status"] == "pass":
            report["overall_status"] = "pass_with_warnings"

    return report
