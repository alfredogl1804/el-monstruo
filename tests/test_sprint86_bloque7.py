"""
Tests · Sprint 86 Bloque 7 (Dashboard de Salud + E2E del Catastro).

Cobertura:
  · DashboardEngine: summary/timeline/curators con mock DB sintética.
  · Modo degraded: sin db_factory, db falla, sin datos.
  · Cache LRU 60s + invalidate.
  · Auth condicional: dashboard público por defecto, endurecible via env.
  · APIRouter integration: TestClient + 4 endpoints dashboard.
  · HTML render: contenido + identidad de marca.
  · E2E: pipeline (mocks) + recommend + status secuencial.

Disciplinas:
  · NO red ni Supabase real (todo con FakeClient/FakeQuery local).
  · Identidad de marca: errores `catastro_dashboard_*`.
  · Anti-Dory: env vars leídas fresh en cada request.
  · 1 test opt-in marcado para integración real (skip por defecto).

[Hilo Manus Catastro] · Sprint 86 Bloque 7 · 2026-05-04 · v0.86.7
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import pytest

from kernel.catastro import __version__
from kernel.catastro.dashboard import (
    CHART_JS_CDN,
    DEFAULT_TIMELINE_DAYS,
    MAX_TIMELINE_DAYS,
    CatastroDashboardError,
    CatastroDashboardInvalidArgs,
    CuradorsResponse,
    DashboardEngine,
    SummarySnapshot,
    TimelineResponse,
    dashboard_requires_auth,
    render_html_dashboard,
)


# ============================================================================
# Helpers fake DB (espejo del patrón de _smoke_catastro_mcp_sprint86.py)
# ============================================================================


class _FakeQuery:
    """Mini-builder que imita supabase-py: select/eq/gte/lte/order/limit/execute."""

    def __init__(self, table: str, rows: list[dict[str, Any]]):
        self._table = table
        self._rows = list(rows)
        self._filters: list[tuple[str, str, Any]] = []
        self._limit: Optional[int] = None

    def select(self, _fields: str = "*") -> "_FakeQuery":
        return self

    def eq(self, col: str, val: Any) -> "_FakeQuery":
        self._filters.append((col, "eq", val))
        return self

    def gte(self, col: str, val: Any) -> "_FakeQuery":
        self._filters.append((col, "gte", val))
        return self

    def lte(self, col: str, val: Any) -> "_FakeQuery":
        self._filters.append((col, "lte", val))
        return self

    def order(self, _col: str, desc: bool = False) -> "_FakeQuery":
        return self

    def limit(self, n: int) -> "_FakeQuery":
        self._limit = int(n)
        return self

    def _apply_filters(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out = []
        for r in rows:
            ok = True
            for col, op, val in self._filters:
                rv = r.get(col)
                if op == "eq" and rv != val:
                    ok = False
                    break
                if op == "gte" and (rv is None or str(rv) < str(val)):
                    ok = False
                    break
                if op == "lte" and (rv is None or str(rv) > str(val)):
                    ok = False
                    break
            if ok:
                out.append(r)
        return out

    def execute(self) -> Any:
        rows = self._apply_filters(self._rows)
        if self._limit:
            rows = rows[: self._limit]
        class _Res:
            def __init__(self, data):
                self.data = data
        return _Res(rows)


class _FakeClient:
    """Cliente Supabase fake: dict de tabla → rows."""

    def __init__(self, tables: dict[str, list[dict[str, Any]]]):
        self._tables = tables

    def table(self, name: str) -> _FakeQuery:
        return _FakeQuery(name, self._tables.get(name, []))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def synthetic_db() -> _FakeClient:
    """DB sintética con 4 modelos, 3 curadores, 8 eventos en últimos 14 días."""
    now = _now()
    modelos = [
        {
            "id": "claude-opus-4.7",
            "nombre": "Claude Opus 4.7",
            "proveedor": "anthropic",
            "macroarea": "inteligencia",
            "dominios": ["llm_frontier"],
            "estado": "production",
            "ultima_validacion": _iso(now - timedelta(hours=6)),
        },
        {
            "id": "gpt-5.4",
            "nombre": "GPT 5.4",
            "proveedor": "openai",
            "macroarea": "inteligencia",
            "dominios": ["llm_frontier"],
            "estado": "production",
            "ultima_validacion": _iso(now - timedelta(hours=12)),
        },
        {
            "id": "gemini-3.1-pro",
            "nombre": "Gemini 3.1 Pro",
            "proveedor": "google",
            "macroarea": "inteligencia",
            "dominios": ["llm_frontier"],
            "estado": "production",
            "ultima_validacion": _iso(now - timedelta(hours=18)),
        },
        {
            "id": "qwen-3.6-coder",
            "nombre": "Qwen 3.6 Coder",
            "proveedor": "alibaba",
            "macroarea": "inteligencia",
            "dominios": ["coding_llms"],
            "estado": "preview",
            "ultima_validacion": _iso(now - timedelta(days=2)),
        },
    ]
    curadores = [
        {
            "id": "curator-anthropic-opus",
            "proveedor": "anthropic",
            "modelo_llm": "claude-opus-4.7",
            "trust_score": 0.92,
            "trust_delta_7d": 0.02,
            "invocations_total": 412,
            "invocations_7d": 87,
            "last_invocation_at": _iso(now - timedelta(hours=3)),
            "rol": "primary",
            "estado": "active",
        },
        {
            "id": "curator-openai-gpt",
            "proveedor": "openai",
            "modelo_llm": "gpt-5.4",
            "trust_score": 0.88,
            "trust_delta_7d": -0.01,
            "invocations_total": 380,
            "invocations_7d": 75,
            "last_invocation_at": _iso(now - timedelta(hours=8)),
            "rol": "primary",
            "estado": "active",
        },
        {
            "id": "curator-google-gemini",
            "proveedor": "google",
            "modelo_llm": "gemini-3.1-pro",
            "trust_score": 0.85,
            "trust_delta_7d": 0.05,
            "invocations_total": 265,
            "invocations_7d": 60,
            "last_invocation_at": _iso(now - timedelta(hours=5)),
            "rol": "secondary",
            "estado": "active",
        },
    ]
    eventos = [
        # 3 cron_run ok
        {"id": "ev1", "tipo": "cron_run", "estado": "ok", "prioridad": "baja",
         "detectado_en": _iso(now - timedelta(hours=2))},
        {"id": "ev2", "tipo": "cron_run", "estado": "ok", "prioridad": "baja",
         "detectado_en": _iso(now - timedelta(days=1))},
        {"id": "ev3", "tipo": "cron_run", "estado": "ok", "prioridad": "baja",
         "detectado_en": _iso(now - timedelta(days=2))},
        # 1 cron_run fallido (drift)
        {"id": "ev4", "tipo": "cron_run", "estado": "failed", "prioridad": "alta",
         "detectado_en": _iso(now - timedelta(days=3))},
        # 4 nuevos_descubrimientos
        {"id": "ev5", "tipo": "nuevo_descubrimiento", "estado": "ok",
         "prioridad": "media", "detectado_en": _iso(now - timedelta(days=5))},
        {"id": "ev6", "tipo": "nuevo_descubrimiento", "estado": "ok",
         "prioridad": "media", "detectado_en": _iso(now - timedelta(days=7))},
        {"id": "ev7", "tipo": "evento_critico", "estado": "ok",
         "prioridad": "critica", "detectado_en": _iso(now - timedelta(hours=10))},
        {"id": "ev8", "tipo": "validacion", "estado": "ok",
         "prioridad": "baja", "detectado_en": _iso(now - timedelta(days=10))},
    ]
    return _FakeClient({
        "catastro_modelos": modelos,
        "catastro_eventos": eventos,
        "catastro_curadores": curadores,
    })


# ============================================================================
# Versionado y exports
# ============================================================================


def test_versionado_sprint86_bloque7():
    """v0.86.7 firmado tras bump del Bloque 7."""
    assert __version__.startswith("0.86."), f"versión inesperada: {__version__}"
    # No assert hard '0.86.7' — sobrevive bumps menores futuros


def test_dashboard_module_exports():
    """API pública del módulo dashboard."""
    from kernel.catastro import dashboard
    expected = {
        "DashboardEngine", "SummarySnapshot", "TimelineResponse",
        "CuradorsResponse", "FuenteHealth", "CuradorSnapshot",
        "TimelinePoint", "CatastroDashboardError",
        "CatastroDashboardInvalidArgs", "render_html_dashboard",
        "dashboard_requires_auth", "build_default_dashboard_db_factory",
    }
    actual = {n for n in dir(dashboard) if not n.startswith("_")}
    missing = expected - actual
    assert not missing, f"exports faltantes: {missing}"


# ============================================================================
# DashboardEngine — modo degraded
# ============================================================================


def test_engine_summary_degraded_no_db_factory():
    eng = DashboardEngine(db_factory=None)
    s = eng.summary()
    assert s.degraded is True
    assert s.degraded_reason == "no_db_factory_configured"
    assert s.trust_level == "down"
    assert s.modelos_total == 0


def test_engine_timeline_degraded_no_db_factory():
    eng = DashboardEngine(db_factory=None)
    t = eng.timeline(days=7)
    assert t.degraded is True
    assert t.points == []
    assert t.days == 7


def test_engine_curators_degraded_no_db_factory():
    eng = DashboardEngine(db_factory=None)
    c = eng.curators()
    assert c.degraded is True
    assert c.curadores == []


def test_engine_summary_db_explosion():
    """Si el db_factory levanta, debe degradar a supabase_down (NO crashear)."""
    def boom():
        raise RuntimeError("supabase down hard")
    eng = DashboardEngine(db_factory=boom)
    s = eng.summary()
    # db_factory falla en _client_or_none → returns None → no_db_factory
    assert s.degraded is True
    assert s.trust_level == "down"


# ============================================================================
# DashboardEngine — happy path con DB sintética
# ============================================================================


def test_engine_summary_happy_path(synthetic_db: _FakeClient):
    eng = DashboardEngine(db_factory=lambda: synthetic_db)
    s = eng.summary()
    assert s.degraded is False
    assert s.trust_level == "healthy"
    assert s.modelos_total == 4
    assert s.modelos_production == 3  # 3 production, 1 preview
    assert s.dominios_count == 2  # llm_frontier + coding_llms
    assert "inteligencia" in s.macroareas
    assert s.drift_detected >= 1  # ev7 critica + posiblemente ev4 alta
    assert s.last_run_at is not None
    assert len(s.fuentes) >= 1


def test_engine_summary_returns_pydantic_model(synthetic_db: _FakeClient):
    eng = DashboardEngine(db_factory=lambda: synthetic_db)
    s = eng.summary()
    assert isinstance(s, SummarySnapshot)
    # Pydantic dump funciona
    d = s.model_dump()
    assert "trust_level" in d
    assert "modelos_total" in d


def test_engine_timeline_happy_path(synthetic_db: _FakeClient):
    eng = DashboardEngine(db_factory=lambda: synthetic_db)
    t = eng.timeline(days=14)
    assert t.degraded is False
    assert t.days == 14
    assert len(t.points) == 14
    assert t.total_eventos > 0
    assert t.total_runs >= 1
    # avg_failure_rate puede ser None si todos los runs son ok en ese día


def test_engine_timeline_invalid_args():
    eng = DashboardEngine(db_factory=None)
    with pytest.raises(CatastroDashboardInvalidArgs) as exc:
        eng.timeline(days=0)
    assert exc.value.code == "catastro_dashboard_invalid_args"
    with pytest.raises(CatastroDashboardInvalidArgs):
        eng.timeline(days=MAX_TIMELINE_DAYS + 1)


def test_engine_curators_happy_path(synthetic_db: _FakeClient):
    eng = DashboardEngine(db_factory=lambda: synthetic_db)
    c = eng.curators()
    assert c.degraded is False
    assert c.total == 3
    assert c.avg_trust is not None
    assert 0.8 <= c.avg_trust <= 0.95
    # Verificar shape de cada curador
    for cu in c.curadores:
        assert cu.trust_score >= 0.0 and cu.trust_score <= 1.0
        assert cu.id.startswith("curator-")


# ============================================================================
# Cache LRU + invalidate
# ============================================================================


def test_engine_cache_summary_hit(synthetic_db: _FakeClient):
    eng = DashboardEngine(db_factory=lambda: synthetic_db)
    s1 = eng.summary()
    s2 = eng.summary()
    # Mismo objeto cacheado (Pydantic immutable retornado tal cual)
    assert s1 is s2 or s1.queried_at == s2.queried_at


def test_engine_cache_invalidate(synthetic_db: _FakeClient):
    eng = DashboardEngine(db_factory=lambda: synthetic_db)
    eng.summary()
    eng.timeline(days=7)
    eng.curators()
    flushed = eng.invalidate_cache()
    assert flushed == 3


def test_engine_cache_separate_per_method(synthetic_db: _FakeClient):
    """Verificar que cache de timeline NO contamina summary."""
    eng = DashboardEngine(db_factory=lambda: synthetic_db)
    eng.timeline(days=7)
    eng.timeline(days=14)
    # 2 entries de timeline (días distintos), 0 de summary aún
    s = eng.summary()
    assert s.cache_entries == 2  # snapshot del cache ANTES de set


# ============================================================================
# Auth condicional
# ============================================================================


def test_dashboard_requires_auth_default_false(monkeypatch):
    monkeypatch.delenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", raising=False)
    assert dashboard_requires_auth() is False


def test_dashboard_requires_auth_true(monkeypatch):
    monkeypatch.setenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", "true")
    assert dashboard_requires_auth() is True
    monkeypatch.setenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", "yes")
    assert dashboard_requires_auth() is True
    monkeypatch.setenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", "1")
    assert dashboard_requires_auth() is True


def test_dashboard_requires_auth_explicit_false(monkeypatch):
    monkeypatch.setenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", "false")
    assert dashboard_requires_auth() is False
    monkeypatch.setenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", "")
    assert dashboard_requires_auth() is False


# ============================================================================
# HTML render
# ============================================================================


def test_render_html_dashboard_basic():
    html = render_html_dashboard()
    assert isinstance(html, str)
    assert len(html) > 1000
    assert "<!DOCTYPE html>" in html
    assert "El Catastro" in html
    assert "Dashboard de Salud" in html


def test_render_html_dashboard_brand_compliance():
    """Identidad de marca: orange forja + graphite + Chart.js."""
    html = render_html_dashboard()
    assert "#F97316" in html  # orange forja
    assert "#1C1917" in html  # graphite
    assert "#A8A29E" in html  # acero
    assert CHART_JS_CDN in html
    assert "Chart" in html


def test_render_html_dashboard_consumes_three_endpoints():
    html = render_html_dashboard()
    assert "/summary" in html
    assert "/timeline" in html
    assert "/curators" in html


# ============================================================================
# APIRouter integration (TestClient sin Supabase real)
# ============================================================================


def _build_test_app(db_factory):
    """Construye FastAPI con catastro_router montado + engines inyectados."""
    from fastapi import FastAPI
    from kernel.catastro.catastro_routes import router, set_dependencies
    from kernel.catastro.recommendation import RecommendationEngine

    app = FastAPI()
    rec = RecommendationEngine(db_factory=db_factory)
    dash = DashboardEngine(db_factory=db_factory)
    app.state.catastro_engine = rec
    app.state.catastro_dashboard_engine = dash
    set_dependencies(rec, dash)
    app.include_router(router, prefix="/v1/catastro")
    return app


def test_api_dashboard_summary_no_auth(synthetic_db: _FakeClient, monkeypatch):
    """Dashboard summary sin auth (default público)."""
    from fastapi.testclient import TestClient
    monkeypatch.delenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", raising=False)
    client = TestClient(_build_test_app(lambda: synthetic_db))
    r = client.get("/v1/catastro/dashboard/summary")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["trust_level"] == "healthy"
    assert body["modelos_total"] == 4
    assert "macroareas" in body


def test_api_dashboard_summary_auth_required(synthetic_db: _FakeClient, monkeypatch):
    """Si CATASTRO_DASHBOARD_REQUIRE_AUTH=true → 401 sin key."""
    from fastapi.testclient import TestClient
    monkeypatch.setenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", "true")
    monkeypatch.setenv("MONSTRUO_API_KEY", "test-secret-key-001")
    client = TestClient(_build_test_app(lambda: synthetic_db))
    r = client.get("/v1/catastro/dashboard/summary")
    assert r.status_code == 401
    # Con key → 200
    r2 = client.get("/v1/catastro/dashboard/summary",
                    headers={"X-API-Key": "test-secret-key-001"})
    assert r2.status_code == 200


def test_api_dashboard_timeline_with_query(synthetic_db: _FakeClient, monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.delenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", raising=False)
    client = TestClient(_build_test_app(lambda: synthetic_db))
    r = client.get("/v1/catastro/dashboard/timeline?days=7")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["days"] == 7
    assert len(body["points"]) == 7


def test_api_dashboard_timeline_invalid_days(synthetic_db: _FakeClient, monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.delenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", raising=False)
    client = TestClient(_build_test_app(lambda: synthetic_db))
    r = client.get("/v1/catastro/dashboard/timeline?days=0")
    assert r.status_code == 422  # FastAPI Query validation kick in


def test_api_dashboard_curators(synthetic_db: _FakeClient, monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.delenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", raising=False)
    client = TestClient(_build_test_app(lambda: synthetic_db))
    r = client.get("/v1/catastro/dashboard/curators")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 3


def test_api_dashboard_html_render(synthetic_db: _FakeClient, monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.delenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", raising=False)
    client = TestClient(_build_test_app(lambda: synthetic_db))
    r = client.get("/v1/catastro/dashboard/")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    assert "<!DOCTYPE html>" in r.text
    assert "El Catastro" in r.text


def test_api_dashboard_html_auth_required(synthetic_db: _FakeClient, monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.setenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", "true")
    monkeypatch.setenv("MONSTRUO_API_KEY", "test-secret-key-002")
    client = TestClient(_build_test_app(lambda: synthetic_db))
    r = client.get("/v1/catastro/dashboard/")
    assert r.status_code == 401
    r2 = client.get("/v1/catastro/dashboard/",
                    headers={"X-API-Key": "test-secret-key-002"})
    assert r2.status_code == 200


def test_api_dashboard_degraded_when_no_db(monkeypatch):
    """Sin db_factory, los endpoints retornan 200 con degraded=true."""
    from fastapi.testclient import TestClient
    monkeypatch.delenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", raising=False)
    client = TestClient(_build_test_app(db_factory=None))
    r = client.get("/v1/catastro/dashboard/summary")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["degraded"] is True
    assert body["trust_level"] == "down"


# ============================================================================
# E2E: pipeline + recommend + dashboard secuencial
# ============================================================================


def test_e2e_dashboard_after_recommend_calls(synthetic_db: _FakeClient, monkeypatch):
    """E2E: simular recommend + status + dashboard en mismo cliente."""
    from fastapi.testclient import TestClient
    monkeypatch.setenv("MONSTRUO_API_KEY", "test-secret-e2e-001")
    monkeypatch.delenv("CATASTRO_DASHBOARD_REQUIRE_AUTH", raising=False)

    # Construir app — recommend usa catastro_trono_view, no catastro_modelos.
    # Para este E2E mínimo, agregamos al fake la vista trono también.
    tables = synthetic_db._tables
    tables["catastro_trono_view"] = [
        {"id": "claude-opus-4.7", "nombre": "Claude Opus 4.7",
         "proveedor": "anthropic", "macroarea": "inteligencia",
         "dominio": "llm_frontier", "estado": "production",
         "trono_global": 88.5, "trono_low": 82.0, "trono_high": 95.0,
         "rank_dominio": 1, "trono_delta": 2.1},
        {"id": "gpt-5.4", "nombre": "GPT 5.4", "proveedor": "openai",
         "macroarea": "inteligencia", "dominio": "llm_frontier",
         "estado": "production", "trono_global": 86.0, "trono_low": 80.0,
         "trono_high": 92.0, "rank_dominio": 2, "trono_delta": 0.5},
    ]
    client = TestClient(_build_test_app(lambda: synthetic_db))

    # 1. recommend (con auth)
    r1 = client.post("/v1/catastro/recommend",
                     headers={"X-API-Key": "test-secret-e2e-001"},
                     json={"use_case": "razonamiento legal LATAM",
                           "dominios": ["llm_frontier"], "top_n": 2})
    assert r1.status_code == 200, r1.text
    assert len(r1.json()["modelos"]) == 2

    # 2. dashboard summary (sin auth, default público)
    r2 = client.get("/v1/catastro/dashboard/summary")
    assert r2.status_code == 200
    assert r2.json()["trust_level"] == "healthy"

    # 3. dashboard timeline
    r3 = client.get("/v1/catastro/dashboard/timeline?days=14")
    assert r3.status_code == 200
    assert r3.json()["days"] == 14

    # 4. dashboard curators
    r4 = client.get("/v1/catastro/dashboard/curators")
    assert r4.status_code == 200
    assert r4.json()["total"] == 3


# ============================================================================
# Opt-in: integración real contra Supabase production
# ============================================================================


@pytest.mark.skipif(
    os.environ.get("SUPABASE_INTEGRATION_TESTS") != "true",
    reason="opt-in: setear SUPABASE_INTEGRATION_TESTS=true para correr",
)
def test_integration_dashboard_real_supabase():
    """Test opt-in: dashboard contra Supabase production (requiere envs)."""
    from kernel.catastro.dashboard import build_default_dashboard_db_factory
    factory = build_default_dashboard_db_factory()
    eng = DashboardEngine(db_factory=factory)
    s = eng.summary()
    # No assert hard sobre trust_level — depende del estado real
    assert isinstance(s, SummarySnapshot)
    print(f"\n[REAL] trust={s.trust_level} modelos={s.modelos_total} "
          f"dominios={s.dominios_count} drift={s.drift_detected}")
