"""
tools/browser.py — Cloudflare Browser Run integration (Los Ojos del Embrión)

Sprint 33B | v0.27.0-sprint33 | 29 abril 2026

Provides the Embrión with the ability to browse the web, extract content,
and interact with pages using Cloudflare Browser Run (formerly Browser Rendering).

Architecture:
    Cloudflare Browser Run Quick Actions API (stateless, single HTTP POST)
    ├── /markdown   — Extract Markdown from a webpage (primary)
    ├── /content    — Fetch fully rendered HTML
    ├── /scrape     — Extract structured data via CSS selectors
    ├── /links      — Retrieve all links from a page
    └── /screenshot — Capture screenshot (returns base64)

Authentication:
    - CF_ACCOUNT_ID: Cloudflare account ID
    - CF_API_TOKEN:  API token with "Browser Rendering - Edit" permission
    Both must be set in Railway env vars.

Fallback:
    If Cloudflare credentials are not configured, falls back to httpx
    (basic HTTP GET + HTML-to-text extraction, no JS rendering).

Security:
    - Read-only operations (no writes, no form submissions)
    - No secrets are exposed to target pages
    - Cloudflare handles browser isolation

Validated:
    - Cloudflare Browser Run API: GA (April 2026)
    - Endpoint format: https://api.cloudflare.com/client/v4/accounts/{id}/browser-rendering/{action}
    - httpx==0.28.1 (already in requirements.txt)
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Optional

logger = logging.getLogger("monstruo.tools.browser")

# ── Configuration ──────────────────────────────────────────────────────────
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID", "")
CF_API_TOKEN = os.getenv("CF_API_TOKEN", "")
CF_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/browser-rendering"

# Maximum content length to return (prevent token explosion)
MAX_CONTENT_LENGTH = 30_000  # ~7.5k tokens

# Supported actions
ACTIONS = {
    "markdown": "Extract Markdown from a webpage",
    "content": "Fetch fully rendered HTML",
    "scrape": "Extract structured data via CSS selectors",
    "links": "Retrieve all links from a page",
    "screenshot": "Capture screenshot (base64)",
}


def _is_cloudflare_configured() -> bool:
    """Check if Cloudflare Browser Run credentials are available."""
    return bool(CF_ACCOUNT_ID) and bool(CF_API_TOKEN)


def _truncate(text: str, max_len: int = MAX_CONTENT_LENGTH) -> str:
    """Truncate text to max length with indicator."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + f"\n\n... [TRUNCATED — {len(text)} chars total, showing first {max_len}]"


# ── Cloudflare Browser Run Backend ─────────────────────────────────────────


async def _cf_request(action: str, payload: dict) -> dict:
    """Make a request to Cloudflare Browser Run Quick Actions API."""
    import httpx

    url = f"{CF_BASE_URL}/{action}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

        # /screenshot returns binary, everything else returns JSON
        if action == "screenshot":
            import base64

            return {
                "success": True,
                "result": base64.b64encode(response.content).decode("utf-8"),
                "format": "png_base64",
            }

        return response.json()


async def _cf_markdown(url: str, wait_for_js: bool = True) -> str:
    """Extract Markdown from a URL using Cloudflare Browser Run."""
    payload: dict[str, Any] = {"url": url}
    if wait_for_js:
        payload["gotoOptions"] = {"waitUntil": "networkidle2"}

    data = await _cf_request("markdown", payload)
    if data.get("success") and data.get("result"):
        return _truncate(data["result"])
    raise RuntimeError(f"Cloudflare /markdown failed: {json.dumps(data.get('errors', []))}")


async def _cf_content(url: str, wait_for_js: bool = True) -> str:
    """Fetch rendered HTML from a URL using Cloudflare Browser Run."""
    payload: dict[str, Any] = {"url": url}
    if wait_for_js:
        payload["gotoOptions"] = {"waitUntil": "networkidle2"}

    data = await _cf_request("content", payload)
    if data.get("success") and data.get("result"):
        return _truncate(data["result"])
    raise RuntimeError(f"Cloudflare /content failed: {json.dumps(data.get('errors', []))}")


async def _cf_scrape(url: str, selectors: list[str], wait_for_js: bool = True) -> list[dict]:
    """Scrape specific elements from a URL using CSS selectors."""
    payload: dict[str, Any] = {
        "url": url,
        "elements": [{"selector": s} for s in selectors],
    }
    if wait_for_js:
        payload["gotoOptions"] = {"waitUntil": "networkidle2"}

    data = await _cf_request("scrape", payload)
    if data.get("success") and data.get("result"):
        return data["result"]
    raise RuntimeError(f"Cloudflare /scrape failed: {json.dumps(data.get('errors', []))}")


async def _cf_links(url: str) -> list[dict]:
    """Retrieve all links from a URL."""
    payload = {"url": url, "gotoOptions": {"waitUntil": "networkidle2"}}
    data = await _cf_request("links", payload)
    if data.get("success") and data.get("result"):
        return data["result"]
    raise RuntimeError(f"Cloudflare /links failed: {json.dumps(data.get('errors', []))}")


# ── Fallback Backend (httpx + basic HTML parsing) ──────────────────────────


async def _fallback_browse(url: str) -> str:
    """Basic HTTP GET with HTML-to-text extraction (no JS rendering)."""
    import httpx

    async with httpx.AsyncClient(
        timeout=20.0,
        follow_redirects=True,
        headers={"User-Agent": "ElMonstruo/0.27.0 (browser-tool)"},
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        html = response.text

        # Basic HTML to text extraction
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        # Extract title
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""

        result = {
            "url": str(response.url),
            "status": response.status_code,
            "title": title,
            "content_type": content_type,
            "backend": "httpx_fallback",
            "note": "JS not rendered — Cloudflare Browser Run not configured (set CF_ACCOUNT_ID + CF_API_TOKEN)",
            "text": _truncate(text),
        }
        return json.dumps(result, ensure_ascii=False)


# ── Public API ─────────────────────────────────────────────────────────────


async def browse_web(
    url: str,
    action: str = "markdown",
    selectors: Optional[list[str]] = None,
    wait_for_js: bool = True,
) -> str:
    """
    Browse a web page and extract content.

    Args:
        url: The URL to browse.
        action: What to extract. One of: "markdown", "content", "scrape", "links".
                Default: "markdown" (best for LLM consumption).
        selectors: CSS selectors for "scrape" action. Required if action="scrape".
        wait_for_js: Whether to wait for JavaScript rendering. Default: True.

    Returns:
        JSON string with the result.
    """
    if not url:
        return json.dumps({"error": "url is required"})

    # Normalize action
    action = action.lower().strip()
    if action not in ACTIONS:
        action = "markdown"

    # ── Cloudflare Backend ──
    if _is_cloudflare_configured():
        try:
            if action == "markdown":
                content = await _cf_markdown(url, wait_for_js)
                result = {
                    "url": url,
                    "action": "markdown",
                    "backend": "cloudflare_browser_run",
                    "content": content,
                }

            elif action == "content":
                content = await _cf_content(url, wait_for_js)
                result = {
                    "url": url,
                    "action": "content",
                    "backend": "cloudflare_browser_run",
                    "content": content,
                }

            elif action == "scrape":
                if not selectors:
                    return json.dumps({"error": "selectors required for scrape action"})
                elements = await _cf_scrape(url, selectors, wait_for_js)
                result = {
                    "url": url,
                    "action": "scrape",
                    "backend": "cloudflare_browser_run",
                    "elements": elements,
                }

            elif action == "links":
                links = await _cf_links(url)
                result = {
                    "url": url,
                    "action": "links",
                    "backend": "cloudflare_browser_run",
                    "links": links,
                }

            else:
                result = {"error": f"Unknown action: {action}"}

            logger.info(
                "browser_browse_ok",
                url=url[:80],
                action=action,
                backend="cloudflare",
            )
            return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            logger.warning(
                "browser_cf_error_fallback",
                url=url[:80],
                action=action,
                error=str(e),
            )
            # Fall through to fallback
            fallback_result = await _fallback_browse(url)
            return fallback_result

    # ── Fallback Backend ──
    else:
        logger.info(
            "browser_fallback",
            url=url[:80],
            reason="cloudflare_not_configured",
        )
        return await _fallback_browse(url)
