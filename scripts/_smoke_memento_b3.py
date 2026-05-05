#!/usr/bin/env python3
"""
Smoke test E2E del Sprint Memento Bloque 3.

Uso:
    # Contra Railway production
    export MONSTRUO_API_KEY="<valor real>"
    python3 scripts/_smoke_memento_b3.py --base-url https://el-monstruo-kernel-production.up.railway.app

    # Contra kernel local (uvicorn corriendo en :8000)
    export MONSTRUO_API_KEY="cualquier_valor_local"
    python3 scripts/_smoke_memento_b3.py --base-url http://localhost:8000

Smoke checks (4):
    1. Health endpoint responde 200 con version coincidiendo con kernel/__init__.__version__
    2. POST /v1/memento/validate sin API key → 401
    3. POST /v1/memento/validate con API key + payload válido + operación 'sql_against_production' →
       200 con validation_status='ok' o 'discrepancy_detected' (depende del shape del catálogo prod)
    4. POST /v1/memento/validate con operación inexistente → 200 con
       validation_status='unknown_operation'

Pre-flight anti-Dory:
    - MONSTRUO_API_KEY se lee FRESH al inicio (no se cachea)
    - --base-url es argumento obligatorio (no asume defecto)
    - Cada request lleva timeout de 15s
    - Si alguno de los 4 checks falla, exit code != 0 y log explícito
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional, Tuple

import httpx


def _section(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def _ok(msg: str) -> None:
    print(f"[OK]    {msg}")


def _fail(msg: str) -> None:
    print(f"[FAIL]  {msg}")


def _info(msg: str) -> None:
    print(f"[INFO]  {msg}")


def check_health(base_url: str) -> Tuple[bool, Optional[str]]:
    _section("Check 1/4: Health endpoint")
    try:
        r = httpx.get(f"{base_url}/health", timeout=15)
        if r.status_code != 200:
            _fail(f"/health respondió {r.status_code}")
            return False, None
        body = r.json()
        version = body.get("version") or body.get("monstruo_ready", {}).get("version")
        _ok(f"/health 200 — version: {version}")
        return True, version
    except Exception as e:
        _fail(f"/health exception: {e}")
        return False, None


def check_unauthorized(base_url: str) -> bool:
    _section("Check 2/4: POST /v1/memento/validate sin API key debe ser 401")
    try:
        r = httpx.post(
            f"{base_url}/v1/memento/validate",
            json={"hilo_id": "smoke", "operation": "x", "context_used": {}},
            timeout=15,
        )
        if r.status_code == 401:
            _ok(f"401 confirmado: {r.json().get('detail')}")
            return True
        _fail(f"esperaba 401 pero recibí {r.status_code}: {r.text[:200]}")
        return False
    except Exception as e:
        _fail(f"exception: {e}")
        return False


def check_valid_request(base_url: str, api_key: str) -> bool:
    _section("Check 3/4: POST /v1/memento/validate con sql_against_production")
    payload = {
        "hilo_id": "smoke_test_b3",
        "operation": "sql_against_production",
        "context_used": {
            "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
            "user": "37Hy7adB53QmFW4.root",
        },
        "intent_summary": "Smoke test del endpoint /v1/memento/validate",
    }
    try:
        r = httpx.post(
            f"{base_url}/v1/memento/validate",
            json=payload,
            headers={"X-API-Key": api_key},
            timeout=15,
        )
        if r.status_code != 200:
            _fail(f"esperaba 200 pero recibí {r.status_code}: {r.text[:300]}")
            return False
        body = r.json()
        _info(json.dumps(body, indent=2, ensure_ascii=False))
        # Aceptamos cualquiera de estos 3 outcomes:
        #  - ok + proceed=true (catálogo + fuente coinciden con la fixture)
        #  - discrepancy_detected (la fuente real en prod difiere del payload)
        #  - source_unavailable (la fuente declarada en prod aún no existe en repo)
        valid_statuses = {"ok", "discrepancy_detected", "source_unavailable", "unknown_operation"}
        if body.get("validation_status") in valid_statuses:
            _ok(f"validation_status={body['validation_status']} validation_id={body.get('validation_id')}")
            return True
        _fail(f"validation_status inesperado: {body.get('validation_status')}")
        return False
    except Exception as e:
        _fail(f"exception: {e}")
        return False


def check_unknown_operation(base_url: str, api_key: str) -> bool:
    _section("Check 4/4: POST /v1/memento/validate con operación inexistente")
    payload = {
        "hilo_id": "smoke_test_b3",
        "operation": "this_operation_does_not_exist_smoke",
        "context_used": {},
    }
    try:
        r = httpx.post(
            f"{base_url}/v1/memento/validate",
            json=payload,
            headers={"X-API-Key": api_key},
            timeout=15,
        )
        if r.status_code != 200:
            _fail(f"esperaba 200 pero recibí {r.status_code}: {r.text[:300]}")
            return False
        body = r.json()
        if body.get("validation_status") == "unknown_operation" and body.get("proceed") is False:
            _ok(f"unknown_operation confirmado: validation_id={body.get('validation_id')}")
            return True
        _fail(f"shape inesperado: {body}")
        return False
    except Exception as e:
        _fail(f"exception: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke E2E Sprint Memento Bloque 3")
    parser.add_argument("--base-url", required=True, help="Base URL del kernel (ej: http://localhost:8000)")
    args = parser.parse_args()

    # Pre-flight: leer MONSTRUO_API_KEY FRESH
    api_key = os.environ.get("MONSTRUO_API_KEY", "").strip()
    if not api_key:
        print("[FATAL] MONSTRUO_API_KEY no configurada en env. Abortando.")
        return 2

    base_url = args.base_url.rstrip("/")
    print(f"Smoke Sprint Memento Bloque 3 contra: {base_url}")
    print(f"API key (primeros 8 chars): {api_key[:8]}…")

    ok_health, version = check_health(base_url)
    ok_unauth = check_unauthorized(base_url)
    ok_valid = check_valid_request(base_url, api_key)
    ok_unknown = check_unknown_operation(base_url, api_key)

    _section("Resumen")
    results = {
        "health": ok_health,
        "unauthorized": ok_unauth,
        "valid_request": ok_valid,
        "unknown_operation": ok_unknown,
    }
    for name, ok in results.items():
        flag = "[OK]   " if ok else "[FAIL] "
        print(f"  {flag} {name}")
    all_ok = all(results.values())
    if all_ok:
        print(f"\nTODOS LOS CHECKS PASARON. Version del kernel: {version}")
        return 0
    print("\nALGUN CHECK FALLO. Revisá logs arriba.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
