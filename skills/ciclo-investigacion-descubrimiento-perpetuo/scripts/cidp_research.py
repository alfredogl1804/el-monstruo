#!/usr/bin/env python3.11
"""
cidp_research.py — Stage 2: Deep Research Mesh.

Investigación paralela en 19+ dimensiones usando Perplexity Sonar
y validación cruzada. Genera research cards con score de confianza.
"""

import asyncio
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

SKILL_DIR = Path(__file__).parent.parent


def load_dimensions():
    """Load dimension definitions."""
    path = SKILL_DIR / "config" / "dimensions.yaml"
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {d["id"]: d for d in data.get("dimensions", [])}


async def research_dimension(target: str, dimension: dict, iteration: int, previous_findings: list) -> dict:
    """Research a single dimension using Perplexity for real-time data."""
    dim_id = dimension["id"]
    dim_name = dimension["name"]
    prompts = dimension.get("research_prompts", [])

    # Build research prompt
    prompt_parts = [f"Investiga en profundidad la dimensión '{dim_name}' del software/plataforma: {target}"]
    for p in prompts:
        prompt_parts.append(p.replace("{target}", target))

    if previous_findings:
        prompt_parts.append("\nHallazgos previos a profundizar o verificar:")
        for f in previous_findings[:5]:
            prompt_parts.append(f"- {f}")

    prompt_parts.append("""
Responde con JSON:
{
  "dimension": "...",
  "findings": [
    {"finding": "...", "confidence": 0.0-1.0, "source": "...", "evidence": "..."}
  ],
  "unknowns": ["cosas que no pudiste determinar"],
  "contradictions": ["contradicciones encontradas"],
  "opportunities_10x": ["oportunidades para mejora 10x en esta dimensión"]
}""")

    full_prompt = "\n\n".join(prompt_parts)

    try:
        # Use Perplexity for real-time research
        response = await consultar_sabio("perplexity", full_prompt)
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
                    "dimension": dim_id,
                    "findings": [
                        {"finding": text[:500], "confidence": 0.5, "source": "perplexity", "evidence": "raw_response"}
                    ],
                    "unknowns": [],
                    "contradictions": [],
                    "opportunities_10x": [],
                }

        result["dimension"] = dim_id
        result["dimension_name"] = dim_name
        result["status"] = "completed"
        result["cost_usd"] = response.get("tokens_total", 0) * 0.000005  # Approximate

    except Exception as e:
        result = {
            "dimension": dim_id,
            "dimension_name": dim_name,
            "status": "failed",
            "error": str(e),
            "findings": [],
            "unknowns": [f"Research failed: {e}"],
            "contradictions": [],
            "opportunities_10x": [],
            "cost_usd": 0,
        }

    return result


async def run_research(
    target: str, dimensions: list, iteration: int, previous_findings: dict, output_dir: Path
) -> dict:
    """Execute Stage 2: Deep Research Mesh across all active dimensions."""
    all_dims = load_dimensions()
    active_dims = [all_dims[d] for d in dimensions if d in all_dims]

    print(f"  Researching {len(active_dims)} dimensions...")

    # Research dimensions in parallel (batches of 3 to avoid rate limits)
    all_cards = []
    total_cost = 0.0
    evidence_count = 0

    for i in range(0, len(active_dims), 3):
        batch = active_dims[i : i + 3]
        tasks = []
        for dim in batch:
            prev = previous_findings.get(dim["id"], []) if isinstance(previous_findings, dict) else []
            tasks.append(research_dimension(target, dim, iteration, prev))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, Exception):
                all_cards.append({"status": "error", "error": str(r)})
            else:
                all_cards.append(r)
                total_cost += r.get("cost_usd", 0)
                evidence_count += len(r.get("findings", []))

    # Compile research result
    result = {
        "iteration": iteration,
        "target": target,
        "dimensions_researched": len(active_dims),
        "cards": all_cards,
        "evidence_count": evidence_count,
        "cost_usd": total_cost,
        "all_unknowns": [],
        "all_contradictions": [],
        "all_opportunities": [],
    }

    # Aggregate
    for card in all_cards:
        result["all_unknowns"].extend(card.get("unknowns", []))
        result["all_contradictions"].extend(card.get("contradictions", []))
        result["all_opportunities"].extend(card.get("opportunities_10x", []))

    # Save
    cards_path = output_dir / "research_cards.json"
    with open(cards_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Save evidence pack
    evidence = []
    for card in all_cards:
        for finding in card.get("findings", []):
            evidence.append(
                {
                    "dimension": card.get("dimension", "unknown"),
                    "finding": finding.get("finding", ""),
                    "confidence": finding.get("confidence", 0),
                    "source": finding.get("source", ""),
                }
            )

    evidence_path = output_dir / "evidence_pack.json"
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)

    return result
