"""
kernel/output_sanitizer.py — Real output sanitization for tool results.

Sprint 10c Fix 3: Strip dangerous content from tool outputs before
they are returned to the LLM context. Prevents prompt injection,
XSS payloads, and excessive data from polluting the conversation.

Anti-autoboicot: validated 2026-04-18
"""

from __future__ import annotations

import re

import structlog

logger = structlog.get_logger("kernel.output_sanitizer")

# ── Configuration ────────────────────────────────────────────────
MAX_OUTPUT_CHARS = 8_000  # Truncate tool outputs beyond this
MAX_ITEMS_IN_LIST = 50  # Cap list results
STRIP_HTML_TAGS = True  # Remove HTML/script tags from output

# ── Dangerous patterns ───────────────────────────────────────────
_SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_STYLE_RE = re.compile(r"<style[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+a", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"\[INST\]", re.IGNORECASE),
    re.compile(r"<<SYS>>", re.IGNORECASE),
]
_BASE64_DATA_RE = re.compile(r"data:[^;]+;base64,[A-Za-z0-9+/=]{100,}")
_LONG_URL_RE = re.compile(r"https?://[^\s]{500,}")


def sanitize_tool_output(output: str, *, tool_name: str = "") -> str:
    """
    Sanitize a tool output string before it enters the LLM context.

    Steps:
    1. Strip <script> and <style> blocks
    2. Strip remaining HTML tags (optional)
    3. Remove base64 data URIs (large, useless for LLM)
    4. Remove excessively long URLs
    5. Detect and defang prompt injection attempts
    6. Truncate to MAX_OUTPUT_CHARS

    Returns the sanitized string.
    """
    if not output:
        return output

    original_len = len(output)
    result = output

    # 1. Strip <script> and <style> blocks
    result = _SCRIPT_RE.sub("[SCRIPT_REMOVED]", result)
    result = _STYLE_RE.sub("[STYLE_REMOVED]", result)

    # 2. Strip HTML tags
    if STRIP_HTML_TAGS:
        result = _HTML_TAG_RE.sub("", result)

    # 3. Remove base64 data URIs
    result = _BASE64_DATA_RE.sub("[BASE64_DATA_REMOVED]", result)

    # 4. Remove excessively long URLs
    result = _LONG_URL_RE.sub("[LONG_URL_REMOVED]", result)

    # 5. Detect prompt injection attempts
    injection_found = False
    for pattern in _PROMPT_INJECTION_PATTERNS:
        if pattern.search(result):
            injection_found = True
            result = pattern.sub("[INJECTION_ATTEMPT_REMOVED]", result)

    if injection_found:
        logger.warning(
            "prompt_injection_detected",
            tool=tool_name,
            original_length=original_len,
        )

    # 6. Truncate
    if len(result) > MAX_OUTPUT_CHARS:
        result = result[:MAX_OUTPUT_CHARS] + f"\n\n[TRUNCATED: {original_len} chars → {MAX_OUTPUT_CHARS}]"
        logger.info(
            "output_truncated",
            tool=tool_name,
            original_len=original_len,
            truncated_to=MAX_OUTPUT_CHARS,
        )

    # Log if significant changes were made
    if len(result) < original_len * 0.8:
        logger.info(
            "output_sanitized",
            tool=tool_name,
            original_len=original_len,
            sanitized_len=len(result),
            reduction_pct=f"{(1 - len(result) / original_len) * 100:.1f}%",
        )

    return result


def sanitize_tool_output_dict(output: dict, *, tool_name: str = "") -> dict:
    """
    Sanitize a dict tool output. Recursively sanitizes string values.
    Also caps list lengths and removes the _untrusted marker (it's
    re-added by the broker after sanitization).
    """
    if not isinstance(output, dict):
        return output

    sanitized = {}
    for key, value in output.items():
        if key == "_untrusted":
            # Preserve the untrusted marker
            sanitized[key] = value
        elif isinstance(value, str):
            sanitized[key] = sanitize_tool_output(value, tool_name=tool_name)
        elif isinstance(value, list):
            # Cap list length
            if len(value) > MAX_ITEMS_IN_LIST:
                logger.info(
                    "list_capped",
                    tool=tool_name,
                    key=key,
                    original_len=len(value),
                    capped_to=MAX_ITEMS_IN_LIST,
                )
                value = value[:MAX_ITEMS_IN_LIST]
            # Recursively sanitize list items
            sanitized[key] = [
                sanitize_tool_output(item, tool_name=tool_name)
                if isinstance(item, str)
                else sanitize_tool_output_dict(item, tool_name=tool_name)
                if isinstance(item, dict)
                else item
                for item in value
            ]
        elif isinstance(value, dict):
            sanitized[key] = sanitize_tool_output_dict(value, tool_name=tool_name)
        else:
            sanitized[key] = value

    return sanitized
