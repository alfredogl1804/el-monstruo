# Sprint 55 — "El Tejido Causal y la Red de Protocolos"

**Fecha de planificación:** 1 mayo 2026
**Pre-requisito:** Sprints 51-54 completados (Cimientos + Manos + Capas Transversales + Primera Chispa de Emergencia)
**Capa:** 2 — Inteligencia Emergente + 3 — Simulación Predictiva
**Objetivos primarios:** #10 (Simulador Predictivo Causal), #8 (Inteligencia Emergente Colectiva)
**Objetivos secundarios:** #7 (No Inventar la Rueda — adoptar MCP/A2A), #12 (Ecosistema — interoperabilidad)
**Duración estimada:** 8-12 días

---

## Contexto Técnico Actual (Validado contra código real)

El Monstruo ya tiene infraestructura MCP parcial y la base para emergencia. Sprint 55 la expande hacia dos fronteras: la red de protocolos (MCP Hub + A2A) y el primer prototipo del Simulador Causal.

| Componente | Estado | Archivo |
|---|---|---|
| FastMCP Server | 5 tools expuestas (web_search, consult_sabios, github_ops, database_query, web_browse) | `kernel/fastmcp_server.py` |
| FastMCP montaje | Montado en `/mcp` vía `app.mount("/mcp", mcp_asgi)` | `kernel/main.py:475` |
| MCP Client | 3 preset servers (GitHub, Filesystem, Supabase) via stdio | `kernel/mcp_client.py` (456 líneas) |
| A2A Card | Básico, estático, sin discovery dinámico | Sprint 54 (pendiente implementación) |
| Embrión Factory | Crea Embriones especializados con cognición evolutiva | `kernel/embrion_factory.py` |
| Debate Protocol | Debate estructurado entre Embriones (3 rondas) | `kernel/debate_protocol.py` |
| Shared Knowledge | Propagación de descubrimientos entre Embriones | Sprint 54 |
| Thoughts Store | Persistencia + embeddings + búsqueda semántica en Supabase | `memory/thoughts.py` |
| Knowledge Graph | LightRAG + pgvector, entidades + relaciones con peso | `memory/knowledge_graph.py` |
| Supabase Client | Wrapper async con insert, select, upsert, rpc | `memory/supabase_client.py` |

**Lo que falta:**
1. El MCP Server solo expone 5 herramientas propias — no conecta servidores de productividad externos (Notion, Gmail, Calendar, Slack)
2. A2A es un concepto en Sprint 54 pero no tiene registry dinámico ni discovery real
3. El Simulador Causal (Objetivo #10) no tiene ni una línea de código — es la pieza más ambiciosa pendiente
4. No existe base de datos de eventos causales ni motor de descomposición

---

## Épica 55.1 — MCP Hub: El Monstruo como Nodo de Productividad

**Objetivo:** Expandir el MCP Hub para que El Monstruo pueda conectar con servidores MCP externos de productividad (Notion, Gmail, Calendar, Slack) como herramientas nativas, sin reinventar integraciones.

**Herramientas adoptadas (Obj #7 — No Inventar la Rueda):**
- `@notionhq/notion-mcp-server@2.2.1` (npm, Mar 2026) — Oficial de Notion
- `@techsend/gmail-mcp-server@2.1.1` (npm, Dec 2025) — Gmail con 25+ tools
- `@anthropic/mcp-server-google-calendar` (npm) — Google Calendar
- `@anthropic/mcp-server-slack` (npm) — Slack oficial

**Principio:** No construir integraciones con APIs de Gmail/Notion/Slack. Los MCP servers ya existen, están mantenidos por las propias empresas, y nuestro `MCPClientManager` ya sabe conectarse via stdio. Solo hay que registrar los presets.

### Archivo a modificar: `kernel/mcp_client.py`

Agregar nuevos presets en `get_preset_configs()`:

```python
# ── Notion MCP Server ──────────────────────────────────────────
# @notionhq/notion-mcp-server@2.2.1 (npm, Mar 2026)
# Requiere: NOTION_API_KEY (Integration token)
notion_key = os.environ.get("NOTION_API_KEY")
if notion_key:
    presets.append(
        MCPServerConfig(
            name="notion",
            transport="stdio",
            command="npx",
            args=["-y", "@notionhq/notion-mcp-server"],
            env={"NOTION_API_KEY": notion_key},
            timeout_s=30.0,
        )
    )
    logger.info("mcp_preset_enabled", server="notion", pkg="notion-mcp-server@2.2.1")

# ── Gmail MCP Server ──────────────────────────────────────────
# @techsend/gmail-mcp-server@2.1.1 (npm, Dec 2025)
# Requiere: GMAIL_OAUTH_CLIENT_ID, GMAIL_OAUTH_CLIENT_SECRET, GMAIL_REFRESH_TOKEN
gmail_client_id = os.environ.get("GMAIL_OAUTH_CLIENT_ID")
gmail_client_secret = os.environ.get("GMAIL_OAUTH_CLIENT_SECRET")
gmail_refresh_token = os.environ.get("GMAIL_REFRESH_TOKEN")
if gmail_client_id and gmail_client_secret and gmail_refresh_token:
    presets.append(
        MCPServerConfig(
            name="gmail",
            transport="stdio",
            command="npx",
            args=["-y", "@techsend/gmail-mcp-server"],
            env={
                "GMAIL_OAUTH_CLIENT_ID": gmail_client_id,
                "GMAIL_OAUTH_CLIENT_SECRET": gmail_client_secret,
                "GMAIL_REFRESH_TOKEN": gmail_refresh_token,
            },
            timeout_s=30.0,
        )
    )
    logger.info("mcp_preset_enabled", server="gmail", pkg="gmail-mcp-server@2.1.1")

# ── Slack MCP Server ──────────────────────────────────────────
# Slack official MCP server
# Requiere: SLACK_BOT_TOKEN, SLACK_TEAM_ID
slack_token = os.environ.get("SLACK_BOT_TOKEN")
slack_team = os.environ.get("SLACK_TEAM_ID")
if slack_token and slack_team:
    presets.append(
        MCPServerConfig(
            name="slack",
            transport="stdio",
            command="npx",
            args=["-y", "@anthropic/mcp-server-slack"],
            env={
                "SLACK_BOT_TOKEN": slack_token,
                "SLACK_TEAM_ID": slack_team,
            },
            timeout_s=30.0,
        )
    )
    logger.info("mcp_preset_enabled", server="slack", pkg="mcp-server-slack")

# ── Google Calendar MCP Server ─────────────────────────────────
# Requiere: GOOGLE_CALENDAR_CREDENTIALS (JSON path)
gcal_creds = os.environ.get("GOOGLE_CALENDAR_CREDENTIALS")
if gcal_creds:
    presets.append(
        MCPServerConfig(
            name="google_calendar",
            transport="stdio",
            command="npx",
            args=["-y", "@anthropic/mcp-server-google-calendar"],
            env={"GOOGLE_CALENDAR_CREDENTIALS": gcal_creds},
            timeout_s=30.0,
        )
    )
    logger.info("mcp_preset_enabled", server="google_calendar")
```

### Archivo a modificar: `kernel/fastmcp_server.py`

Agregar herramienta `list_mcp_servers` para que agentes externos puedan descubrir qué servidores están disponibles:

```python
@mcp.tool(
    name="list_mcp_servers",
    description=(
        "List all connected MCP servers and their available tools. "
        "Use this to discover what integrations El Monstruo has access to."
    ),
    tags={"discovery", "read-only"},
)
async def list_mcp_servers() -> str:
    """List connected MCP servers and their tools."""
    from fastapi import Request
    # Access MCPClientManager from app state
    manager = getattr(_app_state, "mcp_client_manager", None)
    if not manager:
        return json.dumps({"error": "MCPClientManager not initialized"})
    
    status = manager.get_status()
    return json.dumps(status, default=str)
```

### Archivo nuevo: `kernel/mcp_hub_config.py`

```python
"""
El Monstruo — MCP Hub Configuration (Sprint 55)
================================================
Centraliza la configuración del MCP Hub.
Permite agregar/remover servidores MCP dinámicamente via API.

Sprint 55 | Validated: fastmcp==3.2.4, mcp==1.27.0
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

from kernel.mcp_client import MCPClientManager, MCPServerConfig

logger = structlog.get_logger("kernel.mcp_hub")


@dataclass
class MCPHubStatus:
    """Estado completo del MCP Hub."""
    total_servers: int = 0
    active_servers: int = 0
    total_tools: int = 0
    servers: list[dict[str, Any]] = field(default_factory=list)


class MCPHub:
    """
    Capa de gestión sobre MCPClientManager.
    Permite:
      - Registrar servidores dinámicamente (sin restart)
      - Listar servidores y herramientas disponibles
      - Health check de conexiones
      - Métricas de uso por servidor
    """

    def __init__(self, manager: MCPClientManager):
        self._manager = manager
        self._usage_stats: dict[str, int] = {}  # server_name → call_count

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

    async def add_server(self, config: MCPServerConfig) -> dict[str, Any]:
        """
        Agregar un servidor MCP dinámicamente (hot-plug).
        No requiere restart del servicio.
        """
        try:
            if config.transport == "stdio":
                session = await self._manager._connect_stdio(config)
            elif config.transport == "sse":
                session = await self._manager._connect_sse(config)
            else:
                return {"error": f"Unsupported transport: {config.transport}"}

            # Discover tools from new server
            tools = await session.list_tools()
            for tool in tools.tools:
                from kernel.mcp_client import MCPTool
                mcp_tool = MCPTool(
                    server_name=config.name,
                    name=tool.name,
                    description=tool.description or "",
                    input_schema=tool.inputSchema or {},
                )
                self._manager._tools.append(mcp_tool)

            self._manager._sessions[config.name] = session
            logger.info("mcp_server_added_dynamically", server=config.name, tools=len(tools.tools))
            return {"success": True, "server": config.name, "tools_discovered": len(tools.tools)}

        except Exception as e:
            logger.error("mcp_server_add_failed", server=config.name, error=str(e))
            return {"error": str(e), "server": config.name}

    def record_usage(self, server_name: str) -> None:
        """Registrar uso de un servidor MCP."""
        self._usage_stats[server_name] = self._usage_stats.get(server_name, 0) + 1

    def get_usage_stats(self) -> dict[str, int]:
        """Obtener estadísticas de uso."""
        return dict(self._usage_stats)
```

### Variables de entorno requeridas (Railway):

| Variable | Descripción | Cuándo activar |
|---|---|---|
| `NOTION_API_KEY` | Notion Integration token | Cuando Alfredo conecte Notion |
| `GMAIL_OAUTH_CLIENT_ID` | Google OAuth Client ID | Cuando Alfredo conecte Gmail |
| `GMAIL_OAUTH_CLIENT_SECRET` | Google OAuth Secret | Cuando Alfredo conecte Gmail |
| `GMAIL_REFRESH_TOKEN` | Gmail refresh token | Cuando Alfredo conecte Gmail |
| `SLACK_BOT_TOKEN` | Slack Bot OAuth token | Cuando Alfredo conecte Slack |
| `SLACK_TEAM_ID` | Slack workspace ID | Cuando Alfredo conecte Slack |
| `GOOGLE_CALENDAR_CREDENTIALS` | Path a JSON de credenciales | Cuando Alfredo conecte Calendar |

### Criterio de éxito:

- **T1:** `MCPClientManager.initialize()` conecta Notion si `NOTION_API_KEY` está presente
- **T2:** `list_mcp_servers` tool retorna lista completa de servidores y herramientas
- **T3:** `MCPHub.add_server()` agrega un servidor sin restart
- **T4:** Tool dispatch ruta `mcp__notion__search_pages` correctamente al servidor Notion
- **T5:** Métricas de uso se registran por servidor

---

## Épica 55.2 — A2A Registry: Descubrimiento Dinámico entre Embriones

**Objetivo:** Implementar un registro A2A compliant donde cada Embrión publica su Agent Card y puede descubrir a otros Embriones dinámicamente — sin hardcode. Esto es la base para que el Ecosistema de Monstruos (Obj #12) funcione a futuro.

**Herramienta adoptada (Obj #7):**
- `a2a-sdk==1.0.2` (PyPI, Apr 24, 2026) — Google LLC, Apache 2.0
- A2A Protocol Spec v1.0 — JSON-RPC + HTTP+JSON/REST
- Extras: `http-server` (FastAPI), `postgresql`, `telemetry`

**Principio:** El A2A SDK de Google ya implementa Agent Cards, discovery, y comunicación. No reinventamos el protocolo — lo adoptamos y lo conectamos con nuestro Embrión Factory.

### Archivo nuevo: `kernel/a2a_registry.py`

```python
"""
El Monstruo — A2A Agent Registry (Sprint 55)
=============================================
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

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

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
    capabilities: list[str] = field(default_factory=list)
    input_modes: list[str] = field(default_factory=lambda: ["text/plain"])
    output_modes: list[str] = field(default_factory=lambda: ["text/plain"])
    
    # Comunicación
    endpoint: Optional[str] = None  # URL para comunicación directa
    protocol: str = "a2a/1.0"
    
    # Metadata
    role: str = "general"
    status: str = "active"  # active, idle, busy, offline
    last_heartbeat: Optional[str] = None
    registered_at: Optional[str] = None
    
    # Auth
    auth_schemes: list[str] = field(default_factory=lambda: ["bearer"])
    
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
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


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
                card = AgentCard.from_dict(row.get("card_data", {}))
                card.agent_id = row["id"]
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
        card.registered_at = datetime.now(timezone.utc).isoformat()
        card.last_heartbeat = card.registered_at
        
        self._agents[card.agent_id] = card

        if self._db:
            await self._db.upsert("a2a_agents", {
                "id": card.agent_id,
                "name": card.name,
                "role": card.role,
                "status": card.status,
                "card_data": card.to_dict(),
                "registered_at": card.registered_at,
                "last_heartbeat": card.last_heartbeat,
            })

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
            await self._db.update(
                "a2a_agents",
                {"last_heartbeat": now},
                filters={"id": agent_id},
            )
        return True

    async def deregister(self, agent_id: str) -> bool:
        """Marcar un agente como offline."""
        if agent_id not in self._agents:
            return False
        
        self._agents[agent_id].status = "offline"
        
        if self._db:
            await self._db.update(
                "a2a_agents",
                {"status": "offline"},
                filters={"id": agent_id},
            )
        
        logger.info("a2a_agent_deregistered", agent_id=agent_id)
        return True

    def get_all_cards(self) -> list[dict[str, Any]]:
        """Obtener todas las Agent Cards (para endpoint de discovery)."""
        return [card.to_dict() for card in self._agents.values()]

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas del registry."""
        by_role = {}
        by_status = {}
        for card in self._agents.values():
            by_role[card.role] = by_role.get(card.role, 0) + 1
            by_status[card.status] = by_status.get(card.status, 0) + 1
        
        return {
            "total_agents": len(self._agents),
            "by_role": by_role,
            "by_status": by_status,
        }
```

### Archivo nuevo: `kernel/a2a_routes.py`

```python
"""
El Monstruo — A2A Protocol Routes (Sprint 55)
==============================================
Endpoints REST para el protocolo A2A:
  GET  /.well-known/agent.json  → Agent Card de El Monstruo (discovery)
  GET  /v1/a2a/agents           → Listar todos los agentes registrados
  POST /v1/a2a/register         → Registrar un agente externo
  POST /v1/a2a/discover         → Buscar agentes por capacidad
  POST /v1/a2a/heartbeat        → Actualizar heartbeat
  POST /v1/a2a/send             → Enviar tarea a un agente (futuro)
"""
from __future__ import annotations

from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = structlog.get_logger("kernel.a2a_routes")

router = APIRouter(prefix="/v1/a2a", tags=["a2a"])

# Dependency injection
_registry = None


def set_registry(registry) -> None:
    """Inyectar el A2ARegistry."""
    global _registry
    _registry = registry


# ── Models ─────────────────────────────────────────────────────

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
async def list_agents():
    """Listar todos los agentes registrados."""
    if not _registry:
        raise HTTPException(503, "A2A Registry not initialized")
    return {"agents": _registry.get_all_cards(), "stats": _registry.get_stats()}


@router.post("/register")
async def register_agent(req: RegisterRequest):
    """Registrar un agente en el registry."""
    if not _registry:
        raise HTTPException(503, "A2A Registry not initialized")
    
    from kernel.a2a_registry import AgentCard
    from uuid import uuid4
    
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
    return {"agent_id": agent_id, "card": card.to_dict()}


@router.post("/discover")
async def discover_agents(req: DiscoverRequest):
    """Descubrir agentes por capacidad o rol."""
    if not _registry:
        raise HTTPException(503, "A2A Registry not initialized")
    
    agents = await _registry.discover(
        capability=req.capability,
        role=req.role,
        status=req.status,
    )
    return {"agents": [a.to_dict() for a in agents], "count": len(agents)}


@router.post("/heartbeat")
async def agent_heartbeat(req: HeartbeatRequest):
    """Actualizar heartbeat de un agente."""
    if not _registry:
        raise HTTPException(503, "A2A Registry not initialized")
    
    success = await _registry.heartbeat(req.agent_id)
    if not success:
        raise HTTPException(404, f"Agent {req.agent_id} not found")
    return {"success": True, "agent_id": req.agent_id}


@router.get("/stats")
async def registry_stats():
    """Estadísticas del A2A Registry."""
    if not _registry:
        raise HTTPException(503, "A2A Registry not initialized")
    return _registry.get_stats()
```

### Schema SQL (Supabase):

```sql
-- Sprint 55: A2A Agent Registry
CREATE TABLE IF NOT EXISTS a2a_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'general',
    status TEXT NOT NULL DEFAULT 'active',
    card_data JSONB NOT NULL DEFAULT '{}',
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    last_heartbeat TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_a2a_agents_role ON a2a_agents(role);
CREATE INDEX idx_a2a_agents_status ON a2a_agents(status);
CREATE INDEX idx_a2a_agents_heartbeat ON a2a_agents(last_heartbeat);
```

### Well-Known Agent Card (endpoint raíz):

Agregar en `kernel/main.py`:

```python
@app.get("/.well-known/agent.json", tags=["a2a"])
async def agent_card():
    """A2A Agent Card — Discovery endpoint para El Monstruo."""
    return {
        "name": "El Monstruo",
        "description": "Sovereign AI orchestrator. Creates digital businesses, predicts futures, never repeats mistakes.",
        "version": "0.55.0",
        "protocol": "a2a/1.0",
        "capabilities": [
            "web_search", "code_generation", "web_development",
            "multi_model_consultation", "causal_analysis",
            "autonomous_operation", "business_creation",
        ],
        "input_modes": ["text/plain", "application/json"],
        "output_modes": ["text/plain", "application/json", "text/html"],
        "endpoint": os.environ.get("A2A_ENDPOINT", "https://el-monstruo.up.railway.app/v1/a2a"),
        "auth_schemes": ["bearer"],
        "owner": "Alfredo Gongora",
    }
```

### Criterio de éxito:

- **T1:** `GET /.well-known/agent.json` retorna Agent Card válida de El Monstruo
- **T2:** Cada Embrión creado por Factory se auto-registra en A2ARegistry
- **T3:** `POST /v1/a2a/discover?capability=causal_analysis` retorna Embrión-Causal
- **T4:** Heartbeat actualiza timestamp y detecta agentes inactivos (>5min sin heartbeat)
- **T5:** Agente externo puede registrarse vía `POST /v1/a2a/register`

---

## Épica 55.3 — Causal Knowledge Base: La Memoria del Pasado Descompuesto

**Objetivo:** Crear la base de datos de eventos causales — cada evento del mundo descompuesto en sus factores atómicos con pesos probabilísticos y embeddings para búsqueda semántica. Esta es la materia prima del Simulador Predictivo (Obj #10).

**Herramientas adoptadas:**
- Supabase (pgvector) — Ya en el stack, ya usado para embeddings en `thoughts.py`
- OpenAI `text-embedding-3-small` — Ya usado en `memory/thoughts.py` para embeddings
- Patrón de `memory/thoughts.py` — Reutilizar la arquitectura probada (CRUD + embeddings + búsqueda semántica)

**Principio:** No reinventar la capa de persistencia. El patrón de `ThoughtsStore` (embeddings + Supabase + búsqueda semántica via RPC) ya funciona. Se replica para eventos causales.

### Archivo nuevo: `memory/causal_kb.py`

```python
"""
El Monstruo — Causal Knowledge Base (Sprint 55)
================================================
Base de conocimiento causal persistente.
Almacena eventos del mundo descompuestos en factores causales atómicos.

Cada evento tiene:
  - Descripción del evento
  - Categoría (político, económico, tecnológico, social, empresarial)
  - Factores causales (lista de factores con peso probabilístico)
  - Embedding del evento (para búsqueda semántica)
  - Fuentes (de dónde se extrajo la información)
  - Fecha del evento
  - Predicciones derivadas (si aplica)

Arquitectura: Mismo patrón que memory/thoughts.py
  - Supabase tabla `causal_events`
  - pgvector para embeddings
  - RPC para búsqueda semántica
  - CRUD completo

Validated: Supabase pgvector (ya en stack), text-embedding-3-small (ya en uso)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("memory.causal_kb")


@dataclass
class CausalFactor:
    """Un factor causal atómico con peso probabilístico."""
    factor_id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    category: str = "general"  # economic, political, social, technological, cultural, environmental
    weight: float = 0.5  # 0.0 (irrelevante) a 1.0 (determinante)
    confidence: float = 0.7  # Confianza en que este factor es causal (no correlacional)
    direction: str = "positive"  # positive (contribuye), negative (previene), neutral
    evidence: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "factor_id": self.factor_id,
            "description": self.description,
            "category": self.category,
            "weight": self.weight,
            "confidence": self.confidence,
            "direction": self.direction,
            "evidence": self.evidence,
        }


@dataclass
class CausalEvent:
    """Un evento del mundo descompuesto en factores causales."""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    category: str = "general"
    date: Optional[str] = None  # ISO date del evento
    outcome: str = ""  # Qué pasó como resultado
    factors: list[CausalFactor] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    decomposed_by: str = "system"  # Quién lo descompuso (sabio, embrion, manual)
    decomposed_at: Optional[str] = None
    validation_score: float = 0.0  # 0-1, qué tan validada está la descomposición
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "date": self.date,
            "outcome": self.outcome,
            "factors": [f.to_dict() for f in self.factors],
            "sources": self.sources,
            "tags": self.tags,
            "decomposed_by": self.decomposed_by,
            "decomposed_at": self.decomposed_at,
            "validation_score": self.validation_score,
        }


class CausalKnowledgeBase:
    """
    Base de conocimiento causal con persistencia en Supabase.
    Patrón: ThoughtsStore (memory/thoughts.py) adaptado para causalidad.
    """

    TABLE = "causal_events"
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIM = 1536

    def __init__(self, db=None):
        self._db = db
        self._openai = None
        self._initialized = False

    async def initialize(self) -> None:
        """Inicializar cliente OpenAI para embeddings."""
        try:
            from openai import AsyncOpenAI
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self._openai = AsyncOpenAI(api_key=api_key)
            self._initialized = True
            logger.info("causal_kb_initialized")
        except Exception as e:
            logger.error("causal_kb_init_failed", error=str(e))
            self._initialized = True

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generar embedding para un texto."""
        if not self._openai:
            return [0.0] * self.EMBEDDING_DIM
        
        response = await self._openai.embeddings.create(
            model=self.EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding

    async def store_event(self, event: CausalEvent) -> str:
        """
        Almacenar un evento causal con su embedding.
        El embedding se genera del título + descripción + factores.
        """
        # Construir texto para embedding
        factors_text = "; ".join([
            f"{f.description} (peso:{f.weight}, dir:{f.direction})"
            for f in event.factors
        ])
        embed_text = f"{event.title}. {event.description}. Factores: {factors_text}"
        
        embedding = await self._generate_embedding(embed_text)
        
        event.decomposed_at = datetime.now(timezone.utc).isoformat()
        
        row = {
            "id": event.event_id,
            "title": event.title,
            "description": event.description,
            "category": event.category,
            "event_date": event.date,
            "outcome": event.outcome,
            "factors": json.dumps([f.to_dict() for f in event.factors]),
            "sources": event.sources,
            "tags": event.tags,
            "decomposed_by": event.decomposed_by,
            "decomposed_at": event.decomposed_at,
            "validation_score": event.validation_score,
            "embedding": embedding,
        }
        
        if self._db:
            await self._db.upsert(self.TABLE, row)
        
        logger.info(
            "causal_event_stored",
            event_id=event.event_id,
            title=event.title,
            factors=len(event.factors),
        )
        return event.event_id

    async def search_similar(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Buscar eventos causales similares por semántica."""
        embedding = await self._generate_embedding(query)
        
        if not self._db:
            return []
        
        # RPC call para búsqueda vectorial
        results = await self._db.rpc("search_causal_events", {
            "query_embedding": embedding,
            "match_threshold": 0.7,
            "match_count": limit,
        })
        
        return results or []

    async def get_factors_for_category(self, category: str) -> list[dict[str, Any]]:
        """Obtener todos los factores causales de una categoría."""
        if not self._db:
            return []
        
        rows = await self._db.select(self.TABLE, filters={"category": category})
        all_factors = []
        for row in rows:
            factors = json.loads(row.get("factors", "[]"))
            for f in factors:
                f["event_title"] = row.get("title", "")
                f["event_id"] = row.get("id", "")
                all_factors.append(f)
        
        return all_factors

    async def get_stats(self) -> dict[str, Any]:
        """Estadísticas de la base causal."""
        if not self._db:
            return {"total_events": 0, "status": "no_db"}
        
        count = await self._db.count(self.TABLE)
        return {
            "total_events": count,
            "status": "active",
            "embedding_model": self.EMBEDDING_MODEL,
        }
```

### Schema SQL (Supabase):

```sql
-- Sprint 55: Causal Knowledge Base
CREATE TABLE IF NOT EXISTS causal_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT 'general',
    event_date DATE,
    outcome TEXT DEFAULT '',
    factors JSONB NOT NULL DEFAULT '[]',
    sources TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    decomposed_by TEXT DEFAULT 'system',
    decomposed_at TIMESTAMPTZ DEFAULT NOW(),
    validation_score FLOAT DEFAULT 0.0,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_causal_events_category ON causal_events(category);
CREATE INDEX idx_causal_events_date ON causal_events(event_date);
CREATE INDEX idx_causal_events_validation ON causal_events(validation_score);
CREATE INDEX idx_causal_events_embedding ON causal_events 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- RPC para búsqueda semántica
CREATE OR REPLACE FUNCTION search_causal_events(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    description TEXT,
    category TEXT,
    event_date DATE,
    outcome TEXT,
    factors JSONB,
    sources TEXT[],
    tags TEXT[],
    validation_score FLOAT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ce.id,
        ce.title,
        ce.description,
        ce.category,
        ce.event_date,
        ce.outcome,
        ce.factors,
        ce.sources,
        ce.tags,
        ce.validation_score,
        1 - (ce.embedding <=> query_embedding) AS similarity
    FROM causal_events ce
    WHERE 1 - (ce.embedding <=> query_embedding) > match_threshold
    ORDER BY ce.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Trigger para updated_at
CREATE OR REPLACE FUNCTION update_causal_events_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER causal_events_updated
    BEFORE UPDATE ON causal_events
    FOR EACH ROW
    EXECUTE FUNCTION update_causal_events_timestamp();
```

### Criterio de éxito:

- **T1:** `CausalKnowledgeBase.store_event()` persiste evento con embedding en Supabase
- **T2:** `search_similar("crisis financiera 2008")` retorna eventos relevantes con similarity > 0.7
- **T3:** `get_factors_for_category("economic")` retorna factores agregados de todos los eventos económicos
- **T4:** Embedding se genera correctamente con `text-embedding-3-small`
- **T5:** RPC `search_causal_events` funciona con pgvector ivfflat index

---

## Épica 55.4 — Causal Decomposition Engine: Descomponer el Mundo en Átomos Causales

**Objetivo:** Crear el motor que toma cualquier evento complejo y lo descompone en sus factores causales atómicos usando los Sabios (multi-modelo) + investigación en tiempo real. Este es el "cerebro" que alimenta la Causal Knowledge Base.

**Herramientas adoptadas:**
- Los 6 Sabios (GPT 5.2, Gemini 3 Pro, Sonar Pro, etc.) — Ya en `tools/consult_sabios.py`
- DoWhy 0.14 — Framework de causal inference para validación (Model → Identify → Estimate → Refute)
- Perplexity Sonar — Para investigación en tiempo real de factores

**Principio:** La descomposición causal es un problema de razonamiento profundo. Los LLMs son excelentes para esto cuando se les da estructura. DoWhy valida que las relaciones sean causales (no solo correlacionales).

### Archivo nuevo: `kernel/causal_decomposer.py`

```python
"""
El Monstruo — Causal Decomposition Engine (Sprint 55)
=====================================================
Motor de descomposición causal.
Toma cualquier evento y lo descompone en factores causales atómicos.

Pipeline:
  1. Recibe evento (título + contexto)
  2. Consulta Sabios para descomposición inicial (multi-modelo)
  3. Investiga en tiempo real factores adicionales (Perplexity)
  4. Asigna pesos probabilísticos a cada factor
  5. Valida causalidad vs correlación (DoWhy heurístico)
  6. Almacena en CausalKnowledgeBase

Ejemplo:
  Input: "Tesla superó $1T de market cap en 2021"
  Output: [
    {factor: "EV adoption acceleration", weight: 0.85, direction: "positive"},
    {factor: "Elon Musk cult following", weight: 0.7, direction: "positive"},
    {factor: "Zero interest rate environment", weight: 0.8, direction: "positive"},
    {factor: "Supply chain constraints on competitors", weight: 0.6, direction: "positive"},
    {factor: "Regulatory EV credits revenue", weight: 0.5, direction: "positive"},
    ...
  ]

Validated: consult_sabios (ya en stack), Perplexity Sonar (ya en stack)
Future: DoWhy 0.14 para validación estadística cuando haya datos suficientes
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

from memory.causal_kb import CausalEvent, CausalFactor, CausalKnowledgeBase

logger = structlog.get_logger("kernel.causal_decomposer")


DECOMPOSITION_PROMPT = """Eres un analista causal experto. Tu trabajo es descomponer eventos complejos en sus factores causales atómicos.

EVENTO A DESCOMPONER:
{event_title}

CONTEXTO:
{event_context}

INSTRUCCIONES:
1. Identifica TODOS los factores que causaron este evento (no solo los obvios)
2. Para cada factor, asigna:
   - description: Descripción clara y específica del factor
   - category: Una de [economic, political, social, technological, cultural, environmental, psychological]
   - weight: 0.0 a 1.0 (qué tan determinante fue este factor)
   - direction: "positive" (contribuyó al evento), "negative" (lo frenó pero no lo impidió), "neutral"
   - confidence: 0.0 a 1.0 (qué tan seguro estás de que es CAUSAL y no solo correlacional)
   - evidence: Lista de evidencias que soportan esta relación causal

3. REGLAS:
   - Mínimo 5 factores, máximo 15
   - Los pesos NO tienen que sumar 1.0 (múltiples factores pueden ser altamente determinantes)
   - Distingue CAUSA de CORRELACIÓN. Si algo solo co-ocurrió pero no causó, NO lo incluyas
   - Incluye factores de segundo orden (causas de las causas) si son relevantes
   - Sé específico, no genérico. "Condiciones económicas favorables" es malo. "Tasas de interés en 0% por política Fed post-COVID" es bueno.

RESPONDE EN JSON:
{{
  "factors": [
    {{
      "description": "...",
      "category": "...",
      "weight": 0.X,
      "direction": "positive|negative|neutral",
      "confidence": 0.X,
      "evidence": ["...", "..."]
    }}
  ],
  "meta": {{
    "total_factors": N,
    "dominant_category": "...",
    "causal_complexity": "low|medium|high|extreme",
    "temporal_span": "...",
    "counterfactual": "Si [factor principal] no hubiera existido, [qué habría pasado]"
  }}
}}
"""


class CausalDecomposer:
    """
    Motor de descomposición causal.
    Usa multi-modelo (Sabios) para descomponer eventos en factores atómicos.
    """

    def __init__(self, causal_kb: CausalKnowledgeBase, sabios_fn=None, search_fn=None):
        """
        Args:
            causal_kb: Base de conocimiento causal para almacenar resultados
            sabios_fn: Función para consultar Sabios (async)
            search_fn: Función para búsqueda web en tiempo real (async)
        """
        self._kb = causal_kb
        self._consult_sabios = sabios_fn
        self._web_search = search_fn

    async def decompose(
        self,
        title: str,
        context: str = "",
        category: str = "general",
        event_date: Optional[str] = None,
        sources: Optional[list[str]] = None,
        enrich_with_research: bool = True,
    ) -> CausalEvent:
        """
        Descomponer un evento en factores causales atómicos.
        
        Pipeline:
          1. Consultar Sabios para descomposición multi-modelo
          2. (Opcional) Investigar factores adicionales con Perplexity
          3. Consolidar y asignar pesos
          4. Almacenar en CausalKnowledgeBase
        """
        logger.info("causal_decomposition_start", title=title, category=category)

        # ── Paso 1: Descomposición multi-modelo ────────────────────
        prompt = DECOMPOSITION_PROMPT.format(
            event_title=title,
            event_context=context or "No additional context provided.",
        )

        raw_decomposition = await self._call_sabios(prompt)
        factors = self._parse_factors(raw_decomposition)

        # ── Paso 2: Enriquecimiento con investigación ──────────────
        if enrich_with_research and self._web_search:
            additional_factors = await self._research_additional_factors(title, factors)
            factors.extend(additional_factors)

        # ── Paso 3: Buscar eventos similares para contexto ─────────
        similar = await self._kb.search_similar(title, limit=3)
        if similar:
            # Usar factores de eventos similares como validación cruzada
            cross_validated = self._cross_validate(factors, similar)
            factors = cross_validated

        # ── Paso 4: Construir y almacenar evento ───────────────────
        event = CausalEvent(
            title=title,
            description=context,
            category=category,
            date=event_date,
            outcome=title,  # El evento mismo es su outcome
            factors=factors,
            sources=sources or [],
            decomposed_by="causal_decomposer_v1",
            validation_score=self._calculate_validation_score(factors),
        )

        event_id = await self._kb.store_event(event)
        
        logger.info(
            "causal_decomposition_complete",
            event_id=event_id,
            title=title,
            factors_count=len(factors),
            validation_score=event.validation_score,
        )

        return event

    async def _call_sabios(self, prompt: str) -> str:
        """Consultar Sabios para descomposición."""
        if self._consult_sabios:
            try:
                result = await self._consult_sabios(prompt)
                return result if isinstance(result, str) else json.dumps(result)
            except Exception as e:
                logger.error("sabios_call_failed", error=str(e))
        
        # Fallback: usar OpenAI directamente
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("openai_fallback_failed", error=str(e))
            return "{}"

    async def _research_additional_factors(
        self, title: str, existing_factors: list[CausalFactor]
    ) -> list[CausalFactor]:
        """Investigar factores adicionales no capturados por los Sabios."""
        if not self._web_search:
            return []

        # Buscar factores causales que los modelos podrían no conocer
        query = f"causas factores que provocaron: {title}"
        try:
            search_result = await self._web_search(query)
            # Parse search results y extraer factores no duplicados
            # (Implementación simplificada — en producción usaría otro LLM call)
            return []  # Por ahora, los Sabios son suficientes
        except Exception as e:
            logger.warning("research_failed", error=str(e))
            return []

    def _parse_factors(self, raw: str) -> list[CausalFactor]:
        """Parsear respuesta JSON de los Sabios a CausalFactors."""
        try:
            data = json.loads(raw)
            factors_data = data.get("factors", [])
            
            factors = []
            for f in factors_data:
                factor = CausalFactor(
                    description=f.get("description", ""),
                    category=f.get("category", "general"),
                    weight=float(f.get("weight", 0.5)),
                    confidence=float(f.get("confidence", 0.7)),
                    direction=f.get("direction", "positive"),
                    evidence=f.get("evidence", []),
                )
                factors.append(factor)
            
            return factors
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error("factor_parse_failed", error=str(e), raw_length=len(raw))
            return []

    def _cross_validate(
        self, factors: list[CausalFactor], similar_events: list[dict]
    ) -> list[CausalFactor]:
        """
        Validar factores contra eventos similares.
        Si un factor aparece en eventos similares, sube su confianza.
        """
        # Extraer factores de eventos similares
        similar_factor_descriptions = set()
        for event in similar_events:
            event_factors = json.loads(event.get("factors", "[]"))
            for f in event_factors:
                similar_factor_descriptions.add(f.get("description", "").lower())

        # Boost confidence si factor aparece en similares
        for factor in factors:
            desc_lower = factor.description.lower()
            for sim_desc in similar_factor_descriptions:
                if desc_lower in sim_desc or sim_desc in desc_lower:
                    factor.confidence = min(1.0, factor.confidence + 0.1)
                    break

        return factors

    def _calculate_validation_score(self, factors: list[CausalFactor]) -> float:
        """
        Calcular score de validación de la descomposición.
        Basado en: diversidad de categorías, confianza promedio, evidencia.
        """
        if not factors:
            return 0.0

        # Diversidad de categorías (más categorías = mejor descomposición)
        categories = set(f.category for f in factors)
        diversity_score = min(1.0, len(categories) / 4.0)

        # Confianza promedio
        avg_confidence = sum(f.confidence for f in factors) / len(factors)

        # Evidencia (factores con evidencia son más confiables)
        evidence_ratio = sum(1 for f in factors if f.evidence) / len(factors)

        # Score compuesto
        return round(
            (diversity_score * 0.3) + (avg_confidence * 0.4) + (evidence_ratio * 0.3),
            3,
        )
```

### Criterio de éxito:

- **T1:** `decompose("Tesla superó $1T market cap en 2021")` retorna ≥5 factores con pesos
- **T2:** Cada factor tiene category, weight, confidence, direction asignados
- **T3:** `validation_score` se calcula correctamente (diversidad + confianza + evidencia)
- **T4:** Cross-validation contra eventos similares incrementa confianza
- **T5:** Resultado se almacena automáticamente en CausalKnowledgeBase

---

## Épica 55.5 — Monte Carlo Causal Simulator: Predecir Variando Factores

**Objetivo:** Crear el primer prototipo del simulador que toma un escenario hipotético, varía sus factores causales, y ejecuta simulaciones Monte Carlo para estimar probabilidades de diferentes outcomes. Este es el corazón del Objetivo #10.

**Herramientas adoptadas:**
- PyMC (v5.x, Apr 2026) — Bayesian modeling con MCMC nativo, gold standard para Monte Carlo
- NumPy/SciPy — Distribuciones probabilísticas y sampling
- CausalKnowledgeBase (Épica 55.3) — Fuente de factores y pesos históricos

**Principio:** El simulador NO necesita ser perfecto en v1. Necesita ser funcional y mejorable. "Semi-exacto es infinitamente mejor que intuición humana" (Obj #10). La precisión sube perpetuamente con más datos.

### Archivo nuevo: `kernel/causal_simulator.py`

```python
"""
El Monstruo — Causal Monte Carlo Simulator (Sprint 55)
======================================================
Primer prototipo del Simulador Predictivo Causal (Objetivo #10).

Toma un escenario hipotético y simula N variaciones Monte Carlo
para estimar la distribución de probabilidad de diferentes outcomes.

Pipeline:
  1. Recibe escenario (pregunta + factores conocidos)
  2. Busca eventos similares en CausalKnowledgeBase
  3. Construye modelo probabilístico con factores + pesos
  4. Ejecuta N simulaciones Monte Carlo
  5. Agrega resultados en distribución de probabilidad
  6. Retorna predicción con intervalos de confianza

Ejemplo:
  Input: "¿Qué probabilidad tiene una startup de AI en 2026 de llegar a $10M ARR en 2 años?"
  Factores: [market_size=0.9, team_quality=0.8, timing=0.85, competition=0.6, funding=0.7]
  Output: {
    "probability": 0.23,
    "confidence_interval": [0.15, 0.31],
    "dominant_factors": ["market_size", "timing"],
    "risk_factors": ["competition"],
    "simulations_run": 10000
  }

Validated: numpy (ya en stack), scipy (ya en stack)
Future: PyMC para modelos Bayesianos más sofisticados
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import numpy as np
import structlog

from memory.causal_kb import CausalKnowledgeBase

logger = structlog.get_logger("kernel.causal_simulator")


@dataclass
class SimulationScenario:
    """Escenario a simular."""
    question: str  # La pregunta predictiva
    known_factors: dict[str, float] = field(default_factory=dict)  # factor → valor actual (0-1)
    time_horizon: str = "1_year"  # Horizonte temporal
    category: str = "general"
    context: str = ""


@dataclass
class SimulationResult:
    """Resultado de una simulación Monte Carlo."""
    scenario: str
    probability: float  # Probabilidad estimada del outcome
    confidence_interval: tuple[float, float] = (0.0, 1.0)  # 95% CI
    dominant_factors: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    simulations_run: int = 0
    mean_outcome: float = 0.0
    std_outcome: float = 0.0
    percentiles: dict[str, float] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario": self.scenario,
            "probability": round(self.probability, 4),
            "confidence_interval": [round(x, 4) for x in self.confidence_interval],
            "dominant_factors": self.dominant_factors,
            "risk_factors": self.risk_factors,
            "simulations_run": self.simulations_run,
            "mean_outcome": round(self.mean_outcome, 4),
            "std_outcome": round(self.std_outcome, 4),
            "percentiles": {k: round(v, 4) for k, v in self.percentiles.items()},
            "timestamp": self.timestamp,
        }


class CausalSimulator:
    """
    Simulador Monte Carlo Causal.
    Primer prototipo — usa distribuciones Beta para modelar factores
    y sampling Monte Carlo para estimar outcomes.
    """

    DEFAULT_SIMULATIONS = 10_000
    CONFIDENCE_LEVEL = 0.95

    def __init__(self, causal_kb: CausalKnowledgeBase):
        self._kb = causal_kb

    async def simulate(
        self,
        scenario: SimulationScenario,
        n_simulations: int = DEFAULT_SIMULATIONS,
    ) -> SimulationResult:
        """
        Ejecutar simulación Monte Carlo para un escenario.
        
        Método:
          1. Obtener factores base de eventos similares
          2. Combinar con factores conocidos del escenario
          3. Modelar cada factor como distribución Beta(α, β)
          4. Samplear N veces y calcular outcome agregado
          5. Retornar distribución de probabilidad
        """
        logger.info(
            "simulation_start",
            question=scenario.question,
            n_simulations=n_simulations,
            known_factors=len(scenario.known_factors),
        )

        # ── Paso 1: Obtener factores históricos ────────────────────
        historical_factors = await self._get_historical_factors(scenario)

        # ── Paso 2: Combinar factores ──────────────────────────────
        combined_factors = self._combine_factors(
            historical_factors, scenario.known_factors
        )

        if not combined_factors:
            # Sin factores, retornar prior uniforme
            return SimulationResult(
                scenario=scenario.question,
                probability=0.5,
                confidence_interval=(0.2, 0.8),
                simulations_run=0,
                mean_outcome=0.5,
                std_outcome=0.25,
            )

        # ── Paso 3: Ejecutar Monte Carlo ───────────────────────────
        outcomes = self._run_monte_carlo(combined_factors, n_simulations)

        # ── Paso 4: Analizar resultados ────────────────────────────
        result = self._analyze_outcomes(outcomes, combined_factors, scenario)

        logger.info(
            "simulation_complete",
            question=scenario.question,
            probability=result.probability,
            ci=result.confidence_interval,
            simulations=result.simulations_run,
        )

        return result

    async def _get_historical_factors(
        self, scenario: SimulationScenario
    ) -> list[dict[str, Any]]:
        """Obtener factores de eventos históricos similares."""
        similar_events = await self._kb.search_similar(scenario.question, limit=5)
        
        all_factors = []
        for event in similar_events:
            factors = json.loads(event.get("factors", "[]"))
            for f in factors:
                f["source_event"] = event.get("title", "unknown")
                f["source_similarity"] = event.get("similarity", 0.0)
                all_factors.append(f)
        
        return all_factors

    def _combine_factors(
        self,
        historical: list[dict[str, Any]],
        known: dict[str, float],
    ) -> dict[str, dict[str, float]]:
        """
        Combinar factores históricos con factores conocidos.
        Retorna: {factor_name: {weight, confidence, value}}
        """
        combined = {}

        # Agregar factores históricos (promediando pesos de eventos similares)
        for f in historical:
            desc = f.get("description", "unknown")
            if desc not in combined:
                combined[desc] = {
                    "weight": f.get("weight", 0.5),
                    "confidence": f.get("confidence", 0.5),
                    "value": f.get("weight", 0.5),  # Usar peso como valor base
                    "direction": f.get("direction", "positive"),
                    "count": 1,
                }
            else:
                # Promediar con factores existentes
                existing = combined[desc]
                existing["weight"] = (existing["weight"] * existing["count"] + f.get("weight", 0.5)) / (existing["count"] + 1)
                existing["confidence"] = max(existing["confidence"], f.get("confidence", 0.5))
                existing["count"] += 1

        # Override con factores conocidos del escenario
        for factor_name, value in known.items():
            if factor_name in combined:
                combined[factor_name]["value"] = value
                combined[factor_name]["confidence"] = 0.9  # Conocido = alta confianza
            else:
                combined[factor_name] = {
                    "weight": value,
                    "confidence": 0.9,
                    "value": value,
                    "direction": "positive",
                    "count": 1,
                }

        return combined

    def _run_monte_carlo(
        self,
        factors: dict[str, dict[str, float]],
        n_simulations: int,
    ) -> np.ndarray:
        """
        Ejecutar N simulaciones Monte Carlo.
        
        Cada factor se modela como Beta(α, β) donde:
          α = value * confidence * 10
          β = (1 - value) * confidence * 10
        
        El outcome de cada simulación es el producto ponderado
        de los factores sampleados.
        """
        n_factors = len(factors)
        factor_list = list(factors.values())
        
        # Matriz de samples: (n_simulations, n_factors)
        samples = np.zeros((n_simulations, n_factors))
        weights = np.zeros(n_factors)
        directions = np.ones(n_factors)

        for i, (name, f) in enumerate(factors.items()):
            value = np.clip(f["value"], 0.01, 0.99)
            confidence = np.clip(f["confidence"], 0.1, 0.99)
            
            # Parámetros Beta
            alpha = value * confidence * 10
            beta = (1 - value) * confidence * 10
            
            # Samplear
            samples[:, i] = np.random.beta(alpha, beta, size=n_simulations)
            weights[i] = f["weight"]
            
            if f.get("direction") == "negative":
                directions[i] = -1.0

        # Outcome = weighted average de factores (con dirección)
        weighted_samples = samples * weights[np.newaxis, :] * directions[np.newaxis, :]
        outcomes = np.mean(weighted_samples, axis=1)
        
        # Normalizar a [0, 1]
        outcomes = (outcomes - outcomes.min()) / (outcomes.max() - outcomes.min() + 1e-10)
        
        return outcomes

    def _analyze_outcomes(
        self,
        outcomes: np.ndarray,
        factors: dict[str, dict[str, float]],
        scenario: SimulationScenario,
    ) -> SimulationResult:
        """Analizar distribución de outcomes."""
        # Estadísticas básicas
        mean = float(np.mean(outcomes))
        std = float(np.std(outcomes))
        
        # Intervalo de confianza 95%
        alpha = (1 - self.CONFIDENCE_LEVEL) / 2
        ci_low = float(np.percentile(outcomes, alpha * 100))
        ci_high = float(np.percentile(outcomes, (1 - alpha) * 100))
        
        # Probabilidad = proporción de outcomes > 0.5 (umbral de "éxito")
        probability = float(np.mean(outcomes > 0.5))
        
        # Factores dominantes (top 3 por peso * valor)
        factor_impact = [
            (name, f["weight"] * f["value"])
            for name, f in factors.items()
        ]
        factor_impact.sort(key=lambda x: x[1], reverse=True)
        dominant = [name for name, _ in factor_impact[:3]]
        
        # Factores de riesgo (dirección negativa o valor bajo)
        risk = [
            name for name, f in factors.items()
            if f.get("direction") == "negative" or f["value"] < 0.4
        ]
        
        # Percentiles
        percentiles = {
            "p10": float(np.percentile(outcomes, 10)),
            "p25": float(np.percentile(outcomes, 25)),
            "p50": float(np.percentile(outcomes, 50)),
            "p75": float(np.percentile(outcomes, 75)),
            "p90": float(np.percentile(outcomes, 90)),
        }
        
        return SimulationResult(
            scenario=scenario.question,
            probability=probability,
            confidence_interval=(ci_low, ci_high),
            dominant_factors=dominant,
            risk_factors=risk[:3],
            simulations_run=len(outcomes),
            mean_outcome=mean,
            std_outcome=std,
            percentiles=percentiles,
        )

    async def simulate_counterfactual(
        self,
        scenario: SimulationScenario,
        removed_factor: str,
        n_simulations: int = DEFAULT_SIMULATIONS,
    ) -> dict[str, Any]:
        """
        Simulación contrafactual: ¿Qué habría pasado SIN un factor específico?
        Compara outcome con y sin el factor para medir su impacto causal.
        """
        # Simulación con todos los factores
        result_with = await self.simulate(scenario, n_simulations)
        
        # Simulación sin el factor
        modified_scenario = SimulationScenario(
            question=scenario.question,
            known_factors={k: v for k, v in scenario.known_factors.items() if k != removed_factor},
            time_horizon=scenario.time_horizon,
            category=scenario.category,
        )
        result_without = await self.simulate(modified_scenario, n_simulations)
        
        # Impacto causal = diferencia en probabilidad
        causal_impact = result_with.probability - result_without.probability
        
        return {
            "factor_removed": removed_factor,
            "probability_with": result_with.probability,
            "probability_without": result_without.probability,
            "causal_impact": round(causal_impact, 4),
            "interpretation": (
                f"Removing '{removed_factor}' changes probability from "
                f"{result_with.probability:.2%} to {result_without.probability:.2%} "
                f"(impact: {causal_impact:+.2%})"
            ),
        }
```

### Criterio de éxito:

- **T1:** `simulate(scenario)` ejecuta 10,000 simulaciones en <5 segundos
- **T2:** Resultado incluye probability, confidence_interval, dominant_factors
- **T3:** `simulate_counterfactual()` muestra impacto de remover un factor
- **T4:** Distribución Beta modela correctamente la incertidumbre de cada factor
- **T5:** Con más eventos en CausalKB, las predicciones se vuelven más precisas (testeable)

---

## Integración en `kernel/main.py`

Agregar en el lifespan de la aplicación:

```python
# ── Sprint 55: A2A Registry ──────────────────────────────────
from kernel.a2a_registry import A2ARegistry
from kernel.a2a_routes import router as a2a_router, set_registry

a2a_registry = A2ARegistry(db=db)
await a2a_registry.initialize()
set_registry(a2a_registry)
app.include_router(a2a_router)
app.state.a2a_registry = a2a_registry
logger.info("a2a_registry_initialized", agents=a2a_registry.get_stats()["total_agents"])

# ── Sprint 55: Causal Knowledge Base + Simulator ──────────────
from memory.causal_kb import CausalKnowledgeBase
from kernel.causal_decomposer import CausalDecomposer
from kernel.causal_simulator import CausalSimulator

causal_kb = CausalKnowledgeBase(db=db)
await causal_kb.initialize()
app.state.causal_kb = causal_kb

causal_decomposer = CausalDecomposer(causal_kb=causal_kb)
app.state.causal_decomposer = causal_decomposer

causal_simulator = CausalSimulator(causal_kb=causal_kb)
app.state.causal_simulator = causal_simulator
logger.info("causal_system_initialized")

# ── Sprint 55: MCP Hub ────────────────────────────────────────
from kernel.mcp_hub_config import MCPHub

if hasattr(app.state, "mcp_client_manager"):
    mcp_hub = MCPHub(manager=app.state.mcp_client_manager)
    app.state.mcp_hub = mcp_hub
    logger.info("mcp_hub_initialized")
```

---

## Dependencias Nuevas (requirements.txt)

```
# Sprint 55 — nuevas dependencias
a2a-sdk[http-server,postgresql,telemetry]==1.0.2
# DoWhy para validación causal futura (no bloqueante para v1)
# dowhy==0.14  # Activar cuando haya datos suficientes para validación estadística
```

**Nota:** `fastmcp==3.2.4`, `numpy`, `scipy` ya están en el stack. No se agregan.

---

## Costos Estimados

| Componente | Costo mensual estimado | Notas |
|---|---|---|
| MCP Servers (Notion, Gmail, etc.) | $0 | npm packages, corren como subprocesos |
| A2A Registry (Supabase) | $0 | Dentro del plan existente de Supabase |
| Causal KB embeddings | ~$2-5/mes | text-embedding-3-small, ~$0.02/1M tokens |
| Causal Decomposer (Sabios) | ~$5-15/mes | Depende de frecuencia de descomposición |
| Monte Carlo Simulator | $0 | CPU puro (numpy), sin costo de API |
| **Total Sprint 55** | **~$7-20/mes** | Marginal sobre costos existentes |

---

## Orden de Implementación

| Orden | Épica | Dependencia | Estimación |
|---|---|---|---|
| 1 | 55.3 — Causal Knowledge Base | Ninguna (Supabase ya existe) | 1-2 días |
| 2 | 55.4 — Causal Decomposer | Requiere 55.3 | 2-3 días |
| 3 | 55.5 — Monte Carlo Simulator | Requiere 55.3 | 2-3 días |
| 4 | 55.1 — MCP Hub | Ninguna (MCPClient ya existe) | 1-2 días |
| 5 | 55.2 — A2A Registry | Ninguna (Supabase ya existe) | 2-3 días |

**Total:** 8-13 días (con buffer para testing e integración)

---

## Referencias

[1] FastMCP 3.2.4 — https://pypi.org/project/fastmcp/ (Released Apr 14, 2026)
[2] a2a-sdk 1.0.2 — https://pypi.org/project/a2a-sdk/ (Released Apr 24, 2026)
[3] @notionhq/notion-mcp-server 2.2.1 — https://www.npmjs.com/package/@notionhq/notion-mcp-server (Mar 2026)
[4] @techsend/gmail-mcp-server 2.1.1 — https://www.npmjs.com/package/@techsend/gmail-mcp-server (Dec 2025)
[5] DoWhy 0.14 — https://pypi.org/project/dowhy/ (Nov 2025, Microsoft)
[6] PyMC 5.x — https://pypi.org/project/pymc/ (Apr 2026)
[7] A2A Protocol Spec v1.0 — https://google.github.io/A2A/specification/
[8] MCP SDK 1.27.0 — https://pypi.org/project/mcp/ (Anthropic, MIT)
[9] StatsPAI v1.0 — Reddit/PyPI (Apr 2026, unified causal inference)
[10] InferenceEvolve — ArXiv Apr 2026 (self-evolving causal estimation)
