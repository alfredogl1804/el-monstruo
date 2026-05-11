"""
kernel/dashboards/cowork_sessions.py — T6 PREMIUM Sprint COWORK-RUNTIME-001

Dashboard HTML estatico de sesiones Cowork.

Lee tabla `cowork_sesiones` (creada en migration 0009) y genera HTML autocontenido
en `bridge/cowork_session_dashboard.html` con metricas binarias visibles para Alfredo.

Sin servidor, sin auth. Mismo patron que kernel/dashboards/cost_history.py.
Refs: M6 de AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from kernel.cowork_runtime.session_memory import (  # noqa: E402
    SessionMemoryStore,
    CoworkSesion,
)


@dataclass
class DashboardMetrics:
    total_sesiones: int
    sesiones_24h: int
    sesiones_7d: int
    preflight_ratio: float
    avance_ratio: float
    sesiones_audit_only: int
    sesiones_avance_real: int
    palabras_clave_alfredo: dict = field(default_factory=dict)
    correctivos_count: dict = field(default_factory=dict)
    ultima_sesion: Optional[CoworkSesion] = None


class CoworkSessionsDashboard:
    """Genera dashboard HTML de sesiones Cowork."""

    DEFAULT_OUTPUT = _REPO_ROOT / "bridge" / "cowork_session_dashboard.html"

    def __init__(
        self,
        store: Optional[SessionMemoryStore] = None,
        output_path: Optional[Path] = None,
        lookback_days: int = 30,
        limit: int = 200,
    ) -> None:
        self.store = store or SessionMemoryStore()
        self.output_path = output_path or self.DEFAULT_OUTPUT
        self.lookback_days = lookback_days
        self.limit = limit

    def generate(self) -> Path:
        sesiones = self.store.read_recent(limit=self.limit)
        metrics = self._compute_metrics(sesiones)
        html_text = self._render_html(metrics, sesiones)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(html_text, encoding="utf-8")
        return self.output_path

    @staticmethod
    def _parse_dt(s: Optional[str]) -> datetime:
        if not s:
            return datetime.now(timezone.utc)
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return datetime.now(timezone.utc)

    @staticmethod
    def _as_list(v) -> list:
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [parsed]
            except Exception:
                return [v] if v else []
        return [v]

    def _compute_metrics(self, sesiones: list[dict]) -> DashboardMetrics:
        now = datetime.now(timezone.utc)
        h24 = now - timedelta(hours=24)
        d7 = now - timedelta(days=7)

        total = len(sesiones)
        s_24h = sum(1 for s in sesiones if self._parse_dt(s.get("fecha_inicio")) >= h24)
        s_7d = sum(1 for s in sesiones if self._parse_dt(s.get("fecha_inicio")) >= d7)
        preflight_ok = sum(1 for s in sesiones if s.get("pre_flight_ejecutado"))
        avance_ok = sum(1 for s in sesiones if (s.get("commits_productivos") or 0) > 0)
        audit_only = sum(
            1 for s in sesiones
            if (s.get("commits_productivos") or 0) == 0
            and self._as_list(s.get("violaciones_detectadas"))
        )

        preflight_ratio = (preflight_ok / total) if total else 0.0
        avance_ratio = (avance_ok / total) if total else 0.0

        palabras: dict = {}
        correctivos: dict = {}
        for s in sesiones:
            if self._parse_dt(s.get("fecha_inicio")) < d7:
                continue
            for k in self._as_list(s.get("palabras_clave_alfredo")):
                palabras[k] = palabras.get(k, 0) + 1
            for c in self._as_list(s.get("correctivos_recibidos")):
                key = (c if isinstance(c, str) else str(c))[:50]
                correctivos[key] = correctivos.get(key, 0) + 1

        ultima = None
        if sesiones:
            ultima = CoworkSesion.from_dict(sesiones[0])

        return DashboardMetrics(
            total_sesiones=total,
            sesiones_24h=s_24h,
            sesiones_7d=s_7d,
            preflight_ratio=preflight_ratio,
            avance_ratio=avance_ratio,
            sesiones_audit_only=audit_only,
            sesiones_avance_real=avance_ok,
            palabras_clave_alfredo=palabras,
            correctivos_count=correctivos,
            ultima_sesion=ultima,
        )

    def _render_html(self, m: DashboardMetrics, sesiones: list[dict]) -> str:
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        preflight_color = "#22c55e" if m.preflight_ratio >= 0.95 else "#f59e0b" if m.preflight_ratio >= 0.5 else "#ef4444"
        avance_color = "#22c55e" if m.avance_ratio >= 0.7 else "#f59e0b" if m.avance_ratio >= 0.3 else "#ef4444"

        kw_rows = ""
        for kw, count in sorted(m.palabras_clave_alfredo.items(), key=lambda x: -x[1])[:15]:
            kw_rows += f"<tr><td><code>{html.escape(str(kw))}</code></td><td>{count}</td></tr>\n"
        if not kw_rows:
            kw_rows = "<tr><td colspan='2'><em>Sin correctivos en los ultimos 7 dias</em></td></tr>"

        sess_rows = ""
        for s in sesiones[:20]:
            preflight_ok = bool(s.get("pre_flight_ejecutado"))
            preflight_icon = "✓" if preflight_ok else "✗"
            preflight_class = "ok" if preflight_ok else "fail"
            commits = s.get("commits_productivos") or 0
            violaciones = len(self._as_list(s.get("violaciones_detectadas")))
            inicio = (s.get("fecha_inicio") or "")[:16].replace("T", " ")
            sprint = html.escape(str(s.get("sprint_activo") or ""))
            duracion = s.get("duracion_minutos") or "—"
            sess_rows += (
                f"<tr>"
                f"<td>{inicio}</td>"
                f"<td>{sprint}</td>"
                f"<td class='{preflight_class}'>{preflight_icon}</td>"
                f"<td>{commits}</td>"
                f"<td>{violaciones}</td>"
                f"<td>{duracion}</td>"
                f"</tr>\n"
            )
        if not sess_rows:
            sess_rows = "<tr><td colspan='6'><em>Sin sesiones registradas</em></td></tr>"

        ultima_block = ""
        if m.ultima_sesion:
            u = m.ultima_sesion
            deudas_list = self._as_list(u.deudas_pendientes_proxima_sesion)
            deudas = "<br>".join(html.escape(str(d)) for d in deudas_list[:5]) or "<em>ninguna</em>"
            correctivos_list = self._as_list(u.correctivos_recibidos)
            correctivos = "<br>".join(html.escape(str(c))[:120] for c in correctivos_list[-5:]) or "<em>ninguno</em>"
            violaciones_list = self._as_list(u.violaciones_detectadas)
            ultima_block = f"""
            <div class="card">
              <h2>Ultima sesion</h2>
              <p><strong>ID:</strong> <code>{html.escape(u.id or '—')}</code></p>
              <p><strong>Sprint activo:</strong> {html.escape(u.sprint_activo or '—')}</p>
              <p><strong>Fecha inicio:</strong> {html.escape(u.fecha_inicio or '—')}</p>
              <p><strong>Duracion:</strong> {u.duracion_minutos or '—'} min · <strong>Turnos:</strong> {u.turnos_totales}</p>
              <p><strong>Pre-flight ejecutado:</strong>
                 <span class="{'ok' if u.pre_flight_ejecutado else 'fail'}">
                   {'SI' if u.pre_flight_ejecutado else 'NO'}
                 </span>
              </p>
              <p><strong>Commits productivos:</strong> {u.commits_productivos}</p>
              <p><strong>Violaciones detectadas:</strong> {len(violaciones_list)}</p>
              <p><strong>Kernel version:</strong> <code>{html.escape(u.kernel_version or '—')}</code></p>
              <p><strong>Embrion ultimo latido:</strong> <code>{html.escape(u.embrion_ultimo_latido or '—')}</code></p>
              <p><strong>Resumen lecciones:</strong> <em>{html.escape(u.resumen_lecciones or '(ninguno)')}</em></p>
              <p><strong>Correctivos recibidos:</strong><br>{correctivos}</p>
              <p><strong>Deudas pendientes proxima sesion:</strong><br>{deudas}</p>
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<title>Cowork Sessions Dashboard — El Monstruo</title>
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:24px; }}
  h1 {{ color:#fff; margin-top:0; }}
  h2 {{ color:#cbd5e1; border-bottom:1px solid #334155; padding-bottom:6px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; margin-bottom:24px; }}
  .kpi {{ background:#1e293b; border-radius:8px; padding:18px; border-left:4px solid #475569; }}
  .kpi .v {{ font-size:32px; font-weight:bold; color:#fff; }}
  .kpi .l {{ font-size:13px; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; margin-top:4px; }}
  .card {{ background:#1e293b; border-radius:8px; padding:18px; margin-bottom:16px; }}
  table {{ width:100%; border-collapse:collapse; }}
  th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid #334155; font-size:13px; }}
  th {{ color:#94a3b8; font-weight:600; text-transform:uppercase; font-size:11px; letter-spacing:0.05em; }}
  code {{ background:#0f172a; padding:2px 6px; border-radius:3px; font-size:12px; }}
  .ok {{ color:#22c55e; font-weight:bold; }}
  .fail {{ color:#ef4444; font-weight:bold; }}
  .footer {{ margin-top:24px; padding-top:16px; border-top:1px solid #334155; color:#64748b; font-size:12px; }}
  .bar {{ height:8px; background:#334155; border-radius:4px; overflow:hidden; margin-top:6px; }}
  .bar > div {{ height:100%; transition:width 0.3s; }}
</style>
</head>
<body>
<h1>Cowork Sessions Dashboard</h1>
<p style="color:#94a3b8; margin-top:-12px;">M6 — Visibilidad de Alfredo de la salud operacional de Cowork</p>

<div class="grid">
  <div class="kpi" style="border-left-color:#3b82f6;">
    <div class="v">{m.total_sesiones}</div>
    <div class="l">Sesiones totales</div>
  </div>
  <div class="kpi" style="border-left-color:#8b5cf6;">
    <div class="v">{m.sesiones_24h}</div>
    <div class="l">Ultimas 24h</div>
  </div>
  <div class="kpi" style="border-left-color:#06b6d4;">
    <div class="v">{m.sesiones_7d}</div>
    <div class="l">Ultimos 7 dias</div>
  </div>
  <div class="kpi" style="border-left-color:{preflight_color};">
    <div class="v">{m.preflight_ratio*100:.0f}%</div>
    <div class="l">Pre-flight Memento</div>
    <div class="bar"><div style="width:{m.preflight_ratio*100:.0f}%; background:{preflight_color};"></div></div>
  </div>
  <div class="kpi" style="border-left-color:{avance_color};">
    <div class="v">{m.avance_ratio*100:.0f}%</div>
    <div class="l">Sesiones con commits</div>
    <div class="bar"><div style="width:{m.avance_ratio*100:.0f}%; background:{avance_color};"></div></div>
  </div>
  <div class="kpi" style="border-left-color:#f59e0b;">
    <div class="v">{m.sesiones_audit_only}</div>
    <div class="l">Sesiones audit-only</div>
  </div>
</div>

{ultima_block}

<div class="card">
  <h2>Palabras clave correctivas de Alfredo (ultimos 7 dias)</h2>
  <table>
    <thead><tr><th>Palabra clave</th><th>Veces</th></tr></thead>
    <tbody>{kw_rows}</tbody>
  </table>
</div>

<div class="card">
  <h2>Ultimas 20 sesiones</h2>
  <table>
    <thead>
      <tr>
        <th>Inicio (UTC)</th><th>Sprint</th><th>Pre-flight</th>
        <th>Commits</th><th>Violaciones</th><th>Min</th>
      </tr>
    </thead>
    <tbody>{sess_rows}</tbody>
  </table>
</div>

<div class="footer">
  Generado: {now_iso} · Fuente: <code>cowork_sesiones</code> (Supabase) ·
  Lookback: {self.lookback_days}d ·
  Refs: M6 de <code>AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md</code>
</div>
</body>
</html>
"""


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generador dashboard sesiones Cowork (T6).")
    parser.add_argument("--output", "-o", help="Path de salida HTML.")
    parser.add_argument("--lookback-days", type=int, default=30)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args(argv)

    output_path = Path(args.output) if args.output else None
    dashboard = CoworkSessionsDashboard(
        output_path=output_path,
        lookback_days=args.lookback_days,
        limit=args.limit,
    )
    path = dashboard.generate()
    print(f"[COWORK_DASHBOARD] generado en {path} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
