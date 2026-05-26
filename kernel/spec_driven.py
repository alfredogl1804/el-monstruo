"""
Spec-Driven Development (SDD)
==============================
Implementación basada en la arquitectura de Kiro (Amazon).
Antes de ejecutar cualquier tarea compleja, el Monstruo define:

1. requirements.md — QUÉ debe hacer (en formato WHEN/SHALL)
2. design.md       — CÓMO lo va a hacer (arquitectura y decisiones)
3. tasks.md        — LISTA de tareas atómicas con checkboxes

Esto resuelve el problema de "lanzarse a ejecutar antes de pensar"
que el usuario identificó como el fallo más recurrente del agente.

Formato WHEN/SHALL (Kiro):
  WHEN <condición>
  SHALL <comportamiento esperado>

Ejemplo:
  WHEN el usuario pide investigar un agente de IA
  SHALL buscar primero en fuentes en tiempo real (GitHub, Reddit, blogs oficiales)
  SHALL validar que el agente existe y tiene actividad en los últimos 60 días
  SHALL incluir la versión actual y fecha del último commit
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger()


@dataclass
class Requirement:
    """Un requisito en formato WHEN/SHALL."""

    when: str
    shall: str
    priority: str = "must"  # must | should | could


@dataclass
class DesignDecision:
    """Una decisión de diseño arquitectónico."""

    title: str
    rationale: str
    alternatives_considered: list[str] = field(default_factory=list)


@dataclass
class Task:
    """Una tarea atómica ejecutable."""

    id: str
    description: str
    completed: bool = False
    depends_on: list[str] = field(default_factory=list)


@dataclass
class Spec:
    """Una especificación completa de una tarea."""

    title: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    requirements: list[Requirement] = field(default_factory=list)
    design_decisions: list[DesignDecision] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def to_markdown(self) -> dict[str, str]:
        """Convierte la spec a 3 archivos markdown (formato Kiro)."""

        # requirements.md
        req_lines = [f"# Requirements: {self.title}\n"]
        for i, req in enumerate(self.requirements, 1):
            req_lines.append(f"## Requirement {i}")
            req_lines.append(f"**WHEN** {req.when}")
            req_lines.append(f"**SHALL** {req.shall}")
            req_lines.append(f"**Priority:** {req.priority}\n")

        # design.md
        design_lines = [f"# Design: {self.title}\n"]
        for decision in self.design_decisions:
            design_lines.append(f"## {decision.title}")
            design_lines.append(f"**Rationale:** {decision.rationale}")
            if decision.alternatives_considered:
                design_lines.append("**Alternatives considered:**")
                for alt in decision.alternatives_considered:
                    design_lines.append(f"- {alt}")
            design_lines.append("")

        # tasks.md
        tasks_lines = [f"# Tasks: {self.title}\n"]
        for task in self.tasks:
            checkbox = "[x]" if task.completed else "[ ]"
            tasks_lines.append(f"- {checkbox} **{task.id}**: {task.description}")
            if task.depends_on:
                tasks_lines.append(f"  - Depends on: {', '.join(task.depends_on)}")

        return {
            "requirements.md": "\n".join(req_lines),
            "design.md": "\n".join(design_lines),
            "tasks.md": "\n".join(tasks_lines),
        }

    def save(self, directory: str | Path) -> None:
        """Guarda la spec en 3 archivos en el directorio dado."""
        spec_dir = Path(directory)
        spec_dir.mkdir(parents=True, exist_ok=True)

        files = self.to_markdown()
        for filename, content in files.items():
            (spec_dir / filename).write_text(content, encoding="utf-8")

        logger.info("spec_saved", title=self.title, directory=str(spec_dir))

    def get_next_task(self) -> Optional[Task]:
        """Retorna la próxima tarea pendiente cuyas dependencias están completas."""
        completed_ids = {t.id for t in self.tasks if t.completed}
        for task in self.tasks:
            if not task.completed:
                if all(dep in completed_ids for dep in task.depends_on):
                    return task
        return None

    def mark_task_complete(self, task_id: str) -> bool:
        """Marca una tarea como completada."""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                logger.info("task_completed", task_id=task_id, spec=self.title)
                return True
        return False

    def progress(self) -> dict:
        """Retorna el progreso actual de la spec."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        return {
            "total": total,
            "completed": completed,
            "percentage": (completed / total * 100) if total > 0 else 0,
            "next_task": self.get_next_task().id if self.get_next_task() else None,
        }


class SpecDrivenPlanner:
    """
    Planificador que obliga al Monstruo a definir specs antes de ejecutar.

    Principio de Kiro: "Spec first, code second."
    El agente NUNCA debe ejecutar una tarea compleja sin antes definir:
    1. Qué debe hacer (requirements)
    2. Cómo lo va a hacer (design)
    3. Qué pasos va a seguir (tasks)
    """

    COMPLEXITY_THRESHOLD = 3  # Tareas con más de 3 pasos requieren spec

    def __init__(self, specs_dir: str | Path = "/tmp/monstruo_specs"):
        self.specs_dir = Path(specs_dir)
        self.specs_dir.mkdir(parents=True, exist_ok=True)
        self.active_specs: dict[str, Spec] = {}

    def requires_spec(self, task_description: str) -> bool:
        """
        Determina si una tarea requiere una spec antes de ejecutarse.

        Criterios (basados en Kiro):
        - Tareas que mencionan múltiples pasos o componentes
        - Tareas de investigación amplia
        - Tareas de implementación de código
        - Tareas que afectan múltiples archivos
        """
        complexity_keywords = [
            "implementar",
            "construir",
            "crear",
            "diseñar",
            "investigar",
            "analizar",
            "comparar",
            "refactorizar",
            "migrar",
            "integrar",
            "implement",
            "build",
            "create",
            "design",
            "research",
            "analyze",
        ]
        task_lower = task_description.lower()
        return any(kw in task_lower for kw in complexity_keywords)

    def create_spec(self, title: str, task_description: str) -> Spec:
        """Crea una spec básica para una tarea dada."""
        spec = Spec(title=title)

        # Requisito básico derivado de la descripción
        spec.requirements.append(
            Requirement(
                when=f"el usuario solicita: {task_description}",
                shall="completar la tarea de manera autónoma y documentar el proceso",
                priority="must",
            )
        )
        spec.requirements.append(
            Requirement(
                when="se encuentre un error o bloqueo",
                shall="intentar auto-corrección antes de escalar al usuario",
                priority="must",
            )
        )

        # Decisión de diseño básica
        spec.design_decisions.append(
            DesignDecision(
                title="Estrategia de Ejecución",
                rationale="Definir el enfoque antes de ejecutar para evitar retrabajo",
                alternatives_considered=["Ejecución directa sin spec (rechazado: propenso a errores)"],
            )
        )

        # Tareas básicas
        spec.tasks = [
            Task(id="T1", description="Analizar el contexto y requisitos"),
            Task(id="T2", description="Ejecutar la tarea principal", depends_on=["T1"]),
            Task(id="T3", description="Validar el resultado", depends_on=["T2"]),
            Task(id="T4", description="Reportar al usuario", depends_on=["T3"]),
        ]

        # Guardar la spec
        spec_dir = self.specs_dir / title.replace(" ", "_").lower()[:50]
        spec.save(spec_dir)
        self.active_specs[title] = spec

        return spec

    def load_spec(self, title: str) -> Optional[Spec]:
        """Carga una spec existente por título."""
        return self.active_specs.get(title)

    def list_active_specs(self) -> list[dict]:
        """Lista todas las specs activas con su progreso."""
        return [{"title": title, **spec.progress()} for title, spec in self.active_specs.items()]


# Instancia global
_planner: Optional[SpecDrivenPlanner] = None


def get_spec_planner() -> SpecDrivenPlanner:
    """Retorna la instancia global del SpecDrivenPlanner."""
    global _planner
    if _planner is None:
        _planner = SpecDrivenPlanner()
    return _planner
