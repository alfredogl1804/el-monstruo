"""
Memento Preflight Library — Sprint Memento Bloque 4 (Capa Memoria Soberana v1.0)
=================================================================================

Cliente standalone para el endpoint POST /v1/memento/validate.

Diseño y decisiones (Capa Memento — autoría + fecha + contexto):

  AUTORÍA: Hilo Manus Ejecutor
  FECHA:   2026-05-04 (Sprint Memento Bloque 4)
  CONTEXTO: Cowork firmó B3 verde y emitió spec del B4 indicando que la
            library debe ser standalone (sin depender del kernel del
            Monstruo) para que cualquier hilo Manus en cualquier sandbox
            pueda hacer pip install / copy y empezar a usarla.

DECISIONES CONTEXTUALES:

1. SOLO httpx + stdlib. Pydantic no es obligatorio (la library define
   PreflightResult como dataclass para no forzar dependencia adicional).
   El endpoint del kernel sí valida con Pydantic, pero el cliente no.

2. Decorator detecta async vs sync automáticamente vía
   inspect.iscoroutinefunction. Para funciones sync, la llamada al
   endpoint corre en un thread con asyncio.run en un loop nuevo, para
   no bloquear ni asumir loop existente.

3. Cache local in-memory con TTL configurable (default 60s). Key
   estable basada en (operation, sorted(context_used.items())).
   Thread-safe via threading.Lock.

4. Retry con backoff exponencial: 1s → 2s → 4s (3 intentos por defecto,
   configurable via MEMENTO_RETRY_ATTEMPTS).

5. Fallback policy: "block" (default) levanta MementoPreflightUnavailableError
   si todos los retries fallan; "warn" loguea via stdlib logging y permite
   ejecución (útil para hilos no críticos / dev). Configurable via env
   MEMENTO_FALLBACK_POLICY.

6. Auth dual (hallazgo del Bloque 3 smoke productivo): el endpoint acepta
   tanto X-API-Key como Authorization: Bearer <key>. Default = x-api-key.
   Configurable via MEMENTO_AUTH_FORMAT.

7. Anti-Dory: TODA lectura de env (URL, API key, formato auth, fallback)
   se hace en cada request, no se cachea al import. Test específico
   valida que monkeypatch.setenv en runtime actualiza el comportamiento.

8. Idempotencia: PreflightCache.invalidate() público para uso explícito
   en escenarios donde el contexto cambió entre validaciones (ej. después
   de rotar credenciales, el hilo debe invalidar para no usar el resultado
   stale).

REFS:
    - bridge/sprint_memento_preinvestigation/spec_sprint_memento.md
    - kernel/memento_routes.py (endpoint)
    - kernel/memento/models.py (shape de Request/Response)
    - tools/memento_preflight_README.md (guía operativa para los 3 hilos)
"""
from __future__ import annotations

import asyncio
import functools
import hashlib
import inspect
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, Union

import httpx

logger = logging.getLogger("memento.preflight")

# ===========================================================================
# Defaults (overridables vía env)
# ===========================================================================

DEFAULT_VALIDATOR_URL = (
    "https://el-monstruo-kernel-production.up.railway.app/v1/memento/validate"
)
DEFAULT_TIMEOUT_SECONDS = 5.0
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_BACKOFF_BASE = 1.0  # 1s, 2s, 4s
DEFAULT_CACHE_TTL_SECONDS = 60
DEFAULT_AUTH_FORMAT = "x-api-key"  # "x-api-key" | "bearer"
DEFAULT_FALLBACK_POLICY = "block"  # "block" | "warn"


# ===========================================================================
# Excepciones
# ===========================================================================

class MementoPreflightError(Exception):
    """Base para errores de pre-flight."""


class MementoPreflightUnavailableError(MementoPreflightError):
    """El endpoint no respondió tras todos los retries (fallback=block)."""


class MementoPreflightDiscrepancyError(MementoPreflightError):
    """proceed=False — la validación detectó discrepancia o la operación es desconocida."""

    def __init__(self, message: str, result: "PreflightResult") -> None:
        super().__init__(message)
        self.result = result


class MementoPreflightConfigError(MementoPreflightError):
    """Falta configuración crítica (ej. MONSTRUO_API_KEY o MEMENTO_API_KEY)."""


# ===========================================================================
# Resultado
# ===========================================================================

@dataclass
class PreflightResult:
    """
    Resultado parseado del endpoint /v1/memento/validate.

    Espejo del shape devuelto por kernel/memento_routes.py:memento_validate.
    """
    validation_id: str
    validation_status: str  # "ok" | "discrepancy_detected" | "unknown_operation" | "source_unavailable"
    proceed: bool
    context_freshness_seconds: int = 0
    discrepancy: Optional[Dict[str, Any]] = None
    remediation: Optional[str] = None
    source_consulted: Optional[str] = None
    persistence_failed: bool = False
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_response_json(cls, data: Dict[str, Any]) -> "PreflightResult":
        return cls(
            validation_id=data.get("validation_id", ""),
            validation_status=data.get("validation_status", ""),
            proceed=bool(data.get("proceed", False)),
            context_freshness_seconds=int(data.get("context_freshness_seconds", 0)),
            discrepancy=data.get("discrepancy"),
            remediation=data.get("remediation"),
            source_consulted=data.get("source_consulted"),
            persistence_failed=bool(data.get("persistence_failed", False)),
            raw=data,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ===========================================================================
# Cache local thread-safe
# ===========================================================================

class PreflightCache:
    """
    Cache LRU-naive (sin tope de tamaño en v1.0) con TTL.
    Thread-safe vía threading.Lock.

    Diseño:
        - Key derivada de (operation, sorted(context_used.items())) →
          hash estable independiente del orden de keys del dict.
        - Value = (PreflightResult, expires_at_epoch).
        - get() devuelve None si la key no existe O si está expirada
          (y la elimina en ese caso).
        - invalidate(operation, context_used) borra una entrada específica.
        - clear() vacía todo el cache.
    """
    def __init__(self, default_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS) -> None:
        self._store: Dict[str, tuple[PreflightResult, float]] = {}
        self._lock = threading.Lock()
        self._default_ttl = default_ttl_seconds

    @staticmethod
    def _make_key(operation: str, context_used: Dict[str, Any]) -> str:
        try:
            ctx_str = json.dumps(context_used, sort_keys=True, default=str)
        except Exception:
            ctx_str = repr(sorted((str(k), str(v)) for k, v in context_used.items()))
        h = hashlib.sha256(f"{operation}|{ctx_str}".encode("utf-8")).hexdigest()
        return h[:32]

    def get(self, operation: str, context_used: Dict[str, Any]) -> Optional[PreflightResult]:
        key = self._make_key(operation, context_used)
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            result, expires_at = entry
            if time.time() >= expires_at:
                self._store.pop(key, None)
                return None
            return result

    def set(
        self,
        operation: str,
        context_used: Dict[str, Any],
        result: PreflightResult,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        key = self._make_key(operation, context_used)
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        with self._lock:
            self._store[key] = (result, time.time() + ttl)

    def invalidate(self, operation: str, context_used: Dict[str, Any]) -> bool:
        key = self._make_key(operation, context_used)
        with self._lock:
            return self._store.pop(key, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)


# ===========================================================================
# Config helpers (siempre lectura fresh — anti-Dory)
# ===========================================================================

def _resolve_validator_url() -> str:
    return os.environ.get("MEMENTO_VALIDATOR_URL", DEFAULT_VALIDATOR_URL)


def _resolve_api_key() -> str:
    """
    Acepta MEMENTO_API_KEY (alias preferido para hilos no-kernel) o
    MONSTRUO_API_KEY (mismo key del kernel).
    """
    key = (
        os.environ.get("MEMENTO_API_KEY", "").strip()
        or os.environ.get("MONSTRUO_API_KEY", "").strip()
    )
    if not key:
        raise MementoPreflightConfigError(
            "memento_api_key_missing: set MEMENTO_API_KEY or MONSTRUO_API_KEY env var"
        )
    return key


def _resolve_auth_format() -> str:
    fmt = os.environ.get("MEMENTO_AUTH_FORMAT", DEFAULT_AUTH_FORMAT).lower()
    if fmt not in ("x-api-key", "bearer"):
        logger.warning("memento_invalid_auth_format got=%s fallback=%s", fmt, DEFAULT_AUTH_FORMAT)
        fmt = DEFAULT_AUTH_FORMAT
    return fmt


def _resolve_fallback_policy() -> str:
    policy = os.environ.get("MEMENTO_FALLBACK_POLICY", DEFAULT_FALLBACK_POLICY).lower()
    if policy not in ("block", "warn"):
        logger.warning("memento_invalid_fallback_policy got=%s fallback=%s", policy, DEFAULT_FALLBACK_POLICY)
        policy = DEFAULT_FALLBACK_POLICY
    return policy


def _resolve_int_env(env_var: str, default: int) -> int:
    try:
        return int(os.environ.get(env_var, str(default)))
    except (ValueError, TypeError):
        return default


def _resolve_float_env(env_var: str, default: float) -> float:
    try:
        return float(os.environ.get(env_var, str(default)))
    except (ValueError, TypeError):
        return default


def _build_auth_headers(api_key: str, auth_format: str) -> Dict[str, str]:
    if auth_format == "bearer":
        return {"Authorization": f"Bearer {api_key}"}
    return {"X-API-Key": api_key}


# ===========================================================================
# Cache singleton (compartido entre llamadas de la misma library)
# ===========================================================================

_GLOBAL_CACHE = PreflightCache(default_ttl_seconds=DEFAULT_CACHE_TTL_SECONDS)


def get_cache() -> PreflightCache:
    """Retorna el cache singleton. Útil para invalidar manualmente o limpiar en tests."""
    return _GLOBAL_CACHE


# ===========================================================================
# Cliente principal
# ===========================================================================

async def _do_request(
    *,
    url: str,
    payload: Dict[str, Any],
    headers: Dict[str, str],
    timeout: float,
    http_client_factory: Optional[Callable[[], httpx.AsyncClient]] = None,
) -> httpx.Response:
    """Una sola llamada HTTP. Inyectable para tests."""
    if http_client_factory is None:
        http_client_factory = lambda: httpx.AsyncClient(timeout=timeout)
    async with http_client_factory() as client:
        return await client.post(url, json=payload, headers=headers)


async def preflight_check_async(
    *,
    operation: str,
    context_used: Dict[str, Any],
    hilo_id: Optional[str] = None,
    intent_summary: Optional[str] = None,
    use_cache: bool = True,
    cache_ttl_seconds: Optional[int] = None,
    timeout: Optional[float] = None,
    retry_attempts: Optional[int] = None,
    retry_backoff_base: Optional[float] = None,
    fallback_policy: Optional[str] = None,
    http_client_factory: Optional[Callable[[], httpx.AsyncClient]] = None,
) -> PreflightResult:
    """
    Versión async de preflight_check. Llama al endpoint /v1/memento/validate.

    Args:
        operation: ID de la operación crítica (debe estar en el catálogo
            memento_critical_operations).
        context_used: Dict con el contexto declarado por el hilo.
        hilo_id: Identificador del hilo. Default: env MEMENTO_HILO_ID o
            "hilo_unknown".
        intent_summary: Texto libre con el propósito.
        use_cache: Si True, intenta servir desde cache antes de llamar.
        cache_ttl_seconds: TTL para guardar en cache (default 60s).
        timeout: Timeout HTTP por request (default 5s).
        retry_attempts: Reintentos en caso de fallo de red (default 3).
        retry_backoff_base: Base del backoff exponencial (default 1s).
        fallback_policy: "block" o "warn" si todos los retries fallan.
        http_client_factory: Factory para inyectar cliente custom (tests).

    Returns:
        PreflightResult con todos los campos del endpoint + raw response.

    Raises:
        MementoPreflightConfigError: si falta API key.
        MementoPreflightUnavailableError: si todos los retries fallan
            y fallback_policy="block".
        MementoPreflightDiscrepancyError: NO se levanta acá; la library
            devuelve PreflightResult crudo, y el decorator (o el caller)
            decide si raise.
    """
    # Lectura fresh de config (anti-Dory)
    url = _resolve_validator_url()
    api_key = _resolve_api_key()
    auth_format = _resolve_auth_format()
    timeout = timeout if timeout is not None else _resolve_float_env(
        "MEMENTO_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS
    )
    retry_attempts = retry_attempts if retry_attempts is not None else _resolve_int_env(
        "MEMENTO_RETRY_ATTEMPTS", DEFAULT_RETRY_ATTEMPTS
    )
    retry_backoff_base = retry_backoff_base if retry_backoff_base is not None else _resolve_float_env(
        "MEMENTO_RETRY_BACKOFF_BASE", DEFAULT_RETRY_BACKOFF_BASE
    )
    fallback_policy = (fallback_policy or _resolve_fallback_policy()).lower()
    if fallback_policy not in ("block", "warn"):
        fallback_policy = "block"

    if not hilo_id:
        hilo_id = os.environ.get("MEMENTO_HILO_ID", "hilo_unknown")

    # Cache hit?
    if use_cache:
        cached = _GLOBAL_CACHE.get(operation, context_used)
        if cached is not None:
            logger.debug("memento_preflight_cache_hit operation=%s validation_id=%s", operation, cached.validation_id)
            return cached

    payload = {
        "hilo_id": hilo_id,
        "operation": operation,
        "context_used": context_used,
    }
    if intent_summary:
        payload["intent_summary"] = intent_summary

    headers = _build_auth_headers(api_key, auth_format)
    headers["Content-Type"] = "application/json"

    last_exc: Optional[Exception] = None
    for attempt in range(1, retry_attempts + 1):
        try:
            response = await _do_request(
                url=url,
                payload=payload,
                headers=headers,
                timeout=timeout,
                http_client_factory=http_client_factory,
            )
            if response.status_code == 200:
                data = response.json()
                result = PreflightResult.from_response_json(data)
                if use_cache:
                    _GLOBAL_CACHE.set(operation, context_used, result, ttl_seconds=cache_ttl_seconds)
                return result
            elif response.status_code in (401, 403):
                raise MementoPreflightConfigError(
                    f"memento_auth_failed: status={response.status_code} body={response.text[:200]}"
                )
            elif response.status_code == 422:
                # Body inválido — no reintentar, error del caller
                raise MementoPreflightError(
                    f"memento_request_invalid: {response.text[:300]}"
                )
            else:
                # 500, 503, etc. — reintentar
                last_exc = MementoPreflightError(
                    f"memento_endpoint_status_{response.status_code}: {response.text[:200]}"
                )
                logger.warning("memento_preflight_retry_due_to_status attempt=%s status=%s",
                    attempt, response.status_code)
        except (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError, httpx.ReadError) as exc:
            last_exc = exc
            logger.warning("memento_preflight_retry_due_to_exception attempt=%s exc_type=%s error=%s",
                attempt, type(exc).__name__, str(exc))
        except (MementoPreflightConfigError, MementoPreflightError):
            # Errores hard — no reintentar
            raise

        # Backoff antes del próximo intento (excepto en el último)
        if attempt < retry_attempts:
            backoff = retry_backoff_base * (2 ** (attempt - 1))
            await asyncio.sleep(backoff)

    # Todos los retries fallaron
    if fallback_policy == "warn":
        logger.warning("memento_preflight_unavailable_warn operation=%s attempts=%s last_error=%s",
            operation, retry_attempts, str(last_exc))
        # Devolver un resultado "permisivo" no validado
        return PreflightResult(
            validation_id="mv_fallback_warn",
            validation_status="source_unavailable",
            proceed=True,  # warn = permite ejecución
            context_freshness_seconds=0,
            discrepancy=None,
            remediation=f"endpoint_unavailable_after_{retry_attempts}_retries: {last_exc}",
            source_consulted=None,
            persistence_failed=True,
            raw={"fallback": "warn", "last_error": str(last_exc)},
        )

    # fallback_policy == "block"
    raise MementoPreflightUnavailableError(
        f"memento_endpoint_unavailable_after_{retry_attempts}_retries: {last_exc}"
    )


def preflight_check(
    *,
    operation: str,
    context_used: Dict[str, Any],
    hilo_id: Optional[str] = None,
    intent_summary: Optional[str] = None,
    use_cache: bool = True,
    cache_ttl_seconds: Optional[int] = None,
    timeout: Optional[float] = None,
    retry_attempts: Optional[int] = None,
    retry_backoff_base: Optional[float] = None,
    fallback_policy: Optional[str] = None,
    http_client_factory: Optional[Callable[[], httpx.AsyncClient]] = None,
) -> PreflightResult:
    """
    Versión sync de preflight_check.

    Si ya hay un loop corriendo en el thread, levanta RuntimeError —
    en ese caso usar preflight_check_async directamente con await.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            raise RuntimeError(
                "memento_preflight_sync_in_running_loop: usá preflight_check_async + await"
            )
    except RuntimeError:
        pass  # No hay loop activo, podemos crear uno nuevo

    return asyncio.run(preflight_check_async(
        operation=operation,
        context_used=context_used,
        hilo_id=hilo_id,
        intent_summary=intent_summary,
        use_cache=use_cache,
        cache_ttl_seconds=cache_ttl_seconds,
        timeout=timeout,
        retry_attempts=retry_attempts,
        retry_backoff_base=retry_backoff_base,
        fallback_policy=fallback_policy,
        http_client_factory=http_client_factory,
    ))


# ===========================================================================
# Decorator
# ===========================================================================

F = TypeVar("F", bound=Callable[..., Any])


def requires_memento_preflight(
    operation: str,
    *,
    context_from_kwargs: Optional[list[str]] = None,
    hilo_id: Optional[str] = None,
    intent_summary: Optional[str] = None,
    use_cache: bool = True,
    cache_ttl_seconds: Optional[int] = None,
    timeout: Optional[float] = None,
    retry_attempts: Optional[int] = None,
    fallback_policy: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Decorator que ejecuta pre-flight ANTES del cuerpo de la función.

    Args:
        operation: ID de la operación crítica.
        context_from_kwargs: Lista de nombres de kwargs/args a usar como
            context_used. Si None, infiere TODOS los kwargs como context.
        hilo_id: Override del hilo_id (default: env MEMENTO_HILO_ID).
        intent_summary: Override del propósito.
        use_cache: Si True, hits de cache se aprovechan.
        ...

    Comportamiento:
        - Llama a preflight_check_async (o sync si la función decorada es sync).
        - Si proceed=False → raise MementoPreflightDiscrepancyError con detalle.
        - Si proceed=True → ejecuta el cuerpo normalmente.
        - Si endpoint unavailable + fallback="block" → raise MementoPreflightUnavailableError
          (no se ejecuta el cuerpo).
        - Si endpoint unavailable + fallback="warn" → loguea y ejecuta el cuerpo.

    Ejemplo:
        @requires_memento_preflight(
            operation="sql_against_production",
            context_from_kwargs=["host", "user"],
        )
        async def query_tidb(host: str, user: str, query: str): ...
    """
    def decorator(func: F) -> F:
        is_async = inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)

        def _build_context(args, kwargs) -> Dict[str, Any]:
            try:
                bound = sig.bind_partial(*args, **kwargs)
                bound.apply_defaults()
            except TypeError:
                bound = None

            ctx: Dict[str, Any] = {}
            if context_from_kwargs:
                # Modo explícito — solo los nombres pedidos
                if bound is not None:
                    for name in context_from_kwargs:
                        if name in bound.arguments:
                            ctx[name] = bound.arguments[name]
            else:
                # Modo implícito — TODO el bound except 'self' / 'cls'
                if bound is not None:
                    for name, val in bound.arguments.items():
                        if name in ("self", "cls"):
                            continue
                        # Filtrar valores no JSON-serializables groseros
                        try:
                            json.dumps(val, default=str)
                            ctx[name] = val
                        except Exception:
                            pass
            return ctx

        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                ctx = _build_context(args, kwargs)
                result = await preflight_check_async(
                    operation=operation,
                    context_used=ctx,
                    hilo_id=hilo_id,
                    intent_summary=intent_summary,
                    use_cache=use_cache,
                    cache_ttl_seconds=cache_ttl_seconds,
                    timeout=timeout,
                    retry_attempts=retry_attempts,
                    fallback_policy=fallback_policy,
                )
                if not result.proceed:
                    raise MementoPreflightDiscrepancyError(
                        f"memento_preflight_blocked: status={result.validation_status} "
                        f"remediation={result.remediation}",
                        result=result,
                    )
                return await func(*args, **kwargs)
            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            ctx = _build_context(args, kwargs)
            result = preflight_check(
                operation=operation,
                context_used=ctx,
                hilo_id=hilo_id,
                intent_summary=intent_summary,
                use_cache=use_cache,
                cache_ttl_seconds=cache_ttl_seconds,
                timeout=timeout,
                retry_attempts=retry_attempts,
                fallback_policy=fallback_policy,
            )
            if not result.proceed:
                raise MementoPreflightDiscrepancyError(
                    f"memento_preflight_blocked: status={result.validation_status} "
                    f"remediation={result.remediation}",
                    result=result,
                )
            return func(*args, **kwargs)
        return sync_wrapper  # type: ignore[return-value]

    return decorator


__all__ = [
    "PreflightResult",
    "PreflightCache",
    "MementoPreflightError",
    "MementoPreflightUnavailableError",
    "MementoPreflightDiscrepancyError",
    "MementoPreflightConfigError",
    "preflight_check",
    "preflight_check_async",
    "requires_memento_preflight",
    "get_cache",
]
