# tests/test_transversales_seo_constraints.py
"""
Tests del DSC-as-Contract de la Capa SEO (DSC-G-017 enforcement).

Mismo patron que tests/test_transversales_ventas_constraints.py: cada test
parsea el archivo .md del DSC autoritativo y verifica que el constant
Python en seo/_canonical_constraints.py coincide con el texto.

Cubrimiento:
  - DSC-CIP-005 sureste MX ↔ geo_target_states contiene yucatan/qroo/campeche
  - DSC-CIP-001 propiedad nunca enajena ↔ disclosure tokens_no_son_equity
  - DSC-LT-002 313 butacas ↔ schema_org_types incluye Event
  - DSC-K365-001 365 dias merida ↔ differentiator_keywords incluye 365_dias
  - DSC-BG-PEND-001 COFEPRIS ↔ robots_indexable False
  - DSC-MB-001 OPSEC ↔ require_commercial levanta para Mena Baduy
  - SeoLayer recommend genera robots.indexable + schema + geo + url + keyword
  - SeoLayer recommend para BG marca indexable False con razon CofePRIS
  - SeoLayer recommend etiqueta keyword research con NEEDS_PERPLEXITY_VALIDATION
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kernel.transversales import (  # noqa: E402
    BusinessModelArchetype,
    GeoRegion,
    RestrictedVerticalError,
    TransversalContext,
    TransversalRecommendations,
    VerticalId,
)
from kernel.transversales.seo import SeoLayer  # noqa: E402
from kernel.transversales.seo._canonical_constraints import (  # noqa: E402
    NON_COMMERCIAL_VERTICALS,
    SEO_CANONICAL_PER_VERTICAL,
    is_commercial,
    require_commercial,
)


CAPILLA = ROOT / "discovery_forense" / "CAPILLA_DECISIONES"


def _read_dsc(path: Path) -> str:
    assert path.exists(), f"DSC no existe: {path}"
    return path.read_text(encoding="utf-8")


def test_dsc_cip_005_seo_geo_target_sureste():
    dsc = _read_dsc(
        CAPILLA / "CIP" / "DSC-CIP-005_lanzamiento_focalizado_sureste_mx.md"
    )
    text_low = dsc.lower()
    assert "sureste" in text_low
    cip = SEO_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert cip["geo_target"] == GeoRegion.MX_SURESTE.value
    states = cip["geo_target_states"]
    assert "yucatan" in states
    assert "quintana_roo" in states
    assert "campeche" in states
    assert "DSC-CIP-005" in cip["source_dscs"]


def test_dsc_cip_001_seo_disclosure_tokens_no_equity():
    dsc = _read_dsc(CAPILLA / "CIP" / "DSC-CIP-001_propiedad_nunca_se_vende.md")
    text_low = dsc.lower()
    assert "nunca se vende" in text_low or "nunca se enajena" in text_low
    cip = SEO_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert "tokens_no_son_equity_inmueble" in cip["required_disclosures"]
    assert "DSC-CIP-001" in cip["source_dscs"]


def test_dsc_cip_seo_schema_types_canonical():
    cip = SEO_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    types = cip["schema_org_types"]
    assert "InvestmentOrInvestmentScheme" in types
    assert "RealEstateListing" in types


def test_dsc_lt_002_seo_event_schema():
    dsc = _read_dsc(
        CAPILLA / "LIKETICKETS" / "DSC-LT-002_producto_piloto_313_butacas.md"
    )
    assert "313" in dsc
    lt = SEO_CANONICAL_PER_VERTICAL[VerticalId.LIKETICKETS]
    assert "Event" in lt["schema_org_types"]
    assert "Product" in lt["schema_org_types"]
    required = lt["required_schema_fields_event"]
    assert "startDate" in required
    assert "location.address" in required
    assert "offers.price" in required


def test_dsc_k365_001_seo_365_differentiator_keyword():
    dsc = _read_dsc(
        CAPILLA / "KUKULKAN-365" / "DSC-K365-001_distrito_entretenimiento_climatizado.md"
    )
    assert "365" in dsc
    text_low = dsc.lower()
    assert "merida" in text_low or "mérida" in text_low
    k = SEO_CANONICAL_PER_VERTICAL[VerticalId.KUKULKAN_365]
    keywords = k["differentiator_keywords"]
    assert "365_dias" in keywords
    assert "climatizado" in keywords
    assert "merida_yucatan" in keywords
    assert "EntertainmentBusiness" in k["schema_org_types"]
    assert k["geo_target"] == GeoRegion.MX_MERIDA.value


def test_dsc_bg_pend_cofepris_seo_no_indexable():
    bg = SEO_CANONICAL_PER_VERTICAL[VerticalId.BIOGUARD]
    assert bg["robots_indexable"] is False
    assert bg["robots_indexable_blocker_reason"] is not None
    assert "COFEPRIS" in bg["robots_indexable_blocker_reason"]
    assert "DSC-BG-PEND-001" in bg["source_dscs"]
    disclosures = bg["required_disclosures"]
    assert "regulatory_status_pendiente_cofepris" in disclosures
    assert "MedicalDevice" in bg["schema_org_types"]


def test_dsc_mb_001_seo_no_indexable_per_opsec():
    assert VerticalId.MENA_BADUY in NON_COMMERCIAL_VERTICALS
    assert not is_commercial(VerticalId.MENA_BADUY)
    try:
        require_commercial(VerticalId.MENA_BADUY)
        raise AssertionError("require_commercial debe levantar para MENA_BADUY")
    except RestrictedVerticalError as e:
        assert "OPSEC" in str(e) or "comercial" in str(e).lower()


def test_seo_layer_instantiable():
    layer = SeoLayer()
    assert layer.layer_name == "seo"


def test_seo_recommend_for_cip_returns_structured_data():
    layer = SeoLayer()
    ctx = TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
        geo_region=GeoRegion.MX_SURESTE,
    )
    result = layer.recommend(ctx)
    assert isinstance(result, TransversalRecommendations)
    assert result.layer_name == "seo"
    indexable = next(
        (r for r in result.recommendations if r.rule_id == "seo.robots.indexable"),
        None,
    )
    assert indexable is not None
    assert indexable.value["indexable"] is True
    schema = next(
        (r for r in result.recommendations if r.rule_id == "seo.schema_org.types"),
        None,
    )
    assert schema is not None
    assert "InvestmentOrInvestmentScheme" in schema.value["types"]
    geo = next(
        (r for r in result.recommendations if r.rule_id == "seo.geo.targeting"),
        None,
    )
    assert geo is not None
    assert "yucatan" in geo.value["geo_target_states"]
    disclosure = next(
        (r for r in result.recommendations
         if r.rule_id == "seo.disclosures.required"),
        None,
    )
    assert disclosure is not None
    assert "tokens_no_son_equity_inmueble" in disclosure.value["disclosures"]
    keyword = next(
        (r for r in result.recommendations
         if r.rule_id == "seo.keywords.research_pending"),
        None,
    )
    assert keyword is not None
    assert any(
        "[NEEDS_PERPLEXITY_VALIDATION]" in tag
        for tag in keyword.needs_validation_tags
    )


def test_seo_recommend_for_bioguard_blocks_indexability():
    layer = SeoLayer()
    ctx = TransversalContext(
        vertical=VerticalId.BIOGUARD,
        archetype=BusinessModelArchetype.IOT_B2B_REGULATED,
    )
    result = layer.recommend(ctx)
    indexable = next(
        (r for r in result.recommendations if r.rule_id == "seo.robots.indexable"),
        None,
    )
    assert indexable is not None
    assert indexable.value["indexable"] is False
    assert indexable.value["robots_meta"] == "noindex,nofollow"
    assert "COFEPRIS" in (indexable.value["blocker_reason"] or "")


def test_seo_recommend_for_mena_baduy_raises():
    layer = SeoLayer()
    ctx = TransversalContext(
        vertical=VerticalId.MENA_BADUY,
        archetype=BusinessModelArchetype.AGENT_PLATFORM_B2B,
    )
    try:
        layer.recommend(ctx)
        raise AssertionError("Debio levantar RestrictedVerticalError")
    except RestrictedVerticalError as e:
        assert "MENA" in str(e).upper() or "comercial" in str(e).lower()


def test_seo_implement_not_implemented():
    layer = SeoLayer()
    ctx = TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
    )
    rec = layer.recommend(ctx)
    try:
        layer.implement(rec)
        raise AssertionError("Debio levantar NotImplementedError")
    except NotImplementedError as e:
        assert "TRANSVERSAL-001" in str(e)
        assert "[NEEDS_PERPLEXITY_VALIDATION]" in str(e)


def test_seo_aggregates_validation_tags():
    layer = SeoLayer()
    ctx = TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
    )
    result = layer.recommend(ctx)
    assert any("keyword_research_2026" in t for t in result.aggregated_validation_tags)
    assert any("competitor_seo_2026" in t for t in result.aggregated_validation_tags)
    assert any("google_ranking_factors_2026" in t for t in result.aggregated_validation_tags)


if __name__ == "__main__":
    test_dsc_cip_005_seo_geo_target_sureste()
    test_dsc_cip_001_seo_disclosure_tokens_no_equity()
    test_dsc_cip_seo_schema_types_canonical()
    test_dsc_lt_002_seo_event_schema()
    test_dsc_k365_001_seo_365_differentiator_keyword()
    test_dsc_bg_pend_cofepris_seo_no_indexable()
    test_dsc_mb_001_seo_no_indexable_per_opsec()
    test_seo_layer_instantiable()
    test_seo_recommend_for_cip_returns_structured_data()
    test_seo_recommend_for_bioguard_blocks_indexability()
    test_seo_recommend_for_mena_baduy_raises()
    test_seo_implement_not_implemented()
    test_seo_aggregates_validation_tags()
    print("\n[ok] Los 13 tests del DSC-as-Contract de Capa SEO pasaron.")
