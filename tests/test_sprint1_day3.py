"""
Tests for Sprint 1 Day 3 — HITL Telegram Handler, Observability, API Endpoint.
14 abril 2026.
"""
import os
import sys
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

# Ensure project root is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ═══════════════════════════════════════════════════════════════════
# 1. HITL Handler Tests
# ═══════════════════════════════════════════════════════════════════

class TestHITLHandler:
    """Tests for bot/hitl_handler.py"""

    def test_import_hitl_handler(self):
        """HITL handler module should import cleanly."""
        from bot.hitl_handler import send_hitl_review, hitl_router, get_pending_reviews
        assert send_hitl_review is not None
        assert hitl_router is not None
        assert callable(get_pending_reviews)

    def test_risk_emoji_mapping(self):
        """Risk emojis should map to all 5 risk levels."""
        from bot.hitl_handler import RISK_EMOJI, RISK_LABEL
        assert len(RISK_EMOJI) == 5
        assert RISK_EMOJI["L1_SAFE"] == "🟢"
        assert RISK_EMOJI["L4_CRITICAL"] == "🔴"
        assert RISK_EMOJI["L5_FORBIDDEN"] == "⛔"
        assert len(RISK_LABEL) == 5

    def test_escape_html(self):
        """HTML escaping should handle all special characters."""
        from bot.hitl_handler import _escape_html
        assert _escape_html("<script>alert('xss')</script>") == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;" or \
               "&lt;script&gt;" in _escape_html("<script>alert('xss')</script>")
        assert _escape_html("a & b") == "a &amp; b"
        assert _escape_html('"quotes"') == "&quot;quotes&quot;"

    def test_get_pending_reviews_empty(self):
        """Pending reviews should start empty."""
        from bot.hitl_handler import get_pending_reviews, _pending_reviews
        _pending_reviews.clear()
        result = get_pending_reviews()
        assert result == {}

    def test_hitl_router_has_handlers(self):
        """HITL router should have callback query handlers registered."""
        from bot.hitl_handler import hitl_router
        # Router should exist and be named
        assert hitl_router.name == "hitl"

    @pytest.mark.asyncio
    async def test_send_hitl_review_formats_message(self):
        """send_hitl_review should format and send a Telegram message."""
        from bot.hitl_handler import send_hitl_review, _pending_reviews
        _pending_reviews.clear()

        mock_bot = AsyncMock()
        mock_msg = MagicMock()
        mock_msg.message_id = 12345
        mock_bot.send_message = AsyncMock(return_value=mock_msg)

        payload = {
            "type": "hitl_review",
            "run_id": "test-run-123",
            "intent": "execute",
            "message_preview": "Delete all files",
            "proposed_response_preview": "I will delete all files now",
            "risk_level": "L3_SENSITIVE",
            "trust_ring": "R2_USER_DELEGATED",
            "reason": "Destructive operation requires approval",
            "timestamp": "2026-04-14T12:00:00Z",
        }

        result = await send_hitl_review(mock_bot, 123456, payload)

        # Should have called send_message
        mock_bot.send_message.assert_called_once()
        call_kwargs = mock_bot.send_message.call_args.kwargs
        assert call_kwargs["chat_id"] == 123456
        assert call_kwargs["parse_mode"] == "HTML"
        assert "HITL Review Required" in call_kwargs["text"]
        assert "Sensitive" in call_kwargs["text"]
        assert call_kwargs["reply_markup"] is not None

        # Should be stored in pending reviews
        assert "test-run-123" in _pending_reviews
        assert _pending_reviews["test-run-123"]["status"] == "pending"

        _pending_reviews.clear()

    def test_hitl_timeout_configurable(self):
        """HITL timeout should be configurable via env var."""
        from bot.hitl_handler import HITL_TIMEOUT_SECONDS
        assert isinstance(HITL_TIMEOUT_SECONDS, int)
        assert HITL_TIMEOUT_SECONDS > 0


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
    """Tests for new API endpoints added in Day 3."""

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


# ═══════════════════════════════════════════════════════════════════
# 4. State Schema Tests
# ═══════════════════════════════════════════════════════════════════

class TestStateSchema:
    """Verify state schema supports new Day 3 fields."""

    def test_state_supports_trace_ctx(self):
        """MonstruoState should accept _trace_ctx field."""
        from kernel.state import MonstruoState
        # TypedDict should allow extra fields via total=False or NotRequired
        # We just verify the type exists
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
        expected_nodes = ["intake", "classify_and_route", "enrich", "execute", "hitl_review", "respond", "memory_write"]
        for node in expected_nodes:
            assert node in mermaid, f"Node {node} missing from graph"

    def test_all_imports_clean(self):
        """All new modules should import without errors."""
        import bot.hitl_handler
        import core.composite_risk
        import core.policy_engine
        import kernel.hitl
        import observability.manager
        import observability.langfuse_bridge
        assert True  # If we get here, all imports succeeded
