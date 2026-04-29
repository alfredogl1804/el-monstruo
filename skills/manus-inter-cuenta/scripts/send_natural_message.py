#!/usr/bin/env python3
"""
Enviar un mensaje en lenguaje natural a un hilo de cualquier cuenta de Manus.
Usa la API key de la cuenta dueña del hilo destino.

Uso:
    python3 send_natural_message.py --key "$API_KEY" --task-id "abc123" --message "Oye, necesito que..."
    python3 send_natural_message.py --key "$API_KEY" --create --message "Ayúdame a investigar..."
"""

import argparse
import json
import sys
import time

import requests

BASE_URL = "https://api.manus.ai/v2"


def send_message(api_key: str, task_id: str, message: str) -> dict:
    """Enviar mensaje a hilo existente."""
    r = requests.post(
        f"{BASE_URL}/task.sendMessage",
        headers={"x-manus-api-key": api_key, "Content-Type": "application/json"},
        json={"task_id": task_id, "message": {"content": message}},
        timeout=30,
    )
    return r.json()


def create_task(api_key: str, message: str) -> dict:
    """Crear nuevo hilo con mensaje inicial."""
    r = requests.post(
        f"{BASE_URL}/task.create",
        headers={"x-manus-api-key": api_key, "Content-Type": "application/json"},
        json={"message": {"content": message}},
        timeout=30,
    )
    return r.json()


def wait_for_response(api_key: str, task_id: str, max_wait: int = 300) -> str | None:
    """Polling hasta que el agente responda."""
    url = f"{BASE_URL}/task.listMessages?task_id={task_id}&limit=5"
    headers = {"x-manus-api-key": api_key}
    start = time.time()
    print(f"Esperando respuesta (max {max_wait}s)...", file=sys.stderr)
    while time.time() - start < max_wait:
        r = requests.get(url, headers=headers, timeout=20).json()
        for msg in r.get("messages", []):
            if "assistant_message" in msg:
                content = msg["assistant_message"]["content"]
                if len(content) > 100:
                    return content
            if "status_update" in msg:
                if msg["status_update"].get("agent_status") == "stopped":
                    for m2 in r["messages"]:
                        if "assistant_message" in m2:
                            return m2["assistant_message"]["content"]
        elapsed = int(time.time() - start)
        print(f"  ...{elapsed}s transcurridos, sin respuesta aún", file=sys.stderr)
        time.sleep(15)
    return None


def validate_message(message: str) -> list[str]:
    """Verificar que el mensaje cumple las reglas de lenguaje natural."""
    warnings = []
    forbidden = ["[INTER-CUENTA]", "[SISTEMA]", "[BRIDGE]", "<instruction>",
                 "Timestamp:", "sandbox", "API key", "inter-cuenta"]
    for tag in forbidden:
        if tag.lower() in message.lower():
            warnings.append(f"Contiene texto prohibido: '{tag}'")
    if message.startswith("[") or message.startswith("<"):
        warnings.append("Empieza con etiqueta técnica — reescribir en lenguaje natural")
    if len(message) < 20:
        warnings.append("Mensaje muy corto — incluir contexto suficiente")
    return warnings


def main():
    parser = argparse.ArgumentParser(description="Enviar mensaje inter-cuenta Manus")
    parser.add_argument("--key", required=True, help="API key de la cuenta destino")
    parser.add_argument("--task-id", help="ID del hilo existente")
    parser.add_argument("--create", action="store_true", help="Crear nuevo hilo")
    parser.add_argument("--message", required=True, help="Mensaje en lenguaje natural")
    parser.add_argument("--wait", action="store_true", help="Esperar respuesta")
    parser.add_argument("--max-wait", type=int, default=300, help="Segundos máximos de espera")
    args = parser.parse_args()

    # Validar mensaje
    warnings = validate_message(args.message)
    if warnings:
        print("ADVERTENCIAS sobre el mensaje:", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)
        print("El agente receptor podría rechazar este mensaje.", file=sys.stderr)
        print("Reescríbelo en lenguaje natural conversacional.", file=sys.stderr)
        sys.exit(1)

    # Enviar o crear
    if args.create:
        result = create_task(args.key, args.message)
        print(json.dumps(result, indent=2))
        task_id = result.get("task_id")
    elif args.task_id:
        result = send_message(args.key, args.task_id, args.message)
        print(json.dumps(result, indent=2))
        task_id = args.task_id
    else:
        print("Error: especificar --task-id o --create", file=sys.stderr)
        sys.exit(1)

    # Esperar respuesta si se pidió
    if args.wait and task_id:
        response = wait_for_response(args.key, task_id, args.max_wait)
        if response:
            print("\n=== RESPUESTA DEL AGENTE ===")
            print(response)
        else:
            print("Sin respuesta dentro del tiempo límite.", file=sys.stderr)


if __name__ == "__main__":
    main()
