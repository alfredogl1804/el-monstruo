"""
El Monstruo — Config Module
Model catalog, LiteLLM configuration, and system settings.
"""

from config.model_catalog import (
    MODELS,
    FALLBACK_CHAINS,
    SPRINT2_CANDIDATES,
    get_model,
    get_litellm_alias,
    get_models_for_role,
    get_fallback_chain,
)

__all__ = [
    "MODELS",
    "FALLBACK_CHAINS",
    "SPRINT2_CANDIDATES",
    "get_model",
    "get_litellm_alias",
    "get_models_for_role",
    "get_fallback_chain",
]
