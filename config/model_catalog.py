"""El Monstruo — Catálogo de Modelos Unificado
Sprint 29 | 0.22.0-sprint29 | 25 abril 2026

CADA model_id fue verificado contra la API real del proveedor.
Sprint 29 changes:
  - BUG-2 FIX: gpt-5.4-pro-2026-03-05 → gpt-5.5 (flagship, /v1/responses API)
  - GPT-5.5 restriction: temperature NOT supported (HTTP 400 confirmed 2026-04-25)
  - gpt-5.4-mini → gpt-4.1-mini (Épica 1: worker económico)
  - Groq llama-4-scout-17b-16e-instruct added (Épica 5: fallback)
  - Together meta-llama/Llama-4-Scout-17B-16E-Instruct added (Épica 5: fallback)
  - Fallback chains extended with Groq/Together as last resort
  - grok-4.20 kept as-is (validated xAI API)
"""

# ===================== CATÁLOGO VALIDADO 25 ABRIL 2026 (Sprint 29) =====================

MODELS: dict = {
    # ─── TIER 1: Flagship (razonamiento complejo, agéntico) ───
    "gpt-5.5": {
        "provider": "openai",
        "model_id": "gpt-5.5",  # Sprint 29 BUG-2 FIX: was gpt-5.4-pro-2026-03-05
        "litellm_alias": "gpt-5",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "api_type": "responses",  # Sprint 29: uses /v1/responses API, NOT chat/completions
        "context_window": 1_000_000,
        "max_output_tokens": 16_384,
        "use_max_completion_tokens": False,  # Uses max_output_tokens param
        "supports_temperature": False,  # Sprint 29: HTTP 400 confirmed — temperature NOT supported
        "pricing": {"input": 2.50, "output": 10.00},  # $/M tokens
        "roles": [
            "estratega",
            "sintetizador",
            "clasificador",
            "planificador",
            "ejecutor",
        ],
        "validated": "2026-04-25",
        "source": "https://developers.openai.com/api/docs/models",
    },
    "claude-opus-4-7": {
        "provider": "anthropic",
        "model_id": "claude-opus-4-7",  # Sprint 25: confirmed latest opus
        "litellm_alias": "claude-opus",
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": None,
        "context_window": 1_000_000,
        "max_tokens": 4096,
        "use_max_completion_tokens": False,
        "supports_temperature": True,
        "pricing": {"input": 5.00, "output": 25.00},
        "roles": ["analisis", "critico", "arquitecto", "codigo"],
        "validated": "2026-04-25",
        "source": "https://www.anthropic.com/news/claude-opus-4-7",
    },
    "claude-opus-4-6": {
        "provider": "anthropic",
        "model_id": "claude-opus-4-6",
        "litellm_alias": "claude-opus-prev",
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": None,
        "context_window": 1_000_000,
        "max_tokens": 4096,
        "use_max_completion_tokens": False,
        "supports_temperature": True,
        "pricing": {"input": 5.00, "output": 25.00},
        "roles": ["analisis", "critico", "arquitecto"],
        "validated": "2026-04-12",
        "source": "https://platform.claude.com/docs/en/about-claude/models/overview",
    },
    # ─── TIER 2: Especialistas (código, investigación, razonamiento) ───
    "grok-4.20": {
        "provider": "xai",
        "model_id": "grok-4.20-0309-non-reasoning",  # non-reasoning for tool calling compat
        "litellm_alias": "grok",
        "api_key_env": "XAI_API_KEY",
        "base_url": "https://api.x.ai/v1",
        "context_window": 2_000_000,
        "max_tokens": 4000,
        "use_max_completion_tokens": False,
        "supports_temperature": True,
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
        "context_window": 163_840,
        "max_tokens": 4000,
        "use_max_completion_tokens": False,
        "supports_temperature": True,
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
        "supports_temperature": True,
        "pricing": {"input": 2.00, "output": 8.00},
        "roles": ["investigador"],
        "validated": "2026-04-12",
        "source": "https://docs.perplexity.ai/docs/sonar/models",
    },
    # ─── TIER 3: Rápidos y baratos (clasificación, tareas masivas) ───
    "gpt-4.1-mini": {
        "provider": "openai",
        "model_id": "gpt-4.1-mini",  # Sprint 29: replaces gpt-5.4-mini as worker económico
        "litellm_alias": "gpt-4-mini",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "context_window": 1_048_576,  # 1M tokens
        "max_tokens": 16_384,
        "use_max_completion_tokens": True,
        "supports_temperature": True,
        "pricing": {"input": 0.40, "output": 1.60},  # $/M tokens — very cheap
        "roles": ["clasificador_rapido", "worker_economico"],
        "validated": "2026-04-25",
        "source": "https://developers.openai.com/api/docs/models",
    },
    "claude-sonnet-4-6": {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-6",
        "litellm_alias": "claude-sonnet",
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": None,
        "context_window": 1_000_000,
        "max_tokens": 4096,
        "use_max_completion_tokens": False,
        "supports_temperature": True,
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
        "supports_temperature": True,
        "pricing": {"input": 0.00, "output": 0.00},  # Free tier
        "roles": ["chat_rapido", "background", "worker_economico"],
        "validated": "2026-04-12",
        "source": "https://ai.google.dev/gemini-api/docs/models",
    },
    "gemini-3.1-pro": {
        "provider": "google",
        "model_id": "gemini-3.1-pro-preview",
        "litellm_alias": "gemini-pro",
        "api_key_env": "GEMINI_API_KEY",
        "base_url": None,
        "context_window": 1_000_000,
        "max_tokens": 4000,
        "use_max_completion_tokens": False,
        "supports_temperature": True,
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
        "supports_temperature": True,
        "pricing": {"input": 0.3827, "output": 1.72},
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
        "supports_temperature": True,
        "pricing": {"input": 3.00, "output": 15.00},
        "roles": ["investigador_general"],
        "validated": "2026-04-12",
        "source": "https://docs.perplexity.ai/docs/sonar/models",
    },
    # ─── TIER 4: Fallback económicos (Groq/Together — Épica 5) ───
    "groq-llama-scout": {
        "provider": "groq",
        "model_id": "meta-llama/llama-4-scout-17b-16e-instruct",
        "litellm_alias": "groq-llama",
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "context_window": 131_072,
        "max_tokens": 4096,
        "use_max_completion_tokens": False,
        "supports_temperature": True,
        "pricing": {"input": 0.11, "output": 0.34},  # $/M tokens — ultra cheap
        "roles": ["fallback", "worker_economico"],
        "validated": "2026-04-25",
        "source": "https://console.groq.com/docs/models",
    },
    "together-llama-scout": {
        "provider": "together",
        "model_id": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
        "litellm_alias": "together-llama",
        "api_key_env": "TOGETHER_API_KEY",
        "base_url": "https://api.together.xyz/v1",
        "context_window": 131_072,
        "max_tokens": 4096,
        "use_max_completion_tokens": False,
        "supports_temperature": True,
        "pricing": {"input": 0.18, "output": 0.59},  # $/M tokens
        "roles": ["fallback", "worker_economico"],
        "validated": "2026-04-25",
        "source": "https://docs.together.ai/docs/serverless-models",
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


# ===================== FALLBACK CHAINS (by role) — Sprint 29: +Groq/Together =====================

FALLBACK_CHAINS: dict[str, list[str]] = {
    "estratega": ["gpt-5.5", "claude-opus-4-7", "claude-opus-4-6", "gemini-3.1-pro", "groq-llama-scout"],
    "investigador": ["sonar-reasoning-pro", "sonar-pro", "grok-4.20", "gpt-5.5", "groq-llama-scout"],
    "razonador": ["deepseek-r1-0528", "gpt-5.5", "claude-opus-4-7", "together-llama-scout"],
    "sintetizador": ["gpt-5.5", "claude-opus-4-7", "gemini-3.1-pro", "groq-llama-scout"],
    "critico": ["grok-4.20", "deepseek-r1-0528", "claude-opus-4-7", "together-llama-scout"],
    "creativo": ["gemini-3.1-pro", "gpt-5.5", "claude-opus-4-7", "groq-llama-scout"],
    "codigo": ["claude-opus-4-7", "claude-sonnet-4-6", "grok-4.20", "deepseek-r1-0528", "together-llama-scout"],
    "analisis": ["claude-opus-4-7", "gpt-5.5", "deepseek-r1-0528", "groq-llama-scout"],
    "motor_barato": ["kimi-k2.5", "gemini-3.1-flash-lite", "gpt-4.1-mini", "groq-llama-scout", "together-llama-scout"],
    "clasificador": ["gpt-4.1-mini", "kimi-k2.5", "gemini-3.1-flash-lite", "groq-llama-scout"],
    "planificador": ["gpt-5.5", "claude-opus-4-7", "gemini-3.1-pro", "groq-llama-scout"],
    "ejecutor": ["gpt-5.5", "claude-sonnet-4-6", "grok-4.20", "together-llama-scout"],
    "arquitecto": ["claude-opus-4-7", "gpt-5.5", "grok-4.20", "together-llama-scout"],
    "chat_rapido": ["gemini-3.1-flash-lite", "gpt-4.1-mini", "kimi-k2.5", "groq-llama-scout"],
    "fallback": ["groq-llama-scout", "together-llama-scout", "gemini-3.1-flash-lite", "gpt-4.1-mini"],
    "worker_economico": ["gemini-3.1-flash-lite", "gpt-4.1-mini", "groq-llama-scout", "together-llama-scout"],
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


def supports_temperature(name: str) -> bool:
    """Check if a model supports the temperature parameter."""
    return MODELS.get(name, {}).get("supports_temperature", True)


# ===================== SPRINT 29 CANDIDATES =====================

SPRINT29_CANDIDATES: dict = {
    "gpt-5.5-pro": {
        "reason": "Pro variant of GPT-5.5 — same restrictions (no temperature), higher quality",
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
}


# ===================== ALIAS (for health endpoint import) =====================
MODEL_CATALOG = MODELS
