#!/usr/bin/env python3.11
"""
Site Resolver — Normaliza coordenadas, radio, orientación y vistas objetivo.
"""

import math
from datetime import date


def resolve_site(lat: float, lng: float, radius: int, name: str, target_date: str = None, views: list = None) -> dict:
    """Normaliza la información del sitio para el pipeline."""

    target_date = target_date or date.today().isoformat()
    views = views or ["N", "S", "E", "W", "aerial"]

    # Calcular bounding box
    lat_delta = radius / 111320
    lng_delta = radius / (111320 * math.cos(math.radians(lat)))

    bbox = {
        "south": round(lat - lat_delta, 6),
        "north": round(lat + lat_delta, 6),
        "west": round(lng - lng_delta, 6),
        "east": round(lng + lng_delta, 6),
    }

    # Calcular puntos cardinales a distancia del radio
    cardinal_points = {
        "N": {"lat": round(lat + lat_delta, 6), "lng": round(lng, 6)},
        "S": {"lat": round(lat - lat_delta, 6), "lng": round(lng, 6)},
        "E": {"lat": round(lat, 6), "lng": round(lng + lng_delta, 6)},
        "W": {"lat": round(lat, 6), "lng": round(lng - lng_delta, 6)},
    }

    return {
        "name": name,
        "lat": lat,
        "lng": lng,
        "radius_m": radius,
        "target_date": target_date,
        "reconstruction_date": date.today().isoformat(),
        "views": views,
        "bbox": bbox,
        "cardinal_points": cardinal_points,
        "bbox_overpass": f"{bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']}",
    }
