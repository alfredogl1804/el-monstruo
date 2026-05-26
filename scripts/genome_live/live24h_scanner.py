#!/usr/bin/env python3
"""
live24h_scanner.py — Scanner Live 24h del Monstruo (Sprint 91 F4).

Lee los outputs ya generados por F1+F2+F3 y produce una vista unificada
de TODO lo que tocó el Monstruo en las últimas 24 horas:

  - GitHub: commits recientes por repo (sólo los con activity en ≤ 24 h)
  - Railway: deployments recientes en ≤ 24 h con estado
  - Supabase: migrations aplicadas en ≤ 24 h
  - Kernel: estado /health y conteos de cualquier endpoint que reporte counts
  - Drift detectado: servicios con commit_hash != commit en GitHub

Verificación binaria:
  - coverage_match = True si todas las fuentes leyeron correctamente
  - report.drift_detected: lista de servicios con drift > 7 días

Autor: Manus — Sprint 91
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
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

KERNEL_URL = os.environ.get("KERNEL_URL", "https://el-monstruo-kernel-production.up.railway.app")
NOW = datetime.now(timezone.utc)
T24H = NOW - timedelta(hours=24)
T7D = NOW - timedelta(days=7)


def parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


def load_json(name: str) -> dict | None:
    p = OUT_DIR / name
    if not p.exists():
        print(f"  [WARN] {p} no existe — corre F1/F2/F3 primero", flush=True)
        return None
    return json.loads(p.read_text())


def fetch_kernel_health() -> dict:
    try:
        r = requests.get(f"{KERNEL_URL}/health", timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def scan() -> dict[str, Any]:
    started = NOW.isoformat()
    print(f"[{started}] Iniciando scan Live 24h...", flush=True)

    gh = load_json("github.json") or {}
    rly = load_json("railway.json") or {}
    sb = load_json("supabase.json") or {}

    # 1. Commits recientes (≤24h) por repo
    # Sprint 91.6 hotfix — contrato correcto: el github_scanner produce
    # repo["branches"][i]["last_commit"], NO repo["last_commit"].
    print("  github commits 24h...", flush=True)
    gh_recent = []
    seen_shas: set[str] = set()
    for repo in gh.get("repos", []):
        repo_full = repo.get("full_name") or repo.get("name")
        for branch in repo.get("branches", []) or []:
            last_commit = branch.get("last_commit") or {}
            sha = last_commit.get("sha")
            ts = parse_iso(last_commit.get("date"))
            if not (ts and ts >= T24H):
                continue
            # Deduplicar por sha (mismo commit en múltiples branches del mismo repo)
            dedup_key = f"{repo_full}:{sha}" if sha else None
            if dedup_key and dedup_key in seen_shas:
                continue
            if dedup_key:
                seen_shas.add(dedup_key)
            gh_recent.append(
                {
                    "repo": repo_full,
                    "branch": branch.get("name") or repo.get("default_branch"),
                    "sha": sha,
                    "message": (last_commit.get("message") or "")[:200],
                    "date": last_commit.get("date"),
                    "author": last_commit.get("author"),
                }
            )
    gh_recent.sort(key=lambda x: x["date"] or "", reverse=True)
    print(f"    {len(gh_recent)} commits en últimas 24h", flush=True)

    # 2. Deploys recientes (≤24h) por servicio Railway
    print("  railway deploys 24h...", flush=True)
    rly_recent = []
    drift_warnings = []
    for ws in rly.get("workspaces", []):
        for proj in ws.get("projects", []):
            for svc in proj.get("services", []):
                for inst in svc.get("instances", []):
                    deploy = inst.get("deploy") or {}
                    ts = parse_iso(deploy.get("created_at"))
                    entry = {
                        "project": proj.get("name"),
                        "service": svc.get("name"),
                        "service_id": svc.get("id"),
                        "status": deploy.get("status"),
                        "commit_hash": deploy.get("commit_hash"),
                        "commit_message": deploy.get("commit_message"),
                        "branch": deploy.get("branch"),
                        "repo": deploy.get("repo"),
                        "deployed_at": deploy.get("created_at"),
                    }
                    if ts and ts >= T24H:
                        rly_recent.append(entry)
                    # detectar drift: deploy > 7 días
                    if ts and ts < T7D:
                        drift_warnings.append(
                            {
                                **entry,
                                "days_since_deploy": (NOW - ts).days,
                            }
                        )
    rly_recent.sort(key=lambda x: x["deployed_at"] or "", reverse=True)
    drift_warnings.sort(key=lambda x: x["days_since_deploy"], reverse=True)
    print(f"    {len(rly_recent)} deploys en últimas 24h", flush=True)
    print(f"    {len(drift_warnings)} servicios con drift > 7 días", flush=True)

    # 3. Migraciones recientes Supabase
    print("  supabase migrations 24h...", flush=True)
    sb_recent = []
    for mig in sb.get("migrations_recent", []):
        version = str(mig.get("version", ""))
        # versions usualmente formato YYYYMMDDHHMMSS
        if len(version) >= 8:
            try:
                year = int(version[:4])
                month = int(version[4:6])
                day = int(version[6:8])
                ts = datetime(year, month, day, tzinfo=timezone.utc)
                if ts >= T24H - timedelta(hours=24):  # buffer
                    sb_recent.append({"version": version, "name": mig.get("name")})
            except Exception:
                pass
    print(f"    {len(sb_recent)} migrations recientes", flush=True)

    # 4. Kernel /health
    print("  kernel /health...", flush=True)
    kernel_health = fetch_kernel_health()
    print(f"    kernel status: {kernel_health.get('status', 'unreachable')}", flush=True)

    finished = datetime.now(timezone.utc).isoformat()

    coverage_match = bool(gh) and bool(rly) and bool(sb) and "error" not in kernel_health

    result = {
        "scanner": "live24h",
        "version": 1,
        "started_at": started,
        "finished_at": finished,
        "window": {
            "now_utc": NOW.isoformat(),
            "since_24h": T24H.isoformat(),
            "since_7d": T7D.isoformat(),
        },
        "github_commits_24h": gh_recent,
        "github_commits_24h_count": len(gh_recent),
        "railway_deploys_24h": rly_recent,
        "railway_deploys_24h_count": len(rly_recent),
        "supabase_migrations_24h": sb_recent,
        "supabase_migrations_24h_count": len(sb_recent),
        "drift_services_over_7d": drift_warnings,
        "drift_services_over_7d_count": len(drift_warnings),
        "kernel_health": kernel_health,
        "coverage_match": coverage_match,
    }

    return result


def main() -> int:
    out_dir = OUT_DIR
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "live24h.json"

    result = scan()
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    print("\nLIVE 24H SCAN RESUMEN")
    print(f"  github_commits_24h    : {result['github_commits_24h_count']}")
    print(f"  railway_deploys_24h   : {result['railway_deploys_24h_count']}")
    print(f"  supabase_migrations   : {result['supabase_migrations_24h_count']}")
    print(f"  drift > 7d            : {result['drift_services_over_7d_count']}")
    print(f"  kernel reachable      : {'error' not in result['kernel_health']}")
    print(f"  coverage_match        : {result['coverage_match']}")
    print(f"  output                : {out_file}")
    print(f"  size                  : {out_file.stat().st_size:,} bytes")

    return 0 if result["coverage_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
