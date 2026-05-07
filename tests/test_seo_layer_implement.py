"""Tests del SeoLayer.implement() y .monitor() reales (DSC-G-002)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kernel.transversales import (  # noqa: E402
    BusinessModelArchetype,
    GeoRegion,
    RestrictedVerticalError,
    TransversalContext,
    VerticalId,
)
from kernel.transversales.seo import SeoLayer  # noqa: E402


def _ctx(vertical: VerticalId, archetype: BusinessModelArchetype) -> TransversalContext:
    return TransversalContext(vertical=vertical, archetype=archetype)


def test_implement_for_cip_returns_json_ld_with_investment_schema():
    layer = SeoLayer()
    ctx = _ctx(VerticalId.CIP, BusinessModelArchetype.TOKENIZED_REAL_ESTATE)
    rec = layer.recommend(ctx)
    art = layer.implement(rec)

    parsed = json.loads(art["json_ld_block"])
    assert parsed["@context"] == "https://schema.org"
    types = parsed["@type"]
    if isinstance(types, list):
        assert "InvestmentOrInvestmentScheme" in types
        assert "RealEstateListing" in types
    else:
        assert types in ("InvestmentOrInvestmentScheme", "RealEstateListing")
    assert art["indexable"] is True
    assert art["robots_meta"] == "index,follow"
    assert "disclosure_tokens_no_son_equity_inmueble_slot" in art["disclosures_required"]


def test_implement_for_bioguard_marks_noindex_per_cofepris():
    layer = SeoLayer()
    ctx = _ctx(VerticalId.BIOGUARD, BusinessModelArchetype.IOT_B2B_REGULATED)
    rec = layer.recommend(ctx)
    art = layer.implement(rec)
    assert art["indexable"] is False
    assert art["robots_meta"] == "noindex,nofollow"
    assert "COFEPRIS" in (art["indexable_blocker_reason"] or "")


def test_implement_for_liketickets_event_schema_with_required_fields():
    layer = SeoLayer()
    ctx = _ctx(
        VerticalId.LIKETICKETS,
        BusinessModelArchetype.TICKETING_LIMITED_INVENTORY,
    )
    rec = layer.recommend(ctx)
    art = layer.implement(rec)
    parsed = json.loads(art["json_ld_block"])
    types = parsed["@type"]
    types_list = types if isinstance(types, list) else [types]
    assert "Event" in types_list
    assert "Product" in types_list
    assert "startDate" in parsed
    assert "STARTDATE" in str(parsed["startDate"])
    assert "location" in parsed
    assert "offers" in parsed
    assert art["ssr_required"] is True


def test_implement_for_k365_includes_geo_yucatan():
    layer = SeoLayer()
    ctx = _ctx(VerticalId.KUKULKAN_365, BusinessModelArchetype.REAL_ESTATE_DISTRICT)
    rec = layer.recommend(ctx)
    art = layer.implement(rec)
    geo_meta = [m for m in art["meta_tags_html"] if "geo.region" in m]
    assert len(geo_meta) == 1
    assert "MX-YUC" in geo_meta[0]
    assert "365_dias" in art["differentiator_keywords"]
    assert "climatizado" in art["differentiator_keywords"]


def test_implement_includes_canonical_link_and_hreflang():
    layer = SeoLayer()
    ctx = _ctx(VerticalId.CIP, BusinessModelArchetype.TOKENIZED_REAL_ESTATE)
    rec = layer.recommend(ctx)
    art = layer.implement(rec)
    canonical_tags = [m for m in art["meta_tags_html"] if "canonical" in m]
    assert len(canonical_tags) == 1
    hreflang = art["hreflang_links_html"]
    assert any('hreflang="es-MX"' in h for h in hreflang)


def test_implement_json_ld_is_valid_json():
    layer = SeoLayer()
    archetypes_per_vertical = {
        VerticalId.CIP: BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
        VerticalId.LIKETICKETS: BusinessModelArchetype.TICKETING_LIMITED_INVENTORY,
        VerticalId.KUKULKAN_365: BusinessModelArchetype.REAL_ESTATE_DISTRICT,
        VerticalId.BIOGUARD: BusinessModelArchetype.IOT_B2B_REGULATED,
        VerticalId.TOP_CONTROL_PC: BusinessModelArchetype.AI_AGENT_PLATFORM_CONSUMER,
        VerticalId.MUNDO_DE_TATA: BusinessModelArchetype.ECOMMERCE_ARTISANAL,
        VerticalId.EL_MONSTRUO_APP: BusinessModelArchetype.AGENT_PLATFORM_B2B,
    }
    for vertical, archetype in archetypes_per_vertical.items():
        ctx = _ctx(vertical, archetype)
        rec = layer.recommend(ctx)
        art = layer.implement(rec)
        try:
            json.loads(art["json_ld_block"])
        except json.JSONDecodeError as e:
            raise AssertionError(f"{vertical.value}: JSON-LD invalido: {e}")


def test_implement_propagates_validation_tags():
    layer = SeoLayer()
    ctx = _ctx(VerticalId.CIP, BusinessModelArchetype.TOKENIZED_REAL_ESTATE)
    rec = layer.recommend(ctx)
    art = layer.implement(rec)
    assert any(
        "[NEEDS_PERPLEXITY_VALIDATION]" in t
        for t in art["validation_tags_pending"]
    )


def test_implement_for_mena_baduy_raises_via_recommend():
    layer = SeoLayer()
    ctx = _ctx(VerticalId.MENA_BADUY, BusinessModelArchetype.AGENT_PLATFORM_B2B)
    try:
        layer.recommend(ctx)
        raise AssertionError("debio levantar")
    except RestrictedVerticalError:
        pass


def test_monitor_for_cip_returns_health_report():
    layer = SeoLayer()
    ctx = _ctx(VerticalId.CIP, BusinessModelArchetype.TOKENIZED_REAL_ESTATE)
    health = layer.monitor(ctx)
    assert health["vertical"] == "cip"
    assert health["structural_health"]["indexable"] is True
    assert health["structural_health"]["schema_types_count"] == 2
    assert health["search_console_health"]["status"] == "pending_implementation"
    assert any("Perplexity" in w for w in health["warnings"])


def test_monitor_for_bioguard_reports_indexability_blocker():
    layer = SeoLayer()
    ctx = _ctx(VerticalId.BIOGUARD, BusinessModelArchetype.IOT_B2B_REGULATED)
    health = layer.monitor(ctx)
    assert any("COFEPRIS" in b for b in health["blockers"])
    assert health["structural_health"]["indexable"] is False


def test_implement_for_top_control_pc_includes_software_app_required_fields():
    layer = SeoLayer()
    ctx = _ctx(
        VerticalId.TOP_CONTROL_PC,
        BusinessModelArchetype.AI_AGENT_PLATFORM_CONSUMER,
    )
    rec = layer.recommend(ctx)
    art = layer.implement(rec)
    parsed = json.loads(art["json_ld_block"])
    assert parsed["@type"] == "SoftwareApplication"
    assert "applicationCategory" in parsed
    assert "operatingSystem" in parsed


if __name__ == "__main__":
    test_implement_for_cip_returns_json_ld_with_investment_schema()
    test_implement_for_bioguard_marks_noindex_per_cofepris()
    test_implement_for_liketickets_event_schema_with_required_fields()
    test_implement_for_k365_includes_geo_yucatan()
    test_implement_includes_canonical_link_and_hreflang()
    test_implement_json_ld_is_valid_json()
    test_implement_propagates_validation_tags()
    test_implement_for_mena_baduy_raises_via_recommend()
    test_monitor_for_cip_returns_health_report()
    test_monitor_for_bioguard_reports_indexability_blocker()
    test_implement_for_top_control_pc_includes_software_app_required_fields()
    print("\n[ok] Los 11 tests de SeoLayer.implement+monitor pasaron.")
