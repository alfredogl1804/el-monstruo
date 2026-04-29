#!/usr/bin/env python3.11
"""
cidp_convergence.py — Stage 7: Convergence Gate.

Evalúa si el ciclo debe continuar o detenerse basándose en:
- Mejora del score 10x
- Presupuesto restante
- Riesgo aceptable
- Evidencia suficiente
- Alineación con scope
"""

import json
from pathlib import Path


def run_convergence_gate(current_score: float, new_score: float, iteration: int,
                         max_iterations: int, budget_remaining: float,
                         threshold: float, validation: dict,
                         output_dir: Path) -> dict:
    """Execute Stage 7: Convergence Gate."""
    score_delta = new_score - current_score
    target_score = threshold * 100  # Convert 0-1 threshold to 0-100

    # Decision logic
    decision = "continue"
    reasons = []

    # Check convergence
    if new_score >= target_score:
        decision = "converged"
        reasons.append(f"Score {new_score:.1f} >= target {target_score:.1f}")

    # Check diminishing returns
    elif score_delta < 2.0 and iteration > 2:
        decision = "stop"
        reasons.append(f"Diminishing returns: delta {score_delta:.1f} < 2.0 after iteration {iteration}")

    # Check budget
    elif budget_remaining <= 0:
        decision = "stop"
        reasons.append(f"Budget exhausted: ${budget_remaining:.2f} remaining")

    # Check max iterations
    elif iteration >= max_iterations:
        decision = "stop"
        reasons.append(f"Max iterations reached: {iteration}/{max_iterations}")

    # Check validation quality
    elif validation.get("validation_score", 0) < 0.5:
        reasons.append(f"Low validation score: {validation.get('validation_score', 0):.2f}")
        # Don't stop, but flag it

    # Check critical contradictions
    critical_contradictions = [
        c for c in validation.get("contradictions", [])
        if c.get("type") == "outdated"
    ]
    if len(critical_contradictions) > 3:
        reasons.append(f"High contradiction count: {len(critical_contradictions)} outdated claims")

    # If still continuing, check if improvement is meaningful
    if decision == "continue":
        if score_delta > 0:
            reasons.append(f"Score improved by {score_delta:.1f} points")
        else:
            reasons.append(f"Score did not improve (delta: {score_delta:.1f})")
            if iteration > 3:
                decision = "stop"
                reasons.append("No improvement after 3+ iterations")

    result = {
        "decision": decision,
        "reason": "; ".join(reasons),
        "current_score": new_score,
        "previous_score": current_score,
        "score_delta": score_delta,
        "target_score": target_score,
        "iteration": iteration,
        "budget_remaining": budget_remaining,
        "validation_score": validation.get("validation_score", 0),
        "contradictions_count": len(validation.get("contradictions", [])),
    }

    # Save
    report_path = output_dir / "convergence_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result
