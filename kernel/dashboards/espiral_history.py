"""kernel.dashboards.espiral_history — Dashboard HTML/JSON/CLI de la Espiral.

Sprint ESPIRAL-001 T5 — visualiza embrion_homeostasis_log:
- Episodios por consumer en 24h/7d/30d
- Distribución de adjustment_reason (spike_dampening, undershoot_acceleration, return_to_canonical)
- Métrica clave: deviation_ratio promedio + tail (P95/P99)

Patrón idéntico a:
- kernel.escape.dashboard
- kernel.rotor.dashboard
- kernel.dashboards.cost_history

Render:
- HTML estático standalone (CDN-free, una sola página)
- JSON estructurado para consumo programático
- CLI text-only para audits via SSH

DSC-G-008 v3 §4: dashboard NO reescribe nada del log, sólo lee. Si la conexión
falla, retorna placeholder con "no data available".

Cierre del PR #116 puntualizó tickets de seguimiento:
- D7_DASHBOARD_XSS_AUDIT_001 (audit XSS de los dashboards Reloj Suizo) → este dashboard
  hereda esa deuda. Aplicamos html.escape() defensivo en todo string user-controlled
  (consumer es app-controlled pero por defensa en profundidad escapamos).
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Awaitable, Callable, Optional

import structlog

logger = structlog.get_logger("dashboards.espiral_history")


# Tipo del query function — inyectable. Recibe (window_hours,) y retorna lista de filas.
# Cada fila es dict con keys: id, created_at, consumer, pulse_rate_observed,
# pulse_rate_baseline, deviation_ratio, pulse_interval_adjusted_to,
# pulse_interval_canonical, adjustment_reason, window_minutes, metadata
QueryFn = Callable[[int], Awaitable[list[dict]]]


@dataclass
class HomeostasisRow:
    """Fila normalizada del log."""

    id: str
    created_at: datetime
    consumer: str
    pulse_rate_observed: float
    pulse_rate_baseline: float
    deviation_ratio: float
    pulse_interval_adjusted_to: int
    pulse_interval_canonical: int
    adjustment_reason: str
    window_minutes: int
    metadata: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "HomeostasisRow":
        # Acepta created_at como str ISO o datetime
        ca = d.get("created_at")
        if isinstance(ca, str):
            ca = datetime.fromisoformat(ca.replace("Z", "+00:00"))
        elif ca is None:
            ca = datetime.now(timezone.utc)
        return cls(
            id=str(d.get("id", "")),
            created_at=ca,
            consumer=str(d.get("consumer", "")),
            pulse_rate_observed=float(d.get("pulse_rate_observed", 0)),
            pulse_rate_baseline=float(d.get("pulse_rate_baseline", 0)),
            deviation_ratio=float(d.get("deviation_ratio", 0)),
            pulse_interval_adjusted_to=int(d.get("pulse_interval_adjusted_to", 0)),
            pulse_interval_canonical=int(d.get("pulse_interval_canonical", 0)),
            adjustment_reason=str(d.get("adjustment_reason", "")),
            window_minutes=int(d.get("window_minutes", 15)),
            metadata=d.get("metadata") or {},
        )


def _percentile(values: list[float], pct: float) -> float:
    """P95/P99 — implementación simple sin numpy."""
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(round((pct / 100.0) * (len(s) - 1)))))
    return s[k]


def aggregate_history(rows: list[HomeostasisRow]) -> dict:
    """Agrega métricas clave del histórico para summary.

    Returns:
        dict con:
        - total_events: int
        - by_consumer: dict[consumer] -> count
        - by_reason: dict[reason] -> count
        - deviation_avg: float
        - deviation_p95: float
        - deviation_p99: float
    """
    if not rows:
        return {
            "total_events": 0,
            "by_consumer": {},
            "by_reason": {
                "spike_dampening": 0,
                "undershoot_acceleration": 0,
                "return_to_canonical": 0,
            },
            "deviation_avg": 0.0,
            "deviation_p95": 0.0,
            "deviation_p99": 0.0,
        }

    by_consumer: dict[str, int] = {}
    by_reason: dict[str, int] = {
        "spike_dampening": 0,
        "undershoot_acceleration": 0,
        "return_to_canonical": 0,
    }
    deviations: list[float] = []

    for row in rows:
        by_consumer[row.consumer] = by_consumer.get(row.consumer, 0) + 1
        by_reason[row.adjustment_reason] = by_reason.get(row.adjustment_reason, 0) + 1
        deviations.append(row.deviation_ratio)

    avg = sum(deviations) / len(deviations) if deviations else 0.0
    return {
        "total_events": len(rows),
        "by_consumer": by_consumer,
        "by_reason": by_reason,
        "deviation_avg": round(avg, 4),
        "deviation_p95": round(_percentile(deviations, 95), 4),
        "deviation_p99": round(_percentile(deviations, 99), 4),
    }


def render_json(rows: list[HomeostasisRow], window_hours: int) -> str:
    """Render JSON estructurado del histórico."""
    summary = aggregate_history(rows)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_hours": window_hours,
        "summary": summary,
        "events": [
            {
                "id": r.id,
                "created_at": r.created_at.isoformat() if isinstance(r.created_at, datetime) else r.created_at,
                "consumer": r.consumer,
                "pulse_rate_observed": r.pulse_rate_observed,
                "pulse_rate_baseline": r.pulse_rate_baseline,
                "deviation_ratio": r.deviation_ratio,
                "pulse_interval_adjusted_to": r.pulse_interval_adjusted_to,
                "pulse_interval_canonical": r.pulse_interval_canonical,
                "adjustment_reason": r.adjustment_reason,
                "window_minutes": r.window_minutes,
            }
            for r in rows
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def render_html(rows: list[HomeostasisRow], window_hours: int) -> str:
    """Render HTML estático standalone.

    Defense in depth: html.escape() en todo string user-controlled (D7_DASHBOARD_XSS_AUDIT_001).
    """
    summary = aggregate_history(rows)

    # Build event rows (escaped)
    event_rows_html = ""
    for r in rows[:200]:  # cap visual a 200 eventos más recientes
        dev_class = (
            "spike"
            if r.adjustment_reason == "spike_dampening"
            else "under"
            if r.adjustment_reason == "undershoot_acceleration"
            else "ret"
        )
        ts = r.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(r.created_at, datetime) else str(r.created_at)
        event_rows_html += (
            f'<tr class="{dev_class}">'
            f"<td>{html.escape(ts)}</td>"
            f"<td>{html.escape(r.consumer)}</td>"
            f"<td>{r.pulse_rate_observed:.4f}</td>"
            f"<td>{r.pulse_rate_baseline:.4f}</td>"
            f"<td><strong>{r.deviation_ratio:.4f}</strong></td>"
            f"<td>{r.pulse_interval_adjusted_to}s</td>"
            f"<td>{r.pulse_interval_canonical}s</td>"
            f"<td>{html.escape(r.adjustment_reason)}</td>"
            f"</tr>"
        )

    by_consumer_html = (
        "".join(
            f"<li>{html.escape(c)}: <strong>{n}</strong></li>"
            for c, n in sorted(summary["by_consumer"].items(), key=lambda x: -x[1])
        )
        or "<li>(sin eventos)</li>"
    )

    by_reason = summary["by_reason"]
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Espiral Homeostasis — Dashboard ({window_hours}h)</title>
<style>
  body {{ font-family: 'JetBrains Mono', 'SF Mono', Menlo, monospace; background: #1C1917; color: #A8A29E; margin: 0; padding: 24px; }}
  h1 {{ color: #F97316; border-bottom: 2px solid #F97316; padding-bottom: 8px; }}
  h2 {{ color: #F97316; margin-top: 32px; }}
  .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 16px 0; }}
  .card {{ background: #292524; border-left: 4px solid #F97316; padding: 12px 16px; border-radius: 4px; }}
  .card .label {{ font-size: 11px; text-transform: uppercase; opacity: 0.7; }}
  .card .value {{ font-size: 24px; color: #FAFAF9; font-weight: bold; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 12px; }}
  th, td {{ padding: 6px 10px; text-align: left; border-bottom: 1px solid #44403C; }}
  th {{ background: #292524; color: #F97316; font-weight: bold; text-transform: uppercase; font-size: 11px; }}
  tr.spike {{ background: rgba(220, 38, 38, 0.08); }}
  tr.under {{ background: rgba(59, 130, 246, 0.08); }}
  tr.ret {{ background: rgba(34, 197, 94, 0.08); }}
  ul {{ list-style: none; padding-left: 0; }}
  li {{ padding: 4px 0; border-bottom: 1px dashed #44403C; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 11px; }}
  .badge-spike {{ background: #DC2626; color: white; }}
  .badge-under {{ background: #3B82F6; color: white; }}
  .badge-ret {{ background: #22C55E; color: white; }}
  .footer {{ margin-top: 32px; padding-top: 16px; border-top: 1px solid #44403C; opacity: 0.6; font-size: 11px; }}
</style>
</head>
<body>
<h1>🌀 Espiral (Hairspring) — Pieza #5 Reloj Suizo</h1>
<p>Feedback negativo dinámico — ventana últimas {window_hours}h. Sprint ESPIRAL-001.</p>

<h2>Resumen</h2>
<div class="summary">
  <div class="card"><div class="label">Total eventos</div><div class="value">{summary["total_events"]}</div></div>
  <div class="card"><div class="label"><span class="badge badge-spike">SPIKE</span> Dampening</div><div class="value">{by_reason["spike_dampening"]}</div></div>
  <div class="card"><div class="label"><span class="badge badge-under">UNDER</span> Acceleration</div><div class="value">{by_reason["undershoot_acceleration"]}</div></div>
  <div class="card"><div class="label"><span class="badge badge-ret">RET</span> Canonical</div><div class="value">{by_reason["return_to_canonical"]}</div></div>
  <div class="card"><div class="label">Deviation avg</div><div class="value">{summary["deviation_avg"]}</div></div>
  <div class="card"><div class="label">Deviation P95</div><div class="value">{summary["deviation_p95"]}</div></div>
  <div class="card"><div class="label">Deviation P99</div><div class="value">{summary["deviation_p99"]}</div></div>
</div>

<h2>Por consumer</h2>
<ul>{by_consumer_html}</ul>

<h2>Eventos recientes (últimos 200)</h2>
<table>
  <thead>
    <tr>
      <th>Timestamp UTC</th>
      <th>Consumer</th>
      <th>Rate Obs</th>
      <th>Rate Base</th>
      <th>Deviation</th>
      <th>Interval New</th>
      <th>Interval Canon</th>
      <th>Reason</th>
    </tr>
  </thead>
  <tbody>{event_rows_html}</tbody>
</table>

<div class="footer">
  Generado: {html.escape(datetime.now(timezone.utc).isoformat())}<br>
  El Monstruo · Reloj Suizo · Sprint ESPIRAL-001 (Pieza #5 Hairspring)
</div>
</body>
</html>
"""


def render_text_cli(rows: list[HomeostasisRow], window_hours: int) -> str:
    """Render text plain para CLI/SSH audits."""
    summary = aggregate_history(rows)
    lines = [
        "=" * 72,
        f"  Espiral (Hairspring) — Pieza #5 Reloj Suizo  ·  últimas {window_hours}h",
        "=" * 72,
        f"  Total eventos: {summary['total_events']}",
        f"  Spike dampening:        {summary['by_reason']['spike_dampening']}",
        f"  Undershoot acceleration:{summary['by_reason']['undershoot_acceleration']}",
        f"  Return to canonical:    {summary['by_reason']['return_to_canonical']}",
        f"  Deviation avg / P95 / P99: {summary['deviation_avg']} / {summary['deviation_p95']} / {summary['deviation_p99']}",
        "-" * 72,
        "  Por consumer:",
    ]
    for c, n in sorted(summary["by_consumer"].items(), key=lambda x: -x[1]):
        lines.append(f"    {c:40s} {n:>4d}")
    lines.append("-" * 72)
    lines.append(f"  Generado: {datetime.now(timezone.utc).isoformat()}")
    lines.append("=" * 72)
    return "\n".join(lines)


async def build_dashboard(
    window_hours: int = 24,
    query_fn: Optional[QueryFn] = None,
) -> tuple[list[HomeostasisRow], dict]:
    """Construye dataset del dashboard.

    Args:
        window_hours: ventana temporal a consultar.
        query_fn: función inyectable que retorna filas crudas. Si None, retorna [].

    Returns:
        Tupla (rows, summary).
    """
    rows: list[HomeostasisRow] = []
    if query_fn is not None:
        try:
            raw = await query_fn(window_hours)
            rows = [HomeostasisRow.from_dict(r) for r in raw]
        except Exception as e:  # noqa: BLE001
            logger.warning("dashboard_query_failed", error=str(e))
            rows = []
    summary = aggregate_history(rows)
    return rows, summary


def cli_main(argv: Optional[list[str]] = None) -> int:
    """CLI entrypoint para SSH/CI."""
    parser = argparse.ArgumentParser(
        description="Dashboard Espiral (Hairspring) — Pieza #5 Reloj Suizo",
    )
    parser.add_argument("--window-hours", type=int, default=24, help="Ventana en horas (default 24)")
    parser.add_argument(
        "--format",
        choices=("text", "json", "html"),
        default="text",
        help="Formato de salida (default text)",
    )
    parser.add_argument("--output", type=str, default=None, help="Archivo de salida (default stdout)")
    args = parser.parse_args(argv)

    # Sin query_fn inyectable desde CLI por defecto: retorna placeholder.
    # En producción, la integración real con Supabase REST se hace fuera
    # del CLI standalone (e.g., desde un wrapper en kernel.dashboards.runner).
    rows: list[HomeostasisRow] = []

    if args.format == "json":
        out = render_json(rows, args.window_hours)
    elif args.format == "html":
        out = render_html(rows, args.window_hours)
    else:
        out = render_text_cli(rows, args.window_hours)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(cli_main())


__all__ = [
    "HomeostasisRow",
    "aggregate_history",
    "render_json",
    "render_html",
    "render_text_cli",
    "build_dashboard",
    "cli_main",
]
