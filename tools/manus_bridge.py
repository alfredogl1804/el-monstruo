"""Manus M2M Bridge v2 — Machine-to-Machine task delegation via Manus API.

Allows El Monstruo to delegate complex tasks (browser research, code execution,
multi-step workflows) to Manus agents via their REST API.

ENV VARS (set in Railway):
    MANUS_API_KEY_GOOGLE  — API key for Google-linked Manus account
    MANUS_API_KEY_APPLE   — API key for Apple-linked Manus account

Usage:
    from tools.manus_bridge import create_task, get_task_status, wait_for_completion

    task = create_task("Research the top 5 AI frameworks in 2026")
    result = wait_for_completion(task["task_id"], timeout=300)
    print(result["output"])
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

TERMINAL_STATUSES = frozenset({"completed", "failed", "cancelled", "error"})
DEFAULT_POLL_INTERVAL = 5.0   # seconds between status checks
DEFAULT_TIMEOUT = 300.0       # max wait time in seconds
MAX_RETRIES = 3

logger = logging.getLogger("monstruo.manus_bridge")

AccountType = Literal["google", "apple"]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ManusBridgeError(Exception):
    """Base exception for Manus Bridge errors."""


class ManusTimeoutError(ManusBridgeError):
    """Raised when wait_for_completion exceeds timeout."""


class ManusTaskFailedError(ManusBridgeError):
    """Raised when a Manus task ends in failed/error status."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_api_key(account: AccountType) -> str:
    """Resolve the API key from environment variables."""
    env_var = _API_KEYS.get(account)
    if env_var is None:
        raise ValueError(
            f"Unknown account type: {account!r}. Use 'google' or 'apple'."
        )
    key = os.environ.get(env_var)
    if not key:
        raise EnvironmentError(
            f"Environment variable {env_var} is not set. "
            f"Configure it in Railway before using account={account!r}."
        )
    return key


def _headers(account: AccountType) -> dict[str, str]:
    """Build request headers with auth token."""
    return {
        "Authorization": f"Bearer {_get_api_key(account)}",
        "Content-Type": "application/json",
    }


def _request_with_retry(
    method: str,
    url: str,
    account: AccountType,
    json_payload: Optional[dict[str, Any]] = None,
    timeout: float = 30.0,
    retries: int = MAX_RETRIES,
) -> dict[str, Any]:
    """Execute an HTTP request with exponential backoff retry."""
    last_error: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                if method.upper() == "POST":
                    resp = client.post(
                        url, headers=_headers(account), json=json_payload
                    )
                else:
                    resp = client.get(url, headers=_headers(account))
                resp.raise_for_status()
                return resp.json()
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            last_error = exc
            if attempt < retries:
                wait = 2 ** attempt
                logger.warning(
                    "Manus API %s %s attempt %d/%d failed: %s — retrying in %ds",
                    method, url, attempt, retries, exc, wait,
                )
                time.sleep(wait)
            else:
                logger.error(
                    "Manus API %s %s failed after %d attempts: %s",
                    method, url, retries, exc,
                )

    raise ManusBridgeError(
        f"Manus API request failed after {retries} attempts: {last_error}"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_task(
    prompt: str,
    *,
    account: AccountType = "google",
    project_id: Optional[str] = None,
) -> dict[str, Any]:
    """Create a new task on Manus.

    Args:
        prompt: The instruction/prompt for the Manus agent.
        account: Which Manus account to use ('google' or 'apple').
        project_id: Optional Manus project ID to associate the task with.

    Returns:
        dict with at least {"task_id": str, "status": str}.

    Raises:
        ManusBridgeError: If the API call fails after retries.
        EnvironmentError: If the API key env var is missing.
    """
    payload: dict[str, Any] = {"prompt": prompt}
    if project_id:
        payload["project_id"] = project_id

    logger.info("Creating Manus task (account=%s): %.120s...", account, prompt)

    result = _request_with_retry(
        "POST",
        f"{MANUS_BASE_URL}/tasks",
        account=account,
        json_payload=payload,
    )

    logger.info(
        "Manus task created: id=%s status=%s",
        result.get("task_id", "?"),
        result.get("status", "?"),
    )
    return result


def get_task_status(
    task_id: str,
    *,
    account: AccountType = "google",
) -> dict[str, Any]:
    """Get the current status of a Manus task.

    Args:
        task_id: The Manus task ID.
        account: Which Manus account to use.

    Returns:
        dict with {"task_id", "status", "output", ...}.

    Raises:
        ManusBridgeError: If the API call fails after retries.
    """
    return _request_with_retry(
        "GET",
        f"{MANUS_BASE_URL}/tasks/{task_id}",
        account=account,
    )


def wait_for_completion(
    task_id: str,
    *,
    account: AccountType = "google",
    timeout: float = DEFAULT_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
) -> dict[str, Any]:
    """Poll a Manus task until it reaches a terminal status.

    Args:
        task_id: The Manus task ID to monitor.
        account: Which Manus account to use.
        timeout: Max seconds to wait before raising ManusTimeoutError.
        poll_interval: Seconds between status polls.

    Returns:
        Final task dict with {"task_id", "status", "output", ...}.

    Raises:
        ManusTimeoutError: If timeout is exceeded.
        ManusTaskFailedError: If the task ends in failed/error/cancelled.
        ManusBridgeError: If a status poll fails after retries.
    """
    logger.info(
        "Waiting for Manus task %s (timeout=%ds, poll=%ds)",
        task_id, timeout, poll_interval,
    )
    deadline = time.monotonic() + timeout

    while True:
        status_data = get_task_status(task_id, account=account)
        current_status = status_data.get("status", "unknown")

        logger.debug("Task %s status: %s", task_id, current_status)

        if current_status in TERMINAL_STATUSES:
            if current_status == "completed":
                logger.info("Manus task %s completed successfully.", task_id)
                return status_data
            raise ManusTaskFailedError(
                f"Manus task {task_id} ended with status: {current_status}. "
                f"Output: {status_data.get('output', 'N/A')}"
            )

        if time.monotonic() >= deadline:
            raise ManusTimeoutError(
                f"Manus task {task_id} did not complete within {timeout}s. "
                f"Last status: {current_status}"
            )

        time.sleep(poll_interval)


# ---------------------------------------------------------------------------
# Convenience: create + wait in one call
# ---------------------------------------------------------------------------


def create_and_wait(
    prompt: str,
    *,
    account: AccountType = "google",
    project_id: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
) -> dict[str, Any]:
    """Create a Manus task and wait for its completion.

    Combines create_task + wait_for_completion for simple use cases.

    Args:
        prompt: The instruction for the Manus agent.
        account: Which Manus account to use.
        project_id: Optional Manus project ID.
        timeout: Max seconds to wait.
        poll_interval: Seconds between polls.

    Returns:
        Final task dict with output.

    Raises:
        ManusTimeoutError: If timeout exceeded.
        ManusTaskFailedError: If task fails.
        ManusBridgeError: If API calls fail.
    """
    task = create_task(prompt, account=account, project_id=project_id)
    task_id = task.get("task_id")
    if not task_id:
        raise ManusBridgeError(
            f"Manus create_task did not return a task_id. Response: {task}"
        )
    return wait_for_completion(
        task_id,
        account=account,
        timeout=timeout,
        poll_interval=poll_interval,
    )


# ---------------------------------------------------------------------------
# CLI quick-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    prompt_text = " ".join(sys.argv[1:]) or "Hello Manus — ping test from El Monstruo."
    print(f"Sending prompt: {prompt_text}")
    result = create_and_wait(prompt_text, timeout=120)
    print(f"Result: {result}")
