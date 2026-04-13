"""
El Monstruo — Prompts Module
System prompts, brain prompts, and user dossier for the sovereign AI.
"""

from prompts.system_prompts import (
    get_brain_prompt,
    get_classifier_prompt,
    get_user_dossier,
    get_available_brains,
    BRAIN_PROMPTS,
    CLASSIFIER_PROMPT,
    USER_DOSSIER,
)

__all__ = [
    "get_brain_prompt",
    "get_classifier_prompt",
    "get_user_dossier",
    "get_available_brains",
    "BRAIN_PROMPTS",
    "CLASSIFIER_PROMPT",
    "USER_DOSSIER",
]
