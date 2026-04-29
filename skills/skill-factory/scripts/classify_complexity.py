#!/usr/bin/env python3.11
"""
classify_complexity.py — Clasifica la complejidad de una skill.

Lee el skill_spec.yaml y calcula un score de complejidad basado en
10 dimensiones definidas en complexity-rubric.md.

Uso:
    python3.11 classify_complexity.py --spec spec.yaml --output classification.yaml
"""

import argparse, yaml, sys
from pathlib import Path

RUBRIC_PATH = Path(__file__).parent.parent / "references" / "complexity-rubric.md"

def classify(spec: dict) -> dict:
    """Calcula el score de complejidad basado en 10 dimensiones."""
    
    scores = {}
    
    # 1. api_count
    api_count = len(spec.get("apis_needed", []))
    scores["api_count"] = min(1.0, api_count / 3.0) if api_count > 0 else 0.0
    
    # 2. state_mgmt
    if spec.get("needs_database"):
        scores["state_mgmt"] = 1.0
    elif spec.get("estimated_references", 0) > 3:
        scores["state_mgmt"] = 0.5
    else:
        scores["state_mgmt"] = 0.0
    
    # 3. domain_depth
    regulated_domains = {"legal", "finance", "health"}
    if spec.get("regulated") and spec.get("domain") in regulated_domains:
        scores["domain_depth"] = 1.0
    elif spec.get("domain") != "general":
        scores["domain_depth"] = 0.5
    else:
        scores["domain_depth"] = 0.0
    
    # 4. error_handling (inferido de complejidad general)
    est_scripts = spec.get("estimated_scripts", 1)
    if est_scripts > 15:
        scores["error_handling"] = 1.0
    elif est_scripts > 5:
        scores["error_handling"] = 0.5
    else:
        scores["error_handling"] = 0.2
    
    # 5. validation
    if spec.get("needs_sabios_consultation"):
        scores["validation"] = 1.0
    elif spec.get("regulated"):
        scores["validation"] = 0.8
    elif est_scripts > 5:
        scores["validation"] = 0.5
    else:
        scores["validation"] = 0.2
    
    # 6. research_needed
    if spec.get("needs_realtime_research") and spec.get("regulated"):
        scores["research_needed"] = 1.0
    elif spec.get("needs_realtime_research"):
        scores["research_needed"] = 0.7
    elif spec.get("domain") != "general":
        scores["research_needed"] = 0.3
    else:
        scores["research_needed"] = 0.0
    
    # 7. script_count
    if est_scripts >= 9:
        scores["script_count"] = 1.0
    elif est_scripts >= 3:
        scores["script_count"] = 0.5
    else:
        scores["script_count"] = 0.2
    
    # 8. integration_count
    mcps = len(spec.get("mcps_needed", []))
    tools = len(spec.get("tools_needed", []))
    total_integrations = mcps + tools
    if total_integrations >= 4:
        scores["integration_count"] = 1.0
    elif total_integrations >= 1:
        scores["integration_count"] = 0.5
    else:
        scores["integration_count"] = 0.0
    
    # 9. compliance
    sensitivity = spec.get("data_sensitivity", "bajo")
    sensitivity_map = {"bajo": 0.0, "medio": 0.3, "alto": 0.7, "critico": 1.0}
    scores["compliance"] = sensitivity_map.get(sensitivity, 0.0)
    
    # 10. improvement_cycle
    if spec.get("needs_sabios_consultation") and spec.get("needs_database"):
        scores["improvement_cycle"] = 1.0
    elif spec.get("needs_database"):
        scores["improvement_cycle"] = 0.5
    else:
        scores["improvement_cycle"] = 0.1
    
    # Calcular score total
    total = sum(scores.values()) / len(scores) * 10
    
    # Determinar nivel
    if total >= 7:
        level = "advanced" if total < 9.5 else "expert"
    elif total >= 4:
        level = "standard"
    else:
        level = "minimal"
    
    # Determinar template
    template_map = {
        "minimal": "skill_minimal",
        "standard": "skill_standard",
        "advanced": "skill_advanced",
        "expert": "skill_advanced"
    }
    
    return {
        "complexity_score": round(total, 2),
        "complexity_level": level,
        "template": template_map[level],
        "dimensions": {k: round(v, 2) for k, v in scores.items()},
        "recommendations": generate_recommendations(level, scores, spec)
    }


def generate_recommendations(level: str, scores: dict, spec: dict) -> list:
    """Genera recomendaciones basadas en la clasificación."""
    recs = []
    
    if level in ("advanced", "expert"):
        recs.append("Usar investigación de dominio profunda antes de generar")
        recs.append("Implementar quality gate multidimensional")
    
    if level == "expert":
        recs.append("Consultar a los sabios para diseño arquitectónico")
        recs.append("Implementar ciclo de mejora perpetua")
    
    if scores.get("compliance", 0) > 0.5:
        recs.append("Ejecutar research_regulatory.py antes de generar")
        recs.append("Implementar redacción de PII")
        recs.append("Documentar transferencias a APIs de terceros")
    
    if scores.get("api_count", 0) > 0.5:
        recs.append("Implementar fallback policy para APIs externas")
        recs.append("Usar conector_sabios.py si usa APIs de IA")
    
    if scores.get("research_needed", 0) > 0.5:
        recs.append("Investigar estado del arte del dominio antes de diseñar")
    
    if not recs:
        recs.append("Skill simple — generar directamente con template minimal")
    
    return recs


def main():
    parser = argparse.ArgumentParser(description="Clasifica la complejidad de una skill")
    parser.add_argument("--spec", required=True, help="Path al skill_spec.yaml")
    parser.add_argument("--output", required=True, help="Path de salida para classification.yaml")
    args = parser.parse_args()
    
    # Leer spec
    with open(args.spec, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    
    print(f"📊 Clasificando complejidad de: {spec.get('name', 'unknown')}")
    
    # Clasificar
    classification = classify(spec)
    
    # Guardar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(classification, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Complejidad: {classification['complexity_level']} (score: {classification['complexity_score']}/10)")
    print(f"📁 Template recomendado: {classification['template']}")
    print(f"📋 Recomendaciones:")
    for r in classification['recommendations']:
        print(f"   → {r}")
    print(f"📁 Guardado en: {args.output}")

if __name__ == "__main__":
    main()
