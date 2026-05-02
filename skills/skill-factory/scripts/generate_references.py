#!/usr/bin/env python3.11
"""
generate_references.py — Genera los archivos de referencia de una skill.

Toma la arquitectura y el dossier de dominio, y usa GPT-5.4 para generar
los archivos de referencia (.md) definidos en la arquitectura.

Uso:
    python3.11 generate_references.py --spec spec.yaml --architecture arch.yaml \
        --dossier dossier.md --target /path/to/skill/references/
"""

import argparse
import asyncio
import sys
from pathlib import Path

import yaml

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

REFGEN_SYSTEM = """Eres un experto en documentación técnica. Generas archivos de referencia
para skills de Manus (un agente de IA autónomo).

REGLAS:
1. Formato Markdown limpio
2. Usar tablas para datos estructurados
3. Ser conciso pero completo
4. Incluir información verificable y actualizada
5. No repetir información que ya está en el SKILL.md
6. Cada referencia debe ser autosuficiente (no depender de otras)

Responde SOLO con el contenido Markdown, sin bloques de código envolventes."""


async def generate_single_reference(ref_detail: dict, spec: dict, dossier_excerpt: str) -> str:
    """Genera el contenido de un archivo de referencia."""

    prompt = f"""Genera el archivo de referencia para esta skill.

## Skill
Nombre: {spec.get("name")}
Dominio: {spec.get("domain")}
Descripción: {spec.get("description")}

## Referencia a Generar
Archivo: {ref_detail.get("filename")}
Propósito: {ref_detail.get("purpose")}
Secciones requeridas: {ref_detail.get("sections", [])}

## Contexto del Dominio (investigación en tiempo real)
{dossier_excerpt[:5000] if dossier_excerpt else "No hay dossier disponible."}

Genera el contenido completo del archivo de referencia. Responde SOLO con Markdown."""

    response = await consultar_sabio("gpt54", prompt, timeout=90)
    content = response.get("respuesta", "")

    # Limpiar markdown envolvente
    if content.startswith("```markdown"):
        content = content[len("```markdown") :].strip()
    if content.startswith("```"):
        content = content[3:].strip()
    if content.endswith("```"):
        content = content[:-3].strip()

    return content


async def main():
    parser = argparse.ArgumentParser(description="Genera los archivos de referencia de una skill")
    parser.add_argument("--spec", required=True, help="Path al skill_spec.yaml")
    parser.add_argument("--architecture", required=True, help="Path al architecture.yaml")
    parser.add_argument("--dossier", default=None, help="Path al dossier de dominio")
    parser.add_argument("--target", required=True, help="Directorio destino para las referencias")
    args = parser.parse_args()

    with open(args.spec, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    with open(args.architecture, "r", encoding="utf-8") as f:
        architecture = yaml.safe_load(f)

    dossier = ""
    if args.dossier and Path(args.dossier).exists():
        dossier = Path(args.dossier).read_text(encoding="utf-8")

    target = Path(args.target)
    target.mkdir(parents=True, exist_ok=True)

    refs = architecture.get("references_detail", [])

    if not refs:
        print("ℹ️ No hay referencias definidas en la arquitectura")
        return

    print(f"📚 Generando {len(refs)} referencias para: {spec.get('name')}")

    generated = 0
    errors = 0

    for i, ref_detail in enumerate(refs):
        filename = ref_detail.get("filename", f"reference_{i}.md")
        print(f"\n  [{i + 1}/{len(refs)}] Generando {filename}...")

        try:
            content = await generate_single_reference(ref_detail, spec, dossier)

            if not content.strip():
                print(f"    ❌ Contenido vacío para {filename}")
                errors += 1
                continue

            ref_path = target / filename
            ref_path.write_text(content, encoding="utf-8")
            generated += 1

            lines = len(content.split("\n"))
            print(f"    ✅ {filename}: {lines} líneas, {len(content):,} chars")

        except Exception as e:
            print(f"    ❌ Error generando {filename}: {e}")
            errors += 1

    print(f"\n{'=' * 50}")
    print(f"✅ Generadas: {generated}/{len(refs)} referencias")
    if errors:
        print(f"❌ Errores: {errors}")
    print(f"📁 Destino: {target}")


if __name__ == "__main__":
    asyncio.run(main())
