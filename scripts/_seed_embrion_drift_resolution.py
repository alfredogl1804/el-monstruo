"""Sembrar semilla en embrion_memoria del cierre MEGA-CATASTRO-DRIFT-RESOLUTION-001."""
from __future__ import annotations
import json, os, sys, urllib.request


def main() -> int:
    url = os.environ.get("SUPABASE_URL", "https://xsumzuhwmivjgftsneov.supabase.co")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get(
        "SUPABASE_SERVICE_ROLE_KEY"
    )
    if not key:
        print("[FAIL] SUPABASE_SERVICE_KEY no presente")
        return 1

    payload = {
        "hilo_origen": "manus_hilo_catastro",
        "tipo": "sprint_cierre",
        "contenido": {
            "sprint_id": "MEGA-CATASTRO-DRIFT-RESOLUTION-001",
            "estado": "DECLARADO_VERDE",
            "drifts_resueltos": ["DRIFT-001", "DRIFT-009", "DRIFT-012", "DRIFT-014"],
            "commits": ["6b53a50", "1054eed", "f21ca5a", "0d95bf8"],
            "frase_canonica": "MEGA-CATASTRO-DRIFT-RESOLUTION-001 — DECLARADO (4/4 drifts resueltos)",
            "hallazgos_binarios_clave": {
                "DRIFT-001": "archivo doctrinal contenia 15 objetivos en headers; rename + stub redirect ejecutados",
                "DRIFT-009": "Supabase prod confirma 98 agentes / 12 dominios; cifras 111/14 eran target aspiracional handoff 10-may",
                "DRIFT-012": "drift inverso al spec: 66 fisicos / 56 codigos unicos; 7 git mv + 20 entradas tipo B agregadas",
                "DRIFT-014": "10 biblias canonizadas en monstruo_biblias/; 8 sabios canonicos vs 10 biblias = 2 extras documentadas; deuda Copilot 365",
            },
            "pendientes_fuera_scope": [
                "DSC-S-005 conflict resolution (decision T1)",
                "rename DSC-G-001 14->15 (preservar trazabilidad)",
                "Biblia Copilot 365 (crear)",
                "Cierre Sprint 89 PREFLIGHT_BLOCKED (ahora desbloqueable)",
            ],
            "bridge_report": "bridge/manus_to_cowork_MEGA_CATASTRO_DRIFT_RESOLUTION_001_CIERRE_2026_05_12.md",
        },
    }

    req = urllib.request.Request(
        f"{url}/rest/v1/embrion_memoria",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            row_id = data[0].get("id") if data else None
            print(f"[OK] Semilla sembrada: id={row_id}")
            return 0
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
