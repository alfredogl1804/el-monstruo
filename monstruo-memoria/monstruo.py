#!/usr/bin/env python3
"""
MONSTRUO — Sistema Completo de Memoria Persistente.

Este es el script maestro. Hace todo:
1. Detecta si hubo compactación (perdida de contexto)
2. Si sí: ejecuta inject.py para recuperar contexto
3. Ejecuta heartbeat.py para guardar estado actual
4. Imprime instrucciones para el agente

Uso:
  python3 monstruo.py          → Ciclo completo (detectar + inyectar + heartbeat)
  python3 monstruo.py inject   → Solo inyectar contexto
  python3 monstruo.py heartbeat → Solo guardar estado
  python3 monstruo.py legacy "resumen" → Depositar legado antes de morir
  python3 monstruo.py status   → Ver estado del sistema
"""

import json
import os
import sys
from datetime import datetime, timedelta

import requests

SANDBOX_HOME = os.environ.get("HOME", "/home/ubuntu")
KERNEL_URL = "https://el-monstruo-kernel-production.up.railway.app"
KERNEL_KEY = "c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259"
STATE_FILE = os.path.join(SANDBOX_HOME, ".monstruo_state.json")


def load_state():
    """Carga el estado persistente del sistema."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_heartbeat": None,
        "last_inject": None,
        "compaction_count": 0,
        "total_heartbeats": 0,
        "total_injects": 0,
        "total_legacies": 0,
    }


def save_state(state):
    """Guarda el estado persistente."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def detect_compaction(state):
    """Detecta si hubo compactación del sandbox."""
    # Señales de compactación:
    # 1. CONTEXT.md no existe (debería existir si inject corrió antes)
    # 2. El state file tiene un last_heartbeat pero RECOVERY.md es viejo
    # 3. Archivos que deberían existir no existen

    context_exists = os.path.exists(os.path.join(SANDBOX_HOME, "CONTEXT.md"))
    recovery_exists = os.path.exists(os.path.join(SANDBOX_HOME, "RECOVERY.md"))

    if state["last_heartbeat"] and not context_exists:
        return True  # Teníamos contexto, ya no lo tenemos

    if state["last_heartbeat"]:
        # Verificar si el heartbeat es muy viejo
        last = datetime.fromisoformat(state["last_heartbeat"].replace("Z", ""))
        age = datetime.utcnow() - last
        if age > timedelta(hours=1):
            return True  # Más de 1 hora sin heartbeat = probable compactación

    return False


def check_kernel():
    """Verifica estado del kernel."""
    try:
        resp = requests.get(f"{KERNEL_URL}/health", headers={"X-API-Key": KERNEL_KEY}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


def run_inject():
    """Ejecuta inyección de contexto."""
    from inject import main as inject_main

    return inject_main()


def run_heartbeat():
    """Ejecuta heartbeat."""
    from heartbeat import main as heartbeat_main

    return heartbeat_main()


def run_legacy(summary=""):
    """Ejecuta legado."""
    from legacy import main as legacy_main

    if summary:
        sys.argv = ["legacy.py", summary]
    return legacy_main()


def print_status(state):
    """Imprime estado del sistema."""
    kernel = check_kernel()

    print("=" * 60)
    print("  MONSTRUO — Sistema de Memoria Persistente")
    print("=" * 60)
    print()
    print(f"  Kernel:           {'ONLINE' if kernel else 'OFFLINE'}")
    if kernel:
        print(f"  Kernel version:   {kernel.get('version', 'unknown')}")
    print(f"  Last heartbeat:   {state.get('last_heartbeat', 'nunca')}")
    print(f"  Last inject:      {state.get('last_inject', 'nunca')}")
    print(f"  Compactaciones:   {state.get('compaction_count', 0)}")
    print(f"  Total heartbeats: {state.get('total_heartbeats', 0)}")
    print(f"  Total injects:    {state.get('total_injects', 0)}")
    print(f"  Total legacies:   {state.get('total_legacies', 0)}")
    print()

    context_exists = os.path.exists(os.path.join(SANDBOX_HOME, "CONTEXT.md"))
    recovery_exists = os.path.exists(os.path.join(SANDBOX_HOME, "RECOVERY.md"))
    print(f"  CONTEXT.md:       {'existe' if context_exists else 'NO EXISTE'}")
    print(f"  RECOVERY.md:      {'existe' if recovery_exists else 'NO EXISTE'}")
    print()
    print("=" * 60)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    state = load_state()

    # Parsear comando
    cmd = sys.argv[1] if len(sys.argv) > 1 else "auto"

    if cmd == "status":
        print_status(state)
        return

    if cmd == "inject":
        run_inject()
        state["last_inject"] = datetime.utcnow().isoformat() + "Z"
        state["total_injects"] = state.get("total_injects", 0) + 1
        save_state(state)
        return

    if cmd == "heartbeat":
        run_heartbeat()
        state["last_heartbeat"] = datetime.utcnow().isoformat() + "Z"
        state["total_heartbeats"] = state.get("total_heartbeats", 0) + 1
        save_state(state)
        return

    if cmd == "legacy":
        summary = " ".join(sys.argv[2:])
        run_legacy(summary)
        state["total_legacies"] = state.get("total_legacies", 0) + 1
        save_state(state)
        return

    # --- MODO AUTO: Ciclo completo ---
    print("[monstruo] Modo automático — detectando estado...")

    compacted = detect_compaction(state)

    if compacted:
        print("[monstruo] ⚠ COMPACTACIÓN DETECTADA. Recuperando contexto...")
        state["compaction_count"] = state.get("compaction_count", 0) + 1
        run_inject()
        state["last_inject"] = datetime.utcnow().isoformat() + "Z"
        state["total_injects"] = state.get("total_injects", 0) + 1
        print()
        print("[monstruo] Contexto recuperado. Lee ~/CONTEXT.md")
    else:
        print("[monstruo] No se detectó compactación.")

    # Siempre hacer heartbeat
    print("[monstruo] Ejecutando heartbeat...")
    run_heartbeat()
    state["last_heartbeat"] = datetime.utcnow().isoformat() + "Z"
    state["total_heartbeats"] = state.get("total_heartbeats", 0) + 1

    save_state(state)

    print()
    print("[monstruo] Sistema listo.")
    print("[monstruo] Lee ~/CONTEXT.md para contexto completo.")
    print("[monstruo] Lee ~/RECOVERY.md para estado del sandbox.")


if __name__ == "__main__":
    main()
