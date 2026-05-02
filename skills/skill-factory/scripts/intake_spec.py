#!/usr/bin/env python3.11
"""
intake_spec.py — Captura y estructura la especificación de una skill.

Toma una descripción en lenguaje natural (o un archivo) y usa GPT-5.4
para extraer una especificación estructurada en YAML.

Uso:
    python3.11 intake_spec.py --input "Descripción de la skill" --output spec.yaml
    python3.11 intake_spec.py --input /path/to/description.md --output spec.yaml
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

SYSTEM_PROMPT = """Eres un arquitecto de skills de IA. Tu trabajo es tomar una descripción
ambigua de una skill y producir una especificación estructurada completa.

Responde SOLO con un bloque JSON válido (sin markdown, sin explicaciones) con esta estructura exacta:

{
  "name": "nombre-de-la-skill (kebab-case)",
  "title": "Título Legible de la Skill",
  "description": "Descripción concisa de qué hace y cuándo usarla (1-2 oraciones)",
  "domain": "software|research|legal|finance|health|education|marketing|operations|creative|general",
  "subdomain": "subdomain específico si aplica",
  "target_user": "quién usará esta skill",
  "core_capabilities": ["lista de capacidades principales"],
  "inputs": ["qué recibe la skill como entrada"],
  "outputs": ["qué produce la skill como salida"],
  "apis_needed": ["APIs externas que probablemente necesite"],
  "mcps_needed": ["MCPs que probablemente necesite"],
  "tools_needed": ["herramientas CLI o sandbox que necesite"],
  "data_sensitivity": "bajo|medio|alto|critico",
  "jurisdiction": "MX|US|EU|global|NA",
  "regulated": false,
  "regulatory_frameworks": ["marcos regulatorios aplicables si regulated=true"],
  "similar_skills": ["skills existentes que podrían reutilizarse parcialmente"],
  "success_criteria": ["criterios medibles de éxito"],
  "constraints": ["restricciones o limitaciones conocidas"],
  "estimated_scripts": 5,
  "estimated_references": 3,
  "needs_templates": false,
  "needs_database": false,
  "needs_realtime_research": false,
  "needs_sabios_consultation": false
}

Sé preciso y concreto. Si algo no aplica, usa null o lista vacía.
Infiere lo que puedas razonablemente de la descripción.
Si el dominio es regulado (salud, finanzas, legal), SIEMPRE marca regulated=true."""


async def generate_spec(description: str) -> dict:
    """Genera la especificación estructurada usando GPT-5.4."""
    prompt = f"""Analiza esta descripción de skill y genera la especificación estructurada:

---
{description}
---

Responde SOLO con el JSON estructurado."""

    response = await consultar_sabio("gpt54", prompt, system_prompt=SYSTEM_PROMPT)

    # Extraer JSON de la respuesta
    text = response.get("respuesta", "")

    # Intentar parsear directamente
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Buscar bloque JSON en la respuesta
    import re

    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No se pudo extraer JSON de la respuesta:\n{text[:500]}")


def enrich_spec(spec: dict) -> dict:
    """Enriquece la spec con valores por defecto y validaciones."""

    # Asegurar campos obligatorios
    required = ["name", "title", "description", "domain"]
    for field in required:
        if not spec.get(field):
            raise ValueError(f"Campo obligatorio faltante: {field}")

    # Normalizar nombre
    spec["name"] = spec["name"].lower().replace(" ", "-").replace("_", "-")

    # Defaults
    spec.setdefault("subdomain", None)
    spec.setdefault("target_user", "Manus agent")
    spec.setdefault("core_capabilities", [])
    spec.setdefault("inputs", [])
    spec.setdefault("outputs", [])
    spec.setdefault("apis_needed", [])
    spec.setdefault("mcps_needed", [])
    spec.setdefault("tools_needed", [])
    spec.setdefault("data_sensitivity", "bajo")
    spec.setdefault("jurisdiction", "NA")
    spec.setdefault("regulated", False)
    spec.setdefault("regulatory_frameworks", [])
    spec.setdefault("similar_skills", [])
    spec.setdefault("success_criteria", [])
    spec.setdefault("constraints", [])
    spec.setdefault("estimated_scripts", 3)
    spec.setdefault("estimated_references", 1)
    spec.setdefault("needs_templates", False)
    spec.setdefault("needs_database", False)
    spec.setdefault("needs_realtime_research", False)
    spec.setdefault("needs_sabios_consultation", False)

    # Auto-inferencias
    regulated_domains = {"legal", "finance", "health"}
    if spec["domain"] in regulated_domains:
        spec["regulated"] = True
        if spec["data_sensitivity"] in ("bajo", "medio"):
            spec["data_sensitivity"] = "alto"

    if spec["regulated"] and not spec["needs_realtime_research"]:
        spec["needs_realtime_research"] = True

    if spec.get("estimated_scripts", 0) > 15:
        spec["needs_sabios_consultation"] = True

    return spec


async def main():
    parser = argparse.ArgumentParser(description="Genera especificación estructurada de una skill")
    parser.add_argument("--input", required=True, help="Descripción de la skill (texto o path a archivo)")
    parser.add_argument("--output", required=True, help="Path de salida para el spec YAML")
    args = parser.parse_args()

    # Leer input
    input_path = Path(args.input)
    if input_path.exists():
        description = input_path.read_text(encoding="utf-8")
        print(f"📄 Leyendo descripción desde: {args.input}")
    else:
        description = args.input
        print(f"📝 Usando descripción directa ({len(description)} chars)")

    # Generar spec
    print("🤖 GPT-5.4 analizando descripción y generando especificación...")
    spec = await generate_spec(description)

    # Enriquecer
    spec = enrich_spec(spec)
    print(f"✅ Especificación generada: {spec['name']} ({spec['domain']})")

    # Guardar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"📁 Guardada en: {args.output}")

    # Resumen
    print("\n--- Resumen ---")
    print(f"  Nombre: {spec['name']}")
    print(f"  Dominio: {spec['domain']}")
    print(f"  Sensibilidad: {spec['data_sensitivity']}")
    print(f"  Regulado: {'Sí' if spec['regulated'] else 'No'}")
    print(f"  Scripts estimados: {spec['estimated_scripts']}")
    print(f"  Necesita investigación: {'Sí' if spec['needs_realtime_research'] else 'No'}")
    print(f"  Necesita sabios: {'Sí' if spec['needs_sabios_consultation'] else 'No'}")


if __name__ == "__main__":
    asyncio.run(main())
