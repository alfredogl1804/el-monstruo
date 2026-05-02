"""
El Monstruo — A2A Protocol Routes (Sprint 55.2)
================================================
Endpoints REST para el protocolo A2A:
  GET  /v1/a2a/agents           → Listar todos los agentes registrados
  POST /v1/a2a/register         → Registrar un agente externo
  POST /v1/a2a/discover         → Buscar agentes por capacidad
  POST /v1/a2a/heartbeat        → Actualizar heartbeat
  GET  /v1/a2a/stats            → Estadísticas del registry

El endpoint /.well-known/agent.json está en main.py (raíz de la app).
"""

from __future__ import annotations

from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = structlog.get_logger("kernel.a2a_routes")

router = APIRouter(prefix="/v1/a2a", tags=["a2a"])

# Dependency injection — se inyecta desde main.py
_registry = None


def set_registry(registry) -> None:
    """Inyectar el A2ARegistry en los routes."""
    global _registry
    _registry = registry


# ── Request Models ──────────────────────────────────────────────


class RegisterRequest(BaseModel):
    name: str
    description: str
    capabilities: list[str] = []
    role: str = "general"
    endpoint: Optional[str] = None
    input_modes: list[str] = ["text/plain"]
    output_modes: list[str] = ["text/plain"]


class DiscoverRequest(BaseModel):
    capability: Optional[str] = None
    role: Optional[str] = None
    status: str = "active"


class HeartbeatRequest(BaseModel):
    agent_id: str


# ── Endpoints ──────────────────────────────────────────────────


@router.get("/agents")
async def list_agents() -> dict[str, Any]:
    """Listar todos los agentes registrados en el A2A Registry."""
    if not _registry:
        raise HTTPException(503, "A2A Registry not initialized")
    return {
        "agents": _registry.get_all_cards(),
        "stats": _registry.get_stats(),
    }


@router.post("/register")
async def register_agent(req: RegisterRequest) -> dict[str, Any]:
    """
    Registrar un agente externo en el registry.
    T5: Agente externo puede registrarse vía este endpoint.
    """
    if not _registry:
        raise HTTPException(503, "A2A Registry not initialized")

    from uuid import uuid4

    from kernel.a2a_registry import AgentCard

    card = AgentCard(
        agent_id=str(uuid4()),
        name=req.name,
        description=req.description,
        capabilities=req.capabilities,
        role=req.role,
        endpoint=req.endpoint,
        input_modes=req.input_modes,
        output_modes=req.output_modes,
    )

    agent_id = await _registry.register(card)
    logger.info("a2a_external_agent_registered", agent_id=agent_id, name=req.name)
    return {"agent_id": agent_id, "card": card.to_dict()}


@router.post("/discover")
async def discover_agents(req: DiscoverRequest) -> dict[str, Any]:
    """
    Descubrir agentes por capacidad o rol.
    T3: POST /v1/a2a/discover con capability retorna agentes que la tienen.
    """
    if not _registry:
        raise HTTPException(503, "A2A Registry not initialized")

    agents = await _registry.discover(
        capability=req.capability,
        role=req.role,
        status=req.status,
    )
    return {
        "agents": [a.to_dict() for a in agents],
        "count": len(agents),
        "filters": {
            "capability": req.capability,
            "role": req.role,
            "status": req.status,
        },
    }


@router.post("/heartbeat")
async def agent_heartbeat(req: HeartbeatRequest) -> dict[str, Any]:
    """
    Actualizar heartbeat de un agente.
    T4: Heartbeat actualiza timestamp y detecta agentes inactivos.
    """
    if not _registry:
        raise HTTPException(503, "A2A Registry not initialized")

    success = await _registry.heartbeat(req.agent_id)
    if not success:
        raise HTTPException(404, f"Agent {req.agent_id} not found in registry")

    # Marcar stale como idle (>5min sin heartbeat)
    stale_count = await _registry.mark_stale_offline(max_silence_minutes=5)

    return {
        "success": True,
        "agent_id": req.agent_id,
        "stale_agents_marked_idle": stale_count,
    }


@router.get("/stats")
async def registry_stats() -> dict[str, Any]:
    """Estadísticas del A2A Registry."""
    if not _registry:
        raise HTTPException(503, "A2A Registry not initialized")
    return _registry.get_stats()


@router.delete("/agents/{agent_id}")
async def deregister_agent(agent_id: str) -> dict[str, Any]:
    """Marcar un agente como offline (deregistrar)."""
    if not _registry:
        raise HTTPException(503, "A2A Registry not initialized")

    success = await _registry.deregister(agent_id)
    if not success:
        raise HTTPException(404, f"Agent {agent_id} not found in registry")

    return {"success": True, "agent_id": agent_id, "status": "offline"}
