#!/usr/bin/env python3
"""Sprint 88 Tarea 3.B.1 — Guardrail 2: verificar que los 7 repos NO tienen secrets.

Ejecuta `gh api repos/<owner>/<repo>/contents` para cada repo y reporta archivos.
Si detecta archivos sospechosos (.env, secrets.json, credentials.md, *.pem, etc.)
imprime ALERT y devuelve exit 1.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

ANSI = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")
OWNER = "alfredogl1804"

# Patrones SOSPECHOSOS — si aparecen, parar
SUSPICIOUS = re.compile(
    r"(\.env$|secrets?\.json$|credentials?\.md$|\.pem$|\.key$|"
    r"id_rsa|api[_-]?keys?|tokens?\.(json|txt|md)|"
    r"firebase[_-]?adminsdk|service[_-]?account|"
    r"DATABASE_URL|SUPABASE_SERVICE)",
    re.IGNORECASE,
)

REPOS = [
    "monstruo-hac--una-landing-premium-para--3_888e5d",
    "monstruo-hac--una-landing-premium-para--4_401772",
    "monstruo-hac--una-landing-premium-para--0_9e2e6c",
    "monstruo-hace-una-landing-premium-para--9_4a4e12",
    "monstruo-hace-una-landing-premium-para--7_f71120",
    "monstruo-hace-una-landing-premium-para--3_e85981",
    "monstruo-hace-una-landing-premium-para--7_c4ec87",
]


def list_contents(repo: str) -> list[str]:
    """Lista archivos en root del repo. Devuelve [] si vacío o error."""
    cmd = ["gh", "api", f"repos/{OWNER}/{repo}/contents"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return []
    try:
        clean = ANSI.sub("", r.stdout)
        data = json.loads(clean)
        return [item["path"] for item in data]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def main() -> int:
    print("Sprint 88 Tarea 3.B.1 — Guardrail 2: audit secrets pre-cleanup")
    print("=" * 70)
    alerts = 0
    for repo in REPOS:
        paths = list_contents(repo)
        suspicious_paths = [p for p in paths if SUSPICIOUS.search(p)]
        status = "OK" if not suspicious_paths else "ALERT"
        if suspicious_paths:
            alerts += 1
        print(f"\n[{status}] {repo}")
        print(f"  Files ({len(paths)}): {', '.join(paths) if paths else '(empty)'}")
        if suspicious_paths:
            print(f"  >>> SOSPECHOSOS: {suspicious_paths}")

    print()
    print("=" * 70)
    if alerts > 0:
        print(f"ALERTA: {alerts} repos con archivos sospechosos. PARAR delete.")
        return 1
    print(f"VERIFICADO: 0 archivos sospechosos en {len(REPOS)} repos. Safe to delete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
