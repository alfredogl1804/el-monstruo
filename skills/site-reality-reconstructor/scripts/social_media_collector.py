#!/usr/bin/env python3.11
"""
Social Media Collector — Búsqueda agresiva en redes sociales y web
de fotos y videos recientes del sitio y sus alrededores.

Fuentes:
1. Google Images (via search tool / Perplexity)
2. YouTube (via search + manus-analyze-video)
3. Instagram (via location search / hashtag research)
4. General web (via Perplexity Sonar)
"""

import asyncio
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

# ── Google Images Search ─────────────────────────────────────────────────────


async def _search_google_images(site_name: str, location: str, output_dir: Path) -> list:
    """Search for recent images of the site via Perplexity."""
    api_key = os.environ.get("SONAR_API_KEY")
    if not api_key:
        return []

    observations = []
    queries = [
        f"{site_name} {location} 2025 2026 fotos",
        f"{site_name} remodelación fotos recientes",
        f"{site_name} alrededores entorno exterior",
        f"{site_name} estacionamiento explanada",
    ]

    for i, query in enumerate(queries):
        try:
            resp = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar-pro",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Eres un investigador visual. Tu trabajo es encontrar y describir "
                                "fotos e imágenes recientes del lugar indicado. Para cada imagen que "
                                "encuentres, describe: 1) URL de la fuente, 2) Qué se ve en la imagen, "
                                "3) Desde qué ángulo/orientación fue tomada, 4) Fecha aproximada. "
                                "Prioriza fotos recientes (2024-2026). Incluye fotos de redes sociales, "
                                "noticias, Google Maps, y cualquier fuente pública."
                            ),
                        },
                        {"role": "user", "content": query},
                    ],
                    "max_tokens": 2000,
                },
                timeout=60,
            )

            if resp.status_code == 200:
                data = resp.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                citations = data.get("citations", [])

                obs = {
                    "observation_id": f"social_images_{i}",
                    "category": "visual_reference",
                    "source": "google_images_search",
                    "description": text[:500],
                    "attributes": {
                        "query": query,
                        "full_response": text,
                        "citations": citations,
                        "image_urls_found": _extract_urls(text),
                    },
                    "confidence": 0.65,
                }
                observations.append(obs)
                print(f"      Google Images {i + 1}/4: {len(citations)} citas, {len(_extract_urls(text))} URLs")

        except Exception as e:
            print(f"      Google Images {i + 1}/4 error: {str(e)[:60]}")

        await asyncio.sleep(1)

    return observations


# ── YouTube Video Search ─────────────────────────────────────────────────────


async def _search_youtube(site_name: str, location: str, output_dir: Path) -> list:
    """Search YouTube for recent videos of the site and analyze them."""
    api_key = os.environ.get("SONAR_API_KEY")
    if not api_key:
        return []

    observations = []

    # First, find relevant YouTube videos via Perplexity
    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Encuentra videos de YouTube recientes (2024-2026) del lugar indicado. "
                            "Para cada video proporciona: 1) URL completa de YouTube, 2) Título, "
                            "3) Fecha de publicación, 4) Descripción de qué muestra. "
                            "Prioriza videos que muestren el estado actual del lugar, tours, "
                            "recorridos, o noticias sobre remodelaciones."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Videos de YouTube recientes de {site_name} en {location}",
                    },
                ],
                "max_tokens": 2000,
            },
            timeout=60,
        )

        if resp.status_code == 200:
            data = resp.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = data.get("citations", [])

            # Extract YouTube URLs
            yt_urls = [u for u in _extract_urls(text) if "youtube.com" in u or "youtu.be" in u]

            obs = {
                "observation_id": "social_youtube_search",
                "category": "video_reference",
                "source": "youtube_search",
                "description": text[:500],
                "attributes": {
                    "full_response": text,
                    "youtube_urls": yt_urls,
                    "citations": citations,
                },
                "confidence": 0.7,
            }
            observations.append(obs)
            print(f"      YouTube: {len(yt_urls)} videos encontrados")

            # Analyze up to 3 YouTube videos with manus-analyze-video
            for j, url in enumerate(yt_urls[:3]):
                try:
                    print(f"      Analizando video {j + 1}/3: {url[:60]}...")
                    result = subprocess.run(
                        [
                            "manus-analyze-video",
                            url,
                            f"Describe en detalle qué se ve en este video de {site_name}. "
                            f"Enfócate en: 1) Estado actual de las instalaciones, "
                            f"2) Alrededores visibles (edificios, calles, terrenos), "
                            f"3) Materiales, colores, alturas de construcciones, "
                            f"4) Vegetación, estacionamientos, infraestructura. "
                            f"Solo describe lo que VES.",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )

                    if result.returncode == 0 and result.stdout:
                        video_obs = {
                            "observation_id": f"social_youtube_video_{j}",
                            "category": "video_analysis",
                            "source": "youtube_video",
                            "description": result.stdout[:500],
                            "attributes": {
                                "url": url,
                                "full_analysis": result.stdout,
                            },
                            "confidence": 0.75,
                        }
                        observations.append(video_obs)
                        print(f"      Video {j + 1} analizado: {len(result.stdout)} chars")

                except subprocess.TimeoutExpired:
                    print(f"      Video {j + 1} timeout")
                except Exception as e:
                    print(f"      Video {j + 1} error: {str(e)[:60]}")

    except Exception as e:
        print(f"      YouTube search error: {str(e)[:60]}")

    return observations


# ── Instagram Location Search ────────────────────────────────────────────────


async def _search_instagram(site_name: str, lat: float, lng: float, output_dir: Path) -> list:
    """Search Instagram for location-tagged posts near the site."""
    api_key = os.environ.get("SONAR_API_KEY")
    if not api_key:
        return []

    observations = []

    # Use Perplexity to find Instagram posts about the location
    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Busca publicaciones recientes de Instagram sobre el lugar indicado. "
                            "Identifica: 1) Hashtags populares usados, 2) Descripción de las fotos "
                            "más recientes, 3) Qué muestran las fotos (estado actual del lugar), "
                            "4) Perfiles relevantes que publican sobre el lugar. "
                            "También busca en TikTok y Facebook."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Publicaciones recientes de Instagram y TikTok sobre {site_name}",
                    },
                ],
                "max_tokens": 2000,
            },
            timeout=60,
        )

        if resp.status_code == 200:
            data = resp.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = data.get("citations", [])

            # Extract hashtags
            hashtags = re.findall(r"#\w+", text)

            obs = {
                "observation_id": "social_instagram_search",
                "category": "social_media_reference",
                "source": "instagram_search",
                "description": text[:500],
                "attributes": {
                    "full_response": text,
                    "hashtags_found": list(set(hashtags)),
                    "citations": citations,
                    "social_urls": _extract_urls(text),
                },
                "confidence": 0.6,
            }
            observations.append(obs)
            print(f"      Instagram/TikTok: {len(hashtags)} hashtags, {len(citations)} citas")

    except Exception as e:
        print(f"      Instagram search error: {str(e)[:60]}")

    return observations


# ── Render/SketchUp Catalog ──────────────────────────────────────────────────


async def _catalog_existing_renders(renders_dir: str, site_name: str) -> list:
    """Analyze existing renders and SketchUp screenshots from the project."""
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return []

    client = genai.Client(api_key=api_key)
    observations = []
    renders_path = Path(renders_dir)

    if not renders_path.exists():
        return []

    extensions = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"}
    render_files = sorted([f for f in renders_path.rglob("*") if f.suffix.lower() in extensions and f.is_file()])

    if not render_files:
        return []

    print(f"      Analizando {len(render_files)} renders/screenshots existentes...")

    for i, render_file in enumerate(render_files[:30]):  # Max 30 renders
        try:
            with open(render_file, "rb") as f:
                img_bytes = f.read()

            ext = render_file.suffix.lower()
            mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(
                ext.lstrip("."), "image/jpeg"
            )

            prompt = f"""Esta es una imagen de render/diseño/screenshot del proyecto "{site_name}".
Analiza qué muestra esta imagen y extrae información útil para reconstruir la realidad del espacio.
Responde en JSON:
{{
  "image_type": "architectural_render|sketchup_screenshot|floor_plan|elevation|section|photo|other",
  "view_angle": "aerial|eye_level|interior|detail",
  "elements_shown": [
    {{"type": "string", "description": "string", "dimensions_visible": "string or null"}}
  ],
  "spatial_info": "qué información espacial/dimensional se puede extraer",
  "materials_visible": ["lista de materiales visibles"],
  "colors_visible": ["lista de colores dominantes"],
  "scale_reference": "algún elemento que sirva de referencia de escala"
}}"""

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

            obs = {
                "observation_id": f"render_catalog_{i}",
                "category": "design_reference",
                "source": "existing_render",
                "description": analysis.get("spatial_info", ""),
                "attributes": {
                    "filename": render_file.name,
                    "path": str(render_file),
                    "image_type": analysis.get("image_type"),
                    "view_angle": analysis.get("view_angle"),
                    "elements": analysis.get("elements_shown", []),
                    "materials": analysis.get("materials_visible", []),
                    "colors": analysis.get("colors_visible", []),
                },
                "confidence": 0.85,  # Renders are design intent, high confidence for design
            }
            observations.append(obs)

            if (i + 1) % 5 == 0:
                print(f"      Renders: {i + 1}/{min(len(render_files), 30)} analizados")

        except Exception as e:
            print(f"      Render {render_file.name} error: {str(e)[:60]}")

        if i % 5 == 4:
            await asyncio.sleep(1)

    print(f"      ✓ {len(observations)} renders catalogados")
    return observations


# ── Utilities ────────────────────────────────────────────────────────────────


def _extract_urls(text: str) -> list:
    """Extract URLs from text."""
    url_pattern = r"https?://[^\s\)\]\}\"\'<>]+"
    return list(set(re.findall(url_pattern, text)))


# ── Main Entry Point ─────────────────────────────────────────────────────────


async def collect_social_media(
    site_name: str,
    location: str,
    lat: float,
    lng: float,
    output_dir: str,
    renders_dir: Optional[str] = None,
) -> dict:
    """
    Run all social media and web searches in parallel:
    1. Google Images search
    2. YouTube video search + analysis
    3. Instagram/TikTok location search
    4. Existing render catalog (if renders_dir provided)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("  Buscando en redes sociales y web...")

    # Run searches in parallel
    tasks = [
        _search_google_images(site_name, location, output_path),
        _search_youtube(site_name, location, output_path),
        _search_instagram(site_name, lat, lng, output_path),
    ]

    if renders_dir:
        tasks.append(_catalog_existing_renders(renders_dir, site_name))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_observations = []
    sources_summary = {}

    source_names = ["google_images", "youtube", "instagram_tiktok"]
    if renders_dir:
        source_names.append("existing_renders")

    for name, result in zip(source_names, results):
        if isinstance(result, Exception):
            print(f"    ✗ {name}: ERROR — {str(result)[:60]}")
            sources_summary[name] = {"status": "error", "count": 0}
        elif isinstance(result, list):
            all_observations.extend(result)
            sources_summary[name] = {"status": "ok", "count": len(result)}
            print(f"    ✓ {name}: {len(result)} observaciones")
        else:
            sources_summary[name] = {"status": "empty", "count": 0}

    # Save raw results
    with open(output_path / "social_media_raw.json", "w") as f:
        json.dump(
            {
                "site_name": site_name,
                "search_date": datetime.now().isoformat(),
                "sources": sources_summary,
                "observations": all_observations,
            },
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    print(f"\n  ✓ Total: {len(all_observations)} observaciones de redes/web")

    return {
        "source": "social_media",
        "observations": all_observations,
        "summary": sources_summary,
    }
