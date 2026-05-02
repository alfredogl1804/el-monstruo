#!/usr/bin/env python3.11
"""
Módulo 3: Benchmark Research
Investiga los mejores proyectos de referencia del mundo que aplican
para el terreno y tipo de proyecto específico.

Fuentes:
- Perplexity Sonar (investigación en tiempo real)
- GPT-5.4 (análisis y síntesis)
- Búsqueda web de Manus (imágenes de referencia)

Salida: benchmarks.md con análisis de casos + benchmarks_data.yaml
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio


async def identify_benchmark_categories(brief: dict, site_report: str) -> list:
    """GPT-5.4 identifica las categorías de benchmarks relevantes."""

    prompt = f"""Eres un consultor inmobiliario de clase mundial. Analiza este proyecto y determina 
qué categorías de benchmarks internacionales son relevantes.

## Project Brief
```yaml
{yaml.dump(brief, default_flow_style=False, allow_unicode=True)}
```

## Extracto del Site Report
{site_report[:3000]}

---

Devuelve SOLO un JSON con esta estructura:
{{
    "categorias": [
        {{
            "nombre": "nombre de la categoría",
            "descripcion": "por qué es relevante",
            "query_perplexity": "query optimizada para buscar estos benchmarks",
            "ejemplos_conocidos": ["ejemplo1", "ejemplo2"],
            "relevancia": "alta/media/baja"
        }}
    ],
    "tipo_proyecto_detectado": "string",
    "escala_estimada": "string",
    "mercado_objetivo": "string"
}}

Incluye entre 5 y 8 categorías, priorizando las más relevantes."""

    resultado = await consultar_sabio("gpt54", prompt)

    if resultado.get("status") == "ok":
        text = resultado["text"]
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
                return data.get("categorias", [])
        except json.JSONDecodeError:
            pass
    return []


async def research_benchmarks(categories: list) -> list:
    """Investiga benchmarks en paralelo usando Perplexity Sonar."""

    async def research_one(cat: dict) -> dict:
        query = cat.get("query_perplexity", cat.get("nombre", ""))
        resultado = await consultar_sabio("perplexity", query)
        return {
            "categoria": cat.get("nombre", ""),
            "relevancia": cat.get("relevancia", "media"),
            "research": resultado.get("text", "") if resultado.get("status") == "ok" else "Error en investigación",
            "status": resultado.get("status", "error"),
        }

    tasks = [research_one(cat) for cat in categories]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    benchmarks = []
    for r in results:
        if isinstance(r, dict):
            benchmarks.append(r)
        else:
            benchmarks.append({"error": str(r)})

    return benchmarks


async def synthesize_benchmarks(brief: dict, categories: list, research_results: list, output_dir: str) -> dict:
    """GPT-5.4 sintetiza la investigación en un reporte de benchmarks estructurado."""

    research_text = ""
    for i, (cat, res) in enumerate(zip(categories, research_results)):
        research_text += f"\n### Categoría {i + 1}: {cat.get('nombre', 'N/A')}\n"
        research_text += f"Relevancia: {cat.get('relevancia', 'N/A')}\n"
        research_text += f"Investigación:\n{res.get('research', 'No disponible')[:3000]}\n"

    prompt = f"""Eres un consultor inmobiliario de clase mundial especializado en benchmarking internacional.

## Proyecto
```yaml
{yaml.dump({k: v for k, v in brief.items() if not k.startswith("_")}, default_flow_style=False, allow_unicode=True)}
```

## Investigación de Benchmarks
{research_text}

---

Genera un REPORTE DE BENCHMARKS INTERNACIONALES en Markdown con:

1. **Resumen Ejecutivo** — Los 3-5 benchmarks más relevantes y por qué
2. **Tabla Comparativa de Benchmarks** con columnas: Proyecto, Ubicación, Tipo, Escala, Inversión, Año, Lección Clave, Relevancia para este proyecto
3. **Análisis Detallado por Benchmark** (top 8-10 proyectos):
   - Descripción del proyecto
   - Contexto y similitudes con nuestro caso
   - Métricas clave (GLA, inversión, ROI, ocupación, etc.)
   - Lecciones aplicables
   - Qué replicar y qué evitar
4. **Patrones Comunes** — Qué tienen en común los proyectos exitosos
5. **Anti-patrones** — Qué evitar basado en fracasos documentados
6. **Programa Arquitectónico Sugerido** — Basado en benchmarks, qué componentes debería tener este proyecto
7. **Métricas de Referencia** — Tabla con KPIs típicos del tipo de proyecto

IMPORTANTE: 
- Etiqueta cada dato como [VERIFICADO], [ESTIMADO] o [REFERENCIA]
- No inventes proyectos. Si no tienes datos, di "PENDIENTE"
- Prioriza proyectos reales y documentados
- Incluye al menos 2 benchmarks latinoamericanos si existen"""

    resultado = await consultar_sabio("gpt54", prompt)

    report = ""
    if resultado.get("status") == "ok":
        report = resultado["text"]
    else:
        report = "# Error generando reporte de benchmarks\n\nNo se pudo generar."

    # Guardar reporte
    report_path = os.path.join(output_dir, "benchmarks.md")
    Path(report_path).write_text(report, encoding="utf-8")

    # Guardar datos
    data = {
        "categorias": [c.get("nombre") for c in categories],
        "benchmarks_investigados": len(research_results),
        "exitosos": sum(1 for r in research_results if r.get("status") == "ok"),
        "timestamp": datetime.now().isoformat(),
    }
    data_path = os.path.join(output_dir, "benchmarks_data.yaml")
    with open(data_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    return {
        "report_path": report_path,
        "data_path": data_path,
        "report_size": len(report),
        "categories_researched": len(categories),
        "successful_researches": sum(1 for r in research_results if r.get("status") == "ok"),
    }


async def run_benchmark_research(brief_path: str, site_report_path: str, output_dir: str) -> dict:
    """Ejecuta el pipeline completo de Benchmark Research."""

    print("=" * 60)
    print("🔍 MÓDULO 3: BENCHMARK RESEARCH")
    print(f"   Fecha: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("=" * 60)

    # 1. Cargar inputs
    with open(brief_path, "r", encoding="utf-8") as f:
        brief = yaml.safe_load(f)

    site_report = ""
    if site_report_path and Path(site_report_path).exists():
        site_report = Path(site_report_path).read_text(encoding="utf-8")

    # 2. Identificar categorías de benchmarks
    print("  🤖 GPT-5.4 identificando categorías de benchmarks...")
    categories = await identify_benchmark_categories(brief, site_report)
    print(f"  📋 {len(categories)} categorías identificadas")
    for cat in categories:
        print(f"     • {cat.get('nombre', 'N/A')} [{cat.get('relevancia', '?')}]")

    # 3. Investigar benchmarks en paralelo
    print(f"\n  🌐 Investigando {len(categories)} categorías con Perplexity Sonar...")
    research_results = await research_benchmarks(categories)
    ok = sum(1 for r in research_results if r.get("status") == "ok")
    print(f"  ✅ {ok}/{len(categories)} categorías investigadas exitosamente")

    # 4. Sintetizar
    print("  🤖 Sintetizando reporte de benchmarks con GPT-5.4...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    result = await synthesize_benchmarks(brief, categories, research_results, output_dir)

    print("\n✅ Benchmark Research completado")
    print(f"  📄 Reporte: {result['report_path']} ({result['report_size']:,} chars)")
    print(f"  📊 Categorías: {result['categories_researched']}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo 3: Benchmark Research")
    parser.add_argument("--brief", required=True, help="Ruta al project_brief.yaml")
    parser.add_argument("--site-report", help="Ruta al site_report.md")
    parser.add_argument("--output-dir", required=True, help="Directorio de salida")

    args = parser.parse_args()
    result = asyncio.run(run_benchmark_research(args.brief, args.site_report, args.output_dir))
