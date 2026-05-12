"""Tests de scaffolding para Brand Engine — PR-A (T1-T3).

Estos tests validan que la estructura del módulo es correcta sin tocar LLM real.
Tests reales con LLM live se agregan en PR-B (T4-T6).

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Permitir importar kernel sin instalación.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from kernel.embriones.brand_engine import (
    BrandEngine,
    ValidationResult,
    ValidationVerdict,
)
from kernel.embriones.brand_engine.config_loader import (
    BrandEngineConfig,
    DimensionConfig,
    DimensionesConfig,
    apply_env_overrides,
    load_brand_engine_config,
)
from kernel.embriones.brand_engine.dimensions import (
    DimensionEvaluator,
    DimensionResult,
)
from kernel.embriones.brand_engine.dimensions.brand_tono import BrandTonoEvaluator
from kernel.embriones.brand_engine.dimensions.honestidad import HonestidadEvaluator
from kernel.embriones.brand_engine.dimensions.doctrina import DoctrinaEvaluator
from kernel.embriones.brand_engine.dimensions.apple_tesla import AppleTeslaEvaluator


# ── Fixtures ──────────────────────────────────────────────────────────────

CONFIG_YAML_PATH = (
    Path(__file__).resolve().parents[2]
    / "kernel"
    / "embriones"
    / "brand_engine_config.yaml"
)


def _make_test_config(enabled: bool = True, mode: str = "shadow") -> BrandEngineConfig:
    """Construye una config válida en memoria para tests sin tocar el YAML."""
    dim = DimensionConfig(enabled=True, umbral_pass=0.7, criterios=["criterio test"])
    return BrandEngineConfig(
        enabled=enabled,
        mode=mode,
        evaluator_llm="claude-opus-4-7",
        evaluator_fallback="claude-opus-4-6",
        max_reintentos_embrion_1=2,
        budget_diario_usd=10.0,
        budget_alerta_telegram_usd=8.0,
        budget_kill_switch_usd=12.0,
        dimensiones=DimensionesConfig(
            D1_brand_tono=dim,
            D2_honestidad_pura=dim,
            D3_consistencia_doctrina=dim,
            D4_calidad_apple_tesla=dim,
        ),
    )


# ── T1: estructura del módulo ─────────────────────────────────────────────


class TestModuleStructure:
    """T1 — la estructura del paquete cumple naming canónico DSC-G-004."""

    def test_brand_engine_class_exists_and_importable(self):
        assert BrandEngine is not None
        assert hasattr(BrandEngine, "validate")
        assert hasattr(BrandEngine, "from_config_file")

    def test_validation_result_is_immutable_dataclass(self):
        # Frozen dataclass → asignación post-construcción debe fallar.
        result = ValidationResult(
            validation_id="test-id",
            verdict=ValidationVerdict.APPROVED,
            d1_brand_tono=None,
            d2_honestidad=None,
            d3_doctrina=None,
            d4_apple_tesla=None,
            razon_rejection=None,
            sugerencia_reintento=None,
            cost_usd=0.0,
            latency_ms=10,
            evaluator_llm="claude-opus-4-7",
            mode="shadow",
            timestamp="2026-05-11T00:00:00+00:00",
        )
        with pytest.raises((AttributeError, TypeError)):
            result.verdict = ValidationVerdict.REJECTED  # type: ignore[misc]

    def test_validation_verdict_enum_values(self):
        assert ValidationVerdict.APPROVED.value == "approved"
        assert ValidationVerdict.REJECTED.value == "rejected"
        assert ValidationVerdict.TIMEOUT.value == "timeout"
        assert ValidationVerdict.ERROR.value == "error"

    def test_no_prohibited_naming_in_module_paths(self):
        """DSC-G-004: ningún archivo del módulo usa nombres prohibidos."""
        module_root = (
            Path(__file__).resolve().parents[2]
            / "kernel"
            / "embriones"
            / "brand_engine"
        )
        prohibited = {"service", "handler", "utils", "helper", "misc"}
        for py_file in module_root.rglob("*.py"):
            stem = py_file.stem.lower()
            assert stem not in prohibited, (
                f"Archivo {py_file} viola DSC-G-004 naming canónico"
            )


# ── T2: las 4 dimensiones implementan la interfaz ─────────────────────────


class TestDimensionsInterface:
    """T2 — las 4 dimensiones implementan DimensionEvaluator y siguen contract."""

    @pytest.mark.parametrize(
        "evaluator_cls,expected_name",
        [
            (BrandTonoEvaluator, "D1_brand_tono"),
            (HonestidadEvaluator, "D2_honestidad_pura"),
            (DoctrinaEvaluator, "D3_consistencia_doctrina"),
            (AppleTeslaEvaluator, "D4_calidad_apple_tesla"),
        ],
    )
    def test_evaluator_implements_interface(self, evaluator_cls, expected_name):
        evaluator = evaluator_cls()
        assert isinstance(evaluator, DimensionEvaluator)
        assert evaluator.name == expected_name

    @pytest.mark.parametrize(
        "evaluator_cls",
        [BrandTonoEvaluator, HonestidadEvaluator, DoctrinaEvaluator, AppleTeslaEvaluator],
    )
    def test_evaluator_returns_dimension_result(self, evaluator_cls):
        evaluator = evaluator_cls()
        result = evaluator.evaluate(
            respuesta_candidata="texto de prueba",
            criterios=["criterio test"],
            umbral_pass=0.7,
        )
        assert isinstance(result, DimensionResult)
        assert 0.0 <= result.score <= 1.0
        assert isinstance(result.passed, bool)


# ── BrandEngine validate() smoke tests ────────────────────────────────────


class TestBrandEngineValidate:
    """Smoke tests del método validate() en modo scaffolding (PR-A)."""

    def test_validate_disabled_engine_returns_approved(self):
        engine = BrandEngine(_make_test_config(enabled=False))
        result = engine.validate("cualquier respuesta")
        assert result.verdict == ValidationVerdict.APPROVED
        assert result.cost_usd == 0.0

    def test_validate_empty_response_is_rejected(self):
        engine = BrandEngine(_make_test_config(enabled=True))
        result = engine.validate("   ")
        assert result.verdict == ValidationVerdict.REJECTED
        assert result.razon_rejection is not None

    def test_validate_corporate_phrase_is_rejected(self):
        engine = BrandEngine(_make_test_config(enabled=True))
        result = engine.validate("Hola, estoy aquí para ayudarte con tu duda.")
        assert result.verdict == ValidationVerdict.REJECTED

    def test_validate_monstruo_voice_is_approved(self):
        engine = BrandEngine(_make_test_config(enabled=True))
        result = engine.validate(
            "Forja activada. Tres opciones, costo binario, decides tú."
        )
        assert result.verdict == ValidationVerdict.APPROVED

    def test_shadow_mode_never_blocks(self):
        engine = BrandEngine(_make_test_config(enabled=True, mode="shadow"))
        result = engine.validate("   ")
        # Rejected en shadow NO debe ser blocking.
        assert result.verdict == ValidationVerdict.REJECTED
        assert result.is_blocking() is False

    def test_enforce_mode_blocks_rejected(self):
        engine = BrandEngine(_make_test_config(enabled=True, mode="enforce"))
        result = engine.validate("   ")
        assert result.verdict == ValidationVerdict.REJECTED
        assert result.is_blocking() is True


# ── T5: config loader (Pydantic schema) ───────────────────────────────────


class TestConfigLoader:
    """T5 anticipado — config loader valida schema y env overrides."""

    def test_loads_canonical_yaml(self):
        config = load_brand_engine_config(str(CONFIG_YAML_PATH))
        assert config.enabled is False  # default seguro
        assert config.mode == "shadow"  # canary default
        assert config.evaluator_llm == "claude-opus-4-7"

    def test_rejects_invalid_mode(self):
        from pydantic import ValidationError

        dim = DimensionConfig(enabled=True, umbral_pass=0.7, criterios=["x"])
        with pytest.raises(ValidationError):
            BrandEngineConfig(
                enabled=False,
                mode="produccion_full",  # no whitelist
                dimensiones=DimensionesConfig(
                    D1_brand_tono=dim,
                    D2_honestidad_pura=dim,
                    D3_consistencia_doctrina=dim,
                    D4_calidad_apple_tesla=dim,
                ),
            )

    def test_rejects_non_whitelisted_evaluator(self):
        from pydantic import ValidationError

        dim = DimensionConfig(enabled=True, umbral_pass=0.7, criterios=["x"])
        with pytest.raises(ValidationError):
            BrandEngineConfig(
                enabled=False,
                mode="shadow",
                evaluator_llm="gpt-3.5-turbo",  # no whitelist
                dimensiones=DimensionesConfig(
                    D1_brand_tono=dim,
                    D2_honestidad_pura=dim,
                    D3_consistencia_doctrina=dim,
                    D4_calidad_apple_tesla=dim,
                ),
            )

    def test_env_override_applies(self, monkeypatch):
        config = _make_test_config(enabled=False, mode="shadow")
        monkeypatch.setenv("BRAND_ENGINE_ENABLED", "true")
        monkeypatch.setenv("BRAND_ENGINE_MODE", "enforce")
        overridden = apply_env_overrides(config)
        assert overridden.enabled is True
        assert overridden.mode == "enforce"

    def test_env_override_noop_when_unset(self):
        config = _make_test_config(enabled=False, mode="shadow")
        overridden = apply_env_overrides(config)
        # Sin env vars seteadas → config sin cambios.
        assert overridden.enabled == config.enabled
        assert overridden.mode == config.mode

    def test_dimension_umbral_pass_range(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            DimensionConfig(enabled=True, umbral_pass=1.5, criterios=["x"])
        with pytest.raises(ValidationError):
            DimensionConfig(enabled=True, umbral_pass=-0.1, criterios=["x"])

    def test_dimension_requires_at_least_one_criterio(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            DimensionConfig(enabled=True, umbral_pass=0.7, criterios=[])


# ── T3 migration: smoke test sintáctico ───────────────────────────────────


class TestMigration0020:
    """Smoke test del archivo SQL — no aplica contra DB en este test suite."""

    def test_migration_file_exists(self):
        migration_path = (
            Path(__file__).resolve().parents[2]
            / "migrations"
            / "sql"
            / "0020_embrion_validation_log.sql"
        )
        assert migration_path.exists(), "Migration 0020 file missing"

    def test_migration_has_rls_enabled(self):
        migration_path = (
            Path(__file__).resolve().parents[2]
            / "migrations"
            / "sql"
            / "0020_embrion_validation_log.sql"
        )
        content = migration_path.read_text(encoding="utf-8")
        assert "ENABLE ROW LEVEL SECURITY" in content, (
            "Migration 0020 NO habilita RLS — viola DSC-S-006"
        )
        assert "CREATE POLICY" in content, (
            "Migration 0020 NO crea policy — viola DSC-S-006"
        )

    def test_migration_has_verification_block(self):
        migration_path = (
            Path(__file__).resolve().parents[2]
            / "migrations"
            / "sql"
            / "0020_embrion_validation_log.sql"
        )
        content = migration_path.read_text(encoding="utf-8")
        # Verifica que la migración tiene su propio bloque de assertion post.
        assert "RAISE EXCEPTION" in content
        assert "RAISE NOTICE" in content
