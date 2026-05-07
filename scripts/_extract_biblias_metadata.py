#!/usr/bin/env python3
"""Extrae metadata estructurada de las 21 biblias canónicas de docs/biblias_agentes_2026/.

Para cada biblia, extrae:
- nombre canónico (primer H1)
- proveedor (busca patrones "Proveedor:", "Provider:", etc.)
- primeros 5 H2 (categorías de contenido)
- líneas que mencionan capabilities/capacidades

Output: JSON pretty con un objeto por biblia.

Uso:
    python3 scripts/_extract_biblias_metadata.py > /tmp/biblias_metadata.json
"""

import json
import os
import re
import sys

BIBLIA_DIR = os.path.expanduser("~/el-monstruo/docs/biblias_agentes_2026")


def extract(path: str) -> dict:
    with open(path) as f:
        content = f.read()
    lines = content.split("\n")
    head_lines = lines[:200]
    h1 = [l for l in head_lines if l.startswith("# ")][:1]
    h2 = [l for l in head_lines if l.startswith("## ")][:8]
    prov = [
        l for l in head_lines
        if re.search(r"(Proveedor|Provider|Empresa|Company|Creator|Maker|Por\b)\s*[:\-]", l, re.I)
    ][:2]
    cap = [
        l for l in head_lines
        if re.search(r"(Capabilit|Capacidad|Función|Use Cases?|Casos de Uso)", l, re.I)
    ][:5]
    auth = [
        l for l in head_lines
        if re.search(r"(API[\s-]?[Kk]ey|OAuth|Auth\w*|Suscripci|Subscription|Free Tier)", l, re.I)
    ][:3]
    return {
        "file": os.path.basename(path),
        "h1": h1,
        "h2_first8": h2,
        "provider_line": prov,
        "capability_hint": cap,
        "auth_hint": auth,
        "size_bytes": len(content),
    }


def main():
    out = []
    for fn in sorted(os.listdir(BIBLIA_DIR)):
        if not fn.startswith("BIBLIA_") or not fn.endswith(".md"):
            continue
        path = os.path.join(BIBLIA_DIR, fn)
        out.append(extract(path))
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
