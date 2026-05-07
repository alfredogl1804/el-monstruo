"""Tests del DSC-as-Contract de la Capa Finanzas (DSC-G-017)."""
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
from kernel.transversales.finanzas import FinanzasLayer  # noqa: E402
from kernel.transversales.finanzas._canonical_constraints import (  # noqa: E402
    FINANZAS_CANONICAL_PER_VERTICAL,
    SUPPORTED_REVENUE_MODELS,
    SUPPORTED_TAX_FRAMEWORKS,
    is_commercial,
    require_commercial,
)


def test_revenue_models_subset_of_supported():
    for v, cfg in FINANZAS_CANONICAL_PER_VERTICAL.items():
        for rm in cfg.get("revenue_models", []):
            assert rm in SUPPORTED_REVENUE_MODELS, (
                f"{v.value} usa revenue_model {rm!r} no soportado"
            )


def test_tax_frameworks_subset_of_supported():
    for v, cfg in FINANZAS_CANONICAL_PER_VERTICAL.items():
        for tf in cfg.get("tax_frameworks_candidate", []):
            assert tf in SUPPORTED_TAX_FRAMEWORKS, (
                f"{v.value} usa tax framework {tf!r} no soportado"
            )


def test_dsc_cip_002_per_token_revenue():
    cip = FINANZAS_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert "transactional_per_token" in cip["revenue_models"]
    assert cip["min_unit_revenue_usd"] == 0.01


def test_dsc_cip_pend_tax_pending():
    cip = FINANZAS_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert cip["tax_framework_pending_decision"] is True
    assert "DSC-CIP-PEND-001" in cip["tax_blocker_reason"]


def test_dsc_cip_002_alt_distribution_pending():
    cip = FINANZAS_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert cip["distribution_method_pending"] is True
    candidates = cip["distribution_methods_candidate"]
    assert "usdc_stablecoin_on_chain_polygon" in candidates
    assert "fiat_mxn_spei_off_chain" in candidates


def test_dsc_lt_002_unit_economics_per_seat():
    lt = FINANZAS_CANONICAL_PER_VERTICAL[VerticalId.LIKETICKETS]
    ue = lt["unit_economics_tracked"]
    assert "revenue_per_seat_per_event" in ue
    assert "fill_rate_42_games_temporada" in ue


def test_dsc_k365_001_climatizado_cost_tracked():
    k = FINANZAS_CANONICAL_PER_VERTICAL[VerticalId.KUKULKAN_365]
    ue = k["unit_economics_tracked"]
    assert "cost_climatizacion_per_dia" in ue


def test_dsc_bg_pend_revenue_blocked_mx():
    bg = FINANZAS_CANONICAL_PER_VERTICAL[VerticalId.BIOGUARD]
    assert bg["revenue_can_be_recognized_mx_today"] is False
    assert bg["tax_framework_pending_decision"] is True


def test_dsc_cip_004_polygon_compliance_reporting():
    cip = FINANZAS_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    compliance = cip["compliance_reporting"]
    assert any("polygon_erc3643" in c for c in compliance)
    assert "DSC-CIP-004" in cip["source_dscs"]


def test_mena_baduy_no_finanzas_comercial():
    try:
        require_commercial(VerticalId.MENA_BADUY)
        raise AssertionError("debio levantar")
    except RestrictedVerticalError:
        pass


def test_layer_instantiable_and_recommend():
    layer = FinanzasLayer()
    assert layer.layer_name == "finanzas"
    ctx = TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
    )
    result = layer.recommend(ctx)
    rule_ids = {r.rule_id for r in result.recommendations}
    assert "finanzas.revenue.models" in rule_ids
    assert "finanzas.tax.framework" in rule_ids
    assert "finanzas.distribution.pending" in rule_ids
    assert any("tax_rates_2026" in t for t in result.aggregated_validation_tags)


def test_layer_implement_not_implemented():
    layer = FinanzasLayer()
    ctx = TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
    )
    rec = layer.recommend(ctx)
    try:
        layer.implement(rec)
        raise AssertionError("debio levantar NotImplementedError")
    except NotImplementedError as e:
        assert "TRANSVERSAL-001" in str(e)


if __name__ == "__main__":
    test_revenue_models_subset_of_supported()
    test_tax_frameworks_subset_of_supported()
    test_dsc_cip_002_per_token_revenue()
    test_dsc_cip_pend_tax_pending()
    test_dsc_cip_002_alt_distribution_pending()
    test_dsc_lt_002_unit_economics_per_seat()
    test_dsc_k365_001_climatizado_cost_tracked()
    test_dsc_bg_pend_revenue_blocked_mx()
    test_dsc_cip_004_polygon_compliance_reporting()
    test_mena_baduy_no_finanzas_comercial()
    test_layer_instantiable_and_recommend()
    test_layer_implement_not_implemented()
    print("\n[ok] Los 12 tests del DSC-as-Contract de Capa Finanzas pasaron.")
