"""
El Monstruo — Router Engine (Día 1)
=====================================
Cliente del proxy LiteLLM para routing inteligente de modelos.
El Router NO decide las transiciones de estado — eso es del Kernel.
El Router solo decide: qué modelo usar y ejecuta la llamada.

Principio: El Monstruo decide el routing. LiteLLM ejecuta.
"""

from __future__ import annotations

import os
from typing import Any, AsyncIterator, Optional

import httpx
import structlog

from contracts.kernel_interface import IntentType

logger = structlog.get_logger("router")


# ── Intent → Model Mapping ──────────────────────────────────────────

# Configurable mapping: intent → preferred model name (as defined in litellm_config.yaml)
DEFAULT_MODEL_MAP: dict[IntentType, str] = {
    IntentType.CHAT: "fast-chat",         # Gemini Flash — rápido y barato
    IntentType.DEEP_THINK: "gpt-5",       # GPT-5 — razonamiento complejo
    IntentType.EXECUTE: "claude-sonnet",   # Claude — código y ejecución
    IntentType.BACKGROUND: "gemini-flash", # Gemini — tareas largas
    IntentType.SYSTEM: "fast-chat",        # Respuestas rápidas del sistema
}

# Fallback chain per model
FALLBACK_CHAIN: dict[str, list[str]] = {
    "gpt-5": ["claude-sonnet", "gemini-flash"],
    "claude-sonnet": ["gpt-5", "gemini-flash"],
    "gemini-flash": ["gpt-5", "claude-sonnet"],
    "fast-chat": ["gpt-5"],
    "grok": ["gpt-5", "deepseek-r1"],
    "deepseek-r1": ["grok", "gpt-5"],
    "sonar-pro": ["gpt-5", "gemini-flash"],
}

# Intent classification prompt
INTENT_SYSTEM_PROMPT = """You are an intent classifier for El Monstruo AI system.
Classify the user message into exactly ONE of these intents:
- chat: Simple conversation, greetings, quick questions
- deep_think: Complex analysis, reasoning, comparison, evaluation, long explanations
- execute: Actions to perform (create, send, publish, generate, build)
- background: Long-running tasks that should run asynchronously
- system: System commands, status checks, health queries

Respond with ONLY the intent name, nothing else."""


class RouterEngine:
    """
    Router that talks to LiteLLM proxy for model execution.

    Responsibilities:
        - Classify intent from user message
        - Map intent to optimal model
        - Execute requests via LiteLLM proxy
        - Handle fallbacks on failure
        - Track usage (tokens, cost)
    """

    def __init__(
        self,
        litellm_url: Optional[str] = None,
        litellm_key: Optional[str] = None,
        model_map: Optional[dict[IntentType, str]] = None,
        use_llm_classification: bool = True,
    ) -> None:
        self._base_url = (
            litellm_url
            or os.environ.get("LITELLM_URL", "http://localhost:4000")
        )
        self._api_key = (
            litellm_key
            or os.environ.get("LITELLM_MASTER_KEY", "sk-monstruo-dev")
        )
        self._model_map = model_map or DEFAULT_MODEL_MAP
        self._use_llm_classification = use_llm_classification
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    # ── Public Interface ────────────────────────────────────────────

    async def route(
        self,
        message: str,
        channel: str = "api",
        context: Optional[dict[str, Any]] = None,
    ) -> tuple[IntentType, str]:
        """
        Classify intent and select model.
        Returns (intent, model_name).
        """
        # Classify intent
        if self._use_llm_classification:
            intent = await self._classify_intent_llm(message)
        else:
            intent = _classify_intent_local(message)

        # Select model based on intent
        model = self._model_map.get(intent, "gpt-5")

        # Override: if context requests a specific model, use it
        if context and context.get("force_model"):
            model = context["force_model"]

        logger.info(
            "route_decided",
            intent=intent.value,
            model=model,
            channel=channel,
            message_preview=message[:80],
        )

        return intent, model

    async def execute(
        self,
        message: str,
        model: str,
        intent: IntentType,
        context: Optional[dict[str, Any]] = None,
    ) -> tuple[str, dict[str, Any]]:
        """
        Execute a request against the selected model via LiteLLM proxy.
        Returns (response_text, usage_dict).
        """
        system_prompt = _get_system_prompt(intent, context)
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        # Add conversation history if provided
        if context and context.get("history"):
            # Insert history before the current message
            history = context["history"]
            messages = (
                messages[:1]  # system prompt
                + history
                + messages[1:]  # current message
            )

        # Try primary model, then fallbacks
        models_to_try = [model] + FALLBACK_CHAIN.get(model, [])

        last_error = None
        for attempt_model in models_to_try:
            try:
                response, usage = await self._call_litellm(attempt_model, messages)

                if attempt_model != model:
                    logger.warning(
                        "fallback_used",
                        original_model=model,
                        fallback_model=attempt_model,
                    )

                return response, usage

            except Exception as e:
                last_error = e
                logger.warning(
                    "model_failed",
                    model=attempt_model,
                    error=str(e),
                )
                continue

        # All models failed
        raise RuntimeError(
            f"All models failed for intent {intent.value}. "
            f"Tried: {models_to_try}. Last error: {last_error}"
        )

    async def stream(
        self,
        message: str,
        model: str,
        intent: IntentType,
    ) -> AsyncIterator[str]:
        """Stream tokens from model execution."""
        system_prompt = _get_system_prompt(intent)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }

        async with self._client.stream(
            "POST",
            "/v1/chat/completions",
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    import json
                    try:
                        chunk = json.loads(line[6:])
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

    async def health_check(self) -> dict[str, Any]:
        """Check if LiteLLM proxy is healthy."""
        try:
            resp = await self._client.get("/health")
            return {"status": "ok", "litellm": resp.json()}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ── Internal Methods ────────────────────────────────────────────

    async def _call_litellm(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> tuple[str, dict[str, Any]]:
        """Make a chat completion call to LiteLLM proxy."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
        }

        resp = await self._client.post("/v1/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

        # Extract response
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("No choices in LiteLLM response")

        content = choices[0].get("message", {}).get("content", "")

        # Extract usage
        usage_data = data.get("usage", {})
        usage = {
            "prompt_tokens": usage_data.get("prompt_tokens", 0),
            "completion_tokens": usage_data.get("completion_tokens", 0),
            "total_tokens": usage_data.get("total_tokens", 0),
            "cost_usd": data.get("_hidden_params", {}).get("response_cost", 0.0),
            "model_used": data.get("model", model),
        }

        return content, usage

    async def _classify_intent_llm(self, message: str) -> IntentType:
        """Classify intent using a fast LLM call."""
        try:
            payload = {
                "model": "fast-chat",
                "messages": [
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                "temperature": 0.0,
                "max_tokens": 20,
            }

            resp = await self._client.post("/v1/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()

            raw = data["choices"][0]["message"]["content"].strip().lower()

            intent_map = {
                "chat": IntentType.CHAT,
                "deep_think": IntentType.DEEP_THINK,
                "execute": IntentType.EXECUTE,
                "background": IntentType.BACKGROUND,
                "system": IntentType.SYSTEM,
            }

            return intent_map.get(raw, IntentType.CHAT)

        except Exception as e:
            logger.warning("llm_classification_failed", error=str(e))
            return _classify_intent_local(message)


# ── System Prompts per Intent ───────────────────────────────────────

def _get_system_prompt(
    intent: IntentType,
    context: Optional[dict[str, Any]] = None,
) -> str:
    """Get the system prompt based on intent."""
    base_identity = (
        "Eres El Monstruo, un sistema de inteligencia artificial soberana "
        "creado por Alfredo Góngora para Hive Business Center. "
        "Respondes en español a menos que te hablen en otro idioma. "
        "Eres directo, preciso y profesional."
    )

    intent_additions = {
        IntentType.CHAT: (
            " Mantén las respuestas concisas y útiles. "
            "Si la pregunta es simple, responde brevemente."
        ),
        IntentType.DEEP_THINK: (
            " Analiza en profundidad. Usa razonamiento paso a paso. "
            "Considera múltiples perspectivas. Cita fuentes cuando sea posible."
        ),
        IntentType.EXECUTE: (
            " El usuario quiere que ejecutes una acción. "
            "Confirma qué vas a hacer antes de ejecutar. "
            "Si necesitas más información, pregunta."
        ),
        IntentType.BACKGROUND: (
            " Esta es una tarea de fondo. Sé exhaustivo y detallado. "
            "Proporciona un resumen ejecutivo al final."
        ),
        IntentType.SYSTEM: (
            " Responde con información del sistema de forma clara y estructurada."
        ),
    }

    # Add custom system prompt from context if provided
    custom = ""
    if context and context.get("system_prompt"):
        custom = f"\n\nInstrucciones adicionales: {context['system_prompt']}"

    return base_identity + intent_additions.get(intent, "") + custom


# ── Local Intent Classification (no LLM) ───────────────────────────

def _classify_intent_local(message: str) -> IntentType:
    """Keyword-based intent classification. Fast, free, offline."""
    msg = message.lower().strip()

    deep_keywords = {
        "analiza", "piensa", "razona", "explica", "compara", "evalúa",
        "investiga", "profundiza", "detalla", "por qué",
        "analyze", "think", "reason", "explain", "compare", "evaluate",
    }
    exec_keywords = {
        "haz", "ejecuta", "crea", "genera", "envía", "publica",
        "construye", "despliega", "configura", "instala",
        "do", "execute", "create", "generate", "send", "publish",
    }
    system_keywords = {
        "status", "health", "estado", "salud", "/start", "/help",
        "/status", "/cancel", "/stop",
    }

    words = set(msg.split())

    if words & system_keywords or msg.startswith("/"):
        return IntentType.SYSTEM
    if words & exec_keywords:
        return IntentType.EXECUTE
    if words & deep_keywords or len(msg) > 500:
        return IntentType.DEEP_THINK
    return IntentType.CHAT
