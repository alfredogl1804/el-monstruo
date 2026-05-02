"""
Tests for SP9: Adaptive Model Selection
========================================
Validates select_optimal_model() logic per Hilo B spec:
  - complexity < 0.3 → modelo barato
  - 0.3 <= complexity <= 0.7 → modelo estándar
  - complexity > 0.7 → modelo premium
  - Respeta budget restante
"""

import os
import sys
from unittest.mock import AsyncMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.adaptive_model_selector import (
    _MODELS_BY_TIER,
    MODEL_CATALOG,
    ModelTier,
    _estimate_complexity,
    get_model_for_step,
    read_cost_history,
    select_optimal_model,
)

# ─── Core Selection Tests ─────────────────────────────────────────────────────


class TestSelectOptimalModel:
    """Tests for the core selection function."""

    def test_simple_task_selects_cheap_model(self):
        """complexity < 0.3 → cheap tier."""
        result = select_optimal_model(
            task_complexity=0.1,
            budget_remaining=1.0,
        )
        assert result.tier_selected == ModelTier.CHEAP
        assert result.model.tier == ModelTier.CHEAP
        assert not result.budget_constrained

    def test_medium_task_selects_standard_model(self):
        """0.3 <= complexity <= 0.7 → standard tier."""
        result = select_optimal_model(
            task_complexity=0.5,
            budget_remaining=1.0,
        )
        assert result.tier_selected == ModelTier.STANDARD
        assert result.model.tier == ModelTier.STANDARD
        assert not result.budget_constrained

    def test_complex_task_selects_premium_model(self):
        """complexity > 0.7 → premium tier."""
        result = select_optimal_model(
            task_complexity=0.9,
            budget_remaining=1.0,
        )
        assert result.tier_selected == ModelTier.PREMIUM
        assert result.model.tier == ModelTier.PREMIUM
        assert not result.budget_constrained

    def test_boundary_03_is_standard(self):
        """complexity == 0.3 → standard (inclusive)."""
        result = select_optimal_model(
            task_complexity=0.3,
            budget_remaining=1.0,
        )
        assert result.tier_selected == ModelTier.STANDARD

    def test_boundary_07_is_standard(self):
        """complexity == 0.7 → standard (inclusive)."""
        result = select_optimal_model(
            task_complexity=0.7,
            budget_remaining=1.0,
        )
        assert result.tier_selected == ModelTier.STANDARD

    def test_boundary_071_is_premium(self):
        """complexity == 0.71 → premium."""
        result = select_optimal_model(
            task_complexity=0.71,
            budget_remaining=1.0,
        )
        assert result.tier_selected == ModelTier.PREMIUM

    def test_boundary_029_is_cheap(self):
        """complexity == 0.29 → cheap."""
        result = select_optimal_model(
            task_complexity=0.29,
            budget_remaining=1.0,
        )
        assert result.tier_selected == ModelTier.CHEAP


# ─── Budget Constraint Tests ──────────────────────────────────────────────────


class TestBudgetConstraints:
    """Tests for budget-aware model selection."""

    def test_budget_forces_downgrade_from_premium(self):
        """If budget can't afford premium, downgrade to standard or cheap."""
        result = select_optimal_model(
            task_complexity=0.9,
            budget_remaining=0.0001,
            estimated_tokens=5000,
        )
        assert result.budget_constrained is True
        assert result.model.tier in (ModelTier.STANDARD, ModelTier.CHEAP)

    def test_budget_exhausted_uses_free_model(self):
        """If budget is 0, use free model (gemma3)."""
        result = select_optimal_model(
            task_complexity=0.9,
            budget_remaining=0.0,
            estimated_tokens=10000,
        )
        assert result.budget_constrained is True
        assert result.model.cost_per_1k_tokens == 0.0

    def test_sufficient_budget_no_constraint(self):
        """With ample budget, no constraint flag."""
        result = select_optimal_model(
            task_complexity=0.9,
            budget_remaining=10.0,
        )
        assert result.budget_constrained is False

    def test_budget_downgrade_from_standard_to_cheap(self):
        """Standard task with tiny budget → cheap model."""
        result = select_optimal_model(
            task_complexity=0.5,
            budget_remaining=0.00001,
            estimated_tokens=5000,
        )
        assert result.budget_constrained is True
        assert result.model.tier == ModelTier.CHEAP


# ─── Provider Preference Tests ────────────────────────────────────────────────


class TestProviderPreference:
    """Tests for provider preference."""

    def test_prefer_google_in_standard(self):
        """Preferring google should select gemini."""
        result = select_optimal_model(
            task_complexity=0.5,
            budget_remaining=1.0,
            prefer_provider="google",
        )
        assert result.model.provider == "google"

    def test_prefer_anthropic_in_premium(self):
        """Preferring anthropic should select claude."""
        result = select_optimal_model(
            task_complexity=0.9,
            budget_remaining=1.0,
            prefer_provider="anthropic",
        )
        assert result.model.provider == "anthropic"

    def test_unknown_provider_still_works(self):
        """Unknown provider preference doesn't break selection."""
        result = select_optimal_model(
            task_complexity=0.5,
            budget_remaining=1.0,
            prefer_provider="nonexistent",
        )
        assert result.model is not None
        assert result.tier_selected == ModelTier.STANDARD


# ─── Complexity Estimation Tests ──────────────────────────────────────────────


class TestComplexityEstimation:
    """Tests for _estimate_complexity heuristic."""

    def test_simple_description_low_complexity(self):
        """Short simple task → low complexity."""
        c = _estimate_complexity("lista los archivos")
        assert c < 0.4

    def test_complex_description_high_complexity(self):
        """Complex keywords → high complexity."""
        c = _estimate_complexity(
            "analiza la arquitectura del sistema, investiga las dependencias, "
            "diseña una solución de refactorización multi-paso con pipeline"
        )
        assert c > 0.6

    def test_medium_description(self):
        """Generic description → medium complexity."""
        c = _estimate_complexity("procesa el documento y genera un reporte")
        assert 0.2 <= c <= 0.8

    def test_empty_description(self):
        """Empty string → base complexity."""
        c = _estimate_complexity("")
        assert 0.0 <= c <= 1.0

    def test_complexity_clamped_to_0_1(self):
        """Result always between 0 and 1."""
        c = _estimate_complexity(
            "analiza investiga diseña arquitectura optimiza refactoriza "
            "multi-paso integra compara evalúa razonamiento profundo complejo "
            "estrategia código implementa debug pipeline"
        )
        assert 0.0 <= c <= 1.0


# ─── get_model_for_step Tests ─────────────────────────────────────────────────


class TestGetModelForStep:
    """Tests for the TaskPlanner integration helper."""

    def test_simple_step(self):
        """Simple step description → cheap model."""
        result = get_model_for_step(
            step_description="lista los archivos del directorio",
            plan_total_cost=0.0,
            plan_budget=1.0,
        )
        assert result.tier_selected == ModelTier.CHEAP

    def test_complex_step(self):
        """Complex step → premium model."""
        result = get_model_for_step(
            step_description=(
                "analiza la arquitectura del sistema e investiga "
                "las dependencias para diseñar un pipeline de refactorización"
            ),
            plan_total_cost=0.0,
            plan_budget=1.0,
        )
        assert result.tier_selected == ModelTier.PREMIUM

    def test_budget_exhausted_step(self):
        """When plan cost equals budget → free model."""
        result = get_model_for_step(
            step_description="analiza el código complejo",
            plan_total_cost=1.0,
            plan_budget=1.0,
        )
        assert result.budget_constrained is True


# ─── Cost History Tests ───────────────────────────────────────────────────────


class TestCostHistory:
    """Tests for read_cost_history."""

    @pytest.mark.asyncio
    async def test_no_db_returns_zeros(self):
        """None db → zero defaults."""
        result = await read_cost_history(None)
        assert result["total_spent_usd"] == 0.0
        assert result["plans_count"] == 0

    @pytest.mark.asyncio
    async def test_db_query_success(self):
        """Successful DB query returns parsed values."""
        mock_db = AsyncMock()
        mock_db.fetch_one.return_value = {
            "total_spent": 2.5,
            "avg_cost": 0.25,
            "plans_count": 10,
            "tokens_total": 50000,
        }
        result = await read_cost_history(mock_db)
        assert result["total_spent_usd"] == 2.5
        assert result["avg_cost_per_plan"] == 0.25
        assert result["plans_count"] == 10
        assert result["tokens_total"] == 50000

    @pytest.mark.asyncio
    async def test_db_error_returns_zeros(self):
        """DB exception → graceful fallback to zeros."""
        mock_db = AsyncMock()
        mock_db.fetch_one.side_effect = Exception("connection failed")
        result = await read_cost_history(mock_db)
        assert result["total_spent_usd"] == 0.0
        assert result["plans_count"] == 0


# ─── ModelSelection.to_dict Tests ─────────────────────────────────────────────


class TestModelSelectionDict:
    """Tests for serialization."""

    def test_to_dict_structure(self):
        """to_dict returns expected keys."""
        result = select_optimal_model(0.5, 1.0)
        d = result.to_dict()
        assert "model_name" in d
        assert "provider" in d
        assert "tier" in d
        assert "cost_per_1k" in d
        assert "reason" in d
        assert "budget_constrained" in d

    def test_to_dict_values_match(self):
        """to_dict values match the selection."""
        result = select_optimal_model(0.1, 1.0)
        d = result.to_dict()
        assert d["tier"] == "cheap"
        assert d["model_name"] == result.model.name


# ─── Model Catalog Integrity ─────────────────────────────────────────────────


class TestModelCatalog:
    """Tests for model catalog integrity."""

    def test_all_tiers_have_models(self):
        """Every tier has at least one model."""
        for tier in ModelTier:
            assert len(_MODELS_BY_TIER.get(tier, [])) > 0

    def test_cheap_models_are_cheapest(self):
        """Cheap models cost less than standard."""
        cheap_max = max(m.cost_per_1k_tokens for m in _MODELS_BY_TIER[ModelTier.CHEAP])
        standard_min = min(m.cost_per_1k_tokens for m in _MODELS_BY_TIER[ModelTier.STANDARD])
        assert cheap_max <= standard_min

    def test_catalog_has_free_model(self):
        """At least one free model exists for emergency fallback."""
        free_models = [m for m in MODEL_CATALOG if m.cost_per_1k_tokens == 0.0]
        assert len(free_models) >= 1
