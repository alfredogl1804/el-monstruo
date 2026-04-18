"""
El Monstruo — User Dossier Tool (Sprint 9)
============================================
Allows the LLM to read and update the user's persistent profile (dossier)
and manage active missions. Also provides a formatted dossier string for
injection into system prompts.

Actions:
  - get_dossier: Read the full user profile
  - update_dossier: Update specific fields in the profile
  - list_missions: List active missions
  - update_mission: Update a mission's status/priority
  - create_mission: Create a new mission
  - get_prompt_dossier: Get formatted dossier for system prompt injection
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger("monstruo.tools.user_dossier")

# Module-level DB reference (set by set_tool_db in tool_dispatch)
_db = None


def set_db(db):
    global _db
    _db = db


async def execute(action: str, args: dict[str, Any], db=None) -> str:
    """Execute a user_dossier action."""
    effective_db = db or _db
    if not effective_db:
        return json.dumps({"error": "Database not available. Cannot access user dossier."})

    user_id = args.get("user_id", "alfredo")

    try:
        if action == "get_dossier":
            return await _get_dossier(effective_db, user_id)
        elif action == "update_dossier":
            return await _update_dossier(effective_db, user_id, args)
        elif action == "list_missions":
            return await _list_missions(effective_db, user_id, args.get("status", "active"))
        elif action == "update_mission":
            return await _update_mission(effective_db, args)
        elif action == "create_mission":
            return await _create_mission(effective_db, user_id, args)
        elif action == "get_prompt_dossier":
            return await get_prompt_dossier(effective_db, user_id)
        else:
            return json.dumps({"error": f"Unknown action: {action}"})
    except Exception as e:
        logger.error("user_dossier_error", action=action, error=str(e))
        return json.dumps({"error": str(e)})


async def _get_dossier(db, user_id: str) -> str:
    """Get the full user dossier."""
    rows = await db.select("user_dossier", filters={"user_id": user_id}, limit=1)
    if not rows:
        return json.dumps({"error": f"No dossier found for user '{user_id}'"})

    dossier = rows[0]
    # Clean up for display
    result = {
        "user_id": dossier.get("user_id"),
        "full_name": dossier.get("full_name"),
        "company": dossier.get("company"),
        "rfc": dossier.get("rfc"),
        "location": dossier.get("location"),
        "role": dossier.get("role"),
        "industry": dossier.get("industry"),
        "timezone": dossier.get("timezone"),
        "email": dossier.get("email"),
        "github_username": dossier.get("github_username"),
        "telegram_id": dossier.get("telegram_id"),
        "communication_prefs": dossier.get("communication_prefs"),
        "context": dossier.get("context"),
        "custom_fields": dossier.get("custom_fields"),
        "updated_at": str(dossier.get("updated_at", "")),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


async def _update_dossier(db, user_id: str, args: dict) -> str:
    """Update specific fields in the user dossier."""
    # Allowed top-level fields
    allowed_fields = {
        "full_name", "company", "rfc", "location", "role", "industry",
        "timezone", "email", "github_username", "telegram_id", "phone",
    }

    updates = {}
    for key, value in args.items():
        if key in allowed_fields:
            updates[key] = value

    # Handle JSONB fields (merge, don't replace)
    for jsonb_field in ("communication_prefs", "context", "custom_fields"):
        if jsonb_field in args and isinstance(args[jsonb_field], dict):
            # Fetch current value, merge
            rows = await db.select("user_dossier", filters={"user_id": user_id}, limit=1)
            if rows:
                current = rows[0].get(jsonb_field) or {}
                if isinstance(current, str):
                    current = json.loads(current)
                current.update(args[jsonb_field])
                updates[jsonb_field] = json.dumps(current)

    if not updates:
        return json.dumps({"error": "No valid fields to update. Allowed: " + ", ".join(sorted(allowed_fields | {"communication_prefs", "context", "custom_fields"}))})

    result = await db.update("user_dossier", updates, filters={"user_id": user_id})
    if result:
        logger.info("dossier_updated", user_id=user_id, fields=list(updates.keys()))
        return json.dumps({"success": True, "updated_fields": list(updates.keys())}, ensure_ascii=False)
    else:
        return json.dumps({"error": "Update failed — user not found or no changes made"})


async def _list_missions(db, user_id: str, status: str = "active") -> str:
    """List missions filtered by status."""
    filters = {"user_id": user_id}
    if status != "all":
        filters["status"] = status

    rows = await db.select("active_missions", filters=filters, limit=20)
    missions = []
    for row in rows:
        missions.append({
            "id": row.get("id"),
            "name": row.get("name"),
            "description": row.get("description"),
            "status": row.get("status"),
            "priority": row.get("priority"),
            "tags": row.get("tags", []),
            "started_at": str(row.get("started_at", "")),
        })

    # Sort by priority descending
    missions.sort(key=lambda m: m.get("priority", 0), reverse=True)
    return json.dumps({"missions": missions, "count": len(missions)}, ensure_ascii=False, indent=2)


async def _update_mission(db, args: dict) -> str:
    """Update a mission's status, priority, or description."""
    mission_id = args.get("mission_id")
    mission_name = args.get("mission_name")

    if not mission_id and not mission_name:
        return json.dumps({"error": "Provide mission_id or mission_name to identify the mission"})

    updates = {}
    for field in ("status", "priority", "description", "name"):
        if field in args and field not in ("mission_id", "mission_name"):
            updates[field] = args[field]

    # Handle status transitions
    if "status" in updates:
        if updates["status"] == "paused":
            updates["paused_at"] = "now()"
        elif updates["status"] == "completed":
            updates["completed_at"] = "now()"

    if not updates:
        return json.dumps({"error": "No fields to update. Provide status, priority, description, or name."})

    if mission_id:
        result = await db.update("active_missions", updates, filters={"id": mission_id})
    else:
        result = await db.update("active_missions", updates, filters={"name": mission_name})

    if result:
        logger.info("mission_updated", mission=mission_name or mission_id, fields=list(updates.keys()))
        return json.dumps({"success": True, "updated_fields": list(updates.keys())}, ensure_ascii=False)
    else:
        return json.dumps({"error": "Mission not found or no changes made"})


async def _create_mission(db, user_id: str, args: dict) -> str:
    """Create a new active mission."""
    name = args.get("name")
    if not name:
        return json.dumps({"error": "Mission name is required"})

    data = {
        "user_id": user_id,
        "name": name,
        "description": args.get("description", ""),
        "status": "active",
        "priority": args.get("priority", 5),
        "tags": args.get("tags", []),
        "metadata": json.dumps(args.get("metadata", {})),
    }

    result = await db.insert("active_missions", data)
    if result:
        logger.info("mission_created", name=name, user_id=user_id)
        return json.dumps({"success": True, "mission_id": result.get("id"), "name": name}, ensure_ascii=False)
    else:
        return json.dumps({"error": "Failed to create mission"})


async def get_prompt_dossier(db, user_id: str = "alfredo") -> str:
    """
    Build a formatted dossier string for injection into system prompts.
    This replaces the hardcoded USER_DOSSIER in prompts/system_prompts.py.
    Returns a Markdown-formatted string ready for prompt injection.
    """
    try:
        rows = await db.select("user_dossier", filters={"user_id": user_id}, limit=1)
        if not rows:
            # Fallback to hardcoded dossier
            from prompts.system_prompts import USER_DOSSIER
            return USER_DOSSIER

        d = rows[0]
        prefs = d.get("communication_prefs") or {}
        if isinstance(prefs, str):
            prefs = json.loads(prefs)
        ctx = d.get("context") or {}
        if isinstance(ctx, str):
            ctx = json.loads(ctx)

        # Build missions section
        missions_text = ""
        try:
            mission_rows = await db.select(
                "active_missions",
                filters={"user_id": user_id, "status": "active"},
                limit=10
            )
            if mission_rows:
                sorted_missions = sorted(mission_rows, key=lambda m: m.get("priority", 0), reverse=True)
                missions_lines = []
                for m in sorted_missions:
                    tags = ", ".join(m.get("tags", []))
                    missions_lines.append(f"- **{m['name']}** (P{m.get('priority', 5)}) — {m.get('description', '')}" + (f" [{tags}]" if tags else ""))
                missions_text = "\n".join(missions_lines)
        except Exception:
            missions_text = "No se pudieron cargar las misiones activas."

        # Build formatted dossier
        dossier = f"""## Dossier del Usuario Principal (Dinámico)
**Nombre:** {d.get('full_name', 'Desconocido')}
**Empresa:** {d.get('company', '')}
**Ubicación:** {d.get('location', '')}
**Rol:** {d.get('role', '')}
**Industria:** {d.get('industry', '')}
**Timezone:** {d.get('timezone', 'America/Merida')}
**Email:** {d.get('email', '')}
**GitHub:** {d.get('github_username', '')}

**Preferencias de comunicación:**
- Idioma: {prefs.get('language', 'es-MX')}
- Formato preferido: {prefs.get('format', 'bullet_points')}
- Estilo: {prefs.get('style', 'direct')}
- Incluir en propuestas: {', '.join(prefs.get('include_in_proposals', ['cost', 'time', 'risk']))}
- Horario de trabajo: {prefs.get('working_hours', '07:00-23:00 CST')}

**Misiones activas:**
{missions_text or 'Sin misiones activas registradas.'}

**Contexto operativo:**
- Gestiona múltiples empresas y proyectos simultáneamente
- Usa IA como multiplicador de capacidad (no como reemplazo)
- Prefiere respuestas directas, sin rodeos, con datos concretos
- Valora la velocidad de ejecución sobre la perfección teórica"""

        return dossier

    except Exception as e:
        logger.error("get_prompt_dossier_error", error=str(e))
        # Fallback to hardcoded
        from prompts.system_prompts import USER_DOSSIER
        return USER_DOSSIER
