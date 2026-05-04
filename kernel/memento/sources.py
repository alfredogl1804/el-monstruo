"""
Lectores de fuentes de verdad para la Capa Memento.

Cada lector retorna dict con shape uniforme:
    {
        "value": <dict | str>,        # valor parseado
        "fetched_at": <datetime>,     # timestamp de cuando se leyó
        "source_id": <str>,           # ID de la fuente consultada
        "raw_hash": <str>,            # SHA-256 truncado del contenido normalizado
    }

Disciplina anti-Dory aplicada:
    - os.environ.get() en cada uso (no cacheo al boot)
    - Pre-flight de variables antes de hacer requests externos
    - Cache TTL configurable por fuente (lock asyncio thread-safe)
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional


REPO_ROOT_ENV = "MEMENTO_REPO_ROOT"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_content(content: str) -> str:
    """SHA-256 truncado a 12 chars del contenido normalizado."""
    normalized = content.strip().encode("utf-8", errors="replace")
    return hashlib.sha256(normalized).hexdigest()[:12]


def _resolve_repo_root() -> Path:
    """Lee MEMENTO_REPO_ROOT fresh desde env. Default: cwd."""
    root = os.environ.get(REPO_ROOT_ENV, "").strip()
    if root:
        path = Path(root).expanduser().resolve()
        if path.exists():
            return path
    return Path.cwd()


def read_credential_source(path: str) -> Dict[str, Any]:
    """
    Lee un archivo `credentials.md` del repo y parsea su contenido.

    Formato esperado (parser `credentials_md_v1`):
        # Credentials — <project>
        - **host:** gateway05.us-east-1.prod.aws.tidbcloud.com
        - **user:** 37Hy7adB53QmFW4.root
        - **db:** R5HMD5sAyPAWW34dhuZc9u
        - **credential_hash_first_8:** 4N6caSwp

    Args:
        path: ruta relativa al root del repo (ej. "skills/ticketlike-ops/references/credentials.md")

    Returns:
        dict con shape uniforme. `value` contiene el dict parseado.

    Raises:
        FileNotFoundError: si el archivo no existe en el repo
    """
    repo_root = _resolve_repo_root()
    full_path = repo_root / path
    if not full_path.exists():
        raise FileNotFoundError(f"credentials_source_missing: {full_path}")

    content = full_path.read_text(encoding="utf-8")
    parsed: Dict[str, str] = {}
    # Patrón: "- **key:** value" o "- key: value"
    pattern = re.compile(r"^\s*-\s+\*?\*?(?P<key>[a-zA-Z_][a-zA-Z0-9_]*)\*?\*?\s*:\s*(?P<value>.+?)\s*$", re.MULTILINE)
    for match in pattern.finditer(content):
        key = match.group("key").strip().lower()
        value = match.group("value").strip()
        # Quitar markdown emphasis residual y backticks
        value = value.strip("`*_").strip()
        parsed[key] = value

    return {
        "value": parsed,
        "fetched_at": _now(),
        "source_id": path,
        "raw_hash": _hash_content(content),
    }


async def read_railway_env_var(
    service: str,
    var_name: str,
    *,
    api_token_env: str = "RAILWAY_API_TOKEN",
    http_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Consulta el valor actual de una env var en Railway via API.

    NOTA: el kernel sí leería su propia env (`os.environ.get`), pero el
    validator valida contra Railway as source-of-truth para hilos externos
    que pueden tener contexto compactado.

    Args:
        service: identificador del servicio (ej. "el-monstruo-kernel")
        var_name: nombre de la variable (ej. "MONSTRUO_API_KEY")
        api_token_env: nombre del env var que contiene el Railway token
        http_client: cliente async para tests (debe exponer .post())

    Returns:
        dict con shape uniforme. `value` es el string del env var.

    Raises:
        RuntimeError: si no hay token o la API falla
    """
    token = os.environ.get(api_token_env, "").strip()
    if not token:
        raise RuntimeError(f"railway_token_missing: {api_token_env} not in env")

    if http_client is None:
        # Lazy import para no exigir aiohttp si no se usa
        try:
            import aiohttp  # type: ignore
        except ImportError as exc:
            raise RuntimeError("railway_http_client_missing: pip install aiohttp") from exc

        async with aiohttp.ClientSession() as session:
            return await _railway_query(session, token, service, var_name)
    else:
        return await _railway_query(http_client, token, service, var_name)


async def _railway_query(session: Any, token: str, service: str, var_name: str) -> Dict[str, Any]:
    """Helper interno: query GraphQL a Railway API."""
    query = """
    query ($service: String!) {
      service(name: $service) {
        variables { name, value }
      }
    }
    """
    payload = {"query": query, "variables": {"service": service}}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with session.post(
        "https://backboard.railway.app/graphql/v2",
        json=payload,
        headers=headers,
    ) as resp:
        if resp.status >= 400:
            text = await resp.text()
            raise RuntimeError(f"railway_api_error: status={resp.status} body={text[:200]}")
        data = await resp.json()

    variables = (
        data.get("data", {})
        .get("service", {})
        .get("variables", [])
    )
    if not isinstance(variables, list):
        raise RuntimeError(f"railway_unexpected_response: {data!r}")

    for entry in variables:
        if entry.get("name") == var_name:
            value = entry.get("value", "")
            return {
                "value": value,
                "fetched_at": _now(),
                "source_id": f"{service}:{var_name}",
                "raw_hash": _hash_content(value),
            }

    raise RuntimeError(f"railway_var_not_found: service={service} var={var_name}")


# ---------------------------------------------------------------------------
# Cache con TTL configurable
# ---------------------------------------------------------------------------

@dataclass
class _CacheEntry:
    value: Dict[str, Any]
    fetched_at: datetime
    ttl_seconds: int


class SourceCache:
    """
    Cache local thread-safe de fuentes de verdad.

    Uso típico:
        cache = SourceCache()
        result = await cache.get_or_fetch(
            source_id="ticketlike_credentials",
            ttl_seconds=60,
            fetcher=lambda: read_credential_source("skills/ticketlike-ops/references/credentials.md"),
        )
    """

    def __init__(self) -> None:
        self._entries: Dict[str, _CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get_or_fetch(
        self,
        *,
        source_id: str,
        ttl_seconds: int,
        fetcher: Callable[[], Any],
    ) -> Dict[str, Any]:
        """
        Devuelve el valor cacheado si está fresh; si no, llama a `fetcher` y cachea.

        `fetcher` puede ser sync o async (coroutine).
        """
        async with self._lock:
            entry = self._entries.get(source_id)
            now = _now()
            if entry is not None:
                age = (now - entry.fetched_at).total_seconds()
                if age < entry.ttl_seconds:
                    # cache hit
                    return entry.value

            # cache miss → llamar al fetcher
            raw = fetcher()
            if asyncio.iscoroutine(raw):
                raw = await raw

            if not isinstance(raw, dict) or "value" not in raw:
                raise RuntimeError(f"source_fetcher_invalid_shape: source_id={source_id}")

            self._entries[source_id] = _CacheEntry(
                value=raw,
                fetched_at=now,
                ttl_seconds=ttl_seconds,
            )
            return raw

    async def invalidate(self, source_id: str) -> None:
        async with self._lock:
            self._entries.pop(source_id, None)

    async def get_freshness(self, source_id: str) -> Optional[int]:
        """Edad en segundos del cache para `source_id`. None si no está cacheado."""
        async with self._lock:
            entry = self._entries.get(source_id)
            if entry is None:
                return None
            return int((_now() - entry.fetched_at).total_seconds())

    async def clear(self) -> None:
        async with self._lock:
            self._entries.clear()


__all__ = [
    "read_credential_source",
    "read_railway_env_var",
    "SourceCache",
]
