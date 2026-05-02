"""
Tests for SP9 (Adaptive Model Selection), SP10 (Command Center Bridge),
and SP11 (Browser Automation).

Sprint: SP9/SP10/SP11 (Embrión Superpowers)
"""
import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ════════════════════════════════════════════════════════════════════
# SP9: Adaptive Model Selector Tests
# ════════════════════════════════════════════════════════════════════

from kernel.adaptive_model_selector import (
    AdaptiveModelSelector,
    TaskClass,
    classify_task,
    DEFAULT_ROUTING,
    MODEL_REGISTRY,
    PerformanceRecord,
    init_adaptive_model_selector,
    get_adaptive_model_selector,
)


class TestTaskClassification:
    """Test task classification logic."""

    def test_classify_creative_task(self):
        assert classify_task("Escribe un copy para Instagram") == TaskClass.CREATIVE

    def test_classify_reasoning_task(self):
        assert classify_task("Analiza por qué el sistema falla") == TaskClass.REASONING

    def test_classify_factual_search(self):
        assert classify_task("Busca estadísticas de ventas 2025") == TaskClass.FACTUAL_SEARCH

    def test_classify_code_generation(self):
        assert classify_task("Escribe código para un API endpoint") == TaskClass.CODE_GENERATION

    def test_classify_code_review(self):
        assert classify_task("Revisa el código y encuentra el bug") == TaskClass.CODE_REVIEW

    def test_classify_planning(self):
        assert classify_task("Crea un plan paso a paso para el deploy") == TaskClass.PLANNING

    def test_classify_analysis(self):
        assert classify_task("Resume este documento largo") == TaskClass.ANALYSIS

    def test_classify_translation(self):
        assert classify_task("Traduce esto al inglés") == TaskClass.TRANSLATION

    def test_classify_with_tool_hint(self):
        assert classify_task("Haz algo", tool_hint="web_search") == TaskClass.FACTUAL_SEARCH
        assert classify_task("Haz algo", tool_hint="code_exec") == TaskClass.CODE_GENERATION

    def test_classify_unknown_defaults_to_analysis(self):
        assert classify_task("xyz abc 123") == TaskClass.ANALYSIS


class TestAdaptiveModelSelector:
    """Test the adaptive model selector."""

    @pytest.fixture
    def selector(self):
        return AdaptiveModelSelector(db=None)

    def test_select_model_default_routing(self, selector):
        """Without performance data, should use default routing."""
        model = selector.select_model(TaskClass.CREATIVE)
        assert model == "gemini-3.1-pro"

        model = selector.select_model(TaskClass.REASONING)
        assert model == "claude-opus-4-7"

        model = selector.select_model(TaskClass.FACTUAL_SEARCH)
        assert model == "sonar-reasoning-pro"

    def test_select_model_with_tool_requirement(self, selector):
        """Should filter models that don't support tools."""
        model = selector.select_model(TaskClass.FACTUAL_SEARCH, require_tools=True)
        # sonar-reasoning-pro doesn't support tools, should skip to next
        assert model != "sonar-reasoning-pro"

    def test_select_model_with_budget(self, selector):
        """Should respect budget constraints."""
        model = selector.select_model(TaskClass.REASONING, budget_usd=0.001)
        # claude-opus-4-7 costs 0.015, should be skipped
        assert model != "claude-opus-4-7"

    def test_select_model_learned_override(self, selector):
        """With enough performance data, should override defaults."""
        # Simulate gpt-5.5 being better than gemini for creative tasks
        key = f"{TaskClass.CREATIVE.value}:gpt-5.5"
        selector._performance_cache[key] = PerformanceRecord(
            task_class=TaskClass.CREATIVE.value,
            model_id="gpt-5.5",
            total_calls=10,
            successes=9,
            failures=1,
            avg_quality_score=0.9,
            avg_latency_ms=500,
            avg_cost_usd=0.005,
        )

        model = selector.select_model(TaskClass.CREATIVE)
        assert model == "gpt-5.5"

    @pytest.mark.asyncio
    async def test_record_outcome(self, selector):
        """Should record outcomes and update cache."""
        await selector.record_outcome(
            task_class=TaskClass.REASONING,
            model_id="claude-opus-4-7",
            success=True,
            latency_ms=1200,
            cost_usd=0.02,
            quality_score=0.85,
        )

        key = f"{TaskClass.REASONING.value}:claude-opus-4-7"
        assert key in selector._performance_cache
        record = selector._performance_cache[key]
        assert record.total_calls == 1
        assert record.successes == 1
        assert record.avg_quality_score > 0.5

    @pytest.mark.asyncio
    async def test_record_multiple_outcomes(self, selector):
        """Should compute running averages correctly."""
        for i in range(5):
            await selector.record_outcome(
                task_class=TaskClass.ANALYSIS,
                model_id="gpt-5.5",
                success=True,
                latency_ms=500 + i * 100,
                cost_usd=0.01,
                quality_score=0.8,
            )

        key = f"{TaskClass.ANALYSIS.value}:gpt-5.5"
        record = selector._performance_cache[key]
        assert record.total_calls == 5
        assert record.successes == 5
        assert record.success_rate == 1.0

    def test_get_rankings(self, selector):
        """Should return ranked models."""
        # Add some data
        selector._performance_cache["creative:gpt-5.5"] = PerformanceRecord(
            task_class="creative", model_id="gpt-5.5",
            total_calls=10, successes=8, avg_quality_score=0.8,
        )
        selector._performance_cache["creative:claude-opus-4-7"] = PerformanceRecord(
            task_class="creative", model_id="claude-opus-4-7",
            total_calls=10, successes=9, avg_quality_score=0.9,
        )

        rankings = selector.get_rankings(TaskClass.CREATIVE)
        assert len(rankings) == 2
        # Higher composite score first
        assert rankings[0]["model_id"] == "claude-opus-4-7"

    def test_get_stats(self, selector):
        """Should return valid stats."""
        stats = selector.get_stats()
        assert "selections" in stats
        assert "cache_size" in stats
        assert stats["models_registered"] == len(MODEL_REGISTRY)


class TestPerformanceRecord:
    """Test performance record calculations."""

    def test_success_rate_no_calls(self):
        record = PerformanceRecord(task_class="test", model_id="test")
        assert record.success_rate == 0.5  # neutral prior

    def test_success_rate_with_calls(self):
        record = PerformanceRecord(
            task_class="test", model_id="test",
            total_calls=10, successes=8, failures=2,
        )
        assert record.success_rate == 0.8

    def test_composite_score_range(self):
        record = PerformanceRecord(
            task_class="test", model_id="gpt-5.5",
            total_calls=10, successes=10,
            avg_quality_score=1.0, avg_cost_usd=0.0,
        )
        assert 0 <= record.composite_score <= 1.0


# ════════════════════════════════════════════════════════════════════
# SP10: Command Center Bridge Tests
# ════════════════════════════════════════════════════════════════════

from kernel.command_center_bridge import (
    CommandCenterBridge,
    ExecutionSnapshot,
    DelegationRequest,
    DelegationResult,
    init_command_center_bridge,
    get_command_center_bridge,
)


class TestExecutionSnapshot:
    """Test snapshot data model."""

    def test_snapshot_to_dict(self):
        snapshot = ExecutionSnapshot(
            snapshot_id="test-123",
            source="embrion",
            task_id="task-456",
            status="running",
            tool_calls=3,
            cost_usd=0.015,
        )
        d = snapshot.to_dict()
        assert d["snapshot_id"] == "test-123"
        assert d["source"] == "embrion"
        assert d["task_id"] == "task-456"
        assert d["tool_calls"] == 3
        assert d["cost_usd"] == 0.015

    def test_snapshot_defaults(self):
        snapshot = ExecutionSnapshot(snapshot_id="x")
        d = snapshot.to_dict()
        assert d["status"] == "running"
        assert d["progress_pct"] == 0.0
        assert d["tool_calls"] == 0


class TestCommandCenterBridge:
    """Test the Command Center bridge."""

    @pytest.fixture
    def bridge(self):
        return CommandCenterBridge()

    @pytest.mark.asyncio
    async def test_send_snapshot_not_initialized(self, bridge):
        """Should silently skip if not initialized."""
        snapshot = ExecutionSnapshot(snapshot_id="test")
        result = await bridge.send_snapshot(snapshot)
        assert result is False

    @pytest.mark.asyncio
    async def test_send_snapshot_rate_limiting(self, bridge):
        """Should rate limit snapshots."""
        bridge._initialized = True
        bridge._http_client = AsyncMock()
        bridge._http_client.post = AsyncMock(
            return_value=MagicMock(status_code=200)
        )

        # Send MAX_SNAPSHOTS_PER_MINUTE + 1 snapshots
        from kernel.command_center_bridge import MAX_SNAPSHOTS_PER_MINUTE, _snapshot_timestamps
        _snapshot_timestamps.clear()

        results = []
        for i in range(MAX_SNAPSHOTS_PER_MINUTE + 2):
            snapshot = ExecutionSnapshot(snapshot_id=f"test-{i}")
            result = await bridge.send_snapshot(snapshot)
            results.append(result)

        # Last ones should be rate limited
        assert results[-1] is False

    @pytest.mark.asyncio
    async def test_send_snapshot_success(self, bridge):
        """Should send snapshot successfully."""
        from kernel.command_center_bridge import _snapshot_timestamps
        _snapshot_timestamps.clear()

        bridge._initialized = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        bridge._http_client = AsyncMock()
        bridge._http_client.post = AsyncMock(return_value=mock_response)

        snapshot = ExecutionSnapshot(
            snapshot_id="test-success",
            status="completed",
            tool_calls=5,
        )
        result = await bridge.send_snapshot(snapshot)
        assert result is True
        assert bridge._stats["snapshots_sent"] == 1

    @pytest.mark.asyncio
    async def test_send_snapshot_failure(self, bridge):
        """Should handle HTTP errors gracefully."""
        from kernel.command_center_bridge import _snapshot_timestamps
        _snapshot_timestamps.clear()

        bridge._initialized = True
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        bridge._http_client = AsyncMock()
        bridge._http_client.post = AsyncMock(return_value=mock_response)

        snapshot = ExecutionSnapshot(snapshot_id="test-fail")
        result = await bridge.send_snapshot(snapshot)
        assert result is False
        assert bridge._stats["snapshots_failed"] == 1

    def test_get_stats(self, bridge):
        """Should return valid stats."""
        stats = bridge.get_stats()
        assert "snapshots_sent" in stats
        assert "delegations_created" in stats
        assert "initialized" in stats


class TestDelegationRequest:
    """Test delegation data models."""

    def test_delegation_request_defaults(self):
        req = DelegationRequest(prompt="Research AI trends")
        assert req.account == "google"
        assert req.priority == "normal"
        assert req.timeout_s == 300.0

    def test_delegation_result_to_dict(self):
        result = DelegationResult(
            task_id="task-789",
            status="completed",
            output="Found 5 trends",
            cost_usd=0.05,
            latency_ms=15000,
        )
        d = result.to_dict()
        assert d["task_id"] == "task-789"
        assert d["status"] == "completed"
        assert d["output"] == "Found 5 trends"


# ════════════════════════════════════════════════════════════════════
# SP11: Browser Automation Tests
# ════════════════════════════════════════════════════════════════════

from tools.browser_automation import (
    BrowserAction,
    BrowserResult,
    BrowserSession,
    _is_url_safe,
    _truncate,
    ACTIONS,
    handle_browser_automation,
)


class TestURLSafety:
    """Test URL safety checks."""

    def test_safe_urls(self):
        assert _is_url_safe("https://google.com") is True
        assert _is_url_safe("https://example.com/path") is True
        assert _is_url_safe("http://api.github.com") is True

    def test_blocked_urls(self):
        assert _is_url_safe("http://localhost:3000") is False
        assert _is_url_safe("http://127.0.0.1") is False
        assert _is_url_safe("http://0.0.0.0:8080") is False

    def test_invalid_urls(self):
        assert _is_url_safe("") is False
        assert _is_url_safe("ftp://files.com") is False
        assert _is_url_safe("file:///etc/passwd") is False


class TestTruncate:
    """Test text truncation."""

    def test_short_text_unchanged(self):
        assert _truncate("hello", 100) == "hello"

    def test_long_text_truncated(self):
        long_text = "x" * 200
        result = _truncate(long_text, 100)
        assert len(result) < 200
        assert "TRUNCATED" in result


class TestBrowserAction:
    """Test browser action data model."""

    def test_navigate_action(self):
        action = BrowserAction(action="navigate", url="https://example.com")
        assert action.action == "navigate"
        assert action.url == "https://example.com"
        assert action.timeout_ms == 30_000

    def test_click_action(self):
        action = BrowserAction(action="click", selector="button.submit")
        assert action.selector == "button.submit"


class TestBrowserResult:
    """Test browser result data model."""

    def test_success_result(self):
        result = BrowserResult(
            success=True,
            action="navigate",
            data="Page content",
            url="https://example.com",
            title="Example",
            latency_ms=1500.5,
        )
        d = result.to_dict()
        assert d["success"] is True
        assert d["action"] == "navigate"
        assert d["data"] == "Page content"
        assert d["latency_ms"] == 1500.5

    def test_error_result(self):
        result = BrowserResult(
            success=False,
            action="click",
            error="Element not found",
        )
        d = result.to_dict()
        assert d["success"] is False
        assert d["error"] == "Element not found"


class TestBrowserSession:
    """Test browser session (mocked, no real Playwright)."""

    @pytest.fixture
    def session(self):
        return BrowserSession()

    def test_initial_state(self, session):
        assert session._initialized is False
        assert session._stats["actions_executed"] == 0

    @pytest.mark.asyncio
    async def test_execute_without_init_triggers_init(self, session):
        """Should try to initialize on first execute and handle failure."""
        action = BrowserAction(action="navigate", url="https://example.com")

        # Patch the initialize to raise — execute catches it in the outer try/except
        with patch.object(session, 'initialize', side_effect=RuntimeError("Playwright not installed")):
            result = await session.execute(action)
            assert result.success is False
            assert "Playwright not installed" in result.error

    def test_get_stats(self, session):
        stats = session.get_stats()
        assert stats["actions_executed"] == 0
        assert stats["initialized"] is False


class TestHandleBrowserAutomation:
    """Test the tool handler entry point."""

    @pytest.mark.asyncio
    async def test_handle_unknown_action(self):
        """Should handle unknown actions gracefully."""
        with patch("tools.browser_automation.get_browser_session") as mock_get:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(return_value=BrowserResult(
                success=False,
                action="unknown_action",
                error="Unknown action: unknown_action",
            ))
            mock_get.return_value = mock_session

            result = await handle_browser_automation({"action": "unknown_action"})
            assert result["success"] is False

    @pytest.mark.asyncio
    async def test_handle_multi_step_empty(self):
        """Should error on empty multi_step."""
        with patch("tools.browser_automation.get_browser_session") as mock_get:
            mock_session = AsyncMock()
            mock_get.return_value = mock_session

            result = await handle_browser_automation({
                "action": "multi_step",
                "steps": [],
            })
            assert "error" in result

    @pytest.mark.asyncio
    async def test_handle_navigate(self):
        """Should handle navigate action."""
        with patch("tools.browser_automation.get_browser_session") as mock_get:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(return_value=BrowserResult(
                success=True,
                action="navigate",
                data="Page content here",
                url="https://example.com",
                title="Example",
                latency_ms=800,
            ))
            mock_get.return_value = mock_session

            result = await handle_browser_automation({
                "action": "navigate",
                "url": "https://example.com",
            })
            assert result["success"] is True
            assert result["url"] == "https://example.com"


# ════════════════════════════════════════════════════════════════════
# Integration Tests (cross-SP)
# ════════════════════════════════════════════════════════════════════

class TestSPIntegration:
    """Test integration between superpowers."""

    @pytest.mark.asyncio
    async def test_selector_records_feed_rankings(self):
        """SP9: Recording outcomes should affect future selections."""
        selector = AdaptiveModelSelector(db=None)

        # Record many successes for a non-default model
        for _ in range(10):
            await selector.record_outcome(
                task_class=TaskClass.CREATIVE,
                model_id="gpt-5.5",
                success=True,
                quality_score=0.95,
                latency_ms=400,
                cost_usd=0.005,
            )

        # Now it should select gpt-5.5 over the default gemini-3.1-pro
        selected = selector.select_model(TaskClass.CREATIVE)
        assert selected == "gpt-5.5"

    def test_snapshot_captures_verification(self):
        """SP10 + SP5: Snapshot should capture verification data."""
        snapshot = ExecutionSnapshot(
            snapshot_id="integration-test",
            source="verifier",
            verification_verdict="SUCCESS",
            verification_evidence=["tool_output: Created file"],
            tool_calls=3,
        )
        d = snapshot.to_dict()
        assert d["verification_verdict"] == "SUCCESS"
        assert d["tool_calls"] == 3
        assert len(d["verification_evidence"]) == 1
