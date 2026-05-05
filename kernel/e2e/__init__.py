"""
Sprint 87 NUEVO — Ejecución Autónoma E2E.

Pipeline lineal de 12 pasos: frase de Alfredo → URL viva con tráfico real.
Patrón firme: consultar Catastro en runtime para cada step LLM (NO hardcodear modelos).
"""

from kernel.e2e.schema import (
    EstadoRun,
    StepName,
    StepStatus,
    Veredicto,
    E2ERun,
    E2EStepLog,
    RunRequest,
    RunResponse,
    JudgmentRequest,
    DashboardSnapshot,
    PIPELINE_STEPS,
)

__all__ = [
    "EstadoRun",
    "StepName",
    "StepStatus",
    "Veredicto",
    "E2ERun",
    "E2EStepLog",
    "RunRequest",
    "RunResponse",
    "JudgmentRequest",
    "DashboardSnapshot",
    "PIPELINE_STEPS",
]
