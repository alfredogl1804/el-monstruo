"""
Tests Sprint 86.4.5 Bloque 2 — Enriquecimiento de campos métricos.

Cubre:
  - Carga del field_mapping.yaml (happy + invalid_shape + not_found)
  - apply_field_mapping con cache sintético: AA + OR + LMArena
  - Normalización passthrough (quality_score)
  - Normalización minmax (speed_score)
  - Normalización inverse_log (cost_efficiency)
  - Fallback derived_from_quorum (reliability_score)
  - Tolerancia: solo 1 fuente reporta → otros campos quedan None
  - Memento preflight: warning cuando una fuente esperada no aporta
  - Integración con build_modelo_from_pipeline_persistible

Disciplina anti-Dory: cada test es atómico y no comparte mutación.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pytest
import yaml

from kernel.catastro.persistence import build_modelo_from_pipeline_persistible
from kernel.catastro.sources.field_mapping import (
    DEFAULT_YAML_PATH,
    FieldMappingApplyError,
    FieldMappingLoadError,
    apply_field_mapping,
    load_field_mapping,
)


# ============================================================================
# Fixtures
# ============================================================================

def _build_persistible(slug: str, confirming_sources: list[str]) -> dict:
    """Persistible mínimo (estilo _extract_persistible)."""
    return {
        "slug": slug,
        "fields": {},
        "presence_confidence": 0.85,
        "confirming_sources": confirming_sources,
    }


def _build_cache_full() -> dict:
    """
    Cache sintético con 3 modelos. Cada uno reporta distintos campos
    para ejercitar normalizaciones min-max e inverse_log.

    Modelo A (premium): high quality, high speed, high price
    Modelo B (mid):     mid quality, mid speed, mid price
    Modelo C (cheap):   low quality, low speed, low price
    """
    return {
        "modelo-a": {
            "artificial_analysis": {
                "raw_slug": "modelo-a",
                "name": "Modelo A",
                "organization": "OrgA",
                "quality_score": 90.0,
                "pricing": {"input_per_million": 30.0, "output_per_million": 60.0},
                "tokens_per_second": 200.0,
                "ttft_seconds": 0.3,
            },
            "openrouter": {
                "raw_id": "orga/modelo-a",
                "name": "Modelo A",
                "pricing": {"input_per_million": 30.0, "output_per_million": 60.0},
            },
            "lmarena": {
                "raw_model_name": "modelo-a",
                "organization": "OrgA",
                "arena_score": 1300,
            },
        },
        "modelo-b": {
            "artificial_analysis": {
                "raw_slug": "modelo-b",
                "name": "Modelo B",
                "organization": "OrgB",
                "quality_score": 70.0,
                "pricing": {"input_per_million": 5.0, "output_per_million": 15.0},
                "tokens_per_second": 100.0,
            },
            "openrouter": {
                "pricing": {"input_per_million": 5.0, "output_per_million": 15.0},
            },
        },
        "modelo-c": {
            "artificial_analysis": {
                "raw_slug": "modelo-c",
                "name": "Modelo C",
                "organization": "OrgC",
                "quality_score": 50.0,
                "pricing": {"input_per_million": 0.5, "output_per_million": 1.5},
                "tokens_per_second": 50.0,
            },
        },
    }


# ============================================================================
# 1. Carga del yaml
# ============================================================================

class TestLoadFieldMapping:

    def test_carga_default_yaml_real(self):
        mapping = load_field_mapping()
        assert "fields" in mapping
        assert "quality_score" in mapping["fields"]
        assert "reliability_score" in mapping["fields"]
        assert "cost_efficiency" in mapping["fields"]
        assert "speed_score" in mapping["fields"]
        assert mapping["version"] == "1.0"

    def test_yaml_not_found(self, tmp_path):
        bogus = tmp_path / "no_existe.yaml"
        with pytest.raises(FieldMappingLoadError, match="not_found"):
            load_field_mapping(bogus)

    def test_yaml_invalid_shape(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("just_a_string", encoding="utf-8")
        with pytest.raises(FieldMappingLoadError, match="invalid_shape"):
            load_field_mapping(bad)

    def test_yaml_parse_error(self, tmp_path):
        bad = tmp_path / "broken.yaml"
        bad.write_text("fields:\n  - [unclosed", encoding="utf-8")
        with pytest.raises(FieldMappingLoadError):
            load_field_mapping(bad)


# ============================================================================
# 2. apply_field_mapping con cache sintético
# ============================================================================

class TestApplyFieldMapping:

    def test_quality_score_passthrough_aa(self):
        cache = _build_cache_full()
        persistibles = {
            "modelo-a": _build_persistible("modelo-a", ["artificial_analysis", "openrouter", "lmarena"]),
            "modelo-b": _build_persistible("modelo-b", ["artificial_analysis", "openrouter"]),
            "modelo-c": _build_persistible("modelo-c", ["artificial_analysis"]),
        }
        results = apply_field_mapping(persistibles, cache)

        assert results["modelo-a"]["quality_score"] == 90.0
        assert results["modelo-b"]["quality_score"] == 70.0
        assert results["modelo-c"]["quality_score"] == 50.0

    def test_speed_score_minmax_normalization(self):
        cache = _build_cache_full()
        persistibles = {
            "modelo-a": _build_persistible("modelo-a", ["artificial_analysis"]),
            "modelo-b": _build_persistible("modelo-b", ["artificial_analysis"]),
            "modelo-c": _build_persistible("modelo-c", ["artificial_analysis"]),
        }
        results = apply_field_mapping(persistibles, cache)

        # tokens_per_second: A=200, B=100, C=50. Min=50, Max=200.
        # A → 100*(200-50)/(200-50) = 100.0
        # B → 100*(100-50)/(200-50) = 33.33
        # C → 100*(50-50)/(200-50) = 0.0
        assert results["modelo-a"]["speed_score"] == pytest.approx(100.0)
        assert results["modelo-b"]["speed_score"] == pytest.approx(33.333, rel=1e-3)
        assert results["modelo-c"]["speed_score"] == pytest.approx(0.0)

    def test_cost_efficiency_inverse_log(self):
        cache = _build_cache_full()
        persistibles = {
            "modelo-a": _build_persistible("modelo-a", ["artificial_analysis"]),
            "modelo-b": _build_persistible("modelo-b", ["artificial_analysis"]),
            "modelo-c": _build_persistible("modelo-c", ["artificial_analysis"]),
        }
        results = apply_field_mapping(persistibles, cache)

        # input_per_million: A=30, B=5, C=0.5
        # cost_efficiency es inverse_log: más barato = score mayor
        # Modelo C debe tener mayor cost_efficiency que A
        ce_a = results["modelo-a"]["cost_efficiency"]
        ce_b = results["modelo-b"]["cost_efficiency"]
        ce_c = results["modelo-c"]["cost_efficiency"]
        assert ce_c > ce_b > ce_a, f"orden invertido: A={ce_a} B={ce_b} C={ce_c}"
        assert 0 <= ce_a <= 100
        assert 0 <= ce_c <= 100

    def test_reliability_score_derived_from_quorum(self):
        cache = _build_cache_full()
        persistibles = {
            "modelo-a": _build_persistible("modelo-a", ["artificial_analysis", "openrouter", "lmarena"]),
            "modelo-b": _build_persistible("modelo-b", ["artificial_analysis", "openrouter"]),
            "modelo-c": _build_persistible("modelo-c", ["artificial_analysis"]),
        }
        results = apply_field_mapping(persistibles, cache)

        # 3 fuentes oficiales totales
        assert results["modelo-a"]["reliability_score"] == pytest.approx(100.0)
        assert results["modelo-b"]["reliability_score"] == pytest.approx(66.67, rel=1e-2)
        assert results["modelo-c"]["reliability_score"] == pytest.approx(33.33, rel=1e-2)

    def test_precio_input_output_passthrough(self):
        cache = _build_cache_full()
        persistibles = {
            "modelo-a": _build_persistible("modelo-a", ["artificial_analysis"]),
        }
        results = apply_field_mapping(persistibles, cache)

        assert results["modelo-a"]["precio_input_per_million"] == 30.0
        assert results["modelo-a"]["precio_output_per_million"] == 60.0

    def test_persistible_fields_mutated(self):
        """apply_field_mapping debe mutar persistible.fields IN-PLACE."""
        cache = _build_cache_full()
        persistibles = {
            "modelo-a": _build_persistible("modelo-a", ["artificial_analysis", "openrouter", "lmarena"]),
        }
        apply_field_mapping(persistibles, cache)

        f = persistibles["modelo-a"]["fields"]
        assert f["quality_score"] == 90.0
        assert f["reliability_score"] == pytest.approx(100.0)
        assert "precio_input_per_million" in f

    def test_solo_una_fuente_los_otros_quedan_none(self):
        """Modelo solo en LMArena (sin AA ni OR) → métricas AA-dependientes None."""
        cache = {
            "solo-lmarena": {
                "lmarena": {
                    "raw_model_name": "solo-lmarena",
                    "organization": "X",
                    "arena_score": 1100,
                },
            },
        }
        persistibles = {
            "solo-lmarena": _build_persistible("solo-lmarena", ["lmarena"]),
        }
        results = apply_field_mapping(persistibles, cache)

        assert results["solo-lmarena"]["quality_score"] is None
        assert results["solo-lmarena"]["speed_score"] is None
        assert results["solo-lmarena"]["cost_efficiency"] is None
        # reliability_score se DERIVA → debe ser 33.33 (1/3 fuentes)
        assert results["solo-lmarena"]["reliability_score"] == pytest.approx(33.33, rel=1e-2)


# ============================================================================
# 3. Memento preflight
# ============================================================================

class TestMementoPreflight:

    def test_preflight_warning_cuando_aa_falta_quality_score(self, caplog):
        """Si AA reporta pero NO trae quality_score, preflight loggea warning."""
        cache = {
            "raro": {
                "artificial_analysis": {
                    # NO quality_score, NO tokens_per_second
                    "raw_slug": "raro",
                    "name": "Raro",
                },
            },
        }
        persistibles = {
            "raro": _build_persistible("raro", ["artificial_analysis"]),
        }
        with caplog.at_level(logging.WARNING):
            apply_field_mapping(persistibles, cache)

        msgs = [r.message for r in caplog.records]
        # Debe haber al menos 1 warning de memento_preflight_missing
        assert any("memento_preflight_missing" in m for m in msgs), msgs

    def test_preflight_no_warning_cuando_todo_presente(self, caplog):
        cache = _build_cache_full()
        persistibles = {
            "modelo-a": _build_persistible("modelo-a", ["artificial_analysis", "openrouter"]),
        }
        with caplog.at_level(logging.WARNING):
            apply_field_mapping(persistibles, cache)

        msgs = [r.message for r in caplog.records]
        assert not any("memento_preflight_missing" in m for m in msgs), msgs

    def test_preflight_raise_mode(self, tmp_path):
        """Si on_missing=raise, FieldMappingApplyError."""
        # Crear yaml local con on_missing=raise
        full = load_field_mapping()
        full["memento_preflight"]["on_missing"] = "raise"
        custom_yaml = tmp_path / "custom.yaml"
        custom_yaml.write_text(yaml.safe_dump(full), encoding="utf-8")
        custom = load_field_mapping(custom_yaml)

        cache = {
            "raro": {
                "artificial_analysis": {"raw_slug": "raro"},  # sin quality_score
            },
        }
        persistibles = {
            "raro": _build_persistible("raro", ["artificial_analysis"]),
        }
        with pytest.raises(FieldMappingApplyError, match="memento_preflight_missing"):
            apply_field_mapping(persistibles, cache, mapping=custom)


# ============================================================================
# 4. Integración con build_modelo_from_pipeline_persistible
# ============================================================================

class TestBuildModeloIntegracion:

    def test_modelo_construido_con_metricas_enriquecidas(self):
        cache = _build_cache_full()
        # 3 modelos en persistibles para que minmax tenga rango real
        persistibles = {
            "modelo-a": _build_persistible("modelo-a", ["artificial_analysis", "openrouter", "lmarena"]),
            "modelo-b": _build_persistible("modelo-b", ["artificial_analysis", "openrouter"]),
            "modelo-c": _build_persistible("modelo-c", ["artificial_analysis"]),
        }
        apply_field_mapping(persistibles, cache)

        modelo = build_modelo_from_pipeline_persistible(
            slug="modelo-a",
            persistible=persistibles["modelo-a"],
            quorum_results=[],
        )

        assert modelo.id == "modelo-a"
        assert modelo.quality_score == pytest.approx(90.0)
        assert modelo.reliability_score == pytest.approx(100.0)
        assert modelo.cost_efficiency is not None
        assert modelo.speed_score == pytest.approx(100.0)  # mayor t/s del run
        assert modelo.precio_input_per_million == pytest.approx(30.0)
        assert modelo.precio_output_per_million == pytest.approx(60.0)

    def test_modelo_sin_enriquecimiento_campos_none(self):
        """Si _enrich_with_metrics no corrió, todos los campos métricos None."""
        persistible = {
            "slug": "viejo",
            "fields": {"organization": "X"},  # sin quality/reliability/etc
            "presence_confidence": 0.5,
            "confirming_sources": ["artificial_analysis"],
        }
        modelo = build_modelo_from_pipeline_persistible(
            slug="viejo",
            persistible=persistible,
            quorum_results=[],
        )
        assert modelo.quality_score is None
        assert modelo.reliability_score is None
        assert modelo.cost_efficiency is None
        assert modelo.speed_score is None


# ============================================================================
# 5. Robustez: empty / edge cases
# ============================================================================

class TestEdgeCases:

    def test_persistibles_vacio(self):
        results = apply_field_mapping({}, {})
        assert results == {}

    def test_cache_con_modelo_no_persistible_se_ignora(self):
        cache = _build_cache_full()
        persistibles = {
            "modelo-a": _build_persistible("modelo-a", ["artificial_analysis"]),
            # modelo-b y modelo-c NO en persistibles
        }
        results = apply_field_mapping(persistibles, cache)
        assert "modelo-a" in results
        assert "modelo-b" not in results
        assert "modelo-c" not in results

    def test_minmax_con_un_solo_valor_devuelve_50(self):
        """Si todos los valores son iguales, normalización min-max → 50.0."""
        cache = {
            "uno": {
                "artificial_analysis": {
                    "quality_score": 80.0,
                    "tokens_per_second": 100.0,
                    "pricing": {"input_per_million": 5.0, "output_per_million": 10.0},
                },
            },
        }
        persistibles = {"uno": _build_persistible("uno", ["artificial_analysis"])}
        results = apply_field_mapping(persistibles, cache)
        # Con un solo valor, max=min → minmax devuelve 50.0
        assert results["uno"]["speed_score"] == pytest.approx(50.0)
