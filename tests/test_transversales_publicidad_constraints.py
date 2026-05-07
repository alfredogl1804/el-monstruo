# tests/test_transversales_publicidad_constraints.py
"""
Tests del DSC-as-Contract de la Capa Publicidad (DSC-G-017 enforcement).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kernel.transversales import (  # noqa: E402
    BusinessModelArchetype,
    RestrictedVerticalError,
    TransversalContext,
    VerticalId,
)
from kernel.transversales.publicidad import PublicidadLayer  # noqa: E402
from kernel.transversales.publicidad._canonical_constraints import (  # noqa: E402
    PUBLICIDAD_CANONICAL_PER_VERTICAL,
    SUPPORTED_AD_PLATFORMS,
    is_commercial,
    require_commercial,
)


CAPILLA = ROOT / "discovery_forense" / "CAPILLA_DECISIONES"


def _read_dsc(path: Path) -> str:
    assert path.exists(), f"DSC no existe: {path}"
    return path.read_text(encoding="utf-8")


def test_cip_blocks_tiktok_audience_mismatch():
    cip = PUBLICIDAD_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert "tiktok_ads" in cip["ad_platforms_explicitly_blocked"]
    assert "tiktok_ads" not in cip["ad_platforms_allowed"]
    assert cip["ad_platforms_block_reason"] is not None
    disclaimers = cip["required_disclaimers"]
    assert "tokens_no_son_equity_inmueble" in disclaimers
    assert "rendimiento_no_garantizado_pasado_no_indica_futuro" in disclaimers


def test_dsc_cip_005_publicidad_geo_sureste():
    dsc = _read_dsc(
        CAPILLA / "CIP" / "DSC-CIP-005_lanzamiento_focalizado_sureste_mx.md"
    )
    assert "sureste" in dsc.lower()
    cip = PUBLICIDAD_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert "yucatan" in cip["geo_target_states"]
    assert "quintana_roo" in cip["geo_target_states"]
    assert "campeche" in cip["geo_target_states"]
    assert "DSC-CIP-005" in cip["source_dscs"]


def test_dsc_lt_002_publicidad_scarcity_angle():
    dsc = _read_dsc(
        CAPILLA / "LIKETICKETS" / "DSC-LT-002_producto_piloto_313_butacas.md"
    )
    assert "313" in dsc
    lt = PUBLICIDAD_CANONICAL_PER_VERTICAL[VerticalId.LIKETICKETS]
    angles = lt["creative_angles_canonical"]
    assert any("313" in a or "scarcity" in a for a in angles)


def test_dsc_k365_001_publicidad_climatizado_angle():
    dsc = _read_dsc(
        CAPILLA / "KUKULKAN-365" / "DSC-K365-001_distrito_entretenimiento_climatizado.md"
    )
    assert "365" in dsc
    k = PUBLICIDAD_CANONICAL_PER_VERTICAL[VerticalId.KUKULKAN_365]
    angles = k["creative_angles_canonical"]
    assert any("climatizado" in a for a in angles)
    assert any("365" in a for a in angles)


def test_bg_bloquea_consumer_ads_y_geo_mx():
    bg = PUBLICIDAD_CANONICAL_PER_VERTICAL[VerticalId.BIOGUARD]
    assert bg["ad_platforms_allowed"] == ["linkedin_ads"]
    assert "meta_ads" in bg["ad_platforms_explicitly_blocked"]
    assert "tiktok_ads" in bg["ad_platforms_explicitly_blocked"]
    assert "mx_nacional" in bg["geo_blocked"]
    assert "COFEPRIS" in bg["geo_blocked_reason"]
    assert bg["ad_priority_phase_1"] is False
    assert "DSC-BG-PEND-001" in bg["source_dscs"]


def test_dsc_mb_001_mena_baduy_no_publicidad():
    assert not is_commercial(VerticalId.MENA_BADUY)
    try:
        require_commercial(VerticalId.MENA_BADUY)
        raise AssertionError("require_commercial debe levantar")
    except RestrictedVerticalError:
        pass


def test_supported_platforms_finite_set():
    expected = {
        "meta_ads", "google_ads", "tiktok_ads", "linkedin_ads",
        "reddit_ads", "x_ads", "pinterest_ads", "youtube_ads",
    }
    assert SUPPORTED_AD_PLATFORMS == expected


def test_all_allowed_platforms_in_supported_set():
    for vertical, cfg in PUBLICIDAD_CANONICAL_PER_VERTICAL.items():
        for p in cfg.get("ad_platforms_allowed", []):
            assert p in SUPPORTED_AD_PLATFORMS, (
                f"{vertical.value} permite {p} que NO esta en "
                f"SUPPORTED_AD_PLATFORMS. Adicion requiere DSC."
            )


def test_publicidad_layer_instantiable():
    layer = PublicidadLayer()
    assert layer.layer_name == "publicidad"


def test_publicidad_recommend_for_cip_returns_structured_data():
    layer = PublicidadLayer()
    ctx = TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
    )
    result = layer.recommend(ctx)
    platforms = next(
        (r for r in result.recommendations
         if r.rule_id == "publicidad.platforms.allowed_blocked"),
        None,
    )
    assert platforms is not None
    assert "tiktok_ads" in platforms.value["platforms_explicitly_blocked"]
    assert "meta_ads" in platforms.value["platforms_allowed"]
    disclaimer = next(
        (r for r in result.recommendations
         if r.rule_id == "publicidad.disclaimers.required"),
        None,
    )
    assert disclaimer is not None
    assert "tokens_no_son_equity_inmueble" in disclaimer.value["disclaimers"]
    assert any(
        "[NEEDS_PERPLEXITY_VALIDATION]" in t
        for t in result.aggregated_validation_tags
    )


def test_publicidad_recommend_for_bioguard_blocks_geo_mx():
    layer = PublicidadLayer()
    ctx = TransversalContext(
        vertical=VerticalId.BIOGUARD,
        archetype=BusinessModelArchetype.IOT_B2B_REGULATED,
    )
    result = layer.recommend(ctx)
    geo = next(
        (r for r in result.recommendations
         if r.rule_id == "publicidad.geo.targeting"),
        None,
    )
    assert geo is not None
    assert "mx_nacional" in geo.value["geo_blocked"]
    assert "COFEPRIS" in (geo.value["geo_blocked_reason"] or "")


def test_publicidad_recommend_for_mena_baduy_raises():
    layer = PublicidadLayer()
    ctx = TransversalContext(
        vertical=VerticalId.MENA_BADUY,
        archetype=BusinessModelArchetype.AGENT_PLATFORM_B2B,
    )
    try:
        layer.recommend(ctx)
        raise AssertionError("Debio levantar RestrictedVerticalError")
    except RestrictedVerticalError:
        pass


def test_publicidad_implement_not_implemented():
    layer = PublicidadLayer()
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


if __name__ == "__main__":
    test_cip_blocks_tiktok_audience_mismatch()
    test_dsc_cip_005_publicidad_geo_sureste()
    test_dsc_lt_002_publicidad_scarcity_angle()
    test_dsc_k365_001_publicidad_climatizado_angle()
    test_bg_bloquea_consumer_ads_y_geo_mx()
    test_dsc_mb_001_mena_baduy_no_publicidad()
    test_supported_platforms_finite_set()
    test_all_allowed_platforms_in_supported_set()
    test_publicidad_layer_instantiable()
    test_publicidad_recommend_for_cip_returns_structured_data()
    test_publicidad_recommend_for_bioguard_blocks_geo_mx()
    test_publicidad_recommend_for_mena_baduy_raises()
    test_publicidad_implement_not_implemented()
    print("\n[ok] Los 13 tests del DSC-as-Contract de Capa Publicidad pasaron.")
