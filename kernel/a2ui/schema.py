"""
kernel/a2ui/schema.py - A2UI Protocol Schema v1.0

Pydantic models para validar componentes A2UI antes de enviarlos al WebSocket
hacia la app Flutter. Cualquier output de Embrion/orchestrator que pretenda
ser A2UI DEBE validar contra este schema.

Si validacion falla: fallback automatico a Markdown plain + warning interno.
Disciplina anti-Dory: la UX del usuario nunca se rompe.

Spec firmado: bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md (Cowork T2 delegada)
Sprint origen: MOBILE_1B Tarea T1 (kernel side)
DSC: DSC-MO-011 Embryo Patch Lane v1 (Capa 8 Memento)
"""
from __future__ import annotations

from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Constantes canonizadas
# ============================================================================

A2UI_VERSION = "1.0"

A2UI_WHITELIST_TYPES = frozenset({
    # Contenedores (3)
    "Stack",
    "Card",
    "Section",
    # Contenido (6)
    "Text",
    "Markdown",
    "Image",
    "Link",
    "Code",
    "Divider",
    # Accion (2)
    "Button",
    "ButtonGroup",
    # Datos (3)
    "KeyValueList",
    "Table",
    "Badge",
    # Progreso (2)
    "Progress",
    "Stepper",
    # Especializados Monstruo (3)
    "EmpresaResultCard",
    "LeadCard",
    "ContenidoCard",
})


# ============================================================================
# Modelo base
# ============================================================================

class A2UIComponent(BaseModel):
    """
    Componente A2UI recursivo. Todo nodo del arbol tiene type, props y
    opcionalmente children.

    El tipo debe estar en A2UI_WHITELIST_TYPES o la validacion falla.
    """
    type: str
    props: dict[str, Any] = Field(default_factory=dict)
    children: list["A2UIComponent"] = Field(default_factory=list)

    @field_validator("type")
    @classmethod
    def validate_type_in_whitelist(cls, v: str) -> str:
        if v not in A2UI_WHITELIST_TYPES:
            raise ValueError(
                f"A2UI type '{v}' no esta en whitelist v{A2UI_VERSION}. "
                f"Tipos validos: {sorted(A2UI_WHITELIST_TYPES)}"
            )
        return v


# Forward reference para el campo recursivo children
A2UIComponent.model_rebuild()


# ============================================================================
# Documento A2UI completo
# ============================================================================

class A2UIDocument(BaseModel):
    """
    Documento A2UI completo. Es lo que el kernel envia al WebSocket.

    Formato canonico:
    {
        "a2ui_version": "1.0",
        "root": { ...A2UIComponent... }
    }
    """
    a2ui_version: str = Field(default=A2UI_VERSION)
    root: A2UIComponent

    @field_validator("a2ui_version")
    @classmethod
    def validate_version_compatible(cls, v: str) -> str:
        major, _ = v.split(".", 1)
        expected_major, _ = A2UI_VERSION.split(".", 1)
        if major != expected_major:
            raise ValueError(
                f"A2UI version major incompatible. Recibido: {v}, "
                f"soportado: {A2UI_VERSION}"
            )
        return v


# ============================================================================
# Eventos de accion del usuario
# ============================================================================

class A2UIAction(BaseModel):
    """
    Evento generado por la app cuando el usuario interactua con un componente
    A2UI (ej. tap en Button con action_id).

    La app envia esto al kernel via WebSocket message tipo a2ui_action.
    """
    type: Literal["a2ui_action"] = "a2ui_action"
    action_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    thread_id: Optional[str] = None
    component_path: Optional[str] = None
    timestamp: Optional[str] = None


# ============================================================================
# Validacion + fallback
# ============================================================================

def validate_a2ui_document(payload: dict[str, Any]) -> tuple[bool, Optional[A2UIDocument], Optional[str]]:
    """
    Valida un payload contra el schema A2UI v1.0.

    Returns:
        (is_valid, document_or_none, error_message_or_none)

    Si valido: (True, A2UIDocument, None)
    Si invalido: (False, None, error_str)
    """
    try:
        doc = A2UIDocument.model_validate(payload)
        return True, doc, None
    except Exception as e:
        return False, None, str(e)


def fallback_to_markdown(original_payload: Any, error: str) -> A2UIDocument:
    """
    Genera un A2UIDocument valido con un solo componente Markdown que muestra
    el contenido original como texto plano. Disciplina anti-Dory: la UX nunca
    se rompe aunque un Embrion alucine un tipo invalido.

    El warning queda en log interno, no en UI del usuario.
    """
    if isinstance(original_payload, dict):
        # Intentar extraer texto si el payload tenia algo legible
        fallback_text = str(original_payload.get("root", original_payload))
    else:
        fallback_text = str(original_payload)

    return A2UIDocument(
        a2ui_version=A2UI_VERSION,
        root=A2UIComponent(
            type="Markdown",
            props={"value": fallback_text},
            children=[],
        ),
    )


# ============================================================================
# Helpers de logging
# ============================================================================

def log_a2ui_validation_failure(error: str, payload_preview: str) -> None:
    """
    Hook para Capa 8 Memento: registra fallos de validacion A2UI sin
    interrumpir flujo de UX. Implementacion futura: escribir a error_memory.
    """
    # Placeholder - implementacion completa requiere wiring con kernel.error_memory
    import logging
    logger = logging.getLogger("kernel.a2ui")
    logger.warning(
        "A2UI validation failed. Falling back to Markdown. Error: %s | "
        "Payload preview: %s",
        error,
        payload_preview[:200],
    )
