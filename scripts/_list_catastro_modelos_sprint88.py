#!/usr/bin/env python3
"""
Sprint 88 - Lista los modelos actuales del Catastro (macroarea inteligencia)
para cruzar con propuesta de 18 agentes.

Uso:
    railway run --service el-monstruo-kernel python3 scripts/_list_catastro_modelos_sprint88.py
"""

from __future__ import annotations

import json
import os
import sys
from urllib import request


def main() -> int:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not (url and key):
        print("ERROR: SUPABASE_URL or SUPABASE_SERVICE_KEY not set", file=sys.stderr)
        return 1

    req = request.Request(
        f"{url}/rest/v1/catastro_modelos"
        "?select=id,nombre,proveedor,dominios,estado,trono_global,quorum_alcanzado"
        "&order=proveedor.asc,trono_global.desc.nullslast"
        "&limit=200",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"TOTAL_MODELOS: {len(data)}")
    print(f"\n{'PROVEEDOR':<20}  {'ID':<35}  {'ESTADO':<12}  {'TRONO':>6}  Q  DOMINIOS")
    print("-" * 110)
    for r in data:
        prov = r.get("proveedor", "")[:20]
        rid = r.get("id", "")[:35]
        estado = (r.get("estado") or "")[:12]
        trono = r.get("trono_global")
        trono_s = f"{trono:.1f}" if trono is not None else "  -  "
        q = "Y" if r.get("quorum_alcanzado") else "n"
        doms = ",".join(r.get("dominios") or [])[:30]
        print(f"{prov:<20}  {rid:<35}  {estado:<12}  {trono_s:>6}  {q}  {doms}")

    # Resumen por proveedor
    print("\n--- RESUMEN POR PROVEEDOR ---")
    from collections import Counter

    counts = Counter(r.get("proveedor") for r in data)
    for prov, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {prov:<25} {n}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
