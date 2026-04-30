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
RATE_LIMIT_PER_HOUR = 5

logger = logging.getLogger("monstruo.manus_bridge")

AccountType = Literal["google", "apple"]

# Simple in-memory rate limiter
_call_timestamps: list[float] = []


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ManusBridgeError(Exception):
    """Base exception for Manus Bridge errors."""


class ManusTimeoutError(ManusBridgeError):
    """Raised when wait_for_completion exceeds timeout."""


class ManusTaskFailedError(ManusBridgeError):
    """Raised when a Manus task ends in failed/error status."""


class ManusRateLimitError(ManusBridgeError):
    """Raised when rate limit (5 calls/hour) is exceeded."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _check_rate_limit() -> None:
    """Enforce max 5 create_task calls per hour."""
    now = time.time()
    cutoff = now - 3600.0
    # Prune old timestamps
    _call_timestamps[:] = [t for t in _call_timestamps if t > cutoff]
    if len(_call_timestamps) >= RATE_LIMIT_PER_HOUR:
        oldest = _call_timestamps[0]
        wait_seconds = int(3600 - (now - oldest)) + 1
        raise ManusRateLimitError(
            f"Rate limit reached ({RATE_LIMIT_PER_HOUR}/hour). "
            f"Try again in {wait_seconds}s."
        )
    _call_timestamps.append(now)


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
            wait = 2 ** attempt
            logger.warning(
                "Manus API %s %s attempt %d/%d failed: %s — retrying in %ds",
                method.upper(), url, attempt, retries, exc, wait,
            )
            if attempt < retries:
                time.sleep(wait)

    raise ManusBridgeError(
        f"Manus API request failed after {retries} attempts: {last_error}"
    ) from last_error


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_task(
    prompt: str,
    *,
    account: AccountType = "google",
    project_id: Optional[str] = None,
) -> dict[str, Any]:
    """Create a new Manus task.

    Args:
        prompt: The instruction/prompt for the Manus agent.
        account: Which Manus account to use ('google' or 'apple').
        project_id: Optional Manus project ID to associate the task with.

    Returns:
        dict with at least: {"task_id": str, "status": str}

    Raises:
        ManusRateLimitError: If 5 calls/hour limit is exceeded.
        ManusBridgeError: On API failure after retries.
    """
    _check_rate_limit()

    payload: dict[str, Any] = {"prompt": prompt}
    if project_id:
        payload["project_id"] = project_id

    logger.info(
        "Creating Manus task (account=%s): %.80s...", account, prompt
    )

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
    """Check the status of a Manus task.

    Args:
        task_id: The Manus task ID.
        account: Which Manus account to use.

    Returns:
        dict with at least: {"task_id": str, "status": str, "output": ...}
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
        task_id: The Manus task ID.
        account: Which Manus account to use.
        timeout: Max seconds to wait before raising ManusTimeoutError.
        poll_interval: Seconds between status checks.

    Returns:
        Final task dict with output.

    Raises:
        ManusTimeoutError: If timeout is exceeded.
        ManusTaskFailedError: If task ends in failed/error/cancelled.
    """
    start = time.time()
    logger.info("Waiting for Manus task %s (timeout=%ds)...", task_id, timeout)

    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            raise ManusTimeoutError(
                f"Task {task_id} did not complete within {timeout}s "
                f"(last poll at {elapsed:.0f}s)."
            )

        result = get_task_status(task_id, account=account)
        status = result.get("status", "unknown")

        logger.debug(
            "Task %s status=%s (%.0fs elapsed)", task_id, status, elapsed
        )

        if status in TERMINAL_STATUSES:
            if status == "completed":
                logger.info(
                    "Task %s completed in %.0fs.", task_id, elapsed
                )
                return result
            raise ManusTaskFailedError(
                f"Task {task_id} ended with status={status!r}. "
                f"Output: {result.get('output', 'N/A')}"
            )

        time.sleep(poll_interval)


# ---------------------------------------------------------------------------
# Handler for El Monstruo tool system
# ---------------------------------------------------------------------------


def handle_manus_bridge(params: dict[str, Any]) -> dict[str, Any]:
    """Entry point called by El Monstruo's tool dispatcher.

    Params:
        action: 'create_task' | 'get_status' | 'create_and_wait'
        prompt: str (required for create_task / create_and_wait)
        task_id: str (required for get_status)
        account: 'google' | 'apple' (default: 'google')
        project_id: optional str
        timeout: optional float (default 300)

    Returns:
        dict with task info or error.
    """
    action = params.get("action", "create_task")
    account: AccountType = params.get("account", "google")  # type: ignore[assignment]
    prompt = params.get("prompt", "")
    task_id = params.get("task_id", "")
    project_id = params.get("project_id")
    timeout = float(params.get("timeout", DEFAULT_TIMEOUT))

    try:
        if action == "create_task":
            if not prompt:
                return {"error": "Missing 'prompt' parameter for create_task."}
            return create_task(
                prompt, account=account, project_id=project_id
            )

        elif action == "get_status":
            if not task_id:
                return {"error": "Missing 'task_id' parameter for get_status."}
            return get_task_status(task_id, account=account)

        elif action == "create_and_wait":
            if not prompt:
                return {"error": "Missing 'prompt' parameter for create_and_wait."}
            task = create_task(
                prompt, account=account, project_id=project_id
            )
            tid = task.get("task_id", "")
            if not tid:
                return {"error": "create_task did not return a task_id.", "raw": task}
            return wait_for_completion(
                tid, account=account, timeout=timeout
            )

        else:
            return {"error": f"Unknown action: {action!r}. Use: create_task, get_status, create_and_wait."}

    except ManusRateLimitError as exc:
        logger.warning("Rate limit hit: %s", exc)
        return {"error": str(exc), "type": "rate_limit"}
    except ManusTimeoutError as exc:
        logger.warning("Timeout: %s", exc)
        return {"error": str(exc), "type": "timeout"}
    except ManusTaskFailedError as exc:
        logger.error("Task failed: %s", exc)
        return {"error": str(exc), "type": "task_failed"}
    except ManusBridgeError as exc:
        logger.error("Bridge error: %s", exc)
        return {"error": str(exc), "type": "bridge_error"}
    except Exception as exc:
        logger.exception("Unexpected error in manus_bridge")
        return {"error": f"Unexpected error: {exc}", "type": "unexpected"}
