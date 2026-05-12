"""
kernel/rotor/dashboard.py — Dashboard del Rotor (HTML estático + CLI)

Sprint: ROTOR-001 (T5) — pieza diferencial Reloj Suizo
Owner: Hilo Ejecutor 2 (manus_hilo_b)
Fecha: 2026-05-12

Mismo patrón que kernel/guardian_runner/dashboard.py: HTML estático sin JS
(audit-friendly, copiable a Notion/PDF). Consulta rotor_activity_log + las
filas de embrion_budget_state con abort_reason='rotor_recharge%' para
mostrar el estado del Rotor en las últimas 24h.

Modos:
  - python -m kernel.rotor.dashboard           → HTML stdout
  - python -m kernel.rotor.dashboard --html    → HTML stdout (explícito)
  - python -m kernel.rotor.dashboard --json    → JSON stdout (para CI/CD)
  - python -m kernel.rotor.dashboard --out FILE → escribir a archivo

Anti-XSS: uso explícito de html.escape en TODOS los valores que vienen de DB.
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

logger = logging.getLogger("rotor.dashboard")


# ---------------------------------------------------------------------------
# Data fetcher (lazy psycopg)
# ---------------------------------------------------------------------------
def _fetch_rotor_state() -> Optional[dict[str, Any]]:
    """
    Consulta DB para obtener el estado del Rotor en las últimas 24h.

    Returns None si DB no accesible (caller maneja con plantilla "no data").
    """
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError:
        logger.warning("psycopg no instalado; dashboard sin datos live")
        return None

    db_url = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        logger.warning("SUPABASE_DB_URL no seteada; dashboard sin datos live")
        return None

    try:
        with psycopg.connect(db_url, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                # 1. Resumen 24h
                cur.execute(
                    """
                    SELECT
                      COUNT(*) AS total_rows,
                      COUNT(*) FILTER (WHERE consumed_by_embrion_at IS NULL) AS pending,
                      COUNT(*) FILTER (WHERE consumed_by_embrion_at IS NOT NULL) AS consumed,
                      COALESCE(SUM(energy_units) FILTER (WHERE energy_units > 0), 0) AS total_positive_units,
                      COALESCE(SUM(energy_units) FILTER (WHERE energy_units < 0), 0) AS total_negative_units
                    FROM public.rotor_activity_log
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    """
                )
                summary = cur.fetchone() or {}

                # 2. Breakdown por source (24h)
                cur.execute(
                    """
                    SELECT
                      source,
                      COUNT(*) AS rows,
                      COALESCE(SUM(energy_units), 0) AS total_units,
                      MAX(created_at) AS last_seen_at
                    FROM public.rotor_activity_log
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    GROUP BY source
                    ORDER BY total_units DESC NULLS LAST
                    """
                )
                by_source = [dict(r) for r in cur.fetchall()]

                # 3. Recharge cycles del día (vía embrion_budget_state)
                cur.execute(
                    """
                    SELECT
                      COUNT(*) AS recharge_cycles,
                      COALESCE(SUM(-cost_actual_usd), 0) AS total_recharged_usd
                    FROM public.embrion_budget_state
                    WHERE abort_reason LIKE 'rotor_recharge%'
                      AND (created_at AT TIME ZONE 'UTC')::date = (NOW() AT TIME ZONE 'UTC')::date
                    """
                )
                recharge_today = cur.fetchone() or {}

                # 4. Últimas 10 actividades
                cur.execute(
                    """
                    SELECT
                      id::text, source, actor, energy_units, consumed_by_embrion_at, created_at
                    FROM public.rotor_activity_log
                    ORDER BY created_at DESC
                    LIMIT 10
                    """
                )
                latest = [dict(r) for r in cur.fetchall()]

        return {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "summary_24h": {k: (str(v) if isinstance(v, Decimal) else v) for k, v in summary.items()},
            "by_source_24h": [
                {
                    "source": r["source"],
                    "rows": r["rows"],
                    "total_units": str(r["total_units"]),
                    "last_seen_at": r["last_seen_at"].isoformat() if r["last_seen_at"] else None,
                }
                for r in by_source
            ],
            "recharge_today": {
                "cycles": recharge_today.get("recharge_cycles", 0),
                "total_recharged_usd": str(recharge_today.get("total_recharged_usd", 0)),
            },
            "latest_activities": [
                {
                    "id": r["id"][:8],
                    "source": r["source"],
                    "actor": r["actor"],
                    "energy_units": str(r["energy_units"]) if r["energy_units"] is not None else None,
                    "consumed": r["consumed_by_embrion_at"] is not None,
                    "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                }
                for r in latest
            ],
        }
    except Exception as exc:
        logger.error("rotor.dashboard.fetch_failed", err=str(exc))
        return None


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------
_NO_DATA_HTML = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>Rotor Dashboard</title>
<style>body{font-family:-apple-system,sans-serif;max-width:900px;margin:40px auto;padding:20px;background:#fafafa;color:#333}
h1{border-bottom:2px solid #ccc;padding-bottom:10px}
.warn{background:#fff3cd;border-left:4px solid #f0ad4e;padding:15px;margin:20px 0}</style></head>
<body><h1>Rotor Dashboard</h1>
<div class="warn"><strong>Sin datos disponibles.</strong> Verificar:
<ul><li>SUPABASE_DB_URL configurada</li><li>psycopg instalado</li>
<li>Migración 0023 aplicada</li><li>Hubo actividad en las últimas 24h</li></ul></div></body></html>"""


def render_html(data: Optional[dict[str, Any]]) -> str:
    """Renderiza el dashboard del Rotor como HTML estático."""
    if data is None:
        return _NO_DATA_HTML

    e = html.escape  # alias anti-XSS

    summary = data.get("summary_24h", {})
    total_rows = e(str(summary.get("total_rows", 0)))
    pending = e(str(summary.get("pending", 0)))
    consumed = e(str(summary.get("consumed", 0)))
    pos_units = e(str(summary.get("total_positive_units", "0")))
    neg_units = e(str(summary.get("total_negative_units", "0")))

    recharge = data.get("recharge_today", {})
    cycles = e(str(recharge.get("cycles", 0)))
    recharged_usd = e(str(recharge.get("total_recharged_usd", "0")))

    # Tabla de sources
    rows_html = []
    for r in data.get("by_source_24h", []):
        last_seen = r.get("last_seen_at") or "—"
        rows_html.append(
            f"<tr><td>{e(r['source'])}</td>"
            f"<td>{e(str(r['rows']))}</td>"
            f"<td>${e(str(r['total_units']))}</td>"
            f"<td class='ts'>{e(last_seen[:19] if last_seen != '—' else last_seen)}</td></tr>"
        )
    by_source_table = "\n".join(rows_html) or "<tr><td colspan='4'><em>Sin datos en 24h</em></td></tr>"

    # Tabla de últimas actividades
    latest_html = []
    for r in data.get("latest_activities", []):
        units = r.get("energy_units") or "—"
        consumed_badge = (
            "<span class='badge ok'>consumido</span>"
            if r.get("consumed")
            else "<span class='badge pending'>pendiente</span>"
        )
        created = (r.get("created_at") or "—")[:19]
        latest_html.append(
            f"<tr><td class='id'>{e(r['id'])}</td>"
            f"<td>{e(r['source'])}</td>"
            f"<td>{e(r['actor'])}</td>"
            f"<td>${e(str(units))}</td>"
            f"<td>{consumed_badge}</td>"
            f"<td class='ts'>{e(created)}</td></tr>"
        )
    latest_table = "\n".join(latest_html) or "<tr><td colspan='6'><em>Sin actividad</em></td></tr>"

    fetched = e(data.get("fetched_at", "—"))

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>Rotor Dashboard</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:1100px;margin:30px auto;padding:20px;background:#fafafa;color:#333}}
h1{{border-bottom:2px solid #2c3e50;padding-bottom:10px}}
h2{{color:#2c3e50;margin-top:30px;border-left:4px solid #2c3e50;padding-left:10px}}
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;margin:20px 0}}
.kpi{{background:white;padding:15px;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,.1)}}
.kpi .label{{font-size:11px;text-transform:uppercase;color:#7f8c8d;letter-spacing:.5px}}
.kpi .val{{font-size:24px;font-weight:bold;color:#2c3e50;margin-top:5px}}
.kpi.recharge .val{{color:#27ae60}}
.kpi.pending .val{{color:#f39c12}}
.kpi.consumed .val{{color:#3498db}}
table{{width:100%;border-collapse:collapse;background:white;margin:15px 0;box-shadow:0 1px 3px rgba(0,0,0,.1)}}
th,td{{padding:8px 12px;text-align:left;border-bottom:1px solid #eee;font-size:13px}}
th{{background:#2c3e50;color:white;text-transform:uppercase;font-size:11px;letter-spacing:.5px}}
.ts{{font-family:monospace;color:#7f8c8d;font-size:12px}}
.id{{font-family:monospace;color:#888;font-size:11px}}
.badge{{display:inline-block;padding:2px 8px;border-radius:3px;font-size:10px;text-transform:uppercase;font-weight:bold}}
.badge.ok{{background:#d4edda;color:#155724}}
.badge.pending{{background:#fff3cd;color:#856404}}
footer{{margin-top:30px;padding-top:15px;border-top:1px solid #ccc;color:#7f8c8d;font-size:11px}}
</style></head><body>
<h1>Rotor Dashboard <small style="color:#7f8c8d;font-size:14px;font-weight:normal">— pieza Reloj Suizo</small></h1>

<h2>Últimas 24 horas</h2>
<div class="kpi-grid">
  <div class="kpi"><div class="label">Total rows</div><div class="val">{total_rows}</div></div>
  <div class="kpi pending"><div class="label">Pending</div><div class="val">{pending}</div></div>
  <div class="kpi consumed"><div class="label">Consumed</div><div class="val">{consumed}</div></div>
  <div class="kpi recharge"><div class="label">Units (+) USD</div><div class="val">${pos_units}</div></div>
  <div class="kpi"><div class="label">Penalties (−) USD</div><div class="val">${neg_units}</div></div>
</div>

<h2>Recharge hoy</h2>
<div class="kpi-grid">
  <div class="kpi recharge"><div class="label">Recharge cycles</div><div class="val">{cycles}</div></div>
  <div class="kpi recharge"><div class="label">Total recharged</div><div class="val">${recharged_usd}</div></div>
  <div class="kpi"><div class="label">Cap diario firmado</div><div class="val">$30.00</div></div>
</div>

<h2>Por source (24h)</h2>
<table><thead><tr><th>Source</th><th>Rows</th><th>Total units USD</th><th>Last seen</th></tr></thead>
<tbody>{by_source_table}</tbody></table>

<h2>Últimas 10 actividades</h2>
<table><thead><tr><th>ID</th><th>Source</th><th>Actor</th><th>Units</th><th>Status</th><th>Created at</th></tr></thead>
<tbody>{latest_table}</tbody></table>

<footer>Fetched at {fetched} — Sprint ROTOR-001 (Reloj Suizo) — Hilo Ejecutor 2</footer>
</body></html>"""


def render_json(data: Optional[dict[str, Any]]) -> str:
    """Renderiza como JSON (para CI/CD)."""
    return json.dumps(data or {"error": "no_data"}, indent=2, default=str)


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------
def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Rotor Dashboard")
    parser.add_argument("--json", action="store_true", help="Render como JSON")
    parser.add_argument("--html", action="store_true", help="Render como HTML (default)")
    parser.add_argument("--out", type=str, help="Path de output (default stdout)")
    args = parser.parse_args(argv)

    data = _fetch_rotor_state()
    output = render_json(data) if args.json else render_html(data)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Escrito en {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(output)

    return 0 if data is not None else 1


if __name__ == "__main__":
    sys.exit(main())
