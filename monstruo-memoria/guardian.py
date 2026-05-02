#!/usr/bin/env python3
"""
GUARDIAN V3 — Anti-Compactación Tri-Anchor + OMEGA Memory
==========================================================
Ejecutado automáticamente por AGENTS.md antes de cualquier razonamiento.

Principio: "La recuperación de contexto no es una tarea que el agente DEBE hacer,
sino una condición del entorno que se DEBE cumplir para poder actuar."

Anclajes:
  1. Filesystem (~/.monstruo/state/identity.json) — inmediato, local
  2. Kernel API (/health + /v1/tools) — verdad en vivo
  3. Database (MySQL/TiDB agent_context_state) — persistencia distribuida

OMEGA Memory (NUEVO en V3):
  - Checkpoint/Resume automático de tareas
  - Búsqueda semántica de memorias
  - Detección de contradicciones
  - Lessons learned persistentes
  - Timeline de decisiones

Flujo:
  1. Verificar 3 anclajes → consenso 2/3
  2. OMEGA resume_task → recuperar último checkpoint
  3. Imprimir contexto restaurado
  4. OMEGA checkpoint → guardar estado actual para próxima compactación
"""
import json
import os
import sys
import asyncio
import hashlib
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════
STATE_DIR = Path.home() / ".monstruo" / "state"
IDENTITY_FILE = STATE_DIR / "identity.json"
LOGS_DIR = Path.home() / ".monstruo" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

KERNEL_URL = os.environ.get("KERNEL_BASE_URL", "")
KERNEL_KEY = os.environ.get("MONSTRUO_API_KEY", "")

def log(msg: str, level: str = "INFO"):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    log_file = LOGS_DIR / "guardian.log"
    with open(log_file, "a") as f:
        f.write(line + "\n")

# ═══════════════════════════════════════════════════════════════
# ANCLAJE 1: FILESYSTEM
# ═══════════════════════════════════════════════════════════════
def check_anchor_filesystem() -> dict:
    try:
        if not IDENTITY_FILE.exists():
            return {"valid": False, "error": "identity.json no existe", "data": None}
        data = json.loads(IDENTITY_FILE.read_text())
        required = ["hilo", "rol", "proyecto_activo", "errores_criticos_no_repetir"]
        missing = [f for f in required if f not in data]
        if missing:
            return {"valid": False, "error": f"Campos faltantes: {missing}", "data": data}
        return {"valid": True, "data": data, "source": "filesystem"}
    except Exception as e:
        return {"valid": False, "error": str(e), "data": None}

# ═══════════════════════════════════════════════════════════════
# ANCLAJE 2: KERNEL API
# ═══════════════════════════════════════════════════════════════
def check_anchor_kernel() -> dict:
    if not KERNEL_URL or not KERNEL_KEY:
        return {"valid": False, "error": "KERNEL_BASE_URL o MONSTRUO_API_KEY no configuradas", "data": None}
    try:
        import urllib.request
        # Health
        req = urllib.request.Request(
            f"{KERNEL_URL}/health",
            headers={"x-api-key": KERNEL_KEY}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            health = json.loads(resp.read())

        # Tools
        req2 = urllib.request.Request(
            f"{KERNEL_URL}/v1/tools",
            headers={"x-api-key": KERNEL_KEY}
        )
        with urllib.request.urlopen(req2, timeout=10) as resp2:
            tools_raw = json.loads(resp2.read())

        tools_list = tools_raw if isinstance(tools_raw, list) else tools_raw.get("tools", [])
        active_tools = [t.get("name", t) if isinstance(t, dict) else str(t) for t in tools_list if (isinstance(t, dict) and t.get("status") == "active")]

        embrion = health.get("embrion", {})
        data = {
            "kernel_online": True,
            "version": health.get("version", "?"),
            "tools_activas": active_tools,
            "tools_total": len(tools_list),
            "embrion_running": embrion.get("running", False),
            "embrion_ciclos": embrion.get("cycles_completed", 0),
            "fcs_score": health.get("fcs", {}).get("score", 0),
        }
        return {"valid": True, "data": data, "source": "kernel_api"}
    except Exception as e:
        return {"valid": False, "error": str(e), "data": None}

# ═══════════════════════════════════════════════════════════════
# ANCLAJE 3: DATABASE (MySQL/TiDB)
# ═══════════════════════════════════════════════════════════════
def _get_db_connection():
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        return None
    try:
        import pymysql
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        return pymysql.connect(
            host=parsed.hostname, port=parsed.port or 4000,
            user=parsed.username, password=parsed.password,
            database=parsed.path.lstrip("/"),
            ssl={"ssl": True}, connect_timeout=10
        )
    except Exception:
        return None

def check_anchor_database() -> dict:
    conn = _get_db_connection()
    if not conn:
        return {"valid": False, "error": "No DATABASE_URL o conexión fallida", "data": None}
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT state_json, created_at FROM agent_context_state ORDER BY created_at DESC LIMIT 1")
            row = cur.fetchone()
            if not row:
                return {"valid": False, "error": "No hay estado guardado en DB", "data": None}
            data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
            return {"valid": True, "data": data, "source": "database", "updated_at": str(row[1])}
    except Exception as e:
        return {"valid": False, "error": str(e), "data": None}
    finally:
        conn.close()

def save_state_to_database(state: dict):
    conn = _get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO agent_context_state (id, hilo, state_json, state_hash, source, created_at) VALUES (%s, %s, %s, %s, %s, NOW()) "
                "ON DUPLICATE KEY UPDATE state_json = VALUES(state_json), state_hash = VALUES(state_hash), created_at = NOW()",
                ("current", state.get("hilo", "B"), json.dumps(state, default=str), 
                 hashlib.sha256(json.dumps(state, sort_keys=True, default=str).encode()).hexdigest()[:64],
                 "guardian_v3")
            )
            conn.commit()
    except Exception as e:
        log(f"Error guardando en DB: {e}", "WARN")
    finally:
        conn.close()

# ═══════════════════════════════════════════════════════════════
# OMEGA MEMORY — Checkpoint/Resume + Semantic Memory
# ═══════════════════════════════════════════════════════════════
OMEGA_AVAILABLE = False
try:
    from omega.server.handlers import (
        handle_omega_checkpoint,
        handle_omega_resume_task,
        handle_omega_store,
        handle_omega_query,
        handle_omega_lessons,
        handle_omega_timeline,
        handle_omega_health as omega_health_check,
    )
    OMEGA_AVAILABLE = True
except ImportError:
    pass

async def omega_resume() -> str:
    """Intenta resumir la última tarea checkpointeada en OMEGA."""
    if not OMEGA_AVAILABLE:
        return ""
    try:
        result = await handle_omega_resume_task(arguments={
            "task_title": "Hilo B",
            "verbosity": "full"
        })
        text = result.get("content", [{}])[0].get("text", "")
        if "no checkpoint" in text.lower() or "0 checkpoint" in text.lower():
            return ""
        return text
    except Exception as e:
        log(f"OMEGA resume falló: {e}", "WARN")
        return ""

async def omega_get_lessons() -> str:
    """Obtiene lessons learned de OMEGA."""
    if not OMEGA_AVAILABLE:
        return ""
    try:
        result = await handle_omega_lessons(arguments={"limit": 10})
        text = result.get("content", [{}])[0].get("text", "")
        if "no" in text.lower() and "found" in text.lower():
            return ""
        return text
    except Exception:
        return ""

async def omega_save_checkpoint(identity: dict, kernel: dict):
    """Guarda checkpoint completo del estado actual en OMEGA."""
    if not OMEGA_AVAILABLE:
        return
    try:
        tools_activas = kernel.get("tools_activas", [])
        errores = identity.get("errores_criticos_no_repetir", [])
        pendientes = identity.get("pendientes_criticos", [])

        await handle_omega_checkpoint(arguments={
            "task_title": "Hilo B - Command Center + Infraestructura",
            "plan": "Construir Command Center, mantener kernel, integrar memoria persistente",
            "progress": f"Kernel: {'ONLINE' if kernel.get('kernel_online') else 'OFFLINE'} v{kernel.get('version', '?')}. "
                       f"Tools activas: {len(tools_activas)} ({', '.join(tools_activas)}). "
                       f"Embrión: {'running' if kernel.get('embrion_running') else 'stopped'} ({kernel.get('embrion_ciclos', 0)} ciclos). "
                       f"FCS: {kernel.get('fcs_score', 0)}. "
                       f"Checkpoint WebDev: {identity.get('ultimo_checkpoint', '?')}.",
            "files_touched": {
                "IDENTIDAD_HILO.md": "Identidad del hilo B",
                "EMERGENCIAS_DIGEST.md": "11 emergencias conversacionales",
                "~/.monstruo/guardian.py": "Guardian V3 con OMEGA",
                "~/.monstruo/state/identity.json": "Filesystem anchor",
                "monstruo-command-center/": "WebDev project - Command Center",
            },
            "decisions": [
                f"Tools activas en prod: SOLO {len(tools_activas)} — {tools_activas}",
                "OMEGA integrado como librería Python (50 handlers > 15 MCP tools)",
                "Guardian V3 = tri-anchor + OMEGA checkpoint/resume",
            ] + [f"ERROR NO REPETIR: {e}" for e in errores[:5]],
            "key_context": (
                f"Soy Hilo B. Proyecto: {identity.get('proyecto_activo', '?')}. "
                f"Path: {identity.get('proyecto_path', '?')}. "
                f"App Flutter en Mac: /Users/alfredogongora/el-monstruo/apps/mobile/. "
                f"Kernel Railway: {KERNEL_URL}. "
                f"REGLA DE ORO: No inventar contexto. Verificar con código. Alfredo es el ancla de la verdad."
            ),
            "next_steps": ". ".join(pendientes[:5]) if pendientes else "Consultar con Alfredo sobre prioridades."
        })
        log("OMEGA checkpoint guardado ✓")
    except Exception as e:
        log(f"OMEGA checkpoint falló: {e}", "WARN")

async def omega_store_lesson(lesson: str):
    """Guarda una lesson learned en OMEGA."""
    if not OMEGA_AVAILABLE:
        return
    try:
        await handle_omega_store(arguments={
            "content": lesson,
            "type": "lesson_learned"
        })
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════
# EJECUCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════
async def run_recovery_async():
    print()
    print("═" * 70)
    print("  GUARDIAN V3 — Tri-Anchor + OMEGA Memory")
    print(f"  {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("═" * 70)
    print()

    # === Verificar los 3 anclajes ===
    log("Anclaje 1: Filesystem...")
    anchor1 = check_anchor_filesystem()
    log(f"  → {'VÁLIDO' if anchor1['valid'] else 'FALLO: ' + anchor1.get('error', '?')}")

    log("Anclaje 2: Kernel API...")
    anchor2 = check_anchor_kernel()
    log(f"  → {'VÁLIDO' if anchor2['valid'] else 'FALLO: ' + anchor2.get('error', '?')}")

    log("Anclaje 3: Database (MySQL/TiDB)...")
    anchor3 = check_anchor_database()
    log(f"  → {'VÁLIDO' if anchor3['valid'] else 'FALLO: ' + anchor3.get('error', '?')}")

    # === OMEGA Memory ===
    log(f"OMEGA Memory: {'DISPONIBLE' if OMEGA_AVAILABLE else 'NO INSTALADO'}")

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
        # Intentar OMEGA como último recurso
        if OMEGA_AVAILABLE:
            log("Intentando recuperación via OMEGA resume...")
            omega_text = await omega_resume()
            if omega_text:
                print()
                print("╔══════════════════════════════════════════════════════════════╗")
                print("║  OMEGA RESCATE — Checkpoint encontrado                      ║")
                print("╠══════════════════════════════════════════════════════════════╣")
                for line in omega_text.split("\n")[:30]:
                    print(f"║  {line[:64]}")
                print("╚══════════════════════════════════════════════════════════════╝")
                return
        print()
        print("  ╔══════════════════════════════════════════════════════════════╗")
        print("  ║  NO PUEDO OPERAR SIN CONTEXTO VERIFICADO.                   ║")
        print("  ║  Pregunta al usuario antes de actuar.                        ║")
        print("  ╚══════════════════════════════════════════════════════════════╝")
        return

    print(f"{'─' * 70}")
    print()

    # === Extraer datos ===
    identity = anchor1.get("data", {}) if anchor1["valid"] else (anchor3.get("data", {}) if anchor3["valid"] else {})
    kernel = anchor2.get("data", {}) if anchor2["valid"] else {}

    # === OMEGA Resume (contexto adicional de sesiones anteriores) ===
    omega_context = ""
    omega_lessons_text = ""
    if OMEGA_AVAILABLE:
        omega_context = await omega_resume()
        omega_lessons_text = await omega_get_lessons()

    # === Imprimir estado restaurado ===
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
            print(f"║  Tools INACTIVAS (en código pero NO en prod):")
            for t in inactivas[:5]:
                print(f"║    - {t}")
            if len(inactivas) > 5:
                print(f"║    ... y {len(inactivas) - 5} más")

    # === OMEGA Context (si hay checkpoint previo) ===
    if omega_context:
        print(f"║")
        print(f"╠══════════════════════════════════════════════════════════════════╣")
        print(f"║              OMEGA — ÚLTIMO CHECKPOINT                          ║")
        print(f"╠══════════════════════════════════════════════════════════════════╣")
        for line in omega_context.split("\n"):
            if line.strip():
                truncated = line[:64]
                print(f"║  {truncated}")

    # === OMEGA Lessons ===
    if omega_lessons_text:
        print(f"║")
        print(f"╠══════════════════════════════════════════════════════════════════╣")
        print(f"║              OMEGA — LESSONS LEARNED                            ║")
        print(f"╠══════════════════════════════════════════════════════════════════╣")
        for line in omega_lessons_text.split("\n")[:10]:
            if line.strip():
                print(f"║  {line[:64]}")

    print(f"║")
    print(f"╚══════════════════════════════════════════════════════════════════╝")
    print()

    # === Guardar en Database ===
    if anchor1["valid"]:
        save_state_to_database(identity)
        log("Estado guardado en Database ✓")

    # === OMEGA Checkpoint (guardar estado actual para próxima compactación) ===
    if OMEGA_AVAILABLE and identity:
        await omega_save_checkpoint(identity, kernel)
        # Guardar lessons de los errores
        for err in errors:
            await omega_store_lesson(err)

    # === Audit log ===
    audit = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "V3",
        "anchors": {
            "filesystem": anchor1["valid"],
            "kernel": anchor2["valid"],
            "database": anchor3["valid"],
            "omega": OMEGA_AVAILABLE,
        },
        "consensus": valid_count,
        "omega_checkpoint_saved": OMEGA_AVAILABLE and bool(identity),
        "action": "restored" if valid_count >= 1 else "halted"
    }
    audit_file = LOGS_DIR / "audit.jsonl"
    with open(audit_file, "a") as f:
        f.write(json.dumps(audit) + "\n")

def run_recovery():
    asyncio.run(run_recovery_async())

# ═══════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    run_recovery()
