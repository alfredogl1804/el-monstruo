"""
El Catastro · Source · LMArena (vía Hugging Face).

LMArena (chatbot-arena) NO expone una API REST oficial — el leaderboard
se publica como dataset Parquet en Hugging Face:

  https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset

Subset usado:
  `text_style_control` (split `latest`)

Auth:
  Pública. Opcional `HF_TOKEN` via env var `HF_TOKEN` para evitar
  rate limits al descargar.

Schema del dataset (extraído 2026-05-04):
  model_name (string)              — identificador
  organization (string)            — proveedor
  license (string)                 — licencia
  rating (float)                   — Arena Score
  rating_lower (float)             — confidence interval inferior
  rating_upper (float)             — confidence interval superior
  variance (float)                 — varianza
  vote_count (int)                 — número de batallas
  rank (int)                       — ranking en categoría
  category (string)                — categoría (overall, coding, math, etc.)
  leaderboard_publish_date (str)   — YYYY-MM-DD

Snapshot público confirmado: 2026-04-27 con claude-opus-4-7 (#3),
gpt-5.5 (#6), gemini-3.1-pro (#13), kimi-k2.6 (#10).

[Hilo Manus Catastro] · Sprint 86 Bloque 2 · 2026-05-04
"""
from __future__ import annotations

import asyncio
import json
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


class LMArenaFuente(BaseFuente):
    """
    Cliente del LMArena leaderboard via Hugging Face Datasets Server API.

    Usa el endpoint REST público de HF (no requiere `datasets` library)
    para mantener dependencias mínimas en Railway.

    Endpoint:
      GET https://datasets-server.huggingface.co/rows
        ?dataset=lmarena-ai%2Fleaderboard-dataset
        &config=text_style_control
        &split=latest
        &offset=0
        &length=100

    Ventaja vs `load_dataset`:
      - No descarga el dataset entero (decenas de MB)
      - No requiere `datasets`/`pyarrow` en producción
      - Soporta paginación si supera 100 filas
    """

    nombre = "lmarena"
    env_key = "HF_TOKEN"  # opcional — la API es pública sin token
    base_url = "https://datasets-server.huggingface.co"

    timeout_seconds = 60.0  # HF a veces tarda más
    max_retries = 2

    DATASET = "lmarena-ai/leaderboard-dataset"
    DEFAULT_CONFIG = "text_style_control"
    DEFAULT_SPLIT = "latest"

    def is_configured(self) -> bool:
        """LMArena via HF es pública — siempre disponible sin token."""
        return True

    async def fetch(self, **kwargs: Any) -> RawSnapshot:
        """
        Obtiene el leaderboard latest desde HF Datasets Server.

        Args:
            config: subset HF (default 'text_style_control')
            split: split (default 'latest')
            length: max filas (default 100, máx 100 por la API)
            offset: paginación (default 0)
            category: filtro local sobre la columna `category`
                      (default 'overall' — el más relevante para Trono)

        Returns:
            RawSnapshot con `payload = {"rows": [...], "num_rows_total": int}`

        Raises:
            FuenteRateLimitError, FuenteTimeoutError, FuenteUnavailableError.
        """
        if self.dry_run:
            return self._dry_run_snapshot()

        config = kwargs.get("config", self.DEFAULT_CONFIG)
        split = kwargs.get("split", self.DEFAULT_SPLIT)
        length = int(kwargs.get("length", 100))
        offset = int(kwargs.get("offset", 0))
        category_filter = kwargs.get("category", "overall")

        url = f"{self.base_url}/rows"
        params = {
            "dataset": self.DATASET,
            "config": config,
            "split": split,
            "offset": str(offset),
            "length": str(min(length, 100)),
        }
        headers: dict[str, str] = {}
        token = self._get_env_key()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    raw = response.json()
                    rows = self._extract_rows(raw, category_filter)
                    payload = {
                        "rows": rows,
                        "num_rows_total": raw.get("num_rows_total", len(rows)),
                        "category_filter": category_filter,
                        "config": config,
                        "split": split,
                    }
                    metadata = {
                        "status_code": 200,
                        "attempt": attempt + 1,
                        "rows_returned": len(rows),
                        "auth_used": bool(token),
                    }
                    return self._make_snapshot(payload=payload, url=url, metadata=metadata)

                if response.status_code in (401, 403):
                    raise FuenteUnauthorizedError(
                        self.nombre,
                        f"HF rechazó token (HTTP {response.status_code})",
                        {"status_code": response.status_code},
                    )

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "unknown")
                    raise FuenteRateLimitError(
                        self.nombre,
                        f"Rate limit HF (HTTP 429), Retry-After={retry_after}",
                        {"retry_after": retry_after},
                    )

                if response.status_code >= 500:
                    last_error = FuenteUnavailableError(
                        self.nombre,
                        f"HF servidor caído (HTTP {response.status_code})",
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
    # Extracción
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_rows(raw: dict, category_filter: Optional[str]) -> list[dict]:
        """
        Extrae la lista de modelos del response HF Datasets Server.

        Estructura esperada:
          { "rows": [ {"row_idx": int, "row": {...}, "truncated_cells": []}, ... ] }
        """
        rows = []
        for entry in raw.get("rows", []):
            row = entry.get("row", {})
            if not row:
                continue
            if category_filter and row.get("category") != category_filter:
                continue
            rows.append(row)
        return rows

    @staticmethod
    def extract_arena_score(row: dict) -> Optional[float]:
        """Arena Score (rating) — proxy de quality_score basado en humanos."""
        rating = row.get("rating")
        if rating is None:
            return None
        try:
            return float(rating)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def extract_rank(row: dict) -> Optional[int]:
        """Rank en la categoría."""
        rank = row.get("rank")
        if rank is None:
            return None
        try:
            return int(rank)
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Dry-run
    # ------------------------------------------------------------------

    def _dry_run_snapshot(self) -> RawSnapshot:
        """Snapshot fake basado en el snapshot real 2026-04-27 (verificado)."""
        payload = {
            "rows": [
                {
                    "model_name": "claude-opus-4-7",
                    "organization": "anthropic",
                    "license": "Proprietary",
                    "rating": 1514.522543,
                    "rating_lower": 1503.331850,
                    "rating_upper": 1525.713236,
                    "variance": 32.600013,
                    "vote_count": 3310,
                    "rank": 3,
                    "category": "overall",
                    "leaderboard_publish_date": "2026-04-27",
                },
                {
                    "model_name": "gpt-5.5",
                    "organization": "openai",
                    "license": "Proprietary",
                    "rating": 1489.916504,
                    "rating_lower": 1473.504940,
                    "rating_upper": 1506.328068,
                    "variance": 70.113841,
                    "vote_count": 1145,
                    "rank": 6,
                    "category": "overall",
                    "leaderboard_publish_date": "2026-04-27",
                },
                {
                    "model_name": "kimi-k2.6",
                    "organization": "moonshot",
                    "license": "Modified MIT",
                    "rating": 1456.672728,
                    "rating_lower": 1442.041550,
                    "rating_upper": 1471.303906,
                    "variance": 55.726579,
                    "vote_count": 1524,
                    "rank": 10,
                    "category": "overall",
                    "leaderboard_publish_date": "2026-04-27",
                },
                {
                    "model_name": "gemini-3.1-pro-preview",
                    "organization": "google",
                    "license": "Proprietary",
                    "rating": 1448.603941,
                    "rating_lower": 1441.950133,
                    "rating_upper": 1455.257748,
                    "variance": 11.525088,
                    "vote_count": 19099,
                    "rank": 13,
                    "category": "overall",
                    "leaderboard_publish_date": "2026-04-27",
                },
            ],
            "num_rows_total": 4,
            "category_filter": "overall",
            "config": "text_style_control",
            "split": "latest",
        }
        return self._make_snapshot(
            payload=payload,
            url=f"{self.base_url}/rows",
            metadata={"dry_run": True, "rows_returned": 4, "auth_used": False},
        )
