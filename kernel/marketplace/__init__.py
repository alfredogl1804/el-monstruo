"""kernel/marketplace — Marketplace de Templates (Sprint 62.4)"""

from kernel.marketplace.marketplace import (
    BUILTIN_TEMPLATES,
    MONSTRUO_VERSION,
    Marketplace,
    TemplateIncompatible,
    TemplateMetadata,
    TemplateNoEncontrado,
    get_marketplace,
    init_marketplace,
)

__all__ = [
    "Marketplace",
    "TemplateMetadata",
    "TemplateNoEncontrado",
    "TemplateIncompatible",
    "get_marketplace",
    "init_marketplace",
    "BUILTIN_TEMPLATES",
    "MONSTRUO_VERSION",
]
