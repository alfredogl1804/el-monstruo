"""
Tests del Sprint 86.6 — Visión Quorum 2-de-3 anti-gaming v2 cross-macroárea.

Cobertura:
- detect_overfit_cross_area: 5+ casos sintéticos
  * 3 sanos (no overfit)
  * 1 intra-SWE gaming (UC Berkeley v1, NO debería disparar v2)
  * 1 cross-area overfit (SWE alto pero razonamiento bajo)
  * 1 cross-area overfit (SWE alto pero arena rank bajo)
- Vocabulario incluye coding-overfit-suspected (16 tags)
- Pipeline E2E con flag enable_coding inyecta data_extra.coding.overfit_*

[Hilo Manus Catastro] · Sprint 86.6 · 2026-05-05
"""
from __future__ import annotations

import os
import pytest

from kernel.catastro.coding_classifier import (
    CodingClassifier,
    CODING_TAGS_VOCABULARY,
)


# ============================================================================
# Vocabulario extendido (16 tags)
# ============================================================================

class TestVocabularyExtension:
    def test_vocabulary_has_16_tags(self):
        assert len(CODING_TAGS_VOCABULARY) == 16

    def test_coding_overfit_suspected_present(self):
        assert "coding-overfit-suspected" in CODING_TAGS_VOCABULARY

    def test_anti_gaming_verified_still_present(self):
        # No regresión sobre Sprint 86.5
        assert "anti-gaming-verified" in CODING_TAGS_VOCABULARY


# ============================================================================
# detect_overfit_cross_area — casos sintéticos
# ============================================================================

class TestDetectOverfitCrossArea:
    def test_sano_cross_area_aligned(self):
        """Modelo top en coding, razonamiento y arena — SIN overfit."""
        is_overfit, ev = CodingClassifier.detect_overfit_cross_area(
            swe_score=68.0,
            razonamiento_score=85.0,
            arena_rank=3,
        )
        assert is_overfit is False
        assert ev["swe_bench"] == 68.0
        assert "reason" not in ev

    def test_sano_swe_below_threshold(self):
        """Modelo coding débil — no califica como coding-strong, regla no dispara."""
        is_overfit, ev = CodingClassifier.detect_overfit_cross_area(
            swe_score=45.0,
            razonamiento_score=30.0,  # razonamiento bajo pero SWE no es alto
            arena_rank=80,
        )
        assert is_overfit is False
        assert "reason" not in ev

    def test_sano_swe_borderline_60(self):
        """SWE = 60.0 (threshold exacto), razonamiento OK, arena OK — sano."""
        is_overfit, ev = CodingClassifier.detect_overfit_cross_area(
            swe_score=60.0,
            razonamiento_score=70.0,
            arena_rank=20,
        )
        assert is_overfit is False

    def test_intra_swe_gaming_no_dispara_cross_area(self):
        """
        Modelo con gaming intra-SWE (Verified > Lite, detectado por v1)
        pero scores cross-area altos. v2 NO debe disparar — son detecciones
        ortogonales.
        """
        # Aunque internamente gaming_detected=True (UC Berkeley v1),
        # detect_overfit_cross_area solo mira swe vs razonamiento/arena.
        is_overfit, ev = CodingClassifier.detect_overfit_cross_area(
            swe_score=65.0,  # Inflado por gaming intra-SWE
            razonamiento_score=78.0,  # Razonamiento sano
            arena_rank=8,  # Arena sano
        )
        assert is_overfit is False  # v2 no se entromete con v1

    def test_overfit_cross_area_reasoning_low(self):
        """Modelo SWE-strong pero razonamiento general débil → overfit."""
        is_overfit, ev = CodingClassifier.detect_overfit_cross_area(
            swe_score=72.0,
            razonamiento_score=42.0,  # < 50 trigger
            arena_rank=10,
        )
        assert is_overfit is True
        assert ev["reason"] == "swe_high_but_reasoning_low"
        assert ev["swe_bench"] == 72.0
        assert ev["razonamiento"] == 42.0

    def test_overfit_cross_area_arena_rank_low(self):
        """SWE-strong pero arena rank bajo → overfit."""
        is_overfit, ev = CodingClassifier.detect_overfit_cross_area(
            swe_score=68.0,
            razonamiento_score=None,  # no tenemos AA data
            arena_rank=45,  # > 30 trigger
        )
        assert is_overfit is True
        assert ev["reason"] == "swe_high_but_arena_rank_low"
        assert ev["arena_rank"] == 45

    def test_evidence_complete_when_overfit_false(self):
        """Evidence siempre incluye los 3 inputs aunque no haya overfit."""
        is_overfit, ev = CodingClassifier.detect_overfit_cross_area(
            swe_score=55.0,
            razonamiento_score=65.0,
            arena_rank=15,
        )
        assert is_overfit is False
        assert "swe_bench" in ev
        assert "razonamiento" in ev
        assert "arena_rank" in ev

    def test_swe_none_returns_false(self):
        """Sin score SWE no se puede evaluar — defensa Memento."""
        is_overfit, ev = CodingClassifier.detect_overfit_cross_area(
            swe_score=None,
            razonamiento_score=20.0,
            arena_rank=99,
        )
        assert is_overfit is False


# ============================================================================
# Pipeline E2E con cross-area injection
# ============================================================================

@pytest.mark.asyncio
class TestPipelineCrossAreaInjection:
    async def test_pipeline_inject_overfit_evidence_dry_run(self, monkeypatch):
        """
        Pipeline E2E con CATASTRO_ENABLE_CODING=true:
        gpt-5-5 y claude-opus-4-7 deben tener data_extra.coding.overfit_evidence
        poblado tras pasar por _enrich_with_coding.
        """
        monkeypatch.setenv("CATASTRO_ENABLE_CODING", "true")
        monkeypatch.setenv("CATASTRO_SKIP_PERSIST", "true")

        from kernel.catastro.pipeline import CatastroPipeline

        pipeline = CatastroPipeline(dry_run=True)
        result = await pipeline.run()

        assert result.is_success
        # Al menos un modelo persistible con coding enriquecido y overfit_evidence
        with_overfit_evidence = [
            slug
            for slug, p in result.modelos_persistibles.items()
            if "data_extra" in p
            and "coding" in p["data_extra"]
            and "overfit_evidence" in p["data_extra"]["coding"]
        ]
        assert len(with_overfit_evidence) >= 1, (
            f"Esperado >=1 persistible con overfit_evidence, encontrados: "
            f"{with_overfit_evidence}"
        )

    async def test_pipeline_overfit_flag_persisted(self, monkeypatch):
        """Verifica que overfit_suspected (bool) se persiste correctamente."""
        monkeypatch.setenv("CATASTRO_ENABLE_CODING", "true")
        monkeypatch.setenv("CATASTRO_SKIP_PERSIST", "true")

        from kernel.catastro.pipeline import CatastroPipeline

        pipeline = CatastroPipeline(dry_run=True)
        result = await pipeline.run()

        for slug, p in result.modelos_persistibles.items():
            coding = p.get("data_extra", {}).get("coding")
            if coding:
                # Sprint 86.6 contract: overfit_suspected siempre presente
                assert "overfit_suspected" in coding
                assert isinstance(coding["overfit_suspected"], bool)
