"""kernel.browser - Sovereign Browser Module (Sprint 84.6).

Wrapper de alto nivel sobre kernel.browser_automation.BrowserAutomation
que expone operaciones HTTP-friendly para el Critic Visual y otros consumidores.
"""

from .sovereign_browser import (
    DEFAULT_DESKTOP_VIEWPORT,
    MOBILE_VIEWPORT,
    CheckMobileResult,
    MetricsResult,
    RenderResult,
    SovereignBrowser,
)

__all__ = [
    "SovereignBrowser",
    "RenderResult",
    "MetricsResult",
    "CheckMobileResult",
    "DEFAULT_DESKTOP_VIEWPORT",
    "MOBILE_VIEWPORT",
]
