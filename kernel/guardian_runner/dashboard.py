"""
Guardian Dashboard — Sprint GUARDIAN-AUTONOMO-001 T4
=====================================================
Reporte HTML estatico del estado de los 15 Objetivos Maestros del Guardian.

Filosofia:
  - Cero JavaScript. Cero CDN. Cero dependencias externas en el HTML.
  - El HTML se genera offline y se sirve via Railway static / file:// local.
  - Consulta las ultimas 24h de `guardian_audit_log` (migration 0021).
  - Si no hay corridas recientes, emite WARN visible pero no falla.

Uso:
    # Generar reporte desde la ultima corrida en DB
    python -m kernel.guardian_runner.dashboard --output /tmp/guardian.html

    # Generar reporte desde una corrida en vivo (sin DB)
    python -m kernel.guardian_runner.dashboard --live --no-persist \
        --output /tmp/guardian.html

    # Generar y abrir en browser
    python -m kernel.guardian_runner.dashboard --output /tmp/guardian.html --open

Fuente de verdad: tabla `guardian_audit_log` (Sprint GUARDIAN-AUTONOMO-001 T5).
Spec firmado: bridge/sprints_propuestos/sprint_GUARDIAN_AUTONOMO_001_activacion.md
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ── Constantes de presentacion ───────────────────────────────────────────────

OBJECTIVE_NAMES: dict[int, str] = {
    1: "Latido Persistente",
    2: "Memoria Causal",
    3: "HITL Soberano",
    4: "Nunca Se Equivoca Dos Veces",
    5: "Auditabilidad Total",
    6: "Resiliencia Auto-Reparable",
    7: "Costo Bajo Control",
    8: "Inteligencia Emergente",
    9: "Simulador Predictivo",
    10: "Causalidad Documentada",
    11: "Identidad Soberana",
    12: "Coordinacion Inter-Hilos",
    13: "Brand Engine",
    14: "El Guardian (meta-objetivo)",
    15: "Doctrina Viviente",
}

# Niveles segun spec: passing >= 80, warning 60-80, critical 40-60, emergency < 40
LEVEL_COLORS: dict[str, tuple[str, str]] = {
    # (background, foreground) — colores accesibles WCAG AA
    "passing": ("#1f7a3a", "#ffffff"),  # verde oscuro
    "warning": ("#b88a00", "#ffffff"),  # amarillo oscuro
    "critical": ("#c2410c", "#ffffff"),  # naranja oscuro
    "emergency": ("#9b1c1c", "#ffffff"),  # rojo oscuro
    "unknown": ("#6b7280", "#ffffff"),  # gris
}


def _classify(score_pct: Optional[float]) -> str:
    """Clasifica un score en passing|warning|critical|emergency|unknown."""
    if score_pct is None:
        return "unknown"
    if score_pct >= 80:
        return "passing"
    if score_pct >= 60:
        return "warning"
    if score_pct >= 40:
        return "critical"
    return "emergency"


# ── DB Access ────────────────────────────────────────────────────────────────


async def _fetch_latest_audit(db_url: Optional[str] = None) -> Optional[dict[str, Any]]:
    """
    Recuperar la ultima corrida del Guardian de `guardian_audit_log`.

    Returns:
        dict con la corrida o None si no hay DB / no hay corridas.

    Fail-soft: si DB no disponible, retorna None sin raise.
    """
    db_url = db_url or os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        logger.warning("dashboard_no_db_url")
        return None

    try:
        import asyncpg
    except ImportError:
        logger.warning("dashboard_asyncpg_not_installed")
        return None

    try:
        conn = await asyncpg.connect(db_url)
        try:
            # Sprint D-2: filtramos por embrion_id si esta seteado, pero
            # como guardian_audit_log no tiene embrion_id (es global), ordenamos
            # por finished_at desc y tomamos el primero.
            row = await conn.fetchrow(
                """
                SELECT
                    run_id,
                    trigger,
                    started_at,
                    finished_at,
                    duration_ms,
                    total_score_pct,
                    passing_count,
                    warning_count,
                    critical_count,
                    emergency_count,
                    objective_scores,
                    degradations_pp,
                    error
                FROM guardian_audit_log
                ORDER BY finished_at DESC NULLS LAST, started_at DESC
                LIMIT 1
                """
            )
            if not row:
                return None
            d = dict(row)
            # asyncpg devuelve JSONB como str sin parse; intentamos parse
            for key in ("objective_scores", "degradations_pp"):
                val = d.get(key)
                if isinstance(val, str):
                    try:
                        d[key] = json.loads(val)
                    except Exception:
                        d[key] = {}
            return d
        finally:
            await conn.close()
    except Exception as e:
        logger.warning("dashboard_fetch_failed: %s", e)
        return None


async def _fetch_recent_history(
    db_url: Optional[str] = None,
    hours: int = 168,  # 7 dias
) -> list[dict[str, Any]]:
    """
    Recuperar corridas de las ultimas N horas para mostrar tendencia.

    Returns:
        Lista de dicts con run_id, finished_at, total_score_pct.
    """
    db_url = db_url or os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        return []

    try:
        import asyncpg
    except ImportError:
        return []

    try:
        conn = await asyncpg.connect(db_url)
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            rows = await conn.fetch(
                """
                SELECT run_id, finished_at, total_score_pct,
                       passing_count, warning_count, critical_count, emergency_count
                FROM guardian_audit_log
                WHERE finished_at IS NOT NULL
                  AND finished_at >= $1
                ORDER BY finished_at DESC
                LIMIT 30
                """,
                cutoff,
            )
            return [dict(r) for r in rows]
        finally:
            await conn.close()
    except Exception as e:
        logger.warning("dashboard_history_fetch_failed: %s", e)
        return []


# ── HTML Rendering ───────────────────────────────────────────────────────────


def _html_escape(s: Any) -> str:
    """HTML-escape minimo para evitar XSS via valores de DB."""
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _fmt_pct(val: Optional[float]) -> str:
    if val is None:
        return "—"
    return f"{val:.2f}%"


def _fmt_ts(ts: Any) -> str:
    if not ts:
        return "—"
    if isinstance(ts, str):
        return ts
    if isinstance(ts, datetime):
        return ts.astimezone(timezone.utc).isoformat(timespec="seconds")
    return str(ts)


def _render_objective_row(obj_id: int, score: Optional[dict[str, Any]]) -> str:
    """Renderiza una fila <tr> para un objetivo."""
    name = OBJECTIVE_NAMES.get(obj_id, f"Objetivo {obj_id}")
    if score is None:
        level = "unknown"
        score_pct = None
        rationale = "(sin datos)"
    else:
        level = score.get("level") or _classify(score.get("score_pct"))
        score_pct = score.get("score_pct")
        rationale = score.get("rationale") or ""
    bg, fg = LEVEL_COLORS.get(level, LEVEL_COLORS["unknown"])

    return f"""
    <tr>
        <td class="obj-id">{obj_id:02d}</td>
        <td class="obj-name">{_html_escape(name)}</td>
        <td class="obj-score"><span class="badge" style="background:{bg};color:{fg};">{_fmt_pct(score_pct)}</span></td>
        <td class="obj-level"><span class="level-{_html_escape(level)}">{_html_escape(level)}</span></td>
        <td class="obj-rationale">{_html_escape(rationale)[:200]}</td>
    </tr>"""


def _render_history_row(row: dict[str, Any]) -> str:
    score = row.get("total_score_pct")
    level = _classify(score)
    bg, fg = LEVEL_COLORS.get(level, LEVEL_COLORS["unknown"])
    return f"""
    <tr>
        <td><code>{_html_escape(str(row.get("run_id", ""))[:8])}</code></td>
        <td>{_html_escape(_fmt_ts(row.get("finished_at")))}</td>
        <td><span class="badge" style="background:{bg};color:{fg};">{_fmt_pct(score)}</span></td>
        <td class="cnt-passing">{row.get("passing_count", 0)}</td>
        <td class="cnt-warning">{row.get("warning_count", 0)}</td>
        <td class="cnt-critical">{row.get("critical_count", 0)}</td>
        <td class="cnt-emergency">{row.get("emergency_count", 0)}</td>
    </tr>"""


def generate_html_report(
    latest: Optional[dict[str, Any]] = None,
    history: Optional[list[dict[str, Any]]] = None,
    generated_at: Optional[datetime] = None,
) -> str:
    """
    Genera el HTML estatico del dashboard.

    Args:
        latest: ultima corrida del Guardian (dict de guardian_audit_log) o None.
        history: lista de corridas recientes (max 30) o None.
        generated_at: timestamp de generacion del reporte.

    Returns:
        HTML completo como str.
    """
    history = history or []
    generated_at = generated_at or datetime.now(timezone.utc)

    if latest:
        objective_scores = latest.get("objective_scores") or {}
        total_score = latest.get("total_score_pct")
        passing = latest.get("passing_count", 0)
        warning = latest.get("warning_count", 0)
        critical = latest.get("critical_count", 0)
        emergency = latest.get("emergency_count", 0)
        run_id = latest.get("run_id", "—")
        trigger = latest.get("trigger", "—")
        started_at = _fmt_ts(latest.get("started_at"))
        finished_at = _fmt_ts(latest.get("finished_at"))
        duration_ms = latest.get("duration_ms", 0) or 0
        error = latest.get("error")
        degradations = latest.get("degradations_pp") or {}
    else:
        objective_scores = {}
        total_score = None
        passing = warning = critical = emergency = 0
        run_id = "—"
        trigger = "—"
        started_at = finished_at = "—"
        duration_ms = 0
        error = None
        degradations = {}

    # Filas de objetivos (1..15)
    rows_objectives = []
    for obj_id in range(1, 16):
        # objective_scores puede tener keys str o int dependiendo del JSON parse
        score_data = objective_scores.get(str(obj_id)) or objective_scores.get(obj_id)
        rows_objectives.append(_render_objective_row(obj_id, score_data))

    # Filas de historial
    rows_history = [_render_history_row(r) for r in history[:30]]

    # Banner WARN si no hay corrida reciente
    no_data_banner = ""
    if latest is None:
        no_data_banner = """
        <div class="banner-warn">
            <strong>WARN — sin datos.</strong> No se encontro corrida reciente del
            Guardian en <code>guardian_audit_log</code>. Posibles causas:
            (1) primera corrida pendiente, (2) DB no disponible, (3) scheduler
            no registrado. El handler <code>daily_guardian_audit</code> deberia
            correr diario a las 03:00 UTC. Revisar <code>scheduled_tasks</code>.
        </div>"""

    error_banner = ""
    if error:
        error_banner = f"""
        <div class="banner-error">
            <strong>ERROR en ultima corrida:</strong> {_html_escape(error)}
        </div>"""

    # Banner de degradaciones
    deg_banner = ""
    if degradations:
        deg_items = "".join(
            f"<li>Objetivo {k}: <strong>-{_html_escape(v)} pp</strong></li>" for k, v in degradations.items()
        )
        deg_banner = f"""
        <div class="banner-warn">
            <strong>Degradaciones detectadas (>= 10pp en 7 dias):</strong>
            <ul>{deg_items}</ul>
        </div>"""

    total_level = _classify(total_score)
    total_bg, total_fg = LEVEL_COLORS.get(total_level, LEVEL_COLORS["unknown"])

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guardian Dashboard — El Monstruo</title>
<style>
    :root {{
        --bg: #0f172a;
        --fg: #e2e8f0;
        --card: #1e293b;
        --border: #334155;
        --muted: #94a3b8;
        --accent: #38bdf8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
        margin: 0;
        padding: 24px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: var(--bg);
        color: var(--fg);
        line-height: 1.5;
    }}
    h1 {{ margin: 0 0 4px 0; font-size: 24px; }}
    h2 {{ margin: 32px 0 12px 0; font-size: 18px; color: var(--accent); }}
    .subtitle {{ color: var(--muted); font-size: 13px; margin-bottom: 24px; }}
    .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
        margin-bottom: 24px;
    }}
    .card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 16px;
    }}
    .card .label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}
    .card .value {{ font-size: 24px; font-weight: 600; margin-top: 4px; }}
    .card .value.score {{ font-size: 32px; }}
    table {{
        width: 100%;
        border-collapse: collapse;
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
    }}
    th, td {{
        padding: 10px 12px;
        text-align: left;
        border-bottom: 1px solid var(--border);
        font-size: 13px;
    }}
    th {{
        background: #0b1220;
        color: var(--muted);
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.05em;
    }}
    tr:last-child td {{ border-bottom: none; }}
    .badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
    }}
    .level-passing {{ color: #4ade80; }}
    .level-warning {{ color: #fbbf24; }}
    .level-critical {{ color: #fb923c; }}
    .level-emergency {{ color: #f87171; }}
    .level-unknown {{ color: var(--muted); }}
    .obj-id {{ font-family: monospace; color: var(--muted); width: 40px; }}
    .obj-name {{ font-weight: 500; }}
    .obj-rationale {{ color: var(--muted); font-size: 12px; max-width: 400px; }}
    .banner-warn, .banner-error {{
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 16px;
        font-size: 13px;
    }}
    .banner-warn {{ background: #422006; border: 1px solid #b88a00; color: #fde68a; }}
    .banner-error {{ background: #450a0a; border: 1px solid #9b1c1c; color: #fecaca; }}
    .banner-warn ul {{ margin: 8px 0 0 0; padding-left: 20px; }}
    code {{ background: #0b1220; padding: 1px 4px; border-radius: 3px; font-size: 12px; }}
    footer {{ margin-top: 32px; padding-top: 16px; border-top: 1px solid var(--border); color: var(--muted); font-size: 12px; }}
    .cnt-passing {{ color: #4ade80; }}
    .cnt-warning {{ color: #fbbf24; }}
    .cnt-critical {{ color: #fb923c; }}
    .cnt-emergency {{ color: #f87171; }}
</style>
</head>
<body>
    <h1>Guardian Dashboard</h1>
    <div class="subtitle">
        El Monstruo — 15 Objetivos Maestros · Sprint GUARDIAN-AUTONOMO-001
    </div>

    {no_data_banner}
    {error_banner}
    {deg_banner}

    <div class="grid">
        <div class="card">
            <div class="label">Score Global</div>
            <div class="value score">
                <span class="badge" style="background:{total_bg};color:{total_fg};">{_fmt_pct(total_score)}</span>
            </div>
        </div>
        <div class="card">
            <div class="label">Passing</div>
            <div class="value cnt-passing">{passing}</div>
        </div>
        <div class="card">
            <div class="label">Warning</div>
            <div class="value cnt-warning">{warning}</div>
        </div>
        <div class="card">
            <div class="label">Critical</div>
            <div class="value cnt-critical">{critical}</div>
        </div>
        <div class="card">
            <div class="label">Emergency</div>
            <div class="value cnt-emergency">{emergency}</div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="label">Run ID</div>
            <div class="value" style="font-size:14px;font-family:monospace;">{_html_escape(str(run_id)[:18])}</div>
        </div>
        <div class="card">
            <div class="label">Trigger</div>
            <div class="value" style="font-size:14px;">{_html_escape(trigger)}</div>
        </div>
        <div class="card">
            <div class="label">Iniciado (UTC)</div>
            <div class="value" style="font-size:13px;">{_html_escape(started_at)}</div>
        </div>
        <div class="card">
            <div class="label">Terminado (UTC)</div>
            <div class="value" style="font-size:13px;">{_html_escape(finished_at)}</div>
        </div>
        <div class="card">
            <div class="label">Duracion (ms)</div>
            <div class="value">{duration_ms}</div>
        </div>
    </div>

    <h2>Estado por Objetivo Maestro</h2>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Objetivo</th>
                <th>Score</th>
                <th>Nivel</th>
                <th>Racional</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows_objectives)}
        </tbody>
    </table>

    <h2>Historial (ultimos 7 dias)</h2>
    <table>
        <thead>
            <tr>
                <th>Run ID</th>
                <th>Terminado (UTC)</th>
                <th>Score</th>
                <th>Pass</th>
                <th>Warn</th>
                <th>Crit</th>
                <th>Emerg</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows_history) if rows_history else '<tr><td colspan="7" style="text-align:center;color:var(--muted);">Sin corridas recientes</td></tr>'}
        </tbody>
    </table>

    <footer>
        Reporte generado: {_fmt_ts(generated_at)} · Fuente: <code>guardian_audit_log</code> ·
        Sprint GUARDIAN-AUTONOMO-001 T4 · El Monstruo
    </footer>
</body>
</html>
"""


# ── CLI ──────────────────────────────────────────────────────────────────────


async def _run_live_audit() -> dict[str, Any]:
    """Ejecuta una corrida en vivo del Guardian (sin tocar DB para no contaminar).

    Nota: `run_audit` es sincrono (no async) y retorna `AuditCycleResult`,
    no un dict. Lo convertimos a dict via `.to_dict()` o serializacion manual.
    Lo corremos en un executor para no bloquear el event loop.
    """
    from kernel.guardian_runner.runner import run_audit

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: run_audit(trigger="manual", persist=False),
    )
    # AuditCycleResult es dataclass: convertir a dict
    if hasattr(result, "to_dict"):
        return result.to_dict()
    if hasattr(result, "__dict__"):
        return dict(result.__dict__)
    # Fallback: si ya es dict
    if isinstance(result, dict):
        return result
    return {"error": f"unexpected result type: {type(result).__name__}"}


async def _amain(args: argparse.Namespace) -> int:
    logging.basicConfig(
        level=logging.INFO if not args.quiet else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    latest: Optional[dict[str, Any]] = None
    history: list[dict[str, Any]] = []

    if args.live:
        logger.info("dashboard_running_live_audit")
        try:
            live_result = await _run_live_audit()
            # Adaptamos el resultado de run_audit al formato de guardian_audit_log
            latest = {
                "run_id": live_result.get("run_id", "live"),
                "trigger": live_result.get("trigger", "manual"),
                "started_at": live_result.get("started_at"),
                "finished_at": live_result.get("finished_at"),
                "duration_ms": live_result.get("duration_ms", 0),
                "total_score_pct": live_result.get("total_score_pct"),
                "passing_count": live_result.get("passing_count", 0),
                "warning_count": live_result.get("warning_count", 0),
                "critical_count": live_result.get("critical_count", 0),
                "emergency_count": live_result.get("emergency_count", 0),
                "objective_scores": live_result.get("objective_scores", {}),
                "degradations_pp": live_result.get("degradations_pp", {}),
                "error": live_result.get("error"),
            }
        except Exception as e:
            logger.error("dashboard_live_audit_failed: %s", e)
            return 2
    else:
        # Fetch desde DB
        latest = await _fetch_latest_audit(args.db_url)
        history = await _fetch_recent_history(args.db_url, hours=args.history_hours)

    html = generate_html_report(latest=latest, history=history)

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    logger.info("dashboard_written path=%s bytes=%d", str(output_path), len(html))

    if args.open:
        try:
            webbrowser.open(f"file://{output_path}")
        except Exception as e:
            logger.warning("dashboard_open_failed: %s", e)

    # Tambien escribimos un JSON de metadata para integraciones
    if args.json_meta:
        meta = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "output": str(output_path),
            "html_bytes": len(html),
            "has_data": latest is not None,
            "total_score_pct": latest.get("total_score_pct") if latest else None,
            "history_count": len(history),
        }
        Path(args.json_meta).write_text(json.dumps(meta, indent=2), encoding="utf-8")
        logger.info("dashboard_meta_written path=%s", args.json_meta)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="guardian_dashboard",
        description="Genera reporte HTML estatico del estado del Guardian (15 Objetivos Maestros).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="/tmp/guardian_dashboard.html",
        help="Ruta de salida del HTML (default: /tmp/guardian_dashboard.html)",
    )
    parser.add_argument(
        "--db-url",
        default=None,
        help="Postgres URL (default: env SUPABASE_DB_URL)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Ejecutar una corrida en vivo del Guardian en lugar de consultar DB (no persiste)",
    )
    parser.add_argument(
        "--no-persist",
        action="store_true",
        help="(compat con --live) No persistir la corrida en DB",
    )
    parser.add_argument(
        "--history-hours",
        type=int,
        default=168,
        help="Horas de historial a mostrar (default: 168 = 7 dias)",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Abrir el HTML en el browser default tras generar",
    )
    parser.add_argument(
        "--json-meta",
        default=None,
        help="Ruta opcional para escribir un JSON de metadata del reporte",
    )
    parser.add_argument("--quiet", action="store_true", help="Solo loguear WARN/ERROR")
    args = parser.parse_args()

    return asyncio.run(_amain(args))


if __name__ == "__main__":
    sys.exit(main())
