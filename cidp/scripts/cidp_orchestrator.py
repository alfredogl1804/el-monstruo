#!/usr/bin/env python3.11
"""
cidp_orchestrator.py — Stage 3: Synthesis Core.

GPT-5.4 como Arquitecto: sintetiza evidencia, prioriza backlog,
delega tareas a Sabios especializados, y define la North Star.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

SKILL_DIR = Path(__file__).parent.parent


def load_system_prompt():
    """Load orchestrator system prompt."""
    path = SKILL_DIR / "config" / "orchestrator_system.md"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_context(target, objective, iteration, research, memory, current_score, score_weights):
    """Build the context for the orchestrator."""
    # Summarize research findings
    findings_summary = []
    for card in research.get("cards", [])[:15]:
        dim = card.get("dimension_name", card.get("dimension", "?"))
        top_findings = card.get("findings", [])[:3]
        for f in top_findings:
            findings_summary.append(f"[{dim}] {f.get('finding', '')[:200]} (confidence: {f.get('confidence', 0)})")

    # Get memory context
    previous_decisions = memory.get_decisions(limit=5) if memory else []
    known_contradictions = memory.get_contradictions(limit=10) if memory else []

    context = {
        "target": target,
        "objective": objective,
        "iteration": iteration,
        "current_10x_score": current_score,
        "findings_count": research.get("evidence_count", 0),
        "top_findings": findings_summary[:20],
        "unknowns": research.get("all_unknowns", [])[:10],
        "contradictions": research.get("all_contradictions", [])[:10],
        "opportunities": research.get("all_opportunities", [])[:15],
        "previous_decisions": previous_decisions,
        "known_contradictions": known_contradictions,
        "score_components": [c["name"] for c in score_weights.get("score_function", {}).get("components", [])],
    }
    return context


async def run_orchestrator(
    target,
    objective,
    iteration,
    research,
    memory,
    score_weights,
    current_score,
    output_dir,
):
    """Execute Stage 3: Synthesis Core with GPT-5.4."""
    system = load_system_prompt()
    context = build_context(target, objective, iteration, research, memory, current_score, score_weights)

    prompt = f"""CONTEXTO DE ITERACIÓN {iteration}:

{json.dumps(context, indent=2, ensure_ascii=False)}

Basándote en toda la evidencia recopilada, genera el plan de esta iteración.
Asigna tareas a los sabios disponibles: gpt54, claude, gemini, grok, deepseek, perplexity.
Cada tarea debe tener criterios de aceptación medibles.

Responde con el JSON estructurado según tu system prompt."""

    response = await consultar_sabio("gpt54", prompt, system=system)
    text = response.get("respuesta", "")

    # Parse JSON
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        import re

        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                result = json.loads(match.group())
            except json.JSONDecodeError:
                result = _fallback_plan(target, objective, iteration, research)
        else:
            result = _fallback_plan(target, objective, iteration, research)

    result["iteration"] = iteration
    result["cost_usd"] = response.get("tokens_total", 0) * 0.00003  # GPT-5.4 approximate

    # Save
    plan_path = output_dir / "north_star_spec.json"
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Save readable version
    md_path = output_dir / "north_star_spec.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# North Star — Iteration {iteration}\n\n")
        f.write(f"**Objective:** {result.get('north_star', 'N/A')}\n\n")
        f.write(f"**Current Score:** {result.get('score_10x_current', current_score)}\n\n")
        if result.get("backlog"):
            f.write("## Backlog\n\n")
            for task in result["backlog"]:
                f.write(f"### {task.get('id', '?')}: {task.get('title', '?')}\n")
                f.write(f"- **Assigned to:** {task.get('assigned_to', '?')}\n")
                f.write(f"- **Priority:** {task.get('priority', '?')}\n")
                f.write(f"- **Impact:** {task.get('estimated_impact_on_10x', '?')}\n\n")

    # Save task delegations
    delegations_path = output_dir / "task_delegations.json"
    with open(delegations_path, "w", encoding="utf-8") as f:
        json.dump(result.get("backlog", []), f, indent=2, ensure_ascii=False)

    return result


def _fallback_plan(target, objective, iteration, research):
    """Generate a fallback plan if GPT-5.4 fails to produce valid JSON."""
    opportunities = research.get("all_opportunities", [])[:5]
    return {
        "iteration": iteration,
        "north_star": f"Investigate and prototype top opportunities for {target}",
        "score_10x_current": 0,
        "score_10x_target": 20,
        "key_findings": [f"Research found {research.get('evidence_count', 0)} evidence items"],
        "unresolved_contradictions": research.get("all_contradictions", [])[:5],
        "backlog": [
            {
                "id": f"TASK-{i + 1}",
                "title": opp[:100] if opp else f"Investigate opportunity {i + 1}",
                "assigned_to": ["claude", "gemini", "grok", "deepseek", "perplexity"][i % 5],
                "priority": "P1",
                "acceptance_criteria": ["Produce actionable specification"],
                "estimated_impact_on_10x": 5,
            }
            for i, opp in enumerate(opportunities)
        ],
        "risks": ["Fallback plan — may need manual refinement"],
        "decision_log_entry": "Used fallback plan due to JSON parsing failure",
    }
