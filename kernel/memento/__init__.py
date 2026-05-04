"""
El Monstruo — Capa Memoria Soberana (Memento)
==============================================

Módulo del kernel que implementa la Capa 8 — Capa Memento del Objetivo #9
(Transversalidad). Convierte el folklore anti-Síndrome-Dory disperso en
hilos Manus en infraestructura formal con contratos auditables.

Sprint: Memento (Capa Memoria Soberana v1.0)
Fecha: 2026-05-04
Autor: Manus Ejecutor (Hilo A)

Public API:
    MementoValidator       — clase principal, valida contexto operativo
    ValidationResult       — modelo del resultado de una validación
    Discrepancy            — modelo del detalle de discrepancia
    MementoValidationRequest — modelo del request HTTP
    CriticalOperation      — modelo de operación crítica del catálogo
    SourceOfTruth          — modelo de fuente de verdad del catálogo

Uso típico (Bloque 2 — sin endpoint todavía):

    from kernel.memento import MementoValidator

    validator = MementoValidator(catalog=critical_ops, sources=sources_dict)
    result = await validator.validate(
        operation="sql_against_production",
        context_used={"host": "...", "user": "...", "credential_hash_first_8": "..."},
        hilo_id="hilo_manus_ticketlike",
    )
    if not result.proceed:
        raise PermissionError(result.remediation)
"""

from kernel.memento.models import (
    CriticalOperation,
    Discrepancy,
    MementoValidationRequest,
    SourceOfTruth,
    ValidationResult,
    ValidationStatus,
)
from kernel.memento.validator import MementoValidator

__version__ = "1.0.0-sprint-memento-b2"

__all__ = [
    "MementoValidator",
    "ValidationResult",
    "ValidationStatus",
    "Discrepancy",
    "MementoValidationRequest",
    "CriticalOperation",
    "SourceOfTruth",
    "__version__",
]
