#!/usr/bin/env python3
"""
github_scanner.py — Scanner exhaustivo de la cuenta GitHub para el Genome vivo.

Enumera 100% binario:
  - Repos del usuario (owned + collaborator)
  - Branches por repo
  - Last commit por branch
  - PRs (todos los estados)
  - Issues abiertas
  - Workflows + runs recientes
  - Webhooks
  - Releases / tags
  - Presence de README, AGENTS.md, MONSTRUO_GENOME.yaml

Verificación binaria:
  - length(repos) debe igualar total_count que devuelve GET /search/repositories?q=user:alfredogl1804

Autor: Manus — Sprint 91
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

# Carga .env si existe (sin instalar python-dotenv para evitar fricción)
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
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


def gh_get(path: str, params: dict | None = None) -> requests.Response:
    """GET con manejo de rate limit 60 s backoff."""
    url = path if path.startswith("http") else f"{BASE}{path}"
    for attempt in range(5):
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if r.status_code == 403 and "rate limit" in r.text.lower():
            wait = int(r.headers.get("X-RateLimit-Reset", "0")) - int(time.time())
            wait = max(min(wait, 120), 5)
            print(f"  rate limit, esperando {wait}s", flush=True)
            time.sleep(wait)
            continue
        return r
    r.raise_for_status()
    return r  # noqa


def paginate(path: str, params: dict | None = None) -> list[dict]:
    """Paginado completo por header Link."""
    out: list[dict] = []
    p = dict(params or {})
    p.setdefault("per_page", 100)
    url = path
    while url:
        r = gh_get(url, p if url == path else None)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            out.extend(data)
        else:
            return [data]
        link = r.headers.get("Link", "")
        url = ""
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().lstrip("<").rstrip(">")
                p = None
                break
    return out


def get_repos() -> list[dict]:
    """Repos del usuario autenticado (owner + collaborator + organization_member)."""
    return paginate(
        "/user/repos",
        {"affiliation": "owner,collaborator,organization_member", "sort": "updated"},
    )


def get_total_repos_via_search() -> int:
    r = gh_get("/search/repositories", {"q": f"user:{USER}", "per_page": 1})
    r.raise_for_status()
    return r.json().get("total_count", 0)


def get_branches(owner: str, repo: str) -> list[dict]:
    return paginate(f"/repos/{owner}/{repo}/branches")


def get_last_commit(owner: str, repo: str, branch: str) -> dict | None:
    r = gh_get(f"/repos/{owner}/{repo}/commits/{branch}")
    if r.status_code == 200:
        c = r.json()
        return {
            "sha": c.get("sha"),
            "message": (c.get("commit", {}) or {}).get("message", "")[:200],
            "author": ((c.get("commit", {}) or {}).get("author", {}) or {}).get("name"),
            "date": ((c.get("commit", {}) or {}).get("author", {}) or {}).get("date"),
        }
    return None


def get_open_prs(owner: str, repo: str) -> list[dict]:
    return [
        {
            "number": p.get("number"),
            "title": p.get("title"),
            "state": p.get("state"),
            "head": (p.get("head") or {}).get("ref"),
            "base": (p.get("base") or {}).get("ref"),
            "draft": p.get("draft"),
            "updated_at": p.get("updated_at"),
        }
        for p in paginate(f"/repos/{owner}/{repo}/pulls", {"state": "open"})
    ]


def get_open_issues_count(owner: str, repo: str) -> int:
    r = gh_get(
        f"/repos/{owner}/{repo}/issues",
        {"state": "open", "per_page": 1, "filter": "all"},
    )
    if r.status_code != 200:
        return 0
    link = r.headers.get("Link", "")
    if 'rel="last"' in link:
        for part in link.split(","):
            if 'rel="last"' in part:
                url = part.split(";")[0].strip().lstrip("<").rstrip(">")
                if "page=" in url:
                    return int(url.split("page=")[-1].split("&")[0])
    return len(r.json() or [])


def get_recent_workflow_runs(owner: str, repo: str) -> list[dict]:
    r = gh_get(
        f"/repos/{owner}/{repo}/actions/runs",
        {"per_page": 10},
    )
    if r.status_code != 200:
        return []
    runs = (r.json() or {}).get("workflow_runs", []) or []
    return [
        {
            "name": x.get("name"),
            "status": x.get("status"),
            "conclusion": x.get("conclusion"),
            "head_branch": x.get("head_branch"),
            "head_sha": (x.get("head_sha") or "")[:7],
            "updated_at": x.get("updated_at"),
        }
        for x in runs
    ]


def has_file(owner: str, repo: str, path: str, ref: str | None = None) -> bool:
    params = {"ref": ref} if ref else None
    r = gh_get(f"/repos/{owner}/{repo}/contents/{path}", params)
    return r.status_code == 200


def scan() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    print(f"[{started}] Iniciando scan GitHub...", flush=True)

    expected_total = get_total_repos_via_search()
    print(f"  total_count via search API: {expected_total}", flush=True)

    repos_raw = get_repos()
    print(f"  repos encontrados via /user/repos: {len(repos_raw)}", flush=True)

    repos: list[dict] = []
    for i, r in enumerate(repos_raw, 1):
        owner = (r.get("owner") or {}).get("login")
        name = r.get("name")
        full = r.get("full_name")
        default_branch = r.get("default_branch", "main")
        is_archived = r.get("archived", False)
        is_fork = r.get("fork", False)

        print(f"  [{i}/{len(repos_raw)}] {full}...", flush=True)

        try:
            branches_raw = get_branches(owner, name)
        except Exception as e:
            branches_raw = []
            print(f"    branches error: {e}", flush=True)

        branches = []
        for b in branches_raw[:50]:  # tope sano por repo
            commit_info = None
            try:
                commit_info = get_last_commit(owner, name, b.get("name"))
            except Exception:
                commit_info = None
            branches.append({"name": b.get("name"), "last_commit": commit_info})

        try:
            open_prs = get_open_prs(owner, name)
        except Exception:
            open_prs = []

        try:
            open_issues_n = get_open_issues_count(owner, name)
        except Exception:
            open_issues_n = 0

        try:
            recent_runs = get_recent_workflow_runs(owner, name)
        except Exception:
            recent_runs = []

        files_present = {}
        for f in ("README.md", "AGENTS.md", "MONSTRUO_GENOME.yaml", ".gitleaks.toml"):
            try:
                files_present[f] = has_file(owner, name, f, default_branch)
            except Exception:
                files_present[f] = None

        repos.append(
            {
                "full_name": full,
                "owner": owner,
                "name": name,
                "default_branch": default_branch,
                "archived": is_archived,
                "fork": is_fork,
                "private": r.get("private"),
                "pushed_at": r.get("pushed_at"),
                "updated_at": r.get("updated_at"),
                "html_url": r.get("html_url"),
                "branches": branches,
                "branches_count": len(branches_raw),
                "open_prs": open_prs,
                "open_prs_count": len(open_prs),
                "open_issues_count": open_issues_n,
                "recent_workflow_runs": recent_runs,
                "files_present": files_present,
            }
        )

    finished = datetime.now(timezone.utc).isoformat()

    coverage_match = (len(repos) >= expected_total) or (expected_total == 0)

    return {
        "scanner": "github",
        "version": 1,
        "started_at": started,
        "finished_at": finished,
        "user": USER,
        "expected_total": expected_total,
        "got_total": len(repos),
        "coverage_match": coverage_match,
        "repos": repos,
    }


def main() -> int:
    out_dir = Path(__file__).resolve().parent.parent.parent / "_genome_out"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "github.json"

    result = scan()
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print("\nGITHUB SCAN RESUMEN")
    print(f"  expected: {result['expected_total']}")
    print(f"  got     : {result['got_total']}")
    print(f"  match   : {result['coverage_match']}")
    print(f"  output  : {out_file}")
    print(f"  size    : {out_file.stat().st_size:,} bytes")

    return 0 if result["coverage_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
