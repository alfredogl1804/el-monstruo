#!/usr/bin/env python3
"""Audita Railway: lista todos los proyectos, servicios, deployments y dominios.
Escribe inventario.json en /tmp/railway_audit/.
"""

import json
import os
import sys
from urllib.request import Request, urlopen

TOKEN = "aiwZzRUo_zw1MmWtO3E3aoCMVzVAFnrpQ6QqPFtvDrS"
ENDPOINT = "https://backboard.railway.com/graphql/v2"

LIST_PROJECTS_QUERY = """
query Me {
  me {
    workspaces {
      id
      name
      team {
        id
        projects {
          edges {
            node {
              id
              name
              createdAt
              updatedAt
            }
          }
        }
      }
    }
  }
}
"""

PROJECT_DETAIL_QUERY = """
query Project($id: String!) {
  project(id: $id) {
    id
    name
    services {
      edges {
        node {
          id
          name
          deployments(first: 1) {
            edges {
              node {
                id
                status
                staticUrl
                createdAt
                meta
              }
            }
          }
          serviceInstances {
            edges {
              node {
                domains {
                  customDomains { domain }
                  serviceDomains { domain }
                }
                source {
                  repo
                  image
                }
              }
            }
          }
        }
      }
    }
  }
}
"""


def gql(query, variables=None):
    body = {"query": query}
    if variables:
        body["variables"] = variables
    req = Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    os.makedirs("/tmp/railway_audit", exist_ok=True)
    print("=== Listando proyectos del workspace ===", flush=True)
    res = gql(LIST_PROJECTS_QUERY)
    if res.get("errors"):
        print("ERRORES:", json.dumps(res["errors"], indent=2))
        sys.exit(1)

    workspaces = res["data"]["me"]["workspaces"]
    inventario = {"workspaces": []}

    for ws in workspaces:
        ws_data = {"id": ws["id"], "name": ws["name"], "projects": []}
        team = ws.get("team") or {}
        proj_edges = (team.get("projects") or {}).get("edges", [])
        print(f"\nWorkspace: {ws['name']} ({len(proj_edges)} proyectos)")
        for pe in proj_edges:
            p = pe["node"]
            print(f"  - {p['name']} (id={p['id'][:8]}...)", flush=True)
            try:
                detail = gql(PROJECT_DETAIL_QUERY, {"id": p["id"]})
                proj = detail["data"]["project"]
                services = []
                for se in proj["services"]["edges"]:
                    s = se["node"]
                    deploys = s.get("deployments", {}).get("edges", [])
                    latest = deploys[0]["node"] if deploys else None
                    instances = s.get("serviceInstances", {}).get("edges", [])
                    domains = []
                    repos = []
                    for ie in instances:
                        n = ie["node"]
                        d = n.get("domains") or {}
                        for sd in d.get("serviceDomains") or []:
                            domains.append(sd["domain"])
                        for cd in d.get("customDomains") or []:
                            domains.append(cd["domain"] + " (custom)")
                        src = n.get("source") or {}
                        if src.get("repo"):
                            repos.append("repo:" + src["repo"])
                        if src.get("image"):
                            repos.append("image:" + src["image"])
                    meta = (latest or {}).get("meta") or {}
                    services.append(
                        {
                            "id": s["id"],
                            "name": s["name"],
                            "status": (latest or {}).get("status"),
                            "staticUrl": (latest or {}).get("staticUrl"),
                            "createdAt": (latest or {}).get("createdAt"),
                            "domains": domains,
                            "sources": repos,
                            "repo_from_meta": meta.get("repo"),
                            "branch": meta.get("branch"),
                            "commit": (meta.get("commitHash") or "")[:8],
                            "commitMessage": (meta.get("commitMessage") or "")[:80],
                        }
                    )
                ws_data["projects"].append(
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "createdAt": p["createdAt"],
                        "updatedAt": p["updatedAt"],
                        "services": services,
                    }
                )
            except Exception as e:
                print(f"     ERROR detalle: {e}")
        inventario["workspaces"].append(ws_data)

    with open("/tmp/railway_audit/inventario.json", "w") as f:
        json.dump(inventario, f, indent=2)
    print("\n=== /tmp/railway_audit/inventario.json escrito ===")

    print("\n=== RESUMEN ===")
    for ws in inventario["workspaces"]:
        print(f"\n{ws['name']}:")
        for p in ws["projects"]:
            print(f"  Proyecto: {p['name']} ({len(p['services'])} servicios)")
            for s in p["services"]:
                domain = s["domains"][0] if s["domains"] else "(sin dominio)"
                src = s["repo_from_meta"] or (s["sources"][0] if s["sources"] else "(sin repo)")
                print(f"    - {s['name']:30s} | {(s['status'] or 'NULL'):10s} | {domain:55s} | {src}")


if __name__ == "__main__":
    main()
