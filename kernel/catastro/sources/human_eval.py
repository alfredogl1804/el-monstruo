"""
El Catastro · Sources · HumanEval+.

Cliente para extraer datos de BenchLM para HumanEval+ (BigCodeBench).
Fuente independiente para Quorum 2-de-3 de coding.

[Hilo Manus Catastro] · Sprint 86.5 · 2026-05-05
"""
from __future__ import annotations

import httpx
from typing import Any

from kernel.catastro.sources.base import (
    BaseFuente,
    FuenteRateLimitError,
    FuenteTimeoutError,
    FuenteUnavailableError,
    RawSnapshot,
)


class HumanEvalFuente(BaseFuente):
    """
    Fuente para HumanEval+ (BenchLM).
    Pública, no requiere API key.
    """

    nombre = "human_eval"
    env_key = None

    async def fetch(self, **kwargs: Any) -> RawSnapshot:
        if self.dry_run:
            return self._make_snapshot(
                payload=self._get_dry_run_payload(),
                url="https://benchlm.ai/api/v1/benchmarks/humaneval-plus",
                metadata={"dry_run": True},
            )

        url = "https://benchlm.ai/api/v1/benchmarks/humaneval-plus"
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
    def extract_score(item: dict[str, Any]) -> float | None:
        """Extrae el score principal (pass@1)."""
        score = item.get("pass_at_1")
        if score is not None:
            return float(score)
        return None

    def _get_dry_run_payload(self) -> dict[str, Any]:
        return {
            "data": [
                {
                    "model_id": "gpt-5-5",
                    "model_name": "GPT-5.5",
                    "pass_at_1": 92.1
                },
                {
                    "model_id": "claude-opus-4-7",
                    "model_name": "Claude Opus 4.7",
                    "pass_at_1": 90.3
                },
                {
                    "model_id": "claude-3-5-sonnet-20241022",
                    "model_name": "Claude 3.5 Sonnet (New)",
                    "pass_at_1": 88.4
                },
                {
                    "model_id": "overfit-coder-v1",
                    "model_name": "Overfit Coder",
                    "pass_at_1": 95.0  # Sospechosamente alto
                }
            ]
        }
