#!/usr/bin/env python3
"""Lee /tmp/railway_audit/*.json y produce un resumen tabular limpio."""

import glob
import json
import os

FILES = sorted(glob.glob("/tmp/railway_audit/*.json"))

print("=" * 100)
print("INVENTARIO RAILWAY — workspace alfredogl1804's Projects")
print("=" * 100)

resumen = {"total_proyectos": 0, "total_servicios": 0, "vivos": 0, "fallidos": 0, "muertos": 0, "items": []}

for fpath in FILES:
    name = os.path.basename(fpath).replace(".json", "")
    with open(fpath) as f:
        data = json.load(f)
    resumen["total_proyectos"] += 1
    proj_id = data.get("id", "")
    envs = (data.get("environments") or {}).get("edges") or []
    services = []
    for e in envs:
        env = e["node"]
        if env.get("name") != "production":
            continue
        for si_e in (env.get("serviceInstances") or {}).get("edges", []):
            si = si_e["node"]
            srv_name = si.get("serviceName", "?")
            depl = si.get("latestDeployment") or {}
            status = depl.get("status", "NO_DEPLOY")
            static_url = depl.get("staticUrl", "")
            meta = depl.get("meta") or {}
            repo = meta.get("repo", "")
            branch = meta.get("branch", "")
            commit = (meta.get("commitHash") or "")[:8]
            commit_msg = (meta.get("commitMessage") or "").replace("\n", " ")[:70]
            updated = depl.get("updatedAt") or depl.get("createdAt") or ""
            services.append(
                {
                    "name": srv_name,
                    "status": status,
                    "url": static_url,
                    "repo": repo,
                    "branch": branch,
                    "commit": commit,
                    "msg": commit_msg,
                    "updated": updated,
                }
            )
    resumen["items"].append({"project": name, "id": proj_id, "services": services})
    resumen["total_servicios"] += len(services)

    print(f"\n[{name}]  proj_id={proj_id[:8]}...")
    if not services:
        print("    (sin servicios production)")
    for s in services:
        st = s["status"]
        if st == "SUCCESS":
            resumen["vivos"] += 1
            mark = "✅"
        elif st in ("FAILED", "CRASHED"):
            resumen["fallidos"] += 1
            mark = "❌"
        elif st == "REMOVED":
            resumen["muertos"] += 1
            mark = "🪦"
        else:
            mark = "⚠️ "
        url = s["url"][:55] if s["url"] else "(sin url)"
        repo = s["repo"] or "(sin repo)"
        print(f"  {mark} {s['name']:30s} | {st:10s} | {url:55s} | {repo} @ {s['commit']}")
        if s["msg"]:
            print(f'      └─ "{s["msg"]}"  ({s["updated"][:10]})')

print("\n" + "=" * 100)
print(f"TOTAL: {resumen['total_proyectos']} proyectos · {resumen['total_servicios']} servicios")
print(f"  ✅ vivos: {resumen['vivos']}  |  ❌ fallidos: {resumen['fallidos']}  |  🪦 removidos: {resumen['muertos']}")
print("=" * 100)

with open("/tmp/railway_audit/resumen.json", "w") as f:
    json.dump(resumen, f, indent=2)
