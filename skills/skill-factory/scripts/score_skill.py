#!/usr/bin/env python3.11
"""
score_skill.py — Scoring final de una skill combinando estructura y calidad.

Combina los reportes de validate_structure y validate_quality para
producir un score final y un veredicto de entrega.

Uso:
    python3.11 score_skill.py --structure report.yaml --quality quality.yaml --output score.yaml
"""

import argparse
import sys
from pathlib import Path

import yaml


def calculate_final_score(structure: dict, quality: dict) -> dict:
    """Calcula el score final combinando estructura y calidad."""

    # Score de estructura (peso 30%)
    struct_score = structure.get("scores", {}).get("score", 0)
    struct_verdict = structure.get("scores", {}).get("verdict", "FAIL")

    # Score de calidad (peso 70%)
    quality_score = quality.get("global_score", 0)
    quality_grade = quality.get("grade", "Error")

    # Score combinado
    final_score = round(struct_score * 0.3 + quality_score * 0.7, 1)

    # Veredicto final
    if struct_verdict == "FAIL":
        verdict = "BLOCKED"
        action = "Corregir errores críticos de estructura antes de entregar"
    elif final_score >= 90:
        verdict = "EXCELLENT"
        action = "Entregar y registrar como patrón reutilizable"
    elif final_score >= 75:
        verdict = "GOOD"
        action = "Entregar con warnings documentados"
    elif final_score >= 60:
        verdict = "ACCEPTABLE"
        action = "Requiere revisión manual antes de entregar"
    else:
        verdict = "REJECTED"
        action = "Bloquear entrega, iterar y mejorar"

    # Compilar dimensiones
    dimensions = {}
    quality_dims = quality.get("dimensions", {})
    for dim_name, dim_data in quality_dims.items():
        if isinstance(dim_data, dict):
            dimensions[dim_name] = {"score": dim_data.get("score", 0), "reasoning": dim_data.get("reasoning", "")}
        else:
            dimensions[dim_name] = {"score": dim_data, "reasoning": ""}

    return {
        "final_score": final_score,
        "verdict": verdict,
        "action": action,
        "breakdown": {
            "structure_score": struct_score,
            "structure_weight": 0.3,
            "structure_verdict": struct_verdict,
            "quality_score": quality_score,
            "quality_weight": 0.7,
            "quality_grade": quality_grade,
        },
        "dimensions": dimensions,
        "strengths": quality.get("top_strengths", []),
        "weaknesses": quality.get("top_weaknesses", []),
        "critical_fixes": quality.get("critical_fixes", []),
        "improvement_suggestions": quality.get("improvement_suggestions", []),
        "structure_issues": structure.get("issues", []),
        "deliverable": verdict in ("EXCELLENT", "GOOD"),
    }


def main():
    parser = argparse.ArgumentParser(description="Scoring final de una skill")
    parser.add_argument("--structure", required=True, help="Path al reporte de estructura")
    parser.add_argument("--quality", required=True, help="Path al reporte de calidad")
    parser.add_argument("--output", required=True, help="Path de salida para el score final")
    args = parser.parse_args()

    with open(args.structure, "r", encoding="utf-8") as f:
        structure = yaml.safe_load(f)

    with open(args.quality, "r", encoding="utf-8") as f:
        quality = yaml.safe_load(f)

    print("📊 Calculando score final...")

    result = calculate_final_score(structure, quality)

    # Guardar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(result, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # Imprimir
    print(f"\n{'=' * 50}")
    print(f"  SCORE FINAL: {result['final_score']}/100")
    print(f"  VEREDICTO: {result['verdict']}")
    print(f"  ACCIÓN: {result['action']}")
    print(f"  ENTREGABLE: {'Sí' if result['deliverable'] else 'No'}")
    print("\n  Desglose:")
    print(f"    Estructura: {result['breakdown']['structure_score']}/100 (peso 30%)")
    print(f"    Calidad:    {result['breakdown']['quality_score']}/100 (peso 70%)")

    if result["critical_fixes"]:
        print("\n  ❌ Fixes Críticos:")
        for fix in result["critical_fixes"]:
            print(f"     {fix}")

    print(f"\n📁 Score guardado en: {args.output}")

    sys.exit(0 if result["deliverable"] else 1)


if __name__ == "__main__":
    main()
