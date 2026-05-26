"""
StateWriterTool — Sprint 50
============================
Permite al Task Planner / Router persistir el estado de tareas largas
en archivos locales del sandbox, replicando la estrategia de Manus AI
(Módulo M04: Manejo de Contexto y Memoria).

Cuando el contexto se llena o una tarea es muy larga, el agente puede:
1. Guardar su progreso actual en un archivo .progress.json
2. Cargar el progreso en la siguiente iteración
3. Listar tareas en progreso
4. Limpiar tareas completadas

Esto resuelve la brecha crítica #1 identificada en el Backlog Técnico.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Directorio donde se guardan los estados de tareas
STATE_DIR = Path(os.getenv("STATE_DIR", "/tmp/monstruo_state"))
STATE_DIR.mkdir(parents=True, exist_ok=True)


def _task_path(task_id: str) -> Path:
    """Retorna la ruta del archivo de estado para un task_id dado."""
    # Sanitizar el task_id para evitar path traversal
    safe_id = "".join(c for c in task_id if c.isalnum() or c in "-_")[:64]
    return STATE_DIR / f"{safe_id}.progress.json"


def save_task_state(
    task_id: str,
    description: str,
    current_step: int,
    total_steps: int,
    context_summary: str,
    intermediate_results: list[dict[str, Any]],
    metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Guarda el estado actual de una tarea larga en disco.

    Args:
        task_id: Identificador único de la tarea (ej. "research_ai_agents_2026")
        description: Descripción breve de la tarea
        current_step: Paso actual de ejecución
        total_steps: Total de pasos estimados
        context_summary: Resumen del contexto acumulado hasta ahora
        intermediate_results: Lista de resultados parciales obtenidos
        metadata: Datos adicionales opcionales

    Returns:
        dict con status y ruta del archivo guardado
    """
    state = {
        "task_id": task_id,
        "description": description,
        "current_step": current_step,
        "total_steps": total_steps,
        "progress_pct": round((current_step / max(total_steps, 1)) * 100, 1),
        "context_summary": context_summary,
        "intermediate_results": intermediate_results,
        "metadata": metadata or {},
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "saved_at_ts": time.time(),
    }

    path = _task_path(task_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    return {
        "status": "saved",
        "task_id": task_id,
        "path": str(path),
        "progress_pct": state["progress_pct"],
        "message": f"Estado guardado: paso {current_step}/{total_steps} ({state['progress_pct']}%)",
    }


def load_task_state(task_id: str) -> dict[str, Any]:
    """
    Carga el estado guardado de una tarea.

    Args:
        task_id: Identificador único de la tarea

    Returns:
        dict con el estado guardado, o {"status": "not_found"} si no existe
    """
    path = _task_path(task_id)
    if not path.exists():
        return {
            "status": "not_found",
            "task_id": task_id,
            "message": f"No hay estado guardado para la tarea '{task_id}'",
        }

    with open(path, "r", encoding="utf-8") as f:
        state = json.load(f)

    state["status"] = "loaded"
    state["message"] = (
        f"Estado cargado: paso {state['current_step']}/{state['total_steps']} "
        f"({state['progress_pct']}%) — guardado {state['saved_at']}"
    )
    return state


def list_active_tasks() -> dict[str, Any]:
    """
    Lista todas las tareas con estado guardado.

    Returns:
        dict con lista de tareas activas y su progreso
    """
    tasks = []
    for path in sorted(STATE_DIR.glob("*.progress.json")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            tasks.append(
                {
                    "task_id": state["task_id"],
                    "description": state["description"],
                    "progress_pct": state["progress_pct"],
                    "current_step": state["current_step"],
                    "total_steps": state["total_steps"],
                    "saved_at": state["saved_at"],
                }
            )
        except (json.JSONDecodeError, KeyError):
            continue

    return {
        "status": "ok",
        "active_tasks": len(tasks),
        "tasks": tasks,
    }


def complete_task(task_id: str) -> dict[str, Any]:
    """
    Marca una tarea como completada y elimina su archivo de estado.

    Args:
        task_id: Identificador único de la tarea

    Returns:
        dict con confirmación
    """
    path = _task_path(task_id)
    if not path.exists():
        return {
            "status": "not_found",
            "task_id": task_id,
            "message": f"No hay estado guardado para la tarea '{task_id}'",
        }

    path.unlink()
    return {
        "status": "completed",
        "task_id": task_id,
        "message": f"Tarea '{task_id}' marcada como completada y estado eliminado",
    }


def append_result(task_id: str, result: dict[str, Any]) -> dict[str, Any]:
    """
    Agrega un resultado parcial al estado existente de una tarea.
    Útil para ir acumulando resultados sin reescribir todo el estado.

    Args:
        task_id: Identificador único de la tarea
        result: Resultado parcial a agregar

    Returns:
        dict con confirmación
    """
    state = load_task_state(task_id)
    if state.get("status") == "not_found":
        return state

    state["intermediate_results"].append(
        {
            **result,
            "appended_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    state["saved_at"] = datetime.now(timezone.utc).isoformat()
    state["saved_at_ts"] = time.time()

    path = _task_path(task_id)
    with open(path, "w", encoding="utf-8") as f:
        # Eliminar claves de metadatos de carga antes de guardar
        save_state = {k: v for k, v in state.items() if k not in ("status", "message")}
        json.dump(save_state, f, ensure_ascii=False, indent=2)

    return {
        "status": "appended",
        "task_id": task_id,
        "total_results": len(state["intermediate_results"]),
        "message": f"Resultado agregado. Total: {len(state['intermediate_results'])} resultados",
    }


# ===================== TOOL DEFINITIONS =====================
# Formato compatible con el router del Monstruo

TOOL_DEFINITIONS = [
    {
        "name": "save_task_state",
        "description": (
            "Guarda el estado actual de una tarea larga en disco para poder retomarlo "
            "si el contexto se llena o la sesión se interrumpe. "
            "USAR cuando: (1) la tarea tiene más de 5 pasos, (2) el contexto supera el 70% del límite, "
            "(3) la tarea durará más de 10 minutos."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID único de la tarea, ej: 'research_ai_agents_2026'",
                },
                "description": {
                    "type": "string",
                    "description": "Descripción breve de qué hace esta tarea",
                },
                "current_step": {
                    "type": "integer",
                    "description": "Paso actual de ejecución (1-based)",
                },
                "total_steps": {
                    "type": "integer",
                    "description": "Total de pasos estimados para completar la tarea",
                },
                "context_summary": {
                    "type": "string",
                    "description": "Resumen del contexto y hallazgos acumulados hasta ahora",
                },
                "intermediate_results": {
                    "type": "array",
                    "description": "Lista de resultados parciales obtenidos",
                    "items": {"type": "object"},
                },
            },
            "required": ["task_id", "description", "current_step", "total_steps", "context_summary"],
        },
    },
    {
        "name": "load_task_state",
        "description": (
            "Carga el estado guardado de una tarea para retomar desde donde se quedó. "
            "USAR al inicio de una sesión si hay tareas pendientes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID único de la tarea a cargar",
                },
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "list_active_tasks",
        "description": "Lista todas las tareas con estado guardado y su progreso actual.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "complete_task",
        "description": "Marca una tarea como completada y elimina su estado guardado.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID único de la tarea a completar",
                },
            },
            "required": ["task_id"],
        },
    },
]
