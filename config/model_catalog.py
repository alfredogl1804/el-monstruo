"""El Monstruo — Catálogo de Modelos Unificado
Sprint 25 | Baseline de Verdad | 22 abril 2026

CADA model_id fue verificado contra la API real del proveedor.
Sprint 25 changes:
  - gpt-5.4 model_id: gpt-5.4 → gpt-5.4-pro-2026-03-05 (flagship pinned)
  - claude-opus-4-7 confirmed as latest opus (validated Anthropic /v1/models)
  - gemini-3.1-pro-preview confirmed (validated Google generativelanguage API)
  - All validated dates updated to 2026-04-22
"""

# ===================== CATÁLOGO VALIDADO 22 ABRIL 2026 (Sprint 25 Baseline) =====================

MODELS: dict = {
    # ─── TIER 1: Flagship (razonamiento complejo, agéntico) ───
    "gpt-5.4": {
        "provider": "openai",
        "model_id": "gpt-5.4-pro-2026-03-05",  # Sprint 25: pinned to flagship snapshot — validated OpenAI /v1/models 2026-04-22
        "litellm_alias": "gpt-5",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "context_window": 1_000_000,
        "max_completion_tokens": 4000,
        "use_max_completion_tokens": True,
        "pricing": {"input": 2.50, "output": 10.00},  # $/M tokens
        "roles": [
            "estratega",
            "sintetizador",
            "clasificador",
            "planificador",
            "ejecutor",
        ],
        "validated": "2026-04-22",
        "source": "https://developers.openai.com/api/docs/models",
    },
    "claude-opus-4-7": {
        "provider": "anthropic",
        "model_id": "claude-opus-4-7",  # Sprint 25: confirmed latest opus — validated Anthropic /v1/models 2026-04-22
        "litellm_alias": "claude-opus",
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": None,
        "context_window": 1_000_000,
        "max_tokens": 4096,
        "use_max_completion_tokens": False,
        "pricing": {"input": 5.00, "output": 25.00},
        "roles": ["analisis", "critico", "arquitecto", "codigo"],
        "validated": "2026-04-22",
        "source": "https://www.anthropic.com/news/claude-opus-4-7",
    },
    "claude-opus-4-6": {
        "provider": "anthropic",
        "model_id": "claude-opus-4-6",
        "litellm_alias": "claude-opus-prev",
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": None,
        "context_window": 1_000_000,  # 1M — validated 2026-04-12
        "max_tokens": 4096,
        "use_max_completion_tokens": False,
        "pricing": {"input": 5.00, "output": 25.00},
        "roles": ["analisis", "critico", "arquitecto"],
        "validated": "2026-04-12",
        "source": "https://platform.claude.com/docs/en/about-claude/models/overview",
    },
    # ─── TIER 2: Especialistas (código, investigación, razonamiento) ───
    "grok-4.20": {
        "provider": "xai",
        "model_id": "grok-4.20-0309-non-reasoning",  # non-reasoning for tool calling compat — validated 2026-04-16
        "litellm_alias": "grok",
        "api_key_env": "XAI_API_KEY",
        "base_url": "https://api.x.ai/v1",
        "context_window": 2_000_000,  # 2M — validated 2026-04-12 docs.x.ai
        "max_tokens": 4000,
        "use_max_completion_tokens": False,
        "pricing": {"input": 2.00, "output": 6.00},
        "roles": ["codigo", "creativo", "critico"],
        "validated": "2026-04-12",
        "source": "https://docs.x.ai/developers/models",
    },
    "deepseek-r1-0528": {
        "provider": "openrouter",
        "model_id": "deepseek/deepseek-r1-0528",
        "litellm_alias": "deepseek-r1",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "context_window": 163_840,  # 164K — validated 2026-04-12
        "max_tokens": 4000,
        "use_max_completion_tokens": False,
        "pricing": {"input": 0.50, "output": 2.15},
        "roles": ["razonador", "tecnico"],
        "validated": "2026-04-12",
        "source": "https://openrouter.ai/deepseek/deepseek-r1-0528",
    },
    "sonar-reasoning-pro": {
        "provider": "perplexity",
        "model_id": "sonar-reasoning-pro",
        "litellm_alias": "sonar-reasoning",
        "api_key_env": "SONAR_API_KEY",
        "base_url": "https://api.perplexity.ai/chat/completions",
        "context_window": 128_000,
        "max_tokens": 4000,
        "use_max_completion_tokens": False,
        "pricing": {"input": 2.00, "output": 8.00},
        "roles": ["investigador"],
        "validated": "2026-04-12",
        "source": "https://docs.perplexity.ai/docs/sonar/models",
    },
    # ─── TIER 3: Rápidos y baratos (clasificación, tareas masivas) ───
    "gpt-5.4-mini": {
        "provider": "openai",
        "model_id": "gpt-5.4-mini",
        "litellm_alias": "gpt-5-mini",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "context_window": 128_000,
        "max_tokens": 1000,
        "use_max_completion_tokens": True,
        "pricing": {"input": 0.75, "output": 3.00},
        "roles": ["clasificador_rapido"],
        "validated": "2026-04-12",
        "source": "https://developers.openai.com/api/docs/models",
    },
    "claude-sonnet-4-6": {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-6",
        "litellm_alias": "claude-sonnet",
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": None,
        "context_window": 1_000_000,  # 1M — validated 2026-04-12
        "max_tokens": 4096,
        "use_max_completion_tokens": False,
        "pricing": {"input": 3.00, "output": 15.00},
        "roles": ["codigo", "ejecutor"],
        "validated": "2026-04-12",
        "source": "https://platform.claude.com/docs/en/about-claude/models/overview",
    },
    "gemini-3.1-flash-lite": {
        "provider": "google",
        "model_id": "gemini-3.1-flash-lite-preview",
        "litellm_alias": "gemini-flash",
        "api_key_env": "GEMINI_API_KEY",
        "base_url": None,
        "context_window": 1_000_000,
        "max_tokens": 4096,
        "use_max_completion_tokens": False,
        "pricing": {"input": 0.00, "output": 0.00},  # Free tier
        "roles": ["chat_rapido", "background"],
        "validated": "2026-04-12",
        "source": "https://ai.google.dev/gemini-api/docs/models",
    },
    "gemini-3.1-pro": {
        "provider": "google",
        "model_id": "gemini-3.1-pro-preview",  # Sprint 25: confirmed — validated Google generativelanguage API 2026-04-22
        "litellm_alias": "gemini-pro",
        "api_key_env": "GEMINI_API_KEY",
        "base_url": None,
        "context_window": 1_000_000,
        "max_tokens": 4000,
        "use_max_completion_tokens": False,
        "pricing": {"input": 1.25, "output": 5.00},
        "roles": ["creativo", "multimodal"],
        "validated": "2026-04-22",
        "source": "https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview",
    },
    "kimi-k2.5": {
        "provider": "openrouter",
        "model_id": "moonshotai/kimi-k2.5",
        "litellm_alias": "kimi",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "context_window": 262_000,
        "max_tokens": 4000,
        "use_max_completion_tokens": False,
        "pricing": {
            "input": 0.3827,
            "output": 1.72,
        },  # CORREGIDO: $0.38 no $0.60 — validated 2026-04-12
        "roles": ["motor_barato", "background"],
        "validated": "2026-04-12",
        "source": "https://openrouter.ai/moonshotai/kimi-k2.5",
    },
    "sonar-pro": {
        "provider": "perplexity",
        "model_id": "sonar-pro",
        "litellm_alias": "sonar-pro",
        "api_key_env": "SONAR_API_KEY",
        "base_url": "https://api.perplexity.ai/chat/completions",
        "context_window": 200_000,
        "max_tokens": 4000,
        "use_max_completion_tokens": False,
        "pricing": {"input": 3.00, "output": 15.00},
        "roles": ["investigador_general"],
        "validated": "2026-04-12",
        "source": "https://docs.perplexity.ai/docs/sonar/models",
    },
    # ─── EMBEDDINGS ───
    "text-embedding-3-small": {
        "provider": "openai",
        "model_id": "text-embedding-3-small",
        "litellm_alias": "embeddings",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "roles": ["embeddings"],
        "validated": "2026-04-12",
        "source": "https://developers.openai.com/api/docs/models",
    },
}


# ===================== FALLBACK CHAINS (by role) =====================

FALLBACK_CHAINS: dict[str, list[str]] = {
    "estratega": ["gpt-5.4", "claude-opus-4-7", "claude-opus-4-6", "gemini-3.1-pro"],
    "investigador": ["sonar-reasoning-pro", "sonar-pro", "grok-4.20", "gpt-5.4"],
    "razonador": ["deepseek-r1-0528", "gpt-5.4", "claude-opus-4-7"],
    "sintetizador": ["gpt-5.4", "claude-opus-4-7", "gemini-3.1-pro"],
    "critico": ["grok-4.20", "deepseek-r1-0528", "claude-opus-4-7"],
    "creativo": ["gemini-3.1-pro", "gpt-5.4", "claude-opus-4-7"],
    "codigo": ["claude-opus-4-7", "claude-sonnet-4-6", "grok-4.20", "deepseek-r1-0528"],
    "analisis": ["claude-opus-4-7", "gpt-5.4", "deepseek-r1-0528"],
    "motor_barato": ["kimi-k2.5", "gemini-3.1-flash-lite", "gpt-5.4-mini"],
    "clasificador": ["gpt-5.4-mini", "kimi-k2.5", "gemini-3.1-flash-lite"],
    "planificador": ["gpt-5.4", "claude-opus-4-7", "gemini-3.1-pro"],
    "ejecutor": ["gpt-5.4", "claude-sonnet-4-6", "grok-4.20"],
    "arquitecto": ["claude-opus-4-7", "gpt-5.4", "grok-4.20"],
    "chat_rapido": ["gemini-3.1-flash-lite", "gpt-5.4-mini", "kimi-k2.5"],
}


# ===================== HELPER FUNCTIONS =====================


def get_model(name: str) -> dict:
    """Get model config by catalog name. Raises KeyError if not found."""
    return MODELS[name]


def get_litellm_alias(name: str) -> str:
    """Get the LiteLLM alias for a catalog model name."""
    return MODELS[name]["litellm_alias"]


def get_models_for_role(role: str) -> list[str]:
    """Get all model names that have a given role."""
    return [name for name, cfg in MODELS.items() if role in cfg.get("roles", [])]


def get_fallback_chain(role: str) -> list[str]:
    """Get the fallback chain for a role. Returns empty list if role unknown."""
    return FALLBACK_CHAINS.get(role, [])


# ===================== SPRINT 2 CANDIDATES =====================

SPRINT2_CANDIDATES: dict = {
    "gpt-5.4-nano": {
        "reason": "Ultra-barato $0.20/M para clasificación masiva",
        "source": "https://developers.openai.com/api/docs/models",
    },
    "deepseek-v3.2": {
        "reason": "Agentic + reasoning, más nuevo que R1, DSA attention",
        "source": "https://openrouter.ai/deepseek/deepseek-v3.2",
    },
    "sonar-deep-research": {
        "reason": "Investigación exhaustiva con cientos de fuentes",
        "source": "https://docs.perplexity.ai/docs/sonar/models",
    },
    "gemini-3-flash-preview": {
        "reason": "Tier medio entre flash-lite y pro",
        "source": "https://ai.google.dev/gemini-api/docs/models",
    },
}


# ===================== ALIAS (for health endpoint import) =====================
MODEL_CATALOG = MODELS
