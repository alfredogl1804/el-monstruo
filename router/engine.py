"""
El Monstruo — Router Engine (Sprint 1 — Soberano)
====================================================
Router inteligente de modelos con cliente multi-proveedor nativo.
NO depende de LiteLLM proxy. Usa SDKs nativos + httpx.

El Router decide: qué modelo usar y ejecuta la llamada.
El Kernel decide: las transiciones de estado.

Convergencia: Usa model_catalog.py para aliases y fallbacks.
System prompts vienen de prompts/system_prompts.py (6 cerebros).

Principio: El Monstruo decide el routing. Los SDKs ejecutan.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import structlog

from contracts.kernel_interface import IntentType
from config.model_catalog import MODELS, FALLBACK_CHAINS
from router.llm_client import LLMClient

logger = structlog.get_logger("router")


# ── Intent → Catalog Model Mapping ──────────────────────────────────
# Maps kernel intents to model_catalog.py keys (not litellm aliases)

DEFAULT_MODEL_MAP: dict[IntentType, str] = {
    IntentType.CHAT: "gemini-3.1-flash-lite",       # Rápido y gratis
    IntentType.DEEP_THINK: "gpt-5.4",               # Razonamiento complejo
    IntentType.EXECUTE: "claude-sonnet-4-6",         # Código y ejecución
    IntentType.BACKGROUND: "gemini-3.1-flash-lite",  # Tareas largas baratas
    IntentType.SYSTEM: "gemini-3.1-flash-lite",      # Respuestas rápidas
}

# Brain → Catalog Model mapping (6 cerebros del Monstruo)
BRAIN_MODEL_MAP: dict[str, str] = {
    "estratega":     "gpt-5.4",
    "investigador":  "sonar-reasoning-pro",
    "arquitecto":    "claude-opus-4-6",
    "creativo":      "gemini-3.1-pro",
    "critico":       "grok-4.20",
    "operador":      "gemini-3.1-flash-lite",
}

# Alias → Catalog key mapping (para compatibilidad con código existente)
ALIAS_TO_CATALOG: dict[str, str] = {
    cfg["litellm_alias"]: name
    for name, cfg in MODELS.items()
    if "litellm_alias" in cfg
}

# Fallback chain per catalog model name
FALLBACK_CHAIN: dict[str, list[str]] = {
    "gpt-5.4": ["claude-opus-4-6", "claude-sonnet-4-6", "gemini-3.1-pro"],
    "claude-opus-4-6": ["gpt-5.4", "claude-sonnet-4-6", "gemini-3.1-pro"],
    "claude-sonnet-4-6": ["gpt-5.4", "claude-opus-4-6", "gemini-3.1-flash-lite"],
    "gemini-3.1-flash-lite": ["gpt-5.4-mini", "kimi-k2.5", "gpt-5.4"],
    "gemini-3.1-pro": ["gpt-5.4", "claude-opus-4-6", "gemini-3.1-flash-lite"],
    "grok-4.20": ["gpt-5.4", "deepseek-r1-0528", "claude-opus-4-6"],
    "deepseek-r1-0528": ["grok-4.20", "gpt-5.4", "claude-opus-4-6"],
    "sonar-reasoning-pro": ["sonar-pro", "gpt-5.4", "grok-4.20"],
    "sonar-pro": ["sonar-reasoning-pro", "gpt-5.4", "gemini-3.1-flash-lite"],
    "gpt-5.4-mini": ["kimi-k2.5", "gemini-3.1-flash-lite"],
    "kimi-k2.5": ["gemini-3.1-flash-lite", "gpt-5.4-mini"],
}

# Intent classification prompt
INTENT_SYSTEM_PROMPT = """You are an intent classifier for El Monstruo AI system.
Classify the user message into exactly ONE of these intents:
- chat: Conversation, greetings, questions, personal queries, asking about projects/preferences/memories, small talk, opinions
- deep_think: Complex analysis, reasoning, comparison, evaluation, research, long explanations, "why" questions
- execute: Actions to perform (create, send, publish, generate, build, deploy, configure, delete)
- background: Long-running tasks that should run asynchronously
- system: ONLY literal system commands like /start /help /status /cancel, or explicit requests about bot health/version

IMPORTANT: Questions like "what is my project?" or "what do you remember about me?" are CHAT, not system.
Only classify as system if the user is asking about the AI system itself (health, version, status) or using a / command.

Respond with ONLY the intent name, nothing else."""


class RouterEngine:
    """
    Router soberano que habla directamente con cada proveedor.

    Responsibilities:
        - Classify intent from user message
        - Map intent to optimal model (or brain to model)
        - Execute requests via SDKs nativos
        - Handle fallbacks on failure
        - Track usage (tokens, cost)
    """

    def __init__(
        self,
        model_map: Optional[dict[IntentType, str]] = None,
        use_llm_classification: bool = True,
    ) -> None:
        self._model_map = model_map or DEFAULT_MODEL_MAP
        self._use_llm_classification = use_llm_classification
        self._llm = LLMClient()

    async def close(self) -> None:
        """Close the LLM client."""
        await self._llm.close()

    # ── Public Interface ────────────────────────────────────────────

    async def route(
        self,
        message: str,
        channel: str = "api",
        context: Optional[dict[str, Any]] = None,
    ) -> tuple[IntentType, str]:
        """
        Classify intent and select model.
        Returns (intent, catalog_model_name).
        """
        # Classify intent
        if self._use_llm_classification:
            intent = await self._classify_intent_llm(message)
        else:
            intent = _classify_intent_local(message)

        # If context specifies a brain, use brain→model mapping
        if context and context.get("brain"):
            brain = context["brain"]
            model = BRAIN_MODEL_MAP.get(brain, "gpt-5.4")
            logger.info(
                "route_by_brain",
                brain=brain,
                model=model,
                channel=channel,
            )
            return intent, model

        # Select model based on intent
        model = self._model_map.get(intent, "gpt-5.4")

        # Override: if context requests a specific model, use it
        if context and context.get("force_model"):
            forced = context["force_model"]
            # Resolve alias to catalog key if needed
            model = ALIAS_TO_CATALOG.get(forced, forced)

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
        Execute a request against the selected model via native SDKs.
        Returns (response_text, usage_dict).
        """
        system_prompt = _get_system_prompt(intent, context)
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        # Add conversation history if provided
        if context and context.get("history"):
            history = context["history"]
            messages = (
                messages[:1]  # system prompt
                + history
                + messages[1:]  # current message
            )

        # Resolve model name: could be alias or catalog key
        catalog_key = ALIAS_TO_CATALOG.get(model, model)

        # Build models to try: primary + fallbacks
        models_to_try = [catalog_key] + FALLBACK_CHAIN.get(catalog_key, [])

        last_error = None
        for attempt_model in models_to_try:
            try:
                model_config = MODELS.get(attempt_model)
                if model_config is None:
                    logger.warning("model_not_in_catalog", model=attempt_model)
                    continue

                response, usage = await self._llm.chat(
                    model_config=model_config,
                    messages=messages,
                    temperature=0.7,
                )

                if attempt_model != catalog_key:
                    logger.warning(
                        "fallback_used",
                        original_model=catalog_key,
                        fallback_model=attempt_model,
                    )

                # Enrich usage with model info
                usage["model_used"] = attempt_model
                usage["provider"] = model_config["provider"]

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

    async def health_check(self) -> dict[str, Any]:
        """Check if at least one model is reachable."""
        try:
            # Quick test with the cheapest model
            model_config = MODELS.get("gemini-3.1-flash-lite")
            if model_config is None:
                return {"status": "error", "error": "gemini-3.1-flash-lite not in catalog"}

            response, usage = await self._llm.chat(
                model_config=model_config,
                messages=[{"role": "user", "content": "ping"}],
                temperature=0.0,
                max_tokens=10,
            )
            return {
                "status": "ok",
                "test_model": "gemini-3.1-flash-lite",
                "response_preview": response[:50],
                "tokens": usage.get("total_tokens", 0),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ── Internal Methods ────────────────────────────────────────────

    async def _classify_intent_llm(self, message: str) -> IntentType:
        """Classify intent using a fast LLM call (Gemini Flash Lite — free)."""
        try:
            model_config = MODELS.get("gemini-3.1-flash-lite")
            if model_config is None:
                return _classify_intent_local(message)

            response, _ = await self._llm.chat(
                model_config=model_config,
                messages=[
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                temperature=0.0,
                max_tokens=20,
            )

            raw = response.strip().lower()

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
    """
    Get the system prompt.
    Priority:
    1. Enriched system_prompt from kernel's enrich() node (has memory context)
    2. Brain-specific prompt (if brain specified)
    3. Default intent-based prompt
    """
    # Priority 1: If enriched system_prompt from enrich() node, use it directly
    # This contains the base identity + relevant memories + knowledge entities
    if context and context.get("system_prompt"):
        enriched = context["system_prompt"]
        # Only use if it's the full enriched prompt (not a short custom instruction)
        if len(enriched) > 100:  # Enriched prompts are always long
            return enriched

    # Priority 2: If a brain is specified, use the rich prompt
    if context and context.get("brain"):
        try:
            from prompts.system_prompts import get_brain_prompt
            return get_brain_prompt(context["brain"])
        except ImportError:
            pass  # Fall through to default

    # Priority 3: Default intent-based prompts
    base_identity = (
        "Eres El Monstruo, un sistema de inteligencia artificial soberana "
        "creado por Alfredo Gongora para Hive Business Center. "
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

    # Add custom system prompt from context if provided (short instructions)
    custom = ""
    if context and context.get("custom_instructions"):
        custom = f"\n\nInstrucciones adicionales: {context['custom_instructions']}"

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
