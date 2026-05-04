"""
Pydantic models para la Capa Memento.

Espejo exacto de los schemas declarados en
bridge/sprint_memento_preinvestigation/spec_sprint_memento.md.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    """Resultados posibles de una validación Memento."""

    OK = "ok"
    DISCREPANCY_DETECTED = "discrepancy_detected"
    UNKNOWN_OPERATION = "unknown_operation"
    SOURCE_UNAVAILABLE = "source_unavailable"


class Discrepancy(BaseModel):
    """Detalle de una discrepancia detectada entre `context_used` y la fuente de verdad."""

    field: str = Field(..., description="Nombre del campo discrepante (ej. 'host', 'credential_hash_first_8')")
    context_used: Any = Field(..., description="Valor que el hilo declaró usar")
    source_of_truth: Any = Field(..., description="Valor real según la fuente de verdad")
    source: str = Field(..., description="Identificador de la fuente consultada (ej. 'skills/ticketlike-ops/references/credentials.md')")
    source_last_updated: Optional[datetime] = Field(None, description="Última actualización conocida de la fuente")


class MementoValidationRequest(BaseModel):
    """Request body para POST /v1/memento/validate (Bloque 3)."""

    hilo_id: str = Field(..., min_length=1, description="Identificador del hilo Manus que solicita validación")
    operation: str = Field(..., min_length=1, description="ID de la operación crítica (ej. 'sql_against_production')")
    context_used: Dict[str, Any] = Field(..., description="Contexto declarado por el hilo (host, user, hash, etc.)")
    intent_summary: Optional[str] = Field(None, description="Texto libre con el propósito de la operación")


class ValidationResult(BaseModel):
    """Resultado de una validación Memento."""

    validation_status: ValidationStatus
    proceed: bool = Field(..., description="True => hilo puede proceder; False => debe abortar")
    validation_id: str = Field(..., description="ID único formato 'mv_<timestamp>_<hash6>'")
    context_freshness_seconds: int = Field(0, description="Segundos desde la última actualización conocida de la fuente")
    discrepancy: Optional[Discrepancy] = None
    contamination_warning: bool = Field(False, description="v1.0: flag no bloqueante. v1.1: puede ser bloqueante")
    contamination_evidence: Optional[Dict[str, Any]] = None
    remediation: Optional[str] = Field(None, description="Instrucciones para remediar la situación si proceed=False")
    source_consulted: Optional[str] = Field(None, description="Ruta o identificador de la fuente consultada")


class CriticalOperation(BaseModel):
    """Modelo de una operación crítica del catálogo `memento_critical_operations`."""

    id: str
    nombre: str
    descripcion: str
    triggers: List[str]
    requires_validation: bool = True
    requires_confirmation: Optional[str] = None
    source_of_truth_ids: List[str] = Field(default_factory=list)
    activo: bool = True
    version: int = 1


class SourceOfTruth(BaseModel):
    """Modelo de una fuente de verdad del catálogo `memento_sources_of_truth`."""

    id: str
    nombre: str
    descripcion: str
    source_type: Literal["repo_file", "railway_env", "supabase_table", "external_dashboard", "env_var"]
    location: str
    parser_id: Optional[str] = None
    parser_config: Dict[str, Any] = Field(default_factory=dict)
    cache_ttl_seconds: int = 60
    last_known_update: Optional[datetime] = None
    last_known_hash: Optional[str] = None
    activo: bool = True


__all__ = [
    "ValidationStatus",
    "Discrepancy",
    "MementoValidationRequest",
    "ValidationResult",
    "CriticalOperation",
    "SourceOfTruth",
]
