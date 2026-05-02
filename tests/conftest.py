"""
Shared pytest fixtures and configuration.
Fixes event loop contamination between test files that mix
sync asyncio.new_event_loop().run_until_complete() with pytest-asyncio.
"""

from __future__ import annotations

import asyncio

import pytest


@pytest.fixture(autouse=True)
def _reset_event_loop_policy():
    """Reset the asyncio event loop policy after each test to prevent contamination."""
    yield
    asyncio.set_event_loop_policy(None)
