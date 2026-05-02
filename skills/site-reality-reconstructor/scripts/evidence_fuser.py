#!/usr/bin/env python3.11
"""
Evidence Fuser — Fusiona evidencia de múltiples fuentes por atributo,
resuelve conflictos usando la jerarquía de verdad, e identifica blind spots.
"""

import json
import os

EVIDENCE_HIERARCHY = {
    "user_photo": 1,
    "street_view": 2,
    "satellite": 3,
    "osm": 4,
    "maps_grounding": 5,
    "web_research": 6,
    "inference": 7,
}


async def fuse_evidence(site_info: dict, collected_results: dict, confidence_threshold: float = 0.6) -> dict:
    """Fusiona toda la evidencia recolectada usando GPT-5.4."""
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_API_BASE")
    if not api_key:
        return _fallback_fuse(collected_results, confidence_threshold)

    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    # Compile all observations
    all_observations = []
    for source_name, result in collected_results.items():
        if isinstance(result, dict) and "observations" in result:
            for obs in result["observations"]:
                obs["_source_name"] = source_name
                all_observations.append(obs)

    # Prepare context for GPT-5.4
    obs_summary = json.dumps(all_observations, indent=1, ensure_ascii=False, default=str)

    prompt = f"""Eres un experto en reconstrucción de realidad urbana. Tu trabajo es fusionar evidencia de múltiples fuentes sobre el sitio "{site_info["name"]}" (coordenadas: {site_info["lat"]}, {site_info["lng"]}).

## Jerarquía de Verdad (mayor rango = más confiable)
1. Fotos/videos del usuario (user_photo)
2. Street View (street_view)
3. Imagen satelital (satellite)
4. OpenStreetMap (osm)
5. Google Maps Grounding (maps_grounding)
6. Web/noticias (web_research)
7. Inferencia (inference)

## Regla de Conflictos
Cuando hay conflicto entre fuentes, SIEMPRE gana la de mayor rango.
Recencia + visibilidad directa + trazabilidad vencen semántica general.

## Evidencia Recolectada
{obs_summary[:30000]}

## Tu Tarea
Analiza TODA la evidencia y produce un JSON con esta estructura exacta:

{{
  "observations": [
    {{
      "observation_id": "fused_001",
      "category": "building|vegetation|road|infrastructure|empty_lot|parking|other",
      "description": "Descripción factual del elemento",
      "location": {{
        "relative_position": "norte|sur|este|oeste|centro|noreste|etc",
        "distance_m": 0,
        "orientation": "descripción"
      }},
      "attributes": {{
        "height_levels": null,
        "material": null,
        "color": null,
        "condition": null,
        "area_m2": null
      }},
      "confidence": 0.0,
      "evidence_ids": ["source_obs_id"],
      "source_priority": "user_photo|osm|maps_grounding|etc"
    }}
  ],
  "surrounding_context": {{
    "north": {{"description": "", "buildings": "", "heights": "", "land_use": "", "confidence": 0.0, "evidence_ids": []}},
    "south": {{"description": "", "buildings": "", "heights": "", "land_use": "", "confidence": 0.0, "evidence_ids": []}},
    "east": {{"description": "", "buildings": "", "heights": "", "land_use": "", "confidence": 0.0, "evidence_ids": []}},
    "west": {{"description": "", "buildings": "", "heights": "", "land_use": "", "confidence": 0.0, "evidence_ids": []}}
  }},
  "blind_spots": [
    {{
      "zone": "descripción de la zona",
      "status": "confirmed_visible|mapped_not_visible|high_confidence_inferred|low_confidence_inferred|unknown_do_not_detail",
      "reason": "por qué es blind spot",
      "render_policy": "omit|neutral_mass|low_detail_context"
    }}
  ],
  "conflicts_resolved": 0,
  "conflict_details": []
}}

REGLAS CRÍTICAS:
- NO inventes información que no esté en la evidencia
- Si no hay datos para una dirección, marca como blind spot
- Prioriza SIEMPRE la fuente de mayor rango
- Cada observación debe tener evidence_ids trazables
- Confidence debe reflejar la calidad real de la evidencia"""

    try:
        response = client.chat.completions.create(
            model="gpt-5.4",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un sistema de fusión de evidencia geoespacial. Respondes SOLO en JSON válido.",
                },
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=16000,
            response_format={"type": "json_object"},
        )

        text = response.choices[0].message.content
        fused = json.loads(text)
        fused["_fusion_model"] = "gpt-5.4"
        fused["_total_input_observations"] = len(all_observations)
        return fused

    except Exception as e:
        print(f"      GPT-5.4 fusion error: {e}")
        return _fallback_fuse(collected_results, confidence_threshold)


def _fallback_fuse(collected_results: dict, confidence_threshold: float) -> dict:
    """Fusión simple sin LLM — agrupa por fuente y filtra por confianza."""
    all_obs = []
    for source_name, result in collected_results.items():
        if isinstance(result, dict) and "observations" in result:
            for obs in result["observations"]:
                if obs.get("confidence", 0) >= confidence_threshold:
                    all_obs.append(obs)

    return {
        "observations": all_obs,
        "surrounding_context": {
            "north": {"description": "Sin datos suficientes", "confidence": 0.0},
            "south": {"description": "Sin datos suficientes", "confidence": 0.0},
            "east": {"description": "Sin datos suficientes", "confidence": 0.0},
            "west": {"description": "Sin datos suficientes", "confidence": 0.0},
        },
        "blind_spots": [
            {
                "zone": "Todo el contexto",
                "status": "low_confidence_inferred",
                "reason": "Fusión sin LLM",
                "render_policy": "neutral_mass",
            }
        ],
        "conflicts_resolved": 0,
        "_fusion_model": "fallback_simple",
    }
