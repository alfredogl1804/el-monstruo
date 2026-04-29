"""Manus M2M Bridge — Async Machine-to-Machine task delegation via Manus API v1.

Allows El Monstruo to delegate complex tasks (browser research, code execution,
multi-step workflows) to Manus agents via their REST API.

Sprint 34 rewrite:
  - Fully async (httpx.AsyncClient) — no sync blocking in event loop
  - Registered in tool_dispatch.py as a first-class tool
  - Rate-limited to 5 calls/hour via ToolBroker
  - Follows repo patterns from tools/browser.py and tools/webhook.py

ENV VARS (set in Railway):
    MANUS_API_KEY_GOOGLE  — API key for Google-linked Manus account
    MANUS_API_KEY_APPLE   — API key for Apple-linked Manus account

Usage:
    from tools.manus_bridge import create_task, get_task_status, wait_for_completion

    task = await create_task("Research the top 5 AI frameworks in 2026", account="google")
    result = await wait_for_completion(task["task_id"], timeout=300)
"""

from __future__ import annotations

import asyncio
import os
import logging
from typing import Any, Literal, Optional

import httpx

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MANUS_BASE_URL = "https://api.manus.im/v1"
DEFAULT_TIMEOUT = 30.0
POLL_INTERVAL = 5.0
MAX_WAIT_TIMEOUT = 600.0

_API_KEYS: dict[str, str] = {
    "google": "MANUS_API_KEY_GOOGLE",
    "apple": "MANUS_API_KEY_APPLE",
}

logger = logging.getLogger("monstruo.manus_bridge")

AccountType = Literal["google", "apple"]

TERMINAL_STATES = {"completed", "failed", "cancelled"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_api_key(account: AccountType) -> str:
    """Resolve the API key from environment variables."""
    env_var = _API_KEYS.get(account)
    if env_var is None:
        raise ValueError(f"Unknown account type: {account!r}. Use 'google' or 'apple'.")
    key = os.environ.get(env_var)
    if not key:
        raise EnvironmentError(
            f"Environment variable {env_var} is not set. "
            f"Configure it in Railway before using account={account!r}."
        )
    return key


def _headers(account: AccountType) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_api_key(account)}",
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Public API (fully async)
# ---------------------------------------------------------------------------


async def create_task(
    prompt: str,
    account: AccountType = "google",
    project_id: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Create a new Manus task.

    Args:
        prompt: The instruction / prompt for the Manus agent.
        account: Which Manus account to use ('google' or 'apple').
        project_id: Optional Manus project ID to group tasks.
        timeout: HTTP request timeout in seconds.

    Returns:
        dict with at least {"task_id": str, "status": str}.

    Raises:
        httpx.HTTPStatusError: On non-2xx responses.
        EnvironmentError: If the API key env var is missing.
    """
    payload: dict[str, Any] = {"prompt": prompt}
    if project_id:
        payload["project_id"] = project_id

    logger.info("Creating Manus task (account=%s): %.120s...", account, prompt)

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{MANUS_BASE_URL}/tasks",
            headers=_headers(account),
            json=payload,
        )
        resp.raise_for_status()

    data = resp.json()
    logger.info("Manus task created: %s (status=%s)", data.get("task_id"), data.get("status"))
    return data


async def get_task_status(
    task_id: str,
    account: AccountType = "google",
    timeout: float = 15.0,
) -> dict[str, Any]:
    """Poll the status of an existing Manus task.

    Args:
        task_id: The Manus task ID returned by create_task().
        account: Which Manus account to authenticate with.
        timeout: HTTP request timeout in seconds.

    Returns:
        dict with {"task_id": str, "status": str, "output": str | None, ...}.
    """
    logger.debug("Polling Manus task %s", task_id)

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(
            f"{MANUS_BASE_URL}/tasks/{task_id}",
            headers=_headers(account),
        )
        resp.raise_for_status()

    return resp.json()


async def wait_for_completion(
    task_id: str,
    account: AccountType = "google",
    timeout: float = MAX_WAIT_TIMEOUT,
    poll_interval: float = POLL_INTERVAL,
) -> dict[str, Any]:
    """Async wait until a Manus task reaches a terminal state or times out.

    Terminal states: 'completed', 'failed', 'cancelled'.

    Args:
        task_id: The Manus task ID.
        account: Which Manus account to authenticate with.
        timeout: Max seconds to wait before raising TimeoutError.
        poll_interval: Seconds between status polls.

    Returns:
        Final task status dict.

    Raises:
        TimeoutError: If the task doesn't finish within `timeout` seconds.
    """
    import time

    start = time.monotonic()

    logger.info("Waiting for Manus task %s (timeout=%ss)", task_id, timeout)

    while True:
        elapsed = time.monotonic() - start
        if elapsed >= timeout:
            raise TimeoutError(
                f"Manus task {task_id} did not complete within {timeout}s. "
                f"Last poll at {elapsed:.1f}s."
            )

        status = await get_task_status(task_id, account=account)
        current = status.get("status", "unknown")

        logger.debug("Task %s status: %s (%.1fs elapsed)", task_id, current, elapsed)

        if current in TERMINAL_STATES:
            logger.info(
                "Manus task %s finished: %s (%.1fs)", task_id, current, elapsed
            )
            return status

        # Non-blocking sleep — does NOT block the event loop
        await asyncio.sleep(poll_interval)


# ---------------------------------------------------------------------------
# Tool dispatch entry point
# ---------------------------------------------------------------------------


async def execute_manus_bridge(
    action: str,
    prompt: str = "",
    task_id: str = "",
    account: str = "google",
    project_id: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
    wait_timeout: float = MAX_WAIT_TIMEOUT,
) -> dict[str, Any]:
    """Unified entry point for tool_dispatch.py.

    Actions:
        create_task: Create a new Manus task (requires prompt).
        get_status:  Check status of an existing task (requires task_id).
        create_and_wait: Create a task and wait for completion (requires prompt).

    Returns:
        dict with result or error.
    """
    try:
        acct: AccountType = account if account in ("google", "apple") else "google"

        if action == "create_task":
            if not prompt:
                return {"error": "prompt is required for create_task action"}
            return await create_task(prompt, account=acct, project_id=project_id, timeout=timeout)

        elif action == "get_status":
            if not task_id:
                return {"error": "task_id is required for get_status action"}
            return await get_task_status(task_id, account=acct, timeout=timeout)

        elif action == "create_and_wait":
            if not prompt:
                return {"error": "prompt is required for create_and_wait action"}
            task = await create_task(prompt, account=acct, project_id=project_id, timeout=timeout)
            tid = task.get("task_id")
            if not tid:
                return {"error": "create_task did not return a task_id", "raw": task}
            result = await wait_for_completion(tid, account=acct, timeout=wait_timeout)
            return result

        else:
            return {"error": f"Unknown action: {action!r}. Use: create_task, get_status, create_and_wait"}

    except httpx.HTTPStatusError as e:
        logger.error("Manus API HTTP error: %s", e)
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:500]}"}
    except EnvironmentError as e:
        logger.error("Manus bridge env error: %s", e)
        return {"error": str(e)}
    except TimeoutError as e:
        logger.error("Manus bridge timeout: %s", e)
        return {"error": str(e)}
    except Exception as e:
        logger.error("Manus bridge unexpected error: %s", e)
        return {"error": f"Unexpected: {str(e)}"}


# ---------------------------------------------------------------------------
# CLI quick-test (async)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

    if len(sys.argv) < 2:
        print("Usage: python -m tools.manus_bridge 'Your prompt here' [google|apple]")
        sys.exit(1)

    _prompt = sys.argv[1]
    _account: AccountType = sys.argv[2] if len(sys.argv) > 2 else "google"  # type: ignore[assignment]

    async def _main():
        task_resp = await create_task(_prompt, account=_account)
        print(json.dumps(task_resp, indent=2))

        if task_resp.get("task_id"):
            result = await wait_for_completion(task_resp["task_id"], account=_account, timeout=300)
            print(json.dumps(result, indent=2))

    asyncio.run(_main())
