"""
El Catastro · Sources · MBPP.

Cliente para extraer datos de BenchLM para MBPP (sanitized + plus).
Tercera fuente independiente para Quorum 2-de-3 de coding.

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


class MBPPFuente(BaseFuente):
    """
    Fuente para MBPP+ (BenchLM).
    Pública, no requiere API key.
    """

    nombre = "mbpp"
    env_key = None

    async def fetch(self, **kwargs: Any) -> RawSnapshot:
        if self.dry_run:
            return self._make_snapshot(
                payload=self._get_dry_run_payload(),
                url="https://benchlm.ai/api/v1/benchmarks/mbpp-plus",
                metadata={"dry_run": True},
            )

        url = "https://benchlm.ai/api/v1/benchmarks/mbpp-plus"
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
                    "model_id": "claude-3-5-sonnet-20241022",
                    "model_name": "Claude 3.5 Sonnet (New)",
                    "pass_at_1": 89.5
                },
                {
                    "model_id": "gpt-4o-2024-08-06",
                    "model_name": "GPT-4o",
                    "pass_at_1": 87.2
                },
                {
                    "model_id": "overfit-coder-v1",
                    "model_name": "Overfit Coder",
                    "pass_at_1": 94.0
                }
            ]
        }
