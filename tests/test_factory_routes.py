"""
Tests for kernel.factory_routes — Cognitive Republic Aggregator
================================================================

Sprint cero (SPR-FACTORY-AGGREGATORS-000) — DSC-G-019.

Coverage:
  - Schema validity for each endpoint
  - Filters (tier, kind, window, types)
  - Honest disclaimer for missing telemetry
  - No secret leakage in responses
  - No `kimi-k2-6` mentions in responses
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Importar solo el router; montarlo en una app FastAPI minimal para test
# aislado del kernel/main.py (que tiene side-effects pesados).
from fastapi import FastAPI

from kernel.factory_routes import factory_router


@pytest.fixture(scope="module")
def client():
    """Build a minimal FastAPI app with only factory_router for isolated testing."""
    app = FastAPI()
    app.include_router(factory_router)
    return TestClient(app)


# ---------------------------------------------------------------------------
# /v1/factory/constellation
# ---------------------------------------------------------------------------


def test_constellation_returns_200_and_valid_schema(client):
    """Endpoint must return 200 with required top-level keys."""
    resp = client.get("/v1/factory/constellation")
    assert resp.status_code == 200
    data = resp.json()
    for key in ("version", "generated_at", "binario_100", "nodes", "edges", "totals"):
        assert key in data, f"missing key: {key}"


def test_constellation_includes_kernel_core_node(client):
    """Core kernel must always appear as the central forge."""
    data = client.get("/v1/factory/constellation").json()
    kernel = next((n for n in data["nodes"] if n["forge_id"] == "kernel-monstruo"), None)
    assert kernel is not None
    assert kernel["tier"] == "core"
    assert kernel["kind"] == "kernel"


def test_constellation_filters_by_tier(client):
    """tier query param must filter the response correctly."""
    resp = client.get("/v1/factory/constellation?tier=core")
    data = resp.json()
    assert all(n["tier"] == "core" for n in data["nodes"])


def test_constellation_filters_by_kind(client):
    """kind query param must filter the response correctly."""
    resp = client.get("/v1/factory/constellation?kind=embryo_line")
    data = resp.json()
    assert all(n["kind"] == "embryo_line" for n in data["nodes"])


def test_constellation_no_secrets_in_response(client):
    """Response must not leak env var values for secrets."""
    raw = client.get("/v1/factory/constellation").text
    # Patrones de secretos comunes
    forbidden_patterns = [
        r"-----BEGIN (PRIVATE|RSA|EC) KEY-----",
        r"sk-[A-Za-z0-9]{20,}",
        r"eyJ[A-Za-z0-9]{30,}",  # JWT-like
        r"DATABASE_URL=.+",
    ]
    for pat in forbidden_patterns:
        assert not re.search(pat, raw), f"secret pattern leaked: {pat}"


# ---------------------------------------------------------------------------
# /v1/factory/economy
# ---------------------------------------------------------------------------


def test_economy_returns_200_and_valid_schema(client):
    resp = client.get("/v1/factory/economy")
    assert resp.status_code == 200
    data = resp.json()
    for key in ("version", "window", "kpis", "formulas_used", "data_quality"):
        assert key in data


def test_economy_kpis_include_all_15_keys(client):
    """The 15 canonical KPIs must all be present (some null)."""
    data = client.get("/v1/factory/economy").json()
    kpi_keys = {
        "cost_per_production_order_usd",
        "cost_per_embryo_line_usd",
        "cost_per_accepted_evidence_usd",
        "cost_per_verified_claim_usd",
        "cost_per_pr_draft_usd",
        "cost_per_t1_decision_usd",
        "rework_cost_usd",
        "dory_cost_avoided_usd",
        "human_time_saved_hours",
        "model_efficiency_index",
        "evidence_acceptance_rate",
        "production_throughput_per_day",
        "defect_rate",
        "autonomy_roi",
        "sovereignty_score",
    }
    assert kpi_keys.issubset(set(data["kpis"].keys()))


def test_economy_includes_5_canonical_formulas(client):
    """The 5 canonical formulas must always be present."""
    data = client.get("/v1/factory/economy").json()
    formula_keys = {
        "cognitive_roi",
        "dory_cost_avoided",
        "evidence_yield",
        "embryo_productivity",
        "t1_leverage",
    }
    assert formula_keys == set(data["formulas_used"].keys())


def test_economy_window_param_validation(client):
    """Invalid window must return 422."""
    resp = client.get("/v1/factory/economy?window=foo")
    assert resp.status_code == 422


def test_economy_window_24h_works(client):
    resp = client.get("/v1/factory/economy?window=24h")
    assert resp.status_code == 200
    assert resp.json()["window"] == "24h"


def test_economy_returns_null_for_missing_metrics(client):
    """KPIs sin telemetría devuelven null + disclaimer honesto."""
    data = client.get("/v1/factory/economy").json()
    assert data["data_quality"]["coverage"] == "partial"
    assert "honest_disclaimer" in data["data_quality"]
    assert isinstance(data["data_quality"]["missing_metrics"], list)


# ---------------------------------------------------------------------------
# /v1/factory/timeline
# ---------------------------------------------------------------------------


def test_timeline_returns_200_and_valid_schema(client):
    resp = client.get("/v1/factory/timeline")
    assert resp.status_code == 200
    data = resp.json()
    for key in ("version", "events", "totals", "window"):
        assert key in data


def test_timeline_returns_dsc_events(client):
    """At least some DSC events should be present (we have 30+ canonized)."""
    data = client.get("/v1/factory/timeline?types=dsc_signed").json()
    assert all(e["type"] == "dsc_signed" for e in data["events"])
    assert data["totals"]["dscs_signed"] > 0


def test_timeline_respects_limit(client):
    """limit param must cap the events array."""
    data = client.get("/v1/factory/timeline?limit=5").json()
    assert len(data["events"]) <= 5


def test_timeline_limit_max_500(client):
    """Limit > 500 must be rejected."""
    resp = client.get("/v1/factory/timeline?limit=999")
    assert resp.status_code == 422


def test_timeline_event_schema(client):
    """Each event must follow the SovereignTimelineEvent schema."""
    data = client.get("/v1/factory/timeline?limit=10").json()
    if not data["events"]:
        pytest.skip("no events to validate (empty repo)")
    ev = data["events"][0]
    required = {"id", "type", "timestamp", "title", "source", "severity"}
    assert required.issubset(set(ev.keys()))


# ---------------------------------------------------------------------------
# /v1/factory/diff
# ---------------------------------------------------------------------------


def test_diff_returns_200_or_503(client):
    """Diff returns 200 if genome present, 503 if not."""
    resp = client.get("/v1/factory/diff")
    assert resp.status_code in (200, 503)


def test_diff_schema_when_genome_present(client):
    """When genome_now.json exists, diff has full schema."""
    resp = client.get("/v1/factory/diff")
    if resp.status_code != 200:
        pytest.skip("genome_now.json not present in test env")
    data = resp.json()
    for key in ("version", "binario_100_live", "drift_count", "domains"):
        assert key in data
    for domain in ("github", "railway", "supabase", "live24h"):
        assert domain in data["domains"]


# ---------------------------------------------------------------------------
# Anti-patrones DSC-G-019
# ---------------------------------------------------------------------------


def test_no_kimi_k2_6_mentioned_in_any_endpoint(client):
    """DSC-G-019 prohíbe mencionar kimi-k2-6 en respuestas (ni como blacklist)."""
    for path in (
        "/v1/factory/constellation",
        "/v1/factory/economy",
        "/v1/factory/timeline",
        "/v1/factory/diff",
    ):
        resp = client.get(path)
        if resp.status_code == 200:
            assert "kimi-k2-6" not in resp.text.lower(), f"kimi-k2-6 leaked in {path}"


def test_no_factory_mode_string_in_responses(client):
    """DSC-G-019 deprecó 'Factory Mode'. No debe aparecer en respuestas."""
    for path in (
        "/v1/factory/constellation",
        "/v1/factory/economy",
        "/v1/factory/timeline",
    ):
        resp = client.get(path)
        if resp.status_code == 200:
            text_lower = resp.text.lower()
            assert "factory mode" not in text_lower, f"'Factory Mode' leaked in {path}"
            assert "factorymode" not in text_lower
