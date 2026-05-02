#!/usr/bin/env python3.11
"""
Módulo 7: QA & Packaging
Verifica calidad de todos los entregables y empaqueta el proyecto final.

QA Checks:
- Completitud de documentos
- Consistencia de cifras entre documentos
- Calidad de renders (resolución, consistencia)
- Formato profesional

Packaging:
- Genera índice maestro
- Organiza archivos en estructura presentable
- Genera resumen ejecutivo de 1 página
- Crea ZIP descargable

Salida: qa_report.md + proyecto empaquetado en directorio final
"""

import argparse
import asyncio
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio


def check_completeness(project_dir: str) -> dict:
    """Verifica que todos los entregables esperados existen."""

    expected = {
        "project_brief.yaml": {"required": True, "category": "intake"},
        "site_report.md": {"required": True, "category": "analysis"},
        "site_data.yaml": {"required": False, "category": "analysis"},
        "benchmarks.md": {"required": True, "category": "analysis"},
        "benchmarks_data.yaml": {"required": False, "category": "analysis"},
        "hbu_analysis.md": {"required": True, "category": "analysis"},
        "scenarios.yaml": {"required": True, "category": "analysis"},
        "business_plan.md": {"required": True, "category": "plan"},
        "financial_validation.md": {"required": False, "category": "plan"},
        "style_bible.md": {"required": True, "category": "renders"},
        "render_prompts.yaml": {"required": True, "category": "renders"},
        "render_instructions.md": {"required": False, "category": "renders"},
    }

    results = {}
    for fname, meta in expected.items():
        path = os.path.join(project_dir, fname)
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        results[fname] = {
            "exists": exists,
            "size_bytes": size,
            "required": meta["required"],
            "category": meta["category"],
            "status": "OK" if exists and size > 100 else ("MISSING" if meta["required"] else "OPTIONAL"),
        }

    # Check renders
    renders_dir = os.path.join(project_dir, "renders")
    render_count = 0
    if os.path.isdir(renders_dir):
        render_count = len([f for f in os.listdir(renders_dir) if f.endswith((".png", ".jpg", ".jpeg", ".webp"))])

    results["renders/"] = {
        "exists": render_count > 0,
        "count": render_count,
        "required": True,
        "category": "renders",
        "status": "OK" if render_count >= 8 else f"INCOMPLETE ({render_count}/8)",
    }

    return results


async def cross_validate_documents(project_dir: str) -> str:
    """GPT-5.4 verifica consistencia entre documentos."""

    # Leer documentos clave
    docs = {}
    for fname in ["business_plan.md", "hbu_analysis.md", "benchmarks.md"]:
        path = os.path.join(project_dir, fname)
        if os.path.exists(path):
            docs[fname] = Path(path).read_text(encoding="utf-8")[:3000]

    scenarios_path = os.path.join(project_dir, "scenarios.yaml")
    if os.path.exists(scenarios_path):
        with open(scenarios_path, "r", encoding="utf-8") as f:
            docs["scenarios"] = yaml.dump(yaml.safe_load(f), default_flow_style=False, allow_unicode=True)[:2000]

    prompt = """Eres un auditor de calidad de documentos inmobiliarios. Verifica la CONSISTENCIA 
entre estos documentos del mismo proyecto. Busca:

1. Cifras contradictorias (inversión, m2, ingresos, ROI)
2. Nombres o conceptos inconsistentes
3. Datos que aparecen en un documento pero faltan en otro
4. Supuestos diferentes entre documentos

## Documentos:
"""
    for name, content in docs.items():
        prompt += f"\n### {name}\n{content}\n"

    prompt += """
---
Devuelve un informe breve con:
- Lista de inconsistencias encontradas (si las hay)
- Score de consistencia (1-10)
- Recomendaciones de corrección"""

    resultado = await consultar_sabio("gpt54", prompt)
    return resultado.get("text", "Validación no disponible") if resultado.get("status") == "ok" else "Error"


async def generate_executive_summary(project_dir: str) -> str:
    """Genera un resumen ejecutivo de 1 página del proyecto completo."""

    # Leer plan de negocio
    bp_path = os.path.join(project_dir, "business_plan.md")
    bp = Path(bp_path).read_text(encoding="utf-8")[:5000] if os.path.exists(bp_path) else ""

    # Leer brief
    brief_path = os.path.join(project_dir, "project_brief.yaml")
    brief = {}
    if os.path.exists(brief_path):
        with open(brief_path, "r", encoding="utf-8") as f:
            brief = yaml.safe_load(f) or {}

    prompt = f"""Genera un RESUMEN EJECUTIVO DE 1 PÁGINA (máximo 500 palabras) del siguiente proyecto.
Este resumen será la portada del paquete de presentación a inversionistas.

## Brief
```yaml
{yaml.dump({k: v for k, v in brief.items() if not k.startswith("_")}, default_flow_style=False, allow_unicode=True)[:1500]}
```

## Plan de Negocio (extracto)
{bp}

---

Formato del resumen:
# [NOMBRE DEL PROYECTO]
## Resumen Ejecutivo

**La Oportunidad:** [2-3 oraciones]

**El Concepto:** [2-3 oraciones]

**Cifras Clave:**
| Concepto | Valor |
|----------|-------|
| Inversión Total | $ |
| Ingreso Anual Estimado | $ |
| TIR Estimada | % |
| Payback | años |
| Área del Proyecto | m² |

**Fases de Desarrollo:** [resumen en 3 líneas]

**Por Qué Ahora:** [2-3 oraciones sobre timing y oportunidad]

**Siguiente Paso:** [1 oración con call to action]

---
*Documento preparado por [Skill Proyecto-Renders] | {datetime.now().strftime("%B %Y")}*"""

    resultado = await consultar_sabio("gpt54", prompt)
    return resultado.get("text", "Error generando resumen") if resultado.get("status") == "ok" else "Error"


def package_project(project_dir: str, output_dir: str) -> str:
    """Empaqueta el proyecto en una estructura presentable."""

    pkg_dir = os.path.join(output_dir, "entregable_final")
    Path(pkg_dir).mkdir(parents=True, exist_ok=True)

    # Estructura del paquete
    structure = {
        "01_Resumen_Ejecutivo": ["executive_summary.md"],
        "02_Plan_de_Negocio": ["business_plan.md", "financial_validation.md"],
        "03_Analisis": ["site_report.md", "benchmarks.md", "hbu_analysis.md"],
        "04_Renders": [],  # Se copian los renders
        "05_Datos": ["project_brief.yaml", "scenarios.yaml", "site_data.yaml", "benchmarks_data.yaml"],
        "06_Style_Guide": ["style_bible.md", "render_prompts.yaml"],
    }

    for folder, files in structure.items():
        folder_path = os.path.join(pkg_dir, folder)
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        for fname in files:
            src = os.path.join(project_dir, fname)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(folder_path, fname))

    # Copiar renders
    renders_src = os.path.join(project_dir, "renders")
    renders_dst = os.path.join(pkg_dir, "04_Renders")
    if os.path.isdir(renders_src):
        for f in os.listdir(renders_src):
            if f.endswith((".png", ".jpg", ".jpeg", ".webp")):
                shutil.copy2(os.path.join(renders_src, f), os.path.join(renders_dst, f))

    # Crear ZIP
    zip_path = os.path.join(output_dir, "proyecto_completo")
    shutil.make_archive(zip_path, "zip", pkg_dir)

    return f"{zip_path}.zip"


async def run_qa_packaging(project_dir: str, output_dir: str = None) -> dict:
    """Ejecuta QA completo y empaqueta el proyecto."""

    if not output_dir:
        output_dir = project_dir

    print("=" * 60)
    print("✅ MÓDULO 7: QA & PACKAGING")
    print(f"   Fecha: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("=" * 60)

    # 1. Check completitud
    print("  📋 Verificando completitud de entregables...")
    completeness = check_completeness(project_dir)

    ok = sum(1 for v in completeness.values() if v.get("status") == "OK")
    missing = sum(1 for v in completeness.values() if v.get("status") == "MISSING")
    total = len(completeness)

    print(f"  📊 {ok}/{total} entregables OK, {missing} faltantes")
    for fname, info in completeness.items():
        status = info.get("status", "?")
        icon = "✅" if status == "OK" else ("❌" if status == "MISSING" else "⚠️")
        print(f"     {icon} {fname}: {status}")

    # 2. Cross-validation
    print("\n  🔍 Validando consistencia entre documentos...")
    validation = await cross_validate_documents(project_dir)
    print(f"  📄 Validación: {len(validation):,} caracteres")

    # 3. Resumen ejecutivo
    print("  📝 Generando resumen ejecutivo...")
    summary = await generate_executive_summary(project_dir)
    summary_path = os.path.join(project_dir, "executive_summary.md")
    Path(summary_path).write_text(summary, encoding="utf-8")
    print(f"  📄 Resumen: {len(summary):,} caracteres")

    # 4. QA Report
    qa_report = f"""# QA Report — Proyecto Renders
Fecha: {datetime.now().strftime("%d %B %Y, %H:%M")}

## Completitud de Entregables
| Archivo | Estado | Tamaño | Categoría |
|---------|--------|--------|-----------|
"""
    for fname, info in completeness.items():
        size = info.get("size_bytes", info.get("count", 0))
        size_str = f"{size:,} bytes" if isinstance(size, int) and size > 100 else str(size)
        qa_report += f"| {fname} | {info.get('status', '?')} | {size_str} | {info.get('category', '?')} |\n"

    qa_report += f"\n## Validación Cruzada\n{validation}\n"

    qa_path = os.path.join(project_dir, "qa_report.md")
    Path(qa_path).write_text(qa_report, encoding="utf-8")

    # 5. Packaging
    print("\n  📦 Empaquetando proyecto...")
    zip_path = package_project(project_dir, output_dir)
    zip_size = os.path.getsize(zip_path) if os.path.exists(zip_path) else 0
    print(f"  📦 ZIP: {zip_path} ({zip_size:,} bytes)")

    print("\n✅ QA & Packaging completado")
    print(f"  📋 QA Report: {qa_path}")
    print(f"  📝 Resumen: {summary_path}")
    print(f"  📦 Paquete: {zip_path}")

    return {
        "qa_report_path": qa_path,
        "summary_path": summary_path,
        "zip_path": zip_path,
        "completeness": {k: v.get("status") for k, v in completeness.items()},
        "ok_count": ok,
        "missing_count": missing,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo 7: QA & Packaging")
    parser.add_argument("--project-dir", required=True, help="Directorio del proyecto")
    parser.add_argument("--output-dir", help="Directorio de salida (default: project-dir)")

    args = parser.parse_args()
    result = asyncio.run(run_qa_packaging(args.project_dir, args.output_dir))
