"""
Factory Smoke Test — generador de evidencia para SPR-FACTORY-AGGREGATORS-000
=============================================================================

Levanta una FastAPI minimal con factory_router, hace 4 llamadas de evidencia,
y guarda el output en `bridge/missions/SPR-FACTORY-AGGREGATORS-000/evidence/`.

Reemplaza `curl` real para evitar levantar un kernel completo (con todas sus
dependencias supabase/openai) que requeriría secrets en runtime de tests.

Uso:
  .venv-test/bin/python scripts/factory_smoke_test.py
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from kernel.factory_routes import factory_router


def main() -> int:
    out_dir = Path("bridge/missions/SPR-FACTORY-AGGREGATORS-000/evidence")
    out_dir.mkdir(parents=True, exist_ok=True)

    app = FastAPI(title="Factory Smoke Test")
    app.include_router(factory_router)
    client = TestClient(app)

    endpoints = [
        ("constellation", "/v1/factory/constellation"),
        ("constellation_tier_core", "/v1/factory/constellation?tier=core"),
        ("economy_24h", "/v1/factory/economy?window=24h"),
        ("economy_lifetime", "/v1/factory/economy?window=lifetime"),
        ("timeline_dsc_only", "/v1/factory/timeline?types=dsc_signed&limit=10"),
        ("timeline_full", "/v1/factory/timeline?limit=20"),
        ("diff", "/v1/factory/diff"),
    ]

    print("=" * 70)
    print("FACTORY SMOKE TEST — Cognitive Republic Aggregator (DSC-G-019)")
    print("=" * 70)

    for name, path in endpoints:
        print(f"\n→ {path}")
        resp = client.get(path)
        out_path = out_dir / f"{name}.json"
        body = resp.json() if resp.status_code in (200,) else {"status": resp.status_code, "text": resp.text}
        out_path.write_text(json.dumps(body, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  status={resp.status_code} size={len(resp.text)}B → {out_path}")

        # Spot-check
        if name == "constellation":
            print(f"  nodes_total={body.get('totals', {}).get('nodes_total')}")
            print(f"  binario_100={body.get('binario_100')}")
        elif name == "economy_24h":
            mq = body.get("data_quality", {})
            print(f"  coverage={mq.get('coverage')} missing={len(mq.get('missing_metrics', []))}")
        elif name == "timeline_dsc_only":
            t = body.get("totals", {})
            print(f"  dscs_signed={t.get('dscs_signed')} events_returned={t.get('events_returned')}")
        elif name == "diff":
            print(f"  binario_100_live={body.get('binario_100_live')}")
            print(f"  drift_count={body.get('drift_count')}")

    print("\n" + "=" * 70)
    print(f"Evidence saved to: {out_dir}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
