#!/usr/bin/env python3.11
"""
Debug del error rpc_validation observado en el primer run del Catastro
(37/37 modelos fallaron). Llama UNA RPC real con un modelo sintético y
captura el error_message completo para diagnóstico.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from supabase import create_client  # type: ignore


def main() -> int:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        or os.environ.get("SUPABASE_SERVICE_KEY", "")
    ).strip()
    if not (url and key):
        print("ERROR: SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY requeridas", file=sys.stderr)
        return 1

    client = create_client(url, key)

    p_modelo = {
        "id": "debug-test-model-001",
        "nombre": "Debug Test Model",
        "proveedor": "DebugLab",
        "macroarea": "llm_frontier",
        "dominios": ["llm_frontier"],
        "estado": "production",
        "quality_score": 0.5,
        "cost_efficiency": 0.5,
        "speed_score": 0.5,
        "reliability_score": 0.5,
        "brand_fit": 0.5,
        "sovereignty": 0.5,
        "velocity": 0.5,
        "trono_global": 50.0,
        "trono_delta": 0.0,
        "confidence": 0.7,
        "open_weights": False,
    }
    p_evento = {
        "tipo": "new_model",
        "prioridad": "info",
        "modelo_id": "debug-test-model-001",
        "descripcion": "debug call to expose rpc_validation error",
    }
    p_trust_deltas = {"openrouter": 0.0}

    print("=== Llamando catastro_apply_quorum_outcome ===")
    try:
        resp = client.rpc(
            "catastro_apply_quorum_outcome",
            {"p_modelo": p_modelo, "p_evento": p_evento, "p_trust_deltas": p_trust_deltas},
        ).execute()
        print(f"OK data={getattr(resp, 'data', None)}")
    except Exception as exc:  # noqa: BLE001
        print(f"EXCEPTION: {type(exc).__name__}: {exc}")
        for attr in ("args", "message", "response", "code", "details", "hint"):
            v = getattr(exc, attr, None)
            if v:
                print(f"  .{attr}: {v}")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
