# tests/test_transversales_ventas_implement_monitor.py
"""
Sprint TRANSVERSAL-001 T2 — tests de VentasLayer.implement() y .monitor().

Cubre el wiring canonico stub (HubSpot Products + Stripe Products/Prices)
con slots conceptuales. Valida que:
  - implement() produce payloads estructuralmente correctos
  - monitor() detecta credenciales pendientes y tags Perplexity
  - dry_run=True hasta firma HITL via DSC-G-002
"""
from __future__ import annotations

from kernel.transversales.base import (
    BusinessModelArchetype,
    GeoRegion,
    TransversalContext,
    VerticalId,
)
from kernel.transversales.ventas import VentasLayer


def _ctx_liketickets() -> TransversalContext:
    return TransversalContext(
        vertical=VerticalId.LIKETICKETS,
        archetype=BusinessModelArchetype.TICKETING_LIMITED_INVENTORY,
        geo_region=GeoRegion.MX_MERIDA,
    )


def _ctx_cip() -> TransversalContext:
    return TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
    )


def test_implement_returns_canonical_keys():
    """implement() debe devolver el dict con keys canonicas."""
    layer = VentasLayer()
    recs = layer.recommend(_ctx_liketickets())
    impl = layer.implement(recs)

    expected_keys = {
        "vertical", "crm_target", "billing_target", "pricing_envelope",
        "hubspot_products_payload", "stripe_products_payload",
        "funnel_pipeline_stages", "checkout_pattern",
        "dry_run", "dry_run_reason",
        "pending_credentials", "validation_log_anchor",
        "validation_tags_pending",
    }
    assert expected_keys.issubset(impl.keys()), (
        f"keys faltantes: {expected_keys - impl.keys()}"
    )


def test_implement_crm_targets_are_canonical():
    """CA: crm_target=hubspot, billing_target=stripe (constantes canonicas)."""
    layer = VentasLayer()
    recs = layer.recommend(_ctx_cip())
    impl = layer.implement(recs)
    assert impl["crm_target"] == "hubspot"
    assert impl["billing_target"] == "stripe"


def test_implement_dry_run_true_by_default():
    """CA: dry_run debe ser True por defecto (push real requiere firma DSC-G-002)."""
    layer = VentasLayer()
    recs = layer.recommend(_ctx_liketickets())
    impl = layer.implement(recs)
    assert impl["dry_run"] is True
    assert "DSC-G-002" in impl["dry_run_reason"]


def test_implement_hubspot_payload_uses_canonical_endpoint():
    """CA: cada hubspot payload debe declarar endpoint canonico v3 products."""
    layer = VentasLayer()
    recs = layer.recommend(_ctx_liketickets())
    impl = layer.implement(recs)
    for payload in impl["hubspot_products_payload"]:
        assert payload["endpoint"] == "POST /crm/v3/objects/products"
        assert "properties" in payload
        # SKU canonico: <vertical>-<tier_label_slot>
        assert payload["properties"]["hs_sku"].startswith("liketickets-")


def test_implement_uses_slots_not_hardcoded_copy():
    """CA: payload usa slots {{...}}, NO copy hardcodeado (obj #9 doctrina)."""
    layer = VentasLayer()
    recs = layer.recommend(_ctx_liketickets())
    impl = layer.implement(recs)
    for payload in impl["hubspot_products_payload"]:
        name = payload["properties"]["name"]
        price = payload["properties"]["price"]
        desc = payload["properties"]["description"]
        assert name.startswith("{{") and name.endswith("_SLOT}}")
        assert price.startswith("{{") and price.endswith("_SLOT}}")
        assert desc.startswith("{{") and desc.endswith("_SLOT}}")


def test_implement_validation_log_anchor_present():
    """CA5: implement() ancla la validation magna hubspot_api_2026 vigente."""
    layer = VentasLayer()
    recs = layer.recommend(_ctx_liketickets())
    impl = layer.implement(recs)
    anchor = impl["validation_log_anchor"]
    assert anchor["claim_type"] == "hubspot_api_2026"
    assert anchor["validator"] == "perplexity"
    assert anchor["ttl_seconds"] >= 86400  # al menos 1 dia


def test_implement_funnel_stages_match_archetype():
    """CA: funnel stages para TICKETING_LIMITED_INVENTORY tiene 5 stages canonicos."""
    layer = VentasLayer()
    recs = layer.recommend(_ctx_liketickets())
    impl = layer.implement(recs)
    stages = impl["funnel_pipeline_stages"]
    assert "scarcity_alert" in stages
    assert "checkout_stripe_canonical" in stages


def test_monitor_returns_canonical_health_keys():
    """monitor() devuelve dict con structural_health + cac_ltv_health."""
    layer = VentasLayer()
    mon = layer.monitor(_ctx_liketickets())
    assert "structural_health" in mon
    assert "cac_ltv_health" in mon
    assert mon["cac_ltv_health"]["status"] == "pending_credentials"


def test_monitor_pending_credentials_warning_when_envs_missing(monkeypatch):
    """monitor() emite warning si HUBSPOT_ACCESS_TOKEN o STRIPE_SECRET_KEY faltan."""
    monkeypatch.delenv("HUBSPOT_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    layer = VentasLayer()
    mon = layer.monitor(_ctx_liketickets())
    creds_warn = [
        w for w in mon["warnings"] if "Credenciales pendientes" in w
    ]
    assert len(creds_warn) == 1
    assert "HUBSPOT_ACCESS_TOKEN" in creds_warn[0]
    assert "STRIPE_SECRET_KEY" in creds_warn[0]


def test_monitor_perplexity_tags_warning_when_pending():
    """monitor() emite warning si hay tags Perplexity pendientes."""
    layer = VentasLayer()
    mon = layer.monitor(_ctx_liketickets())
    tag_warn = [w for w in mon["warnings"] if "Perplexity" in w]
    assert len(tag_warn) == 1


def test_monitor_does_not_raise_for_cip():
    """CIP es vertical comercial \u2014 monitor() no debe levantar."""
    layer = VentasLayer()
    mon = layer.monitor(_ctx_cip())
    assert mon["vertical"] == "cip"
    assert "structural_health" in mon
