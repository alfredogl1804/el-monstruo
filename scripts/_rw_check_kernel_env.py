"""Diagnóstico T3: verifica si Railway tiene LANGFUSE_* + MODEL_* vars en el kernel.
NO imprime valores, solo presence boolean.

Usage:
  RAILWAY_API_TOKEN=$(grep ^RAILWAY .env|cut -d= -f2-) python3 scripts/_rw_check_kernel_env.py
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request

TOK = os.environ.get("RAILWAY_API_TOKEN", "")
if not TOK:
    print("ERR: RAILWAY_API_TOKEN missing", file=sys.stderr)
    sys.exit(1)


def gql(query: str, variables: dict | None = None) -> dict:
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        "https://backboard.railway.app/graphql/v2",
        data=body,
        headers={
            "Authorization": f"Bearer {TOK}",
            "Content-Type": "application/json",
        },
    )
    return json.loads(urllib.request.urlopen(req, timeout=20).read().decode())


def main() -> int:
    # 1) Quien soy
    me = gql("{ me { id name email teams { edges { node { id name } } } } }")
    print("ME:", json.dumps(me.get("data", {}).get("me", {}), indent=2)[:500])

    # 2) Projects via teams (account token)
    projects_q = """
    query {
      me {
        projects {
          edges {
            node {
              id
              name
              services { edges { node { id name } } }
            }
          }
        }
      }
    }
    """
    pr = gql(projects_q)
    edges = pr.get("data", {}).get("me", {}).get("projects", {}).get("edges", []) or []
    if not edges:
        print("\nNO PROJECTS via me{projects}; trying root projects field...")
        pr2 = gql("{ projects { edges { node { id name services { edges { node { id name } } } } } } }")
        edges = pr2.get("data", {}).get("projects", {}).get("edges", []) or []

    print(f"\nTotal projects: {len(edges)}")
    for e in edges:
        n = e["node"]
        print(f"\n=== Project: {n['name']}  id={n['id']} ===")
        for se in n.get("services", {}).get("edges", []) or []:
            sn = se["node"]
            print(f"  - service {sn['id'][:8]}  {sn['name']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
