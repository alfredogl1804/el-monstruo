"""Tests del DSC-as-Contract de la Capa Tendencias (DSC-G-017)."""
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
from kernel.transversales.tendencias import TendenciasLayer  # noqa: E402
from kernel.transversales.tendencias._canonical_constraints import (  # noqa: E402
    MONITORING_CADENCES,
    SUPPORTED_DATA_SOURCES,
    TENDENCIAS_CANONICAL_PER_VERTICAL,
    is_commercial,
    require_commercial,
)


def test_data_sources_are_subset_of_supported():
    for vertical, cfg in TENDENCIAS_CANONICAL_PER_VERTICAL.items():
        for ds in cfg.get("data_sources", []):
            assert ds in SUPPORTED_DATA_SOURCES, (
                f"{vertical.value} usa data_source {ds!r} no soportado"
            )


def test_cadence_in_canonical_set():
    for vertical, cfg in TENDENCIAS_CANONICAL_PER_VERTICAL.items():
        cad = cfg.get("monitoring_cadence")
        if cad:
            assert cad in MONITORING_CADENCES, f"{vertical}: cadence invalida {cad}"


def test_cip_blockchain_analytics_present():
    cip = TENDENCIAS_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert "blockchain_analytics" in cip["data_sources"]
    assert "DSC-CIP-004" in cip["source_dscs"]


def test_liketickets_real_time_cadence():
    lt = TENDENCIAS_CANONICAL_PER_VERTICAL[VerticalId.LIKETICKETS]
    assert lt["monitoring_cadence"] == "real_time"


def test_bg_regulatory_feeds_priorized():
    bg = TENDENCIAS_CANONICAL_PER_VERTICAL[VerticalId.BIOGUARD]
    assert "regulatory_feeds" in bg["data_sources"]
    assert bg.get("monitoring_cadence_critical_signals") == "real_time"
    signals = bg["signal_types_priorizados"]
    assert any("cofepris" in s for s in signals)


def test_mena_baduy_no_tendencias_comercial():
    try:
        require_commercial(VerticalId.MENA_BADUY)
        raise AssertionError("debio levantar")
    except RestrictedVerticalError:
        pass


def test_layer_instantiable_and_recommend():
    layer = TendenciasLayer()
    assert layer.layer_name == "tendencias"
    ctx = TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
    )
    result = layer.recommend(ctx)
    rule_ids = {r.rule_id for r in result.recommendations}
    assert "tendencias.data_sources" in rule_ids
    assert "tendencias.monitoring_cadence" in rule_ids
    assert "tendencias.signal_types" in rule_ids
    assert any("[NEEDS_PERPLEXITY_VALIDATION]" in t
               for t in result.aggregated_validation_tags)


def test_layer_implement_not_implemented():
    layer = TendenciasLayer()
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


def test_recommend_for_mena_baduy_raises():
    layer = TendenciasLayer()
    ctx = TransversalContext(
        vertical=VerticalId.MENA_BADUY,
        archetype=BusinessModelArchetype.AGENT_PLATFORM_B2B,
    )
    try:
        layer.recommend(ctx)
        raise AssertionError("debio levantar")
    except RestrictedVerticalError:
        pass


if __name__ == "__main__":
    test_data_sources_are_subset_of_supported()
    test_cadence_in_canonical_set()
    test_cip_blockchain_analytics_present()
    test_liketickets_real_time_cadence()
    test_bg_regulatory_feeds_priorized()
    test_mena_baduy_no_tendencias_comercial()
    test_layer_instantiable_and_recommend()
    test_layer_implement_not_implemented()
    test_recommend_for_mena_baduy_raises()
    print("\n[ok] Los 9 tests del DSC-as-Contract de Capa Tendencias pasaron.")
