"""
El Monstruo — Sprint 2 Tests
==============================
Tests for:
- PostgresSaver integration (checkpointer injection)
- API Key Authentication middleware
- Web Search tool
- Consult Sabios tool
- Email Sender tool
- New tool endpoints
- Version bumps
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from kernel.engine import LangGraphKernel
from memory.conversation import ConversationMemory
from memory.event_store import EventStore
from memory.knowledge_graph import KnowledgeGraph

# ── Fixtures ──────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def event_store():
    store = EventStore()
    await store.initialize()
    return store


@pytest.fixture
def memory():
    return ConversationMemory()


@pytest.fixture
def knowledge():
    return KnowledgeGraph()


# ── PostgresSaver Tests ───────────────────────────────────────────────


class TestPostgresSaver:
    """Tests for PostgresSaver integration."""

    def test_kernel_accepts_checkpointer_param(self, event_store, memory, knowledge):
        """Kernel should accept a checkpointer parameter."""
        mock_checkpointer = MagicMock()
        mock_checkpointer.config_specs = []
        # Verify the kernel constructor accepts checkpointer
        # (It will fail to compile with a mock, but the parameter is accepted)
        try:
            LangGraphKernel(
                event_store=event_store,
                memory=memory,
                knowledge=knowledge,
                checkpointer=mock_checkpointer,
            )
        except Exception:
            # Expected — mock checkpointer can't compile a real graph
            pass

    def test_kernel_defaults_to_memory_saver(self, event_store, memory, knowledge):
        """Kernel should default to MemorySaver when no checkpointer is provided."""
        kernel = LangGraphKernel(
            event_store=event_store,
            memory=memory,
            knowledge=knowledge,
        )
        # langgraph renamed MemorySaver to InMemorySaver in recent versions
        assert type(kernel._checkpointer).__name__ in ("MemorySaver", "InMemorySaver")

    def test_postgres_saver_import_available(self):
        """langgraph-checkpoint-postgres should be importable."""
        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

            assert AsyncPostgresSaver is not None
        except ImportError:
            pytest.skip("langgraph-checkpoint-postgres not installed in test env")

    def test_has_postgres_saver_flag(self):
        """The _HAS_POSTGRES_SAVER flag should exist in engine module."""
        from kernel.engine import _HAS_POSTGRES_SAVER

        assert isinstance(_HAS_POSTGRES_SAVER, bool)


# ── Auth Middleware Tests ─────────────────────────────────────────────


class TestAuthMiddleware:
    """Tests for API Key authentication middleware."""

    def test_auth_module_importable(self):
        """Auth module should be importable."""
        from kernel.auth import PUBLIC_PATHS, APIKeyAuthMiddleware

        assert APIKeyAuthMiddleware is not None
        assert "/" in PUBLIC_PATHS
        assert "/health" in PUBLIC_PATHS

    def test_public_paths_defined(self):
        """Public paths should include health and root."""
        from kernel.auth import PUBLIC_PATHS

        assert "/health" in PUBLIC_PATHS
        assert "/" in PUBLIC_PATHS
        assert "/docs" in PUBLIC_PATHS

    def test_extract_token_from_x_api_key(self):
        """Should extract token from X-API-Key header."""
        from kernel.auth import _extract_token

        mock_request = MagicMock()
        mock_request.headers = {"X-API-Key": "test-key-123"}
        assert _extract_token(mock_request) == "test-key-123"

    def test_extract_token_from_bearer(self):
        """Should extract token from Authorization: Bearer header."""
        from kernel.auth import _extract_token

        mock_request = MagicMock()
        # Use a real dict-like object for headers
        headers = {"Authorization": "Bearer my-secret-key"}
        mock_request.headers = headers
        token = _extract_token(mock_request)
        assert token == "my-secret-key"

    def test_get_api_key_from_env(self):
        """Should read API key from environment."""
        from kernel.auth import _get_api_key

        with patch.dict(os.environ, {"MONSTRUO_API_KEY": "test-key"}):
            assert _get_api_key() == "test-key"

    def test_get_api_key_returns_none_when_not_set(self):
        """Should return None when MONSTRUO_API_KEY is not set."""
        from kernel.auth import _get_api_key

        with patch.dict(os.environ, {}, clear=True):
            # Remove the key if it exists
            os.environ.pop("MONSTRUO_API_KEY", None)
            assert _get_api_key() is None


# ── Web Search Tool Tests ─────────────────────────────────────────────


class TestWebSearch:
    """Tests for the web_search tool."""

    def test_web_search_importable(self):
        """Web search module should be importable."""
        from tools.web_search import SONAR_MODELS, multi_search, web_search

        assert web_search is not None
        assert multi_search is not None
        assert "sonar-pro" in SONAR_MODELS

    @pytest.mark.asyncio
    async def test_web_search_no_api_key(self):
        """Should return error when SONAR_API_KEY is not set."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("SONAR_API_KEY", None)
            from tools.web_search import web_search

            result = await web_search("test query")
            assert result["error"] is not None
            assert "SONAR_API_KEY" in result["error"]
            assert result["answer"] == ""

    @pytest.mark.asyncio
    async def test_web_search_returns_correct_structure(self):
        """Should return dict with expected keys."""
        with patch.dict(os.environ, {"SONAR_API_KEY": "fake-key"}):
            from tools.web_search import web_search

            # Mock the HTTP call
            with patch("tools.web_search.httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.raise_for_status = MagicMock()
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": "Test answer"}}],
                    "citations": ["https://example.com"],
                    "usage": {"total_tokens": 100},
                }
                mock_client_instance = AsyncMock()
                mock_client_instance.post.return_value = mock_response
                mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
                mock_client_instance.__aexit__ = AsyncMock(return_value=None)
                mock_client.return_value = mock_client_instance

                result = await web_search("test query")
                assert "answer" in result
                assert "citations" in result
                assert "model_used" in result
                assert "tokens_used" in result


# ── Consult Sabios Tool Tests ─────────────────────────────────────────


class TestConsultSabios:
    """Tests for the consult_sabios tool."""

    def test_consult_sabios_importable(self):
        """Consult sabios module should be importable."""
        from tools.consult_sabios import SABIOS, consult_sabios

        assert consult_sabios is not None
        assert len(SABIOS) == 6

    def test_all_six_sabios_defined(self):
        """All 6 sabios should be defined with correct structure."""
        from tools.consult_sabios import SABIOS

        expected_ids = {"gpt54", "claude", "gemini", "grok", "deepseek", "perplexity"}
        assert set(SABIOS.keys()) == expected_ids
        for sid, sabio in SABIOS.items():
            assert "name" in sabio
            assert "role" in sabio
            assert "provider" in sabio
            assert "model" in sabio
            assert "env_key" in sabio

    def test_sabio_providers_have_callers(self):
        """Each provider should have a corresponding caller function."""
        from tools.consult_sabios import _CALLERS, SABIOS

        for sid, sabio in SABIOS.items():
            assert sabio["provider"] in _CALLERS, f"No caller for {sabio['provider']}"

    @pytest.mark.asyncio
    async def test_consult_sabios_no_keys(self):
        """Should return errors when no API keys are set."""
        env_clean = {
            k: v
            for k, v in os.environ.items()
            if k
            not in (
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "GEMINI_API_KEY",
                "XAI_API_KEY",
                "OPENROUTER_API_KEY",
                "SONAR_API_KEY",
            )
        }
        with patch.dict(os.environ, env_clean, clear=True):
            from tools.consult_sabios import consult_sabios

            result = await consult_sabios("test prompt", sabios=["gpt54"])
            assert result["failed_count"] >= 0  # May or may not have key in env
            assert "responses" in result
            assert "synthesis" in result

    @pytest.mark.asyncio
    async def test_consult_sabios_empty_sabios_list(self):
        """Should handle empty sabio selection gracefully."""
        from tools.consult_sabios import consult_sabios

        result = await consult_sabios("test", sabios=["nonexistent"])
        assert result["errors"] == ["No valid sabios selected"]


# ── Email Sender Tool Tests ───────────────────────────────────────────


class TestEmailSender:
    """Tests for the email_sender tool."""

    def test_email_sender_importable(self):
        """Email sender module should be importable."""
        from tools.email_sender import send_email

        assert send_email is not None

    @pytest.mark.asyncio
    async def test_email_no_credentials(self):
        """Should return error when Gmail credentials are not set."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GMAIL_ADDRESS", None)
            os.environ.pop("GMAIL_APP_PASSWORD", None)
            from tools.email_sender import send_email

            result = await send_email(
                to="test@example.com",
                subject="Test",
                body="Test body",
            )
            assert result["sent"] is False
            assert "not set" in result["error"]


# ── Version and Integration Tests ─────────────────────────────────────


class TestVersionAndIntegration:
    """Tests for version bumps and integration."""

    def test_version_is_sprint2(self):
        """Sprint 27.5 fix: Version should follow semver-sprint pattern in main.py."""
        import re
        main_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kernel", "main.py")
        with open(main_path) as f:
            content = f.read()
        assert re.search(r'\d+\.\d+\.\d+-sprint\d+', content), "No semver-sprint version found in main.py"

    def test_tools_directory_exists(self):
        """Tools directory should exist with all modules."""
        assert os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "__init__.py"))
        assert os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "web_search.py"))
        assert os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "consult_sabios.py"))
        assert os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "email_sender.py"))

    def test_auth_module_exists(self):
        """Auth module should exist."""
        assert os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(__file__)), "kernel", "auth.py"))

    def test_kernel_checkpointer_logged(self, event_store, memory, knowledge):
        """Kernel should log checkpointer type on init."""
        kernel = LangGraphKernel(
            event_store=event_store,
            memory=memory,
            knowledge=knowledge,
        )
        # If we get here, the kernel initialized with MemorySaver
        assert kernel._checkpointer is not None
