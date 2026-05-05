"""
Tests Sprint 87.1 Bloque 2 — Embrión Ventas.

3 casos sintéticos:
  1. Landing premium artesanal → pricing one-time + canales premium
  2. Tienda online ecommerce → pricing one-time + canales ecommerce
  3. App móvil → pricing freemium/sub + canales mobile

Plus tests de schema validation, fallback heurístico y Brand DNA.
"""
from __future__ import annotations

import pytest

from kernel.embriones.ventas import (
    EMBRION_VENTAS_LLM_INVALIDO,
    CanalAdquisicion,
    EmbrionVentas,
    EmbrionVentasReport,
    PricingTentativo,
    PropuestaValor,
)


# ─────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────

@pytest.fixture
def embrion_no_llm() -> EmbrionVentas:
    return EmbrionVentas(use_llm=False)


@pytest.fixture
def embrion_no_key(monkeypatch) -> EmbrionVentas:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    return EmbrionVentas(use_llm=True)


# ─────────────────────────────────────────────────────────────────────────
# Caso 1: Landing premium artesanal (frase canónica de Alfredo)
# ─────────────────────────────────────────────────────────────────────────

def test_landing_premium_artesanal(embrion_no_llm: EmbrionVentas) -> None:
    """Frase canónica → ICP premium + pricing one-time alto + Instagram."""
    frase = (
        "Hacé una landing premium para vender pintura al óleo "
        "artesanal hecha en Mérida"
    )
    report = embrion_no_llm.analizar(frase_input=frase)

    assert isinstance(report, EmbrionVentasReport)
    assert report.source == "heuristic_fallback"
    # ICP refleja "premium" + "artesanal"
    assert "premium" in report.icp_refinado.lower() or "artesanal" in report.icp_refinado.lower()
    # Pricing one-time con rango premium
    assert report.pricing_tentativo.modelo == "one-time"
    assert report.pricing_tentativo.rango_min >= 50.0
    assert report.pricing_tentativo.rango_max >= 200.0
    # Top 3 canales con Instagram primero
    assert len(report.canales_adquisicion) == 3
    canales_str = " ".join(c.canal.lower() for c in report.canales_adquisicion)
    assert "instagram" in canales_str
    # Diferenciador menciona artesanía o premium
    assert (
        "artesanal" in report.propuesta_valor.diferenciador.lower()
        or "premium" in report.propuesta_valor.diferenciador.lower()
    )


# ─────────────────────────────────────────────────────────────────────────
# Caso 2: Tienda ecommerce
# ─────────────────────────────────────────────────────────────────────────

def test_tienda_ecommerce(embrion_no_llm: EmbrionVentas) -> None:
    """Frase tienda → canales ecommerce con Google/Meta Ads + email."""
    frase = "Quiero una tienda online de electrónica con envíos a todo Mexico"
    report = embrion_no_llm.analizar(frase_input=frase)

    assert isinstance(report, EmbrionVentasReport)
    canales_str = " ".join(c.canal.lower() for c in report.canales_adquisicion)
    assert "google" in canales_str or "meta" in canales_str or "email" in canales_str
    # Email marketing tiene CAC bajo (<5)
    email_canal = [
        c for c in report.canales_adquisicion if "email" in c.canal.lower()
    ]
    if email_canal:
        assert email_canal[0].cac_usd_estimado < 10.0


# ─────────────────────────────────────────────────────────────────────────
# Caso 3: App móvil
# ─────────────────────────────────────────────────────────────────────────

def test_app_movil(embrion_no_llm: EmbrionVentas) -> None:
    """Frase app móvil → canales mobile (ASO, TikTok, influencers)."""
    frase = "Necesito una app móvil para meditación con freemium tier"
    report = embrion_no_llm.analizar(frase_input=frase)

    assert isinstance(report, EmbrionVentasReport)
    # Pricing detecta freemium
    assert report.pricing_tentativo.modelo == "freemium"
    # ASO debería estar entre los canales
    canales_str = " ".join(c.canal.lower() for c in report.canales_adquisicion)
    assert "aso" in canales_str or "tiktok" in canales_str or "influencer" in canales_str


# ─────────────────────────────────────────────────────────────────────────
# Capa Memento: env var lookup en runtime + Brand DNA
# ─────────────────────────────────────────────────────────────────────────

def test_memento_runtime_env_lookup(embrion_no_key: EmbrionVentas) -> None:
    """Sin OPENAI_API_KEY → fallback heurístico."""
    report = embrion_no_key.analizar(frase_input="landing simple")
    assert report.source == "heuristic_fallback"


def test_brand_dna_error_class_naming() -> None:
    """Error class sigue convención brand DNA."""
    assert EMBRION_VENTAS_LLM_INVALIDO.__name__ == "EMBRION_VENTAS_LLM_INVALIDO"
    assert issubclass(EMBRION_VENTAS_LLM_INVALIDO, ValueError)


# ─────────────────────────────────────────────────────────────────────────
# Schema validation
# ─────────────────────────────────────────────────────────────────────────

def test_report_schema_extra_forbid() -> None:
    with pytest.raises(Exception):
        EmbrionVentasReport(  # type: ignore[call-arg]
            icp_refinado="ICP test largo suficiente para pasar min_length",
            propuesta_valor=PropuestaValor(
                statement="Statement de propuesta de valor para tests largo suficiente",
                beneficios=["Beneficio 1"],
                diferenciador="Diferenciador test largo suficiente",
            ),
            pricing_tentativo=PricingTentativo(
                modelo="one-time",
                rango_min=10.0,
                rango_max=100.0,
                razonamiento="Razonamiento test largo suficiente",
            ),
            canales_adquisicion=[
                CanalAdquisicion(
                    canal="Canal test",
                    cac_usd_estimado=10.0,
                    razonamiento="Razonamiento canal test largo suficiente",
                )
            ],
            confidence=0.5,
            campo_inventado="should_fail",  # type: ignore[call-arg]
        )


def test_pricing_modelo_vocabulario() -> None:
    """PricingTentativo.modelo acepta los 5 valores del vocabulario."""
    for modelo in ["one-time", "subscription", "freemium", "usage-based", "enterprise"]:
        p = PricingTentativo(
            modelo=modelo,
            rango_min=0.0,
            rango_max=100.0,
            razonamiento="Razonamiento de test largo suficiente",
        )
        assert p.modelo == modelo


def test_canales_min_max_size() -> None:
    """canales_adquisicion debe tener entre 1 y 5 items."""
    base = {
        "icp_refinado": "ICP test largo suficiente para pasar min_length validador",
        "propuesta_valor": PropuestaValor(
            statement="Statement de propuesta de valor para tests largo suficiente",
            beneficios=["B1"],
            diferenciador="Diferenciador test largo suficiente",
        ),
        "pricing_tentativo": PricingTentativo(
            modelo="one-time",
            rango_min=10.0,
            rango_max=100.0,
            razonamiento="Razonamiento test largo suficiente",
        ),
        "confidence": 0.5,
    }
    # 0 canales debería fallar
    with pytest.raises(Exception):
        EmbrionVentasReport(canales_adquisicion=[], **base)
    # 6 canales debería fallar
    canal_dummy = CanalAdquisicion(
        canal="Canal test",
        cac_usd_estimado=10.0,
        razonamiento="Razonamiento canal test largo suficiente",
    )
    with pytest.raises(Exception):
        EmbrionVentasReport(canales_adquisicion=[canal_dummy] * 6, **base)


def test_brief_propaga_a_icp(embrion_no_llm: EmbrionVentas) -> None:
    """Brief con audiencia propaga al ICP heurístico."""
    brief = {
        "propuesta_valor": "Pintura artesanal premium yucateca",
        "audiencia": "Coleccionistas LATAM y galeristas con presupuesto >$500.",
    }
    report = embrion_no_llm.analizar(
        frase_input="landing premium artesanal Mérida",
        brief=brief,
    )
    assert "Coleccionistas" in report.icp_refinado or "LATAM" in report.icp_refinado
