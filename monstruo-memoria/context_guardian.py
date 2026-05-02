#!/usr/bin/env python3
"""
CONTEXT GUARDIAN — Guardián de Contexto Ejecutable.

PROBLEMA: AGENTS.md dice "lee estos archivos" pero el agente puede ignorarlo.
El texto es sugerencia. El código es obligación.

SOLUCION: Este script se ejecuta AUTOMATICAMENTE al inicio de cada acción
del agente (via AGENTS.md que dice "ejecuta este script"). La diferencia:
- AGENTS.md dice "ejecuta" (no "lee") → el agente ejecuta código
- El código IMPRIME el contexto directamente al stdout
- El agente VE el output como resultado de su acción
- No puede ignorarlo porque es el resultado de una tool call

MECANISMO:
1. Se ejecuta via: python3 ~/el-monstruo/monstruo-memoria/context_guardian.py
2. Imprime un RESUMEN EJECUTABLE del estado actual
3. Valida que los archivos críticos existen
4. Si algo falta, lo regenera desde GitHub o el kernel
5. Imprime INSTRUCCIONES OBLIGATORIAS que el agente debe seguir

INTEGRACIÓN CON AGENTS.md:
Cambiar AGENTS.md de:
  "1. Si existe ~/EMERGENCIAS_DIGEST.md, léelo primero."
A:
  "1. Ejecuta: python3 ~/el-monstruo/monstruo-memoria/context_guardian.py"

La diferencia es que "ejecuta" produce OUTPUT que el agente ve.
"Lee" es una instrucción que el agente puede saltarse.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

SANDBOX_HOME = os.environ.get("HOME", "/home/ubuntu")
REPO_DIR = os.path.join(SANDBOX_HOME, "el-monstruo")
MEMORIA_DIR = os.path.join(REPO_DIR, "monstruo-memoria")

# Archivos críticos que DEBEN existir
CRITICAL_FILES = {
    "identidad": os.path.join(SANDBOX_HOME, "IDENTIDAD_HILO.md"),
    "emergencias": os.path.join(SANDBOX_HOME, "EMERGENCIAS_DIGEST.md"),
}

# Estado del guardian
STATE_FILE = os.path.join(SANDBOX_HOME, ".context_guardian_state.json")


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"runs": 0, "last_run": None, "compactions_detected": 0}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def check_critical_files():
    """Verifica que los archivos críticos existen. Si no, los restaura."""
    missing = []
    for name, path in CRITICAL_FILES.items():
        if not os.path.exists(path):
            missing.append((name, path))
    return missing


def restore_from_repo(missing):
    """Restaura archivos faltantes desde el repo clonado."""
    restored = []
    mapping = {
        "identidad": "IDENTIDAD_HILO_B.md",
        "emergencias": "EMERGENCIAS_DIGEST.md",
    }
    for name, target_path in missing:
        source_name = mapping.get(name)
        if source_name:
            source_path = os.path.join(MEMORIA_DIR, source_name)
            if os.path.exists(source_path):
                subprocess.run(["cp", source_path, target_path], check=True)
                restored.append(name)
            else:
                # Try to pull from git
                try:
                    subprocess.run(
                        ["git", "-C", REPO_DIR, "pull", "--rebase"],
                        capture_output=True, timeout=15
                    )
                    if os.path.exists(source_path):
                        subprocess.run(["cp", source_path, target_path], check=True)
                        restored.append(name)
                except Exception:
                    pass
    return restored


def detect_compaction(state):
    """Detecta si hubo compactación basándose en señales."""
    signals = []

    # Signal 1: CONTEXT.md no existe pero ya corrimos antes
    if state["runs"] > 0 and not os.path.exists(os.path.join(SANDBOX_HOME, "CONTEXT.md")):
        signals.append("CONTEXT.md desaparecio")

    # Signal 2: Estado tiene runs > 0 pero identidad no existe
    if state["runs"] > 0:
        for name, path in CRITICAL_FILES.items():
            if not os.path.exists(path):
                signals.append(f"{name} desaparecio")

    return signals


def print_context_summary():
    """Imprime el resumen de contexto que el agente DEBE ver."""
    print("=" * 70)
    print("  CONTEXT GUARDIAN — RESUMEN EJECUTABLE")
    print("=" * 70)
    print()

    # Identidad
    identidad_path = CRITICAL_FILES["identidad"]
    if os.path.exists(identidad_path):
        with open(identidad_path) as f:
            lines = f.readlines()
        # Extraer las primeras líneas clave
        for line in lines[:20]:
            line = line.strip()
            if line and not line.startswith("---"):
                print(f"  {line}")
    else:
        print("  ⚠️  IDENTIDAD NO ENCONTRADA — contexto perdido")

    print()
    print("-" * 70)
    print("  ESTADO VERIFICADO DEL KERNEL (desde última auditoría)")
    print("-" * 70)

    # Leer estado del kernel desde identidad
    if os.path.exists(identidad_path):
        with open(identidad_path) as f:
            content = f.read()
        # Extraer sección de estado real
        if "ESTADO REAL DEL KERNEL" in content:
            start = content.index("ESTADO REAL DEL KERNEL")
            end = content.index("---", start + 10) if "---" in content[start + 10:] else len(content)
            section = content[start:start + end - start]
            for line in section.split("\n")[:20]:
                if line.strip():
                    print(f"  {line.strip()}")

    print()
    print("-" * 70)
    print("  ERRORES A NO REPETIR")
    print("-" * 70)

    if os.path.exists(identidad_path):
        with open(identidad_path) as f:
            content = f.read()
        if "ERRORES QUE COMETI" in content:
            start = content.index("ERRORES QUE COMETI")
            end_markers = ["---", "## PENDIENTES"]
            end = len(content)
            for marker in end_markers:
                if marker in content[start + 10:]:
                    candidate = content.index(marker, start + 10)
                    end = min(end, candidate)
            section = content[start:end]
            for line in section.split("\n"):
                if line.strip():
                    print(f"  {line.strip()}")

    print()
    print("=" * 70)
    print("  INSTRUCCIONES OBLIGATORIAS (código, no texto)")
    print("=" * 70)
    print()
    print("  1. NO afirmes nada sobre el kernel sin verificar con curl/código")
    print("  2. Si no recuerdas algo, di 'no lo recuerdo' y verifica")
    print("  3. Alfredo es la fuente de verdad, no tu memoria")
    print("  4. Las tools activas en prod son SOLO 3 (web_search, consult_sabios, email)")
    print("  5. El embrión tiene tool_calls_total=0 — nunca ha ejecutado tools exitosamente")
    print("  6. La app Flutter la construiste TÚ en este hilo via Manus My Computer")
    print("  7. Checkpoint actual del Command Center: 272ff959")
    print()
    print("=" * 70)


def run_kernel_health_check():
    """Ejecuta un health check rápido al kernel y reporta."""
    kernel_url = os.environ.get("KERNEL_BASE_URL", "")
    api_key = os.environ.get("MONSTRUO_API_KEY", "")

    if not kernel_url or not api_key:
        print("  [KERNEL] No hay credenciales — no puedo verificar")
        return

    try:
        import requests
        resp = requests.get(
            f"{kernel_url}/v1/health",
            headers={"x-api-key": api_key},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status", "unknown")
            uptime = data.get("uptime_seconds", 0)
            print(f"  [KERNEL] Status: {status} | Uptime: {uptime // 3600}h {(uptime % 3600) // 60}m")
        else:
            print(f"  [KERNEL] Error: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  [KERNEL] No alcanzable: {e}")


def main():
    state = load_state()

    # Detectar compactación
    compaction_signals = detect_compaction(state)
    if compaction_signals:
        state["compactions_detected"] += 1
        print(f"\n⚠️  COMPACTACION DETECTADA (señales: {', '.join(compaction_signals)})")
        print(f"    Compactaciones totales detectadas: {state['compactions_detected']}")
        print()

    # Verificar archivos críticos
    missing = check_critical_files()
    if missing:
        print(f"  Restaurando {len(missing)} archivo(s) faltante(s)...")
        restored = restore_from_repo(missing)
        if restored:
            print(f"  ✓ Restaurados: {', '.join(restored)}")
        not_restored = [name for name, _ in missing if name not in restored]
        if not_restored:
            print(f"  ✗ NO restaurados: {', '.join(not_restored)}")

    # Imprimir resumen de contexto
    print_context_summary()

    # Health check rápido
    print("\n  KERNEL HEALTH CHECK (en vivo):")
    run_kernel_health_check()

    # Actualizar estado
    state["runs"] += 1
    state["last_run"] = datetime.utcnow().isoformat()
    save_state(state)

    print(f"\n  [Guardian] Run #{state['runs']} completado @ {state['last_run']}")
    print()


if __name__ == "__main__":
    main()
