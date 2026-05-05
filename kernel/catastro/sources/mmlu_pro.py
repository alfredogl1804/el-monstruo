"""
El Catastro · Sources · MMLU-Pro (Massive Multitask Language Understanding Pro).

Cliente para extraer scores MMLU Basic (4-opción) + MMLU-Pro (10-opción) de
BenchLM. Pro es el rediseño "harder" con 10 opciones de respuesta y razonamiento
multi-paso. Anti-gaming v1: si `mmlu_pro > mmlu_basic + 20` el modelo
posiblemente memorizó el reformulado Pro (más nuevo, mayor riesgo de
contaminación). Se espera mmlu_pro <= mmlu_basic en modelos sanos (Pro es
más difícil), o cuando mucho Pro ~ Basic ± 5pp.

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


class MMLUProFuente(BaseFuente):
    """
    Fuente MMLU Basic + MMLU-Pro (BenchLM).
    Pública, no requiere API key.
    """

    nombre = "mmlu_pro"
    env_key = None  # API pública

    async def fetch(self, **kwargs: Any) -> RawSnapshot:
        if self.dry_run:
            return self._make_snapshot(
                payload=self._get_dry_run_payload(),
                url="https://benchlm.ai/api/v1/benchmarks/mmlu-pro",
                metadata={"dry_run": True},
            )

        url = "https://benchlm.ai/api/v1/benchmarks/mmlu-pro"
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(url)

                if response.status_code == 429:
                    raise FuenteRateLimitError(self.nombre, "Rate limit en BenchLM MMLU-Pro")
                if response.status_code >= 500:
                    raise FuenteUnavailableError(
                        self.nombre, f"Error {response.status_code} en BenchLM MMLU-Pro"
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
        """Extrae mmlu_basic y mmlu_pro (accuracy 0-100)."""
        scores: dict[str, float] = {}
        if "mmlu_basic_score" in item:
            scores["mmlu_basic"] = float(item["mmlu_basic_score"])
        if "mmlu_pro_score" in item:
            scores["mmlu_pro"] = float(item["mmlu_pro_score"])
        return scores

    @staticmethod
    def detect_gaming(scores: dict[str, float]) -> bool:
        """
        Anti-gaming v1 MMLU-Pro:
        Gaming si mmlu_pro > mmlu_basic + 20. Pro es más difícil (10 opciones,
        razonamiento multi-paso) — los modelos sanos scoren PEOR en Pro o
        igual. Si Pro está 20+ pp mejor que Basic, es señal de contaminación
        (Pro reformulado se filtró al training data).
        """
        basic = scores.get("mmlu_basic")
        pro = scores.get("mmlu_pro")

        if basic is None or pro is None:
            return False

        return pro > (basic + 20.0)

    def _get_dry_run_payload(self) -> dict[str, Any]:
        return {
            "data": [
                {
                    "model_id": "gpt-5-5",
                    "model_name": "GPT-5.5",
                    "mmlu_basic_score": 92.5,
                    "mmlu_pro_score": 78.3,  # Pro < Basic → sano
                },
                {
                    "model_id": "claude-opus-4-7",
                    "model_name": "Claude Opus 4.7",
                    "mmlu_basic_score": 91.8,
                    "mmlu_pro_score": 76.2,  # Pro < Basic → sano
                },
                {
                    "model_id": "deepseek-r1",
                    "model_name": "DeepSeek R1",
                    "mmlu_basic_score": 88.0,
                    "mmlu_pro_score": 72.5,  # Pro < Basic → sano
                },
                {
                    "model_id": "pro-overfit-v1",
                    "model_name": "Pro Overfit",
                    "mmlu_basic_score": 60.0,
                    "mmlu_pro_score": 85.0,  # GAMING! diff +25 (>20)
                },
            ]
        }
