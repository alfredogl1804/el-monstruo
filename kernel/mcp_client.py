"""
El Monstruo — MCP Client Manager (Sprint 19)
=============================================
Native integration with Model Context Protocol (MCP) servers.

Sprint 18: Preset configs for 3 IVD-validated MCP servers.
Sprint 19: MemPalace integrated (memory/mempalace_bridge.py), not MCP.

Supports two transports:
  - stdio: Local MCP servers launched as subprocesses
  - sse:   Remote MCP servers over HTTP/SSE

Architecture:
    MCPClientManager (this file)
        ├── connects to N MCP servers on startup
        ├── discovers tools from each server
        ├── registers tools in tool_dispatch.py
        └── routes tool calls to the correct server

The MCPClientManager is a singleton initialized in main.py lifespan.
tool_dispatch.py calls execute_mcp_tool() for any tool prefixed with "mcp__".

Validated against: mcp==1.27.0 (MIT, PyPI latest 2026-04-20)
Sprint 18 IVD: checkout@v6.0.2, setup-python@v6.2.0 SHAs confirmed
Reference: https://github.com/modelcontextprotocol/python-sdk

Principio: MCP es un protocolo, no un framework. Nosotros controlamos el dispatch.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.mcp_client")


@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server connection."""

    name: str  # Unique server name (e.g., "filesystem", "github")
    transport: str  # "stdio" or "sse"
    command: Optional[str] = None  # For stdio: command to launch (e.g., "npx")
    args: list[str] = field(default_factory=list)  # For stdio: command arguments
    env: dict[str, str] = field(default_factory=dict)  # Extra env vars for subprocess
    url: Optional[str] = None  # For sse: server URL
    headers: dict[str, str] = field(default_factory=dict)  # For sse: auth headers
    timeout_s: float = 30.0  # Connection timeout


@dataclass
class MCPTool:
    """A tool discovered from an MCP server."""

    server_name: str
    name: str
    description: str
    input_schema: dict[str, Any]

    @property
    def qualified_name(self) -> str:
        """Fully qualified name: mcp__{server}__{tool}."""
        return f"mcp__{self.server_name}__{self.name}"


class MCPClientManager:
    """
    Manages connections to multiple MCP servers and routes tool calls.

    Lifecycle:
        1. main.py creates MCPClientManager with server configs
        2. initialize() connects to all servers and discovers tools
        3. tool_dispatch.py calls execute_mcp_tool() for mcp__* tools
        4. shutdown() closes all connections

    Transport support (validated against mcp==1.27.0):
        - stdio: Uses mcp.client.stdio.stdio_client context manager
        - sse:   Uses mcp.client.sse.sse_client context manager
    """

    def __init__(self, configs: list[MCPServerConfig]):
        self._configs = {c.name: c for c in configs}
        self._sessions: dict[str, Any] = {}  # server_name → ClientSession
        self._transports: dict[str, Any] = {}  # server_name → transport context
        self._tools: dict[str, MCPTool] = {}  # qualified_name → MCPTool
        self._initialized = False

    @property
    def tools(self) -> list[MCPTool]:
        """All discovered MCP tools across all servers."""
        return list(self._tools.values())

    @property
    def tool_specs(self) -> list[dict[str, Any]]:
        """Tool specs in the format expected by tool_dispatch.py / LLM."""
        specs = []
        for tool in self._tools.values():
            specs.append(
                {
                    "name": tool.qualified_name,
                    "description": f"[MCP:{tool.server_name}] {tool.description}",
                    "parameters": tool.input_schema,
                    "risk": "medium",  # MCP tools are external → medium risk
                }
            )
        return specs

    async def initialize(self) -> dict[str, Any]:
        """
        Connect to all configured MCP servers and discover their tools.

        Returns a status dict with connection results per server.
        """
        results = {}

        for name, config in self._configs.items():
            try:
                if config.transport == "stdio":
                    session = await self._connect_stdio(config)
                elif config.transport == "sse":
                    session = await self._connect_sse(config)
                else:
                    logger.error("mcp_unknown_transport", server=name, transport=config.transport)
                    results[name] = {"status": "error", "error": f"Unknown transport: {config.transport}"}
                    continue

                if session:
                    self._sessions[name] = session
                    # Discover tools from this server
                    tools_response = await session.list_tools()
                    server_tools = []
                    for t in tools_response.tools:
                        mcp_tool = MCPTool(
                            server_name=name,
                            name=t.name,
                            description=t.description or f"MCP tool: {t.name}",
                            input_schema=t.inputSchema if hasattr(t, "inputSchema") else {},
                        )
                        self._tools[mcp_tool.qualified_name] = mcp_tool
                        server_tools.append(t.name)

                    logger.info(
                        "mcp_server_connected",
                        server=name,
                        transport=config.transport,
                        tools_discovered=len(server_tools),
                        tool_names=server_tools,
                    )
                    results[name] = {
                        "status": "connected",
                        "tools": server_tools,
                        "transport": config.transport,
                    }
                else:
                    results[name] = {"status": "error", "error": "Session creation returned None"}

            except Exception as e:
                logger.error("mcp_connection_failed", server=name, error=str(e))
                results[name] = {"status": "error", "error": str(e)}

        self._initialized = True
        logger.info(
            "mcp_manager_initialized",
            total_servers=len(self._configs),
            connected=sum(1 for r in results.values() if r["status"] == "connected"),
            total_tools=len(self._tools),
        )
        return results

    async def execute_tool(self, qualified_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """
        Execute an MCP tool by its qualified name (mcp__{server}__{tool}).

        Returns the tool result as a dict.
        """
        tool = self._tools.get(qualified_name)
        if not tool:
            return {"error": f"Unknown MCP tool: {qualified_name}"}

        session = self._sessions.get(tool.server_name)
        if not session:
            return {"error": f"MCP server not connected: {tool.server_name}"}

        try:
            result = await session.call_tool(tool.name, arguments=args)

            # Extract content from MCP result
            if hasattr(result, "content") and result.content:
                # MCP returns a list of content blocks
                texts = []
                for block in result.content:
                    if hasattr(block, "text"):
                        texts.append(block.text)
                    elif hasattr(block, "data"):
                        texts.append(f"[binary data: {len(block.data)} bytes]")
                    else:
                        texts.append(str(block))

                return {
                    "result": "\n".join(texts),
                    "server": tool.server_name,
                    "tool": tool.name,
                    "is_error": getattr(result, "isError", False),
                }
            else:
                return {
                    "result": str(result),
                    "server": tool.server_name,
                    "tool": tool.name,
                }

        except Exception as e:
            logger.error(
                "mcp_tool_execution_failed",
                tool=qualified_name,
                server=tool.server_name,
                error=str(e),
            )
            return {"error": str(e), "server": tool.server_name, "tool": tool.name}

    async def shutdown(self) -> None:
        """Close all MCP server connections."""
        for name in list(self._sessions.keys()):
            try:
                # Close transport contexts
                transport_ctx = self._transports.get(name)
                if transport_ctx and hasattr(transport_ctx, "__aexit__"):
                    await transport_ctx.__aexit__(None, None, None)
                logger.info("mcp_server_disconnected", server=name)
            except Exception as e:
                logger.warning("mcp_disconnect_error", server=name, error=str(e))

        self._sessions.clear()
        self._transports.clear()
        self._tools.clear()
        self._initialized = False

    def get_status(self) -> dict[str, Any]:
        """Return current status of all MCP connections."""
        return {
            "initialized": self._initialized,
            "servers": {
                name: {
                    "connected": name in self._sessions,
                    "transport": self._configs[name].transport,
                    "tools": [t.name for t in self._tools.values() if t.server_name == name],
                }
                for name in self._configs
            },
            "total_tools": len(self._tools),
        }

    # ── Private: Transport Connections ──────────────────────────────────

    async def _connect_stdio(self, config: MCPServerConfig) -> Any:
        """Connect to an MCP server via stdio transport."""
        from mcp import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client

        params = StdioServerParameters(
            command=config.command or "npx",
            args=config.args,
            env={**os.environ, **config.env},
        )

        # Create the stdio transport
        # NOTE: stdio_client is an async context manager that yields (read, write)
        # We need to keep the context alive for the lifetime of the session
        transport_ctx = stdio_client(params)
        streams = await transport_ctx.__aenter__()
        self._transports[config.name] = transport_ctx

        # Create and initialize the session
        read_stream, write_stream = streams
        session = ClientSession(read_stream, write_stream)
        await session.initialize()

        return session

    async def _connect_sse(self, config: MCPServerConfig) -> Any:
        """Connect to an MCP server via SSE transport."""
        from mcp import ClientSession
        from mcp.client.sse import sse_client

        # Create the SSE transport
        transport_ctx = sse_client(
            url=config.url,
            headers=config.headers,
            timeout=config.timeout_s,
        )
        streams = await transport_ctx.__aenter__()
        self._transports[config.name] = transport_ctx

        # Create and initialize the session
        read_stream, write_stream = streams
        session = ClientSession(read_stream, write_stream)
        await session.initialize()

        return session


# ── Factory: Load MCP configs from environment ──────────────────────────


def load_mcp_configs_from_env() -> list[MCPServerConfig]:
    """
    Load MCP server configurations from environment variables.

    Format: MCP_SERVERS=name1:transport:command_or_url,...
    Or individual: MCP_SERVER_{NAME}_TRANSPORT, MCP_SERVER_{NAME}_COMMAND, etc.

    For now, returns an empty list if no MCP servers are configured.
    The user configures servers via env vars or a config file.
    """
    configs = []

    # Check for individual server configs
    # Pattern: MCP_SERVER_{NAME}_TRANSPORT=stdio|sse
    #          MCP_SERVER_{NAME}_COMMAND=npx (for stdio)
    #          MCP_SERVER_{NAME}_ARGS=arg1,arg2 (for stdio)
    #          MCP_SERVER_{NAME}_URL=https://... (for sse)
    #          MCP_SERVER_{NAME}_HEADERS=key:value,key2:value2 (for sse)

    for key, value in os.environ.items():
        if key.startswith("MCP_SERVER_") and key.endswith("_TRANSPORT"):
            name = key.replace("MCP_SERVER_", "").replace("_TRANSPORT", "").lower()
            transport = value.lower()

            config = MCPServerConfig(
                name=name,
                transport=transport,
                command=os.environ.get(f"MCP_SERVER_{name.upper()}_COMMAND"),
                args=os.environ.get(f"MCP_SERVER_{name.upper()}_ARGS", "").split(","),
                url=os.environ.get(f"MCP_SERVER_{name.upper()}_URL"),
                timeout_s=float(os.environ.get(f"MCP_SERVER_{name.upper()}_TIMEOUT", "30")),
            )

            # Parse headers if present
            headers_str = os.environ.get(f"MCP_SERVER_{name.upper()}_HEADERS", "")
            if headers_str:
                for h in headers_str.split(","):
                    if ":" in h:
                        k, v = h.split(":", 1)
                        config.headers[k.strip()] = v.strip()

            configs.append(config)
            logger.info("mcp_config_loaded", server=name, transport=transport)

    return configs


# ── Presets: IVD-Validated MCP Server Configs ────────────────────────────


def get_preset_configs() -> list[MCPServerConfig]:
    """
    Return preset MCP server configs for the 3 IVD-validated servers.

    These are activated ONLY if the corresponding env vars are set:
      - GITHUB_PERSONAL_ACCESS_TOKEN → enables server-github
      - MCP_FILESYSTEM_PATHS → enables server-filesystem
      - SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY → enables mcp-server-supabase

    IVD Validated 2026-04-20:
      - @modelcontextprotocol/server-github: 2025.4.8 (npm)
      - @modelcontextprotocol/server-filesystem: 2026.1.14 (npm)
      - @supabase/mcp-server-supabase: 0.7.0 (npm)
      - @modelcontextprotocol/server-git: DOES NOT EXIST (npm 404)
    """
    presets = []

    # ── GitHub MCP Server ──────────────────────────────────────────
    github_token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if github_token:
        presets.append(
            MCPServerConfig(
                name="github",
                transport="stdio",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token},
                timeout_s=30.0,
            )
        )
        logger.info("mcp_preset_enabled", server="github", pkg="server-github@2025.4.8")

    # ── Filesystem MCP Server ──────────────────────────────────────
    fs_paths = os.environ.get("MCP_FILESYSTEM_PATHS")
    if fs_paths:
        # fs_paths is comma-separated list of allowed directories
        path_list = [p.strip() for p in fs_paths.split(",") if p.strip()]
        presets.append(
            MCPServerConfig(
                name="filesystem",
                transport="stdio",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem"] + path_list,
                timeout_s=30.0,
            )
        )
        logger.info("mcp_preset_enabled", server="filesystem", pkg="server-filesystem@2026.1.14", paths=path_list)

    # ── Supabase MCP Server ────────────────────────────────────────
    supabase_url = os.environ.get("SUPABASE_URL")
    # Sprint 21: Railway has SUPABASE_SERVICE_KEY, not SUPABASE_SERVICE_ROLE_KEY
    # Accept both names for compatibility
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
    if supabase_url and supabase_key:
        presets.append(
            MCPServerConfig(
                name="supabase",
                transport="stdio",
                command="npx",
                args=[
                    "-y",
                    "@supabase/mcp-server-supabase",
                    "--supabase-url",
                    supabase_url,
                    "--supabase-key",
                    supabase_key,
                ],
                timeout_s=30.0,
            )
        )
        logger.info("mcp_preset_enabled", server="supabase", pkg="mcp-server-supabase@0.7.0")

    return presets


def build_mcp_configs() -> list[MCPServerConfig]:
    """
    Build the final MCP config list: presets + env-based custom configs.
    Presets are loaded first, then any custom configs from env vars.
    Duplicates (by name) are resolved in favor of env-based configs.
    """
    preset_configs = get_preset_configs()
    env_configs = load_mcp_configs_from_env()

    # Merge: env configs override presets by name
    merged = {c.name: c for c in preset_configs}
    for c in env_configs:
        merged[c.name] = c  # env overrides preset

    final = list(merged.values())
    logger.info(
        "mcp_configs_built",
        preset_count=len(preset_configs),
        env_count=len(env_configs),
        total=len(final),
        servers=[c.name for c in final],
    )
    return final
