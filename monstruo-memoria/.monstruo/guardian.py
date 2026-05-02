#!/usr/bin/env python3
"""
GUARDIAN V2 — Sistema Anti-Compactación Tri-Anchor + A.R.C.A.
=============================================================
Ejecutado automáticamente por AGENTS.md antes de cualquier razonamiento.

Principio: "La recuperación de contexto no es una tarea que el agente DEBE hacer,
sino una condición del entorno que se DEBE cumplir para poder actuar."

Anclajes:
  1. Filesystem (~/.monstruo/state/identity.json) — inmediato, local
  2. Kernel API (/v1/health + /v1/embrion/estado) — verdad en vivo
  3. Supabase (agent_context_state) — persistencia distribuida

Consenso: 2 de 3 deben coincidir para proceder.
Si <2: HALT + alertar al usuario.
"""
import json
import os
import sys
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════
STATE_DIR = Path.home() / ".monstruo" / "state"
IDENTITY_FILE = STATE_DIR / "identity.json"
LOGS_DIR = Path.home() / ".monstruo" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Env vars (inyectadas por el proyecto webdev o el sandbox)
KERNEL_URL = os.environ.get("KERNEL_BASE_URL", "")
KERNEL_KEY = os.environ.get("MONSTRUO_API_KEY", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


def log(msg: str, level: str = "INFO"):
    """Log a archivo y stdout"""
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    log_file = LOGS_DIR / "guardian.log"
    with open(log_file, "a") as f:
        f.write(line + "\n")


# ═══════════════════════════════════════════════════════════════
# ANCLAJE 1: FILESYSTEM (Local, inmediato)
# ═══════════════════════════════════════════════════════════════
def check_anchor_filesystem() -> dict:
    """Lee identity.json del disco. Si existe y es válido, retorna estado."""
    try:
        if not IDENTITY_FILE.exists():
            return {"valid": False, "error": "identity.json no existe", "data": None}
        
        data = json.loads(IDENTITY_FILE.read_text())
        
        # Verificar campos mínimos
        required = ["hilo", "rol", "proyecto_activo", "errores_criticos_no_repetir"]
        missing = [f for f in required if f not in data]
        if missing:
            return {"valid": False, "error": f"Campos faltantes: {missing}", "data": data}
        
        return {"valid": True, "data": data, "source": "filesystem"}
    
    except Exception as e:
        return {"valid": False, "error": str(e), "data": None}


# ═══════════════════════════════════════════════════════════════
# ANCLAJE 2: KERNEL API (Verdad en vivo)
# ═══════════════════════════════════════════════════════════════
def check_anchor_kernel() -> dict:
    """Consulta el kernel real para obtener estado verificado."""
    if not KERNEL_URL or not KERNEL_KEY:
        return {"valid": False, "error": "KERNEL_BASE_URL o MONSTRUO_API_KEY no configuradas", "data": None}
    
    try:
        import requests
        
        # Health check
        health_resp = requests.get(
            f"{KERNEL_URL}/health",
            headers={"x-api-key": KERNEL_KEY},
            timeout=10
        )
        
        if health_resp.status_code != 200:
            return {"valid": False, "error": f"Kernel health failed: {health_resp.status_code}", "data": None}
        
        health = health_resp.json()
        
        # Tools activas
        tools_resp = requests.get(
            f"{KERNEL_URL}/v1/tools",
            headers={"x-api-key": KERNEL_KEY},
            timeout=10
        )
        
        tools_list = []
        if tools_resp.status_code == 200:
            tools_data = tools_resp.json()
            # tools is a list of {name, endpoint, status, description}
            raw_tools = tools_data.get("tools", [])
            if isinstance(raw_tools, list):
                tools_list = [t["name"] for t in raw_tools if t.get("status") == "active"]
            elif isinstance(raw_tools, dict):
                tools_list = [name for name, info in raw_tools.items() if info.get("status") == "active"]
        
        # Embrión data from health response (it's embedded in components)
        components = health.get("components", {})
        embrion_loop = components.get("embrion_loop", {})
        
        kernel_state = {
            "kernel_online": True,
            "version": health.get("version", "unknown"),
            "uptime": health.get("uptime_seconds", 0),
            "tools_activas": tools_list,
            "embrion_running": embrion_loop.get("running", False),
            "embrion_ciclos": embrion_loop.get("cycle_count", 0),
            "fcs_score": embrion_loop.get("fcs", {}).get("score", 0) if isinstance(embrion_loop.get("fcs"), dict) else 0,
            "thoughts_today": embrion_loop.get("thoughts_today", 0),
            "models_available": health.get("models_available", [])
        }
        
        return {"valid": True, "data": kernel_state, "source": "kernel_api"}
    
    except Exception as e:
        return {"valid": False, "error": str(e), "data": None}


# ═══════════════════════════════════════════════════════════════
# ANCLAJE 3: SUPABASE (Persistencia distribuida)
# ═══════════════════════════════════════════════════════════════
def check_anchor_supabase() -> dict:
    """Consulta Supabase para obtener último estado guardado."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"valid": False, "error": "SUPABASE_URL o SUPABASE_SERVICE_KEY no configuradas", "data": None}
    
    try:
        import requests
        
        # Consultar tabla agent_context_state (si existe)
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/agent_context_state?hilo=eq.B&order=created_at.desc&limit=1",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if resp.status_code == 200:
            rows = resp.json()
            if rows:
                return {"valid": True, "data": rows[0].get("state_json", {}), "source": "supabase"}
            else:
                # Tabla existe pero no hay datos — primera vez
                return {"valid": False, "error": "No hay estado previo en Supabase (primera ejecución)", "data": None}
        elif resp.status_code == 404:
            # Tabla no existe aún
            return {"valid": False, "error": "Tabla agent_context_state no existe aún", "data": None}
        else:
            return {"valid": False, "error": f"Supabase error: {resp.status_code}", "data": None}
    
    except Exception as e:
        return {"valid": False, "error": str(e), "data": None}


# ═══════════════════════════════════════════════════════════════
# CONSENSO + RESTAURACIÓN
# ═══════════════════════════════════════════════════════════════
def save_state_to_supabase(state: dict):
    """Guarda estado verificado en Supabase para futuras recuperaciones."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return
    
    try:
        import requests
        state_str = json.dumps(state, sort_keys=True)
        state_hash = hashlib.sha256(state_str.encode()).hexdigest()
        
        requests.post(
            f"{SUPABASE_URL}/rest/v1/agent_context_state",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json={
                "hilo": "B",
                "state_json": state,
                "state_hash": state_hash,
                "source": "guardian_v2"
            },
            timeout=10
        )
    except Exception:
        pass  # Best effort


def run_recovery():
    """Ejecuta el ciclo completo de recuperación tri-anchor."""
    
    print("=" * 70)
    print("  GUARDIAN V2 — Sistema Anti-Compactación Tri-Anchor")
    print("  Fecha:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    print("=" * 70)
    print()
    
    # === Verificar los 3 anclajes ===
    log("Verificando Anclaje 1: Filesystem...")
    anchor1 = check_anchor_filesystem()
    log(f"  → {'VÁLIDO' if anchor1['valid'] else 'FALLO: ' + anchor1.get('error', '?')}")
    
    log("Verificando Anclaje 2: Kernel API...")
    anchor2 = check_anchor_kernel()
    log(f"  → {'VÁLIDO' if anchor2['valid'] else 'FALLO: ' + anchor2.get('error', '?')}")
    
    log("Verificando Anclaje 3: Supabase...")
    anchor3 = check_anchor_supabase()
    log(f"  → {'VÁLIDO' if anchor3['valid'] else 'FALLO: ' + anchor3.get('error', '?')}")
    
    # === Consenso ===
    valid_count = sum(1 for a in [anchor1, anchor2, anchor3] if a["valid"])
    
    print()
    print(f"{'─' * 70}")
    print(f"  CONSENSO: {valid_count}/3 anclajes válidos", end="")
    
    if valid_count >= 2:
        print(" ✓ PROCEDER")
    elif valid_count == 1:
        print(" ⚠ DEGRADADO (1 anclaje, proceder con cautela)")
    else:
        print(" ✗ HALT — Sin contexto verificado")
        print()
        print("  ╔══════════════════════════════════════════════════════════════╗")
        print("  ║  NO PUEDO OPERAR SIN CONTEXTO VERIFICADO.                   ║")
        print("  ║  Pregunta al usuario antes de actuar.                        ║")
        print("  ╚══════════════════════════════════════════════════════════════╝")
        return
    
    print(f"{'─' * 70}")
    print()
    
    # === Imprimir estado restaurado ===
    # Prioridad: Filesystem > Kernel > Supabase
    identity = anchor1.get("data", {}) if anchor1["valid"] else (anchor3.get("data", {}) if anchor3["valid"] else {})
    kernel = anchor2.get("data", {}) if anchor2["valid"] else {}
    
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                    IDENTIDAD RESTAURADA                         ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    
    if identity:
        print(f"║  Hilo: {identity.get('hilo', '?')}")
        print(f"║  Rol: {identity.get('rol', '?')}")
        print(f"║  Proyecto: {identity.get('proyecto_activo', '?')}")
        print(f"║  Path: {identity.get('proyecto_path', '?')}")
    
    if kernel:
        print(f"║")
        print(f"║  Kernel: {'ONLINE' if kernel.get('kernel_online') else 'OFFLINE'} (v{kernel.get('version', '?')})")
        print(f"║  Tools activas: {kernel.get('tools_activas', [])}")
        print(f"║  Embrión: {'running' if kernel.get('embrion_running') else 'stopped'} ({kernel.get('embrion_ciclos', 0)} ciclos)")
        print(f"║  FCS: {kernel.get('fcs_score', 0)}")
    
    print(f"║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║              ERRORES CRÍTICOS — NO REPETIR                      ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    
    errors = identity.get("errores_criticos_no_repetir", [])
    for i, err in enumerate(errors, 1):
        # Wrap long lines
        if len(err) > 64:
            print(f"║  {i}. {err[:64]}")
            print(f"║     {err[64:]}")
        else:
            print(f"║  {i}. {err}")
    
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║              CAPACIDADES REALES (VERIFICADAS)                   ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    
    if kernel:
        tools = kernel.get("tools_activas", [])
        print(f"║  Tools ACTIVAS en producción: {tools}")
        inactivas = identity.get("tools_inactivas_produccion", [])
        if inactivas:
            print(f"║  Tools INACTIVAS (existen en código pero NO en prod):")
            for t in inactivas[:5]:
                print(f"║    - {t}")
            if len(inactivas) > 5:
                print(f"║    ... y {len(inactivas) - 5} más")
    
    print(f"║")
    print(f"╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    # === Guardar en Supabase para futuras recuperaciones ===
    if anchor1["valid"]:
        save_state_to_supabase(identity)
        log("Estado guardado en Supabase para futura recuperación")
    
    # === Log de auditoría ===
    audit = {
        "timestamp": datetime.utcnow().isoformat(),
        "anchors": {
            "filesystem": anchor1["valid"],
            "kernel": anchor2["valid"],
            "supabase": anchor3["valid"]
        },
        "consensus": valid_count,
        "action": "restored" if valid_count >= 1 else "halted"
    }
    
    audit_file = LOGS_DIR / "audit.jsonl"
    with open(audit_file, "a") as f:
        f.write(json.dumps(audit) + "\n")


# ═══════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    run_recovery()
