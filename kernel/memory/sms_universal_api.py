"""
kernel/memory/sms_universal_api.py — Universal Multi-Agent API for SMS

A lightweight FastAPI service that exposes the Sovereign Memory System to ANY AI:
- ChatGPT (via Custom GPT Actions / API calls)
- Claude (via tool_use / MCP)
- Gemini (via function calling)
- Grok (via API)
- Manus (via direct import or HTTP)
- Any custom agent with HTTP access

Endpoints:
  POST /sms/ingest       — Store a new memory
  POST /sms/recall       — Semantic search over memories
  POST /sms/crystallize  — Promote a memory to axiom
  GET  /sms/axioms       — Get all sovereign axioms
  GET  /sms/context      — Get context injection block (for session start)
  POST /sms/validate     — Validate/confirm an axiom
  POST /sms/conflict     — Report a contradiction
  GET  /sms/gaps         — Get unresolved knowledge gaps
  POST /sms/gap/resolve  — Mark a gap as resolved
  GET  /sms/health       — System health check
  POST /sms/register     — Register a new agent

Authentication: Bearer token (SMS_API_KEY env var)
Agent identification: X-Agent-ID header or agent_id in body

Author: Manus C (Batch 011 — SMS Universal)
Date: 2026-05-21
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Optional

# Add parent paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import BackgroundTasks, FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from kernel.memory.sms_supabase_adapter import SMSSupabaseAdapter, SMSConfig

logger = logging.getLogger("monstruo.sms.api")

# ═══════════════════════════════════════════════════════════════════════════════
# APP CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Sovereign Memory System — Universal API",
    description=(
        "Universal memory persistence for AI agents. "
        "Any LLM (ChatGPT, Claude, Gemini, Grok, Manus) can read/write sovereign memories."
    ),
    version="1.0.0",
    docs_url="/sms/docs",
    redoc_url="/sms/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global adapter
_adapter: Optional[SMSSupabaseAdapter] = None


def get_adapter() -> SMSSupabaseAdapter:
    global _adapter
    if _adapter is None:
        _adapter = SMSSupabaseAdapter()
    return _adapter


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════

SMS_API_KEY = os.environ.get("SMS_API_KEY", "")


async def verify_auth(authorization: str = Header(None), x_api_key: str = Header(None, alias="X-Api-Key")):
    """Verify Bearer token or X-Api-Key header."""
    if not SMS_API_KEY:
        return  # No auth configured = open (dev mode)

    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    elif x_api_key:
        token = x_api_key

    if token != SMS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def get_agent_id(request: Request, body_agent: str = None) -> str:
    """Extract agent_id from X-Agent-ID header or body."""
    header_agent = request.headers.get("X-Agent-ID")
    return header_agent or body_agent or "unknown"


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class IngestRequest(BaseModel):
    content: str = Field(..., description="The memory content to store")
    memory_type: str = Field("episodic", description="episodic|semantic|procedural|causal")
    source: str = Field("agent", description="Where this memory came from")
    agent_id: Optional[str] = Field(None, description="Agent storing the memory")
    confidence: float = Field(0.7, ge=0, le=1)
    causal_parent_id: Optional[str] = Field(None, description="ID of causal parent memory")
    tags: list[str] = Field(default_factory=list)


class RecallRequest(BaseModel):
    query: str = Field(..., description="Semantic search query")
    agent_id: Optional[str] = Field(None, description="Filter by agent")
    memory_type: Optional[str] = Field(None, description="Filter by type")
    threshold: float = Field(0.65, ge=0, le=1)
    limit: int = Field(10, ge=1, le=50)


class CrystallizeRequest(BaseModel):
    statement: str = Field(..., description="The axiom statement to crystallize")
    confidence: float = Field(1.0, ge=0, le=1)
    implications: list[str] = Field(default_factory=list)
    agent_id: Optional[str] = Field(None)
    tags: list[str] = Field(default_factory=list)


class ValidateRequest(BaseModel):
    axiom_id: str = Field(..., description="UUID of the axiom to validate")


class ConflictRequest(BaseModel):
    claim_a: str = Field(..., description="First claim")
    claim_b: str = Field(..., description="Contradicting claim")
    agent_id: Optional[str] = Field(None)


class ResolveGapRequest(BaseModel):
    gap_id: str = Field(..., description="UUID of the gap to resolve")
    resolved_by_memory_id: Optional[str] = Field(None)


class RegisterAgentRequest(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_name: str = Field(..., description="Human-readable name")
    agent_type: str = Field("llm", description="llm|human|system|tool")
    provider: str = Field("custom", description="manus|openai|anthropic|google|xai|custom")
    model: Optional[str] = Field(None)
    permissions: dict = Field(
        default_factory=lambda: {"read": True, "write": True, "crystallize": False, "forget": False}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/sms/ingest", dependencies=[Depends(verify_auth)])
async def ingest_memory(request: Request, body: IngestRequest):
    """
    Store a new memory in the Sovereign Memory System.
    
    Any AI agent can call this to persist knowledge that survives across sessions.
    Automatically generates embeddings and deduplicates.
    """
    adapter = get_adapter()
    agent = get_agent_id(request, body.agent_id)

    # Permission check
    if not adapter.check_permission(agent, "write"):
        # If agent not registered, allow with default perms (auto-register)
        adapter.register_agent(agent, f"Auto-registered: {agent}", "llm", "custom")

    result = adapter.store_memory(
        content=body.content,
        memory_type=body.memory_type,
        source=body.source,
        agent_id=agent,
        confidence=body.confidence,
        causal_parent_id=body.causal_parent_id,
        tags=body.tags,
    )

    if result:
        return {"status": "stored", "memory_id": result.get("id"), "agent_id": agent}
    return {"status": "degraded", "reason": "storage_unavailable"}


@app.post("/sms/recall", dependencies=[Depends(verify_auth)])
async def recall_memories(request: Request, body: RecallRequest):
    """
    Semantic search over all memories.
    
    Returns the most relevant memories for the given query.
    Can filter by agent_id to get only your own memories, or leave empty for global search.
    """
    adapter = get_adapter()
    agent = get_agent_id(request, body.agent_id)

    results = adapter.search_memories_semantic(
        query=body.query,
        threshold=body.threshold,
        limit=body.limit,
        agent_filter=body.agent_id,  # None = search all agents
        type_filter=body.memory_type,
    )

    return {
        "query": body.query,
        "results": results,
        "count": len(results),
        "agent_id": agent,
    }


@app.post("/sms/crystallize", dependencies=[Depends(verify_auth)])
async def crystallize_axiom(request: Request, body: CrystallizeRequest):
    """
    Promote an understanding to a Sovereign Axiom.
    
    Axioms are compaction-proof: they NEVER decay and are always injected
    into context at session start. Only agents with 'crystallize' permission
    can create axioms (by default: monstruo and alfredo_t1).
    """
    adapter = get_adapter()
    agent = get_agent_id(request, body.agent_id)

    if not adapter.check_permission(agent, "crystallize"):
        raise HTTPException(
            status_code=403,
            detail=f"Agent '{agent}' lacks 'crystallize' permission. Only T1/Monstruo can create axioms.",
        )

    result = adapter.upsert_axiom(
        statement=body.statement,
        confidence=body.confidence,
        implications=body.implications,
        source_agent=agent,
        tags=body.tags,
    )

    if result:
        return {"status": "crystallized", "axiom_id": result.get("id"), "statement": body.statement}
    return {"status": "degraded", "reason": "storage_unavailable"}


@app.get("/sms/axioms", dependencies=[Depends(verify_auth)])
async def get_axioms(
    request: Request,
    agent_id: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 50,
):
    """
    Get sovereign axioms.
    
    If query is provided, returns semantically similar axioms.
    Otherwise returns all active axioms (optionally filtered by agent).
    """
    adapter = get_adapter()

    if query:
        results = adapter.search_axioms_semantic(query, limit=limit, agent_filter=agent_id)
    else:
        results = adapter.get_axioms(source_agent=agent_id, limit=limit)

    return {"axioms": results, "count": len(results)}


@app.get("/sms/context", dependencies=[Depends(verify_auth)])
async def get_context(
    request: Request,
    agent_id: Optional[str] = None,
    query: Optional[str] = None,
):
    """
    Get the context injection block for session start.
    
    This is THE key endpoint. Call this at the beginning of every session
    to receive sovereign axioms, relevant memories, and knowledge gaps.
    Inject the response directly into your system prompt.
    
    Works for ANY AI: ChatGPT, Claude, Gemini, Grok, Manus, custom.
    """
    adapter = get_adapter()
    agent = agent_id or get_agent_id(request)

    injection = adapter.get_context_injection(
        agent_id=agent,
        query=query,
    )

    return {
        "agent_id": agent,
        "context_block": injection,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "instruction": "Inject this block into your system prompt at session start. These are sovereign truths that must not be contradicted.",
    }


@app.post("/sms/validate", dependencies=[Depends(verify_auth)])
async def validate_axiom(request: Request, body: ValidateRequest):
    """Validate (confirm) an axiom. Increases its confidence."""
    adapter = get_adapter()
    success = adapter.validate_axiom(body.axiom_id)
    return {"status": "validated" if success else "failed", "axiom_id": body.axiom_id}


@app.post("/sms/conflict", dependencies=[Depends(verify_auth)])
async def report_conflict(request: Request, body: ConflictRequest):
    """
    Report a contradiction between two claims.
    
    The system will resolve based on confidence, validation count, and source.
    """
    adapter = get_adapter()
    agent = get_agent_id(request, body.agent_id)

    # Store both claims as memories, then resolve
    mem_a = adapter.store_memory(body.claim_a, source="conflict", agent_id=agent)
    mem_b = adapter.store_memory(body.claim_b, source="conflict", agent_id=agent)

    if mem_a and mem_b:
        adapter.log_conflict(
            memory_a_id=mem_a.get("id", ""),
            memory_b_id=mem_b.get("id", ""),
            winner_id=mem_a.get("id", ""),  # Default: first claim wins (needs semantic analysis)
            reason="First claim has priority (manual review recommended)",
            resolved_by=agent,
        )
        return {
            "status": "logged",
            "resolution": "first_claim_priority",
            "note": "Manual review recommended for definitive resolution",
        }

    return {"status": "degraded", "reason": "storage_unavailable"}


@app.get("/sms/gaps", dependencies=[Depends(verify_auth)])
async def get_gaps(request: Request, agent_id: Optional[str] = None, limit: int = 20):
    """Get unresolved knowledge gaps."""
    adapter = get_adapter()
    gaps = adapter.get_unresolved_gaps(agent_id=agent_id, limit=limit)
    return {"gaps": gaps, "count": len(gaps)}


@app.post("/sms/gap/resolve", dependencies=[Depends(verify_auth)])
async def resolve_gap(request: Request, body: ResolveGapRequest):
    """Mark a knowledge gap as resolved."""
    adapter = get_adapter()
    success = adapter.resolve_gap(body.gap_id, body.resolved_by_memory_id)
    return {"status": "resolved" if success else "failed", "gap_id": body.gap_id}


@app.get("/sms/health", dependencies=[Depends(verify_auth)])
async def health_check():
    """System health check."""
    adapter = get_adapter()
    health = adapter.get_health()
    return health


@app.post("/sms/register", dependencies=[Depends(verify_auth)])
async def register_agent(request: Request, body: RegisterAgentRequest):
    """
    Register a new AI agent in the universal registry.
    
    Once registered, the agent can read/write memories based on its permissions.
    Default permissions: read=true, write=true, crystallize=false, forget=false.
    """
    adapter = get_adapter()
    result = adapter.register_agent(
        agent_id=body.agent_id,
        agent_name=body.agent_name,
        agent_type=body.agent_type,
        provider=body.provider,
        model=body.model,
        permissions=body.permissions,
    )

    if result:
        return {"status": "registered", "agent_id": body.agent_id}
    return {"status": "degraded", "reason": "storage_unavailable"}


# ═══════════════════════════════════════════════════════════════════════════════
# REM CYCLE (Nightly Consolidation)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/sms/rem-cycle", dependencies=[Depends(verify_auth)])
async def trigger_rem_cycle(background_tasks: BackgroundTasks):
    """
    Trigger the REM Cycle (nightly memory consolidation).

    Runs in background: decay, crystallize, deduplicate, forget, detect gaps,
    resolve conflicts, and log stats. Inspired by biological REM sleep.

    Can be triggered by:
    - Railway cron job (daily at 3:00 AM CST)
    - Manus scheduled task
    - Manual invocation
    """
    try:
        from kernel.memory.sms_rem_cycle import run_sms_rem_cycle
        background_tasks.add_task(run_sms_rem_cycle)
        return {"status": "triggered", "message": "REM Cycle started in background"}
    except ImportError as e:
        return {"status": "error", "message": f"REM Cycle module not available: {e}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# OPENAPI SPEC EXPORT (for ChatGPT Custom GPT Actions)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/sms/openapi.json")
async def get_openapi_spec():
    """
    Export OpenAPI spec for integration with ChatGPT Custom GPT Actions.
    
    Use this URL as the Actions schema URL in your Custom GPT configuration.
    """
    return app.openapi()


# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("SMS_PORT", "8100"))
    print(f"Starting SMS Universal API on port {port}...")
    print(f"Docs: http://localhost:{port}/sms/docs")
    print(f"OpenAPI: http://localhost:{port}/sms/openapi.json")
    uvicorn.run(app, host="0.0.0.0", port=port)
