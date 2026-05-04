"""
El Catastro · Source · Artificial Analysis.

Cliente del API público de https://artificialanalysis.ai

Endpoint:
  GET https://artificialanalysis.ai/api/v2/data/llms/models

Auth:
  Header `x-api-key: <token>` — env var `ARTIFICIAL_ANALYSIS_API_KEY`

Rate limit:
  1000 req/día (free tier 2026-Q2)

Cubre: GPT, Claude, Gemini, xAI, Mistral, Llama (frontier benchmarks).

Schema clave del response (extraído de docs 2026-05-04):
  data[].{
    id, name, slug, model_creator,
    evaluations: {
      intelligence_index, coding_index, math_index,
      mmlu_pro, gpqa, hle, livecodebench, scicode,
      math_500, aime
    },
    pricing: { price_1m_input_tokens, price_1m_output_tokens },
    median_output_tokens_per_second,
    median_time_to_first_token_seconds
  }

[Hilo Manus Catastro] · Sprint 86 Bloque 2 · 2026-05-04
"""
from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx

from kernel.catastro.sources.base import (
    BaseFuente,
    FuenteRateLimitError,
    FuenteTimeoutError,
    FuenteUnauthorizedError,
    FuenteUnavailableError,
    RawSnapshot,
)


class ArtificialAnalysisFuente(BaseFuente):
    """Cliente del Artificial Analysis API."""

    nombre = "artificial_analysis"
    env_key = "ARTIFICIAL_ANALYSIS_API_KEY"
    base_url = "https://artificialanalysis.ai/api/v2"

    timeout_seconds = 30.0
    max_retries = 2

    async def fetch(self, **kwargs: Any) -> RawSnapshot:
        """
        Obtiene el catalogo completo de LLMs evaluados por Artificial Analysis.

        Args:
            **kwargs: ignorado (la API no tiene parámetros relevantes para
                      el listado completo).

        Returns:
            RawSnapshot con `payload = {"data": [...]}`

        Raises:
            FuenteUnauthorizedError: API key faltante o inválida.
            FuenteRateLimitError: 429 con Retry-After header.
            FuenteTimeoutError: timeout de red.
            FuenteUnavailableError: 5xx u otro error transient.
        """
        if self.dry_run:
            return self._dry_run_snapshot()

        api_key = self._get_env_key()
        if not api_key:
            raise FuenteUnauthorizedError(
                self.nombre,
                f"env var {self.env_key} no configurada",
                {"remediation": "Setear ARTIFICIAL_ANALYSIS_API_KEY en Railway"},
            )

        url = f"{self.base_url}/data/llms/models"
        headers = {"x-api-key": api_key}

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    payload = response.json()
                    metadata = {
                        "status_code": 200,
                        "attempt": attempt + 1,
                        "rate_limit_remaining": response.headers.get("x-ratelimit-remaining"),
                    }
                    return self._make_snapshot(payload=payload, url=url, metadata=metadata)

                if response.status_code in (401, 403):
                    raise FuenteUnauthorizedError(
                        self.nombre,
                        f"API rechazó key (HTTP {response.status_code})",
                        {"status_code": response.status_code, "body": response.text[:500]},
                    )

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "unknown")
                    raise FuenteRateLimitError(
                        self.nombre,
                        f"Rate limit (HTTP 429), Retry-After={retry_after}",
                        {"retry_after": retry_after},
                    )

                if response.status_code >= 500:
                    last_error = FuenteUnavailableError(
                        self.nombre,
                        f"Servidor caído (HTTP {response.status_code})",
                        {"status_code": response.status_code, "attempt": attempt + 1},
                    )
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.backoff_base_seconds * (2 ** attempt))
                        continue
                    raise last_error

                raise FuenteUnavailableError(
                    self.nombre,
                    f"Status inesperado HTTP {response.status_code}",
                    {"status_code": response.status_code, "body": response.text[:500]},
                )

            except httpx.TimeoutException as e:
                last_error = FuenteTimeoutError(
                    self.nombre,
                    f"Timeout tras {self.timeout_seconds}s",
                    {"attempt": attempt + 1},
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(self.backoff_base_seconds * (2 ** attempt))
                    continue
                raise last_error from e

            except httpx.HTTPError as e:
                last_error = FuenteUnavailableError(
                    self.nombre,
                    f"Error HTTP: {type(e).__name__}: {e}",
                    {"attempt": attempt + 1},
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(self.backoff_base_seconds * (2 ** attempt))
                    continue
                raise last_error from e

        # Defensa en profundidad — no debería llegar aquí
        raise last_error or FuenteUnavailableError(self.nombre, "Loop de retry agotado sin error registrado")

    # ------------------------------------------------------------------
    # Helpers para tests offline
    # ------------------------------------------------------------------

    def _dry_run_snapshot(self) -> RawSnapshot:
        """Snapshot fake determinístico para tests."""
        payload = {
            "data": [
                {
                    "id": "openai/gpt-5.5",
                    "name": "GPT-5.5",
                    "slug": "gpt-5-5",
                    "model_creator": {"name": "OpenAI"},
                    "evaluations": {
                        "intelligence_index": 87.4,
                        "coding_index": 89.1,
                        "math_index": 91.0,
                    },
                    "pricing": {
                        "price_1m_input_tokens": 1.50,
                        "price_1m_output_tokens": 12.00,
                    },
                    "median_output_tokens_per_second": 142.3,
                    "median_time_to_first_token_seconds": 0.42,
                },
                {
                    "id": "anthropic/claude-opus-4-7",
                    "name": "Claude Opus 4.7",
                    "slug": "claude-opus-4-7",
                    "model_creator": {"name": "Anthropic"},
                    "evaluations": {
                        "intelligence_index": 89.2,
                        "coding_index": 92.4,
                        "math_index": 90.5,
                    },
                    "pricing": {
                        "price_1m_input_tokens": 15.00,
                        "price_1m_output_tokens": 75.00,
                    },
                    "median_output_tokens_per_second": 78.5,
                    "median_time_to_first_token_seconds": 1.20,
                },
            ]
        }
        return self._make_snapshot(
            payload=payload,
            url=f"{self.base_url}/data/llms/models",
            metadata={"dry_run": True, "models_count": 2},
        )

    # ------------------------------------------------------------------
    # Helpers de extracción (delegados al pipeline para normalizar)
    # ------------------------------------------------------------------

    @staticmethod
    def extract_quality_score(model_data: dict) -> Optional[float]:
        """
        Extrae el quality_score (0-100) desde un item del payload.
        Usa intelligence_index como proxy de calidad general.
        """
        evals = model_data.get("evaluations", {})
        idx = evals.get("intelligence_index")
        if idx is None:
            return None
        try:
            return float(idx)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def extract_pricing(model_data: dict) -> dict[str, Optional[float]]:
        """Extrae precios input/output por millón de tokens."""
        pricing = model_data.get("pricing", {}) or {}
        return {
            "input_per_million": pricing.get("price_1m_input_tokens"),
            "output_per_million": pricing.get("price_1m_output_tokens"),
        }
