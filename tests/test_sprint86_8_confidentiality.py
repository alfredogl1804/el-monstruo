"""
Sprint 86.8 — Tests para confidentiality_tier filtering en RecommendationEngine.

Cobertura:
- Validacion de min_tier_required (4 valores validos + invalido)
- Filtrado por tier (4 escenarios por tier semantico)
- Cache key incluye min_tier_required (no cross-contamina entre tiers)
- raise_on_no_eligible_tier semantica
- ModeloRecomendado expone confidentiality_tier
- Migration 027 SQL coherente (idempotencia + check constraint)

[Hilo Manus Catastro] · Sprint 86.8 Bloque 4 · 2026-05-05
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from kernel.catastro.recommendation import (
    CONFIDENTIALITY_TIER_RANK,
    DEFAULT_MIN_TIER_REQUIRED,
    VALID_CONFIDENTIALITY_TIERS,
    CatastroChooseModelNoEligibleTier,
    CatastroRecommendInvalidArgs,
    ModeloRecomendado,
    RecommendationEngine,
)


# ============================================================================
# Helpers
# ============================================================================


def _row(model_id: str, tier: str, trono: float = 80.0, dominio: str = "general") -> dict:
    """Genera una fila simulada de catastro_trono_view."""
    return {
        "id": model_id,
        "nombre": model_id,
        "proveedor": "test_provider",
        "macroarea": "reasoning",
        "dominio": dominio,
        "estado": "production",
        "trono_global": trono,
        "trono_low": trono - 5.0,
        "trono_high": trono + 5.0,
        "rank_dominio": 1,
        "quality_score": 80.0,
        "cost_efficiency": 70.0,
        "speed_score": 75.0,
        "reliability_score": 85.0,
        "brand_fit": 80.0,
        "confidence": 0.85,
        "precio_input_per_million": 1.0,
        "precio_output_per_million": 2.0,
        "open_weights": False,
        "confidentiality_tier": tier,
        "ultima_validacion": "2026-05-05T00:00:00Z",
    }


class _ChainMock:
    """Stub fluido tipo Supabase: cualquier metodo devuelve self; execute() devuelve data."""
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def select(self, *a, **kw): return self
    def eq(self, *a, **kw): return self
    def order(self, *a, **kw): return self
    def limit(self, *a, **kw): return self

    def execute(self):
        return MagicMock(data=self._rows)


class _ClientMock:
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def table(self, *a, **kw):
        return _ChainMock(self._rows)


def _mock_db_factory(rows: list[dict]):
    """
    Crea un db_factory que devuelve un cliente Supabase mock.
    Implementacion via clases reales (no MagicMock fluido) para garantizar
    que execute() devuelva un result con .data == rows reales.
    """
    return lambda: _ClientMock(rows)


# ============================================================================
# Bloque A — Validacion de constantes
# ============================================================================


def test_tier_rank_orden_semantico():
    """local_only es mas estricto (rank 0); cloud_only es mas permisivo (rank 3)."""
    assert CONFIDENTIALITY_TIER_RANK["local_only"] == 0
    assert CONFIDENTIALITY_TIER_RANK["tee_capable"] == 1
    assert CONFIDENTIALITY_TIER_RANK["cloud_anonymized_ok"] == 2
    assert CONFIDENTIALITY_TIER_RANK["cloud_only"] == 3


def test_valid_tiers_set():
    """Los 4 tiers documentados son los unicos validos."""
    assert VALID_CONFIDENTIALITY_TIERS == frozenset({
        "local_only",
        "tee_capable",
        "cloud_anonymized_ok",
        "cloud_only",
    })


def test_default_min_tier_es_permisivo():
    """Default debe ser cloud_only (acepta todos) por compat hacia atras."""
    assert DEFAULT_MIN_TIER_REQUIRED == "cloud_only"


# ============================================================================
# Bloque B — Validacion de min_tier_required
# ============================================================================


def test_recommend_rechaza_tier_invalido():
    """min_tier_required='bogus' debe lanzar CatastroRecommendInvalidArgs."""
    eng = RecommendationEngine(db_factory=None)
    with pytest.raises(CatastroRecommendInvalidArgs) as exc_info:
        eng.recommend(use_case="x", min_tier_required="bogus_tier")
    assert exc_info.value.code == "catastro_recommend_invalid_args"


@pytest.mark.parametrize("tier", [
    "local_only", "tee_capable", "cloud_anonymized_ok", "cloud_only",
])
def test_recommend_acepta_los_4_tiers_validos(tier):
    """Los 4 tiers documentados deben ser aceptados sin error."""
    eng = RecommendationEngine(db_factory=None)
    res = eng.recommend(use_case="x", min_tier_required=tier)
    # Sin DB -> degraded, pero NO debe haber lanzado exception
    assert res.degraded is True
    assert res.degraded_reason == "no_db_factory_configured"


# ============================================================================
# Bloque C — Filtrado por tier (semantica de rank)
# ============================================================================


def test_filtro_local_only_descarta_cloud():
    """min='local_only' (rank 0) excluye TODO excepto local_only."""
    rows = [
        _row("llama-7b-local", "local_only", trono=70),
        _row("claude-cloud", "cloud_anonymized_ok", trono=90),
        _row("gpt5-cloud", "cloud_only", trono=95),
    ]
    eng = RecommendationEngine(db_factory=_mock_db_factory(rows))
    res = eng.recommend(use_case="legal review", min_tier_required="local_only")
    assert res.degraded is False
    assert len(res.modelos) == 1
    assert res.modelos[0].id == "llama-7b-local"
    assert res.modelos[0].confidentiality_tier == "local_only"


def test_filtro_tee_capable_acepta_local_y_tee():
    """min='tee_capable' (rank 1) acepta rank<=1 (local_only + tee_capable)."""
    rows = [
        _row("llama-local", "local_only", trono=70),
        _row("claude-tee", "tee_capable", trono=85),
        _row("gpt-cloud", "cloud_anonymized_ok", trono=90),
        _row("hf-cloud", "cloud_only", trono=92),
    ]
    eng = RecommendationEngine(db_factory=_mock_db_factory(rows))
    res = eng.recommend(use_case="x", min_tier_required="tee_capable", top_n=10)
    assert res.degraded is False
    ids = [m.id for m in res.modelos]
    assert "llama-local" in ids
    assert "claude-tee" in ids
    assert "gpt-cloud" not in ids
    assert "hf-cloud" not in ids


def test_filtro_cloud_anonymized_acepta_3_tiers():
    """min='cloud_anonymized_ok' (rank 2) acepta rank<=2 (excluye solo cloud_only)."""
    rows = [
        _row("llama-local", "local_only", trono=70),
        _row("claude-tee", "tee_capable", trono=85),
        _row("gpt-anon", "cloud_anonymized_ok", trono=90),
        _row("hf-raw", "cloud_only", trono=92),
    ]
    eng = RecommendationEngine(db_factory=_mock_db_factory(rows))
    res = eng.recommend(
        use_case="contract", min_tier_required="cloud_anonymized_ok", top_n=10
    )
    assert res.degraded is False
    ids = [m.id for m in res.modelos]
    assert {"llama-local", "claude-tee", "gpt-anon"}.issubset(set(ids))
    assert "hf-raw" not in ids


def test_filtro_cloud_only_acepta_todos():
    """min='cloud_only' (rank 3, default) NO filtra nada."""
    rows = [
        _row("llama-local", "local_only", trono=70),
        _row("hf-raw", "cloud_only", trono=92),
    ]
    eng = RecommendationEngine(db_factory=_mock_db_factory(rows))
    res = eng.recommend(use_case="x", min_tier_required="cloud_only", top_n=10)
    assert len(res.modelos) == 2


# ============================================================================
# Bloque D — Edge cases
# ============================================================================


def test_filtro_estricto_sin_candidatos_devuelve_degraded():
    """Si filtro deja la lista vacia y raise_on_no_eligible=False, devuelve degraded."""
    rows = [
        _row("hf-raw", "cloud_only", trono=92),
    ]
    eng = RecommendationEngine(db_factory=_mock_db_factory(rows))
    res = eng.recommend(use_case="x", min_tier_required="local_only")
    assert res.degraded is True
    # Sprint 86.8: razon especifica para filtro tier vs no_data generico
    assert res.degraded_reason == "no_models_match_tier_filter"
    assert len(res.modelos) == 0


def test_filtro_estricto_con_raise_lanza_excepcion():
    """raise_on_no_eligible_tier=True + filtro vacio -> CatastroChooseModelNoEligibleTier."""
    rows = [
        _row("hf-raw", "cloud_only", trono=92),
    ]
    eng = RecommendationEngine(db_factory=_mock_db_factory(rows))
    with pytest.raises(CatastroChooseModelNoEligibleTier) as exc_info:
        eng.recommend(
            use_case="legal", min_tier_required="local_only",
            raise_on_no_eligible_tier=True,
        )
    assert exc_info.value.code == "catastro_choose_model_no_eligible_tier"


def test_tier_null_en_db_se_trata_como_cloud_only():
    """Modelos con confidentiality_tier=None se tratan como cloud_only (defensivo)."""
    rows = [
        _row("legacy-no-tier", "cloud_only", trono=80),
    ]
    rows[0]["confidentiality_tier"] = None  # legacy DB sin migration aplicada
    eng = RecommendationEngine(db_factory=_mock_db_factory(rows))
    # Con cloud_only debe pasarlo
    res = eng.recommend(use_case="x", min_tier_required="cloud_only")
    assert len(res.modelos) == 1
    # Con local_only no
    res = eng.recommend(use_case="x", min_tier_required="local_only")
    assert len(res.modelos) == 0


# ============================================================================
# Bloque E — Cache invalidation por tier
# ============================================================================


def test_cache_key_incluye_min_tier():
    """Mismo use_case con tiers distintos NO debe cachear cross-tier."""
    rows = [
        _row("llama-local", "local_only", trono=70),
        _row("hf-raw", "cloud_only", trono=92),
    ]
    eng = RecommendationEngine(db_factory=_mock_db_factory(rows))
    # Primera llamada con cloud_only (acepta todos)
    res_a = eng.recommend(use_case="task", min_tier_required="cloud_only", top_n=10)
    # Segunda con local_only (filtra)
    res_b = eng.recommend(use_case="task", min_tier_required="local_only", top_n=10)
    assert len(res_a.modelos) == 2
    assert len(res_b.modelos) == 1
    # B no debe ser cache hit de A
    assert res_b.cache_hit is False


def test_cache_hit_funciona_para_misma_combinacion_tier():
    """Misma (use_case, tier) reusa cache."""
    rows = [_row("llama-local", "local_only", trono=70)]
    eng = RecommendationEngine(db_factory=_mock_db_factory(rows))
    res_first = eng.recommend(use_case="task", min_tier_required="local_only")
    res_second = eng.recommend(use_case="task", min_tier_required="local_only")
    assert res_first.cache_hit is False
    assert res_second.cache_hit is True


# ============================================================================
# Bloque F — ModeloRecomendado expone confidentiality_tier
# ============================================================================


def test_modelo_recomendado_serializa_tier():
    """ModeloRecomendado debe exponer confidentiality_tier en JSON output."""
    m = ModeloRecomendado(
        id="claude",
        nombre="Claude",
        proveedor="anthropic",
        macroarea="reasoning",
        dominio="general",
        trono_global=92.0,
        trono_low=87.0,
        trono_high=97.0,
        rank_dominio=1,
        confidentiality_tier="cloud_anonymized_ok",
    )
    payload = m.model_dump()
    assert payload["confidentiality_tier"] == "cloud_anonymized_ok"


def test_modelo_recomendado_tier_opcional():
    """confidentiality_tier es Optional — default None para compat."""
    m = ModeloRecomendado(
        id="x", nombre="X", proveedor="p", dominio="g",
        trono_global=50.0, trono_low=45.0, trono_high=55.0, rank_dominio=1,
    )
    assert m.confidentiality_tier is None


# ============================================================================
# Bloque G — Migration 027 SQL coherencia
# ============================================================================


def test_migration_027_sql_existe_y_es_idempotente():
    """Migration SQL debe existir y usar IF NOT EXISTS."""
    sql_path = Path(__file__).resolve().parent.parent / "scripts" / "027_sprint86_8_confidentiality_tier_schema.sql"
    assert sql_path.exists(), f"Migration 027 no encontrado: {sql_path}"
    sql_text = sql_path.read_text()
    # Idempotencia: debe usar IF NOT EXISTS para columna e indice
    assert "IF NOT EXISTS confidentiality_tier" in sql_text or "ADD COLUMN IF NOT EXISTS confidentiality_tier" in sql_text
    assert "CREATE INDEX IF NOT EXISTS" in sql_text


def test_migration_027_sql_check_constraint_4_tiers():
    """SQL debe enumerar exactamente los 4 tiers en CHECK constraint."""
    sql_path = Path(__file__).resolve().parent.parent / "scripts" / "027_sprint86_8_confidentiality_tier_schema.sql"
    sql_text = sql_path.read_text()
    for tier in ["local_only", "tee_capable", "cloud_anonymized_ok", "cloud_only"]:
        assert f"'{tier}'" in sql_text, f"Tier {tier} ausente en CHECK constraint"


def test_assignment_sql_existe():
    """Asignacion inicial conservadora debe existir como script separado."""
    sql_path = Path(__file__).resolve().parent.parent / "scripts" / "027_sprint86_8_assign_confidentiality_tiers.sql"
    assert sql_path.exists(), f"Asignacion inicial no encontrada: {sql_path}"


def test_run_migration_027_existe():
    """run_migration_027.py debe existir como helper Python."""
    py_path = Path(__file__).resolve().parent.parent / "scripts" / "run_migration_027.py"
    assert py_path.exists(), f"run_migration_027.py no encontrado: {py_path}"


# ============================================================================
# Bloque H — Schema_generated drift
# ============================================================================


def test_schema_generated_incluye_confidentiality_tier():
    """schema_generated.py regenerado debe contener confidentiality_tier."""
    schema_path = Path(__file__).resolve().parent.parent / "kernel" / "catastro" / "schema_generated.py"
    text = schema_path.read_text()
    assert "confidentiality_tier" in text
    # Debe estar en la lista de columnas de catastro_modelos
    assert "'confidentiality_tier'" in text


# ============================================================================
# Bloque I — Anti-Dory: filtro no rompe pipeline existente
# ============================================================================


def test_recommend_default_compat_hacia_atras():
    """recommend() sin min_tier_required usa default cloud_only (acepta todos)."""
    rows = [
        _row("a", "local_only"),
        _row("b", "cloud_only"),
        _row("c", "tee_capable"),
    ]
    eng = RecommendationEngine(db_factory=_mock_db_factory(rows))
    res = eng.recommend(use_case="x", top_n=10)  # SIN min_tier_required
    assert len(res.modelos) == 3
