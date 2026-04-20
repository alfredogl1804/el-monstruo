"""
El Monstruo — Config Module
Model catalog, LiteLLM configuration, and system settings.
"""

from config.model_catalog import (
    FALLBACK_CHAINS,
    MODELS,
    SPRINT2_CANDIDATES,
    get_fallback_chain,
    get_litellm_alias,
    get_model,
    get_models_for_role,
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
