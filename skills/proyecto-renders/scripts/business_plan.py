#!/usr/bin/env python3.11
"""
Módulo 5: Business Plan Generator
Genera un plan de negocio ejecutivo completo basado en el escenario
ganador del análisis HBU, los benchmarks y el site intelligence.

Salida: business_plan.md (documento ejecutivo presentable)
"""

import asyncio
import json
import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio


async def generate_business_plan(brief: dict, site_report: str, benchmarks: str, hbu: str, scenarios: dict) -> str:
    """GPT-5.4 genera el plan de negocio ejecutivo completo."""
    
    recommended = scenarios.get("escenario_recomendado", "No definido")
    scenarios_yaml = yaml.dump(scenarios.get("escenarios", []), default_flow_style=False, allow_unicode=True)
    
    prompt = f"""Eres un consultor de negocios de clase mundial especializado en desarrollo inmobiliario y entretenimiento. 
Genera un PLAN DE NEGOCIO EJECUTIVO completo y presentable para inversionistas.

## Escenario Seleccionado: {recommended}

## Project Brief
```yaml
{yaml.dump({k: v for k, v in brief.items() if not k.startswith('_')}, default_flow_style=False, allow_unicode=True)}
```

## Escenarios Evaluados
```yaml
{scenarios_yaml[:3000]}
```

## Site Intelligence (extracto)
{site_report[:3000]}

## Benchmarks (extracto)
{benchmarks[:3000]}

## Análisis HBU (extracto)
{hbu[:3000]}

---

GENERA EL PLAN DE NEGOCIO con estas secciones exactas:

# PLAN DE NEGOCIO — [Nombre del Proyecto]

## 1. Resumen Ejecutivo
- Oportunidad en 3 párrafos
- Propuesta de valor única
- Cifras clave: inversión, retorno esperado, timeline

## 2. Análisis de Mercado
- Mercado objetivo (demografía, psicografía, tamaño)
- Tendencias relevantes del mercado
- Demanda estimada
- Competencia directa e indirecta

## 3. Concepto del Proyecto
- Visión y misión
- Programa arquitectónico detallado (tabla: componente, m2, uso, capacidad)
- Experiencia del usuario (journey del visitante)
- Diferenciadores vs competencia

## 4. Modelo de Negocio
- Fuentes de ingreso (tabla: línea, tipo, ingreso mensual estimado, % del total)
- Estructura de precios
- Modelo operativo (propio, concesión, mixto)
- Partners estratégicos potenciales

## 5. Plan de Desarrollo por Fases
- Fase 1: Descripción, inversión, timeline, hitos
- Fase 2: Condiciones de activación, descripción, inversión
- Fase 3: Condiciones de activación, descripción, inversión
- Gantt simplificado (tabla)

## 6. Proyecciones Financieras
- CAPEX desglosado por fase (tabla)
- OPEX anual proyectado (tabla: concepto, monto, % del ingreso)
- Estado de resultados proyectado (Años 1-5, tabla)
- Flujo de caja libre proyectado
- Indicadores: TIR, VPN, Payback, Cap Rate, DSCR
- Análisis de sensibilidad (3 escenarios: optimista, base, conservador)

## 7. Análisis de Riesgos
- Tabla: Riesgo, Probabilidad, Impacto, Mitigación
- Top 5 riesgos críticos

## 8. Equipo y Gobernanza
- Estructura organizacional sugerida
- Perfiles clave requeridos
- Modelo de gobernanza

## 9. Estrategia de Salida
- Opciones de exit (venta, REIT, IPO parcial)
- Valoración estimada al año 5 y 10

## 10. Conclusión y Siguiente Paso
- Resumen de la oportunidad
- Call to action para inversionistas
- Próximos pasos inmediatos (3-5 acciones concretas)

REGLAS:
- Cada cifra debe estar etiquetada: [VERIFICADO], [BENCHMARK], [ESTIMADO], [SUPUESTO]
- Usa moneda MXN y USD donde aplique (tipo de cambio actual)
- Incluye tablas profesionales donde corresponda
- Tono: profesional, confiable, orientado a inversionistas
- Extensión: 3,000-5,000 palabras"""

    resultado = await consultar_sabio("gpt54", prompt)
    return resultado.get("text", "Error generando plan de negocio") if resultado.get("status") == "ok" else "Error"


async def validate_financials(plan_text: str) -> str:
    """Gemini valida las proyecciones financieras del plan."""
    
    prompt = f"""Eres un analista financiero senior. Revisa las proyecciones financieras de este plan de negocio 
y señala inconsistencias, supuestos agresivos, o errores matemáticos.

{plan_text[:8000]}

Devuelve un breve informe de validación con:
1. Consistencia de las cifras (✅ o ⚠️ por sección)
2. Supuestos que parecen agresivos o conservadores
3. Errores matemáticos detectados
4. Comparación con benchmarks típicos del sector
5. Score de confiabilidad general (1-10)
6. Recomendaciones de mejora"""

    resultado = await consultar_sabio("gemini", prompt)
    return resultado.get("text", "Validación no disponible") if resultado.get("status") == "ok" else "Error"


async def run_business_plan(brief_path: str, site_report_path: str, benchmarks_path: str, 
                            hbu_path: str, scenarios_path: str, output_dir: str) -> dict:
    """Ejecuta el pipeline completo de generación de plan de negocio."""
    
    print("=" * 60)
    print("📋 MÓDULO 5: BUSINESS PLAN GENERATOR")
    print(f"   Fecha: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("=" * 60)
    
    # 1. Cargar inputs
    with open(brief_path, "r", encoding="utf-8") as f:
        brief = yaml.safe_load(f)
    
    site_report = Path(site_report_path).read_text(encoding="utf-8") if site_report_path and Path(site_report_path).exists() else ""
    benchmarks = Path(benchmarks_path).read_text(encoding="utf-8") if benchmarks_path and Path(benchmarks_path).exists() else ""
    hbu = Path(hbu_path).read_text(encoding="utf-8") if hbu_path and Path(hbu_path).exists() else ""
    
    scenarios = {}
    if scenarios_path and Path(scenarios_path).exists():
        with open(scenarios_path, "r", encoding="utf-8") as f:
            scenarios = yaml.safe_load(f) or {}
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 2. Generar plan de negocio
    print(f"  ⭐ Escenario: {scenarios.get('escenario_recomendado', 'No definido')}")
    print("  🤖 GPT-5.4 generando plan de negocio ejecutivo...")
    plan_text = await generate_business_plan(brief, site_report, benchmarks, hbu, scenarios)
    
    plan_path = os.path.join(output_dir, "business_plan.md")
    Path(plan_path).write_text(plan_text, encoding="utf-8")
    print(f"  📄 Plan: {len(plan_text):,} caracteres")
    
    # 3. Validar financieros con Gemini
    print("  🔍 Gemini validando proyecciones financieras...")
    validation = await validate_financials(plan_text)
    
    validation_path = os.path.join(output_dir, "financial_validation.md")
    Path(validation_path).write_text(f"# Validación Financiera\n\n{validation}", encoding="utf-8")
    print(f"  ✅ Validación: {len(validation):,} caracteres")
    
    print(f"\n✅ Business Plan completado")
    print(f"  📄 Plan: {plan_path}")
    print(f"  🔍 Validación: {validation_path}")
    
    return {
        "plan_path": plan_path,
        "validation_path": validation_path,
        "plan_size": len(plan_text),
        "scenario": scenarios.get("escenario_recomendado", "N/A")
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo 5: Business Plan Generator")
    parser.add_argument("--brief", required=True)
    parser.add_argument("--site-report", help="Ruta al site_report.md")
    parser.add_argument("--benchmarks", help="Ruta al benchmarks.md")
    parser.add_argument("--hbu", help="Ruta al hbu_analysis.md")
    parser.add_argument("--scenarios", help="Ruta al scenarios.yaml")
    parser.add_argument("--output-dir", required=True)
    
    args = parser.parse_args()
    result = asyncio.run(run_business_plan(
        args.brief, args.site_report, args.benchmarks,
        args.hbu, args.scenarios, args.output_dir
    ))
