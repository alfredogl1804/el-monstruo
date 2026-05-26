# tests/test_transversales_seo_monitor.py
"""
Sprint TRANSVERSAL-001 T3 — tests de SeoLayer.monitor().

Valida:
  - search_console_health declara endpoints y scopes oficiales (validation
    log anchor id=28 vigente)
  - schema_org_anchor presente (validation_log id=27)
  - disabled_until_oauth_configured=True cuando envs faltan
  - dry_run=True por defecto (HITL DSC-G-002)
"""

from __future__ import annotations

from kernel.transversales.base import (
    BusinessModelArchetype,
    TransversalContext,
    VerticalId,
)
from kernel.transversales.seo import SeoLayer


def _ctx() -> TransversalContext:
    return TransversalContext(
        vertical=VerticalId.LIKETICKETS,
        archetype=BusinessModelArchetype.TICKETING_LIMITED_INVENTORY,
    )


def test_monitor_returns_search_console_health():
    layer = SeoLayer()
    mon = layer.monitor(_ctx())
    assert "search_console_health" in mon
    assert "schema_org_anchor" in mon


def test_search_console_health_endpoints_are_canonical():
    """CA: endpoints declarados deben coincidir con docs oficiales 2026."""
    layer = SeoLayer()
    mon = layer.monitor(_ctx())
    sch = mon["search_console_health"]
    assert sch["api_version"] == "v1"
    assert "googleapis.com/webmasters/v3/sites/" in sch["endpoint_searchanalytics"]
    assert "searchAnalytics/query" in sch["endpoint_searchanalytics"]
    assert "webmasters.readonly" in sch["oauth_scope_required"]


def test_search_console_health_disabled_when_envs_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_SEARCH_CONSOLE_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("GOOGLE_SEARCH_CONSOLE_SITE_URL", raising=False)
    layer = SeoLayer()
    mon = layer.monitor(_ctx())
    sch = mon["search_console_health"]
    assert sch["status"] == "disabled_until_oauth_configured"
    assert sch["disabled_until_oauth_configured"] is True
    assert "GOOGLE_SEARCH_CONSOLE_OAUTH_TOKEN" in sch["pending_envs"]
    assert "GOOGLE_SEARCH_CONSOLE_SITE_URL" in sch["pending_envs"]


def test_search_console_health_ready_when_envs_present(monkeypatch):
    monkeypatch.setenv("GOOGLE_SEARCH_CONSOLE_OAUTH_TOKEN", "fake-token-xx")
    monkeypatch.setenv("GOOGLE_SEARCH_CONSOLE_SITE_URL", "https://liketickets.mx/")
    layer = SeoLayer()
    mon = layer.monitor(_ctx())
    sch = mon["search_console_health"]
    assert sch["status"] == "ready_for_fetch"
    assert sch["disabled_until_oauth_configured"] is False
    assert sch["pending_envs"] == []


def test_search_console_health_validation_log_anchor():
    """CA5: ancla la validation magna search_console_api_2026."""
    layer = SeoLayer()
    mon = layer.monitor(_ctx())
    anchor = mon["search_console_health"]["validation_log_anchor"]
    assert anchor["claim_type"] == "search_console_api_2026"
    assert anchor["validator"] == "perplexity"
    assert anchor["ttl_seconds"] >= 86400


def test_schema_org_anchor_present():
    """CA5: ancla la validation magna schema_org_vocabulary_2026."""
    layer = SeoLayer()
    mon = layer.monitor(_ctx())
    anchor = mon["schema_org_anchor"]
    assert anchor["claim_type"] == "schema_org_vocabulary_2026"
    assert anchor["validator"] == "perplexity"


def test_dry_run_default_true():
    """CA: dry_run=True por defecto (DSC-G-002 HITL)."""
    layer = SeoLayer()
    mon = layer.monitor(_ctx())
    assert mon["search_console_health"]["dry_run"] is True
    assert "DSC-G-002" in mon["search_console_health"]["dry_run_reason"]
