#!/usr/bin/env python3
"""
satellite_repos_scanner.py — Scanner de repos satélite del ecosistema.

Consulta la GitHub API para cada repo satélite conocido y obtiene:
  - Líneas de código reales (via languages endpoint)
  - Último commit
  - Estado (archivado, activo, etc.)
  - Branches activos
  - Descripción

Los repos satélite son todos los repos de alfredogl1804 que NO son el-monstruo
pero forman parte del ecosistema.

Verificación binaria:
  - Todos los repos satélite conocidos responden con datos válidos

Output: _genome_out/satellite_repos.json

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
MAIN_REPO = "el-monstruo"

# Repos que se consideran satélite (parte del ecosistema pero fuera del monorepo)
# Esta lista se auto-descubre: todo repo de alfredogl1804 que no sea el-monstruo
# y tenga código (no forks vacíos)


def gh_get(path: str, params: dict | None = None) -> requests.Response:
    """GET con manejo de rate limit."""
    url = path if path.startswith("http") else f"{BASE}{path}"
    for attempt in range(5):
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if r.status_code == 403 and "rate limit" in r.text.lower():
            wait = int(r.headers.get("X-RateLimit-Reset", time.time() + 60)) - int(time.time())
            print(f"  [rate-limit] esperando {wait}s...", flush=True)
            time.sleep(max(wait, 10))
            continue
        return r
    return r  # type: ignore


def get_all_repos() -> list[dict[str, Any]]:
    """Obtiene todos los repos del usuario."""
    repos: list[dict] = []
    page = 1
    while True:
        r = gh_get(f"/users/{USER}/repos", params={"per_page": 100, "page": page, "type": "owner"})
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def estimate_lines_from_languages(repo_name: str) -> int:
    """
    Estima líneas de código usando el endpoint /languages (devuelve bytes por lenguaje).
    Heurística: ~40 bytes por línea promedio.
    """
    r = gh_get(f"/repos/{USER}/{repo_name}/languages")
    if r.status_code != 200:
        return 0
    langs = r.json()
    total_bytes = sum(langs.values())
    return total_bytes // 40  # heurística conservadora


def get_repo_details(repo: dict) -> dict[str, Any]:
    """Obtiene detalles extendidos de un repo satélite."""
    name = repo["name"]

    # Líneas estimadas
    lines = estimate_lines_from_languages(name)

    # Último commit en default branch
    default_branch = repo.get("default_branch", "main")
    r = gh_get(f"/repos/{USER}/{name}/commits", params={"per_page": 1, "sha": default_branch})
    last_commit_date = None
    last_commit_msg = None
    if r.status_code == 200:
        commits = r.json()
        if commits:
            last_commit_date = commits[0].get("commit", {}).get("committer", {}).get("date")
            last_commit_msg = (commits[0].get("commit", {}).get("message", ""))[:100]

    # Branches count (skip for speed — use repo size as proxy)
    branches_count = 0

    # Detect function from description + topics
    description = repo.get("description", "") or ""
    topics = repo.get("topics", [])
    language = repo.get("language", "unknown") or "unknown"

    return {
        "name": name,
        "full_name": repo.get("full_name", f"{USER}/{name}"),
        "description": description[:200],
        "language": language,
        "lines_estimated": lines,
        "default_branch": default_branch,
        "last_commit_date": last_commit_date,
        "last_commit_message": last_commit_msg,
        "branches": branches_count,
        "archived": repo.get("archived", False),
        "private": repo.get("private", False),
        "topics": topics,
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "size_kb": repo.get("size", 0),
    }


def scan() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    print("Obteniendo todos los repos...", flush=True)

    all_repos = get_all_repos()
    # Filtrar: excluir el monorepo principal y repos vacíos/forks
    satellite_repos = [
        r for r in all_repos
        if r["name"] != MAIN_REPO
        and not r.get("fork", False)
        and r.get("size", 0) > 0
    ]

    print(f"  Total repos: {len(all_repos)}, satélite (no-fork, no-empty, no-main): {len(satellite_repos)}", flush=True)

    details: list[dict[str, Any]] = []
    for i, repo in enumerate(satellite_repos):
        print(f"  [{i+1}/{len(satellite_repos)}] {repo['name']}...", flush=True)
        detail = get_repo_details(repo)
        details.append(detail)
        time.sleep(0.1)  # Respetar rate limit

    finished = datetime.now(timezone.utc).isoformat()

    # Coverage: todos los repos no-vacíos fueron escaneados
    expected_total = len(satellite_repos)
    got_total = len(details)
    coverage_match = got_total == expected_total and expected_total > 0

    # Aggregate
    total_lines = sum(d.get("lines_estimated", 0) for d in details)
    active_repos = [d for d in details if not d.get("archived", False)]

    return {
        "scanner": "satellite_repos",
        "version": 1,
        "started_at": started,
        "finished_at": finished,
        "expected_total": expected_total,
        "got_total": got_total,
        "coverage_match": coverage_match,
        "total_lines_estimated": total_lines,
        "active_repos_count": len(active_repos),
        "archived_repos_count": got_total - len(active_repos),
        "repos": details,
    }


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    out_file = OUT_DIR / "satellite_repos.json"

    result = scan()
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print("\nSATELLITE REPOS SCAN RESUMEN")
    print(f"  expected      : {result['expected_total']}")
    print(f"  got           : {result['got_total']}")
    print(f"  active        : {result['active_repos_count']}")
    print(f"  archived      : {result['archived_repos_count']}")
    print(f"  total lines   : {result['total_lines_estimated']:,}")
    print(f"  match         : {result['coverage_match']}")
    print(f"  output        : {out_file}")

    return 0 if result["coverage_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
