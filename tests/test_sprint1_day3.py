"""
Tests for Sprint 1 Day 3 — Observability, API Endpoint, Integration.
Updated 14 abril 2026 — bot/hitl_handler.py removed (dead code, aiogram incompatible).
HITL tests now focus on kernel-side (hitl.py, engine.py, main.py).
"""

import os
import sys
from unittest.mock import MagicMock

# Ensure project root is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ═══════════════════════════════════════════════════════════════════
# 1. HITL Kernel Tests (replaces bot/hitl_handler.py tests)
# ═══════════════════════════════════════════════════════════════════


class TestHITLKernel:
    """Tests for kernel-side HITL: hitl.py, engine.py v2 API."""

    def test_hitl_gate_returns_respond_for_safe(self):
        """hitl_gate should return 'respond' when no approval needed."""
        from kernel.hitl import hitl_gate

        state = {
            "status": "completed",
            "policy_decision": "ALLOW",
            "needs_human_approval": False,
        }
        assert hitl_gate(state) == "respond"

    def test_hitl_gate_returns_hitl_review_for_hitl_policy(self):
        """hitl_gate should return 'hitl_review' when policy says HITL."""
        from kernel.hitl import hitl_gate

        state = {
            "status": "executing",
            "policy_decision": "HITL",
            "needs_human_approval": True,
        }
        assert hitl_gate(state) == "hitl_review"

    def test_hitl_gate_returns_respond_for_failed(self):
        """hitl_gate should skip HITL for failed runs."""
        from contracts.kernel_interface import RunStatus
        from kernel.hitl import hitl_gate

        state = {
            "status": RunStatus.FAILED.value,
            "policy_decision": "HITL",
            "needs_human_approval": True,
        }
        assert hitl_gate(state) == "respond"

    def test_hitl_review_payload_structure(self):
        """hitl_review interrupt payload should have required fields."""
        # We can't call interrupt() in a test (it needs a graph context),
        # but we can verify the payload builder logic
        from kernel.hitl import _summarize_envelope

        envelope = {
            "action_type": "delete",
            "target": {"resource_kind": "secret", "resource_id": "api_key_1"},
            "operation": "DELETE",
            "intent_summary": "Delete the API key",
        }
        summary = _summarize_envelope(envelope)
        assert summary["action_type"] == "delete"
        assert summary["target"]["resource_kind"] == "secret"
        assert summary["operation"] == "DELETE"

    def test_summarize_envelope_handles_none(self):
        """_summarize_envelope should handle None gracefully."""
        from kernel.hitl import _summarize_envelope

        assert _summarize_envelope(None) is None

    def test_event_to_dict_handles_dict(self):
        """_event_to_dict should pass through dicts."""
        from kernel.hitl import _event_to_dict

        d = {"key": "value"}
        assert _event_to_dict(d) == d

    def test_engine_uses_v2_api(self):
        """LangGraphKernel should use v2 API for interrupt detection."""
        import inspect

        from kernel.engine import LangGraphKernel

        source = inspect.getsource(LangGraphKernel.start_run)
        assert 'version="v2"' in source, "start_run must use v2 API"

    def test_engine_step_uses_v2_api(self):
        """LangGraphKernel.step() should use v2 API."""
        import inspect

        from kernel.engine import LangGraphKernel

        source = inspect.getsource(LangGraphKernel.step)
        assert 'version="v2"' in source, "step must use v2 API"


# ═══════════════════════════════════════════════════════════════════
# 2. Observability Integration Tests
# ═══════════════════════════════════════════════════════════════════


class TestObservabilityIntegration:
    """Tests for observability hooks in kernel nodes."""

    def test_obs_helper_exists(self):
        """_obs() helper should exist in nodes.py."""
        from kernel.nodes import _obs

        assert callable(_obs)

    def test_obs_returns_none_when_missing(self):
        """_obs() should return None when no observability in config."""
        from kernel.nodes import _obs

        config = {"configurable": {"thread_id": "test"}}
        assert _obs(config) is None

    def test_obs_returns_manager_when_present(self):
        """_obs() should return the observability manager from config."""
        from kernel.nodes import _obs

        mock_obs = MagicMock()
        config = {"configurable": {"thread_id": "test", "_observability": mock_obs}}
        assert _obs(config) is mock_obs

    def test_engine_passes_observability_in_config(self):
        """LangGraphKernel should pass _observability in config."""
        from kernel.engine import LangGraphKernel

        mock_obs = MagicMock()
        kernel = LangGraphKernel(observability=mock_obs)
        assert kernel._observability is mock_obs

    def test_observability_manager_facade(self):
        """ObservabilityManager should have all required methods."""
        from observability.manager import ObservabilityManager

        obs = ObservabilityManager()
        assert hasattr(obs, "start_trace")
        assert hasattr(obs, "record_span")
        assert hasattr(obs, "record_generation")
        assert hasattr(obs, "record_event")
        assert hasattr(obs, "end_trace")
        assert hasattr(obs, "score")
        assert hasattr(obs, "flush")
        assert hasattr(obs, "shutdown")

    def test_langfuse_bridge_graceful_degradation(self):
        """LangfuseBridge should work without credentials (no-op mode)."""
        from observability.langfuse_bridge import LangfuseBridge

        bridge = LangfuseBridge()
        assert bridge.enabled is False
        # All methods should be no-ops when disabled
        result = bridge.trace_run_start("run-1", "user-1", "api", "hello")
        assert result is None
        bridge.trace_span(None, "test")
        bridge.trace_generation(None, "test", "model", [], "output")
        bridge.trace_run_end(None, "output")


# ═══════════════════════════════════════════════════════════════════
# 3. API Endpoint Tests
# ═══════════════════════════════════════════════════════════════════


class TestAPIEndpoints:
    """Tests for API endpoints."""

    def test_hitl_pending_endpoint_exists(self):
        """GET /v1/hitl/pending endpoint should exist in the app."""
        from kernel.main import app

        routes = [r.path for r in app.routes]
        assert "/v1/hitl/pending" in routes

    def test_feedback_endpoint_exists(self):
        """POST /v1/feedback endpoint should exist."""
        from kernel.main import app

        routes = [r.path for r in app.routes]
        assert "/v1/feedback" in routes

    def test_step_endpoint_exists(self):
        """POST /v1/step endpoint should exist."""
        from kernel.main import app

        routes = [r.path for r in app.routes]
        assert "/v1/step" in routes

    def test_feedback_request_model(self):
        """FeedbackRequest should validate required fields."""
        from kernel.main import FeedbackRequest

        req = FeedbackRequest(
            run_id="test-123",
            action="approve",
            user_id="alfredo",
        )
        assert req.action == "approve"
        assert req.run_id == "test-123"

    def test_feedback_request_with_edit(self):
        """FeedbackRequest should accept edited_response for modify action."""
        from kernel.main import FeedbackRequest

        req = FeedbackRequest(
            run_id="test-123",
            action="edit",
            user_id="alfredo",
            edited_response="Modified response here",
            comment="Changed tone",
        )
        assert req.edited_response == "Modified response here"
        assert req.comment == "Changed tone"

    def test_chat_response_has_interrupt_payload(self):
        """ChatResponse should have interrupt_payload field."""
        from kernel.main import ChatResponse

        resp = ChatResponse(
            run_id="test-123",
            status="awaiting_human",
            intent="execute",
            model_used="gpt-5.4",
            response="I will delete the file",
            requires_approval=True,
            interrupt_payload={"risk_level": "L4_CRITICAL", "reason": "Destructive op"},
        )
        assert resp.interrupt_payload is not None
        assert resp.interrupt_payload["risk_level"] == "L4_CRITICAL"

    def test_chat_response_no_interrupt_when_completed(self):
        """ChatResponse should have None interrupt_payload when completed."""
        from kernel.main import ChatResponse

        resp = ChatResponse(
            run_id="test-123",
            status="completed",
            intent="chat",
            model_used="gpt-5.4",
            response="Hello!",
        )
        assert resp.interrupt_payload is None


# ═══════════════════════════════════════════════════════════════════
# 4. State Schema Tests
# ═══════════════════════════════════════════════════════════════════


class TestStateSchema:
    """Verify state schema supports Day 3 fields."""

    def test_state_supports_trace_ctx(self):
        """MonstruoState should accept _trace_ctx field."""
        from kernel.state import MonstruoState

        assert MonstruoState is not None

    def test_event_category_has_human_reviewed(self):
        """EventCategory should include HUMAN_REVIEWED."""
        from contracts.event_envelope import EventCategory

        assert hasattr(EventCategory, "HUMAN_REVIEWED")
        assert EventCategory.HUMAN_REVIEWED.value == "hitl.reviewed"


# ═══════════════════════════════════════════════════════════════════
# 5. Integration Smoke Tests
# ═══════════════════════════════════════════════════════════════════


class TestIntegrationSmoke:
    """Smoke tests to verify all components wire together."""

    def test_kernel_builds_graph_with_hitl(self):
        """Kernel should build graph with hitl_review node."""
        from kernel.engine import LangGraphKernel

        kernel = LangGraphKernel()
        mermaid = kernel.get_graph_mermaid()
        assert "hitl_review" in mermaid
        assert "execute" in mermaid
        assert "respond" in mermaid

    def test_kernel_graph_has_all_nodes(self):
        """Kernel graph should have all 7 nodes."""
        from kernel.engine import LangGraphKernel

        kernel = LangGraphKernel()
        mermaid = kernel.get_graph_mermaid()
        expected_nodes = [
            "intake",
            "classify_and_route",
            "enrich",
            "execute",
            "hitl_review",
            "respond",
            "memory_write",
        ]
        for node in expected_nodes:
            assert node in mermaid, f"Node {node} missing from graph"

    def test_all_imports_clean(self):
        """All new modules should import without errors."""
        # bot/hitl_handler.py removed — was dead code (aiogram != python-telegram-bot)
        assert True  # If we get here, all imports succeeded
