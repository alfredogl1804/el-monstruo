#!/usr/bin/env python3
"""
Smoke E2E · Sprint 86 Bloque 7 — Dashboard del Catastro.

Valida los 4 endpoints dashboard contra un deployment real (Railway o local):
  · GET /v1/catastro/dashboard/summary    → JSON snapshot
  · GET /v1/catastro/dashboard/timeline   → JSON timeline (?days=14)
  · GET /v1/catastro/dashboard/curators   → JSON trust scores
  · GET /v1/catastro/dashboard/           → HTML render

Disciplinas:
  · stdlib only (urllib.request) — sin dependencias externas.
  · Auth opcional: si el dashboard exige auth, se incluye X-API-Key.
  · Acepta KERNEL_URL del env o el primer argumento posicional.
  · Exit codes: 0=ok, 1=assertion_failure, 2=config/network_error.

Uso:
  KERNEL_URL=https://el-monstruo-mvp.up.railway.app \\
  MONSTRUO_API_KEY=<key> \\
  python3 scripts/_smoke_dashboard_sprint86.py

  # O contra local
  python3 scripts/_smoke_dashboard_sprint86.py http://localhost:8000

[Hilo Manus Catastro] · Sprint 86 Bloque 7 · 2026-05-04
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Optional

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------

DEFAULT_TIMEOUT = 15
EXIT_OK = 0
EXIT_ASSERTION = 1
EXIT_CONFIG = 2

# ANSI colors (terminal)
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
GREY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _color(c: str, msg: str) -> str:
    if not sys.stdout.isatty():
        return msg
    return f"{c}{msg}{RESET}"


def info(msg: str) -> None:
    print(_color(CYAN, "[INFO] ") + msg)


def ok(msg: str) -> None:
    print(_color(GREEN, "[OK]   ") + msg)


def warn(msg: str) -> None:
    print(_color(YELLOW, "[WARN] ") + msg)


def fail(msg: str) -> None:
    print(_color(RED, "[FAIL] ") + msg)


def header(msg: str) -> None:
    print()
    print(_color(BOLD + CYAN, f"━━━ {msg} ━━━"))


# ----------------------------------------------------------------------------
# HTTP helper
# ----------------------------------------------------------------------------


def http_call(
    base_url: str,
    path: str,
    *,
    api_key: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
    accept: str = "application/json",
) -> tuple[int, dict[str, Any] | str]:
    url = base_url.rstrip("/") + path
    headers = {"Accept": accept}
    if api_key:
        headers["X-API-Key"] = api_key
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
            if accept.startswith("application/json"):
                try:
                    return status, json.loads(body)
                except json.JSONDecodeError:
                    return status, body
            return status, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        try:
            return exc.code, json.loads(body)
        except Exception:
            return exc.code, body
    except urllib.error.URLError as exc:
        raise SystemExit(_color(RED, f"network error en {url}: {exc.reason}"))


# ----------------------------------------------------------------------------
# Asserts con identidad de marca
# ----------------------------------------------------------------------------


def assert_status(actual: int, expected: int, label: str) -> bool:
    if actual == expected:
        ok(f"{label}: status={actual}")
        return True
    fail(f"{label}: esperado {expected}, recibido {actual}")
    return False


def assert_key_in(body: Any, key: str, label: str) -> bool:
    if isinstance(body, dict) and key in body:
        ok(f"{label}: key '{key}' presente")
        return True
    fail(f"{label}: key '{key}' faltante en body")
    return False


def assert_html(body: str, label: str) -> bool:
    if isinstance(body, str) and "<!DOCTYPE html>" in body and "El Catastro" in body:
        ok(f"{label}: HTML válido (len={len(body)})")
        return True
    fail(f"{label}: no es HTML válido del Catastro")
    return False


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    base_url = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.environ.get("KERNEL_URL", "")
    )
    if not base_url:
        fail("KERNEL_URL no definido (env o argv[1])")
        info("Ejemplo: KERNEL_URL=https://el-monstruo-mvp.up.railway.app python3 ...")
        return EXIT_CONFIG

    api_key = os.environ.get("MONSTRUO_API_KEY", "")
    require_auth = os.environ.get("CATASTRO_DASHBOARD_REQUIRE_AUTH", "").lower() in (
        "true", "1", "yes",
    )

    header(f"Smoke Dashboard Sprint 86 B7 → {base_url}")
    info(f"auth_obligatoria={require_auth} api_key_set={bool(api_key)}")
    if require_auth and not api_key:
        warn("CATASTRO_DASHBOARD_REQUIRE_AUTH=true pero MONSTRUO_API_KEY ausente")

    auth_kwarg = api_key if (require_auth or api_key) else None
    failures = 0

    # 1. /summary
    header("[1/4] /v1/catastro/dashboard/summary")
    status, body = http_call(base_url, "/v1/catastro/dashboard/summary", api_key=auth_kwarg)
    if not assert_status(status, 200, "summary"):
        failures += 1
    elif not isinstance(body, dict):
        fail("summary: body no es dict")
        failures += 1
    else:
        assert_key_in(body, "trust_level", "summary")
        assert_key_in(body, "modelos_total", "summary")
        assert_key_in(body, "macroareas", "summary")
        info(f"  trust={body.get('trust_level')} modelos={body.get('modelos_total')} "
             f"degraded={body.get('degraded')}")

    # 2. /timeline
    header("[2/4] /v1/catastro/dashboard/timeline?days=14")
    status, body = http_call(base_url, "/v1/catastro/dashboard/timeline?days=14",
                             api_key=auth_kwarg)
    if not assert_status(status, 200, "timeline"):
        failures += 1
    elif not isinstance(body, dict):
        fail("timeline: body no es dict")
        failures += 1
    else:
        assert_key_in(body, "days", "timeline")
        assert_key_in(body, "points", "timeline")
        if body.get("days") != 14:
            fail(f"timeline: días esperado 14, recibido {body.get('days')}")
            failures += 1
        else:
            ok(f"timeline: days=14 points={len(body.get('points', []))} "
               f"runs={body.get('total_runs')} eventos={body.get('total_eventos')}")

    # 3. /curators
    header("[3/4] /v1/catastro/dashboard/curators")
    status, body = http_call(base_url, "/v1/catastro/dashboard/curators",
                             api_key=auth_kwarg)
    if not assert_status(status, 200, "curators"):
        failures += 1
    elif not isinstance(body, dict):
        fail("curators: body no es dict")
        failures += 1
    else:
        assert_key_in(body, "total", "curators")
        assert_key_in(body, "curadores", "curators")
        info(f"  total={body.get('total')} avg_trust={body.get('avg_trust')}")

    # 4. /  (HTML)
    header("[4/4] /v1/catastro/dashboard/  (HTML)")
    status, body = http_call(
        base_url, "/v1/catastro/dashboard/",
        api_key=auth_kwarg, accept="text/html",
    )
    if not assert_status(status, 200, "html"):
        failures += 1
    elif not assert_html(body if isinstance(body, str) else "", "html"):
        failures += 1

    # Resumen
    header("RESUMEN")
    if failures == 0:
        ok(f"4/4 endpoints PASS → smoke verde")
        return EXIT_OK
    else:
        fail(f"{failures} fallos detectados")
        return EXIT_ASSERTION


if __name__ == "__main__":
    sys.exit(main())
