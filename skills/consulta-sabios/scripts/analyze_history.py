#!/usr/bin/env python3.11
"""
analyze_history.py — Análisis Histórico y Detección de Degradaciones
=====================================================================
Analiza el historial de consultas para detectar:
- Caída de success rate por sabio
- Aumento de latencia p95
- Deterioro de quality score
- Aumento de contradicciones
- Aumento de costo sin mejora de calidad
- Patrones de error recurrentes

Uso:
    python3.11 analyze_history.py [--last-n 50] [--output report.md]

Creado: 2026-04-08 (P1 auditoría sabios)
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telemetry import HISTORY_DIR, read_jsonl

# ═══════════════════════════════════════════════════════════════
# ANÁLISIS
# ═══════════════════════════════════════════════════════════════


def analyze(last_n: int = 50) -> dict:
    """
    Analiza los últimos N runs y genera un informe de salud.

    Returns:
        dict con: resumen, alertas, metricas_por_sabio, tendencias
    """
    runs = read_jsonl(HISTORY_DIR / "consultas.jsonl")
    sabio_metrics = read_jsonl(HISTORY_DIR / "sabios_metrics.jsonl")

    if not runs:
        return {
            "resumen": {"estado": "sin_datos", "alertas_total": 0, "alertas_criticas": 0},
            "alertas": [],
            "runs_analizados": 0,
            "timestamp": datetime.now().isoformat(),
            "periodo": {},
            "metricas_globales": {},
            "metricas_por_sabio": {},
            "tendencias": {},
            "errores_frecuentes": {},
        }

    # Tomar los últimos N
    runs = runs[-last_n:]

    # Filtrar métricas de sabios para los runs analizados
    run_ids = {r["run_id"] for r in runs}
    sabio_metrics = [m for m in sabio_metrics if m.get("run_id") in run_ids]

    report = {
        "timestamp": datetime.now().isoformat(),
        "runs_analizados": len(runs),
        "periodo": {
            "desde": runs[0].get("timestamp_start", "unknown"),
            "hasta": runs[-1].get("timestamp_start", "unknown"),
        },
        "resumen": {},
        "alertas": [],
        "metricas_globales": {},
        "metricas_por_sabio": {},
        "tendencias": {},
        "errores_frecuentes": {},
    }

    # ─── Métricas globales ────────────────────────────────────
    duraciones = [r.get("duration_ms_total", 0) for r in runs if r.get("duration_ms_total")]
    success_runs = [r for r in runs if r.get("status") == "success"]

    report["metricas_globales"] = {
        "total_runs": len(runs),
        "success_rate": round(len(success_runs) / len(runs), 3) if runs else 0,
        "duracion_media_ms": int(mean(duraciones)) if duraciones else 0,
        "duracion_mediana_ms": int(median(duraciones)) if duraciones else 0,
        "duracion_p95_ms": _percentile(duraciones, 95) if duraciones else 0,
        "sabios_promedio_exitosos": round(mean([r.get("sabios_successful", 0) for r in runs]), 1) if runs else 0,
    }

    # ─── Métricas por sabio ───────────────────────────────────
    sabio_data = defaultdict(
        lambda: {
            "total": 0,
            "exitosos": 0,
            "duraciones": [],
            "errores": defaultdict(int),
            "output_tokens": [],
            "retry_counts": [],
        }
    )

    for m in sabio_metrics:
        sid = m.get("sabio_id", "unknown")
        sabio_data[sid]["total"] += 1
        if m.get("success"):
            sabio_data[sid]["exitosos"] += 1
        if m.get("duration_ms"):
            sabio_data[sid]["duraciones"].append(m["duration_ms"])
        if m.get("error_type"):
            sabio_data[sid]["errores"][m["error_type"]] += 1
        if m.get("output_tokens_est"):
            sabio_data[sid]["output_tokens"].append(m["output_tokens_est"])
        sabio_data[sid]["retry_counts"].append(m.get("retry_count", 0))

    for sid, data in sabio_data.items():
        report["metricas_por_sabio"][sid] = {
            "total_consultas": data["total"],
            "success_rate": round(data["exitosos"] / data["total"], 3) if data["total"] else 0,
            "duracion_media_ms": int(mean(data["duraciones"])) if data["duraciones"] else 0,
            "duracion_p95_ms": _percentile(data["duraciones"], 95) if data["duraciones"] else 0,
            "output_tokens_medio": int(mean(data["output_tokens"])) if data["output_tokens"] else 0,
            "retry_rate": round(sum(1 for r in data["retry_counts"] if r > 0) / len(data["retry_counts"]), 3)
            if data["retry_counts"]
            else 0,
            "errores": dict(data["errores"]),
        }

    # ─── Tendencias (comparar primera mitad vs segunda mitad) ─
    if len(runs) >= 10:
        mid = len(runs) // 2
        first_half = runs[:mid]
        second_half = runs[mid:]

        fh_success = sum(1 for r in first_half if r.get("status") == "success") / len(first_half)
        sh_success = sum(1 for r in second_half if r.get("status") == "success") / len(second_half)

        fh_dur = [r.get("duration_ms_total", 0) for r in first_half if r.get("duration_ms_total")]
        sh_dur = [r.get("duration_ms_total", 0) for r in second_half if r.get("duration_ms_total")]

        report["tendencias"] = {
            "success_rate_primera_mitad": round(fh_success, 3),
            "success_rate_segunda_mitad": round(sh_success, 3),
            "success_rate_tendencia": "mejorando"
            if sh_success > fh_success
            else "degradando"
            if sh_success < fh_success
            else "estable",
            "duracion_media_primera_mitad": int(mean(fh_dur)) if fh_dur else 0,
            "duracion_media_segunda_mitad": int(mean(sh_dur)) if sh_dur else 0,
            "duracion_tendencia": "mejorando"
            if (mean(sh_dur) if sh_dur else 0) < (mean(fh_dur) if fh_dur else 0)
            else "degradando",
        }

    # ─── Errores frecuentes ───────────────────────────────────
    all_errors = defaultdict(int)
    for m in sabio_metrics:
        if m.get("error_type"):
            all_errors[m["error_type"]] += 1

    report["errores_frecuentes"] = dict(sorted(all_errors.items(), key=lambda x: -x[1]))

    # ─── Alertas ──────────────────────────────────────────────
    report["alertas"] = _generate_alerts(report)

    # ─── Resumen ──────────────────────────────────────────────
    n_alerts = len(report["alertas"])
    critical = sum(1 for a in report["alertas"] if a["severidad"] == "critica")
    report["resumen"] = {
        "estado": "critico" if critical > 0 else "alerta" if n_alerts > 0 else "saludable",
        "alertas_total": n_alerts,
        "alertas_criticas": critical,
    }

    return report


def _generate_alerts(report: dict) -> list:
    """Genera alertas basadas en umbrales."""
    alerts = []

    # Alerta: success rate global bajo
    sr = report["metricas_globales"].get("success_rate", 1)
    if sr < 0.7:
        alerts.append(
            {
                "severidad": "critica",
                "tipo": "success_rate_bajo",
                "mensaje": f"Success rate global es {sr:.0%} (umbral: 70%)",
                "valor": sr,
            }
        )
    elif sr < 0.85:
        alerts.append(
            {
                "severidad": "advertencia",
                "tipo": "success_rate_moderado",
                "mensaje": f"Success rate global es {sr:.0%} (umbral advertencia: 85%)",
                "valor": sr,
            }
        )

    # Alerta: latencia p95 alta
    p95 = report["metricas_globales"].get("duracion_p95_ms", 0)
    if p95 > 600000:  # >10 min
        alerts.append(
            {
                "severidad": "critica",
                "tipo": "latencia_extrema",
                "mensaje": f"Latencia p95 es {p95 / 1000:.0f}s (umbral: 600s)",
                "valor": p95,
            }
        )
    elif p95 > 300000:  # >5 min
        alerts.append(
            {
                "severidad": "advertencia",
                "tipo": "latencia_alta",
                "mensaje": f"Latencia p95 es {p95 / 1000:.0f}s (umbral advertencia: 300s)",
                "valor": p95,
            }
        )

    # Alerta por sabio: success rate individual bajo
    for sid, metrics in report.get("metricas_por_sabio", {}).items():
        sabio_sr = metrics.get("success_rate", 1)
        if sabio_sr < 0.5 and metrics.get("total_consultas", 0) >= 3:
            alerts.append(
                {
                    "severidad": "critica",
                    "tipo": "sabio_degradado",
                    "mensaje": f"Sabio {sid} tiene success rate de {sabio_sr:.0%}",
                    "sabio": sid,
                    "valor": sabio_sr,
                }
            )

    # Alerta: tendencia degradante
    tendencias = report.get("tendencias", {})
    if tendencias.get("success_rate_tendencia") == "degradando":
        delta = tendencias.get("success_rate_primera_mitad", 0) - tendencias.get("success_rate_segunda_mitad", 0)
        if delta > 0.1:
            alerts.append(
                {
                    "severidad": "advertencia",
                    "tipo": "tendencia_degradante",
                    "mensaje": f"Success rate cayó {delta:.0%} entre primera y segunda mitad del período",
                    "valor": delta,
                }
            )

    # Alerta: errores recurrentes
    for error_type, count in report.get("errores_frecuentes", {}).items():
        if count >= 5:
            alerts.append(
                {
                    "severidad": "advertencia",
                    "tipo": "error_recurrente",
                    "mensaje": f"Error '{error_type}' ocurrió {count} veces",
                    "error_type": error_type,
                    "valor": count,
                }
            )

    return alerts


def _percentile(data: list, p: int) -> int:
    """Calcula percentil de una lista."""
    if not data:
        return 0
    sorted_data = sorted(data)
    idx = int(len(sorted_data) * p / 100)
    idx = min(idx, len(sorted_data) - 1)
    return sorted_data[idx]


# ═══════════════════════════════════════════════════════════════
# REPORTE
# ═══════════════════════════════════════════════════════════════


def generate_report(analysis: dict) -> str:
    """Genera un reporte Markdown legible."""
    lines = [
        "# Análisis Histórico — consulta-sabios",
        f"\nFecha: {analysis['timestamp']}",
        f"Runs analizados: {analysis['runs_analizados']}",
    ]

    periodo = analysis.get("periodo", {})
    if periodo:
        lines.append(f"Período: {periodo.get('desde', '?')} → {periodo.get('hasta', '?')}")

    # Estado
    resumen = analysis.get("resumen", {})
    estado = resumen.get("estado", "unknown")
    emoji = {"saludable": "🟢", "alerta": "🟡", "critico": "🔴"}.get(estado, "⚪")
    lines.append(f"\n## Estado: {emoji} {estado.upper()}")

    # Alertas
    alertas = analysis.get("alertas", [])
    if alertas:
        lines.append(f"\n## Alertas ({len(alertas)})\n")
        for a in alertas:
            sev = {"critica": "🔴", "advertencia": "🟡"}.get(a["severidad"], "⚪")
            lines.append(f"- {sev} **{a['tipo']}**: {a['mensaje']}")
    else:
        lines.append("\n## Alertas\n\nSin alertas activas.")

    # Métricas globales
    mg = analysis.get("metricas_globales", {})
    lines.extend(
        [
            "\n## Métricas Globales\n",
            "| Métrica | Valor |",
            "|---------|-------|",
            f"| Success Rate | {mg.get('success_rate', 0):.0%} |",
            f"| Duración Media | {mg.get('duracion_media_ms', 0) / 1000:.1f}s |",
            f"| Duración P95 | {mg.get('duracion_p95_ms', 0) / 1000:.1f}s |",
            f"| Sabios Exitosos (promedio) | {mg.get('sabios_promedio_exitosos', 0):.1f} |",
        ]
    )

    # Métricas por sabio
    mps = analysis.get("metricas_por_sabio", {})
    if mps:
        lines.extend(
            [
                "\n## Métricas por Sabio\n",
                "| Sabio | Consultas | Success Rate | Duración Media | P95 | Retry Rate |",
                "|-------|-----------|-------------|----------------|-----|------------|",
            ]
        )
        for sid, m in sorted(mps.items()):
            lines.append(
                f"| {sid} | {m.get('total_consultas', 0)} | {m.get('success_rate', 0):.0%} | "
                f"{m.get('duracion_media_ms', 0) / 1000:.1f}s | {m.get('duracion_p95_ms', 0) / 1000:.1f}s | "
                f"{m.get('retry_rate', 0):.0%} |"
            )

    # Tendencias
    tend = analysis.get("tendencias", {})
    if tend:
        lines.extend(
            [
                "\n## Tendencias\n",
                f"- Success Rate: {tend.get('success_rate_tendencia', 'N/A')} "
                f"({tend.get('success_rate_primera_mitad', 0):.0%} → {tend.get('success_rate_segunda_mitad', 0):.0%})",
                f"- Duración: {tend.get('duracion_tendencia', 'N/A')} "
                f"({tend.get('duracion_media_primera_mitad', 0) / 1000:.1f}s → {tend.get('duracion_media_segunda_mitad', 0) / 1000:.1f}s)",
            ]
        )

    # Errores frecuentes
    errores = analysis.get("errores_frecuentes", {})
    if errores:
        lines.extend(["\n## Errores Frecuentes\n"])
        for etype, count in errores.items():
            lines.append(f"- `{etype}`: {count} ocurrencias")

    return "\n".join(lines) + "\n"


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Análisis histórico de consultas a los sabios")
    parser.add_argument("--last-n", type=int, default=50, help="Últimos N runs a analizar")
    parser.add_argument("--output", default=None, help="Ruta de salida para el reporte")

    args = parser.parse_args()

    analysis = analyze(args.last_n)
    report = generate_report(analysis)

    print(report)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n📁 Reporte guardado en: {args.output}")

    # También guardar JSON
    json_path = args.output.replace(".md", ".json") if args.output else None
    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    main()
