#!/usr/bin/env python3.11
"""
SRD Builder — Genera el Site Reality Document completo
(site_reality.json + render_constraints.json).
"""

import json
import os
from datetime import date


async def build_srd(site_info: dict, fused_evidence: dict, coverage: dict) -> dict:
    """Construye el Site Reality Document completo."""
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_API_BASE")
    if not api_key:
        return _build_srd_simple(site_info, fused_evidence, coverage)

    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    fused_json = json.dumps(fused_evidence, indent=1, ensure_ascii=False, default=str)

    prompt = f"""Eres un arquitecto de datos geoespaciales. Tu trabajo es construir un Site Reality Document (SRD) completo y estructurado para el sitio "{site_info["name"]}".

## Datos del Sitio
- Coordenadas: {site_info["lat"]}, {site_info["lng"]}
- Radio: {site_info["radius_m"]}m
- Fecha objetivo: {site_info["target_date"]}
- Semáforo cobertura: {coverage.get("semaphore", "unknown")}

## Evidencia Fusionada
{fused_json[:25000]}

## Tu Tarea
Genera un JSON con la estructura EXACTA del SRD:

{{
  "site_metadata": {{
    "name": "{site_info["name"]}",
    "coordinates": {{"lat": {site_info["lat"]}, "lng": {site_info["lng"]}}},
    "radius_m": {site_info["radius_m"]},
    "target_reality_date": "{site_info["target_date"]}",
    "reconstruction_date": "{date.today().isoformat()}"
  }},
  "source_registry": [
    {{"source_id": "string", "type": "user_photo|satellite|street_view|osm|maps_grounding|web|inference", "date": "YYYY-MM-DD", "confidence": 0.0, "license": "string"}}
  ],
  "site_conditions": {{
    "terrain": "descripción del terreno",
    "climate": "descripción del clima",
    "elevation": 0,
    "vegetation_type": "tipo de vegetación dominante"
  }},
  "surrounding_context": {{
    "north": {{"description": "", "buildings": "", "heights": "", "land_use": "", "confidence": 0.0, "evidence_ids": []}},
    "south": {{"description": "", "buildings": "", "heights": "", "land_use": "", "confidence": 0.0, "evidence_ids": []}},
    "east": {{"description": "", "buildings": "", "heights": "", "land_use": "", "confidence": 0.0, "evidence_ids": []}},
    "west": {{"description": "", "buildings": "", "heights": "", "land_use": "", "confidence": 0.0, "evidence_ids": []}}
  }},
  "visual_observations": [
    {{"observation_id": "", "category": "", "description": "", "location": {{}}, "attributes": {{}}, "confidence": 0.0, "evidence_ids": []}}
  ],
  "blind_spots": [
    {{"zone": "", "status": "", "reason": "", "render_policy": ""}}
  ],
  "render_constraints": {{
    "must_include": [{{"element": "", "description": "", "evidence_id": ""}}],
    "must_not_include": [{{"element": "", "reason": "", "evidence_id": ""}}],
    "height_limits": [{{"zone": "", "max_levels": 0, "evidence_id": ""}}],
    "landscape_constraints": [{{"zone": "", "type": "", "evidence_id": ""}}],
    "color_palette": [{{"element": "", "colors": []}}],
    "materials": [{{"element": "", "material": ""}}]
  }},
  "overall_confidence": {{
    "core_site": "high|medium|low",
    "immediate_context": "high|medium|low",
    "extended_context": "high|medium|low",
    "coverage_mode": "rich|medium|sparse"
  }},
  "validation_rules": {{
    "critical": [{{"rule": "", "description": ""}}],
    "major": [{{"rule": "", "description": ""}}],
    "minor": [{{"rule": "", "description": ""}}]
  }}
}}

REGLAS CRÍTICAS PARA render_constraints:
1. must_not_include DEBE listar todo lo que NO existe en la realidad pero que la IA podría inventar
2. height_limits DEBE reflejar las alturas REALES del contexto, no aspiracionales
3. landscape_constraints DEBE prohibir paisajismo inexistente
4. must_include DEBE listar elementos confirmados que deben aparecer en renders

REGLAS PARA validation_rules:
- critical: violaciones que invalidan el render (inventar edificios, subir alturas, etc.)
- major: violaciones significativas (materiales incorrectos, vegetación exagerada)
- minor: detalles menores (colores ligeramente diferentes, mobiliario genérico)"""

    try:
        response = client.chat.completions.create(
            model="gpt-5.4",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un sistema de construcción de documentos de realidad geoespacial. Respondes SOLO en JSON válido.",
                },
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=16000,
            response_format={"type": "json_object"},
        )

        text = response.choices[0].message.content
        srd = json.loads(text)
        return srd

    except Exception as e:
        print(f"      SRD builder error: {e}")
        return _build_srd_simple(site_info, fused_evidence, coverage)


def _build_srd_simple(site_info: dict, fused: dict, coverage: dict) -> dict:
    """Construye SRD simple sin LLM."""
    return {
        "site_metadata": {
            "name": site_info["name"],
            "coordinates": {"lat": site_info["lat"], "lng": site_info["lng"]},
            "radius_m": site_info["radius_m"],
            "target_reality_date": site_info["target_date"],
            "reconstruction_date": date.today().isoformat(),
        },
        "source_registry": [],
        "site_conditions": {},
        "surrounding_context": fused.get("surrounding_context", {}),
        "visual_observations": fused.get("observations", []),
        "blind_spots": fused.get("blind_spots", []),
        "render_constraints": {
            "must_include": [],
            "must_not_include": [],
            "height_limits": [],
            "landscape_constraints": [],
        },
        "overall_confidence": {
            "core_site": "low",
            "immediate_context": "low",
            "extended_context": "low",
            "coverage_mode": coverage.get("semaphore", "sparse"),
        },
        "validation_rules": {"critical": [], "major": [], "minor": []},
    }
