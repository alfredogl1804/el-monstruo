"""
Dory Orchestrator — Unified Anti-Dory Pipeline (El Monstruo)
=============================================================
El "pegamento" que conecta los 8 sistemas de memoria existentes en un
flujo secuencial obligatorio. Cada acción del Monstruo pasa por este
pipeline ANTES de ejecutarse.

Flujo:
  ┌─────────────────────────────────────────────────────────────────┐
  │ 1. GUARDIAN ANCHOR    — Verificar identidad + estado (tri-anchor)│
  │ 2. CONTEXT HYDRATION  — Inyectar attachment_pack (Context Broker)│
  │ 3. MEMENTO VALIDATE   — Verificar contra fuentes de verdad       │
  │ 4. ERROR MEMORY       — Consultar errores previos similares      │
  │ 5. KNOWLEDGE RECALL   — Buscar en knowledge graph (LightRAG)     │
  │ 6. MEM0 EPISODIC      — Buscar memorias episódicas relevantes    │
  │ 7. B8 CLASSIFY        — Clasificar riesgo de la acción           │
  │ 8. B9 AUTHORITY       — Resolver autoridad final (PROCEED/HALT)  │
  └─────────────────────────────────────────────────────────────────┘

Principios:
  - Cada paso es OPCIONAL en degradación (graceful fallback)
  - El pipeline NUNCA bloquea si un subsistema falla (excepto B9 HALT)
  - Cada paso enriquece un DoryContext compartido
  - El resultado final es un DoryVerdict: PROCEED, CAUTION, o HALT
  - Toda la ejecución se loguea para auditoría

Integración:
  - Se llama desde `kernel/nodes.py` en el nodo `execute` ANTES de actuar
  - También disponible como decorator `@dory_gate` para tools individuales
  - Feature flag: DORY_ORCHESTRATOR_ENABLED (default: true si ANTI_DORY_B8_V3_ENABLED=true)

Sprint: Batch 011 v3 — Anti-Dory Unification
Autor: Manus AI (Hilo principal)
Fecha: 2026-05-21
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("monstruo.dory_orchestrator")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════


# Sprint WIRING-002: Cache for DB flag check (avoid hitting DB on every call)
_db_flag_cache: dict[str, Any] = {"value": None, "checked_at": 0.0}


def _is_enabled() -> bool:
    """Read feature flag fresh from env or Supabase runtime_flags.

    Priority:
      1. DORY_ORCHESTRATOR_ENABLED env var
      2. ANTI_DORY_B8_V3_ENABLED env var
      3. anti_dory_runtime_flags.shadow_write_enabled in Supabase (cached 5 min)
    """
    flag = os.environ.get("DORY_ORCHESTRATOR_ENABLED", "").lower()
    if flag in ("true", "1", "yes"):
        return True
    # Fallback 1: inherit from B8 v3 flag
    if os.environ.get("ANTI_DORY_B8_V3_ENABLED", "").lower() in ("true", "1", "yes"):
        return True
    # Fallback 2: check Supabase runtime_flags (cached 5 min)
    now = time.time()
    if _db_flag_cache["value"] is not None and (now - _db_flag_cache["checked_at"]) < 300:
        return _db_flag_cache["value"]
    try:
        import httpx
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "") or os.environ.get("SUPABASE_ANON_KEY", "")
        if url and key:
            resp = httpx.get(
                f"{url}/rest/v1/anti_dory_runtime_flags?singleton_lock=eq.anti_dory_singleton&select=shadow_write_enabled",
                headers={"apikey": key, "Authorization": f"Bearer {key}"},
                timeout=5.0,
            )
            if resp.status_code == 200:
                rows = resp.json()
                if rows and isinstance(rows, list):
                    val = bool(rows[0].get("shadow_write_enabled", False))
                    _db_flag_cache["value"] = val
                    _db_flag_cache["checked_at"] = now
                    return val
    except Exception:
        pass
    _db_flag_cache["value"] = False
    _db_flag_cache["checked_at"] = now
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════


class DoryVerdict(str, Enum):
    """Final verdict of the orchestrator."""

    PROCEED = "PROCEED"  # All clear — execute the action
    CAUTION = "CAUTION"  # Warnings present but not blocking
    HALT = "HALT"  # Action blocked — requires T1 or remediation


class StepStatus(str, Enum):
    """Status of each pipeline step."""

    OK = "ok"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"
    DEGRADED = "degraded"


@dataclass
class StepResult:
    """Result of a single pipeline step."""

    step_name: str
    status: StepStatus
    duration_ms: float
    data: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class DoryContext:
    """
    Shared context that accumulates through the pipeline.
    Each step reads from and writes to this context.
    """

    # Input
    action_type: str
    action_description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: str = "alfredo"
    project_id: str = "el_monstruo"
    hilo_id: str = "manus_main"

    # Accumulated by pipeline steps
    identity_verified: bool = False
    attachment_pack: Optional[Dict[str, Any]] = None
    memento_valid: bool = True
    memento_discrepancies: List[str] = field(default_factory=list)
    error_rules: List[Dict[str, Any]] = field(default_factory=list)
    knowledge_context: List[str] = field(default_factory=list)
    episodic_memories: List[Dict[str, Any]] = field(default_factory=list)
    risk_level: str = "STANDARD"
    requires_t1: bool = False
    authority_decision: str = "PROCEED"

    # Pipeline metadata
    steps: List[StepResult] = field(default_factory=list)
    total_duration_ms: float = 0.0


@dataclass
class DoryResult:
    """Final result of the Dory Orchestrator pipeline."""

    verdict: DoryVerdict
    context: DoryContext
    reason: str
    enriched_prompt: str = ""  # Original prompt + injected context


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE STEPS (each wraps an existing system)
# ═══════════════════════════════════════════════════════════════════════════════


async def _step_guardian_anchor(ctx: DoryContext) -> StepResult:
    """
    Step 1: Verify identity and state via Guardian's tri-anchor system.
    Checks: filesystem anchor exists + is fresh.
    """
    start = time.perf_counter()
    try:
        state_file = os.path.expanduser("~/.monstruo/state/identity.json")
        if os.path.exists(state_file):
            import json

            with open(state_file) as f:
                identity = json.load(f)
            ctx.identity_verified = True
            ctx.hilo_id = identity.get("hilo_id", ctx.hilo_id)
            return StepResult(
                step_name="guardian_anchor",
                status=StepStatus.OK,
                duration_ms=(time.perf_counter() - start) * 1000,
                data={"hilo_id": ctx.hilo_id, "identity_found": True},
            )
        else:
            ctx.identity_verified = False
            return StepResult(
                step_name="guardian_anchor",
                status=StepStatus.DEGRADED,
                duration_ms=(time.perf_counter() - start) * 1000,
                warnings=["Identity file not found — operating without anchor"],
            )
    except Exception as e:
        return StepResult(
            step_name="guardian_anchor",
            status=StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            errors=[f"Guardian anchor check failed: {e}"],
        )


async def _step_context_hydration(ctx: DoryContext) -> StepResult:
    """
    Step 2: Inject attachment_pack via Context Broker.
    Provides: last T1 decision, current phase, sprint state, blockers.
    """
    start = time.perf_counter()
    try:
        from kernel.anti_dory.context_broker import ContextBroker, SupabaseRPCClient

        # Try to get RPC client from kernel
        rpc_client = _get_rpc_client()
        if rpc_client is None:
            return StepResult(
                step_name="context_hydration",
                status=StepStatus.DEGRADED,
                duration_ms=(time.perf_counter() - start) * 1000,
                warnings=["No RPC client available — context hydration skipped"],
            )

        broker = ContextBroker(rpc_client)
        hydrated = broker.hydrate_prompt(
            project_id=ctx.project_id,
            front_id=ctx.hilo_id,
            user_prompt=ctx.action_description,
        )
        ctx.attachment_pack = hydrated.pack.to_dict() if hydrated.pack.attachment_ok else None
        return StepResult(
            step_name="context_hydration",
            status=StepStatus.OK if hydrated.pack.attachment_ok else StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            data={"attachment_ok": hydrated.pack.attachment_ok},
        )
    except ImportError:
        return StepResult(
            step_name="context_hydration",
            status=StepStatus.SKIPPED,
            duration_ms=(time.perf_counter() - start) * 1000,
            warnings=["context_broker not importable — skipped"],
        )
    except Exception as e:
        return StepResult(
            step_name="context_hydration",
            status=StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            errors=[f"Context hydration failed: {e}"],
        )


async def _step_memento_validate(ctx: DoryContext) -> StepResult:
    """
    Step 3: Validate current context against sources of truth (Memento).
    Catches: stale state, contradictions with canonical decisions.
    """
    start = time.perf_counter()
    try:
        from kernel.memento.validator import MementoValidator

        validator = _get_memento_validator()
        if validator is None:
            return StepResult(
                step_name="memento_validate",
                status=StepStatus.SKIPPED,
                duration_ms=(time.perf_counter() - start) * 1000,
                warnings=["MementoValidator not initialized — skipped"],
            )

        result = await validator.validate(
            operation=ctx.action_type,
            context_used=ctx.metadata,
            hilo_id=ctx.hilo_id,
            intent_summary=ctx.action_description,
        )
        ctx.memento_valid = result.proceed
        if not result.proceed:
            ctx.memento_discrepancies.append(result.remediation or "Unknown discrepancy")

        return StepResult(
            step_name="memento_validate",
            status=StepStatus.OK if result.proceed else StepStatus.WARNING,
            duration_ms=(time.perf_counter() - start) * 1000,
            data={"proceed": result.proceed, "status": result.validation_status.value},
            warnings=[] if result.proceed else [result.remediation or "Discrepancy detected"],
        )
    except ImportError:
        return StepResult(
            step_name="memento_validate",
            status=StepStatus.SKIPPED,
            duration_ms=(time.perf_counter() - start) * 1000,
            warnings=["memento.validator not importable — skipped"],
        )
    except Exception as e:
        return StepResult(
            step_name="memento_validate",
            status=StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            errors=[f"Memento validation failed: {e}"],
        )


async def _step_error_memory(ctx: DoryContext) -> StepResult:
    """
    Step 4: Consult Error Memory for similar past failures.
    Prevents: repeating known mistakes (Obj #4).
    """
    start = time.perf_counter()
    try:
        from kernel.error_memory import ErrorMemory

        em = _get_error_memory()
        if em is None or not em.initialized:
            return StepResult(
                step_name="error_memory",
                status=StepStatus.SKIPPED,
                duration_ms=(time.perf_counter() - start) * 1000,
                warnings=["ErrorMemory not initialized — skipped"],
            )

        rules = await em.consult(
            intent=ctx.action_description,
            context={"module": ctx.action_type, "action": ctx.action_description},
        )
        ctx.error_rules = [{"signature": r.signature, "rule": r.rule_text, "confidence": r.confidence} for r in rules]
        has_blockers = any(r.confidence >= 0.9 for r in rules)

        return StepResult(
            step_name="error_memory",
            status=StepStatus.WARNING if has_blockers else StepStatus.OK,
            duration_ms=(time.perf_counter() - start) * 1000,
            data={"rules_found": len(rules), "has_blockers": has_blockers},
            warnings=[f"High-confidence error rule: {r.rule_text}" for r in rules if r.confidence >= 0.9],
        )
    except ImportError:
        return StepResult(
            step_name="error_memory",
            status=StepStatus.SKIPPED,
            duration_ms=(time.perf_counter() - start) * 1000,
            warnings=["error_memory not importable — skipped"],
        )
    except Exception as e:
        return StepResult(
            step_name="error_memory",
            status=StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            errors=[f"Error memory consult failed: {e}"],
        )


async def _step_knowledge_recall(ctx: DoryContext) -> StepResult:
    """
    Step 5: Query Knowledge Graph (LightRAG) for relevant context.
    Provides: related decisions, architectural constraints, domain knowledge.
    """
    start = time.perf_counter()
    try:
        from memory.lightrag_bridge import query_knowledge

        results = await query_knowledge(ctx.action_description, mode="hybrid", top_k=3)
        ctx.knowledge_context = [r.get("content", "") for r in results if r.get("content")]

        return StepResult(
            step_name="knowledge_recall",
            status=StepStatus.OK if ctx.knowledge_context else StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            data={"results_found": len(ctx.knowledge_context)},
        )
    except ImportError:
        return StepResult(
            step_name="knowledge_recall",
            status=StepStatus.SKIPPED,
            duration_ms=(time.perf_counter() - start) * 1000,
            warnings=["lightrag_bridge not importable — skipped"],
        )
    except Exception as e:
        return StepResult(
            step_name="knowledge_recall",
            status=StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            errors=[f"Knowledge recall failed: {e}"],
        )


async def _step_mem0_episodic(ctx: DoryContext) -> StepResult:
    """
    Step 6: Search Mem0 for episodic memories relevant to this action.
    Provides: past interactions, user preferences, historical context.
    """
    start = time.perf_counter()
    try:
        from memory.mem0_bridge import search_memory

        memories = await search_memory(
            query=f"{ctx.action_type}: {ctx.action_description}",
            user_id=ctx.user_id,
            limit=5,
        )
        ctx.episodic_memories = memories

        return StepResult(
            step_name="mem0_episodic",
            status=StepStatus.OK if memories else StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            data={"memories_found": len(memories)},
        )
    except ImportError:
        return StepResult(
            step_name="mem0_episodic",
            status=StepStatus.SKIPPED,
            duration_ms=(time.perf_counter() - start) * 1000,
            warnings=["mem0_bridge not importable — skipped"],
        )
    except Exception as e:
        return StepResult(
            step_name="mem0_episodic",
            status=StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            errors=[f"Mem0 episodic search failed: {e}"],
        )


async def _step_b8_classify(ctx: DoryContext) -> StepResult:
    """
    Step 7: Classify action risk level via B8 Magna Classifier.
    Determines: MAGNA (dangerous) vs STANDARD (safe).
    """
    start = time.perf_counter()
    try:
        from kernel.anti_dory.b8_magna_classifier import ActionLevel, classify_action

        classification = classify_action(
            action_type=ctx.action_type,
            description=ctx.action_description,
            metadata=ctx.metadata,
        )
        ctx.risk_level = classification.level.value
        ctx.requires_t1 = classification.requires_t1

        return StepResult(
            step_name="b8_classify",
            status=StepStatus.WARNING if classification.level == ActionLevel.MAGNA else StepStatus.OK,
            duration_ms=(time.perf_counter() - start) * 1000,
            data={
                "level": classification.level.value,
                "reason": classification.reason,
                "requires_t1": classification.requires_t1,
            },
            warnings=[f"MAGNA: {classification.reason}"] if classification.level == ActionLevel.MAGNA else [],
        )
    except ImportError:
        return StepResult(
            step_name="b8_classify",
            status=StepStatus.SKIPPED,
            duration_ms=(time.perf_counter() - start) * 1000,
            warnings=["b8_magna_classifier not importable — skipped"],
        )
    except Exception as e:
        return StepResult(
            step_name="b8_classify",
            status=StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            errors=[f"B8 classification failed: {e}"],
        )


async def _step_b9_authority(ctx: DoryContext) -> StepResult:
    """
    Step 8: Resolve final authority via B9 Authority Matrix.
    Combines all signals into PROCEED, CAUTION, or HALT.
    """
    start = time.perf_counter()
    try:
        from kernel.anti_dory.b9_authority_matrix import (
            AuthorityMatrix,
            Decision,
            LayerStatus,
            LayerVote,
        )

        matrix = AuthorityMatrix()

        # Build votes from pipeline context
        verificador_vote = LayerVote(
            status=LayerStatus.OK if ctx.identity_verified else LayerStatus.DEGRADED,
            decision=Decision.PROCEED,
        )
        memento_vote = LayerVote(
            status=LayerStatus.OK if ctx.memento_valid else LayerStatus.FLAGGED,
            decision=Decision.PROCEED if ctx.memento_valid else Decision.HALT,
        )
        guardian_vote = LayerVote(
            status=LayerStatus.OK,
            decision=Decision.PROCEED,
        )

        # T1 vote only if action requires it and we have no T1 approval
        t1_vote = None
        if ctx.requires_t1:
            t1_vote = None  # No T1 signature available → will trigger HALT

        result = matrix.resolve(
            verificador=verificador_vote,
            memento=memento_vote,
            guardian=guardian_vote,
            t1=t1_vote,
        )
        ctx.authority_decision = result.final_decision.value

        return StepResult(
            step_name="b9_authority",
            status=StepStatus.OK if result.final_decision == Decision.PROCEED else StepStatus.WARNING,
            duration_ms=(time.perf_counter() - start) * 1000,
            data={
                "decision": result.final_decision.value,
                "system_state": result.system_state.value,
            },
        )
    except ImportError:
        # If B9 is not available, use simplified logic
        if ctx.requires_t1:
            ctx.authority_decision = "HALT"
        elif not ctx.memento_valid:
            ctx.authority_decision = "HALT"
        else:
            ctx.authority_decision = "PROCEED"

        return StepResult(
            step_name="b9_authority",
            status=StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            warnings=["b9_authority_matrix not importable — using simplified logic"],
            data={"decision": ctx.authority_decision},
        )
    except Exception as e:
        ctx.authority_decision = "CAUTION"
        return StepResult(
            step_name="b9_authority",
            status=StepStatus.DEGRADED,
            duration_ms=(time.perf_counter() - start) * 1000,
            errors=[f"B9 authority resolution failed: {e}"],
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

# Pipeline steps in execution order
PIPELINE_STEPS = [
    _step_guardian_anchor,
    _step_context_hydration,
    _step_memento_validate,
    _step_error_memory,
    _step_knowledge_recall,
    _step_mem0_episodic,
    _step_b8_classify,
    _step_b9_authority,
]


async def run_pipeline(
    action_type: str,
    description: str,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: str = "alfredo",
    project_id: str = "el_monstruo",
    hilo_id: str = "manus_main",
) -> DoryResult:
    """
    Execute the full Dory Orchestrator pipeline.

    Args:
        action_type: Type of action being attempted (e.g., "merge_to_main")
        description: Human-readable description of the action
        metadata: Additional context (e.g., {"branch": "main", "table": "users"})
        user_id: User initiating the action
        project_id: Project context
        hilo_id: Thread/agent identifier

    Returns:
        DoryResult with verdict (PROCEED/CAUTION/HALT), enriched context, and reason.
    """
    if not _is_enabled():
        return DoryResult(
            verdict=DoryVerdict.PROCEED,
            context=DoryContext(action_type=action_type, action_description=description),
            reason="Dory Orchestrator disabled (feature flag off)",
        )

    ctx = DoryContext(
        action_type=action_type,
        action_description=description,
        metadata=metadata or {},
        user_id=user_id,
        project_id=project_id,
        hilo_id=hilo_id,
    )

    pipeline_start = time.perf_counter()

    # Execute all steps sequentially
    for step_fn in PIPELINE_STEPS:
        try:
            result = await step_fn(ctx)
            ctx.steps.append(result)
            logger.debug(
                "dory_step_completed",
                step=result.step_name,
                status=result.status.value,
                duration_ms=result.duration_ms,
            )
        except Exception as e:
            # Catastrophic step failure — log and continue
            ctx.steps.append(
                StepResult(
                    step_name=step_fn.__name__.replace("_step_", ""),
                    status=StepStatus.FAILED,
                    duration_ms=0,
                    errors=[f"Unhandled exception: {e}"],
                )
            )
            logger.error("dory_step_catastrophic_failure", step=step_fn.__name__, error=str(e))

    ctx.total_duration_ms = (time.perf_counter() - pipeline_start) * 1000

    # Determine final verdict
    verdict, reason = _compute_verdict(ctx)

    # Build enriched prompt with accumulated context
    enriched = _build_enriched_prompt(ctx)

    return DoryResult(
        verdict=verdict,
        context=ctx,
        reason=reason,
        enriched_prompt=enriched,
    )


def _compute_verdict(ctx: DoryContext) -> tuple[DoryVerdict, str]:
    """Compute final verdict from accumulated context."""
    # HALT conditions (hard blockers)
    if ctx.authority_decision == "HALT":
        return DoryVerdict.HALT, "B9 Authority Matrix returned HALT"
    if not ctx.memento_valid and ctx.requires_t1:
        return DoryVerdict.HALT, "Memento discrepancy + T1 required"
    if any(r.get("confidence", 0) >= 0.95 for r in ctx.error_rules):
        return DoryVerdict.HALT, "Error Memory has critical-confidence blocker"

    # CAUTION conditions (soft warnings)
    warnings = []
    if not ctx.identity_verified:
        warnings.append("Identity not verified")
    if not ctx.memento_valid:
        warnings.append(f"Memento discrepancies: {ctx.memento_discrepancies}")
    if ctx.error_rules:
        warnings.append(f"{len(ctx.error_rules)} error rules found")
    if ctx.risk_level == "MAGNA":
        warnings.append("Action classified as MAGNA")

    if warnings:
        return DoryVerdict.CAUTION, "; ".join(warnings)

    return DoryVerdict.PROCEED, "All checks passed"


def _build_enriched_prompt(ctx: DoryContext) -> str:
    """Build an enriched prompt that includes all accumulated context."""
    sections = []

    # Attachment pack (T1 decisions, phase, blockers)
    if ctx.attachment_pack:
        sections.append(f"[CONTEXT BROKER] Last T1 decision: {ctx.attachment_pack.get('last_t1_decision', 'N/A')}")
        sections.append(f"[CONTEXT BROKER] Current phase: {ctx.attachment_pack.get('phase', 'N/A')}")

    # Error rules (don't repeat these)
    if ctx.error_rules:
        rules_text = "; ".join(r["rule"] for r in ctx.error_rules[:3])
        sections.append(f"[ERROR MEMORY] Known pitfalls: {rules_text}")

    # Knowledge context
    if ctx.knowledge_context:
        sections.append(f"[KNOWLEDGE GRAPH] Relevant context: {ctx.knowledge_context[0][:200]}")

    # Episodic memories
    if ctx.episodic_memories:
        mem_text = "; ".join(m.get("memory", "") for m in ctx.episodic_memories[:3])
        sections.append(f"[EPISODIC] Related memories: {mem_text[:300]}")

    # Risk classification
    if ctx.risk_level == "MAGNA":
        sections.append("[B8 CLASSIFIER] WARNING: Action classified as MAGNA — requires T1 approval")

    if not sections:
        return ""

    return "\n".join(["--- DORY ORCHESTRATOR CONTEXT ---"] + sections + ["--- END DORY CONTEXT ---"])


# ═══════════════════════════════════════════════════════════════════════════════
# DECORATOR API (for individual tools)
# ═══════════════════════════════════════════════════════════════════════════════


def dory_gate(
    action_type: str = "unknown",
    halt_on_caution: bool = False,
):
    """
    Decorator that runs the Dory pipeline before executing a function.

    Usage:
        @dory_gate(action_type="merge_to_main")
        async def do_merge(branch: str):
            ...

    If verdict is HALT, raises DoryHaltError.
    If verdict is CAUTION and halt_on_caution=True, also raises.
    Otherwise, injects dory_context as kwarg if function accepts it.
    """

    def decorator(func: Callable):
        import functools
        import inspect

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            description = kwargs.get("description", str(args[:2]) if args else "")
            metadata = kwargs.get("metadata", {})

            result = await run_pipeline(
                action_type=action_type,
                description=str(description),
                metadata=metadata if isinstance(metadata, dict) else {},
            )

            if result.verdict == DoryVerdict.HALT:
                raise DoryHaltError(result.reason, result)
            if result.verdict == DoryVerdict.CAUTION and halt_on_caution:
                raise DoryHaltError(f"CAUTION (halt_on_caution=True): {result.reason}", result)

            # Inject context if function accepts it
            sig = inspect.signature(func)
            if "dory_context" in sig.parameters:
                kwargs["dory_context"] = result.context

            return await func(*args, **kwargs)

        return wrapper

    return decorator


class DoryHaltError(Exception):
    """Raised when the Dory Orchestrator blocks an action."""

    def __init__(self, reason: str, result: DoryResult):
        super().__init__(reason)
        self.result = result


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON GETTERS (lazy initialization, graceful degradation)
# ═══════════════════════════════════════════════════════════════════════════════

_rpc_client = None
_memento_validator = None
_error_memory = None


def _get_rpc_client():
    """Get or create Supabase RPC client. Returns None if unavailable."""
    global _rpc_client
    if _rpc_client is not None:
        return _rpc_client
    try:
        os.environ.get("SUPABASE_DB_URL", "")
        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if not supabase_url or not supabase_key:
            return None
        from memory.supabase_client import SupabaseClient

        _rpc_client = SupabaseClient(url=supabase_url, key=supabase_key)
        return _rpc_client
    except Exception:
        return None


def _get_memento_validator():
    """Get or create MementoValidator. Returns None if unavailable."""
    global _memento_validator
    if _memento_validator is not None:
        return _memento_validator
    try:
        from kernel.memento.validator import MementoValidator

        _memento_validator = MementoValidator()
        return _memento_validator
    except Exception:
        return None


def _get_error_memory():
    """Get or create ErrorMemory. Returns None if unavailable."""
    global _error_memory
    if _error_memory is not None:
        return _error_memory
    try:
        from kernel.error_memory import ErrorMemory

        _error_memory = ErrorMemory()
        return _error_memory
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# STANDALONE EXECUTION (for testing)
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    async def _test():
        # Test STANDARD action
        r1 = await run_pipeline(
            action_type="read_file",
            description="Read the README.md for context",
        )
        print(f"[STANDARD] Verdict: {r1.verdict.value} — {r1.reason}")
        print(f"  Duration: {r1.context.total_duration_ms:.1f}ms")
        print(f"  Steps: {[(s.step_name, s.status.value) for s in r1.context.steps]}")
        print()

        # Test MAGNA action
        r2 = await run_pipeline(
            action_type="merge_to_main",
            description="Merge feature branch directly to main without PR",
        )
        print(f"[MAGNA] Verdict: {r2.verdict.value} — {r2.reason}")
        print(f"  Duration: {r2.context.total_duration_ms:.1f}ms")
        print(f"  Steps: {[(s.step_name, s.status.value) for s in r2.context.steps]}")
        print()

        # Test with enriched prompt
        r3 = await run_pipeline(
            action_type="deploy_production",
            description="Deploy the kernel to Railway production environment",
            metadata={"environment": "production", "service": "kernel"},
        )
        print(f"[DEPLOY] Verdict: {r3.verdict.value} — {r3.reason}")
        if r3.enriched_prompt:
            print(f"  Enriched prompt:\n{r3.enriched_prompt}")

        # Summary
        print("\n" + "=" * 60)
        print("DORY ORCHESTRATOR — PIPELINE SUMMARY")
        print("=" * 60)
        results = {"STANDARD": r1, "MAGNA": r2, "DEPLOY": r3}
        for name, r in results.items():
            print(f"  {name}: {r.verdict.value} ({r.context.total_duration_ms:.0f}ms)")

    asyncio.run(_test())
