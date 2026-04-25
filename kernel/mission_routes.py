"""
El Monstruo — Mission Control Routes (Sprint 9)
=================================================
REST API for managing active missions and user dossier.
Endpoints:
  GET  /missions/         — List missions (filter by status)
  POST /missions/         — Create a new mission
  PUT  /missions/{id}     — Update a mission
  GET  /dossier/          — Get user dossier
  PUT  /dossier/          — Update user dossier
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("monstruo.missions")

router = APIRouter(prefix="/v1/missions", tags=["missions"])
dossier_router = APIRouter(prefix="/v1/dossier", tags=["dossier"])

# ── Dependencies (set by main.py) ────────────────────────────────────
_db = None


def set_dependencies(db: Any) -> None:
    global _db
    _db = db


# ── Pydantic Models ──────────────────────────────────────────────────


class MissionCreate(BaseModel):
    name: str
    description: str = ""
    priority: int = Field(default=5, ge=1, le=10)
    tags: list[str] = []
    metadata: dict = {}


class MissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=1, le=10)
    tags: Optional[list[str]] = None


class DossierUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    role: Optional[str] = None
    industry: Optional[str] = None
    email: Optional[str] = None
    github_username: Optional[str] = None
    telegram_id: Optional[str] = None
    timezone: Optional[str] = None
    communication_prefs: Optional[dict] = None
    context: Optional[dict] = None
    custom_fields: Optional[dict] = None


# ── Mission Endpoints ─────────────────────────────────────────────────


@router.get("/")
async def list_missions(status: str = "active", user_id: str = "anonymous"):
    """List missions filtered by status."""
    if not _db:
        raise HTTPException(503, "Database not available")

    filters = {"user_id": user_id}
    if status != "all":
        filters["status"] = status

    rows = await _db.select("active_missions", filters=filters, limit=50)
    missions = []
    for row in rows:
        missions.append(
            {
                "id": row.get("id"),
                "name": row.get("name"),
                "description": row.get("description"),
                "status": row.get("status"),
                "priority": row.get("priority"),
                "tags": row.get("tags", []),
                "metadata": row.get("metadata", {}),
                "started_at": str(row.get("started_at", "")),
                "updated_at": str(row.get("updated_at", "")),
            }
        )

    # Sort by priority descending
    missions.sort(key=lambda m: m.get("priority", 0), reverse=True)
    return {"missions": missions, "count": len(missions)}


@router.post("/")
async def create_mission(body: MissionCreate, user_id: str = "anonymous"):
    """Create a new active mission."""
    if not _db:
        raise HTTPException(503, "Database not available")

    data = {
        "user_id": user_id,
        "name": body.name,
        "description": body.description,
        "status": "active",
        "priority": body.priority,
        "tags": body.tags,
        "metadata": json.dumps(body.metadata),
    }

    result = await _db.insert("active_missions", data)
    if result:
        logger.info("mission_created_via_api", name=body.name)
        return {"success": True, "mission": result}
    raise HTTPException(500, "Failed to create mission")


@router.put("/{mission_id}")
async def update_mission(mission_id: str, body: MissionUpdate):
    """Update an existing mission."""
    if not _db:
        raise HTTPException(503, "Database not available")

    updates = {}
    for field in ("name", "description", "status", "priority", "tags"):
        val = getattr(body, field, None)
        if val is not None:
            updates[field] = val

    if body.status == "paused":
        updates["paused_at"] = "now()"
    elif body.status == "completed":
        updates["completed_at"] = "now()"

    if not updates:
        raise HTTPException(400, "No fields to update")

    result = await _db.update("active_missions", updates, filters={"id": mission_id})
    if result:
        logger.info("mission_updated_via_api", id=mission_id)
        return {"success": True, "updated_fields": list(updates.keys())}
    raise HTTPException(404, "Mission not found")


# ── Dossier Endpoints ─────────────────────────────────────────────────


@dossier_router.get("/")
async def get_dossier(user_id: str = "anonymous"):
    """Get the user dossier."""
    if not _db:
        raise HTTPException(503, "Database not available")

    rows = await _db.select("user_dossier", filters={"user_id": user_id}, limit=1)
    if not rows:
        raise HTTPException(404, f"No dossier for user '{user_id}'")

    d = rows[0]
    return {
        "user_id": d.get("user_id"),
        "full_name": d.get("full_name"),
        "company": d.get("company"),
        "rfc": d.get("rfc"),
        "location": d.get("location"),
        "role": d.get("role"),
        "industry": d.get("industry"),
        "timezone": d.get("timezone"),
        "email": d.get("email"),
        "github_username": d.get("github_username"),
        "telegram_id": d.get("telegram_id"),
        "communication_prefs": d.get("communication_prefs"),
        "context": d.get("context"),
        "custom_fields": d.get("custom_fields"),
        "updated_at": str(d.get("updated_at", "")),
    }


@dossier_router.put("/")
async def update_dossier(body: DossierUpdate, user_id: str = "anonymous"):
    """Update the user dossier."""
    if not _db:
        raise HTTPException(503, "Database not available")

    updates = {}
    for field in (
        "full_name",
        "company",
        "location",
        "role",
        "industry",
        "email",
        "github_username",
        "telegram_id",
        "timezone",
    ):
        val = getattr(body, field, None)
        if val is not None:
            updates[field] = val

    # Handle JSONB merge fields
    for jsonb_field in ("communication_prefs", "context", "custom_fields"):
        val = getattr(body, jsonb_field, None)
        if val is not None and isinstance(val, dict):
            rows = await _db.select("user_dossier", filters={"user_id": user_id}, limit=1)
            if rows:
                current = rows[0].get(jsonb_field) or {}
                if isinstance(current, str):
                    current = json.loads(current)
                current.update(val)
                updates[jsonb_field] = json.dumps(current)

    if not updates:
        raise HTTPException(400, "No fields to update")

    result = await _db.update("user_dossier", updates, filters={"user_id": user_id})
    if result:
        logger.info("dossier_updated_via_api", fields=list(updates.keys()))
        return {"success": True, "updated_fields": list(updates.keys())}
    raise HTTPException(404, "Dossier not found")
