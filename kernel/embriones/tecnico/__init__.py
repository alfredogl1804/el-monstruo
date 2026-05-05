"""
Embrión Técnico — análisis técnico de un brief de producto.

Sprint 87.1 Bloque 1.
Cierra deuda #2 del Sprint 87 NUEVO (Embriones Técnico + Ventas stubs).

Patrón:
- LLM-as-parser con Structured Outputs Pydantic (semilla 39 reaplicada)
- Capa Memento: lee OPENAI_API_KEY en runtime, fallback heurístico determinístico
- Brand DNA en errores: embrion_tecnico_*_failed
"""
from kernel.embriones.tecnico.embrion_tecnico import (
    EmbrionTecnico,
    EmbrionTecnicoReport,
    StackRecomendado,
    RiesgoTecnico,
    EMBRION_TECNICO_LLM_INVALIDO,
)

__all__ = [
    "EmbrionTecnico",
    "EmbrionTecnicoReport",
    "StackRecomendado",
    "RiesgoTecnico",
    "EMBRION_TECNICO_LLM_INVALIDO",
]
