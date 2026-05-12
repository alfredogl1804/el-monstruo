#!/usr/bin/env python3
"""Siembra una semilla embrion_memoria para el cierre del sprint
DSC-G-008-V4-INDEX-DRIFT-ENFORCEMENT-001."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    sb_url = os.environ.get("SUPABASE_URL")
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get(
        "SUPABASE_SERVICE_ROLE"
    )
    if not sb_url or not sb_key:
        print("[err] missing SUPABASE_URL or SUPABASE_SERVICE_KEY", file=sys.stderr)
        return 2

    payload = {
        "tipo": "doctrina",
        "contenido": (
            "Sprint DSC-G-008-V4-INDEX-DRIFT-ENFORCEMENT-001 cerrado verde "
            "(4/4) por Manus Hilo Catastro el 2026-05-12. Implementado el "
            "contrato ejecutable propuesto durante el spike DSC-S-005-CANONICAL"
            "-AUDIT-001 ('drifts documentales sobreviven a su resolucion "
            "material si no hay enforcement automatizado'). Contratos nuevos: "
            "tools/_check_index_drift.py (12 tests verdes), "
            ".github/workflows/index-drift-audit.yml (cron weekly lunes "
            "06:00 UTC + auto-issue), entry actualizada en "
            "_dsc_contracts_index.yaml con version v4 estructurada. "
            "Suite total: 22/22 tests verdes (12 drift + 6 spec_lint + 4 "
            "dsc_contract_check). Estado vigente del corpus DSC al cierre: "
            "62 declared codes = 62 filesystem files, has_drift=false. "
            "Insight propio canonizado por Cowork T2-A como clausula 5 de "
            "DSC-G-008 v4."
        ),
        "hilo_origen": "catastro",
        "importancia": 8,
        "contexto": {
            "sprint": "DSC-G-008-V4-INDEX-DRIFT-ENFORCEMENT-001",
            "fecha": "2026-05-12",
            "estado": "verde",
            "doctrinas": [
                "DSC-G-008-v4",
                "DSC-G-009",
                "DSC-G-017",
                "DSC-S-016",
            ],
            "tipo_entrega": "contrato-ejecutable",
            "tests": "22-verdes",
            "insight_propio": "drifts documentales sobreviven a su resolucion material si no hay enforcement automatizado",
        },
    }
    data = json.dumps(payload).encode("utf-8")
    url = f"{sb_url.rstrip('/')}/rest/v1/embrion_memoria"
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            print(f"[ok] HTTP {resp.status}")
            try:
                arr = json.loads(body)
                if isinstance(arr, list) and arr:
                    print(f"[ok] id={arr[0].get('id')}")
            except Exception:
                pass
            return 0
    except urllib.error.HTTPError as exc:
        print(f"[err] HTTP {exc.code}: {exc.read().decode('utf-8')}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
