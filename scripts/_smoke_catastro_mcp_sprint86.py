"""
Sprint 86 Bloque 5 — Smoke E2E del MCP Server catastro.recommend()

Valida sin tocar Supabase real:
  · RecommendationEngine en modo degraded (sin db)
  · RecommendationEngine con fake client (datos mock)
  · Cache LRU funciona (hit/miss)
  · APIRouter /v1/catastro/* con auth Bearer
  · Sub-FastMCP catastro_mcp se construye (si fastmcp está instalado)

Run:
  $ python3 scripts/_smoke_catastro_mcp_sprint86.py

[Hilo Manus Catastro] · Sprint 86 Bloque 5 · 2026-05-04
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock

# Ensure repo root in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.catastro import (
    CATASTRO_TRONO_VIEW,
    DEFAULT_TOP_N,
    MAX_TOP_N,
    RecommendationEngine,
    __version__,
    __bloque__,
)
from kernel.catastro import catastro_routes as _routes
from kernel.catastro import mcp_tools as _mcp_tools


# ============================================================================
# FAKES
# ============================================================================


class _FakeQuery:
    def __init__(self, rows):
        self._rows = list(rows)
        self._filters = []
        self._limit = None

    def select(self, *a, **k): return self
    def eq(self, col, val, **k):
        self._filters.append((col, val))
        return self
    def neq(self, col, val, **k): return self
    def order(self, *a, **k): return self
    def limit(self, n, **k):
        self._limit = n
        return self

    def execute(self):
        rows = self._rows
        for col, val in self._filters:
            rows = [r for r in rows if r.get(col) == val]
        if self._limit is not None:
            rows = rows[: self._limit]
        return MagicMock(data=rows)


class _FakeClient:
    def __init__(self, rows_by_table):
        self._rows = rows_by_table

    def table(self, name):
        return _FakeQuery(self._rows.get(name, []))


def view_row(id="alpha-model", trono=70.0, dominio="llm_frontier", rank=1):
    return {
        "id": id,
        "nombre": id.title(),
        "proveedor": "test",
        "macroarea": "Inteligencia",
        "dominio": dominio,
        "estado": "production",
        "quality_score": 80.0,
        "cost_efficiency": 70.0,
        "speed_score": 75.0,
        "reliability_score": 90.0,
        "brand_fit": 0.8,
        "confidence": 0.8,
        "trono_global": trono,
        "trono_delta": 1.5,
        "trono_low": trono - 2.0,
        "trono_high": trono + 2.0,
        "rank_dominio": rank,
        "precio_input_per_million": 5.0,
        "precio_output_per_million": 15.0,
        "open_weights": False,
        "last_validated_at": "2026-05-04T20:00:00Z",
    }


# ============================================================================
# ESCENARIOS
# ============================================================================


def header(label):
    print(f"\n{'─' * 76}\n▸ {label}\n{'─' * 76}")


def main():
    print(f"\nCatastro MCP Server — Smoke Sprint 86 Bloque 5 (v{__version__}, bloque {__bloque__})")
    print("=" * 76)

    # ── Escenario 1: Modo degraded sin db ───────────────────────────────
    header("1 · Modo degraded sin db_factory")
    e = RecommendationEngine(db_factory=None)
    snap = e.status()
    print(f"  trust_level: {snap.trust_level}")
    print(f"  degraded: {snap.degraded} (reason: {snap.degraded_reason})")
    assert snap.trust_level == "down"
    assert snap.degraded is True

    resp = e.recommend(use_case="cualquier cosa")
    print(f"  recommend.degraded: {resp.degraded} ({resp.degraded_reason})")
    assert resp.degraded is True

    # ── Escenario 2: Engine con datos mock ──────────────────────────────
    header("2 · Engine con fake client (3 modelos en llm_frontier)")
    rows_view = [
        view_row("alpha-model", trono=85.0, rank=1),
        view_row("beta-model", trono=72.0, rank=2),
        view_row("gamma-model", trono=58.0, rank=3),
    ]
    rows_modelos = [
        {"id": "alpha-model", "nombre": "Alpha", "proveedor": "test",
         "macroarea": "Inteligencia", "dominios": ["llm_frontier"],
         "trono_global": 85.0, "estado": "production",
         "last_validated_at": "2026-05-04T20:00:00Z"},
        {"id": "beta-model", "nombre": "Beta", "proveedor": "test",
         "macroarea": "Inteligencia", "dominios": ["llm_frontier"],
         "trono_global": 72.0, "estado": "production",
         "last_validated_at": "2026-05-04T20:00:00Z"},
    ]
    factory = lambda: _FakeClient({
        CATASTRO_TRONO_VIEW: rows_view,
        "catastro_modelos": rows_modelos,
    })
    e2 = RecommendationEngine(db_factory=factory)
    resp = e2.recommend(use_case="razonamiento legal", dominio="llm_frontier", top_n=2)
    print(f"  modelos retornados: {len(resp.modelos)}")
    print(f"  top1: {resp.modelos[0].id} (trono={resp.modelos[0].trono_global})")
    print(f"  cache_hit: {resp.cache_hit}")
    assert len(resp.modelos) == 2
    assert resp.modelos[0].id == "alpha-model"
    assert resp.cache_hit is False

    # ── Escenario 3: Cache LRU ──────────────────────────────────────────
    header("3 · Cache LRU (segunda llamada idéntica → hit)")
    resp2 = e2.recommend(use_case="razonamiento legal", dominio="llm_frontier", top_n=2)
    print(f"  cache_hit: {resp2.cache_hit}")
    print(f"  cache_size: {e2._cache.size()}")
    assert resp2.cache_hit is True
    flushed = e2.invalidate_cache()
    print(f"  invalidated: {flushed} entries")

    # ── Escenario 4: get_modelo por id ──────────────────────────────────
    header("4 · get_modelo por id (existe vs no existe)")
    m = e2.get_modelo("alpha-model")
    print(f"  alpha-model: {'existe' if m else 'NO existe'} (trono={m.trono_global if m else 'N/A'})")
    m_none = e2.get_modelo("zzz-no-existe")
    print(f"  zzz-no-existe: {'existe' if m_none else 'NO existe'}")
    assert m is not None
    assert m_none is None

    # ── Escenario 5: list_dominios ──────────────────────────────────────
    header("5 · list_dominios agrupado por macroárea")
    list_resp = e2.list_dominios()
    print(f"  macroareas: {list(list_resp.macroareas.keys())}")
    print(f"  total_dominios: {list_resp.total_dominios}")
    print(f"  degraded: {list_resp.degraded}")
    assert "Inteligencia" in list_resp.macroareas

    # ── Escenario 6: status healthy ─────────────────────────────────────
    header("6 · status healthy con modelos cargados")
    snap2 = e2.status()
    print(f"  trust_level: {snap2.trust_level}")
    print(f"  modelos_count: {snap2.modelos_count}, dominios_count: {snap2.dominios_count}")
    assert snap2.trust_level == "healthy"

    # ── Escenario 7: APIRouter REST + auth ──────────────────────────────
    header("7 · APIRouter /v1/catastro/* con auth Bearer")
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        os.environ["MONSTRUO_API_KEY"] = "smoke-test-key-b5"
        app = FastAPI()
        app.state.catastro_engine = e2
        _routes.set_dependencies(e2)
        app.include_router(_routes.router, prefix="/v1/catastro")
        client = TestClient(app)

        # Sin auth → 401
        r = client.get("/v1/catastro/status")
        print(f"  GET /status sin auth: {r.status_code}")
        assert r.status_code == 401

        # Con auth → 200
        r = client.get("/v1/catastro/status",
                       headers={"X-API-Key": "smoke-test-key-b5"})
        print(f"  GET /status con auth: {r.status_code} - trust_level={r.json().get('trust_level')}")
        assert r.status_code == 200

        r = client.post("/v1/catastro/recommend",
                        json={"use_case": "test", "dominio": "llm_frontier"},
                        headers={"X-API-Key": "smoke-test-key-b5"})
        print(f"  POST /recommend con auth: {r.status_code} - modelos={len(r.json().get('modelos', []))}")
        assert r.status_code == 200
    finally:
        os.environ.pop("MONSTRUO_API_KEY", None)

    # ── Escenario 8: FastMCP sub-server ─────────────────────────────────
    header("8 · FastMCP sub-server build")
    mcp = _mcp_tools.build_catastro_mcp()
    if mcp is None:
        print("  fastmcp no instalado → catastro_mcp = None (graceful)")
    else:
        print(f"  catastro_mcp OK: {mcp.__class__.__name__}")
    _mcp_tools.set_mcp_engine(e2)
    assert _mcp_tools._get_engine() is e2

    print("\n" + "=" * 76)
    print("  ✓ SMOKE SPRINT 86 BLOQUE 5 — TODOS LOS ESCENARIOS PASS")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    main()
