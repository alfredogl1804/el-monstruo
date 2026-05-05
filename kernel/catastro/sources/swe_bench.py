"""
El Catastro · Sources · SWE-bench Verified.

Cliente para extraer datos de BenchLM para SWE-bench Verified, 
la métrica anti-gaming de UC Berkeley.
Requiere que Lite >= Verified y Multilingual.python >= Verified - 10pp
para detectar gaming (overfitting al test set).

[Hilo Manus Catastro] · Sprint 86.5 · 2026-05-05
"""
from __future__ import annotations

import httpx
from typing import Any, Optional

from kernel.catastro.sources.base import (
    BaseFuente,
    FuenteRateLimitError,
    FuenteTimeoutError,
    FuenteUnavailableError,
    RawSnapshot,
)


class SWEBenchFuente(BaseFuente):
    """
    Fuente para SWE-bench Verified (BenchLM).
    Pública, no requiere API key.
    """

    nombre = "swe_bench"
    env_key = None  # API pública

    async def fetch(self, **kwargs: Any) -> RawSnapshot:
        if self.dry_run:
            return self._make_snapshot(
                payload=self._get_dry_run_payload(),
                url="https://benchlm.ai/api/v1/benchmarks/swe-bench-verified",
                metadata={"dry_run": True},
            )

        url = "https://benchlm.ai/api/v1/benchmarks/swe-bench-verified"
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(url)

                if response.status_code == 429:
                    raise FuenteRateLimitError(self.nombre, "Rate limit excedido en BenchLM")
                if response.status_code >= 500:
                    raise FuenteUnavailableError(self.nombre, f"Error {response.status_code} en BenchLM")
                
                response.raise_for_status()
                payload = response.json()

                return self._make_snapshot(
                    payload=payload,
                    url=url,
                    metadata={"status_code": response.status_code},
                )
        except httpx.TimeoutException as e:
            raise FuenteTimeoutError(self.nombre, f"Timeout conectando a {url}") from e
        except httpx.RequestError as e:
            raise FuenteUnavailableError(self.nombre, f"Error de red: {e}") from e

    @staticmethod
    def extract_scores(item: dict[str, Any]) -> dict[str, float]:
        """Extrae los scores descompuestos."""
        scores = {}
        if "verified_score" in item:
            scores["verified"] = float(item["verified_score"])
        if "lite_score" in item:
            scores["lite"] = float(item["lite_score"])
        if "multilingual_python_score" in item:
            scores["multilingual_python"] = float(item["multilingual_python_score"])
        return scores

    @staticmethod
    def detect_gaming(scores: dict[str, float]) -> bool:
        """
        Regla anti-gaming UC Berkeley:
        Gaming detectado si Verified > Lite o Verified > Multilingual.python + 10.
        """
        verified = scores.get("verified")
        lite = scores.get("lite")
        multi_py = scores.get("multilingual_python")

        if verified is None:
            return False

        if lite is not None and verified > lite:
            return True
        
        if multi_py is not None and verified > (multi_py + 10.0):
            return True

        return False

    def _get_dry_run_payload(self) -> dict[str, Any]:
        # Slugs alineados con dry_run de las 3 fuentes core
        # (gpt-5-5, claude-opus-4-7) para que el smoke E2E valide
        # el path completo: cross-source presence + coding enrichment.
        return {
            "data": [
                {
                    "model_id": "gpt-5-5",
                    "model_name": "GPT-5.5",
                    "verified_score": 65.2,
                    "lite_score": 68.1,
                    "multilingual_python_score": 62.8
                },
                {
                    "model_id": "claude-opus-4-7",
                    "model_name": "Claude Opus 4.7",
                    "verified_score": 58.4,
                    "lite_score": 61.2,
                    "multilingual_python_score": 55.9
                },
                {
                    "model_id": "claude-3-5-sonnet-20241022",
                    "model_name": "Claude 3.5 Sonnet (New)",
                    "verified_score": 50.8,
                    "lite_score": 53.0,
                    "multilingual_python_score": 48.5
                },
                {
                    "model_id": "overfit-coder-v1",
                    "model_name": "Overfit Coder",
                    "verified_score": 48.0,
                    "lite_score": 35.0,  # Gaming! Verified > Lite
                    "multilingual_python_score": 30.0
                }
            ]
        }
