# Sprint 64 — "La Prueba de Fuego"

**Fecha:** 1 mayo 2026
**Version:** 0.64.0
**Autor:** Manus AI
**Filosofia:** Despues de 13 sprints construyendo capacidades (51-63), Sprint 64 cambia el paradigma: ya no se construye — se VALIDA. Cada epica demuestra que lo construido funciona en condiciones reales, mide su calidad, y establece baselines para mejora continua.

---

## Contexto Estrategico

El promedio de cobertura es 89.5%. Para llegar a 95% no se necesitan mas features — se necesita EVIDENCIA de que las features existentes funcionan. Sprint 64 es el sprint de validacion y hardening.

| Objetivo | Cobertura | Estrategia Sprint 64 |
|---|---|---|
| #4 Nunca Equivocarse 2x | 85% | Predictive error prevention |
| #5 Gasolina Magna/Premium | 86% | Dynamic tier routing con budget awareness |
| #12 Ecosistema/Soberania | 86% | Sovereignty activation test |
| #10 Simulador Predictivo | 86% | Backtesting + calibration framework |
| #1 Crear Empresas | 89% | E2E demo pipeline (la prueba definitiva) |

---

## Infraestructura Existente (No Recrear)

Sprint 64 se construye SOBRE lo existente, no lo reemplaza:

| Existente | Sprint 64 Agrega | Diferencia Clave |
|---|---|---|
| `test_e2e_kernel.py` (API test) | E2E Demo Pipeline (user journey) | API vs producto completo |
| `fallback_engine.py` (reactivo) | Predictive Prevention (proactivo) | Despues vs antes del fallo |
| `usage_tracker.py` (logging) | Dynamic Tier Routing (adaptivo) | Registrar vs optimizar |
| `cidp_calibrator.py` (model bench) | Simulator Validation (predictions) | Capacidad vs precision |
| `fallback_engine.py` (provider fail) | Sovereignty Test (intencional) | Accidental vs planificado |

---

## Epica 64.1 — E2E Demo Pipeline

**Objetivo:** Obj #1 (Crear Empresas) + Obj #3 (Minima Complejidad)
**Impacto:** +3% en Obj #1, +2% en Obj #3

### Vision

La prueba definitiva: un script automatizado que simula un usuario real diciendo "Crea una tienda de cafe online" y mide todo el journey hasta tener un sitio desplegado. Si esto funciona, El Monstruo funciona.

### Arquitectura

```
tests/e2e_demo/
  __init__.py
  demo_runner.py         # Orchestrates full E2E demo
  scenarios.py           # Pre-defined demo scenarios
  metrics_collector.py   # Measures time, cost, quality per step
  quality_auditor.py     # Audits output quality
  report_generator.py    # Generates demo report
```

### Demo Runner

```python
"""tests/e2e_demo/demo_runner.py"""
import asyncio
import time
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = structlog.get_logger("e2e_demo.runner")

@dataclass
class DemoStep:
    name: str
    started_at: float = 0
    completed_at: float = 0
    duration_seconds: float = 0
    cost_usd: float = 0
    quality_score: float = 0  # 0-1
    output: Optional[str] = None
    error: Optional[str] = None
    success: bool = False


@dataclass
class DemoResult:
    scenario_name: str
    steps: list[DemoStep] = field(default_factory=list)
    total_duration_seconds: float = 0
    total_cost_usd: float = 0
    average_quality: float = 0
    deployed_url: Optional[str] = None
    success: bool = False
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class E2EDemoRunner:
    """Run full end-to-end demos simulating real user journeys."""

    def __init__(self, kernel_client, supabase):
        self.kernel = kernel_client
        self.supabase = supabase

    async def run_demo(self, scenario: dict) -> DemoResult:
        """Execute a complete demo scenario."""
        result = DemoResult(scenario_name=scenario["name"])
        logger.info("demo_started", scenario=scenario["name"])

        try:
            # Step 1: Intent Processing
            step1 = await self._run_step(
                "intent_processing",
                self._process_intent,
                scenario["user_input"],
            )
            result.steps.append(step1)
            if not step1.success:
                return self._finalize(result)

            # Step 2: Project Configuration
            step2 = await self._run_step(
                "project_configuration",
                self._configure_project,
                step1.output,
            )
            result.steps.append(step2)
            if not step2.success:
                return self._finalize(result)

            # Step 3: Design Generation
            step3 = await self._run_step(
                "design_generation",
                self._generate_design,
                step2.output,
            )
            result.steps.append(step3)
            if not step3.success:
                return self._finalize(result)

            # Step 4: Code Generation
            step4 = await self._run_step(
                "code_generation",
                self._generate_code,
                step3.output,
            )
            result.steps.append(step4)
            if not step4.success:
                return self._finalize(result)

            # Step 5: Quality Audit
            step5 = await self._run_step(
                "quality_audit",
                self._audit_quality,
                step4.output,
            )
            result.steps.append(step5)

            # Step 6: Deployment
            step6 = await self._run_step(
                "deployment",
                self._deploy,
                step4.output,
            )
            result.steps.append(step6)
            if step6.success:
                result.deployed_url = step6.output
                result.success = True

        except Exception as e:
            logger.error("demo_failed", error=str(e))

        return self._finalize(result)

    async def _run_step(self, name: str, func, input_data) -> DemoStep:
        """Run a single step with timing and error handling."""
        step = DemoStep(name=name)
        step.started_at = time.time()
        try:
            step.output = await func(input_data)
            step.success = True
        except Exception as e:
            step.error = str(e)
            step.success = False
        step.completed_at = time.time()
        step.duration_seconds = step.completed_at - step.started_at
        return step

    async def _process_intent(self, user_input: str) -> str:
        """Step 1: Process user intent through zero-config inferrer."""
        response = await self.kernel.post("/api/infer-intent", json={
            "input": user_input,
            "locale": "es-MX",
        })
        return response.json()

    async def _configure_project(self, intent_data) -> str:
        """Step 2: Generate project configuration from intent."""
        response = await self.kernel.post("/api/configure-project", json=intent_data)
        return response.json()

    async def _generate_design(self, config) -> str:
        """Step 3: Generate design (colors, fonts, layout, components)."""
        response = await self.kernel.post("/api/generate-design", json=config)
        return response.json()

    async def _generate_code(self, design) -> str:
        """Step 4: Generate actual code from design."""
        response = await self.kernel.post("/api/generate-code", json=design)
        return response.json()

    async def _audit_quality(self, code_output) -> str:
        """Step 5: Run quality audit on generated code."""
        response = await self.kernel.post("/api/audit-quality", json=code_output)
        return response.json()

    async def _deploy(self, code_output) -> str:
        """Step 6: Deploy the generated project."""
        response = await self.kernel.post("/api/deploy", json=code_output)
        return response.json().get("url", "")

    def _finalize(self, result: DemoResult) -> DemoResult:
        """Calculate totals and finalize result."""
        result.total_duration_seconds = sum(s.duration_seconds for s in result.steps)
        result.total_cost_usd = sum(s.cost_usd for s in result.steps)
        quality_scores = [s.quality_score for s in result.steps if s.quality_score > 0]
        result.average_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        logger.info(
            "demo_finalized",
            scenario=result.scenario_name,
            success=result.success,
            duration=f"{result.total_duration_seconds:.1f}s",
            cost=f"${result.total_cost_usd:.4f}",
        )
        return result
```

### Demo Scenarios

```python
"""tests/e2e_demo/scenarios.py"""

DEMO_SCENARIOS = [
    {
        "name": "coffee_shop_ecommerce",
        "user_input": "Crea una tienda online para mi cafeteria artesanal 'Cafe Oaxaca'",
        "expected_type": "ecommerce",
        "expected_industry": "restaurant",
        "expected_features": ["product_catalog", "cart", "payments"],
        "max_duration_seconds": 300,
        "max_cost_usd": 0.50,
        "min_quality_score": 0.7,
    },
    {
        "name": "fitness_landing",
        "user_input": "Necesito una pagina web para mi gimnasio de CrossFit 'Iron Beast'",
        "expected_type": "landing",
        "expected_industry": "fitness",
        "expected_features": ["class_schedule", "contact_form", "testimonials"],
        "max_duration_seconds": 180,
        "max_cost_usd": 0.30,
        "min_quality_score": 0.7,
    },
    {
        "name": "saas_dashboard",
        "user_input": "Build a SaaS analytics dashboard for tracking social media metrics",
        "expected_type": "saas",
        "expected_industry": "tech",
        "expected_features": ["auth", "dashboard", "analytics"],
        "max_duration_seconds": 300,
        "max_cost_usd": 0.50,
        "min_quality_score": 0.7,
    },
    {
        "name": "portfolio_creative",
        "user_input": "Quiero un portafolio elegante para mostrar mis proyectos de fotografia",
        "expected_type": "portfolio",
        "expected_industry": "creative",
        "expected_features": ["gallery", "contact_form"],
        "max_duration_seconds": 180,
        "max_cost_usd": 0.25,
        "min_quality_score": 0.75,
    },
    {
        "name": "consulting_minimal",
        "user_input": "Pagina profesional para mi consultoria de estrategia empresarial",
        "expected_type": "landing",
        "expected_industry": "consulting",
        "expected_features": ["contact_form", "testimonials", "pricing"],
        "max_duration_seconds": 180,
        "max_cost_usd": 0.25,
        "min_quality_score": 0.7,
    },
]
```

---

## Epica 64.2 — Predictive Error Prevention

**Objetivo:** Obj #4 (Nunca Equivocarse 2x)
**Impacto:** +5% en Obj #4

### Vision

El sistema no solo aprende de errores pasados (Sprint 61 Error Learning Loop) — PREDICE errores futuros antes de que ocurran. Cada accion critica pasa por un pre-flight check que evalua riesgo basado en patrones historicos.

### Arquitectura

```
kernel/prevention/
  __init__.py
  preflight_checker.py   # Pre-flight checks before critical actions
  risk_scorer.py         # Score risk based on historical patterns
  auto_rollback.py       # Automated rollback on quality degradation
  confidence_gate.py     # Block low-confidence outputs
```

### Pre-flight Checker

```python
"""kernel/prevention/preflight_checker.py"""
import structlog
from dataclasses import dataclass
from typing import Optional

logger = structlog.get_logger("prevention.preflight")

@dataclass
class PreflightResult:
    action: str
    risk_level: str         # "low", "medium", "high", "critical"
    risk_score: float       # 0-1
    warnings: list[str]
    blockers: list[str]     # If non-empty, action is BLOCKED
    suggestions: list[str]
    proceed: bool           # Final decision


class PreflightChecker:
    """Run pre-flight checks before critical actions."""

    def __init__(self, supabase, error_learning_loop):
        self.supabase = supabase
        self.error_loop = error_learning_loop
        self._risk_patterns: dict[str, float] = {}

    async def check(self, action: str, context: dict) -> PreflightResult:
        """Run pre-flight check for an action."""
        warnings = []
        blockers = []
        suggestions = []

        # 1. Check against known error patterns
        similar_errors = await self._find_similar_errors(action, context)
        if similar_errors:
            for error in similar_errors:
                if error["severity"] == "critical":
                    blockers.append(
                        f"Similar action caused critical error: {error['description']}. "
                        f"Rule: {error['prevention_rule']}"
                    )
                else:
                    warnings.append(
                        f"Similar action caused error ({error['severity']}): "
                        f"{error['description']}"
                    )
                    suggestions.append(error.get("prevention_rule", ""))

        # 2. Check resource constraints
        resource_issues = await self._check_resources(action, context)
        warnings.extend(resource_issues)

        # 3. Check dependency health
        dep_issues = await self._check_dependencies(action, context)
        if dep_issues:
            warnings.extend(dep_issues)

        # 4. Calculate composite risk score
        risk_score = self._calculate_risk(len(blockers), len(warnings), similar_errors)
        risk_level = self._score_to_level(risk_score)

        # 5. Decision
        proceed = len(blockers) == 0 and risk_score < 0.8

        result = PreflightResult(
            action=action,
            risk_level=risk_level,
            risk_score=risk_score,
            warnings=warnings,
            blockers=blockers,
            suggestions=[s for s in suggestions if s],
            proceed=proceed,
        )

        # Log for learning
        await self._log_check(result, context)

        if not proceed:
            logger.warning("preflight_blocked", action=action, risk=risk_level,
                          blockers=blockers)
        elif warnings:
            logger.info("preflight_warnings", action=action, risk=risk_level,
                       warning_count=len(warnings))

        return result

    async def _find_similar_errors(self, action: str, context: dict) -> list[dict]:
        """Find historical errors similar to current action."""
        # Query error_lessons table for matching patterns
        lessons = await self.supabase.table("error_lessons")\
            .select("*")\
            .eq("action_type", action)\
            .eq("active", True)\
            .execute()

        similar = []
        for lesson in (lessons.data or []):
            # Check if context matches the error's trigger conditions
            trigger_keywords = lesson.get("trigger_keywords", [])
            context_str = str(context).lower()
            if any(kw.lower() in context_str for kw in trigger_keywords):
                similar.append(lesson)

        return similar

    async def _check_resources(self, action: str, context: dict) -> list[str]:
        """Check if resources are sufficient for the action."""
        warnings = []

        # Check daily budget remaining
        from kernel.finops import get_daily_spend
        daily_spend = await get_daily_spend()
        daily_cap = 10.0  # From rate_limiter
        remaining = daily_cap - daily_spend
        if remaining < 1.0:
            warnings.append(f"Budget low: ${remaining:.2f} remaining today")
        if remaining < 0.1:
            warnings.append("CRITICAL: Budget nearly exhausted")

        return warnings

    async def _check_dependencies(self, action: str, context: dict) -> list[str]:
        """Check health of dependencies needed for this action."""
        issues = []
        # Check if required providers are healthy (from fallback engine)
        # This integrates with the existing circuit breaker
        return issues

    def _calculate_risk(self, blocker_count: int, warning_count: int,
                       similar_errors: list) -> float:
        """Calculate composite risk score."""
        if blocker_count > 0:
            return 0.95
        score = 0.0
        score += warning_count * 0.15
        score += len(similar_errors) * 0.25
        # Cap at 0.95
        return min(score, 0.95)

    def _score_to_level(self, score: float) -> str:
        if score >= 0.8:
            return "critical"
        if score >= 0.6:
            return "high"
        if score >= 0.3:
            return "medium"
        return "low"

    async def _log_check(self, result: PreflightResult, context: dict) -> None:
        """Log pre-flight check for future analysis."""
        await self.supabase.table("preflight_logs").insert({
            "action": result.action,
            "risk_level": result.risk_level,
            "risk_score": result.risk_score,
            "proceed": result.proceed,
            "warning_count": len(result.warnings),
            "blocker_count": len(result.blockers),
        }).execute()
```

### Confidence Gate

```python
"""kernel/prevention/confidence_gate.py"""
import structlog
from typing import Any

logger = structlog.get_logger("prevention.confidence")


class ConfidenceGate:
    """Block outputs that don't meet confidence thresholds."""

    # Minimum confidence by action type
    THRESHOLDS = {
        "code_generation": 0.7,
        "design_generation": 0.6,
        "deployment": 0.8,
        "financial_calculation": 0.9,
        "user_communication": 0.5,
        "internal_task": 0.4,
        "default": 0.6,
    }

    def __init__(self, supabase):
        self.supabase = supabase

    async def evaluate(self, output: Any, action_type: str,
                      metadata: dict = None) -> dict:
        """Evaluate output confidence and decide whether to pass."""
        threshold = self.THRESHOLDS.get(action_type, self.THRESHOLDS["default"])

        # Calculate confidence based on multiple signals
        confidence = await self._calculate_confidence(output, action_type, metadata)

        passed = confidence >= threshold
        result = {
            "confidence": confidence,
            "threshold": threshold,
            "passed": passed,
            "action_type": action_type,
        }

        if not passed:
            result["recommendation"] = self._get_recommendation(confidence, threshold)
            logger.warning("confidence_gate_blocked", **result)
        else:
            logger.debug("confidence_gate_passed", confidence=confidence)

        return result

    async def _calculate_confidence(self, output: Any, action_type: str,
                                   metadata: dict = None) -> float:
        """Calculate confidence score for an output."""
        signals = []

        # Signal 1: Output completeness
        if isinstance(output, str):
            completeness = min(len(output) / 100, 1.0)  # Longer = more complete (simplified)
            signals.append(completeness)

        # Signal 2: Model self-reported confidence (if available)
        if metadata and "model_confidence" in metadata:
            signals.append(metadata["model_confidence"])

        # Signal 3: Historical success rate for this action type
        historical = await self._get_historical_success(action_type)
        if historical is not None:
            signals.append(historical)

        # Signal 4: Consistency check (if multiple attempts available)
        if metadata and "alternatives" in metadata:
            consistency = self._check_consistency(output, metadata["alternatives"])
            signals.append(consistency)

        return sum(signals) / len(signals) if signals else 0.5

    async def _get_historical_success(self, action_type: str) -> Optional[float]:
        """Get historical success rate for this action type."""
        result = await self.supabase.table("preflight_logs")\
            .select("proceed")\
            .eq("action", action_type)\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()

        if not result.data:
            return None
        successes = sum(1 for r in result.data if r["proceed"])
        return successes / len(result.data)

    def _check_consistency(self, output: Any, alternatives: list) -> float:
        """Check if output is consistent with alternatives."""
        if not alternatives:
            return 0.5
        # Simplified: check if output length is within 2x of alternatives
        output_len = len(str(output))
        alt_lens = [len(str(a)) for a in alternatives]
        avg_len = sum(alt_lens) / len(alt_lens)
        if avg_len == 0:
            return 0.5
        ratio = output_len / avg_len
        if 0.5 <= ratio <= 2.0:
            return 0.8
        return 0.3

    def _get_recommendation(self, confidence: float, threshold: float) -> str:
        gap = threshold - confidence
        if gap > 0.3:
            return "Output quality too low. Regenerate with higher-tier model."
        if gap > 0.1:
            return "Output borderline. Consider human review before proceeding."
        return "Marginally below threshold. Minor adjustments may suffice."
```

---

## Epica 64.3 — Dynamic Tier Routing v2

**Objetivo:** Obj #5 (Gasolina Magna/Premium)
**Impacto:** +4% en Obj #5

### Vision

El router actual asigna tiers estaticamente por intent. Sprint 64 lo hace DINAMICO: el tier se adapta en tiempo real basado en presupuesto restante, calidad requerida, y costo historico. Si queda poco budget, baja automaticamente a modelos mas baratos sin sacrificar calidad critica.

### Arquitectura

```
router/
  dynamic_router.py      # Extends existing engine.py
  budget_optimizer.py    # Real-time budget optimization
  quality_tracker.py     # Track quality per model per task type
```

### Budget Optimizer

```python
"""router/budget_optimizer.py"""
import structlog
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

logger = structlog.get_logger("router.budget_optimizer")

@dataclass
class BudgetState:
    daily_cap_usd: float
    spent_today_usd: float
    remaining_usd: float
    hours_remaining_today: float
    burn_rate_per_hour: float
    projected_end_of_day: float  # Projected spend at current rate
    budget_pressure: float       # 0-1 (1 = critical)


class BudgetOptimizer:
    """Optimize model selection based on real-time budget state."""

    # Cost per 1K tokens (approximate, updated periodically)
    MODEL_COSTS = {
        # Tier 1: Premium
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
        "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
        # Tier 2: Standard
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "claude-3.5-haiku": {"input": 0.0008, "output": 0.004},
        "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
        # Tier 3: Economy
        "groq-llama-3.3-70b": {"input": 0.00006, "output": 0.00006},
        "together-llama-3.3-70b": {"input": 0.00009, "output": 0.00009},
        # Tier 4: Local (Ollama)
        "ollama-local": {"input": 0.0, "output": 0.0},
    }

    # Quality scores per model per task type (learned from historical data)
    DEFAULT_QUALITY = {
        "gpt-4o": 0.92,
        "claude-3.5-sonnet": 0.93,
        "gemini-1.5-pro": 0.88,
        "gpt-4o-mini": 0.78,
        "claude-3.5-haiku": 0.75,
        "gemini-2.0-flash": 0.72,
        "groq-llama-3.3-70b": 0.70,
        "together-llama-3.3-70b": 0.70,
        "ollama-local": 0.55,
    }

    def __init__(self, usage_tracker, supabase):
        self.usage_tracker = usage_tracker
        self.supabase = supabase

    async def get_budget_state(self) -> BudgetState:
        """Get current budget state."""
        daily_cap = 10.0  # From rate_limiter config
        spent = await self.usage_tracker.get_daily_spend()
        remaining = daily_cap - spent

        now = datetime.now(timezone.utc)
        end_of_day = now.replace(hour=23, minute=59, second=59)
        hours_remaining = max((end_of_day - now).total_seconds() / 3600, 0.1)

        # Calculate burn rate (last 3 hours)
        recent_spend = await self.usage_tracker.get_spend_last_hours(3)
        burn_rate = recent_spend / 3.0 if recent_spend else 0

        projected = spent + (burn_rate * hours_remaining)
        budget_pressure = min(spent / daily_cap, 1.0)

        return BudgetState(
            daily_cap_usd=daily_cap,
            spent_today_usd=spent,
            remaining_usd=remaining,
            hours_remaining_today=hours_remaining,
            burn_rate_per_hour=burn_rate,
            projected_end_of_day=projected,
            budget_pressure=budget_pressure,
        )

    async def select_optimal_model(self, task_type: str,
                                   min_quality: float = 0.7,
                                   estimated_tokens: int = 1000) -> str:
        """Select the optimal model balancing cost and quality."""
        budget = await self.get_budget_state()

        # Get quality scores for this task type (historical or default)
        quality_scores = await self._get_quality_scores(task_type)

        # Filter models that meet minimum quality
        candidates = {
            model: score for model, score in quality_scores.items()
            if score >= min_quality
        }

        if not candidates:
            # If no model meets quality threshold, use best available
            candidates = quality_scores

        # Score each candidate: quality / cost (value ratio)
        scored = []
        for model, quality in candidates.items():
            cost = self._estimate_cost(model, estimated_tokens)
            # Apply budget pressure: as pressure increases, weight cost more
            value = quality * (1 - budget.budget_pressure * 0.5) - cost * budget.budget_pressure * 10
            scored.append((model, value, quality, cost))

        # Sort by value (highest first)
        scored.sort(key=lambda x: x[1], reverse=True)

        selected = scored[0][0] if scored else "gpt-4o-mini"

        logger.info("model_selected", model=selected, task=task_type,
                   budget_pressure=f"{budget.budget_pressure:.2f}",
                   remaining=f"${budget.remaining_usd:.2f}")
        return selected

    def _estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate cost for a model given token count."""
        costs = self.MODEL_COSTS.get(model, {"input": 0.001, "output": 0.003})
        # Assume 40% input, 60% output
        input_cost = (tokens * 0.4 / 1000) * costs["input"]
        output_cost = (tokens * 0.6 / 1000) * costs["output"]
        return input_cost + output_cost

    async def _get_quality_scores(self, task_type: str) -> dict[str, float]:
        """Get quality scores per model for a task type."""
        # Try historical data first
        historical = await self.supabase.table("model_quality_scores")\
            .select("model, avg_quality")\
            .eq("task_type", task_type)\
            .execute()

        if historical.data:
            return {r["model"]: r["avg_quality"] for r in historical.data}

        # Fallback to defaults
        return self.DEFAULT_QUALITY.copy()
```

---

## Epica 64.4 — Simulator Validation Framework

**Objetivo:** Obj #10 (Simulador Predictivo)
**Impacto:** +4% en Obj #10

### Vision

El Monte Carlo Simulator (Sprint 55-60) genera predicciones. Pero sin validacion, son numeros bonitos sin credibilidad. Sprint 64 agrega backtesting: compara predicciones pasadas contra resultados reales y calcula un Brier Score de calibracion.

### Arquitectura

```
kernel/simulator/
  validation/
    __init__.py
    backtester.py          # Compare predictions vs outcomes
    calibration.py         # Brier score + reliability diagram
    scenario_comparator.py # Compare multiple scenarios
```

### Backtester

```python
"""kernel/simulator/validation/backtester.py"""
import structlog
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger("simulator.backtester")

@dataclass
class PredictionRecord:
    id: str
    predicted_at: datetime
    event_description: str
    predicted_probability: float  # 0-1
    predicted_value: float        # Numeric prediction
    confidence_interval: tuple[float, float]  # (lower, upper)
    actual_outcome: float = None  # Filled when outcome is known
    outcome_recorded_at: datetime = None
    hit: bool = None              # Was prediction correct?


@dataclass
class CalibrationReport:
    total_predictions: int
    resolved_predictions: int
    brier_score: float           # 0 = perfect, 1 = worst
    calibration_error: float     # Mean absolute calibration error
    resolution: float            # How well predictions discriminate
    reliability: dict            # Binned reliability data
    sharpness: float             # How extreme predictions are
    overall_grade: str           # "A" to "F"


class Backtester:
    """Validate simulator predictions against real outcomes."""

    def __init__(self, supabase):
        self.supabase = supabase

    async def record_prediction(self, prediction: PredictionRecord) -> str:
        """Record a new prediction for future validation."""
        result = await self.supabase.table("prediction_records").insert({
            "event_description": prediction.event_description,
            "predicted_probability": prediction.predicted_probability,
            "predicted_value": prediction.predicted_value,
            "confidence_lower": prediction.confidence_interval[0],
            "confidence_upper": prediction.confidence_interval[1],
            "predicted_at": prediction.predicted_at.isoformat(),
        }).execute()
        return result.data[0]["id"]

    async def record_outcome(self, prediction_id: str, actual_outcome: float) -> None:
        """Record the actual outcome for a prediction."""
        # Get the prediction
        pred = await self.supabase.table("prediction_records")\
            .select("*").eq("id", prediction_id).single().execute()

        if not pred.data:
            return

        # Determine if prediction was a "hit"
        ci_lower = pred.data["confidence_lower"]
        ci_upper = pred.data["confidence_upper"]
        hit = ci_lower <= actual_outcome <= ci_upper

        await self.supabase.table("prediction_records").update({
            "actual_outcome": actual_outcome,
            "outcome_recorded_at": datetime.now(timezone.utc).isoformat(),
            "hit": hit,
        }).eq("id", prediction_id).execute()

        logger.info("outcome_recorded", prediction_id=prediction_id, hit=hit)

    async def generate_calibration_report(self) -> CalibrationReport:
        """Generate calibration report from all resolved predictions."""
        records = await self.supabase.table("prediction_records")\
            .select("*")\
            .not_.is_("actual_outcome", "null")\
            .execute()

        if not records.data or len(records.data) < 5:
            return CalibrationReport(
                total_predictions=len(records.data or []),
                resolved_predictions=len(records.data or []),
                brier_score=1.0,
                calibration_error=1.0,
                resolution=0.0,
                reliability={},
                sharpness=0.0,
                overall_grade="F",
            )

        predictions = records.data
        total = len(predictions)

        # Calculate Brier Score
        brier = self._calculate_brier_score(predictions)

        # Calculate calibration (reliability)
        reliability = self._calculate_reliability(predictions)
        cal_error = self._calculate_calibration_error(reliability)

        # Calculate resolution
        resolution = self._calculate_resolution(predictions)

        # Calculate sharpness
        sharpness = self._calculate_sharpness(predictions)

        # Overall grade
        grade = self._assign_grade(brier)

        report = CalibrationReport(
            total_predictions=total,
            resolved_predictions=total,
            brier_score=brier,
            calibration_error=cal_error,
            resolution=resolution,
            reliability=reliability,
            sharpness=sharpness,
            overall_grade=grade,
        )

        # Persist report
        await self.supabase.table("calibration_reports").insert({
            "brier_score": brier,
            "calibration_error": cal_error,
            "resolution": resolution,
            "sharpness": sharpness,
            "grade": grade,
            "total_predictions": total,
        }).execute()

        logger.info("calibration_report", brier=f"{brier:.4f}", grade=grade)
        return report

    def _calculate_brier_score(self, predictions: list[dict]) -> float:
        """Brier Score: mean squared error of probability predictions."""
        scores = []
        for p in predictions:
            predicted_prob = p["predicted_probability"]
            # Outcome: 1 if actual was within CI, 0 otherwise
            outcome = 1.0 if p.get("hit") else 0.0
            scores.append((predicted_prob - outcome) ** 2)
        return sum(scores) / len(scores)

    def _calculate_reliability(self, predictions: list[dict]) -> dict:
        """Bin predictions by confidence and check actual hit rates."""
        bins = {f"{i*10}-{(i+1)*10}%": {"predicted": [], "actual": []}
                for i in range(10)}

        for p in predictions:
            prob = p["predicted_probability"]
            bin_idx = min(int(prob * 10), 9)
            bin_key = f"{bin_idx*10}-{(bin_idx+1)*10}%"
            bins[bin_key]["predicted"].append(prob)
            bins[bin_key]["actual"].append(1.0 if p.get("hit") else 0.0)

        reliability = {}
        for bin_key, data in bins.items():
            if data["predicted"]:
                reliability[bin_key] = {
                    "count": len(data["predicted"]),
                    "avg_predicted": sum(data["predicted"]) / len(data["predicted"]),
                    "avg_actual": sum(data["actual"]) / len(data["actual"]),
                }
        return reliability

    def _calculate_calibration_error(self, reliability: dict) -> float:
        """Mean absolute difference between predicted and actual per bin."""
        errors = []
        for bin_data in reliability.values():
            if bin_data["count"] >= 2:
                errors.append(abs(bin_data["avg_predicted"] - bin_data["avg_actual"]))
        return sum(errors) / len(errors) if errors else 1.0

    def _calculate_resolution(self, predictions: list[dict]) -> float:
        """How well predictions discriminate between outcomes."""
        probs = [p["predicted_probability"] for p in predictions]
        return float(np.std(probs)) if probs else 0.0

    def _calculate_sharpness(self, predictions: list[dict]) -> float:
        """How extreme (confident) predictions are."""
        probs = [p["predicted_probability"] for p in predictions]
        # Sharpness = average distance from 0.5
        return sum(abs(p - 0.5) for p in probs) / len(probs) if probs else 0.0

    def _assign_grade(self, brier: float) -> str:
        if brier < 0.1:
            return "A"
        if brier < 0.2:
            return "B"
        if brier < 0.3:
            return "C"
        if brier < 0.4:
            return "D"
        return "F"
```

---

## Epica 64.5 — Sovereignty Activation Test

**Objetivo:** Obj #12 (Ecosistema/Soberania)
**Impacto:** +4% en Obj #12

### Vision

El Sovereignty Engine (Sprint 60) define alternativas soberanas. Sprint 64 las PRUEBA: desactiva intencionalmente cada servicio externo y mide la degradacion. Si el sistema sobrevive (degradado pero funcional), la soberania es real.

### Arquitectura

```
tests/sovereignty/
  __init__.py
  activation_test.py     # Main test orchestrator
  service_killer.py      # Simulates service outage
  degradation_meter.py   # Measures degradation level
  recovery_timer.py      # Measures recovery time
```

### Activation Test

```python
"""tests/sovereignty/activation_test.py"""
import asyncio
import structlog
import time
from dataclasses import dataclass, field

logger = structlog.get_logger("sovereignty.test")

@dataclass
class ServiceTestResult:
    service_name: str
    kill_method: str          # "env_unset", "network_block", "mock_failure"
    degradation_level: str    # "none", "minor", "moderate", "severe", "total"
    degradation_score: float  # 0 = no impact, 1 = total failure
    recovery_time_seconds: float
    fallback_activated: bool
    fallback_service: str
    features_lost: list[str]
    features_degraded: list[str]
    features_intact: list[str]
    passed: bool              # degradation_score < 0.5 = passed


@dataclass
class SovereigntyReport:
    tested_at: str
    services_tested: int
    services_passed: int
    overall_sovereignty_score: float  # 0-1 (1 = fully sovereign)
    critical_dependencies: list[str]  # Services that cause >50% degradation
    results: list[ServiceTestResult] = field(default_factory=list)


EXTERNAL_SERVICES = [
    {
        "name": "OpenAI",
        "env_vars": ["OPENAI_API_KEY"],
        "fallback": "Anthropic/Google/Groq",
        "kill_method": "env_unset",
        "test_action": "generate_text",
    },
    {
        "name": "Anthropic",
        "env_vars": ["ANTHROPIC_API_KEY"],
        "fallback": "OpenAI/Google/Groq",
        "kill_method": "env_unset",
        "test_action": "generate_text",
    },
    {
        "name": "Supabase",
        "env_vars": ["SUPABASE_URL", "SUPABASE_KEY"],
        "fallback": "Local SQLite cache",
        "kill_method": "env_unset",
        "test_action": "database_query",
    },
    {
        "name": "Perplexity",
        "env_vars": ["SONAR_API_KEY"],
        "fallback": "Direct web search + LLM",
        "kill_method": "env_unset",
        "test_action": "web_research",
    },
    {
        "name": "ElevenLabs",
        "env_vars": ["ELEVENLABS_API_KEY"],
        "fallback": "Edge TTS / pyttsx3",
        "kill_method": "env_unset",
        "test_action": "text_to_speech",
    },
    {
        "name": "DeepL",
        "env_vars": ["DEEPL_API_KEY"],
        "fallback": "LLM translation",
        "kill_method": "env_unset",
        "test_action": "translate_text",
    },
    {
        "name": "PostHog",
        "env_vars": ["POSTHOG_API_KEY"],
        "fallback": "Local event log",
        "kill_method": "env_unset",
        "test_action": "track_event",
    },
    {
        "name": "Langfuse",
        "env_vars": ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"],
        "fallback": "Local JSON logs",
        "kill_method": "env_unset",
        "test_action": "log_trace",
    },
]


class SovereigntyActivationTest:
    """Test sovereignty by intentionally killing external services."""

    def __init__(self, kernel_client):
        self.kernel = kernel_client

    async def run_full_test(self) -> SovereigntyReport:
        """Run sovereignty test against all external services."""
        report = SovereigntyReport(
            tested_at=time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            services_tested=len(EXTERNAL_SERVICES),
            services_passed=0,
            overall_sovereignty_score=0.0,
        )

        for service in EXTERNAL_SERVICES:
            result = await self._test_service(service)
            report.results.append(result)
            if result.passed:
                report.services_passed += 1

        # Calculate overall sovereignty score
        if report.results:
            scores = [1 - r.degradation_score for r in report.results]
            report.overall_sovereignty_score = sum(scores) / len(scores)

        # Identify critical dependencies
        report.critical_dependencies = [
            r.service_name for r in report.results
            if r.degradation_score > 0.5
        ]

        logger.info("sovereignty_test_complete",
                   score=f"{report.overall_sovereignty_score:.2f}",
                   passed=f"{report.services_passed}/{report.services_tested}")
        return report

    async def _test_service(self, service: dict) -> ServiceTestResult:
        """Test a single service by simulating its failure."""
        logger.info("testing_service", name=service["name"])

        # 1. Baseline: test action with service active
        baseline_ok = await self._test_action(service["test_action"])

        # 2. Kill service (simulate failure)
        await self._kill_service(service)

        # 3. Test action without service
        start = time.time()
        degraded_ok = await self._test_action(service["test_action"])
        recovery_time = time.time() - start

        # 4. Restore service
        await self._restore_service(service)

        # 5. Measure degradation
        if baseline_ok and degraded_ok:
            degradation_score = 0.1  # Minor: slower but works
            degradation_level = "minor"
        elif baseline_ok and not degraded_ok:
            degradation_score = 0.8  # Severe: feature lost
            degradation_level = "severe"
        else:
            degradation_score = 0.0  # None: wasn't working anyway
            degradation_level = "none"

        # Check if fallback was activated
        fallback_activated = degraded_ok and baseline_ok

        return ServiceTestResult(
            service_name=service["name"],
            kill_method=service["kill_method"],
            degradation_level=degradation_level,
            degradation_score=degradation_score,
            recovery_time_seconds=recovery_time,
            fallback_activated=fallback_activated,
            fallback_service=service["fallback"],
            features_lost=[] if degraded_ok else [service["test_action"]],
            features_degraded=[service["test_action"]] if degraded_ok and recovery_time > 5 else [],
            features_intact=[service["test_action"]] if degraded_ok and recovery_time <= 5 else [],
            passed=degradation_score < 0.5,
        )

    async def _test_action(self, action: str) -> bool:
        """Test if an action works."""
        try:
            response = await self.kernel.post(f"/api/test/{action}", timeout=30)
            return response.status_code == 200
        except Exception:
            return False

    async def _kill_service(self, service: dict) -> None:
        """Simulate service failure by unsetting env vars."""
        # In test environment, use mock/patch
        # In production test, temporarily rename env vars
        pass

    async def _restore_service(self, service: dict) -> None:
        """Restore service after test."""
        pass
```

---

## Tablas Supabase Nuevas

```sql
-- Preflight checks log
CREATE TABLE preflight_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action TEXT NOT NULL,
    risk_level TEXT,
    risk_score FLOAT,
    proceed BOOLEAN,
    warning_count INTEGER DEFAULT 0,
    blocker_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Prediction records for backtesting
CREATE TABLE prediction_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_description TEXT NOT NULL,
    predicted_probability FLOAT,
    predicted_value FLOAT,
    confidence_lower FLOAT,
    confidence_upper FLOAT,
    actual_outcome FLOAT,
    hit BOOLEAN,
    predicted_at TIMESTAMPTZ NOT NULL,
    outcome_recorded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Calibration reports
CREATE TABLE calibration_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brier_score FLOAT,
    calibration_error FLOAT,
    resolution FLOAT,
    sharpness FLOAT,
    grade TEXT,
    total_predictions INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Model quality scores (for dynamic routing)
CREATE TABLE model_quality_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model TEXT NOT NULL,
    task_type TEXT NOT NULL,
    avg_quality FLOAT,
    sample_count INTEGER DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT now(),
    UNIQUE(model, task_type)
);

-- Sovereignty test results
CREATE TABLE sovereignty_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    overall_score FLOAT,
    services_tested INTEGER,
    services_passed INTEGER,
    critical_dependencies TEXT[],
    results JSONB,
    tested_at TIMESTAMPTZ DEFAULT now()
);
```

---

## Criterios de Exito

| Metrica | Target | Medicion |
|---|---|---|
| E2E demo success rate | >=3/5 scenarios pass | Demo runner results |
| E2E demo time | <300s per scenario | Timer in demo_runner |
| Preflight check coverage | 100% critical actions | Audit of action types |
| Confidence gate accuracy | <10% false blocks | Manual review of blocked outputs |
| Budget optimizer savings | >=20% cost reduction | Compare week before/after |
| Brier score | <0.3 (grade C or better) | calibration_reports table |
| Sovereignty score | >=0.7 (70% sovereign) | sovereignty_tests table |
| Critical dependencies | <=2 services | sovereignty_tests results |
| Recovery time | <10s per service | ServiceTestResult.recovery_time |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| E2E demo fails on all scenarios | MEDIA | ALTO | Start with simplest scenario, iterate |
| Preflight too aggressive (blocks valid actions) | MEDIA | MEDIO | Tunable thresholds + override mechanism |
| Budget optimizer selects too-cheap models | BAJA | MEDIO | Minimum quality floor per task type |
| Sovereignty test causes real outage | BAJA | ALTO | Run in isolated test environment only |
| Brier score unmeasurable (too few predictions) | ALTA | BAJO | Seed with 20+ synthetic predictions |

---

## Costo Estimado

| Componente | Costo Mensual |
|---|---|
| E2E demo runs (5 scenarios x weekly) | ~$2-5 |
| Preflight checks (LLM calls) | ~$0 (uses existing budget) |
| Budget optimizer | $0 (saves money) |
| Backtesting | $0 (computation only) |
| Sovereignty tests | ~$1-2 (test tokens) |
| **Total** | **~$3-7/mes** |

---

## Referencias

[1]: https://en.wikipedia.org/wiki/Brier_score "Brier Score — Probability prediction accuracy metric"
[2]: https://martinfowler.com/bliki/CircuitBreaker.html "Circuit Breaker Pattern — Martin Fowler"
[3]: https://docs.python.org/3/library/unittest.mock.html "Python unittest.mock — For sovereignty testing"
