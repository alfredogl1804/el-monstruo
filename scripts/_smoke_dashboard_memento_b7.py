#!/usr/bin/env python3
"""
Smoke E2E productivo — Sprint Memento Bloque 7 — Dashboard + Reload
====================================================================

Ejecuta 6 casos sintéticos contra el kernel productivo (Railway) para validar
visibilidad humana y operación del Memento:

    1. GET /v1/memento/admin/dashboard SIN auth → 401
    2. GET /v1/memento/admin/dashboard JSON → 200 con health + métricas
    3. GET /v1/memento/admin/dashboard HTML (Accept: text/html) → 200 con
       content-type text/html
    4. POST /v1/memento/admin/reload SIN auth → 401
    5. POST /v1/memento/admin/reload con auth → 200 reload exitoso
    6. POST /v1/memento/validate (smoke ya cubierto en B6, lo repetimos
       como sanity check con el catálogo recargado)

Diseño:
    - urllib.request stdlib (sin deps externas)
    - Variables: KERNEL_URL (default Railway prod), MONSTRUO_API_KEY
    - Salida humana legible + exit code 1 si algo falla

Uso:
    export MONSTRUO_API_KEY=...
    python3 scripts/_smoke_dashboard_memento_b7.py

CI / opt-in:
    El test correspondiente está en tests/test_sprint_memento_b7_e2e.py::
    test_integration_dashboard_against_railway (gated por
    MEMENTO_INTEGRATION_TESTS=true).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple

DEFAULT_KERNEL_URL = "https://el-monstruo-kernel-production.up.railway.app"


def _http(
    method: str,
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None,
    timeout_s: int = 15,
) -> Tuple[int, str, Dict[str, str]]:
    """Devuelve (status, body_text, response_headers)."""
    data = None
    headers = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return resp.status, resp.read().decode("utf-8"), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace"), dict(e.headers or {})


def _print(label: str, ok: bool, detail: str = "") -> None:
    mark = "OK " if ok else "FAIL"
    print(f"  [{mark}] {label}{(' — ' + detail) if detail else ''}")


def main() -> int:
    base = os.environ.get("KERNEL_URL", DEFAULT_KERNEL_URL).rstrip("/")
    api_key = os.environ.get("MONSTRUO_API_KEY", "").strip()
    if not api_key:
        print("ERROR: MONSTRUO_API_KEY no está en el ambiente.")
        print("       export MONSTRUO_API_KEY=... y reintentá.")
        return 2

    print(f"\n=== SMOKE DASHBOARD B7 — kernel={base} ===\n")
    failures = 0

    # ── Caso 1: dashboard sin auth → 401 ──────────────────────────────────
    print("[CASO 1: GET /admin/dashboard SIN auth]")
    status, body, _ = _http("GET", f"{base}/v1/memento/admin/dashboard")
    ok = status == 401
    _print("HTTP 401", ok, f"got {status}")
    failures += 0 if ok else 1

    # ── Caso 2: dashboard con auth → 200 + health + métricas ──────────────
    print("\n[CASO 2: GET /admin/dashboard con auth (JSON)]")
    status, body, hdrs = _http(
        "GET",
        f"{base}/v1/memento/admin/dashboard",
        headers={"X-API-Key": api_key, "Accept": "application/json"},
    )
    ok = status == 200
    _print("HTTP 200", ok, f"got {status}")
    failures += 0 if ok else 1
    if ok:
        try:
            data = json.loads(body)
            for key in ("health", "window", "validations_last_24h", "contamination_last_24h", "top_operations", "top_hilos"):
                present = key in data
                _print(f"presente '{key}'", present)
                failures += 0 if present else 1
            health = data.get("health", {})
            _print(
                f"validator_initialized={health.get('validator_initialized')}",
                health.get("validator_initialized") is True,
            )
            _print(
                f"detector_initialized={health.get('detector_initialized')}",
                health.get("detector_initialized") is True,
            )
            print(f"  → sample_size: {data.get('window', {}).get('sample_size')}")
            print(f"  → ok_rate: {data.get('validations_last_24h', {}).get('ok_rate')}")
            print(f"  → contamination warnings: {data.get('contamination_last_24h', {}).get('warnings')}")
        except json.JSONDecodeError:
            _print("JSON parseable", False, body[:200])
            failures += 1

    # ── Caso 3: dashboard HTML ────────────────────────────────────────────
    print("\n[CASO 3: GET /admin/dashboard HTML]")
    status, body, hdrs = _http(
        "GET",
        f"{base}/v1/memento/admin/dashboard",
        headers={"X-API-Key": api_key, "Accept": "text/html"},
    )
    ok = status == 200
    _print("HTTP 200", ok, f"got {status}")
    failures += 0 if ok else 1
    ctype = hdrs.get("content-type", hdrs.get("Content-Type", ""))
    is_html = "text/html" in ctype.lower()
    _print(f"content-type es text/html", is_html, f"got '{ctype}'")
    failures += 0 if is_html else 1

    # ── Caso 4: reload sin auth → 401 ─────────────────────────────────────
    print("\n[CASO 4: POST /admin/reload SIN auth]")
    status, body, _ = _http("POST", f"{base}/v1/memento/admin/reload")
    ok = status == 401
    _print("HTTP 401", ok, f"got {status}")
    failures += 0 if ok else 1

    # ── Caso 5: reload con auth → 200 ─────────────────────────────────────
    print("\n[CASO 5: POST /admin/reload con auth]")
    status, body, _ = _http(
        "POST",
        f"{base}/v1/memento/admin/reload",
        headers={"X-API-Key": api_key},
    )
    ok = status == 200
    _print("HTTP 200", ok, f"got {status}")
    failures += 0 if ok else 1
    if ok:
        try:
            data = json.loads(body)
            for key in ("status", "loaded_from", "critical_operations_count", "sources_of_truth_count", "reload_runtime_ms"):
                _print(f"presente '{key}'", key in data)
                failures += 0 if key in data else 1
            print(f"  → loaded_from: {data.get('loaded_from')}")
            print(f"  → critical_operations: {data.get('critical_operations_count')} (antes {data.get('previous_critical_operations_count')})")
            print(f"  → sources_of_truth:    {data.get('sources_of_truth_count')} (antes {data.get('previous_sources_of_truth_count')})")
            print(f"  → reload_runtime_ms:   {data.get('reload_runtime_ms')}")
        except json.JSONDecodeError:
            _print("JSON parseable", False, body[:200])
            failures += 1

    # ── Caso 6: validate sanity check post-reload ─────────────────────────
    print("\n[CASO 6: POST /validate post-reload (sanity check)]")
    status, body, _ = _http(
        "POST",
        f"{base}/v1/memento/validate",
        headers={"X-API-Key": api_key},
        body={
            "hilo_id": "smoke_b7_post_reload",
            "operation": "sql_against_production",
            "context_used": {
                "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
                "user": "37Hy7adB53QmFW4.root",
                "credential_hash_first_8": "smoke_b7",
            },
            "intent_summary": "smoke b7 post reload sanity",
        },
    )
    ok = status == 200
    _print("HTTP 200", ok, f"got {status}")
    failures += 0 if ok else 1
    if ok:
        try:
            data = json.loads(body)
            for key in ("validation_id", "validation_status", "proceed", "persistence_failed"):
                _print(f"presente '{key}'", key in data)
                failures += 0 if key in data else 1
            print(f"  → validation_status: {data.get('validation_status')}")
            print(f"  → proceed:           {data.get('proceed')}")
            print(f"  → contamination_warning: {data.get('contamination_warning')}")
            print(f"  → persistence_failed:    {data.get('persistence_failed')}")
        except json.JSONDecodeError:
            _print("JSON parseable", False, body[:200])
            failures += 1

    print("\n=== RESUMEN ===")
    print(f"  Total checks fallidos: {failures}")
    if failures == 0:
        print("  Smoke B7 dashboard: VERDE")
        return 0
    print("  Smoke B7 dashboard: ROJO")
    return 1


if __name__ == "__main__":
    sys.exit(main())
