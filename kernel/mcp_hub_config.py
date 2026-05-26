"""
El Monstruo — MCP Hub Configuration (Sprint 55.1)
==================================================
Capa de gestión sobre MCPClientManager.
Permite agregar/remover servidores MCP dinámicamente (hot-plug),
listar servidores y herramientas disponibles, y registrar métricas de uso.

Arquitectura (Biblia Manus v3 — Tool Masking pattern):
  - No se eliminan herramientas del contexto, se enmascaran con logit masking
  - Los servidores se agregan/remueven sin restart del servicio
  - Cada servidor tiene su propio health check y métricas de uso

Sprint 55.1 | Validated: mcp==1.27.0, fastmcp==3.2.4
Biblia de referencia: Manus v3 (Tool Masking, SSE transport)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.mcp_hub")


@dataclass
class MCPHubStatus:
    """Estado completo del MCP Hub."""

    total_servers: int = 0
    active_servers: int = 0
    total_tools: int = 0
    servers: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_servers": self.total_servers,
            "active_servers": self.active_servers,
            "total_tools": self.total_tools,
            "servers": self.servers,
        }


class MCPHub:
    """
    Capa de gestión sobre MCPClientManager.

    Permite:
      - Registrar servidores dinámicamente (hot-plug, sin restart)
      - Listar servidores y herramientas disponibles
      - Health check de conexiones
      - Métricas de uso por servidor

    Principio Manus v3: Tool Masking.
    Las herramientas no se eliminan del contexto cuando un servidor cae —
    se enmascaran para que el LLM no las invoque. Esto evita errores de
    "tool not found" y mantiene el contexto coherente.
    """

    def __init__(self, manager: Any):
        """
        Args:
            manager: Instancia de MCPClientManager (kernel.mcp_client)
        """
        self._manager = manager
        self._usage_stats: dict[str, int] = {}  # server_name → call_count
        self._masked_servers: set[str] = set()  # Servidores enmascarados (Manus v3 pattern)

    @property
    def status(self) -> MCPHubStatus:
        """Obtener estado actual del hub."""
        raw = self._manager.get_status()
        return MCPHubStatus(
            total_servers=raw.get("total_servers", 0),
            active_servers=raw.get("connected_servers", 0),
            total_tools=raw.get("total_tools", 0),
            servers=raw.get("servers", []),
        )

    async def add_server(self, config: Any) -> dict[str, Any]:
        """
        Agregar un servidor MCP dinámicamente (hot-plug).
        No requiere restart del servicio.

        Args:
            config: MCPServerConfig instance

        Returns:
            dict con success/error, server name y tools_discovered
        """
        try:
            if config.transport == "stdio":
                session = await self._manager._connect_stdio(config)
            elif config.transport == "sse":
                session = await self._manager._connect_sse(config)
            else:
                return {"error": f"Unsupported transport: {config.transport}"}

            # Descubrir herramientas del nuevo servidor
            tools = await session.list_tools()
            from kernel.mcp_client import MCPTool

            for tool in tools.tools:
                mcp_tool = MCPTool(
                    server_name=config.name,
                    name=tool.name,
                    description=tool.description or "",
                    input_schema=tool.inputSchema or {},
                )
                self._manager._tools.append(mcp_tool)

            self._manager._sessions[config.name] = session

            # Desenmascara si estaba enmascarado
            self._masked_servers.discard(config.name)

            logger.info(
                "mcp_server_added_dynamically",
                server=config.name,
                tools=len(tools.tools),
            )
            return {
                "success": True,
                "server": config.name,
                "tools_discovered": len(tools.tools),
            }

        except Exception as e:
            logger.error("mcp_server_add_failed", server=config.name, error=str(e))
            return {"error": str(e), "server": config.name}

    def mask_server(self, server_name: str) -> None:
        """
        Enmascarar un servidor (Manus v3 — Tool Masking pattern).
        Las herramientas del servidor siguen en el registry pero no se
        inyectan en el prompt del LLM.
        """
        self._masked_servers.add(server_name)
        logger.info("mcp_server_masked", server=server_name)

    def unmask_server(self, server_name: str) -> None:
        """Desenmascara un servidor previamente enmascarado."""
        self._masked_servers.discard(server_name)
        logger.info("mcp_server_unmasked", server=server_name)

    def get_active_tools(self) -> list[str]:
        """
        Retorna las herramientas activas (no enmascaradas).
        Usado por tool_dispatch.py para filtrar qué tools inyectar al LLM.
        """
        if not hasattr(self._manager, "_tools"):
            return []
        return [t.qualified_name for t in self._manager._tools if t.server_name not in self._masked_servers]

    def record_usage(self, server_name: str) -> None:
        """Registrar uso de un servidor MCP."""
        self._usage_stats[server_name] = self._usage_stats.get(server_name, 0) + 1

    def get_usage_stats(self) -> dict[str, int]:
        """Obtener estadísticas de uso por servidor."""
        return dict(self._usage_stats)

    def get_masked_servers(self) -> list[str]:
        """Listar servidores actualmente enmascarados."""
        return list(self._masked_servers)

    def to_json(self) -> str:
        """Serializar estado completo del hub a JSON."""
        status = self.status
        return json.dumps(
            {
                **status.to_dict(),
                "masked_servers": list(self._masked_servers),
                "usage_stats": self._usage_stats,
            },
            default=str,
        )


# ── Singleton global ──────────────────────────────────────────────────────────

_hub: Optional[MCPHub] = None


def get_mcp_hub(manager: Any = None) -> Optional[MCPHub]:
    """
    Retorna la instancia global del MCPHub.

    Args:
        manager: MCPClientManager — requerido solo en la primera llamada.

    Returns:
        MCPHub instance, o None si no ha sido inicializado.
    """
    global _hub
    if _hub is None and manager is not None:
        _hub = MCPHub(manager)
        logger.info("mcp_hub_initialized")
    return _hub
