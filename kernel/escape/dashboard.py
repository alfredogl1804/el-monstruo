"""
Sprint ESCAPE-001 T5 — Escape History Dashboard.

Renderiza el historial de pulsos del Escape (Throttler Determinístico) en
dos modos:

  - HTML: snapshot estático autocontenido (sin JS, sin red, sin dependencias)
    visualizable abriendo el archivo en cualquier navegador. Pensado para
    pegar en el bridge como evidencia de cierre o postmortem.

  - JSON: serialización determinística del estado actual + filas recientes.
    Útil para consumo programático por dashboards superiores (Volante,
    Reloj Suizo aggregate dashboard, sprint reports).

CLI:
    python -m kernel.escape.dashboard --mode html  --out /tmp/escape.html
    python -m kernel.escape.dashboard --mode json  --out /tmp/escape.json
    python -m kernel.escape.dashboard --mode html  --limit 50

Sin DB: el dashboard cae gracefully a un template "no data" cuando no hay
SUPABASE_URL + SUPABASE_SERVICE_KEY configurados. Esto permite generarlo en
CI o en sandbox local sin acceso a Supabase.

Patrón gemelo a kernel.rotor.dashboard (Sprint ROTOR-001 T5).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger("escape.dashboard")


# ── Data layer ───────────────────────────────────────────────────────


def _fetch_recent_pulses(limit: int = 100) -> Optional[list[dict[str, Any]]]:
    """
    Lee filas recientes de escape_pulse_log via Supabase REST.

    Returns:
        list[dict] si la query tuvo éxito.
        None si no hay credenciales o la query falló (fail-soft).
    """
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    )
    if not url or not key:
        logger.info("escape_dashboard_no_credentials")
        return None

    try:
        import requests  # lazy import
    except ImportError:  # pragma: no cover
        logger.warning("escape_dashboard_requests_missing")
        return None

    endpoint = f"{url.rstrip('/')}/rest/v1/escape_pulse_log"
    params = {
        "select": (
            "pulse_id,consumer,decision,reason,energy_consumed,"
            "budget_consumed_usd,occurred_at,metadata"
        ),
        "order": "occurred_at.desc",
        "limit": str(min(limit, 1000)),
    }
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }

    try:
        resp = requests.get(endpoint, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            logger.warning(
                "escape_dashboard_fetch_failed",
                status=resp.status_code,
                body=resp.text[:200],
            )
            return None
        return list(resp.json())
    except Exception as exc:  # noqa: BLE001
        logger.warning("escape_dashboard_fetch_error", error=str(exc))
        return None


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calcula agregados rápidos sobre las filas recientes para el header.

    Returns dict con:
        - total_pulses: int
        - allowed_pulses: int
        - blocked_pulses: int
        - by_consumer: {consumer_name: {allowed, blocked, total}}
        - total_energy: Decimal-as-float
        - total_budget_usd: Decimal-as-float
        - oldest_at, newest_at
    """
    out: dict[str, Any] = {
        "total_pulses": len(rows),
        "allowed_pulses": 0,
        "blocked_pulses": 0,
        "by_consumer": {},
        "total_energy": 0.0,
        "total_budget_usd": 0.0,
        "oldest_at": None,
        "newest_at": None,
    }
    for r in rows:
        consumer = r.get("consumer", "unknown")
        decision = r.get("decision", "unknown")
        if consumer not in out["by_consumer"]:
            out["by_consumer"][consumer] = {"allowed": 0, "blocked": 0, "total": 0}
        out["by_consumer"][consumer]["total"] += 1
        if decision == "allow":
            out["allowed_pulses"] += 1
            out["by_consumer"][consumer]["allowed"] += 1
        elif decision == "block":
            out["blocked_pulses"] += 1
            out["by_consumer"][consumer]["blocked"] += 1
        try:
            out["total_energy"] += float(r.get("energy_consumed") or 0)
        except (TypeError, ValueError):
            pass
        try:
            out["total_budget_usd"] += float(r.get("budget_consumed_usd") or 0)
        except (TypeError, ValueError):
            pass
        occurred = r.get("occurred_at")
        if occurred:
            if out["oldest_at"] is None or occurred < out["oldest_at"]:
                out["oldest_at"] = occurred
            if out["newest_at"] is None or occurred > out["newest_at"]:
                out["newest_at"] = occurred
    return out


# ── HTML renderer ────────────────────────────────────────────────────


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>ESCAPE-001 — Pulse History</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0d1117;color:#c9d1d9;margin:0;padding:24px;}}
h1{{color:#58a6ff;margin:0 0 8px 0;font-size:22px;}}
.subtitle{{color:#8b949e;font-size:13px;margin-bottom:24px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:24px;}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:14px;}}
.card .label{{color:#8b949e;font-size:11px;text-transform:uppercase;letter-spacing:.5px;}}
.card .value{{color:#c9d1d9;font-size:24px;font-weight:600;margin-top:4px;}}
.card .value.green{{color:#3fb950;}}
.card .value.red{{color:#f85149;}}
.card .value.yellow{{color:#d29922;}}
h2{{color:#58a6ff;font-size:16px;margin:24px 0 12px 0;}}
table{{width:100%;border-collapse:collapse;background:#161b22;border:1px solid #30363d;border-radius:6px;overflow:hidden;}}
th{{background:#21262d;color:#58a6ff;text-align:left;padding:10px 14px;font-size:12px;text-transform:uppercase;}}
td{{padding:10px 14px;border-top:1px solid #30363d;font-size:13px;}}
.badge{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;}}
.badge.allow{{background:#1f3a2d;color:#3fb950;}}
.badge.block{{background:#3a1f1f;color:#f85149;}}
.consumer{{font-family:'SF Mono',Monaco,monospace;font-size:12px;color:#79c0ff;}}
.no-data{{background:#3a2f1f;border:1px solid #d29922;color:#d29922;padding:16px;border-radius:6px;text-align:center;}}
footer{{margin-top:32px;color:#6e7681;font-size:11px;}}
</style>
</head>
<body>
<h1>⏱️ ESCAPE-001 — Pulse History Dashboard</h1>
<div class="subtitle">Throttler Determinístico (Reloj Suizo · pieza magna #2) · snapshot {generated_at}</div>
{body}
<footer>Sprint ESCAPE-001 · kernel.escape.dashboard · Generado offline, sin JS, sin red.</footer>
</body>
</html>"""

_NO_DATA_BODY = """<div class="no-data">
  <strong>No data disponible.</strong><br>
  Razón posible: credenciales Supabase ausentes en el entorno, o la tabla
  <code>escape_pulse_log</code> aún no fue poblada (migración 0024 sin aplicar
  o el Escape aún no emitió pulsos).
</div>"""


def _render_html(
    rows: Optional[list[dict[str, Any]]],
    agg: Optional[dict[str, Any]],
    limit: int,
) -> str:
    """Renderiza el HTML autocontenido."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    if rows is None or agg is None or agg["total_pulses"] == 0:
        return _HTML_TEMPLATE.format(generated_at=generated_at, body=_NO_DATA_BODY)

    # Header agregados
    allowed_pct = (
        (agg["allowed_pulses"] / agg["total_pulses"] * 100)
        if agg["total_pulses"] > 0 else 0
    )
    cards = [
        ("Total pulsos", str(agg["total_pulses"]), ""),
        ("Allowed", str(agg["allowed_pulses"]), "green"),
        ("Blocked", str(agg["blocked_pulses"]), "red" if agg["blocked_pulses"] > 0 else ""),
        ("% Allowed", f"{allowed_pct:.1f}%", "green" if allowed_pct > 80 else "yellow"),
        ("Energy total", f"{agg['total_energy']:.1f}", ""),
        ("Budget USD", f"${agg['total_budget_usd']:.4f}", ""),
    ]
    cards_html = "".join(
        f'<div class="card"><div class="label">{html.escape(label)}</div>'
        f'<div class="value {cls}">{html.escape(value)}</div></div>'
        for label, value, cls in cards
    )

    # Tabla por consumer
    by_consumer_rows = []
    for consumer, stats in sorted(agg["by_consumer"].items()):
        c_pct = (stats["allowed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        by_consumer_rows.append(
            f"<tr><td><span class='consumer'>{html.escape(consumer)}</span></td>"
            f"<td>{stats['total']}</td>"
            f"<td><span class='badge allow'>{stats['allowed']}</span></td>"
            f"<td><span class='badge block'>{stats['blocked']}</span></td>"
            f"<td>{c_pct:.1f}%</td></tr>"
        )
    consumers_table = (
        "<h2>Por consumer</h2><table>"
        "<tr><th>Consumer</th><th>Total</th><th>Allowed</th><th>Blocked</th><th>% Allow</th></tr>"
        + "".join(by_consumer_rows)
        + "</table>"
    )

    # Tabla filas recientes
    recent_rows_html = []
    for r in rows[:limit]:
        decision = r.get("decision", "unknown")
        decision_class = "allow" if decision == "allow" else "block"
        recent_rows_html.append(
            f"<tr>"
            f"<td>{html.escape(str(r.get('pulse_id', '')))}</td>"
            f"<td><span class='consumer'>{html.escape(str(r.get('consumer', '')))}</span></td>"
            f"<td><span class='badge {decision_class}'>{html.escape(decision)}</span></td>"
            f"<td>{html.escape(str(r.get('reason', '') or ''))}</td>"
            f"<td>{html.escape(str(r.get('energy_consumed', '') or ''))}</td>"
            f"<td>{html.escape(str(r.get('budget_consumed_usd', '') or ''))}</td>"
            f"<td>{html.escape(str(r.get('occurred_at', '') or ''))}</td>"
            f"</tr>"
        )
    recent_table = (
        f"<h2>Últimos {len(recent_rows_html)} pulsos</h2><table>"
        "<tr><th>ID</th><th>Consumer</th><th>Decision</th><th>Reason</th>"
        "<th>Energy</th><th>Budget USD</th><th>Occurred at</th></tr>"
        + "".join(recent_rows_html)
        + "</table>"
    )

    window = ""
    if agg.get("oldest_at") and agg.get("newest_at"):
        window = (
            f"<div class='subtitle'>Ventana: "
            f"{html.escape(agg['oldest_at'])} → {html.escape(agg['newest_at'])}</div>"
        )

    body = f'<div class="grid">{cards_html}</div>{window}{consumers_table}{recent_table}'
    return _HTML_TEMPLATE.format(generated_at=generated_at, body=body)


# ── JSON renderer ────────────────────────────────────────────────────


def _render_json(
    rows: Optional[list[dict[str, Any]]],
    agg: Optional[dict[str, Any]],
    limit: int,
) -> str:
    """Renderiza JSON determinístico con agregados + filas recientes."""
    payload = {
        "schema": "escape_pulse_log.dashboard.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "available": rows is not None,
        "aggregates": agg or {},
        "recent_pulses": (rows or [])[:limit],
    }
    return json.dumps(payload, indent=2, default=str, sort_keys=True)


# ── Entry point ──────────────────────────────────────────────────────


def render(mode: str = "html", limit: int = 100) -> str:
    """Función pública del dashboard. Útil para tests y consumo programático."""
    rows = _fetch_recent_pulses(limit=limit)
    agg = _aggregate(rows) if rows is not None else None
    if mode == "json":
        return _render_json(rows, agg, limit)
    return _render_html(rows, agg, limit)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sprint ESCAPE-001 T5 — Escape History Dashboard"
    )
    parser.add_argument(
        "--mode", choices=("html", "json"), default="html",
        help="Output format (html|json)",
    )
    parser.add_argument(
        "--limit", type=int, default=100,
        help="Max filas a incluir (default 100, max 1000)",
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help="Path de salida (default stdout)",
    )
    args = parser.parse_args(argv)

    output = render(mode=args.mode, limit=args.limit)
    if args.out:
        args.out.write_text(output, encoding="utf-8")
        print(f"Wrote {args.out} ({len(output)} chars)")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
