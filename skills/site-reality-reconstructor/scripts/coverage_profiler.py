#!/usr/bin/env python3.11
"""
Coverage Profiler — Evalúa disponibilidad de fuentes por sitio.
Determina el semáforo (green/yellow/red) antes de recolectar.
"""

import os

import requests


async def profile_coverage(site_info: dict, user_photos_dir: str = None) -> dict:
    """Evalúa qué fuentes están disponibles para el sitio."""

    coverage = {
        "site_name": site_info["name"],
        "lat": site_info["lat"],
        "lng": site_info["lng"],
        "radius_m": site_info["radius_m"],
        "sources": {},
        "user_photos_count": 0,
        "osm_density": "unknown",
        "semaphore": "yellow",
        "score": 0.0,
    }

    score = 0.0

    # 1. Check user photos
    if user_photos_dir and os.path.isdir(user_photos_dir):
        photo_exts = (".jpg", ".jpeg", ".png", ".webp", ".heic")
        photos = [f for f in os.listdir(user_photos_dir) if f.lower().endswith(photo_exts)]
        coverage["user_photos_count"] = len(photos)
        coverage["sources"]["user_photos"] = {
            "available": len(photos) > 0,
            "count": len(photos),
            "quality": "high" if len(photos) >= 8 else "medium" if len(photos) >= 4 else "low",
        }
        if len(photos) >= 8:
            score += 0.35
        elif len(photos) >= 4:
            score += 0.25
        elif len(photos) > 0:
            score += 0.15
    else:
        coverage["sources"]["user_photos"] = {"available": False, "count": 0}

    # 2. Check OSM density
    try:
        bbox = site_info["bbox_overpass"]
        query = f"""
        [out:json][timeout:15];
        (
          way["building"]({bbox});
          node["amenity"]({bbox});
          way["highway"]({bbox});
        );
        out count;
        """
        resp = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=20,
        )
        if resp.status_code == 200:
            data = resp.json()
            total = data.get("elements", [{}])[0].get("tags", {}).get("total", 0)
            total = int(total) if total else 0
            if total > 100:
                coverage["osm_density"] = "high"
                score += 0.2
            elif total > 30:
                coverage["osm_density"] = "medium"
                score += 0.15
            elif total > 5:
                coverage["osm_density"] = "low"
                score += 0.05
            else:
                coverage["osm_density"] = "very_low"
            coverage["sources"]["osm"] = {"available": True, "element_count": total}
    except Exception as e:
        coverage["sources"]["osm"] = {"available": False, "error": str(e)}

    # 3. Check Gemini Maps Grounding availability
    gemini_key = os.environ.get("GEMINI_API_KEY")
    coverage["sources"]["maps_grounding"] = {
        "available": bool(gemini_key),
        "api_key_present": bool(gemini_key),
    }
    if gemini_key:
        score += 0.15

    # 4. Check Perplexity availability
    sonar_key = os.environ.get("SONAR_API_KEY")
    coverage["sources"]["perplexity"] = {
        "available": bool(sonar_key),
        "api_key_present": bool(sonar_key),
    }
    if sonar_key:
        score += 0.1

    # 5. Check OpenAI availability
    openai_key = os.environ.get("OPENAI_API_KEY")
    coverage["sources"]["openai"] = {
        "available": bool(openai_key),
        "api_key_present": bool(openai_key),
    }
    if openai_key:
        score += 0.1

    # 6. Browser always available in Manus
    coverage["sources"]["browser"] = {"available": True, "note": "Google Maps/Earth/Street View via browser"}
    score += 0.1

    # Calculate semaphore
    coverage["score"] = round(score, 2)
    if score >= 0.7:
        coverage["semaphore"] = "green"
    elif score >= 0.4:
        coverage["semaphore"] = "yellow"
    else:
        coverage["semaphore"] = "red"

    return coverage
