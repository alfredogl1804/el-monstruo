"""
B8 Magna Classifier — Anti-Dory FORGE v3.0

Clasifica acciones como MAGNA o STANDARD según reglas determinísticas.
Una acción MAGNA requiere aprobación de la Authority Matrix (B9).
Una acción STANDARD puede ejecutarse sin gate adicional.

Reglas de clasificación (v1.0):
- Cualquier acción que toque main → MAGNA
- Cualquier acción que escriba en Supabase producción → MAGNA
- Cualquier acción que despliegue a producción → MAGNA
- Cualquier acción que modifique credenciales → MAGNA
- Cualquier acción que declare "Dory muerto" → MAGNA
- Cualquier acción que apruebe R1 → MAGNA
- Cualquier acción que toque Fase 1 → MAGNA
- Cualquier acción que firme DSC → MAGNA
- Cualquier acción que cree PR → MAGNA
- Todo lo demás → STANDARD
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ActionLevel(Enum):
    MAGNA = "MAGNA"
    STANDARD = "STANDARD"


@dataclass
class ActionClassification:
    level: ActionLevel
    reason: str
    action_description: str
    requires_t1: bool


# Palabras clave que disparan clasificación MAGNA
MAGNA_TRIGGERS = frozenset([
    "merge_to_main",
    "push_to_main",
    "supabase_write_production",
    "deploy_production",
    "modify_credentials",
    "rotate_secrets",
    "declare_dory_dead",
    "approve_r1",
    "phase_1_action",
    "sign_dsc",
    "create_pr",
    "delete_table",
    "drop_migration",
    "override_guardian",
    "disable_rls",
    "expose_private_key",
])


def classify_action(
    action_type: str,
    description: str,
    metadata: Optional[dict] = None,
) -> ActionClassification:
    """
    Clasifica una acción como MAGNA o STANDARD.

    Args:
        action_type: Identificador del tipo de acción (ej. "merge_to_main").
        description: Descripción legible de la acción.
        metadata: Contexto adicional opcional.

    Returns:
        ActionClassification con nivel, razón y si requiere T1.
    """
    action_lower = action_type.lower().strip()

    # Regla 1: Coincidencia directa con triggers
    if action_lower in MAGNA_TRIGGERS:
        return ActionClassification(
            level=ActionLevel.MAGNA,
            reason=f"Action type '{action_type}' is in MAGNA_TRIGGERS set",
            action_description=description,
            requires_t1=True,
        )

    # Regla 2: Coincidencia parcial con keywords peligrosas
    danger_keywords = ["main", "production", "credential", "secret", "dory_dead", "phase_1", "private_key"]
    for keyword in danger_keywords:
        if keyword in action_lower:
            return ActionClassification(
                level=ActionLevel.MAGNA,
                reason=f"Action type contains danger keyword '{keyword}'",
                action_description=description,
                requires_t1=True,
            )

    # Regla 3: Metadata override (si metadata indica forzar MAGNA)
    if metadata and metadata.get("force_magna", False):
        return ActionClassification(
            level=ActionLevel.MAGNA,
            reason="Metadata flag 'force_magna' is True",
            action_description=description,
            requires_t1=True,
        )

    # Default: STANDARD
    return ActionClassification(
        level=ActionLevel.STANDARD,
        reason="No MAGNA triggers matched",
        action_description=description,
        requires_t1=False,
    )
