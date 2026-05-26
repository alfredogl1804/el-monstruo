# tests/test_transversales_publicidad_implement_monitor.py
"""
Sprint TRANSVERSAL-001 T4 — tests de PublicidadLayer.implement+monitor.

Foco: garantizar HARD SAFEGUARDS (paused default + spend_cap=0 + firma
Alfredo requerida). Cero spend sin DSC firmado.
"""

from __future__ import annotations

import pytest

from kernel.transversales.base import (
    BusinessModelArchetype,
    TransversalContext,
    VerticalId,
)
from kernel.transversales.publicidad import PublicidadLayer


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


def test_all_campaigns_paused_by_default(liketickets_ctx):
    """SAFEGUARD CRITICO: ninguna campaign puede tener status != paused."""
    layer = PublicidadLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    assert len(impl["campaigns_plan"]) >= 1
    for c in impl["campaigns_plan"]:
        assert c["status"] == "paused", (
            f"VIOLACION SAFEGUARD: campaign {c['platform']}/{c['angle']} con status={c['status']}"
        )


def test_spend_cap_zero_by_default(liketickets_ctx):
    """SAFEGUARD: spend_cap_daily_usd debe ser exactamente 0.0."""
    layer = PublicidadLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    assert impl["hard_safeguards"]["spend_cap_daily_usd"] == 0.0
    for c in impl["campaigns_plan"]:
        assert c["spend_cap_daily_usd"] == 0.0


def test_activation_requires_firma_alfredo(liketickets_ctx):
    """SAFEGUARD: activation_requires_firma_alfredo=True hard."""
    layer = PublicidadLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    assert impl["hard_safeguards"]["activation_requires_firma_alfredo"] is True
    assert impl["hard_safeguards"]["activation_dsc_gate"] == "DSC-G-002"


def test_campaigns_have_copy_slots(liketickets_ctx):
    """Slots canonicos {{NAME_SLOT}} esperados (patron SEO)."""
    layer = PublicidadLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    for c in impl["campaigns_plan"]:
        assert c["campaign_name_slot"].startswith("{{")
        assert c["primary_text_slot"].startswith("{{")
        assert c["headline_slot"].startswith("{{")


def test_ad_platform_endpoints_canonical(liketickets_ctx):
    """Endpoints REST deben coincidir con docs oficiales 2026."""
    layer = PublicidadLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    for c in impl["campaigns_plan"]:
        endpoints = c["endpoints"]
        if c["platform"] == "meta_ads":
            assert "graph.facebook.com" in endpoints["create_campaign"]
        elif c["platform"] == "google_ads":
            assert "googleads.googleapis.com" in endpoints["create_campaign"]
        elif c["platform"] == "tiktok_ads":
            assert "business-api.tiktok.com" in endpoints["create_campaign"]
        elif c["platform"] == "linkedin_ads":
            assert "api.linkedin.com" in endpoints["create_campaign"]


def test_implement_validation_log_anchors(liketickets_ctx):
    """CA5: implement debe anchor 3 magnas (cpc, ad_formats, platform_policy)."""
    layer = PublicidadLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    claim_types = {a["claim_type"] for a in impl["validation_log_anchors"]}
    assert any(c.startswith("cpc_benchmark_2026:") for c in claim_types)
    assert any(c.startswith("ad_formats_2026:") for c in claim_types)
    assert "platform_policy_2026" in claim_types


def test_monitor_all_paused_status(liketickets_ctx):
    layer = PublicidadLayer()
    mon = layer.monitor(liketickets_ctx)
    assert mon["spend_health"]["status"] == "all_paused"
    assert mon["spend_health"]["spend_observed_24h_usd"] == 0.0
    assert mon["spend_health"]["active_campaigns_count"] == 0
    assert mon["structural_health"]["all_paused"] is True


def test_monitor_no_blockers_for_compliant_setup(liketickets_ctx):
    """LIKETICKETS con setup compliant → 0 blockers en monitor."""
    layer = PublicidadLayer()
    mon = layer.monitor(liketickets_ctx)
    assert mon["blockers"] == []


def test_monitor_warnings_aggregate(cip_ctx):
    """Warnings esperados: envs pendientes + tags Perplexity pendientes."""
    layer = PublicidadLayer()
    mon = layer.monitor(cip_ctx)
    assert isinstance(mon["warnings"], list)
    # Al menos 1 warning (envs pendientes en test env).
    assert len(mon["warnings"]) >= 1


def test_implement_dry_run_default_true(liketickets_ctx):
    layer = PublicidadLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    assert impl["dry_run"] is True
    assert "DSC-G-002" in impl["dry_run_reason"]
