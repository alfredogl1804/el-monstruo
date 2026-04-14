"""
El Monstruo — Kernel State (LangGraph Rewrite)
================================================
Defines the MonstruoState TypedDict that flows through the LangGraph graph.
This is the shared state that all nodes read from and write to.

Principio: El estado es nuestro. LangGraph solo lo transporta.
"""

from __future__ import annotations

from typing import Any, Optional
from typing_extensions import TypedDict
from uuid import UUID


class MonstruoState(TypedDict, total=False):
    """
    Shared state for the LangGraph execution graph.

    Every node reads what it needs and writes what it produces.
    LangGraph manages the state transitions between nodes.

    Fields are grouped by lifecycle phase:
    - Input: set at intake
    - Routing: set at classify + route
    - Enrichment: set at enrich
    - Execution: set at execute
    - Memory: set at memory_write
    - Output: set at respond
    - Meta: tracking and control
    """

    # ── Input (set at intake) ──────────────────────────────────────
    run_id: str                    # UUID as string for serialization
    user_id: str
    channel: str                   # telegram | console | api
    message: str                   # Raw user message
    attachments: list[str]         # File paths or URLs
    context: dict[str, Any]        # Additional context from caller
    parent_run_id: Optional[str]   # For sub-runs

    # ── Routing (set at classify + route) ──────────────────────────
    intent: str                    # chat | deep_think | execute | background | system
    model: str                     # Selected model name (e.g., "gpt-5")
    fallback_models: list[str]     # Ordered fallback chain
    route_reason: str              # Why this model was chosen

    # ── Enrichment (set at enrich) ─────────────────────────────────
    conversation_context: list[dict[str, str]]  # Previous messages for LLM
    relevant_memories: list[dict[str, Any]]     # Semantic search results
    knowledge_entities: list[dict[str, Any]]    # Related entities from graph
    system_prompt: str                          # Constructed system prompt
    enriched: bool                              # Whether enrichment ran

    # ── Execution (set at execute) ─────────────────────────────────
    response: str                  # Model response text
    tool_calls: list[dict[str, Any]]  # Tool calls made during execution
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: float
    model_used: str                # Actual model used (may differ from selected if fallback)
    execution_attempts: int        # Number of attempts (retries)

    # ── Memory (set at memory_write) ───────────────────────────────
    memory_written: bool           # Whether memory was persisted
    entities_extracted: list[dict[str, Any]]  # Entities found in this run
    relations_extracted: list[dict[str, Any]] # Relations found in this run
    episode_id: Optional[str]      # Active episode UUID

    # ── Output (set at respond) ────────────────────────────────────
    final_response: str            # The response sent to the user
    response_channel: str          # Where the response was sent

    # ── Meta (tracking and control) ────────────────────────────────
    status: str                    # Current RunStatus value
    step_count: int                # Number of steps executed
    events: list[dict[str, Any]]   # Accumulated events for this run
    error: Optional[str]           # Error message if failed
    error_type: Optional[str]      # Error class name
    cancelled: bool                # Kill switch flag
    cancel_reason: str             # Why it was cancelled
    started_at: str                # ISO timestamp
    completed_at: Optional[str]    # ISO timestamp

    # ── HITL (Human-in-the-Loop) ───────────────────────────────────
    needs_human_approval: bool     # Whether to pause for human review
    human_approval_reason: str     # Why approval is needed
    human_response: Optional[str]  # Response from human (after resume)

    # ── Governance (set at enrich — Action Envelope v2.0) ─────────
    action_envelope: Optional[dict[str, Any]]  # Serialized ActionEnvelope
    policy_decision: Optional[str]             # ALLOW | HITL | BLOCK
    risk_level: Optional[str]                  # L1_SAFE | L2_CAUTION | L3_SENSITIVE
    trust_ring: Optional[str]                  # R0_KERNEL | R1_INTERNAL | R2_USER | R3_UNTRUSTED
