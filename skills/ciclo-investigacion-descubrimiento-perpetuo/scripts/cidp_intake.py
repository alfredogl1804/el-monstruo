#!/usr/bin/env python3.11
"""
cidp_intake.py — Stage 1: Intake & Scope.

Normaliza el input del usuario, clasifica el software objetivo,
define el scope, presupuesto, guardrails y métricas 10x.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

SKILL_DIR = Path(__file__).parent.parent

SYSTEM = """Eres el módulo de Intake del CIDP (Ciclo de Investigación y Descubrimiento Perpetuo).
Tu trabajo es analizar un software/plataforma objetivo y producir una especificación de scope estructurada.
Responde SOLO con JSON válido, sin markdown ni explicaciones."""


async def run_intake(target: str, objective: str, dimensions: dict, budget_usd: float, output_dir: Path) -> dict:
    """Execute Stage 1: Intake & Scope."""
    print(f"  Analizando target: {target}")
    print(f"  Objetivo: {objective}")

    # Load dimensions
    dim_list = dimensions.get("dimensions", [])
    dim_names = [d["name"] for d in dim_list]
    mandatory_dims = [d["id"] for d in dim_list if d.get("mandatory", False)]

    prompt = f"""Analiza el siguiente software/plataforma y genera la especificación de scope para investigación 10x:

TARGET: {target}
OBJECTIVE: {objective}
BUDGET: ${budget_usd} USD
AVAILABLE DIMENSIONS: {json.dumps(dim_names, ensure_ascii=False)}

Responde con este JSON exacto:
{{
  "target_normalized": "Nombre normalizado del software",
  "target_type": "saas|desktop|mobile|library|framework|platform|api|other",
  "target_url": "URL oficial si la conoces, null si no",
  "target_description": "Descripción breve de qué es y qué hace",
  "domain": "Dominio/industria del software",
  "objective_refined": "Objetivo 10x refinado y específico",
  "active_dimensions": {json.dumps(mandatory_dims)},
  "success_metrics": [
    {{"id": "metric_1", "name": "...", "current_estimate": 0, "target_10x": 0, "unit": "..."}}
  ],
  "guardrails": ["Lista de restricciones y límites"],
  "legal_considerations": ["Consideraciones legales para la investigación"],
  "scope_approved": true,
  "estimated_iterations": 5,
  "risk_level": "low|medium|high|critical"
}}"""

    response = await consultar_sabio("gpt54", prompt, system=SYSTEM)
    text = response.get("respuesta", "")

    # Parse JSON
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        import re

        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            result = json.loads(match.group())
        else:
            result = {
                "target_normalized": target,
                "target_type": "unknown",
                "objective_refined": objective,
                "active_dimensions": mandatory_dims,
                "success_metrics": [],
                "guardrails": [],
                "scope_approved": True,
                "risk_level": "medium",
            }

    # Ensure mandatory dimensions are included
    active = result.get("active_dimensions", [])
    for dim_id in mandatory_dims:
        if dim_id not in active:
            active.append(dim_id)
    result["active_dimensions"] = active

    # Save
    output_path = output_dir / "scope.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Save readable scope
    scope_md = output_dir / "scope.md"
    with open(scope_md, "w", encoding="utf-8") as f:
        f.write(f"# Scope: {result.get('target_normalized', target)}\n\n")
        f.write(f"**Tipo:** {result.get('target_type', 'unknown')}\n\n")
        f.write(f"**Objetivo 10x:** {result.get('objective_refined', objective)}\n\n")
        f.write(f"**Dimensiones activas:** {len(active)}\n\n")
        f.write(f"**Nivel de riesgo:** {result.get('risk_level', 'medium')}\n\n")
        if result.get("success_metrics"):
            f.write("## Métricas de Éxito\n\n")
            for m in result["success_metrics"]:
                f.write(
                    f"- **{m.get('name', 'N/A')}**: {m.get('current_estimate', '?')} → {m.get('target_10x', '?')} {m.get('unit', '')}\n"
                )
        if result.get("guardrails"):
            f.write("\n## Guardrails\n\n")
            for g in result["guardrails"]:
                f.write(f"- {g}\n")

    print(f"  Scope saved: {output_path}")
    return result
