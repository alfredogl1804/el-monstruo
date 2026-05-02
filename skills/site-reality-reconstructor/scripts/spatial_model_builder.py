#!/usr/bin/env python3.11
"""
Spatial Model Builder — Mezclador maestro de todas las fuentes.
Construye un modelo espacial unificado del sitio combinando:
- Fotos del usuario (clasificadas por zona)
- Renders/SketchUp existentes
- OSM footprints
- Google Maps Grounding
- Redes sociales (Instagram, YouTube, Google Images)
- Investigación web (Perplexity)
- Análisis visual (Gemini Vision)

Produce un Spatial Reality Model (SRM) que es la base para el SRD.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# ── Evidence Hierarchy ───────────────────────────────────────────────────────

EVIDENCE_HIERARCHY = {
    # Rank 1: Direct visual evidence from user
    "user_photo": {"rank": 1, "label": "Foto del usuario", "max_confidence": 0.95},
    # Rank 2: Technical documents
    "pdf_plan": {"rank": 2, "label": "Plano técnico PDF", "max_confidence": 0.92},
    "sketchup_model": {"rank": 3, "label": "Modelo SketchUp", "max_confidence": 0.88},
    "existing_render": {"rank": 4, "label": "Render existente del proyecto", "max_confidence": 0.85},
    # Rank 3: Verified external sources
    "street_view": {"rank": 5, "label": "Google Street View", "max_confidence": 0.82},
    "satellite": {"rank": 6, "label": "Imagen satelital", "max_confidence": 0.80},
    "youtube_video": {"rank": 7, "label": "Video de YouTube", "max_confidence": 0.75},
    # Rank 4: Structured data
    "osm": {"rank": 8, "label": "OpenStreetMap", "max_confidence": 0.72},
    "maps_grounding": {"rank": 9, "label": "Google Maps Grounding", "max_confidence": 0.70},
    # Rank 5: Unverified web sources
    "google_images_search": {"rank": 10, "label": "Google Images", "max_confidence": 0.65},
    "instagram_search": {"rank": 11, "label": "Instagram/TikTok", "max_confidence": 0.60},
    "web_research": {"rank": 12, "label": "Investigación web", "max_confidence": 0.58},
    # Rank 6: Inference
    "inference": {"rank": 13, "label": "Inferencia", "max_confidence": 0.40},
}


# ── Zone Definitions ─────────────────────────────────────────────────────────

CARDINAL_ZONES = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
POSITION_RINGS = ["interior", "perimeter", "exterior", "far"]


def _get_all_zones():
    """Generate all possible zone combinations."""
    zones = ["interior"]
    for cardinal in CARDINAL_ZONES:
        for position in ["perimeter", "exterior"]:
            zones.append(f"{cardinal}_{position}")
    zones.append("unknown")
    return zones


# ── Main Builder ─────────────────────────────────────────────────────────────


async def build_spatial_model(
    site_info: dict,
    collected_results: dict,
    output_dir: str,
) -> dict:
    """
    Build the unified Spatial Reality Model from ALL collected evidence.

    Args:
        site_info: Site metadata (name, lat, lng, radius)
        collected_results: Dict with results from all collectors
            Keys: "osm", "maps_grounding", "web_research", "user_photos",
                  "social_media", "sketchup", "visual_analysis"
        output_dir: Where to save the model
    """
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_API_BASE")
    if not api_key:
        return _build_simple_model(site_info, collected_results, output_dir)

    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Aggregate all observations ────────────────────────────────
    print("  [1/4] Agregando observaciones de todas las fuentes...")

    all_observations = []
    source_stats = {}

    for source_name, result in collected_results.items():
        if isinstance(result, dict) and "observations" in result:
            obs_list = result["observations"]
            all_observations.extend(obs_list)
            source_stats[source_name] = {
                "count": len(obs_list),
                "rank": EVIDENCE_HIERARCHY.get(
                    obs_list[0].get("source", "inference") if obs_list else "inference", {"rank": 99}
                ).get("rank", 99),
            }

    print(f"    Total: {len(all_observations)} observaciones de {len(source_stats)} fuentes")

    # ── Step 2: Classify observations by zone ─────────────────────────────
    print("  [2/4] Clasificando por zona espacial...")

    zone_observations = {}
    for zone in _get_all_zones():
        zone_observations[zone] = []

    for obs in all_observations:
        # Try to assign to a zone
        zone = "unknown"
        attrs = obs.get("attributes", {})

        if attrs.get("zone"):
            zone = attrs["zone"]
        elif attrs.get("relative_position"):
            # Map relative positions to zones
            pos = attrs["relative_position"].lower()
            if "north" in pos or "norte" in pos:
                zone = "N_exterior"
            elif "south" in pos or "sur" in pos:
                zone = "S_exterior"
            elif "east" in pos or "este" in pos:
                zone = "E_exterior"
            elif "west" in pos or "oeste" in pos:
                zone = "W_exterior"
            elif "interior" in pos or "dentro" in pos:
                zone = "interior"

        if zone in zone_observations:
            zone_observations[zone].append(obs)
        else:
            zone_observations["unknown"].append(obs)

    # ── Step 3: Build zone-by-zone reality with GPT-5.4 ──────────────────
    print("  [3/4] Construyendo modelo espacial con GPT-5.4...")

    # Prepare condensed evidence per zone
    zone_evidence = {}
    for zone, obs_list in zone_observations.items():
        if obs_list:
            # Sort by source rank (higher rank = more reliable)
            sorted_obs = sorted(
                obs_list,
                key=lambda o: EVIDENCE_HIERARCHY.get(o.get("source", "inference"), {"rank": 99}).get("rank", 99),
            )
            zone_evidence[zone] = sorted_obs

    evidence_json = json.dumps(zone_evidence, indent=1, ensure_ascii=False, default=str)

    prompt = f"""Eres un arquitecto de modelos espaciales. Tu trabajo es construir un MODELO ESPACIAL UNIFICADO del sitio "{site_info["name"]}" (coordenadas: {site_info["lat"]}, {site_info["lng"]}, radio: {site_info["radius_m"]}m).

## JERARQUÍA DE VERDAD (rank 1 = más confiable)
{json.dumps(EVIDENCE_HIERARCHY, indent=1, ensure_ascii=False)}

## REGLAS DE FUSIÓN
1. Cuando hay conflicto entre fuentes, SIEMPRE gana la de rank más bajo (más confiable)
2. Las fotos del usuario son la verdad absoluta — nunca se contradicen
3. Los planos técnicos y modelos SketchUp definen dimensiones exactas
4. Los renders existentes definen la intención de diseño
5. OSM y Maps Grounding definen el contexto urbano
6. Redes sociales y web complementan con contexto temporal
7. Lo que NO tiene evidencia = blind spot (no inventar)

## EVIDENCIA POR ZONA
{evidence_json[:40000]}

## ESTADÍSTICAS DE FUENTES
{json.dumps(source_stats, indent=1)}

## GENERA EL SPATIAL REALITY MODEL (SRM)
Responde en JSON con esta estructura:

{{
  "model_metadata": {{
    "name": "{site_info["name"]}",
    "coordinates": {{"lat": {site_info["lat"]}, "lng": {site_info["lng"]}}},
    "radius_m": {site_info["radius_m"]},
    "model_date": "{datetime.now().isoformat()}",
    "total_observations": {len(all_observations)},
    "sources_used": {len(source_stats)},
    "dominant_source": "la fuente con más observaciones"
  }},

  "site_core": {{
    "description": "Descripción completa del sitio principal",
    "footprint": {{
      "shape": "oval|rectangular|irregular|etc",
      "estimated_area_m2": 0,
      "max_height_m": 0,
      "levels": 0
    }},
    "key_features": [
      {{"feature": "nombre", "description": "detalle", "evidence_source": "fuente", "confidence": 0.0}}
    ],
    "materials": ["lista de materiales confirmados"],
    "colors": ["lista de colores confirmados"]
  }},

  "zones": {{
    "N": {{
      "reality_description": "qué hay realmente al norte",
      "elements": [
        {{
          "type": "building|empty_lot|parking|road|vegetation|commercial|residential|other",
          "description": "descripción factual",
          "height_levels": null,
          "material": null,
          "condition": null,
          "evidence_sources": ["lista de fuentes"],
          "confidence": 0.0
        }}
      ],
      "ground_surface": "asphalt|concrete|dirt|grass|gravel|mixed",
      "vegetation": "none|sparse|moderate|dense",
      "coverage_quality": "high|medium|low|none",
      "evidence_count": 0
    }},
    "NE": {{}},
    "E": {{}},
    "SE": {{}},
    "S": {{}},
    "SW": {{}},
    "W": {{}},
    "NW": {{}}
  }},

  "connectivity": {{
    "main_roads": [
      {{"name": "nombre", "type": "avenida|calle|boulevard", "direction": "N-S|E-W|etc", "lanes": 0, "surface": "tipo"}}
    ],
    "access_points": [
      {{"name": "nombre", "location": "cardinal", "type": "vehicular|peatonal|mixto"}}
    ],
    "parking": [
      {{"location": "cardinal", "type": "asphalt|dirt|structured", "estimated_capacity": 0}}
    ]
  }},

  "adjacent_structures": [
    {{
      "name": "nombre",
      "type": "commercial|residential|institutional|vacant|park|other",
      "zone": "cardinal",
      "distance_m": 0,
      "height_levels": 0,
      "description": "descripción",
      "evidence_source": "fuente",
      "confidence": 0.0
    }}
  ],

  "blind_spots": [
    {{
      "zone": "cardinal o descripción",
      "coverage_quality": "none|low",
      "reason": "por qué no hay datos",
      "render_policy": "omit|neutral_mass|low_detail|ask_user",
      "suggested_action": "qué se podría hacer para llenar el blind spot"
    }}
  ],

  "confidence_map": {{
    "interior": 0.0,
    "N": 0.0, "NE": 0.0, "E": 0.0, "SE": 0.0,
    "S": 0.0, "SW": 0.0, "W": 0.0, "NW": 0.0,
    "overall": 0.0
  }},

  "render_constraints": {{
    "hard_constraints": [
      {{"rule": "descripción de restricción dura", "zone": "afectada", "evidence": "fuente"}}
    ],
    "soft_constraints": [
      {{"rule": "descripción de restricción suave", "zone": "afectada", "evidence": "fuente"}}
    ],
    "prohibited_elements": [
      {{"element": "qué NO poner", "zone": "dónde", "reason": "por qué"}}
    ]
  }}
}}

REGLAS CRÍTICAS:
1. NO inventes NADA que no esté en la evidencia
2. Si una zona no tiene evidencia, marca confidence 0.0 y agrega a blind_spots
3. Cada elemento debe tener evidence_sources trazables
4. Las hard_constraints son INQUEBRANTABLES — si se violan, el render es inválido
5. Los prohibited_elements son cosas que la IA tiende a inventar pero NO existen"""

    try:
        response = client.chat.completions.create(
            model="gpt-5.4",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un sistema de modelado espacial. Respondes SOLO en JSON válido. Tu modelo debe ser la representación más fiel posible de la realidad basada en la evidencia disponible.",
                },
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=16000,
            response_format={"type": "json_object"},
        )

        text = response.choices[0].message.content
        model = json.loads(text)

    except Exception as e:
        print(f"    GPT-5.4 error: {e}")
        model = _build_simple_model(site_info, collected_results, output_dir)

    # ── Step 4: Save and return ───────────────────────────────────────────
    print("  [4/4] Guardando modelo espacial...")

    model_path = output_path / "spatial_model.json"
    with open(model_path, "w") as f:
        json.dump(model, f, indent=2, ensure_ascii=False, default=str)

    # Also save a human-readable summary
    summary_path = output_path / "spatial_model_summary.md"
    _write_summary(model, summary_path, site_info)

    # Save zone evidence for debugging
    evidence_path = output_path / "zone_evidence.json"
    with open(evidence_path, "w") as f:
        json.dump(
            {
                "source_stats": source_stats,
                "zone_counts": {z: len(obs) for z, obs in zone_observations.items() if obs},
                "total_observations": len(all_observations),
            },
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    print(f"\n  ✓ Modelo espacial guardado: {model_path}")
    print(f"  ✓ Resumen: {summary_path}")

    confidence = model.get("confidence_map", {}).get("overall", 0)
    blind_count = len(model.get("blind_spots", []))
    hard_count = len(model.get("render_constraints", {}).get("hard_constraints", []))

    print(f"  ✓ Confianza global: {confidence:.0%}")
    print(f"  ✓ Blind spots: {blind_count}")
    print(f"  ✓ Restricciones duras: {hard_count}")

    return model


def _write_summary(model: dict, path: Path, site_info: dict):
    """Write a human-readable summary of the spatial model."""
    lines = [
        f"# Modelo Espacial: {site_info['name']}",
        f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Coordenadas:** {site_info['lat']}, {site_info['lng']}",
        f"**Radio:** {site_info['radius_m']}m",
        "",
        "## Sitio Principal",
        model.get("site_core", {}).get("description", "Sin descripción"),
        "",
        "## Contexto por Zona",
    ]

    zones = model.get("zones", {})
    for cardinal in CARDINAL_ZONES:
        zone = zones.get(cardinal, {})
        conf = model.get("confidence_map", {}).get(cardinal, 0)
        desc = zone.get("reality_description", "Sin datos")
        lines.append(f"### {cardinal} (confianza: {conf:.0%})")
        lines.append(desc)
        lines.append("")

    lines.append("## Blind Spots")
    for bs in model.get("blind_spots", []):
        lines.append(f"- **{bs.get('zone', '?')}**: {bs.get('reason', '?')} → {bs.get('render_policy', '?')}")

    lines.append("")
    lines.append("## Restricciones Duras para Renders")
    for hc in model.get("render_constraints", {}).get("hard_constraints", []):
        lines.append(f"- **{hc.get('zone', '?')}**: {hc.get('rule', '?')}")

    lines.append("")
    lines.append("## Elementos Prohibidos")
    for pe in model.get("render_constraints", {}).get("prohibited_elements", []):
        lines.append(f"- **{pe.get('zone', '?')}**: NO poner {pe.get('element', '?')} — {pe.get('reason', '?')}")

    with open(path, "w") as f:
        f.write("\n".join(lines))


def _build_simple_model(site_info: dict, collected_results: dict, output_dir: str) -> dict:
    """Fallback: build a simple model without LLM."""
    return {
        "model_metadata": {
            "name": site_info["name"],
            "coordinates": {"lat": site_info["lat"], "lng": site_info["lng"]},
            "radius_m": site_info["radius_m"],
            "model_date": datetime.now().isoformat(),
            "total_observations": sum(
                len(r.get("observations", [])) for r in collected_results.values() if isinstance(r, dict)
            ),
            "sources_used": len(collected_results),
            "dominant_source": "fallback",
        },
        "site_core": {"description": "Modelo generado sin LLM — revisar manualmente"},
        "zones": {c: {"reality_description": "Sin datos LLM", "coverage_quality": "none"} for c in CARDINAL_ZONES},
        "blind_spots": [{"zone": "all", "reason": "LLM no disponible", "render_policy": "ask_user"}],
        "confidence_map": {c: 0.0 for c in ["interior"] + CARDINAL_ZONES + ["overall"]},
        "render_constraints": {"hard_constraints": [], "soft_constraints": [], "prohibited_elements": []},
    }
