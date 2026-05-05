"""
El Catastro — Sistema de inteligencia viva sobre modelos IA externos.

Sprint 86 Bloques 1-5: Schema + Pipeline + Persistencia atómica + Trono Score + MCP Server catastro.recommend().

Macroárea 1 (Sprint 86): Inteligencia (LLMs)
  - llm_frontier (GPT, Claude, Gemini, xAI)
  - llm_open_source (Llama, Qwen, DeepSeek, Kimi, Mistral)
  - coding_llms (DeepSeek Coder, Qwen Coder, Codestral)
  - small_edge (Phi, Gemma, Qwen 1.5B-7B)

Sprints futuros:
  - 87: Macroárea 2 (Visión generativa) + validador adversarial
  - 88: Macroárea 3 (Agentes) + UI Next.js + 12 macroáreas totales

Componentes públicos del módulo:
  schema      — Pydantic models de las 5 tablas + tipos enum (Sprint 86 Bloque 1)
  pipeline    — Pipeline diario MVP (Sprint 86 Bloque 2)
  quorum      — QuorumValidator 2-de-3 + cross-validation (Sprint 86 Bloque 2)
  sources     — Clientes API REST oficiales (Sprint 86 Bloque 2)
  cron        — Entrypoint Railway scheduled task (Sprint 86 Bloque 2)
  persistence — Wiring atómico a Supabase via RPC PL/pgSQL (Sprint 86 Bloque 3)
  trono          — Cálculo Trono Score por dominio (Sprint 86 Bloque 4)
  recommendation — RecommendationEngine + cache LRU + modo degraded (Sprint 86 Bloque 5)
  catastro_routes— APIRouter REST /v1/catastro/* con auth Bearer (Sprint 86 Bloque 5)
  mcp_tools      — FastMCP sub-server con 4 tools (Sprint 86 Bloque 5)
"""
from __future__ import annotations

__version__ = "0.86.5"  # Sprint 86 Bloque 5 — MCP Server catastro.recommend()
__sprint__ = "86"
__bloque__ = "5"

# Re-exports públicos del módulo schema (poblados conforme se construye)
# Bloque 5 — MCP Server catastro.recommend()
from kernel.catastro.recommendation import (
    CATASTRO_TRONO_VIEW,
    DEFAULT_TOP_N,
    MAX_TOP_N,
    CatastroRecommendError,
    CatastroRecommendInvalidArgs,
    CatastroRecommendModeloNotFound,
    DominioInfo,
    ListDominiosResponse,
    ModeloDetallado,
    ModeloRecomendado,
    RecommendationEngine,
    RecommendationResponse,
    StatusSnapshot,
    build_default_db_factory,
)

# Bloque 4 — Trono Score
from kernel.catastro.trono import (
    DEFAULT_WEIGHTS,
    METRIC_FIELDS,
    CatastroTronoEmptyInput,
    CatastroTronoError,
    CatastroTronoInvalidDomain,
    CatastroTronoInvalidWeights,
    TronoCalculator,
    TronoResult,
    apply_results_to_models,
)

# Bloque 3 — Persistencia
from kernel.catastro.persistence import (
    CatastroPersistence,
    CatastroPersistError,
    CatastroPersistMissingClient,
    CatastroPersistRpcFailure,
    ErrorCategory,
    PersistResult,
    build_modelo_from_pipeline_persistible,
)

# Bloque 2 — Pipeline + Quorum
from kernel.catastro.pipeline import CatastroPipeline, PipelineRunResult
from kernel.catastro.quorum import (
    FieldType,
    FuenteVote,
    QuorumOutcome,
    QuorumResult,
    QuorumValidator,
)

# Bloque 1 — Schema
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
    # Bloque 1 — Schema
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
    # Bloque 2 — Pipeline + Quorum
    "CatastroPipeline",
    "PipelineRunResult",
    "QuorumValidator",
    "QuorumOutcome",
    "QuorumResult",
    "FieldType",
    "FuenteVote",
    # Bloque 3 — Persistencia
    "CatastroPersistence",
    "PersistResult",
    "CatastroPersistError",
    "CatastroPersistRpcFailure",
    "CatastroPersistMissingClient",
    "ErrorCategory",
    "build_modelo_from_pipeline_persistible",
    # Bloque 4 — Trono Score
    "TronoCalculator",
    "TronoResult",
    "DEFAULT_WEIGHTS",
    "METRIC_FIELDS",
    "CatastroTronoError",
    "CatastroTronoInvalidWeights",
    "CatastroTronoInvalidDomain",
    "CatastroTronoEmptyInput",
    "apply_results_to_models",
    # Bloque 5 — MCP Server
    "RecommendationEngine",
    "RecommendationResponse",
    "ModeloRecomendado",
    "ModeloDetallado",
    "DominioInfo",
    "ListDominiosResponse",
    "StatusSnapshot",
    "CatastroRecommendError",
    "CatastroRecommendInvalidArgs",
    "CatastroRecommendModeloNotFound",
    "DEFAULT_TOP_N",
    "MAX_TOP_N",
    "CATASTRO_TRONO_VIEW",
    "build_default_db_factory",
]
