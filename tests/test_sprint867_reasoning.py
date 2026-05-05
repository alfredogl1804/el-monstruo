"""
Tests Sprint 86.7 — Macroárea 4 LLM Razonamiento Estructurado.

Cubre:
  - 3 sources nuevas: AIME / GPQA / MMLU-Pro (anti-gaming v1)
  - reasoning_classifier (vocabulario 13 tags + heuristic)
  - Pipeline integration (flag CATASTRO_ENABLE_REASONING + cache)
  - Anti-gaming v2 cross-area (reasoning vs coding/raz/arena)
  - E2E con persistibles + data_extra.reasoning poblado

[Hilo Manus Catastro] · Sprint 86.7 · 2026-05-05
"""
from __future__ import annotations

import asyncio
import os

import pytest

from kernel.catastro.sources import (
    AIMEFuente,
    GPQAFuente,
    MMLUProFuente,
)
from kernel.catastro.reasoning_classifier import (
    REASONING_TAGS_VOCABULARY,
    ReasoningClassification,
    ReasoningClassifier,
)
from kernel.catastro.pipeline import CatastroPipeline


# ============================================================================
# TESTS BLOQUE 1 — SOURCES (AIME / GPQA / MMLU-PRO)
# ============================================================================

class TestSourcesAIME:
    def test_aime_dry_run_returns_data(self):
        f = AIMEFuente(dry_run=True)
        snap = asyncio.run(f.fetch())
        assert snap.fuente == "aime"
        assert "data" in snap.payload
        assert len(snap.payload["data"]) >= 3

    def test_aime_extract_scores(self):
        item = {"aime_2024_score": 80.0, "aime_2025_score": 75.0}
        scores = AIMEFuente.extract_scores(item)
        assert scores["aime_2024"] == 80.0
        assert scores["aime_2025"] == 75.0

    def test_aime_anti_gaming_memorizacion_detected(self):
        # AIME 2024 mucho más alto que 2025 (>= +10) → gaming v1
        scores = {"aime_2024": 95.0, "aime_2025": 60.0}
        assert AIMEFuente.detect_gaming(scores) is True

    def test_aime_anti_gaming_clean(self):
        # Diferencia <= 10 → no gaming
        scores = {"aime_2024": 80.0, "aime_2025": 75.0}
        assert AIMEFuente.detect_gaming(scores) is False

    def test_aime_anti_gaming_2025_higher_clean(self):
        # 2025 más alto que 2024 → modelo más capaz, NO gaming
        scores = {"aime_2024": 70.0, "aime_2025": 85.0}
        assert AIMEFuente.detect_gaming(scores) is False


class TestSourcesGPQA:
    def test_gpqa_dry_run_returns_data(self):
        f = GPQAFuente(dry_run=True)
        snap = asyncio.run(f.fetch())
        assert snap.fuente == "gpqa"
        assert "data" in snap.payload
        assert len(snap.payload["data"]) >= 3

    def test_gpqa_extract_scores(self):
        item = {"gpqa_main_score": 70.0, "gpqa_diamond_score": 75.0}
        scores = GPQAFuente.extract_scores(item)
        assert scores["gpqa_main"] == 70.0
        assert scores["gpqa_diamond"] == 75.0

    def test_gpqa_anti_gaming_diamond_too_high(self):
        # Diamond >> Main (+15) → sospecha gaming
        scores = {"gpqa_main": 40.0, "gpqa_diamond": 80.0}
        assert GPQAFuente.detect_gaming(scores) is True

    def test_gpqa_anti_gaming_diamond_lower_clean(self):
        # Diamond <= Main → orden esperado, no gaming
        scores = {"gpqa_main": 75.0, "gpqa_diamond": 60.0}
        assert GPQAFuente.detect_gaming(scores) is False


class TestSourcesMMLUPro:
    def test_mmlu_pro_dry_run_returns_data(self):
        f = MMLUProFuente(dry_run=True)
        snap = asyncio.run(f.fetch())
        assert snap.fuente == "mmlu_pro"
        assert "data" in snap.payload
        assert len(snap.payload["data"]) >= 3

    def test_mmlu_pro_extract_scores(self):
        item = {"mmlu_basic_score": 80.0, "mmlu_pro_score": 65.0}
        scores = MMLUProFuente.extract_scores(item)
        assert scores["mmlu_basic"] == 80.0
        assert scores["mmlu_pro"] == 65.0

    def test_mmlu_pro_anti_gaming_pro_too_high(self):
        # Pro mucho más alto que Basic (>= +20) → sospecha
        scores = {"mmlu_basic": 50.0, "mmlu_pro": 75.0}
        assert MMLUProFuente.detect_gaming(scores) is True

    def test_mmlu_pro_anti_gaming_clean(self):
        # Basic >= Pro → orden esperado (Pro es más difícil)
        scores = {"mmlu_basic": 85.0, "mmlu_pro": 70.0}
        assert MMLUProFuente.detect_gaming(scores) is False


# ============================================================================
# TESTS BLOQUE 2 — REASONING CLASSIFIER (Heuristic + Vocabulario)
# ============================================================================

class TestReasoningClassifier:
    def test_vocabulary_size_at_least_13(self):
        assert len(REASONING_TAGS_VOCABULARY) >= 13

    def test_vocabulary_includes_anti_gaming(self):
        assert "anti-gaming-reasoning-verified" in REASONING_TAGS_VOCABULARY
        assert "reasoning-overfit-suspected" in REASONING_TAGS_VOCABULARY

    def test_classify_high_aime_returns_math_strong(self):
        c = ReasoningClassifier(use_llm=False)
        result = c.classify("test-model", {"aime": 85.0, "gpqa": 50.0, "mmlu_pro": 50.0})
        assert "math-strong" in result.tags
        assert result.primary_strength == "math-strong"

    def test_classify_high_gpqa_returns_multidominio(self):
        c = ReasoningClassifier(use_llm=False)
        result = c.classify("test-model", {"aime": 50.0, "gpqa": 80.0, "mmlu_pro": 50.0})
        assert "multidominio-strong" in result.tags

    def test_classify_gaming_no_anti_gaming_tag(self):
        c = ReasoningClassifier(use_llm=False)
        result = c.classify(
            "test-model",
            {"aime": 90.0, "gpqa": 80.0, "mmlu_pro": 70.0},
            gaming_detected=True,
        )
        assert "anti-gaming-reasoning-verified" not in result.tags

    def test_classify_clean_high_score_has_anti_gaming_tag(self):
        c = ReasoningClassifier(use_llm=False)
        result = c.classify(
            "test-model",
            {"aime": 80.0, "gpqa": 75.0, "mmlu_pro": 65.0},
            gaming_detected=False,
        )
        assert "anti-gaming-reasoning-verified" in result.tags

    def test_classify_returns_pydantic_model(self):
        c = ReasoningClassifier(use_llm=False)
        result = c.classify("test-model", {"aime": 80.0, "gpqa": 75.0, "mmlu_pro": 65.0})
        assert isinstance(result, ReasoningClassification)
        assert 0.0 <= result.confidence <= 1.0


# ============================================================================
# TESTS BLOQUE 4 — ANTI-GAMING V2 CROSS-AREA REASONING
# ============================================================================

class TestAntiGamingV2Reasoning:
    def test_overfit_reasoning_high_coding_low(self):
        """Reasoning >= 70 pero coding < 30 → overfit cross-area."""
        is_overfit, ev = ReasoningClassifier.detect_overfit_reasoning_cross_area(
            aime_score=85.0, gpqa_score=80.0, mmlu_pro_score=75.0,
            coding_score=20.0,  # bajo coding
            razonamiento_general=60.0,
            arena_rank=10,
        )
        assert is_overfit is True
        assert "reasoning_high_but_coding_low" in ev["all_reasons"]

    def test_overfit_reasoning_high_arena_rank_bad(self):
        """Reasoning >= 70 pero arena_rank > 50 → overfit cross-area."""
        is_overfit, ev = ReasoningClassifier.detect_overfit_reasoning_cross_area(
            aime_score=80.0, gpqa_score=75.0, mmlu_pro_score=70.0,
            coding_score=60.0,
            razonamiento_general=60.0,
            arena_rank=70,  # rank pobre
        )
        assert is_overfit is True
        assert "reasoning_high_but_arena_rank_low" in ev["all_reasons"]

    def test_overfit_reasoning_high_general_low(self):
        """Reasoning >= 70 pero razonamiento general < 40 → overfit cross-area."""
        is_overfit, ev = ReasoningClassifier.detect_overfit_reasoning_cross_area(
            aime_score=85.0, gpqa_score=70.0, mmlu_pro_score=70.0,
            coding_score=50.0,
            razonamiento_general=30.0,  # bajo
            arena_rank=20,
        )
        assert is_overfit is True
        assert "reasoning_high_but_general_reasoning_low" in ev["all_reasons"]

    def test_no_overfit_when_all_consistent(self):
        """Modelo sano: reasoning + coding + arena coherentes."""
        is_overfit, ev = ReasoningClassifier.detect_overfit_reasoning_cross_area(
            aime_score=80.0, gpqa_score=75.0, mmlu_pro_score=70.0,
            coding_score=65.0,
            razonamiento_general=70.0,
            arena_rank=8,
        )
        assert is_overfit is False

    def test_no_overfit_when_reasoning_below_70(self):
        """Si reasoning < 70 (no es strong), no aplica regla v2."""
        is_overfit, ev = ReasoningClassifier.detect_overfit_reasoning_cross_area(
            aime_score=60.0, gpqa_score=50.0, mmlu_pro_score=55.0,
            coding_score=10.0,
            razonamiento_general=20.0,
            arena_rank=80,
        )
        assert is_overfit is False

    def test_no_overfit_when_data_missing(self):
        """Si todos los reasoning scores son None, NO aplica regla."""
        is_overfit, ev = ReasoningClassifier.detect_overfit_reasoning_cross_area(
            aime_score=None, gpqa_score=None, mmlu_pro_score=None,
            coding_score=20.0,
            razonamiento_general=30.0,
            arena_rank=80,
        )
        assert is_overfit is False


# ============================================================================
# TESTS BLOQUE 3 — PIPELINE INTEGRATION (E2E + flag CATASTRO_ENABLE_REASONING)
# ============================================================================

class TestPipelineIntegrationReasoning:
    def setup_method(self):
        os.environ["CATASTRO_ENABLE_REASONING"] = "true"
        os.environ["CATASTRO_ENABLE_CODING"] = "true"
        os.environ["CATASTRO_SKIP_PERSIST"] = "true"

    def teardown_method(self):
        os.environ.pop("CATASTRO_ENABLE_REASONING", None)
        os.environ.pop("CATASTRO_ENABLE_CODING", None)
        os.environ.pop("CATASTRO_SKIP_PERSIST", None)

    def test_pipeline_includes_reasoning_sources_when_flag_active(self):
        p = CatastroPipeline(dry_run=True)
        nombres = {s.nombre for s in p.sources}
        assert "aime" in nombres
        assert "gpqa" in nombres
        assert "mmlu_pro" in nombres

    def test_pipeline_excludes_reasoning_sources_when_flag_off(self):
        os.environ.pop("CATASTRO_ENABLE_REASONING", None)
        p = CatastroPipeline(dry_run=True)
        nombres = {s.nombre for s in p.sources}
        assert "aime" not in nombres
        assert "gpqa" not in nombres
        assert "mmlu_pro" not in nombres

    def test_pipeline_run_e2e_populates_data_extra_reasoning(self):
        p = CatastroPipeline(dry_run=True)
        result = asyncio.run(p.run())
        # Al menos 1 modelo persistible debe tener data_extra.reasoning
        modelos_with_reasoning = [
            m for m in result.modelos_persistibles.values()
            if "reasoning" in m.get("data_extra", {})
        ]
        assert len(modelos_with_reasoning) >= 1, (
            f"Expected at least 1 model with data_extra.reasoning, "
            f"got {len(modelos_with_reasoning)}"
        )

    def test_pipeline_run_reasoning_classification_present(self):
        p = CatastroPipeline(dry_run=True)
        result = asyncio.run(p.run())
        for slug, m in result.modelos_persistibles.items():
            r = m.get("data_extra", {}).get("reasoning")
            if r and r.get("classification"):
                cls = r["classification"]
                assert "tags" in cls
                assert "primary_strength" in cls
                assert isinstance(cls["tags"], list)
                # Todos los tags están en el vocabulario controlado
                for tag in cls["tags"]:
                    assert tag in REASONING_TAGS_VOCABULARY, (
                        f"Tag '{tag}' not in vocabulary"
                    )
                return  # OK con primer modelo classificado
        # Si llegamos acá, ningún modelo classificado → fail
        pytest.fail("No model with reasoning.classification found")

    def test_pipeline_run_overfit_field_present(self):
        p = CatastroPipeline(dry_run=True)
        result = asyncio.run(p.run())
        for slug, m in result.modelos_persistibles.items():
            r = m.get("data_extra", {}).get("reasoning")
            if r:
                # Campos overfit deben existir (aunque sean False)
                assert "overfit_suspected" in r
                assert "overfit_evidence" in r
                return
        pytest.fail("No reasoning data found in any persistible")
