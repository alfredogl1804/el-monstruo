#!/usr/bin/env python3
"""
railway_scanner.py — Scanner exhaustivo de Railway para el Genome vivo.

Enumera 100% binario via Railway Public GraphQL API:
  - Workspaces del usuario y todos sus proyectos
  - Environments por proyecto
  - Servicios por proyecto
  - Service instances con último deployment, source, domains
  - Plugins (Postgres, Redis, etc.)

Verificación binaria:
  - Suma total de servicios debe ser >= expected_total_services (env var, default 19).

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

# Carga .env si existe
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
if ENV_PATH.exists():
    for raw in ENV_PATH.read_text().splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            k, v = raw.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

TOKEN = os.environ.get("RAILWAY_API_TOKEN", "").strip()
if not TOKEN:
    sys.exit("ERROR: RAILWAY_API_TOKEN requerido")

ENDPOINT = "https://backboard.railway.com/graphql/v2"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "monstruo-genome-scanner",
}


def gql(query: str, variables: dict | None = None) -> dict:
    """POST GraphQL con manejo de errores."""
    for attempt in range(3):
        try:
            r = requests.post(
                ENDPOINT,
                headers=HEADERS,
                json={"query": query, "variables": variables or {}},
                timeout=30,
            )
            if r.status_code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            r.raise_for_status()
            data = r.json()
            if "errors" in data:
                raise RuntimeError(f"GraphQL errors: {data['errors']}")
            return data.get("data", {})
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))
    return {}


# Query principal: me { workspaces { projects { ... } } }
# Es el único path que devuelve los proyectos para account tokens.
QUERY = """
query MeWorkspacesProjects {
  me {
    id
    email
    name
    workspaces {
      id
      name
      projects {
        edges {
          node {
            id
            name
            description
            createdAt
            updatedAt
            isPublic
            environments {
              edges {
                node {
                  id
                  name
                }
              }
            }
            services {
              edges {
                node {
                  id
                  name
                  createdAt
                  updatedAt
                  serviceInstances {
                    edges {
                      node {
                        id
                        environmentId
                        latestDeployment {
                          id
                          status
                          createdAt
                          meta
                        }
                        source {
                          repo
                          image
                        }
                        domains {
                          serviceDomains {
                            domain
                          }
                          customDomains {
                            domain
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            plugins {
              edges {
                node {
                  id
                  name
                  friendlyName
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


def scan() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    print(f"[{started}] Iniciando scan Railway...", flush=True)

    data = gql(QUERY)
    me = data.get("me") or {}
    workspaces_raw = me.get("workspaces") or []

    workspaces: list[dict] = []
    total_services = 0
    total_envs = 0
    total_projects = 0

    for ws in workspaces_raw:
        ws_id = ws.get("id")
        ws_name = ws.get("name")
        projects_edges = (ws.get("projects") or {}).get("edges") or []

        projects_out: list[dict] = []
        for pe in projects_edges:
            p = pe.get("node") or {}
            envs = [e.get("node", {}) for e in (p.get("environments") or {}).get("edges", [])]
            services_raw = [s.get("node", {}) for s in (p.get("services") or {}).get("edges", [])]
            plugins = [pl.get("node", {}) for pl in (p.get("plugins") or {}).get("edges", [])]

            services_out = []
            for s in services_raw:
                instances = []
                for ie in (s.get("serviceInstances") or {}).get("edges", []):
                    inst = ie.get("node") or {}
                    latest = inst.get("latestDeployment") or {}
                    meta = latest.get("meta") or {}
                    domains_block = inst.get("domains") or {}
                    source = inst.get("source") or {}
                    instances.append(
                        {
                            "id": inst.get("id"),
                            "environment_id": inst.get("environmentId"),
                            "deploy": {
                                "id": latest.get("id"),
                                "status": latest.get("status"),
                                "created_at": latest.get("createdAt"),
                                "commit_hash": meta.get("commitHash"),
                                "commit_message": (meta.get("commitMessage") or "")[:200],
                                "branch": meta.get("branch"),
                                "repo": meta.get("repo"),
                            },
                            "source": {
                                "repo": source.get("repo"),
                                "image": source.get("image"),
                            },
                            "domains": {
                                "service": [d.get("domain") for d in domains_block.get("serviceDomains") or []],
                                "custom": [d.get("domain") for d in domains_block.get("customDomains") or []],
                            },
                        }
                    )

                services_out.append(
                    {
                        "id": s.get("id"),
                        "name": s.get("name"),
                        "created_at": s.get("createdAt"),
                        "updated_at": s.get("updatedAt"),
                        "instances": instances,
                    }
                )

            projects_out.append(
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "description": p.get("description"),
                    "created_at": p.get("createdAt"),
                    "updated_at": p.get("updatedAt"),
                    "is_public": p.get("isPublic"),
                    "workspace_id": ws_id,
                    "workspace_name": ws_name,
                    "environments": envs,
                    "environments_count": len(envs),
                    "services": services_out,
                    "services_count": len(services_out),
                    "plugins": plugins,
                    "plugins_count": len(plugins),
                }
            )

            total_services += len(services_out)
            total_envs += len(envs)
            total_projects += 1
            print(
                f"  [{ws_name}] {p.get('name')} — {len(envs)} env(s), {len(services_out)} servicio(s), {len(plugins)} plugin(s)",
                flush=True,
            )

        workspaces.append(
            {
                "id": ws_id,
                "name": ws_name,
                "projects": projects_out,
                "projects_count": len(projects_out),
            }
        )

    finished = datetime.now(timezone.utc).isoformat()

    expected = int(os.environ.get("RAILWAY_EXPECTED_SERVICES", "19"))
    coverage_match = total_services >= expected

    return {
        "scanner": "railway",
        "version": 1,
        "started_at": started,
        "finished_at": finished,
        "user": {
            "id": me.get("id"),
            "name": me.get("name"),
            "email": me.get("email"),
        },
        "workspaces_count": len(workspaces),
        "projects_count": total_projects,
        "total_services": total_services,
        "total_environments": total_envs,
        "expected_total_services": expected,
        "coverage_match": coverage_match,
        "workspaces": workspaces,
    }


def main() -> int:
    out_dir = Path(__file__).resolve().parent.parent.parent / "_genome_out"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "railway.json"

    result = scan()
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print("\nRAILWAY SCAN RESUMEN")
    print(f"  workspaces         : {result['workspaces_count']}")
    print(f"  proyectos          : {result['projects_count']}")
    print(f"  total_services     : {result['total_services']}")
    print(f"  total_environments : {result['total_environments']}")
    print(f"  expected_services  : {result['expected_total_services']}")
    print(f"  coverage_match     : {result['coverage_match']}")
    print(f"  output             : {out_file}")
    print(f"  size               : {out_file.stat().st_size:,} bytes")

    return 0 if result["coverage_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
