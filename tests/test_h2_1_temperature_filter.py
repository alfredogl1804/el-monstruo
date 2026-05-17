"""
H2.1 — Temperature filter for GPT-5.x reasoning models.

Bug: router/llm_client.py always passed `temperature` even when the catalog
declared `supports_temperature=False`. OpenAI rejects with HTTP 400:

    Unsupported value: 'temperature' does not support 0.7 with this model.
    Only the default (1) value is supported.

Fix: respect `supports_temperature` flag from model_catalog when building
the request payload in:

  - _call_openai (SDK kwargs)
  - _stream_openai (SDK kwargs)
  - _call_openai_compatible (httpx payload, xai/openrouter)
  - _stream_openai_compatible (httpx payload, xai/openrouter)

Tests use AST inspection (no live network calls) to verify the source code
correctly conditions `temperature` on the catalog flag.
"""
from __future__ import annotations

import ast
import pathlib

REPO_ROOT = pathlib.Path(__file__).parent.parent
LLM_CLIENT_PATH = REPO_ROOT / "router" / "llm_client.py"
CATALOG_PATH = REPO_ROOT / "config" / "model_catalog.py"


def _source() -> str:
    return LLM_CLIENT_PATH.read_text()


def test_catalog_marks_gpt55_no_temperature():
    """gpt-5.5 must declare supports_temperature=False (post-Sprint 29)."""
    from config.model_catalog import MODELS

    assert "gpt-5.5" in MODELS
    assert MODELS["gpt-5.5"]["supports_temperature"] is False, (
        "gpt-5.5 must have supports_temperature=False — OpenAI rejects "
        "any non-default temperature with HTTP 400."
    )


def test_call_openai_respects_supports_temperature():
    """_call_openai must NOT include 'temperature' unconditionally."""
    src = _source()
    # Locate _call_openai body
    tree = ast.parse(src)
    func = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.AsyncFunctionDef) and n.name == "_call_openai"
    )
    body_src = ast.unparse(func)

    # The kwargs dict literal must NOT contain "temperature": temperature
    # as an unconditional entry — it must be inside an `if`.
    # We verify by checking that the function body contains a guarded assignment.
    # ast.unparse normalizes quotes to  accept both forms.single 
    assert (
        'kwargs["temperature"] = temperature' in body_src
        or "kwargs['temperature'] = temperature" in body_src
    ), (
        "_call_openai must add temperature inside an if-guard, "
        "not directly in the kwargs literal."
    )

    # And the unconditional literal pattern must be gone.
    bad_literal = '"temperature": temperature,\n        }'
    assert bad_literal not in src.split("def _call_openai")[1].split("def _call_anthropic")[0], (
        "_call_openai still contains unconditional 'temperature' in dict literal."
    )


def test_stream_openai_respects_supports_temperature():
    """_stream_openai must NOT include 'temperature' unconditionally."""
    src = _source()
    # Slice from _stream_openai to next def
    after = src.split("def _stream_openai(", 1)[1]
    body = after.split("\n    async def ", 1)[0]
    # The literal `"temperature": temperature,` must NOT appear inside the dict.
    assert '"temperature": temperature,' not in body, (
        "_stream_openai still has unconditional temperature in dict literal."
    )
    # But there must be a guarded assignment.
    assert 'kwargs["temperature"] = temperature' in body, (
        "_stream_openai must add temperature inside an if-guard."
    )


def test_call_openai_compatible_respects_supports_temperature():
    """_call_openai_compatible must NOT include 'temperature' unconditionally."""
    src = _source()
    after = src.split("def _call_openai_compatible(", 1)[1]
    body = after.split("\n    async def ", 1)[0]
    assert '"temperature": temperature,' not in body, (
        "_call_openai_compatible still has unconditional temperature."
    )
    assert 'payload["temperature"] = temperature' in body, (
        "_call_openai_compatible must add temperature inside an if-guard."
    )


def test_stream_openai_compatible_respects_supports_temperature():
    """_stream_openai_compatible must NOT include 'temperature' unconditionally."""
    src = _source()
    after = src.split("def _stream_openai_compatible(", 1)[1]
    body = after  # last function in file likely
    assert '"temperature": temperature,' not in body, (
        "_stream_openai_compatible still has unconditional temperature."
    )
    assert 'payload["temperature"] = temperature' in body, (
        "_stream_openai_compatible must add temperature inside an if-guard."
    )


def test_supports_temperature_default_true():
    """Models without explicit flag default to supports_temperature=True (backward compat)."""
    from config.model_catalog import supports_temperature

    # Unknown models should NOT fail, should return True (permissive default)
    assert supports_temperature("nonexistent-model") is True


def test_supports_temperature_false_for_gpt5():
    """gpt-5.5 returns False from helper."""
    from config.model_catalog import supports_temperature

    assert supports_temperature("gpt-5.5") is False
