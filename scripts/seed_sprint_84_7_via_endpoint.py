"""
Persiste las 8 semillas Sprint 84.7 (19va a 26va) vía POST /v1/error-memory/seed.

USO:
    export MONSTRUO_API_KEY="..."
    python3 scripts/seed_sprint_84_7_via_endpoint.py [base_url]

Por defecto usa https://el-monstruo-kernel-production.up.railway.app
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
import urllib.error

# Importar las 8 semillas
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kernel.seeds_sprint_84_7 import SEEDS_SPRINT_84_7  # noqa: E402


def adapt_seed_to_endpoint_schema(seed: dict) -> dict:
    """Mapea seed dict (Sprint 84.7) al schema del endpoint /seed.

    Schema endpoint:
        Required: error_signature, sanitized_message, resolution
        Optional: confidence, module, action, error_type, status
    """
    fix_steps = seed.get("fix_steps", [])
    prevention = seed.get("prevention", "")
    resolution_lines = []
    if fix_steps:
        resolution_lines.append("FIX:")
        for step in fix_steps:
            resolution_lines.append(f"  - {step}")
    if prevention:
        resolution_lines.append(f"PREVENTION: {prevention}")
    resolution = "\n".join(resolution_lines) or "(no resolution provided)"

    return {
        "error_signature": seed["error_signature"],
        "sanitized_message": seed.get("description", "")[:1000],
        "resolution": resolution[:2000],
        "confidence": float(seed.get("confidence", 0.85)),
        "module": "sprint_84_7.seeds",
        "error_type": "SeededRule",
        "status": "resolved",
    }


def post_seed(base_url: str, api_key: str, seed: dict) -> dict:
    """POST a /v1/error-memory/seed con un seed dict (mapeado al schema)."""
    url = f"{base_url.rstrip('/')}/v1/error-memory/seed"
    payload = adapt_seed_to_endpoint_schema(seed)
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            data["_http_status"] = resp.status
            data["_latency_ms"] = int((time.time() - t0) * 1000)
            return data
    except urllib.error.HTTPError as e:
        return {
            "_http_status": e.code,
            "_latency_ms": int((time.time() - t0) * 1000),
            "error": e.read().decode("utf-8", errors="ignore")[:500],
        }
    except Exception as e:
        return {
            "_http_status": 0,
            "_latency_ms": int((time.time() - t0) * 1000),
            "error": str(e),
        }


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://el-monstruo-kernel-production.up.railway.app"
    api_key = os.environ.get("MONSTRUO_API_KEY", "").strip()
    if not api_key:
        print("ERROR: MONSTRUO_API_KEY no definido en env")
        sys.exit(1)

    print(f"Sembrando {len(SEEDS_SPRINT_84_7)} semillas Sprint 84.7 a {base_url}")
    print("-" * 80)

    inserted, updated, failed = 0, 0, 0
    for i, seed in enumerate(SEEDS_SPRINT_84_7, start=19):  # 19-26
        sig = seed["error_signature"]
        result = post_seed(base_url, api_key, seed)
        # Endpoint devuelve `seeded` no `status`
        status = result.get("seeded", result.get("status", "?"))
        if result.get("_http_status") == 200 and status in ("inserted", "updated"):
            if status == "inserted":
                inserted += 1
            else:
                updated += 1
            print(f"  [{i:>2}va] {status:>8s}  {result['_latency_ms']:>4d}ms  {sig}")
        else:
            failed += 1
            err = result.get("error", "")[:120]
            print(f"  [{i:>2}va] FAILED   {result['_latency_ms']:>4d}ms  {sig}")
            print(f"         http={result.get('_http_status')} err={err}")

    print("-" * 80)
    print(f"Total: inserted={inserted}  updated={updated}  failed={failed}  / {len(SEEDS_SPRINT_84_7)}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
