#!/usr/bin/env python3.11
"""
cidp_builder.py — Stage 6: Build / Prototype / Eval.

Genera especificaciones, prototipos, código, tests y benchmarks
de la nueva solución. Puede invocar el GPU broker si se requiere
entrenamiento o inferencia pesada.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

SKILL_DIR = Path(__file__).parent.parent


async def generate_build_plan(validated_plan: dict, orchestrator_plan: dict,
                              iteration: int) -> dict:
    """Generate a build plan based on validated findings."""
    # Collect verified claims and validated outputs
    verified = validated_plan.get("verified_claims", [])
    backlog = orchestrator_plan.get("backlog", [])
    north_star = orchestrator_plan.get("north_star", "")

    # Pre-format JSON strings to avoid f-string brace conflicts
    verified_json = json.dumps([v.get('claim', '') for v in verified if v.get('verified')], ensure_ascii=False)[:3000]
    backlog_json = json.dumps([{'id': t.get('id'), 'title': t.get('title')} for t in backlog], ensure_ascii=False)[:2000]

    prompt = f"""Basándote en los siguientes hallazgos validados, genera un plan de construcción:

NORTH STAR: {north_star}
ITERACIÓN: {iteration}

HALLAZGOS VALIDADOS ({len(verified)} claims verificados):
{verified_json}

BACKLOG:
{backlog_json}

Responde con JSON:
{{
  "build_plan": {{
    "phase": "spec|prototype|code|test|benchmark",
    "description": "Qué se va a construir en esta iteración",
    "components": [
      {{
        "name": "...",
        "type": "spec|code|config|test|doc",
        "description": "...",
        "estimated_effort": "low|medium|high",
        "dependencies": []
      }}
    ],
    "requires_gpu": false,
    "gpu_workload": null
  }},
  "artifacts": [
    {{
      "name": "...",
      "type": "spec|code|config|test|doc|benchmark",
      "content_summary": "..."
    }}
  ]
}}"""

    response = await consultar_sabio("gpt54", prompt)
    text = response.get("respuesta", "")

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                result = json.loads(match.group())
            except json.JSONDecodeError:
                result = _fallback_build_plan(iteration)
        else:
            result = _fallback_build_plan(iteration)

    result["cost_usd"] = response.get("tokens_total", 0) * 0.00003
    return result


def _fallback_build_plan(iteration):
    """Fallback build plan."""
    return {
        "build_plan": {
            "phase": "spec",
            "description": f"Generate specifications for iteration {iteration}",
            "components": [],
            "requires_gpu": False,
        },
        "artifacts": [],
        "cost_usd": 0,
    }


async def execute_build(build_plan: dict, output_dir: Path) -> dict:
    """Execute the build plan and generate artifacts."""
    artifacts = []
    plan = build_plan.get("build_plan", {})
    components = plan.get("components", [])

    for comp in components:
        comp_name = comp.get("name", "unnamed")
        comp_type = comp.get("type", "doc")

        # For specs and docs, generate with Claude (architecture expert)
        if comp_type in ("spec", "doc"):
            prompt = f"""Genera el siguiente artefacto de construcción:

NOMBRE: {comp_name}
TIPO: {comp_type}
DESCRIPCIÓN: {comp.get('description', '')}

Produce un documento completo y profesional."""

            try:
                response = await consultar_sabio("claude", prompt)
                content = response.get("respuesta", "")
                artifacts.append({
                    "name": comp_name,
                    "type": comp_type,
                    "content": content[:10000],
                    "status": "generated",
                })
            except Exception as e:
                artifacts.append({
                    "name": comp_name,
                    "type": comp_type,
                    "status": "failed",
                    "error": str(e),
                })

        # For code, generate with DeepSeek (optimization expert)
        elif comp_type == "code":
            prompt = f"""Genera el siguiente código:

NOMBRE: {comp_name}
DESCRIPCIÓN: {comp.get('description', '')}

Produce código limpio, documentado y con manejo de errores."""

            try:
                response = await consultar_sabio("deepseek", prompt)
                content = response.get("respuesta", "")
                artifacts.append({
                    "name": comp_name,
                    "type": comp_type,
                    "content": content[:10000],
                    "status": "generated",
                })
            except Exception as e:
                artifacts.append({
                    "name": comp_name,
                    "type": comp_type,
                    "status": "failed",
                    "error": str(e),
                })

    return {"artifacts": artifacts}


async def run_builder(validated_plan: dict, orchestrator_plan: dict,
                      iteration: int, enable_gpu: bool, gpu_budget: float,
                      output_dir: Path) -> dict:
    """Execute Stage 6: Build / Prototype / Eval."""
    # Generate build plan
    print("  Generating build plan...")
    build_plan = await generate_build_plan(validated_plan, orchestrator_plan, iteration)

    # Check if GPU is needed
    requires_gpu = build_plan.get("build_plan", {}).get("requires_gpu", False)
    if requires_gpu and enable_gpu:
        print("  GPU required — invoking GPU broker...")
        # Import and use gpu_broker
        try:
            from gpu_broker import provision_gpu
            gpu_result = await provision_gpu(
                workload=build_plan.get("build_plan", {}).get("gpu_workload", {}),
                budget_usd=gpu_budget,
            )
            build_plan["gpu_provisioned"] = gpu_result
        except Exception as e:
            print(f"  GPU broker failed: {e}")
            build_plan["gpu_provisioned"] = {"status": "failed", "error": str(e)}

    # Execute build
    print("  Executing build plan...")
    build_result = await execute_build(build_plan, output_dir)

    # Combine results
    result = {
        **build_plan,
        **build_result,
        "iteration": iteration,
        "cost_usd": build_plan.get("cost_usd", 0),
    }

    # Save
    plan_path = output_dir / "build_plan.json"
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result
