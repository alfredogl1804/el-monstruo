"""
kernel/a2ui — Agent-to-User-Interface protocol v1.0

Contrato JSON entre el kernel del Monstruo y la app Flutter para generar
interfaces dinamicas que la app renderiza sin que el kernel necesite saber
Flutter ni la app necesite hardcodear pantallas.

Spec firmado: bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md
Origen: DSC-MO-011 (Capa 8 Memento aplicada a rendering)
Whitelist v1: 16 tipos basicos + 3 especializados Monstruo.
"""

from kernel.a2ui.schema import (
    A2UI_VERSION,
    A2UI_WHITELIST_TYPES,
    A2UIAction,
    A2UIComponent,
    A2UIDocument,
    fallback_to_markdown,
    validate_a2ui_document,
)

__all__ = [
    "A2UIComponent",
    "A2UIDocument",
    "A2UIAction",
    "validate_a2ui_document",
    "fallback_to_markdown",
    "A2UI_WHITELIST_TYPES",
    "A2UI_VERSION",
]
