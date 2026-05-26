#!/usr/bin/env python3
"""
Verifica el estado del deploy en Railway para ticketlike.mx.
Uso: python3 railway_status.py
"""

import json
import subprocess

TOKEN = "f1f96bae-eb9c-46b1-9e39-7fd08002c33b"
ENDPOINT = "https://backboard.railway.app/graphql/v2"
SERVICE_ID = "0aabcefd-4de2-4e88-804e-73c5196dfb7e"


def railway_query(gql):
    """Ejecuta una query GraphQL contra Railway API via curl (Cloudflare bloquea urllib)."""
    result = subprocess.run(
        [
            "curl",
            "-s",
            "-X",
            "POST",
            ENDPOINT,
            "-H",
            f"Authorization: Bearer {TOKEN}",
            "-H",
            "Content-Type: application/json",
            "-H",
            "User-Agent: Mozilla/5.0",
            "-d",
            json.dumps({"query": gql}),
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    return json.loads(result.stdout)


try:
    data = railway_query(
        """
    query {
      deployments(first: 3, input: { serviceId: "%s" }) {
        edges {
          node {
            id
            status
            createdAt
            updatedAt
          }
        }
      }
    }
    """
        % SERVICE_ID
    )

    deployments = data.get("data", {}).get("deployments", {}).get("edges", [])

    print("=" * 50)
    print("RAILWAY STATUS \u2014 ticketlike.mx")
    print("=" * 50)

    if not deployments:
        print("No se encontraron deployments")
    else:
        for i, edge in enumerate(deployments):
            d = edge["node"]
            marker = " \u2190 ACTUAL" if i == 0 else ""
            print(f"\nDeploy #{i + 1}{marker}")
            print(f"  ID: {d['id']}")
            print(f"  Status: {d['status']}")
            print(f"  Creado: {d['createdAt']}")
            print(f"  Actualizado: {d['updatedAt']}")

    # Quick health check
    print("\n--- Health Check ---")
    try:
        hc = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "10", "https://ticketlike.mx/"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        print(f"  ticketlike.mx: HTTP {hc.stdout.strip()}")
    except Exception as e:
        print(f"  ticketlike.mx: ERROR - {e}")

except Exception as e:
    print(f"Error consultando Railway API: {e}")
