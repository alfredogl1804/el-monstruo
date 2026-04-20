"""
El Monstruo — Delegate Task Tool (Sprint 7)
=============================================
Multi-agent orchestration via role-based delegation.

Architecture (validated by GPT-5.4 Consejo, 2026-04-18):
  - Option A "con esteroides": simple delegation via router.execute()
  - Each delegate gets: task + role system prompt + relevant_context + constraints
  - Delegates CANNOT delegate (MAX_DELEGATION_DEPTH = 1)
  - Max 2 delegations per LLM turn
  - Auto-executable (no HITL) — sensitive actions are gated downstream

Anti-autoboicot: All model IDs from config/model_catalog.py (validated 2026-04-18).
Principio: El Monstruo orquesta. Los delegados ejecutan.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Optional

import structlog

logger = structlog.get_logger("tools.delegate")

# ── Guards ─────────────────────────────────────────────────────────────
MAX_DELEGATION_DEPTH = 1  # Delegates cannot delegate
MAX_DELEGATIONS_PER_TURN = 3  # Max parallel delegations in one call
MAX_TASK_LENGTH = 4000  # Max chars for task description
MAX_CONTEXT_LENGTH = 8000  # Max chars for relevant_context
DELEGATE_TIMEOUT_S = 60  # Default timeout per delegation

# ── Role → Model Mapping ──────────────────────────────────────────────
# Uses FALLBACK_CHAINS from model_catalog.py for automatic fallback.
# First model in each chain is the primary.

ROLE_CONFIGS: dict[str, dict[str, Any]] = {
    "estratega": {
        "primary_model": "gpt-5.4",
        "temperature": 0.3,
        "max_tokens": 4000,
        "system_prompt_key": "estratega",
        "description": "Strategic analysis, business decisions, opportunity evaluation",
    },
    "investigador": {
        "primary_model": "sonar-reasoning-pro",
        "temperature": 0.2,
        "max_tokens": 4000,
        "system_prompt_key": "investigador",
        "description": "Research, fact-checking, data synthesis with web sources",
    },
    "razonador": {
        "primary_model": "deepseek-r1-0528",
        "temperature": 0.2,
        "max_tokens": 4000,
        "system_prompt_key": None,  # Uses generic reasoning prompt
        "description": "Complex reasoning, logic decomposition, step-by-step analysis",
    },
    "critico": {
        "primary_model": "grok-4.20",
        "temperature": 0.2,
        "max_tokens": 3000,
        "system_prompt_key": "critico",
        "description": "Critical review, risk detection, assumption validation",
    },
    "creativo": {
        "primary_model": "gemini-3.1-pro",
        "temperature": 0.8,
        "max_tokens": 4000,
        "system_prompt_key": "creativo",
        "description": "Creative ideation, content generation, innovative solutions",
    },
    "arquitecto": {
        "primary_model": "claude-opus-4-7",
        "temperature": 0.3,
        "max_tokens": 4000,
        "system_prompt_key": "arquitecto",
        "description": "System design, architecture decisions, technical planning",
    },
    "codigo": {
        "primary_model": "claude-opus-4-7",
        "temperature": 0.2,
        "max_tokens": 4000,
        "system_prompt_key": None,  # Uses generic code prompt
        "description": "Code generation, debugging, technical implementation",
    },
    "sintetizador": {
        "primary_model": "gpt-5.4",
        "temperature": 0.3,
        "max_tokens": 4000,
        "system_prompt_key": None,  # Uses generic synthesis prompt
        "description": "Synthesize multiple inputs into coherent output",
    },
    "verificador": {
        "primary_model": "gemini-3.1-flash-lite",
        "temperature": 0.1,
        "max_tokens": 2000,
        "system_prompt_key": None,
        "description": "Quick verification, fact-checking, consistency validation",
    },
}

# Roles that don't have a dedicated brain prompt get a generic one
GENERIC_ROLE_PROMPTS: dict[str, str] = {
    "razonador": (
        "Eres un razonador experto. Descompones problemas complejos en pasos "
        "lógicos, identificas supuestos implícitos, y produces conclusiones "
        "bien fundamentadas. Muestra tu cadena de razonamiento."
    ),
    "codigo": (
        "Eres un experto en programación. Escribes código limpio, eficiente "
        "y bien documentado. Explicas tus decisiones técnicas. Priorizas "
        "soluciones probadas y mantenibles."
    ),
    "sintetizador": (
        "Eres un sintetizador experto. Tu trabajo es tomar múltiples fuentes "
        "de información y producir un documento coherente, completo y accionable. "
        "Preserva los matices pero elimina la redundancia."
    ),
    "verificador": (
        "Eres un verificador. Tu trabajo es validar afirmaciones, detectar "
        "inconsistencias, y confirmar o refutar datos. Sé preciso y conciso. "
        "Si algo no se puede verificar, dilo explícitamente."
    ),
}


async def delegate_task(
    task: str,
    role: str,
    mode: str = "single",
    relevant_context: str = "",
    constraints: Optional[list[str]] = None,
    parallel_roles: Optional[list[str]] = None,
    model_hint: Optional[str] = None,
    timeout_s: Optional[int] = None,
) -> dict[str, Any]:
    """
    Delegate a cognitive task to a specialized role/model.

    Args:
        task: The task description for the delegate
        role: Role name from ROLE_CONFIGS (estratega, investigador, etc.)
        mode: "single" (one role) or "parallel" (multiple roles, synthesized)
        relevant_context: Curated context for the delegate (NOT full conversation)
        constraints: List of constraints for the delegate
        parallel_roles: Roles to use in parallel mode (overrides role param)
        model_hint: Override the default model for the role
        timeout_s: Timeout in seconds (default: 60)

    Returns:
        Dict with role, response, model_used, latency_ms, and metadata
    """
    time.monotonic()

    # ── Input validation ──────────────────────────────────────────────
    if not task or not task.strip():
        return {"error": "Task description is required", "role": role}

    if len(task) > MAX_TASK_LENGTH:
        task = task[:MAX_TASK_LENGTH] + "... [truncated]"

    if relevant_context and len(relevant_context) > MAX_CONTEXT_LENGTH:
        relevant_context = relevant_context[:MAX_CONTEXT_LENGTH] + "... [truncated]"

    effective_timeout = timeout_s or DELEGATE_TIMEOUT_S

    # ── Mode dispatch ─────────────────────────────────────────────────
    if mode == "parallel":
        roles_to_use = parallel_roles or [role]
        if len(roles_to_use) > MAX_DELEGATIONS_PER_TURN:
            roles_to_use = roles_to_use[:MAX_DELEGATIONS_PER_TURN]
            logger.warning(
                "delegate_parallel_truncated",
                requested=len(parallel_roles or []),
                max=MAX_DELEGATIONS_PER_TURN,
            )
        return await _parallel_delegate(
            task=task,
            roles=roles_to_use,
            relevant_context=relevant_context,
            constraints=constraints or [],
            model_hint=model_hint,
            timeout_s=effective_timeout,
        )
    else:
        return await _single_delegate(
            task=task,
            role=role,
            relevant_context=relevant_context,
            constraints=constraints or [],
            model_hint=model_hint,
            timeout_s=effective_timeout,
        )


async def _single_delegate(
    task: str,
    role: str,
    relevant_context: str,
    constraints: list[str],
    model_hint: Optional[str],
    timeout_s: int,
) -> dict[str, Any]:
    """Execute a single delegation to one role."""
    start_time = time.monotonic()

    # Resolve role config
    role_config = ROLE_CONFIGS.get(role)
    if role_config is None:
        available = ", ".join(sorted(ROLE_CONFIGS.keys()))
        return {
            "error": f"Unknown role: '{role}'. Available roles: {available}",
            "role": role,
        }

    # Build the delegate's system prompt
    system_prompt = _build_delegate_prompt(role, role_config, constraints)

    # Build the user message with task + context
    user_message = _build_delegate_message(task, relevant_context)

    # Resolve model
    model_key = model_hint or role_config["primary_model"]
    temperature = role_config["temperature"]
    max_tokens = role_config["max_tokens"]

    logger.info(
        "delegate_single_start",
        role=role,
        model=model_key,
        task_preview=task[:100],
    )

    try:
        # Import router components
        from config.model_catalog import FALLBACK_CHAINS as ROLE_FALLBACKS
        from config.model_catalog import MODELS
        from router.llm_client import LLMClient

        llm = LLMClient()

        # Build fallback chain: model_hint (if provided) + role's chain
        if model_hint and model_hint in MODELS:
            models_to_try = [model_hint]
        else:
            role_chain = ROLE_FALLBACKS.get(role, [])
            models_to_try = role_chain if role_chain else [model_key]

        # Try each model in the chain
        response_text = ""
        model_used = ""
        usage = {}

        for attempt_model in models_to_try:
            model_config = MODELS.get(attempt_model)
            if model_config is None:
                continue

            effective_config = dict(model_config)
            effective_config["max_tokens"] = max_tokens
            if effective_config.get("use_max_completion_tokens"):
                effective_config["max_completion_tokens"] = max_tokens

            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ]

                resp, usg = await asyncio.wait_for(
                    llm.chat(
                        model_config=effective_config,
                        messages=messages,
                        temperature=temperature,
                    ),
                    timeout=timeout_s,
                )

                response_text = resp
                model_used = attempt_model
                usage = usg
                break

            except asyncio.TimeoutError:
                logger.warning("delegate_timeout", model=attempt_model, timeout=timeout_s)
                continue
            except Exception as e:
                logger.warning("delegate_model_failed", model=attempt_model, error=str(e))
                continue

        if not response_text:
            return {
                "error": f"All models failed for role '{role}'",
                "role": role,
                "models_tried": models_to_try,
            }

        elapsed_ms = (time.monotonic() - start_time) * 1000

        logger.info(
            "delegate_single_complete",
            role=role,
            model_used=model_used,
            latency_ms=f"{elapsed_ms:.0f}",
            response_len=len(response_text),
        )

        return {
            "role": role,
            "response": response_text,
            "model_used": model_used,
            "latency_ms": round(elapsed_ms),
            "tokens": usage,
            "mode": "single",
        }

    except Exception as e:
        elapsed_ms = (time.monotonic() - start_time) * 1000
        logger.error("delegate_single_error", role=role, error=str(e))
        return {
            "error": str(e),
            "role": role,
            "latency_ms": round(elapsed_ms),
        }


async def _parallel_delegate(
    task: str,
    roles: list[str],
    relevant_context: str,
    constraints: list[str],
    model_hint: Optional[str],
    timeout_s: int,
) -> dict[str, Any]:
    """Execute parallel delegations to multiple roles, then synthesize."""
    start_time = time.monotonic()

    logger.info(
        "delegate_parallel_start",
        roles=roles,
        task_preview=task[:100],
    )

    # Launch all delegations in parallel
    tasks = [
        _single_delegate(
            task=task,
            role=r,
            relevant_context=relevant_context,
            constraints=constraints,
            model_hint=model_hint,
            timeout_s=timeout_s,
        )
        for r in roles
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect successful responses
    successful = []
    failed = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed.append({"role": roles[i], "error": str(result)})
        elif isinstance(result, dict) and "error" in result:
            failed.append(result)
        else:
            successful.append(result)

    if not successful:
        return {
            "error": "All parallel delegations failed",
            "roles": roles,
            "failures": failed,
        }

    # If only one succeeded, return it directly
    if len(successful) == 1:
        result = successful[0]
        result["mode"] = "parallel"
        result["parallel_roles"] = roles
        result["failed_roles"] = [f["role"] for f in failed]
        return result

    # Synthesize multiple responses
    synthesis_input = _build_synthesis_input(task, successful)

    synthesis_result = await _single_delegate(
        task=synthesis_input,
        role="sintetizador",
        relevant_context="",
        constraints=[
            "Sintetiza las perspectivas de los diferentes roles",
            "Preserva los matices y diferencias de opinión",
            "Produce un documento coherente y accionable",
            "Si hay contradicciones, señálalas explícitamente",
        ],
        model_hint=None,
        timeout_s=timeout_s,
    )

    elapsed_ms = (time.monotonic() - start_time) * 1000

    return {
        "mode": "parallel",
        "parallel_roles": roles,
        "individual_responses": successful,
        "failed_roles": [f["role"] for f in failed],
        "synthesis": synthesis_result.get("response", ""),
        "synthesis_model": synthesis_result.get("model_used", ""),
        "total_latency_ms": round(elapsed_ms),
    }


# ── Prompt Builders ───────────────────────────────────────────────────


def _build_delegate_prompt(
    role: str,
    role_config: dict[str, Any],
    constraints: list[str],
) -> str:
    """Build the system prompt for a delegate."""
    # Try to get brain prompt from system_prompts.py
    prompt_key = role_config.get("system_prompt_key")
    base_prompt = ""

    if prompt_key:
        try:
            from prompts.system_prompts import get_brain_prompt

            base_prompt = get_brain_prompt(prompt_key)
        except Exception:
            pass

    if not base_prompt:
        base_prompt = GENERIC_ROLE_PROMPTS.get(role, f"Eres un experto en el rol de {role}.")

    # Add delegation context
    delegation_header = (
        "\n\n## Contexto de Delegación\n"
        "Esta es una sub-tarea delegada por El Monstruo. "
        "Responde SOLO a la tarea asignada. No preguntes — ejecuta. "
        "No tienes acceso a herramientas. Usa solo tu conocimiento y el contexto proporcionado."
    )

    # Add constraints
    constraints_section = ""
    if constraints:
        constraints_section = "\n\n## Restricciones\n" + "\n".join(f"- {c}" for c in constraints)

    return base_prompt + delegation_header + constraints_section


def _build_delegate_message(task: str, relevant_context: str) -> str:
    """Build the user message for a delegate."""
    parts = [f"## Tarea\n{task}"]

    if relevant_context:
        parts.append(f"\n## Contexto Relevante\n{relevant_context}")

    return "\n".join(parts)


def _build_synthesis_input(task: str, responses: list[dict]) -> str:
    """Build the synthesis input from multiple delegate responses."""
    parts = [
        f"## Tarea Original\n{task}",
        "\n## Respuestas de los Delegados\n",
    ]

    for resp in responses:
        role = resp.get("role", "unknown")
        model = resp.get("model_used", "unknown")
        text = resp.get("response", "")
        parts.append(f"### {role.upper()} (modelo: {model})\n{text}\n")

    return "\n".join(parts)


# ── Public API for tool_dispatch ──────────────────────────────────────


def get_available_roles() -> list[dict[str, str]]:
    """Return list of available roles with descriptions."""
    return [{"role": role, "description": config["description"]} for role, config in ROLE_CONFIGS.items()]
