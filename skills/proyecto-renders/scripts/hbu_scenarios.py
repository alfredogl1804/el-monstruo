#!/usr/bin/env python3.11
"""
Módulo 4: Highest and Best Use (HBU) + Escenarios + Quick Financial Model
Determina el mejor uso del terreno usando análisis multicriterio,
genera escenarios comparables y un modelo financiero rápido.

Framework: HBU Analysis (Legally Permissible, Physically Possible,
Financially Feasible, Maximally Productive)

Salida: hbu_analysis.md + scenarios.yaml + financial_model.md
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


async def generate_hbu_analysis(brief: dict, site_report: str, benchmarks: str) -> str:
    """GPT-5.4 realiza el análisis HBU completo."""

    prompt = f"""Eres un analista inmobiliario senior especializado en estudios de Highest and Best Use (HBU).

## Project Brief
```yaml
{yaml.dump({k: v for k, v in brief.items() if not k.startswith("_")}, default_flow_style=False, allow_unicode=True)}
```

## Site Intelligence (extracto)
{site_report[:4000]}

## Benchmarks (extracto)
{benchmarks[:4000]}

---

Realiza un ANÁLISIS HBU COMPLETO con estas secciones:

## 1. Filtro Legal (Legally Permissible)
- Usos permitidos por zonificación (conocidos o estimados)
- Restricciones regulatorias
- Nivel de certeza: [VERIFICADO/ESTIMADO/PENDIENTE]

## 2. Filtro Físico (Physically Possible)
- Capacidad del terreno por tipo de uso
- Restricciones topográficas, climáticas, de acceso
- Infraestructura existente aprovechable

## 3. Filtro Financiero (Financially Feasible)
- Usos con demanda demostrada en el mercado
- Rangos de inversión por tipo de uso
- Viabilidad financiera preliminar

## 4. Máxima Productividad (Maximally Productive)
- Ranking de usos por valor residual estimado
- Análisis multicriterio (10 criterios, peso, score 1-5)

## 5. Escenarios Propuestos (4 escenarios)
Para cada escenario incluye:
- Nombre y concepto
- Programa arquitectónico (componentes y m2)
- Inversión estimada (rango)
- Ingresos anuales estimados (rango)
- ROI estimado y payback
- Riesgo (alto/medio/bajo)
- Sinergia con activos existentes
- Nivel de evidencia

## 6. Modelo Financiero Rápido (para el escenario recomendado)
- CAPEX desglosado
- OPEX anual estimado
- Ingresos por línea
- NOI proyectado
- Cap rate de mercado
- Valor terminal estimado
- IRR estimado (rango)
- Sensibilidad: optimista / base / conservador

## 7. Recomendación
- Escenario ganador y por qué
- Condiciones para validar
- Siguiente paso inmediato

REGLAS CRÍTICAS:
- Etiqueta CADA número como [VERIFICADO], [BENCHMARK], [ESTIMADO] o [SUPUESTO]
- No finjas precisión. Usa rangos cuando no tengas datos exactos
- Si un dato es crítico y no está verificado, márcalo como GAP CRÍTICO
- Incluye tabla comparativa de los 4 escenarios al final"""

    resultado = await consultar_sabio("gpt54", prompt)
    return resultado.get("text", "Error en análisis HBU") if resultado.get("status") == "ok" else "Error"


async def generate_scenarios_yaml(hbu_text: str) -> dict:
    """Extrae los escenarios del análisis HBU en formato estructurado."""

    prompt = f"""Del siguiente análisis HBU, extrae los escenarios propuestos y devuélvelos como JSON.

{hbu_text[:8000]}

Devuelve SOLO un JSON con esta estructura:
{{
    "escenario_recomendado": "nombre del escenario ganador",
    "escenarios": [
        {{
            "nombre": "string",
            "concepto": "string breve",
            "componentes": [
                {{"nombre": "string", "m2": "float o null", "tipo": "string"}}
            ],
            "inversion_mxn": {{"min": "float", "max": "float", "nivel": "ESTIMADO/BENCHMARK"}},
            "ingresos_anuales_mxn": {{"min": "float", "max": "float", "nivel": "ESTIMADO/BENCHMARK"}},
            "roi_estimado": "string",
            "payback_anos": "string",
            "riesgo": "alto/medio/bajo",
            "sinergia": "alta/media/baja",
            "fortalezas": ["lista"],
            "debilidades": ["lista"]
        }}
    ],
    "criterios_decision": [
        {{"criterio": "string", "peso": "float 0-1", "descripcion": "string"}}
    ]
}}"""

    resultado = await consultar_sabio("gpt54", prompt)

    if resultado.get("status") == "ok":
        text = resultado["text"]
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    return {"error": "No se pudieron extraer escenarios", "escenarios": []}


async def run_hbu_analysis(brief_path: str, site_report_path: str, benchmarks_path: str, output_dir: str) -> dict:
    """Ejecuta el pipeline completo de HBU + Escenarios + Financial Model."""

    print("=" * 60)
    print("📊 MÓDULO 4: HBU + ESCENARIOS + MODELO FINANCIERO")
    print(f"   Fecha: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("=" * 60)

    # 1. Cargar inputs
    with open(brief_path, "r", encoding="utf-8") as f:
        brief = yaml.safe_load(f)

    site_report = ""
    if site_report_path and Path(site_report_path).exists():
        site_report = Path(site_report_path).read_text(encoding="utf-8")

    benchmarks = ""
    if benchmarks_path and Path(benchmarks_path).exists():
        benchmarks = Path(benchmarks_path).read_text(encoding="utf-8")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 2. Análisis HBU
    print("  🤖 GPT-5.4 realizando análisis HBU completo...")
    hbu_text = await generate_hbu_analysis(brief, site_report, benchmarks)

    hbu_path = os.path.join(output_dir, "hbu_analysis.md")
    Path(hbu_path).write_text(hbu_text, encoding="utf-8")
    print(f"  📄 Análisis HBU: {len(hbu_text):,} caracteres")

    # 3. Extraer escenarios estructurados
    print("  🤖 Extrayendo escenarios estructurados...")
    scenarios = await generate_scenarios_yaml(hbu_text)

    scenarios_path = os.path.join(output_dir, "scenarios.yaml")
    with open(scenarios_path, "w", encoding="utf-8") as f:
        yaml.dump(scenarios, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    n_scenarios = len(scenarios.get("escenarios", []))
    recommended = scenarios.get("escenario_recomendado", "No definido")
    print(f"  📋 {n_scenarios} escenarios generados")
    print(f"  ⭐ Recomendado: {recommended}")

    print("\n✅ HBU + Escenarios completado")
    print(f"  📄 HBU: {hbu_path}")
    print(f"  📊 Escenarios: {scenarios_path}")

    return {
        "hbu_path": hbu_path,
        "scenarios_path": scenarios_path,
        "hbu_size": len(hbu_text),
        "num_scenarios": n_scenarios,
        "recommended": recommended,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo 4: HBU + Escenarios")
    parser.add_argument("--brief", required=True, help="Ruta al project_brief.yaml")
    parser.add_argument("--site-report", help="Ruta al site_report.md")
    parser.add_argument("--benchmarks", help="Ruta al benchmarks.md")
    parser.add_argument("--output-dir", required=True, help="Directorio de salida")

    args = parser.parse_args()
    result = asyncio.run(run_hbu_analysis(args.brief, args.site_report, args.benchmarks, args.output_dir))
