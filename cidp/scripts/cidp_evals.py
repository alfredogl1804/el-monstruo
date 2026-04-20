#!/usr/bin/env python3.11
"""
cidp_evals.py — Evaluación multi-modelo.

Evalúa la solución construida contra la función objetivo 10x
usando múltiples modelos para cross-validation.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio


async def evaluate_solution(
    solution_spec: str, target_description: str, success_metrics: list, output_dir: Path
) -> dict:
    """
    Evaluate the proposed solution against the reference and success metrics.

    Uses multiple models for cross-validation.
    """
    evaluators = {
        "claude": "Evalúa la calidad arquitectónica, mantenibilidad y elegancia del diseño.",
        "gemini": "Evalúa la factibilidad técnica, UX/accesibilidad y alineación con estándares actuales.",
        "grok": "Evalúa críticamente: busca debilidades, riesgos ocultos y suposiciones no validadas.",
    }

    prompt_template = """Evalúa esta solución propuesta contra el software de referencia:

REFERENCIA: {target}

SOLUCIÓN PROPUESTA:
{solution}

MÉTRICAS DE ÉXITO:
{metrics}

{role_instruction}

Responde con JSON:
{{
  "overall_score": 0-100,
  "component_scores": {{
    "user_value": 0-100,
    "technical_quality": 0-100,
    "feasibility": 0-100,
    "innovation": 0-100,
    "risk_level": 0-100
  }},
  "strengths": ["..."],
  "weaknesses": ["..."],
  "risks": ["..."],
  "recommendations": ["..."],
  "confidence": 0.0-1.0
}}"""

    results = {}
    total_cost = 0.0

    for sabio_id, role in evaluators.items():
        prompt = prompt_template.format(
            target=target_description[:1000],
            solution=solution_spec[:3000],
            metrics=json.dumps(success_metrics, ensure_ascii=False)[:1000],
            role_instruction=role,
        )

        try:
            response = await consultar_sabio(sabio_id, prompt)
            text = response.get("respuesta", "")

            try:
                eval_result = json.loads(text)
            except json.JSONDecodeError:
                import re

                match = re.search(r"\{[\s\S]*\}", text)
                if match:
                    eval_result = json.loads(match.group())
                else:
                    eval_result = {
                        "overall_score": 50,
                        "confidence": 0.3,
                        "raw": text[:500],
                    }

            results[sabio_id] = eval_result
            total_cost += response.get("tokens_total", 0) * 0.00001

        except Exception as e:
            results[sabio_id] = {"error": str(e), "overall_score": 0, "confidence": 0}

    # Aggregate scores
    scores = [r.get("overall_score", 0) for r in results.values() if "error" not in r]
    confidences = [r.get("confidence", 0) for r in results.values() if "error" not in r]

    aggregate = {
        "evaluators": results,
        "avg_score": sum(scores) / len(scores) if scores else 0,
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
        "consensus": max(scores) - min(scores) < 20 if len(scores) >= 2 else False,
        "cost_usd": total_cost,
    }

    # Save
    eval_path = output_dir / "eval_results.json"
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(aggregate, f, indent=2, ensure_ascii=False)

    return aggregate
