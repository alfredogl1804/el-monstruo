"""
MementoValidator — clase principal de la Capa Memento.

Responsabilidades:
    1. Cargar catálogo de operaciones críticas (Supabase o YAML fallback)
    2. Cargar catálogo de fuentes de verdad
    3. Para cada call a `validate(operation, context_used)`:
         a) Identificar la operación crítica
         b) Resolver las fuentes de verdad asociadas
         c) Leer las fuentes (con cache TTL)
         d) Comparar `context_used` vs fuente de verdad
         e) Retornar `ValidationResult` con proceed=true/false

Decisión de diseño: NO endpoint HTTP en este bloque. La clase es
importable y testeable. El endpoint /v1/memento/validate es Bloque 3.

Disciplina anti-Dory:
    - Lectura de fuente fresh con cache TTL configurable
    - invalidate_cache(source_id) para forzar refresh manual
    - get_freshness(source_id) para introspección
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from kernel.memento.models import (
    CriticalOperation,
    Discrepancy,
    SourceOfTruth,
    ValidationResult,
    ValidationStatus,
)
from kernel.memento.sources import (
    SourceCache,
    read_credential_source,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _generate_validation_id() -> str:
    """Formato 'mv_<isoZ>_<hash6>' (compatible con spec_sprint_memento.md)."""
    ts = _now().strftime("%Y-%m-%dT%H:%M:%S")
    rand = secrets.token_hex(3)  # 6 hex chars
    return f"mv_{ts}_{rand}"


# Tipo de fetcher: funciones sync o async que retornan dict con shape uniforme
SourceFetcher = Callable[[], Any]


class MementoValidator:
    """
    Validador de contexto operativo contra fuentes de verdad.

    Args:
        critical_operations: dict[str, CriticalOperation] indexado por id
        sources_of_truth: dict[str, SourceOfTruth] indexado por id
        source_fetchers: dict[str, SourceFetcher] mapping source_id -> función
            que retorna dict con shape uniforme. Permite inyectar mocks en tests.
        cache: SourceCache opcional (instancia compartida). Default: nueva.
        repo_root: Path del root del repo. Si se provee, se usa como base
            para lecturas de archivos. Si no, usa cwd o MEMENTO_REPO_ROOT env.
    """

    def __init__(
        self,
        *,
        critical_operations: Dict[str, CriticalOperation],
        sources_of_truth: Dict[str, SourceOfTruth],
        source_fetchers: Optional[Dict[str, SourceFetcher]] = None,
        cache: Optional[SourceCache] = None,
        repo_root: Optional[Path] = None,
    ) -> None:
        self.critical_operations = critical_operations
        self.sources_of_truth = sources_of_truth
        self._source_fetchers = source_fetchers or {}
        self._cache = cache or SourceCache()
        self._repo_root = repo_root

        # Para cada fuente sin fetcher explícito, generar uno por defecto
        for source_id, source in self.sources_of_truth.items():
            if source_id not in self._source_fetchers:
                self._source_fetchers[source_id] = self._build_default_fetcher(source)

    def _build_default_fetcher(self, source: SourceOfTruth) -> SourceFetcher:
        """Construye un fetcher por defecto según `source_type`."""

        def fetcher() -> Dict[str, Any]:
            if source.source_type == "repo_file":
                # Usar el lector de credentials.md
                return read_credential_source(source.location)
            elif source.source_type == "env_var":
                # Lectura local del env (el kernel sí puede leer su propia env)
                import os
                value = os.environ.get(source.location, "")
                from kernel.memento.sources import _hash_content  # type: ignore
                return {
                    "value": value,
                    "fetched_at": _now(),
                    "source_id": source.id,
                    "raw_hash": _hash_content(value),
                }
            elif source.source_type == "railway_env":
                raise RuntimeError(
                    f"railway_env_fetcher_not_configured: source_id={source.id}. "
                    f"Inyectá un fetcher mock o usá read_railway_env_var con http_client."
                )
            else:
                raise RuntimeError(
                    f"unsupported_source_type: source_id={source.id} type={source.source_type}"
                )

        return fetcher

    async def validate(
        self,
        *,
        operation: str,
        context_used: Dict[str, Any],
        hilo_id: str = "unknown",
        intent_summary: Optional[str] = None,
    ) -> ValidationResult:
        """
        Valida que el contexto declarado coincida con la fuente de verdad.

        Returns:
            ValidationResult con `proceed=True` si OK, `proceed=False` si discrepancia.
        """
        validation_id = _generate_validation_id()

        # 1. Identificar operación crítica
        op = self.critical_operations.get(operation)
        if op is None or not op.activo:
            return ValidationResult(
                validation_status=ValidationStatus.UNKNOWN_OPERATION,
                proceed=False,
                validation_id=validation_id,
                context_freshness_seconds=0,
                remediation=(
                    f"operation_not_in_catalog: '{operation}' no está registrada como "
                    f"operación crítica activa. Revisá memento_critical_operations en Supabase "
                    f"o el catálogo YAML local."
                ),
            )

        # 2. Resolver fuentes de verdad asociadas
        source_ids = op.source_of_truth_ids or []
        if not source_ids:
            # Operación crítica sin fuentes asociadas: validar como OK pero loggear
            return ValidationResult(
                validation_status=ValidationStatus.OK,
                proceed=True,
                validation_id=validation_id,
                context_freshness_seconds=0,
                remediation=None,
                source_consulted=None,
            )

        # 3. Leer fuentes con cache + comparar
        for source_id in source_ids:
            source = self.sources_of_truth.get(source_id)
            if source is None or not source.activo:
                continue

            fetcher = self._source_fetchers.get(source_id)
            if fetcher is None:
                return ValidationResult(
                    validation_status=ValidationStatus.SOURCE_UNAVAILABLE,
                    proceed=False,
                    validation_id=validation_id,
                    context_freshness_seconds=0,
                    remediation=f"source_fetcher_missing: source_id={source_id}",
                    source_consulted=source_id,
                )

            try:
                raw = await self._cache.get_or_fetch(
                    source_id=source_id,
                    ttl_seconds=source.cache_ttl_seconds,
                    fetcher=fetcher,
                )
            except Exception as exc:
                return ValidationResult(
                    validation_status=ValidationStatus.SOURCE_UNAVAILABLE,
                    proceed=False,
                    validation_id=validation_id,
                    context_freshness_seconds=0,
                    remediation=(
                        f"source_read_failed: source_id={source_id} error={exc!s}. "
                        f"Verificá la fuente y reintentá."
                    ),
                    source_consulted=source_id,
                )

            freshness = await self._cache.get_freshness(source_id) or 0
            discrepancy = self._compare(
                context_used=context_used,
                source_value=raw["value"],
                source=source,
            )

            if discrepancy is not None:
                return ValidationResult(
                    validation_status=ValidationStatus.DISCREPANCY_DETECTED,
                    proceed=False,
                    validation_id=validation_id,
                    context_freshness_seconds=freshness,
                    discrepancy=discrepancy,
                    remediation=(
                        f"context_stale_or_contaminated: el campo '{discrepancy.field}' que "
                        f"declaraste no coincide con la fuente de verdad ({discrepancy.source}). "
                        f"Re-leé la fuente y reintentá. Do NOT use context from compacted memory."
                    ),
                    source_consulted=source_id,
                )

        # 4. Si llegamos acá, todas las fuentes coinciden con context_used
        any_freshness = 0
        for source_id in source_ids:
            f = await self._cache.get_freshness(source_id)
            if f is not None and f > any_freshness:
                any_freshness = f

        return ValidationResult(
            validation_status=ValidationStatus.OK,
            proceed=True,
            validation_id=validation_id,
            context_freshness_seconds=any_freshness,
            source_consulted=",".join(source_ids),
        )

    def _compare(
        self,
        *,
        context_used: Dict[str, Any],
        source_value: Any,
        source: SourceOfTruth,
    ) -> Optional[Discrepancy]:
        """
        Compara `context_used` vs la fuente de verdad.

        Política v1.0 (simple pero robusta):
            - Si `source_value` es dict: comparar campo por campo solo los campos
              que están en AMBOS (context_used ∩ source_value)
            - Si `source_value` es str (env var): no comparar directamente; el
              hilo no debe declarar el valor del secret; no podemos validar shape
              sin un parser específico → retornar None (validación pasa)
        """
        if not isinstance(source_value, dict):
            # Fuentes tipo env_var no se comparan campo a campo
            return None

        for key, expected in source_value.items():
            if key not in context_used:
                continue
            actual = context_used[key]
            if str(actual).strip() != str(expected).strip():
                return Discrepancy(
                    field=key,
                    context_used=actual,
                    source_of_truth=expected,
                    source=source.location,
                    source_last_updated=source.last_known_update,
                )
        return None

    async def invalidate_cache(self, source_id: str) -> None:
        """Fuerza refresh de una fuente en el próximo `validate`."""
        await self._cache.invalidate(source_id)

    async def get_freshness(self, source_id: str) -> Optional[int]:
        """Edad en segundos del cache. None si no está cacheado."""
        return await self._cache.get_freshness(source_id)


__all__ = ["MementoValidator"]
