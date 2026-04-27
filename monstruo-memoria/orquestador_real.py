#!/usr/bin/env python3.11
"""
ORQUESTADOR REAL DEL MONSTRUO
==============================
Endpoints verificados con 13/13 pruebas el 27-abr-2026.
Cada función usa SOLO endpoints que funcionaron en producción.

PROBLEMA QUE RESUELVE:
- Hilos pierden contexto al compactarse
- Hilos nuevos nacen vacíos
- El orquestador (yo) también pierde contexto
- Alfredo termina reparando todo manualmente

SOLUCIÓN:
- force_skills inyecta contexto obligatorio (no texto que se olvida)
- task.listMessages detecta si un hilo se desvió
- task.sendMessage + force_skills re-inyecta contexto
- project.instruction actúa como system prompt persistente

ENDPOINTS VERIFICADOS (27-abr-2026):
- POST /v2/task.create        → Crear hilo con force_skills
- POST /v2/task.sendMessage    → Enviar mensaje + force_skills
- GET  /v2/task.listMessages   → Leer mensajes de un hilo
- GET  /v2/task.detail         → Estado de un hilo
- GET  /v2/task.list           → Listar hilos
- GET  /v2/skill.list          → Listar skills con IDs
- POST /v2/project.create      → Crear proyecto con instruction
- POST /v2/task.stop           → Detener hilo
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

API_KEY = os.environ.get("MANUS_API_KEY", "")
BASE_URL = "https://api.manus.ai/v2"
HEADERS = {
    "x-manus-api-key": API_KEY,
    "Content-Type": "application/json"
}

# IDs de skills verificados el 27-abr-2026
SKILLS = {
    "el-monstruo-core":       "MvbdheoAYox4QiBRPZ6Xen",
    "anti-autoboicot":        "NmYEopC7fyZQWq7K5VTtc6",
    "optimizador-creditos":   "CbSnEs3A9mUTHKDVDSzsAQ",
    "validacion-tiempo-real": "QgmiFhEpWHrpuX4ZXx2egY",
    "protocolo-operativo-core": "gF54YRcKJCANhzHEZ7P7ND",
    "consulta-sabios":        "ZmPsg592DDwc7gZGnTJPhj",
    "el-monstruo-plan":       "Q8eaFgefAGfXLPwqKuoUHg",
    "el-monstruo-estado":     "dPTWYaVFHSYhUFwAvASU8Z",
    "manus-inter-cuenta":     "ApiegZwSY5TTVVSXuJfBvV",
    "api-context-injector":   "55ZoNoe9YXfacEpGbbbvVr",
}

# Perfiles de skills por tipo de tarea
PERFILES = {
    "monstruo": {
        "force": ["el-monstruo-core", "anti-autoboicot", "optimizador-creditos", "el-monstruo-plan"],
        "enable": ["el-monstruo-estado", "consulta-sabios", "api-context-injector", "manus-inter-cuenta"],
        "desc": "Construcción/modificación del Monstruo"
    },
    "codigo": {
        "force": ["el-monstruo-core", "anti-autoboicot", "optimizador-creditos"],
        "enable": ["validacion-tiempo-real", "api-context-injector"],
        "desc": "Desarrollo de código general"
    },
    "investigacion": {
        "force": ["el-monstruo-core", "validacion-tiempo-real", "optimizador-creditos"],
        "enable": ["consulta-sabios", "protocolo-operativo-core", "api-context-injector"],
        "desc": "Investigación y análisis"
    },
    "analisis": {
        "force": ["el-monstruo-core", "protocolo-operativo-core", "optimizador-creditos"],
        "enable": ["consulta-sabios", "validacion-tiempo-real", "api-context-injector"],
        "desc": "Análisis profundo con sabios"
    },
    "orquestacion": {
        "force": ["el-monstruo-core", "anti-autoboicot", "optimizador-creditos", "manus-inter-cuenta"],
        "enable": ["el-monstruo-plan", "el-monstruo-estado", "api-context-injector", "validacion-tiempo-real"],
        "desc": "Orquestación de hilos (el orquestador mismo)"
    },
    "minimo": {
        "force": ["el-monstruo-core", "optimizador-creditos"],
        "enable": [],
        "desc": "Tarea simple con contexto mínimo"
    }
}

# Modelos prohibidos — si aparecen en la respuesta del agente, está alucinando
MODELOS_PROHIBIDOS = [
    "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5",
    "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
    "claude-3.5", "gemini-1.5", "gemini-2.0", "gemini-2.5",
    "gemini-1.0", "gemini pro", "gemini ultra",
]

# Estado persistente
STATE_FILE = Path.home() / ".orquestador_state.json"

# ============================================================
# API — Solo endpoints verificados
# ============================================================

def api(method, endpoint, data=None, params=None, timeout=20):
    """Llamada a la API. Devuelve (ok, response_dict)."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        if method == "GET":
            r = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
        elif method == "POST":
            r = requests.post(url, headers=HEADERS, json=data, timeout=timeout)
        else:
            return False, {"error": f"Método {method} no soportado"}
        resp = r.json()
        return resp.get("ok", False), resp
    except requests.Timeout:
        return False, {"error": "TIMEOUT"}
    except Exception as e:
        return False, {"error": str(e)}

# ============================================================
# ESTADO PERSISTENTE
# ============================================================

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"hilos": {}, "proyecto_id": None, "created": datetime.now().isoformat()}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

# ============================================================
# CREAR HILO CON CONTEXTO FORZADO
# ============================================================

def crear_hilo(tarea, tipo="monstruo", proyecto_id=None, lite=False):
    """
    Crea un hilo nuevo con force_skills según el tipo de tarea.
    
    Verificado: task.create + force_skills funciona (prueba 3, 27-abr-2026)
    Verificado: múltiples force_skills simultáneos funciona (prueba 13)
    Verificado: task.create con project_id funciona (prueba 11)
    """
    if tipo not in PERFILES:
        print(f"ERROR: Tipo '{tipo}' no existe. Opciones: {list(PERFILES.keys())}")
        return None
    
    perfil = PERFILES[tipo]
    force_ids = [SKILLS[s] for s in perfil["force"] if s in SKILLS]
    enable_ids = [SKILLS[s] for s in perfil["enable"] if s in SKILLS]
    
    # Construir el mensaje con contexto explícito
    mensaje_contexto = f"""CONTEXTO OBLIGATORIO — LEE ANTES DE HACER NADA:

1. Eres parte del ecosistema del Monstruo de Alfredo Góngora
2. Se te forzaron {len(force_ids)} skills — LÉELOS TODOS antes de actuar
3. Valida TODO con código y en tiempo real — NUNCA dependas solo de tu entrenamiento
4. Si no sabes algo, investiga en tiempo real — no inventes
5. Cuando termines, deposita tu conocimiento ejecutando: python3 ~/el-monstruo/monstruo-memoria/legacy.py

TAREA: {tarea}"""

    payload = {
        "message": {
            "content": [{"type": "text", "text": mensaje_contexto}],
            "force_skills": force_ids,
        },
        "title": f"[{tipo.upper()}] {tarea[:60]}",
        "hide_in_task_list": False,
        "agent_profile": "manus-1.6-lite" if lite else "manus-1.6"
    }
    
    if enable_ids:
        payload["message"]["enable_skills"] = enable_ids
    
    if proyecto_id:
        payload["project_id"] = proyecto_id
    
    ok, resp = api("POST", "task.create", payload)
    
    if not ok:
        print(f"ERROR creando hilo: {resp}")
        return None
    
    task_id = resp.get("task_id")
    task_url = resp.get("task_url", "")
    
    # Guardar en estado
    state = load_state()
    state["hilos"][task_id] = {
        "tipo": tipo,
        "tarea": tarea,
        "url": task_url,
        "created": datetime.now().isoformat(),
        "force_skills": perfil["force"],
        "status": "running",
        "violations": 0
    }
    save_state(state)
    
    print(f"HILO CREADO [{tipo}]")
    print(f"  task_id: {task_id}")
    print(f"  url: {task_url}")
    print(f"  force_skills: {perfil['force']}")
    print(f"  enable_skills: {perfil['enable']}")
    return task_id

# ============================================================
# MONITOREAR UN HILO
# ============================================================

def monitorear(task_id, verbose=False):
    """
    Lee los mensajes de un hilo y detecta problemas.
    
    Verificado: task.listMessages funciona (prueba 4, 27-abr-2026)
    Verificado: devuelve user_message, assistant_message, status_update
    """
    ok, resp = api("GET", "task.listMessages", params={
        "task_id": task_id,
        "limit": "30",
        "order": "desc"
    })
    
    if not ok:
        print(f"ERROR leyendo mensajes de {task_id}: {resp}")
        return None
    
    msgs = resp.get("messages", [])
    
    # Analizar
    agent_msgs = []
    status_msgs = []
    violations = []
    
    for m in msgs:
        t = m.get("type", "")
        if t == "assistant_message":
            content = m["assistant_message"].get("content", "")
            agent_msgs.append(content)
            
            # Buscar modelos prohibidos
            content_lower = content.lower()
            for modelo in MODELOS_PROHIBIDOS:
                if modelo in content_lower:
                    violations.append(f"Modelo prohibido detectado: {modelo}")
            
        elif t == "status_update":
            su = m["status_update"]
            status_msgs.append({
                "status": su.get("agent_status", "?"),
                "brief": su.get("brief", "")
            })
    
    # Determinar estado actual
    current_status = "unknown"
    if status_msgs:
        current_status = status_msgs[0]["status"]
    
    # Detectar señales de pérdida de contexto
    if agent_msgs:
        last_msg = agent_msgs[0].lower()
        context_loss_signals = [
            "no tengo acceso", "no puedo ver", "no conozco el contexto",
            "no sé qué", "empecemos desde cero", "¿podrías darme más contexto",
            "no tengo información sobre"
        ]
        for signal in context_loss_signals:
            if signal in last_msg:
                violations.append(f"Señal de pérdida de contexto: '{signal}'")
    
    result = {
        "task_id": task_id,
        "status": current_status,
        "total_messages": len(msgs),
        "agent_messages": len(agent_msgs),
        "violations": violations,
        "last_agent_msg": agent_msgs[0][:300] if agent_msgs else "(sin respuesta)"
    }
    
    # Actualizar estado
    state = load_state()
    if task_id in state["hilos"]:
        state["hilos"][task_id]["status"] = current_status
        state["hilos"][task_id]["violations"] = len(violations)
        state["hilos"][task_id]["last_check"] = datetime.now().isoformat()
        save_state(state)
    
    if verbose:
        print(f"\nMONITOR [{task_id[:12]}...]")
        print(f"  Status: {current_status}")
        print(f"  Mensajes: {len(msgs)} total, {len(agent_msgs)} del agente")
        print(f"  Violaciones: {len(violations)}")
        for v in violations:
            print(f"    ⚠ {v}")
        print(f"  Última respuesta: {result['last_agent_msg'][:200]}")
    
    return result

# ============================================================
# RECUPERAR UN HILO (RE-INYECTAR CONTEXTO)
# ============================================================

def recuperar(task_id, mensaje_extra=""):
    """
    Re-inyecta contexto en un hilo que se desvió.
    
    Verificado: task.sendMessage + force_skills funciona (prueba 7, 27-abr-2026)
    """
    state = load_state()
    hilo_info = state.get("hilos", {}).get(task_id, {})
    tipo = hilo_info.get("tipo", "monstruo")
    tarea_original = hilo_info.get("tarea", "tarea desconocida")
    
    perfil = PERFILES.get(tipo, PERFILES["monstruo"])
    force_ids = [SKILLS[s] for s in perfil["force"] if s in SKILLS]
    
    mensaje = f"""RECUPERACIÓN DE CONTEXTO — LEER OBLIGATORIAMENTE:

Perdiste contexto. Esto es lo que necesitas saber:

1. Eres un hilo de tipo [{tipo}] del ecosistema del Monstruo
2. Tu tarea original: {tarea_original}
3. Se te están re-inyectando {len(force_ids)} skills — LÉELOS TODOS
4. Valida TODO con código — no confíes en tu memoria
5. Si necesitas más contexto, ejecuta: python3 ~/el-monstruo/monstruo-memoria/inject.py

{f'INSTRUCCIÓN ADICIONAL: {mensaje_extra}' if mensaje_extra else ''}

Continúa con tu tarea original. No empieces de cero."""

    ok, resp = api("POST", "task.sendMessage", {
        "task_id": task_id,
        "message": {
            "content": [{"type": "text", "text": mensaje}],
            "force_skills": force_ids
        }
    })
    
    if not ok:
        print(f"ERROR recuperando {task_id}: {resp}")
        return False
    
    print(f"RECUPERACIÓN ENVIADA a {task_id[:12]}...")
    print(f"  Skills re-forzados: {perfil['force']}")
    return True

# ============================================================
# MONITOREAR TODOS LOS HILOS
# ============================================================

def monitorear_todos():
    """Monitorea todos los hilos registrados y detecta problemas."""
    state = load_state()
    hilos = state.get("hilos", {})
    
    if not hilos:
        print("No hay hilos registrados.")
        return
    
    print(f"\n{'='*70}")
    print(f"MONITOR GLOBAL — {len(hilos)} hilos registrados")
    print(f"{'='*70}")
    
    problemas = []
    
    for task_id, info in hilos.items():
        result = monitorear(task_id, verbose=True)
        if result and result["violations"]:
            problemas.append((task_id, result))
    
    if problemas:
        print(f"\n{'='*70}")
        print(f"ALERTA: {len(problemas)} hilos con problemas")
        print(f"{'='*70}")
        for task_id, result in problemas:
            print(f"\n  {task_id[:12]}... — {len(result['violations'])} violaciones:")
            for v in result["violations"]:
                print(f"    ⚠ {v}")
            print(f"  → Ejecuta: python3 orquestador_real.py recover {task_id}")
    else:
        print(f"\nTodos los hilos OK.")

# ============================================================
# CREAR PROYECTO (SYSTEM PROMPT PERSISTENTE)
# ============================================================

def crear_proyecto(nombre, instrucciones):
    """
    Crea un proyecto con instrucciones que actúan como system prompt.
    
    Verificado: project.create funciona (prueba 10, 27-abr-2026)
    """
    ok, resp = api("POST", "project.create", {
        "name": nombre,
        "instruction": instrucciones
    })
    
    if not ok:
        print(f"ERROR creando proyecto: {resp}")
        return None
    
    project_id = resp.get("project", {}).get("id")
    
    # Guardar en estado
    state = load_state()
    state["proyecto_id"] = project_id
    state["proyecto_nombre"] = nombre
    save_state(state)
    
    print(f"PROYECTO CREADO: {nombre}")
    print(f"  project_id: {project_id}")
    return project_id

# ============================================================
# LEER MENSAJES DE UN HILO EXTERNO
# ============================================================

def leer_hilo(task_id, limit=20):
    """
    Lee los mensajes de cualquier hilo (propio o externo).
    
    Verificado: task.listMessages funciona con cualquier task_id de la cuenta.
    """
    ok, resp = api("GET", "task.listMessages", params={
        "task_id": task_id,
        "limit": str(limit),
        "order": "desc"
    })
    
    if not ok:
        print(f"ERROR: {resp}")
        return
    
    msgs = resp.get("messages", [])
    print(f"\nMENSAJES DE {task_id[:12]}... ({len(msgs)} mensajes)")
    print("="*60)
    
    for m in reversed(msgs):
        t = m.get("type", "?")
        if t == "user_message":
            content = m["user_message"]["content"]
            print(f"\n[USER] {content[:500]}")
        elif t == "assistant_message":
            content = m["assistant_message"]["content"]
            print(f"\n[AGENT] {content[:500]}")
        elif t == "status_update":
            su = m["status_update"]
            brief = su.get("brief", "")
            status = su.get("agent_status", "?")
            if brief:
                print(f"[STATUS] {status} — {brief[:200]}")

# ============================================================
# ENVIAR MENSAJE A UN HILO
# ============================================================

def enviar_mensaje(task_id, mensaje, force_tipo=None):
    """
    Envía un mensaje a un hilo existente, opcionalmente con force_skills.
    
    Verificado: task.sendMessage funciona (prueba 6, 27-abr-2026)
    Verificado: task.sendMessage + force_skills funciona (prueba 7)
    """
    payload = {
        "task_id": task_id,
        "message": {
            "content": [{"type": "text", "text": mensaje}]
        }
    }
    
    if force_tipo and force_tipo in PERFILES:
        perfil = PERFILES[force_tipo]
        force_ids = [SKILLS[s] for s in perfil["force"] if s in SKILLS]
        payload["message"]["force_skills"] = force_ids
    
    ok, resp = api("POST", "task.sendMessage", payload)
    
    if not ok:
        print(f"ERROR: {resp}")
        return False
    
    print(f"MENSAJE ENVIADO a {task_id[:12]}...")
    return True

# ============================================================
# STATUS GENERAL
# ============================================================

def status():
    """Muestra el estado del orquestador y todos los hilos."""
    state = load_state()
    
    print(f"\n{'='*70}")
    print(f"ORQUESTADOR DEL MONSTRUO — STATUS")
    print(f"{'='*70}")
    print(f"Proyecto: {state.get('proyecto_nombre', 'ninguno')} ({state.get('proyecto_id', 'N/A')})")
    print(f"Hilos registrados: {len(state.get('hilos', {}))}")
    
    hilos = state.get("hilos", {})
    if hilos:
        print(f"\n{'ID':<15} {'Tipo':<15} {'Status':<12} {'Violaciones':<12} {'Tarea'}")
        print("-"*70)
        for tid, info in hilos.items():
            print(f"{tid[:12]}... {info.get('tipo','?'):<15} {info.get('status','?'):<12} {info.get('violations',0):<12} {info.get('tarea','?')[:30]}")
    
    # Verificar API
    ok, resp = api("GET", "skill.list")
    if ok:
        skills = resp.get("data", [])
        print(f"\nAPI: OK ({len(skills)} skills disponibles)")
    else:
        print(f"\nAPI: ERROR — {resp}")

# ============================================================
# ACTUALIZAR SKILL IDS (por si cambian)
# ============================================================

def actualizar_skills():
    """Consulta skill.list y actualiza los IDs. Verificado: prueba 1."""
    ok, resp = api("GET", "skill.list")
    if not ok:
        print(f"ERROR: {resp}")
        return
    
    skills = resp.get("data", [])
    print(f"\n{len(skills)} SKILLS DISPONIBLES:")
    print(f"{'Nombre':<35} {'ID'}")
    print("-"*70)
    
    actualizados = 0
    for s in skills:
        nombre = s.get("name", "?")
        sid = s.get("id", "?")
        marker = ""
        if nombre in SKILLS:
            if SKILLS[nombre] != sid:
                marker = " ← CAMBIÓ!"
                actualizados += 1
            else:
                marker = " ✓"
        print(f"{nombre:<35} {sid}{marker}")
    
    if actualizados:
        print(f"\n⚠ {actualizados} skills cambiaron de ID. Actualiza SKILLS en el código.")
    else:
        print(f"\nTodos los IDs verificados — sin cambios.")

# ============================================================
# BOOTSTRAP — Auto-aplicar al hilo actual
# ============================================================

def bootstrap():
    """
    Se auto-aplica el contexto a ESTE hilo.
    Útil cuando el orquestador pierde contexto.
    """
    print("BOOTSTRAP — Recuperando contexto del orquestador...")
    
    # 1. Verificar API
    ok, _ = api("GET", "skill.list")
    if not ok:
        print("ERROR: API no responde. Verificar MANUS_API_KEY.")
        return False
    print("  API: OK")
    
    # 2. Cargar estado
    state = load_state()
    print(f"  Estado: {len(state.get('hilos', {}))} hilos registrados")
    
    # 3. Verificar skills
    actualizar_skills()
    
    # 4. Recordar identidad
    identidad = Path.home() / "IDENTIDAD_HILO.md"
    if identidad.exists():
        print(f"\n  IDENTIDAD: {identidad.read_text()[:200]}")
    else:
        print("\n  ⚠ No hay IDENTIDAD_HILO.md — crear uno")
    
    print("\nBOOTSTRAP COMPLETO. El orquestador está operativo.")
    return True

# ============================================================
# MAIN
# ============================================================

HELP = """
ORQUESTADOR REAL DEL MONSTRUO
==============================
Endpoints verificados con 13/13 pruebas (27-abr-2026).

Comandos:
  create <tarea> [tipo]     Crear hilo con contexto forzado
                            Tipos: monstruo, codigo, investigacion, analisis, orquestacion, minimo
  
  monitor [task_id]         Monitorear un hilo o todos
  
  recover <task_id> [msg]   Re-inyectar contexto en un hilo desviado
  
  read <task_id> [limit]    Leer mensajes de cualquier hilo
  
  send <task_id> <mensaje>  Enviar mensaje a un hilo
  
  project <nombre>          Crear proyecto con system prompt del Monstruo
  
  skills                    Verificar y actualizar IDs de skills
  
  status                    Estado general del orquestador
  
  bootstrap                 Auto-recuperar contexto del orquestador
  
  stop <task_id>            Detener un hilo

Ejemplos:
  python3 orquestador_real.py create "Arregla el bug del HITL gate" monstruo
  python3 orquestador_real.py monitor
  python3 orquestador_real.py recover abc123 "Vuelve a leer el skill core"
  python3 orquestador_real.py read fwXoLkA7Kjs86GCw6XAUeU 30
"""

if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: MANUS_API_KEY no está configurada.")
        sys.exit(1)
    
    args = sys.argv[1:]
    
    if not args or args[0] in ["-h", "--help", "help"]:
        print(HELP)
        sys.exit(0)
    
    cmd = args[0]
    
    if cmd == "create":
        if len(args) < 2:
            print("Uso: create <tarea> [tipo]")
            sys.exit(1)
        tarea = args[1]
        tipo = args[2] if len(args) > 2 else "monstruo"
        lite = "--lite" in args
        state = load_state()
        crear_hilo(tarea, tipo, state.get("proyecto_id"), lite)
    
    elif cmd == "monitor":
        if len(args) > 1:
            monitorear(args[1], verbose=True)
        else:
            monitorear_todos()
    
    elif cmd == "recover":
        if len(args) < 2:
            print("Uso: recover <task_id> [mensaje]")
            sys.exit(1)
        msg = " ".join(args[2:]) if len(args) > 2 else ""
        recuperar(args[1], msg)
    
    elif cmd == "read":
        if len(args) < 2:
            print("Uso: read <task_id> [limit]")
            sys.exit(1)
        limit = int(args[2]) if len(args) > 2 else 20
        leer_hilo(args[1], limit)
    
    elif cmd == "send":
        if len(args) < 3:
            print("Uso: send <task_id> <mensaje>")
            sys.exit(1)
        enviar_mensaje(args[1], " ".join(args[2:]))
    
    elif cmd == "project":
        if len(args) < 2:
            print("Uso: project <nombre>")
            sys.exit(1)
        instrucciones = """Eres parte del ecosistema del Monstruo de Alfredo Góngora.
REGLAS OBLIGATORIAS:
1. Valida TODO con código en tiempo real — NUNCA dependas solo de tu entrenamiento
2. Usa los modelos correctos: GPT-5.4, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, DeepSeek R1, Perplexity Sonar Pro
3. Si pierdes contexto, ejecuta: python3 ~/el-monstruo/monstruo-memoria/inject.py
4. Antes de escribir código, ejecuta: python3 ~/el-monstruo/monstruo-memoria/guardia.py scan
5. Cuando termines, deposita tu conocimiento: python3 ~/el-monstruo/monstruo-memoria/legacy.py
6. NUNCA tomes atajos. NUNCA inventes datos. NUNCA uses modelos obsoletos."""
        crear_proyecto(args[1], instrucciones)
    
    elif cmd == "skills":
        actualizar_skills()
    
    elif cmd == "status":
        status()
    
    elif cmd == "bootstrap":
        bootstrap()
    
    elif cmd == "stop":
        if len(args) < 2:
            print("Uso: stop <task_id>")
            sys.exit(1)
        ok, resp = api("POST", "task.stop", {"task_id": args[1]})
        print(f"{'OK' if ok else 'ERROR'}: {resp}")
    
    else:
        print(f"Comando desconocido: {cmd}")
        print(HELP)
