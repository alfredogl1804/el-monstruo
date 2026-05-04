"""
El Catastro · Source · OpenRouter.

Cliente del API público de https://openrouter.ai

Endpoint:
  GET https://openrouter.ai/api/v1/models

Auth:
  Header `Authorization: Bearer <token>` — env var `OPENROUTER_API_KEY`
  Nota: el listado de modelos públicos puede llamarse SIN auth, pero
  con auth se obtienen también `per_request_limits` y los modelos
  disponibles para esa cuenta. Usamos auth siempre que esté presente.

Rate limit:
  Generoso (no documentado en límites diarios para listing).

Cubre: 300+ modelos vía proveedores agregados (frontier + open source +
edge). Único source con `pricing` en vivo y `context_length` por modelo.

Schema clave del response (extraído de docs 2026-05-04):
  data[].{
    id, canonical_slug, hugging_face_id?, name, description,
    context_length, created,
    architecture: { input_modalities, output_modalities, modality,
                    instruct_type, tokenizer },
    pricing: { prompt, completion, image, request },
    top_provider: { is_moderated, context_length, max_completion_tokens },
    per_request_limits, supported_parameters
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


class OpenRouterFuente(BaseFuente):
    """Cliente del OpenRouter Models API."""

    nombre = "openrouter"
    env_key = "OPENROUTER_API_KEY"
    base_url = "https://openrouter.ai/api/v1"

    timeout_seconds = 30.0
    max_retries = 2

    def is_configured(self) -> bool:
        """OpenRouter es CONSULTABLE sin auth para el endpoint de listing."""
        return True

    async def fetch(self, **kwargs: Any) -> RawSnapshot:
        """
        Obtiene el catalogo completo de modelos de OpenRouter.

        Args:
            **kwargs: ignorado para listing completo. Soporta opcional
                      `category` para filtrar por categoría.

        Returns:
            RawSnapshot con `payload = {"data": [...]}`

        Raises:
            FuenteRateLimitError: 429.
            FuenteTimeoutError: timeout.
            FuenteUnavailableError: 5xx u otro transient.
            FuenteUnauthorizedError: solo si se pasó key inválida.
        """
        if self.dry_run:
            return self._dry_run_snapshot()

        api_key = self._get_env_key()
        url = f"{self.base_url}/models"
        headers: dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        params: dict[str, str] = {}
        if "category" in kwargs and kwargs["category"]:
            params["category"] = str(kwargs["category"])

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    payload = response.json()
                    metadata = {
                        "status_code": 200,
                        "attempt": attempt + 1,
                        "models_count": len(payload.get("data", [])),
                        "auth_used": bool(api_key),
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

        raise last_error or FuenteUnavailableError(self.nombre, "Loop de retry agotado sin error registrado")

    # ------------------------------------------------------------------
    # Helpers de extracción (delegados al pipeline para normalizar)
    # ------------------------------------------------------------------

    @staticmethod
    def extract_pricing(model_data: dict) -> dict[str, Optional[float]]:
        """
        OpenRouter retorna pricing en USD POR TOKEN (string).
        Convertimos a USD POR MILLÓN para consistencia con Artificial Analysis.
        """
        pricing = model_data.get("pricing", {}) or {}

        def _to_per_million(value: Any) -> Optional[float]:
            if value is None:
                return None
            try:
                per_token = float(value)
                return per_token * 1_000_000
            except (TypeError, ValueError):
                return None

        return {
            "input_per_million": _to_per_million(pricing.get("prompt")),
            "output_per_million": _to_per_million(pricing.get("completion")),
        }

    @staticmethod
    def extract_context_length(model_data: dict) -> Optional[int]:
        """Context length en tokens — preferir top_provider si existe."""
        top = model_data.get("top_provider", {}) or {}
        ctx = top.get("context_length") or model_data.get("context_length")
        if ctx is None:
            return None
        try:
            return int(ctx)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def is_open_source(model_data: dict) -> bool:
        """
        Heurística: si el id incluye un proveedor abierto conocido o existe
        `hugging_face_id`, lo marcamos como open-weights.
        """
        if model_data.get("hugging_face_id"):
            return True
        model_id = (model_data.get("id") or "").lower()
        open_orgs = ("meta-llama/", "qwen/", "deepseek/", "mistralai/", "google/gemma", "moonshotai/")
        return any(model_id.startswith(org) for org in open_orgs)

    # ------------------------------------------------------------------
    # Dry-run
    # ------------------------------------------------------------------

    def _dry_run_snapshot(self) -> RawSnapshot:
        """Snapshot fake determinístico para tests."""
        payload = {
            "data": [
                {
                    "id": "openai/gpt-5.5",
                    "canonical_slug": "openai/gpt-5-5",
                    "name": "GPT-5.5",
                    "description": "Latest OpenAI flagship model",
                    "context_length": 256_000,
                    "created": 1730000000,
                    "architecture": {
                        "input_modalities": ["text", "image"],
                        "output_modalities": ["text"],
                        "modality": "text+image->text",
                        "instruct_type": "chatml",
                        "tokenizer": "GPT",
                    },
                    "pricing": {
                        "prompt": "0.0000015",
                        "completion": "0.000012",
                        "image": "0",
                        "request": "0",
                    },
                    "top_provider": {"is_moderated": True, "context_length": 256_000},
                    "supported_parameters": ["temperature", "top_p", "max_tokens"],
                },
                {
                    "id": "anthropic/claude-opus-4.7",
                    "canonical_slug": "anthropic/claude-opus-4-7",
                    "name": "Claude Opus 4.7",
                    "description": "Anthropic's most powerful model",
                    "context_length": 500_000,
                    "created": 1734000000,
                    "architecture": {
                        "input_modalities": ["text", "image"],
                        "output_modalities": ["text"],
                        "modality": "text+image->text",
                        "instruct_type": "claude",
                        "tokenizer": "Claude",
                    },
                    "pricing": {
                        "prompt": "0.000015",
                        "completion": "0.000075",
                        "image": "0",
                        "request": "0",
                    },
                    "top_provider": {"is_moderated": True, "context_length": 500_000},
                    "supported_parameters": ["temperature", "top_p", "max_tokens"],
                },
                {
                    "id": "qwen/qwen3-coder-32b",
                    "canonical_slug": "qwen/qwen3-coder-32b",
                    "hugging_face_id": "Qwen/Qwen3-Coder-32B",
                    "name": "Qwen3 Coder 32B",
                    "description": "Open-weights coding specialist",
                    "context_length": 131_072,
                    "created": 1735000000,
                    "architecture": {
                        "input_modalities": ["text"],
                        "output_modalities": ["text"],
                        "modality": "text->text",
                        "instruct_type": "qwen",
                        "tokenizer": "Qwen",
                    },
                    "pricing": {"prompt": "0.0000003", "completion": "0.0000006", "image": "0", "request": "0"},
                    "top_provider": {"is_moderated": False, "context_length": 131_072},
                    "supported_parameters": ["temperature", "top_p", "max_tokens"],
                },
            ]
        }
        return self._make_snapshot(
            payload=payload,
            url=f"{self.base_url}/models",
            metadata={"dry_run": True, "models_count": 3, "auth_used": False},
        )
