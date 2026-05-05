"""
El Catastro · Fuentes de evidencia.

Sprint 86 Bloque 2 — clientes API REST oficiales para extracción diaria
de datos sobre modelos IA. Cada cliente devuelve `RawSnapshot` (dict
crudo + payload_hash + fetched_at) sin transformar — la normalización
ocurre en el pipeline.

Fuentes activas:
  - artificial_analysis  (GPT/Claude/Gemini frontier benchmarks)
  - openrouter           (catalogo de modelos + pricing en vivo)
  - lmarena              (Arena Score via Hugging Face dataset)

Disciplina os.environ: cada cliente lee la API key dentro de su método
`fetch()`, no en `__init__` ni a nivel de módulo. Esto permite que
Railway inyecte secretos en runtime sin reiniciar el proceso.

[Hilo Manus Catastro] · 2026-05-04
"""
from __future__ import annotations

from kernel.catastro.sources.base import (
    BaseFuente,
    RawSnapshot,
    FuenteError,
    FuenteRateLimitError,
    FuenteTimeoutError,
    FuenteUnauthorizedError,
    FuenteUnavailableError,
)
from kernel.catastro.sources.artificial_analysis import ArtificialAnalysisFuente
from kernel.catastro.sources.openrouter import OpenRouterFuente
from kernel.catastro.sources.lmarena import LMArenaFuente
from kernel.catastro.sources.swe_bench import SWEBenchFuente
from kernel.catastro.sources.human_eval import HumanEvalFuente
from kernel.catastro.sources.mbpp import MBPPFuente
from kernel.catastro.sources.aime import AIMEFuente
from kernel.catastro.sources.gpqa import GPQAFuente
from kernel.catastro.sources.mmlu_pro import MMLUProFuente

__all__ = [
    "BaseFuente",
    "RawSnapshot",
    "FuenteError",
    "FuenteRateLimitError",
    "FuenteTimeoutError",
    "FuenteUnauthorizedError",
    "FuenteUnavailableError",
    "ArtificialAnalysisFuente",
    "OpenRouterFuente",
    "LMArenaFuente",
    "SWEBenchFuente",
    "HumanEvalFuente",
    "MBPPFuente",
    "AIMEFuente",
    "GPQAFuente",
    "MMLUProFuente",
]
