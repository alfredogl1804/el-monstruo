"""kernel/marketplace — Marketplace de Templates (Sprint 62.4)"""
from kernel.marketplace.marketplace import (
    Marketplace,
    TemplateMetadata,
    TemplateNoEncontrado,
    TemplateIncompatible,
    get_marketplace,
    init_marketplace,
    BUILTIN_TEMPLATES,
    MONSTRUO_VERSION,
)

__all__ = [
    "Marketplace", "TemplateMetadata",
    "TemplateNoEncontrado", "TemplateIncompatible",
    "get_marketplace", "init_marketplace",
    "BUILTIN_TEMPLATES", "MONSTRUO_VERSION",
]
