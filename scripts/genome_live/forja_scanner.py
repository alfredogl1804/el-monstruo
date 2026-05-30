#!/usr/bin/env python3
"""
forja_scanner.py — Scanner del Forja Protocol (tablero-campana + forja-mcp).

Consulta GitHub API para obtener el estado del Forja Protocol:
  - Firmas ed25519 (SubEnvelopes)
  - Estado del tablero-campana (branches, último commit, PRs)
  - Estado del forja-mcp gateway
  - Doctrinas firmadas en el monorepo (forja_omega_tramo_1/)

Verificación binaria:
  - El repo tablero-campana existe y responde
  - El directorio forja_omega_tramo_1/ tiene contenido

Output: _genome_out/forja.json

Autor: Manus — Sprint 91.11
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "_genome_out"

# Carga .env si existe
ENV_PATH = ROOT / ".env"
if ENV_PATH.exists():
    for raw in ENV_PATH.read_text().splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            k, v = raw.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or ""
if not GH_TOKEN:
    sys.exit("ERROR: GITHUB_TOKEN o GITHUB_PERSONAL_ACCESS_TOKEN requerido")

BASE = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "monstruo-genome-scanner",
}
USER = "alfredogl1804"

FORJA_REPOS = ["tablero-campana", "forja-mcp"]
FORJA_LOCAL_DIR = ROOT / "forja_omega_tramo_1"


def gh_get(path: str, params: dict | None = None) -> requests.Response:
    """GET con manejo de rate limit."""
    url = path if path.startswith("http") else f"{BASE}{path}"
    for attempt in range(3):
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if r.status_code == 403 and "rate limit" in r.text.lower():
            time.sleep(30)
            continue
        return r
    return r  # type: ignore


def scan_forja_repo(repo_name: str) -> dict[str, Any]:
    """Escanea un repo del Forja Protocol."""
    # Repo info
    r = gh_get(f"/repos/{USER}/{repo_name}")
    if r.status_code != 200:
        return {"name": repo_name, "status": "not_found", "error": r.status_code}

    repo = r.json()

    # Last commit
    default_branch = repo.get("default_branch", "main")
    r = gh_get(f"/repos/{USER}/{repo_name}/commits", params={"per_page": 1, "sha": default_branch})
    last_commit = None
    if r.status_code == 200:
        commits = r.json()
        if commits:
            last_commit = {
                "date": commits[0].get("commit", {}).get("committer", {}).get("date"),
                "message": (commits[0].get("commit", {}).get("message", ""))[:100],
                "sha": commits[0].get("sha", "")[:8],
            }

    # Branches
    r = gh_get(f"/repos/{USER}/{repo_name}/branches", params={"per_page": 100})
    branches = []
    if r.status_code == 200:
        branches = [b["name"] for b in r.json()]

    # Open PRs
    r = gh_get(f"/repos/{USER}/{repo_name}/pulls", params={"state": "open", "per_page": 10})
    open_prs = 0
    if r.status_code == 200:
        open_prs = len(r.json())

    # Languages (lines estimate)
    r = gh_get(f"/repos/{USER}/{repo_name}/languages")
    lines_estimated = 0
    languages = {}
    if r.status_code == 200:
        languages = r.json()
        lines_estimated = sum(languages.values()) // 40

    return {
        "name": repo_name,
        "status": "active" if not repo.get("archived") else "archived",
        "description": (repo.get("description") or "")[:200],
        "default_branch": default_branch,
        "last_commit": last_commit,
        "branches_count": len(branches),
        "branches": branches[:20],
        "open_prs": open_prs,
        "lines_estimated": lines_estimated,
        "languages": languages,
        "private": repo.get("private", False),
        "updated_at": repo.get("updated_at"),
    }


def scan_local_forja() -> dict[str, Any]:
    """Escanea el directorio forja_omega_tramo_1/ local."""
    if not FORJA_LOCAL_DIR.exists():
        return {"exists": False, "doctrines_count": 0, "files": 0, "lines": 0}

    # Count files
    all_files = list(FORJA_LOCAL_DIR.rglob("*"))
    files = [f for f in all_files if f.is_file() and not f.name.startswith(".")]

    # Count lines
    total_lines = 0
    for f in files:
        if f.suffix in (".md", ".py", ".sh", ".json", ".jsonl", ".yaml", ".yml", ".txt"):
            try:
                total_lines += len(f.read_text(errors="ignore").splitlines())
            except Exception:
                pass

    # Count doctrines in bitacora.jsonl
    doctrines_count = 0
    bitacora = FORJA_LOCAL_DIR / "bitacora.jsonl"
    if bitacora.exists():
        try:
            doctrines_count = sum(1 for line in bitacora.read_text().splitlines() if line.strip())
        except Exception:
            pass

    # Check for signed blocks
    index_file = FORJA_LOCAL_DIR / "bitacora_index.md"
    signed_blocks = 0
    if index_file.exists():
        try:
            content = index_file.read_text()
            signed_blocks = content.count("FIRMADO") + content.count("firmado")
        except Exception:
            pass

    return {
        "exists": True,
        "doctrines_count": doctrines_count,
        "signed_blocks": signed_blocks,
        "files": len(files),
        "lines": total_lines,
        "has_bitacora": bitacora.exists(),
        "has_index": index_file.exists(),
        "has_scripts": (FORJA_LOCAL_DIR / "scripts").exists(),
    }


def scan() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()

    # Scan remote repos
    print("  Escaneando repos Forja...", flush=True)
    repos_data: list[dict[str, Any]] = []
    for repo_name in FORJA_REPOS:
        print(f"    → {repo_name}...", flush=True)
        data = scan_forja_repo(repo_name)
        repos_data.append(data)
        time.sleep(0.5)

    # Scan local forja directory
    print("  Escaneando forja_omega_tramo_1/ local...", flush=True)
    local_forja = scan_local_forja()

    finished = datetime.now(timezone.utc).isoformat()

    # Coverage: tablero-campana exists + local forja has content
    tablero_ok = any(r["name"] == "tablero-campana" and r.get("status") != "not_found" for r in repos_data)
    local_ok = local_forja.get("exists", False) and local_forja.get("doctrines_count", 0) > 0
    coverage_match = tablero_ok and local_ok

    return {
        "scanner": "forja",
        "version": 1,
        "started_at": started,
        "finished_at": finished,
        "coverage_match": coverage_match,
        "repos": repos_data,
        "local_forja": local_forja,
        "total_doctrines": local_forja.get("doctrines_count", 0),
        "total_signed_blocks": local_forja.get("signed_blocks", 0),
    }


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    out_file = OUT_DIR / "forja.json"

    result = scan()
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print("\nFORJA SCAN RESUMEN")
    print(f"  repos escaneados  : {len(result['repos'])}")
    print(f"  tablero-campana   : {next((r['status'] for r in result['repos'] if r['name']=='tablero-campana'), 'N/A')}")
    print(f"  forja-mcp         : {next((r['status'] for r in result['repos'] if r['name']=='forja-mcp'), 'N/A')}")
    print(f"  local doctrines   : {result['total_doctrines']}")
    print(f"  signed blocks     : {result['total_signed_blocks']}")
    print(f"  match             : {result['coverage_match']}")
    print(f"  output            : {out_file}")

    return 0 if result["coverage_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
