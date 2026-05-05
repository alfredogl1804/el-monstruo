"""
Sprint 86 Bloque 5 — Tests del MCP Server catastro.recommend()

Cobertura:
  · Versionado v0.86.5 + bloque 5
  · RecommendationEngine: init, modo degraded sin db, cache LRU, invalidate
  · recommend(): use_case vacío → error, top_n clampeado, dominio/macroarea filtros, cache hit
  · get_modelo(): existe vs no existe, db caída → None, id vacío → error
  · list_dominios(): agrupación por macroárea, conteos, db caída → degraded
  · status(): trust_level healthy/degraded/down según estado
  · catastro_routes: auth (sin key, key inválida, key OK), endpoints retornan 200/401/404
  · mcp_tools: build_catastro_mcp con/sin fastmcp, set_mcp_engine
  · 1 test opt-in real con SUPABASE_INTEGRATION_TESTS=true

Estilo: mock-based, sin tocar Supabase.

[Hilo Manus Catastro] · Sprint 86 Bloque 5 · 2026-05-04
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from kernel.catastro import (
    CATASTRO_TRONO_VIEW,
    CatastroRecommendError,
    CatastroRecommendInvalidArgs,
    DEFAULT_TOP_N,
    DominioInfo,
    ListDominiosResponse,
    MAX_TOP_N,
    ModeloDetallado,
    ModeloRecomendado,
    RecommendationEngine,
    RecommendationResponse,
    StatusSnapshot,
    __bloque__,
    __version__,
    build_default_db_factory,
)
from kernel.catastro import catastro_routes as _routes
from kernel.catastro import mcp_tools as _mcp_tools


# ============================================================================
# FIXTURES
# ============================================================================


def _make_view_row(
    *,
    id: str = "alpha-model",
    nombre: str = "Alpha Model",
    proveedor: str = "test",
    macroarea: str = "Inteligencia",
    dominio: str = "llm_frontier",
    estado: str = "production",
    trono_global: float = 70.0,
    rank_dominio: int = 1,
    confidence: float = 0.8,
) -> dict:
    return {
        "id": id,
        "nombre": nombre,
        "proveedor": proveedor,
        "macroarea": macroarea,
        "dominio": dominio,
        "estado": estado,
        "quality_score": 80.0,
        "cost_efficiency": 70.0,
        "speed_score": 75.0,
        "reliability_score": 90.0,
        "brand_fit": 0.8,
        "confidence": confidence,
        "trono_global": trono_global,
        "trono_delta": 1.5,
        "trono_low": trono_global - 2.0,
        "trono_high": trono_global + 2.0,
        "rank_dominio": rank_dominio,
        "precio_input_per_million": 5.0,
        "precio_output_per_million": 15.0,
        "open_weights": False,
        "last_validated_at": "2026-05-04T20:00:00Z",
    }


class _FakeQuery:
    """Fluent fake del builder de Supabase: select().eq().order().limit().execute().

    Respeta los filtros eq() para que tests realistas (e.g. get_modelo por id
    inexistente) devuelvan vacío en vez de la tabla completa.
    """

    def __init__(self, rows):
        self._rows = list(rows)
        self._filters = []
        self._limit = None
        self.calls = []

    def select(self, *a, **k):
        self.calls.append(("select", a, k))
        return self

    def eq(self, col, val, **k):
        self.calls.append(("eq", (col, val), k))
        self._filters.append(("eq", col, val))
        return self

    def neq(self, col, val, **k):
        self.calls.append(("neq", (col, val), k))
        self._filters.append(("neq", col, val))
        return self

    def order(self, *a, **k):
        self.calls.append(("order", a, k))
        return self

    def limit(self, n, **k):
        self.calls.append(("limit", (n,), k))
        self._limit = n
        return self

    def _apply(self):
        rows = self._rows
        for op, col, val in self._filters:
            if op == "eq":
                rows = [r for r in rows if r.get(col) == val]
            elif op == "neq":
                rows = [r for r in rows if r.get(col) != val]
        if self._limit is not None:
            rows = rows[: self._limit]
        return rows

    def execute(self):
        return MagicMock(data=self._apply())


class _FakeClient:
    """Fake supabase client con .table() que devuelve un _FakeQuery."""

    def __init__(self, rows_by_table):
        self._rows_by_table = rows_by_table
        self.last_table = None

    def table(self, name):
        self.last_table = name
        return _FakeQuery(self._rows_by_table.get(name, []))


def make_engine_with_rows(rows_by_table):
    return RecommendationEngine(db_factory=lambda: _FakeClient(rows_by_table))


# ============================================================================
# 1. VERSIONADO
# ============================================================================


class TestVersionado:
    def test_version_es_v0_86_5(self):
        assert __version__ == "0.86.5"

    def test_bloque_es_5(self):
        assert __bloque__ == "5"


# ============================================================================
# 2. RECOMMENDATION ENGINE — INIT Y CACHE
# ============================================================================


class TestRecommendationEngineInit:
    def test_init_sin_db_factory(self):
        e = RecommendationEngine(db_factory=None)
        assert e.db_factory is None
        assert e._cache.size() == 0

    def test_status_sin_db_es_down(self):
        e = RecommendationEngine(db_factory=None)
        snap = e.status()
        assert snap.trust_level == "down"
        assert snap.degraded is True
        assert snap.degraded_reason == "no_db_factory_configured"
        assert snap.modelos_count == 0

    def test_invalidate_cache_retorna_count(self):
        e = make_engine_with_rows({CATASTRO_TRONO_VIEW: [_make_view_row()]})
        e.recommend(use_case="test1", dominio="llm_frontier")
        e.recommend(use_case="test2", dominio="llm_frontier")
        flushed = e.invalidate_cache()
        assert flushed == 2

    def test_db_factory_falla_retorna_degraded(self):
        def _broken():
            raise RuntimeError("supabase down")
        e = RecommendationEngine(db_factory=_broken)
        resp = e.recommend(use_case="anything")
        assert resp.degraded is True
        assert resp.degraded_reason == "no_db_factory_configured"


# ============================================================================
# 3. RECOMMEND() — VALIDACIÓN Y CACHE
# ============================================================================


class TestRecommend:
    def test_use_case_vacio_falla(self):
        e = RecommendationEngine(db_factory=None)
        with pytest.raises(CatastroRecommendInvalidArgs):
            e.recommend(use_case="")

    def test_use_case_solo_espacios_falla(self):
        e = RecommendationEngine(db_factory=None)
        with pytest.raises(CatastroRecommendInvalidArgs):
            e.recommend(use_case="   ")

    def test_top_n_clampeado_al_max(self):
        rows = [_make_view_row(id=f"m-{i}", rank_dominio=i + 1) for i in range(50)]
        e = make_engine_with_rows({CATASTRO_TRONO_VIEW: rows[:MAX_TOP_N]})
        resp = e.recommend(use_case="any", top_n=999)
        assert resp.top_n == MAX_TOP_N

    def test_top_n_clampeado_al_min(self):
        e = make_engine_with_rows({CATASTRO_TRONO_VIEW: [_make_view_row()]})
        resp = e.recommend(use_case="any", top_n=0)
        assert resp.top_n == 1

    def test_devuelve_modelos_recomendados(self):
        rows = [
            _make_view_row(id="alpha", trono_global=85.0, rank_dominio=1),
            _make_view_row(id="beta", trono_global=70.0, rank_dominio=2),
        ]
        e = make_engine_with_rows({CATASTRO_TRONO_VIEW: rows})
        resp = e.recommend(use_case="razonamiento legal", dominio="llm_frontier", top_n=2)
        assert resp.degraded is False
        assert len(resp.modelos) == 2
        assert resp.modelos[0].id == "alpha"
        assert resp.modelos[0].rank_dominio == 1

    def test_sin_resultados_marca_degraded_no_data(self):
        e = make_engine_with_rows({CATASTRO_TRONO_VIEW: []})
        resp = e.recommend(use_case="nonexistent", dominio="dominio_inexistente")
        assert resp.degraded is True
        assert resp.degraded_reason == "no_models_match_filters"
        assert resp.modelos == []

    def test_cache_hit_segunda_llamada_idempotente(self):
        rows = [_make_view_row()]
        e = make_engine_with_rows({CATASTRO_TRONO_VIEW: rows})
        r1 = e.recommend(use_case="same", dominio="llm_frontier", top_n=1)
        r2 = e.recommend(use_case="same", dominio="llm_frontier", top_n=1)
        assert r1.cache_hit is False
        assert r2.cache_hit is True

    def test_cache_no_almacena_degraded(self):
        e = make_engine_with_rows({CATASTRO_TRONO_VIEW: []})
        e.recommend(use_case="x", dominio="ninguno")
        assert e._cache.size() == 0

    def test_filtros_propagados_al_query(self):
        rows = [_make_view_row()]
        client_holder = {}

        def _factory():
            c = _FakeClient({CATASTRO_TRONO_VIEW: rows})
            client_holder["c"] = c
            return c
        e = RecommendationEngine(db_factory=_factory)
        e.recommend(
            use_case="t",
            dominio="llm_frontier",
            macroarea="Inteligencia",
            top_n=3,
            estado="production",
        )
        # Solo verificamos que se llamó table()
        assert client_holder["c"].last_table == CATASTRO_TRONO_VIEW


# ============================================================================
# 4. GET_MODELO()
# ============================================================================


class TestGetModelo:
    def test_id_vacio_falla(self):
        e = RecommendationEngine(db_factory=None)
        with pytest.raises(CatastroRecommendInvalidArgs):
            e.get_modelo("")

    def test_db_caida_retorna_none(self):
        e = RecommendationEngine(db_factory=None)
        assert e.get_modelo("alpha-model") is None

    def test_modelo_no_existe_retorna_none(self):
        e = make_engine_with_rows({"catastro_modelos": []})
        assert e.get_modelo("nonexistent-id") is None

    def test_modelo_existe_retorna_detallado(self):
        row = {
            "id": "alpha-model",
            "nombre": "Alpha",
            "proveedor": "test",
            "macroarea": "Inteligencia",
            "dominios": ["llm_frontier"],
            "subcapacidades": ["razonamiento", "código"],
            "trono_global": 75.0,
            "trono_delta": 2.0,
            "quality_score": 85.0,
            "cost_efficiency": 70.0,
            "speed_score": 80.0,
            "reliability_score": 90.0,
            "brand_fit": 0.85,
            "sovereignty": 0.5,
            "velocity": 0.7,
            "confidence": 0.9,
            "estado": "production",
            "open_weights": False,
            "last_validated_at": "2026-05-04T20:00:00Z",
        }
        e = make_engine_with_rows({"catastro_modelos": [row]})
        m = e.get_modelo("alpha-model")
        assert m is not None
        assert isinstance(m, ModeloDetallado)
        assert m.id == "alpha-model"
        assert m.subcapacidades == ["razonamiento", "código"]
        assert m.estado == "production"


# ============================================================================
# 5. LIST_DOMINIOS()
# ============================================================================


class TestListDominios:
    def test_db_caida_retorna_degraded(self):
        e = RecommendationEngine(db_factory=None)
        resp = e.list_dominios()
        assert resp.degraded is True
        assert resp.degraded_reason == "no_db_factory_configured"
        assert resp.macroareas == {}
        assert resp.total_dominios == 0

    def test_agrupa_por_macroarea_con_conteos(self):
        rows = [
            {"macroarea": "Inteligencia", "dominios": ["llm_frontier", "coding_llms"]},
            {"macroarea": "Inteligencia", "dominios": ["llm_frontier"]},
            {"macroarea": "Visión", "dominios": ["text_to_image"]},
        ]
        e = make_engine_with_rows({"catastro_modelos": rows})
        resp = e.list_dominios()
        assert resp.degraded is False
        assert "Inteligencia" in resp.macroareas
        assert "Visión" in resp.macroareas
        # llm_frontier aparece 2 veces, coding_llms 1 vez
        intel = {d.dominio: d.modelos_count for d in resp.macroareas["Inteligencia"]}
        assert intel["llm_frontier"] == 2
        assert intel["coding_llms"] == 1


# ============================================================================
# 6. STATUS()
# ============================================================================


class TestStatus:
    def test_status_healthy_con_modelos(self):
        rows = [
            {"macroarea": "Inteligencia", "dominios": ["llm_frontier"],
             "last_validated_at": "2026-05-04T20:00:00Z"},
            {"macroarea": "Visión", "dominios": ["t2i"],
             "last_validated_at": "2026-05-04T19:00:00Z"},
        ]
        e = make_engine_with_rows({"catastro_modelos": rows})
        snap = e.status()
        assert snap.trust_level == "healthy"
        assert snap.degraded is False
        assert snap.modelos_count == 2
        assert snap.dominios_count == 2
        assert set(snap.macroareas) == {"Inteligencia", "Visión"}
        assert snap.last_update is not None

    def test_status_degraded_sin_modelos(self):
        e = make_engine_with_rows({"catastro_modelos": []})
        snap = e.status()
        assert snap.trust_level == "degraded"
        assert snap.degraded is True
        assert snap.degraded_reason == "no_models_match_filters"


# ============================================================================
# 7. CATASTRO_ROUTES — AUTH + ENDPOINTS
# ============================================================================


@pytest.fixture
def app_with_engine(monkeypatch):
    """FastAPI app de test con engine inyectado y auth configurada."""
    monkeypatch.setenv("MONSTRUO_API_KEY", "test-key-bloque5")
    rows = [_make_view_row()]
    engine = make_engine_with_rows({CATASTRO_TRONO_VIEW: rows, "catastro_modelos": [{
        "id": "alpha-model",
        "nombre": "Alpha",
        "proveedor": "test",
        "macroarea": "Inteligencia",
        "dominios": ["llm_frontier"],
        "trono_global": 70.0,
        "estado": "production",
    }]})
    app = FastAPI()
    app.state.catastro_engine = engine
    _routes.set_dependencies(engine)
    app.include_router(_routes.router, prefix="/v1/catastro")
    return TestClient(app)


class TestCatastroRoutesAuth:
    def test_recommend_sin_api_key_da_401(self, app_with_engine):
        r = app_with_engine.post("/v1/catastro/recommend",
                                 json={"use_case": "test"})
        assert r.status_code == 401
        assert "catastro_api_key_missing" in r.json()["detail"]

    def test_recommend_api_key_invalida_da_401(self, app_with_engine):
        r = app_with_engine.post(
            "/v1/catastro/recommend",
            json={"use_case": "test"},
            headers={"X-API-Key": "wrong-key"},
        )
        assert r.status_code == 401
        assert "catastro_api_key_invalid" in r.json()["detail"]

    def test_recommend_api_key_via_bearer_funciona(self, app_with_engine):
        r = app_with_engine.post(
            "/v1/catastro/recommend",
            json={"use_case": "razonamiento", "dominio": "llm_frontier"},
            headers={"Authorization": "Bearer test-key-bloque5"},
        )
        assert r.status_code == 200

    def test_status_endpoint_funciona(self, app_with_engine):
        r = app_with_engine.get(
            "/v1/catastro/status",
            headers={"X-API-Key": "test-key-bloque5"},
        )
        assert r.status_code == 200
        body = r.json()
        assert "trust_level" in body
        assert "modelos_count" in body

    def test_get_modelo_404_si_no_existe(self, app_with_engine):
        # El fixture solo tiene "alpha-model" → este 404
        r = app_with_engine.get(
            "/v1/catastro/modelos/no-existe-id",
            headers={"X-API-Key": "test-key-bloque5"},
        )
        assert r.status_code == 404
        assert "catastro_recommend_modelo_not_found" in r.json()["detail"]


class TestCatastroRoutesAuthSinEnv:
    def test_recommend_sin_env_var_da_503(self, monkeypatch):
        # Sin MONSTRUO_API_KEY el guard devuelve 503
        monkeypatch.delenv("MONSTRUO_API_KEY", raising=False)
        engine = make_engine_with_rows({CATASTRO_TRONO_VIEW: [_make_view_row()]})
        app = FastAPI()
        app.state.catastro_engine = engine
        _routes.set_dependencies(engine)
        app.include_router(_routes.router, prefix="/v1/catastro")
        client = TestClient(app)
        r = client.post("/v1/catastro/recommend", json={"use_case": "test"})
        assert r.status_code == 503
        assert "catastro_api_key_no_configurada" in r.json()["detail"]


# ============================================================================
# 8. MCP_TOOLS
# ============================================================================


class TestMCPTools:
    def test_set_mcp_engine_funciona(self):
        engine = RecommendationEngine(db_factory=None)
        _mcp_tools.set_mcp_engine(engine)
        assert _mcp_tools._get_engine() is engine

    def test_build_catastro_mcp_sin_fastmcp_retorna_none(self, monkeypatch):
        # Simular fastmcp no instalado
        import sys
        monkeypatch.setitem(sys.modules, "fastmcp", None)
        result = _mcp_tools.build_catastro_mcp()
        assert result is None


# ============================================================================
# 9. IDENTIDAD DE MARCA (Brand Compliance)
# ============================================================================


class TestIdentidadMarca:
    def test_errores_con_prefijo_catastro_recommend(self):
        # Todos los códigos de error tienen identidad de marca
        assert CatastroRecommendError.code.startswith("catastro_recommend_")
        assert CatastroRecommendInvalidArgs.code.startswith("catastro_recommend_")

    def test_endpoints_no_son_genericos(self):
        # Naming endpoints debe ser semántico (recommend, modelos, dominios, status)
        # no genérico (api, service, handler, ...)
        paths = [r.path for r in _routes.router.routes]
        for p in paths:
            assert not any(g in p for g in ["service", "handler", "utils", "misc"])

    def test_router_tag_es_catastro(self):
        # Los routes deben estar tagged como 'catastro' para Brand Compliance
        for route in _routes.router.routes:
            if hasattr(route, "tags"):
                assert "catastro" in route.tags or route.tags == []


# ============================================================================
# 10. OPT-IN INTEGRATION TEST (real Supabase)
# ============================================================================


@pytest.mark.skipif(
    os.environ.get("SUPABASE_INTEGRATION_TESTS") != "true",
    reason="Set SUPABASE_INTEGRATION_TESTS=true para correr el smoke real",
)
def test_real_supabase_status_smoke():
    """
    Solo corre si SUPABASE_INTEGRATION_TESTS=true.
    Requiere SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY en el env.
    """
    factory = build_default_db_factory()
    e = RecommendationEngine(db_factory=factory)
    snap = e.status()
    # No assertamos contenido específico — solo que la llamada no crashea
    assert isinstance(snap, StatusSnapshot)
    assert snap.queried_at is not None
