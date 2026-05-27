"""
El Monstruo — Tool Definitions (DAN P0.4-mínimo)
=================================================
Capa tipada de definiciones de tools sobre `kernel/tool_dispatch.py` y
`kernel/tool_broker.py` ya existentes. NO reemplaza al dispatch ni al broker —
solo provee los Pydantic models que el DAN exige (`ToolDefinition`, `ToolResult`)
para que callers tipados (apps, futuro mission_events) puedan razonar sobre las
tools y sus resultados sin parsear dicts crudos.

Anti-duplicación (DSC-G-004): NO crear `ToolExecutor` paralelo. El dispatch
existente con su broker ya ejecuta — esta capa solo formaliza el contrato.

Sprint DAN — P0.4 — 2026-05-27 — Manus E1
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """
    Definición tipada de un tool del Monstruo.

    Equivalente conceptual a `router.llm_client.ToolSpec` (que se envía al LLM
    para function-calling) pero con campos operativos extra que el DAN exige:
    `version`, `requires_approval` (HITL), `timeout_ms`, costos/latencias
    estimados para budget gating. Los campos extendidos `risk_class`,
    `replay_policy`, etc. quedan para Sprint 2 (no en alcance P0.4-mínimo).
    """

    name: str = Field(..., description="Nombre canónico del tool, ej. 'web_search', 'github_ops'.")
    version: str = Field(default="1.0", description="Versión semántica del tool.")
    description_for_model: str = Field(
        ...,
        description="Descripción que se envía al LLM para que decida cuándo invocarlo.",
    )
    json_schema: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema de los argumentos (compatible con OpenAI function-calling).",
    )
    requires_approval: bool = Field(
        default=False,
        description="Si True, el tool requiere HITL antes de ejecutarse (ej. github_ops merge_pr).",
    )
    timeout_ms: int = Field(
        default=30_000, description="Timeout duro en milisegundos."
    )
    cost_usd_estimated: float = Field(
        default=0.0,
        description="Costo USD estimado por invocación (para budget gating, NO real).",
    )
    latency_ms_estimated: int = Field(
        default=0,
        description="Latencia ms estimada por invocación (para SLO, NO real).",
    )

    model_config = {"frozen": True}  # inmutable post-creación


class ToolResult(BaseModel):
    """
    Resultado tipado de una invocación de tool.

    Status mapping:
      - `success`: ejecución completa, `output` poblado.
      - `error`: el handler lanzó excepción o devolvió `error` no-vacío.
      - `denied`: tool no registrado, denegado por policy/HITL, o approval rejected.
      - `timeout`: timeout duro alcanzado.
    """

    status: Literal["success", "error", "denied", "timeout"]
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    cost_usd: float = 0.0
    latency_ms: int = 0
    tool_name: str = ""
    run_id: Optional[str] = None

    @classmethod
    def from_handler_result(
        cls,
        *,
        tool_name: str,
        result: dict[str, Any],
        latency_ms: int,
        run_id: Optional[str] = None,
    ) -> "ToolResult":
        """
        Construye un ToolResult desde el dict que devuelven los handlers
        existentes en `tool_dispatch._execute_tool`. Convención:
          - Si `result["error"]` está presente y no-vacío → status='error'.
          - Si `result["status"] == "denied"` → status='denied'.
          - Si `result["status"] == "timeout"` → status='timeout'.
          - En otro caso → status='success'.
        """
        err = result.get("error") if isinstance(result, dict) else None
        cost = float(result.get("cost_usd", 0.0)) if isinstance(result, dict) else 0.0

        if isinstance(result, dict) and result.get("status") == "denied":
            return cls(
                status="denied",
                error=err,
                tool_name=tool_name,
                latency_ms=latency_ms,
                run_id=run_id,
            )
        if isinstance(result, dict) and result.get("status") == "timeout":
            return cls(
                status="timeout",
                error=err or "timeout",
                tool_name=tool_name,
                latency_ms=latency_ms,
                run_id=run_id,
            )
        if err:
            return cls(
                status="error",
                error=err,
                output=result if isinstance(result, dict) else None,
                tool_name=tool_name,
                latency_ms=latency_ms,
                cost_usd=cost,
                run_id=run_id,
            )
        return cls(
            status="success",
            output=result if isinstance(result, dict) else {"value": result},
            cost_usd=cost,
            latency_ms=latency_ms,
            tool_name=tool_name,
            run_id=run_id,
        )


# ── Catálogo canónico DAN P0.4-mínimo ─────────────────────────────────
#
# 3 tools obligatorias del spec. Las metadata aquí son la fuente de verdad
# tipada que apps/CI pueden consumir. Los handlers concretos viven en:
#   - tools/web_search_tool.py (ya en main desde P0.5)
#   - tools/skill_read.py (nuevo en P0.4)
#   - tools/github_ops.py (nuevo en P0.4 — tool crítica para desbloquear S5)

WEB_SEARCH_TOOL_DEF = ToolDefinition(
    name="web_search",
    version="1.0",
    description_for_model=(
        "Search the web for real-time information. MUST be called when the user "
        "asks about current prices, exchange rates, news, weather, stock prices, "
        "sports scores, recent events, or ANY fact that may have changed after "
        "your training cutoff. Returns answer with citations."
    ),
    json_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"},
            "context": {"type": "string", "description": "Optional context"},
        },
        "required": ["query"],
    },
    requires_approval=False,
    timeout_ms=60_000,
    cost_usd_estimated=0.005,  # P0.5: blended Sonar approx; refinará con runs reales
    latency_ms_estimated=800,  # Sonar reasoning typical TTLT
)

SKILL_READ_TOOL_DEF = ToolDefinition(
    name="skill_read",
    version="1.0",
    description_for_model=(
        "Read the contents of a skill's SKILL.md file from skills/<name>/SKILL.md. "
        "Read-only operation. PII is redacted from the output. Use this when you "
        "need to access procedural knowledge stored in a skill."
    ),
    json_schema={
        "type": "object",
        "properties": {
            "skill_name": {
                "type": "string",
                "description": "Name of the skill directory under skills/, e.g. 'el-monstruo-core'.",
            },
        },
        "required": ["skill_name"],
    },
    requires_approval=False,
    timeout_ms=10_000,
    cost_usd_estimated=0.0,  # local read; no LLM/API cost
    latency_ms_estimated=20,
)

GITHUB_OPS_TOOL_DEF = ToolDefinition(
    name="github_ops",
    version="1.0",
    description_for_model=(
        "Execute GitHub repository operations via tools/github.py::execute_github(). "
        "Read actions (search_repos, search_code, get_file, list_issues, list_prs) "
        "are auto-allowed. Write actions split in two: COMMIT_LOOP (create_branch, "
        "create_or_update_file, create_pull_request) are auto-approved because the "
        "PR itself is the human gate; HITL_WRITE (create_issue, update_issue) require "
        "explicit human approval before execution. Pass the GitHub action name in "
        "`action` and its arguments as a flat dict in `params`."
    ),
    json_schema={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    # READ actions
                    "search_repos",
                    "search_code",
                    "get_file",
                    "list_issues",
                    "list_prs",
                    # COMMIT_LOOP write actions (auto-approved, PR is the gate)
                    "create_branch",
                    "create_or_update_file",
                    "create_pull_request",
                    # HITL_WRITE actions (require human approval)
                    "create_issue",
                    "update_issue",
                ],
                "description": "GitHub action name (must match tools/github.py).",
            },
            "params": {
                "type": "object",
                "description": (
                    "Flat dict of arguments forwarded to the action function. Keys depend on action: "
                    "`repo` is required for repo-scoped actions; `query`, `path`, `ref`, `state`, "
                    "`limit`, `branch`, `from_branch`, `title`, `body`, `head_branch`, `base_branch`, "
                    "`labels`, `issue_number`, `content`, `commit_message`, `auto_create_branch` "
                    "are passed through as **kwargs."
                ),
            },
        },
        "required": ["action", "params"],
    },
    # github_ops as a TOOL requires approval at the tool boundary; the dispatch
    # then forwards `hitl_approved` into execute_github, which applies its own
    # finer-grained gating (HITL_WRITE_ACTIONS frozenset in tools/github.py).
    requires_approval=True,
    timeout_ms=30_000,
    cost_usd_estimated=0.0,  # GitHub REST API: rate-limit only, no USD per call
    latency_ms_estimated=400,
)


def get_p04_tool_definitions() -> list[ToolDefinition]:
    """Devuelve las 3 ToolDefinitions canónicas del DAN P0.4-mínimo."""
    return [WEB_SEARCH_TOOL_DEF, SKILL_READ_TOOL_DEF, GITHUB_OPS_TOOL_DEF]


def get_tool_definition(name: str) -> Optional[ToolDefinition]:
    """Lookup tipado de una ToolDefinition por nombre."""
    for d in get_p04_tool_definitions():
        if d.name == name:
            return d
    return None
