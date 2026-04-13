"""
El Monstruo — Day 3 Tests: Observability Layer
================================================
Tests for the Langfuse bridge, OTel bridge, and ObservabilityManager.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# ── Langfuse Bridge Tests ──────────────────────────────────────────

class TestLangfuseBridge:
    """Tests for the Langfuse bridge — graceful degradation is key."""

    def test_import(self):
        """Bridge module can be imported."""
        from observability.langfuse_bridge import LangfuseBridge
        bridge = LangfuseBridge()
        assert bridge is not None
        assert bridge.enabled is False

    @pytest.mark.asyncio
    async def test_initialize_without_credentials(self):
        """Bridge gracefully disables when no credentials are set."""
        from observability.langfuse_bridge import LangfuseBridge
        bridge = LangfuseBridge()
        result = await bridge.initialize()
        assert result is False
        assert bridge.enabled is False

    def test_trace_run_start_when_disabled(self):
        """trace_run_start returns None when disabled."""
        from observability.langfuse_bridge import LangfuseBridge
        bridge = LangfuseBridge()
        result = bridge.trace_run_start("run_1", "user_1", "api", "hello")
        assert result is None

    def test_trace_span_when_disabled(self):
        """trace_span returns None when no trace."""
        from observability.langfuse_bridge import LangfuseBridge
        bridge = LangfuseBridge()
        result = bridge.trace_span(None, "test_span")
        assert result is None

    def test_trace_generation_when_disabled(self):
        """trace_generation returns None when no trace."""
        from observability.langfuse_bridge import LangfuseBridge
        bridge = LangfuseBridge()
        result = bridge.trace_generation(
            None, "test", "gpt-5.4", [{"role": "user", "content": "hi"}], "hello"
        )
        assert result is None

    def test_trace_run_end_when_disabled(self):
        """trace_run_end is a no-op when no trace."""
        from observability.langfuse_bridge import LangfuseBridge
        bridge = LangfuseBridge()
        bridge.trace_run_end(None, "output", "completed")  # Should not raise

    def test_trace_event_when_disabled(self):
        """trace_event is a no-op when no trace."""
        from observability.langfuse_bridge import LangfuseBridge
        bridge = LangfuseBridge()
        bridge.trace_event(None, "test_event")  # Should not raise

    def test_score_run_when_disabled(self):
        """score_run is a no-op when no trace."""
        from observability.langfuse_bridge import LangfuseBridge
        bridge = LangfuseBridge()
        bridge.score_run(None, "quality", 0.9)  # Should not raise

    @pytest.mark.asyncio
    async def test_flush_when_disabled(self):
        """flush is a no-op when disabled."""
        from observability.langfuse_bridge import LangfuseBridge
        bridge = LangfuseBridge()
        await bridge.flush()  # Should not raise

    @pytest.mark.asyncio
    async def test_shutdown_when_disabled(self):
        """shutdown is a no-op when disabled."""
        from observability.langfuse_bridge import LangfuseBridge
        bridge = LangfuseBridge()
        await bridge.shutdown()  # Should not raise


# ── OTel Bridge Tests ──────────────────────────────────────────────

class TestOTelBridge:
    """Tests for the OpenTelemetry bridge."""

    def test_import(self):
        """OTel bridge module can be imported."""
        from observability.otel_bridge import OTelBridge
        bridge = OTelBridge()
        assert bridge is not None
        assert bridge.enabled is False

    @pytest.mark.asyncio
    async def test_initialize_without_endpoint(self):
        """OTel bridge gracefully disables when no endpoint is set."""
        from observability.otel_bridge import OTelBridge
        bridge = OTelBridge()
        # Clear any env vars that might be set
        with patch.dict("os.environ", {}, clear=True):
            result = await bridge.initialize()
            assert result is False
            assert bridge.enabled is False

    def test_span_when_disabled(self):
        """span context manager works as no-op when disabled."""
        from observability.otel_bridge import OTelBridge
        bridge = OTelBridge()
        with bridge.span("test_span", {"key": "value"}) as span:
            span.set_attribute("test", "value")  # Should not raise
            span.add_event("test_event")  # Should not raise

    def test_record_exception_when_disabled(self):
        """record_exception is a no-op when disabled."""
        from observability.otel_bridge import OTelBridge, _NoOpSpan
        bridge = OTelBridge()
        bridge.record_exception(_NoOpSpan(), ValueError("test"))  # Should not raise

    @pytest.mark.asyncio
    async def test_shutdown_when_disabled(self):
        """shutdown is a no-op when disabled."""
        from observability.otel_bridge import OTelBridge
        bridge = OTelBridge()
        await bridge.shutdown()  # Should not raise


# ── NoOp Span Tests ────────────────────────────────────────────────

class TestNoOpSpan:
    """Tests for the _NoOpSpan fallback."""

    def test_all_methods_are_noop(self):
        """All methods on _NoOpSpan should be no-ops."""
        from observability.otel_bridge import _NoOpSpan
        span = _NoOpSpan()
        span.set_attribute("key", "value")
        span.record_exception(ValueError("test"))
        span.set_status(None)
        span.add_event("test", {"key": "value"})


# ── Observability Manager Tests ────────────────────────────────────

class TestObservabilityManager:
    """Tests for the unified ObservabilityManager facade."""

    def test_import(self):
        """Manager can be imported."""
        from observability.manager import ObservabilityManager
        manager = ObservabilityManager()
        assert manager is not None

    @pytest.mark.asyncio
    async def test_initialize_returns_status(self):
        """initialize returns a dict with bridge statuses."""
        from observability.manager import ObservabilityManager
        manager = ObservabilityManager()
        status = await manager.initialize()
        assert isinstance(status, dict)
        assert "langfuse" in status
        assert "opentelemetry" in status
        # Both should be False without credentials
        assert status["langfuse"] is False

    def test_start_trace(self):
        """start_trace returns a TraceContext."""
        from observability.manager import ObservabilityManager, TraceContext
        manager = ObservabilityManager()
        ctx = manager.start_trace("run_1", "user_1", "api", "hello")
        assert isinstance(ctx, TraceContext)
        assert ctx.run_id == "run_1"

    def test_record_span_without_trace(self):
        """record_span works even when bridges are disabled."""
        from observability.manager import ObservabilityManager, TraceContext
        manager = ObservabilityManager()
        ctx = TraceContext(run_id="run_1")
        manager.record_span(ctx, "test_span")  # Should not raise

    def test_record_generation_without_trace(self):
        """record_generation works even when bridges are disabled."""
        from observability.manager import ObservabilityManager, TraceContext
        manager = ObservabilityManager()
        ctx = TraceContext(run_id="run_1")
        manager.record_generation(
            ctx, "test", "gpt-5.4",
            [{"role": "user", "content": "hi"}],
            "hello",
            {"prompt_tokens": 10, "completion_tokens": 20},
        )  # Should not raise

    def test_record_event_without_trace(self):
        """record_event works even when bridges are disabled."""
        from observability.manager import ObservabilityManager, TraceContext
        manager = ObservabilityManager()
        ctx = TraceContext(run_id="run_1")
        manager.record_event(ctx, "policy_check", {"passed": True})

    def test_score_without_trace(self):
        """score works even when bridges are disabled."""
        from observability.manager import ObservabilityManager, TraceContext
        manager = ObservabilityManager()
        ctx = TraceContext(run_id="run_1")
        manager.score(ctx, "quality", 0.95, "Good response")

    def test_end_trace_without_trace(self):
        """end_trace works even when bridges are disabled."""
        from observability.manager import ObservabilityManager, TraceContext
        manager = ObservabilityManager()
        ctx = TraceContext(run_id="run_1")
        manager.end_trace(ctx, "response text", "completed")

    @pytest.mark.asyncio
    async def test_flush_without_bridges(self):
        """flush works even when bridges are disabled."""
        from observability.manager import ObservabilityManager
        manager = ObservabilityManager()
        await manager.flush()

    @pytest.mark.asyncio
    async def test_shutdown_without_bridges(self):
        """shutdown works even when bridges are disabled."""
        from observability.manager import ObservabilityManager
        manager = ObservabilityManager()
        await manager.shutdown()

    def test_properties(self):
        """Property accessors work."""
        from observability.manager import ObservabilityManager
        manager = ObservabilityManager()
        assert manager.langfuse_enabled is False
        assert manager.otel_enabled is False


# ── TraceContext Tests ─────────────────────────────────────────────

class TestTraceContext:
    """Tests for the TraceContext dataclass."""

    def test_creation(self):
        """TraceContext can be created with just run_id."""
        from observability.manager import TraceContext
        ctx = TraceContext(run_id="test_run")
        assert ctx.run_id == "test_run"
        assert ctx.langfuse_trace is None
        assert ctx.otel_spans == {}

    def test_with_traces(self):
        """TraceContext can hold trace references."""
        from observability.manager import TraceContext
        mock_trace = MagicMock()
        ctx = TraceContext(
            run_id="test_run",
            langfuse_trace=mock_trace,
        )
        assert ctx.langfuse_trace is mock_trace


# ── Integration: Kernel + Observability ────────────────────────────

class TestKernelObservabilityIntegration:
    """Tests that the kernel accepts and stores the observability parameter."""

    def test_kernel_accepts_observability(self):
        """LangGraphKernel constructor accepts observability parameter."""
        from kernel.engine import LangGraphKernel
        from observability.manager import ObservabilityManager

        obs = ObservabilityManager()
        kernel = LangGraphKernel(observability=obs)
        assert kernel._observability is obs

    def test_kernel_works_without_observability(self):
        """LangGraphKernel works fine without observability (backward compat)."""
        from kernel.engine import LangGraphKernel
        kernel = LangGraphKernel()
        assert kernel._observability is None


# ── Integration: Main App Health Endpoint ──────────────────────────

class TestMainAppObservability:
    """Tests that main.py correctly imports and references observability."""

    def test_main_imports_observability(self):
        """main.py can import ObservabilityManager."""
        from observability.manager import ObservabilityManager
        obs = ObservabilityManager()
        assert obs is not None

    def test_main_has_observability_global(self):
        """kernel/main.py has the observability global variable."""
        import kernel.main as main_module
        assert hasattr(main_module, "observability")
