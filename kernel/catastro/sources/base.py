"""
El Catastro · Sources · Base.

Define el contrato común de todas las fuentes de evidencia:
  - `RawSnapshot`: el shape devuelto por cada `fetch()`
  - `BaseFuente`: clase abstracta con utilidades compartidas
  - Jerarquía de errores tipados (rate limit, timeout, unauthorized, etc.)

Cada fuente concreta hereda de `BaseFuente` e implementa `fetch()`.
La disciplina os.environ es enforzada vía `_get_env_key()` que lee
SIEMPRE en runtime, nunca cachea.

[Hilo Manus Catastro] · Sprint 86 Bloque 2 · 2026-05-04
"""
from __future__ import annotations

import hashlib
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


# ============================================================================
# JERARQUÍA DE ERRORES
# ============================================================================

class FuenteError(Exception):
    """Error base de cualquier fuente del Catastro."""

    def __init__(self, fuente: str, mensaje: str, contexto: Optional[dict] = None):
        self.fuente = fuente
        self.mensaje = mensaje
        self.contexto = contexto or {}
        super().__init__(f"[{fuente}] {mensaje}")


class FuenteRateLimitError(FuenteError):
    """429 — cuota agotada o ventana excedida. Se debe esperar y reintentar."""


class FuenteTimeoutError(FuenteError):
    """Timeout de red. Reintentar con backoff."""


class FuenteUnauthorizedError(FuenteError):
    """401/403 — API key inválida o ausente. NO reintentar."""


class FuenteUnavailableError(FuenteError):
    """5xx / DNS error / fuente caída. Reintentar 1 vez, luego degradar."""


# ============================================================================
# RAW SNAPSHOT — shape común de todas las fuentes
# ============================================================================

@dataclass(frozen=True)
class RawSnapshot:
    """
    Resultado de un `fetch()` exitoso.

    Inmutable y trazable. El payload se hashea para citation tracking
    (FuenteEvidencia.payload_hash).
    """
    fuente: str
    """Identificador de la fuente: 'artificial_analysis', 'openrouter', 'lmarena'."""

    fetched_at: datetime
    """Timestamp UTC de cuando se obtuvo el snapshot."""

    payload: dict[str, Any]
    """Datos crudos retornados por la fuente, sin transformar."""

    payload_hash: str
    """SHA-256 truncado (16 hex chars) del payload serializado."""

    url: str
    """URL exacta consultada — para auditoría."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Metadata extra (rate limit headers, paginación, etc.)."""

    def to_evidencia(self, curador: str, tipo_dato: str) -> dict[str, Any]:
        """
        Convierte este snapshot en una entrada de FuenteEvidencia
        para serializar al campo `fuentes_evidencia` JSONB.
        """
        return {
            "url": self.url,
            "fetched_at": self.fetched_at.isoformat(),
            "payload_hash": self.payload_hash,
            "curador": curador,
            "tipo_dato": tipo_dato,
        }


# ============================================================================
# BASE FUENTE
# ============================================================================

class BaseFuente(ABC):
    """
    Clase abstracta de toda fuente del Catastro.

    Subclases deben:
      1. Definir `nombre` (str) — slug único de la fuente.
      2. Definir `env_key` (str) — nombre de la env var que contiene la
         API key (None si la fuente es pública, ej. lmarena via HF).
      3. Implementar `async def fetch(self, **kwargs) -> RawSnapshot`.
    """

    nombre: str = ""  # subclase debe override
    env_key: Optional[str] = None  # subclase debe override; None = pública

    # Configuración de retry/timeout (subclase puede override)
    timeout_seconds: float = 30.0
    max_retries: int = 2
    backoff_base_seconds: float = 1.0

    def __init__(self, *, dry_run: bool = False) -> None:
        """
        Args:
            dry_run: Si True, fetch() devuelve un RawSnapshot fake sin
                     llamar a la API real. Útil para tests offline.
        """
        self.dry_run = dry_run

    # ------------------------------------------------------------------
    # API pública abstracta
    # ------------------------------------------------------------------

    @abstractmethod
    async def fetch(self, **kwargs: Any) -> RawSnapshot:
        """
        Obtiene un snapshot de la fuente.

        Raises:
            FuenteUnauthorizedError: API key inválida o ausente.
            FuenteRateLimitError: cuota agotada.
            FuenteTimeoutError: timeout de red.
            FuenteUnavailableError: 5xx o DNS error.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Utilidades para subclases
    # ------------------------------------------------------------------

    def _get_env_key(self) -> Optional[str]:
        """
        Lee la API key SIEMPRE en runtime desde os.environ.

        Disciplina obligatoria del Sprint 86: NUNCA cachear keys a nivel
        módulo o constructor. Permite rotación sin reiniciar.

        Returns:
            La API key si está presente, None si la fuente es pública o
            la key no está seteada.
        """
        if not self.env_key:
            return None
        return os.environ.get(self.env_key)

    def _hash_payload(self, payload: Any) -> str:
        """
        SHA-256 truncado a 16 hex chars del payload serializado.

        Determinístico: mismo payload → mismo hash.
        """
        serialized = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
        full_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return full_hash[:16]

    def _now_utc(self) -> datetime:
        """Timestamp UTC consistente."""
        return datetime.now(timezone.utc)

    def _make_snapshot(
        self,
        payload: dict[str, Any],
        url: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> RawSnapshot:
        """Helper para construir un RawSnapshot con hash automático."""
        return RawSnapshot(
            fuente=self.nombre,
            fetched_at=self._now_utc(),
            payload=payload,
            payload_hash=self._hash_payload(payload),
            url=url,
            metadata=metadata or {},
        )

    # ------------------------------------------------------------------
    # Health check estándar
    # ------------------------------------------------------------------

    def is_configured(self) -> bool:
        """
        True si la fuente tiene todo lo necesario para correr.

        Para fuentes con env_key, verifica que la key esté presente.
        Para fuentes públicas, siempre True.
        """
        if not self.env_key:
            return True
        return bool(self._get_env_key())
