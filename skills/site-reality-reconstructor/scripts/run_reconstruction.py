#!/usr/bin/env python3.11
"""
Site Reality Reconstructor v2.0 — Orquestador Principal
Ejecuta el DAG completo de reconstrucción de realidad de un sitio.

Módulos v2.0:
- site_resolver: Normaliza coordenadas y bbox
- coverage_profiler: Evalúa disponibilidad de fuentes
- osm_collector: Footprints de edificios, vías, POIs
- maps_grounding_collector: Negocios y contexto via Gemini
- web_researcher: Noticias y descripciones via Perplexity
- visual_analyzer: Análisis de imágenes con Gemini Vision
- photo_processor: Procesamiento masivo de fotos del usuario (NUEVO v2.0)
- social_media_collector: Búsqueda en redes sociales (NUEVO v2.0)
- sketchup_analyzer: Extracción de datos de modelos 3D (NUEVO v2.0)
- spatial_model_builder: Mezclador de todas las fuentes (NUEVO v2.0)
- evidence_fuser: Fusión de evidencia con jerarquía de verdad
- srd_builder: Genera el Site Reality Document
- render_validator: Valida renders contra el SRD
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from coverage_profiler import profile_coverage
from evidence_fuser import fuse_evidence
from maps_grounding_collector import collect_maps_grounding
from osm_collector import collect_osm
from photo_processor import process_photos
from site_resolver import resolve_site
from sketchup_analyzer import analyze_sketchup
from social_media_collector import collect_social_media
from spatial_model_builder import build_spatial_model
from srd_builder import build_srd
from visual_analyzer import analyze_visuals
from web_researcher import research_web


def parse_args():
    parser = argparse.ArgumentParser(description="Site Reality Reconstructor v2.0")
    parser.add_argument("--lat", type=float, required=True, help="Latitud del sitio")
    parser.add_argument("--lng", type=float, required=True, help="Longitud del sitio")
    parser.add_argument("--radius", type=int, default=300, help="Radio de análisis en metros")
    parser.add_argument("--name", type=str, required=True, help="Nombre del sitio")
    parser.add_argument("--location", type=str, default="", help="Ciudad/Estado para búsquedas")
    parser.add_argument("--output-dir", type=str, required=True, help="Directorio de salida")

    # Fuentes de fotos del usuario
    parser.add_argument("--user-photos", type=str, default=None, help="Directorio con fotos del usuario del sitio")
    parser.add_argument("--max-photos", type=int, default=100, help="Máximo de fotos a procesar")

    # Renders y SketchUp existentes
    parser.add_argument("--renders-dir", type=str, default=None, help="Directorio con renders existentes del proyecto")
    parser.add_argument(
        "--sketchup-renders", type=str, default=None, help="Directorio con renders/screenshots del modelo SketchUp"
    )
    parser.add_argument("--sketchup-files", type=str, default=None, help="Directorio con archivos .skp")
    parser.add_argument("--pdf-plans", type=str, default=None, help="Directorio con planos PDF del proyecto")

    # Opciones de búsqueda
    parser.add_argument(
        "--search-social",
        action="store_true",
        default=True,
        help="Buscar en redes sociales (Instagram, YouTube, TikTok)",
    )
    parser.add_argument("--no-social", action="store_true", help="Desactivar búsqueda en redes sociales")

    # Opciones existentes
    parser.add_argument("--target-date", type=str, default=None, help="Fecha objetivo YYYY-MM-DD")
    parser.add_argument("--views", type=str, default="N,S,E,W,aerial", help="Vistas objetivo")
    parser.add_argument("--only-collect", action="store_true", help="Solo recolectar, no fusionar")
    parser.add_argument("--skip-browser", action="store_true", help="Omitir recolección via navegador")
    parser.add_argument("--skip-grounding", action="store_true", help="Omitir Gemini Maps Grounding")
    parser.add_argument("--skip-spatial-model", action="store_true", help="Omitir spatial model builder")
    parser.add_argument("--confidence-threshold", type=float, default=0.6)

    return parser.parse_args()


async def run_pipeline(args):
    start_time = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = output_dir / "evidence"
    evidence_dir.mkdir(exist_ok=True)

    target_date_str = args.target_date or date.today().isoformat()
    views = [v.strip() for v in args.views.split(",")]
    location = args.location or args.name

    print("=" * 60)
    print("SITE REALITY RECONSTRUCTOR v2.0")
    print("=" * 60)

    # ─── PASO 1: Site Resolver ───────────────────────────────────────────
    print("\n[1/10] Resolviendo sitio...")
    site_info = resolve_site(
        lat=args.lat,
        lng=args.lng,
        radius=args.radius,
        name=args.name,
        target_date=target_date_str,
        views=views,
    )
    with open(output_dir / "site_info.json", "w") as f:
        json.dump(site_info, f, indent=2, ensure_ascii=False)
    print(f"    Sitio: {site_info['name']} ({site_info['lat']}, {site_info['lng']})")
    print(f"    Radio: {site_info['radius_m']}m | Fecha objetivo: {site_info['target_date']}")

    # ─── PASO 2: Coverage Profiler ───────────────────────────────────────
    print("\n[2/10] Evaluando cobertura de fuentes...")
    coverage = await profile_coverage(site_info, args.user_photos)
    with open(output_dir / "coverage_report.json", "w") as f:
        json.dump(coverage, f, indent=2, ensure_ascii=False)
    semaphore = coverage.get("semaphore", "yellow")
    print(f"    Semáforo: {semaphore.upper()}")
    print(f"    User photos: {coverage.get('user_photos_count', 0)}")

    # ─── PASO 3: Recolección Base (paralelo) ─────────────────────────────
    print("\n[3/10] Recolectando evidencia base (paralelo)...")
    base_collectors = []

    # OSM siempre
    base_collectors.append(("osm", collect_osm(site_info, evidence_dir)))

    # Maps Grounding
    if not args.skip_grounding:
        base_collectors.append(("maps_grounding", collect_maps_grounding(site_info, evidence_dir)))

    # Web Research
    base_collectors.append(("web_research", research_web(site_info, evidence_dir)))

    results = {}
    tasks = {name: asyncio.create_task(coro) for name, coro in base_collectors}
    for name, task in tasks.items():
        try:
            result = await task
            results[name] = result
            obs_count = len(result.get("observations", []))
            print(f"    ✓ {name}: {obs_count} observaciones")
        except Exception as e:
            print(f"    ✗ {name}: Error — {str(e)[:80]}")
            results[name] = {"observations": [], "error": str(e)}

    # ─── PASO 4: Fotos del usuario (NUEVO v2.0) ─────────────────────────
    if args.user_photos and os.path.isdir(args.user_photos):
        print(f"\n[4/10] Procesando fotos del usuario ({args.user_photos})...")
        try:
            photo_result = await process_photos(
                photo_dir=args.user_photos,
                site_lat=args.lat,
                site_lng=args.lng,
                site_name=args.name,
                radius_m=args.radius,
                output_dir=str(evidence_dir / "user_photos"),
                max_photos=args.max_photos,
            )
            results["user_photos"] = photo_result
            obs_count = len(photo_result.get("observations", []))
            print(
                f"    ✓ Fotos usuario: {obs_count} observaciones de {photo_result.get('summary', {}).get('total_photos', 0)} fotos"
            )
        except Exception as e:
            print(f"    ✗ Fotos usuario: Error — {str(e)[:80]}")
            results["user_photos"] = {"observations": [], "error": str(e)}
    else:
        print("\n[4/10] Sin fotos del usuario — omitiendo")
        # Also run visual analyzer with any existing reference images
        user_photo_paths = []
        if args.user_photos and os.path.isdir(args.user_photos):
            for f_name in os.listdir(args.user_photos):
                if f_name.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".heic")):
                    user_photo_paths.append(os.path.join(args.user_photos, f_name))
        if user_photo_paths:
            try:
                vis_result = await analyze_visuals(site_info, user_photo_paths, evidence_dir)
                results["visual_analysis"] = vis_result
            except Exception as e:
                results["visual_analysis"] = {"observations": [], "error": str(e)}

    # ─── PASO 5: Redes sociales (NUEVO v2.0) ─────────────────────────────
    if not args.no_social:
        print("\n[5/10] Buscando en redes sociales...")
        try:
            social_result = await collect_social_media(
                site_name=args.name,
                location=location,
                lat=args.lat,
                lng=args.lng,
                output_dir=str(evidence_dir / "social_media"),
                renders_dir=args.renders_dir,
            )
            results["social_media"] = social_result
            obs_count = len(social_result.get("observations", []))
            print(f"    ✓ Redes sociales: {obs_count} observaciones")
        except Exception as e:
            print(f"    ✗ Redes sociales: Error — {str(e)[:80]}")
            results["social_media"] = {"observations": [], "error": str(e)}
    else:
        print("\n[5/10] Búsqueda en redes sociales desactivada")

    # ─── PASO 6: SketchUp / Renders existentes (NUEVO v2.0) ─────────────
    has_sketchup = args.sketchup_renders or args.sketchup_files or args.pdf_plans
    if has_sketchup:
        print("\n[6/10] Analizando modelos SketchUp y planos...")
        try:
            sketchup_result = await analyze_sketchup(
                site_name=args.name,
                renders_dir=args.sketchup_renders,
                skp_dir=args.sketchup_files,
                pdf_dir=args.pdf_plans,
                output_dir=str(evidence_dir / "sketchup"),
            )
            results["sketchup"] = sketchup_result
            obs_count = len(sketchup_result.get("observations", []))
            print(f"    ✓ SketchUp: {obs_count} observaciones")
        except Exception as e:
            print(f"    ✗ SketchUp: Error — {str(e)[:80]}")
            results["sketchup"] = {"observations": [], "error": str(e)}
    else:
        print("\n[6/10] Sin modelos SketchUp — omitiendo")

    # Guardar evidencia cruda
    with open(evidence_dir / "raw_evidence.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    # ─── PASO 7: Spatial Model Builder (NUEVO v2.0) ──────────────────────
    if not args.skip_spatial_model:
        print("\n[7/10] Construyendo modelo espacial unificado...")
        try:
            spatial_model = await build_spatial_model(
                site_info={
                    "name": args.name,
                    "lat": args.lat,
                    "lng": args.lng,
                    "radius_m": args.radius,
                },
                collected_results=results,
                output_dir=str(evidence_dir / "spatial_model"),
            )
            results["spatial_model"] = {"observations": [], "model": spatial_model}
            print("    ✓ Modelo espacial construido")
            blind_count = len(spatial_model.get("blind_spots", []))
            conf = spatial_model.get("confidence_map", {}).get("overall", 0)
            print(f"    Confianza global: {conf:.0%} | Blind spots: {blind_count}")
        except Exception as e:
            print(f"    ✗ Modelo espacial: Error — {str(e)[:80]}")
            spatial_model = None
    else:
        print("\n[7/10] Modelo espacial omitido")
        spatial_model = None

    if args.only_collect:
        elapsed = time.time() - start_time
        print(f"\n[DONE] Solo recolección completada en {elapsed:.1f}s")
        return

    # ─── PASO 8: Fusión de Evidencia ─────────────────────────────────────
    print("\n[8/10] Fusionando evidencia...")
    fused = await fuse_evidence(site_info, results, args.confidence_threshold)
    with open(evidence_dir / "fused_evidence.json", "w") as f:
        json.dump(fused, f, indent=2, ensure_ascii=False, default=str)
    print(f"    Observaciones fusionadas: {len(fused.get('observations', []))}")
    print(f"    Blind spots: {len(fused.get('blind_spots', []))}")
    print(f"    Conflictos resueltos: {fused.get('conflicts_resolved', 0)}")

    # ─── PASO 9: Construir SRD ───────────────────────────────────────────
    print("\n[9/10] Construyendo Site Reality Document...")

    # Enrich fused evidence with spatial model data
    if spatial_model:
        fused["spatial_model"] = spatial_model

    srd = await build_srd(site_info, fused, coverage)
    with open(output_dir / "site_reality.json", "w") as f:
        json.dump(srd, f, indent=2, ensure_ascii=False, default=str)

    # Generate Markdown
    md_content = generate_srd_markdown(srd, spatial_model)
    with open(output_dir / "site_reality.md", "w") as f:
        f.write(md_content)

    # Extract render constraints
    constraints = extract_render_constraints(srd, spatial_model)
    with open(output_dir / "render_constraints.json", "w") as f:
        json.dump(constraints, f, indent=2, ensure_ascii=False, default=str)

    print("    SRD generado: site_reality.json")
    print("    Markdown: site_reality.md")
    print(f"    must_include: {len(constraints.get('must_include', []))}")
    print(f"    must_not_include: {len(constraints.get('must_not_include', []))}")

    # ─── PASO 10: Resumen Final ──────────────────────────────────────────
    elapsed = time.time() - start_time
    total_obs = sum(len(r.get("observations", [])) for r in results.values() if isinstance(r, dict))

    print("\n" + "=" * 60)
    print(f"RECONSTRUCCIÓN COMPLETADA v2.0 en {elapsed:.1f}s")
    print(f"Semáforo: {semaphore.upper()}")
    print(f"Total observaciones: {total_obs}")
    print(f"Fuentes activas: {len([r for r in results.values() if isinstance(r, dict) and r.get('observations')])}")
    if spatial_model:
        print(f"Confianza espacial: {spatial_model.get('confidence_map', {}).get('overall', 0):.0%}")
    print(f"Confianza SRD core: {srd.get('overall_confidence', {}).get('core_site', 'N/A')}")
    print(f"Confianza SRD contexto: {srd.get('overall_confidence', {}).get('immediate_context', 'N/A')}")
    print(f"Archivos en: {output_dir}")
    print("=" * 60)

    return srd


def generate_srd_markdown(srd, spatial_model=None):
    """Genera versión Markdown legible del SRD enriquecido con modelo espacial."""
    lines = []
    meta = srd.get("site_metadata", {})
    lines.append(f"# Site Reality Document v2.0 — {meta.get('name', 'Unknown')}")
    lines.append(
        f"\n**Coordenadas:** {meta.get('coordinates', {}).get('lat', '')}, {meta.get('coordinates', {}).get('lng', '')}"
    )
    lines.append(f"**Radio:** {meta.get('radius_m', '')}m")
    lines.append(f"**Fecha objetivo:** {meta.get('target_reality_date', '')}")
    lines.append(f"**Fecha reconstrucción:** {meta.get('reconstruction_date', '')}")

    # Fuentes
    lines.append("\n## Fuentes Consultadas\n")
    for src in srd.get("source_registry", []):
        lines.append(
            f"- **{src.get('type', '')}**: {src.get('source_id', '')} (confianza: {src.get('confidence', '')})"
        )

    # Spatial Model Summary (if available)
    if spatial_model:
        lines.append("\n## Modelo Espacial Unificado\n")

        site_core = spatial_model.get("site_core", {})
        if isinstance(site_core, dict):
            lines.append("### Sitio Principal")
            lines.append(site_core.get("description", "Sin descripción"))
            lines.append("")

        zones = spatial_model.get("zones", {})
        for cardinal in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
            zone = zones.get(cardinal, {})
            if zone:
                conf = spatial_model.get("confidence_map", {}).get(cardinal, 0)
                desc = zone.get("reality_description", "Sin datos")
                lines.append(f"### {cardinal} (confianza: {conf:.0%})")
                lines.append(desc)
                lines.append("")

        # Blind spots from spatial model
        lines.append("### Blind Spots del Modelo Espacial\n")
        for bs in spatial_model.get("blind_spots", []):
            lines.append(
                f"- **{bs.get('zone', '?')}**: {bs.get('reason', '?')} → Política: {bs.get('render_policy', '?')}"
            )
        lines.append("")

    # Contexto por orientación (from SRD)
    lines.append("\n## Contexto por Orientación (SRD)\n")
    for direction in ["north", "south", "east", "west"]:
        ctx = srd.get("surrounding_context", {}).get(direction, {})
        if ctx:
            lines.append(f"### {direction.upper()}")
            lines.append(f"{ctx.get('description', 'Sin datos')}")
            lines.append(f"- Edificios: {ctx.get('buildings', 'N/A')}")
            lines.append(f"- Alturas: {ctx.get('heights', 'N/A')}")
            lines.append(f"- Uso de suelo: {ctx.get('land_use', 'N/A')}")
            lines.append(f"- Confianza: {ctx.get('confidence', 'N/A')}")
            lines.append("")

    # Observaciones
    lines.append("\n## Observaciones Visuales\n")
    for obs in srd.get("visual_observations", []):
        lines.append(
            f"- **{obs.get('category', '')}**: {obs.get('description', '')} (confianza: {obs.get('confidence', '')})"
        )

    # Blind Spots
    lines.append("\n## Blind Spots\n")
    for bs in srd.get("blind_spots", []):
        lines.append(
            f"- **{bs.get('zone', '')}**: {bs.get('status', '')} — {bs.get('reason', '')} → Política: {bs.get('render_policy', '')}"
        )

    # Restricciones
    lines.append("\n## Restricciones de Render\n")
    rc = srd.get("render_constraints", {})
    if rc.get("must_include"):
        lines.append("### DEBE incluir:")
        for item in rc["must_include"]:
            lines.append(f"- {item.get('element', '')}: {item.get('description', '')}")
    if rc.get("must_not_include"):
        lines.append("\n### NO DEBE incluir:")
        for item in rc["must_not_include"]:
            lines.append(f"- {item.get('element', '')}: {item.get('reason', '')}")

    # Confianza general
    lines.append("\n## Confianza General\n")
    oc = srd.get("overall_confidence", {})
    lines.append(f"- Core site: **{oc.get('core_site', 'N/A')}**")
    lines.append(f"- Contexto inmediato: **{oc.get('immediate_context', 'N/A')}**")
    lines.append(f"- Contexto extendido: **{oc.get('extended_context', 'N/A')}**")
    lines.append(f"- Modo cobertura: **{oc.get('coverage_mode', 'N/A')}**")

    return "\n".join(lines) + "\n"


def extract_render_constraints(srd, spatial_model=None):
    """Extrae las restricciones de render del SRD + modelo espacial."""
    constraints = srd.get(
        "render_constraints",
        {
            "must_include": [],
            "must_not_include": [],
            "height_limits": [],
            "landscape_constraints": [],
            "color_palette": [],
            "materials": [],
        },
    )

    # Enrich with spatial model constraints
    if spatial_model:
        sm_constraints = spatial_model.get("render_constraints", {})

        # Add hard constraints
        for hc in sm_constraints.get("hard_constraints", []):
            constraints.setdefault("must_include", []).append(
                {
                    "element": hc.get("rule", ""),
                    "description": f"[Spatial Model] Zona: {hc.get('zone', '?')} — Evidencia: {hc.get('evidence', '?')}",
                    "source": "spatial_model",
                }
            )

        # Add prohibited elements
        for pe in sm_constraints.get("prohibited_elements", []):
            constraints.setdefault("must_not_include", []).append(
                {
                    "element": pe.get("element", ""),
                    "reason": f"[Spatial Model] Zona: {pe.get('zone', '?')} — {pe.get('reason', '?')}",
                    "source": "spatial_model",
                }
            )

    return constraints


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run_pipeline(args))
