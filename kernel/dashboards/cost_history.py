"""Dashboard estático: histórico de costo del Embrión.

Consulta `embrion_budget_state` en Supabase y produce un HTML estático con:

  * KPIs agregados (gasto últimas 24h, 7d y 30d)
  * Tabla de los últimos N cycles (cost_actual, cap_excedido, abort_reason, modelo)
  * Mini gráfica SVG del gasto diario acumulado (sin libs externas)
  * Sección de cycles abortados (frenazo del Budget Tracker)

Diseño:
  * Cero dependencias JS externas (Chart.js NO, todo SVG inline)
  * Cero credenciales en el HTML — se renderiza server-side
  * Idempotente: misma data → mismo HTML byte-a-byte (excepto generated_at)
  * Reusa `_SupabaseRest` y `_get_supabase_client` de `kernel.embrion_budget`
    para mantener una sola superficie de conexión a Supabase

Entry points:
  * `generate_dashboard_html(...)` — devuelve string HTML
  * `write_dashboard(output_path=...)` — escribe a disco
  * `python -m kernel.dashboards.cost_history --output bridge/embrion_dashboard.html`
"""
from __future__ import annotations

import argparse
import html
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Optional

from kernel.embrion_budget import _SupabaseRest, _get_supabase_client


# ────────────────────────────────────────────────────────────────────
# Modelo

@dataclass
class CostHistorySnapshot:
    """Snapshot agregado del estado del presupuesto para el dashboard."""

    rows: list[dict] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    daily_budget_usd: float = 0.0
    cap_per_latido_usd: float = 0.0

    @property
    def total_cycles(self) -> int:
        return len(self.rows)

    @property
    def aborted_cycles(self) -> list[dict]:
        return [r for r in self.rows if r.get("abort_reason")]

    @property
    def cap_excedido_count(self) -> int:
        return sum(1 for r in self.rows if r.get("cap_excedido"))

    def spend_in_window(self, hours: int) -> float:
        """Suma cost_actual_usd en las últimas `hours` horas."""
        cutoff = self.generated_at - timedelta(hours=hours)
        total = 0.0
        for r in self.rows:
            ts = _parse_iso(r.get("completed_at") or r.get("created_at"))
            if ts is None:
                continue
            if ts >= cutoff:
                total += float(r.get("cost_actual_usd") or 0)
        return round(total, 4)

    def daily_buckets(self, days: int = 14) -> list[tuple[str, float]]:
        """Bucketiza gasto por día (UTC) durante los últimos `days` días."""
        end = self.generated_at.replace(hour=0, minute=0, second=0, microsecond=0)
        buckets: dict[str, float] = {}
        for offset in range(days - 1, -1, -1):
            day = end - timedelta(days=offset)
            buckets[day.date().isoformat()] = 0.0

        for r in self.rows:
            ts = _parse_iso(r.get("completed_at") or r.get("created_at"))
            if ts is None:
                continue
            key = ts.date().isoformat()
            if key in buckets:
                buckets[key] += float(r.get("cost_actual_usd") or 0)

        return [(k, round(v, 4)) for k, v in buckets.items()]


# ────────────────────────────────────────────────────────────────────
# Helpers

def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        # Supabase devuelve `2026-05-10T12:24:33.123+00:00` o con `Z`
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def fetch_cost_history(
    *,
    limit: int = 500,
    supabase_client: Optional[_SupabaseRest] = None,
) -> CostHistorySnapshot:
    """Lee `embrion_budget_state` y construye un snapshot.

    Args:
        limit: máximo de filas a leer (default 500, suficiente para 14d).
        supabase_client: opcional, inyectable en tests.
    """
    client = supabase_client or _get_supabase_client()

    rows, _ = client.select(
        "embrion_budget_state",
        params={
            "select": (
                "cycle_id,latido_id,cap_per_latido_usd,cost_actual_usd,"
                "cost_estimated_usd,cap_excedido,abort_reason,tokens_used,"
                "tokens_input,tokens_output,model_used,trigger_type,"
                "trigger_detail,completed_at,created_at"
            ),
            "order": "created_at.desc",
            "limit": str(limit),
        },
    )

    daily_budget = float(os.environ.get("EMBRION_DAILY_BUDGET_USD", "5.0"))
    cap_per_latido = float(os.environ.get("EMBRION_CAP_PER_LATIDO_USD", "0.05"))

    return CostHistorySnapshot(
        rows=list(rows or []),
        daily_budget_usd=daily_budget,
        cap_per_latido_usd=cap_per_latido,
    )


# ────────────────────────────────────────────────────────────────────
# Render HTML (sin Jinja, sin libs externas)

_CSS = """
:root {
  --bg:#0b0f14; --panel:#111821; --line:#1f2a37; --text:#e6edf3;
  --muted:#8b98a5; --ok:#3fb950; --warn:#d29922; --err:#f85149;
  --accent:#58a6ff;
}
*{box-sizing:border-box}
body{margin:0;padding:24px;background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;
  font-size:14px;line-height:1.5}
h1{font-size:20px;margin:0 0 4px}
h2{font-size:15px;margin:24px 0 12px;color:var(--muted);text-transform:uppercase;
  letter-spacing:.05em}
.subtitle{color:var(--muted);margin:0 0 24px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px}
.kpi-label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.kpi-value{font-size:24px;font-weight:600;margin-top:6px;font-variant-numeric:tabular-nums}
.kpi-sub{font-size:11px;color:var(--muted);margin-top:4px}
table{width:100%;border-collapse:collapse;background:var(--panel);
  border:1px solid var(--line);border-radius:8px;overflow:hidden}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);
  font-variant-numeric:tabular-nums;font-size:13px}
th{background:#0d1520;color:var(--muted);font-weight:500;text-transform:uppercase;
  letter-spacing:.05em;font-size:11px}
tr:last-child td{border-bottom:none}
.tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:500}
.tag.ok{background:rgba(63,185,80,.15);color:var(--ok)}
.tag.warn{background:rgba(210,153,34,.15);color:var(--warn)}
.tag.err{background:rgba(248,81,73,.15);color:var(--err)}
.empty{padding:24px;text-align:center;color:var(--muted);font-style:italic}
.svg-wrap{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px}
.footer{margin-top:32px;font-size:11px;color:var(--muted);text-align:center}
.code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;
  background:#0d1520;padding:2px 6px;border-radius:3px;color:var(--accent)}
"""


def _render_kpi(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{html.escape(sub)}</div>' if sub else ""
    return (
        '<div class="card">'
        f'<div class="kpi-label">{html.escape(label)}</div>'
        f'<div class="kpi-value">{html.escape(value)}</div>'
        f'{sub_html}'
        '</div>'
    )


def _render_chart_svg(buckets: list[tuple[str, float]], daily_budget: float) -> str:
    """Renderiza SVG inline de barras verticales para gasto diario."""
    if not buckets:
        return '<div class="empty">Sin datos para graficar</div>'

    width, height = 720, 180
    pad_l, pad_r, pad_t, pad_b = 40, 12, 12, 28
    chart_w = width - pad_l - pad_r
    chart_h = height - pad_t - pad_b

    values = [v for _, v in buckets]
    max_v = max(max(values), daily_budget, 0.01)
    bar_w = chart_w / max(len(buckets), 1)

    bars = []
    for i, (day, v) in enumerate(buckets):
        h_px = (v / max_v) * chart_h if max_v > 0 else 0
        x = pad_l + i * bar_w + 1
        y = pad_t + (chart_h - h_px)
        color = "#f85149" if v > daily_budget else "#58a6ff"
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w-2:.1f}" '
            f'height="{h_px:.1f}" fill="{color}" rx="2">'
            f'<title>{html.escape(day)}: ${v:.4f}</title></rect>'
        )

    # Línea de daily budget
    budget_y = pad_t + chart_h - (daily_budget / max_v) * chart_h
    budget_line = (
        f'<line x1="{pad_l}" y1="{budget_y:.1f}" x2="{width-pad_r}" '
        f'y2="{budget_y:.1f}" stroke="#d29922" stroke-dasharray="4,4" stroke-width="1"/>'
        f'<text x="{width-pad_r-4}" y="{budget_y-4:.1f}" fill="#d29922" '
        f'font-size="10" text-anchor="end">cap diario ${daily_budget:.2f}</text>'
    )

    # Eje Y simplificado
    y_axis = (
        f'<text x="4" y="{pad_t+10}" fill="#8b98a5" font-size="10">${max_v:.2f}</text>'
        f'<text x="4" y="{pad_t+chart_h+4:.1f}" fill="#8b98a5" font-size="10">$0</text>'
    )

    # Etiquetas X (primero, último)
    if buckets:
        first_lbl = (
            f'<text x="{pad_l}" y="{height-8}" fill="#8b98a5" font-size="10">'
            f'{html.escape(buckets[0][0][5:])}</text>'
        )
        last_lbl = (
            f'<text x="{width-pad_r}" y="{height-8}" fill="#8b98a5" font-size="10" '
            f'text-anchor="end">{html.escape(buckets[-1][0][5:])}</text>'
        )
    else:
        first_lbl = last_lbl = ""

    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" '
        f'preserveAspectRatio="xMidYMid meet" role="img" aria-label="cost history">'
        f'{y_axis}{"".join(bars)}{budget_line}{first_lbl}{last_lbl}'
        f'</svg>'
    )


def _render_table(rows: Iterable[dict], limit: int = 30) -> str:
    rows = list(rows)[:limit]
    if not rows:
        return '<div class="empty">Sin cycles registrados</div>'

    head = (
        "<thead><tr>"
        "<th>cycle_id</th><th>completed_at (UTC)</th><th>model</th>"
        "<th>cost_actual</th><th>tokens</th><th>status</th><th>trigger</th>"
        "</tr></thead>"
    )

    body_rows = []
    for r in rows:
        cycle_id = html.escape(str(r.get("cycle_id") or ""))
        ts = r.get("completed_at") or r.get("created_at") or ""
        ts_short = html.escape(ts[:19].replace("T", " "))
        model = html.escape(str(r.get("model_used") or "—"))
        cost = float(r.get("cost_actual_usd") or 0)
        cost_str = f"${cost:.4f}"
        tokens = int(r.get("tokens_used") or 0)
        tokens_str = f"{tokens:,}" if tokens else "—"
        cap_excedido = bool(r.get("cap_excedido"))
        abort = r.get("abort_reason")
        if abort:
            status = f'<span class="tag err">{html.escape(str(abort))}</span>'
        elif cap_excedido:
            status = '<span class="tag warn">cap_excedido</span>'
        else:
            status = '<span class="tag ok">ok</span>'
        trigger = html.escape(str(r.get("trigger_type") or "—"))
        body_rows.append(
            f"<tr><td>{cycle_id}</td><td>{ts_short}</td><td>{model}</td>"
            f"<td>{cost_str}</td><td>{tokens_str}</td><td>{status}</td>"
            f"<td>{trigger}</td></tr>"
        )

    return f"<table>{head}<tbody>{''.join(body_rows)}</tbody></table>"


def _render_aborts(rows: Iterable[dict]) -> str:
    aborts = [r for r in rows if r.get("abort_reason")]
    if not aborts:
        return '<div class="empty">Sin cycles abortados — el embrión está corriendo limpio</div>'

    head = (
        "<thead><tr><th>cycle_id</th><th>when</th><th>abort_reason</th>"
        "<th>cost_estimated</th><th>model</th></tr></thead>"
    )
    body_rows = []
    for r in aborts[:20]:
        cycle_id = html.escape(str(r.get("cycle_id") or ""))
        ts = (r.get("completed_at") or r.get("created_at") or "")[:19]
        ts_short = html.escape(ts.replace("T", " "))
        reason = html.escape(str(r.get("abort_reason") or ""))
        est = float(r.get("cost_estimated_usd") or 0)
        model = html.escape(str(r.get("model_used") or "—"))
        body_rows.append(
            f'<tr><td>{cycle_id}</td><td>{ts_short}</td>'
            f'<td><span class="tag err">{reason}</span></td>'
            f'<td>${est:.4f}</td><td>{model}</td></tr>'
        )
    return f"<table>{head}<tbody>{''.join(body_rows)}</tbody></table>"


def render_dashboard_html(snapshot: CostHistorySnapshot) -> str:
    """Renderiza el HTML completo a partir de un snapshot."""
    spend_24h = snapshot.spend_in_window(24)
    spend_7d = snapshot.spend_in_window(24 * 7)
    spend_30d = snapshot.spend_in_window(24 * 30)

    pct_today = (
        (spend_24h / snapshot.daily_budget_usd) * 100
        if snapshot.daily_budget_usd > 0 else 0
    )

    kpis = (
        _render_kpi("Gasto últimas 24h", f"${spend_24h:.4f}",
                    f"{pct_today:.1f}% del cap diario (${snapshot.daily_budget_usd:.2f})")
        + _render_kpi("Gasto últimos 7 días", f"${spend_7d:.4f}",
                      f"avg/día ${spend_7d/7:.4f}")
        + _render_kpi("Gasto últimos 30 días", f"${spend_30d:.4f}",
                      f"avg/día ${spend_30d/30:.4f}")
        + _render_kpi("Cycles totales (window)", str(snapshot.total_cycles))
        + _render_kpi("Cap excedido", str(snapshot.cap_excedido_count),
                      f"cap/latido ${snapshot.cap_per_latido_usd:.4f}")
        + _render_kpi("Cycles abortados", str(len(snapshot.aborted_cycles)),
                      "frenazos del Budget Tracker")
    )

    chart = _render_chart_svg(snapshot.daily_buckets(days=14), snapshot.daily_budget_usd)
    table = _render_table(snapshot.rows, limit=30)
    aborts = _render_aborts(snapshot.rows)
    generated = snapshot.generated_at.strftime("%Y-%m-%d %H:%M:%S UTC")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>El Monstruo · Embrión · Cost History</title>
<style>{_CSS}</style>
</head>
<body>
<h1>Embrión · Cost History</h1>
<p class="subtitle">Histórico de costo por cycle del embrión autónomo · fuente: <span class="code">embrion_budget_state</span></p>

<h2>KPIs</h2>
<div class="grid">{kpis}</div>

<h2>Gasto diario (últimos 14 días)</h2>
<div class="svg-wrap">{chart}</div>

<h2>Últimos cycles</h2>
{table}

<h2>Cycles abortados</h2>
{aborts}

<div class="footer">
  Generado en {html.escape(generated)} · El Monstruo · Sprint EMBRION-NEEDS-002
</div>
</body>
</html>
"""


def generate_dashboard_html(
    *,
    limit: int = 500,
    supabase_client: Optional[_SupabaseRest] = None,
) -> str:
    """Pipeline completo: fetch + render. Útil para tests E2E."""
    snapshot = fetch_cost_history(limit=limit, supabase_client=supabase_client)
    return render_dashboard_html(snapshot)


def write_dashboard(
    *,
    output_path: str,
    limit: int = 500,
    supabase_client: Optional[_SupabaseRest] = None,
) -> str:
    """Escribe el dashboard a `output_path`. Devuelve el path absoluto."""
    html_str = generate_dashboard_html(limit=limit, supabase_client=supabase_client)
    abs_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_path) or ".", exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(html_str)
    return abs_path


# ────────────────────────────────────────────────────────────────────
# CLI

def _main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Genera el dashboard estático de cost history del embrión."
    )
    parser.add_argument(
        "--output",
        "-o",
        default="bridge/embrion_dashboard.html",
        help="Path destino del HTML (default: bridge/embrion_dashboard.html)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Filas máximas a leer de embrion_budget_state",
    )
    args = parser.parse_args(argv)

    try:
        path = write_dashboard(output_path=args.output, limit=args.limit)
    except Exception as exc:
        print(f"[cost_history] ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"[cost_history] dashboard escrito en {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
