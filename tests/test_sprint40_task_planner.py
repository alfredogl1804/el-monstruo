"""
Tests Sprint 40 — Task Planner
==============================
Valida el Task Planner: creación de planes, detección de objetivos complejos,
ejecución de pasos, revisión de planes fallidos, y persistencia en Supabase.
"""
from __future__ import annotations

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from kernel.task_planner import TaskPlanner, TaskPlan, TaskStep, StepStatus, PlanStatus


# ── Helpers ──────────────────────────────────────────────────────────

def make_step(index: int, description: str = "Paso de prueba", tool_hint: str = "code_exec") -> TaskStep:
    """Create a TaskStep using the real API (no expected_output, no status in __init__)."""
    step = TaskStep(
        step_id=str(uuid4()),
        index=index,
        description=description,
        tool_hint=tool_hint,
    )
    return step


def make_step_with_status(index: int, status: StepStatus, description: str = "Paso") -> TaskStep:
    """Create a TaskStep and set its status manually."""
    step = make_step(index, description)
    step.status = status
    return step


# ── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def mock_kernel():
    """Mock del LangGraphKernel para tests — usa start_run como el planner real."""
    kernel = MagicMock()

    # El planner llama self._kernel.start_run(run_input) y espera result.response
    # La fase de planning espera JSON con {"steps": [...]}
    plan_json = json.dumps({
        "steps": [
            {"index": 0, "description": "Paso 1: Analizar el estado actual", "tool_hint": "browse_web", "depends_on": []},
            {"index": 1, "description": "Paso 2: Implementar la solución", "tool_hint": "code_exec", "depends_on": [0]},
            {"index": 2, "description": "Paso 3: Verificar y hacer commit", "tool_hint": "github", "depends_on": [1]},
        ],
        "rationale": "Plan de 3 pasos para el objetivo"
    })

    # Mock result object for planning phase
    plan_result = MagicMock()
    plan_result.response = plan_json
    plan_result.tokens_used = 300
    plan_result.cost_usd = 0.006

    # Mock result object for execution phase
    exec_result = MagicMock()
    exec_result.response = "Paso completado exitosamente."
    exec_result.tokens_used = 150
    exec_result.cost_usd = 0.003

    # start_run returns plan_result first (planning), then exec_result (execution)
    kernel.start_run = AsyncMock(side_effect=[plan_result, exec_result, exec_result, exec_result, exec_result, exec_result, exec_result, exec_result, exec_result, exec_result])
    return kernel


@pytest.fixture
def mock_db():
    """Mock del SupabaseClient para tests."""
    db = MagicMock()
    db.insert = AsyncMock(return_value={"plan_id": "test-plan-id"})
    db.update = AsyncMock(return_value=True)
    db.select = AsyncMock(return_value=[])
    db.upsert = AsyncMock(return_value=True)
    return db


@pytest.fixture
def planner(mock_kernel, mock_db):
    """TaskPlanner con dependencias mockeadas."""
    return TaskPlanner(kernel=mock_kernel, db=mock_db)


# ── Tests: Detección de objetivos complejos ──────────────────────────

class TestComplexObjectiveDetection:

    def test_simple_objective_not_complex(self, planner):
        """Objetivos simples no deben activar el Task Planner."""
        simple_objectives = [
            "¿Qué hora es?",
            "Hola",
            "¿Cómo estás?",
            "Dame el estado del sistema",
        ]
        for obj in simple_objectives:
            assert not planner.is_complex_objective(obj), f"'{obj}' debería ser simple"

    def test_long_complex_objective_detected(self, planner):
        """Objetivos largos con múltiples verbos deben activar el Task Planner."""
        complex_objectives = [
            # 2+ keywords: migra + verifica + persiste + supabase + redeploy
            "Migra LightRAG de /tmp a pgvector en Supabase y verifica que los datos persisten entre redeploys del servidor de producción",
            # 2+ keywords: crea + analiza + detecta + agrupa + envía
            "Crea un script que analice los logs de Railway, detecta errores recurrentes, los agrupa por tipo y envía un resumen por Telegram",
            # 2+ keywords: implementa + integra + despliega
            "Implementa el Task Planner, integra con el Embrión y despliega en Railway con tests",
        ]
        for obj in complex_objectives:
            assert planner.is_complex_objective(obj), f"'{obj}' debería ser complejo"

    def test_multi_step_keywords_trigger_complexity(self, planner):
        """Palabras clave multi-paso deben detectarse como complejas."""
        keywords_objectives = [
            "primero investiga X, luego implementa Y y finalmente despliega Z en producción",
            "paso 1: analiza el código, paso 2: implementa los cambios, paso 3: escribe los tests",
        ]
        for obj in keywords_objectives:
            assert planner.is_complex_objective(obj), f"'{obj}' debería ser complejo por keywords"


# ── Tests: Creación de planes ────────────────────────────────────────

class TestPlanCreation:

    @pytest.mark.asyncio
    async def test_plan_creates_steps(self, mock_db):
        """El plan debe crear al menos 2 pasos para un objetivo complejo."""
        # Create a fresh kernel mock for this test
        plan_json = json.dumps({
            "steps": [
                {"index": 0, "description": "Paso 1: Analizar", "tool_hint": "browse_web", "depends_on": []},
                {"index": 1, "description": "Paso 2: Implementar", "tool_hint": "code_exec", "depends_on": [0]},
            ],
            "rationale": "Plan de 2 pasos"
        })
        result = MagicMock()
        result.response = plan_json
        result.tokens_used = 200
        result.cost_usd = 0.004
        kernel = MagicMock()
        kernel.start_run = AsyncMock(return_value=result)
        p = TaskPlanner(kernel=kernel, db=mock_db)

        plan = await p.plan(
            objective="Migra LightRAG a pgvector en Supabase",
            context={"sprint": 40},
            user_id="test",
        )

        assert plan is not None
        assert len(plan.steps) >= 2
        assert plan.status in (PlanStatus.CREATED, PlanStatus.RUNNING)
        assert plan.objective == "Migra LightRAG a pgvector en Supabase"

    @pytest.mark.asyncio
    async def test_plan_has_unique_id(self, mock_db):
        """Cada plan debe tener un ID único."""
        plan_json = json.dumps({
            "steps": [{"index": 0, "description": "Paso", "tool_hint": "code_exec", "depends_on": []}]
        })
        result = MagicMock()
        result.response = plan_json
        result.tokens_used = 100
        result.cost_usd = 0.002
        kernel = MagicMock()
        kernel.start_run = AsyncMock(return_value=result)
        p = TaskPlanner(kernel=kernel, db=mock_db)

        plan1 = await p.plan("Objetivo 1 con múltiples pasos", user_id="test")
        plan2 = await p.plan("Objetivo 2 con múltiples pasos", user_id="test")

        assert plan1.plan_id != plan2.plan_id

    @pytest.mark.asyncio
    async def test_plan_fallback_on_invalid_json(self, mock_db):
        """Si el LLM devuelve JSON inválido, debe usar el plan de fallback."""
        result = MagicMock()
        result.response = "No puedo crear un plan ahora mismo."
        result.tokens_used = 50
        result.cost_usd = 0.001
        kernel = MagicMock()
        kernel.start_run = AsyncMock(return_value=result)
        p = TaskPlanner(kernel=kernel, db=mock_db)

        plan = await p.plan(
            objective="Objetivo complejo de prueba con múltiples pasos",
            user_id="test",
        )

        # Debe crear un plan de fallback con al menos 1 paso
        assert plan is not None
        assert len(plan.steps) >= 1


# ── Tests: TaskStep API ──────────────────────────────────────────────

class TestTaskStepAPI:

    def test_step_default_status_is_pending(self):
        """El estado por defecto de un TaskStep debe ser PENDING."""
        step = make_step(0)
        assert step.status == StepStatus.PENDING

    def test_step_status_can_be_set(self):
        """El estado de un TaskStep puede cambiarse."""
        step = make_step(0)
        step.status = StepStatus.DONE
        assert step.status == StepStatus.DONE

    def test_step_to_dict_has_required_fields(self):
        """to_dict de TaskStep debe incluir los campos requeridos."""
        step = make_step(0, "Test step", "code_exec")
        d = step.to_dict()
        required = ["step_id", "index", "description", "tool_hint", "status"]
        for field in required:
            assert field in d, f"Campo '{field}' faltante en TaskStep.to_dict()"


# ── Tests: TaskPlan.to_dict ──────────────────────────────────────────

class TestTaskPlanSerialization:

    def test_to_dict_has_required_fields(self):
        """to_dict debe incluir todos los campos requeridos."""
        plan = TaskPlan(
            plan_id="test-id",
            objective="Test objective",
            steps=[make_step(0, "Step 1", "code_exec")],
        )

        d = plan.to_dict()

        required_fields = ["plan_id", "objective", "status", "steps", "progress_pct", "total_steps"]
        for field in required_fields:
            assert field in d, f"Campo '{field}' faltante en to_dict()"

    def test_progress_pct_calculation(self):
        """progress_pct debe calcularse correctamente."""
        steps = [
            make_step_with_status(0, StepStatus.DONE, "S1"),
            make_step_with_status(1, StepStatus.DONE, "S2"),
            make_step_with_status(2, StepStatus.PENDING, "S3"),
            make_step_with_status(3, StepStatus.PENDING, "S4"),
        ]
        plan = TaskPlan(
            plan_id="test-id",
            objective="Test",
            steps=steps,
        )
        plan.status = PlanStatus.RUNNING

        d = plan.to_dict()
        assert d["progress_pct"] == 50.0
        assert d["done_steps"] == 2
        assert d["total_steps"] == 4

    def test_step_status_values(self):
        """StepStatus debe tener los valores esperados."""
        assert StepStatus.PENDING == "pending"
        assert StepStatus.RUNNING == "running"
        assert StepStatus.DONE == "done"
        assert StepStatus.FAILED == "failed"
        assert StepStatus.SKIPPED == "skipped"

    def test_plan_status_values(self):
        """PlanStatus debe tener los valores esperados."""
        assert PlanStatus.CREATED == "created"
        assert PlanStatus.RUNNING == "running"
        assert PlanStatus.DONE == "done"
        assert PlanStatus.FAILED == "failed"


# ── Tests: Persistencia ──────────────────────────────────────────────

class TestPlanPersistence:

    @pytest.mark.asyncio
    async def test_plan_created_with_valid_id(self, mock_db):
        """El plan debe crearse con un ID válido."""
        result = MagicMock()
        result.response = json.dumps({"steps": [{"index": 0, "description": "Paso", "tool_hint": "code_exec", "depends_on": []}]})
        result.tokens_used = 50
        result.cost_usd = 0.001
        kernel = MagicMock()
        kernel.start_run = AsyncMock(return_value=result)
        p = TaskPlanner(kernel=kernel, db=mock_db)

        plan = await p.plan("Objetivo para persistir", user_id="test")
        assert plan is not None
        assert plan.plan_id is not None
        assert len(plan.plan_id) > 0

    def test_get_active_plans(self, planner):
        """get_active_plans debe retornar lista."""
        plans = planner.get_active_plans()
        assert isinstance(plans, list)

    def test_get_plan_not_found(self, planner):
        """get_plan con ID inexistente debe retornar None."""
        plan = planner.get_plan("non-existent-id")
        assert plan is None

    @pytest.mark.asyncio
    async def test_plan_registered_in_active_plans(self, mock_db):
        """Después de crear un plan, debe aparecer en get_active_plans."""
        result = MagicMock()
        result.response = json.dumps({"steps": [{"index": 0, "description": "Paso", "tool_hint": "code_exec", "depends_on": []}]})
        result.tokens_used = 50
        result.cost_usd = 0.001
        kernel = MagicMock()
        kernel.start_run = AsyncMock(return_value=result)
        p = TaskPlanner(kernel=kernel, db=mock_db)

        plan = await p.plan("Objetivo para registrar", user_id="test")
        found = p.get_plan(plan.plan_id)
        assert found is not None
        assert found.plan_id == plan.plan_id


# ── Tests: Revisión de planes ────────────────────────────────────────

class TestPlanRevision:

    @pytest.mark.asyncio
    async def test_plan_revision_increments_count(self, mock_db):
        """La revisión de un plan debe incrementar revision_count."""
        # Build a plan with a failed step
        failed_step = make_step_with_status(0, StepStatus.FAILED, "Paso fallido")
        failed_step.error = "Error: timeout"

        # Mock kernel that returns a valid revision JSON
        revision_json = json.dumps({
            "steps": [
                {"index": 1, "description": "Paso revisado: enfoque alternativo", "tool_hint": "browse_web", "depends_on": []},
            ],
            "rationale": "Enfoque alternativo"
        })
        revision_result = MagicMock()
        revision_result.response = revision_json
        revision_result.tokens_used = 150
        revision_result.cost_usd = 0.003
        kernel = MagicMock()
        kernel.start_run = AsyncMock(return_value=revision_result)

        # Add a PENDING step so _revise_plan has something to revise
        pending_step = make_step_with_status(1, StepStatus.PENDING, "Paso pendiente")

        plan = TaskPlan(
            plan_id=str(uuid4()),
            objective="Objetivo que falló",
            steps=[failed_step, pending_step],
        )
        plan.status = PlanStatus.FAILED
        plan.inject_kernel(kernel)  # Inject kernel into plan for _revise_plan

        p = TaskPlanner(kernel=kernel, db=mock_db)
        revised_plan = await p.revise(plan, failed_step_index=0)

        assert revised_plan is not None
        assert revised_plan.revision_count >= 1


# ── Tests: Integración con embrion_loop ─────────────────────────────

class TestEmbrionLoopIntegration:

    def test_task_planner_importable_from_kernel(self):
        """TaskPlanner debe ser importable desde kernel.task_planner."""
        assert TaskPlanner is not None
        assert TaskPlan is not None
        assert TaskStep is not None
        assert StepStatus is not None
        assert PlanStatus is not None

    def test_planner_routes_importable(self):
        """planner_routes debe ser importable."""
        from kernel.planner_routes import router
        assert router is not None

    def test_planner_routes_has_endpoints(self):
        """planner_routes debe tener los endpoints esperados."""
        from kernel.planner_routes import router
        paths = [route.path for route in router.routes]
        # Al menos uno de los paths esperados debe existir
        expected = ["/plan", "/plans", "/plan_and_run", "/history"]
        found = any(any(e in p for e in expected) for p in paths)
        assert found, f"No se encontraron endpoints esperados. Paths: {paths}"

    def test_embrion_loop_imports_task_planner(self):
        """embrion_loop.py debe referenciar TaskPlanner."""
        import kernel.embrion_loop as el
        import inspect
        source = inspect.getsource(el)
        assert "TaskPlanner" in source, "embrion_loop no referencia TaskPlanner"
        assert "is_complex_objective" in source, "embrion_loop no llama is_complex_objective"
