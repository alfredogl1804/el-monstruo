"""
Brand Engine integration tests (Sprint PAR_BICEFALO_001 PR-B).

55 tests organizados en 4 categorias:
- Mock dimensions (15) — patch evaluar_dimension_via_sabio
- Brand Engine end-to-end mocked (15) — patch _evaluate_all_dimensions
- Hook embrion_loop simulation (10) — verifica flag + fail-open
- Replay corpus (15) — corpus deterministico para pre-filtro anti-corp

Todos los tests usan mocks/patches — NO golpean APIs reales.
Test live con APIs reales esta en test_brand_engine_live_smoke.py
(skip por default, requiere BRAND_ENGINE_LIVE=1).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# sys.path setup canonico del repo
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from kernel.embriones.brand_engine.brand_engine import (  # noqa: E402
    BrandEngine,
    ValidationVerdict,
)
from kernel.embriones.brand_engine.config_loader import (  # noqa: E402
    BrandEngineConfig,
    DimensionConfig,
    DimensionesConfig,
    apply_env_overrides,
    load_brand_engine_config,
)
from kernel.embriones.brand_engine.dimensions import (  # noqa: E402
    BaseSabioDimension,
    DimensionEvaluator,
    DimensionResult,
)
from kernel.embriones.brand_engine.dimensions.apple_tesla import AppleTeslaEvaluator  # noqa: E402
from kernel.embriones.brand_engine.dimensions.brand_tono import BrandTonoEvaluator  # noqa: E402
from kernel.embriones.brand_engine.dimensions.doctrina import DoctrinaEvaluator  # noqa: E402
from kernel.embriones.brand_engine.dimensions.honestidad import HonestidadEvaluator  # noqa: E402
from kernel.embriones.brand_engine.sabio_evaluator import SabioEvaluation  # noqa: E402

# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────


def _make_config(
    mode: str = "shadow",
    enabled: bool = True,
    umbral: float = 0.7,
    budget_kill_switch: float = 12.0,
) -> BrandEngineConfig:
    """Construye config minima reutilizable alineada al schema real."""
    dim_cfg = DimensionConfig(
        enabled=True,
        umbral_pass=umbral,
        criterios=["criterio1", "criterio2"],
    )
    return BrandEngineConfig(
        enabled=enabled,
        mode=mode,
        evaluator_llm="claude-opus-4-7",
        evaluator_fallback="claude-opus-4-6",
        max_reintentos_embrion_1=2,
        budget_diario_usd=10.0,
        budget_alerta_telegram_usd=8.0,
        budget_kill_switch_usd=budget_kill_switch,
        dimensiones=DimensionesConfig(
            D1_brand_tono=dim_cfg,
            D2_honestidad_pura=dim_cfg,
            D3_consistencia_doctrina=dim_cfg,
            D4_calidad_apple_tesla=dim_cfg,
        ),
    )


def _mk_dim_result(score: float, passed: bool = None, cost: float = 0.01) -> DimensionResult:
    """DimensionResult con passed auto-calculado si no se da."""
    if passed is None:
        passed = score >= 0.7
    return DimensionResult(
        score=score,
        passed=passed,
        reason=None if passed else "mock reason",
        cost_usd=cost,
        latency_ms=100,
    )


def _mk_sabio_evaluation(
    score: float = 0.85,
    error: str = None,
    cost: float = 0.012,
) -> SabioEvaluation:
    """SabioEvaluation fake para mockear evaluar_dimension_via_sabio."""
    return SabioEvaluation(
        score=score,
        reason="mock reason",
        raw_response='{"score": 0.85, "reason": "mock"}',
        cost_usd=cost,
        latency_ms=320,
        evaluator_llm="claude-opus-4-7",
        error=error,
    )


# ─────────────────────────────────────────────────────────────────
# Categoria 1 — Mock dimensions (15 tests)
# ─────────────────────────────────────────────────────────────────


class TestDimensionEvaluators:
    """Verifica interfaz y comportamiento de cada dimension con Sabio mockeado."""

    @pytest.mark.parametrize(
        "evaluator_cls,expected_name",
        [
            (BrandTonoEvaluator, "D1_brand_tono"),
            (HonestidadEvaluator, "D2_honestidad_pura"),
            (DoctrinaEvaluator, "D3_consistencia_doctrina"),
            (AppleTeslaEvaluator, "D4_calidad_apple_tesla"),
        ],
    )
    def test_evaluator_name_canonical(self, evaluator_cls, expected_name):
        ev = evaluator_cls()
        assert ev.name == expected_name

    @pytest.mark.parametrize(
        "evaluator_cls",
        [
            BrandTonoEvaluator,
            HonestidadEvaluator,
            DoctrinaEvaluator,
            AppleTeslaEvaluator,
        ],
    )
    def test_evaluator_implements_interface(self, evaluator_cls):
        ev = evaluator_cls()
        assert isinstance(ev, DimensionEvaluator)
        assert isinstance(ev, BaseSabioDimension)
        assert hasattr(ev, "evaluate")
        assert hasattr(ev, "evaluate_async")

    def test_evaluate_async_passing_score(self):
        with patch(
            "kernel.embriones.brand_engine.sabio_evaluator.evaluar_dimension_via_sabio",
            new=AsyncMock(return_value=_mk_sabio_evaluation(score=0.85)),
        ):
            ev = BrandTonoEvaluator()
            result = asyncio.run(ev.evaluate_async("texto", ["c1"], 0.7))
            assert result.score == 0.85
            assert result.passed is True

    def test_evaluate_async_failing_score(self):
        with patch(
            "kernel.embriones.brand_engine.sabio_evaluator.evaluar_dimension_via_sabio",
            new=AsyncMock(return_value=_mk_sabio_evaluation(score=0.3)),
        ):
            ev = BrandTonoEvaluator()
            result = asyncio.run(ev.evaluate_async("texto", ["c1"], 0.7))
            assert result.score == 0.3
            assert result.passed is False
            assert result.reason is not None  # razón presente cuando falla

    def test_evaluate_async_fail_open_on_error(self):
        """Si Sabio devuelve error → passed=True fail-open absoluto."""
        with patch(
            "kernel.embriones.brand_engine.sabio_evaluator.evaluar_dimension_via_sabio",
            new=AsyncMock(return_value=_mk_sabio_evaluation(score=0.5, error="rate_limit")),
        ):
            ev = BrandTonoEvaluator()
            result = asyncio.run(ev.evaluate_async("texto", ["c1"], 0.7))
            assert result.passed is True  # fail-open
            assert result.reason is None  # fail-open no propaga reason

    def test_cost_tracked_in_result(self):
        with patch(
            "kernel.embriones.brand_engine.sabio_evaluator.evaluar_dimension_via_sabio",
            new=AsyncMock(return_value=_mk_sabio_evaluation(score=0.85, cost=0.025)),
        ):
            ev = BrandTonoEvaluator()
            result = asyncio.run(ev.evaluate_async("texto", ["c1"], 0.7))
            assert result.cost_usd == 0.025

    def test_latency_tracked_in_result(self):
        with patch(
            "kernel.embriones.brand_engine.sabio_evaluator.evaluar_dimension_via_sabio",
            new=AsyncMock(return_value=_mk_sabio_evaluation(score=0.85)),
        ):
            ev = BrandTonoEvaluator()
            result = asyncio.run(ev.evaluate_async("texto", ["c1"], 0.7))
            assert result.latency_ms >= 0

    def test_passed_threshold_boundary(self):
        """Score == umbral_pass debe ser passed=True."""
        with patch(
            "kernel.embriones.brand_engine.sabio_evaluator.evaluar_dimension_via_sabio",
            new=AsyncMock(return_value=_mk_sabio_evaluation(score=0.7)),
        ):
            ev = BrandTonoEvaluator()
            result = asyncio.run(ev.evaluate_async("texto", ["c1"], 0.7))
            assert result.passed is True

    def test_passed_below_threshold(self):
        with patch(
            "kernel.embriones.brand_engine.sabio_evaluator.evaluar_dimension_via_sabio",
            new=AsyncMock(return_value=_mk_sabio_evaluation(score=0.699)),
        ):
            ev = BrandTonoEvaluator()
            result = asyncio.run(ev.evaluate_async("texto", ["c1"], 0.7))
            assert result.passed is False


# ─────────────────────────────────────────────────────────────────
# Categoria 2 — Brand Engine end-to-end mocked (15 tests)
# ─────────────────────────────────────────────────────────────────


class TestBrandEngineE2E:
    """Verifica BrandEngine.validate_async() con _evaluate_all_dimensions mockeado."""

    def _patch_dims(self, engine, dim_results: dict):
        """Helper: parchea _evaluate_all_dimensions para retornar dict fake."""
        engine._evaluate_all_dimensions = AsyncMock(return_value=dim_results)

    def _patch_budget(self, engine, killed: bool = False):
        """Helper: mockea budget tracker para no escribir a disco en tests."""
        mock_bt = MagicMock()
        mock_bt.is_killed.return_value = killed
        mock_bt.record = MagicMock()
        engine._get_budget_tracker = MagicMock(return_value=mock_bt)

    def test_disabled_returns_approved_sintetico(self):
        config = _make_config(enabled=False)
        engine = BrandEngine(config)
        self._patch_budget(engine)
        result = asyncio.run(engine.validate_async("cualquier texto"))
        assert result.verdict == ValidationVerdict.APPROVED
        assert result.cost_usd == 0.0  # no llamó Sabio

    def test_empty_input_rejected(self):
        config = _make_config(enabled=True, mode="enforce")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        result = asyncio.run(engine.validate_async(""))
        assert result.verdict == ValidationVerdict.REJECTED
        assert "vac" in (result.razon_rejection or "").lower()

    def test_whitespace_only_rejected(self):
        config = _make_config(enabled=True, mode="enforce")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        result = asyncio.run(engine.validate_async("   \n\t  "))
        assert result.verdict == ValidationVerdict.REJECTED

    def test_budget_killed_returns_approved_sintetico(self):
        config = _make_config(enabled=True, mode="enforce")
        engine = BrandEngine(config)
        self._patch_budget(engine, killed=True)
        result = asyncio.run(engine.validate_async("texto válido"))
        assert result.verdict == ValidationVerdict.APPROVED
        assert result.cost_usd == 0.0

    def test_all_pass_returns_approved(self):
        config = _make_config(enabled=True, mode="enforce")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        self._patch_dims(
            engine,
            {
                "D1_brand_tono": _mk_dim_result(0.85),
                "D2_honestidad_pura": _mk_dim_result(0.85),
                "D3_consistencia_doctrina": _mk_dim_result(0.85),
                "D4_calidad_apple_tesla": _mk_dim_result(0.85),
            },
        )
        result = asyncio.run(engine.validate_async("Listo. Avanzo."))
        assert result.verdict == ValidationVerdict.APPROVED

    def test_all_fail_returns_rejected_in_enforce(self):
        config = _make_config(enabled=True, mode="enforce")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        self._patch_dims(
            engine,
            {
                "D1_brand_tono": _mk_dim_result(0.3),
                "D2_honestidad_pura": _mk_dim_result(0.3),
                "D3_consistencia_doctrina": _mk_dim_result(0.3),
                "D4_calidad_apple_tesla": _mk_dim_result(0.3),
            },
        )
        result = asyncio.run(engine.validate_async("texto malo"))
        assert result.verdict == ValidationVerdict.REJECTED

    def test_all_fail_in_shadow_does_not_block(self):
        config = _make_config(enabled=True, mode="shadow")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        self._patch_dims(
            engine,
            {
                "D1_brand_tono": _mk_dim_result(0.3),
                "D2_honestidad_pura": _mk_dim_result(0.3),
                "D3_consistencia_doctrina": _mk_dim_result(0.3),
                "D4_calidad_apple_tesla": _mk_dim_result(0.3),
            },
        )
        result = asyncio.run(engine.validate_async("texto"))
        assert result.is_blocking() is False  # shadow nunca bloquea

    def test_validation_id_unique_per_call(self):
        config = _make_config(enabled=True, mode="shadow")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        self._patch_dims(engine, {"D1_brand_tono": _mk_dim_result(0.85)})
        r1 = asyncio.run(engine.validate_async("a"))
        r2 = asyncio.run(engine.validate_async("b"))
        assert r1.validation_id != r2.validation_id

    def test_cost_accumulates_across_dimensions(self):
        config = _make_config(enabled=True, mode="shadow")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        self._patch_dims(
            engine,
            {
                "D1_brand_tono": _mk_dim_result(0.85, cost=0.01),
                "D2_honestidad_pura": _mk_dim_result(0.85, cost=0.02),
                "D3_consistencia_doctrina": _mk_dim_result(0.85, cost=0.03),
                "D4_calidad_apple_tesla": _mk_dim_result(0.85, cost=0.04),
            },
        )
        result = asyncio.run(engine.validate_async("texto"))
        assert abs(result.cost_usd - 0.10) < 0.001

    def test_validation_result_has_all_dim_fields(self):
        config = _make_config(enabled=True, mode="shadow")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        self._patch_dims(
            engine,
            {
                "D1_brand_tono": _mk_dim_result(0.85),
                "D2_honestidad_pura": _mk_dim_result(0.85),
                "D3_consistencia_doctrina": _mk_dim_result(0.85),
                "D4_calidad_apple_tesla": _mk_dim_result(0.85),
            },
        )
        result = asyncio.run(engine.validate_async("texto"))
        assert result.d1_brand_tono is not None
        assert result.d2_honestidad is not None
        assert result.d3_doctrina is not None
        assert result.d4_apple_tesla is not None

    def test_anti_corp_prefilter_rejects_template(self):
        """Pre-filtro mecánico rechaza SIN llamar Sabio."""
        config = _make_config(enabled=True, mode="enforce")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        # NO mockeamos dimensiones — el pre-filtro debe disparar antes
        result = asyncio.run(engine.validate_async("Estoy aquí para ayudarte. Cómo puedo asistirte hoy?"))
        assert result.verdict == ValidationVerdict.REJECTED
        assert result.cost_usd == 0.0  # no gastó Sabio
        assert "anti-corp" in (result.razon_rejection or "").lower()

    def test_is_blocking_only_in_enforce_with_rejected(self):
        config_enforce = _make_config(enabled=True, mode="enforce")
        config_shadow = _make_config(enabled=True, mode="shadow")
        for cfg, expected_blocking in [(config_enforce, True), (config_shadow, False)]:
            engine = BrandEngine(cfg)
            self._patch_budget(engine)
            self._patch_dims(
                engine,
                {
                    "D1_brand_tono": _mk_dim_result(0.3),
                    "D2_honestidad_pura": _mk_dim_result(0.3),
                    "D3_consistencia_doctrina": _mk_dim_result(0.3),
                    "D4_calidad_apple_tesla": _mk_dim_result(0.3),
                },
            )
            result = asyncio.run(engine.validate_async("texto"))
            assert result.is_blocking() is expected_blocking

    def test_partial_dim_failures_dont_crash(self):
        """Algunas dim retornan None (Sabio caído) — engine sigue funcionando."""
        config = _make_config(enabled=True, mode="enforce")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        self._patch_dims(
            engine,
            {
                "D1_brand_tono": None,
                "D2_honestidad_pura": _mk_dim_result(0.85),
                "D3_consistencia_doctrina": None,
                "D4_calidad_apple_tesla": _mk_dim_result(0.85),
            },
        )
        result = asyncio.run(engine.validate_async("texto"))
        assert result is not None  # no crashea

    def test_latency_recorded_total(self):
        config = _make_config(enabled=True, mode="shadow")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        self._patch_dims(engine, {"D1_brand_tono": _mk_dim_result(0.85)})
        result = asyncio.run(engine.validate_async("texto"))
        assert result.latency_ms >= 0

    def test_evaluator_llm_recorded(self):
        config = _make_config(enabled=True, mode="shadow")
        engine = BrandEngine(config)
        self._patch_budget(engine)
        self._patch_dims(engine, {"D1_brand_tono": _mk_dim_result(0.85)})
        result = asyncio.run(engine.validate_async("texto"))
        assert result.evaluator_llm == "claude-opus-4-7"

    def test_mode_recorded_in_result(self):
        for mode in ("shadow", "enforce"):
            config = _make_config(enabled=True, mode=mode)
            engine = BrandEngine(config)
            self._patch_budget(engine)
            self._patch_dims(engine, {"D1_brand_tono": _mk_dim_result(0.85)})
            result = asyncio.run(engine.validate_async("texto"))
            assert result.mode == mode


# ─────────────────────────────────────────────────────────────────
# Categoria 3 — Hook embrion_loop simulation (10 tests)
# ─────────────────────────────────────────────────────────────────


class TestEmbrionLoopHook:
    """Simula el camino del hook en embrion_loop.py sin ejecutar el loop completo."""

    def test_flag_disabled_by_default(self, monkeypatch):
        monkeypatch.delenv("BRAND_ENGINE_ENABLED", raising=False)
        import importlib

        from kernel import embrion_loop as el

        importlib.reload(el)
        assert el.BRAND_ENGINE_ENABLED is False

    def test_flag_enabled_via_env(self, monkeypatch):
        monkeypatch.setenv("BRAND_ENGINE_ENABLED", "true")
        import importlib

        from kernel import embrion_loop as el

        importlib.reload(el)
        assert el.BRAND_ENGINE_ENABLED is True

    def test_engine_exception_fails_open(self):
        """Si validate_async tira excepcion en una dim, fail-open absoluto."""
        config = _make_config(enabled=True, mode="enforce")
        engine = BrandEngine(config)
        mock_bt = MagicMock()
        mock_bt.is_killed.return_value = False
        mock_bt.record = MagicMock()
        engine._get_budget_tracker = MagicMock(return_value=mock_bt)
        # _evaluate_all_dimensions tira excepción
        engine._evaluate_all_dimensions = AsyncMock(side_effect=RuntimeError("Sabio down"))
        with pytest.raises(RuntimeError):
            # Sin try/except en el hook, sí debería propagar. El fail-open
            # vive en el embrion_loop, no aquí.
            asyncio.run(engine.validate_async("texto"))

    def test_default_mode_is_shadow(self):
        config = load_brand_engine_config()
        assert config.mode == "shadow"

    def test_default_enabled_is_false(self):
        config = load_brand_engine_config()
        assert config.enabled is False

    def test_env_override_enables_engine(self, monkeypatch):
        monkeypatch.setenv("BRAND_ENGINE_ENABLED", "true")
        config = apply_env_overrides(load_brand_engine_config())
        assert config.enabled is True

    def test_env_override_promotes_to_enforce(self, monkeypatch):
        monkeypatch.setenv("BRAND_ENGINE_MODE", "enforce")
        config = apply_env_overrides(load_brand_engine_config())
        assert config.mode == "enforce"

    def test_hook_imports_dont_break_loop(self):
        from kernel.embriones.brand_engine.brand_engine import BrandEngine
        from kernel.embriones.brand_engine.config_loader import apply_env_overrides, load_brand_engine_config

        assert BrandEngine is not None
        assert callable(load_brand_engine_config)
        assert callable(apply_env_overrides)

    def test_validation_id_present_for_logging(self):
        config = _make_config(enabled=True, mode="shadow")
        engine = BrandEngine(config)
        mock_bt = MagicMock()
        mock_bt.is_killed.return_value = False
        mock_bt.record = MagicMock()
        engine._get_budget_tracker = MagicMock(return_value=mock_bt)
        engine._evaluate_all_dimensions = AsyncMock(
            return_value={
                "D1_brand_tono": _mk_dim_result(0.85),
            }
        )
        result = asyncio.run(engine.validate_async("texto"))
        assert result.validation_id is not None
        assert len(result.validation_id) > 0

    def test_brand_engine_aborted_only_in_enforce(self):
        """En mode=shadow, is_blocking() es siempre False aunque verdict=REJECTED."""
        config = _make_config(enabled=True, mode="shadow")
        engine = BrandEngine(config)
        mock_bt = MagicMock()
        mock_bt.is_killed.return_value = False
        mock_bt.record = MagicMock()
        engine._get_budget_tracker = MagicMock(return_value=mock_bt)
        engine._evaluate_all_dimensions = AsyncMock(
            return_value={
                "D1_brand_tono": _mk_dim_result(0.3),
                "D2_honestidad_pura": _mk_dim_result(0.3),
                "D3_consistencia_doctrina": _mk_dim_result(0.3),
                "D4_calidad_apple_tesla": _mk_dim_result(0.3),
            }
        )
        result = asyncio.run(engine.validate_async("texto"))
        assert result.is_blocking() is False  # shadow no bloquea


# ─────────────────────────────────────────────────────────────────
# Categoria 4 — Replay corpus (15 tests)
# ─────────────────────────────────────────────────────────────────


class TestReplayCorpus:
    """Corpus deterministico — verifica pre-filtro anti-corp sin invocar LLM."""

    CORP_PHRASES = [
        "Estoy aquí para ayudarte. Cómo puedo asistirte hoy?",
        "Como modelo de lenguaje, no tengo acceso a esa información.",
        "Lamento la inconveniencia. Permíteme buscar eso para usted.",
        "Espero haber sido de ayuda. Quedo a sus órdenes.",
        "Estoy a su disposición para cualquier consulta adicional.",
    ]

    MONSTRUO_PHRASES = [
        "Listo. PR #106 abierto.",
        "Cleanup ejecutado: 17,710 filas borradas.",
        "Falla detectada en latido #19. Aplico fix.",
        "Migración 0019 aplicada con constraint UNIQUE.",
        "Deploy verde. Avanzo al siguiente sprint.",
    ]

    AMBIGUOUS_PHRASES = [
        "Revisé la base de datos y encontré un patrón.",
        "El Embrión procesa 50 latidos por hora.",
        "Investigando opciones para el Brand Engine.",
        "Hay una decisión pendiente sobre la migración.",
        "Consideremos las implicaciones de este cambio.",
    ]

    def _engine_no_sabio(self, mode="enforce"):
        """Engine con pre-filtro activo + dimensiones forzadas a None."""
        config = _make_config(enabled=True, mode=mode)
        engine = BrandEngine(config)
        mock_bt = MagicMock()
        mock_bt.is_killed.return_value = False
        mock_bt.record = MagicMock()
        engine._get_budget_tracker = MagicMock(return_value=mock_bt)
        # Si llega a evaluar dims (pre-filtro no disparó), todas retornan None
        engine._evaluate_all_dimensions = AsyncMock(
            return_value={
                "D1_brand_tono": None,
                "D2_honestidad_pura": None,
                "D3_consistencia_doctrina": None,
                "D4_calidad_apple_tesla": None,
            }
        )
        return engine

    @pytest.mark.parametrize("phrase", CORP_PHRASES)
    def test_corp_phrases_rejected_by_prefilter(self, phrase):
        engine = self._engine_no_sabio(mode="enforce")
        result = asyncio.run(engine.validate_async(phrase))
        assert result.verdict == ValidationVerdict.REJECTED, f"Esperaba REJECTED: {phrase}"
        assert result.cost_usd == 0.0  # pre-filtro no gasta

    @pytest.mark.parametrize("phrase", MONSTRUO_PHRASES)
    def test_monstruo_phrases_not_rejected_by_prefilter(self, phrase):
        """Frases voz Monstruo no deben ser rechazadas por pre-filtro mecánico.
        Como dims retornan None → fail-open APPROVED."""
        engine = self._engine_no_sabio(mode="enforce")
        result = asyncio.run(engine.validate_async(phrase))
        assert result.verdict == ValidationVerdict.APPROVED, f"Esperaba APPROVED: {phrase}"

    @pytest.mark.parametrize("phrase", AMBIGUOUS_PHRASES)
    def test_ambiguous_phrases_pass_prefilter(self, phrase):
        engine = self._engine_no_sabio(mode="enforce")
        result = asyncio.run(engine.validate_async(phrase))
        assert result.verdict == ValidationVerdict.APPROVED, f"Esperaba APPROVED: {phrase}"
