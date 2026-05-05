"""
Tests Sprint Memento Bloque 4 — Pre-flight library standalone.

Cubre:
    - Lectura fresh de env (anti-Dory)
    - PreflightCache: hit, miss, expiración, invalidación, thread-safety básica
    - preflight_check_async + sync con mocks de httpx
    - Decorator @requires_memento_preflight: async + sync
    - Manejo de auth dual (X-API-Key vs Bearer)
    - Retry con backoff exponencial
    - Fallback policy: block vs warn
    - Errores: config (sin API key), discrepancy (proceed=False), unavailable
    - Hallazgo del B3: aceptar ambos detail strings de 401
"""
from __future__ import annotations

import asyncio
import json
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from unittest.mock import patch, AsyncMock

import httpx
import pytest

from tools.memento_preflight import (
    DEFAULT_CACHE_TTL_SECONDS,
    DEFAULT_VALIDATOR_URL,
    MementoPreflightConfigError,
    MementoPreflightDiscrepancyError,
    MementoPreflightError,
    MementoPreflightUnavailableError,
    PreflightCache,
    PreflightResult,
    _build_auth_headers,
    _resolve_api_key,
    _resolve_auth_format,
    _resolve_fallback_policy,
    _resolve_validator_url,
    get_cache,
    preflight_check,
    preflight_check_async,
    requires_memento_preflight,
)

# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture(autouse=True)
def _clean_cache_and_env(monkeypatch):
    """Antes de cada test: limpia cache global y normaliza env mínima."""
    get_cache().clear()
    # API key default para que la mayoría de tests no necesite definirla
    monkeypatch.setenv("MONSTRUO_API_KEY", "test_api_key_123")
    monkeypatch.delenv("MEMENTO_API_KEY", raising=False)
    monkeypatch.delenv("MEMENTO_VALIDATOR_URL", raising=False)
    monkeypatch.delenv("MEMENTO_AUTH_FORMAT", raising=False)
    monkeypatch.delenv("MEMENTO_FALLBACK_POLICY", raising=False)
    monkeypatch.delenv("MEMENTO_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("MEMENTO_RETRY_ATTEMPTS", raising=False)
    monkeypatch.delenv("MEMENTO_RETRY_BACKOFF_BASE", raising=False)
    monkeypatch.delenv("MEMENTO_HILO_ID", raising=False)
    yield
    get_cache().clear()


# ===========================================================================
# MockHttpClient — emula httpx.AsyncClient inyectable
# ===========================================================================

class _MockResponse:
    def __init__(self, status_code: int, json_data: Optional[Dict[str, Any]] = None, text: str = "") -> None:
        self.status_code = status_code
        self._json = json_data
        self.text = text or (json.dumps(json_data) if json_data else "")

    def json(self) -> Dict[str, Any]:
        if self._json is None:
            raise ValueError("no json")
        return self._json


class MockHttpClient:
    """
    Reemplazo inyectable de httpx.AsyncClient.
    
    Modos:
        - responses=[lista de _MockResponse o Exception]: cada call consume una entrada.
        - exception=<Exception>: TODAS las calls levantan esa excepción.
        - default_response: si la lista se agota, devuelve esto.
    """
    def __init__(self,
                 responses: Optional[List[Any]] = None,
                 exception: Optional[Exception] = None,
                 default_response: Optional[_MockResponse] = None) -> None:
        self.responses = list(responses or [])
        self.exception = exception
        self.default_response = default_response
        self.calls: List[Dict[str, Any]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url: str, json: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None, **kwargs) -> _MockResponse:
        self.calls.append({"url": url, "json": json, "headers": headers or {}})
        if self.exception is not None:
            raise self.exception
        if self.responses:
            entry = self.responses.pop(0)
            if isinstance(entry, Exception):
                raise entry
            return entry
        if self.default_response is not None:
            return self.default_response
        raise RuntimeError("MockHttpClient: no responses left and no default")


def _factory(client: MockHttpClient):
    """Devuelve una factory compatible con http_client_factory."""
    return lambda: client


# ===========================================================================
# Section 1 — Config helpers (anti-Dory: fresh env por request)
# ===========================================================================

class TestConfigHelpers:

    def test_resolve_validator_url_default(self):
        assert _resolve_validator_url() == DEFAULT_VALIDATOR_URL

    def test_resolve_validator_url_overridable(self, monkeypatch):
        monkeypatch.setenv("MEMENTO_VALIDATOR_URL", "http://localhost:9999/v1/memento/validate")
        assert _resolve_validator_url() == "http://localhost:9999/v1/memento/validate"

    def test_resolve_api_key_uses_monstruo_env(self):
        # MONSTRUO_API_KEY ya está seteada por la fixture
        assert _resolve_api_key() == "test_api_key_123"

    def test_resolve_api_key_prefers_memento_env(self, monkeypatch):
        monkeypatch.setenv("MEMENTO_API_KEY", "memento_only_key")
        # MONSTRUO_API_KEY también está seteada → MEMENTO debería ganar
        assert _resolve_api_key() == "memento_only_key"

    def test_resolve_api_key_raises_when_missing(self, monkeypatch):
        monkeypatch.delenv("MONSTRUO_API_KEY", raising=False)
        monkeypatch.delenv("MEMENTO_API_KEY", raising=False)
        with pytest.raises(MementoPreflightConfigError, match="memento_api_key_missing"):
            _resolve_api_key()

    def test_resolve_auth_format_default_x_api_key(self):
        assert _resolve_auth_format() == "x-api-key"

    def test_resolve_auth_format_bearer(self, monkeypatch):
        monkeypatch.setenv("MEMENTO_AUTH_FORMAT", "Bearer")
        assert _resolve_auth_format() == "bearer"

    def test_resolve_auth_format_invalid_falls_back(self, monkeypatch):
        monkeypatch.setenv("MEMENTO_AUTH_FORMAT", "garbage")
        assert _resolve_auth_format() == "x-api-key"

    def test_resolve_fallback_policy_default_block(self):
        assert _resolve_fallback_policy() == "block"

    def test_resolve_fallback_policy_warn(self, monkeypatch):
        monkeypatch.setenv("MEMENTO_FALLBACK_POLICY", "warn")
        assert _resolve_fallback_policy() == "warn"

    def test_build_auth_headers_x_api_key(self):
        h = _build_auth_headers("k", "x-api-key")
        assert h == {"X-API-Key": "k"}

    def test_build_auth_headers_bearer(self):
        h = _build_auth_headers("k", "bearer")
        assert h == {"Authorization": "Bearer k"}


# ===========================================================================
# Section 2 — PreflightCache
# ===========================================================================

class TestPreflightCache:

    def test_set_get_basic(self):
        cache = PreflightCache(default_ttl_seconds=60)
        result = PreflightResult(validation_id="mv_test_1", validation_status="ok", proceed=True)
        cache.set("op_x", {"a": 1}, result)
        assert cache.get("op_x", {"a": 1}) is result

    def test_get_miss(self):
        cache = PreflightCache(default_ttl_seconds=60)
        assert cache.get("op_y", {"x": 1}) is None

    def test_key_stable_regardless_of_dict_order(self):
        cache = PreflightCache(default_ttl_seconds=60)
        result = PreflightResult(validation_id="mv_test_2", validation_status="ok", proceed=True)
        cache.set("op_x", {"a": 1, "b": 2}, result)
        # Mismo contenido, orden distinto
        assert cache.get("op_x", {"b": 2, "a": 1}) is result

    def test_ttl_expiration(self):
        cache = PreflightCache(default_ttl_seconds=1)
        result = PreflightResult(validation_id="mv_test_3", validation_status="ok", proceed=True)
        cache.set("op_x", {"a": 1}, result, ttl_seconds=0)  # expira inmediato
        time.sleep(0.01)
        assert cache.get("op_x", {"a": 1}) is None

    def test_invalidate_removes_entry(self):
        cache = PreflightCache()
        result = PreflightResult(validation_id="mv_test_4", validation_status="ok", proceed=True)
        cache.set("op_x", {"a": 1}, result)
        assert cache.invalidate("op_x", {"a": 1}) is True
        assert cache.get("op_x", {"a": 1}) is None
        assert cache.invalidate("op_x", {"a": 1}) is False  # idempotente

    def test_clear_empties_cache(self):
        cache = PreflightCache()
        result = PreflightResult(validation_id="mv_test_5", validation_status="ok", proceed=True)
        cache.set("op_a", {"a": 1}, result)
        cache.set("op_b", {"b": 2}, result)
        assert len(cache) == 2
        cache.clear()
        assert len(cache) == 0


# ===========================================================================
# Section 3 — preflight_check_async (camino feliz + variaciones)
# ===========================================================================

class TestPreflightCheckAsyncHappyPath:

    @pytest.mark.asyncio
    async def test_returns_parsed_result_on_200(self):
        ok_response = _MockResponse(200, {
            "validation_id": "mv_2026-05-04T12:00_abc123",
            "validation_status": "ok",
            "proceed": True,
            "context_freshness_seconds": 30,
            "discrepancy": None,
            "remediation": None,
            "source_consulted": "ticketlike_credentials",
            "persistence_failed": False,
        })
        client = MockHttpClient(responses=[ok_response])
        result = await preflight_check_async(
            operation="sql_against_production",
            context_used={"host": "gateway05.us-west-2.prod.aws.tidbcloud.com"},
            hilo_id="test_hilo",
            http_client_factory=_factory(client),
            use_cache=False,
        )
        assert result.proceed is True
        assert result.validation_status == "ok"
        assert result.validation_id == "mv_2026-05-04T12:00_abc123"
        assert result.context_freshness_seconds == 30
        assert result.source_consulted == "ticketlike_credentials"
        assert client.calls[0]["url"] == DEFAULT_VALIDATOR_URL
        assert client.calls[0]["json"]["hilo_id"] == "test_hilo"
        assert client.calls[0]["json"]["operation"] == "sql_against_production"
        assert "X-API-Key" in client.calls[0]["headers"]
        assert client.calls[0]["headers"]["X-API-Key"] == "test_api_key_123"

    @pytest.mark.asyncio
    async def test_uses_cache_on_second_call(self):
        ok_response = _MockResponse(200, {
            "validation_id": "mv_cache_1",
            "validation_status": "ok",
            "proceed": True,
        })
        client = MockHttpClient(responses=[ok_response])
        # First call → hits endpoint
        await preflight_check_async(
            operation="op_cached",
            context_used={"a": 1},
            hilo_id="h",
            http_client_factory=_factory(client),
        )
        # Second call → cache hit, NO endpoint call
        await preflight_check_async(
            operation="op_cached",
            context_used={"a": 1},
            hilo_id="h",
            http_client_factory=_factory(client),
        )
        assert len(client.calls) == 1  # solo el primer call llegó al mock

    @pytest.mark.asyncio
    async def test_use_cache_false_skips_cache(self):
        responses = [_MockResponse(200, {"validation_id": "mv_no_cache", "validation_status": "ok", "proceed": True}) for _ in range(3)]
        client = MockHttpClient(responses=responses)
        for _ in range(3):
            await preflight_check_async(
                operation="op_x",
                context_used={"a": 1},
                hilo_id="h",
                http_client_factory=_factory(client),
                use_cache=False,
            )
        assert len(client.calls) == 3

    @pytest.mark.asyncio
    async def test_intent_summary_included_in_payload(self):
        ok_response = _MockResponse(200, {"validation_id": "mv_x", "validation_status": "ok", "proceed": True})
        client = MockHttpClient(responses=[ok_response])
        await preflight_check_async(
            operation="op_x",
            context_used={"a": 1},
            intent_summary="testing intent_summary inclusion",
            hilo_id="h",
            http_client_factory=_factory(client),
            use_cache=False,
        )
        assert client.calls[0]["json"]["intent_summary"] == "testing intent_summary inclusion"

    @pytest.mark.asyncio
    async def test_hilo_id_falls_back_to_env(self, monkeypatch):
        monkeypatch.setenv("MEMENTO_HILO_ID", "hilo_from_env")
        ok_response = _MockResponse(200, {"validation_id": "mv_y", "validation_status": "ok", "proceed": True})
        client = MockHttpClient(responses=[ok_response])
        await preflight_check_async(
            operation="op_x",
            context_used={"a": 1},
            http_client_factory=_factory(client),
            use_cache=False,
        )
        assert client.calls[0]["json"]["hilo_id"] == "hilo_from_env"


class TestPreflightCheckAsyncAuthFormats:

    @pytest.mark.asyncio
    async def test_x_api_key_default_format(self):
        ok_response = _MockResponse(200, {"validation_id": "mv_a", "validation_status": "ok", "proceed": True})
        client = MockHttpClient(responses=[ok_response])
        await preflight_check_async(
            operation="op_x",
            context_used={"a": 1},
            hilo_id="h",
            http_client_factory=_factory(client),
            use_cache=False,
        )
        assert client.calls[0]["headers"].get("X-API-Key") == "test_api_key_123"
        assert "Authorization" not in client.calls[0]["headers"]

    @pytest.mark.asyncio
    async def test_bearer_format_when_env_set(self, monkeypatch):
        monkeypatch.setenv("MEMENTO_AUTH_FORMAT", "bearer")
        ok_response = _MockResponse(200, {"validation_id": "mv_b", "validation_status": "ok", "proceed": True})
        client = MockHttpClient(responses=[ok_response])
        await preflight_check_async(
            operation="op_x",
            context_used={"a": 1},
            hilo_id="h",
            http_client_factory=_factory(client),
            use_cache=False,
        )
        assert client.calls[0]["headers"].get("Authorization") == "Bearer test_api_key_123"
        assert "X-API-Key" not in client.calls[0]["headers"]


# ===========================================================================
# Section 4 — Errores y retries
# ===========================================================================

class TestPreflightCheckAsyncErrorsAndRetries:

    @pytest.mark.asyncio
    async def test_raises_config_error_when_no_api_key(self, monkeypatch):
        monkeypatch.delenv("MONSTRUO_API_KEY", raising=False)
        monkeypatch.delenv("MEMENTO_API_KEY", raising=False)
        client = MockHttpClient(responses=[_MockResponse(200, {"validation_id": "mv_x", "validation_status": "ok", "proceed": True})])
        with pytest.raises(MementoPreflightConfigError, match="memento_api_key_missing"):
            await preflight_check_async(
                operation="op_x",
                context_used={"a": 1},
                hilo_id="h",
                http_client_factory=_factory(client),
            )

    @pytest.mark.asyncio
    async def test_401_raises_config_error(self):
        # Hallazgo B3: aceptar tanto el detail del middleware global como del helper interno
        client = MockHttpClient(responses=[_MockResponse(401, text="Missing API key. Use X-API-Key header...")])
        with pytest.raises(MementoPreflightConfigError, match="memento_auth_failed.*401"):
            await preflight_check_async(
                operation="op_x",
                context_used={"a": 1},
                hilo_id="h",
                http_client_factory=_factory(client),
                use_cache=False,
            )

    @pytest.mark.asyncio
    async def test_403_raises_config_error(self):
        client = MockHttpClient(responses=[_MockResponse(403, text="forbidden")])
        with pytest.raises(MementoPreflightConfigError, match="memento_auth_failed.*403"):
            await preflight_check_async(
                operation="op_x",
                context_used={"a": 1},
                hilo_id="h",
                http_client_factory=_factory(client),
                use_cache=False,
            )

    @pytest.mark.asyncio
    async def test_422_raises_request_invalid_no_retry(self):
        client = MockHttpClient(responses=[_MockResponse(422, text='{"detail":"invalid"}')])
        with pytest.raises(MementoPreflightError, match="memento_request_invalid"):
            await preflight_check_async(
                operation="op_x",
                context_used={"a": 1},
                hilo_id="h",
                http_client_factory=_factory(client),
                use_cache=False,
            )
        assert len(client.calls) == 1  # NO retry

    @pytest.mark.asyncio
    async def test_500_retries_then_recovers(self):
        responses = [
            _MockResponse(500, text="bad"),
            _MockResponse(200, {"validation_id": "mv_recovered", "validation_status": "ok", "proceed": True}),
        ]
        client = MockHttpClient(responses=responses)
        result = await preflight_check_async(
            operation="op_x",
            context_used={"a": 1},
            hilo_id="h",
            http_client_factory=_factory(client),
            use_cache=False,
            retry_backoff_base=0.001,  # acelerar
        )
        assert result.validation_id == "mv_recovered"
        assert len(client.calls) == 2

    @pytest.mark.asyncio
    async def test_timeout_retries_then_unavailable_block(self):
        client = MockHttpClient(exception=httpx.TimeoutException("timeout"))
        with pytest.raises(MementoPreflightUnavailableError, match="memento_endpoint_unavailable"):
            await preflight_check_async(
                operation="op_x",
                context_used={"a": 1},
                hilo_id="h",
                http_client_factory=_factory(client),
                use_cache=False,
                retry_attempts=2,
                retry_backoff_base=0.001,
            )
        assert len(client.calls) == 2

    @pytest.mark.asyncio
    async def test_timeout_warn_fallback_returns_permissive_result(self):
        client = MockHttpClient(exception=httpx.TimeoutException("timeout"))
        result = await preflight_check_async(
            operation="op_x",
            context_used={"a": 1},
            hilo_id="h",
            http_client_factory=_factory(client),
            use_cache=False,
            retry_attempts=2,
            retry_backoff_base=0.001,
            fallback_policy="warn",
        )
        assert result.proceed is True  # warn permite ejecución
        assert result.validation_status == "source_unavailable"
        assert result.persistence_failed is True
        assert "endpoint_unavailable_after" in (result.remediation or "")

    @pytest.mark.asyncio
    async def test_network_error_retries(self):
        client = MockHttpClient(exception=httpx.ConnectError("conn refused"))
        with pytest.raises(MementoPreflightUnavailableError):
            await preflight_check_async(
                operation="op_x",
                context_used={"a": 1},
                hilo_id="h",
                http_client_factory=_factory(client),
                use_cache=False,
                retry_attempts=3,
                retry_backoff_base=0.001,
            )
        assert len(client.calls) == 3


# ===========================================================================
# Section 5 — Sync wrapper preflight_check
# ===========================================================================

class TestPreflightCheckSync:

    def test_sync_call_works_when_no_loop(self):
        ok_response = _MockResponse(200, {"validation_id": "mv_sync_1", "validation_status": "ok", "proceed": True})
        client = MockHttpClient(responses=[ok_response])
        result = preflight_check(
            operation="op_x",
            context_used={"a": 1},
            hilo_id="h",
            http_client_factory=_factory(client),
            use_cache=False,
        )
        assert result.proceed is True
        assert result.validation_id == "mv_sync_1"


# ===========================================================================
# Section 6 — Decorator @requires_memento_preflight
# ===========================================================================

class TestDecoratorAsync:

    @pytest.mark.asyncio
    async def test_async_function_executes_when_proceed_true(self):
        ok_response = _MockResponse(200, {"validation_id": "mv_dec_1", "validation_status": "ok", "proceed": True})
        client = MockHttpClient(responses=[ok_response])

        @requires_memento_preflight(
            operation="sql_against_production",
            context_from_kwargs=["host", "user"],
            use_cache=False,
        )
        async def query(host: str, user: str, query: str):
            return f"{host}/{user}/{query}"

        async def _proxy(**kw):
            return await client.post(kw["url"], json=kw["payload"], headers=kw["headers"])
        with patch("tools.memento_preflight._do_request", side_effect=_proxy):
            result = await query(host="gateway05", user="postgres", query="SELECT 1")
            assert result == "gateway05/postgres/SELECT 1"
            # Verifica que el context se construyó solo con host+user (no query)
            assert client.calls[0]["json"]["context_used"] == {"host": "gateway05", "user": "postgres"}

    @pytest.mark.asyncio
    async def test_async_function_blocked_when_proceed_false(self):
        block_response = _MockResponse(200, {
            "validation_id": "mv_blocked",
            "validation_status": "discrepancy_detected",
            "proceed": False,
            "discrepancy": {"field": "host", "context_used": "gateway01", "source_of_truth": "gateway05", "source": "credentials.md"},
            "remediation": "context_stale_or_contaminated",
        })
        client = MockHttpClient(responses=[block_response])

        @requires_memento_preflight(
            operation="sql_against_production",
            context_from_kwargs=["host"],
            use_cache=False,
        )
        async def query(host: str):
            return "should_not_reach"

        async def _proxy(**kw):
            return await client.post(kw["url"], json=kw["payload"], headers=kw["headers"])
        with patch("tools.memento_preflight._do_request", side_effect=_proxy):
            with pytest.raises(MementoPreflightDiscrepancyError) as exc_info:
                await query(host="gateway01")
            assert exc_info.value.result.proceed is False
            assert exc_info.value.result.discrepancy["field"] == "host"

    @pytest.mark.asyncio
    async def test_implicit_context_from_all_kwargs(self):
        ok_response = _MockResponse(200, {"validation_id": "mv_impl", "validation_status": "ok", "proceed": True})
        client = MockHttpClient(responses=[ok_response])

        @requires_memento_preflight(operation="op_x", use_cache=False)
        async def some_op(a: int, b: str):
            return a + len(b)

        async def _proxy(**kw):
            return await client.post(kw["url"], json=kw["payload"], headers=kw["headers"])
        with patch("tools.memento_preflight._do_request", side_effect=_proxy):
            await some_op(a=10, b="hello")
            assert client.calls[0]["json"]["context_used"] == {"a": 10, "b": "hello"}


class TestDecoratorSync:

    def test_sync_function_executes_when_proceed_true(self):
        ok_response = _MockResponse(200, {"validation_id": "mv_sync_dec", "validation_status": "ok", "proceed": True})
        client = MockHttpClient(responses=[ok_response])

        @requires_memento_preflight(
            operation="op_y",
            context_from_kwargs=["x"],
            use_cache=False,
        )
        def compute(x: int):
            return x * 2

        async def _proxy(**kw):
            return await client.post(kw["url"], json=kw["payload"], headers=kw["headers"])
        with patch("tools.memento_preflight._do_request", side_effect=_proxy):
            assert compute(x=5) == 10
            assert client.calls[0]["json"]["context_used"] == {"x": 5}

    def test_sync_function_blocked(self):
        block_response = _MockResponse(200, {
            "validation_id": "mv_block",
            "validation_status": "unknown_operation",
            "proceed": False,
            "remediation": "operation_not_in_catalog",
        })
        client = MockHttpClient(responses=[block_response])

        @requires_memento_preflight(operation="bogus_op", use_cache=False)
        def some_call(z: int):
            return "nope"

        async def _proxy(**kw):
            return await client.post(kw["url"], json=kw["payload"], headers=kw["headers"])
        with patch("tools.memento_preflight._do_request", side_effect=_proxy):
            with pytest.raises(MementoPreflightDiscrepancyError):
                some_call(z=42)


# ===========================================================================
# Section 7 — Integración: cache + decorator
# ===========================================================================

class TestCacheIntegration:

    @pytest.mark.asyncio
    async def test_decorator_uses_cache_across_calls(self):
        ok_response = _MockResponse(200, {"validation_id": "mv_int_cache", "validation_status": "ok", "proceed": True})
        client = MockHttpClient(responses=[ok_response])

        @requires_memento_preflight(
            operation="op_z",
            context_from_kwargs=["arg"],
            use_cache=True,
        )
        async def op(arg: str):
            return arg.upper()

        async def _proxy(**kw):
            return await client.post(kw["url"], json=kw["payload"], headers=kw["headers"])
        with patch("tools.memento_preflight._do_request", side_effect=_proxy):
            r1 = await op(arg="hello")
            r2 = await op(arg="hello")  # cache hit
            assert r1 == r2 == "HELLO"
            assert len(client.calls) == 1  # solo un endpoint call

    @pytest.mark.asyncio
    async def test_explicit_cache_invalidate(self):
        responses = [
            _MockResponse(200, {"validation_id": "mv_first", "validation_status": "ok", "proceed": True}),
            _MockResponse(200, {"validation_id": "mv_second", "validation_status": "ok", "proceed": True}),
        ]
        client = MockHttpClient(responses=responses)

        async def _proxy(**kw):
            return await client.post(kw["url"], json=kw["payload"], headers=kw["headers"])
        with patch("tools.memento_preflight._do_request", side_effect=_proxy):
            r1 = await preflight_check_async(operation="op_x", context_used={"a": 1}, hilo_id="h")
            assert r1.validation_id == "mv_first"
            get_cache().invalidate("op_x", {"a": 1})
            r2 = await preflight_check_async(operation="op_x", context_used={"a": 1}, hilo_id="h")
            assert r2.validation_id == "mv_second"
            assert len(client.calls) == 2
