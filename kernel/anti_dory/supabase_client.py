"""
kernel/anti_dory/supabase_client.py
====================================

Implementación concreta del Protocol `SupabaseRPCClient` declarado en
`kernel.anti_dory.context_broker`. Habilita FASE D del sprint
MANUS-ANTI-DORY-002 v1 (activación operacional del Context Broker).

Diseño
------
- **Sincrónico** por contrato: el Protocol declara `call_rpc(name, params) -> Any`
  como método sync. El callsite (`tools/manus_bridge.create_task`) es sync.
- **httpx.Client** dedicado (no `AsyncClient`): coherente con el contrato.
- **PostgREST RPC endpoint**: `POST {SUPABASE_URL}/rest/v1/rpc/{function_name}`
  con headers `apikey` + `Authorization: Bearer ...` + `Content-Type: application/json`.
  Patrón estándar Supabase PostgREST.
- **Fail-closed sobre el cliente, fail-open sobre el broker**: si `httpx` lanza,
  `call_rpc` propaga la excepción y el broker (en `context_broker.py`) la
  captura en su `try/except RuntimeError` y devuelve `attachment_ok=False` con
  `fallback_reason="rpc_error: ..."` (comportamiento ya implementado en FASE B
  y validado por test `test_broker_exception_fallback_to_original_prompt`).

Factory default
---------------
`build_default_broker_factory()` retorna una factory invocable por
`tools/manus_bridge.set_anti_dory_broker_factory()` que construye un
`ContextBroker` con un `HTTPXSupabaseRPCClient` configurado desde env vars
`SUPABASE_URL` y `SUPABASE_SERVICE_KEY`.

Si las env vars no están configuradas, la factory devuelve `None` para activar
fail-open en `tools/manus_bridge.create_task` (no se hidrata, se loguea WARN).

Constraints respetados
----------------------
- F24: NO inventa firmas. Implementa exactamente el Protocol existente.
- F26: código real, no doctrina.
- DSC-S: NO imprime ni loguea secret values (SERVICE_KEY masked en logs).
- No-CRUCE: NO toca `kernel/cowork_runtime/*`, `tools/cowork_guardian.py`,
  `kernel/main.py`, `kernel/engine.py`, migrations 0001-0028.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Callable, Optional

import httpx

from kernel.anti_dory.context_broker import ContextBroker

logger = logging.getLogger(__name__)


# =============================================================================
# Constantes
# =============================================================================

# Timeout default para llamadas RPC. Anti-Dory broker NUNCA debe bloquear
# task.create más allá de este límite. Si timeout → broker fail-open.
_DEFAULT_RPC_TIMEOUT_SECONDS: float = float(os.environ.get("ANTI_DORY_RPC_TIMEOUT_SECONDS", "5.0"))

# Connect timeout separado (no debe colgar arrancando la conexión).
_DEFAULT_RPC_CONNECT_TIMEOUT_SECONDS: float = float(os.environ.get("ANTI_DORY_RPC_CONNECT_TIMEOUT_SECONDS", "2.0"))

# User-Agent identificable para logs Supabase / observabilidad.
_USER_AGENT = "el-monstruo/anti-dory-v1 (sprint MANUS-ANTI-DORY-002)"


# =============================================================================
# Cliente concreto: HTTPXSupabaseRPCClient
# =============================================================================


class HTTPXSupabaseRPCClient:
    """
    Implementación concreta sincrónica del Protocol `SupabaseRPCClient`
    declarado en `kernel.anti_dory.context_broker`.

    Usa `httpx.Client` para llamar a Supabase PostgREST RPC endpoint:
        POST {url}/rest/v1/rpc/{function_name}
        Headers:
          apikey: {service_key}
          Authorization: Bearer {service_key}
          Content-Type: application/json
        Body: JSON-serialized params dict.

    Args
    ----
    url : str
        Supabase project URL (e.g. "https://xxx.supabase.co").
    service_key : str
        Supabase service role key. SECRET — nunca loguear su valor.
    timeout : float, optional
        Timeout en segundos por request. Default 5.0s.
    connect_timeout : float, optional
        Connect timeout en segundos. Default 2.0s.
    http_client : httpx.Client, optional
        Cliente httpx pre-construido (útil para tests que mockean transport).
        Si no se pasa, se construye uno nuevo.

    Notes
    -----
    - Esta clase NO contiene su propio retry: errores propagan a broker que
      fail-opens. Diseño deliberado para no agregar latencia al callsite.
    - El cliente es reusable (mantener una instancia por proceso reduce overhead
      de conexión TLS). La factory default cachea una instancia global.
    """

    def __init__(
        self,
        url: str,
        service_key: str,
        *,
        timeout: float = _DEFAULT_RPC_TIMEOUT_SECONDS,
        connect_timeout: float = _DEFAULT_RPC_CONNECT_TIMEOUT_SECONDS,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        if not url:
            raise ValueError("HTTPXSupabaseRPCClient requires non-empty url")
        if not service_key:
            raise ValueError("HTTPXSupabaseRPCClient requires non-empty service_key")

        # Normalizar URL: garantizar terminación sin "/"
        self._url = url.rstrip("/")
        self._service_key = service_key
        self._timeout = timeout
        self._connect_timeout = connect_timeout

        # Cliente httpx reusable (inyectable para tests).
        if http_client is None:
            self._client = httpx.Client(
                timeout=httpx.Timeout(
                    self._timeout,
                    connect=self._connect_timeout,
                ),
                headers={
                    "apikey": self._service_key,
                    "Authorization": f"Bearer {self._service_key}",
                    "Content-Type": "application/json",
                    "User-Agent": _USER_AGENT,
                    # Prefer: return=representation es opcional pero
                    # útil para que RPCs devuelvan el JSON completo.
                    "Prefer": "return=representation",
                },
            )
            self._owns_client = True
        else:
            self._client = http_client
            self._owns_client = False

    # -------------------------------------------------------------------------
    # Contrato Protocol: call_rpc(name, params) -> Any
    # -------------------------------------------------------------------------

    def call_rpc(self, name: str, params: dict[str, Any]) -> Any:
        """
        Invoca una función RPC de Supabase. Sincrónico por contrato.

        Returns
        -------
        Any
            JSON-decoded response body de PostgREST (típicamente list[dict] o dict).

        Raises
        ------
        httpx.HTTPError
            Si la llamada falla (timeout, connection error, HTTP >= 400, etc.).
            El broker captura esto y hace fail-open.
        """
        if not name or not isinstance(name, str):
            raise ValueError(f"RPC name must be non-empty str, got: {name!r}")
        if not isinstance(params, dict):
            raise ValueError(f"RPC params must be dict, got: {type(params).__name__}")

        endpoint = f"{self._url}/rest/v1/rpc/{name}"

        # Log estructurado SIN secret value. Solo el nombre del RPC y keys de
        # params (no values, que pueden ser sensibles).
        logger.debug(
            "anti_dory_rpc_call",
            extra={
                "rpc_name": name,
                "param_keys": sorted(params.keys()),
                "endpoint_host": self._url.split("//", 1)[-1].split("/")[0],
            },
        )

        response = self._client.post(endpoint, json=params)

        # PostgREST retorna 200/201 en happy path. RPCs sin retorno pueden
        # devolver 204.
        if response.status_code >= 400:
            # Cuerpo puede contener detalle del error PostgREST. NO incluir
            # request body en log (podría tener secret).
            try:
                error_detail = response.json()
            except Exception:
                error_detail = response.text[:500]
            logger.warning(
                "anti_dory_rpc_error",
                extra={
                    "rpc_name": name,
                    "status_code": response.status_code,
                    "error_detail": error_detail,
                },
            )
            response.raise_for_status()

        # 204 No Content → devolver None (caller broker lo trata como pack vacío).
        if response.status_code == 204 or not response.content:
            return None

        return response.json()

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    def close(self) -> None:
        """Cierra el cliente HTTP si es propio. No-op si fue inyectado."""
        if self._owns_client and self._client is not None:
            try:
                self._client.close()
            except Exception as exc:  # pragma: no cover - cleanup
                logger.warning(
                    "anti_dory_client_close_error",
                    extra={"error": str(exc)},
                )

    def __enter__(self) -> "HTTPXSupabaseRPCClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


# =============================================================================
# Factory default — entry-point para tools/manus_bridge
# =============================================================================


# Caché de instancia global. Una sola conexión por proceso es suficiente y
# preferible (reuso TLS).
_GLOBAL_CLIENT: Optional[HTTPXSupabaseRPCClient] = None
_GLOBAL_BROKER: Optional[ContextBroker] = None


def _get_global_client() -> Optional[HTTPXSupabaseRPCClient]:
    """
    Construye (o reusa) el cliente global desde env vars `SUPABASE_URL` y
    `SUPABASE_SERVICE_KEY`. Si alguno falta, retorna None (fail-open).
    """
    global _GLOBAL_CLIENT

    if _GLOBAL_CLIENT is not None:
        return _GLOBAL_CLIENT

    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()

    if not url or not key:
        logger.warning(
            "anti_dory_supabase_not_configured",
            extra={
                "has_url": bool(url),
                "has_key": bool(key),
                "hint": "set SUPABASE_URL + SUPABASE_SERVICE_KEY",
            },
        )
        return None

    try:
        _GLOBAL_CLIENT = HTTPXSupabaseRPCClient(url=url, service_key=key)
        logger.info(
            "anti_dory_supabase_client_initialized",
            extra={
                "endpoint_host": url.split("//", 1)[-1].split("/")[0],
            },
        )
        return _GLOBAL_CLIENT
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(
            "anti_dory_supabase_client_init_failed",
            extra={"error_type": type(exc).__name__},
        )
        return None


def build_default_broker() -> Optional[ContextBroker]:
    """
    Construye (o reusa) un `ContextBroker` global usando el cliente HTTPX
    sobre Supabase prod (env vars).

    Returns
    -------
    ContextBroker | None
        Broker listo para inyectar, o None si Supabase no está configurado.
    """
    global _GLOBAL_BROKER

    if _GLOBAL_BROKER is not None:
        return _GLOBAL_BROKER

    client = _get_global_client()
    if client is None:
        return None

    _GLOBAL_BROKER = ContextBroker(rpc_client=client)
    return _GLOBAL_BROKER


def build_default_broker_factory() -> Callable[[], Optional[ContextBroker]]:
    """
    Retorna una factory invocable por
    `tools.manus_bridge.set_anti_dory_broker_factory()`.

    El callsite invoca la factory cada vez que necesita hidratar — la factory
    devuelve el broker global (o None si fail-open).
    """
    return build_default_broker


# =============================================================================
# Test helper (público, NO production)
# =============================================================================


def _reset_global_state_for_tests() -> None:
    """
    Reset del estado global. SOLO para tests. Permite verificar la lógica de
    init/fail-open sin contaminación entre tests.
    """
    global _GLOBAL_CLIENT, _GLOBAL_BROKER
    if _GLOBAL_CLIENT is not None:
        try:
            _GLOBAL_CLIENT.close()
        except Exception:
            pass
    _GLOBAL_CLIENT = None
    _GLOBAL_BROKER = None
