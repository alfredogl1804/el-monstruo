"""
El Monstruo — Kernel Nodes (LangGraph Rewrite — Optimized)
============================================================
The 6 node functions that form the sovereign execution graph:

    intake → classify_and_route → [enrich] → execute → respond
                                                ↓ (async)
                                          memory_write (fire-and-forget)

Optimizations applied (v1.1):
  OPT-1: Fused classify+route into single node (eliminates duplicate LLM call)
  OPT-2: Parallelized memory lookups in enrich (asyncio.gather)
  OPT-3: Fast-path for simple queries (skip enrich when no personal context needed)
  OPT-4: Verified Flash-Lite for chat intent (fastest model)
  OPT-5: Memory write is fire-and-forget (doesn't block response)
  OPT-6: Intent classification cache (LRU with TTL)

Each node receives (state, config). Dependencies (router, memory, knowledge,
event_store) are injected via config["configurable"] — NOT via state — so
LangGraph's checkpointer never tries to serialize them.

Principio: Los nodos son nuestros. LangGraph solo los conecta.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

import structlog
from langchain_core.runnables import RunnableConfig

from contracts.event_envelope import EventBuilder, EventCategory, Severity
from contracts.kernel_interface import IntentType, RunStatus

# Action Envelope v2.0 — Governance
from core.action_envelope import (
    ActionType,
    ActorRef,
    ResourceKind,
    ResourceRef,
    RiskLevel,
    TrustRing,
    create_envelope,
    envelope_to_dict,
)
from core.action_validator import validate_and_classify
from kernel.state import MonstruoState

logger = structlog.get_logger("kernel.nodes")


# ── OPT-6: Intent Classification Cache ───────────────────────────────

_intent_cache: dict[str, tuple[str, float]] = {}
_INTENT_CACHE_TTL = 300  # 5 minutes
_INTENT_CACHE_MAX_SIZE = 500


def _cache_get_intent(message: str) -> Optional[str]:
    """Check cache for a previously classified intent."""
    normalized = message.strip().lower()[:200]
    cache_key = hashlib.md5(normalized.encode()).hexdigest()
    entry = _intent_cache.get(cache_key)
    if entry:
        intent_str, ts = entry
        if time.time() - ts < _INTENT_CACHE_TTL:
            logger.debug("intent_cache_hit", intent=intent_str)
            return intent_str
        else:
            del _intent_cache[cache_key]
    return None


def _cache_set_intent(message: str, intent_str: str) -> None:
    """Store a classified intent in cache."""
    # Evict oldest entries if cache is full
    if len(_intent_cache) >= _INTENT_CACHE_MAX_SIZE:
        oldest_key = min(_intent_cache, key=lambda k: _intent_cache[k][1])
        del _intent_cache[oldest_key]
    normalized = message.strip().lower()[:200]
    cache_key = hashlib.md5(normalized.encode()).hexdigest()
    _intent_cache[cache_key] = (intent_str, time.time())


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


def _obs(config: RunnableConfig) -> Any:
    """Extract observability manager from config. Returns None if not available."""
    return config.get("configurable", {}).get("_observability")


def _em(config: RunnableConfig) -> Any:
    """Extract ErrorMemory instance from config. Returns None if not available.
    Sprint 81 — Capa 0.1.
    """
    return config.get("configurable", {}).get("_error_memory") if config else None


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

    event = (
        EventBuilder()
        .category(EventCategory.RUN_STARTED)
        .actor("kernel.intake")
        .action(f"Run started for user {user_id} on {channel}")
        .for_run_str(run_id)
        .for_user(user_id)
        .on_channel(channel)
        .with_payload({"message_preview": message[:200]})
        .build()
    )

    # ── Observability: start trace for this run ──
    obs = _obs(config)
    trace_ctx = None
    if obs:
        trace_ctx = obs.start_trace(
            run_id=run_id,
            user_id=user_id,
            channel=channel,
            message=message,
        )
        obs.record_span(
            ctx=trace_ctx,
            name="intake",
            input={"message_len": len(message), "channel": channel},
            output={"status": "routing"},
        )

    result: dict[str, Any] = {
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
    # Store trace context in state for downstream nodes
    if trace_ctx:
        result["_trace_ctx"] = trace_ctx
    return result


# ══════════════════════════════════════════════════════════════════════
# Node 2: CLASSIFY_AND_ROUTE (OPT-1: Fused classify + route)
# ══════════════════════════════════════════════════════════════════════


async def classify_and_route(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    OPT-1: Single node that classifies intent AND selects model.

    Sprint 43 — Heuristic-First Routing:
    Run the supervisor heuristic (0ms) BEFORE the LLM classify call.
    For SIMPLE/MODERATE tiers, skip the LLM classify entirely and use
    the regex-based _local_classify() (0ms). Only pay the LLM classify
    cost (~1.8s) for COMPLEX/DEEP queries where intent accuracy matters.

    This reduces TTFT from ~3.3s to ~1.4s for 90%+ of queries.
    """
    message = state.get("message", "")
    channel = state.get("channel", "api")
    context = state.get("context", {})
    router, _, _, _ = _deps(config)

    start_time = time.monotonic()
    intent_str = IntentType.CHAT.value
    model = "gemini-3.1-flash-lite"
    fallbacks: list[str] = []
    reason = "default"
    cache_hit = False
    classify_source = "default"

    # ── Sprint 33D: Respect intent_override and model_hint from context ──
    intent_override = context.get("intent_override")
    model_hint = context.get("model_hint")

    if intent_override:
        try:
            intent_str = IntentType(intent_override).value
        except ValueError:
            intent_str = intent_override
        if model_hint:
            model = model_hint
        else:
            model, fallbacks = _default_model_for_intent(intent_str)
        fallbacks = _get_fallback_chain(intent_str, model)
        reason = f"context override: intent={intent_str}, model={model}"
        classify_source = "context_override"
        logger.info(
            "classify_override_from_context",
            intent=intent_str,
            model=model,
            source=context.get("source", "unknown"),
        )
        elapsed_ms = (time.monotonic() - start_time) * 1000
    elif model_hint and not intent_override:
        pass  # Will be applied after classification

    # ── Sprint 43: Heuristic-First Routing ──────────────────────────
    # Step 1: Run supervisor heuristic FIRST (0ms) to determine tier
    # This decides whether we need the expensive LLM classify call.
    skip_enrich = False
    supervisor_tier = "MODERATE"
    try:
        from kernel.supervisor import analyze_complexity
        conversation_context = state.get("conversation_context", [])
        supervisor_decision = analyze_complexity(
            message=state.get("message", ""),
            conversation_depth=len(conversation_context) if conversation_context else 0,
            has_tool_history=bool(state.get("tool_results", [])),
            intent=intent_str,
        )
        skip_enrich = supervisor_decision.skip_enrich
        supervisor_tier = supervisor_decision.tier.value if hasattr(supervisor_decision.tier, 'value') else str(supervisor_decision.tier)
        # Get the supervisor's model recommendation
        if supervisor_decision.model:
            model = supervisor_decision.model
            fallbacks = _get_fallback_chain(intent_str, model)
        logger.info(
            "supervisor_early_decision",
            tier=supervisor_tier,
            skip_enrich=skip_enrich,
            model=model,
        )
    except Exception as e:
        logger.warning("supervisor_early_failed", error=str(e))

    # Step 2: Route based on tier + cache
    if not intent_override:
        cached_intent = _cache_get_intent(message)

        if cached_intent:
            # Cache hit — skip LLM classify entirely (0ms)
            intent_str = cached_intent
            cache_hit = True
            if model_hint:
                model = model_hint
            # Model already set by supervisor above
            fallbacks = _get_fallback_chain(intent_str, model)
            reason = f"cache hit, intent={intent_str}"
            classify_source = "cache"

        elif supervisor_tier in ("SIMPLE", "MODERATE"):
            # FAST PATH: Use regex classify (0ms) — skip LLM entirely
            # The supervisor heuristic is 95%+ accurate for these tiers.
            # The LLM classify adds ~1.8s latency for negligible accuracy gain.
            intent_str = _local_classify(message).value
            # Model already set by supervisor above
            fallbacks = _get_fallback_chain(intent_str, model)
            reason = f"heuristic fast-path: tier={supervisor_tier}, intent={intent_str}"
            classify_source = "heuristic"
            _cache_set_intent(message, intent_str)
            logger.info(
                "classify_fast_path",
                tier=supervisor_tier,
                intent=intent_str,
                model=model,
            )

        elif router:
            # SLOW PATH: COMPLEX/DEEP — use LLM classify for accuracy.
            #
            # Sprint 84.5 — 8va semilla resuelta:
            # Antes del router LLM, ejecutar preflight con _local_classify().
            # Si detecta intent EXECUTE/BACKGROUND con keywords obvios,
            # bypassamos el LLM (~1.8s + costo) y usamos heurística.
            # Para prompts ambiguos sin match, sigue al router LLM original.
            preflight_intent = _local_classify(message)
            if preflight_intent in (IntentType.EXECUTE, IntentType.BACKGROUND):
                intent_str = preflight_intent.value
                if model_hint:
                    model = model_hint
                fallbacks = _get_fallback_chain(intent_str, model)
                reason = (
                    f"slow_path_preflight: tier={supervisor_tier}, "
                    f"intent={intent_str} (local_classify hit)"
                )
                classify_source = "heuristic_preflight"
                _cache_set_intent(message, intent_str)
                logger.info(
                    "classify_slow_path_preflight_hit",
                    tier=supervisor_tier,
                    intent=intent_str,
                    model=model,
                )
            else:
                # No match obvio → router LLM decide.
                try:
                    intent_obj, selected_model = await router.route(message, channel, context)
                    intent_str = intent_obj.value
                    # For COMPLEX/DEEP, supervisor already set the model;
                    # only use router's model if no supervisor model
                    if model_hint:
                        model = model_hint
                    # Keep supervisor model — it's tier-appropriate
                    fallbacks = _get_fallback_chain(intent_str, model)
                    reason = f"router (slow path): tier={supervisor_tier}, intent={intent_str}"
                    classify_source = "llm"
                    _cache_set_intent(message, intent_str)
                except Exception as e:
                    logger.warning("classify_and_route_failed", error=str(e))
                    intent_str = _local_classify(message).value
                    fallbacks = _get_fallback_chain(intent_str, model)
                    reason = f"fallback: router error ({str(e)[:50]})"
                    classify_source = "fallback"
        else:
            intent_str = _local_classify(message).value
            model, fallbacks = _default_model_for_intent(intent_str)
            reason = f"no router, default for intent={intent_str}"
            classify_source = "local_no_router"

    # ── Sprint 21: Multi-Agent Dispatcher Integration ──────────────
    # After intent classification, run the multi-agent dispatcher to
    # determine which specialized agent should handle the task.
    # The dispatcher enriches the execute node with agent-specific
    # system prompt, tools, and model preference.
    agent_type = None
    agent_name = None
    agent_system_prompt = None
    agent_tools: list[str] = []
    agent_model_preference = None

    try:
        from kernel.multi_agent import dispatch as multi_agent_dispatch

        dispatch_result = multi_agent_dispatch(message)
        agent_type = dispatch_result.agent_type.value
        agent_name = dispatch_result.agent_name
        agent_system_prompt = dispatch_result.system_prompt
        agent_tools = dispatch_result.tools
        agent_model_preference = dispatch_result.model_preference

        # If dispatcher has a model preference, use it (unless router already chose)
        if agent_model_preference and not cache_hit:
            model = agent_model_preference
            fallbacks = _get_fallback_chain(intent_str, model)
            reason += f", agent={agent_name} overrode model"

        logger.info(
            "multi_agent_dispatched",
            agent_type=agent_type,
            agent_name=agent_name,
            agent_model=agent_model_preference,
            agent_tools=len(agent_tools),
        )
    except Exception as e:
        logger.warning("multi_agent_dispatch_failed", error=str(e))

    elapsed_ms = (time.monotonic() - start_time) * 1000

    logger.info(
        "classify_and_route",
        intent=intent_str,
        model=model,
        cache_hit=cache_hit,
        latency_ms=f"{elapsed_ms:.0f}",
        message_preview=message[:80],
        agent=agent_name or "none",
    )

    # Emit combined event
    event = (
        EventBuilder()
        .category(EventCategory.INTENT_CLASSIFIED)
        .actor("kernel.classify_and_route")
        .action(f"Intent={intent_str}, Model={model}, Agent={agent_name or 'none'} ({reason})")
        .for_run_str(state.get("run_id", ""))
        .with_payload(
            {
                "intent": intent_str,
                "model": model,
                "fallbacks": fallbacks,
                "reason": reason,
                "cache_hit": cache_hit,
                "classify_route_ms": elapsed_ms,
                "classify_source": classify_source,
                "supervisor_tier": supervisor_tier,
                "agent_type": agent_type,
                "agent_name": agent_name,
                "agent_tools": agent_tools,
            }
        )
        .build()
    )

    # Sprint 43: Supervisor already ran at the top (heuristic-first routing)
    # No duplicate call needed here.

    existing_events = state.get("events", [])
    result: dict[str, Any] = {
        "intent": intent_str,
        "model": model,
        "fallback_models": fallbacks,
        "route_reason": reason,
        "skip_enrich": skip_enrich,
        "supervisor_tier": supervisor_tier,
        "events": existing_events + [_event_to_dict(event)],
    }

    # Sprint 21: Inject agent context into state for execute node
    if agent_system_prompt:
        result["agent_system_prompt"] = agent_system_prompt
    if agent_type:
        result["agent_type"] = agent_type
    if agent_tools:
        result["agent_tools"] = agent_tools

    return result


# ══════════════════════════════════════════════════════════════════════
# Node 3: ENRICH (OPT-2: Parallelized lookups)
# ══════════════════════════════════════════════════════════════════════


async def enrich(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Enrich the context with conversation history and knowledge graph.

    OPT-2: All memory/knowledge lookups run in parallel via asyncio.gather().
    Saves ~200ms by overlapping I/O operations.

    Runs for chat, deep_think, execute, and system intents.
    Chat gets lighter enrichment (fewer messages/memories) for speed.
    """
    intent = state.get("intent", "chat")
    user_id = state.get("user_id", "anonymous")
    channel = state.get("channel", "api")
    message = state.get("message", "")
    _, memory, knowledge, _ = _deps(config)

    start_time = time.monotonic()
    conversation_context: list[dict[str, str]] = []
    relevant_memories: list[dict[str, Any]] = []
    knowledge_entities: list[dict[str, Any]] = []
    lightrag_result: dict[str, Any] = {}  # Sprint 24: LightRAG KG context
    system_prompt = _build_base_system_prompt()

    # Sprint 9: Inject dynamic user dossier from Supabase
    # Sprint 39 Opt-3: Dossier cache con TTL 5min — evita fetch de Supabase en cada request
    from kernel import dossier_cache
    db = config.get("configurable", {}).get("_db")
    cached_dossier = dossier_cache.get(user_id)
    if cached_dossier:
        system_prompt += f"\n\n{cached_dossier}"
        logger.debug("enrich_dossier_from_cache", user_id=user_id, chars=len(cached_dossier))
    elif db:
        try:
            from tools.user_dossier import get_prompt_dossier

            dynamic_dossier = await get_prompt_dossier(db, user_id="anonymous")
            system_prompt += f"\n\n{dynamic_dossier}"
            dossier_cache.store(user_id, dynamic_dossier)  # Cache para próximas requests
            logger.info("enrich_dossier_injected", source="supabase", chars=len(dynamic_dossier))
        except Exception as e:
            # Fallback to hardcoded dossier
            from prompts.system_prompts import USER_DOSSIER

            system_prompt += f"\n\n{USER_DOSSIER}"
            logger.warning("enrich_dossier_fallback", error=str(e))
    else:
        # No DB — use hardcoded dossier
        from prompts.system_prompts import USER_DOSSIER

        system_prompt += f"\n\n{USER_DOSSIER}"

    # P0.2: Inject external system prompts (from Open WebUI or other clients)
    # These come via RunInput.context["system_prompts"] from the OpenAI adapter
    external_system_prompts = state.get("context", {}).get("system_prompts", [])
    if external_system_prompts:
        combined_external = "\n".join(external_system_prompts)
        system_prompt += f"\n\n## Client Instructions\n{combined_external}"
        logger.info(
            "enrich_external_system_prompts_injected",
            count=len(external_system_prompts),
            total_chars=len(combined_external),
        )

    # Sprint 27: Mem0 episodic memory retrieval (replaces Honcho)
    mem0_context = {}

    async def _get_mem0_context():
        try:
            from memory.mem0_bridge import search_memory

            results = await search_memory(query=message, user_id=user_id, limit=3)
            if results:
                return {"mem0_active": True, "memories": results}
            return {"mem0_active": False}
        except Exception as e:
            logger.warning("enrich_mem0_failed", error=str(e))
            return {"mem0_active": False}

    # ══ Sprint 42: Tiered Enrichment + SLA Timeouts ══════════════════════
    # Consensus from Los 3 Sabios (Gemini 3 Pro + Perplexity Sonar Pro, 2026-04-30):
    #   - MODERATE: Only fast retrievers (conversation + semantic search) with 1.5s SLA
    #   - COMPLEX/DEEP: All 6 retrievers with 4.0s/8.0s SLA
    #   - Cancel any task exceeding SLA → use whatever completed in time
    # This reduces TTFT from ~16s to ~3s for MODERATE queries.

    # Determine complexity tier from supervisor decision
    supervisor_tier = state.get("supervisor_tier", "MODERATE").upper()

    if memory:
        # ── Define all retriever coroutines ──────────────────────────

        async def _get_conversation():
            try:
                return await memory.get_conversation_context(
                    user_id=user_id,
                    channel=channel,
                    max_messages=10 if intent == "chat" else 20,
                    max_tokens=2000 if intent == "chat" else 4000,
                )
            except Exception as e:
                logger.warning("enrich_conversation_failed", error=str(e))
                return []

        async def _search_memories():
            try:
                results = await memory.search_hybrid(
                    query=message,
                    user_id=user_id,
                    limit=3 if intent == "chat" else 5,
                )
                return [
                    {
                        "content": r.event.content,
                        "score": r.score,
                        "type": r.event.memory_type.value,
                        "created_at": r.event.created_at.isoformat()
                        if hasattr(r.event.created_at, "isoformat")
                        else str(r.event.created_at),
                    }
                    for r in results
                ]
            except Exception as e:
                logger.warning("enrich_memories_failed", error=str(e))
                return []

        async def _get_knowledge():
            if intent in ("deep_think", "execute") and knowledge:
                try:
                    entities = await knowledge.find_entities(query=message, limit=5)
                    return [
                        {
                            "name": e.name,
                            "type": e.entity_type.value,
                            "attributes": e.attributes,
                        }
                        for e in entities
                    ]
                except Exception as e:
                    logger.warning("enrich_knowledge_failed", error=str(e))
            return []

        async def _recall_mempalace():
            try:
                from memory.mempalace_bridge import recall

                results = await recall(
                    query=message,
                    user_id=user_id,
                    n_results=3 if intent == "chat" else 5,
                )
                return results
            except Exception as e:
                logger.warning("enrich_mempalace_failed", error=str(e))
                return []

        async def _query_lightrag():
            try:
                from memory.lightrag_bridge import query_knowledge

                mode = "hybrid" if intent in ("deep_think", "execute") else "local"
                result = await query_knowledge(
                    query=message,
                    mode=mode,
                    top_k=3 if intent == "chat" else 5,
                )
                if result.get("results") and not result.get("error"):
                    return result
                return {}
            except Exception as e:
                logger.warning("enrich_lightrag_failed", error=str(e))
                return {}

        # ── Sprint 42: Tiered task selection ─────────────────────────
        # SIMPLE tier should never reach enrich (skip_enrich=True),
        # but handle it defensively.
        tasks_by_name: dict[str, Any] = {}

        if supervisor_tier in ("SIMPLE", "MODERATE"):
            # FAST PATH: Only conversation context + semantic memory search
            # These are pure pgvector/Supabase queries — typically <500ms
            tasks_by_name["conversation"] = asyncio.create_task(_get_conversation(), name="conversation")
            tasks_by_name["memories"] = asyncio.create_task(_search_memories(), name="memories")
            sla_timeout = 1.5  # 1.5s hard SLA for MODERATE
            logger.info("enrich_tiered_moderate", retrievers=2, sla_timeout=sla_timeout)
        elif supervisor_tier == "COMPLEX":
            # MEDIUM PATH: Add MemPalace + Mem0 (skip LightRAG which is slowest)
            tasks_by_name["conversation"] = asyncio.create_task(_get_conversation(), name="conversation")
            tasks_by_name["memories"] = asyncio.create_task(_search_memories(), name="memories")
            tasks_by_name["mempalace"] = asyncio.create_task(_recall_mempalace(), name="mempalace")
            tasks_by_name["mem0"] = asyncio.create_task(_get_mem0_context(), name="mem0")
            sla_timeout = 4.0  # 4s SLA for COMPLEX
            logger.info("enrich_tiered_complex", retrievers=4, sla_timeout=sla_timeout)
        else:
            # DEEP PATH: All 6 retrievers — full pipeline
            tasks_by_name["conversation"] = asyncio.create_task(_get_conversation(), name="conversation")
            tasks_by_name["memories"] = asyncio.create_task(_search_memories(), name="memories")
            tasks_by_name["knowledge"] = asyncio.create_task(_get_knowledge(), name="knowledge")
            tasks_by_name["mempalace"] = asyncio.create_task(_recall_mempalace(), name="mempalace")
            tasks_by_name["mem0"] = asyncio.create_task(_get_mem0_context(), name="mem0")
            tasks_by_name["lightrag"] = asyncio.create_task(_query_lightrag(), name="lightrag")
            sla_timeout = 8.0  # 8s SLA for DEEP
            logger.info("enrich_tiered_deep", retrievers=6, sla_timeout=sla_timeout)

        # ── Sprint 42: SLA Enforcement via asyncio.wait() ────────────
        done, pending = await asyncio.wait(
            tasks_by_name.values(),
            timeout=sla_timeout,
            return_when=asyncio.ALL_COMPLETED,
        )

        # Cancel tasks that exceeded SLA
        cancelled_names = []
        for task in pending:
            task_name = task.get_name()
            cancelled_names.append(task_name)
            task.cancel()
        if cancelled_names:
            logger.warning(
                "enrich_sla_timeout",
                cancelled=cancelled_names,
                sla_timeout=sla_timeout,
                tier=supervisor_tier,
            )

        # ── Collect results from completed tasks ─────────────────────
        def _safe_result(task_name: str, default=None):
            """Get result from a named task, or default if it didn't complete."""
            task = tasks_by_name.get(task_name)
            if task and task in done:
                try:
                    return task.result()
                except Exception as e:
                    logger.warning(f"enrich_{task_name}_exception", error=str(e))
            return default if default is not None else ([] if task_name != "lightrag" else {})

        conversation_context = _safe_result("conversation", [])
        relevant_memories = _safe_result("memories", [])
        knowledge_entities = _safe_result("knowledge", [])
        mempalace_memories = _safe_result("mempalace", [])
        mem0_context = _safe_result("mem0", {})
        lightrag_result = _safe_result("lightrag", {})

        # Sprint 21: Merge MemPalace results into relevant_memories
        if mempalace_memories:
            for mem in mempalace_memories:
                relevant_memories.append(
                    {
                        "content": mem.get("content", ""),
                        "score": 1.0 - (mem.get("distance", 0.5)),
                        "type": mem.get("metadata", {}).get("type", "mempalace"),
                        "source": "mempalace",
                    }
                )

        logger.info(
            "enrich_tiered_complete",
            tier=supervisor_tier,
            sla_timeout=sla_timeout,
            completed=len(done),
            cancelled=len(pending),
            conversation=len(conversation_context),
            memories=len(relevant_memories),
            entities=len(knowledge_entities),
            lightrag=bool(lightrag_result),
            intent=intent,
        )

    # ══ Sprint 45: Context Distillation via ZeroEntropy Zerank-2 ════════════
    # Rerank ALL candidate chunks against the user's query before injecting
    # into the system prompt. This reduces context from ~80K to ~8-10K tokens,
    # cutting LLM prefill from 30-45s to 2-4s.
    #
    # Architecture: retrievers → reranker.distill_context() → system_prompt
    # Fallback: If reranker unavailable, uses original score-based sorting.
    from kernel.reranker import distill_context

    # Collect all text candidates into a unified pool for reranking
    _all_candidates: list[dict[str, Any]] = []

    # Add semantic memories (from pgvector hybrid search + MemPalace)
    for m in relevant_memories:
        _all_candidates.append({
            "content": m.get("content", ""),
            "score": m.get("score", 0),
            "type": m.get("type", "memory"),
            "source": m.get("source", "semantic"),
        })

    # Add Mem0 episodic memories
    if mem0_context and mem0_context.get("mem0_active"):
        for mem in mem0_context.get("memories", []):
            mem_text = mem.get("memory", "")
            if mem_text:
                _all_candidates.append({
                    "content": mem_text,
                    "score": mem.get("score", 0.5),
                    "type": "episodic",
                    "source": "mem0",
                })

    # Add LightRAG knowledge graph text (as a single document)
    if lightrag_result and lightrag_result.get("results"):
        rag_text = lightrag_result["results"]
        if isinstance(rag_text, str) and rag_text.strip():
            _all_candidates.append({
                "content": rag_text[:3000],  # Cap individual chunk
                "score": 0.7,
                "type": "knowledge_graph",
                "source": "lightrag",
            })

    # Add knowledge entities as text
    if knowledge_entities:
        for e in knowledge_entities:
            entity_text = f"{e['name']} ({e['type']}): {e.get('attributes', {})}"
            _all_candidates.append({
                "content": entity_text,
                "score": 0.6,
                "type": "entity",
                "source": "knowledge_graph",
            })

    # Determine top_n based on tier
    _rerank_top_n = 3 if supervisor_tier in ("SIMPLE", "MODERATE") else 5

    # Rerank if we have candidates worth filtering
    if len(_all_candidates) > _rerank_top_n:
        _reranked = await distill_context(
            query=message,
            candidates=_all_candidates,
            top_n=_rerank_top_n,
            instruction="Prioritize personal memories and facts about the user over general knowledge. Rank by direct relevance to the query.",
        )
        logger.info(
            "enrich_reranked",
            candidates_in=len(_all_candidates),
            candidates_out=len(_reranked),
            tier=supervisor_tier,
        )
    else:
        _reranked = _all_candidates

    # ── Build enriched system prompt from reranked results ──────────
    if _reranked:
        context_parts = []
        for chunk in _reranked:
            source_tag = chunk.get("source", "memory")
            type_tag = chunk.get("type", "")
            content = chunk.get("content", "")
            score_info = f" (relevance: {chunk.get('rerank_score', chunk.get('score', 0)):.2f})"
            context_parts.append(f"- [{source_tag}/{type_tag}]{score_info}: {content}")
        system_prompt += "\n\n## Relevant Context (Reranked)\n" + "\n".join(context_parts)
    elif relevant_memories:
        # Fallback: no candidates to rerank, use raw memories
        memory_context = "\n".join(f"- [{m['type']}] {m['content']}" for m in relevant_memories[:3])
        system_prompt += f"\n\n## Relevant Context\n{memory_context}"

    # Sprint 36: Inject deep_think specialized prompt section
    if intent == IntentType.DEEP_THINK.value:
        system_prompt += (
            "\n\n## Modo Deep Think — Protocolo de Razonamiento\n"
            "Estás en modo de análisis profundo multi-paso. El pipeline ejecutará:\n"
            "1. **Planificación**: Genera un marco de análisis antes de responder.\n"
            "2. **Consulta a Sabios**: Claude (Arquitecto/Crítico) y Gemini (Investigador/Creativo) aportarán perspectivas.\n"
            "3. **Síntesis**: Integra todas las perspectivas en una respuesta final estructurada.\n\n"
            "Usa la memoria y el contexto proporcionado arriba. "
            "Cita fuentes cuando las tengas. Señala incertidumbre explícitamente. "
            "Termina con nivel de confianza: alto/medio/bajo."
        )
        logger.info("enrich_deep_think_prompt_injected")

    elapsed_ms = (time.monotonic() - start_time) * 1000

    event = (
        EventBuilder()
        .category(EventCategory.CONTEXT_ENRICHED)
        .actor("kernel.enrich")
        .action(
            f"Enriched with {len(conversation_context)} msgs, {len(relevant_memories)} memories, {len(knowledge_entities)} entities in {elapsed_ms:.0f}ms"  # noqa: E501
        )
        .for_run_str(state.get("run_id", ""))
        .with_payload(
            {
                "conversation_messages": len(conversation_context),
                "memories": len(relevant_memories),
                "entities": len(knowledge_entities),
                "intent": intent,
                "enrich_ms": elapsed_ms,
            }
        )
        .build()
    )

    # ── Action Envelope v2.0: Governance ──────────────────────────
    # Create and validate an ActionEnvelope for this request
    envelope_dict = None
    policy_decision_str = "ALLOW"
    risk_level_str = "L1_SAFE"
    trust_ring_str = "R2_USER_DELEGATED"
    needs_hitl = False
    hitl_reason = ""

    try:
        # Map intent to ActionType
        intent_to_action_type = {
            "chat": ActionType.READ,
            "deep_think": ActionType.READ,
            "execute": ActionType.EXECUTE,
            "system": ActionType.READ,
            "background": ActionType.READ,
        }
        action_type = intent_to_action_type.get(intent, ActionType.READ)

        # Map intent to ResourceKind
        intent_to_resource = {
            "chat": ResourceKind.MEMORY,
            "deep_think": ResourceKind.MEMORY,
            "execute": ResourceKind.TOOL,
            "system": ResourceKind.MEMORY,
            "background": ResourceKind.MEMORY,
        }
        resource_kind = intent_to_resource.get(intent, ResourceKind.MEMORY)

        # Determine actor type from channel
        actor_type = "user" if channel in ("telegram", "console", "api") else "agent"

        envelope = create_envelope(
            session_id=state.get("run_id", str(uuid4())),
            trace_id=state.get("run_id", str(uuid4())),
            actor=ActorRef(actor_id=user_id, actor_type=actor_type),
            action_type=action_type,
            target=ResourceRef(
                resource_kind=resource_kind,
                resource_id=f"{intent}_{state.get('run_id', 'unknown')[:8]}",
                locator=f"kernel://{intent}/execute",
            ),
            operation=f"{intent}_response",
            payload={
                "message_preview": message[:100],
                "model": state.get("model", "unknown"),
            },
            intent_summary=f"{intent}: {message[:200]}",
        )

        # Step 1: Validate and classify through action_validator
        envelope, validation_result = validate_and_classify(envelope)

        # Step 2: Run through PolicyEngine v1.0 (composite risk + Cedar rules)
        from core.policy_engine import get_policy_engine

        policy_engine = get_policy_engine()
        policy_eval = policy_engine.evaluate(envelope)

        # Step 3: Bridge PolicyEngine result to ActionEnvelope PolicyDecision
        risk = envelope.policy_decision.risk_level if envelope.policy_decision else RiskLevel.L1_SAFE
        trust = (
            envelope.policy_decision.enforced_trust_ring if envelope.policy_decision else TrustRing.R2_USER_DELEGATED
        )
        final_policy = policy_engine.to_envelope_policy_decision(policy_eval, trust, risk)

        # Use PolicyEngine decision (it includes composite risk)
        from dataclasses import replace as dc_replace

        # Re-seal envelope with PolicyEngine decision
        envelope = dc_replace(envelope, policy_decision=final_policy)

        # Extract governance decisions
        envelope_dict = envelope_to_dict(envelope)
        policy_decision_str = policy_eval.decision
        risk_level_str = risk.value if hasattr(risk, "value") else str(risk)
        trust_ring_str = trust.value if hasattr(trust, "value") else str(trust)
        needs_hitl = policy_eval.requires_hitl
        hitl_reason = policy_eval.decision_reason

        logger.info(
            "action_envelope_created",
            action_id=envelope.action_id,
            action_type=envelope.action_type.value,
            risk=risk_level_str,
            trust=trust_ring_str,
            decision=policy_decision_str,
            requires_hitl=needs_hitl,
            reclassified=validation_result.reclassified,
            composite_risk=policy_eval.composite_risk,
            composite_value=policy_eval.composite_value,
            density_count=policy_eval.density_count,
        )

    except Exception as e:
        logger.warning("action_envelope_failed", error=str(e))
        # Non-fatal: governance is advisory in Sprint 1, not blocking

    # ── Sprint 81: Error Memory — consult before action ────────────────
    try:
        _em_inst = _em(config)
        _recording = os.environ.get("ERROR_MEMORY_RECORDING", "true").lower() == "true"
        if _em_inst and getattr(_em_inst, "initialized", False) and _recording and message:
            rules = await _em_inst.consult(
                intent=message,
                context={
                    "module": "kernel.nodes.enrich",
                    "action": "execute",  # downstream node
                },
                top_k=3,
            )
            if rules:
                hints = [r.to_prompt_hint() for r in rules]
                system_prompt += (
                    "\n\n## Lecciones de errores anteriores\n"
                    + "\n".join(hints)
                    + "\nToma estas lecciones en cuenta para no repetir fallos conocidos."
                )
                logger.info(
                    "enrich_error_memory_advisory_injected",
                    rules_count=len(rules),
                    avg_confidence=round(
                        sum(r.confidence for r in rules) / len(rules), 2
                    ),
                )
    except Exception as _em_err:
        logger.debug("enrich_error_memory_skip", error=str(_em_err))
    # ── /Sprint 81 ───────────────────────────────────────────────────────

    existing_events = state.get("events", [])
    return {
        "conversation_context": conversation_context,
        "relevant_memories": relevant_memories,
        "knowledge_entities": knowledge_entities,
        "system_prompt": system_prompt,
        "enriched": True,
        "events": existing_events + [_event_to_dict(event)],
        # Governance fields
        "action_envelope": envelope_dict,
        "policy_decision": policy_decision_str,
        "risk_level": risk_level_str,
        "trust_ring": trust_ring_str,
        "needs_human_approval": needs_hitl,
        "human_approval_reason": hitl_reason,
    }


# ══════════════════════════════════════════════════════════════════
# Node 4: EXECUTE
# ══════════════════════════════════════════════════════════════════════


async def execute(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Call the LLM with the enriched context and tool definitions.
    Sprint 2: Uses native function calling via execute_with_tools().

    If tool_results exist in state (from a previous tool_dispatch cycle),
    this is a follow-up call where the LLM receives tool results.

    CRITICAL: Passes enriched system_prompt and conversation_context
    to the router so the LLM sees memory and context from enrich().
    """
    message = state.get("message", "")
    model = state.get("model", "gpt-5.5")
    intent = state.get("intent", "chat")
    system_prompt = state.get("system_prompt", _build_base_system_prompt())
    conversation_context = state.get("conversation_context", [])
    tool_results = state.get("tool_results", [])  # From previous tool_dispatch
    tool_loop_count = state.get("tool_loop_count", 0)
    router, _, _, _ = _deps(config)

    # ── External Agent Dispatch ──────────────────────────────────────
    # If dispatch_agent is set in context, route to external agent instead
    dispatch_agent = state.get("context", {}).get("dispatch_agent")
    if dispatch_agent and not tool_results:
        try:
            from kernel.external_agents import ExternalAgentDispatcher
            dispatcher = ExternalAgentDispatcher()
            # Build context from conversation history
            history_context = "\n".join(
                f"{m.get('role', 'user')}: {m.get('content', '')}"
                for m in conversation_context[-10:]
            ) if conversation_context else ""
            result = await dispatcher.dispatch(
                agent_id=dispatch_agent,
                message=message,
                context=history_context,
                thread_id=state.get("context", {}).get("thread_id", ""),
            )
            if result.get("success"):
                return {
                    "response": result["content"],
                    "model_used": f"{dispatch_agent}:{result.get('model_used', 'unknown')}",
                    "usage": {"total_tokens": result.get("tokens_used", 0)},
                    "latency_ms": result.get("latency_ms", 0),
                }
            else:
                logger.warning("external_agent_dispatch_failed", agent=dispatch_agent, error=result.get("error"))
                # Fall through to normal execution
        except Exception as e:
            logger.error("external_agent_dispatch_error", agent=dispatch_agent, error=str(e))
            # Fall through to normal execution

    # Sprint 21: Multi-Agent — inject agent-specific system prompt
    agent_system_prompt = state.get("agent_system_prompt")
    agent_type = state.get("agent_type")
    if agent_system_prompt:
        # Prepend agent specialization to the enriched system prompt
        system_prompt = f"## Agent Role: {agent_type or 'general'}\n{agent_system_prompt}\n\n{system_prompt}"
        logger.info(
            "execute_agent_prompt_injected",
            agent_type=agent_type,
            prompt_len=len(agent_system_prompt),
        )

    start_time = time.monotonic()
    response = ""
    usage: dict[str, Any] = {}
    model_used = model
    pending_tool_calls: list[dict[str, Any]] = []

    # Inject enriched context into router context dict
    enriched_context = dict(state.get("context", {}))
    if conversation_context:
        enriched_context["history"] = conversation_context
    if system_prompt:
        enriched_context["system_prompt"] = system_prompt

    is_followup = bool(tool_results)
    logger.info(
        "execute_start",
        history_messages=len(conversation_context),
        has_enriched_prompt=bool(system_prompt),
        intent=intent,
        model=model,
        is_tool_followup=is_followup,
        tool_loop_count=tool_loop_count,
    )

    # Sprint 39 Opt-2: Response cache check — skip LLM call on hit
    if not is_followup:
        from kernel import response_cache
        cached_response = response_cache.get(message, intent)
        if cached_response:
            logger.info("execute_cache_hit", intent=intent, preview=message[:50])
            existing_events = state.get("events", [])
            return {
                "status": RunStatus.EXECUTING.value,
                "response": cached_response,
                "pending_tool_calls": [],
                "tool_results": [],
                "tokens_in": state.get("tokens_in", 0),
                "tokens_out": state.get("tokens_out", 0),
                "cost_usd": state.get("cost_usd", 0.0),
                "latency_ms": 1,
                "model_used": "cache",
                "execution_attempts": state.get("execution_attempts", 0) + 1,
                "needs_human_approval": False,
                "human_approval_reason": None,
                "events": existing_events,
            }

    # Get tool specs for native function calling
    from kernel.tool_dispatch import get_tool_specs

    tool_specs = get_tool_specs()

    try:
        # Sprint 36: deep_think usa pipeline multi-paso con consulta a Sabios
        if intent == IntentType.DEEP_THINK.value and router and not is_followup:
            from kernel.deep_think_pipeline import run_deep_think_pipeline

            logger.info("execute_deep_think_pipeline", model=model)
            response, usage = await run_deep_think_pipeline(
                message=message,
                context=enriched_context,
                router=router,
                model=model,
            )
            model_used = usage.get("model_used", model)

        elif router and hasattr(router, "execute_with_tools"):
            llm_response = await router.execute_with_tools(
                message=message,
                model=model,
                intent=IntentType(intent),
                context=enriched_context,
                tools=tool_specs,
                tool_results=tool_results if is_followup else None,
            )

            response = llm_response.content
            usage = llm_response.usage
            model_used = llm_response.usage.get("model_used", model)

            # If LLM wants to use tools, store them as pending
            if llm_response.has_tool_calls:
                pending_tool_calls = [tc.to_dict() for tc in llm_response.tool_calls]
                logger.info(
                    "execute_tool_calls_requested",
                    tool_count=len(pending_tool_calls),
                    tools=[tc.name for tc in llm_response.tool_calls],
                    loop_count=tool_loop_count,
                )

        elif router:
            # Fallback to old execute() without tools
            response, usage = await router.execute(message, model, IntentType(intent), enriched_context)
            model_used = model
        else:
            # Sprint 38: router no disponible — error real en lugar de stub silencioso
            logger.error("execute_no_router", model=model, run_id=state.get("run_id", ""))
            raise RuntimeError(
                f"Router no disponible. No se puede ejecutar el modelo '{model}'. "
                "Verifica que el sistema esté correctamente inicializado."
            )

    except Exception as e:
        logger.error("execute_failed", model=model, error=str(e))

        # ── Sprint 81: Error Memory — record execution failures ──────
        try:
            _em_inst = _em(config)
            _recording = os.environ.get("ERROR_MEMORY_RECORDING", "true").lower() == "true"
            if _em_inst and getattr(_em_inst, "initialized", False) and _recording:
                import asyncio
                asyncio.create_task(_em_inst.record(
                    error=e,
                    context={
                        "module": "kernel.nodes.execute",
                        "action": "llm_call",
                        "model": model,
                        "intent": intent,
                        "run_id": state.get("run_id", ""),
                        "message_preview": (message[:100] if message else ""),
                        "tool_loop_count": tool_loop_count,
                    },
                ))
        except Exception:
            pass  # Error Memory is best-effort — never blocks execution
        # ── /Sprint 81 ───────────────────────────────────────────────────────

        event = (
            EventBuilder()
            .category(EventCategory.RUN_FAILED)
            .severity(Severity.ERROR)
            .actor("kernel.execute")
            .action(f"Execute failed: {str(e)[:200]}")
            .for_run_str(state.get("run_id", ""))
            .with_payload({"error": str(e)})
            .build()
        )

        existing_events = state.get("events", [])
        return {
            "status": RunStatus.FAILED.value,
            "error": str(e),
            "error_type": type(e).__name__,
            "execution_attempts": state.get("execution_attempts", 0) + 1,
            "latency_ms": (time.monotonic() - start_time) * 1000,
            "events": existing_events + [_event_to_dict(event)],
        }

    elapsed_ms = (time.monotonic() - start_time) * 1000

    # Check if HITL is needed for high-risk tool calls
    # Sprint 33D: Skip HITL when context.autonomous=True (Embrión loop)
    # The Embrión operates without a human in the loop — HITL would
    # cause an infinite interrupt() that blocks the graph forever.
    # This is UNIVERSAL: any autonomous caller can set autonomous=True.
    is_autonomous = state.get("context", {}).get("autonomous", False)
    needs_approval = False
    approval_reason = ""
    if pending_tool_calls and not is_autonomous:
        high_risk_tools = {s.name for s in tool_specs if s.risk in ("medium", "high")}
        requested_tools = {tc["name"] for tc in pending_tool_calls}
        if requested_tools & high_risk_tools:
            needs_approval = True
            approval_reason = f"Tool calls include high-risk tools: {requested_tools & high_risk_tools}"

    logger.info(
        "execute_completed",
        model=model_used,
        latency_ms=f"{elapsed_ms:.0f}",
        tokens_in=usage.get("prompt_tokens", 0),
        tokens_out=usage.get("completion_tokens", 0),
        has_tool_calls=bool(pending_tool_calls),
        tool_count=len(pending_tool_calls),
    )

    # ── Observability: record LLM generation ──
    obs = _obs(config)
    if obs:
        trace_ctx = state.get("_trace_ctx")
        if trace_ctx:
            obs.record_generation(
                ctx=trace_ctx,
                name="execute" + ("_followup" if is_followup else ""),
                model=model_used,
                input_messages=[{"role": "user", "content": message[:500]}],
                output=response[:500] if response else f"tool_calls={len(pending_tool_calls)}",
                usage={
                    "input": usage.get("prompt_tokens", 0),
                    "output": usage.get("completion_tokens", 0),
                    "unit": "TOKENS",
                },
                metadata={
                    "intent": intent,
                    "latency_ms": elapsed_ms,
                    "cost_usd": usage.get("cost_usd", 0.0),
                    "tool_calls": len(pending_tool_calls),
                    "is_followup": is_followup,
                },
            )

    event = (
        EventBuilder()
        .category(EventCategory.MODEL_CALLED)
        .actor("kernel.execute")
        .action(
            f"Executed on {model_used} in {elapsed_ms:.0f}ms"
            + (f" (tools: {len(pending_tool_calls)})" if pending_tool_calls else "")
        )
        .for_run_str(state.get("run_id", ""))
        .with_payload(
            {
                "model": model_used,
                "tokens_in": usage.get("prompt_tokens", 0),
                "tokens_out": usage.get("completion_tokens", 0),
                "cost_usd": usage.get("cost_usd", 0.0),
                "latency_ms": elapsed_ms,
                "tool_calls": len(pending_tool_calls),
                "is_followup": is_followup,
            }
        )
        .build()
    )

    # Sprint 39 Opt-2: Store response in cache for future hits
    if response and not is_followup and not pending_tool_calls:
        from kernel import response_cache
        response_cache.store(message, intent, response)

    # Accumulate tokens across tool loops
    existing_events = state.get("events", [])
    return {
        "status": RunStatus.EXECUTING.value,
        "response": response,
        "pending_tool_calls": pending_tool_calls,
        "tool_results": [],  # Clear tool_results after consuming them
        "tokens_in": state.get("tokens_in", 0) + usage.get("prompt_tokens", 0),
        "tokens_out": state.get("tokens_out", 0) + usage.get("completion_tokens", 0),
        "cost_usd": state.get("cost_usd", 0.0) + usage.get("cost_usd", 0.0),
        "latency_ms": state.get("latency_ms", 0) + elapsed_ms,
        "model_used": model_used,
        "execution_attempts": state.get("execution_attempts", 0) + 1,
        "needs_human_approval": needs_approval,
        "human_approval_reason": approval_reason,
        "events": existing_events + [_event_to_dict(event)],
    }


# ══════════════════════════════════════════════════════════════════════
# Node 5: MEMORY_WRITE (OPT-5: fire-and-forget from respond)
# ══════════════════════════════════════════════════════════════════════


async def memory_write(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Persist the conversation to memory and extract entities for the knowledge graph.

    OPT-5: This node is now called as a fire-and-forget background task
    from respond(), so it doesn't block the user response.
    The graph still includes it for completeness, but respond() also
    triggers it asynchronously.
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
            from uuid import UUID as UUIDType

            from contracts.memory_interface import MemoryEvent, MemoryType

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

    # Sprint 21: Write to MemPalace long-term memory
    try:
        from memory.mempalace_bridge import store_episode

        episode_content = f"User ({intent}): {message}\nAssistant: {response[:500]}" if response else message
        await store_episode(
            user_id=user_id,
            session_id=run_id,
            content=episode_content,
            metadata={
                "intent": intent,
                "model": state.get("model_used", ""),
                "channel": channel,
                "agent_type": state.get("agent_type", "default"),
            },
        )
        logger.info("mempalace_episode_stored", run_id=run_id)
    except Exception as e:
        logger.warning("mempalace_store_failed", error=str(e))

    # Sprint 27: Store interaction in Mem0 (replaces Honcho update_user_model)
    try:
        from memory.mem0_bridge import add_memory

        mem0_messages = [
            {"role": "user", "content": message[:500]},
        ]
        if response:
            mem0_messages.append({"role": "assistant", "content": response[:500]})

        mem0_result = await add_memory(
            messages=mem0_messages,
            user_id=user_id,
            metadata={"intent": intent, "channel": channel, "run_id": run_id},
        )
        if mem0_result.get("added", 0) > 0:
            logger.info("mem0_memory_stored", run_id=run_id, added=mem0_result["added"])
        else:
            logger.debug("mem0_store_skipped", reason=mem0_result.get("error", "no_facts_extracted"))
    except Exception as e:
        logger.warning("mem0_store_failed", error=str(e))

    # Write events to sovereign event store
    if event_store:
        try:
            for evt_dict in state.get("events", []):
                event = (
                    EventBuilder()
                    .category(EventCategory(evt_dict.get("category", "run.started")))
                    .actor(evt_dict.get("actor", "kernel"))
                    .action(evt_dict.get("action", ""))
                    .for_run_str(run_id)
                    .for_user(user_id)
                    .build()
                )
                await event_store.append(event)
        except Exception as e:
            logger.warning("event_store_write_failed", error=str(e))

    event = (
        EventBuilder()
        .category(EventCategory.MEMORY_UPDATED)
        .actor("kernel.memory_write")
        .action(f"Memory written for run {run_id}")
        .for_run_str(state.get("run_id", ""))
        .with_payload(
            {
                "entities_extracted": len(entities_extracted),
                "relations_extracted": len(relations_extracted),
            }
        )
        .build()
    )

    existing_events = state.get("events", [])
    return {
        "memory_written": True,
        "entities_extracted": entities_extracted,
        "relations_extracted": relations_extracted,
        "events": existing_events + [_event_to_dict(event)],
    }


# ══════════════════════════════════════════════════════════════════════
# Node 6: RESPOND
# ══════════════════════════════════════════════════════════════════════


async def respond(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Build and emit the final response.
    """
    response = state.get("response", "")
    status = state.get("status", RunStatus.COMPLETED.value)
    error = state.get("error")
    model_used = state.get("model_used", "unknown")

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

    # ── Observability: end trace ──
    obs = _obs(config)
    if obs:
        trace_ctx = state.get("_trace_ctx")
        if trace_ctx:
            obs.end_trace(
                ctx=trace_ctx,
                output=final_response[:500],
                status=status,
                metadata={
                    "model_used": model_used,
                    "latency_ms": state.get("latency_ms", 0),
                    "tokens_in": state.get("tokens_in", 0),
                    "tokens_out": state.get("tokens_out", 0),
                },
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
    OPT-3: Smart conditional edge after classify_and_route.

    Fast-path: Skip enrich for simple queries that don't need memory context.
    This saves ~300ms for greetings, math, and generic questions.

    Always enrich for:
    - deep_think, execute (need full context)
    - Messages with personal markers (mi, mis, proyecto, recuerda, etc.)
    - Messages referencing past conversations
    - ANY message when the thread has prior conversation history

    Skip enrich for:
    - background tasks
    - Short, simple chat without personal references AND no prior history
    """
    intent = state.get("intent", "chat")
    message = state.get("message", "").lower().strip()

    # Always skip for background
    if intent == "background":
        return "execute"

    # Always enrich for heavy intents
    if intent in ("deep_think", "execute"):
        return "enrich"

    # ── Sprint 56 Fix: Memory-aware markers check BEFORE supervisor skip ──
    # Personal markers indicate the user is referencing memory/history.
    # These OVERRIDE the supervisor's skip_enrich decision.
    personal_markers = {
        # ── Posesivos / referencias personales ──
        "mi ",
        "mis ",
        "tu ",
        "nuestro",
        "nuestra",
        # ── Verbos de memoria (con y sin acento) ──
        "recuerda",
        "recuerdas",
        "sabes",
        "sabías",
        "sabias",
        "acuerdas",
        "te acuerdas",
        # ── Proyectos / identidad ──
        "proyecto",
        "cip",
        "monstruo",
        "hive",
        # ── Temporales ──
        "ayer",
        "antes",
        "pasado",
        "semana",
        "mes",
        "instante",
        "hace un",
        "hace rato",
        "hace poco",
        "momento",
        "anterior",
        "previo",
        "último",
        "ultima",
        "última",
        "minuto",
        "recién",
        "recien",
        "ahorita",
        "apenas",
        # ── Verbos de conversación (con y sin acento) ──
        "dije",
        "dijiste",
        "dijimos",
        "hablamos",
        "mencioné",
        "mencione",
        "mencionaste",
        "pedí",
        "pedi",
        "pregunté",
        "pregunte",
        "conté",
        "conte",
        "contaste",
        "platiqué",
        "platique",
        "platicamos",
        "comenté",
        "comente",
        "comentaste",
        # ── Frases compuestas (con y sin acento) ──
        "te dije",
        "me dijiste",
        "te pregunté",
        "te pregunte",
        "te pedí",
        "te pedi",
        "te conté",
        "te conte",
        "me contaste",
        "te comenté",
        "te comente",
        "que te pedi",
        "que te pedí",
        # ── Personales del usuario ──
        "color favorito",
        "gato",
        "perro",
        "mascota",
        "anonymous",
        "góngora",
        "gongora",
    }

    needs_memory = any(marker in message for marker in personal_markers)
    if needs_memory:
        logger.info("enrich_forced_by_markers", message_preview=message[:60])
        return "enrich"

    # ── Sprint 56 Fix: If thread has conversation history, always enrich ──
    # This prevents the "I don't remember anything" bug when the user
    # asks about prior messages in a short/simple way.
    conversation_history = state.get("conversation_history", [])
    if conversation_history and len(conversation_history) > 0:
        logger.info("enrich_forced_by_history", history_len=len(conversation_history), message_preview=message[:60])
        return "enrich"

    # Sprint 39 Opt-1: Respetar skip_enrich del Supervisor (tier SIMPLE)
    # ONLY skip enrich if no markers matched AND no prior history exists
    if state.get("skip_enrich", False):
        logger.info("fast_path_supervisor_skip_enrich", intent=intent, message_preview=message[:60])
        return "execute"

    # OPT-3: Fast-path for simple chat (no markers, no history)
    if intent == "chat" and len(message) < 80:
        logger.info("fast_path_skip_enrich", message_preview=message[:60])
        return "execute"

    # Default: enrich for context-aware responses
    return "enrich"


def check_hitl(state: MonstruoState) -> str:
    """
    Conditional edge after execute: HITL check or proceed.
    - If execution failed → respond (with error)
    - If needs human approval → respond (with pause message)
    - Otherwise → memory_write
    """
    status = state.get("status", "")
    if status == RunStatus.FAILED.value:
        return "respond"
    if state.get("needs_human_approval", False):
        return "memory_write"
    return "memory_write"


# ══════════════════════════════════════════════════════════════════════
# Helper Functions
# ══════════════════════════════════════════════════════════════════════


# ── Sprint 84.5: Keyword matching con word boundaries ───────────
# Bug 14va semilla: substring matching sin word boundaries genera
# falsos positivos ("no voy a ejecutar" matcheaba "ejecuta").
# Pre-compilados a nivel módulo para evitar re-compilar por llamada.

_EXECUTE_KEYWORDS: tuple[str, ...] = (
    "ejecuta",
    "haz",
    "crea",
    "deploy",
    "instala",
    "configura",
    "borra",
    "elimina",
    "actualiza",
    "publica",
    "envía",
    "manda",
    "run",
    "execute",
    "do",
    "create",
    "delete",
    "update",
    "send",
)

_THINK_KEYWORDS: tuple[str, ...] = (
    "analiza",
    "piensa",
    "evalúa",
    "compara",
    "investiga",
    "explica",
    "por qué",
    "cómo funciona",
    "qué opinas",
    "analyze",
    "think",
    "evaluate",
    "compare",
    "research",
    "explain",
    "why",
    "how does",
)

# Word boundary regex (case-insensitive). \b respeta "ejecuta" pero
# rechaza "ejecutar" porque la palabra continúa más allá del keyword.
# Para verbos conjugados que SÍ deben matchear ("crear", "creando")
# preferimos rama LLM o keyword explícito; mantenemos foco en formas
# imperativas/infinitivo cortas que ya están en la lista.
_EXECUTE_KEYWORDS_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(kw) for kw in _EXECUTE_KEYWORDS) + r")\b",
    re.IGNORECASE,
)
_THINK_KEYWORDS_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(kw) for kw in _THINK_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

# Filtro de negaciones / preguntas que invalidan el match aunque
# contengan un execute keyword. Si CUALQUIERA matchea, el mensaje NO
# es una orden ejecutable.
_NEGATION_OR_QUESTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bno\s+(?:quiero|voy\s+a|deber[ií]a|necesito|puedo|hay|me|lo|la|los|las)\b", re.IGNORECASE),
    re.compile(r"\bantes\s+de\b", re.IGNORECASE),
    re.compile(r"\bc[oó]mo\s+se\b", re.IGNORECASE),
    re.compile(r"\b(?:podr[ií]as|puedes|sabes|sab[eé]s)\b", re.IGNORECASE),  # preguntas educadas
    re.compile(r"^\s*[¿?]", re.IGNORECASE),  # arranca con signo de pregunta
    re.compile(r"[¿?]\s*$", re.IGNORECASE),  # termina con signo de pregunta
)


def _is_negation_or_question(msg: str) -> bool:
    """Detecta si el mensaje es negación o pregunta (no es orden).

    Sprint 84.5 — 14va semilla. Los execute keywords solo deben
    disparar EXECUTE cuando el mensaje es una orden imperativa.
    """
    return any(pat.search(msg) for pat in _NEGATION_OR_QUESTION_PATTERNS)


def _local_classify(message: str) -> IntentType:
    """
    Keyword-based intent classification (fallback when no router/LLM).

    Sprint 84.5 fixes:
      - Word boundary matching (era substring crudo, 14va semilla).
      - Filtro de negaciones y preguntas antes de devolver EXECUTE.
    """
    msg = message.lower().strip()

    # Edge case: mensaje vacío → CHAT (sin crash, error controlado).
    if not msg:
        return IntentType.CHAT

    if msg.startswith("/") or msg.startswith("!"):
        return IntentType.SYSTEM

    # Execute con word boundaries + filtro de negación/pregunta.
    if _EXECUTE_KEYWORDS_PATTERN.search(msg) and not _is_negation_or_question(msg):
        return IntentType.EXECUTE

    # Think con word boundaries (no necesita filtro de negación porque
    # think no es destructivo si hay falso positivo).
    if _THINK_KEYWORDS_PATTERN.search(msg) or "por qué" in msg or "cómo funciona" in msg or "qué opinas" in msg or "how does" in msg:
        return IntentType.DEEP_THINK

    return IntentType.CHAT


def _default_model_for_intent(intent: str) -> tuple[str, list[str]]:
    """
    Default model selection when no router is available.
    Returns (primary_model, fallback_chain).

    OPT-4: chat uses gemini-3.1-flash-lite (fastest, cheapest).
    """
    INTENT_MODELS = {
        "chat": ("gemini-3.1-flash-lite", ["gpt-5.5", "claude-sonnet-4-6"]),
        "deep_think": ("gpt-5.5", ["claude-sonnet-4-6", "gemini-3.1-flash-lite"]),
        "execute": ("gpt-5.5", ["claude-sonnet-4-6", "gemini-3.1-flash-lite"]),
        "background": ("claude-sonnet-4-6", ["gpt-5.5", "gemini-3.1-flash-lite"]),
        "system": ("gemini-3.1-flash-lite", ["gpt-5.5", "claude-sonnet-4-6"]),
    }
    return INTENT_MODELS.get(intent, INTENT_MODELS["chat"])


def _get_fallback_chain(intent: str, primary_model: str) -> list[str]:
    """
    Build fallback chain excluding the primary model.
    """
    all_models = ["gpt-5.5", "claude-sonnet-4-6", "gemini-3.1-flash-lite"]
    return [m for m in all_models if m != primary_model][:2]


def _build_base_system_prompt() -> str:
    """
    Build the base system prompt for El Monstruo.
    Includes tool descriptions so the LLM can request tool usage.
    """
    from kernel.tool_dispatch import get_tool_aware_prompt_suffix

    tool_suffix = get_tool_aware_prompt_suffix()
    return (
        """Eres El Monstruo, el asistente de inteligencia artificial soberana de Alfredo Góngora.

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
        + tool_suffix
    )


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
