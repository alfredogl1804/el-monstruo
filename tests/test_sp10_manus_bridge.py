"""
Tests for SP10: Manus Bridge (Multi-Agent Delegation)
======================================================
Validates post_bridge_snapshot and read_bridge_snapshots per Hilo B spec.
"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.manus_bridge import (
    COMMAND_CENTER_URL,
    SNAPSHOT_ENDPOINT,
    BridgeResponse,
    BridgeSnapshot,
    post_bridge_snapshot,
    read_bridge_snapshots,
    report_completion,
    report_error,
    report_task_progress,
)

# ─── BridgeSnapshot Tests ─────────────────────────────────────────────────────


class TestBridgeSnapshot:
    """Tests for the BridgeSnapshot dataclass."""

    def test_create_snapshot(self):
        """Basic snapshot creation."""
        snap = BridgeSnapshot(
            hilo_id="hilo_c",
            status="active",
            metrics={"tasks": 5},
        )
        assert snap.hilo_id == "hilo_c"
        assert snap.status == "active"
        assert snap.metrics == {"tasks": 5}
        assert snap.timestamp > 0

    def test_to_dict(self):
        """Serialization to dict."""
        snap = BridgeSnapshot(
            hilo_id="hilo_a",
            status="idle",
            metrics={"cost": 0.5},
            metadata={"sprint": 27},
        )
        d = snap.to_dict()
        assert d["hilo_id"] == "hilo_a"
        assert d["status"] == "idle"
        assert d["metrics"]["cost"] == 0.5
        assert d["metadata"]["sprint"] == 27
        assert "timestamp" in d

    def test_default_values(self):
        """Default metrics and metadata are empty dicts."""
        snap = BridgeSnapshot(hilo_id="test", status="active")
        assert snap.metrics == {}
        assert snap.metadata == {}


# ─── BridgeResponse Tests ─────────────────────────────────────────────────────


class TestBridgeResponse:
    """Tests for BridgeResponse."""

    def test_success_response(self):
        resp = BridgeResponse(success=True, data={"id": "123"}, status_code=200)
        assert resp.success is True
        assert resp.data == {"id": "123"}
        assert resp.error is None

    def test_error_response(self):
        resp = BridgeResponse(success=False, error="timeout", status_code=0)
        assert resp.success is False
        assert resp.error == "timeout"

    def test_to_dict(self):
        resp = BridgeResponse(success=True, data=[1, 2], status_code=200)
        d = resp.to_dict()
        assert d["success"] is True
        assert d["data"] == [1, 2]
        assert d["status_code"] == 200


# ─── post_bridge_snapshot Tests ───────────────────────────────────────────────


class TestPostBridgeSnapshot:
    """Tests for posting snapshots to Command Center."""

    @pytest.mark.asyncio
    async def test_no_api_key_returns_error(self):
        """Missing API key → error response."""
        import kernel.manus_bridge as mb

        # Temporarily override the module-level var
        original = mb.BRIDGE_API_KEY
        mb.BRIDGE_API_KEY = ""
        try:
            result = await post_bridge_snapshot("hilo_c", "active")
            assert result.success is False
            assert "not configured" in result.error
        finally:
            mb.BRIDGE_API_KEY = original

    @pytest.mark.asyncio
    async def test_successful_post(self):
        """Successful POST returns success response."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "snap_123"}
        mock_response.text = ""

        with patch("kernel.manus_bridge.BRIDGE_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_cls.return_value = mock_client

                result = await post_bridge_snapshot(
                    hilo_id="hilo_c",
                    status="active",
                    metrics={"tasks": 3},
                )

        assert result.success is True
        assert result.data == {"id": "snap_123"}
        assert result.status_code == 201

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Timeout → graceful error."""
        with patch("kernel.manus_bridge.BRIDGE_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post.side_effect = httpx.TimeoutException("timed out")
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_cls.return_value = mock_client

                result = await post_bridge_snapshot("hilo_c", "active")

        assert result.success is False
        assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_connect_error_handling(self):
        """Connection error → graceful error."""
        with patch("kernel.manus_bridge.BRIDGE_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post.side_effect = httpx.ConnectError("refused")
                mock_client.__aenter__ = AsyncMock(return_value=None)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_cls.return_value = mock_client

                # Need to handle the context manager properly
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                result = await post_bridge_snapshot("hilo_c", "error")

        assert result.success is False
        assert "connection" in result.error.lower()

    @pytest.mark.asyncio
    async def test_server_error_response(self):
        """500 response → success=False with error text."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = None

        with patch("kernel.manus_bridge.BRIDGE_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_cls.return_value = mock_client

                result = await post_bridge_snapshot("hilo_c", "active")

        assert result.success is False
        assert result.status_code == 500


# ─── read_bridge_snapshots Tests ──────────────────────────────────────────────


class TestReadBridgeSnapshots:
    """Tests for reading snapshots from Command Center."""

    @pytest.mark.asyncio
    async def test_no_api_key_returns_error(self):
        """Missing API key → error response."""
        import kernel.manus_bridge as mb

        original = mb.BRIDGE_API_KEY
        mb.BRIDGE_API_KEY = ""
        try:
            result = await read_bridge_snapshots()
            assert result.success is False
            assert "not configured" in result.error
        finally:
            mb.BRIDGE_API_KEY = original

    @pytest.mark.asyncio
    async def test_successful_read(self):
        """Successful GET returns list of snapshots."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"hilo_id": "hilo_a", "status": "active"},
            {"hilo_id": "hilo_b", "status": "idle"},
        ]

        with patch("kernel.manus_bridge.BRIDGE_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.get.return_value = mock_response
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_cls.return_value = mock_client

                result = await read_bridge_snapshots()

        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["hilo_id"] == "hilo_a"

    @pytest.mark.asyncio
    async def test_read_with_filter(self):
        """GET with hilo_filter passes params."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"hilo_id": "hilo_a", "status": "active"}]

        with patch("kernel.manus_bridge.BRIDGE_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.get.return_value = mock_response
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_cls.return_value = mock_client

                result = await read_bridge_snapshots(hilo_filter="hilo_a")

                # Verify params were passed
                call_kwargs = mock_client.get.call_args
                assert call_kwargs.kwargs["params"]["hilo_id"] == "hilo_a"

        assert result.success is True

    @pytest.mark.asyncio
    async def test_read_timeout(self):
        """Timeout on read → graceful error."""
        with patch("kernel.manus_bridge.BRIDGE_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.get.side_effect = httpx.TimeoutException("timeout")
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_cls.return_value = mock_client

                result = await read_bridge_snapshots()

        assert result.success is False
        assert "timed out" in result.error.lower()


# ─── Convenience Helper Tests ─────────────────────────────────────────────────


class TestConvenienceHelpers:
    """Tests for report_task_progress, report_error, report_completion."""

    @pytest.mark.asyncio
    async def test_report_task_progress(self):
        """report_task_progress structures metrics correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"ok": True}
        mock_response.text = ""

        with patch("kernel.manus_bridge.BRIDGE_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_cls.return_value = mock_client

                result = await report_task_progress(
                    hilo_id="hilo_c",
                    task_id="task_001",
                    step_id="step_3",
                    tools_used=["web_search", "code_exec"],
                    cost_usd=0.05,
                    model_used="claude-opus-4.7",
                )

        assert result.success is True
        # Verify the payload structure
        call_kwargs = mock_client.post.call_args
        payload = call_kwargs.kwargs["json"]
        assert payload["hilo_id"] == "hilo_c"
        assert payload["status"] == "active"
        assert payload["metrics"]["task_id"] == "task_001"
        assert payload["metrics"]["tools_used"] == ["web_search", "code_exec"]

    @pytest.mark.asyncio
    async def test_report_error(self):
        """report_error sends error status."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"ok": True}
        mock_response.text = ""

        with patch("kernel.manus_bridge.BRIDGE_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_cls.return_value = mock_client

                result = await report_error(
                    hilo_id="hilo_c",
                    error_msg="API rate limited",
                    context={"retry_after": 60},
                )

        assert result.success is True
        call_kwargs = mock_client.post.call_args
        payload = call_kwargs.kwargs["json"]
        assert payload["status"] == "error"
        assert payload["metrics"]["error"] == "API rate limited"
        assert payload["metadata"]["retry_after"] == 60

    @pytest.mark.asyncio
    async def test_report_completion(self):
        """report_completion sends completed status with totals."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"ok": True}
        mock_response.text = ""

        with patch("kernel.manus_bridge.BRIDGE_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_cls.return_value = mock_client

                result = await report_completion(
                    hilo_id="hilo_c",
                    task_id="task_001",
                    total_cost_usd=0.35,
                    total_steps=7,
                )

        assert result.success is True
        call_kwargs = mock_client.post.call_args
        payload = call_kwargs.kwargs["json"]
        assert payload["status"] == "completed"
        assert payload["metrics"]["total_cost_usd"] == 0.35
        assert payload["metrics"]["total_steps"] == 7


# ─── URL Construction Tests ───────────────────────────────────────────────────


class TestURLConstruction:
    """Tests for URL and header construction."""

    def test_command_center_url(self):
        """Default URL is correct."""
        assert "monstruodash" in COMMAND_CENTER_URL
        assert COMMAND_CENTER_URL.startswith("https://")

    def test_snapshot_endpoint(self):
        """Endpoint path is correct."""
        assert SNAPSHOT_ENDPOINT == "/api/bridge/snapshot"

    def test_full_url(self):
        """Full URL construction."""
        full = f"{COMMAND_CENTER_URL}{SNAPSHOT_ENDPOINT}"
        assert full == "https://monstruodash-ggmndxgx.manus.space/api/bridge/snapshot"
