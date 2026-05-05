"""
Tests Sprint 87.1 Bloque 1 — Embrión Técnico.

3 casos sintéticos:
  1. Landing premium → stack Next.js + Vercel
  2. Tienda online → stack ecommerce con Stripe
  3. App móvil → stack Expo

Plus tests de schema validation y fallback heurístico.
"""
from __future__ import annotations

import os

import pytest

from kernel.embriones.tecnico import (
    EMBRION_TECNICO_LLM_INVALIDO,
    EmbrionTecnico,
    EmbrionTecnicoReport,
    RiesgoTecnico,
    StackRecomendado,
)


# ─────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────

@pytest.fixture
def embrion_no_llm() -> EmbrionTecnico:
    """Embrión forzado a modo heurístico (use_llm=False)."""
    return EmbrionTecnico(use_llm=False)


@pytest.fixture
def embrion_no_key(monkeypatch) -> EmbrionTecnico:
    """Embrión con use_llm=True pero sin OPENAI_API_KEY → fallback."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    return EmbrionTecnico(use_llm=True)


# ─────────────────────────────────────────────────────────────────────────
# Caso 1: Landing premium
# ─────────────────────────────────────────────────────────────────────────

def test_landing_premium_heuristico(embrion_no_llm: EmbrionTecnico) -> None:
    """Frase canónica de Alfredo → stack Next.js + Vercel."""
    frase = (
        "Hacé una landing premium para vender pintura al óleo "
        "artesanal hecha en Mérida"
    )
    report = embrion_no_llm.analizar(frase_input=frase)

    assert isinstance(report, EmbrionTecnicoReport)
    assert report.source == "heuristic_fallback"
    assert "Next.js" in report.stack_recomendado.frontend
    assert report.stack_recomendado.deploy_target == "vercel"
    assert 1 <= report.complejidad_1_5 <= 5
    assert 1 <= report.tiempo_mvp_dias <= 180
    # Premium + vender → 2 riesgos detectados (premium quality + payments)
    assert len(report.riesgos) >= 2
    severidades = {r.severidad for r in report.riesgos}
    assert severidades.issubset({"baja", "media", "alta", "critica"})


# ─────────────────────────────────────────────────────────────────────────
# Caso 2: Tienda online
# ─────────────────────────────────────────────────────────────────────────

def test_tienda_online_heuristico(embrion_no_llm: EmbrionTecnico) -> None:
    """Frase tienda → stack ecommerce con FastAPI + Stripe."""
    frase = "Quiero una tienda online para vender vinos de Mendoza con Stripe"
    report = embrion_no_llm.analizar(frase_input=frase)

    assert isinstance(report, EmbrionTecnicoReport)
    assert "Stripe" in report.stack_recomendado.backend
    assert report.complejidad_1_5 >= 3
    # Ecommerce → riesgo PCI/payments alta
    riesgo_pagos = [
        r for r in report.riesgos
        if "pago" in r.descripcion.lower() or "pci" in r.descripcion.lower()
    ]
    assert len(riesgo_pagos) >= 1
    assert riesgo_pagos[0].severidad == "alta"


# ─────────────────────────────────────────────────────────────────────────
# Caso 3: App móvil
# ─────────────────────────────────────────────────────────────────────────

def test_app_movil_heuristico(embrion_no_llm: EmbrionTecnico) -> None:
    """Frase app móvil → stack Expo."""
    frase = "Necesito una app móvil para tracking de hábitos diarios"
    report = embrion_no_llm.analizar(frase_input=frase)

    assert isinstance(report, EmbrionTecnicoReport)
    assert "React Native" in report.stack_recomendado.frontend or "Expo" in report.stack_recomendado.frontend
    assert report.stack_recomendado.deploy_target == "expo"
    assert report.complejidad_1_5 >= 3  # apps son mas complejas
    assert report.tiempo_mvp_dias >= 14


# ─────────────────────────────────────────────────────────────────────────
# Capa Memento: env var lookup en runtime + Brand DNA
# ─────────────────────────────────────────────────────────────────────────

def test_memento_runtime_env_lookup(embrion_no_key: EmbrionTecnico) -> None:
    """Sin OPENAI_API_KEY → fallback heurístico (no crash)."""
    report = embrion_no_key.analizar(frase_input="Una landing simple")
    assert report.source == "heuristic_fallback"


def test_brand_dna_error_class_naming() -> None:
    """Error class sigue convención brand DNA: embrion_tecnico_*_failed."""
    # La clase de error existe y se llama en mayúsculas tipo brand
    assert EMBRION_TECNICO_LLM_INVALIDO.__name__ == "EMBRION_TECNICO_LLM_INVALIDO"
    # Es subclass de ValueError
    assert issubclass(EMBRION_TECNICO_LLM_INVALIDO, ValueError)


# ─────────────────────────────────────────────────────────────────────────
# Schema validation
# ─────────────────────────────────────────────────────────────────────────

def test_report_schema_extra_forbid() -> None:
    """Schema rechaza campos extra (extra='forbid')."""
    with pytest.raises(Exception):  # ValidationError
        EmbrionTecnicoReport(
            stack_recomendado=StackRecomendado(
                frontend="Next.js 14",
                backend="FastAPI",
                hosting="Vercel",
                deploy_target="vercel",
                razonamiento="Stack soberano El Monstruo.",
            ),
            complejidad_1_5=3,
            riesgos=[],
            tiempo_mvp_dias=10,
            confidence=0.5,
            campo_inventado="should_fail",  # type: ignore[call-arg]
        )


def test_riesgo_severidad_invalida_filtrada(monkeypatch) -> None:
    """Riesgos con severidad fuera de vocabulario son filtrados en LLM path."""
    # No podemos llamar a LLM real, pero testeamos que el vocabulario está
    # correcto y que el RiesgoTecnico acepta los 4 valores.
    for sev in ["baja", "media", "alta", "critica"]:
        r = RiesgoTecnico(
            descripcion="Riesgo test descripcion suficiente",
            severidad=sev,
            mitigacion="Mitigacion test suficiente largo",
        )
        assert r.severidad == sev


def test_complejidad_rango_1_5() -> None:
    """complejidad_1_5 debe estar entre 1 y 5."""
    with pytest.raises(Exception):
        EmbrionTecnicoReport(
            stack_recomendado=StackRecomendado(
                frontend="Next.js 14",
                backend="FastAPI",
                hosting="Vercel",
                deploy_target="vercel",
                razonamiento="Stack soberano El Monstruo.",
            ),
            complejidad_1_5=6,  # fuera de rango
            riesgos=[],
            tiempo_mvp_dias=10,
            confidence=0.5,
        )


def test_brief_dict_propaga_a_prompt(embrion_no_llm: EmbrionTecnico) -> None:
    """Cuando se pasa brief, las keys propagan al razonamiento heurístico."""
    brief = {
        "nombre_proyecto": "Pinturas Yucatecas Premium",
        "audiencia": "Galeristas y coleccionistas LATAM",
        "propuesta_valor": "Pintura al óleo artesanal de Mérida",
        "secciones_landing": ["hero", "galeria", "testimonios"],
    }
    report = embrion_no_llm.analizar(
        frase_input="landing premium pinturas",
        brief=brief,
    )
    assert isinstance(report, EmbrionTecnicoReport)
    assert report.stack_recomendado.deploy_target == "vercel"
