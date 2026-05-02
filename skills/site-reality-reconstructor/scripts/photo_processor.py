#!/usr/bin/env python3.11
"""
Photo Processor — Procesamiento masivo de fotos del usuario.
Extrae EXIF/GPS, clasifica por orientación y zona, agrupa por cobertura espacial,
y analiza cada foto con Gemini Vision para extraer observaciones del entorno real.
"""

import asyncio
import json
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import ExifTags, Image

# ── EXIF Extraction ──────────────────────────────────────────────────────────


def _dms_to_decimal(dms_tuple, ref: str) -> Optional[float]:
    """Convert EXIF DMS (degrees, minutes, seconds) to decimal degrees."""
    try:
        if isinstance(dms_tuple, (list, tuple)) and len(dms_tuple) == 3:
            d, m, s = dms_tuple
            # Handle IFDRational or tuple format
            if hasattr(d, "numerator"):
                d = d.numerator / d.denominator if d.denominator else 0
            if hasattr(m, "numerator"):
                m = m.numerator / m.denominator if m.denominator else 0
            if hasattr(s, "numerator"):
                s = s.numerator / s.denominator if s.denominator else 0
            elif isinstance(d, tuple):
                d = d[0] / d[1] if d[1] else 0
                m = m[0] / m[1] if m[1] else 0
                s = s[0] / s[1] if s[1] else 0

            decimal = float(d) + float(m) / 60 + float(s) / 3600
            if ref in ("S", "W"):
                decimal = -decimal
            return decimal
    except Exception:
        pass
    return None


def _extract_exif(image_path: str) -> dict:
    """Extract EXIF metadata from an image file."""
    result = {
        "has_gps": False,
        "lat": None,
        "lng": None,
        "altitude": None,
        "compass_heading": None,
        "timestamp": None,
        "camera_make": None,
        "camera_model": None,
        "focal_length": None,
        "orientation": None,
        "width": None,
        "height": None,
    }

    try:
        img = Image.open(image_path)
        result["width"] = img.width
        result["height"] = img.height

        exif_data = img._getexif()
        if not exif_data:
            return result

        # Parse standard EXIF tags
        for tag_id, value in exif_data.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            if tag == "Make":
                result["camera_make"] = str(value)
            elif tag == "Model":
                result["camera_model"] = str(value)
            elif tag == "DateTimeOriginal":
                result["timestamp"] = str(value)
            elif tag == "FocalLength":
                if hasattr(value, "numerator"):
                    result["focal_length"] = value.numerator / value.denominator if value.denominator else None
                elif isinstance(value, tuple) and len(value) == 2:
                    result["focal_length"] = value[0] / value[1] if value[1] else None
            elif tag == "Orientation":
                result["orientation"] = int(value)

        # Parse GPS tags
        gps_info = exif_data.get(34853)  # GPSInfo tag
        if gps_info:
            gps_tags = {}
            for key, val in gps_info.items():
                tag = ExifTags.GPSTAGS.get(key, key)
                gps_tags[tag] = val

            # Latitude
            if "GPSLatitude" in gps_tags and "GPSLatitudeRef" in gps_tags:
                lat = _dms_to_decimal(gps_tags["GPSLatitude"], gps_tags["GPSLatitudeRef"])
                if lat is not None:
                    result["lat"] = lat
                    result["has_gps"] = True

            # Longitude
            if "GPSLongitude" in gps_tags and "GPSLongitudeRef" in gps_tags:
                lng = _dms_to_decimal(gps_tags["GPSLongitude"], gps_tags["GPSLongitudeRef"])
                if lng is not None:
                    result["lng"] = lng

            # Altitude
            if "GPSAltitude" in gps_tags:
                alt = gps_tags["GPSAltitude"]
                if hasattr(alt, "numerator"):
                    result["altitude"] = alt.numerator / alt.denominator if alt.denominator else None
                elif isinstance(alt, tuple) and len(alt) == 2:
                    result["altitude"] = alt[0] / alt[1] if alt[1] else None

            # Compass heading (direction camera was pointing)
            if "GPSImgDirection" in gps_tags:
                heading = gps_tags["GPSImgDirection"]
                if hasattr(heading, "numerator"):
                    result["compass_heading"] = heading.numerator / heading.denominator if heading.denominator else None
                elif isinstance(heading, tuple) and len(heading) == 2:
                    result["compass_heading"] = heading[0] / heading[1] if heading[1] else None
                elif isinstance(heading, (int, float)):
                    result["compass_heading"] = float(heading)

    except Exception as e:
        result["_exif_error"] = str(e)

    return result


# ── Spatial Classification ───────────────────────────────────────────────────


def _heading_to_cardinal(heading: float) -> str:
    """Convert compass heading to cardinal direction."""
    directions = [
        (0, 22.5, "N"),
        (22.5, 67.5, "NE"),
        (67.5, 112.5, "E"),
        (112.5, 157.5, "SE"),
        (157.5, 202.5, "S"),
        (202.5, 247.5, "SW"),
        (247.5, 292.5, "W"),
        (292.5, 337.5, "NW"),
        (337.5, 360, "N"),
    ]
    for low, high, name in directions:
        if low <= heading < high:
            return name
    return "N"


def _distance_m(lat1, lng1, lat2, lng2) -> float:
    """Haversine distance in meters."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _bearing_from_site(photo_lat, photo_lng, site_lat, site_lng) -> float:
    """Calculate bearing from photo location to site center."""
    phi1 = math.radians(photo_lat)
    phi2 = math.radians(site_lat)
    dlam = math.radians(site_lng - photo_lng)
    x = math.sin(dlam) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def _classify_zone(photo_exif: dict, site_lat: float, site_lng: float, radius_m: float) -> dict:
    """Classify a photo into a spatial zone relative to the site."""
    classification = {
        "zone": "unknown",
        "cardinal_from_site": None,
        "distance_from_site_m": None,
        "looking_direction": None,
        "position": "unknown",  # interior, perimeter, exterior, far
        "quality_score": 0.0,
    }

    if photo_exif.get("has_gps") and photo_exif["lat"] and photo_exif["lng"]:
        dist = _distance_m(photo_exif["lat"], photo_exif["lng"], site_lat, site_lng)
        classification["distance_from_site_m"] = round(dist, 1)

        # Bearing from site center to photo position
        bearing = _bearing_from_site(site_lat, site_lng, photo_exif["lat"], photo_exif["lng"])
        classification["cardinal_from_site"] = _heading_to_cardinal(bearing)

        # Position classification
        if dist < radius_m * 0.3:
            classification["position"] = "interior"
        elif dist < radius_m * 0.7:
            classification["position"] = "perimeter"
        elif dist < radius_m * 1.5:
            classification["position"] = "exterior"
        else:
            classification["position"] = "far"

        # Zone name
        classification["zone"] = f"{classification['cardinal_from_site']}_{classification['position']}"

    # Camera direction
    if photo_exif.get("compass_heading") is not None:
        classification["looking_direction"] = _heading_to_cardinal(photo_exif["compass_heading"])

    # Quality score (0-1)
    score = 0.3  # Base for having a photo
    if photo_exif.get("has_gps"):
        score += 0.3
    if photo_exif.get("compass_heading") is not None:
        score += 0.2
    if photo_exif.get("timestamp"):
        score += 0.1
    w = photo_exif.get("width", 0) or 0
    h = photo_exif.get("height", 0) or 0
    if w * h > 4_000_000:  # > 4MP
        score += 0.1
    classification["quality_score"] = min(score, 1.0)

    return classification


# ── Visual Analysis with Gemini ──────────────────────────────────────────────


async def _analyze_photo_batch(photos: list, site_name: str, batch_size: int = 5) -> list:
    """Analyze a batch of photos with Gemini Vision for spatial content."""
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return [{"error": "No GEMINI_API_KEY"} for _ in photos]

    client = genai.Client(api_key=api_key)
    results = []

    for i in range(0, len(photos), batch_size):
        batch = photos[i : i + batch_size]
        for photo in batch:
            try:
                path = photo["path"]
                exif = photo.get("exif", {})
                zone = photo.get("zone", {})

                context = "Foto tomada"
                if zone.get("position") != "unknown":
                    context += f" desde posición {zone['position']}"
                if zone.get("cardinal_from_site"):
                    context += f" ({zone['cardinal_from_site']} del sitio)"
                if zone.get("looking_direction"):
                    context += f", mirando hacia {zone['looking_direction']}"
                if exif.get("timestamp"):
                    context += f", fecha: {exif['timestamp']}"

                prompt = f"""Analiza esta foto del sitio "{site_name}" y su entorno.
Contexto: {context}

Extrae SOLO lo que VES en la imagen. Responde en JSON:
{{
  "scene_type": "interior|exterior|aerial|detail|panoramic",
  "elements_visible": [
    {{
      "type": "building|road|parking|empty_lot|vegetation|signage|infrastructure|vehicle|person|sky|other",
      "description": "descripción factual breve",
      "approximate_height_levels": null,
      "material": null,
      "color": null,
      "condition": "new|good|fair|poor|construction",
      "relative_position": "foreground|midground|background|left|right|center"
    }}
  ],
  "ground_surface": "asphalt|concrete|dirt|grass|gravel|mixed",
  "sky_visible": true,
  "lighting": "day|night|sunset|overcast",
  "notable_text_signs": [],
  "overall_description": "descripción de 1-2 oraciones de lo que muestra la foto"
}}

IMPORTANTE: Solo describe lo que VES. No inventes ni supongas."""

                with open(path, "rb") as f:
                    img_bytes = f.read()

                ext = Path(path).suffix.lower()
                mime = {
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "png": "image/png",
                    "webp": "image/webp",
                    "heic": "image/heic",
                }.get(ext.lstrip("."), "image/jpeg")

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Content(
                            parts=[
                                types.Part(text=prompt),
                                types.Part(inline_data=types.Blob(mime_type=mime, data=img_bytes)),
                            ]
                        )
                    ],
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )

                text = response.text if response.text else "{}"
                analysis = json.loads(text)
                analysis["_photo_file"] = os.path.basename(path)
                results.append(analysis)
                print(
                    f"      Foto {len(results)}/{len(photos)}: {os.path.basename(path)} — {analysis.get('scene_type', '?')}"
                )

            except Exception as e:
                results.append({"error": str(e), "_photo_file": os.path.basename(photo["path"])})
                print(f"      Foto {len(results)}/{len(photos)}: ERROR — {str(e)[:60]}")

        # Rate limit between batches
        if i + batch_size < len(photos):
            await asyncio.sleep(1)

    return results


# ── Main Entry Point ─────────────────────────────────────────────────────────


async def process_photos(
    photo_dir: str,
    site_lat: float,
    site_lng: float,
    site_name: str,
    radius_m: float,
    output_dir: str,
    max_photos: int = 100,
) -> dict:
    """
    Process all photos in a directory:
    1. Extract EXIF/GPS from each
    2. Classify by zone and orientation
    3. Analyze with Gemini Vision
    4. Build a photo catalog with spatial index
    """
    photo_dir = Path(photo_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all image files
    extensions = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".tiff", ".bmp"}
    all_files = sorted([f for f in photo_dir.rglob("*") if f.suffix.lower() in extensions and f.is_file()])

    if not all_files:
        return {"error": "No photos found", "photo_count": 0}

    # Limit photos
    if len(all_files) > max_photos:
        print(f"  Limitando a {max_photos} fotos de {len(all_files)} encontradas")
        all_files = all_files[:max_photos]

    print(f"  Procesando {len(all_files)} fotos...")

    # Step 1: Extract EXIF from all photos
    print("  [1/4] Extrayendo EXIF...")
    photos = []
    gps_count = 0
    heading_count = 0

    for f in all_files:
        exif = _extract_exif(str(f))
        if exif.get("has_gps"):
            gps_count += 1
        if exif.get("compass_heading") is not None:
            heading_count += 1
        photos.append({"path": str(f), "filename": f.name, "exif": exif})

    print(f"    {gps_count}/{len(photos)} con GPS, {heading_count}/{len(photos)} con heading")

    # Step 2: Classify by zone
    print("  [2/4] Clasificando por zona...")
    zone_counts = {}
    for photo in photos:
        zone = _classify_zone(photo["exif"], site_lat, site_lng, radius_m)
        photo["zone"] = zone
        z = zone["zone"]
        zone_counts[z] = zone_counts.get(z, 0) + 1

    print(f"    Zonas: {json.dumps(zone_counts, indent=2)}")

    # Step 3: Analyze with Gemini Vision
    print("  [3/4] Analizando con Gemini Vision...")
    analyses = await _analyze_photo_batch(photos, site_name)

    for photo, analysis in zip(photos, analyses):
        photo["visual_analysis"] = analysis

    # Step 4: Build spatial catalog
    print("  [4/4] Construyendo catálogo espacial...")

    # Group by zone
    zones = {}
    for photo in photos:
        z = photo["zone"]["zone"]
        if z not in zones:
            zones[z] = {
                "zone_name": z,
                "position": photo["zone"]["position"],
                "cardinal": photo["zone"].get("cardinal_from_site"),
                "photos": [],
                "elements_found": [],
            }
        zones[z]["photos"].append(
            {
                "filename": photo["filename"],
                "quality_score": photo["zone"]["quality_score"],
                "looking_direction": photo["zone"].get("looking_direction"),
                "distance_m": photo["zone"].get("distance_from_site_m"),
                "timestamp": photo["exif"].get("timestamp"),
            }
        )

        # Aggregate elements from visual analysis
        if "elements_visible" in photo.get("visual_analysis", {}):
            for elem in photo["visual_analysis"]["elements_visible"]:
                zones[z]["elements_found"].append(
                    {
                        **elem,
                        "_from_photo": photo["filename"],
                    }
                )

    # Build the catalog
    catalog = {
        "site_name": site_name,
        "site_coordinates": {"lat": site_lat, "lng": site_lng},
        "radius_m": radius_m,
        "processing_date": datetime.now().isoformat(),
        "summary": {
            "total_photos": len(photos),
            "with_gps": gps_count,
            "with_heading": heading_count,
            "zones_covered": len(zones),
            "zone_distribution": zone_counts,
        },
        "zones": zones,
        "coverage_assessment": {
            "interior": any(z.get("position") == "interior" for z in zones.values()),
            "perimeter_N": any("N_" in z.get("zone_name", "") for z in zones.values()),
            "perimeter_S": any("S_" in z.get("zone_name", "") for z in zones.values()),
            "perimeter_E": any("E_" in z.get("zone_name", "") for z in zones.values()),
            "perimeter_W": any("W_" in z.get("zone_name", "") for z in zones.values()),
            "exterior": any(z.get("position") == "exterior" for z in zones.values()),
        },
        "all_photos": [
            {
                "filename": p["filename"],
                "path": p["path"],
                "exif": {k: v for k, v in p["exif"].items() if not k.startswith("_")},
                "zone": p["zone"],
                "scene_type": p.get("visual_analysis", {}).get("scene_type"),
                "overall_description": p.get("visual_analysis", {}).get("overall_description"),
            }
            for p in photos
        ],
    }

    # Save catalog
    catalog_path = output_dir / "photo_catalog.json"
    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False, default=str)

    # Save detailed analyses
    analyses_path = output_dir / "photo_analyses.json"
    with open(analyses_path, "w") as f:
        json.dump(analyses, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n  ✓ Catálogo guardado: {catalog_path}")
    print(f"  ✓ Análisis guardados: {analyses_path}")
    print(f"  ✓ {len(photos)} fotos procesadas en {len(zones)} zonas")

    return {
        "source": "user_photos",
        "catalog_path": str(catalog_path),
        "observations": _catalog_to_observations(catalog),
        "summary": catalog["summary"],
    }


def _catalog_to_observations(catalog: dict) -> list:
    """Convert photo catalog to standard observation format for evidence fusion."""
    observations = []
    for zone_name, zone_data in catalog.get("zones", {}).items():
        for elem in zone_data.get("elements_found", []):
            obs = {
                "observation_id": f"photo_{zone_name}_{len(observations)}",
                "category": elem.get("type", "other"),
                "source": "user_photo",
                "description": elem.get("description", ""),
                "attributes": {
                    "height_levels": elem.get("approximate_height_levels"),
                    "material": elem.get("material"),
                    "color": elem.get("color"),
                    "condition": elem.get("condition"),
                    "relative_position": elem.get("relative_position"),
                    "from_photo": elem.get("_from_photo"),
                    "zone": zone_name,
                },
                "confidence": 0.9,  # User photos = highest confidence
            }
            observations.append(obs)

    return observations
