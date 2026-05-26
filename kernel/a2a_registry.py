"""
El Monstruo — A2A Agent Registry (Sprint 55.2)
===============================================
Registro dinámico de agentes A2A compliant.
Cada Embrión se registra con un Agent Card que describe:
  - Nombre, rol, capacidades
  - Inputs que acepta, outputs que produce
  - Endpoint de comunicación
  - Estado de salud

Otros agentes (internos o externos) pueden:
  - Descubrir Embriones por capacidad
  - Enviar tareas a Embriones específicos
  - Recibir resultados asíncronos

Validated: a2a-sdk==1.0.2 (Google LLC, Apache 2.0, Apr 24, 2026)
A2A Protocol Spec v1.0 — JSON-RPC transport
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.a2a_registry")


@dataclass
class AgentCard:
    """
    A2A Agent Card — describe las capacidades de un agente.
    Spec: https://google.github.io/A2A/specification/
    """

    agent_id: str
    name: str
    description: str
    version: str = "1.0.0"

    # Capacidades
    capabilities: list = field(default_factory=list)
    input_modes: list = field(default_factory=lambda: ["text/plain"])
    output_modes: list = field(default_factory=lambda: ["text/plain"])

    # Comunicación
    endpoint: Optional[str] = None  # URL para comunicación directa
    protocol: str = "a2a/1.0"

    # Metadata
    role: str = "general"
    status: str = "active"  # active, idle, busy, offline
    last_heartbeat: Optional[str] = None
    registered_at: Optional[str] = None

    # Auth
    auth_schemes: list = field(default_factory=lambda: ["bearer"])

    def to_dict(self) -> dict[str, Any]:
        """Serializar a dict para persistencia y discovery."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": self.capabilities,
            "input_modes": self.input_modes,
            "output_modes": self.output_modes,
            "endpoint": self.endpoint,
            "protocol": self.protocol,
            "role": self.role,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat,
            "registered_at": self.registered_at,
            "auth_schemes": self.auth_schemes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentCard":
        """Deserializar desde dict."""
        valid_fields = {
            "agent_id",
            "name",
            "description",
            "version",
            "capabilities",
            "input_modes",
            "output_modes",
            "endpoint",
            "protocol",
            "role",
            "status",
            "last_heartbeat",
            "registered_at",
            "auth_schemes",
        }
        return cls(**{k: v for k, v in data.items() if k in valid_fields})


class A2ARegistry:
    """
    Registro central de agentes A2A.
    Persistido en Supabase tabla `a2a_agents`.
    In-memory cache para discovery rápido.
    """

    def __init__(self, db=None):
        self._db = db  # memory.supabase_client instance
        self._agents: dict[str, AgentCard] = {}  # agent_id → AgentCard
        self._initialized = False

    async def initialize(self) -> None:
        """Cargar agentes registrados desde Supabase."""
        if not self._db:
            logger.warning("a2a_registry_no_db", hint="Running in memory-only mode")
            self._initialized = True
            return

        try:
            rows = await self._db.select("a2a_agents", filters={"status": "active"})
            for row in rows:
                card_data = row.get("card_data", {})
                if not card_data.get("agent_id"):
                    card_data["agent_id"] = row["id"]
                if not card_data.get("name"):
                    card_data["name"] = row.get("name", "unknown")
                if not card_data.get("description"):
                    card_data["description"] = ""
                card = AgentCard.from_dict(card_data)
                self._agents[card.agent_id] = card

            logger.info("a2a_registry_loaded", agents=len(self._agents))
            self._initialized = True
        except Exception as e:
            logger.error("a2a_registry_load_failed", error=str(e))
            self._initialized = True  # Funcionar en modo degradado

    async def register(self, card: AgentCard) -> str:
        """
        Registrar un agente en el registry.
        Si ya existe (mismo agent_id), actualiza.
        """
        now = datetime.now(timezone.utc).isoformat()
        card.registered_at = now
        card.last_heartbeat = now

        self._agents[card.agent_id] = card

        if self._db:
            try:
                await self._db.upsert(
                    "a2a_agents",
                    {
                        "id": card.agent_id,
                        "name": card.name,
                        "role": card.role,
                        "status": card.status,
                        "card_data": card.to_dict(),
                        "registered_at": card.registered_at,
                        "last_heartbeat": card.last_heartbeat,
                    },
                )
            except Exception as e:
                logger.warning("a2a_register_persist_failed", error=str(e))

        logger.info("a2a_agent_registered", agent_id=card.agent_id, name=card.name, role=card.role)
        return card.agent_id

    async def discover(
        self,
        capability: Optional[str] = None,
        role: Optional[str] = None,
        status: str = "active",
    ) -> list[AgentCard]:
        """
        Descubrir agentes por capacidad, rol, o estado.
        Retorna Agent Cards que matchean los filtros.
        """
        results = []
        for card in self._agents.values():
            if card.status != status:
                continue
            if capability and capability not in card.capabilities:
                continue
            if role and card.role != role:
                continue
            results.append(card)

        return results

    async def heartbeat(self, agent_id: str) -> bool:
        """Actualizar heartbeat de un agente."""
        if agent_id not in self._agents:
            return False

        now = datetime.now(timezone.utc).isoformat()
        self._agents[agent_id].last_heartbeat = now

        if self._db:
            try:
                await self._db.update(
                    "a2a_agents",
                    {"last_heartbeat": now},
                    filters={"id": agent_id},
                )
            except Exception as e:
                logger.warning("a2a_heartbeat_persist_failed", error=str(e))
        return True

    async def deregister(self, agent_id: str) -> bool:
        """Marcar un agente como offline."""
        if agent_id not in self._agents:
            return False

        self._agents[agent_id].status = "offline"

        if self._db:
            try:
                await self._db.update(
                    "a2a_agents",
                    {"status": "offline"},
                    filters={"id": agent_id},
                )
            except Exception as e:
                logger.warning("a2a_deregister_persist_failed", error=str(e))

        logger.info("a2a_agent_deregistered", agent_id=agent_id)
        return True

    async def mark_stale_offline(self, max_silence_minutes: int = 5) -> int:
        """
        Marcar como offline los agentes que no han enviado heartbeat
        en los últimos `max_silence_minutes` minutos.
        Retorna el número de agentes marcados.
        T4: detecta agentes inactivos (>5min sin heartbeat)
        """
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=max_silence_minutes)
        marked = 0

        for card in self._agents.values():
            if card.status != "active":
                continue
            if not card.last_heartbeat:
                continue
            try:
                last = datetime.fromisoformat(card.last_heartbeat)
                if last < cutoff:
                    card.status = "idle"
                    marked += 1
            except Exception:
                pass

        if marked:
            logger.info("a2a_stale_agents_marked", count=marked, threshold_minutes=max_silence_minutes)
        return marked

    def get_all_cards(self) -> list[dict[str, Any]]:
        """Obtener todas las Agent Cards (para endpoint de discovery)."""
        return [card.to_dict() for card in self._agents.values()]

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas del registry."""
        by_role: dict[str, int] = {}
        by_status: dict[str, int] = {}
        for card in self._agents.values():
            by_role[card.role] = by_role.get(card.role, 0) + 1
            by_status[card.status] = by_status.get(card.status, 0) + 1

        return {
            "total_agents": len(self._agents),
            "by_role": by_role,
            "by_status": by_status,
        }


# ── Singleton ──────────────────────────────────────────────────────

_registry_instance: Optional[A2ARegistry] = None


def get_a2a_registry() -> Optional[A2ARegistry]:
    """Obtener el singleton del A2A Registry."""
    return _registry_instance


async def init_a2a_registry(db=None) -> A2ARegistry:
    """
    Inicializar el A2A Registry singleton.
    Llamar desde el lifespan de main.py.
    """
    global _registry_instance
    registry = A2ARegistry(db=db)
    await registry.initialize()

    # Auto-registrar El Monstruo como agente principal
    from kernel.a2a_registry import AgentCard

    monstruo_card = AgentCard(
        agent_id="el-monstruo-core",
        name="El Monstruo",
        description=(
            "Sovereign AI orchestrator. Creates digital businesses, predicts futures, never repeats mistakes."
        ),
        version="0.55.0",
        capabilities=[
            "web_search",
            "code_generation",
            "web_development",
            "multi_model_consultation",
            "causal_analysis",
            "autonomous_operation",
            "business_creation",
            "wide_research",
            "spec_driven_planning",
        ],
        input_modes=["text/plain", "application/json"],
        output_modes=["text/plain", "application/json", "text/html"],
        endpoint=os.environ.get("A2A_ENDPOINT", "https://el-monstruo.up.railway.app/v1/a2a"),
        role="orchestrator",
        status="active",
    )
    await registry.register(monstruo_card)

    _registry_instance = registry
    logger.info("a2a_registry_initialized", total_agents=len(registry._agents))
    return registry
