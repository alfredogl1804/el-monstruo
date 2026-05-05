"""
El Catastro · Sources · AIME (American Invitational Mathematics Examination).

Cliente para extraer scores AIME 2024 y AIME 2025 de BenchLM.
Anti-gaming v1: si `aime_2024 >= aime_2025 + 10` el modelo posiblemente
memorizó el test set 2024 (filtrado a su entrenamiento) y NO razona sobre
problemas nuevos. Patrón análogo al UC Berkeley SWE-bench Verified vs Lite.

[Hilo Manus Catastro] · Sprint 86.7 · 2026-05-05
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


class AIMEFuente(BaseFuente):
    """
    Fuente AIME 2024 + AIME 2025 (BenchLM).
    Pública, no requiere API key.
    """

    nombre = "aime"
    env_key = None  # API pública

    async def fetch(self, **kwargs: Any) -> RawSnapshot:
        if self.dry_run:
            return self._make_snapshot(
                payload=self._get_dry_run_payload(),
                url="https://benchlm.ai/api/v1/benchmarks/aime",
                metadata={"dry_run": True},
            )

        url = "https://benchlm.ai/api/v1/benchmarks/aime"
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(url)

                if response.status_code == 429:
                    raise FuenteRateLimitError(self.nombre, "Rate limit en BenchLM AIME")
                if response.status_code >= 500:
                    raise FuenteUnavailableError(
                        self.nombre, f"Error {response.status_code} en BenchLM AIME"
                    )

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
        """Extrae aime_2024 y aime_2025 (accuracy 0-100)."""
        scores: dict[str, float] = {}
        if "aime_2024_score" in item:
            scores["aime_2024"] = float(item["aime_2024_score"])
        if "aime_2025_score" in item:
            scores["aime_2025"] = float(item["aime_2025_score"])
        return scores

    @staticmethod
    def detect_gaming(scores: dict[str, float]) -> bool:
        """
        Anti-gaming v1 AIME:
        Gaming si aime_2024 >= aime_2025 + 10 (memorización del test set 2024
        filtrado al training data del modelo). El AIME 2025 es held-out después
        del training cutoff de la mayoría de modelos.
        """
        aime_2024 = scores.get("aime_2024")
        aime_2025 = scores.get("aime_2025")

        if aime_2024 is None or aime_2025 is None:
            return False

        return aime_2024 >= (aime_2025 + 10.0)

    def _get_dry_run_payload(self) -> dict[str, Any]:
        # Slugs alineados con dry_run core (gpt-5-5, claude-opus-4-7)
        # + 1 modelo "memorizador" sintético (memorizer-math-v1) para
        # validar que detect_gaming dispara correctamente.
        return {
            "data": [
                {
                    "model_id": "gpt-5-5",
                    "model_name": "GPT-5.5",
                    "aime_2024_score": 87.5,
                    "aime_2025_score": 82.3,  # diff < 10 → sano
                },
                {
                    "model_id": "claude-opus-4-7",
                    "model_name": "Claude Opus 4.7",
                    "aime_2024_score": 79.2,
                    "aime_2025_score": 76.8,  # diff < 10 → sano
                },
                {
                    "model_id": "deepseek-r1",
                    "model_name": "DeepSeek R1",
                    "aime_2024_score": 91.0,
                    "aime_2025_score": 84.5,  # diff < 10 → sano
                },
                {
                    "model_id": "memorizer-math-v1",
                    "model_name": "Memorizer Math",
                    "aime_2024_score": 78.0,
                    "aime_2025_score": 45.0,  # GAMING! diff = 33 (>10)
                },
            ]
        }
