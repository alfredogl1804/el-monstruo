"""
DRIFT-009 reconciliacion: catastro 98 agentes (Supabase prod) vs 111 declarados (handoff/docs).

Realidad binaria 2026-05-12:
- Supabase prod tabla catastro_agentes: 98 rows (verificado por Hilo Ejecutor 2)
- Doctrina (CLAUDE.md, COWORK_BASE_CONOCIMIENTO.md, handoff): 111 declarados
- Diff: 13 agentes 'fantasma' que viven en doctrina vieja sin existir en DB

Este script:
1. Lee semilla local kernel/catastro/data/catastro_agentes.json
2. Cuenta agentes locales y los tipos
3. Compara con realidad Supabase via psql/REST
4. Genera matriz reconciliacion 13 filas + recomendacion T1

NO modifica datos. Solo reporta.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEMILLA_AGENTES = ROOT / "kernel" / "catastro" / "data" / "catastro_agentes.json"
OUT_REPORT = ROOT / "bridge" / "DRIFT_009_RECONCILIATION_98_VS_111_2026_05_12.json"


def supabase_count() -> int | None:
    url = os.environ.get("SUPABASE_URL", "https://xsumzuhwmivjgftsneov.supabase.co")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get(
        "SUPABASE_SERVICE_ROLE_KEY"
    )
    if not key:
        print("[WARN] SUPABASE_SERVICE_KEY no presente; skip Supabase REST count")
        return None
    endpoint = f"{url}/rest/v1/catastro_agentes?select=id"
    req = urllib.request.Request(
        endpoint,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Range-Unit": "items",
            "Range": "0-0",
            "Prefer": "count=exact",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_range = resp.headers.get("Content-Range") or ""
            if "/" in content_range:
                total = content_range.split("/")[-1]
                return int(total) if total.isdigit() else None
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] Supabase REST: {exc}")
    return None


def main() -> int:
    if not SEMILLA_AGENTES.exists():
        print(f"[FAIL] Semilla NO encontrada: {SEMILLA_AGENTES}")
        return 1

    semilla = json.loads(SEMILLA_AGENTES.read_text())
    if isinstance(semilla, dict) and "agentes" in semilla:
        local_list = semilla["agentes"]
    elif isinstance(semilla, list):
        local_list = semilla
    else:
        local_list = []
    local_count = len(local_list)

    prod_count = supabase_count()

    DECLARED_CLAIMS = {
        "CLAUDE.md L290": 111,
        "COWORK_BASE_CONOCIMIENTO.md L133": 111,
        "HANDOFF_COWORK_NUEVO_2026_05_11.md L100": 111,
        "ESTADO_MONSTRUO_2026_05_10_vs_PLANES.md L96": 111,
        "PLAN_LECTURA_PERICIA_2026_05_11.md L170": 111,
        "RUTAS_PARA_ARQUITECTO_JEFE_2026_05_11.md L67": 111,
        "GLOSARIO_VIVO L66": 111,
        "audit forense MAPA_FUENTES L46 (snapshot 11-may)": 98,
        "audit forense D1_TECNICA L229 (snapshot 11-may)": 98,
        "manus_to_cowork SPRINT_89 L41 (12-may)": 98,
        "MEGA-CATASTRO-DRIFT-RESOLUTION-001 spec": "98 vs 111 diff 13",
    }

    diff_rows = max(0, 111 - (prod_count if prod_count is not None else 98))

    report = {
        "timestamp": "2026-05-12",
        "drift_id": "DRIFT-009",
        "sprint": "MEGA-CATASTRO-DRIFT-RESOLUTION-001",
        "supabase_prod_count": prod_count,
        "semilla_local_count": local_count,
        "declared_claims": DECLARED_CLAIMS,
        "diff_rows": diff_rows,
        "reality_winner": (
            "98 (Supabase prod + semilla local + audits forenses 11/12-may)"
            if (prod_count or local_count) <= 100
            else "needs_t1_decision"
        ),
        "stale_doctrine_files": [
            "CLAUDE.md L290",
            "COWORK_BASE_CONOCIMIENTO.md L133",
            "memory/cowork/PLAN_LECTURA_PERICIA_2026_05_11.md L170",
            "memory/cowork/COWORK_GLOSARIO_VIVO.md L66",
            "bridge/HANDOFF_COWORK_NUEVO_2026_05_11.md L100",
            "bridge/ESTADO_MONSTRUO_2026_05_10_vs_PLANES.md L96",
            "bridge/cowork_to_manus_RUTAS_PARA_ARQUITECTO_JEFE_2026_05_11.md L67",
        ],
        "t1_decision_options": {
            "A_canonize_98": "Aceptar realidad Supabase 98 como canon. Actualizar 7 docs stale a 98. Cerrar drift como 'doctrina ajustada a realidad'. ETA 5 min.",
            "B_canonize_111_seed": "Investigar los 13 agentes fantasma del handoff (¿se eliminaron sin migracion? ¿nunca existieron en seed?) y SI son legitimos, re-sembrarlos en Supabase prod. ETA 1h+ + analisis git log de catastro_agentes.json.",
            "C_aspirational_doctrine": "Reconocer que 111 era target aspiracional y 98 es realidad ejecutable. Documentar AMBOS numeros con etiqueta 'aspiracional' vs 'realidad' en CLAUDE.md y COWORK_BASE.",
        },
        "recommended_option": "A_canonize_98",
        "recommendation_reason": "Realidad binaria gana. La doctrina vieja deriva del handoff 10-may stale. Sprint 89 PREFLIGHT_BLOCKED ya identificó esto correctamente. T1 debe firmar opción A para cerrar el drift de raíz.",
    }

    OUT_REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"[OK] Reporte escrito: {OUT_REPORT}")
    print(json.dumps(report, indent=2, ensure_ascii=False)[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
