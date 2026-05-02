#!/usr/bin/env python3.11
"""
Entrypoint: run_proyecto.py
Orquesta los 7 módulos del pipeline proyecto-renders en secuencia.

Uso:
    python3.11 run_proyecto.py \
        --description "Descripción del proyecto" \
        --address "Dirección del terreno" \
        --output-dir /tmp/mi_proyecto

El pipeline ejecuta:
1. Intake & Normalización
2. Site Intelligence
3. Benchmark Research
4. HBU + Escenarios + Financial Model
5. Business Plan
6. Render Pipeline (genera prompts; renders los genera el agente)
7. QA & Packaging

NOTA: El paso 6 genera los prompts de renders pero NO las imágenes.
Las imágenes las genera el agente usando la herramienta generate
después de que este script termina.
"""

import argparse
import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Agregar scripts al path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")

from benchmark_research import run_benchmark_research
from business_plan import run_business_plan
from hbu_scenarios import run_hbu_analysis
from intake_normalize import run_intake
from qa_packaging import run_qa_packaging
from render_pipeline import run_render_pipeline
from site_intelligence import run_site_intelligence


async def run_full_pipeline(
    description: str,
    address: str = None,
    lat: float = None,
    lng: float = None,
    drive_folder: str = None,
    local_files: list = None,
    output_dir: str = "/tmp/proyecto_renders",
    skip_renders: bool = False,
    skip_qa: bool = False,
) -> dict:
    """Ejecuta el pipeline completo de proyecto-renders."""

    start_time = time.time()

    print("=" * 70)
    print("🏗️  PROYECTO RENDERS — PIPELINE COMPLETO")
    print(f"   Fecha: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print(f"   Output: {output_dir}")
    print("=" * 70)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    results = {}

    # ═══════════════════════════════════════════════
    # MÓDULO 1: INTAKE
    # ═══════════════════════════════════════════════
    print("\n" + "─" * 70)
    brief_path = os.path.join(output_dir, "project_brief.yaml")

    try:
        brief = await run_intake(
            description=description,
            address=address,
            lat=lat,
            lng=lng,
            drive_folder=drive_folder,
            local_files=local_files,
            output_path=brief_path,
        )
        results["intake"] = {"status": "ok", "path": brief_path}
    except Exception as e:
        print(f"  ❌ Error en Intake: {e}")
        results["intake"] = {"status": "error", "error": str(e)}
        return results

    # ═══════════════════════════════════════════════
    # MÓDULO 2: SITE INTELLIGENCE
    # ═══════════════════════════════════════════════
    print("\n" + "─" * 70)
    try:
        site_result = await run_site_intelligence(brief_path, output_dir)
        results["site_intelligence"] = {"status": "ok", **site_result}
    except Exception as e:
        print(f"  ❌ Error en Site Intelligence: {e}")
        results["site_intelligence"] = {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════════════
    # MÓDULO 3: BENCHMARK RESEARCH
    # ═══════════════════════════════════════════════
    print("\n" + "─" * 70)
    site_report_path = os.path.join(output_dir, "site_report.md")

    try:
        bench_result = await run_benchmark_research(brief_path, site_report_path, output_dir)
        results["benchmarks"] = {"status": "ok", **bench_result}
    except Exception as e:
        print(f"  ❌ Error en Benchmarks: {e}")
        results["benchmarks"] = {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════════════
    # MÓDULO 4: HBU + ESCENARIOS
    # ═══════════════════════════════════════════════
    print("\n" + "─" * 70)
    benchmarks_path = os.path.join(output_dir, "benchmarks.md")

    try:
        hbu_result = await run_hbu_analysis(brief_path, site_report_path, benchmarks_path, output_dir)
        results["hbu"] = {"status": "ok", **hbu_result}
    except Exception as e:
        print(f"  ❌ Error en HBU: {e}")
        results["hbu"] = {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════════════
    # MÓDULO 5: BUSINESS PLAN
    # ═══════════════════════════════════════════════
    print("\n" + "─" * 70)
    hbu_path = os.path.join(output_dir, "hbu_analysis.md")
    scenarios_path = os.path.join(output_dir, "scenarios.yaml")

    try:
        bp_result = await run_business_plan(
            brief_path, site_report_path, benchmarks_path, hbu_path, scenarios_path, output_dir
        )
        results["business_plan"] = {"status": "ok", **bp_result}
    except Exception as e:
        print(f"  ❌ Error en Business Plan: {e}")
        results["business_plan"] = {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════════════
    # MÓDULO 6: RENDER PIPELINE
    # ═══════════════════════════════════════════════
    if not skip_renders:
        print("\n" + "─" * 70)
        site_data_path = os.path.join(output_dir, "site_data.yaml")

        try:
            render_result = await run_render_pipeline(
                brief_path, scenarios_path, benchmarks_path, site_data_path, output_dir
            )
            results["render_pipeline"] = {"status": "ok", **render_result}
        except Exception as e:
            print(f"  ❌ Error en Render Pipeline: {e}")
            results["render_pipeline"] = {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════════════
    # MÓDULO 7: QA & PACKAGING
    # ═══════════════════════════════════════════════
    if not skip_qa:
        print("\n" + "─" * 70)
        try:
            qa_result = await run_qa_packaging(output_dir)
            results["qa_packaging"] = {"status": "ok", **qa_result}
        except Exception as e:
            print(f"  ❌ Error en QA: {e}")
            results["qa_packaging"] = {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════════════
    # RESUMEN FINAL
    # ═══════════════════════════════════════════════
    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print("🏁 PIPELINE COMPLETADO")
    print(f"   Tiempo total: {elapsed / 60:.1f} minutos")
    print(f"   Directorio: {output_dir}")
    print("─" * 70)

    for module, res in results.items():
        icon = "✅" if res.get("status") == "ok" else "❌"
        print(f"   {icon} {module}")

    ok_count = sum(1 for r in results.values() if r.get("status") == "ok")
    total_count = len(results)
    print(f"\n   Resultado: {ok_count}/{total_count} módulos exitosos")

    if not skip_renders:
        print("\n   ⚠️ SIGUIENTE PASO: El agente debe generar los 8 renders")
        print(f"      usando los prompts en: {output_dir}/render_prompts.yaml")
        print(f"      y guardarlos en: {output_dir}/renders/")

    print("=" * 70)

    results["_summary"] = {
        "elapsed_seconds": round(elapsed, 1),
        "ok_modules": ok_count,
        "total_modules": total_count,
        "output_dir": output_dir,
        "timestamp": datetime.now().isoformat(),
    }

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Proyecto Renders — Pipeline Completo")
    parser.add_argument("--description", required=True, help="Descripción del proyecto")
    parser.add_argument("--address", help="Dirección del terreno")
    parser.add_argument("--lat", type=float, help="Latitud")
    parser.add_argument("--lng", type=float, help="Longitud")
    parser.add_argument("--drive-folder", help="Carpeta de Google Drive")
    parser.add_argument("--local-files", nargs="+", help="Archivos locales")
    parser.add_argument("--output-dir", default="/tmp/proyecto_renders", help="Directorio de salida")
    parser.add_argument("--skip-renders", action="store_true", help="Omitir generación de prompts de renders")
    parser.add_argument("--skip-qa", action="store_true", help="Omitir QA y packaging")

    args = parser.parse_args()

    result = asyncio.run(
        run_full_pipeline(
            description=args.description,
            address=args.address,
            lat=args.lat,
            lng=args.lng,
            drive_folder=args.drive_folder,
            local_files=args.local_files,
            output_dir=args.output_dir,
            skip_renders=args.skip_renders,
            skip_qa=args.skip_qa,
        )
    )
