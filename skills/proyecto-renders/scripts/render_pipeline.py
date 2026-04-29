#!/usr/bin/env python3.11
"""
Módulo 6: Render Pipeline
Genera renders fotorrealistas del proyecto usando IA generativa.

Pipeline:
1. Style Bible — Define el lenguaje visual (materiales, paleta, estilo)
2. Hero Image — Render canónico principal (vista aérea o perspectiva)
3. Vistas Derivadas — 7 renders adicionales desde diferentes ángulos/zonas

Herramienta: Manus generate mode (invocado por el agente)
Este script genera los prompts optimizados; la generación real
la ejecuta el agente usando la herramienta generate.

Salida: style_bible.md + render_prompts.yaml (8 prompts listos para generar)
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


async def generate_style_bible(brief: dict, scenarios: dict, benchmarks: str, site_data: dict) -> str:
    """GPT-5.4 genera la Style Bible del proyecto."""
    
    recommended = scenarios.get("escenario_recomendado", "Proyecto")
    escenarios = scenarios.get("escenarios", [])
    escenario_ganador = next((e for e in escenarios if e.get("nombre") == recommended), escenarios[0] if escenarios else {})
    
    clima = site_data.get("climate", {})
    ciudad = brief.get("ubicacion", {}).get("ciudad", "")
    estado = brief.get("ubicacion", {}).get("estado", "")
    
    prompt = f"""Eres un director creativo de una firma de arquitectura y visualización de clase mundial.
Genera una STYLE BIBLE completa para los renders de este proyecto.

## Proyecto: {recommended}
- Ubicación: {ciudad}, {estado}
- Clima: Temp {clima.get('temp_min_promedio', '?')}°C - {clima.get('temp_max_promedio', '?')}°C
- Concepto: {escenario_ganador.get('concepto', 'N/A')}

## Componentes del Proyecto
```yaml
{yaml.dump(escenario_ganador.get('componentes', []), default_flow_style=False, allow_unicode=True)}
```

## Benchmarks de Referencia (extracto)
{benchmarks[:2000]}

---

Genera la STYLE BIBLE en Markdown con:

## 1. Concepto Visual
- Narrativa visual en 2-3 párrafos
- Palabras clave del estilo (5-7 keywords)
- Referentes visuales (proyectos reales de referencia)

## 2. Paleta de Materiales
- Materiales principales (tabla: material, uso, acabado, referencia)
- Materiales secundarios
- Materiales de acento

## 3. Paleta de Color
- Colores primarios (hex + nombre + uso)
- Colores secundarios
- Colores de acento
- Regla de proporción (60-30-10)

## 4. Vegetación y Paisajismo
- Especies principales (adaptadas al clima)
- Estilo de paisajismo
- Elementos de agua

## 5. Iluminación
- Hora del día para renders (golden hour, etc.)
- Tipo de iluminación artificial
- Ambiente nocturno

## 6. Mobiliario y Elementos
- Estilo de mobiliario urbano
- Señalización y wayfinding
- Elementos experienciales

## 7. Personas y Actividad
- Tipo de personas (demografía visual)
- Actividades representadas
- Densidad de personas por vista

## 8. Reglas de Consistencia
- Ángulo de cámara estándar
- Distancia focal sugerida
- Proporción cielo/edificio
- Elementos que DEBEN aparecer en todos los renders
- Elementos que NUNCA deben aparecer"""

    resultado = await consultar_sabio("gpt54", prompt)
    return resultado.get("text", "Error generando style bible") if resultado.get("status") == "ok" else "Error"


async def generate_render_prompts(brief: dict, scenarios: dict, style_bible: str) -> list:
    """GPT-5.4 genera los 8 prompts optimizados para generación de renders."""
    
    recommended = scenarios.get("escenario_recomendado", "Proyecto")
    escenarios = scenarios.get("escenarios", [])
    escenario_ganador = next((e for e in escenarios if e.get("nombre") == recommended), escenarios[0] if escenarios else {})
    
    ciudad = brief.get("ubicacion", {}).get("ciudad", "")
    
    prompt = f"""Eres un experto en generación de imágenes con IA. Genera 8 prompts fotorrealistas 
para crear renders arquitectónicos de este proyecto.

## Proyecto: {recommended}
- Ciudad: {ciudad}
- Componentes: {[c.get('nombre') for c in escenario_ganador.get('componentes', [])]}

## Style Bible (extracto)
{style_bible[:3000]}

---

Genera EXACTAMENTE 8 prompts como JSON array. Cada prompt debe ser:
- En INGLÉS (los modelos de imagen funcionan mejor en inglés)
- Altamente descriptivo (150-250 palabras)
- Fotorrealista (no cartoon, no sketch)
- Consistente con la style bible

Estructura del JSON:
[
    {{
        "id": 1,
        "nombre": "Hero — Vista Aérea General",
        "tipo": "hero",
        "angulo": "aerial 45 degrees",
        "hora": "golden hour sunset",
        "foco": "descripción de qué muestra esta vista",
        "prompt": "el prompt completo en inglés para generar la imagen",
        "negative_prompt": "lo que NO debe aparecer",
        "aspect_ratio": "16:9",
        "importancia": "critica/alta/media"
    }},
    ...
]

Las 8 vistas DEBEN ser:
1. Hero — Vista aérea general del proyecto completo
2. Plaza principal / espacio central (eye-level)
3. Food hall / zona gastronómica (interior o semi-exterior)
4. Fachada principal / entrada (perspectiva peatonal)
5. Zona de entretenimiento / experiencial (eye-level)
6. Vista nocturna del proyecto iluminado (aérea o perspectiva)
7. Área familiar / zona verde (eye-level)
8. Detalle arquitectónico / materialidad (close-up)

REGLAS PARA LOS PROMPTS:
- Incluir: "photorealistic architectural render, 8K, professional photography"
- Incluir materiales específicos de la style bible
- Incluir vegetación tropical si aplica
- Incluir personas realizando actividades
- NO incluir: logos, texto, marcas de agua, wireframes"""

    resultado = await consultar_sabio("gpt54", prompt)
    
    if resultado.get("status") == "ok":
        text = resultado["text"]
        try:
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    
    return []


async def run_render_pipeline(brief_path: str, scenarios_path: str, benchmarks_path: str,
                               site_data_path: str, output_dir: str) -> dict:
    """Ejecuta el pipeline de preparación de renders."""
    
    print("=" * 60)
    print("🎨 MÓDULO 6: RENDER PIPELINE")
    print(f"   Fecha: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("=" * 60)
    
    # 1. Cargar inputs
    with open(brief_path, "r", encoding="utf-8") as f:
        brief = yaml.safe_load(f)
    
    scenarios = {}
    if scenarios_path and Path(scenarios_path).exists():
        with open(scenarios_path, "r", encoding="utf-8") as f:
            scenarios = yaml.safe_load(f) or {}
    
    benchmarks = Path(benchmarks_path).read_text(encoding="utf-8") if benchmarks_path and Path(benchmarks_path).exists() else ""
    
    site_data = {}
    if site_data_path and Path(site_data_path).exists():
        with open(site_data_path, "r", encoding="utf-8") as f:
            site_data = yaml.safe_load(f) or {}
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    renders_dir = os.path.join(output_dir, "renders")
    Path(renders_dir).mkdir(parents=True, exist_ok=True)
    
    # 2. Generar Style Bible
    print("  🎨 GPT-5.4 generando Style Bible...")
    style_bible = await generate_style_bible(brief, scenarios, benchmarks, site_data)
    
    style_path = os.path.join(output_dir, "style_bible.md")
    Path(style_path).write_text(style_bible, encoding="utf-8")
    print(f"  📄 Style Bible: {len(style_bible):,} caracteres")
    
    # 3. Generar prompts de renders
    print("  🤖 GPT-5.4 generando 8 prompts de renders...")
    render_prompts = await generate_render_prompts(brief, scenarios, style_bible)
    
    prompts_path = os.path.join(output_dir, "render_prompts.yaml")
    with open(prompts_path, "w", encoding="utf-8") as f:
        yaml.dump(render_prompts, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"  📋 {len(render_prompts)} prompts generados")
    for rp in render_prompts:
        print(f"     {rp.get('id', '?')}. {rp.get('nombre', 'N/A')} [{rp.get('importancia', '?')}]")
    
    # 4. Guardar instrucciones para el agente
    instructions = f"""# Instrucciones de Generación de Renders

## Directorio de salida: {renders_dir}

## Proceso:
El agente debe entrar en modo `generate` y crear cada imagen usando los prompts
del archivo `render_prompts.yaml`. Guardar cada render en el directorio `renders/`
con el nombre: `render_{{id:02d}}_{{nombre_corto}}.png`

## Orden de generación:
1. Primero el Hero (id=1) — es la imagen canónica
2. Luego las demás en orden de importancia
3. Después de generar el hero, verificar consistencia visual
4. Si el hero no es satisfactorio, regenerar antes de continuar

## Quality checks:
- Verificar que los materiales coinciden con la style bible
- Verificar que la vegetación es tropical (si aplica)
- Verificar que hay personas y actividad
- Verificar consistencia de paleta de colores entre renders
"""
    
    instructions_path = os.path.join(output_dir, "render_instructions.md")
    Path(instructions_path).write_text(instructions, encoding="utf-8")
    
    print(f"\n✅ Render Pipeline preparado")
    print(f"  📄 Style Bible: {style_path}")
    print(f"  📋 Prompts: {prompts_path}")
    print(f"  📁 Renders dir: {renders_dir}")
    print(f"  📝 Instrucciones: {instructions_path}")
    
    return {
        "style_bible_path": style_path,
        "prompts_path": prompts_path,
        "renders_dir": renders_dir,
        "instructions_path": instructions_path,
        "num_prompts": len(render_prompts),
        "prompts": render_prompts
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo 6: Render Pipeline")
    parser.add_argument("--brief", required=True)
    parser.add_argument("--scenarios", required=True)
    parser.add_argument("--benchmarks", help="Ruta al benchmarks.md")
    parser.add_argument("--site-data", help="Ruta al site_data.yaml")
    parser.add_argument("--output-dir", required=True)
    
    args = parser.parse_args()
    result = asyncio.run(run_render_pipeline(
        args.brief, args.scenarios, args.benchmarks, args.site_data, args.output_dir
    ))
