"""
T4 — Unit tests for tools/github.py::list_prs instrumentation
==============================================================
Sprint: list-prs-instrumentation-2026-05-27
Spec: bridge/cowork_to_e1_LIST_PRS_FIX_SPEC_2026_05_27.md

Coverage:
- Scenario 1 (Happy path): GitHub returns a list of PRs → returns pull_requests
  with correct structure and emits 3 structured logs.
- Scenario 2 (API error): _request returns an error dict → returns empty list
  with error + note fields surfaced.
- Scenario 3 (Invalid repo format): repo without "/" → returns empty list with
  format error message without calling GitHub API.
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from tools.github import list_prs


# ── Fixtures ──────────────────────────────────────────────────────


MOCK_PR_LIST = [
    {
        "number": 42,
        "title": "feat: add memory layer",
        "state": "open",
        "head": {"ref": "feat/memory-layer"},
        "base": {"ref": "main"},
        "html_url": "https://github.com/alfredogl1804/el-monstruo/pull/42",
    },
    {
        "number": 43,
        "title": "fix: ghost gate regex",
        "state": "open",
        "head": {"ref": "fix/ghost-gate"},
        "base": {"ref": "main"},
        "html_url": "https://github.com/alfredogl1804/el-monstruo/pull/43",
    },
]

MOCK_ERROR_RESPONSE = {
    "error": "GitHub API returned 401",
    "detail": "Bad credentials",
}


# ── Scenario 1: Happy path ───────────────────────────────────────


@pytest.mark.asyncio
async def test_list_prs_happy_path():
    """GitHub returns a valid list of PRs → structured response with correct fields."""
    with patch("tools.github._request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = MOCK_PR_LIST

        result = await list_prs("alfredogl1804/el-monstruo", state="open", limit=10)

    # Verify _request was called with correct path
    mock_req.assert_called_once_with(
        "GET", "/repos/alfredogl1804/el-monstruo/pulls?state=open&per_page=10"
    )

    # Verify response structure
    assert "pull_requests" in result
    assert len(result["pull_requests"]) == 2
    assert "error" not in result

    # Verify PR fields
    pr = result["pull_requests"][0]
    assert pr["number"] == 42
    assert pr["title"] == "feat: add memory layer"
    assert pr["state"] == "open"
    assert pr["head"] == "feat/memory-layer"
    assert pr["base"] == "main"
    assert pr["url"] == "https://github.com/alfredogl1804/el-monstruo/pull/42"


@pytest.mark.asyncio
async def test_list_prs_happy_path_logs(caplog):
    """Happy path emits 3 structured log events: called, raw_response, returning."""
    with patch("tools.github._request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = MOCK_PR_LIST

        import logging

        with caplog.at_level(logging.INFO, logger="monstruo.tools.github"):
            await list_prs("alfredogl1804/el-monstruo")

    log_messages = [r.message for r in caplog.records]
    assert "list_prs_called" in log_messages
    assert "list_prs_raw_response" in log_messages
    assert "list_prs_returning" in log_messages


# ── Scenario 2: API error surfaced ───────────────────────────────


@pytest.mark.asyncio
async def test_list_prs_api_error_surfaced():
    """When _request returns an error dict, list_prs surfaces it with note field."""
    with patch("tools.github._request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = MOCK_ERROR_RESPONSE

        result = await list_prs("alfredogl1804/el-monstruo")

    # Must return empty list (not omit the key)
    assert result["pull_requests"] == []

    # Must surface the error
    assert result["error"] == "GitHub API returned 401"
    assert result["detail"] == "Bad credentials"

    # Must include the note so LLM doesn't hallucinate "no PRs"
    assert "note" in result
    assert "NOT a confirmation" in result["note"]


# ── Scenario 3: Invalid repo format ──────────────────────────────


@pytest.mark.asyncio
async def test_list_prs_invalid_repo_format_no_slash():
    """Repo without '/' → returns error without calling GitHub API."""
    with patch("tools.github._request", new_callable=AsyncMock) as mock_req:
        result = await list_prs("el-monstruo")

    # _request must NOT be called
    mock_req.assert_not_called()

    # Must return empty list with error
    assert result["pull_requests"] == []
    assert "error" in result
    assert "owner/repo" in result["error"]
    assert "note" in result
    assert "NOT a confirmation" in result["note"]


@pytest.mark.asyncio
async def test_list_prs_invalid_repo_format_multiple_slashes():
    """Repo with multiple '/' → returns error without calling GitHub API."""
    with patch("tools.github._request", new_callable=AsyncMock) as mock_req:
        result = await list_prs("alfredogl1804/el-monstruo/extra")

    mock_req.assert_not_called()
    assert result["pull_requests"] == []
    assert "error" in result


@pytest.mark.asyncio
async def test_list_prs_empty_repo():
    """Empty string repo → returns error without calling GitHub API."""
    with patch("tools.github._request", new_callable=AsyncMock) as mock_req:
        result = await list_prs("")

    mock_req.assert_not_called()
    assert result["pull_requests"] == []
    assert "error" in result
