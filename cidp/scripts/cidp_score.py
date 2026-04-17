#!/usr/bin/env python3.11
"""
cidp_score.py — Función Objetivo 10x.

Score compuesto configurable que mide qué tan superior es la nueva
solución vs la referencia. Escala 0-100, donde >= 80 = "10x superior".
"""

import json
import yaml
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent


def load_weights():
    """Load score weights from config."""
    path = SKILL_DIR / "config" / "score_weights.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_10x_score(build_result: dict, research: dict,
                        validation: dict, weights: dict = None) -> float:
    """
    Calculate the composite 10x score.

    The score is based on:
    - Evidence quality from research
    - Validation success rate
    - Build artifact completeness
    - Opportunity coverage
    """
    if weights is None:
        weights = load_weights()

    score_config = weights.get("score_function", {})
    components = score_config.get("components", [])

    total_score = 0.0
    total_weight = 0.0

    for comp in components:
        comp_id = comp.get("id", "")
        weight = comp.get("weight", 0)
        total_weight += weight

        # Calculate component score based on available data
        comp_score = _calculate_component(comp_id, build_result, research, validation)
        total_score += comp_score * weight

    # Normalize to 0-100
    if total_weight > 0:
        normalized = (total_score / total_weight) * 100
    else:
        normalized = 0

    return min(max(normalized, 0), 100)


def _calculate_component(comp_id: str, build: dict, research: dict,
                         validation: dict) -> float:
    """Calculate a single component score (0-1)."""
    if comp_id == "user_value":
        # Based on opportunities identified and artifacts generated
        opportunities = len(research.get("all_opportunities", []))
        artifacts = len(build.get("artifacts", []))
        return min((opportunities * 0.05 + artifacts * 0.1), 1.0)

    elif comp_id == "time_to_value":
        # Based on build plan completeness
        plan = build.get("build_plan", {})
        components = len(plan.get("components", []))
        return min(components * 0.15, 1.0)

    elif comp_id == "quality_reliability":
        # Based on validation score
        return validation.get("validation_score", 0)

    elif comp_id == "cost_per_task":
        # Based on research into economics dimension
        cards = research.get("cards", [])
        econ_cards = [c for c in cards if c.get("dimension") == "economics_finops"]
        if econ_cards:
            findings = econ_cards[0].get("findings", [])
            return min(len(findings) * 0.2, 1.0)
        return 0.3  # Default if not researched

    elif comp_id == "security_posture":
        # Based on security dimension research
        cards = research.get("cards", [])
        sec_cards = [c for c in cards if c.get("dimension") == "security"]
        if sec_cards:
            findings = sec_cards[0].get("findings", [])
            avg_confidence = sum(f.get("confidence", 0) for f in findings) / max(len(findings), 1)
            return avg_confidence
        return 0.3

    elif comp_id == "maintainability":
        # Based on architecture research
        cards = research.get("cards", [])
        arch_cards = [c for c in cards if c.get("dimension") == "architecture_tech_debt"]
        if arch_cards:
            findings = arch_cards[0].get("findings", [])
            return min(len(findings) * 0.15, 1.0)
        return 0.3

    elif comp_id == "competitive_advantage":
        # Based on competitive positioning research
        cards = research.get("cards", [])
        comp_cards = [c for c in cards if c.get("dimension") == "competitive_positioning"]
        if comp_cards:
            opportunities = comp_cards[0].get("opportunities_10x", [])
            return min(len(opportunities) * 0.2, 1.0)
        return 0.2

    elif comp_id == "scalability_headroom":
        # Based on scalability research
        cards = research.get("cards", [])
        scale_cards = [c for c in cards if c.get("dimension") == "scalability"]
        if scale_cards:
            findings = scale_cards[0].get("findings", [])
            return min(len(findings) * 0.15, 1.0)
        return 0.3

    return 0.3  # Default for unknown components


def score_summary(score: float, weights: dict = None) -> str:
    """Generate a human-readable score summary."""
    if weights is None:
        weights = load_weights()

    threshold = weights.get("score_function", {}).get("threshold_10x", 80)

    if score >= threshold:
        status = "10x ACHIEVED"
    elif score >= threshold * 0.75:
        status = "APPROACHING 10x"
    elif score >= threshold * 0.5:
        status = "MODERATE PROGRESS"
    else:
        status = "EARLY STAGE"

    return f"Score: {score:.1f}/100 — {status} (threshold: {threshold})"
