"""
El Catastro — Sistema de inteligencia viva sobre modelos IA externos.

Sprint 86 Bloque 1: Schema Supabase + módulos cimentadores.

Macroárea 1 (Sprint 86): Inteligencia (LLMs)
  - llm_frontier (GPT, Claude, Gemini, xAI)
  - llm_open_source (Llama, Qwen, DeepSeek, Kimi, Mistral)
  - coding_llms (DeepSeek Coder, Qwen Coder, Codestral)
  - small_edge (Phi, Gemma, Qwen 1.5B-7B)

Sprints futuros:
  - 87: Macroárea 2 (Visión generativa) + validador adversarial
  - 88: Macroárea 3 (Agentes) + UI Next.js + 12 macroáreas totales

Componentes públicos del módulo:
  schema      — Pydantic models de las 5 tablas + tipos enum
  pipeline    — Pipeline diario MVP (Sprint 86 Bloque 2, próximo)
  sources     — Clientes API REST oficiales (Sprint 86 Bloque 3)
  trono       — Cálculo Trono Score por dominio (Sprint 86 Bloque 4)
  mcp         — Servidor MCP del Catastro (Sprint 86 Bloque 6)
"""
from __future__ import annotations

__version__ = "0.86.1"  # Sprint 86 Bloque 1
__sprint__ = "86"
__bloque__ = "1"

# Re-exports públicos del módulo schema (poblados conforme se construye)
from kernel.catastro.schema import (
    EstadoModelo,
    TipoLicencia,
    Macroarea,
    DominioInteligencia,
    PrioridadEvento,
    TipoEvento,
    RolCurador,
    CatastroModelo,
    CatastroHistorial,
    CatastroEvento,
    CatastroNota,
    CatastroCurador,
    FuenteEvidencia,
)

__all__ = [
    "__version__",
    "__sprint__",
    "__bloque__",
    "EstadoModelo",
    "TipoLicencia",
    "Macroarea",
    "DominioInteligencia",
    "PrioridadEvento",
    "TipoEvento",
    "RolCurador",
    "CatastroModelo",
    "CatastroHistorial",
    "CatastroEvento",
    "CatastroNota",
    "CatastroCurador",
    "FuenteEvidencia",
]
