#!/usr/bin/env python3
"""
Trigger de redeploy manual en Railway para ticketlike.mx.
Uso: python3 railway_redeploy.py
"""

import json
import subprocess

TOKEN = "f1f96bae-eb9c-46b1-9e39-7fd08002c33b"
ENDPOINT = "https://backboard.railway.app/graphql/v2"
SERVICE_ID = "0aabcefd-4de2-4e88-804e-73c5196dfb7e"
ENVIRONMENT_ID = "26d6f4be-2576-400f-ae03-46a60e90024e"

QUERY = """
mutation {
  serviceInstanceRedeploy(
    serviceId: "%s"
    environmentId: "%s"
  )
}
""" % (SERVICE_ID, ENVIRONMENT_ID)

try:
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
            json.dumps({"query": QUERY}),
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    data = json.loads(result.stdout)

    if "errors" in data:
        print(f"\u274c Error: {data['errors']}")
    else:
        print("\u2705 Redeploy triggered exitosamente")
        print("   Railway est\u00e1 rebuilding y redeployando el servicio.")
        print("   Verificar con: python3 railway_status.py")

except Exception as e:
    print(f"Error: {e}")
