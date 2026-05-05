"""
Test suite Sprint 86.5 — Catastro Macroárea 3 LLM Coding.

Coverage:
  1. SWEBenchFuente: extract_scores, detect_gaming UC Berkeley
  2. HumanEvalFuente: extract_score, dry_run shape
  3. MBPPFuente: extract_score, dry_run shape
  4. CodingClassifier: heuristic mode, vocabulario controlado, gaming flag
  5. CatastroPipeline integration: cross_validate_coding + enrich_with_coding
  6. Anti-gaming UC Berkeley end-to-end (Overfit Coder detectado)

[Hilo Manus Catastro] · Sprint 86.5 · 2026-05-05
"""
from __future__ import annotations

import asyncio
import os

import pytest

from kernel.catastro.coding_classifier import (
    CODING_TAGS_VOCABULARY,
    CodingClassification,
    CodingClassifier,
)
from kernel.catastro.pipeline import CatastroPipeline
from kernel.catastro.sources import (
    HumanEvalFuente,
    MBPPFuente,
    SWEBenchFuente,
)


# ============================================================================
# 1. SWE-BENCH FUENTE
# ============================================================================

class TestSWEBenchFuente:
    """Tests para SWEBenchFuente y su detector de gaming."""

    def test_nombre_y_env_key(self):
        f = SWEBenchFuente(dry_run=True)
        assert f.nombre == "swe_bench"
        assert f.env_key is None  # API pública

    def test_extract_scores_completo(self):
        item = {
            "verified_score": 50.8,
            "lite_score": 53.0,
            "multilingual_python_score": 48.5,
        }
        scores = SWEBenchFuente.extract_scores(item)
        assert scores == {"verified": 50.8, "lite": 53.0, "multilingual_python": 48.5}

    def test_extract_scores_parcial(self):
        item = {"verified_score": 40.0}
        scores = SWEBenchFuente.extract_scores(item)
        assert scores == {"verified": 40.0}
        assert "lite" not in scores

    def test_detect_gaming_clean(self):
        """Modelo limpio: Verified < Lite, Verified <= Multi.python + 10."""
        scores = {"verified": 50.8, "lite": 53.0, "multilingual_python": 48.5}
        assert SWEBenchFuente.detect_gaming(scores) is False

    def test_detect_gaming_verified_gt_lite(self):
        """Caso UC Berkeley: Verified > Lite => gaming."""
        scores = {"verified": 48.0, "lite": 35.0}
        assert SWEBenchFuente.detect_gaming(scores) is True

    def test_detect_gaming_verified_gt_multilingual(self):
        """Caso UC Berkeley: Verified > Multi.python + 10 => gaming."""
        scores = {"verified": 48.0, "multilingual_python": 30.0}
        assert SWEBenchFuente.detect_gaming(scores) is True

    def test_detect_gaming_no_verified(self):
        scores = {"lite": 50.0}
        assert SWEBenchFuente.detect_gaming(scores) is False

    def test_dry_run_payload_shape(self):
        f = SWEBenchFuente(dry_run=True)
        snapshot = asyncio.run(f.fetch())
        assert snapshot.fuente == "swe_bench"
        assert "data" in snapshot.payload
        assert len(snapshot.payload["data"]) >= 2
        assert snapshot.metadata.get("dry_run") is True

    def test_dry_run_contains_overfit_coder(self):
        """Dry run debe contener un caso conocido de gaming para integration tests."""
        f = SWEBenchFuente(dry_run=True)
        snapshot = asyncio.run(f.fetch())
        ids = [item["model_id"] for item in snapshot.payload["data"]]
        assert "overfit-coder-v1" in ids


# ============================================================================
# 2. HUMAN EVAL FUENTE
# ============================================================================

class TestHumanEvalFuente:
    def test_nombre_y_env_key(self):
        f = HumanEvalFuente(dry_run=True)
        assert f.nombre == "human_eval"
        assert f.env_key is None

    def test_extract_score(self):
        assert HumanEvalFuente.extract_score({"pass_at_1": 88.4}) == 88.4
        assert HumanEvalFuente.extract_score({}) is None

    def test_dry_run_shape(self):
        f = HumanEvalFuente(dry_run=True)
        snapshot = asyncio.run(f.fetch())
        assert "data" in snapshot.payload


# ============================================================================
# 3. MBPP FUENTE
# ============================================================================

class TestMBPPFuente:
    def test_nombre_y_env_key(self):
        f = MBPPFuente(dry_run=True)
        assert f.nombre == "mbpp"
        assert f.env_key is None

    def test_extract_score(self):
        assert MBPPFuente.extract_score({"pass_at_1": 89.5}) == 89.5
        assert MBPPFuente.extract_score({}) is None


# ============================================================================
# 4. CODING CLASSIFIER
# ============================================================================

class TestCodingClassifier:
    def test_vocabulario_15_tags(self):
        # Sprint 86.5 entregó 15 tags; Sprint 86.6 extiende a 16
        # con 'coding-overfit-suspected'. Mantener test compatible con
        # ambos históricos.
        assert len(CODING_TAGS_VOCABULARY) >= 15

    def test_heuristic_mode_alto_score(self):
        """Heuristic mode con scores altos debe asignar tags adecuados."""
        classifier = CodingClassifier(use_llm=False)
        result = classifier.classify(
            modelo_id="test-claude-sonnet",
            scores={"swe_bench": 50.8, "human_eval": 88.4, "mbpp": 89.5},
            gaming_detected=False,
        )
        assert isinstance(result, CodingClassification)
        assert "agentic-coding" in result.tags
        assert "python-strong" in result.tags
        assert "anti-gaming-verified" in result.tags  # gaming False, swe>=50

    def test_heuristic_mode_gaming_no_anti_gaming_tag(self):
        """Si gaming detectado, no debe asignar 'anti-gaming-verified'."""
        classifier = CodingClassifier(use_llm=False)
        result = classifier.classify(
            modelo_id="overfit-coder-v1",
            scores={"swe_bench": 48.0, "human_eval": 95.0, "mbpp": 94.0},
            gaming_detected=True,
        )
        assert "anti-gaming-verified" not in result.tags

    def test_heuristic_mode_low_scores(self):
        """Scores bajos: tags mínimos pero no vacíos."""
        classifier = CodingClassifier(use_llm=False)
        result = classifier.classify(
            modelo_id="weak-coder",
            scores={"swe_bench": 10.0, "human_eval": 50.0, "mbpp": 45.0},
            gaming_detected=False,
        )
        assert len(result.tags) >= 1
        assert result.confidence == 0.5  # heuristic = baja confianza

    def test_tags_validados_contra_vocabulario(self):
        """Heuristic mode siempre genera tags del vocabulario controlado."""
        classifier = CodingClassifier(use_llm=False)
        result = classifier.classify(
            modelo_id="test",
            scores={"swe_bench": 60.0, "human_eval": 95.0, "mbpp": 92.0},
            gaming_detected=False,
        )
        for tag in result.tags:
            assert tag in CODING_TAGS_VOCABULARY, f"Tag inválido: {tag}"


# ============================================================================
# 5. PIPELINE INTEGRATION (dry-run, sin red)
# ============================================================================

class TestPipelineCodingIntegration:
    def test_pipeline_coding_disabled_por_default(self):
        """Sin CATASTRO_ENABLE_CODING, las 3 fuentes coding no entran."""
        os.environ.pop("CATASTRO_ENABLE_CODING", None)
        pipeline = CatastroPipeline(dry_run=True, skip_persist=True)
        nombres = [s.nombre for s in pipeline.sources]
        assert "swe_bench" not in nombres
        assert "human_eval" not in nombres
        assert "mbpp" not in nombres

    def test_pipeline_coding_enabled_con_flag(self):
        """Con CATASTRO_ENABLE_CODING=true, las 3 fuentes coding entran."""
        os.environ["CATASTRO_ENABLE_CODING"] = "true"
        try:
            pipeline = CatastroPipeline(dry_run=True, skip_persist=True)
            nombres = [s.nombre for s in pipeline.sources]
            assert "swe_bench" in nombres
            assert "human_eval" in nombres
            assert "mbpp" in nombres
        finally:
            os.environ.pop("CATASTRO_ENABLE_CODING", None)


# ============================================================================
# 6. INTEGRATION TEST E2E ANTI-GAMING UC BERKELEY
# ============================================================================

class TestE2EAntiGaming:
    def test_e2e_overfit_coder_detectado(self):
        """
        E2E: pipeline dry-run con coding habilitado debe detectar al
        Overfit Coder (Verified > Lite) como gaming en data_extra.coding.
        """
        os.environ["CATASTRO_ENABLE_CODING"] = "true"
        try:
            pipeline = CatastroPipeline(dry_run=True, skip_persist=True)
            result = asyncio.run(pipeline.run())

            # Verificar que el smoke pipeline corrió sin crash
            assert result.is_success
            
            # Verificar que el cache de coding tiene entries
            assert hasattr(pipeline, "_coding_cache")
            cache = pipeline._coding_cache
            assert "overfit-coder-v1" in cache, f"Slugs en cache: {list(cache.keys())}"
            
            overfit = cache["overfit-coder-v1"]
            assert overfit.get("gaming_detected") is True, \
                f"Gaming NO detectado en overfit-coder-v1: {overfit}"

            # Caso clean: Claude 3.5 Sonnet no debería tener gaming
            claude_slug = "claude-3-5-sonnet-20241022"
            assert claude_slug in cache
            assert cache[claude_slug].get("gaming_detected") is False
        finally:
            os.environ.pop("CATASTRO_ENABLE_CODING", None)
