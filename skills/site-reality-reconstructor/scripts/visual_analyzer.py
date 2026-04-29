#!/usr/bin/env python3.11
"""
Visual Analyzer — Analiza imágenes (fotos del usuario, satelitales, street view)
usando Gemini Vision para extraer observaciones del entorno real.
"""
import base64
import json
import os
from pathlib import Path


def _encode_image(path: str) -> str:
    """Encode image to base64."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _get_mime_type(path: str) -> str:
    """Get MIME type from file extension."""
    ext = Path(path).suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".heic": "image/heic",
    }
    return mime_map.get(ext, "image/jpeg")


async def analyze_visuals(site_info: dict, image_paths: list, evidence_dir: Path) -> dict:
    """Analiza imágenes del sitio con Gemini Vision."""
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"source": "visual_analysis", "observations": [], "error": "No GEMINI_API_KEY"}

    client = genai.Client(api_key=api_key)
    observations = []
    raw_analyses = []

    analysis_prompt = f"""Analiza esta imagen del sitio "{site_info['name']}" y su entorno.
Extrae la siguiente información de forma OBJETIVA y FACTUAL:

1. EDIFICIOS/CONSTRUCCIONES visibles:
   - Tipo (residencial, comercial, industrial, estadio, etc.)
   - Altura aproximada (número de niveles)
   - Material dominante (concreto, block, lámina, etc.)
   - Estado de conservación
   - Color dominante

2. TERRENO/SUELO visible:
   - Tipo (pavimentado, tierra, pasto, estacionamiento, etc.)
   - Estado (bueno, deteriorado, baldío, en construcción)

3. VEGETACIÓN visible:
   - Tipo (árboles grandes, arbustos, pasto, sin vegetación)
   - Densidad (abundante, moderada, escasa, nula)

4. INFRAESTRUCTURA visible:
   - Vialidades (tipo, ancho aproximado, estado)
   - Postes, cableado, señalización
   - Bardas, cercas, muros

5. ELEMENTOS NOTABLES:
   - Letreros, marcas, nombres visibles
   - Vehículos, mobiliario urbano
   - Cualquier elemento distintivo

IMPORTANTE:
- Solo describe lo que VES en la imagen. NO inventes ni supongas.
- Si algo no es visible o es ambiguo, dilo explícitamente.
- Indica la orientación/ángulo aproximado de la toma si es posible.
- Responde en formato JSON con la estructura indicada."""

    for i, img_path in enumerate(image_paths[:20]):  # Max 20 images
        try:
            img_data = _encode_image(img_path)
            mime = _get_mime_type(img_path)

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Content(
                        parts=[
                            types.Part(text=analysis_prompt),
                            types.Part(inline_data=types.Blob(mime_type=mime, data=base64.b64decode(img_data))),
                        ]
                    )
                ],
            )

            text = response.text if response.text else ""
            raw_analyses.append({
                "image": os.path.basename(img_path),
                "analysis": text,
            })

            # Create observation from analysis
            obs = {
                "observation_id": f"visual_{i}",
                "category": "visual_analysis",
                "source": "user_photo",
                "description": text[:500] if text else "Análisis no disponible",
                "attributes": {
                    "image_file": os.path.basename(img_path),
                    "full_analysis": text,
                },
                "confidence": 0.9,  # User photos = highest confidence
            }
            observations.append(obs)

            print(f"      Visual analysis {i+1}/{min(len(image_paths), 20)}: {len(text)} chars")

        except Exception as e:
            print(f"      Visual analysis {i+1} error: {str(e)[:80]}")
            raw_analyses.append({"image": os.path.basename(img_path), "error": str(e)})

    # Save raw analyses
    with open(evidence_dir / "visual_analysis_raw.json", "w") as f:
        json.dump(raw_analyses, f, indent=2, ensure_ascii=False, default=str)

    return {
        "source": "visual_analysis",
        "observations": observations,
        "summary": {
            "images_analyzed": len(raw_analyses),
            "successful": len([a for a in raw_analyses if "error" not in a]),
        },
    }
