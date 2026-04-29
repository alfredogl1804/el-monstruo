"""Manus M2M Bridge — Machine-to-Machine task delegation via Manus API v1.

Allows El Monstruo to delegate complex tasks (browser research, code execution,
multi-step workflows) to Manus agents via their REST API.

ENV VARS (set in Railway):
    MANUS_API_KEY_GOOGLE  — API key for Google-linked Manus account
    MANUS_API_KEY_APPLE   — API key for Apple-linked Manus account

Usage:
    from tools.manus_bridge import create_task, get_task_status, wait_for_completion

    task = create_task("Research the top 5 AI frameworks in 2026", account="google")
    result = wait_for_completion(task["task_id"], timeout=300)
"""

from __future__ import annotations

import os
import time
import logging
from typing import Any, Literal, Optional

import httpx

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MANUS_BASE_URL = "https://api.manus.im/v1"

_API_KEYS: dict[str, str] = {
    "google": "MANUS_API_KEY_GOOGLE",
    "apple": "MANUS_API_KEY_APPLE",
}

logger = logging.getLogger("monstruo.manus_bridge")

AccountType = Literal["google", "apple"]


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
# Public API
# ---------------------------------------------------------------------------


def create_task(
    prompt: str,
    account: AccountType = "google",
    project_id: Optional[str] = None,
    timeout: float = 30.0,
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

    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            f"{MANUS_BASE_URL}/tasks",
            headers=_headers(account),
            json=payload,
        )
        resp.raise_for_status()

    data = resp.json()
    logger.info("Manus task created: %s (status=%s)", data.get("task_id"), data.get("status"))
    return data


def get_task_status(
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

    with httpx.Client(timeout=timeout) as client:
        resp = client.get(
            f"{MANUS_BASE_URL}/tasks/{task_id}",
            headers=_headers(account),
        )
        resp.raise_for_status()

    return resp.json()


def wait_for_completion(
    task_id: str,
    account: AccountType = "google",
    timeout: float = 600.0,
    poll_interval: float = 5.0,
) -> dict[str, Any]:
    """Block until a Manus task reaches a terminal state or times out.

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
    terminal_states = {"completed", "failed", "cancelled"}
    start = time.monotonic()

    logger.info("Waiting for Manus task %s (timeout=%ss)", task_id, timeout)

    while True:
        elapsed = time.monotonic() - start
        if elapsed >= timeout:
            raise TimeoutError(
                f"Manus task {task_id} did not complete within {timeout}s. "
                f"Last poll at {elapsed:.1f}s."
            )

        status = get_task_status(task_id, account=account)
        current = status.get("status", "unknown")

        logger.debug("Task %s status: %s (%.1fs elapsed)", task_id, current, elapsed)

        if current in terminal_states:
            logger.info(
                "Manus task %s finished: %s (%.1fs)", task_id, current, elapsed
            )
            return status

        time.sleep(poll_interval)


# ---------------------------------------------------------------------------
# CLI quick-test
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

    task_resp = create_task(_prompt, account=_account)
    print(json.dumps(task_resp, indent=2))

    if task_resp.get("task_id"):
        result = wait_for_completion(task_resp["task_id"], account=_account, timeout=300)
        print(json.dumps(result, indent=2))
