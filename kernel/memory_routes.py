"""
El Monstruo — Memory Routes (Sprint 12)
=========================================
REST API for the persistent thoughts memory system.

Endpoints:
    POST   /v1/memory/thoughts           → Create a thought
    GET    /v1/memory/thoughts            → List thoughts (with filters)
    GET    /v1/memory/thoughts/{id}       → Get single thought
    PATCH  /v1/memory/thoughts/{id}       → Update a thought
    DELETE /v1/memory/thoughts/{id}       → Delete a thought
    POST   /v1/memory/thoughts/{id}/supersede → Supersede a thought
    POST   /v1/memory/search             → Hybrid search
    POST   /v1/memory/search/semantic    → Pure semantic search
    GET    /v1/memory/boot               → Boot sequence
    GET    /v1/memory/stats              → Memory statistics
"""

from __future__ import annotations

from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = structlog.get_logger("memory_routes")

router = APIRouter(prefix="/v1/memory", tags=["memory"])

# ── Module-level dependency (injected at startup) ─────────────────
_thoughts_store = None


def set_dependencies(thoughts_store=None):
    """Inject dependencies from lifespan."""
    global _thoughts_store
    _thoughts_store = thoughts_store


# ── Request/Response Models ───────────────────────────────────────


class CreateThoughtRequest(BaseModel):
    user_id: str = Field(default="anonymous")  # Sprint 29 DT-8
    layer: str = Field(..., description="episodic | semantic | procedural")
    content: str = Field(..., min_length=1, max_length=50000)
    summary: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    importance: int = Field(default=5, ge=1, le=10)
    project: Optional[str] = None
    source: Optional[str] = None
    source_ref: Optional[str] = None
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    parent_id: Optional[str] = None
    procedure_steps: Optional[list[dict]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    generate_embedding: bool = True


class UpdateThoughtRequest(BaseModel):
    content: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[list[str]] = None
    importance: Optional[int] = Field(default=None, ge=1, le=10)
    project: Optional[str] = None
    procedure_steps: Optional[list[dict]] = None
    metadata: Optional[dict[str, Any]] = None


class SupersedeRequest(BaseModel):
    new_content: str = Field(..., min_length=1, max_length=50000)
    new_summary: Optional[str] = None
    new_tags: Optional[list[str]] = None
    new_importance: Optional[int] = Field(default=None, ge=1, le=10)


class SearchRequest(BaseModel):
    user_id: str = Field(default="anonymous")  # Sprint 29 DT-8
    query: str = Field(..., min_length=1, max_length=2000)
    layer: Optional[str] = None
    project: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)
    min_importance: int = Field(default=1, ge=1, le=10)


# ── Routes ────────────────────────────────────────────────────────


@router.post("/thoughts")
async def create_thought(req: CreateThoughtRequest):
    """Create a new thought with optional embedding."""
    if not _thoughts_store:
        raise HTTPException(503, "Thoughts store not initialized")

    result = await _thoughts_store.create(
        user_id=req.user_id,
        layer=req.layer,
        content=req.content,
        summary=req.summary,
        tags=req.tags,
        importance=req.importance,
        project=req.project,
        source=req.source,
        source_ref=req.source_ref,
        session_id=req.session_id,
        agent_id=req.agent_id,
        parent_id=req.parent_id,
        procedure_steps=req.procedure_steps,
        metadata=req.metadata,
        generate_embedding=req.generate_embedding,
    )

    if not result:
        raise HTTPException(500, "Failed to create thought")

    return {"status": "created", "thought": result}


@router.get("/thoughts")
async def list_thoughts(
    user_id: str = Query(default="anonymous")  # Sprint 29 DT-8 FIX,
    layer: Optional[str] = Query(default=None),
    project: Optional[str] = Query(default=None),
    include_superseded: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """List thoughts with optional filters."""
    if not _thoughts_store:
        raise HTTPException(503, "Thoughts store not initialized")

    thoughts = await _thoughts_store.list_thoughts(
        user_id=user_id,
        layer=layer,
        project=project,
        include_superseded=include_superseded,
        limit=limit,
        offset=offset,
    )

    return {"thoughts": thoughts, "count": len(thoughts)}


@router.get("/thoughts/{thought_id}")
async def get_thought(thought_id: str):
    """Get a single thought by ID."""
    if not _thoughts_store:
        raise HTTPException(503, "Thoughts store not initialized")

    thought = await _thoughts_store.get(thought_id)
    if not thought:
        raise HTTPException(404, "Thought not found")

    return {"thought": thought}


@router.patch("/thoughts/{thought_id}")
async def update_thought(thought_id: str, req: UpdateThoughtRequest, user_id: str = Query(default="anonymous")  # Sprint 29 DT-8 FIX):
    """Update a thought. Regenerates embedding if content/summary changed."""
    if not _thoughts_store:
        raise HTTPException(503, "Thoughts store not initialized")

    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "No fields to update")

    result = await _thoughts_store.update(thought_id, user_id, updates)
    if not result:
        raise HTTPException(404, "Thought not found or update failed")

    return {"status": "updated", "thought": result}


@router.delete("/thoughts/{thought_id}")
async def delete_thought(thought_id: str, user_id: str = Query(default="anonymous")  # Sprint 29 DT-8 FIX):
    """Delete a thought."""
    if not _thoughts_store:
        raise HTTPException(503, "Thoughts store not initialized")

    success = await _thoughts_store.delete(thought_id, user_id)
    if not success:
        raise HTTPException(404, "Thought not found or delete failed")

    return {"status": "deleted", "id": thought_id}


@router.post("/thoughts/{thought_id}/supersede")
async def supersede_thought(
    thought_id: str,
    req: SupersedeRequest,
    user_id: str = Query(default="anonymous")  # Sprint 29 DT-8 FIX,
):
    """Supersede an old thought with a new one."""
    if not _thoughts_store:
        raise HTTPException(503, "Thoughts store not initialized")

    new_thought = await _thoughts_store.supersede(
        old_thought_id=thought_id,
        user_id=user_id,
        new_content=req.new_content,
        new_summary=req.new_summary,
        new_tags=req.new_tags,
        new_importance=req.new_importance,
    )

    if not new_thought:
        raise HTTPException(404, "Original thought not found or supersede failed")

    return {"status": "superseded", "old_id": thought_id, "new_thought": new_thought}


@router.post("/search")
async def hybrid_search(req: SearchRequest):
    """Hybrid search (semantic + lexical with RRF fusion)."""
    if not _thoughts_store:
        raise HTTPException(503, "Thoughts store not initialized")

    results = await _thoughts_store.hybrid_search(
        user_id=req.user_id,
        query=req.query,
        layer=req.layer,
        project=req.project,
        limit=req.limit,
        min_importance=req.min_importance,
    )

    return {"results": results, "count": len(results), "query": req.query}


@router.post("/search/semantic")
async def semantic_search(req: SearchRequest):
    """Pure semantic (vector) search."""
    if not _thoughts_store:
        raise HTTPException(503, "Thoughts store not initialized")

    results = await _thoughts_store.semantic_search(
        user_id=req.user_id,
        query=req.query,
        layer=req.layer,
        project=req.project,
        limit=req.limit,
        min_importance=req.min_importance,
    )

    return {"results": results, "count": len(results), "query": req.query}


@router.get("/boot")
async def boot_sequence(
    user_id: str = Query(default="anonymous")  # Sprint 29 DT-8 FIX,
    project: Optional[str] = Query(default=None),
    procedural_limit: int = Query(default=5, ge=1, le=20),
    semantic_limit: int = Query(default=5, ge=1, le=20),
    episodic_limit: int = Query(default=10, ge=1, le=50),
):
    """Boot sequence — load high-priority memories for session start."""
    if not _thoughts_store:
        raise HTTPException(503, "Thoughts store not initialized")

    memories = await _thoughts_store.boot_sequence(
        user_id=user_id,
        project=project,
        procedural_limit=procedural_limit,
        semantic_limit=semantic_limit,
        episodic_limit=episodic_limit,
    )

    return {
        "memories": memories,
        "count": len(memories),
        "layers": {
            "procedural": sum(1 for m in memories if m.get("layer") == "procedural"),
            "semantic": sum(1 for m in memories if m.get("layer") == "semantic"),
            "episodic": sum(1 for m in memories if m.get("layer") == "episodic"),
        },
    }


@router.get("/stats")
async def memory_stats(user_id: str = Query(default="anonymous")  # Sprint 29 DT-8 FIX):
    """Get memory statistics."""
    if not _thoughts_store:
        raise HTTPException(503, "Thoughts store not initialized")

    stats = await _thoughts_store.get_stats(user_id)
    return {"stats": stats}
