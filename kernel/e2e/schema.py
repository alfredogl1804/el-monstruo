"""
Sprint 87 — Schema Pydantic para e2e_runs y e2e_step_log.

Espeja la migration 021_sprint87_e2e_schema.sql.
Brand DNA: nombres directos, error formats {module}_{action}_{failure_type}.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# =================== Enums ===================


class EstadoRun(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_JUDGMENT = "awaiting_judgment"


class StepStatus(str, Enum):
    OK = "ok"
    FAILED = "failed"
    SKIPPED = "skipped"


class Veredicto(str, Enum):
    COMERCIALIZABLE = "comercializable"
    REWORK = "rework"
    DESCARTAR = "descartar"


class StepName(str, Enum):
    INTAKE = "INTAKE"
    INVESTIGAR = "INVESTIGAR"
    ARCHITECT = "ARCHITECT"
    ESTRATEGIA = "ESTRATEGIA"
    FINANZAS = "FINANZAS"
    CREATIVO = "CREATIVO"
    VENTAS = "VENTAS"
    TECNICO = "TECNICO"
    DEPLOY = "DEPLOY"
    CRITIC = "CRITIC"
    TRAFFIC = "TRAFFIC"
    VEREDICTO = "VEREDICTO"


# Pipeline lineal de 12 pasos según spec del Sprint 87.
# El orden es contractual y debe respetarse en pipeline.py.
PIPELINE_STEPS: List[tuple[int, StepName]] = [
    (1, StepName.INTAKE),
    (2, StepName.INVESTIGAR),
    (3, StepName.ARCHITECT),
    (4, StepName.ESTRATEGIA),
    (5, StepName.FINANZAS),
    (6, StepName.CREATIVO),
    (7, StepName.VENTAS),
    (8, StepName.TECNICO),
    (9, StepName.DEPLOY),
    (10, StepName.CRITIC),
    (11, StepName.TRAFFIC),
    (12, StepName.VEREDICTO),
]


# =================== Models ===================


class E2ERun(BaseModel):
    """Espejo Pydantic de la tabla e2e_runs."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., description="ID con formato 'e2e_<utc_epoch>_<hash6>'")
    frase_input: str = Field(..., min_length=3)
    estado: EstadoRun
    pipeline_step: int = Field(0, ge=0, le=12)
    brief: Optional[Dict[str, Any]] = None
    stack_decision: Optional[Dict[str, Any]] = None
    deploy_url: Optional[str] = None
    critic_visual_score: Optional[float] = Field(None, ge=0, le=100)
    veredicto_alfredo: Optional[Veredicto] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class E2EStepLog(BaseModel):
    """Espejo Pydantic de la tabla e2e_step_log."""

    model_config = ConfigDict(extra="ignore")

    id: Optional[int] = None  # BIGSERIAL
    run_id: str
    step_number: int = Field(..., ge=0, le=12)
    step_name: StepName
    embrion_id: Optional[str] = None
    modelo_consultado: Optional[str] = None
    input_payload: Optional[Dict[str, Any]] = None
    output_payload: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = Field(None, ge=0)
    status: StepStatus
    error_message: Optional[str] = None
    ts: Optional[datetime] = None


# =================== Request / Response ===================


class RunRequest(BaseModel):
    """Body de POST /v1/e2e/run."""

    frase_input: str = Field(..., min_length=3, max_length=2000)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RunResponse(BaseModel):
    """Respuesta inmediata de POST /v1/e2e/run."""

    run_id: str
    estado: EstadoRun
    accepted_at: datetime


class JudgmentRequest(BaseModel):
    """Body de POST /v1/e2e/runs/{run_id}/judgment."""

    veredicto: Veredicto
    nota: Optional[str] = Field(None, max_length=2000)


class DashboardSnapshot(BaseModel):
    """Snapshot agregado para GET /v1/e2e/dashboard."""

    runs_total: int
    runs_in_progress: int
    runs_completed: int
    runs_failed: int
    runs_awaiting_judgment: int
    veredictos_breakdown: Dict[str, int]
    avg_critic_visual_score: Optional[float] = None
    last_5_runs: List[Dict[str, Any]] = Field(default_factory=list)
