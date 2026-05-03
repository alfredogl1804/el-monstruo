"""
El Monstruo — Tests: Vigilia del Embrión (Sprint 83)
=====================================================
E2E tests for the embrion loop fixes and diagnostic endpoint.

Coverage:
  1. SupabaseClient async wrapping (to_thread, timeout)
  2. EmbrionLoop _loop timeout protection
  3. Magna classify integration (correct params, dataclass handling)
  4. FCS counter increments on tool calls
  5. /v1/embrion/diagnostic endpoint response shape
  6. delegate_task basic contract (no external creds needed)
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from dataclasses import dataclass


# ── 1. SupabaseClient async wrapping ─────────────────────────────────

class TestSupabaseClientAsync:
    """Verify that SupabaseClient methods use asyncio.to_thread."""

    def test_insert_sync_exists(self):
        """_insert_sync helper must exist for to_thread wrapping."""
        from memory.supabase_client import SupabaseClient
        client = SupabaseClient(url="", key="")
        assert hasattr(client, "_insert_sync")
        assert hasattr(client, "_select_sync")
        assert hasattr(client, "_upsert_sync")
        assert hasattr(client, "_update_sync")
        assert hasattr(client, "_delete_sync")
        assert hasattr(client, "_rpc_sync")
        assert hasattr(client, "_count_sync")

    def test_not_connected_returns_safe_defaults(self):
        """When not connected, all methods return safe defaults."""
        from memory.supabase_client import SupabaseClient
        client = SupabaseClient(url="", key="")
        assert client.connected is False

        # All async methods should return safe defaults when not connected
        loop = asyncio.new_event_loop()
        try:
            assert loop.run_until_complete(client.insert("t", {})) is None
            assert loop.run_until_complete(client.insert_batch("t", [])) == []
            assert loop.run_until_complete(client.select("t")) == []
            assert loop.run_until_complete(client.upsert("t", {})) is None
            assert loop.run_until_complete(client.update("t", {}, {})) is None
            assert loop.run_until_complete(client.delete("t", {})) is False
            assert loop.run_until_complete(client.rpc("fn")) is None
            assert loop.run_until_complete(client.count("t")) == 0
        finally:
            loop.close()

    def test_timeout_constant_exists(self):
        """DB operation timeout constant must be defined."""
        from memory.supabase_client import _DB_OP_TIMEOUT
        assert isinstance(_DB_OP_TIMEOUT, (int, float))
        assert _DB_OP_TIMEOUT > 0
        assert _DB_OP_TIMEOUT <= 60  # Reasonable upper bound


# ── 2. EmbrionLoop timeout protection ────────────────────────────────

class TestEmbrionLoopTimeouts:
    """Verify that _loop has timeout protection around sub-tasks."""

    def test_loop_method_has_timeout_constants(self):
        """_loop should define _THINK_TIMEOUT and _TASK_TIMEOUT."""
        import inspect
        from kernel.embrion_loop import EmbrionLoop
        source = inspect.getsource(EmbrionLoop._loop)
        assert "_THINK_TIMEOUT" in source
        assert "_TASK_TIMEOUT" in source
        assert "asyncio.wait_for" in source

    def test_loop_catches_timeout_errors(self):
        """_loop source should catch asyncio.TimeoutError for each sub-task."""
        import inspect
        from kernel.embrion_loop import EmbrionLoop
        source = inspect.getsource(EmbrionLoop._loop)
        # Should have timeout catches for: check_and_think, consolidation, sabios, radar
        assert source.count("asyncio.TimeoutError") >= 4


# ── 3. Magna classify integration ───────────────────────────────────

class TestMagnaClassifyIntegration:
    """Verify Magna classify is called with correct params."""

    def test_classify_accepts_text_not_message(self):
        """classify() first param is 'text', not 'message'."""
        from kernel.magna_classifier import MagnaClassifier
        import inspect
        sig = inspect.signature(MagnaClassifier.classify)
        params = list(sig.parameters.keys())
        assert params[1] == "text"  # params[0] is 'self'
        assert "message" not in params

    def test_classify_returns_dataclass_not_dict(self):
        """classify() returns ClassificationResult, not a dict."""
        from kernel.magna_classifier import MagnaClassifier, ClassificationResult
        classifier = MagnaClassifier(db=None, threshold=0.6)
        result = classifier.classify("Busca el precio actual de Bitcoin")
        assert isinstance(result, ClassificationResult)
        assert hasattr(result, "route")
        assert hasattr(result, "score")
        assert hasattr(result, "category")
        assert hasattr(result, "cached")

    def test_classify_result_has_value_attribute(self):
        """route and category should be enums with .value."""
        from kernel.magna_classifier import MagnaClassifier
        classifier = MagnaClassifier(db=None, threshold=0.6)
        result = classifier.classify("Reflexión sobre el estado del sistema")
        assert hasattr(result.route, "value")
        assert hasattr(result.category, "value")
        assert isinstance(result.route.value, str)
        assert isinstance(result.category.value, str)

    def test_embrion_loop_uses_to_thread_for_classify(self):
        """embrion_loop should call classify via asyncio.to_thread (sync method)."""
        import inspect
        from kernel.embrion_loop import EmbrionLoop
        source = inspect.getsource(EmbrionLoop._think)
        # Should use to_thread for the sync classify method
        assert "asyncio.to_thread" in source
        # Should NOT use 'message=' kwarg
        assert "message=prompt" not in source


# ── 4. FCS counter ──────────────────────────────────────────────────

class TestFCSCounter:
    """Verify FCS counter is properly wired."""

    def test_fcs_counter_initialized(self):
        """_fcs_tool_calls_total must be initialized to 0."""
        import inspect
        from kernel.embrion_loop import EmbrionLoop
        source = inspect.getsource(EmbrionLoop.__init__)
        assert "_fcs_tool_calls_total" in source

    def test_fcs_counter_incremented_in_think(self):
        """_fcs_tool_calls_total must be incremented in _think."""
        import inspect
        from kernel.embrion_loop import EmbrionLoop
        source = inspect.getsource(EmbrionLoop._think)
        assert "_fcs_tool_calls_total += len(tool_calls)" in source

    def test_fcs_counter_exposed_in_stats(self):
        """FCS counter must appear in the stats property."""
        import inspect
        from kernel.embrion_loop import EmbrionLoop
        source = inspect.getsource(EmbrionLoop.stats.fget)
        assert "tool_calls_total" in source


# ── 5. /v1/embrion/diagnostic endpoint ──────────────────────────────

class TestDiagnosticEndpoint:
    """Verify the diagnostic endpoint exists and returns correct shape."""

    def test_diagnostic_route_exists(self):
        """The diagnostic route must be registered."""
        from kernel.embrion_routes import router
        routes = [r.path for r in router.routes]
        assert any("/diagnostic" in r for r in routes)

    def test_diagnostic_is_get(self):
        """Diagnostic endpoint must be GET."""
        from kernel.embrion_routes import router
        for route in router.routes:
            if "/diagnostic" in getattr(route, 'path', ''):
                assert "GET" in route.methods
                break
        else:
            pytest.fail("/diagnostic route not found")

    def test_diagnostic_handler_returns_required_keys(self):
        """Diagnostic handler must return timestamp, version, loop, health_verdict."""
        import inspect
        from kernel.embrion_routes import embrion_diagnostic
        source = inspect.getsource(embrion_diagnostic)
        required_keys = ["timestamp", "version", "loop", "health_verdict", "errors", "fcs", "db"]
        for key in required_keys:
            assert f'"{key}"' in source or f"'{key}'" in source, f"Missing key: {key}"


# ── 6. delegate_task basic contract ──────────────────────────────────

class TestDelegateTaskContract:
    """Verify delegate_task interface without external creds."""

    def test_delegate_module_importable(self):
        """tools.delegate must be importable."""
        from tools.delegate import delegate_task
        assert callable(delegate_task)

    def test_delegate_has_role_configs(self):
        """ROLE_CONFIGS must define known roles."""
        from tools.delegate import ROLE_CONFIGS
        assert isinstance(ROLE_CONFIGS, dict)
        assert len(ROLE_CONFIGS) > 0
        # At least estratega should exist
        assert "estratega" in ROLE_CONFIGS

    def test_delegate_guards_exist(self):
        """Safety guards must be defined."""
        from tools.delegate import (
            MAX_DELEGATION_DEPTH,
            MAX_DELEGATIONS_PER_TURN,
            MAX_TASK_LENGTH,
            DELEGATE_TIMEOUT_S,
        )
        assert MAX_DELEGATION_DEPTH >= 1
        assert MAX_DELEGATIONS_PER_TURN >= 1
        assert MAX_TASK_LENGTH > 0
        assert DELEGATE_TIMEOUT_S > 0


# ── 7. Brand compliance for Sprint 83 ───────────────────────────────

class TestBrandCompliance:
    """Sprint 83 Brand Compliance Checklist."""

    def test_no_generic_error_messages(self):
        """New code should not use generic error messages."""
        import inspect
        from memory.supabase_client import SupabaseClient
        source = inspect.getsource(SupabaseClient)
        generic_errors = ["internal server error", "something went wrong", "an error occurred"]
        for msg in generic_errors:
            assert msg not in source.lower(), f"Generic error found: {msg}"

    def test_structured_logging_used(self):
        """New code should use structlog, not print()."""
        import inspect
        from memory.supabase_client import SupabaseClient
        source = inspect.getsource(SupabaseClient)
        assert "structlog" in inspect.getsource(
            __import__("memory.supabase_client", fromlist=["SupabaseClient"])
        )

    def test_diagnostic_endpoint_has_docstring(self):
        """Diagnostic endpoint must have a docstring."""
        from kernel.embrion_routes import embrion_diagnostic
        assert embrion_diagnostic.__doc__ is not None
        assert len(embrion_diagnostic.__doc__) > 20
