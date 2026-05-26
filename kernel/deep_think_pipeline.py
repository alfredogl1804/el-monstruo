from __future__ import annotations

import asyncio
import time
from typing import Any

import structlog

from contracts.kernel_interface import IntentType
from router.engine import RouterEngine

logger = structlog.get_logger("kernel.deep_think")


async def run_deep_think_pipeline(
    message: str,
    context: dict[str, Any],
    router: RouterEngine,
    model: str = "gpt-5.5",
) -> tuple[str, dict[str, Any]]:
    """
    Ejecuta el pipeline de razonamiento multi-paso para el intent DEEP_THINK.

    Pasos:
    1. Hipótesis/Planificación: El modelo genera un marco de análisis.
    2. Consulta a Sabios (Opcional): Si la pregunta es compleja, consulta a otros modelos.
    3. Síntesis: Genera la respuesta final estructurada.
    """
    start_time = time.monotonic()
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}

    logger.info("deep_think_pipeline_start", message_preview=message[:100])

    # Paso 1: Generar Hipótesis / Marco de Análisis
    plan_prompt = (
        "Eres el Estratega de El Monstruo. Analiza la siguiente solicitud y crea un plan de "
        "razonamiento paso a paso. NO respondas a la solicitud todavía. Solo genera el marco "
        "de análisis: qué preguntas debes responder, qué perspectivas considerar y qué datos "
        "necesitas de la memoria proporcionada.\n\n"
        "Solicitud: " + message
    )

    plan_context = dict(context)
    plan_context["system_prompt"] = "Eres un planificador analítico experto."

    plan_response, plan_usage = await router.execute(
        message=plan_prompt,
        model=model,
        intent=IntentType.DEEP_THINK,
        context=plan_context,
    )

    _accumulate_usage(total_usage, plan_usage)
    logger.info("deep_think_plan_generated", plan_preview=plan_response[:100])

    # Paso 2: Consulta a Sabios (CIDP)
    # Consultamos a Claude y Gemini en paralelo para obtener perspectivas adicionales
    sabios_context = dict(context)
    sabios_context["system_prompt"] = "Eres un experto consultor. Responde a la solicitud de forma concisa y directa."

    async def consultar_sabio(sabio_model: str, rol: str) -> str:
        try:
            prompt = f"Como {rol}, analiza esta solicitud: {message}\n\nConsidera este plan inicial:\n{plan_response}"
            resp, usage = await router.execute(
                message=prompt,
                model=sabio_model,
                intent=IntentType.DEEP_THINK,
                context=sabios_context,
            )
            _accumulate_usage(total_usage, usage)
            return f"### Perspectiva de {rol} ({sabio_model}):\n{resp}"
        except Exception as e:
            logger.warning("sabio_failed", model=sabio_model, error=str(e))
            return f"### Perspectiva de {rol} ({sabio_model}):\nFalló la consulta: {str(e)}"

    # Ejecutar consultas en paralelo
    sabios_tasks = [
        consultar_sabio("claude-opus-4-7", "Arquitecto/Crítico"),
        consultar_sabio("gemini-3.1-pro", "Investigador/Creativo"),
    ]

    sabios_resultados = await asyncio.gather(*sabios_tasks)
    sabios_texto = "\n\n".join(sabios_resultados)

    logger.info("deep_think_sabios_consulted", count=len(sabios_resultados))

    # Paso 3: Síntesis Final
    sintesis_prompt = (
        "Eres El Monstruo en modo Deep Think. Sintetiza una respuesta final exhaustiva a la solicitud original.\n\n"
        "Solicitud Original: " + message + "\n\n"
        "Plan de Análisis:\n" + plan_response + "\n\n"
        "Perspectivas de los Sabios:\n" + sabios_texto + "\n\n"
        "Instrucciones para la síntesis:\n"
        "1. Sigue el plan de análisis.\n"
        "2. Integra las perspectivas de los sabios, resolviendo contradicciones si las hay.\n"
        "3. Usa la memoria y el contexto proporcionado en tu system prompt.\n"
        "4. Estructura la respuesta con headers (##), bullet points y tablas si es útil.\n"
        "5. Termina con una conclusión clara y un nivel de confianza."
    )

    final_response, final_usage = await router.execute(
        message=sintesis_prompt,
        model=model,
        intent=IntentType.DEEP_THINK,
        context=context,  # Usamos el contexto original enriquecido
    )

    _accumulate_usage(total_usage, final_usage)

    elapsed_ms = (time.monotonic() - start_time) * 1000
    logger.info("deep_think_pipeline_completed", latency_ms=elapsed_ms, total_tokens=total_usage["completion_tokens"])

    return final_response, total_usage


def _accumulate_usage(total: dict[str, Any], current: dict[str, Any]) -> None:
    total["prompt_tokens"] += current.get("prompt_tokens", 0)
    total["completion_tokens"] += current.get("completion_tokens", 0)
    total["cost_usd"] += current.get("cost_usd", 0.0)
