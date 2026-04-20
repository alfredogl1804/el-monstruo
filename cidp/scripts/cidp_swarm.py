#!/usr/bin/env python3.11
"""
cidp_swarm.py — Stage 4: Swarm Execution.

Distribuye tareas del backlog a los Sabios especializados usando
consulta-sabios. Incluye calibración opcional de capacidades.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

SKILL_DIR = Path(__file__).parent.parent

# Role descriptions for each sabio
ROLE_DESCRIPTIONS = {
    "gpt54": "Eres un arquitecto de software y planificador estratégico de primer nivel.",
    "claude": "Eres un experto en arquitectura de software, calidad de código y detección de patrones anti-autoboicot.",
    "gemini": "Eres un verificador factual con acceso a Google Search grounding y experto en UX/visión.",
    "grok": "Eres un revisor adversarial y estratega de producto. Tu trabajo es encontrar debilidades y proponer alternativas contrarian.",  # noqa: E501
    "deepseek": "Eres un optimizador de rendimiento y generador de código de alta calidad.",
    "perplexity": "Eres un investigador en tiempo real con acceso a información actualizada del mercado.",
}


async def execute_task(task: dict) -> dict:
    """Execute a single task by sending it to the assigned sabio."""
    sabio_id = task.get("assigned_to", "gpt54")
    task_id = task.get("id", "UNKNOWN")
    title = task.get("title", "No title")
    criteria = task.get("acceptance_criteria", [])

    system = ROLE_DESCRIPTIONS.get(sabio_id, "Eres un experto analista.")

    prompt = f"""TAREA: {title}

ID: {task_id}
PRIORIDAD: {task.get("priority", "P1")}

CRITERIOS DE ACEPTACIÓN:
{json.dumps(criteria, ensure_ascii=False)}

Ejecuta esta tarea con la máxima calidad. Tu respuesta debe cumplir TODOS los criterios de aceptación.
Responde con JSON:
{{
  "task_id": "{task_id}",
  "status": "completed|partial|failed",
  "output": "Tu respuesta detallada aquí",
  "claims": ["Lista de afirmaciones verificables que haces"],
  "confidence": 0.0-1.0,
  "suggestions": ["Sugerencias adicionales"],
  "needs_validation": ["Cosas que necesitan verificación en tiempo real"]
}}"""

    try:
        response = await consultar_sabio(sabio_id, prompt, system=system)
        text = response.get("respuesta", "")

        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            import re

            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                try:
                    result = json.loads(match.group())
                except json.JSONDecodeError:
                    result = {
                        "task_id": task_id,
                        "status": "completed",
                        "output": text[:5000],
                        "claims": [],
                        "confidence": 0.7,
                        "suggestions": [],
                        "needs_validation": [],
                    }
            else:
                result = {
                    "task_id": task_id,
                    "status": "completed",
                    "output": text[:5000],
                    "claims": [],
                    "confidence": 0.7,
                    "suggestions": [],
                    "needs_validation": [],
                }

        result["sabio"] = sabio_id
        result["task_id"] = task_id
        result["cost_usd"] = response.get("tokens_total", 0) * 0.00001
        result["quality_score"] = _evaluate_quality(result, criteria)

    except Exception as e:
        result = {
            "task_id": task_id,
            "sabio": sabio_id,
            "status": "failed",
            "error": str(e),
            "output": "",
            "claims": [],
            "confidence": 0,
            "quality_score": 0,
            "cost_usd": 0,
        }

    return result


def _evaluate_quality(response: dict, criteria: list) -> float:
    """Simple quality evaluation based on response completeness."""
    score = 0.0
    output = response.get("output", "")

    # Length check
    if len(output) > 100:
        score += 0.3
    if len(output) > 500:
        score += 0.2

    # Claims present
    if response.get("claims"):
        score += 0.2

    # Confidence
    score += response.get("confidence", 0) * 0.3

    return min(score, 1.0)


async def run_calibration(config: dict, output_dir: Path) -> dict:
    """Run sabio calibration to benchmark real capabilities."""
    print("  Running sabio calibration...")

    calibration_prompt = """Responde con JSON exacto:
{
  "model_name": "Tu nombre de modelo exacto",
  "capabilities": {
    "code_generation": 0.0-1.0,
    "architecture_design": 0.0-1.0,
    "factual_accuracy": 0.0-1.0,
    "creative_thinking": 0.0-1.0,
    "adversarial_review": 0.0-1.0,
    "realtime_research": 0.0-1.0
  },
  "context_limit_tokens": 0,
  "strengths": ["..."],
  "weaknesses": ["..."]
}
Sé honesto sobre tus capacidades reales."""

    sabios = ["gpt54", "claude", "gemini", "grok", "deepseek", "perplexity"]
    results = {}

    for sabio_id in sabios:
        try:
            resp = await consultar_sabio(sabio_id, calibration_prompt)
            text = resp.get("respuesta", "")
            try:
                results[sabio_id] = json.loads(text)
            except json.JSONDecodeError:
                import re

                match = re.search(r"\{[\s\S]*\}", text)
                if match:
                    results[sabio_id] = json.loads(match.group())
                else:
                    results[sabio_id] = {"status": "parse_failed", "raw": text[:500]}
        except Exception as e:
            results[sabio_id] = {"status": "failed", "error": str(e)}

    # Save calibration
    cal_path = SKILL_DIR / "data" / "calibration_results.json"
    cal_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cal_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return results


async def run_swarm(tasks: list, config: dict, skip_calibration: bool, output_dir: Path) -> dict:
    """Execute Stage 4: Swarm Execution."""
    # Calibration (if needed)
    cal_path = SKILL_DIR / "data" / "calibration_results.json"
    if not skip_calibration and not cal_path.exists():
        await run_calibration(config, output_dir)

    if not tasks:
        return {
            "responses_count": 0,
            "responses": [],
            "avg_quality": 0,
            "cost_usd": 0,
        }

    print(f"  Executing {len(tasks)} tasks across sabios...")

    # Execute tasks in parallel (batches of 4)
    all_responses = []
    total_cost = 0.0

    for i in range(0, len(tasks), 4):
        batch = tasks[i : i + 4]
        results = await asyncio.gather(*[execute_task(t) for t in batch], return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                all_responses.append({"status": "error", "error": str(r)})
            else:
                all_responses.append(r)
                total_cost += r.get("cost_usd", 0)

    # Calculate average quality
    qualities = [r.get("quality_score", 0) for r in all_responses if r.get("status") != "error"]
    avg_quality = sum(qualities) / len(qualities) if qualities else 0

    result = {
        "responses_count": len(all_responses),
        "responses": all_responses,
        "avg_quality": avg_quality,
        "cost_usd": total_cost,
        "successful": sum(1 for r in all_responses if r.get("status") in ("completed", "partial")),
        "failed": sum(1 for r in all_responses if r.get("status") in ("failed", "error")),
    }

    # Save
    responses_path = output_dir / "sabios_responses.json"
    with open(responses_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result
