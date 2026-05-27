#!/usr/bin/env python3
"""Query Railway logs del kernel via GraphQL para ventana del E2E iPhone."""
import os
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

TOKEN = os.environ.get("RAILWAY_API_TOKEN", "").strip()
if not TOKEN:
    print("FAIL: RAILWAY_API_TOKEN no definido")
    sys.exit(1)

URL = "https://backboard.railway.com/graphql/v2"

def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(URL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"errors": [{"message": f"HTTP {e.code}: {e.read().decode()[:300]}"}]}

res = gql("query { me { projects { edges { node { id name } } } } }")
if "errors" in res:
    print("ERR projects:", res["errors"])
    sys.exit(2)

projects = res["data"]["me"]["projects"]["edges"]
print("Proyectos visibles:")
monstruo_pid = None
for e in projects:
    n = e["node"]
    print(f"  {n['id'][:8]}... {n['name']}")
    name_lower = n["name"].lower()
    if "monstruo" in name_lower or "kernel" in name_lower:
        monstruo_pid = n["id"]

if not monstruo_pid:
    print("FAIL: no encontre proyecto Monstruo/kernel")
    sys.exit(3)

print(f"\nProject ID: {monstruo_pid}")

q = """query($id: String!) {
    project(id: $id) {
        services { edges { node { id name } } }
        environments { edges { node { id name } } }
    }
}"""
res = gql(q, {"id": monstruo_pid})
if "errors" in res:
    print("ERR services:", res["errors"])
    sys.exit(4)

p = res["data"]["project"]
print("\nServicios:")
kernel_sid = None
for e in p["services"]["edges"]:
    n = e["node"]
    print(f"  {n['id'][:8]}... {n['name']}")
    if "kernel" in n["name"].lower():
        kernel_sid = n["id"]
print("\nEnvironments:")
prod_eid = None
for e in p["environments"]["edges"]:
    n = e["node"]
    print(f"  {n['id'][:8]}... {n['name']}")
    if n["name"].lower() in ("production", "prod"):
        prod_eid = n["id"]

if not kernel_sid or not prod_eid:
    print(f"FAIL: kernel_sid={kernel_sid} prod_eid={prod_eid}")
    sys.exit(5)

end = datetime.now(timezone.utc)
start = end - timedelta(minutes=15)

# Schema real Railway 2026
q = """query($projectId: String!, $serviceId: String!, $environmentId: String!, $startDate: DateTime!, $endDate: DateTime!, $filter: String) {
    environmentLogs(
        projectId: $projectId
        environmentId: $environmentId
        filter: $filter
        startDate: $startDate
        endDate: $endDate
        limit: 100
    ) {
        message
        timestamp
        severity
    }
}"""

print(f"\nLogs ventana {start.isoformat()} -> {end.isoformat()}...")
res = gql(q, {
    "projectId": monstruo_pid,
    "serviceId": kernel_sid,
    "environmentId": prod_eid,
    "startDate": start.isoformat(),
    "endDate": end.isoformat(),
    "filter": f'@service:"kernel"'
})

if "errors" in res:
    print("Schema environmentLogs no aplica, intentando deploymentLogs...")
    # Buscar deployment activo
    q2 = """query($sid: String!, $eid: String!) {
        deployments(input: { serviceId: $sid, environmentId: $eid }, first: 1) {
            edges { node { id status createdAt } }
        }
    }"""
    res2 = gql(q2, {"sid": kernel_sid, "eid": prod_eid})
    print("deployments:", json.dumps(res2, indent=2)[:1500])
else:
    print(json.dumps(res, indent=2)[:5000])
