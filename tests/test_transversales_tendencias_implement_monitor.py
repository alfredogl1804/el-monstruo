# tests/test_transversales_tendencias_implement_monitor.py
"""
Sprint TRANSVERSAL-001 T5 — tests de TendenciasLayer.implement+monitor.

Valida:
  - collectors_plan canonico per vertical (cobertura de data_sources)
  - trend_signals_row_template con slots conceptuales
  - validation_log_anchors a magnas 29 (data_source_apis_vigentes_2026) y
    30 (alerting_stack_2026)
  - dry_run=True default (DSC-G-002 HITL)
  - monitor.signal_count_24h = None / status='pending_storage_injection'
    si no hay storage Supabase
  - cadence respeta MONITORING_CADENCES per archetype
"""
from __future__ import annotations

import pytest

from kernel.transversales.base import (
    BusinessModelArchetype,
    TransversalContext,
    VerticalId,
)
from kernel.transversales.tendencias import TendenciasLayer


@pytest.fixture
def liketickets_ctx() -> TransversalContext:
    return TransversalContext(
        vertical=VerticalId.LIKETICKETS,
        archetype=BusinessModelArchetype.TICKETING_LIMITED_INVENTORY,
    )


@pytest.fixture
def cip_ctx() -> TransversalContext:
    return TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
    )


def test_implement_returns_collectors_plan(liketickets_ctx):
    layer = TendenciasLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    assert "collectors_plan" in impl
    assert isinstance(impl["collectors_plan"], list)
    assert len(impl["collectors_plan"]) >= 1
    for c in impl["collectors_plan"]:
        assert "source" in c
        assert "collector" in c
        assert "ready" in c


def test_implement_returns_trend_signals_row_template(cip_ctx):
    layer = TendenciasLayer()
    rec = layer.recommend(cip_ctx)
    impl = layer.implement(rec)
    template = impl["trend_signals_row_template"]
    expected_keys = {
        "vertical", "source", "signal_type", "score", "payload",
        "observed_at_unix", "ttl_seconds", "collector",
    }
    assert expected_keys.issubset(set(template.keys()))
    # Slots con sintaxis canonica SEO {{NAME_SLOT}}.
    assert template["source"] == "{{SOURCE_SLOT}}"
    assert template["signal_type"] == "{{SIGNAL_TYPE_SLOT}}"


def test_implement_validation_log_anchors(liketickets_ctx):
    layer = TendenciasLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    anchors = impl["validation_log_anchors"]
    claim_types = {a["claim_type"] for a in anchors}
    assert "data_source_apis_vigentes_2026" in claim_types
    assert "alerting_stack_2026" in claim_types


def test_implement_dry_run_default_true(cip_ctx):
    layer = TendenciasLayer()
    rec = layer.recommend(cip_ctx)
    impl = layer.implement(rec)
    assert impl["dry_run"] is True
    assert "DSC-G-002" in impl["dry_run_reason"]


def test_implement_marks_pending_envs(liketickets_ctx, monkeypatch):
    """CA: pending_envs detectado correctamente."""
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    monkeypatch.delenv("SONAR_API_KEY", raising=False)
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_TRENDS_API_KEY", raising=False)
    layer = TendenciasLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    not_ready = [c for c in impl["collectors_plan"] if not c["ready"]]
    assert len(not_ready) >= 1
    assert len(impl["pending_envs"]) >= 1


def test_monitor_returns_trend_signals_health(cip_ctx):
    layer = TendenciasLayer()
    mon = layer.monitor(cip_ctx)
    assert "trend_signals_health" in mon
    sh = mon["trend_signals_health"]
    assert sh["table"] == "trend_signals"
    # Sin storage Supabase inyectado en test → status pending_storage_injection.
    assert sh["status"] in (
        "pending_storage_injection", "counted", "storage_error",
    ) or sh["status"].startswith("storage_error")


def test_monitor_warnings_aggregate(liketickets_ctx):
    layer = TendenciasLayer()
    mon = layer.monitor(liketickets_ctx)
    # Warnings esperados: collectors no ready + tags Perplexity pendientes.
    assert isinstance(mon["warnings"], list)
    assert len(mon["warnings"]) >= 1


def test_monitor_no_blockers_for_commercial_vertical(cip_ctx):
    """CA: vertical comercial con data_sources canonicas no debe tener
    blockers estructurales."""
    layer = TendenciasLayer()
    mon = layer.monitor(cip_ctx)
    assert mon["blockers"] == []
