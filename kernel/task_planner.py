"""
El Monstruo — Task Planner (Sprint 40)
=======================================
Gives the Embrión the ability to decompose complex objectives into
executable sub-tasks using the ReAct (Reason + Act) pattern.

Architecture:
    TaskPlanner.plan(objective) → TaskPlan
    TaskPlan.execute()          → iterates sub-tasks with ReAct loop
    TaskPlan.revise()           → re-plans if a step fails

Patterns used:
    - Plan-and-Execute: generate full plan first, then execute step by step
    - ReAct: Reason → Act → Observe → Reason loop per step
    - Self-correction: if a step fails, revise the remaining plan

Integration:
    - EmbrionLoop._think() detects complex objectives and delegates to TaskPlanner
    - AutonomousRunner can create TaskPlans for multi-step scheduled jobs
    - Results stored in task_plans table (Supabase) for observability

Cost model:
    - Plan generation: ~$0.05 (one LLM call, gpt-5)
    - Per step execution: ~$0.05-0.15 (depends on tools used)
    - Revision: ~$0.03 (one LLM call, gpt-5)
    - Max steps: 10 per plan (configurable)
    - Hard budget: $1.00 per plan (configurable)

Sprint 40: The Embrión gains the ability to plan.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncIterator, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("kernel.task_planner")

# ── Configuration ────────────────────────────────────────────────────
PLANNER_MODEL = os.environ.get("PLANNER_MODEL", "gpt-5.5")
EXECUTOR_MODEL = os.environ.get("EXECUTOR_MODEL", "gpt-5.5")
MAX_STEPS = int(os.environ.get("PLANNER_MAX_STEPS", "10"))
MAX_RETRIES_PER_STEP = int(os.environ.get("PLANNER_MAX_RETRIES", "2"))
PLAN_BUDGET_USD = float(os.environ.get("PLANNER_BUDGET_USD", "1.0"))
STEP_TIMEOUT_S = int(os.environ.get("PLANNER_STEP_TIMEOUT", "120"))

# ── Sprint 46.3: Stuck Detection ────────────────────────────────────
MAX_REACT_LOOPS = int(os.environ.get("PLANNER_MAX_REACT_LOOPS", "5"))  # Up from 3
STUCK_DETECTION_THRESHOLD = 3  # Same tool called 3x with same args = stuck
MAX_TOTAL_TOOL_CALLS_PER_STEP = 12  # Hard cap per step
MAX_PLAN_DURATION_S = 300  # 5 minutes max for entire plan


# ── Data Models ──────────────────────────────────────────────────────
class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskStep:
    """A single step in a task plan."""

    def __init__(
        self,
        step_id: str,
        index: int,
        description: str,
        tool_hint: Optional[str] = None,
        depends_on: Optional[list[int]] = None,
    ):
        self.step_id = step_id
        self.index = index
        self.description = description
        self.tool_hint = tool_hint  # Suggested tool (github, code_exec, browse_web, etc.)
        self.depends_on = depends_on or []
        self.status = StepStatus.PENDING
        self.result: Optional[str] = None
        self.error: Optional[str] = None
        self.retries = 0
        self.started_at: Optional[float] = None
        self.finished_at: Optional[float] = None
        self.tokens_used = 0
        self.cost_usd = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "index": self.index,
            "description": self.description,
            "tool_hint": self.tool_hint,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "result": self.result[:500] if self.result else None,
            "error": self.error,
            "retries": self.retries,
            "duration_s": round(self.finished_at - self.started_at, 2) if self.finished_at and self.started_at else None,
            "tokens_used": self.tokens_used,
            "cost_usd": round(self.cost_usd, 4),
        }


class PlanStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVISED = "revised"


class TaskPlan:
    """
    A complete plan for achieving an objective.
    Contains ordered steps and tracks execution state.
    """

    def __init__(
        self,
        plan_id: str,
        objective: str,
        steps: list[TaskStep],
        context: Optional[dict[str, Any]] = None,
    ):
        self.plan_id = plan_id
        self.objective = objective
        self.steps = steps
        self.context = context or {}
        self.status = PlanStatus.CREATED
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.started_at: Optional[str] = None
        self.finished_at: Optional[str] = None
        self.total_tokens = 0
        self.total_cost_usd = 0.0
        self.total_tool_calls = 0  # Sprint 43: track actual tool executions
        self.revision_count = 0
        self.final_summary: Optional[str] = None
        self._kernel: Optional[Any] = None  # Injected at execution time

    def inject_kernel(self, kernel: Any) -> None:
        self._kernel = kernel

    @property
    def pending_steps(self) -> list[TaskStep]:
        return [s for s in self.steps if s.status == StepStatus.PENDING]

    @property
    def done_steps(self) -> list[TaskStep]:
        return [s for s in self.steps if s.status == StepStatus.DONE]

    @property
    def failed_steps(self) -> list[TaskStep]:
        return [s for s in self.steps if s.status == StepStatus.FAILED]

    @property
    def progress_pct(self) -> float:
        if not self.steps:
            return 0.0
        done = len([s for s in self.steps if s.status in (StepStatus.DONE, StepStatus.SKIPPED)])
        return round(done / len(self.steps) * 100, 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "objective": self.objective[:200],
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "progress_pct": self.progress_pct,
            "total_steps": len(self.steps),
            "done_steps": len(self.done_steps),
            "failed_steps": len(self.failed_steps),
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "total_tool_calls": self.total_tool_calls,  # Sprint 43
            "revision_count": self.revision_count,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "final_summary": self.final_summary,
            "context": self.context,
        }


# ── Task Planner ─────────────────────────────────────────────────────
class TaskPlanner:
    """
    Decomposes complex objectives into executable sub-tasks.

    Usage:
        planner = TaskPlanner(kernel=kernel_instance)
        plan = await planner.plan("Construir el módulo X con tests y PR")
        result = await planner.execute(plan)
    """

    def __init__(self, kernel: Any, db: Optional[Any] = None):
        self._kernel = kernel
        self._db = db  # Optional Supabase client for persistence
        self._active_plans: dict[str, TaskPlan] = {}

    async def plan(
        self,
        objective: str,
        context: Optional[dict[str, Any]] = None,
        user_id: str = "embrion",
        max_steps: int = MAX_STEPS,
    ) -> TaskPlan:
        """
        Generate a TaskPlan for the given objective.
        Uses LLM to decompose the objective into ordered steps.
        """
        plan_id = str(uuid4())
        logger.info("task_planner_planning", plan_id=plan_id, objective=objective[:100])

        # ── Build planning prompt ────────────────────────────────────
        available_tools = [
            "code_exec — ejecutar código Python/shell en sandbox E2B persistente",
            "file_ops — crear, leer, editar, listar archivos en sandbox E2B persistente",
            "web_dev — scaffold (crear proyecto React+Vite), build (compilar), deploy (desplegar a Vercel)",
            "github — crear branches, archivos, pull requests",
            "browse_web — navegar URLs y extraer contenido",
            "web_search — buscar en internet",
            "manus_bridge — delegar tarea compleja a Manus",
            "ingest_knowledge — agregar documento al knowledge graph",
            "query_knowledge — consultar el knowledge graph",
            "send_message — enviar mensaje a Alfredo",
        ]

        tools_str = "\n".join(f"  - {t}" for t in available_tools)
        context_str = json.dumps(context or {}, ensure_ascii=False)[:500]

        planning_prompt = f"""Eres el planificador del Embrión IA. Tu trabajo es descomponer un objetivo complejo en pasos ejecutables.

OBJETIVO: {objective}

CONTEXTO: {context_str}

HERRAMIENTAS DISPONIBLES:
{tools_str}

INSTRUCCIONES:
1. Descompón el objetivo en máximo {max_steps} pasos concretos y ejecutables
2. Cada paso debe ser atómico (una sola acción)
3. Indica qué herramienta usar en cada paso (tool_hint)
4. Indica dependencias entre pasos si las hay (depends_on: lista de índices)
5. Los pasos deben estar en orden lógico de ejecución

RESPONDE ÚNICAMENTE con un JSON válido en este formato exacto:
{{
  "steps": [
    {{
      "index": 0,
      "description": "Descripción clara y específica del paso",
      "tool_hint": "nombre_de_la_herramienta",
      "depends_on": []
    }},
    {{
      "index": 1,
      "description": "Siguiente paso",
      "tool_hint": "nombre_de_la_herramienta",
      "depends_on": [0]
    }}
  ],
  "rationale": "Breve explicación de la estrategia del plan"
}}

No incluyas texto fuera del JSON. Solo el JSON."""

        try:
            # Sprint 41 FIX v3: usar Anthropic Claude con system prompt JSON-only
            # (OpenAI quota excedida en Railway — Claude-opus-4-7 es el modelo activo)
            import os
            import anthropic

            system_json = """Eres el planificador del Embrion IA. RESPONDE UNICAMENTE con JSON valido.
No incluyas texto fuera del JSON. No uses markdown. Solo el objeto JSON puro.
Formato obligatorio:
{"steps":[{"index":0,"description":"...","tool_hint":"...","depends_on":[]}],"rationale":"..."}"""

            anthropic_client = anthropic.AsyncAnthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY", "")
            )
            msg = await asyncio.wait_for(
                anthropic_client.messages.create(
                    model="claude-opus-4-7",
                    max_tokens=2000,
                    system=system_json,
                    messages=[{"role": "user", "content": planning_prompt}],
                ),
                timeout=90,
            )
            response_text = msg.content[0].text if msg.content else ""

            # Parse JSON response
            steps_data = self._parse_plan_response(response_text)
            steps = [
                TaskStep(
                    step_id=str(uuid4()),
                    index=s["index"],
                    description=s["description"],
                    tool_hint=s.get("tool_hint"),
                    depends_on=s.get("depends_on", []),
                )
                for s in steps_data
            ]

            plan = TaskPlan(
                plan_id=plan_id,
                objective=objective,
                steps=steps,
                context=context or {},
            )
            plan.inject_kernel(self._kernel)

            self._active_plans[plan_id] = plan
            logger.info(
                "task_planner_plan_created",
                plan_id=plan_id,
                steps=len(steps),
                objective=objective[:80],
            )

            # Persist to DB if available
            await self._persist_plan(plan)

            return plan

        except Exception as e:
            logger.error("task_planner_plan_failed", error=str(e), objective=objective[:80])
            # Return a minimal single-step plan as fallback
            fallback_step = TaskStep(
                step_id=str(uuid4()),
                index=0,
                description=objective,
                tool_hint=None,
            )
            plan = TaskPlan(
                plan_id=plan_id,
                objective=objective,
                steps=[fallback_step],
                context={"fallback": True, "error": str(e)},
            )
            plan.inject_kernel(self._kernel)
            self._active_plans[plan_id] = plan
            return plan

    def _parse_plan_response(self, response: str) -> list[dict]:
        """Extract and parse the JSON plan from LLM response."""
        # Try direct JSON parse
        try:
            data = json.loads(response.strip())
            return data.get("steps", [])
        except json.JSONDecodeError:
            pass

        # Try to extract JSON block
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return data.get("steps", [])
            except json.JSONDecodeError:
                pass

        # Fallback: create single step from response
        logger.warning("task_planner_parse_failed", response_len=len(response))
        return [{"index": 0, "description": response[:500], "tool_hint": None, "depends_on": []}]

    async def execute(
        self,
        plan: TaskPlan,
        user_id: str = "embrion",
    ) -> dict[str, Any]:
        """
        Execute a TaskPlan step by step using the ReAct pattern.
        Returns execution summary.
        """
        plan.status = PlanStatus.RUNNING
        plan.started_at = datetime.now(timezone.utc).isoformat()
        logger.info("task_planner_executing", plan_id=plan.plan_id, steps=len(plan.steps))

        try:
            for step in plan.steps:
                # Check budget
                if plan.total_cost_usd >= PLAN_BUDGET_USD:
                    logger.warning(
                        "task_planner_budget_exceeded",
                        plan_id=plan.plan_id,
                        cost=plan.total_cost_usd,
                    )
                    step.status = StepStatus.SKIPPED
                    step.error = f"Budget exceeded: ${plan.total_cost_usd:.2f} >= ${PLAN_BUDGET_USD}"
                    continue

                # Check dependencies
                if not self._dependencies_met(step, plan):
                    step.status = StepStatus.SKIPPED
                    step.error = "Dependencies not met (previous step failed)"
                    logger.warning(
                        "task_planner_step_skipped",
                        plan_id=plan.plan_id,
                        step=step.index,
                        reason="dependencies_not_met",
                    )
                    continue

                # Execute step with ReAct loop
                success = await self._execute_step_with_react(step, plan, user_id)

                if not success and step.retries >= MAX_RETRIES_PER_STEP:
                    # Try to revise the remaining plan
                    revised = await self._revise_plan(plan, step, user_id)
                    if not revised:
                        # Cannot recover — mark plan as failed
                        plan.status = PlanStatus.FAILED
                        break

                # Update DB after each step
                await self._persist_plan(plan)

            # Generate final summary
            plan.final_summary = await self._generate_summary(plan, user_id)
            plan.finished_at = datetime.now(timezone.utc).isoformat()

            if plan.status != PlanStatus.FAILED:
                plan.status = PlanStatus.DONE if not plan.failed_steps else PlanStatus.REVISED

            await self._persist_plan(plan)

            logger.info(
                "task_planner_execution_complete",
                plan_id=plan.plan_id,
                status=plan.status.value,
                progress=plan.progress_pct,
                cost=plan.total_cost_usd,
            )

            return plan.to_dict()

        except Exception as e:
            plan.status = PlanStatus.FAILED
            plan.finished_at = datetime.now(timezone.utc).isoformat()
            plan.final_summary = f"Ejecución fallida: {str(e)}"
            logger.error("task_planner_execution_failed", plan_id=plan.plan_id, error=str(e))
            await self._persist_plan(plan)
            return plan.to_dict()

    def _dependencies_met(self, step: TaskStep, plan: TaskPlan) -> bool:
        """Check if all dependencies for a step are completed."""
        for dep_idx in step.depends_on:
            dep_steps = [s for s in plan.steps if s.index == dep_idx]
            if not dep_steps:
                continue
            dep = dep_steps[0]
            if dep.status not in (StepStatus.DONE, StepStatus.SKIPPED):
                return False
        return True

    # ── Tool definitions for Claude ReAct executor ──────────────────
    _EXECUTOR_TOOLS = [
        {
            "name": "web_search",
            "description": "Buscar información en internet en tiempo real. Usar para noticias, precios, documentación, repositorios.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "La consulta de búsqueda"},
                    "context": {"type": "string", "description": "Contexto adicional opcional"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "browse_web",
            "description": "Navegar a una URL específica y extraer su contenido. Usar para leer documentación, páginas web, APIs.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL a navegar"},
                    "action": {"type": "string", "description": "Acción: markdown (default), screenshot, links"},
                },
                "required": ["url"],
            },
        },
        {
            "name": "code_exec",
            "description": "Ejecutar código Python en un sandbox seguro (E2B). Usar para cálculos, scripts, análisis de datos, generación de archivos.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código Python a ejecutar"},
                    "language": {"type": "string", "description": "Lenguaje (default: python)"},
                    "install_packages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paquetes pip a instalar antes de ejecutar",
                    },
                },
                "required": ["code"],
            },
        },
        {
            "name": "github",
            "description": "Operaciones en GitHub: crear branches, leer/escribir archivos, crear PRs, listar repositorios.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Acción: create_branch, create_file, update_file, create_pr, get_file, list_repos, create_issue",
                    },
                    "params": {
                        "type": "object",
                        "description": "Parámetros de la acción (repo, branch, path, content, title, body, etc.)",
                    },
                },
                "required": ["action", "params"],
            },
        },
        {
            "name": "send_message",
            "description": "Enviar un mensaje o notificación a Alfredo (el usuario). Usar para reportar resultados, pedir confirmación o enviar resúmenes.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "El mensaje a enviar"},
                    "channel": {"type": "string", "description": "Canal: telegram (default)"},
                },
                "required": ["message"],
            },
        },
        {
            "name": "manus_bridge",
            "description": "Sprint 44: Delegar una tarea compleja a un agente Manus externo. Usar cuando la tarea requiere capacidades avanzadas de Manus (browser research, multi-step workflows, análisis profundo). Manus ejecuta la tarea de forma autónoma y devuelve el resultado.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Acción: create_task (solo crear), create_and_wait (crear y esperar resultado)",
                        "enum": ["create_task", "create_and_wait"],
                    },
                    "prompt": {"type": "string", "description": "La tarea a delegar a Manus en lenguaje natural"},
                    "account": {"type": "string", "description": "Cuenta Manus a usar: google (default) o apple"},
                    "timeout": {"type": "number", "description": "Timeout en segundos para create_and_wait (default: 300)"},
                },
                "required": ["action", "prompt"],
            },
        },
        {
            "name": "query_knowledge",
            "description": "Sprint 44: Consultar el knowledge graph del Embrión (LightRAG). Usar para recuperar contexto previo, lecciones aprendidas, decisiones pasadas, o cualquier información almacenada en la memoria del sistema.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Consulta en lenguaje natural"},
                    "mode": {
                        "type": "string",
                        "description": "Modo de búsqueda: hybrid (default), local, global, naive",
                        "enum": ["hybrid", "local", "global", "naive"],
                    },
                    "top_k": {"type": "integer", "description": "Máximo de resultados a retornar (default: 5)"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "ingest_knowledge",
            "description": "Sprint 44: Ingestar un documento o texto al knowledge graph del Embrión (LightRAG). Usar para guardar resultados importantes, aprendizajes, o información que debe persistir en la memoria del sistema.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Texto o documento a ingestar"},
                    "metadata": {
                        "type": "object",
                        "description": "Metadatos opcionales: source, type, sprint, etc.",
                    },
                },
                "required": ["content"],
            },
        },
        {
            "name": "consult_sabios",
            "description": "Sprint 44: Consultar a los 6 Sabios (GPT-5.4, Claude, Gemini, Grok, DeepSeek, Perplexity) en paralelo para obtener perspectivas múltiples sobre un problema. Usar cuando la tarea requiere análisis profundo, validación cruzada, o decisión estratégica importante.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "La pregunta o tarea para los Sabios"},
                    "context": {"type": "string", "description": "Contexto adicional para los Sabios (opcional)"},
                    "sabios": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["gpt54", "claude", "gemini", "grok", "deepseek", "perplexity"]},
                        "description": "Subset de Sabios a consultar (default: todos los 6)",
                    },
                },
                "required": ["prompt"],
            },
        },
        {
            "name": "web_dev",
            "description": "Sprint 47.2: Crear y desplegar sitios web. Acciones: scaffold (crea proyecto Vite+React+Tailwind), build (compila), deploy (sube a Vercel). Usar para crear landing pages, apps web, portfolios.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Acción: scaffold, build, deploy",
                        "enum": ["scaffold", "build", "deploy"],
                    },
                    "project_name": {"type": "string", "description": "Nombre del proyecto (slug, e.g. mi-landing-page)"},
                },
                "required": ["action"],
            },
        },
        {
            "name": "file_ops",
            "description": "Sprint 46.2: Operaciones de archivo en el sandbox. Crear, leer, editar, listar y eliminar archivos. Usar para scaffolding de proyectos, escribir código, crear configuraciones.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Acción: write_file, read_file, edit_file, list_files, delete_file, mkdir",
                        "enum": ["write_file", "read_file", "edit_file", "list_files", "delete_file", "mkdir"],
                    },
                    "path": {"type": "string", "description": "Ruta del archivo o directorio (absoluta, e.g. /home/user/project/index.html)"},
                    "content": {"type": "string", "description": "Contenido a escribir (para write_file)"},
                    "find": {"type": "string", "description": "Texto a buscar (para edit_file)"},
                    "replace": {"type": "string", "description": "Texto de reemplazo (para edit_file)"},
                },
                "required": ["action", "path"],
            },
        },
    ]

    async def _execute_tool_direct(self, tool_name: str, args: dict) -> str:
        """
        Execute a tool directly without going through the full kernel graph.
        Returns a string result for Claude to process.
        """
        try:
            if tool_name == "web_search":
                from tools.web_search import web_search
                result = await web_search(
                    query=args.get("query", ""),
                    context=args.get("context", ""),
                )
                return json.dumps(result, ensure_ascii=False)[:3000]

            elif tool_name == "browse_web":
                from tools.browser import browse_web
                result_str = await browse_web(
                    url=args.get("url", ""),
                    action=args.get("action", "markdown"),
                    wait_for_js=True,
                )
                return result_str[:3000]

            elif tool_name == "code_exec":
                # Sprint 48: Use persistent sandbox via SandboxManager
                from tools.sandbox_manager import execute_in_sandbox
                plan_id = getattr(self, '_current_plan_id', 'default')
                result = await execute_in_sandbox(
                    plan_id=plan_id,
                    code=args.get("code", ""),
                    language=args.get("language", "python"),
                    timeout=args.get("timeout", 60),
                    install_packages=args.get("install_packages"),
                )
                return json.dumps(result, ensure_ascii=False)[:3000]

            elif tool_name == "github":
                from tools.github import execute_github
                result_str = await execute_github(
                    action=args.get("action", ""),
                    params=args.get("params", {}),
                )
                return result_str[:3000]

            elif tool_name == "manus_bridge":
                # Sprint 44: Delegate task to Manus external agent
                import asyncio as _asyncio
                from tools.manus_bridge import handle_manus_bridge
                loop = _asyncio.get_event_loop()
                manus_params = {
                    "action": args.get("action", "create_and_wait"),
                    "prompt": args.get("prompt", ""),
                    "account": args.get("account", "google"),
                    "timeout": args.get("timeout", 300),
                }
                logger.info("task_planner_manus_bridge", action=manus_params["action"], prompt=manus_params["prompt"][:100])
                result = await loop.run_in_executor(None, handle_manus_bridge, manus_params)
                return json.dumps(result, ensure_ascii=False)[:3000]

            elif tool_name == "send_message":
                # Sprint 43: Actually send via TelegramNotifier (not just log)
                msg = args.get("message", "")
                logger.info("task_planner_send_message", message=msg[:200])
                try:
                    from kernel.runner.telegram_notifier import TelegramNotifier
                    _notifier = TelegramNotifier()
                    if _notifier.enabled:
                        await _notifier.send_message(user_id="embrion", text=msg)
                        return json.dumps({"sent": True, "channel": "telegram", "message": msg[:200]})
                    else:
                        logger.warning("task_planner_send_message_notifier_disabled")
                        return json.dumps({"sent": False, "reason": "telegram_notifier_disabled", "message": msg[:200]})
                except Exception as e:
                    logger.error("task_planner_send_message_error", error=str(e))
                    return json.dumps({"sent": False, "error": str(e), "message": msg[:200]})

            elif tool_name == "query_knowledge":
                # Sprint 44: Consultar el knowledge graph del Embrión
                from memory.lightrag_bridge import query_knowledge
                result = await query_knowledge(
                    query=args.get("query", ""),
                    mode=args.get("mode", "hybrid"),
                    top_k=args.get("top_k", 5),
                )
                logger.info(
                    "task_planner_query_knowledge",
                    query=args.get("query", "")[:80],
                    mode=args.get("mode", "hybrid"),
                )
                return json.dumps(result, ensure_ascii=False)[:4000]

            elif tool_name == "ingest_knowledge":
                # Sprint 44: Ingestar documento al knowledge graph del Embrión
                from memory.lightrag_bridge import ingest_document
                result = await ingest_document(
                    content=args.get("content", ""),
                    metadata=args.get("metadata"),
                )
                logger.info(
                    "task_planner_ingest_knowledge",
                    content_length=len(args.get("content", "")),
                )
                return json.dumps(result, ensure_ascii=False)

            elif tool_name == "consult_sabios":
                # Sprint 44: Consultar los 6 Sabios en paralelo
                from tools.consult_sabios import consult_sabios
                result = await consult_sabios(
                    prompt=args.get("prompt", ""),
                    context=args.get("context", ""),
                    sabios=args.get("sabios"),  # None = todos los 6
                    parallel=True,
                )
                logger.info(
                    "task_planner_consult_sabios",
                    prompt=args.get("prompt", "")[:80],
                    successful=result.get("successful_count", 0),
                    failed=result.get("failed_count", 0),
                    latency_ms=result.get("total_latency_ms", 0),
                )
                # Retornar solo la síntesis para no saturar el contexto de Claude
                synthesis = result.get("synthesis", "")
                return synthesis[:6000] if synthesis else json.dumps({"error": "No sabios responded", "errors": result.get("errors", [])})

            elif tool_name == "web_dev":
                # Sprint 48: Web dev using persistent sandbox
                from tools.sandbox_manager import web_dev_in_sandbox
                plan_id = getattr(self, '_current_plan_id', 'default')
                result = await web_dev_in_sandbox(
                    plan_id=plan_id,
                    action=args.get("action", "scaffold"),
                    project_name=args.get("project_name"),
                )
                logger.info(
                    "task_planner_web_dev",
                    action=args.get("action"),
                    project_name=args.get("project_name", ""),
                    success=result.get("success"),
                    url=result.get("url"),
                )
                return json.dumps(result, ensure_ascii=False)[:4000]

            elif tool_name == "file_ops":
                # Sprint 48: File ops using persistent sandbox
                from tools.sandbox_manager import file_op_in_sandbox
                plan_id = getattr(self, '_current_plan_id', 'default')
                result = await file_op_in_sandbox(
                    plan_id=plan_id,
                    action=args.get("action", "read_file"),
                    path=args.get("path", ""),
                    content=args.get("content"),
                    find=args.get("find"),
                    replace=args.get("replace"),
                    recursive=args.get("recursive", False),
                )
                logger.info(
                    "task_planner_file_ops",
                    action=args.get("action"),
                    path=args.get("path", "")[:80],
                    success=result.get("success"),
                )
                return json.dumps(result, ensure_ascii=False)[:4000]

            else:
                return json.dumps({"error": f"Tool '{tool_name}' not available in planner executor"})

        except Exception as e:
            logger.error("task_planner_tool_error", tool=tool_name, error=str(e))
            return json.dumps({"error": str(e), "tool": tool_name})

    async def _execute_step_with_react(
        self,
        step: TaskStep,
        plan: TaskPlan,
        user_id: str,
    ) -> bool:
        """
        Execute a single step using the ReAct pattern with Claude tool_use.
        Reason → Act (tool call) → Observe (tool result) → Reason → ...
        Returns True if step succeeded.

        Sprint 42: Uses Claude claude-opus-4-7 with native tool_use instead of
        routing through the full LangGraph kernel (which had quota/routing issues).
        Max 3 Reason-Act-Observe iterations per step.
        """
        step.status = StepStatus.RUNNING
        step.started_at = time.time()

        # Build context from previous steps
        prev_results = []
        for prev in plan.steps:
            if prev.index < step.index and prev.status == StepStatus.DONE and prev.result:
                prev_results.append(f"Paso {prev.index}: {prev.result[:300]}")
        prev_context = "\n".join(prev_results) if prev_results else "Ninguno"

        tool_hint_str = f"\nHerramienta sugerida: {step.tool_hint}" if step.tool_hint else ""

        system_prompt = """Eres el Embrión IA, un agente autónomo que ejecuta planes de tareas.
Tienes acceso a herramientas reales. Úsalas para completar cada paso.
Sé conciso y directo. Reporta el resultado al final con un resumen claro."""

        user_message = f"""OBJETIVO GENERAL: {plan.objective}

PASO A EJECUTAR ({step.index + 1}/{len(plan.steps)}): {step.description}{tool_hint_str}

RESULTADOS DE PASOS ANTERIORES:
{prev_context}

Ejecuta este paso ahora usando las herramientas disponibles. Al terminar, reporta el resultado."""

        for attempt in range(MAX_RETRIES_PER_STEP + 1):
            try:
                import anthropic

                client = anthropic.AsyncAnthropic(
                    api_key=os.environ.get("ANTHROPIC_API_KEY", "")
                )

                messages = [{"role": "user", "content": user_message}]
                total_tokens = 0
                final_response = ""
                max_react_loops = MAX_REACT_LOOPS
                # Sprint 46.3: Stuck detection state
                _tool_call_history: list[tuple[str, str]] = []  # (tool_name, args_hash)
                _step_tool_calls = 0

                for loop_i in range(max_react_loops):
                    resp = await asyncio.wait_for(
                        client.messages.create(
                            model="claude-opus-4-7",
                            max_tokens=4000,
                            system=system_prompt,
                            tools=self._EXECUTOR_TOOLS,
                            messages=messages,
                        ),
                        timeout=STEP_TIMEOUT_S,
                    )

                    total_tokens += resp.usage.input_tokens + resp.usage.output_tokens

                    # Check stop reason
                    if resp.stop_reason == "end_turn":
                        # Claude finished — extract text response
                        for block in resp.content:
                            if hasattr(block, "text"):
                                final_response += block.text
                        break

                    elif resp.stop_reason == "tool_use":
                        # Claude wants to use a tool — execute it
                        assistant_content = resp.content
                        messages.append({"role": "assistant", "content": assistant_content})

                        tool_results = []
                        for block in resp.content:
                            if block.type == "tool_use":
                                # Sprint 46.3: Stuck detection
                                import hashlib
                                args_hash = hashlib.md5(json.dumps(block.input, sort_keys=True).encode()).hexdigest()[:8]
                                _tool_call_history.append((block.name, args_hash))
                                _step_tool_calls += 1

                                # Check if stuck: same tool+args repeated N times
                                recent = _tool_call_history[-STUCK_DETECTION_THRESHOLD:]
                                if len(recent) == STUCK_DETECTION_THRESHOLD and len(set(recent)) == 1:
                                    logger.warning(
                                        "task_planner_stuck_detected",
                                        plan_id=plan.plan_id,
                                        step=step.index,
                                        tool=block.name,
                                        repeated=STUCK_DETECTION_THRESHOLD,
                                    )
                                    final_response = f"[STUCK] El agente repitió {block.name} {STUCK_DETECTION_THRESHOLD} veces con los mismos argumentos. Paso abortado."
                                    break

                                # Check hard cap on tool calls per step
                                if _step_tool_calls >= MAX_TOTAL_TOOL_CALLS_PER_STEP:
                                    logger.warning(
                                        "task_planner_tool_cap_reached",
                                        plan_id=plan.plan_id,
                                        step=step.index,
                                        total_calls=_step_tool_calls,
                                    )
                                    final_response = f"[CAP] Se alcanzó el límite de {MAX_TOTAL_TOOL_CALLS_PER_STEP} llamadas a herramientas en este paso."
                                    break

                                logger.info(
                                    "task_planner_react_tool_call",
                                    plan_id=plan.plan_id,
                                    step=step.index,
                                    tool=block.name,
                                    loop=loop_i,
                                    call_num=_step_tool_calls,
                                )
                                tool_result = await self._execute_tool_direct(
                                    block.name, block.input
                                )
                                plan.total_tool_calls += 1  # Sprint 43: track real executions
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": tool_result,
                                })

                        # If stuck was detected inside the for loop, break outer loop too
                        if final_response and ("[STUCK]" in final_response or "[CAP]" in final_response):
                            break

                        messages.append({"role": "user", "content": tool_results})

                    else:
                        # Unexpected stop reason — extract whatever text we have
                        for block in resp.content:
                            if hasattr(block, "text"):
                                final_response += block.text
                        break

                # Si Claude terminó los loops usando herramientas pero sin generar texto final,
                # hacer una llamada final SIN herramientas para forzar el resumen.
                if not final_response and messages and messages[-1]["role"] == "user":
                    try:
                        summary_resp = await asyncio.wait_for(
                            client.messages.create(
                                model="claude-opus-4-7",
                                max_tokens=1000,
                                system=system_prompt,
                                messages=messages,  # Sin tools= para forzar end_turn
                            ),
                            timeout=30,
                        )
                        total_tokens += summary_resp.usage.input_tokens + summary_resp.usage.output_tokens
                        for block in summary_resp.content:
                            if hasattr(block, "text"):
                                final_response += block.text
                        logger.info(
                            "task_planner_react_summary_generated",
                            plan_id=plan.plan_id,
                            step=step.index,
                            length=len(final_response),
                        )
                    except Exception as summary_err:
                        logger.warning(
                            "task_planner_react_summary_failed",
                            error=str(summary_err),
                        )

                if not final_response:
                    final_response = f"Paso ejecutado (sin respuesta de texto). Loops ReAct: {loop_i + 1}"

                # Estimate cost: claude-opus-4-7 = $3/M input + $15/M output
                cost = total_tokens * 0.000009  # rough average

                step.result = final_response
                step.status = StepStatus.DONE
                step.finished_at = time.time()
                step.tokens_used = total_tokens
                step.cost_usd = cost
                plan.total_tokens += total_tokens
                plan.total_cost_usd += cost

                logger.info(
                    "task_planner_step_done",
                    plan_id=plan.plan_id,
                    step=step.index,
                    tokens=total_tokens,
                    cost=cost,
                    react_loops=loop_i + 1,
                )
                return True

            except asyncio.TimeoutError:
                step.retries += 1
                step.error = f"Timeout en intento {attempt + 1}"
                logger.warning(
                    "task_planner_step_timeout",
                    plan_id=plan.plan_id,
                    step=step.index,
                    attempt=attempt,
                )
                if attempt < MAX_RETRIES_PER_STEP:
                    await asyncio.sleep(5)
                    continue

            except Exception as e:
                step.retries += 1
                step.error = str(e)[:300]
                logger.error(
                    "task_planner_step_error",
                    plan_id=plan.plan_id,
                    step=step.index,
                    error=str(e),
                    attempt=attempt,
                )
                if attempt < MAX_RETRIES_PER_STEP:
                    await asyncio.sleep(5)
                    continue

        step.status = StepStatus.FAILED
        step.finished_at = time.time()
        return False

    async def _revise_plan(
        self,
        plan: TaskPlan,
        failed_step: TaskStep,
        user_id: str,
    ) -> bool:
        """
        Revise the remaining plan after a step failure.
        Returns True if revision was successful.
        """
        remaining = [s for s in plan.steps if s.status == StepStatus.PENDING]
        if not remaining:
            return True  # Nothing to revise

        plan.revision_count += 1
        logger.info(
            "task_planner_revising",
            plan_id=plan.plan_id,
            failed_step=failed_step.index,
            remaining=len(remaining),
        )

        done_summary = "\n".join(
            f"- Paso {s.index}: {s.description} → {s.result[:200] if s.result else 'sin resultado'}"
            for s in plan.done_steps
        )

        revision_prompt = f"""Eres el planificador del Embrión IA. Un paso falló y necesitas revisar el plan.

OBJETIVO: {plan.objective}

PASO FALLIDO: Paso {failed_step.index} — {failed_step.description}
ERROR: {failed_step.error}

PASOS COMPLETADOS:
{done_summary or "Ninguno"}

PASOS PENDIENTES (a revisar):
{chr(10).join(f"- Paso {s.index}: {s.description}" for s in remaining)}

INSTRUCCIONES:
Revisa los pasos pendientes para alcanzar el objetivo a pesar del fallo.
Puedes modificar, omitir o agregar pasos.

RESPONDE con JSON:
{{
  "steps": [
    {{"index": N, "description": "...", "tool_hint": "...", "depends_on": []}}
  ],
  "rationale": "Por qué este plan revisado funcionará"
}}"""

        try:
            from contracts.kernel_interface import RunInput
            run_input = RunInput(
                message=revision_prompt,
                user_id=user_id,
                channel="internal",
                context={
                    "source": "task_planner_revision",
                    "model_hint": PLANNER_MODEL,
                    "max_tokens": 1500,
                },
            )
            result = await asyncio.wait_for(
                plan._kernel.start_run(run_input),
                timeout=60,
            )
            response = result.response if hasattr(result, "response") else str(result)
            new_steps_data = self._parse_plan_response(response)

            if new_steps_data:
                # Replace pending steps with revised ones
                for step in remaining:
                    step.status = StepStatus.SKIPPED
                    step.error = "Replaced by plan revision"

                # Add new steps
                max_idx = max(s.index for s in plan.steps)
                for i, s_data in enumerate(new_steps_data):
                    new_step = TaskStep(
                        step_id=str(uuid4()),
                        index=max_idx + 1 + i,
                        description=s_data["description"],
                        tool_hint=s_data.get("tool_hint"),
                        depends_on=s_data.get("depends_on", []),
                    )
                    plan.steps.append(new_step)

                plan.status = PlanStatus.REVISED
                logger.info(
                    "task_planner_revised",
                    plan_id=plan.plan_id,
                    new_steps=len(new_steps_data),
                )
                return True

        except Exception as e:
            logger.error("task_planner_revision_failed", plan_id=plan.plan_id, error=str(e))

        return False

    async def _generate_summary(self, plan: TaskPlan, user_id: str) -> str:
        """Generate a concise summary of the plan execution."""
        done = len(plan.done_steps)
        total = len(plan.steps)
        failed = len(plan.failed_steps)

        if done == total:
            status_str = "completado exitosamente"
        elif failed > 0:
            status_str = f"completado con {failed} paso(s) fallido(s)"
        else:
            status_str = "completado parcialmente"

        results_summary = "\n".join(
            f"- Paso {s.index}: {s.result[:200] if s.result else 'sin resultado'}"
            for s in plan.done_steps[:5]  # Max 5 steps in summary
        )

        return (
            f"Plan {status_str}. "
            f"{done}/{total} pasos completados. "
            f"Costo total: ${plan.total_cost_usd:.4f}. "
            f"Revisiones: {plan.revision_count}.\n\n"
            f"Resultados principales:\n{results_summary}"
        )

    async def _persist_plan(self, plan: TaskPlan) -> None:
        """Persist plan state to Supabase (non-fatal)."""
        if not self._db:
            return
        try:
            await self._db.upsert(
                table="task_plans",
                data={
                    "plan_id": plan.plan_id,
                    "objective": plan.objective[:500],
                    "status": plan.status.value,
                    "steps_json": json.dumps([s.to_dict() for s in plan.steps]),
                    "progress_pct": plan.progress_pct,
                    "total_steps": len(plan.steps),
                    "done_steps": len(plan.done_steps),
                    "failed_steps": len(plan.failed_steps),
                    "total_tokens": plan.total_tokens,
                    "total_cost_usd": round(plan.total_cost_usd, 6),
                    "revision_count": plan.revision_count,
                    "created_at": plan.created_at,
                    "started_at": plan.started_at,
                    "finished_at": plan.finished_at,
                    "final_summary": plan.final_summary,
                    "context_json": json.dumps(plan.context),
                },
                on_conflict="plan_id",
            )
        except Exception as e:
            logger.warning("task_planner_persist_failed", error=str(e))

    async def revise(
        self,
        plan: TaskPlan,
        failed_step_index: int = 0,
        user_id: str = "embrion",
    ) -> TaskPlan:
        """Public method to revise a failed plan. Wraps _revise_plan."""
        # Find the failed step by index
        failed_steps = [s for s in plan.steps if s.index == failed_step_index]
        if not failed_steps:
            # Fallback: use first failed step
            failed_steps = [s for s in plan.steps if s.status == StepStatus.FAILED]
        if not failed_steps:
            # Nothing to revise — just increment and return
            plan.revision_count += 1
            return plan
        failed_step = failed_steps[0]
        await self._revise_plan(plan, failed_step, user_id)
        return plan

    def get_plan(self, plan_id: str) -> Optional[TaskPlan]:
        """Get an active plan by ID."""
        return self._active_plans.get(plan_id)

    def get_active_plans(self) -> list[dict[str, Any]]:
        """Get summary of all active plans."""
        return [p.to_dict() for p in self._active_plans.values()]

    def is_complex_objective(self, text: str) -> bool:
        """
        Heuristic to detect if a message contains a complex objective
        that should be handled by the Task Planner instead of direct execution.
        """
        import re
        # Complexity indicators
        complexity_keywords = [
            "construye", "implementa", "crea", "desarrolla", "migra",
            "refactoriza", "agrega", "integra", "conecta", "diseña",
            "sprint", "módulo", "sistema", "pipeline", "endpoint",
            "y luego", "después", "primero", "paso a paso", "en orden",
            "múltiples", "varios", "todo el", "completo", "completa",
            # Multi-step explicit markers
            "luego", "finalmente", "después de", "a continuación",
            # Technical complexity
            "verifica", "despliega", "persiste", "redeploy", "pgvector",
            "supabase", "railway", "docker", "kubernetes",
            "analiza", "detecta", "agrupa", "envía", "reporta",
            # Sprint 47.2: Web dev triggers
            "sitio web", "landing page", "página web", "website",
            "app web", "aplicación web", "portfolio", "dashboard",
        ]
        text_lower = text.lower()
        keyword_count = sum(1 for kw in complexity_keywords if kw in text_lower)

        # Length heuristic: long messages tend to be complex
        is_long = len(text) > 200

        # Multi-sentence heuristic (commas + periods + newlines)
        sentence_count = text.count(".") + text.count("\n") + text.count(",")
        is_multi_sentence = sentence_count >= 2

        # Explicit multi-step patterns: "paso 1", "step 2", "1.", "2."
        has_step_pattern = bool(re.search(r'paso\s+\d|step\s+\d|\b\d+[:\-\.]\s', text_lower))

        return keyword_count >= 2 or has_step_pattern or (is_long and is_multi_sentence)

    # ── Sprint 46.1: Streaming Plan & Execute for User Chat ────────────

    async def stream_plan_and_execute(
        self,
        objective: str,
        context: Optional[dict[str, Any]] = None,
        user_id: str = "user",
        enriched_context: Optional[dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """
        Sprint 46.1: Streaming version of plan + execute for user-facing chat.

        Yields JSON-encoded events compatible with the existing agui_adapter:
          {"type": "step", "id": "...", "status": "in_progress|completed", "label": "...", "icon": "..."}
          {"type": "tool_start", "data": {"name": "...", "args": {...}}}
          {"type": "tool_end", "data": {"result": "..."}}
          {"type": "chunk", "text": "..."}  (final synthesized response)
          {"type": "done", ...}

        This method replaces the normal LLM streaming path when intent == "execute"
        and the task is complex enough to warrant planning.
        """
        import json as _json
        plan_start = time.time()

        # Sprint 48: Acquire persistent sandbox for this plan execution
        from tools.sandbox_manager import acquire as _sandbox_acquire, release as _sandbox_release
        from uuid import uuid4 as _uuid4
        _plan_execution_id = str(_uuid4())
        self._current_plan_id = _plan_execution_id  # Used by _execute_tool_direct

        try:
            sandbox_id = await _sandbox_acquire(_plan_execution_id)
            logger.info("stream_sandbox_acquired", plan_id=_plan_execution_id, sandbox_id=sandbox_id)
        except Exception as sbx_err:
            logger.error("stream_sandbox_acquire_failed", error=str(sbx_err))
            yield _json.dumps({"type": "chunk", "text": f"Error al crear sandbox: {sbx_err}"})
            yield _json.dumps({"type": "done", "error": str(sbx_err)})
            return

        # ── Step 1: Planning ──────────────────────────────────────────
        yield _json.dumps({
            "type": "step",
            "id": "plan",
            "status": "in_progress",
            "label": "Planificando tarea...",
            "icon": "build",
        })

        try:
            plan = await self.plan(
                objective=objective,
                context=context,
                user_id=user_id,
            )
        except Exception as e:
            logger.error("stream_plan_failed", error=str(e))
            yield _json.dumps({
                "type": "step",
                "id": "plan",
                "status": "completed",
                "label": "Ejecutando directamente...",
                "icon": "build",
            })
            # Fallback: yield the error as text and return
            yield _json.dumps({"type": "chunk", "text": f"No pude planificar la tarea: {str(e)}. Intentando respuesta directa."})
            return

        yield _json.dumps({
            "type": "step",
            "id": "plan",
            "status": "completed",
            "label": f"Plan creado ({len(plan.steps)} pasos)",
            "icon": "build",
        })

        # ── Step 2: Execute each step with streaming events ───────────
        plan.status = PlanStatus.RUNNING
        plan.started_at = datetime.now(timezone.utc).isoformat()

        for step in plan.steps:
            # Check budget
            if plan.total_cost_usd >= PLAN_BUDGET_USD:
                step.status = StepStatus.SKIPPED
                step.error = f"Budget exceeded: ${plan.total_cost_usd:.2f}"
                continue

            # Check dependencies
            if not self._dependencies_met(step, plan):
                step.status = StepStatus.SKIPPED
                step.error = "Dependencies not met"
                continue

            # Emit step start
            step_icon = self._icon_for_tool(step.tool_hint)
            yield _json.dumps({
                "type": "step",
                "id": f"step_{step.index}",
                "status": "in_progress",
                "label": f"Paso {step.index + 1}: {step.description[:60]}...",
                "icon": step_icon,
            })

            # Execute step with ReAct loop + streaming tool events
            success = await self._execute_step_streaming(step, plan, user_id, _json)
            # Yield tool events that were collected during execution
            for event in step._streaming_events if hasattr(step, '_streaming_events') else []:
                yield event

            # Emit step completion
            status_label = "completado" if success else "fallido"
            yield _json.dumps({
                "type": "step",
                "id": f"step_{step.index}",
                "status": "completed",
                "label": f"Paso {step.index + 1}: {status_label}",
                "icon": step_icon,
            })

            if not success and step.retries >= MAX_RETRIES_PER_STEP:
                # Try revision
                revised = await self._revise_plan(plan, step, user_id)
                if not revised:
                    plan.status = PlanStatus.FAILED
                    break

            await self._persist_plan(plan)

        # ── Step 3: Generate final response ───────────────────────────
        yield _json.dumps({
            "type": "step",
            "id": "synthesize",
            "status": "in_progress",
            "label": "Sintetizando resultado...",
            "icon": "sparkles",
        })

        plan.finished_at = datetime.now(timezone.utc).isoformat()
        if plan.status != PlanStatus.FAILED:
            plan.status = PlanStatus.DONE if not plan.failed_steps else PlanStatus.REVISED

        # Generate final summary as the user-facing response
        summary = await self._generate_summary(plan, user_id)
        plan.final_summary = summary
        await self._persist_plan(plan)

        yield _json.dumps({
            "type": "step",
            "id": "synthesize",
            "status": "completed",
            "label": "Resultado listo",
            "icon": "sparkles",
        })

        # Stream the final response as chunks (for the text bubble)
        if summary:
            # Emit in small chunks for smooth streaming appearance
            chunk_size = 50
            for i in range(0, len(summary), chunk_size):
                yield _json.dumps({"type": "chunk", "text": summary[i:i + chunk_size]})
                await asyncio.sleep(0.01)  # Small delay for smooth streaming

        # Sprint 48: Release persistent sandbox
        try:
            await _sandbox_release(_plan_execution_id)
            logger.info("stream_sandbox_released", plan_id=_plan_execution_id)
        except Exception as sbx_err:
            logger.warning("stream_sandbox_release_failed", error=str(sbx_err))

        # Done event
        elapsed_ms = (time.time() - plan_start) * 1000
        yield _json.dumps({
            "type": "done",
            "latency_ms": round(elapsed_ms),
            "model_used": EXECUTOR_MODEL,
            "plan_id": plan.plan_id,
            "steps_completed": len(plan.done_steps),
            "steps_total": len(plan.steps),
            "cost_usd": round(plan.total_cost_usd, 4),
            "tool_calls": plan.total_tool_calls,
        })

    async def _execute_step_streaming(
        self,
        step: TaskStep,
        plan: TaskPlan,
        user_id: str,
        _json,
    ) -> bool:
        """
        Execute a single step with ReAct loop, collecting streaming events
        for tool_start/tool_end that will be yielded by the parent generator.
        """
        step.status = StepStatus.RUNNING
        step.started_at = time.time()
        step._streaming_events = []  # Collect events here

        # Build context from previous steps
        prev_results = []
        for prev in plan.steps:
            if prev.index < step.index and prev.status == StepStatus.DONE and prev.result:
                prev_results.append(f"Paso {prev.index}: {prev.result[:300]}")
        prev_context = "\n".join(prev_results) if prev_results else "Ninguno"

        tool_hint_str = f"\nHerramienta sugerida: {step.tool_hint}" if step.tool_hint else ""

        system_prompt = """Eres El Monstruo, un agente autónomo que ejecuta planes de tareas para el usuario.
Tienes acceso a herramientas reales. Úsalas para completar cada paso.
Sé conciso y directo. Reporta el resultado al final con un resumen claro."""

        user_message = f"""OBJETIVO GENERAL: {plan.objective}

PASO A EJECUTAR ({step.index + 1}/{len(plan.steps)}): {step.description}{tool_hint_str}

RESULTADOS DE PASOS ANTERIORES:
{prev_context}

Ejecuta este paso ahora usando las herramientas disponibles. Al terminar, reporta el resultado."""

        for attempt in range(MAX_RETRIES_PER_STEP + 1):
            try:
                import anthropic

                client = anthropic.AsyncAnthropic(
                    api_key=os.environ.get("ANTHROPIC_API_KEY", "")
                )

                messages = [{"role": "user", "content": user_message}]
                total_tokens = 0
                final_response = ""
                max_react_loops = 3

                for loop_i in range(max_react_loops):
                    resp = await asyncio.wait_for(
                        client.messages.create(
                            model=EXECUTOR_MODEL,
                            max_tokens=4000,
                            system=system_prompt,
                            tools=self._EXECUTOR_TOOLS,
                            messages=messages,
                        ),
                        timeout=STEP_TIMEOUT_S,
                    )

                    total_tokens += resp.usage.input_tokens + resp.usage.output_tokens

                    if resp.stop_reason == "end_turn":
                        for block in resp.content:
                            if hasattr(block, "text"):
                                final_response += block.text
                        break

                    elif resp.stop_reason == "tool_use":
                        assistant_content = resp.content
                        messages.append({"role": "assistant", "content": assistant_content})

                        tool_results = []
                        for block in resp.content:
                            if block.type == "tool_use":
                                # Emit tool_start event
                                step._streaming_events.append(_json.dumps({
                                    "type": "tool_start",
                                    "data": {
                                        "name": block.name,
                                        "args": block.input,
                                    },
                                }))

                                logger.info(
                                    "stream_planner_tool_call",
                                    plan_id=plan.plan_id,
                                    step=step.index,
                                    tool=block.name,
                                    loop=loop_i,
                                )

                                tool_result = await self._execute_tool_direct(
                                    block.name, block.input
                                )
                                plan.total_tool_calls += 1

                                # Emit tool_end event
                                step._streaming_events.append(_json.dumps({
                                    "type": "tool_end",
                                    "data": {
                                        "name": block.name,
                                        "result": tool_result[:500],
                                    },
                                }))

                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": tool_result,
                                })

                        messages.append({"role": "user", "content": tool_results})

                    else:
                        for block in resp.content:
                            if hasattr(block, "text"):
                                final_response += block.text
                        break

                # Force summary if no text response
                if not final_response and messages and messages[-1]["role"] == "user":
                    try:
                        summary_resp = await asyncio.wait_for(
                            client.messages.create(
                                model=EXECUTOR_MODEL,
                                max_tokens=1000,
                                system=system_prompt,
                                messages=messages,
                            ),
                            timeout=30,
                        )
                        total_tokens += summary_resp.usage.input_tokens + summary_resp.usage.output_tokens
                        for block in summary_resp.content:
                            if hasattr(block, "text"):
                                final_response += block.text
                    except Exception:
                        pass

                if not final_response:
                    final_response = f"Paso ejecutado. Loops ReAct: {loop_i + 1}"

                cost = total_tokens * 0.000009
                step.result = final_response
                step.status = StepStatus.DONE
                step.finished_at = time.time()
                step.tokens_used = total_tokens
                step.cost_usd = cost
                plan.total_tokens += total_tokens
                plan.total_cost_usd += cost

                logger.info(
                    "stream_planner_step_done",
                    plan_id=plan.plan_id,
                    step=step.index,
                    tokens=total_tokens,
                    cost=cost,
                    react_loops=loop_i + 1,
                )
                return True

            except asyncio.TimeoutError:
                step.retries += 1
                step.error = f"Timeout en intento {attempt + 1}"
                if attempt < MAX_RETRIES_PER_STEP:
                    await asyncio.sleep(5)
                    continue

            except Exception as e:
                step.retries += 1
                step.error = str(e)[:300]
                if attempt < MAX_RETRIES_PER_STEP:
                    await asyncio.sleep(5)
                    continue

        step.status = StepStatus.FAILED
        step.finished_at = time.time()
        return False

    @staticmethod
    def _icon_for_tool(tool_hint: Optional[str]) -> str:
        """Map tool hint to a Flutter-compatible icon name."""
        icon_map = {
            "web_search": "search",
            "browse_web": "search",
            "code_exec": "code",
            "github": "build",
            "manus_bridge": "sparkles",
            "query_knowledge": "memory",
            "ingest_knowledge": "memory",
            "send_message": "sparkles",
            "consult_sabios": "brain",
            # Sprint 48: Task Planner tools
            "file_ops": "file",
            "web_dev": "web",
            "web_dev.scaffold": "scaffold",
            "web_dev.build": "build",
            "web_dev.deploy": "deploy",
            "sandbox": "cloud",
        }
        return icon_map.get(tool_hint or "", "build")
