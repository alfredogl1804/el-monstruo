#!/usr/bin/env python3
"""
aggregator.py — Genome Vivo Aggregator (Sprint 91 F5).

Lee los outputs binarios de F1-F4 y produce un único JSON canónico:

  _genome_out/genome_now.json

Campos clave:
  - meta.generated_at
  - meta.binario_100 (bool): True si todos los scanners reportaron coverage_match
  - github / railway / supabase / live24h: resúmenes ejecutivos + datos completos
  - cross_validation: hallazgos del cruzado entre fuentes

Idempotente: corre N veces sin efectos colaterales.

Autor: Manus — Sprint 91 F5
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "_genome_out"
OUT_FILE = OUT_DIR / "genome_now.json"


def load_or_empty(name: str) -> dict:
    p = OUT_DIR / name
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception as e:
        print(f"  [WARN] {p} corrupto: {e}", flush=True)
        return {}


def cross_validate(gh: dict, rly: dict, sb: dict, live: dict) -> dict:
    """Validación cruzada entre fuentes."""
    findings: list[dict] = []

    # 1. ¿Cada repo Railway aparece en GitHub?
    gh_repos = {r.get("full_name") or r.get("name") for r in gh.get("repos", [])}
    railway_repos: set[str] = set()
    for ws in rly.get("workspaces", []):
        for proj in ws.get("projects", []):
            for svc in proj.get("services", []):
                for inst in svc.get("instances", []):
                    repo = (inst.get("source") or {}).get("repo")
                    if repo:
                        railway_repos.add(repo)
                    deploy_repo = (inst.get("deploy") or {}).get("repo")
                    if deploy_repo:
                        railway_repos.add(deploy_repo)
    railway_repos = {r for r in railway_repos if r}

    missing = railway_repos - gh_repos
    if missing:
        findings.append(
            {
                "kind": "railway_repos_not_in_github",
                "severity": "warning",
                "message": f"{len(missing)} repos referenciados en Railway no aparecen en GitHub scanner",
                "items": sorted(missing)[:20],
            }
        )

    # 2. ¿Hay drift > 7 días?
    drift = live.get("drift_services_over_7d_count", 0)
    if drift > 0:
        findings.append(
            {
                "kind": "railway_drift_over_7d",
                "severity": "info",
                "message": f"{drift} servicios Railway con último deploy > 7 días",
                "count": drift,
            }
        )

    # 3. ¿Coverage_match en todos?
    matches = {
        "github": gh.get("coverage_match", False) if gh else False,
        "railway": rly.get("coverage_match", False) if rly else False,
        "supabase": sb.get("coverage_match", False) if sb else False,
        "live24h": live.get("coverage_match", False) if live else False,
    }

    return {
        "findings": findings,
        "findings_count": len(findings),
        "coverage_match_per_source": matches,
    }


def aggregate() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    print(f"[{started}] Agregando genome_now...", flush=True)

    gh = load_or_empty("github.json")
    rly = load_or_empty("railway.json")
    sb = load_or_empty("supabase.json")
    live = load_or_empty("live24h.json")

    cross = cross_validate(gh, rly, sb, live)

    binario_100 = (
        cross["coverage_match_per_source"]["github"]
        and cross["coverage_match_per_source"]["railway"]
        and cross["coverage_match_per_source"]["supabase"]
        and cross["coverage_match_per_source"]["live24h"]
    )

    # Resúmenes ejecutivos
    summaries = {
        "github": {
            "repos_total": gh.get("repos_count", 0),
            "expected_total": gh.get("expected_total_count", 0),
            "match": gh.get("coverage_match", False),
            "scanned_at": gh.get("finished_at"),
        },
        "railway": {
            "workspaces": rly.get("workspaces_count", 0),
            "projects": rly.get("projects_count", 0),
            "total_services": rly.get("total_services", 0),
            "expected_services": rly.get("expected_total_services", 0),
            "match": rly.get("coverage_match", False),
            "scanned_at": rly.get("finished_at"),
        },
        "supabase": {
            "schemas": sb.get("schemas_count", 0),
            "tables": sb.get("tables_count", 0),
            "functions": sb.get("functions_count", 0),
            "extensions": sb.get("extensions_count", 0),
            "buckets": sb.get("buckets_count", 0),
            "migrations": sb.get("migrations_count", 0),
            "indexes": sb.get("indexes_count", 0),
            "triggers": sb.get("triggers_count", 0),
            "match": sb.get("coverage_match", False),
            "scanned_at": sb.get("finished_at"),
        },
        "live24h": {
            "github_commits_24h": live.get("github_commits_24h_count", 0),
            "railway_deploys_24h": live.get("railway_deploys_24h_count", 0),
            "supabase_migrations_24h": live.get("supabase_migrations_24h_count", 0),
            "drift_over_7d": live.get("drift_services_over_7d_count", 0),
            "kernel_health": live.get("kernel_health", {}).get("status", "unknown"),
            "match": live.get("coverage_match", False),
            "scanned_at": live.get("finished_at"),
        },
    }

    finished = datetime.now(timezone.utc).isoformat()

    return {
        "version": 1,
        "meta": {
            "generated_at": finished,
            "generated_by": "scripts/genome_live/aggregator.py",
            "binario_100": binario_100,
            "sprint": "Sprint 91 — Mapa Vivo 100% del Monstruo",
            "branch": "feat/sprint-91-mapa-vivo-100",
        },
        "summaries": summaries,
        "cross_validation": cross,
        "github": gh,
        "railway": rly,
        "supabase": sb,
        "live24h": live,
    }


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    result = aggregate()
    OUT_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    print("\nAGGREGATOR RESUMEN")
    print(f"  binario_100        : {result['meta']['binario_100']}")
    print(f"  github.match       : {result['summaries']['github']['match']}")
    print(f"  railway.match      : {result['summaries']['railway']['match']}")
    print(f"  supabase.match     : {result['summaries']['supabase']['match']}")
    print(f"  live24h.match      : {result['summaries']['live24h']['match']}")
    print(f"  cross_findings     : {result['cross_validation']['findings_count']}")
    print(f"  output             : {OUT_FILE}")
    print(f"  size               : {OUT_FILE.stat().st_size:,} bytes")

    return 0 if result["meta"]["binario_100"] else 1


if __name__ == "__main__":
    sys.exit(main())
