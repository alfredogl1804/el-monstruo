"""Tests del DSC-as-Contract de la Capa Operaciones (DSC-G-017)."""
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
from kernel.transversales.operaciones import OperacionesLayer  # noqa: E402
from kernel.transversales.operaciones._canonical_constraints import (  # noqa: E402
    OPERACIONES_CANONICAL_PER_VERTICAL,
    SUPPORTED_FULFILLMENT_PATTERNS,
    SUPPORTED_SUPPORT_CHANNELS,
    is_commercial,
    require_commercial,
)


CAPILLA = (
    Path(__file__).resolve().parent.parent
    / "discovery_forense"
    / "CAPILLA_DECISIONES"
)


def _read_dsc(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def test_support_channels_subset_of_supported():
    for v, cfg in OPERACIONES_CANONICAL_PER_VERTICAL.items():
        for ch in cfg.get("support_channels", []):
            assert ch in SUPPORTED_SUPPORT_CHANNELS, (
                f"{v.value} usa channel {ch!r} no soportado"
            )


def test_fulfillment_patterns_subset_of_supported():
    for v, cfg in OPERACIONES_CANONICAL_PER_VERTICAL.items():
        for fp in cfg.get("fulfillment_patterns", []):
            assert fp in SUPPORTED_FULFILLMENT_PATTERNS, (
                f"{v.value} usa fulfillment {fp!r} no soportado"
            )


def test_dsc_cip_pend_blocks_operations():
    cip = OPERACIONES_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert cip["operations_can_launch_mx_today"] is False
    assert "DSC-CIP-PEND-001" in cip["operations_blocker_reason"]
    assert "venta_directa_inmueble_subyacente" in cip["prohibited_operations"]


def test_dsc_liketickets_003_canonical_components():
    dsc = _read_dsc(
        CAPILLA / "LIKETICKETS"
        / "DSC-LIKETICKETS-003_patron_checkout_stripe_replicable.md"
    )
    assert "checkout.session.completed" in dsc
    lt = OPERACIONES_CANONICAL_PER_VERTICAL[VerticalId.LIKETICKETS]
    components = lt["fulfillment_components_required"]
    assert "stripe_session_create" in components
    assert "webhook_checkout_session_completed" in components
    assert "confirmSeatsForOrder_db_write" in components


def test_dsc_lt_002_inventory_313():
    lt = OPERACIONES_CANONICAL_PER_VERTICAL[VerticalId.LIKETICKETS]
    assert lt["inventory_canonical_count"] == 313


def test_dsc_k365_001_support_24_7():
    k = OPERACIONES_CANONICAL_PER_VERTICAL[VerticalId.KUKULKAN_365]
    assert k["support_24_7_required"] is True
    assert "phone_24x7" in k["support_channels"]


def test_dsc_bg_pend_cofepris_ops_blocked():
    bg = OPERACIONES_CANONICAL_PER_VERTICAL[VerticalId.BIOGUARD]
    assert bg["operations_can_launch_mx_today"] is False
    assert "cofepris_pendiente" in bg["regulatory_blockers"]
    post_approval = bg["regulatory_ops_post_approval"]
    assert "cofepris_quarterly_reporting" in post_approval


def test_mena_baduy_no_operaciones():
    try:
        require_commercial(VerticalId.MENA_BADUY)
        raise AssertionError("debio levantar")
    except RestrictedVerticalError:
        pass


def test_layer_instantiable_and_recommend():
    layer = OperacionesLayer()
    assert layer.layer_name == "operaciones"
    ctx = TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
    )
    result = layer.recommend(ctx)
    rule_ids = {r.rule_id for r in result.recommendations}
    assert "operaciones.support.channels" in rule_ids
    assert "operaciones.fulfillment.patterns" in rule_ids
    assert "operaciones.regulatory.gates" in rule_ids
    reg = next(
        r for r in result.recommendations
        if r.rule_id == "operaciones.regulatory.gates"
    )
    assert reg.value["operations_can_launch_mx_today"] is False


def test_layer_implement_not_implemented():
    layer = OperacionesLayer()
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
    test_support_channels_subset_of_supported()
    test_fulfillment_patterns_subset_of_supported()
    test_dsc_cip_pend_blocks_operations()
    test_dsc_liketickets_003_canonical_components()
    test_dsc_lt_002_inventory_313()
    test_dsc_k365_001_support_24_7()
    test_dsc_bg_pend_cofepris_ops_blocked()
    test_mena_baduy_no_operaciones()
    test_layer_instantiable_and_recommend()
    test_layer_implement_not_implemented()
    print("\n[ok] Los 10 tests del DSC-as-Contract de Capa Operaciones pasaron.")
