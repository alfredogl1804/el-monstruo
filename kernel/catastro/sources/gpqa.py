"""
El Catastro · Sources · GPQA Diamond (Graduate-level PhysicsQAs).

Cliente para extraer scores GPQA Main + GPQA Diamond de BenchLM.
Diamond es el subset más difícil (PhD-level). Anti-gaming v1: si
`gpqa_diamond > gpqa_main + 15` el modelo posiblemente memorizó el
subset Diamond (es smaller y más viral en papers, mayor riesgo de
contaminación). El subset main es ~5x más grande.

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


class GPQAFuente(BaseFuente):
    """
    Fuente GPQA Main + Diamond (BenchLM).
    Pública, no requiere API key.
    """

    nombre = "gpqa"
    env_key = None  # API pública

    async def fetch(self, **kwargs: Any) -> RawSnapshot:
        if self.dry_run:
            return self._make_snapshot(
                payload=self._get_dry_run_payload(),
                url="https://benchlm.ai/api/v1/benchmarks/gpqa-diamond",
                metadata={"dry_run": True},
            )

        url = "https://benchlm.ai/api/v1/benchmarks/gpqa-diamond"
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(url)

                if response.status_code == 429:
                    raise FuenteRateLimitError(self.nombre, "Rate limit en BenchLM GPQA")
                if response.status_code >= 500:
                    raise FuenteUnavailableError(
                        self.nombre, f"Error {response.status_code} en BenchLM GPQA"
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
        """Extrae gpqa_main y gpqa_diamond (accuracy 0-100)."""
        scores: dict[str, float] = {}
        if "gpqa_main_score" in item:
            scores["gpqa_main"] = float(item["gpqa_main_score"])
        if "gpqa_diamond_score" in item:
            scores["gpqa_diamond"] = float(item["gpqa_diamond_score"])
        return scores

    @staticmethod
    def detect_gaming(scores: dict[str, float]) -> bool:
        """
        Anti-gaming v1 GPQA:
        Gaming si gpqa_diamond > gpqa_main + 15. Diamond es 198 preguntas
        más virales, mayor riesgo de contaminación. Si un modelo es 15+ pp
        mejor en Diamond que en Main (subset más grande y menos contaminado),
        es señal de memorización.
        """
        main = scores.get("gpqa_main")
        diamond = scores.get("gpqa_diamond")

        if main is None or diamond is None:
            return False

        return diamond > (main + 15.0)

    def _get_dry_run_payload(self) -> dict[str, Any]:
        return {
            "data": [
                {
                    "model_id": "gpt-5-5",
                    "model_name": "GPT-5.5",
                    "gpqa_main_score": 75.4,
                    "gpqa_diamond_score": 78.2,  # diff +3 → sano
                },
                {
                    "model_id": "claude-opus-4-7",
                    "model_name": "Claude Opus 4.7",
                    "gpqa_main_score": 72.1,
                    "gpqa_diamond_score": 80.5,  # diff +8 → sano
                },
                {
                    "model_id": "deepseek-r1",
                    "model_name": "DeepSeek R1",
                    "gpqa_main_score": 70.0,
                    "gpqa_diamond_score": 73.5,  # diff +3.5 → sano
                },
                {
                    "model_id": "diamond-overfit-v1",
                    "model_name": "Diamond Overfit",
                    "gpqa_main_score": 50.0,
                    "gpqa_diamond_score": 72.0,  # GAMING! diff +22 (>15)
                },
            ]
        }
