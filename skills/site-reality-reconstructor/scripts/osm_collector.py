#!/usr/bin/env python3.11
"""
OSM Collector — Recolecta datos de OpenStreetMap via Overpass API.
Obtiene footprints de edificios, vías, uso de suelo, POIs, vegetación.
"""
import asyncio
import json
import requests
from pathlib import Path

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def _query_overpass(query: str, timeout: int = 30) -> dict:
    """Ejecuta una query Overpass y retorna JSON."""
    resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


async def collect_osm(site_info: dict, evidence_dir: Path) -> dict:
    """Recolecta datos OSM del sitio y alrededores."""
    bbox = site_info["bbox_overpass"]
    observations = []
    raw_data = {}

    # 1. Buildings with attributes
    try:
        query = f"""
        [out:json][timeout:30];
        (
          way["building"]({bbox});
          relation["building"]({bbox});
        );
        out body;
        >;
        out skel qt;
        """
        data = _query_overpass(query)
        buildings = [e for e in data.get("elements", []) if e.get("type") in ("way", "relation") and e.get("tags")]
        raw_data["buildings"] = buildings

        for b in buildings:
            tags = b.get("tags", {})
            obs = {
                "observation_id": f"osm_building_{b['id']}",
                "category": "building",
                "source": "osm",
                "description": tags.get("name", f"Edificio {tags.get('building', 'yes')}"),
                "attributes": {
                    "building_type": tags.get("building", "yes"),
                    "height_levels": tags.get("building:levels", tags.get("levels", None)),
                    "height_m": tags.get("height", None),
                    "name": tags.get("name", None),
                    "amenity": tags.get("amenity", None),
                    "shop": tags.get("shop", None),
                    "addr_street": tags.get("addr:street", None),
                },
                "confidence": 0.7,
            }
            observations.append(obs)

        print(f"      OSM: {len(buildings)} edificios encontrados")
    except Exception as e:
        print(f"      OSM buildings error: {e}")

    # Small delay to avoid rate limiting
    await asyncio.sleep(2)

    # 2. Roads and highways
    try:
        query = f"""
        [out:json][timeout:30];
        (
          way["highway"]({bbox});
        );
        out body;
        >;
        out skel qt;
        """
        data = _query_overpass(query)
        roads = [e for e in data.get("elements", []) if e.get("type") == "way" and e.get("tags")]
        raw_data["roads"] = roads

        for r in roads:
            tags = r.get("tags", {})
            obs = {
                "observation_id": f"osm_road_{r['id']}",
                "category": "road",
                "source": "osm",
                "description": tags.get("name", f"Vía {tags.get('highway', 'unknown')}"),
                "attributes": {
                    "highway_type": tags.get("highway", "unknown"),
                    "name": tags.get("name", None),
                    "lanes": tags.get("lanes", None),
                    "surface": tags.get("surface", None),
                    "oneway": tags.get("oneway", None),
                },
                "confidence": 0.75,
            }
            observations.append(obs)

        print(f"      OSM: {len(roads)} vías encontradas")
    except Exception as e:
        print(f"      OSM roads error: {e}")

    # Small delay to avoid rate limiting
    await asyncio.sleep(2)

    # 3. Land use
    try:
        query = f"""
        [out:json][timeout:30];
        (
          way["landuse"]({bbox});
          relation["landuse"]({bbox});
          way["leisure"]({bbox});
          way["natural"]({bbox});
        );
        out body;
        >;
        out skel qt;
        """
        data = _query_overpass(query)
        landuse = [e for e in data.get("elements", []) if e.get("type") in ("way", "relation") and e.get("tags")]
        raw_data["landuse"] = landuse

        for lu in landuse:
            tags = lu.get("tags", {})
            cat = "vegetation" if tags.get("natural") or tags.get("landuse") in ("forest", "grass", "meadow") else "other"
            obs = {
                "observation_id": f"osm_landuse_{lu['id']}",
                "category": cat,
                "source": "osm",
                "description": tags.get("name", f"Uso: {tags.get('landuse', tags.get('leisure', tags.get('natural', 'unknown')))}"),
                "attributes": {
                    "landuse": tags.get("landuse", None),
                    "leisure": tags.get("leisure", None),
                    "natural": tags.get("natural", None),
                    "name": tags.get("name", None),
                },
                "confidence": 0.65,
            }
            observations.append(obs)

        print(f"      OSM: {len(landuse)} áreas de uso de suelo")
    except Exception as e:
        print(f"      OSM landuse error: {e}")

    # Small delay to avoid rate limiting
    await asyncio.sleep(2)

    # 4. POIs (amenities, shops, etc.)
    try:
        query = f"""
        [out:json][timeout:30];
        (
          node["amenity"]({bbox});
          node["shop"]({bbox});
          node["tourism"]({bbox});
          node["sport"]({bbox});
        );
        out body;
        """
        data = _query_overpass(query)
        pois = [e for e in data.get("elements", []) if e.get("tags")]
        raw_data["pois"] = pois

        for p in pois:
            tags = p.get("tags", {})
            obs = {
                "observation_id": f"osm_poi_{p['id']}",
                "category": "infrastructure",
                "source": "osm",
                "description": tags.get("name", f"POI: {tags.get('amenity', tags.get('shop', 'unknown'))}"),
                "attributes": {
                    "amenity": tags.get("amenity", None),
                    "shop": tags.get("shop", None),
                    "tourism": tags.get("tourism", None),
                    "sport": tags.get("sport", None),
                    "name": tags.get("name", None),
                    "lat": p.get("lat"),
                    "lon": p.get("lon"),
                },
                "confidence": 0.7,
            }
            observations.append(obs)

        print(f"      OSM: {len(pois)} POIs encontrados")
    except Exception as e:
        print(f"      OSM POIs error: {e}")

    # Save raw data
    with open(evidence_dir / "osm_raw.json", "w") as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False, default=str)

    return {
        "source": "osm_overpass",
        "observations": observations,
        "summary": {
            "buildings": len(raw_data.get("buildings", [])),
            "roads": len(raw_data.get("roads", [])),
            "landuse": len(raw_data.get("landuse", [])),
            "pois": len(raw_data.get("pois", [])),
        },
    }
