"""
El Monstruo — External Agent Dispatcher
=========================================
Orquesta agentes autónomos externos desde la interfaz de El Monstruo.
Resuelve: Pérdida de contexto entre sesiones.
Solución: La memoria vive en Supabase. Cada agente recibe el contexto
          completo antes de ejecutar. El resultado se escribe de vuelta.

Agentes soportados:
  - manus: Ejecución end-to-end via Manus API (browser, código, archivos)
  - kimi: Kimi K2.5 via OpenRouter (barato, rápido, código abierto)
  - perplexity: Investigación en tiempo real con fuentes citadas
  - gemini: Razonamiento largo, multimodal (Gemini 3.1 Pro)
  - grok: Razonamiento rápido (Grok 4.20 via xAI)

Flujo:
  1. UI envía mensaje + agent_id (o "auto" para selección automática)
  2. Dispatcher inyecta contexto de Supabase (últimos N mensajes + memoria)
  3. Agente ejecuta con contexto completo
  4. Resultado se escribe en conversation_memory de Supabase
  5. UI muestra resultado

Sprint: Multi-Agent Orchestration | mayo 2026
"""
from __future__ import annotations

import asyncio
import os
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import httpx
import structlog

logger = structlog.get_logger("kernel.external_agents")


# ── Agent Types ───────────────────────────────────────────────────────────────

class ExternalAgent(str, Enum):
    """Available external agents."""
    MANUS = "manus"
    KIMI = "kimi"
    PERPLEXITY = "perplexity"
    GEMINI = "gemini"
    GROK = "grok"
    AUTO = "auto"


@dataclass
class AgentProfile:
    """Profile for an external agent."""
    agent_id: ExternalAgent
    name: str
    description: str
    api_key_env: str
    base_url: str
    model: str
    strengths: list[str]
    max_context_tokens: int = 128000
    enabled: bool = True
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


@dataclass
class AgentResponse:
    """Response from an external agent execution."""
    agent_id: str
    agent_name: str
    content: str
    model_used: str
    latency_ms: float
    tokens_used: int = 0
    sources: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


# ── Agent Registry ────────────────────────────────────────────────────────────

AGENT_PROFILES: dict[ExternalAgent, AgentProfile] = {
    ExternalAgent.MANUS: AgentProfile(
        agent_id=ExternalAgent.MANUS,
        name="Manus",
        description="Agente autónomo end-to-end. Browser, código, archivos, deploy.",
        api_key_env="MANUS_API_KEY_GOOGLE",
        base_url="https://api.manus.im/v1",
        model="manus-agent",
        strengths=["browser_research", "code_execution", "file_manipulation", "deploy"],
        max_context_tokens=200000,
        cost_per_1k_input=0.0,  # créditos
        cost_per_1k_output=0.0,
    ),
    ExternalAgent.KIMI: AgentProfile(
        agent_id=ExternalAgent.KIMI,
        name="Kimi K2.5",
        description="Enjambre de agentes. Código abierto, barato, rápido. Ideal para código y análisis.",
        api_key_env="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
        model="moonshot/kimi-k2.5",
        strengths=["code_generation", "analysis", "parallel_tasks", "long_context"],
        max_context_tokens=1000000,  # 1M context
        cost_per_1k_input=0.00045,
        cost_per_1k_output=0.0022,
    ),
    ExternalAgent.PERPLEXITY: AgentProfile(
        agent_id=ExternalAgent.PERPLEXITY,
        name="Perplexity Sonar Pro",
        description="Motor de respuestas en tiempo real. Investigación con fuentes citadas.",
        api_key_env="SONAR_API_KEY",
        base_url="https://api.perplexity.ai",
        model="sonar-reasoning-pro",
        strengths=["real_time_research", "fact_checking", "citations", "news"],
        max_context_tokens=128000,
        cost_per_1k_input=0.002,
        cost_per_1k_output=0.008,
    ),
    ExternalAgent.GEMINI: AgentProfile(
        agent_id=ExternalAgent.GEMINI,
        name="Gemini 3.1 Pro",
        description="Razonamiento largo, multimodal. Ideal para análisis profundo.",
        api_key_env="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        model="gemini-3.1-pro",
        strengths=["deep_reasoning", "multimodal", "long_context", "structured_output"],
        max_context_tokens=2000000,  # 2M context
        cost_per_1k_input=0.00125,
        cost_per_1k_output=0.005,
    ),
    ExternalAgent.GROK: AgentProfile(
        agent_id=ExternalAgent.GROK,
        name="Grok 4.20",
        description="Razonamiento rápido. Bueno para respuestas directas y código.",
        api_key_env="XAI_API_KEY",
        base_url="https://api.x.ai/v1",
        model="grok-4.20",
        strengths=["fast_reasoning", "code", "direct_answers", "humor"],
        max_context_tokens=131072,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
    ),
}


# ── Auto-Selection Logic ──────────────────────────────────────────────────────

def auto_select_agent(
    message: str,
    task_type: Optional[str] = None,
) -> ExternalAgent:
    """
    Automatically select the best agent based on the message/task.
    
    Heuristics:
      - Research/facts/news → Perplexity
      - Code/deploy/browser → Manus
      - Analysis/long docs → Gemini
      - Quick code/fast answer → Grok or Kimi
    """
    msg_lower = message.lower()
    
    # Research indicators
    research_markers = [
        "investiga", "busca", "encuentra", "qué es", "quién es",
        "noticias", "tendencia", "fuentes", "artículo", "paper",
        "research", "search", "find", "news", "trend",
    ]
    if any(m in msg_lower for m in research_markers):
        return ExternalAgent.PERPLEXITY
    
    # Browser/deploy/complex execution indicators
    manus_markers = [
        "browser", "navega", "abre la página", "deploy", "publica",
        "descarga", "sube", "archivo", "screenshot", "scrape",
        "automatiza", "workflow", "end to end",
    ]
    if any(m in msg_lower for m in manus_markers):
        return ExternalAgent.MANUS
    
    # Deep analysis / long document indicators
    analysis_markers = [
        "analiza", "compara", "evalúa", "evalua", "profundiza",
        "documento", "pdf", "resumen largo", "multimodal",
        "imagen", "video", "analyze", "compare",
    ]
    if any(m in msg_lower for m in analysis_markers):
        return ExternalAgent.GEMINI
    
    # Code indicators → Kimi (cheapest for code)
    code_markers = [
        "código", "codigo", "programa", "script", "función", "funcion",
        "bug", "fix", "refactor", "implementa", "code", "debug",
    ]
    if any(m in msg_lower for m in code_markers):
        return ExternalAgent.KIMI
    
    # Default: Grok for fast general answers
    return ExternalAgent.GROK


# ── Agent Execution ───────────────────────────────────────────────────────────

async def execute_agent(
    agent_id: ExternalAgent,
    message: str,
    context: str = "",
    system_prompt: str = "",
    timeout: float = 120.0,
) -> AgentResponse:
    """
    Execute a task on an external agent with full context injection.
    
    Args:
        agent_id: Which agent to use (or AUTO for auto-selection)
        message: The user's message/task
        context: Full conversation context from Supabase (injected)
        system_prompt: System prompt override (optional)
        timeout: Max execution time in seconds
    
    Returns:
        AgentResponse with the agent's output
    """
    # Auto-select if needed
    if agent_id == ExternalAgent.AUTO:
        agent_id = auto_select_agent(message)
        logger.info("agent_auto_selected", agent=agent_id.value)
    
    profile = AGENT_PROFILES.get(agent_id)
    if not profile:
        return AgentResponse(
            agent_id=agent_id.value,
            agent_name="unknown",
            content="",
            model_used="",
            latency_ms=0,
            success=False,
            error=f"Unknown agent: {agent_id}",
        )
    
    if not profile.enabled:
        return AgentResponse(
            agent_id=agent_id.value,
            agent_name=profile.name,
            content="",
            model_used=profile.model,
            latency_ms=0,
            success=False,
            error=f"Agent {profile.name} is disabled",
        )
    
    # Check API key
    api_key = os.environ.get(profile.api_key_env, "")
    if not api_key:
        return AgentResponse(
            agent_id=agent_id.value,
            agent_name=profile.name,
            content="",
            model_used=profile.model,
            latency_ms=0,
            success=False,
            error=f"API key not configured: {profile.api_key_env}",
        )
    
    start = time.time()
    
    try:
        if agent_id == ExternalAgent.MANUS:
            result = await _execute_manus(profile, api_key, message, context, system_prompt, timeout)
        elif agent_id == ExternalAgent.PERPLEXITY:
            result = await _execute_perplexity(profile, api_key, message, context, system_prompt, timeout)
        elif agent_id in (ExternalAgent.KIMI, ExternalAgent.GROK):
            result = await _execute_openai_compatible(profile, api_key, message, context, system_prompt, timeout)
        elif agent_id == ExternalAgent.GEMINI:
            result = await _execute_gemini(profile, api_key, message, context, system_prompt, timeout)
        else:
            result = AgentResponse(
                agent_id=agent_id.value,
                agent_name=profile.name,
                content="",
                model_used=profile.model,
                latency_ms=0,
                success=False,
                error=f"No executor for agent: {agent_id}",
            )
    except Exception as e:
        latency = (time.time() - start) * 1000
        logger.error("agent_execution_failed", agent=agent_id.value, error=str(e))
        result = AgentResponse(
            agent_id=agent_id.value,
            agent_name=profile.name,
            content="",
            model_used=profile.model,
            latency_ms=latency,
            success=False,
            error=str(e),
        )
    
    result.latency_ms = (time.time() - start) * 1000
    logger.info(
        "agent_execution_complete",
        agent=result.agent_id,
        success=result.success,
        latency_ms=round(result.latency_ms),
        tokens=result.tokens_used,
    )
    return result


# ── Provider-Specific Executors ───────────────────────────────────────────────

async def _execute_manus(
    profile: AgentProfile,
    api_key: str,
    message: str,
    context: str,
    system_prompt: str,
    timeout: float,
) -> AgentResponse:
    """Execute via Manus API v2 (task.create + poll)."""
    from tools.manus_bridge import create_task, wait_for_completion
    
    # Inject context into the prompt
    full_prompt = _build_contextual_prompt(message, context, system_prompt)
    
    # Create task (synchronous — run in threadpool)
    loop = asyncio.get_event_loop()
    task_result = await loop.run_in_executor(
        None, lambda: create_task(full_prompt, account="google")
    )
    
    task_id = task_result.get("task_id")
    if not task_id:
        return AgentResponse(
            agent_id=profile.agent_id.value,
            agent_name=profile.name,
            content="",
            model_used=profile.model,
            latency_ms=0,
            success=False,
            error="Manus API did not return a task_id",
        )
    
    # Wait for completion
    try:
        result = await loop.run_in_executor(
            None, lambda: wait_for_completion(task_id, timeout=timeout, account="google")
        )
        content = result.get("output", result.get("content", ""))
    except Exception as e:
        content = ""
        return AgentResponse(
            agent_id=profile.agent_id.value,
            agent_name=profile.name,
            content=content,
            model_used=profile.model,
            latency_ms=0,
            success=False,
            error=f"Manus task failed: {e}",
            metadata={"task_id": task_id},
        )
    
    return AgentResponse(
        agent_id=profile.agent_id.value,
        agent_name=profile.name,
        content=content,
        model_used=profile.model,
        latency_ms=0,
        success=True,
        metadata={"task_id": task_id},
    )


async def _execute_perplexity(
    profile: AgentProfile,
    api_key: str,
    message: str,
    context: str,
    system_prompt: str,
    timeout: float,
) -> AgentResponse:
    """Execute via Perplexity API (chat/completions with sonar-reasoning-pro)."""
    messages = _build_messages(message, context, system_prompt or (
        "Eres un investigador experto. Responde con fuentes citadas. "
        "Usa información en tiempo real de la web."
    ))
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{profile.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": profile.model,
                "messages": messages,
                "search_recency_filter": "day",  # Forzar búsqueda del último día
                "web_search_options": {
                    "search_context_size": "high",  # Más contexto de búsqueda
                },
                "return_related_questions": False,
            },
        )
        resp.raise_for_status()
        data = resp.json()
    
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    citations = data.get("citations", [])
    usage = data.get("usage", {})
    
    return AgentResponse(
        agent_id=profile.agent_id.value,
        agent_name=profile.name,
        content=content,
        model_used=profile.model,
        latency_ms=0,
        tokens_used=usage.get("total_tokens", 0),
        sources=citations,
        success=True,
    )


async def _execute_openai_compatible(
    profile: AgentProfile,
    api_key: str,
    message: str,
    context: str,
    system_prompt: str,
    timeout: float,
) -> AgentResponse:
    """Execute via OpenAI-compatible API (Kimi via OpenRouter, Grok via xAI)."""
    messages = _build_messages(message, context, system_prompt or (
        "Eres El Monstruo, un asistente técnico preciso y directo. "
        "Responde de forma concisa y útil."
    ))
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # OpenRouter requires extra headers
    if "openrouter" in profile.base_url:
        headers["HTTP-Referer"] = "https://el-monstruo.app"
        headers["X-Title"] = "El Monstruo"
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{profile.base_url}/chat/completions",
            headers=headers,
            json={
                "model": profile.model,
                "messages": messages,
                "max_tokens": 4096,
            },
        )
        resp.raise_for_status()
        data = resp.json()
    
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = data.get("usage", {})
    
    return AgentResponse(
        agent_id=profile.agent_id.value,
        agent_name=profile.name,
        content=content,
        model_used=data.get("model", profile.model),
        latency_ms=0,
        tokens_used=usage.get("total_tokens", 0),
        success=True,
    )


async def _execute_gemini(
    profile: AgentProfile,
    api_key: str,
    message: str,
    context: str,
    system_prompt: str,
    timeout: float,
) -> AgentResponse:
    """Execute via Google Gemini API (generateContent)."""
    sys_prompt = system_prompt or (
        "Eres El Monstruo, un asistente de análisis profundo. "
        "Proporciona respuestas exhaustivas y bien estructuradas."
    )
    
    # Build content parts
    parts = []
    if context:
        parts.append({"text": f"[CONTEXTO DE CONVERSACIÓN PREVIA]\n{context}\n[FIN CONTEXTO]"})
    parts.append({"text": message})
    
    payload = {
        "contents": [{"parts": parts}],
        "systemInstruction": {"parts": [{"text": sys_prompt}]},
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.7,
        },
    }
    
    url = (
        f"{profile.base_url}/models/{profile.model}:generateContent"
        f"?key={api_key}"
    )
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
    
    # Extract content from Gemini response
    candidates = data.get("candidates", [])
    if candidates:
        content_parts = candidates[0].get("content", {}).get("parts", [])
        content = "\n".join(p.get("text", "") for p in content_parts)
    else:
        content = ""
    
    usage = data.get("usageMetadata", {})
    total_tokens = usage.get("totalTokenCount", 0)
    
    return AgentResponse(
        agent_id=profile.agent_id.value,
        agent_name=profile.name,
        content=content,
        model_used=profile.model,
        latency_ms=0,
        tokens_used=total_tokens,
        success=True,
    )


# ── Context Building ──────────────────────────────────────────────────────────

def _build_contextual_prompt(
    message: str,
    context: str,
    system_prompt: str,
) -> str:
    """Build a full prompt with context for agents that take a single string (Manus)."""
    parts = []
    if system_prompt:
        parts.append(f"INSTRUCCIONES: {system_prompt}")
    if context:
        parts.append(f"\n--- CONTEXTO DE CONVERSACIÓN PREVIA ---\n{context}\n--- FIN CONTEXTO ---")
    parts.append(f"\nTAREA ACTUAL: {message}")
    return "\n".join(parts)


def _build_messages(
    message: str,
    context: str,
    system_prompt: str,
) -> list[dict[str, str]]:
    """Build OpenAI-compatible messages array with context injection."""
    messages = []
    
    # System prompt
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # Context as assistant memory
    if context:
        messages.append({
            "role": "system",
            "content": (
                f"[MEMORIA DE CONVERSACIÓN PREVIA]\n{context}\n"
                "[FIN MEMORIA — Usa esta información para mantener continuidad.]"
            ),
        })
    
    # User message
    messages.append({"role": "user", "content": message})
    
    return messages


# ── Registry Status ───────────────────────────────────────────────────────────

def get_available_agents() -> list[dict[str, Any]]:
    """Return list of available agents with their status."""
    agents = []
    for agent_id, profile in AGENT_PROFILES.items():
        api_key = os.environ.get(profile.api_key_env, "")
        agents.append({
            "id": agent_id.value,
            "name": profile.name,
            "description": profile.description,
            "model": profile.model,
            "strengths": profile.strengths,
            "enabled": profile.enabled,
            "configured": bool(api_key),
            "cost_per_1k_input": profile.cost_per_1k_input,
            "cost_per_1k_output": profile.cost_per_1k_output,
        })
    return agents


def get_agent_status() -> dict[str, Any]:
    """Return full registry status for /v1/agents/external endpoint."""
    agents = get_available_agents()
    configured = sum(1 for a in agents if a["configured"])
    enabled = sum(1 for a in agents if a["enabled"])
    return {
        "total_agents": len(agents),
        "configured_agents": configured,
        "enabled_agents": enabled,
        "agents": agents,
    }
