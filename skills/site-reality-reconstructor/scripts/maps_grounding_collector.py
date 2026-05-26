#!/usr/bin/env python3.11
"""
Maps Grounding Collector — Usa Gemini con Google Maps Grounding
para obtener información semántica de negocios y lugares alrededor del sitio.
"""

import json
import os
from pathlib import Path


async def collect_maps_grounding(site_info: dict, evidence_dir: Path) -> dict:
    """Recolecta datos de Google Maps via Gemini Maps Grounding."""
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"source": "maps_grounding", "observations": [], "error": "No GEMINI_API_KEY"}

    client = genai.Client(api_key=api_key)
    observations = []
    raw_responses = []

    lat = site_info["lat"]
    lng = site_info["lng"]
    name = site_info["name"]

    # Queries diseñadas para extraer contexto real del entorno
    queries = [
        f"¿Qué negocios, tiendas, restaurantes y establecimientos hay alrededor de {name}? Describe cada uno con su nombre, tipo y ubicación relativa.",
        f"¿Qué edificios, construcciones y estructuras importantes hay cerca de {name}? Incluye alturas aproximadas si es posible.",
        f"¿Hay terrenos baldíos, estacionamientos, parques o áreas verdes cerca de {name}? Describe el estado actual del entorno.",
        f"¿Qué tipo de zona residencial rodea a {name}? ¿Son casas de 1-2 pisos, departamentos, o edificios altos? Describe la tipología.",
        f"¿Cuáles son las calles y avenidas principales alrededor de {name}? ¿Hay transporte público, paradas de autobús?",
    ]

    for i, query in enumerate(queries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_maps=types.GoogleMaps())],
                    tool_config=types.ToolConfig(
                        retrieval_config=types.RetrievalConfig(lat_lng=types.LatLng(latitude=lat, longitude=lng))
                    ),
                ),
            )

            text = response.text if response.text else ""
            raw_entry = {"query": query, "response": text, "sources": []}

            # Extract grounding sources
            if response.candidates and response.candidates[0].grounding_metadata:
                gm = response.candidates[0].grounding_metadata
                if gm.grounding_chunks:
                    for chunk in gm.grounding_chunks:
                        if hasattr(chunk, "maps") and chunk.maps:
                            source = {
                                "title": chunk.maps.title if hasattr(chunk.maps, "title") else None,
                                "uri": chunk.maps.uri if hasattr(chunk.maps, "uri") else None,
                                "place_id": chunk.maps.place_id if hasattr(chunk.maps, "place_id") else None,
                            }
                            raw_entry["sources"].append(source)

                            # Create observation from each grounded place
                            obs = {
                                "observation_id": f"grounding_{i}_{len(observations)}",
                                "category": "infrastructure",
                                "source": "maps_grounding",
                                "description": f"{source.get('title', 'Lugar')} — encontrado via Maps Grounding",
                                "attributes": {
                                    "name": source.get("title"),
                                    "maps_uri": source.get("uri"),
                                    "place_id": source.get("place_id"),
                                    "query_context": query[:80],
                                },
                                "confidence": 0.8,
                            }
                            observations.append(obs)

            # Also create a narrative observation from the full response
            if text:
                obs = {
                    "observation_id": f"grounding_narrative_{i}",
                    "category": "context",
                    "source": "maps_grounding",
                    "description": text[:500],
                    "attributes": {
                        "full_response": text,
                        "query": query,
                        "sources_count": len(raw_entry["sources"]),
                    },
                    "confidence": 0.75,
                }
                observations.append(obs)

            raw_responses.append(raw_entry)
            print(f"      Grounding query {i + 1}/5: {len(raw_entry['sources'])} fuentes Maps")

        except Exception as e:
            print(f"      Grounding query {i + 1}/5 error: {str(e)[:80]}")
            raw_responses.append({"query": query, "error": str(e)})

    # Save raw data
    with open(evidence_dir / "maps_grounding_raw.json", "w") as f:
        json.dump(raw_responses, f, indent=2, ensure_ascii=False, default=str)

    return {
        "source": "maps_grounding",
        "observations": observations,
        "summary": {
            "queries_sent": len(queries),
            "total_places_found": sum(len(r.get("sources", [])) for r in raw_responses),
        },
    }
