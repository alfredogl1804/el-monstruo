#!/usr/bin/env python3
"""
Mapear todos los hilos disponibles en múltiples cuentas de Manus.
Lee API keys de variables de entorno MANUS_API_KEY_1, MANUS_API_KEY_2, etc.

Uso:
    export MANUS_API_KEY_1="sk-..."
    export MANUS_API_KEY_2="sk-..."
    python3 map_accounts.py
"""

import json
import os
import sys

import requests

BASE_URL = "https://api.manus.ai/v2"


def list_tasks(api_key: str, limit: int = 20) -> list[dict]:
    """Listar hilos de una cuenta."""
    r = requests.get(
        f"{BASE_URL}/task.list?limit={limit}",
        headers={"x-manus-api-key": api_key},
        timeout=20,
    )
    data = r.json()
    if not data.get("ok"):
        return []
    return data.get("data", [])


def main():
    # Buscar todas las API keys en env vars
    keys = {}
    for i in range(1, 11):  # soporta hasta 10 cuentas
        env_var = f"MANUS_API_KEY_{i}"
        key = os.environ.get(env_var)
        if key:
            keys[i] = key

    # También buscar MANUS_API_KEY sin número
    base_key = os.environ.get("MANUS_API_KEY")
    if base_key and 1 not in keys:
        keys[1] = base_key

    if not keys:
        print("No se encontraron API keys.", file=sys.stderr)
        print("Configurar: MANUS_API_KEY_1, MANUS_API_KEY_2, etc.", file=sys.stderr)
        sys.exit(1)

    print(f"Encontradas {len(keys)} cuenta(s) configuradas\n")

    all_accounts = {}
    for account_num, api_key in sorted(keys.items()):
        print(f"=== Cuenta {account_num} (key: {api_key[:10]}...{api_key[-4:]}) ===")
        tasks = list_tasks(api_key)
        all_accounts[account_num] = {
            "key_prefix": api_key[:10],
            "tasks": [],
        }
        if not tasks:
            print("  Sin hilos o key inválida\n")
            continue
        for t in tasks:
            task_info = {
                "id": t["id"],
                "title": t.get("title", "Sin título")[:60],
                "status": t.get("status", "unknown"),
                "url": t.get("task_url", ""),
            }
            all_accounts[account_num]["tasks"].append(task_info)
            status_icon = {"running": "🟢", "stopped": "⚪", "error": "🔴"}.get(t.get("status"), "⚪")
            print(f"  {status_icon} {task_info['title']}")
            print(f"     ID: {task_info['id']} | Status: {task_info['status']}")
        print(f"  Total: {len(tasks)} hilos\n")

    # Guardar mapa completo
    output_file = "/tmp/manus_account_map.json"
    with open(output_file, "w") as f:
        json.dump(all_accounts, f, indent=2, ensure_ascii=False)
    print(f"Mapa guardado en {output_file}")


if __name__ == "__main__":
    main()
