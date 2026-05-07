# kernel/milestones/__init__.py
"""
DSC-as-Contract para hitos del Monstruo (DSC-G-017).

Cualquier declaracion de hito (PIPELINE_TECNICO_FUNCIONAL, PRODUCTO_COMERCIALIZABLE,
etc.) debe pasar por kernel.milestones.declare. Texto en bridge.md, en commits, o
en chat NO declara nada — solo este modulo, contra los gates en gates.yaml.

Origen: DSC-G-017 (DSC-as-Contract), 2026-05-07.
Refuerza: DSC-G-014 (PIPELINE TECNICO != PRODUCTO COMERCIALIZABLE).
Texto puede ser desobedecido. Codigo no.
"""
from .declare import (
    GateFailure,
    GateResult,
    MilestoneDeclarationRejected,
    declare,
    evaluate_milestone,
)

__all__ = [
    "GateFailure",
    "GateResult",
    "MilestoneDeclarationRejected",
    "declare",
    "evaluate_milestone",
]
