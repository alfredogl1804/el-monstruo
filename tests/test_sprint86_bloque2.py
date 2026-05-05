"""
Tests Sprint 86 Bloque 2 — Pipeline diario + Quorum + Sources.

Cobertura mínima firmada por Cowork: 80% líneas + 4 casos límite.

Casos límite obligatorios:
  L1. 1 fuente cae → quorum 2-de-3 con las otras 2 sigue funcionando
  L2. 2 fuentes caen → run degradado, no persiste nada
  L3. 3 fuentes responden con valores discrepantes → quorum_failed
  L4. Modelo aparece en 3 fuentes con valores cercanos → quorum_unanimous

Convenciones:
  - Tests offline: NO ejecutan red. Usan dry_run=True o monkey-patch.
  - Marker `pytest.mark.asyncio` para tests async.
  - Imports absolutos desde kernel.catastro.

[Hilo Manus Catastro] · Sprint 86 Bloque 2 · 2026-05-04
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

import pytest

from kernel.catastro.pipeline import CatastroPipeline, PipelineRunResult
from kernel.catastro.quorum import (
    FieldType,
    FuenteVote,
    QuorumOutcome,
    QuorumResult,
    QuorumValidator,
)
from kernel.catastro.sources import (
    ArtificialAnalysisFuente,
    BaseFuente,
    FuenteError,
    FuenteRateLimitError,
    FuenteTimeoutError,
    FuenteUnauthorizedError,
    FuenteUnavailableError,
    LMArenaFuente,
    OpenRouterFuente,
    RawSnapshot,
)


# ============================================================================
# QUORUM VALIDATOR
# ============================================================================

class TestQuorumValidator:
    """Tests del Quorum Validator (corazón del Bloque 2)."""

    def test_unanimous_numeric(self):
        v = QuorumValidator()
        r = v.validate(
            field_name="quality",
            field_type=FieldType.NUMERIC,
            votes=[
                FuenteVote("artificial_analysis", 87.4),
                FuenteVote("openrouter", 88.0),
                FuenteVote("lmarena", 86.5),
            ],
        )
        assert r.outcome == QuorumOutcome.QUORUM_UNANIMOUS
        assert r.is_persistable is True
        assert r.confidence_score == 1.0

    def test_quorum_reached_with_outlier(self):
        v = QuorumValidator()
        r = v.validate(
            field_name="quality",
            field_type=FieldType.NUMERIC,
            votes=[
                FuenteVote("artificial_analysis", 87.0),
                FuenteVote("openrouter", 88.0),
                FuenteVote("lmarena", 50.0),
            ],
        )
        assert r.outcome == QuorumOutcome.QUORUM_REACHED
        assert r.is_persistable is True
        assert "lmarena" in r.dissenting_sources

    def test_insufficient_data(self):
        v = QuorumValidator()
        r = v.validate(
            field_name="quality",
            field_type=FieldType.NUMERIC,
            votes=[
                FuenteVote("artificial_analysis", 87.0),
                FuenteVote("openrouter", None),
                FuenteVote("lmarena", None),
            ],
        )
        assert r.outcome == QuorumOutcome.INSUFFICIENT_DATA
        assert r.is_persistable is False

    def test_quorum_failed_three_discrepant(self):
        """L3: 3 fuentes responden con valores totalmente discrepantes."""
        v = QuorumValidator()
        r = v.validate(
            field_name="quality",
            field_type=FieldType.NUMERIC,
            votes=[
                FuenteVote("artificial_analysis", 30.0),
                FuenteVote("openrouter", 60.0),
                FuenteVote("lmarena", 90.0),
            ],
        )
        assert r.outcome == QuorumOutcome.QUORUM_FAILED
        assert r.is_persistable is False

    def test_categorical_normalization(self):
        v = QuorumValidator()
        r = v.validate(
            field_name="license",
            field_type=FieldType.CATEGORICAL,
            votes=[
                FuenteVote("artificial_analysis", "Proprietary"),
                FuenteVote("openrouter", "proprietary"),
                FuenteVote("lmarena", "PROPRIETARY"),
            ],
        )
        assert r.outcome == QuorumOutcome.QUORUM_UNANIMOUS
        assert str(r.consensus_value).lower() == "proprietary"

    def test_presence_quorum(self):
        v = QuorumValidator()
        r = v.validate(
            field_name="presence",
            field_type=FieldType.PRESENCE,
            votes=[
                FuenteVote("artificial_analysis", True),
                FuenteVote("openrouter", True),
                FuenteVote("lmarena", None),
            ],
        )
        assert r.outcome == QuorumOutcome.QUORUM_REACHED
        assert r.consensus_value is True

    def test_trust_deltas_asymmetric(self):
        v = QuorumValidator()
        r = v.validate(
            field_name="quality",
            field_type=FieldType.NUMERIC,
            votes=[
                FuenteVote("artificial_analysis", 87.0),
                FuenteVote("openrouter", 88.0),
                FuenteVote("lmarena", 50.0),
            ],
        )
        deltas = v.compute_trust_deltas([r])
        assert deltas["lmarena"] < 0
        assert deltas["artificial_analysis"] == 0.0
        assert deltas["openrouter"] == 0.0

    def test_trust_deltas_per_source_floor_caps_explosive_penalty(self):
        """Cowork audit B7: lmarena disintió 6 veces y llegó a -0.30; con
        50 disensos llegaría a -2.50 sin cap. El floor por defecto debe
        capar a -0.30."""
        v = QuorumValidator()
        # Construir 50 resultados donde lmarena disiente sistemáticamente
        results = []
        for _ in range(50):
            r = v.validate(
                field_name="quality",
                field_type=FieldType.NUMERIC,
                votes=[
                    FuenteVote("artificial_analysis", 87.0),
                    FuenteVote("openrouter", 88.0),
                    FuenteVote("lmarena", 50.0),
                ],
            )
            results.append(r)
        deltas = v.compute_trust_deltas(results)
        # Sin cap sería -0.05 * 50 = -2.50; el floor por defecto -0.30 debe limitar
        assert deltas["lmarena"] == -0.30

    def test_trust_deltas_per_source_floor_disabled_legacy_behavior(self):
        """Pasando per_source_floor=None se preserva el comportamiento
        legacy (sin cap), por compatibilidad y testing."""
        v = QuorumValidator()
        results = []
        for _ in range(10):
            r = v.validate(
                field_name="quality",
                field_type=FieldType.NUMERIC,
                votes=[
                    FuenteVote("artificial_analysis", 87.0),
                    FuenteVote("openrouter", 88.0),
                    FuenteVote("lmarena", 50.0),
                ],
            )
            results.append(r)
        deltas = v.compute_trust_deltas(
            results, per_source_floor=None, per_source_ceiling=None
        )
        # 10 disensos * -0.05 = -0.50, no capado
        assert deltas["lmarena"] == pytest.approx(-0.50)


# ============================================================================
# SOURCES
# ============================================================================

class TestSources:

    @pytest.mark.asyncio
    async def test_artificial_analysis_dry_run(self):
        f = ArtificialAnalysisFuente(dry_run=True)
        snap = await f.fetch()
        assert snap.fuente == "artificial_analysis"
        assert "data" in snap.payload
        assert snap.payload_hash

    @pytest.mark.asyncio
    async def test_openrouter_dry_run(self):
        f = OpenRouterFuente(dry_run=True)
        snap = await f.fetch()
        assert snap.fuente == "openrouter"
        assert "data" in snap.payload

    @pytest.mark.asyncio
    async def test_lmarena_dry_run(self):
        f = LMArenaFuente(dry_run=True)
        snap = await f.fetch()
        assert snap.fuente == "lmarena"
        assert "rows" in snap.payload

    def test_aa_extract_quality_score(self):
        item = {"evaluations": {"intelligence_index": 87.4}}
        assert ArtificialAnalysisFuente.extract_quality_score(item) == 87.4

    def test_aa_extract_pricing(self):
        item = {"pricing": {"price_1m_input_tokens": 3.0, "price_1m_output_tokens": 15.0}}
        p = ArtificialAnalysisFuente.extract_pricing(item)
        assert p["input_per_million"] == 3.0
        assert p["output_per_million"] == 15.0

    def test_lmarena_extract_arena_score(self):
        row = {"rating": 1395.5}
        assert LMArenaFuente.extract_arena_score(row) == 1395.5


# ============================================================================
# PIPELINE
# ============================================================================

class TestPipeline:

    @pytest.mark.asyncio
    async def test_pipeline_dry_run_e2e(self):
        pipeline = CatastroPipeline(dry_run=True)
        result = await pipeline.run()
        assert result.is_success is True
        assert len(result.snapshots) >= 2
        assert result.duration_seconds is not None

    @pytest.mark.asyncio
    async def test_pipeline_one_source_down(self):
        """L1: 1 fuente cae, quorum sigue posible con las otras 2."""

        class FailingSource(BaseFuente):
            nombre = "broken_source"
            tipo = "test"

            async def fetch(self):
                raise FuenteError("simulated failure")

        sources = [
            ArtificialAnalysisFuente(dry_run=True),
            OpenRouterFuente(dry_run=True),
            FailingSource(),
        ]
        pipeline = CatastroPipeline(sources=sources, dry_run=True)
        result = await pipeline.run()
        assert result.is_success is True
        assert "broken_source" in result.fuente_errors
        assert len(result.snapshots) == 2

    @pytest.mark.asyncio
    async def test_pipeline_two_sources_down(self):
        """L2: 2 fuentes caen, run degradado."""

        class FailingSource(BaseFuente):
            def __init__(self, nombre: str):
                self.nombre = nombre
                self.tipo = "test"

            async def fetch(self):
                raise FuenteError(f"{self.nombre} simulated failure")

        sources = [
            ArtificialAnalysisFuente(dry_run=True),
            FailingSource("broken_a"),
            FailingSource("broken_b"),
        ]
        pipeline = CatastroPipeline(sources=sources, dry_run=True)
        result = await pipeline.run()
        assert result.is_success is False
        assert len(result.snapshots) == 1
        assert len(result.fuente_errors) == 2
        assert len(result.modelos_persistibles) == 0

    def test_normalize_slug(self):
        assert CatastroPipeline.normalize_slug("claude-opus-4.7") == "claude-opus-4-7"
        assert CatastroPipeline.normalize_slug("anthropic/claude-opus-4.7") == "anthropic-claude-opus-4-7"
        assert CatastroPipeline.normalize_slug("Claude_Opus_4.7") == "claude-opus-4-7"

    @pytest.mark.asyncio
    async def test_pipeline_summary_serializable(self):
        import json
        pipeline = CatastroPipeline(dry_run=True)
        result = await pipeline.run()
        summary = result.summary()
        json_str = json.dumps(summary, default=str)
        assert "run_id" in json_str


# ============================================================================
# CRON
# ============================================================================

class TestCron:

    def test_check_env_no_secrets(self, monkeypatch):
        from kernel.catastro.cron import _check_env
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
        monkeypatch.delenv("ARTIFICIAL_ANALYSIS_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        monkeypatch.delenv("HF_TOKEN", raising=False)

        status = _check_env()
        assert "SUPABASE_URL" in status["required_missing"]

    def test_check_env_with_secrets(self, monkeypatch):
        from kernel.catastro.cron import _check_env
        monkeypatch.setenv("SUPABASE_URL", "https://x.supabase.co")
        monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "eyJ...")
        monkeypatch.setenv("ARTIFICIAL_ANALYSIS_API_KEY", "sk-aa-...")

        status = _check_env()
        assert status["required_missing"] == []
        assert status["recommended_missing"] == []

    def test_cron_main_dry_run(self, monkeypatch, capsys):
        from kernel.catastro.cron import main
        monkeypatch.setenv("CATASTRO_DRY_RUN", "true")
        monkeypatch.setenv("CATASTRO_LOG_LEVEL", "WARNING")

        exit_code = main()
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "catastro_pipeline_summary" in captured.out


# ============================================================================
# DISCIPLINA OS.ENVIRON
# ============================================================================

class TestDisciplinaOsEnviron:
    """Verifica que NO hay os.environ a nivel módulo."""

    def test_no_module_level_env_caching(self):
        import ast
        files_to_check = [
            "kernel/catastro/pipeline.py",
            "kernel/catastro/cron.py",
            "kernel/catastro/sources/base.py",
            "kernel/catastro/sources/artificial_analysis.py",
            "kernel/catastro/sources/openrouter.py",
            "kernel/catastro/sources/lmarena.py",
            "kernel/catastro/quorum.py",
        ]
        for path in files_to_check:
            with open(path) as f:
                tree = ast.parse(f.read())
            for node in tree.body:
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    code = ast.unparse(node) if hasattr(ast, "unparse") else ""
                    assert "os.environ" not in code, (
                        f"DISCIPLINA VIOLADA en {path}: "
                        f"os.environ a nivel módulo: {code[:120]}"
                    )
