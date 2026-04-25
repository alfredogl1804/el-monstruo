"""
El Monstruo — Config Module
Model catalog, LiteLLM configuration, and system settings.
Sprint 29: Updated imports for SPRINT29_CANDIDATES + supports_temperature.
"""

from config.model_catalog import (
    FALLBACK_CHAINS,
    MODELS,
    SPRINT29_CANDIDATES,
    get_fallback_chain,
    get_litellm_alias,
    get_model,
    get_models_for_role,
    supports_temperature,
)

__all__ = [
    "MODELS",
    "FALLBACK_CHAINS",
    "SPRINT29_CANDIDATES",
    "get_model",
    "get_litellm_alias",
    "get_models_for_role",
    "get_fallback_chain",
    "supports_temperature",
]
