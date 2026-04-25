"""
Multi-Agent Dispatcher — Native LangGraph SubGraph Orchestration
Sprint 19 | v0.13.0-sprint19

Architecture Decision:
  hermes-ai==0.3.20 was evaluated and REJECTED:
    - No license declared (legal risk)
    - Requires Python 3.12+ (compatibility risk)
    - Depends on LlamaIndex (we use LangGraph — architecture mismatch)
    - No public GitHub repo (cannot audit code)

  INSTEAD: Native Multi-Agent Dispatcher using LangGraph SubGraphs.
  This maintains sovereignty and avoids external orchestrator dependency.

Design:
  - Each "agent" is a LangGraph SubGraph with its own state + tools
  - Dispatcher routes tasks to the best agent based on classification
  - Agents can delegate to each other via message passing
  - All agents share the same memory layer (MemPalace + Honcho)

Agent Registry:
  - research_agent: Deep research with web search + Perplexity
  - code_agent: Code generation, review, debugging
  - analysis_agent: Data analysis, financial modeling
  - creative_agent: Writing, brainstorming, content creation
  - ops_agent: DevOps, deployment, monitoring
  - default_agent: General-purpose fallback

Integration:
  - Called from execute node when task requires specialized agent
  - Returns result to main graph for respond node
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("monstruo.kernel.multi_agent")


class AgentType(str, Enum):
    """Available agent specializations."""

    RESEARCH = "research"
    CODE = "code"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    OPS = "ops"
    DEFAULT = "default"


@dataclass
class AgentConfig:
    """Configuration for a specialized agent."""

    agent_type: AgentType
    name: str
    description: str
    system_prompt: str
    tools: list[str] = field(default_factory=list)
    model_preference: Optional[str] = None  # e.g., "gpt-5.4" for research
    max_steps: int = 10
    enabled: bool = True


# ── Agent Registry ─────────────────────────────────────────────────

AGENT_REGISTRY: dict[AgentType, AgentConfig] = {
    AgentType.RESEARCH: AgentConfig(
        agent_type=AgentType.RESEARCH,
        name="Investigador",
        description="Deep research with web search, Perplexity, and source validation",
        system_prompt=(
            "You are a research specialist. Your job is to find accurate, "
            "up-to-date information from multiple sources. Always cite sources. "
            "Cross-validate claims. Use Perplexity for real-time web grounding."
        ),
        tools=["web_search", "perplexity", "browser", "mcp__github"],
        model_preference="sonar-pro",
    ),
    AgentType.CODE: AgentConfig(
        agent_type=AgentType.CODE,
        name="Arquitecto",
        description="Code generation, review, debugging, and architecture",
        system_prompt=(
            "You are a senior software architect. Write clean, tested, "
            "production-ready code. Follow SOLID principles. Always include "
            "error handling and type hints. Prefer composition over inheritance."
        ),
        tools=["code_exec", "mcp__github", "mcp__filesystem"],
        model_preference="claude-sonnet-4-20250514",
    ),
    AgentType.ANALYSIS: AgentConfig(
        agent_type=AgentType.ANALYSIS,
        name="Analista",
        description="Data analysis, financial modeling, and quantitative reasoning",
        system_prompt=(
            "You are a data analyst and financial modeler. Use precise "
            "calculations, statistical methods, and clear visualizations. "
            "Always show your work and cite data sources."
        ),
        tools=["code_exec", "mcp__supabase"],
    ),
    AgentType.CREATIVE: AgentConfig(
        agent_type=AgentType.CREATIVE,
        name="Creativo",
        description="Writing, brainstorming, content creation, and strategy",
        system_prompt=(
            "You are a creative strategist. Generate innovative ideas, "
            "compelling narratives, and strategic frameworks. Balance "
            "creativity with practicality."
        ),
        tools=["web_search"],
    ),
    AgentType.OPS: AgentConfig(
        agent_type=AgentType.OPS,
        name="Operador",
        description="DevOps, deployment, monitoring, and infrastructure",
        system_prompt=(
            "You are a DevOps engineer. Manage deployments, CI/CD pipelines, "
            "monitoring, and infrastructure. Prioritize reliability, security, "
            "and observability."
        ),
        tools=["code_exec", "mcp__github", "mcp__filesystem"],
    ),
    AgentType.DEFAULT: AgentConfig(
        agent_type=AgentType.DEFAULT,
        name="General",
        description="General-purpose assistant for unclassified tasks",
        system_prompt=(
            "You are a helpful general-purpose assistant. Handle any task "
            "that doesn't fit a specialized agent. Be thorough and accurate."
        ),
        tools=["web_search", "code_exec"],
    ),
}


# ── Classifier ─────────────────────────────────────────────────────

# Keyword-based fast classifier (no LLM call needed for obvious cases)
_KEYWORD_MAP: dict[str, AgentType] = {
    # Research
    "investiga": AgentType.RESEARCH,
    "busca": AgentType.RESEARCH,
    "research": AgentType.RESEARCH,
    "encuentra": AgentType.RESEARCH,
    "valida": AgentType.RESEARCH,
    # Code
    "código": AgentType.CODE,
    "code": AgentType.CODE,
    "programa": AgentType.CODE,
    "debug": AgentType.CODE,
    "implementa": AgentType.CODE,
    "refactoriza": AgentType.CODE,
    "script": AgentType.CODE,
    # Analysis
    "analiza": AgentType.ANALYSIS,
    "datos": AgentType.ANALYSIS,
    "financiero": AgentType.ANALYSIS,
    "estadístic": AgentType.ANALYSIS,
    "calcula": AgentType.ANALYSIS,
    "modelo": AgentType.ANALYSIS,
    # Creative
    "escribe": AgentType.CREATIVE,
    "redacta": AgentType.CREATIVE,
    "diseña": AgentType.CREATIVE,
    "brainstorm": AgentType.CREATIVE,
    "estrategia": AgentType.CREATIVE,
    "contenido": AgentType.CREATIVE,
    # Ops
    "deploy": AgentType.OPS,
    "despliegue": AgentType.OPS,
    "ci/cd": AgentType.OPS,
    "pipeline": AgentType.OPS,
    "monitor": AgentType.OPS,
    "infraestructura": AgentType.OPS,
}


def classify_task(user_message: str) -> AgentType:
    """
    Classify a user message to determine which agent should handle it.
    Uses keyword matching for speed. Falls back to DEFAULT.
    """
    msg_lower = user_message.lower()
    scores: dict[AgentType, int] = {}

    for keyword, agent_type in _KEYWORD_MAP.items():
        if keyword in msg_lower:
            scores[agent_type] = scores.get(agent_type, 0) + 1

    if scores:
        best = max(scores, key=scores.get)
        logger.info(
            "task_classified",
            extra={"agent": best.value, "score": scores[best], "total_keywords": sum(scores.values())},
        )
        return best

    logger.info("task_classified", extra={"agent": "default", "reason": "no_keyword_match"})
    return AgentType.DEFAULT


# ── Dispatcher ─────────────────────────────────────────────────────


@dataclass
class DispatchResult:
    """Result from dispatching a task to a specialized agent."""

    agent_type: AgentType
    agent_name: str
    system_prompt: str
    tools: list[str]
    model_preference: Optional[str]
    metadata: dict[str, Any] = field(default_factory=dict)


def dispatch(user_message: str, force_agent: Optional[AgentType] = None) -> DispatchResult:
    """
    Dispatch a task to the appropriate specialized agent.

    Args:
        user_message: The user's message/task
        force_agent: Override classification and use this agent

    Returns:
        DispatchResult with agent config for the execute node
    """
    agent_type = force_agent or classify_task(user_message)
    config = AGENT_REGISTRY.get(agent_type, AGENT_REGISTRY[AgentType.DEFAULT])

    if not config.enabled:
        logger.warning(
            "agent_disabled",
            extra={"agent": agent_type.value, "fallback": "default"},
        )
        config = AGENT_REGISTRY[AgentType.DEFAULT]

    result = DispatchResult(
        agent_type=config.agent_type,
        agent_name=config.name,
        system_prompt=config.system_prompt,
        tools=config.tools,
        model_preference=config.model_preference,
        metadata={
            "max_steps": config.max_steps,
            "description": config.description,
        },
    )

    logger.info(
        "task_dispatched",
        extra={
            "agent": result.agent_type.value,
            "name": result.agent_name,
            "tools_count": len(result.tools),
            "model": result.model_preference or "default",
        },
    )
    return result


def get_registry_status() -> dict[str, Any]:
    """Return registry status for /v1/agents/status endpoint."""
    agents = {}
    for agent_type, config in AGENT_REGISTRY.items():
        agents[agent_type.value] = {
            "name": config.name,
            "description": config.description,
            "tools": config.tools,
            "model_preference": config.model_preference,
            "enabled": config.enabled,
        }
    return {
        "total_agents": len(agents),
        "enabled_agents": sum(1 for c in AGENT_REGISTRY.values() if c.enabled),
        "agents": agents,
    }
