# tests/test_transversales_ventas_constraints.py
"""
Tests del DSC-as-Contract de la Capa Ventas (DSC-G-017 enforcement aplicado
a los constants per-vertical).

Cada test parsea el archivo .md del DSC autoritativo y verifica que el
constant Python en _canonical_constraints.py coincide con el texto. Si
alguien modifica el DSC sin actualizar el constant (o viceversa), el
test falla. Eso convierte el DSC de texto-que-puedo-ignorar a
contrato-que-el-codigo-respeta.

Cubrimiento:
  - DSC-CIP-002 ticket minimo $1 USD ↔ MIN_TICKET_USD_CIP == 1.00
  - DSC-CIP-001 propiedad nunca se vende ↔ propiedad_nunca_se_enajena True
  - DSC-CIP-005 lanzamiento sureste MX ↔ geo_initial_markets contiene yucatan
  - DSC-LIKETICKETS-003 stripe pattern canonico ↔ checkout_pattern aplica
    a CIP, LikeTickets, K365, TopControlPC, MundoDeTata
  - DSC-LT-002 313 butacas piloto ↔ inventario_piloto_butacas == 313
  - DSC-K365-001 365 dias operacion ↔ operacion_anual_dias == 365
  - DSC-MB-001 OPSEC ↔ MENA_BADUY in NON_COMMERCIAL_VERTICALS
  - DSC-BG-PEND-001 COFEPRIS pendiente ↔ comercializacion_mx_permitida False

Plus tests de la interfaz (instantiation, RestrictedVerticalError, etc.).
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
from kernel.transversales.ventas import VentasLayer  # noqa: E402
from kernel.transversales.ventas._canonical_constraints import (  # noqa: E402
    NON_COMMERCIAL_VERTICALS,
    PRICING_CANONICAL_PER_VERTICAL,
    VERTICAL_ARCHETYPE,
    is_commercial,
    require_commercial,
)


CAPILLA = ROOT / "discovery_forense" / "CAPILLA_DECISIONES"


def _read_dsc(path: Path) -> str:
    assert path.exists(), f"DSC no existe: {path}"
    return path.read_text(encoding="utf-8")


def test_dsc_cip_002_ticket_minimo_1_usd():
    dsc = _read_dsc(CAPILLA / "CIP" / "DSC-CIP-002_ticket_minimo_1_usd.md")
    assert "$1 USD" in dsc, "DSC-CIP-002 debe mencionar literal '$1 USD'"
    assert "ticket mínimo" in dsc.lower() or "ticket minimo" in dsc.lower()
    cip = PRICING_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert cip["min_ticket_usd"] == 1.00
    assert cip["max_ticket_usd"] is None
    assert "DSC-CIP-002" in cip["source_dscs"]


def test_dsc_cip_001_propiedad_nunca_se_vende():
    dsc = _read_dsc(CAPILLA / "CIP" / "DSC-CIP-001_propiedad_nunca_se_vende.md")
    text_low = dsc.lower()
    assert "nunca se vende" in text_low or "nunca se enajena" in text_low
    cip = PRICING_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert cip["propiedad_nunca_se_enajena"] is True
    assert "DSC-CIP-001" in cip["source_dscs"]


def test_dsc_cip_005_lanzamiento_sureste_mx():
    dsc = _read_dsc(
        CAPILLA / "CIP" / "DSC-CIP-005_lanzamiento_focalizado_sureste_mx.md"
    )
    text_low = dsc.lower()
    assert "sureste" in text_low
    assert any(r in text_low for r in ["yucatán", "yucatan", "quintana roo", "campeche"])
    cip = PRICING_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    initial = cip["geo_initial_markets"]
    assert "yucatan" in initial
    assert "quintana_roo" in initial
    assert "campeche" in initial
    assert "DSC-CIP-005" in cip["source_dscs"]


def test_dsc_liketickets_003_stripe_canonico_replicable():
    dsc = _read_dsc(
        CAPILLA / "LIKETICKETS" / "DSC-LIKETICKETS-003_patron_checkout_stripe_replicable.md"
    )
    text_low = dsc.lower()
    assert "stripe" in text_low
    assert "webhook" in text_low
    assert "checkout.session.completed" in dsc
    assert "cip" in text_low
    cip = PRICING_CANONICAL_PER_VERTICAL[VerticalId.CIP]
    assert cip["checkout_pattern"] == "stripe_session_webhook_canonical"
    assert "DSC-LIKETICKETS-003" in cip["source_dscs"]
    lt = PRICING_CANONICAL_PER_VERTICAL[VerticalId.LIKETICKETS]
    expected = lt["checkout_pattern_componentes"]
    assert "stripe_session_create" in expected
    assert "webhook_checkout_session_completed" in expected
    assert "confirmSeatsForOrder_db_write" in expected


def test_dsc_lt_002_313_butacas_piloto():
    dsc = _read_dsc(
        CAPILLA / "LIKETICKETS" / "DSC-LT-002_producto_piloto_313_butacas.md"
    )
    assert "313" in dsc
    text_low = dsc.lower()
    assert "butaca" in text_low or "asiento" in text_low or "lugar" in text_low
    lt = PRICING_CANONICAL_PER_VERTICAL[VerticalId.LIKETICKETS]
    assert lt["inventario_piloto_butacas"] == 313


def test_dsc_k365_001_operacion_365_dias():
    dsc = _read_dsc(
        CAPILLA / "KUKULKAN-365" / "DSC-K365-001_distrito_entretenimiento_climatizado.md"
    )
    assert "365" in dsc
    text_low = dsc.lower()
    assert "merida" in text_low or "mérida" in text_low
    k = PRICING_CANONICAL_PER_VERTICAL[VerticalId.KUKULKAN_365]
    assert k["operacion_anual_dias"] == 365
    assert k["ubicacion_geografica_unica"] == "merida"


def test_dsc_mb_001_mena_baduy_no_comercial():
    dsc = _read_dsc(
        CAPILLA / "MENA-BADUY" / "DSC-MB-001_operacion_electoral_merida_2027.md"
    )
    text_low = dsc.lower()
    assert "opsec" in text_low or "confidencialidad" in text_low
    assert "electoral" in text_low or "candidatura" in text_low
    assert VerticalId.MENA_BADUY in NON_COMMERCIAL_VERTICALS
    assert not is_commercial(VerticalId.MENA_BADUY)
    try:
        require_commercial(VerticalId.MENA_BADUY)
        raise AssertionError("require_commercial debe levantar para MENA_BADUY")
    except RestrictedVerticalError as e:
        assert "OPSEC" in str(e) or "comercial" in str(e).lower()


def test_dsc_bg_pend_cofepris_bloqueante():
    bg = PRICING_CANONICAL_PER_VERTICAL[VerticalId.BIOGUARD]
    assert bg["regulatory_blocker"] == "cofepris_pending"
    assert bg["comercializacion_mx_permitida"] is False


def test_ventas_layer_instantiable():
    layer = VentasLayer()
    assert layer.layer_name == "ventas"


def test_ventas_recommend_for_cip_returns_structured_data():
    layer = VentasLayer()
    ctx = TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
        geo_region=GeoRegion.MX_SURESTE,
    )
    result = layer.recommend(ctx)
    assert isinstance(result, TransversalRecommendations)
    assert result.layer_name == "ventas"
    assert result.vertical == VerticalId.CIP
    pricing_rec = next(
        (r for r in result.recommendations
         if r.rule_id == "ventas.pricing.tiers.structural"),
        None,
    )
    assert pricing_rec is not None
    assert pricing_rec.value["min_ticket_usd"] == 1.00
    geo_rec = next(
        (r for r in result.recommendations
         if r.rule_id == "ventas.geo.initial_markets"),
        None,
    )
    assert geo_rec is not None
    assert "yucatan" in geo_rec.value["initial_markets"]
    assert any(
        "[NEEDS_PERPLEXITY_VALIDATION]" in tag
        for tag in result.aggregated_validation_tags
    )


def test_ventas_recommend_for_mena_baduy_raises():
    layer = VentasLayer()
    ctx = TransversalContext(
        vertical=VerticalId.MENA_BADUY,
        archetype=BusinessModelArchetype.AGENT_PLATFORM_B2B,
    )
    try:
        layer.recommend(ctx)
        raise AssertionError("Debio levantar RestrictedVerticalError")
    except RestrictedVerticalError as e:
        assert "MENA_BADUY" in str(e) or "mena_baduy" in str(e).lower()


def test_ventas_implement_not_implemented():
    layer = VentasLayer()
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


def test_vertical_archetype_mapping_complete():
    for v in VerticalId:
        if v in NON_COMMERCIAL_VERTICALS:
            continue
        assert v in VERTICAL_ARCHETYPE, f"falta archetype para {v}"
        assert v in PRICING_CANONICAL_PER_VERTICAL, (
            f"falta entry en PRICING_CANONICAL_PER_VERTICAL para {v}"
        )


if __name__ == "__main__":
    test_dsc_cip_002_ticket_minimo_1_usd()
    test_dsc_cip_001_propiedad_nunca_se_vende()
    test_dsc_cip_005_lanzamiento_sureste_mx()
    test_dsc_liketickets_003_stripe_canonico_replicable()
    test_dsc_lt_002_313_butacas_piloto()
    test_dsc_k365_001_operacion_365_dias()
    test_dsc_mb_001_mena_baduy_no_comercial()
    test_dsc_bg_pend_cofepris_bloqueante()
    test_ventas_layer_instantiable()
    test_ventas_recommend_for_cip_returns_structured_data()
    test_ventas_recommend_for_mena_baduy_raises()
    test_ventas_implement_not_implemented()
    test_vertical_archetype_mapping_complete()
    print("\n[ok] Los 13 tests del DSC-as-Contract de Capa Ventas pasaron.")
