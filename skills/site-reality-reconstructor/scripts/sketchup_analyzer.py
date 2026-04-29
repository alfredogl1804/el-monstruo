#!/usr/bin/env python3.11
"""
SketchUp Analyzer — Extrae información de modelos SketchUp.

Estrategia:
- Los archivos SKP nativos son binarios complejos que requieren el SDK de SketchUp.
- En su lugar, este módulo:
  1. Analiza renders/screenshots exportados del modelo SketchUp con Gemini Vision
  2. Extrae metadata de archivos ZIP (SKP 2021+ son ZIP archives)
  3. Procesa PDFs de planos/láminas asociados al modelo
  4. Combina todo para extraer dimensiones, materiales, escala y layout espacial
"""
import asyncio
import json
import os
import zipfile
from pathlib import Path
from typing import Optional


async def _analyze_sketchup_renders(renders_dir: str, model_name: str) -> list:
    """Analyze SketchUp renders/screenshots with Gemini Vision."""
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

    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'}
    files = sorted([
        f for f in renders_path.rglob("*")
        if f.suffix.lower() in extensions and f.is_file()
    ])

    if not files:
        return []

    print(f"      Analizando {len(files)} imágenes del modelo SketchUp...")

    for i, img_file in enumerate(files[:40]):  # Max 40 images
        try:
            with open(img_file, "rb") as f:
                img_bytes = f.read()

            ext = img_file.suffix.lower()
            mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                    "webp": "image/webp"}.get(ext.lstrip("."), "image/jpeg")

            prompt = f"""Esta imagen proviene del modelo SketchUp "{model_name}".
Extrae toda la información dimensional y espacial posible. Responde en JSON:
{{
  "view_type": "perspective|top|front|side|section|detail|floor_plan",
  "structures_visible": [
    {{
      "name": "nombre del elemento",
      "type": "building|wall|roof|floor|staircase|column|beam|furniture|landscape|other",
      "estimated_dimensions": {{
        "width_m": null,
        "height_m": null,
        "depth_m": null,
        "levels": null
      }},
      "materials": ["lista"],
      "colors": ["lista"],
      "notes": "observaciones adicionales"
    }}
  ],
  "spatial_relationships": [
    "Descripción de cómo se relacionan los elementos entre sí"
  ],
  "scale_indicators": "elementos que ayudan a determinar la escala (personas, autos, puertas)",
  "orientation_clues": "pistas sobre la orientación (sombras, norte, etc.)",
  "dimensional_data_extracted": "resumen de dimensiones que se pueden inferir"
}}

IMPORTANTE: Extrae la mayor cantidad de información dimensional posible.
Si ves cotas, medidas, o texto con dimensiones, repórtalas exactamente."""

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Content(parts=[
                        types.Part(text=prompt),
                        types.Part(inline_data=types.Blob(mime_type=mime, data=img_bytes)),
                    ])
                ],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )

            text = response.text if response.text else "{}"
            analysis = json.loads(text)

            obs = {
                "observation_id": f"sketchup_{i}",
                "category": "3d_model",
                "source": "sketchup_model",
                "description": analysis.get("dimensional_data_extracted", ""),
                "attributes": {
                    "filename": img_file.name,
                    "path": str(img_file),
                    "view_type": analysis.get("view_type"),
                    "structures": analysis.get("structures_visible", []),
                    "spatial_relationships": analysis.get("spatial_relationships", []),
                    "scale_indicators": analysis.get("scale_indicators"),
                },
                "confidence": 0.85,
            }
            observations.append(obs)

            if (i + 1) % 10 == 0:
                print(f"      SketchUp: {i+1}/{min(len(files), 40)} analizados")

        except Exception as e:
            print(f"      SketchUp {img_file.name} error: {str(e)[:60]}")

        if i % 5 == 4:
            await asyncio.sleep(1)

    return observations


def _analyze_skp_metadata(skp_dir: str) -> list:
    """Extract metadata from SKP files (which are ZIP archives in newer versions)."""
    observations = []
    skp_path = Path(skp_dir)

    if not skp_path.exists():
        return []

    skp_files = list(skp_path.rglob("*.skp")) + list(skp_path.rglob("*.SKP"))

    for skp_file in skp_files:
        try:
            # Try to read as ZIP (SKP 2021+ format)
            if zipfile.is_zipfile(str(skp_file)):
                with zipfile.ZipFile(str(skp_file), 'r') as zf:
                    file_list = zf.namelist()
                    total_size = sum(info.file_size for info in zf.infolist())

                    obs = {
                        "observation_id": f"skp_meta_{skp_file.stem}",
                        "category": "3d_model",
                        "source": "sketchup_file",
                        "description": f"Modelo SketchUp: {skp_file.name} ({total_size / 1024 / 1024:.1f} MB)",
                        "attributes": {
                            "filename": skp_file.name,
                            "size_mb": round(skp_file.stat().st_size / 1024 / 1024, 1),
                            "internal_files": file_list[:20],
                            "is_zip_format": True,
                            "has_textures": any("texture" in f.lower() or "material" in f.lower() for f in file_list),
                        },
                        "confidence": 0.5,
                    }
                    observations.append(obs)
                    print(f"      SKP metadata: {skp_file.name} — {len(file_list)} archivos internos")
            else:
                # Older binary format
                obs = {
                    "observation_id": f"skp_meta_{skp_file.stem}",
                    "category": "3d_model",
                    "source": "sketchup_file",
                    "description": f"Modelo SketchUp (formato binario): {skp_file.name}",
                    "attributes": {
                        "filename": skp_file.name,
                        "size_mb": round(skp_file.stat().st_size / 1024 / 1024, 1),
                        "is_zip_format": False,
                    },
                    "confidence": 0.3,
                }
                observations.append(obs)

        except Exception as e:
            print(f"      SKP {skp_file.name} error: {str(e)[:60]}")

    return observations


async def _analyze_pdf_plans(pdf_dir: str, site_name: str) -> list:
    """Analyze PDF plans/laminas associated with the model."""
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return []

    client = genai.Client(api_key=api_key)
    observations = []
    pdf_path = Path(pdf_dir)

    if not pdf_path.exists():
        return []

    pdf_files = list(pdf_path.rglob("*.pdf")) + list(pdf_path.rglob("*.PDF"))

    for pdf_file in pdf_files[:5]:  # Max 5 PDFs
        try:
            # Convert PDF pages to images for analysis
            from pdf2image import convert_from_path
            images = convert_from_path(str(pdf_file), first_page=1, last_page=5, dpi=200)

            for page_num, img in enumerate(images):
                import io
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                img_bytes = buf.getvalue()

                prompt = f"""Este es un plano/lámina del proyecto "{site_name}" (página {page_num + 1}).
Extrae TODA la información dimensional, de layout, y técnica. Responde en JSON:
{{
  "plan_type": "floor_plan|elevation|section|site_plan|detail|perspective|other",
  "scale": "escala si es visible (ej: 1:100)",
  "dimensions_found": [
    {{"element": "nombre", "dimension": "medida con unidad"}}
  ],
  "rooms_spaces": [
    {{"name": "nombre del espacio", "area_m2": null, "function": "uso"}}
  ],
  "structural_elements": ["lista de elementos estructurales visibles"],
  "notes_text": ["texto/notas visibles en el plano"],
  "north_arrow": "orientación del norte si es visible"
}}"""

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[
                        types.Content(parts=[
                            types.Part(text=prompt),
                            types.Part(inline_data=types.Blob(mime_type="image/png", data=img_bytes)),
                        ])
                    ],
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )

                text = response.text if response.text else "{}"
                analysis = json.loads(text)

                obs = {
                    "observation_id": f"pdf_plan_{pdf_file.stem}_p{page_num}",
                    "category": "technical_plan",
                    "source": "pdf_plan",
                    "description": f"Plano {analysis.get('plan_type', 'unknown')} — {pdf_file.name} p.{page_num+1}",
                    "attributes": {
                        "filename": pdf_file.name,
                        "page": page_num + 1,
                        "plan_type": analysis.get("plan_type"),
                        "scale": analysis.get("scale"),
                        "dimensions": analysis.get("dimensions_found", []),
                        "rooms": analysis.get("rooms_spaces", []),
                        "notes": analysis.get("notes_text", []),
                    },
                    "confidence": 0.9,  # Technical plans = very high confidence
                }
                observations.append(obs)

            print(f"      PDF: {pdf_file.name} — {len(images)} páginas analizadas")

        except Exception as e:
            print(f"      PDF {pdf_file.name} error: {str(e)[:60]}")

    return observations


# ── Main Entry Point ─────────────────────────────────────────────────────────

async def analyze_sketchup(
    site_name: str,
    renders_dir: Optional[str] = None,
    skp_dir: Optional[str] = None,
    pdf_dir: Optional[str] = None,
    output_dir: str = "/tmp/sketchup_analysis",
) -> dict:
    """
    Analyze SketchUp model data from multiple sources:
    1. Renders/screenshots exported from the model
    2. SKP file metadata
    3. PDF plans/laminas
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    all_observations = []
    summary = {}

    # 1. Analyze renders
    if renders_dir:
        print(f"  [1/3] Analizando renders del modelo SketchUp...")
        render_obs = await _analyze_sketchup_renders(renders_dir, site_name)
        all_observations.extend(render_obs)
        summary["renders_analyzed"] = len(render_obs)
    else:
        summary["renders_analyzed"] = 0

    # 2. Analyze SKP metadata
    if skp_dir:
        print(f"  [2/3] Extrayendo metadata de archivos SKP...")
        skp_obs = _analyze_skp_metadata(skp_dir)
        all_observations.extend(skp_obs)
        summary["skp_files_analyzed"] = len(skp_obs)
    else:
        summary["skp_files_analyzed"] = 0

    # 3. Analyze PDF plans
    if pdf_dir:
        print(f"  [3/3] Analizando planos PDF...")
        pdf_obs = await _analyze_pdf_plans(pdf_dir, site_name)
        all_observations.extend(pdf_obs)
        summary["pdf_pages_analyzed"] = len(pdf_obs)
    else:
        summary["pdf_pages_analyzed"] = 0

    # Save results
    with open(output_path / "sketchup_analysis.json", "w") as f:
        json.dump({
            "site_name": site_name,
            "analysis_date": __import__("datetime").datetime.now().isoformat(),
            "summary": summary,
            "observations": all_observations,
        }, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n  ✓ SketchUp: {len(all_observations)} observaciones totales")

    return {
        "source": "sketchup_model",
        "observations": all_observations,
        "summary": summary,
    }
