"""
Sprint 86 Bloque 4 — Tests del Trono Score por dominio + mejoras audit Cowork.

Cobertura:
  · TronoCalculator (validación pesos, z_score mode, neutral mode, multi-dominio)
  · TronoResult (bandas de confianza, contributions, modes)
  · apply_results_to_models (update in-place)
  · PersistResult.error_category (mejora #2 audit Cowork)
  · PersistResult.failure_rate_observed (single + batch)
  · CatastroPipeline.skip_persist (constructor + CATASTRO_SKIP_PERSIST env)
  · summary() expandido con trono_summary y persist_summary nuevos campos

Estilo: mock-based (sin tocar Supabase). 1 opt-in real con env var.

[Hilo Manus Catastro] · Sprint 86 Bloque 4 · 2026-05-04
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from kernel.catastro import (
    DEFAULT_WEIGHTS,
    METRIC_FIELDS,
    CatastroModelo,
    CatastroPersistence,
    CatastroPipeline,
    CatastroTronoEmptyInput,
    CatastroTronoError,
    CatastroTronoInvalidDomain,
    CatastroTronoInvalidWeights,
    ErrorCategory,
    PersistResult,
    PipelineRunResult,
    TronoCalculator,
    TronoResult,
    apply_results_to_models,
    __bloque__,
    __version__,
)


# ============================================================================
# FIXTURES
# ============================================================================


def _make_modelo(
    slug: str,
    *,
    quality: float = 70.0,
    cost: float = 50.0,
    speed: float = 60.0,
    reliability: float = 80.0,
    brand_fit: float = 0.5,
    confidence: float = 0.8,
    dominios: list[str] | None = None,
    trono_global: float | None = None,
) -> CatastroModelo:
    return CatastroModelo(
        id=slug,
        nombre=slug,
        proveedor="test-provider",
        dominios=dominios or ["llm_frontier"],
        quality_score=quality,
        cost_efficiency=cost,
        speed_score=speed,
        reliability_score=reliability,
        brand_fit=brand_fit,
        confidence=confidence,
        trono_global=trono_global,
    )


@pytest.fixture
def env_clean(monkeypatch):
    """Limpia env vars sensibles para tests."""
    for k in (
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "CATASTRO_SKIP_PERSIST",
        "CATASTRO_DRY_RUN",
        "CATASTRO_FAILURE_RATE_THRESHOLD",
    ):
        monkeypatch.delenv(k, raising=False)
    return monkeypatch


# ============================================================================
# 1. VERSIONADO
# ============================================================================


class TestVersionado:
    def test_version_es_sprint_86(self):
        # Aflojado en Bloque 5: el Sprint 86 sigue versionando hacia arriba
        assert __version__.startswith("0.86.")
        assert __version__ >= "0.86.4"

    def test_bloque_es_al_menos_4(self):
        # El Bloque 4 entregó lo suyo; bloques posteriores incrementan
        assert int(__bloque__) >= 4


# ============================================================================
# 2. TRONO CALCULATOR — INIT Y VALIDACIÓN
# ============================================================================


class TestTronoCalculatorInit:
    def test_default_weights_suman_uno(self):
        calc = TronoCalculator()
        assert abs(sum(calc.weights.values()) - 1.0) < 1e-9
        assert calc.weights == DEFAULT_WEIGHTS

    def test_default_base_y_scale(self):
        calc = TronoCalculator()
        assert calc.base == 50.0
        assert calc.scale == 10.0

    def test_metric_fields_orden_canonico(self):
        assert METRIC_FIELDS == (
            "quality_score",
            "cost_efficiency",
            "speed_score",
            "reliability_score",
            "brand_fit",
        )

    def test_custom_weights_validos(self):
        custom = {
            "quality_score": 0.50,
            "cost_efficiency": 0.20,
            "speed_score": 0.15,
            "reliability_score": 0.10,
            "brand_fit": 0.05,
        }
        calc = TronoCalculator(weights=custom)
        assert calc.weights == custom

    def test_custom_base_scale(self):
        calc = TronoCalculator(base=100.0, scale=20.0)
        assert calc.base == 100.0
        assert calc.scale == 20.0


class TestTronoCalculatorValidacionPesos:
    def test_pesos_no_suman_uno_falla(self):
        with pytest.raises(CatastroTronoInvalidWeights) as exc:
            TronoCalculator(weights={
                "quality_score": 0.30,
                "cost_efficiency": 0.20,
                "speed_score": 0.15,
                "reliability_score": 0.10,
                "brand_fit": 0.10,  # suma 0.85
            })
        assert exc.value.code == "catastro_trono_invalid_weights"
        assert "Σ pesos" in str(exc.value)

    def test_pesos_keys_faltantes_falla(self):
        with pytest.raises(CatastroTronoInvalidWeights) as exc:
            TronoCalculator(weights={"quality_score": 1.0})
        assert "missing=" in str(exc.value)

    def test_pesos_keys_extra_falla(self):
        bad = {**DEFAULT_WEIGHTS, "rogue_metric": 0.0}
        with pytest.raises(CatastroTronoInvalidWeights):
            TronoCalculator(weights=bad)


# ============================================================================
# 3. COMPUTE_FOR_DOMAIN — CASOS BASE Y DEGENERADOS
# ============================================================================


class TestComputeForDomain:
    def test_dominio_vacio_falla(self):
        calc = TronoCalculator()
        with pytest.raises(CatastroTronoInvalidDomain):
            calc.compute_for_domain([_make_modelo("alpha-model")], dominio="")

    def test_modelos_vacios_falla(self):
        calc = TronoCalculator()
        with pytest.raises(CatastroTronoEmptyInput):
            calc.compute_for_domain([], dominio="llm_frontier")

    def test_un_solo_modelo_modo_neutral(self):
        calc = TronoCalculator()
        modelos = [_make_modelo("solo-modelo-test")]
        results = calc.compute_for_domain(modelos, dominio="llm_frontier")
        assert len(results) == 1
        r = results[0]
        assert r.mode == "neutral"
        assert r.trono_new == 50.0
        assert "menos_de_2_modelos" in r.warnings

    def test_dos_modelos_modo_z_score(self):
        calc = TronoCalculator()
        modelos = [
            _make_modelo("alpha-model", quality=90.0, cost=80.0),
            _make_modelo("beta-model", quality=50.0, cost=20.0),
        ]
        results = calc.compute_for_domain(modelos, dominio="llm_frontier")
        assert len(results) == 2
        assert all(r.mode == "z_score" for r in results)
        # Promedio debe ser exactamente 50.0 (propiedad matemática del z-score)
        assert abs(sum(r.trono_new for r in results) / 2 - 50.0) < 0.01

    def test_alpha_mejor_que_beta_recibe_trono_mayor(self):
        calc = TronoCalculator()
        modelos = [
            _make_modelo("alpha-model", quality=95.0, cost=90.0,
                         speed=85.0, reliability=95.0, brand_fit=0.9),
            _make_modelo("beta-model", quality=40.0, cost=30.0,
                         speed=35.0, reliability=45.0, brand_fit=0.2),
        ]
        results = calc.compute_for_domain(modelos, dominio="llm_frontier")
        by_id = {r.modelo_id: r for r in results}
        assert by_id["alpha-model"].trono_new > by_id["beta-model"].trono_new

    def test_metrica_null_se_trata_como_z_cero(self):
        calc = TronoCalculator()
        m1 = _make_modelo("m1-test", quality=80.0)
        m2 = _make_modelo("m2-test", quality=60.0)
        # Forzar quality_score=None en m1 vía atributo
        m1.quality_score = None
        results = calc.compute_for_domain([m1, m2], dominio="llm_frontier")
        by_id = {r.modelo_id: r for r in results}
        # m1 con quality NULL debe tener z_score quality=0 + warning
        assert by_id["m1-test"].z_scores["quality_score"] == 0.0
        assert any("quality_score_null_treated_as_zero_z" in w
                   for w in by_id["m1-test"].warnings)

    def test_filtra_modelos_fuera_del_dominio(self):
        calc = TronoCalculator()
        modelos = [
            _make_modelo("alpha-model", dominios=["llm_frontier"]),
            _make_modelo("beta-model", dominios=["llm_frontier"]),
            _make_modelo("gamma-model", dominios=["coding_llms"]),
        ]
        results = calc.compute_for_domain(modelos, dominio="llm_frontier")
        slugs = {r.modelo_id for r in results}
        assert slugs == {"alpha-model", "beta-model"}


# ============================================================================
# 4. COMPUTE_ALL — MULTI-DOMINIO
# ============================================================================


class TestComputeAll:
    def test_modelos_vacios_falla(self):
        calc = TronoCalculator()
        with pytest.raises(CatastroTronoEmptyInput):
            calc.compute_all([])

    def test_separa_por_dominio(self):
        calc = TronoCalculator()
        modelos = [
            _make_modelo("alpha-model", dominios=["llm_frontier"]),
            _make_modelo("beta-model", dominios=["llm_frontier"]),
            _make_modelo("gamma-model", dominios=["coding_llms"]),
            _make_modelo("delta-model", dominios=["coding_llms"]),
        ]
        out = calc.compute_all(modelos)
        assert set(out.keys()) == {"llm_frontier", "coding_llms"}
        assert len(out["llm_frontier"]) == 2
        assert len(out["coding_llms"]) == 2

    def test_modelo_en_multiples_dominios_aparece_en_ambos(self):
        calc = TronoCalculator()
        m_dual = _make_modelo("dual-model", dominios=["llm_frontier", "coding_llms"])
        modelos = [
            m_dual,
            _make_modelo("only-frontier", dominios=["llm_frontier"]),
            _make_modelo("only-coding", dominios=["coding_llms"]),
        ]
        out = calc.compute_all(modelos)
        assert "dual-model" in {r.modelo_id for r in out["llm_frontier"]}
        assert "dual-model" in {r.modelo_id for r in out["coding_llms"]}


# ============================================================================
# 5. TRONO RESULT — BANDA DE CONFIANZA + EXPLAINABILITY
# ============================================================================


class TestTronoResult:
    def test_banda_low_high_es_simetrica(self):
        calc = TronoCalculator()
        modelos = [
            _make_modelo("alpha-model", confidence=0.6),
            _make_modelo("beta-model", confidence=0.6),
        ]
        results = calc.compute_for_domain(modelos, dominio="llm_frontier")
        for r in results:
            half = (r.trono_high - r.trono_low) / 2
            # half_width esperado = scale * (1 - confidence) = 10 * 0.4 = 4
            assert abs(half - 4.0) < 0.05 or r.trono_low in (0.0, 100.0)

    def test_confidence_alta_banda_estrecha(self):
        calc = TronoCalculator()
        modelos = [
            _make_modelo("alpha-model", confidence=0.95),
            _make_modelo("beta-model", confidence=0.95),
        ]
        results = calc.compute_for_domain(modelos, dominio="llm_frontier")
        # half = 10 * (1 - 0.95) = 0.5
        for r in results:
            assert (r.trono_high - r.trono_low) <= 1.05

    def test_contributions_suman_z_ponderada(self):
        calc = TronoCalculator()
        modelos = [_make_modelo("alpha-model"), _make_modelo("beta-model", quality=30.0)]
        results = calc.compute_for_domain(modelos, dominio="llm_frontier")
        for r in results:
            sum_contrib = sum(r.contributions.values())
            # trono_new = base + scale * sum_contrib (clampeado)
            esperado = 50.0 + 10.0 * sum_contrib
            esperado = max(0.0, min(100.0, esperado))
            assert abs(r.trono_new - round(esperado, 2)) < 0.05


# ============================================================================
# 6. APPLY_RESULTS_TO_MODELS — UPDATE IN-PLACE
# ============================================================================


class TestApplyResultsToModels:
    def test_aplica_trono_in_place(self):
        modelos = [_make_modelo("alpha-model"), _make_modelo("beta-model")]
        results = [
            TronoResult(
                modelo_id="alpha-model", dominio="llm_frontier",
                trono_old=None, trono_new=72.5, trono_delta=22.5,
                trono_low=70.0, trono_high=75.0,
                z_scores={k: 0.0 for k in METRIC_FIELDS},
                contributions={k: 0.0 for k in METRIC_FIELDS},
                confidence=0.8, mode="z_score",
            ),
            TronoResult(
                modelo_id="beta-model", dominio="llm_frontier",
                trono_old=None, trono_new=27.5, trono_delta=-22.5,
                trono_low=25.0, trono_high=30.0,
                z_scores={k: 0.0 for k in METRIC_FIELDS},
                contributions={k: 0.0 for k in METRIC_FIELDS},
                confidence=0.8, mode="z_score",
            ),
        ]
        updated = apply_results_to_models(modelos, results)
        assert updated == 2
        by_id = {m.id: m for m in modelos}
        assert by_id["alpha-model"].trono_global == 72.5
        assert by_id["alpha-model"].trono_delta == 22.5
        assert by_id["beta-model"].trono_global == 27.5

    def test_resultados_sin_modelo_match_se_ignoran(self):
        modelos = [_make_modelo("alpha-model")]
        results = [
            TronoResult(
                modelo_id="ghost-model", dominio="llm_frontier",
                trono_old=None, trono_new=99.0, trono_delta=49.0,
                trono_low=95.0, trono_high=100.0,
                z_scores={k: 0.0 for k in METRIC_FIELDS},
                contributions={k: 0.0 for k in METRIC_FIELDS},
                confidence=0.8, mode="z_score",
            ),
        ]
        updated = apply_results_to_models(modelos, results)
        assert updated == 0


# ============================================================================
# 7. PERSIST RESULT — error_category + failure_rate_observed (audit Cowork)
# ============================================================================


class TestPersistResultMejorasAudit:
    def test_error_category_default_es_none(self):
        pr = PersistResult(modelo_id="a", success=True)
        assert pr.error_category == "none"

    def test_failure_rate_observed_default_es_none(self):
        pr = PersistResult(modelo_id="a", success=True)
        assert pr.failure_rate_observed is None

    def test_summary_incluye_nuevos_campos(self):
        pr = PersistResult(
            modelo_id="a",
            success=False,
            error_category="db_down",
            failure_rate_observed=0.15,
        )
        s = pr.summary()
        assert s["error_category"] == "db_down"
        assert s["failure_rate_observed"] == 0.15

    def test_error_category_typing_exportado(self):
        # Smoke check: ErrorCategory está exportado vía __init__
        assert ErrorCategory is not None


class TestCategorizeError:
    def test_categoriza_timeout(self):
        p = CatastroPersistence(dry_run=True)
        cat = p._categorize_error(TimeoutError("operation timed out"))
        assert cat == "network_timeout"

    def test_categoriza_connection_refused(self):
        p = CatastroPersistence(dry_run=True)
        cat = p._categorize_error(ConnectionRefusedError("Connection refused"))
        assert cat == "db_down"

    def test_categoriza_validation_postgrest(self):
        class APIError(Exception):
            pass
        p = CatastroPersistence(dry_run=True)
        cat = p._categorize_error(APIError("violates check constraint"))
        assert cat == "rpc_validation"

    def test_categoriza_unknown_para_otros(self):
        p = CatastroPersistence(dry_run=True)
        cat = p._categorize_error(ValueError("algo random"))
        assert cat == "unknown"


class TestPersistManyFailureRate:
    def test_calcula_failure_rate_y_propaga(self, env_clean):
        # Cliente que falla en el item 2 (índice 1) y tiene éxito en 0 y 2.
        call_count = {"n": 0}

        def fake_factory(url, key):
            client = MagicMock()
            def rpc(name, params):
                idx = call_count["n"]
                call_count["n"] += 1
                ex = MagicMock()
                if idx == 1:
                    raise ConnectionError("simulated db down")
                ex.execute.return_value = MagicMock(
                    data={"modelo_id": params["p_modelo"]["id"],
                          "evento_id": "00000000-0000-0000-0000-000000000001",
                          "curadores_actualizados": 0,
                          "aplicado_at": "2026-05-04T12:00:00Z"}
                )
                return ex
            client.rpc = rpc
            return client

        env_clean.setenv("SUPABASE_URL", "https://fake.supabase.co")
        env_clean.setenv("SUPABASE_SERVICE_ROLE_KEY", "fake-key")

        persistence = CatastroPersistence(client_factory=fake_factory)
        items = [
            {"modelo": _make_modelo("alpha-model")},
            {"modelo": _make_modelo("beta-model")},
            {"modelo": _make_modelo("gamma-model")},
        ]
        results = persistence.persist_many(items)
        assert len(results) == 3
        # 1 de 3 falló → failure_rate = 0.333...
        for r in results:
            assert r.failure_rate_observed is not None
            assert abs(r.failure_rate_observed - 1/3) < 1e-6
        # El que falló debe tener categoría db_down
        assert results[1].success is False
        assert results[1].error_category == "db_down"


# ============================================================================
# 8. PIPELINE — skip_persist (constructor + env var)
# ============================================================================


class TestPipelineSkipPersist:
    def test_skip_persist_explicito_true(self, env_clean):
        pipe = CatastroPipeline(dry_run=True, skip_persist=True)
        assert pipe.skip_persist is True

    def test_skip_persist_explicito_false_ignora_env(self, env_clean):
        env_clean.setenv("CATASTRO_SKIP_PERSIST", "true")
        pipe = CatastroPipeline(dry_run=True, skip_persist=False)
        assert pipe.skip_persist is False

    def test_skip_persist_env_var_true(self, env_clean):
        env_clean.setenv("CATASTRO_SKIP_PERSIST", "true")
        pipe = CatastroPipeline(dry_run=True)
        assert pipe.skip_persist is True

    def test_skip_persist_env_var_yes(self, env_clean):
        env_clean.setenv("CATASTRO_SKIP_PERSIST", "yes")
        pipe = CatastroPipeline(dry_run=True)
        assert pipe.skip_persist is True

    def test_skip_persist_env_var_invalida_es_false(self, env_clean):
        env_clean.setenv("CATASTRO_SKIP_PERSIST", "maybe")
        pipe = CatastroPipeline(dry_run=True)
        assert pipe.skip_persist is False

    def test_skip_persist_default_false(self, env_clean):
        pipe = CatastroPipeline(dry_run=True)
        assert pipe.skip_persist is False


class TestPipelineRunSkipPersistComportamiento:
    def test_run_con_skip_persist_marca_skipped(self, env_clean):
        pipe = CatastroPipeline(dry_run=True, skip_persist=True)
        result: PipelineRunResult = asyncio.run(pipe.run())
        assert result.persist_skipped is True
        # No debe haber persist_results cuando se skipea
        assert result.persist_results == []

    def test_run_sin_skip_persist_si_persiste_dry_run(self, env_clean):
        pipe = CatastroPipeline(dry_run=True, skip_persist=False)
        result: PipelineRunResult = asyncio.run(pipe.run())
        assert result.persist_skipped is False
        # En dry_run debería haber persist_results dry_run=True
        for r in result.persist_results:
            assert r.dry_run is True


# ============================================================================
# 9. SUMMARY — trono_summary + persist_summary expandido
# ============================================================================


class TestPipelineSummary:
    def test_summary_incluye_trono_summary(self, env_clean):
        pipe = CatastroPipeline(dry_run=True)
        result = asyncio.run(pipe.run())
        s = result.summary()
        assert "trono_summary" in s
        assert "dominios" in s["trono_summary"]
        assert "modelos_calculados" in s["trono_summary"]
        assert "modos" in s["trono_summary"]

    def test_summary_persist_incluye_skipped_y_failure_rate(self, env_clean):
        pipe = CatastroPipeline(dry_run=True)
        result = asyncio.run(pipe.run())
        s = result.summary()
        ps = s["persist_summary"]
        assert "skipped" in ps
        assert "failure_rate_observed" in ps
        assert "error_categories" in ps
        assert isinstance(ps["error_categories"], dict)


# ============================================================================
# 10. INTEGRACIÓN PIPELINE + TRONO (sin red)
# ============================================================================


class TestIntegracionTronoEnPipeline:
    def test_pipeline_calcula_trono_para_persistibles(self, env_clean):
        pipe = CatastroPipeline(dry_run=True)
        result = asyncio.run(pipe.run())
        # En dry_run con fixtures fake, hay persistibles → debe haber trono_results
        if result.modelos_persistibles:
            # Al menos 1 dominio si hubo persistibles
            assert len(result.trono_results) >= 1

    def test_pipeline_trono_calculator_inyectable(self, env_clean):
        custom_calc = TronoCalculator(base=100.0, scale=20.0)
        pipe = CatastroPipeline(dry_run=True, trono_calculator=custom_calc)
        assert pipe.trono_calculator.base == 100.0
        assert pipe.trono_calculator.scale == 20.0


# ============================================================================
# 11. IDENTIDAD DE MARCA (Brand Engine, AGENTS.md regla #4)
# ============================================================================


class TestIdentidadMarcaTrono:
    def test_todos_los_codigos_de_error_son_catastro_trono(self):
        for cls in [
            CatastroTronoError,
            CatastroTronoInvalidWeights,
            CatastroTronoEmptyInput,
            CatastroTronoInvalidDomain,
        ]:
            assert cls.code.startswith("catastro_trono_"), (
                f"{cls.__name__}.code={cls.code} no respeta identidad de marca"
            )


# ============================================================================
# 12. OPT-IN: integración real con Supabase (skipped por defecto)
# ============================================================================


@pytest.mark.skipif(
    os.environ.get("SUPABASE_INTEGRATION_TESTS") != "true",
    reason="Set SUPABASE_INTEGRATION_TESTS=true para correr (requiere SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY reales)",
)
class TestIntegracionRealOptIn:
    def test_recompute_trono_real_via_pipeline(self):
        # Smoke test que corre el pipeline contra Supabase real con skip_persist=False.
        pipe = CatastroPipeline(dry_run=False, skip_persist=False)
        result = asyncio.run(pipe.run())
        assert result.is_success
