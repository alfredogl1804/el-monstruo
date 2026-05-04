"""Patch atomico: aplicar todos los cambios Sprint 84.6 a kernel/browser_automation.py.

Idempotente: si ya esta aplicado, no hace nada.

Cambios:
1. Imports: agregar ipaddress, urlparse
2. Constants: BLOCKED_HOSTNAMES, BLOCKED_HOSTNAME_SUFFIXES, mantener BLOCKED_DOMAINS alias
3. Refactor _is_blocked_url: urlparse + ipaddress (no substring crudo)
4. Agregar set_viewport()
5. Agregar _collect_web_vitals()
6. Enriquecer navigate() con Web Vitals
"""
from pathlib import Path

path = Path("kernel/browser_automation.py")
src = path.read_text(encoding="utf-8")

if "_collect_web_vitals" in src and "BLOCKED_HOSTNAMES" in src:
    print("YA APLICADO -- nada que hacer")
    raise SystemExit(0)

# --- 1. Imports ---
old_imports = (
    "from __future__ import annotations\n\n"
    "import os\n"
    "from dataclasses import dataclass\n"
    "from typing import Any, Optional\n\n"
    "import structlog"
)
new_imports = (
    "from __future__ import annotations\n\n"
    "import ipaddress\n"
    "import os\n"
    "from dataclasses import dataclass\n"
    "from typing import Any, Optional\n"
    "from urllib.parse import urlparse\n\n"
    "import structlog"
)
assert old_imports in src, "anchor de imports no encontrado"
src = src.replace(old_imports, new_imports, 1)

# --- 2. Constants ---
old_constants = (
    "BLOCKED_DOMAINS = [\n"
    "    \"localhost\",\n"
    "    \"127.0.0.1\",\n"
    "    \"0.0.0.0\",\n"
    "    \"169.254.\",\n"
    "    \"10.\",\n"
    "    \"192.168.\",\n"
    "    \"172.16.\",\n"
    "]"
)
new_constants = (
    "# Hostnames bloqueados (match exacto, case-insensitive)\n"
    "BLOCKED_HOSTNAMES = frozenset({\"localhost\", \"localhost.localdomain\"})\n\n"
    "# Sufijos bloqueados (cualquier hostname que termine con esto)\n"
    "BLOCKED_HOSTNAME_SUFFIXES = (\".local\", \".internal\", \".lan\")\n\n"
    "# Backward-compat (Sprint 84.6) -- algunos modulos importan BLOCKED_DOMAINS.\n"
    "# La logica real esta en _is_blocked_url() con urlparse + ipaddress.\n"
    "# Leccion 27va semilla: NO usar substring matching para validacion de seguridad.\n"
    "BLOCKED_DOMAINS = (\n"
    "    \"localhost\",\n"
    "    \"127.0.0.1\",\n"
    "    \"0.0.0.0\",\n"
    "    \"169.254.0.0/16\",\n"
    "    \"10.0.0.0/8\",\n"
    "    \"192.168.0.0/16\",\n"
    "    \"172.16.0.0/12\",\n"
    ")"
)
assert old_constants in src, "anchor de constants no encontrado"
src = src.replace(old_constants, new_constants, 1)

# --- 3. Refactor _is_blocked_url ---
old_blocked = (
    "    def _is_blocked_url(self, url: str) -> bool:\n"
    "        \"\"\"Check if URL targets a blocked domain (security).\"\"\"\n"
    "        url_lower = url.lower()\n"
    "        for blocked in BLOCKED_DOMAINS:\n"
    "            if blocked in url_lower:\n"
    "                return True\n"
    "        return False"
)
new_blocked = (
    "    def _is_blocked_url(self, url: str) -> bool:\n"
    "        \"\"\"Check if URL targets a blocked domain or private IP (security).\n\n"
    "        Validacion estructurada (no substring crudo):\n"
    "        1. Parsea con urlparse\n"
    "        2. Hostname check vs BLOCKED_HOSTNAMES y sufijos\n"
    "        3. IP check via ipaddress.ip_address(host).is_private/loopback/link_local\n"
    "        4. Schema check: solo http/https\n"
    "        \"\"\"\n"
    "        try:\n"
    "            parsed = urlparse(url)\n"
    "        except Exception:\n"
    "            return True\n\n"
    "        if parsed.scheme not in (\"http\", \"https\"):\n"
    "            return True\n\n"
    "        host = (parsed.hostname or \"\").lower().strip()\n"
    "        if not host:\n"
    "            return True\n\n"
    "        if host in BLOCKED_HOSTNAMES:\n"
    "            return True\n\n"
    "        for suffix in BLOCKED_HOSTNAME_SUFFIXES:\n"
    "            if host.endswith(suffix):\n"
    "                return True\n\n"
    "        try:\n"
    "            ip = ipaddress.ip_address(host)\n"
    "            if (\n"
    "                ip.is_private\n"
    "                or ip.is_loopback\n"
    "                or ip.is_link_local\n"
    "                or ip.is_multicast\n"
    "                or ip.is_reserved\n"
    "            ):\n"
    "                return True\n"
    "        except ValueError:\n"
    "            pass\n\n"
    "        return False"
)
assert old_blocked in src, "anchor de _is_blocked_url no encontrado"
src = src.replace(old_blocked, new_blocked, 1)

# --- 4. Enriquecer navigate() ---
old_navigate = (
    "        try:\n"
    "            response = await self._page.goto(url, wait_until=\"domcontentloaded\")\n"
    "            self._current_url = url\n"
    "            title = await self._page.title()\n\n"
    "            page_info = PageInfo(\n"
    "                url=url,\n"
    "                title=title,\n"
    "                status_code=response.status if response else 0,\n"
    "            )\n\n"
    "            logger.info(\"browser_navigated\", url=url, title=title)\n"
    "            return BrowserResult(success=True, data=page_info)"
)
new_navigate = (
    "        try:\n"
    "            response = await self._page.goto(url, wait_until=\"domcontentloaded\")\n"
    "            self._current_url = url\n"
    "            title = await self._page.title()\n\n"
    "            # Sprint 84.6: Web Vitals via performance.timing JS shim\n"
    "            metrics = await self._collect_web_vitals()\n\n"
    "            page_info = {\n"
    "                \"url\": url,\n"
    "                \"title\": title,\n"
    "                \"status_code\": response.status if response else 0,\n"
    "                \"ttfb_ms\": metrics.get(\"ttfb_ms\", 0),\n"
    "                \"lcp_ms\": metrics.get(\"lcp_ms\", 0),\n"
    "                \"load_time_ms\": metrics.get(\"load_time_ms\", 0),\n"
    "            }\n\n"
    "            logger.info(\n"
    "                \"browser_navigated\",\n"
    "                url=url,\n"
    "                title=title,\n"
    "                ttfb_ms=metrics.get(\"ttfb_ms\"),\n"
    "                lcp_ms=metrics.get(\"lcp_ms\"),\n"
    "            )\n"
    "            return BrowserResult(success=True, data=page_info)"
)
assert old_navigate in src, "anchor de navigate no encontrado"
src = src.replace(old_navigate, new_navigate, 1)

# --- 5+6. Insertar set_viewport y _collect_web_vitals antes de "# --- Internal Helpers ---" ---
anchor_helpers = "    # ─── Internal Helpers ─"
assert anchor_helpers in src, "anchor de Internal Helpers no encontrado"

new_methods = (
    "    # --- Sprint 84.6: viewport runtime + Web Vitals ---\n\n"
    "    async def set_viewport(self, width: int, height: int) -> BrowserResult:\n"
    "        \"\"\"Cambia el viewport sin reinicializar el browser.\n\n"
    "        Necesario para el Critic Visual del Sprint 85 (mobile 375x812)\n"
    "        sin pagar el costo de re-init.\n"
    "        \"\"\"\n"
    "        if not self._initialized:\n"
    "            return BrowserResult(\n"
    "                success=False,\n"
    "                error=\"Browser not initialized. Call initialize() first.\",\n"
    "            )\n"
    "        if width <= 0 or height <= 0:\n"
    "            return BrowserResult(\n"
    "                success=False,\n"
    "                error=f\"Invalid viewport dimensions: {width}x{height}\",\n"
    "            )\n"
    "        try:\n"
    "            await self._page.set_viewport_size({\"width\": width, \"height\": height})\n"
    "            self.viewport = {\"width\": width, \"height\": height}\n"
    "            logger.info(\"browser_viewport_changed\", width=width, height=height)\n"
    "            return BrowserResult(\n"
    "                success=True, data={\"width\": width, \"height\": height},\n"
    "            )\n"
    "        except Exception as e:\n"
    "            logger.error(\"browser_viewport_failed\", error=str(e)[:200])\n"
    "            return BrowserResult(\n"
    "                success=False,\n"
    "                error=f\"Viewport change failed: {str(e)[:200]}\",\n"
    "            )\n\n"
    "    async def _collect_web_vitals(self) -> dict[str, int]:\n"
    "        \"\"\"Captura Core Web Vitals via performance.timing JS shim.\n\n"
    "        Returns dict con ttfb_ms, lcp_ms, load_time_ms (milliseconds).\n"
    "        Si falla la captura, retorna ceros (no rompe el flow).\n"
    "        \"\"\"\n"
    "        if not self._initialized or self._page is None:\n"
    "            return {\"ttfb_ms\": 0, \"lcp_ms\": 0, \"load_time_ms\": 0}\n"
    "        try:\n"
    "            metrics = await self._page.evaluate(\"\"\"\n"
    "                () => {\n"
    "                    const t = performance.timing || {};\n"
    "                    const navStart = t.navigationStart || 0;\n"
    "                    const ttfb = (t.responseStart || 0) - navStart;\n"
    "                    const loadTime = (t.loadEventEnd || 0) - navStart;\n"
    "                    let lcp = 0;\n"
    "                    try {\n"
    "                        const lcpEntries = performance.getEntriesByType('largest-contentful-paint');\n"
    "                        if (lcpEntries && lcpEntries.length > 0) {\n"
    "                            lcp = Math.round(lcpEntries[lcpEntries.length - 1].startTime);\n"
    "                        }\n"
    "                    } catch (e) {}\n"
    "                    return {\n"
    "                        ttfb_ms: Math.max(0, Math.round(ttfb)),\n"
    "                        lcp_ms: lcp,\n"
    "                        load_time_ms: Math.max(0, Math.round(loadTime)),\n"
    "                    };\n"
    "                }\n"
    "            \"\"\")\n"
    "            return metrics or {\"ttfb_ms\": 0, \"lcp_ms\": 0, \"load_time_ms\": 0}\n"
    "        except Exception as e:\n"
    "            logger.warning(\"web_vitals_capture_failed\", error=str(e)[:200])\n"
    "            return {\"ttfb_ms\": 0, \"lcp_ms\": 0, \"load_time_ms\": 0}\n\n"
)

src = src.replace(anchor_helpers, new_methods + anchor_helpers, 1)

# Validar sintaxis
import ast
ast.parse(src)

path.write_text(src, encoding="utf-8")
print("OK -- Sprint 84.6 patch aplicado a browser_automation.py")
print(f"   - imports actualizados (ipaddress, urlparse)")
print(f"   - BLOCKED_HOSTNAMES + BLOCKED_HOSTNAME_SUFFIXES + BLOCKED_DOMAINS alias")
print(f"   - _is_blocked_url refactorizado (urlparse + ipaddress)")
print(f"   - set_viewport() agregado")
print(f"   - _collect_web_vitals() agregado")
print(f"   - navigate() enriquecido con Web Vitals")
