"""
Tests Sprint 87.1 Bloque 3 — Steps LLM reales conectados al Catastro.

Valida que:
  1. `run_llm_step` invoca CatastroRuntimeClient
  2. Sin OPENAI_API_KEY → fallback heurístico produce contenido NO trivial
  3. Schemas Pydantic para los 7 outputs son estrictos (extra='forbid')
  4. Pipeline E2E orquestrador integra Embriones reales en VENTAS/TECNICO
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from kernel.e2e.steps.llm_step import (
    StepBrandingOutput,
    StepConceptOutput,
    StepCopyOutput,
    StepEstrategiaOutput,
    StepFinanzasOutput,
    StepICPOutput,
    StepNamingOutput,
    run_llm_step,
)


# ─────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────

@pytest.fixture
def cat_mock():
    """Mock de CatastroRuntimeClient con select_model_for_step async."""
    mock = MagicMock()
    mock.select_model_for_step = AsyncMock(
        return_value={
            "model_id": "gemini-3-1-flash-lite-preview",
            "model_label": "gemini-3-1-flash-lite-preview",
            "source": "catastro",
            "degraded": False,
        }
    )
    return mock


@pytest.fixture(autouse=True)
def no_openai(monkeypatch):
    """Default: sin OPENAI_API_KEY → fallback heurístico."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


# ─────────────────────────────────────────────────────────────────────────
# Test 1: run_llm_step con fallback heurístico produce contenido válido
# ─────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_llm_step_concept_fallback(cat_mock) -> None:
    result = await run_llm_step(
        cat=cat_mock,
        step_name="INVESTIGAR",
        schema=StepConceptOutput,
        system_prompt="test",
        user_prompt="test",
        context={"frase_input": "Hacé una landing premium artesanal en Mérida"},
    )
    assert result["source"] == "heuristic_fallback"
    assert result["modelo_elegido"]["model_id"] == "gemini-3-1-flash-lite-preview"
    payload = result["output_payload"]
    assert "concepto_central" in payload
    assert len(payload["concepto_central"]) >= 15
    assert "keywords_seo" in payload
    assert len(payload["keywords_seo"]) >= 3


@pytest.mark.asyncio
async def test_run_llm_step_copy_fallback(cat_mock) -> None:
    result = await run_llm_step(
        cat=cat_mock,
        step_name="VENTAS",
        schema=StepCopyOutput,
        system_prompt="test",
        user_prompt="test",
        context={"frase_input": "landing premium"},
    )
    payload = result["output_payload"]
    # body_copy debe ser >50 palabras (validación de no trivialidad)
    assert len(payload["body_copy"].split()) >= 30
    assert payload["hero_headline"]
    assert payload["cta_primary"]


@pytest.mark.asyncio
async def test_run_llm_step_branding_fallback(cat_mock) -> None:
    result = await run_llm_step(
        cat=cat_mock,
        step_name="CREATIVO",
        schema=StepBrandingOutput,
        system_prompt="test",
        user_prompt="test",
        context={"nombre_proyecto": "Atelier Yucateca"},
    )
    payload = result["output_payload"]
    assert "Atelier Yucateca" in payload["elevator_pitch"]
    assert len(payload["colores_primarios"]) >= 1


# ─────────────────────────────────────────────────────────────────────────
# Test 2: schemas estrictos extra='forbid'
# ─────────────────────────────────────────────────────────────────────────

def test_schemas_extra_forbid() -> None:
    """Todos los schemas Pydantic rechazan campos extra."""
    schemas = [
        StepConceptOutput,
        StepICPOutput,
        StepNamingOutput,
        StepBrandingOutput,
        StepCopyOutput,
        StepEstrategiaOutput,
        StepFinanzasOutput,
    ]
    for schema in schemas:
        assert schema.model_config.get("extra") == "forbid", (
            f"{schema.__name__} debe tener extra='forbid'"
        )


# ─────────────────────────────────────────────────────────────────────────
# Test 3: latency_ms y model_used están presentes
# ─────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_llm_step_metadata(cat_mock) -> None:
    result = await run_llm_step(
        cat=cat_mock,
        step_name="ESTRATEGIA",
        schema=StepEstrategiaOutput,
        system_prompt="test",
        user_prompt="test",
        context={"frase_input": "landing premium"},
    )
    assert "latency_ms" in result
    assert isinstance(result["latency_ms"], int)
    assert result["latency_ms"] >= 0
    assert result["model_used"] == "heuristic"


# ─────────────────────────────────────────────────────────────────────────
# Test 4: Pipeline integra Embriones reales en VENTAS y TECNICO
# ─────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_step_llm_generic_invoca_embrion_ventas(cat_mock) -> None:
    from kernel.e2e.pipeline import _step_llm_generic

    payload_in = {
        "frase_input": "Hacé una landing premium para vender pintura al óleo artesanal hecha en Mérida",
        "architect": {"brief": {"nombre_proyecto": "Atelier Yucateca"}},
    }
    out = await _step_llm_generic(cat_mock, "VENTAS", payload_in)
    assert out["embrion"] == "embrion_ventas_real"
    assert out["source"] in ("heuristic_fallback", "llm_openai")
    payload = out["output_payload"]
    assert "icp_refinado" in payload
    assert "propuesta_valor" in payload
    assert "canales_adquisicion" in payload


@pytest.mark.asyncio
async def test_pipeline_step_llm_generic_invoca_embrion_tecnico(cat_mock) -> None:
    from kernel.e2e.pipeline import _step_llm_generic

    payload_in = {
        "frase_input": "Hacé una landing premium para vender pintura al óleo",
        "architect": {"brief": {"nombre_proyecto": "Atelier Yucateca"}},
    }
    out = await _step_llm_generic(cat_mock, "TECNICO", payload_in)
    assert out["embrion"] == "embrion_tecnico_real"
    payload = out["output_payload"]
    assert "stack_recomendado" in payload
    assert "complejidad_1_5" in payload


@pytest.mark.asyncio
async def test_pipeline_step_llm_generic_estrategia_real(cat_mock) -> None:
    from kernel.e2e.pipeline import _step_llm_generic

    payload_in = {
        "frase_input": "landing premium artesanal",
        "architect": {"brief": {"nombre_proyecto": "Atelier"}},
    }
    out = await _step_llm_generic(cat_mock, "ESTRATEGIA", payload_in)
    assert "output_payload" in out
    assert "stack_decision" in out["output_payload"]
    assert "kpis" in out["output_payload"]
    # Ya NO es stub
    assert "v1.0 stub" not in str(out.get("output_payload", {}))


@pytest.mark.asyncio
async def test_pipeline_step_unknown_fallback_defensive(cat_mock) -> None:
    """Step desconocido cae en fallback defensivo sin crash."""
    from kernel.e2e.pipeline import _step_llm_generic

    out = await _step_llm_generic(cat_mock, "FOOBAR_NO_EXISTE", {})
    assert out["source"] == "unknown_step"
