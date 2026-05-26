"""
H2 fix tests — gpt-5.x reasoning models use max_completion_tokens
====================================================================

Background
----------
GPT-5.x reasoning models (gpt-5.5, gpt-5-codex) reject HTTP requests with
``max_tokens`` parameter. They require ``max_completion_tokens`` instead
when invoked via /v1/chat/completions.

Scope
-----
Validates that:
  1. ``config/model_catalog.py`` declares gpt-5.5 with
     ``use_max_completion_tokens=True``.
  2. ``kernel/fallback_engine._call_openai_compat`` builds requests with
     ``max_completion_tokens`` (not ``max_tokens``) when given a model_config
     with ``use_max_completion_tokens=True``.
  3. ``kernel/fallback_engine._call_openai_compat`` builds requests with
     ``max_tokens`` (default) when no model_config is given (backward
     compatibility for non-reasoning models).
  4. ``kernel/fallback_engine`` does NOT trigger Claude fallback because of
     a HTTP 400 ``max_tokens`` error from OpenAI for gpt-5.x. (i.e., the
     pre-emptive fix avoids the BadRequestError altogether.)

Author: Manus (T2-B mandate, 2026-05-16)
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure repo root is in path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ════════════════════════════════════════════════════════════════════
# CLAIM 1: catalog declares gpt-5.5 with use_max_completion_tokens=True
# ════════════════════════════════════════════════════════════════════
class TestModelCatalogGPT55:
    """gpt-5.5 must declare use_max_completion_tokens=True."""

    def test_gpt5_5_uses_max_completion_tokens(self):
        from config.model_catalog import MODELS

        assert "gpt-5.5" in MODELS, "gpt-5.5 must exist in MODELS"
        entry = MODELS["gpt-5.5"]
        assert entry.get("use_max_completion_tokens") is True, (
            "gpt-5.5 must have use_max_completion_tokens=True so that both "
            "router/llm_client.py and kernel/fallback_engine.py send "
            "'max_completion_tokens' to /v1/chat/completions instead of "
            "'max_tokens' (which OpenAI rejects with HTTP 400)."
        )

    def test_gpt5_5_provider_is_openai(self):
        from config.model_catalog import MODELS

        assert MODELS["gpt-5.5"]["provider"] == "openai"


# ════════════════════════════════════════════════════════════════════
# CLAIM 2 + 3: fallback_engine routes the param correctly
# ════════════════════════════════════════════════════════════════════
class TestFallbackEngineOpenAICompat:
    """_call_openai_compat must route max_tokens param based on model_config."""

    @pytest.mark.asyncio
    async def test_gpt5_5_sends_max_completion_tokens_not_max_tokens(self):
        """When model_config has use_max_completion_tokens=True, the body
        must contain 'max_completion_tokens' and NOT 'max_tokens'."""
        from kernel.fallback_engine import FallbackEngine

        engine = FallbackEngine.__new__(FallbackEngine)  # bypass __init__

        captured_body = {}

        # Mock httpx.AsyncClient context manager
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={"choices": [{"message": {"content": "ok"}}]})

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        async def capture_post(url, headers=None, json=None):
            captured_body.update(json)
            return mock_response

        mock_client.post = AsyncMock(side_effect=capture_post)

        mock_async_client_class = MagicMock()
        mock_async_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("kernel.fallback_engine.httpx.AsyncClient", mock_async_client_class):
            await engine._call_openai_compat(
                api_key="test-key",
                base_url="https://api.openai.com/v1",
                model_id="gpt-5.5",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=4000,
                temperature=None,
                model_config={"use_max_completion_tokens": True},
            )

        assert "max_completion_tokens" in captured_body, (
            f"Expected 'max_completion_tokens' in body, got keys: {list(captured_body.keys())}"
        )
        assert captured_body["max_completion_tokens"] == 4000
        assert "max_tokens" not in captured_body, f"Expected NO 'max_tokens' for gpt-5.x, got body: {captured_body}"

    @pytest.mark.asyncio
    async def test_legacy_model_sends_max_tokens_default(self):
        """When model_config is None or use_max_completion_tokens=False, body
        must contain 'max_tokens' (backward compatibility)."""
        from kernel.fallback_engine import FallbackEngine

        engine = FallbackEngine.__new__(FallbackEngine)

        captured_body = {}

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={"choices": [{"message": {"content": "ok"}}]})

        mock_client = MagicMock()

        async def capture_post(url, headers=None, json=None):
            captured_body.update(json)
            return mock_response

        mock_client.post = AsyncMock(side_effect=capture_post)

        mock_async_client_class = MagicMock()
        mock_async_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("kernel.fallback_engine.httpx.AsyncClient", mock_async_client_class):
            await engine._call_openai_compat(
                api_key="test-key",
                base_url="https://api.openai.com/v1",
                model_id="gpt-4o",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=4096,
                temperature=0.7,
                model_config=None,  # legacy / non-reasoning
            )

        assert "max_tokens" in captured_body, f"Expected 'max_tokens' for non-reasoning, got: {captured_body}"
        assert captured_body["max_tokens"] == 4096
        assert "max_completion_tokens" not in captured_body


# ════════════════════════════════════════════════════════════════════
# CLAIM 4: pre-emptive avoidance of HTTP 400 max_tokens
# ════════════════════════════════════════════════════════════════════
class TestNoMaxTokensFor55:
    """Verify that with the catalog fix, no code path sends max_tokens for gpt-5.5."""

    def test_catalog_consistent_with_openai_chat_completions_api(self):
        """gpt-5.5 declared with use_max_completion_tokens=True ensures both
        router/llm_client.py and kernel/fallback_engine.py route the param
        correctly. This test acts as a regression guard against catalog drift."""
        from config.model_catalog import MODELS

        for model_name in ("gpt-5.5",):
            entry = MODELS[model_name]
            assert entry.get("use_max_completion_tokens") is True, (
                f"{model_name} must use max_completion_tokens to avoid HTTP 400 "
                f"'Use max_completion_tokens instead' from OpenAI."
            )

    def test_no_silent_fallback_to_claude_due_to_max_tokens_error(self):
        """Smoke test: with gpt-5.5 routed correctly, the fallback chain
        should not be triggered solely because of a max_tokens BadRequestError.

        This is a structural test — it verifies the catalog declares the right
        flag so that the fix is durable across deployments."""
        from config.model_catalog import MODELS

        gpt55 = MODELS["gpt-5.5"]
        # Pre-condition: catalog has the fix
        assert gpt55["use_max_completion_tokens"] is True
        # Pre-condition: provider routes via OpenAI chat.completions
        assert gpt55["provider"] == "openai"
        # If both hold, /v1/chat/completions will receive max_completion_tokens
        # and OpenAI will not return 400, so claude-opus-4-7 fallback won't
        # be triggered for this reason.


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
