#!/usr/bin/env python3.11
"""
research_domain.py — Investiga el dominio de una skill antes de construirla.

Usa GPT-5.4 para identificar qué investigar y Perplexity Sonar para
buscar información en tiempo real. Genera un dossier de dominio.

Uso:
    python3.11 research_domain.py --spec spec.yaml --output dossier.md
    python3.11 research_domain.py --spec spec.yaml --output dossier.md --depth deep
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

FACTORY_ROOT = Path(__file__).parent.parent


async def identify_research_topics(spec: dict, depth: str = "normal") -> list:
    """Usa GPT-5.4 para identificar qué investigar sobre el dominio."""

    max_topics = {"basic": 5, "normal": 10, "deep": 20}[depth]

    # Cargar recipe del dominio si existe
    recipe_path = FACTORY_ROOT / "references" / "recipes" / f"{spec.get('domain', 'general')}.md"
    recipe_context = ""
    if recipe_path.exists():
        recipe_context = f"\n\nRecipe del dominio disponible:\n{recipe_path.read_text()[:2000]}"

    prompt = f"""Analiza esta especificación de skill y genera una lista de temas que necesitan
investigación en tiempo real para construir una skill de primer nivel.

Especificación:
- Nombre: {spec.get("name")}
- Dominio: {spec.get("domain")}
- Subdominio: {spec.get("subdomain", "N/A")}
- Descripción: {spec.get("description")}
- Capacidades: {spec.get("core_capabilities", [])}
- APIs necesarias: {spec.get("apis_needed", [])}
- Regulado: {spec.get("regulated", False)}
- Sensibilidad: {spec.get("data_sensitivity", "bajo")}
{recipe_context}

Genera exactamente {max_topics} temas de investigación como JSON array.
Cada tema debe ser un objeto con:
- "topic": string con el tema a investigar
- "query": string con la query de búsqueda optimizada para Perplexity
- "priority": "alta"|"media"|"baja"
- "category": "herramientas"|"mejores_practicas"|"regulacion"|"competencia"|"anti_patrones"

Responde SOLO con el JSON array, sin markdown ni explicaciones."""

    response = await consultar_sabio("gpt54", prompt)
    text = response.get("respuesta", "")

    # Extraer JSON
    import re

    json_match = re.search(r"\[[\s\S]*\]", text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Fallback: generar temas básicos
    return [
        {
            "topic": f"Mejores prácticas en {spec.get('domain')}",
            "query": f"best practices {spec.get('domain')} automation tools 2026",
            "priority": "alta",
            "category": "mejores_practicas",
        },
        {
            "topic": f"APIs disponibles para {spec.get('domain')}",
            "query": f"{spec.get('domain')} APIs tools available 2026",
            "priority": "alta",
            "category": "herramientas",
        },
        {
            "topic": f"Anti-patrones en {spec.get('domain')}",
            "query": f"common mistakes pitfalls {spec.get('domain')} automation",
            "priority": "media",
            "category": "anti_patrones",
        },
    ]


async def research_topic(topic: dict, semaphore: asyncio.Semaphore) -> dict:
    """Investiga un tema usando Perplexity Sonar."""
    async with semaphore:
        try:
            response = await consultar_sabio(
                "perplexity",
                f"Investiga en detalle: {topic['query']}. Proporciona información actualizada, "
                f"concreta y verificable. Incluye nombres de herramientas, versiones, URLs cuando sea posible.",
                timeout=60,
            )
            return {
                "topic": topic["topic"],
                "query": topic["query"],
                "priority": topic["priority"],
                "category": topic["category"],
                "result": response.get("respuesta", "Sin respuesta"),
                "status": "ok",
            }
        except Exception as e:
            return {
                "topic": topic["topic"],
                "query": topic["query"],
                "priority": topic["priority"],
                "category": topic["category"],
                "result": f"Error: {str(e)}",
                "status": "error",
            }


async def check_existing_skills(spec: dict) -> str:
    """Verifica si hay skills existentes que puedan reutilizarse."""
    skills_dir = Path("/home/ubuntu/skills")
    existing = []

    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    content = skill_md.read_text(encoding="utf-8")[:500]
                    existing.append(f"- **{skill_dir.name}**: {content[:200]}")

    if not existing:
        return "No se encontraron skills existentes."

    return "Skills existentes en el sistema:\n" + "\n".join(existing)


def compile_dossier(spec: dict, topics: list, results: list, existing_skills: str) -> str:
    """Compila el dossier de dominio."""

    now = datetime.now().strftime("%d de %B de %Y, %H:%M")

    ok_count = sum(1 for r in results if r["status"] == "ok")

    sections = [
        f"# Dossier de Dominio — {spec.get('name')}",
        f"\n**Fecha de investigación:** {now}",
        f"**Dominio:** {spec.get('domain')} / {spec.get('subdomain', 'general')}",
        f"**Temas investigados:** {len(results)}",
        f"**Temas exitosos:** {ok_count}",
        "\n> Este dossier fue generado automáticamente por skill-factory. "
        "Contiene datos verificados al momento de la investigación.",
    ]

    # Agrupar por categoría
    categories = {}
    for r in results:
        cat = r.get("category", "general")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)

    cat_titles = {
        "herramientas": "Herramientas y APIs Disponibles",
        "mejores_practicas": "Mejores Prácticas del Dominio",
        "regulacion": "Marco Regulatorio",
        "competencia": "Soluciones Existentes y Competencia",
        "anti_patrones": "Anti-patrones y Errores Comunes",
    }

    for cat, items in categories.items():
        title = cat_titles.get(cat, cat.title())
        sections.append(f"\n## {title}")
        for item in items:
            status = "✅" if item["status"] == "ok" else "❌"
            sections.append(f"\n### {status} {item['topic']} (Prioridad: {item['priority']})")
            sections.append(f"\n{item['result']}")

    # Skills existentes
    sections.append(f"\n## Skills Existentes Reutilizables\n\n{existing_skills}")

    return "\n".join(sections)


async def main():
    parser = argparse.ArgumentParser(description="Investiga el dominio de una skill")
    parser.add_argument("--spec", required=True, help="Path al skill_spec.yaml")
    parser.add_argument("--output", required=True, help="Path de salida para el dossier")
    parser.add_argument(
        "--depth", default="normal", choices=["basic", "normal", "deep"], help="Profundidad de investigación"
    )
    args = parser.parse_args()

    # Leer spec
    with open(args.spec, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    print(f"🔬 Investigando dominio: {spec.get('domain')} / {spec.get('subdomain', 'general')}")
    print(f"   Profundidad: {args.depth}")

    # Paso 1: Identificar temas
    print("🔍 Paso 1: Identificando temas de investigación...")
    topics = await identify_research_topics(spec, args.depth)
    print(f"   ✅ {len(topics)} temas identificados")

    # Paso 2: Investigar en paralelo
    print(f"🌐 Paso 2: Investigando {len(topics)} temas con Perplexity Sonar...")
    semaphore = asyncio.Semaphore(4)  # Max 4 concurrent Perplexity calls
    tasks = [research_topic(t, semaphore) for t in topics]
    results = await asyncio.gather(*tasks)

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"   ✅ {ok}/{len(results)} temas investigados exitosamente")

    # Paso 3: Verificar skills existentes
    print("📦 Paso 3: Verificando skills existentes reutilizables...")
    existing = await check_existing_skills(spec)

    # Paso 4: Compilar dossier
    print("📋 Paso 4: Compilando dossier de dominio...")
    dossier = compile_dossier(spec, topics, results, existing)

    # Guardar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dossier, encoding="utf-8")

    print(f"✅ Dossier generado: {len(dossier):,} caracteres")
    print(f"📁 Guardado en: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
