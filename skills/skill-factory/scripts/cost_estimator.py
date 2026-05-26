#!/usr/bin/env python3.11
"""
cost_estimator.py — Estima costos de API antes de ejecutar el pipeline.

Calcula tokens estimados y costo en USD para cada paso del pipeline,
permitiendo decidir si ejecutar o ajustar la profundidad.

Uso:
    python3.11 cost_estimator.py --spec spec.yaml --classification class.yaml
"""

import argparse
from pathlib import Path

import yaml

# Precios por 1M tokens (input/output) — Abril 2026
MODEL_PRICING = {
    "gpt54": {"input": 2.50, "output": 10.00, "name": "GPT-5.4"},
    "claude": {"input": 15.00, "output": 75.00, "name": "Claude Opus (via OpenRouter)"},
    "gemini": {"input": 1.25, "output": 5.00, "name": "Gemini 2.5 Pro"},
    "grok": {"input": 3.00, "output": 15.00, "name": "Grok 3"},
    "deepseek": {"input": 0.55, "output": 2.19, "name": "DeepSeek R1"},
    "perplexity": {"input": 1.00, "output": 5.00, "name": "Perplexity Sonar Pro"},
}

# Tokens estimados por paso del pipeline
PIPELINE_STEPS = {
    "intake": {"model": "gpt54", "input_tokens": 2000, "output_tokens": 1500},
    "classify": {"model": None, "input_tokens": 0, "output_tokens": 0},  # Local
    "research_topics": {"model": "gpt54", "input_tokens": 3000, "output_tokens": 2000},
    "research_execute": {"model": "perplexity", "input_tokens": 1500, "output_tokens": 3000, "multiplier": 8},
    "architecture": {"model": "gpt54", "input_tokens": 8000, "output_tokens": 5000},
    "generate_scripts": {"model": "gpt54", "input_tokens": 5000, "output_tokens": 8000, "multiplier": 6},
    "generate_refs": {"model": "gpt54", "input_tokens": 3000, "output_tokens": 4000, "multiplier": 3},
    "generate_skillmd": {"model": "gpt54", "input_tokens": 5000, "output_tokens": 3000},
    "validate_quality": {"model": "claude", "input_tokens": 15000, "output_tokens": 3000},
    "sabios_consultation": {"model": "all", "input_tokens": 20000, "output_tokens": 5000},
}

# Multiplicadores por complejidad
COMPLEXITY_MULTIPLIERS = {"minimal": 0.5, "standard": 1.0, "advanced": 1.5, "expert": 2.5}


def estimate_step_cost(step_name: str, step_config: dict, complexity: str) -> dict:
    """Estima el costo de un paso."""
    model = step_config.get("model")
    if model is None:
        return {"step": step_name, "model": "local", "cost_usd": 0, "tokens": 0}

    multiplier = COMPLEXITY_MULTIPLIERS.get(complexity, 1.0)
    step_multiplier = step_config.get("multiplier", 1)

    input_tokens = int(step_config["input_tokens"] * multiplier * step_multiplier)
    output_tokens = int(step_config["output_tokens"] * multiplier * step_multiplier)

    if model == "all":
        # Todos los sabios
        total_cost = 0
        for m, pricing in MODEL_PRICING.items():
            cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
            total_cost += cost
        return {
            "step": step_name,
            "model": "all_sabios",
            "input_tokens": input_tokens * 6,
            "output_tokens": output_tokens * 6,
            "cost_usd": round(total_cost, 4),
        }

    pricing = MODEL_PRICING.get(model, {"input": 5, "output": 15})
    cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000

    return {
        "step": step_name,
        "model": pricing.get("name", model),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 4),
    }


def estimate_total(spec: dict, classification: dict) -> dict:
    """Estima el costo total del pipeline."""
    complexity = classification.get("complexity_level", "standard")
    consult_sabios = spec.get("needs_sabios_consultation", False)
    regulated = spec.get("regulated", False)

    steps = []
    total_cost = 0
    total_input = 0
    total_output = 0

    for step_name, step_config in PIPELINE_STEPS.items():
        # Saltar sabios si no se requiere
        if step_name == "sabios_consultation" and not consult_sabios:
            continue

        estimate = estimate_step_cost(step_name, step_config, complexity)
        steps.append(estimate)
        total_cost += estimate["cost_usd"]
        total_input += estimate.get("input_tokens", 0)
        total_output += estimate.get("output_tokens", 0)

    # Agregar investigación regulatoria si es regulado
    if regulated:
        reg_cost = estimate_step_cost(
            "regulatory_research",
            {"model": "perplexity", "input_tokens": 2000, "output_tokens": 3000, "multiplier": 5},
            complexity,
        )
        steps.append(reg_cost)
        total_cost += reg_cost["cost_usd"]

    return {
        "complexity": complexity,
        "consult_sabios": consult_sabios,
        "regulated": regulated,
        "steps": steps,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_tokens": total_input + total_output,
        "total_cost_usd": round(total_cost, 4),
        "budget_category": "low" if total_cost < 0.10 else "medium" if total_cost < 0.50 else "high",
    }


def main():
    parser = argparse.ArgumentParser(description="Estima costos del pipeline")
    parser.add_argument("--spec", required=True, help="Path al skill_spec.yaml")
    parser.add_argument("--classification", required=True, help="Path al classification.yaml")
    parser.add_argument("--output", default=None, help="Path de salida")
    args = parser.parse_args()

    with open(args.spec, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    with open(args.classification, "r", encoding="utf-8") as f:
        classification = yaml.safe_load(f)

    print(f"💰 Estimando costos para: {spec.get('name')}")

    estimate = estimate_total(spec, classification)

    print(f"\n  Complejidad: {estimate['complexity']}")
    print(f"  Tokens totales: {estimate['total_tokens']:,}")
    print(f"  Costo estimado: ${estimate['total_cost_usd']:.4f} USD")
    print(f"  Categoría: {estimate['budget_category']}")

    print("\n  Desglose por paso:")
    for step in estimate["steps"]:
        if step["cost_usd"] > 0:
            print(f"    {step['step']}: ${step['cost_usd']:.4f} ({step['model']})")

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(estimate, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"\n📁 Estimación guardada en: {args.output}")


if __name__ == "__main__":
    main()
