"""
El Catastro · Dashboard de Salud (Sprint 86 Bloque 7).

Capa de visibilidad operativa del Catastro. Provee 3 endpoints JSON
+ 1 render HTML vanilla con Chart.js para que Alfredo y Cowork puedan
inspeccionar el estado del sistema sin SQL ni MCP cliente.

Endpoints (registrados por catastro_routes.py bajo /v1/catastro/dashboard/*):
  · GET /summary    → Health snapshot + métricas operativas + last_run
  · GET /timeline   → Histórico últimos N runs + failure_rate
  · GET /curators   → Trust scores + trend de los curadores
  · GET /           → HTML render que consume los 3 JSON via fetch+Chart.js

Doctrina (Cowork green light Bloque 7):
  · Auth: público read-only POR DEFECTO. Endurecible vía
    `CATASTRO_DASHBOARD_REQUIRE_AUTH=true` (lectura fresh, anti-Dory).
  · Cache LRU 60s (mismo TTL que recommendation; cache PROPIO para no
    contaminar el de recommend).
  · Modo degraded: si Supabase falla, devolvemos JSON con
    `degraded=true, reason=...` y datos vacíos — NUNCA crashea.
  · HTML render vanilla — sin React/Vue. Chart.js via CDN. Mobile-friendly.
  · Identidad de marca: errores `catastro_dashboard_*`, naming
    `summary/timeline/curators` (no genéricos).

Disciplina anti-Dory:
  · `os.environ.get(...)` en cada uso (no se cachea al boot).
  · `db_factory` inyectable para tests con mock.
  · Cache invalidable explícitamente vía `invalidate_cache()`.
  · Reusa `RecommendationEngine.status()` para no duplicar lógica de salud.

[Hilo Manus Catastro] · Sprint 86 Bloque 7 · 2026-05-04 · v0.86.7
"""
from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Constantes
# ============================================================================

CATASTRO_MODELOS_TABLE = "catastro_modelos"
CATASTRO_EVENTOS_TABLE = "catastro_eventos"
CATASTRO_CURADORES_TABLE = "catastro_curadores"
CATASTRO_HISTORIAL_TABLE = "catastro_historial"

DEFAULT_TIMELINE_DAYS = 14
MAX_TIMELINE_DAYS = 90

DEFAULT_DASHBOARD_CACHE_TTL = 60
DEFAULT_DASHBOARD_CACHE_MAX = 64

DEGRADED_REASON_NO_DB = "no_db_factory_configured"
DEGRADED_REASON_SUPABASE_DOWN = "supabase_down"
DEGRADED_REASON_NO_DATA = "no_data_available"

CHART_JS_CDN = "https://cdn.jsdelivr.net/npm/chart.js@4.4.6/dist/chart.umd.min.js"


# ============================================================================
# Errores con identidad de marca
# ============================================================================


class CatastroDashboardError(Exception):
    """Error base del dashboard. Identidad: catastro_dashboard_*."""

    code: str = "catastro_dashboard_error"

    def __init__(self, message: str, **context: Any) -> None:
        super().__init__(message)
        self.context = context


class CatastroDashboardInvalidArgs(CatastroDashboardError):
    """Argumentos de entrada inválidos (days fuera de rango, etc.)."""

    code = "catastro_dashboard_invalid_args"


# ============================================================================
# Pydantic models — JSON-serializable directo
# ============================================================================


class FuenteHealth(BaseModel):
    """Estado de una fuente del Catastro."""

    nombre: str
    estado: str = Field(..., description='"ok" | "error" | "unknown"')
    last_seen: Optional[datetime] = None


class SummarySnapshot(BaseModel):
    """Snapshot resumido del dashboard /summary."""

    model_config = ConfigDict(extra="ignore")

    trust_level: str = Field(..., description='"healthy" | "degraded" | "down"')
    modelos_total: int = 0
    modelos_production: int = 0
    dominios_count: int = 0
    macroareas: list[str] = Field(default_factory=list)
    last_run_at: Optional[datetime] = None
    last_run_status: Optional[str] = None  # "ok" | "degraded" | "failed"
    fuentes: list[FuenteHealth] = Field(default_factory=list)
    drift_detected: int = 0  # eventos en últimas 24h con prioridad alta
    cache_entries: int = 0
    degraded: bool = False
    degraded_reason: Optional[str] = None
    queried_at: datetime


class TimelinePoint(BaseModel):
    """Un día en el timeline del Catastro."""

    fecha: str  # YYYY-MM-DD
    runs: int = 0
    eventos: int = 0
    drift_alto: int = 0  # eventos con prioridad alta/critica
    failure_rate: Optional[float] = None  # 0.0-1.0


class TimelineResponse(BaseModel):
    """Respuesta de /dashboard/timeline."""

    days: int
    points: list[TimelinePoint]
    total_runs: int = 0
    total_eventos: int = 0
    avg_failure_rate: Optional[float] = None
    degraded: bool = False
    degraded_reason: Optional[str] = None
    queried_at: datetime


class CuradorSnapshot(BaseModel):
    """Trust score + tendencia de un curador."""

    id: str
    proveedor: str
    modelo_llm: str
    trust_score: float = Field(..., description="Trust score actual [0,1]")
    trust_delta_7d: Optional[float] = None  # cambio últimos 7 días
    invocations_total: int = 0
    invocations_7d: int = 0
    last_invocation_at: Optional[datetime] = None
    rol: Optional[str] = None
    estado: str = Field(default="active")


class CuradorsResponse(BaseModel):
    """Respuesta de /dashboard/curators."""

    curadores: list[CuradorSnapshot]
    total: int = 0
    avg_trust: Optional[float] = None
    degraded: bool = False
    degraded_reason: Optional[str] = None
    queried_at: datetime


# ============================================================================
# Cache LRU con TTL — copia minimal del patrón de recommendation.py
# ============================================================================


@dataclass
class _CacheEntry:
    value: Any
    expires_at: float


class _LRUTTLCache:
    """Cache LRU con TTL absoluto. Thread-safe básico (RLock).

    Copia minimal del patrón de recommendation.py para mantener
    independencia (no contaminar el cache del recommend).
    """

    def __init__(self, max_entries: int, ttl_seconds: int) -> None:
        self._max = int(max_entries)
        self._ttl = int(ttl_seconds)
        self._lock = threading.RLock()
        self._store: dict[Any, _CacheEntry] = {}

    def get(self, key: Any) -> Optional[Any]:
        now = time.time()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.expires_at < now:
                self._store.pop(key, None)
                return None
            self._store.pop(key)
            self._store[key] = entry
            return entry.value

    def set(self, key: Any, value: Any) -> None:
        with self._lock:
            if key in self._store:
                self._store.pop(key)
            self._store[key] = _CacheEntry(
                value=value,
                expires_at=time.time() + self._ttl,
            )
            while len(self._store) > self._max:
                oldest_key = next(iter(self._store))
                self._store.pop(oldest_key)

    def invalidate(self) -> int:
        with self._lock:
            n = len(self._store)
            self._store.clear()
            return n

    def size(self) -> int:
        with self._lock:
            return len(self._store)


# ============================================================================
# DashboardEngine
# ============================================================================


class DashboardEngine:
    """
    Motor de visibilidad operativa del Catastro. Sin acoplamiento a
    FastAPI; consumible por tests, scripts, y el HTML render.

    Args:
        db_factory: callable que retorna un cliente Supabase SÍNCRONO.
            Si es None, todos los métodos retornan modo degraded.
        cache_ttl_seconds: TTL del cache LRU en segundos (default 60).
        cache_max_entries: tamaño máximo del cache (default 64).

    Patrones de uso:
        engine = DashboardEngine(db_factory=lambda: supabase_client())
        snapshot = engine.summary()
        timeline = engine.timeline(days=14)
        curators = engine.curators()
    """

    def __init__(
        self,
        db_factory: Optional[Callable[[], Any]] = None,
        *,
        cache_ttl_seconds: int = DEFAULT_DASHBOARD_CACHE_TTL,
        cache_max_entries: int = DEFAULT_DASHBOARD_CACHE_MAX,
    ) -> None:
        self.db_factory = db_factory
        self._cache = _LRUTTLCache(cache_max_entries, cache_ttl_seconds)

    # ------------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------------

    def summary(self) -> SummarySnapshot:
        """Snapshot resumido: salud + conteos + last_run + fuentes + drift."""
        cache_key = ("summary",)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        now = datetime.now(timezone.utc)
        client = self._client_or_none()
        if client is None:
            return SummarySnapshot(
                trust_level="down",
                degraded=True,
                degraded_reason=DEGRADED_REASON_NO_DB,
                queried_at=now,
            )

        try:
            modelos_rows = self._safe_select(
                client,
                CATASTRO_MODELOS_TABLE,
                fields="id,macroarea,dominios,estado,ultima_validacion",
            )
        except Exception:
            return SummarySnapshot(
                trust_level="down",
                degraded=True,
                degraded_reason=DEGRADED_REASON_SUPABASE_DOWN,
                queried_at=now,
            )

        # Drift = eventos críticos/altos últimas 24h
        drift_count = 0
        last_run_at: Optional[datetime] = None
        last_run_status: Optional[str] = None
        try:
            since = (now - timedelta(hours=24)).isoformat()
            ev_rows = self._safe_select(
                client,
                CATASTRO_EVENTOS_TABLE,
                fields="id,prioridad,detectado_en,tipo,estado",
                filters=[("detectado_en", "gte", since)],
                limit=200,
            )
            for ev in ev_rows or []:
                if str(ev.get("prioridad", "")).lower() in ("alta", "critica"):
                    drift_count += 1
                # last_run = evento más reciente del cron
                if ev.get("tipo") in ("pipeline_run", "cron_run"):
                    dt = _parse_dt(ev.get("detectado_en"))
                    if dt and (last_run_at is None or dt > last_run_at):
                        last_run_at = dt
                        last_run_status = str(ev.get("estado") or "ok")
        except Exception:
            pass  # drift es nice-to-have, no bloqueante

        modelos_total = len(modelos_rows or [])
        modelos_prod = sum(1 for r in (modelos_rows or [])
                           if str(r.get("estado", "")).lower() == "production")
        # `dominios` es text[] en la tabla — expandir todos los dominios de cada modelo
        dominios = set()
        for r in (modelos_rows or []):
            for d in (r.get("dominios") or []):
                if d:
                    dominios.add(d)
        macroareas = sorted({r.get("macroarea") for r in (modelos_rows or [])
                             if r.get("macroarea")})

        # ultima_validacion fallback si no hay eventos cron
        if last_run_at is None and modelos_rows:
            for r in modelos_rows:
                dt = _parse_dt(r.get("ultima_validacion") or r.get("last_validated_at"))
                if dt and (last_run_at is None or dt > last_run_at):
                    last_run_at = dt

        fuentes = self._infer_fuentes_health(modelos_rows or [])

        if not modelos_rows:
            trust = "degraded"
        elif modelos_prod == 0:
            trust = "degraded"
        else:
            trust = "healthy"

        snapshot = SummarySnapshot(
            trust_level=trust,
            modelos_total=modelos_total,
            modelos_production=modelos_prod,
            dominios_count=len(dominios),
            macroareas=macroareas,
            last_run_at=last_run_at,
            last_run_status=last_run_status,
            fuentes=fuentes,
            drift_detected=drift_count,
            cache_entries=self._cache.size(),
            degraded=not bool(modelos_rows),
            degraded_reason=None if modelos_rows else DEGRADED_REASON_NO_DATA,
            queried_at=now,
        )
        self._cache.set(cache_key, snapshot)
        return snapshot

    def timeline(self, *, days: int = DEFAULT_TIMELINE_DAYS) -> TimelineResponse:
        """Histórico de últimos N días: runs, eventos, drift, failure_rate."""
        if days < 1 or days > MAX_TIMELINE_DAYS:
            raise CatastroDashboardInvalidArgs(
                f"days fuera de rango [1, {MAX_TIMELINE_DAYS}]",
                given=days,
            )

        cache_key = ("timeline", int(days))
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        now = datetime.now(timezone.utc)
        client = self._client_or_none()
        if client is None:
            return TimelineResponse(
                days=days,
                points=[],
                degraded=True,
                degraded_reason=DEGRADED_REASON_NO_DB,
                queried_at=now,
            )

        try:
            since = (now - timedelta(days=days)).isoformat()
            ev_rows = self._safe_select(
                client,
                CATASTRO_EVENTOS_TABLE,
                fields="id,prioridad,detectado_en,tipo,estado,confianza_estimada",
                filters=[("detectado_en", "gte", since)],
                limit=5000,
            )
        except Exception:
            return TimelineResponse(
                days=days,
                points=[],
                degraded=True,
                degraded_reason=DEGRADED_REASON_SUPABASE_DOWN,
                queried_at=now,
            )

        # Bucketizar por día
        buckets: dict[str, dict[str, Any]] = {}
        for i in range(days):
            d = (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            buckets[d] = {"runs": 0, "eventos": 0, "drift_alto": 0,
                          "failures": 0, "totals": 0}

        for ev in ev_rows or []:
            dt = _parse_dt(ev.get("detectado_en"))
            if dt is None:
                continue
            d = dt.strftime("%Y-%m-%d")
            if d not in buckets:
                continue  # fuera de rango (paranoia)
            buckets[d]["eventos"] += 1
            if ev.get("tipo") in ("pipeline_run", "cron_run"):
                buckets[d]["runs"] += 1
                buckets[d]["totals"] += 1
                if str(ev.get("estado", "")).lower() in ("failed", "error"):
                    buckets[d]["failures"] += 1
            if str(ev.get("prioridad", "")).lower() in ("alta", "critica"):
                buckets[d]["drift_alto"] += 1

        points: list[TimelinePoint] = []
        total_runs = 0
        total_eventos = 0
        all_rates: list[float] = []
        for fecha, b in buckets.items():
            fr: Optional[float] = None
            if b["totals"] > 0:
                fr = round(b["failures"] / b["totals"], 3)
                all_rates.append(fr)
            points.append(TimelinePoint(
                fecha=fecha,
                runs=b["runs"],
                eventos=b["eventos"],
                drift_alto=b["drift_alto"],
                failure_rate=fr,
            ))
            total_runs += b["runs"]
            total_eventos += b["eventos"]

        avg_fr = round(sum(all_rates) / len(all_rates), 3) if all_rates else None

        resp = TimelineResponse(
            days=days,
            points=points,
            total_runs=total_runs,
            total_eventos=total_eventos,
            avg_failure_rate=avg_fr,
            degraded=False,
            queried_at=now,
        )
        self._cache.set(cache_key, resp)
        return resp

    def curators(self) -> CuradorsResponse:
        """Trust scores + tendencia de los curadores del Catastro."""
        cache_key = ("curators",)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        now = datetime.now(timezone.utc)
        client = self._client_or_none()
        if client is None:
            return CuradorsResponse(
                curadores=[],
                degraded=True,
                degraded_reason=DEGRADED_REASON_NO_DB,
                queried_at=now,
            )

        try:
            cur_rows = self._safe_select(
                client,
                CATASTRO_CURADORES_TABLE,
                fields=("id,proveedor,modelo_llm,trust_score,invocations_total,"
                        "last_invocation_at,rol,estado,trust_delta_7d,invocations_7d"),
                limit=200,
            )
        except Exception:
            return CuradorsResponse(
                curadores=[],
                degraded=True,
                degraded_reason=DEGRADED_REASON_SUPABASE_DOWN,
                queried_at=now,
            )

        out: list[CuradorSnapshot] = []
        all_trust: list[float] = []
        for r in cur_rows or []:
            try:
                trust = float(r.get("trust_score") or 0.0)
                snap = CuradorSnapshot(
                    id=str(r["id"]),
                    proveedor=str(r.get("proveedor") or "unknown"),
                    modelo_llm=str(r.get("modelo_llm") or "unknown"),
                    trust_score=trust,
                    trust_delta_7d=r.get("trust_delta_7d"),
                    invocations_total=int(r.get("invocations_total") or 0),
                    invocations_7d=int(r.get("invocations_7d") or 0),
                    last_invocation_at=_parse_dt(r.get("last_invocation_at")),
                    rol=r.get("rol"),
                    estado=str(r.get("estado") or "active"),
                )
                out.append(snap)
                all_trust.append(trust)
            except Exception:
                continue  # fila corrupta, skip

        avg = round(sum(all_trust) / len(all_trust), 3) if all_trust else None

        resp = CuradorsResponse(
            curadores=out,
            total=len(out),
            avg_trust=avg,
            degraded=not bool(out),
            degraded_reason=None if out else DEGRADED_REASON_NO_DATA,
            queried_at=now,
        )
        self._cache.set(cache_key, resp)
        return resp

    def invalidate_cache(self) -> int:
        """Vacía el cache LRU. Retorna el número de entries flusheados."""
        return self._cache.invalidate()

    # ------------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------------

    def _client_or_none(self) -> Optional[Any]:
        if self.db_factory is None:
            return None
        try:
            return self.db_factory()
        except Exception:
            return None

    def _safe_select(
        self,
        client: Any,
        table: str,
        *,
        fields: str = "*",
        filters: Optional[list[tuple[str, str, Any]]] = None,
        limit: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """Helper: select con filtros opcionales. Retorna lista o levanta."""
        q = client.table(table).select(fields)
        for col, op, val in filters or []:
            method = getattr(q, op, None)
            if method is None:
                continue
            q = method(col, val)
        if limit:
            q = q.limit(int(limit))
        res = q.execute()
        return getattr(res, "data", None) or []

    def _infer_fuentes_health(
        self,
        modelos_rows: list[dict[str, Any]],
    ) -> list[FuenteHealth]:
        """Heurística: inferir health de fuentes desde last_validated_at por modelo.

        Si la mayoría de modelos tienen ultima_validacion < 7 días → ok,
        si > 30 días → error, si entre medio → unknown.
        """
        now = datetime.now(timezone.utc)
        if not modelos_rows:
            return []

        last_dt: Optional[datetime] = None
        for r in modelos_rows:
            dt = _parse_dt(r.get("last_validated_at"))
            if dt and (last_dt is None or dt > last_dt):
                last_dt = dt

        if last_dt is None:
            estado = "unknown"
        else:
            age = (now - last_dt).days
            if age <= 7:
                estado = "ok"
            elif age <= 30:
                estado = "unknown"
            else:
                estado = "error"

        # MVP: solo agrega un health agregado — fuentes individuales se
        # pueden discriminar cuando se agregue catastro_runs (siguiente
        # bloque o sprint 86.5).
        return [FuenteHealth(
            nombre="agregado",
            estado=estado,
            last_seen=last_dt,
        )]


# ============================================================================
# Helpers
# ============================================================================


def _parse_dt(value: Any) -> Optional[datetime]:
    """Parser tolerante (copia del helper de recommendation.py)."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            v = value.replace("Z", "+00:00") if value.endswith("Z") else value
            return datetime.fromisoformat(v)
        except Exception:
            return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except Exception:
            return None
    return None


# ============================================================================
# HTML render — vanilla + Chart.js CDN
# ============================================================================


def render_html_dashboard() -> str:
    """
    Devuelve el HTML del dashboard. Consume los 3 endpoints JSON via fetch.

    Diseño deliberado:
      · Sin frontend framework (Cowork: no React/Vue para v1.0).
      · Chart.js CDN (4.4.6) para gráficos.
      · CSS inline minimal, mobile-friendly.
      · Identidad de marca: #F97316 (orange forja), #1C1917 (graphite),
        #A8A29E (acero). Brutalismo industrial refinado (AGENTS.md #4).
      · Auth header opcional via prompt; respeta CATASTRO_DASHBOARD_REQUIRE_AUTH.
    """
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>El Catastro · Dashboard de Salud</title>
<script src="{CHART_JS_CDN}"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, "SF Pro Text", "Inter", system-ui, sans-serif;
    background: #1C1917;
    color: #FAFAF9;
    padding: 24px 16px;
    line-height: 1.5;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  header {{ border-bottom: 2px solid #F97316; padding-bottom: 16px; margin-bottom: 24px; }}
  h1 {{ font-size: 28px; font-weight: 800; letter-spacing: -0.02em; }}
  h1 small {{ font-weight: 400; color: #A8A29E; font-size: 14px; margin-left: 8px; }}
  h2 {{ font-size: 18px; margin: 24px 0 12px; color: #F97316; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
  }}
  .card {{
    background: #292524;
    border: 1px solid #44403C;
    padding: 16px;
    border-radius: 4px;
  }}
  .card .label {{ color: #A8A29E; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .card .value {{ font-size: 28px; font-weight: 700; margin-top: 4px; }}
  .badge {{
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 12px; font-weight: 600;
  }}
  .badge-healthy {{ background: #16A34A; color: white; }}
  .badge-degraded {{ background: #F97316; color: white; }}
  .badge-down {{ background: #DC2626; color: white; }}
  .chart-container {{ background: #292524; padding: 16px; border-radius: 4px; height: 300px; position: relative; }}
  table {{ width: 100%; border-collapse: collapse; background: #292524; border-radius: 4px; overflow: hidden; }}
  th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #44403C; font-size: 14px; }}
  th {{ background: #1C1917; color: #F97316; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.05em; }}
  .error {{ color: #DC2626; padding: 12px; background: #1C1917; border-left: 3px solid #DC2626; border-radius: 2px; }}
  .auth-note {{ color: #A8A29E; font-size: 12px; margin-top: 12px; }}
  footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid #44403C; color: #A8A29E; font-size: 12px; }}
  code {{ background: #1C1917; padding: 1px 6px; border-radius: 2px; font-family: "SF Mono", "Menlo", monospace; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>El Catastro <small>Dashboard de Salud · Sprint 86 Bloque 7</small></h1>
  </header>

  <div id="status-section">
    <h2>Estado General</h2>
    <div class="grid" id="summary-cards">
      <div class="card"><div class="label">Cargando…</div></div>
    </div>
  </div>

  <h2>Timeline (últimos 14 días)</h2>
  <div class="chart-container">
    <canvas id="timeline-chart"></canvas>
  </div>

  <h2>Curadores · Trust Scores</h2>
  <div id="curators-section">
    <table id="curators-table">
      <thead><tr>
        <th>Curador</th><th>Proveedor</th><th>Trust</th><th>Δ 7d</th>
        <th>Invocaciones</th><th>Última</th><th>Estado</th>
      </tr></thead>
      <tbody><tr><td colspan="7">Cargando…</td></tr></tbody>
    </table>
  </div>

  <footer>
    <div>Dashboard <code>/v1/catastro/dashboard/</code> · Endpoints JSON: <code>summary</code>, <code>timeline</code>, <code>curators</code>.</div>
    <div class="auth-note">Si el dashboard requiere auth, será solicitada al cargar (X-API-Key).</div>
  </footer>
</div>

<script>
const API_BASE = window.location.pathname.replace(/\\/$/, "");
let API_KEY = "";

async function fetchJson(path) {{
  const headers = {{}};
  if (API_KEY) headers["X-API-Key"] = API_KEY;
  const res = await fetch(API_BASE + path, {{ headers }});
  if (res.status === 401 || res.status === 503) {{
    if (!API_KEY) {{
      API_KEY = prompt("MONSTRUO_API_KEY (auth requerida):") || "";
      if (API_KEY) return fetchJson(path);
    }}
    throw new Error("auth_required");
  }}
  if (!res.ok) throw new Error("http_" + res.status);
  return res.json();
}}

function renderError(containerId, msg) {{
  document.getElementById(containerId).innerHTML =
    '<div class="error">Error: ' + msg + '</div>';
}}

function badgeFor(level) {{
  return '<span class="badge badge-' + level + '">' + level + '</span>';
}}

async function loadSummary() {{
  try {{
    const s = await fetchJson("/summary");
    const cards = [
      {{ label: "Trust Level", value: badgeFor(s.trust_level) }},
      {{ label: "Modelos Total", value: s.modelos_total }},
      {{ label: "Modelos Production", value: s.modelos_production }},
      {{ label: "Dominios", value: s.dominios_count }},
      {{ label: "Drift 24h", value: s.drift_detected }},
      {{ label: "Last Run", value: s.last_run_at ? new Date(s.last_run_at).toLocaleString() : "—" }},
    ];
    if (s.degraded) cards.push({{ label: "Degraded", value: s.degraded_reason || "yes" }});
    document.getElementById("summary-cards").innerHTML = cards.map(c =>
      '<div class="card"><div class="label">' + c.label + '</div>' +
      '<div class="value">' + c.value + '</div></div>'
    ).join("");
  }} catch (e) {{
    renderError("summary-cards", e.message);
  }}
}}

async function loadTimeline() {{
  try {{
    const t = await fetchJson("/timeline?days=14");
    const ctx = document.getElementById("timeline-chart").getContext("2d");
    new Chart(ctx, {{
      type: "bar",
      data: {{
        labels: t.points.map(p => p.fecha),
        datasets: [
          {{ label: "Runs", data: t.points.map(p => p.runs), backgroundColor: "#F97316" }},
          {{ label: "Eventos", data: t.points.map(p => p.eventos), backgroundColor: "#A8A29E" }},
          {{ label: "Drift Alto", data: t.points.map(p => p.drift_alto), backgroundColor: "#DC2626" }},
        ]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        scales: {{
          x: {{ ticks: {{ color: "#A8A29E" }}, grid: {{ color: "#44403C" }} }},
          y: {{ ticks: {{ color: "#A8A29E" }}, grid: {{ color: "#44403C" }}, beginAtZero: true }}
        }},
        plugins: {{ legend: {{ labels: {{ color: "#FAFAF9" }} }} }}
      }}
    }});
  }} catch (e) {{
    document.querySelector(".chart-container").innerHTML =
      '<div class="error">Error timeline: ' + e.message + '</div>';
  }}
}}

async function loadCurators() {{
  try {{
    const c = await fetchJson("/curators");
    if (!c.curadores.length) {{
      document.querySelector("#curators-table tbody").innerHTML =
        '<tr><td colspan="7" class="auth-note">Sin curadores registrados aún.</td></tr>';
      return;
    }}
    document.querySelector("#curators-table tbody").innerHTML = c.curadores.map(cu => {{
      const delta = cu.trust_delta_7d == null ? "—" :
        (cu.trust_delta_7d >= 0 ? "+" : "") + cu.trust_delta_7d.toFixed(2);
      const last = cu.last_invocation_at ? new Date(cu.last_invocation_at).toLocaleDateString() : "—";
      return '<tr>' +
        '<td>' + cu.id + '</td>' +
        '<td>' + cu.proveedor + '</td>' +
        '<td>' + cu.trust_score.toFixed(2) + '</td>' +
        '<td>' + delta + '</td>' +
        '<td>' + cu.invocations_total + ' (' + cu.invocations_7d + ' / 7d)</td>' +
        '<td>' + last + '</td>' +
        '<td>' + badgeFor(cu.estado === "active" ? "healthy" : "degraded") + '</td>' +
        '</tr>';
    }}).join("");
  }} catch (e) {{
    renderError("curators-section", e.message);
  }}
}}

loadSummary();
loadTimeline();
loadCurators();
</script>
</body>
</html>
"""


# ============================================================================
# Auth helper para dashboard (público O X-API-Key según env var)
# ============================================================================


def dashboard_requires_auth() -> bool:
    """Lee FRESH (anti-Dory) si el dashboard exige auth."""
    val = os.environ.get("CATASTRO_DASHBOARD_REQUIRE_AUTH", "").strip().lower()
    return val in ("true", "1", "yes", "y")


def build_default_dashboard_db_factory() -> Optional[Callable[[], Any]]:
    """Construye db_factory para el dashboard (espejo de recommendation)."""
    def _factory() -> Any:
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        if not url or not key:
            raise CatastroDashboardError(
                "supabase env vars no configuradas",
                missing_url=not bool(url),
                missing_key=not bool(key),
            )
        try:
            from supabase import create_client
        except ImportError as exc:
            raise CatastroDashboardError(
                "supabase package no instalado",
                hint="pip install supabase",
            ) from exc
        return create_client(url, key)

    return _factory
