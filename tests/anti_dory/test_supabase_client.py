"""
tests/anti_dory/test_supabase_client.py
========================================

Tests integration D1 — Sprint MANUS-ANTI-DORY-002 v1 FASE D.

Verifica que `HTTPXSupabaseRPCClient` y `build_default_broker_factory()`
cumplen el contrato del Protocol `SupabaseRPCClient` definido en FASE B.

**Constraints duros respetados:**
- NO toca Supabase real. Usa `httpx.MockTransport` para interceptar HTTP.
- NO usa env vars secretas reales. Setea dummy values con `monkeypatch.setenv`.
- NO depende de red. Todo en-memoria.
- NO contamina otros tests: cada test resetea estado global vía
  `_reset_global_state_for_tests`.

Tests (3 obligatorios + 2 extras de robustez):
  D1.1 — call_rpc happy path: HTTP 200 + JSON body → broker recibe valor correcto.
  D1.2 — call_rpc error HTTP 4xx/5xx → raise → broker fail-open.
  D1.3 — build_default_broker() con env vars OK → retorna ContextBroker funcional.
  D1.4 (extra) — build_default_broker() sin env vars → retorna None (fail-open).
  D1.5 (extra) — call_rpc con timeout → raise httpx.TimeoutException.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from kernel.anti_dory.supabase_client import (
    HTTPXSupabaseRPCClient,
    _reset_global_state_for_tests,
    build_default_broker,
    build_default_broker_factory,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def _reset_global_state():
    """Resetea estado global ANTES y DESPUÉS de cada test."""
    _reset_global_state_for_tests()
    yield
    _reset_global_state_for_tests()


def _make_mock_transport(handler):
    """Helper: construye un httpx.MockTransport con un handler dado."""
    return httpx.MockTransport(handler)


# =============================================================================
# D1.1 — happy path
# =============================================================================


def test_call_rpc_happy_path_returns_decoded_json():
    """call_rpc('rpc_get_attachment_pack', {...}) → HTTP 200 + JSON body
    → cliente devuelve dict decodificado."""

    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        # Capturar para asserts posteriores
        captured["method"] = request.method
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["body"] = json.loads(request.content.decode("utf-8"))
        # Respuesta tipo PostgREST happy path
        return httpx.Response(
            200,
            json={
                "snapshot_id": "abc-123",
                "project_id": "el-monstruo",
                "attachment_ok": True,
            },
        )

    mock_client = httpx.Client(
        transport=_make_mock_transport(handler),
        headers={
            "apikey": "test-key",
            "Authorization": "Bearer test-key",
            "Content-Type": "application/json",
        },
    )
    client = HTTPXSupabaseRPCClient(
        url="https://test.supabase.co",
        service_key="test-key",
        http_client=mock_client,
    )

    result = client.call_rpc(
        "rpc_get_attachment_pack",
        {"p_project_id": "el-monstruo", "p_front_id": "anti-dory-002"},
    )

    # Verificaciones binarias
    assert captured["method"] == "POST"
    assert (
        captured["url"]
        == "https://test.supabase.co/rest/v1/rpc/rpc_get_attachment_pack"
    )
    assert captured["body"] == {
        "p_project_id": "el-monstruo",
        "p_front_id": "anti-dory-002",
    }
    assert result["snapshot_id"] == "abc-123"
    assert result["attachment_ok"] is True


# =============================================================================
# D1.2 — error HTTP → raise
# =============================================================================


def test_call_rpc_http_error_raises_httpx_error():
    """HTTP 401/500 → call_rpc raise → broker fail-open (verificado en otro suite)."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={"message": "Invalid API key", "code": "PGRST301"},
        )

    mock_client = httpx.Client(transport=_make_mock_transport(handler))
    client = HTTPXSupabaseRPCClient(
        url="https://test.supabase.co",
        service_key="bad-key",
        http_client=mock_client,
    )

    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        client.call_rpc("rpc_get_attachment_pack", {"p_project_id": "x"})

    assert excinfo.value.response.status_code == 401


# =============================================================================
# D1.3 — factory default con env vars OK
# =============================================================================


def test_build_default_broker_with_env_vars_returns_broker(monkeypatch):
    """SUPABASE_URL + SUPABASE_SERVICE_KEY presentes → factory devuelve
    ContextBroker funcional con HTTPXSupabaseRPCClient inyectado."""

    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-key-dummy")

    broker = build_default_broker()
    assert broker is not None
    # ContextBroker guarda el cliente en ._rpc (verificado en FASE B impl)
    assert isinstance(broker._rpc, HTTPXSupabaseRPCClient)  # noqa: SLF001

    # Verificar que la factory cachea (segunda llamada devuelve la misma instancia)
    broker2 = build_default_broker()
    assert broker2 is broker

    # build_default_broker_factory wrapper debe devolver el mismo broker
    factory = build_default_broker_factory()
    assert factory() is broker


# =============================================================================
# D1.4 (extra) — sin env vars → fail-open (None)
# =============================================================================


def test_build_default_broker_without_env_vars_returns_none(monkeypatch):
    """Sin SUPABASE_URL o sin SUPABASE_SERVICE_KEY → factory devuelve None
    (fail-open, no rompe el callsite)."""

    # Borrar ambos por si están en el entorno del CI
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

    broker = build_default_broker()
    assert broker is None

    factory = build_default_broker_factory()
    assert factory() is None


# =============================================================================
# D1.5 (extra) — timeout → raise httpx.TimeoutException
# =============================================================================


def test_call_rpc_timeout_propagates_to_caller():
    """Timeout en el cliente HTTPX → call_rpc raise httpx.TimeoutException
    (broker captura y fail-opens en su capa)."""

    def handler(request: httpx.Request) -> httpx.Response:
        # Simular timeout lanzando excepción directamente desde el transport
        raise httpx.ReadTimeout("simulated read timeout", request=request)

    mock_client = httpx.Client(transport=_make_mock_transport(handler))
    client = HTTPXSupabaseRPCClient(
        url="https://test.supabase.co",
        service_key="test-key",
        http_client=mock_client,
    )

    with pytest.raises(httpx.ReadTimeout):
        client.call_rpc("rpc_get_attachment_pack", {"p_project_id": "x"})


# =============================================================================
# Validación de contrato Protocol fidelity
# =============================================================================


def test_client_implements_protocol_contract():
    """Verifica estructuralmente que HTTPXSupabaseRPCClient cumple el Protocol
    SupabaseRPCClient (sin runtime_checkable, hacemos check manual)."""
    from kernel.anti_dory.context_broker import SupabaseRPCClient  # Protocol
    import inspect

    sig = inspect.signature(HTTPXSupabaseRPCClient.call_rpc)
    params = list(sig.parameters.keys())
    # self, name, params
    assert params == ["self", "name", "params"], f"Unexpected params: {params}"

    # Verificar que el Protocol declara los mismos parámetros
    proto_sig = inspect.signature(SupabaseRPCClient.call_rpc)
    proto_params = list(proto_sig.parameters.keys())
    assert proto_params == params


# =============================================================================
# Constructor validation
# =============================================================================


def test_constructor_rejects_empty_url():
    with pytest.raises(ValueError, match="url"):
        HTTPXSupabaseRPCClient(url="", service_key="x")


def test_constructor_rejects_empty_service_key():
    with pytest.raises(ValueError, match="service_key"):
        HTTPXSupabaseRPCClient(url="https://x.supabase.co", service_key="")


def test_call_rpc_rejects_invalid_name():
    client = HTTPXSupabaseRPCClient(
        url="https://test.supabase.co", service_key="k"
    )
    with pytest.raises(ValueError, match="RPC name"):
        client.call_rpc("", {})
    client.close()


def test_call_rpc_rejects_non_dict_params():
    client = HTTPXSupabaseRPCClient(
        url="https://test.supabase.co", service_key="k"
    )
    with pytest.raises(ValueError, match="params"):
        client.call_rpc("rpc_x", "not a dict")  # type: ignore[arg-type]
    client.close()
