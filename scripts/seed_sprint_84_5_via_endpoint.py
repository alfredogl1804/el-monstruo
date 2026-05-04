#!/usr/bin/env python3
"""
El Monstruo — Sprint 84.5.5 — Sembrar 4 semillas via endpoint admin
====================================================================

Llama POST /v1/error-memory/seed del kernel productivo para persistir
las 4 semillas (13va, 14va, 15va, 16va) en error_memory de Supabase.

Idempotente: si la semilla ya existe (mismo error_signature), hace
UPSERT en lugar de duplicar.

Uso:
    export MONSTRUO_API_KEY="..."
    python3 scripts/seed_sprint_84_5_via_endpoint.py

Variables de entorno:
    KERNEL_URL          (default: https://el-monstruo-kernel-production.up.railway.app)
    MONSTRUO_API_KEY    (requerida — auth admin del endpoint)

Sprint 84.5.5 — Hilo Manus Ejecutor — 2026-05-04.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import urllib.request
import urllib.error

# Importar las semillas del módulo del kernel
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from kernel.seeds_sprint_84_5 import SEEDS_SPRINT_84_5  # noqa: E402


KERNEL_URL = os.environ.get(
    "KERNEL_URL",
    "https://el-monstruo-kernel-production.up.railway.app",
).rstrip("/")
ADMIN_KEY = os.environ.get("MONSTRUO_API_KEY", "").strip()
ENDPOINT = f"{KERNEL_URL}/v1/error-memory/seed"
TIMEOUT_S = 20


def _post_seed(seed: dict) -> tuple[int, dict | str]:
    """POST de un payload seed al endpoint admin."""
    payload = {
        "error_signature": seed["error_signature"],
        "sanitized_message": seed["sanitized_message"],
        "resolution": seed["resolution"],
        "confidence": float(seed["confidence"]),
        "module": seed.get("module", "manual.seed"),
        "action": seed.get("action", ""),
        "status": seed.get("status", "resolved"),
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": ADMIN_KEY,
            "User-Agent": "monstruo-seed-script/84.5.5",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw
    except urllib.error.URLError as e:
        return -1, f"URLError: {e.reason}"


def main() -> int:
    if not ADMIN_KEY:
        print("ERROR: MONSTRUO_API_KEY no está en el entorno.", file=sys.stderr)
        return 2

    print(f"=== Sprint 84.5.5 — Sembrando {len(SEEDS_SPRINT_84_5)} semillas ===")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Auth: X-API-Key (len={len(ADMIN_KEY)})")
    print()

    ok = 0
    failed = 0
    results: list[dict] = []

    for i, seed in enumerate(SEEDS_SPRINT_84_5, start=13):
        sig = seed["error_signature"]
        print(f"[{i}va semilla] POST {sig[:60]}…")
        t0 = time.time()
        status, body = _post_seed(seed)
        elapsed = (time.time() - t0) * 1000
        record = {
            "ordinal": f"{i}va",
            "error_signature": sig,
            "http_status": status,
            "response": body,
            "elapsed_ms": round(elapsed, 1),
        }
        results.append(record)
        if status == 200 and isinstance(body, dict) and body.get("ok"):
            print(
                f"   ✓ {body.get('seeded', 'unknown')} "
                f"(occurrences={body.get('occurrences')}, "
                f"{elapsed:.0f}ms)"
            )
            ok += 1
        else:
            print(f"   ✗ http={status} body={body!r} ({elapsed:.0f}ms)")
            failed += 1
        print()

    print("=== Resumen ===")
    print(f"OK:     {ok}/{len(SEEDS_SPRINT_84_5)}")
    print(f"Failed: {failed}/{len(SEEDS_SPRINT_84_5)}")

    out_path = HERE / "seed_sprint_84_5_results.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nResultados guardados en: {out_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
