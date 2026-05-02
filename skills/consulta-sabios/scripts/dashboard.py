#!/usr/bin/env python3.11
"""
dashboard.py — Dashboard Operativo de consulta-sabios
=======================================================
Genera un reporte Markdown con todas las métricas operativas
del sistema. Diseñado para ser ejecutado periódicamente.

Secciones:
    1. Estado general del sistema
    2. Métricas por sabio
    3. Tendencias
    4. Alertas activas
    5. Mejoras pendientes
    6. Caché
    7. Retención de datos

Uso:
    python3.11 dashboard.py [--output dashboard.md]

Creado: 2026-04-08 (P3 auditoría sabios)
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyze_history import analyze
from db_store import init_db, query_improvements, query_runs, query_sabio_stats
from dossier_cache import stats as cache_stats


def generate_dashboard(output_path: str = None) -> str:
    """Genera el dashboard operativo completo."""

    init_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sections = []

    # ═══════════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════════
    sections.append(f"""# Dashboard Operativo — consulta-sabios
> Generado: {now}

---""")

    # ═══════════════════════════════════════════════════════════
    # 1. ESTADO GENERAL
    # ═══════════════════════════════════════════════════════════
    runs = query_runs(limit=1000)
    total_runs = len(runs)
    successful = sum(1 for r in runs if r.get("status") == "success")
    partial = sum(1 for r in runs if r.get("status") == "partial")
    failed = sum(1 for r in runs if r.get("status") == "failed")

    if total_runs > 0:
        sr = successful / total_runs
        status_emoji = "🟢" if sr >= 0.8 else "🟡" if sr >= 0.6 else "🔴"
    else:
        sr = 0
        status_emoji = "⚪"

    sections.append(f"""## 1. Estado General {status_emoji}

| Métrica | Valor |
|---------|-------|
| Total runs | {total_runs} |
| Exitosos | {successful} ({sr:.0%}) |
| Parciales | {partial} |
| Fallidos | {failed} |
| Última ejecución | {runs[0].get("timestamp_start", "N/A") if runs else "Nunca"} |""")

    # Score promedio
    scores = [r.get("score_global") for r in runs if r.get("score_global")]
    if scores:
        avg_score = sum(scores) / len(scores)
        sections.append(f"| Score promedio | {avg_score:.3f} |")

    # ═══════════════════════════════════════════════════════════
    # 2. MÉTRICAS POR SABIO
    # ═══════════════════════════════════════════════════════════
    sabio_stats = query_sabio_stats()

    if sabio_stats:
        sections.append("""
## 2. Métricas por Sabio

| Sabio | Consultas | Exitosos | Tasa | Duración Media | Quality |
|-------|-----------|----------|------|----------------|---------|""")

        for s in sabio_stats:
            total = s.get("total", 0)
            exitosos = s.get("exitosos", 0)
            tasa = f"{exitosos / total:.0%}" if total > 0 else "N/A"
            dur = f"{s.get('duracion_media', 0):.0f}ms" if s.get("duracion_media") else "N/A"
            quality = f"{s.get('quality_media', 0):.2f}" if s.get("quality_media") else "N/A"

            sections.append(f"| {s['sabio_id']} | {total} | {exitosos} | {tasa} | {dur} | {quality} |")
    else:
        sections.append("\n## 2. Métricas por Sabio\n\nSin datos de sabios aún.")

    # ═══════════════════════════════════════════════════════════
    # 3. TENDENCIAS
    # ═══════════════════════════════════════════════════════════
    analysis = analyze(last_n=50)
    tendencias = analysis.get("tendencias", {})

    sections.append("\n## 3. Tendencias")

    if tendencias:
        sr_trend = tendencias.get("success_rate_tendencia", "sin_datos")
        trend_emoji = {"mejorando": "📈", "estable": "➡️", "degradando": "📉"}.get(sr_trend, "❓")
        sections.append(f"\n- Success Rate: {trend_emoji} {sr_trend}")

        if tendencias.get("success_rate_primera_mitad") is not None:
            sections.append(
                f"  - Primera mitad: {tendencias['success_rate_primera_mitad']:.0%} → "
                f"Segunda mitad: {tendencias.get('success_rate_segunda_mitad', 0):.0%}"
            )
    else:
        sections.append("\nInsuficientes datos para tendencias.")

    # ═══════════════════════════════════════════════════════════
    # 4. ALERTAS
    # ═══════════════════════════════════════════════════════════
    alertas = analysis.get("alertas", [])

    sections.append("\n## 4. Alertas")

    if alertas:
        for a in alertas:
            severity = {"critica": "🔴", "alta": "🟠", "media": "🟡"}.get(a.get("severidad", ""), "⚪")
            sections.append(f"\n- {severity} **{a.get('tipo', '')}**: {a.get('mensaje', '')}")
    else:
        sections.append("\n✅ Sin alertas activas.")

    # ═══════════════════════════════════════════════════════════
    # 5. MEJORAS
    # ═══════════════════════════════════════════════════════════
    improvements = query_improvements()

    sections.append("\n## 5. Mejoras")

    if improvements:
        by_status = {}
        for imp in improvements:
            estado = imp.get("estado", "desconocido")
            by_status.setdefault(estado, []).append(imp)

        sections.append("\n| Estado | Cantidad |")
        sections.append("|--------|----------|")
        for estado, items in sorted(by_status.items()):
            sections.append(f"| {estado} | {len(items)} |")

        # Listar pendientes
        pendientes = by_status.get("propuesta", []) + by_status.get("aprobada", [])
        if pendientes:
            sections.append("\n### Pendientes de aplicar:")
            for p in pendientes[:5]:
                sections.append(f"- [{p.get('improvement_id', '')}] {p.get('descripcion', '')}")
    else:
        sections.append("\nSin mejoras registradas.")

    # ═══════════════════════════════════════════════════════════
    # 6. CACHÉ
    # ═══════════════════════════════════════════════════════════
    try:
        cs = cache_stats()
        sections.append(f"""
## 6. Caché de Dossier

| Métrica | Valor |
|---------|-------|
| Dossiers activos | {cs.get("activos", 0)} |
| Dossiers expirados | {cs.get("expirados", 0)} |
| Hits totales | {cs.get("hits_totales", 0)} |
| Chars almacenados | {cs.get("chars_totales", 0):,} |""")
    except Exception:
        sections.append("\n## 6. Caché de Dossier\n\nNo disponible.")

    # ═══════════════════════════════════════════════════════════
    # 7. SISTEMA DE ARCHIVOS
    # ═══════════════════════════════════════════════════════════
    skill_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    data_dir = skill_dir / "data"

    sections.append("\n## 7. Sistema de Archivos")

    if data_dir.exists():
        db_file = data_dir / "consulta_sabios.db"
        db_size = db_file.stat().st_size if db_file.exists() else 0

        runs_dir = data_dir / "runs"
        n_run_dirs = len(list(runs_dir.iterdir())) if runs_dir.exists() else 0

        sections.append(f"""
| Recurso | Valor |
|---------|-------|
| DB SQLite | {db_size / 1024:.1f} KB |
| Directorios de runs | {n_run_dirs} |
| Scripts | {len(list((skill_dir / "scripts").glob("*.py")))} |
| Config files | {len(list((skill_dir / "config").glob("*")))} |""")

    # ═══════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════
    sections.append(f"""
---
*Dashboard generado automáticamente por consulta-sabios v2.0*
*Fecha: {now}*""")

    report = "\n".join(sections)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"📊 Dashboard guardado: {output_path}")

    return report


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dashboard operativo")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    report = generate_dashboard(args.output)
    print(report)
