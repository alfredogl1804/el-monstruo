#!/usr/bin/env python3.11
"""
Módulo 2: Site Intelligence
Analiza el terreno programáticamente: contexto urbano, demografía,
vialidades, competencia, zonificación, clima y accesibilidad.

Fuentes:
- OpenStreetMap / Overpass API (POIs, vialidades, edificios)
- Nominatim (geocodificación inversa)
- Perplexity Sonar (datos en tiempo real)
- GPT-5.4 (síntesis y análisis)

Salida: site_report.md con análisis completo + site_data.yaml con datos estructurados
"""

import asyncio
import json
import os
import sys
import yaml
import argparse
import requests
from pathlib import Path
from datetime import datetime

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def query_overpass(lat: float, lng: float, radius: int = 1000, tags: str = "") -> list:
    """Consulta Overpass API para obtener POIs cercanos."""
    query = f"""
    [out:json][timeout:25];
    (
      node{tags}(around:{radius},{lat},{lng});
      way{tags}(around:{radius},{lat},{lng});
    );
    out center body;
    """
    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("elements", [])
    except Exception:
        pass
    return []


def analyze_surroundings(lat: float, lng: float) -> dict:
    """Analiza el entorno del terreno usando Overpass API."""
    
    results = {
        "comercio": [],
        "restaurantes": [],
        "hoteles": [],
        "educacion": [],
        "salud": [],
        "transporte": [],
        "entretenimiento": [],
        "oficinas": [],
        "residencial": [],
        "vialidades": [],
        "areas_verdes": []
    }
    
    # Queries por categoría
    queries = {
        "comercio": '["shop"]',
        "restaurantes": '["amenity"~"restaurant|cafe|fast_food|bar"]',
        "hoteles": '["tourism"~"hotel|motel|hostel|guest_house"]',
        "educacion": '["amenity"~"school|university|college"]',
        "salud": '["amenity"~"hospital|clinic|pharmacy"]',
        "transporte": '["highway"~"bus_stop|motorway_junction"]["amenity"~"bus_station|taxi"]',
        "entretenimiento": '["leisure"~"park|stadium|sports_centre|fitness_centre"]["amenity"~"cinema|theatre"]',
        "oficinas": '["office"]',
    }
    
    for cat, tag in queries.items():
        elements = query_overpass(lat, lng, radius=1500, tags=tag)
        for el in elements[:20]:  # Limitar a 20 por categoría
            name = el.get("tags", {}).get("name", "Sin nombre")
            el_type = el.get("tags", {}).get("amenity") or el.get("tags", {}).get("shop") or el.get("tags", {}).get("tourism") or el.get("tags", {}).get("leisure") or "otro"
            results[cat].append({"nombre": name, "tipo": el_type})
    
    # Vialidades principales
    vias = query_overpass(lat, lng, radius=500, tags='["highway"~"primary|secondary|tertiary|trunk|motorway"]')
    for v in vias[:10]:
        name = v.get("tags", {}).get("name", "Sin nombre")
        hw_type = v.get("tags", {}).get("highway", "otro")
        results["vialidades"].append({"nombre": name, "tipo": hw_type})
    
    return results


def get_climate_info(lat: float, lng: float) -> dict:
    """Obtiene información climática básica usando Open-Meteo."""
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lng,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "auto",
                "forecast_days": 7
            },
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            daily = data.get("daily", {})
            temps_max = daily.get("temperature_2m_max", [])
            temps_min = daily.get("temperature_2m_min", [])
            return {
                "temp_max_promedio": round(sum(temps_max) / len(temps_max), 1) if temps_max else None,
                "temp_min_promedio": round(sum(temps_min) / len(temps_min), 1) if temps_min else None,
                "timezone": data.get("timezone", ""),
                "elevacion_m": data.get("elevation", None),
                "fuente": "open-meteo"
            }
    except Exception:
        pass
    return {"error": "No disponible"}


async def research_site_context(brief: dict) -> str:
    """Usa Perplexity Sonar para investigar el contexto del sitio en tiempo real."""
    
    ciudad = brief.get("ubicacion", {}).get("ciudad", "")
    estado = brief.get("ubicacion", {}).get("estado", "")
    uso_actual = brief.get("terreno", {}).get("uso_actual", "")
    landmarks = brief.get("contexto", {}).get("landmarks_cercanos", [])
    
    query = f"""Investiga el contexto urbano, demográfico y económico de la zona donde se ubica {uso_actual} en {ciudad}, {estado}. 
Incluye: población del área metropolitana, ingreso per cápita, crecimiento económico, 
principales desarrollos inmobiliarios recientes, zonificación típica, 
planes de desarrollo urbano relevantes, y cualquier proyecto de infraestructura cercano.
Landmarks cercanos: {', '.join(landmarks) if landmarks else 'no especificados'}."""

    resultado = await consultar_sabio("perplexity", query)
    
    if resultado.get("status") == "ok":
        return resultado["text"]
    return "No se pudo obtener contexto en tiempo real."


async def synthesize_site_report(brief: dict, surroundings: dict, climate: dict, research: str, output_dir: str) -> dict:
    """GPT-5.4 sintetiza todo en un reporte de site intelligence."""
    
    prompt = f"""Eres un analista inmobiliario senior especializado en estudios de sitio. 
Con base en los siguientes datos, genera un REPORTE DE INTELIGENCIA DE SITIO completo.

## Project Brief
```yaml
{yaml.dump(brief, default_flow_style=False, allow_unicode=True)}
```

## Análisis de Entorno (Overpass/OSM)
```json
{json.dumps(surroundings, ensure_ascii=False, indent=2)}
```

## Datos Climáticos
```json
{json.dumps(climate, ensure_ascii=False, indent=2)}
```

## Investigación en Tiempo Real (Perplexity)
{research}

---

Genera el reporte en Markdown con estas secciones:

1. **Resumen Ejecutivo del Sitio** (3-5 párrafos)
2. **Ubicación y Accesibilidad** (vialidades, transporte, conectividad)
3. **Contexto Urbano** (tipo de zona, densidad, carácter)
4. **Demografía y Economía** (población, ingreso, crecimiento)
5. **Competencia y Oferta Existente** (qué hay alrededor, saturación)
6. **Clima y Consideraciones Ambientales** (temperaturas, lluvia, confort)
7. **Regulación y Zonificación** (uso de suelo, restricciones conocidas)
8. **Oportunidades Identificadas** (gaps de mercado, ventajas del sitio)
9. **Riesgos del Sitio** (amenazas, debilidades, incertidumbres)
10. **Tabla de Datos Clave** (resumen en tabla)

IMPORTANTE: Etiqueta cada dato como [VERIFICADO], [ESTIMADO], [PENDIENTE] o [BENCHMARK].
Sé específico y cuantitativo. No inventes datos — si no hay información, di "PENDIENTE DE VERIFICACIÓN"."""

    resultado = await consultar_sabio("gpt54", prompt)
    
    report = ""
    if resultado.get("status") == "ok":
        report = resultado["text"]
    else:
        report = "# Error generando reporte de sitio\n\nNo se pudo generar el reporte."
    
    # Guardar reporte
    report_path = os.path.join(output_dir, "site_report.md")
    Path(report_path).write_text(report, encoding="utf-8")
    
    # Guardar datos estructurados
    site_data = {
        "surroundings": surroundings,
        "climate": climate,
        "research_summary": research[:2000] if research else "",
        "timestamp": datetime.now().isoformat()
    }
    data_path = os.path.join(output_dir, "site_data.yaml")
    with open(data_path, "w", encoding="utf-8") as f:
        yaml.dump(site_data, f, default_flow_style=False, allow_unicode=True)
    
    return {
        "report_path": report_path,
        "data_path": data_path,
        "report_size": len(report),
        "pois_found": sum(len(v) for v in surroundings.values() if isinstance(v, list))
    }


async def run_site_intelligence(brief_path: str, output_dir: str) -> dict:
    """Ejecuta el pipeline completo de Site Intelligence."""
    
    print("=" * 60)
    print("🗺️  MÓDULO 2: SITE INTELLIGENCE")
    print(f"   Fecha: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("=" * 60)
    
    # 1. Cargar brief
    with open(brief_path, "r", encoding="utf-8") as f:
        brief = yaml.safe_load(f)
    
    lat = brief.get("ubicacion", {}).get("coordenadas", {}).get("lat")
    lng = brief.get("ubicacion", {}).get("coordenadas", {}).get("lng")
    
    if not lat or not lng:
        print("  ⚠️ Sin coordenadas. Intentando geocodificar...")
        addr = brief.get("ubicacion", {}).get("direccion", "")
        city = brief.get("ubicacion", {}).get("ciudad", "")
        from intake_normalize import geocode_address
        geo = geocode_address(f"{addr}, {city}")
        lat, lng = geo.get("lat"), geo.get("lng")
        if not lat:
            return {"error": "No se pudo determinar ubicación del terreno"}
    
    print(f"  📍 Analizando: {lat}, {lng}")
    
    # 2. Análisis de entorno con OSM
    print("  🔍 Consultando OpenStreetMap/Overpass...")
    surroundings = analyze_surroundings(lat, lng)
    total_pois = sum(len(v) for v in surroundings.values() if isinstance(v, list))
    print(f"  📊 {total_pois} POIs encontrados en radio de 1.5km")
    
    # 3. Datos climáticos
    print("  🌡️ Obteniendo datos climáticos...")
    climate = get_climate_info(lat, lng)
    if climate.get("temp_max_promedio"):
        print(f"  🌡️ Temp: {climate['temp_min_promedio']}°C - {climate['temp_max_promedio']}°C")
    
    # 4. Investigación en tiempo real
    print("  🌐 Investigando contexto con Perplexity Sonar...")
    research = await research_site_context(brief)
    print(f"  📄 Investigación: {len(research):,} caracteres")
    
    # 5. Síntesis
    print("  🤖 Sintetizando reporte con GPT-5.4...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    result = await synthesize_site_report(brief, surroundings, climate, research, output_dir)
    
    print(f"\n✅ Site Intelligence completado")
    print(f"  📄 Reporte: {result['report_path']} ({result['report_size']:,} chars)")
    print(f"  📊 Datos: {result['data_path']}")
    print(f"  📍 POIs analizados: {result['pois_found']}")
    
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo 2: Site Intelligence")
    parser.add_argument("--brief", required=True, help="Ruta al project_brief.yaml")
    parser.add_argument("--output-dir", required=True, help="Directorio de salida")
    
    args = parser.parse_args()
    result = asyncio.run(run_site_intelligence(args.brief, args.output_dir))
