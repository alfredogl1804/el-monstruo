"""
El Monstruo — Browser Automation (SP11)
========================================
Full browser automation using Playwright for the Embrión.
Extends the read-only Cloudflare Browser Run (tools/browser.py) with
interactive capabilities: clicks, form fills, screenshots, navigation.

Architecture:
    Playwright (async) → Chromium headless
    ├── navigate(url)        — Navigate to URL
    ├── click(selector)      — Click an element
    ├── fill(selector, text) — Fill a form field
    ├── screenshot(path)     — Take a screenshot
    ├── evaluate(js)         — Execute JavaScript
    ├── wait_for(selector)   — Wait for element
    ├── extract_text(sel)    — Extract text content
    └── get_page_state()     — Full page state dump

Security:
    - Runs in headless mode (no display)
    - Configurable timeout per action
    - No credential storage (ephemeral sessions)
    - Blocked domains list for safety
    - Max page load time: 30s

Dependencies:
    - playwright (pip install playwright)
    - chromium browser (playwright install chromium)

Sprint: SP11 (Embrión Superpowers)
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("monstruo.tools.browser_automation")

# ── Configuration ────────────────────────────────────────────────────

DEFAULT_TIMEOUT_MS = 30_000  # 30 seconds
MAX_CONTENT_LENGTH = 50_000  # chars
SCREENSHOT_DIR = os.environ.get("SCREENSHOT_DIR", "/tmp/monstruo_screenshots")
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 "
    "ElMonstruo/1.0"
)

# Blocked domains for safety
BLOCKED_DOMAINS = frozenset({
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "internal.",
    ".local",
})

# Supported actions
ACTIONS = {
    "navigate": "Navigate to a URL and return page content",
    "click": "Click an element matching a CSS selector",
    "fill": "Fill a form field with text",
    "screenshot": "Take a screenshot of the current page",
    "evaluate": "Execute JavaScript and return result",
    "wait_for": "Wait for an element to appear",
    "extract_text": "Extract text content from elements matching selector",
    "get_links": "Get all links from the current page",
    "get_page_state": "Get full page state (URL, title, content preview)",
    "multi_step": "Execute multiple actions in sequence",
}


# ── Data Models ──────────────────────────────────────────────────────

@dataclass
class BrowserAction:
    """A single browser action to execute."""
    action: str
    selector: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    javascript: Optional[str] = None
    timeout_ms: int = DEFAULT_TIMEOUT_MS
    screenshot_path: Optional[str] = None


@dataclass
class BrowserResult:
    """Result of a browser action."""
    success: bool
    action: str
    data: Any = None
    error: Optional[str] = None
    url: str = ""
    title: str = ""
    latency_ms: float = 0.0
    screenshot_path: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "success": self.success,
            "action": self.action,
            "url": self.url,
            "title": self.title,
            "latency_ms": round(self.latency_ms, 1),
        }
        if self.data is not None:
            result["data"] = self.data
        if self.error:
            result["error"] = self.error
        if self.screenshot_path:
            result["screenshot_path"] = self.screenshot_path
        return result


# ── Safety Checks ────────────────────────────────────────────────────

def _is_url_safe(url: str) -> bool:
    """Check if URL is safe to navigate to."""
    if not url:
        return False
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        for blocked in BLOCKED_DOMAINS:
            if blocked in hostname:
                return False
        # Must be http or https
        if parsed.scheme not in ("http", "https"):
            return False
        return True
    except Exception:
        return False


def _truncate(text: str, max_len: int = MAX_CONTENT_LENGTH) -> str:
    """Truncate text to max length."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + f"\n... [TRUNCATED — {len(text)} chars total]"


# ── Browser Session Manager ──────────────────────────────────────────

class BrowserSession:
    """
    Manages a Playwright browser session.
    Provides high-level actions for the Embrión.
    """

    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
        self._initialized = False
        self._stats = {
            "actions_executed": 0,
            "pages_visited": 0,
            "screenshots_taken": 0,
            "errors": 0,
        }

    async def initialize(self) -> None:
        """Initialize Playwright browser."""
        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )
            self._context = await self._browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1920, "height": 1080},
                ignore_https_errors=True,
            )
            self._page = await self._context.new_page()
            self._initialized = True
            logger.info("browser_session_initialized")
        except ImportError:
            logger.error(
                "playwright_not_installed",
                hint="Run: pip install playwright && playwright install chromium",
            )
            raise RuntimeError(
                "Playwright not installed. Run: pip install playwright && playwright install chromium"
            )
        except Exception as e:
            logger.error("browser_session_init_failed", error=str(e)[:200])
            raise

    async def close(self) -> None:
        """Close the browser session."""
        if self._browser:
            await self._browser.close()
        if hasattr(self, '_playwright') and self._playwright:
            await self._playwright.stop()
        self._initialized = False
        logger.info("browser_session_closed")

    async def execute(self, action: BrowserAction) -> BrowserResult:
        """Execute a single browser action."""
        if not self._initialized:
            try:
                await self.initialize()
            except Exception as e:
                self._stats["errors"] += 1
                return BrowserResult(
                    success=False,
                    action=action.action,
                    error=str(e)[:500],
                )

        start = time.time()
        self._stats["actions_executed"] += 1

        try:
            if action.action == "navigate":
                return await self._navigate(action)
            elif action.action == "click":
                return await self._click(action)
            elif action.action == "fill":
                return await self._fill(action)
            elif action.action == "screenshot":
                return await self._screenshot(action)
            elif action.action == "evaluate":
                return await self._evaluate(action)
            elif action.action == "wait_for":
                return await self._wait_for(action)
            elif action.action == "extract_text":
                return await self._extract_text(action)
            elif action.action == "get_links":
                return await self._get_links(action)
            elif action.action == "get_page_state":
                return await self._get_page_state(action)
            else:
                return BrowserResult(
                    success=False,
                    action=action.action,
                    error=f"Unknown action: {action.action}. Supported: {list(ACTIONS.keys())}",
                )
        except Exception as e:
            self._stats["errors"] += 1
            latency = (time.time() - start) * 1000
            logger.warning(
                "browser_action_failed",
                action=action.action,
                error=str(e)[:200],
            )
            return BrowserResult(
                success=False,
                action=action.action,
                error=str(e)[:500],
                url=self._page.url if self._page else "",
                latency_ms=latency,
            )

    async def execute_multi(self, actions: list[BrowserAction]) -> list[BrowserResult]:
        """Execute multiple actions in sequence."""
        results = []
        for action in actions:
            result = await self.execute(action)
            results.append(result)
            if not result.success:
                # Stop on first failure unless it's a non-critical action
                break
        return results

    # ── Individual Actions ───────────────────────────────────────────

    async def _navigate(self, action: BrowserAction) -> BrowserResult:
        """Navigate to a URL."""
        url = action.url or ""
        if not _is_url_safe(url):
            return BrowserResult(
                success=False,
                action="navigate",
                error=f"URL blocked or invalid: {url}",
            )

        start = time.time()
        await self._page.goto(url, timeout=action.timeout_ms, wait_until="domcontentloaded")
        self._stats["pages_visited"] += 1

        # Extract content
        title = await self._page.title()
        content = await self._page.content()
        text = await self._page.evaluate("() => document.body?.innerText || ''")

        latency = (time.time() - start) * 1000
        return BrowserResult(
            success=True,
            action="navigate",
            data=_truncate(text),
            url=self._page.url,
            title=title,
            latency_ms=latency,
        )

    async def _click(self, action: BrowserAction) -> BrowserResult:
        """Click an element."""
        if not action.selector:
            return BrowserResult(success=False, action="click", error="selector required")

        start = time.time()
        await self._page.click(action.selector, timeout=action.timeout_ms)
        await self._page.wait_for_load_state("domcontentloaded", timeout=5000)

        latency = (time.time() - start) * 1000
        return BrowserResult(
            success=True,
            action="click",
            data=f"Clicked: {action.selector}",
            url=self._page.url,
            title=await self._page.title(),
            latency_ms=latency,
        )

    async def _fill(self, action: BrowserAction) -> BrowserResult:
        """Fill a form field."""
        if not action.selector:
            return BrowserResult(success=False, action="fill", error="selector required")
        if action.text is None:
            return BrowserResult(success=False, action="fill", error="text required")

        start = time.time()
        await self._page.fill(action.selector, action.text, timeout=action.timeout_ms)

        latency = (time.time() - start) * 1000
        return BrowserResult(
            success=True,
            action="fill",
            data=f"Filled '{action.selector}' with '{action.text[:50]}'",
            url=self._page.url,
            title=await self._page.title(),
            latency_ms=latency,
        )

    async def _screenshot(self, action: BrowserAction) -> BrowserResult:
        """Take a screenshot."""
        start = time.time()
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

        path = action.screenshot_path or os.path.join(
            SCREENSHOT_DIR,
            f"screenshot_{int(time.time())}.png",
        )

        await self._page.screenshot(path=path, full_page=True)
        self._stats["screenshots_taken"] += 1

        latency = (time.time() - start) * 1000
        return BrowserResult(
            success=True,
            action="screenshot",
            data=f"Screenshot saved: {path}",
            url=self._page.url,
            title=await self._page.title(),
            latency_ms=latency,
            screenshot_path=path,
        )

    async def _evaluate(self, action: BrowserAction) -> BrowserResult:
        """Execute JavaScript."""
        if not action.javascript:
            return BrowserResult(success=False, action="evaluate", error="javascript required")

        start = time.time()
        result = await self._page.evaluate(action.javascript)

        latency = (time.time() - start) * 1000
        # Serialize result
        if isinstance(result, (dict, list)):
            data = json.dumps(result, ensure_ascii=False, default=str)[:MAX_CONTENT_LENGTH]
        else:
            data = str(result)[:MAX_CONTENT_LENGTH]

        return BrowserResult(
            success=True,
            action="evaluate",
            data=data,
            url=self._page.url,
            title=await self._page.title(),
            latency_ms=latency,
        )

    async def _wait_for(self, action: BrowserAction) -> BrowserResult:
        """Wait for an element to appear."""
        if not action.selector:
            return BrowserResult(success=False, action="wait_for", error="selector required")

        start = time.time()
        await self._page.wait_for_selector(action.selector, timeout=action.timeout_ms)

        latency = (time.time() - start) * 1000
        return BrowserResult(
            success=True,
            action="wait_for",
            data=f"Element found: {action.selector}",
            url=self._page.url,
            title=await self._page.title(),
            latency_ms=latency,
        )

    async def _extract_text(self, action: BrowserAction) -> BrowserResult:
        """Extract text from elements matching selector."""
        if not action.selector:
            return BrowserResult(success=False, action="extract_text", error="selector required")

        start = time.time()
        elements = await self._page.query_selector_all(action.selector)
        texts = []
        for el in elements[:50]:  # Limit to 50 elements
            text = await el.text_content()
            if text and text.strip():
                texts.append(text.strip())

        latency = (time.time() - start) * 1000
        return BrowserResult(
            success=True,
            action="extract_text",
            data=texts,
            url=self._page.url,
            title=await self._page.title(),
            latency_ms=latency,
        )

    async def _get_links(self, action: BrowserAction) -> BrowserResult:
        """Get all links from the page."""
        start = time.time()
        links = await self._page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                text: a.textContent?.trim().substring(0, 100) || '',
                href: a.href,
            })).filter(l => l.href && l.href.startsWith('http')).slice(0, 100)
        """)

        latency = (time.time() - start) * 1000
        return BrowserResult(
            success=True,
            action="get_links",
            data=links,
            url=self._page.url,
            title=await self._page.title(),
            latency_ms=latency,
        )

    async def _get_page_state(self, action: BrowserAction) -> BrowserResult:
        """Get full page state."""
        start = time.time()
        state = {
            "url": self._page.url,
            "title": await self._page.title(),
            "content_preview": _truncate(
                await self._page.evaluate("() => document.body?.innerText || ''"),
                5000,
            ),
            "forms": await self._page.evaluate("""
                () => Array.from(document.querySelectorAll('form')).map(f => ({
                    action: f.action,
                    method: f.method,
                    inputs: Array.from(f.querySelectorAll('input,textarea,select')).map(i => ({
                        name: i.name,
                        type: i.type,
                        value: i.value?.substring(0, 50),
                    })).slice(0, 20),
                })).slice(0, 5)
            """),
            "buttons": await self._page.evaluate("""
                () => Array.from(document.querySelectorAll('button,[role=button]'))
                    .map(b => b.textContent?.trim().substring(0, 50))
                    .filter(Boolean)
                    .slice(0, 20)
            """),
        }

        latency = (time.time() - start) * 1000
        return BrowserResult(
            success=True,
            action="get_page_state",
            data=state,
            url=self._page.url,
            title=state["title"],
            latency_ms=latency,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get session statistics."""
        return {
            **self._stats,
            "initialized": self._initialized,
            "current_url": self._page.url if self._page else None,
        }


# ── Tool Handler (for tool_dispatch.py integration) ──────────────────

# Singleton session
_browser_session: Optional[BrowserSession] = None


async def get_browser_session() -> BrowserSession:
    """Get or create the browser session singleton."""
    global _browser_session
    if _browser_session is None or not _browser_session._initialized:
        _browser_session = BrowserSession()
        await _browser_session.initialize()
    return _browser_session


async def handle_browser_automation(params: dict[str, Any]) -> dict[str, Any]:
    """
    Entry point for the tool dispatcher.

    Params:
        action: str — One of: navigate, click, fill, screenshot, evaluate,
                      wait_for, extract_text, get_links, get_page_state, multi_step
        url: str — URL for navigate action
        selector: str — CSS selector for click/fill/wait_for/extract_text
        text: str — Text for fill action
        javascript: str — JS code for evaluate action
        steps: list[dict] — List of actions for multi_step
        timeout_ms: int — Timeout in ms (default: 30000)

    Returns:
        dict with result or error.
    """
    action_name = params.get("action", "navigate")
    timeout_ms = int(params.get("timeout_ms", DEFAULT_TIMEOUT_MS))

    try:
        session = await get_browser_session()

        if action_name == "multi_step":
            steps = params.get("steps", [])
            if not steps:
                return {"error": "steps required for multi_step action"}

            actions = [
                BrowserAction(
                    action=step.get("action", "navigate"),
                    url=step.get("url"),
                    selector=step.get("selector"),
                    text=step.get("text"),
                    javascript=step.get("javascript"),
                    timeout_ms=step.get("timeout_ms", timeout_ms),
                )
                for step in steps
            ]
            results = await session.execute_multi(actions)
            return {
                "success": all(r.success for r in results),
                "results": [r.to_dict() for r in results],
            }

        else:
            action = BrowserAction(
                action=action_name,
                url=params.get("url"),
                selector=params.get("selector"),
                text=params.get("text"),
                javascript=params.get("javascript"),
                timeout_ms=timeout_ms,
                screenshot_path=params.get("screenshot_path"),
            )
            result = await session.execute(action)
            return result.to_dict()

    except RuntimeError as e:
        return {"error": str(e), "type": "runtime_error"}
    except Exception as e:
        logger.exception("browser_automation_unexpected_error")
        return {"error": f"Unexpected error: {e}", "type": "unexpected"}
