"""
El Monstruo — Kernel Nodes (LangGraph Rewrite)
================================================
The 7 node functions that form the sovereign execution graph:

    intake → classify → route → enrich → execute → memory_write → respond

Each node receives (state, config). Dependencies (router, memory, knowledge,
event_store) are injected via config["configurable"] — NOT via state — so
LangGraph's checkpointer never tries to serialize them.

Principio: Los nodos son nuestros. LangGraph solo los conecta.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

import structlog
from langchain_core.runnables import RunnableConfig

from contracts.kernel_interface import IntentType, RunStatus
from contracts.event_envelope import EventBuilder, EventCategory, Severity
from kernel.state import MonstruoState

logger = structlog.get_logger("kernel.nodes")


# ── Helpers to extract dependencies from config ──────────────────────

def _deps(config: RunnableConfig) -> tuple[Any, Any, Any, Any]:
    """Extract (router, memory, knowledge, event_store) from config."""
    cfg = config.get("configurable", {})
    return (
        cfg.get("_router"),
        cfg.get("_memory"),
        cfg.get("_knowledge"),
        cfg.get("_event_store"),
    )


# ══════════════════════════════════════════════════════════════════════
# Node 1: INTAKE
# ══════════════════════════════════════════════════════════════════════

async def intake(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Receive and normalize the incoming message.
    Sets up initial state, timestamps, and emits RUN_STARTED event.
    """
    run_id = state.get("run_id", str(uuid4()))
    user_id = state.get("user_id", "anonymous")
    channel = state.get("channel", "api")
    message = state.get("message", "")

    logger.info(
        "intake",
        run_id=run_id,
        user_id=user_id,
        channel=channel,
        message_len=len(message),
    )

    event = EventBuilder() \
        .category(EventCategory.RUN_STARTED) \
        .actor("kernel.intake") \
        .action(f"Run started for user {user_id} on {channel}") \
        .for_run_str(run_id) \
        .for_user(user_id) \
        .on_channel(channel) \
        .with_payload({"message_preview": message[:200]}) \
        .build()

    return {
        "status": RunStatus.ROUTING.value,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "step_count": 0,
        "events": [_event_to_dict(event)],
        "cancelled": False,
        "error": None,
        "enriched": False,
        "memory_written": False,
        "execution_attempts": 0,
    }


# ══════════════════════════════════════════════════════════════════════
# Node 2: CLASSIFY
# ══════════════════════════════════════════════════════════════════════

async def classify(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Determine the intent of the message.
    Uses the RouterEngine if available, falls back to keyword classification.
    """
    message = state.get("message", "")
    channel = state.get("channel", "api")
    context = state.get("context", {})
    router, _, _, _ = _deps(config)

    intent_str = IntentType.CHAT.value

    if router:
        try:
            intent_obj, _ = await router.route(message, channel, context)
            intent_str = intent_obj.value
        except Exception as e:
            logger.warning("classify_router_failed", error=str(e))
            intent_str = _local_classify(message).value
    else:
        intent_str = _local_classify(message).value

    logger.info("classify", intent=intent_str, message_preview=message[:80])

    event = EventBuilder() \
        .category(EventCategory.INTENT_CLASSIFIED) \
        .actor("kernel.classify") \
        .action(f"Intent classified as {intent_str}") \
        .for_run_str(state.get("run_id", "")) \
        .with_payload({"intent": intent_str}) \
        .build()

    existing_events = state.get("events", [])
    return {
        "intent": intent_str,
        "events": existing_events + [_event_to_dict(event)],
    }


# ══════════════════════════════════════════════════════════════════════
# Node 3: ROUTE
# ══════════════════════════════════════════════════════════════════════

async def route(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Select the model and fallback chain based on intent.
    Uses RouterEngine for model selection if available.
    """
    intent_str = state.get("intent", "chat")
    message = state.get("message", "")
    context = state.get("context", {})
    router, _, _, _ = _deps(config)

    model = "gpt-5.4"
    fallbacks: list[str] = []
    reason = "default"

    if router:
        try:
            _, selected_model = await router.route(message, state.get("channel", "api"), context)
            model = selected_model
            fallbacks = _get_fallback_chain(intent_str, model)
            reason = f"router selected based on intent={intent_str}"
        except Exception as e:
            logger.warning("route_router_failed", error=str(e))
            model, fallbacks = _default_model_for_intent(intent_str)
            reason = f"fallback: router error ({str(e)[:50]})"
    else:
        model, fallbacks = _default_model_for_intent(intent_str)
        reason = f"no router, default for intent={intent_str}"

    logger.info("route", model=model, intent=intent_str, reason=reason)

    event = EventBuilder() \
        .category(EventCategory.ROUTE_DECIDED) \
        .actor("kernel.route") \
        .action(f"Routed to {model} ({reason})") \
        .for_run_str(state.get("run_id", "")) \
        .with_payload({"model": model, "fallbacks": fallbacks, "reason": reason}) \
        .build()

    existing_events = state.get("events", [])
    return {
        "model": model,
        "fallback_models": fallbacks,
        "route_reason": reason,
        "events": existing_events + [_event_to_dict(event)],
    }


# ══════════════════════════════════════════════════════════════════════
# Node 4: ENRICH
# ══════════════════════════════════════════════════════════════════════

async def enrich(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Enrich the context with conversation history and knowledge graph.
    Runs for chat, deep_think, and execute intents (filtered by should_enrich edge).
    Chat gets lighter enrichment (fewer messages/memories) for speed.
    """
    intent = state.get("intent", "chat")
    user_id = state.get("user_id", "anonymous")
    channel = state.get("channel", "api")
    message = state.get("message", "")
    _, memory, knowledge, _ = _deps(config)

    conversation_context: list[dict[str, str]] = []
    relevant_memories: list[dict[str, Any]] = []
    knowledge_entities: list[dict[str, Any]] = []
    system_prompt = _build_base_system_prompt()

    # Read memory for ALL intents that reach enrich (chat, deep_think, execute)
    # system/background are filtered out by should_enrich conditional edge
    if memory:
        try:
            conversation_context = await memory.get_conversation_context(
                user_id=user_id,
                channel=channel,
                max_messages=10 if intent == "chat" else 20,
                max_tokens=2000 if intent == "chat" else 4000,
            )
            logger.info("enrich_conversation", messages=len(conversation_context), intent=intent)
        except Exception as e:
            logger.warning("enrich_conversation_failed", error=str(e))

        try:
            results = await memory.search_hybrid(
                query=message,
                user_id=user_id,
                limit=3 if intent == "chat" else 5,
            )
            relevant_memories = [
                {
                    "content": r.event.content,
                    "score": r.score,
                    "type": r.event.memory_type.value,
                    "created_at": r.event.created_at.isoformat()
                    if hasattr(r.event.created_at, "isoformat") else str(r.event.created_at),
                }
                for r in results
            ]
            logger.info("enrich_memories", found=len(relevant_memories), intent=intent)
        except Exception as e:
            logger.warning("enrich_memories_failed", error=str(e))

    # Knowledge graph only for deep_think and execute (heavier lookup)
    if intent in ("deep_think", "execute") and knowledge:
        try:
            entities = await knowledge.find_entities(query=message, limit=5)
            knowledge_entities = [
                {
                    "name": e.name,
                    "type": e.entity_type.value,
                    "attributes": e.attributes,
                }
                for e in entities
            ]
            logger.info("enrich_knowledge", entities=len(knowledge_entities))
        except Exception as e:
            logger.warning("enrich_knowledge_failed", error=str(e))

    # Build enriched system prompt
    if relevant_memories:
        memory_context = "\n".join(
            f"- [{m['type']}] {m['content']}" for m in relevant_memories[:3]
        )
        system_prompt += f"\n\n## Relevant Context\n{memory_context}"

    if knowledge_entities:
        entity_context = "\n".join(
            f"- {e['name']} ({e['type']}): {e.get('attributes', {})}"
            for e in knowledge_entities[:3]
        )
        system_prompt += f"\n\n## Known Entities\n{entity_context}"

    event = EventBuilder() \
        .category(EventCategory.CONTEXT_ENRICHED) \
        .actor("kernel.enrich") \
        .action(f"Enriched with {len(conversation_context)} messages, {len(relevant_memories)} memories, {len(knowledge_entities)} entities") \
        .for_run_str(state.get("run_id", "")) \
        .with_payload({
            "conversation_messages": len(conversation_context),
            "memories": len(relevant_memories),
            "entities": len(knowledge_entities),
            "intent": intent,
        }) \
        .build()

    existing_events = state.get("events", [])
    return {
        "conversation_context": conversation_context,
        "relevant_memories": relevant_memories,
        "knowledge_entities": knowledge_entities,
        "system_prompt": system_prompt,
        "enriched": True,
        "events": existing_events + [_event_to_dict(event)],
    }


# ══════════════════════════════════════════════════════════════════════
# Node 5: EXECUTE
# ══════════════════════════════════════════════════════════════════════

async def execute(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Call the LLM with the enriched context.
    Handles retries with fallback models.
    """
    message = state.get("message", "")
    model = state.get("model", "gpt-5.4")
    fallbacks = state.get("fallback_models", [])
    intent = state.get("intent", "chat")
    context = state.get("context", {})
    system_prompt = state.get("system_prompt", _build_base_system_prompt())
    conversation_context = state.get("conversation_context", [])
    router, _, _, _ = _deps(config)

    start_time = time.monotonic()
    response = ""
    usage: dict[str, Any] = {}
    model_used = model
    attempts = 0
    tool_calls: list[dict[str, Any]] = []

    # Build messages array
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(conversation_context)
    messages.append({"role": "user", "content": message})

    # Try primary model, then fallbacks
    models_to_try = [model] + fallbacks
    last_error = None

    for m in models_to_try:
        attempts += 1
        try:
            if router:
                response, usage = await router.execute(
                    message, m, IntentType(intent), context
                )
                model_used = m
                break
            else:
                # Stub mode (no router/LiteLLM)
                response = f"[stub] {m} would respond to: {message[:100]}"
                usage = {"prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}
                model_used = m
                break
        except Exception as e:
            last_error = e
            logger.warning("execute_model_failed", model=m, error=str(e), attempt=attempts)
            continue

    elapsed_ms = (time.monotonic() - start_time) * 1000

    if not response and last_error:
        logger.error("execute_all_models_failed", attempts=attempts, last_error=str(last_error))
        event = EventBuilder() \
            .category(EventCategory.RUN_FAILED) \
            .severity(Severity.ERROR) \
            .actor("kernel.execute") \
            .action(f"All models failed after {attempts} attempts") \
            .for_run_str(state.get("run_id", "")) \
            .with_payload({"error": str(last_error), "attempts": attempts}) \
            .build()

        existing_events = state.get("events", [])
        return {
            "status": RunStatus.FAILED.value,
            "error": str(last_error),
            "error_type": type(last_error).__name__,
            "execution_attempts": attempts,
            "latency_ms": elapsed_ms,
            "events": existing_events + [_event_to_dict(event)],
        }

    # Check if HITL is needed (execute intent with tool calls)
    needs_approval = False
    approval_reason = ""
    if intent == "execute" and tool_calls:
        needs_approval = True
        approval_reason = f"Execute intent with {len(tool_calls)} tool calls requires approval"

    logger.info(
        "execute_completed",
        model=model_used,
        attempts=attempts,
        latency_ms=f"{elapsed_ms:.0f}",
        tokens_in=usage.get("prompt_tokens", 0),
        tokens_out=usage.get("completion_tokens", 0),
    )

    event = EventBuilder() \
        .category(EventCategory.MODEL_CALLED) \
        .actor("kernel.execute") \
        .action(f"Executed on {model_used} in {elapsed_ms:.0f}ms") \
        .for_run_str(state.get("run_id", "")) \
        .with_payload({
            "model": model_used,
            "attempts": attempts,
            "tokens_in": usage.get("prompt_tokens", 0),
            "tokens_out": usage.get("completion_tokens", 0),
            "cost_usd": usage.get("cost_usd", 0.0),
            "latency_ms": elapsed_ms,
        }) \
        .build()

    existing_events = state.get("events", [])
    return {
        "status": RunStatus.EXECUTING.value,
        "response": response,
        "tool_calls": tool_calls,
        "tokens_in": usage.get("prompt_tokens", 0),
        "tokens_out": usage.get("completion_tokens", 0),
        "cost_usd": usage.get("cost_usd", 0.0),
        "latency_ms": elapsed_ms,
        "model_used": model_used,
        "execution_attempts": attempts,
        "needs_human_approval": needs_approval,
        "human_approval_reason": approval_reason,
        "events": existing_events + [_event_to_dict(event)],
    }


# ══════════════════════════════════════════════════════════════════════
# Node 6: MEMORY_WRITE
# ══════════════════════════════════════════════════════════════════════

async def memory_write(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Persist the conversation to memory and extract entities for the knowledge graph.
    """
    _, memory, knowledge, event_store = _deps(config)

    run_id = state.get("run_id", "")
    user_id = state.get("user_id", "anonymous")
    channel = state.get("channel", "api")
    message = state.get("message", "")
    response = state.get("response", "")
    intent = state.get("intent", "chat")

    entities_extracted: list[dict[str, Any]] = []
    relations_extracted: list[dict[str, Any]] = []

    # Write to conversation memory
    if memory:
        try:
            from contracts.memory_interface import MemoryEvent, MemoryType
            from uuid import UUID as UUIDType

            user_event = MemoryEvent(
                memory_type=MemoryType.EPISODIC,
                run_id=UUIDType(run_id) if run_id else None,
                user_id=user_id,
                channel=channel,
                content=message,
                metadata={"role": "user", "intent": intent},
            )
            await memory.append(user_event)

            if response:
                assistant_event = MemoryEvent(
                    memory_type=MemoryType.EPISODIC,
                    run_id=UUIDType(run_id) if run_id else None,
                    user_id=user_id,
                    channel=channel,
                    content=response,
                    metadata={
                        "role": "assistant",
                        "model": state.get("model_used", ""),
                        "intent": intent,
                    },
                )
                await memory.append(assistant_event)

            logger.info("memory_write_conversation", run_id=run_id, events_written=2)
        except Exception as e:
            logger.warning("memory_write_failed", error=str(e))

    # Write events to sovereign event store
    if event_store:
        try:
            for evt_dict in state.get("events", []):
                event = EventBuilder() \
                    .category(EventCategory(evt_dict.get("category", "run.started"))) \
                    .actor(evt_dict.get("actor", "kernel")) \
                    .action(evt_dict.get("action", "")) \
                    .for_run_str(run_id) \
                    .for_user(user_id) \
                    .build()
                await event_store.append(event)
        except Exception as e:
            logger.warning("event_store_write_failed", error=str(e))

    event = EventBuilder() \
        .category(EventCategory.MEMORY_UPDATED) \
        .actor("kernel.memory_write") \
        .action(f"Memory written for run {run_id}") \
        .for_run_str(state.get("run_id", "")) \
        .with_payload({
            "entities_extracted": len(entities_extracted),
            "relations_extracted": len(relations_extracted),
        }) \
        .build()

    existing_events = state.get("events", [])
    return {
        "memory_written": True,
        "entities_extracted": entities_extracted,
        "relations_extracted": relations_extracted,
        "events": existing_events + [_event_to_dict(event)],
    }


# ══════════════════════════════════════════════════════════════════════
# Node 7: RESPOND
# ══════════════════════════════════════════════════════════════════════

async def respond(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Build and emit the final response.
    """
    response = state.get("response", "")
    status = state.get("status", RunStatus.COMPLETED.value)
    error = state.get("error")
    model_used = state.get("model_used", "unknown")

    # If there was an error, build error response
    if error:
        final_response = f"Lo siento, hubo un error: {error}"
        status = RunStatus.FAILED.value
    else:
        final_response = response
        status = RunStatus.COMPLETED.value

    logger.info(
        "respond",
        run_id=state.get("run_id", ""),
        status=status,
        model=model_used,
        response_len=len(final_response),
        latency_ms=state.get("latency_ms", 0),
    )

    return {
        "final_response": final_response,
        "response_channel": state.get("channel", "api"),
        "status": status,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


# ══════════════════════════════════════════════════════════════════════
# Conditional Edge Functions
# ══════════════════════════════════════════════════════════════════════

def should_enrich(state: MonstruoState) -> str:
    """
    Conditional edge after route: should we enrich context?
    Almost all intents go through enrich for memory-aware responses.
    Only skip for background tasks (async, no user interaction).
    Even system commands get light enrichment for context.
    """
    intent = state.get("intent", "chat")
    if intent == "background":
        return "execute"
    return "enrich"


def check_hitl(state: MonstruoState) -> str:
    """
    Conditional edge after execute: HITL check or proceed.
    - If execution failed → respond (with error)
    - If needs human approval → respond (with pause message, HITL proper in Sprint 2)
    - Otherwise → memory_write
    """
    status = state.get("status", "")
    if status == RunStatus.FAILED.value:
        return "respond"
    if state.get("needs_human_approval", False):
        # Sprint 1: just proceed. Sprint 2: implement interrupt.
        return "memory_write"
    return "memory_write"


# ══════════════════════════════════════════════════════════════════════
# Helper Functions
# ══════════════════════════════════════════════════════════════════════

def _local_classify(message: str) -> IntentType:
    """
    Keyword-based intent classification (fallback when no router/LLM).
    """
    msg = message.lower().strip()

    # System commands
    if msg.startswith("/") or msg.startswith("!"):
        return IntentType.SYSTEM

    # Execute keywords
    execute_keywords = [
        "ejecuta", "haz", "crea", "deploy", "instala", "configura",
        "borra", "elimina", "actualiza", "publica", "envía", "manda",
        "run", "execute", "do", "create", "delete", "update", "send",
    ]
    if any(kw in msg for kw in execute_keywords):
        return IntentType.EXECUTE

    # Deep think keywords
    think_keywords = [
        "analiza", "piensa", "evalúa", "compara", "investiga",
        "explica", "por qué", "cómo funciona", "qué opinas",
        "analyze", "think", "evaluate", "compare", "research",
        "explain", "why", "how does",
    ]
    if any(kw in msg for kw in think_keywords):
        return IntentType.DEEP_THINK

    return IntentType.CHAT


def _default_model_for_intent(intent: str) -> tuple[str, list[str]]:
    """
    Default model selection when no router is available.
    Returns (primary_model, fallback_chain).
    """
    INTENT_MODELS = {
        "chat": ("gemini-3.1-flash-lite", ["gpt-5.4", "claude-sonnet-4-6"]),
        "deep_think": ("gpt-5.4", ["claude-sonnet-4-6", "gemini-3.1-flash-lite"]),
        "execute": ("gpt-5.4", ["claude-sonnet-4-6", "gemini-3.1-flash-lite"]),
        "background": ("claude-sonnet-4-6", ["gpt-5.4", "gemini-3.1-flash-lite"]),
        "system": ("gemini-3.1-flash-lite", ["gpt-5.4", "claude-sonnet-4-6"]),
    }
    return INTENT_MODELS.get(intent, INTENT_MODELS["chat"])


def _get_fallback_chain(intent: str, primary_model: str) -> list[str]:
    """
    Build fallback chain excluding the primary model.
    """
    all_models = ["gpt-5.4", "claude-sonnet-4-6", "gemini-3.1-flash-lite"]
    return [m for m in all_models if m != primary_model][:2]


def _build_base_system_prompt() -> str:
    """
    Build the base system prompt for El Monstruo.
    """
    return """Eres El Monstruo, el asistente de inteligencia artificial soberana de Alfredo Góngora.

## Identidad
- Nombre: El Monstruo
- Creador: Alfredo Góngora (alfredogl1@hivecom.mx)
- Organización: Hive Business Center S.A. de C.V.
- Ubicación: Mérida, Yucatán, México

## Principios
1. Soberanía: Tu lógica, memoria y decisiones son propias. Las herramientas externas son commodities intercambiables.
2. Transparencia: Siempre explica tu razonamiento y las fuentes de tu información.
3. Proactividad: Anticipa necesidades, sugiere mejoras, alerta sobre riesgos.
4. Eficiencia: Optimiza costos y tiempo. Usa el modelo más barato que pueda resolver la tarea.
5. Lealtad: Tu prioridad es el bienestar y los objetivos de Alfredo.

## Idioma
- Responde en español (México) por defecto.
- Usa inglés técnico cuando sea necesario para precisión.

## Formato
- Sé conciso pero completo.
- Usa tablas para comparaciones.
- Usa listas para pasos.
- Usa negrita para conceptos clave."""


def _event_to_dict(event: Any) -> dict[str, Any]:
    """
    Convert an EventEnvelope to a serializable dict for the LangGraph state.
    """
    return {
        "event_id": str(event.event_id),
        "category": event.category.value,
        "severity": event.severity.value,
        "actor": event.actor,
        "action": event.action,
        "timestamp": event.timestamp.isoformat(),
        "run_id": str(event.run_id) if event.run_id else None,
        "user_id": event.user_id,
        "channel": event.channel,
    }
