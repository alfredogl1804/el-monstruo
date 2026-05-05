"""
Sprint 87.1 Bloque 3 — Steps LLM reales conectados al Catastro.

Cada step:
1. Consulta CatastroRuntimeClient en runtime → modelo elegido + selection metadata
2. Ejecuta call LLM real con Pydantic Structured Outputs (semilla 39)
3. Persiste contenido REAL (no stub) en e2e_step_log
4. Fallback heurístico determinístico si OPENAI_API_KEY ausente

Brand DNA: errores tipados como `e2e_step_llm_*_failed`.
"""
from kernel.e2e.steps.llm_step import (
    StepLLMOutput,
    run_llm_step,
    StepConceptOutput,
    StepICPOutput,
    StepNamingOutput,
    StepBrandingOutput,
    StepCopyOutput,
    StepEstrategiaOutput,
    StepFinanzasOutput,
)

__all__ = [
    "StepLLMOutput",
    "run_llm_step",
    "StepConceptOutput",
    "StepICPOutput",
    "StepNamingOutput",
    "StepBrandingOutput",
    "StepCopyOutput",
    "StepEstrategiaOutput",
    "StepFinanzasOutput",
]
