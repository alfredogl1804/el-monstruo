#!/usr/bin/env python3.11
"""
run_experiments.py — Motor de Experimentación A/B
==================================================
Ejecuta experimentos controlados para validar mejoras propuestas.
Compara configuración actual vs propuesta midiendo scores.

Uso:
    python3.11 run_experiments.py --improvement-id imp_abc123 --prompt test_prompt.md

Creado: 2026-04-08 (P2 auditoría sabios)
"""

import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_store import query_improvements, save_improvement


async def run_experiment(
    improvement_id: str,
    test_prompt: str,
    n_runs: int = 2,
) -> dict:
    """
    Ejecuta un experimento A/B para una mejora propuesta.
    
    Args:
        improvement_id: ID de la mejora a probar
        test_prompt: Ruta al prompt de prueba
        n_runs: Número de runs por variante (A=control, B=experimental)
    
    Returns:
        dict con resultados del experimento
    """
    # Buscar la mejora
    improvements = query_improvements()
    target = None
    for imp in improvements:
        if imp.get("improvement_id") == improvement_id:
            target = imp
            break
    
    if not target:
        print(f"❌ Mejora {improvement_id} no encontrada")
        return {"error": "improvement_not_found"}

    print(f"🧪 Experimento para: {target['descripcion']}")
    print(f"   Tipo: {target['tipo']}")
    print(f"   Runs por variante: {n_runs}")

    experiment = {
        "experiment_id": f"exp_{uuid.uuid4().hex[:8]}",
        "improvement_id": improvement_id,
        "timestamp": datetime.now().isoformat(),
        "descripcion": target["descripcion"],
        "n_runs": n_runs,
        "resultados_control": [],
        "resultados_experimental": [],
        "veredicto": "pendiente",
    }

    # En esta versión, el experimento se registra como framework.
    # La ejecución real requiere que el agente ejecute runs manuales
    # con y sin la mejora aplicada, y registre los scores.
    
    print(f"\n📋 Protocolo de experimento {experiment['experiment_id']}:")
    print(f"   1. Ejecutar {n_runs} runs con configuración ACTUAL (control)")
    print(f"   2. Aplicar la mejora temporalmente")
    print(f"   3. Ejecutar {n_runs} runs con configuración MODIFICADA (experimental)")
    print(f"   4. Comparar scores y decidir")
    print(f"\n   Mejora a probar: {target['descripcion']}")
    print(f"   Diff: {target.get('diff_json', target.get('diff', 'N/A'))}")

    # Guardar el experimento como artefacto
    output_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent / "data" / "experiments"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    exp_file = output_dir / f"{experiment['experiment_id']}.json"
    with open(exp_file, "w", encoding="utf-8") as f:
        json.dump(experiment, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n📁 Experimento registrado: {exp_file}")
    return experiment


def record_experiment_result(
    experiment_id: str,
    variant: str,  # "control" o "experimental"
    run_id: str,
    score_global: float,
    scores_detail: dict = None,
):
    """
    Registra el resultado de un run dentro de un experimento.
    
    Args:
        experiment_id: ID del experimento
        variant: "control" o "experimental"
        run_id: ID del run ejecutado
        score_global: Score global del run
        scores_detail: Scores detallados opcionales
    """
    exp_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent / "data" / "experiments"
    exp_file = exp_dir / f"{experiment_id}.json"
    
    if not exp_file.exists():
        print(f"❌ Experimento {experiment_id} no encontrado")
        return
    
    with open(exp_file, "r", encoding="utf-8") as f:
        experiment = json.load(f)
    
    result = {
        "run_id": run_id,
        "score_global": score_global,
        "scores_detail": scores_detail or {},
        "timestamp": datetime.now().isoformat(),
    }
    
    key = f"resultados_{variant}"
    if key not in experiment:
        experiment[key] = []
    experiment[key].append(result)
    
    # Evaluar si el experimento está completo
    n_runs = experiment.get("n_runs", 2)
    control_done = len(experiment.get("resultados_control", []))
    exp_done = len(experiment.get("resultados_experimental", []))
    
    if control_done >= n_runs and exp_done >= n_runs:
        experiment["veredicto"] = _evaluate_experiment(experiment)
    
    with open(exp_file, "w", encoding="utf-8") as f:
        json.dump(experiment, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ Resultado registrado: {variant} run {run_id} (score: {score_global})")
    if experiment["veredicto"] != "pendiente":
        print(f"🏁 Veredicto: {experiment['veredicto']}")


def _evaluate_experiment(experiment: dict) -> str:
    """Evalúa los resultados de un experimento completado."""
    control_scores = [r["score_global"] for r in experiment.get("resultados_control", [])]
    exp_scores = [r["score_global"] for r in experiment.get("resultados_experimental", [])]
    
    if not control_scores or not exp_scores:
        return "insuficiente"
    
    from statistics import mean
    control_mean = mean(control_scores)
    exp_mean = mean(exp_scores)
    
    delta = exp_mean - control_mean
    delta_pct = (delta / control_mean * 100) if control_mean > 0 else 0
    
    experiment["analisis"] = {
        "control_mean": round(control_mean, 3),
        "experimental_mean": round(exp_mean, 3),
        "delta": round(delta, 3),
        "delta_pct": round(delta_pct, 1),
    }
    
    # Criterios de aceptación:
    # - Mejora >= 5% → aceptar
    # - Neutro (-2% a +5%) → rechazar (no vale la complejidad)
    # - Degradación > 2% → rechazar
    if delta_pct >= 5:
        return "aceptar"
    elif delta_pct <= -2:
        return "rechazar_degradacion"
    else:
        return "rechazar_neutro"


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

async def main():
    parser = argparse.ArgumentParser(description="Motor de experimentación A/B")
    parser.add_argument("--improvement-id", required=True)
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--n-runs", type=int, default=2)

    args = parser.parse_args()
    await run_experiment(args.improvement_id, args.prompt, args.n_runs)


if __name__ == "__main__":
    asyncio.run(main())
