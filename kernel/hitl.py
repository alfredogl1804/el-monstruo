"""
El Monstruo — Human-in-the-Loop (HITL) Node v1.0
===================================================
Implementa HITL real usando LangGraph interrupt()/Command(resume=...).
Diseñado por el Consejo de 6 Sabios (Ciclo 3, 14 abril 2026).

Arquitectura:
  1. hitl_gate: nodo condicional que decide si pausar
  2. hitl_review: nodo que llama interrupt() y espera respuesta humana
  3. Integra con PolicyEngine y CompositeRisk para decisiones

Flujo:
  ... → execute → hitl_gate → [hitl_review] → respond → memory_write
                     ↓ (no HITL needed)
                   respond

LangGraph API verificada (14 abril 2026):
  - from langgraph.types import interrupt, Command
  - interrupt() pausa el grafo y retorna payload al caller
  - Command(resume=value) reanuda y value se convierte en return de interrupt()
  - Requiere checkpointer + thread_id en config

Reglas de interrupt():
  1. NO envolver en try/except
  2. NO reordenar calls dentro de un nodo
  3. Payload DEBE ser JSON-serializable
  4. Side effects antes de interrupt() DEBEN ser idempotentes

Dependencias: langgraph>=1.1.6, core/action_envelope.py, core/policy_engine.py
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from contracts.event_envelope import EventBuilder, EventCategory, Severity
from kernel.state import MonstruoState

logger = structlog.get_logger("kernel.hitl")


# ── HITL Gate (conditional edge function) ────────────────────────────

def hitl_gate(state: MonstruoState) -> str:
    """Conditional edge after execute: decide if HITL review is needed.

    Returns:
        "hitl_review" — if human approval is required
        "respond" — if no HITL needed (normal flow)
        "respond" — if execution failed (error flow)
    """
    from contracts.kernel_interface import RunStatus

    status = state.get("status", "")

    # Error flow: skip HITL, go to respond with error
    if status == RunStatus.FAILED.value:
        return "respond"

    # Check governance decision from enrich node
    policy_decision = state.get("policy_decision")
    needs_approval = state.get("needs_human_approval", False)

    if policy_decision == "HITL" or needs_approval:
        logger.info(
            "hitl_gate_triggered",
            run_id=state.get("run_id", ""),
            policy_decision=policy_decision,
            needs_approval=needs_approval,
            reason=state.get("human_approval_reason", ""),
        )
        return "hitl_review"

    return "respond"


# ── HITL Review Node ─────────────────────────────────────────────────

async def hitl_review(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """HITL review node — pauses execution using LangGraph interrupt().

    This node:
    1. Builds a review payload with action details
    2. Calls interrupt() to pause the graph
    3. Waits for Command(resume=...) from the caller
    4. Processes the human response (approve/reject/modify)
    5. Returns updated state

    The interrupt payload is sent to the caller (Telegram bot, API, console)
    which presents it to the human and collects their response.
    """
    run_id = state.get("run_id", "")
    intent = state.get("intent", "")
    message = state.get("message", "")
    response = state.get("response", "")
    risk_level = state.get("risk_level", "L1_SAFE")
    trust_ring = state.get("trust_ring", "R2_USER_DELEGATED")
    approval_reason = state.get("human_approval_reason", "Policy requires approval")
    action_envelope = state.get("action_envelope")

    logger.info(
        "hitl_review_started",
        run_id=run_id,
        risk_level=risk_level,
        reason=approval_reason,
    )

    # Build review payload for the human
    review_payload = {
        "type": "hitl_review",
        "run_id": run_id,
        "intent": intent,
        "message_preview": message[:200],
        "proposed_response_preview": response[:500] if response else "",
        "risk_level": risk_level,
        "trust_ring": trust_ring,
        "reason": approval_reason,
        "action_envelope_summary": _summarize_envelope(action_envelope) if action_envelope else None,
        "options": ["approve", "reject", "modify"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # ── INTERRUPT: Pause graph execution ──────────────────────────
    # This is the real LangGraph interrupt() call.
    # The graph pauses here and the review_payload is sent to the caller.
    # When Command(resume={"decision": "approve"|"reject"|"modify", ...})
    # is invoked, execution resumes and human_response receives that value.
    human_response = interrupt(review_payload)

    # ── Process human response ────────────────────────────────────
    # human_response is the value from Command(resume=...)
    decision = "approve"  # default
    modification = None

    if isinstance(human_response, dict):
        decision = human_response.get("decision", "approve")
        modification = human_response.get("modification")
    elif isinstance(human_response, str):
        decision = human_response.lower()
    elif isinstance(human_response, bool):
        decision = "approve" if human_response else "reject"

    logger.info(
        "hitl_review_completed",
        run_id=run_id,
        decision=decision,
        has_modification=modification is not None,
    )

    # Build event
    event = EventBuilder() \
        .category(EventCategory.HUMAN_REVIEWED) \
        .actor("kernel.hitl_review") \
        .action(f"Human decision: {decision}") \
        .for_run_str(run_id) \
        .severity(Severity.INFO if decision == "approve" else Severity.WARNING) \
        .with_payload({
            "decision": decision,
            "risk_level": risk_level,
            "reason": approval_reason,
            "has_modification": modification is not None,
        }) \
        .build()

    existing_events = state.get("events", [])

    if decision == "reject":
        from contracts.kernel_interface import RunStatus
        return {
            "status": RunStatus.FAILED.value,
            "needs_human_approval": False,
            "human_response": decision,
            "error": f"Action rejected by human: {approval_reason}",
            "events": existing_events + [_event_to_dict(event)],
        }

    if decision == "modify" and modification:
        # Human provided a modified response
        return {
            "needs_human_approval": False,
            "human_response": decision,
            "response": modification,  # Override the LLM response
            "events": existing_events + [_event_to_dict(event)],
        }

    # Default: approved — continue with original response
    return {
        "needs_human_approval": False,
        "human_response": decision,
        "events": existing_events + [_event_to_dict(event)],
    }


# ── Helpers ──────────────────────────────────────────────────────────

def _summarize_envelope(envelope_dict: dict[str, Any] | None) -> dict[str, Any] | None:
    """Extract key fields from serialized ActionEnvelope for human review."""
    if not envelope_dict:
        return None
    return {
        "action_type": envelope_dict.get("action_type"),
        "target": {
            "resource_kind": envelope_dict.get("target", {}).get("resource_kind"),
            "resource_id": envelope_dict.get("target", {}).get("resource_id"),
        },
        "operation": envelope_dict.get("operation"),
        "intent_summary": envelope_dict.get("intent_summary", "")[:200],
    }


def _event_to_dict(event: Any) -> dict[str, Any]:
    """Convert an event to a serializable dict."""
    if isinstance(event, dict):
        return event
    if hasattr(event, "__dict__"):
        d = {}
        for k, v in event.__dict__.items():
            if hasattr(v, "value"):
                d[k] = v.value
            elif hasattr(v, "isoformat"):
                d[k] = v.isoformat()
            elif isinstance(v, dict):
                d[k] = v
            else:
                d[k] = str(v)
        return d
    return {"raw": str(event)}
