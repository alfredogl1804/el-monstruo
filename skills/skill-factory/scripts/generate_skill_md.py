#!/usr/bin/env python3.11
"""
generate_skill_md.py — Genera el SKILL.md para una skill.

Toma la spec, arquitectura y dossier, y usa GPT-5.4 para generar
un SKILL.md completo con frontmatter YAML válido.

Uso:
    python3.11 generate_skill_md.py --spec spec.yaml --architecture arch.yaml \
        --output /path/to/skill/SKILL.md
"""

import argparse
import asyncio
import sys
from pathlib import Path

import yaml

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

MAX_SKILL_MD_LINES = 450  # Dejar margen bajo el límite de 500


async def generate_skill_md(spec: dict, architecture: dict) -> str:
    """Genera el contenido del SKILL.md usando GPT-5.4."""

    # Preparar resumen de scripts
    scripts_summary = ""
    for s in architecture.get("scripts_detail", []):
        scripts_summary += f"- {s['filename']}: {s['purpose']}\n"

    # Preparar flujo
    flow_summary = ""
    for step in architecture.get("execution_flow", []):
        flow_summary += f"{step['step']}. {step['script']}: {step['description']}\n"

    prompt = f"""Genera el SKILL.md para esta skill. REGLAS ESTRICTAS:

1. DEBE empezar con frontmatter YAML:
---
name: {spec.get("name")}
description: {spec.get("description")}
---

2. Máximo {MAX_SKILL_MD_LINES} líneas totales (incluyendo frontmatter)
3. NO incluir README, CHANGELOG ni secciones innecesarias
4. Usar tablas para listas de scripts y configuración
5. Incluir ejemplo de uso del entrypoint
6. Ser conciso pero completo — progressive disclosure (detalles en references/)

## Información de la Skill

Nombre: {spec.get("name")}
Título: {spec.get("title")}
Descripción: {spec.get("description")}
Dominio: {spec.get("domain")}
Regulado: {spec.get("regulated", False)}
Sensibilidad: {spec.get("data_sensitivity", "bajo")}

## Scripts
{scripts_summary}

## Flujo de Ejecución
{flow_summary}

## Entrypoint
{architecture.get("entrypoint", "N/A")}

## Secciones requeridas en SKILL.md
{architecture.get("skill_md_sections", ["Uso", "Scripts", "Configuración"])}

## APIs necesarias
{spec.get("apis_needed", [])}

## Credenciales
Las variables de entorno disponibles son: OPENAI_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY, 
XAI_API_KEY, SONAR_API_KEY, ELEVENLABS_API_KEY, HEYGEN_API_KEY, DROPBOX_API_KEY, 
CLOUDFLARE_API_TOKEN, ANTHROPIC_API_KEY

Genera el SKILL.md completo. Responde SOLO con el contenido del archivo, empezando por ---"""

    response = await consultar_sabio("gpt54", prompt, timeout=90)
    text = response.get("respuesta", "")

    # Asegurar que empieza con frontmatter
    if not text.strip().startswith("---"):
        text = f"""---
name: {spec.get("name")}
description: {spec.get("description")}
---

{text}"""

    # Validar que el frontmatter cierra
    parts = text.split("---")
    if len(parts) < 3:
        # Frontmatter mal formado, reconstruir
        text = f"""---
name: {spec.get("name")}
description: {spec.get("description")}
---

{text}"""

    # Truncar si excede límite
    lines = text.split("\n")
    if len(lines) > MAX_SKILL_MD_LINES:
        lines = lines[:MAX_SKILL_MD_LINES]
        text = "\n".join(lines)

    return text


def validate_skill_md(content: str) -> list:
    """Valida el SKILL.md generado."""
    issues = []

    lines = content.split("\n")

    # Verificar frontmatter
    if not content.strip().startswith("---"):
        issues.append("CRITICAL: Falta frontmatter YAML al inicio")
    else:
        # Verificar que hay name y description
        fm_end = content.find("---", 4)
        if fm_end == -1:
            issues.append("CRITICAL: Frontmatter no cierra con ---")
        else:
            fm = content[3:fm_end]
            if "name:" not in fm:
                issues.append("CRITICAL: Falta 'name' en frontmatter")
            if "description:" not in fm:
                issues.append("CRITICAL: Falta 'description' en frontmatter")

    # Verificar longitud
    if len(lines) > 500:
        issues.append(f"WARNING: SKILL.md tiene {len(lines)} líneas (máximo 500)")

    # Verificar que no tiene secciones prohibidas
    prohibited = ["# README", "# CHANGELOG", "# LICENSE"]
    for p in prohibited:
        if p.lower() in content.lower():
            issues.append(f"WARNING: Contiene sección prohibida: {p}")

    return issues


async def main():
    parser = argparse.ArgumentParser(description="Genera el SKILL.md de una skill")
    parser.add_argument("--spec", required=True, help="Path al skill_spec.yaml")
    parser.add_argument("--architecture", required=True, help="Path al architecture.yaml")
    parser.add_argument("--output", required=True, help="Path de salida para SKILL.md")
    args = parser.parse_args()

    with open(args.spec, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    with open(args.architecture, "r", encoding="utf-8") as f:
        architecture = yaml.safe_load(f)

    print(f"📝 Generando SKILL.md para: {spec.get('name')}")

    content = await generate_skill_md(spec, architecture)

    # Validar
    issues = validate_skill_md(content)
    if issues:
        print("⚠️ Issues encontrados:")
        for issue in issues:
            print(f"   {issue}")

    # Guardar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    lines = content.split("\n")
    print(f"✅ SKILL.md generado: {len(lines)} líneas, {len(content):,} chars")
    print(f"📁 Guardado en: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
