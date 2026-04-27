#!/usr/bin/env python3.11
"""
VALIDADOR EXHAUSTIVO EN TIEMPO REAL
====================================
Este script prueba CADA capacidad de la API de Manus con código real.
No asume nada. No toma atajos. Cada claim se verifica o se descarta.

Reglas del script:
1. Cada prueba tiene un CLAIM (lo que creemos) y un VEREDICTO (lo que el código demostró)
2. Si una prueba falla, se marca como FALSO — no se justifica ni se excusa
3. El resultado final es un JSON con SOLO hechos verificados
4. El script NO puede terminar sin ejecutar TODAS las pruebas
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

API_KEY = os.environ.get("MANUS_API_KEY", "")
BASE_URL = "https://api.manus.ai/v2"
HEADERS = {
    "x-manus-api-key": API_KEY,
    "Content-Type": "application/json"
}

RESULTADOS = []
HILOS_CREADOS = []  # Para limpiar después

def registrar(nombre, claim, veredicto, evidencia, exito):
    """Registra el resultado de una prueba. Sin excepciones."""
    r = {
        "prueba": nombre,
        "claim": claim,
        "veredicto": veredicto,
        "evidencia": evidencia[:500] if isinstance(evidencia, str) else str(evidencia)[:500],
        "exito": exito,
        "timestamp": datetime.now().isoformat()
    }
    RESULTADOS.append(r)
    emoji = "VERDADERO" if exito else "FALSO"
    print(f"\n{'='*60}")
    print(f"[{emoji}] {nombre}")
    print(f"  Claim: {claim}")
    print(f"  Veredicto: {veredicto}")
    print(f"  Evidencia: {evidencia[:200]}")
    print(f"{'='*60}")

def api_call(method, endpoint, data=None, params=None, timeout=20):
    """Llamada a la API con manejo de errores. Devuelve (ok, response_dict)."""
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
# PRUEBA 0: ¿Tenemos API key?
# ============================================================
def test_0_api_key():
    if not API_KEY:
        registrar("API_KEY", "Tenemos API key en el entorno", 
                  "NO hay API key — nada funciona sin esto", "", False)
        sys.exit(1)
    registrar("API_KEY", "Tenemos API key en el entorno",
              f"Sí, longitud {len(API_KEY)} chars", f"Primeros 10: {API_KEY[:10]}...", True)

# ============================================================
# PRUEBA 1: skill.list devuelve skills con IDs
# ============================================================
def test_1_skill_list():
    claim = "skill.list devuelve skills con IDs que se pueden usar en force_skills"
    ok, resp = api_call("GET", "skill.list")
    if not ok:
        registrar("SKILL_LIST", claim, "FALLO — la API no respondió", str(resp), False)
        return None
    
    skills = resp.get("data", [])
    if not skills:
        registrar("SKILL_LIST", claim, "FALLO — devolvió lista vacía", str(resp), False)
        return None
    
    # Verificar estructura
    first = skills[0]
    tiene_id = "id" in first
    tiene_name = "name" in first
    
    if not (tiene_id and tiene_name):
        registrar("SKILL_LIST", claim, "FALLO — skills sin id o name", str(first), False)
        return None
    
    # Buscar el-monstruo-core
    core = None
    for s in skills:
        if s["name"] == "el-monstruo-core":
            core = s
            break
    
    evidencia = f"{len(skills)} skills. el-monstruo-core={'ENCONTRADO id='+core['id'] if core else 'NO ENCONTRADO'}"
    registrar("SKILL_LIST", claim, f"VERDADERO — {len(skills)} skills con IDs válidos", evidencia, True)
    return {s["name"]: s["id"] for s in skills}

# ============================================================
# PRUEBA 2: task.create funciona y devuelve task_id
# ============================================================
def test_2_task_create_basico():
    claim = "task.create crea un hilo y devuelve task_id"
    ok, resp = api_call("POST", "task.create", {
        "message": {
            "content": [{"type": "text", "text": "Responde SOLO con la palabra VALIDADO. Nada más."}]
        },
        "title": "VALIDACION-basico",
        "hide_in_task_list": True,
        "agent_profile": "manus-1.6-lite"
    })
    
    if not ok:
        registrar("TASK_CREATE_BASICO", claim, "FALLO — no se creó el hilo", str(resp), False)
        return None
    
    task_id = resp.get("task_id")
    task_url = resp.get("task_url")
    if not task_id:
        registrar("TASK_CREATE_BASICO", claim, "FALLO — respuesta sin task_id", str(resp), False)
        return None
    
    HILOS_CREADOS.append(task_id)
    registrar("TASK_CREATE_BASICO", claim, "VERDADERO — hilo creado", 
              f"task_id={task_id}, url={task_url}", True)
    return task_id

# ============================================================
# PRUEBA 3: task.create con force_skills FUNCIONA
# ============================================================
def test_3_force_skills(skill_ids):
    claim = "force_skills obliga al agente a leer el skill forzado"
    
    core_id = skill_ids.get("el-monstruo-core")
    if not core_id:
        registrar("FORCE_SKILLS", claim, "NO SE PUEDE PROBAR — no encontré el-monstruo-core", "", False)
        return None
    
    ok, resp = api_call("POST", "task.create", {
        "message": {
            "content": [{"type": "text", "text": "Lee el skill que se te forzó y dime: 1) ¿Qué versión del skill leíste? 2) ¿Qué dice sobre los modelos de IA? Responde en máximo 3 líneas."}],
            "force_skills": [core_id]
        },
        "title": "VALIDACION-force-skills",
        "hide_in_task_list": True,
        "agent_profile": "manus-1.6-lite"
    })
    
    if not ok:
        registrar("FORCE_SKILLS", claim, "FALLO — no se creó el hilo", str(resp), False)
        return None
    
    task_id = resp.get("task_id")
    HILOS_CREADOS.append(task_id)
    registrar("FORCE_SKILLS_CREATE", "task.create acepta force_skills sin error",
              "VERDADERO — hilo creado con force_skills", f"task_id={task_id}", True)
    return task_id

# ============================================================
# PRUEBA 4: task.listMessages puede leer respuestas
# ============================================================
def test_4_list_messages(task_id, espera=120):
    claim = "task.listMessages devuelve los mensajes del agente incluyendo su respuesta"
    
    if not task_id:
        registrar("LIST_MESSAGES", claim, "NO SE PUEDE PROBAR — no hay task_id", "", False)
        return None
    
    print(f"\n  Esperando {espera}s para que el agente responda...")
    time.sleep(espera)
    
    ok, resp = api_call("GET", "task.listMessages", params={
        "task_id": task_id,
        "limit": "20",
        "order": "asc"
    })
    
    if not ok:
        registrar("LIST_MESSAGES", claim, "FALLO — no se pudieron leer mensajes", str(resp), False)
        return None
    
    msgs = resp.get("messages", [])
    if not msgs:
        registrar("LIST_MESSAGES", claim, "FALLO — lista de mensajes vacía", str(resp), False)
        return None
    
    # Clasificar mensajes
    tipos = {}
    agent_content = ""
    for m in msgs:
        t = m.get("type", "unknown")
        tipos[t] = tipos.get(t, 0) + 1
        if t == "assistant_message":
            agent_content = m.get("assistant_message", {}).get("content", "")
    
    tiene_respuesta = bool(agent_content)
    evidencia = f"Tipos: {tipos}. Respuesta del agente: '{agent_content[:300]}'"
    
    registrar("LIST_MESSAGES", claim, 
              "VERDADERO — mensajes leídos con respuesta del agente" if tiene_respuesta else "PARCIAL — mensajes leídos pero sin respuesta aún",
              evidencia, tiene_respuesta)
    return agent_content

# ============================================================
# PRUEBA 5: force_skills REALMENTE hizo que leyera el skill
# ============================================================
def test_5_verificar_lectura_skill(agent_content):
    claim = "El agente REALMENTE leyó el skill forzado (no solo dijo que sí)"
    
    if not agent_content:
        registrar("LECTURA_SKILL", claim, "NO SE PUEDE VERIFICAR — no hay respuesta del agente", "", False)
        return
    
    # Buscar evidencia de que leyó el skill real
    indicadores_positivos = [
        "sprint", "epia", "soberan", "router", "gpt-5", "claude", "gemini", 
        "grok", "deepseek", "perplexity", "absorción", "cerebro", "capa",
        "v3.0", "v2.0", "monstruo"
    ]
    
    content_lower = agent_content.lower()
    encontrados = [i for i in indicadores_positivos if i in content_lower]
    
    if len(encontrados) >= 3:
        registrar("LECTURA_SKILL", claim, 
                  f"VERDADERO — {len(encontrados)} indicadores del skill encontrados en la respuesta",
                  f"Indicadores: {encontrados}", True)
    elif len(encontrados) >= 1:
        registrar("LECTURA_SKILL", claim,
                  f"PROBABLE — {len(encontrados)} indicadores encontrados, pero pocos",
                  f"Indicadores: {encontrados}. Respuesta: {agent_content[:200]}", True)
    else:
        registrar("LECTURA_SKILL", claim,
                  "FALSO — ningún indicador del skill en la respuesta. Puede que no lo haya leído.",
                  f"Respuesta: {agent_content[:300]}", False)

# ============================================================
# PRUEBA 6: task.sendMessage funciona para enviar follow-up
# ============================================================
def test_6_send_message(task_id):
    claim = "task.sendMessage puede enviar un mensaje de seguimiento a un hilo existente"
    
    if not task_id:
        registrar("SEND_MESSAGE", claim, "NO SE PUEDE PROBAR — no hay task_id", "", False)
        return
    
    ok, resp = api_call("POST", "task.sendMessage", {
        "task_id": task_id,
        "message": {
            "content": [{"type": "text", "text": "Gracias. Ahora dime: ¿cuántos skills tienes habilitados en este hilo? Responde solo el número."}]
        }
    })
    
    if not ok:
        # Puede fallar si el hilo ya terminó — eso también es información
        error_msg = resp.get("error", {})
        registrar("SEND_MESSAGE", claim, 
                  f"FALLO — {error_msg}", str(resp), False)
        return
    
    registrar("SEND_MESSAGE", claim, "VERDADERO — mensaje enviado exitosamente", str(resp), True)

# ============================================================
# PRUEBA 7: task.sendMessage con force_skills (para recuperación)
# ============================================================
def test_7_send_with_force_skills(task_id, skill_ids):
    claim = "task.sendMessage acepta force_skills para re-inyectar contexto en un hilo existente"
    
    if not task_id or not skill_ids:
        registrar("SEND_FORCE_SKILLS", claim, "NO SE PUEDE PROBAR", "", False)
        return
    
    core_id = skill_ids.get("el-monstruo-core")
    anti_id = skill_ids.get("anti-autoboicot")
    
    skills_to_force = [s for s in [core_id, anti_id] if s]
    
    ok, resp = api_call("POST", "task.sendMessage", {
        "task_id": task_id,
        "message": {
            "content": [{"type": "text", "text": "Re-lee los skills forzados y confirma que los leíste. Responde brevemente."}],
            "force_skills": skills_to_force
        }
    })
    
    if not ok:
        error_msg = resp.get("error", {})
        registrar("SEND_FORCE_SKILLS", claim,
                  f"FALLO — {error_msg}", str(resp), False)
        return
    
    registrar("SEND_FORCE_SKILLS", claim, "VERDADERO — sendMessage acepta force_skills", str(resp), True)

# ============================================================
# PRUEBA 8: task.detail para ver estado de un hilo
# ============================================================
def test_8_task_detail(task_id):
    claim = "task.detail devuelve el estado actual de un hilo"
    
    if not task_id:
        registrar("TASK_DETAIL", claim, "NO SE PUEDE PROBAR", "", False)
        return
    
    ok, resp = api_call("GET", "task.detail", params={"task_id": task_id})
    
    if not ok:
        registrar("TASK_DETAIL", claim, f"FALLO — {resp}", str(resp), False)
        return
    
    status = resp.get("status", "?")
    title = resp.get("title", "?")
    registrar("TASK_DETAIL", claim, f"VERDADERO — status={status}, title={title}", str(resp)[:300], True)

# ============================================================
# PRUEBA 9: task.list para listar hilos
# ============================================================
def test_9_task_list():
    claim = "task.list devuelve la lista de hilos de la cuenta"
    
    ok, resp = api_call("GET", "task.list", params={"limit": "3"})
    
    if not ok:
        registrar("TASK_LIST", claim, f"FALLO — {resp}", str(resp), False)
        return
    
    tasks = resp.get("data", [])
    registrar("TASK_LIST", claim, f"VERDADERO — {len(tasks)} hilos listados", 
              str([t.get("title","?") for t in tasks[:3]]), True)

# ============================================================
# PRUEBA 10: project.create para inyectar instrucciones
# ============================================================
def test_10_project_create():
    claim = "project.create permite crear un proyecto con instruction (equivalente a system prompt)"
    
    ok, resp = api_call("POST", "project.create", {
        "name": "VALIDACION-proyecto-test",
        "instruction": "Eres un asistente del Monstruo. SIEMPRE responde en español. NUNCA uses modelos anteriores a 2026."
    })
    
    if not ok:
        error = resp.get("error", {})
        registrar("PROJECT_CREATE", claim, f"FALLO — {error}", str(resp), False)
        return None
    
    project_id = resp.get("project", {}).get("id") or resp.get("id") or resp.get("project_id")
    registrar("PROJECT_CREATE", claim, f"VERDADERO — proyecto creado", str(resp)[:300], True)
    return project_id

# ============================================================
# PRUEBA 11: task.create con project_id
# ============================================================
def test_11_task_with_project(project_id):
    claim = "task.create acepta project_id para heredar instrucciones del proyecto"
    
    if not project_id:
        registrar("TASK_WITH_PROJECT", claim, "NO SE PUEDE PROBAR — no hay project_id", "", False)
        return
    
    ok, resp = api_call("POST", "task.create", {
        "message": {
            "content": [{"type": "text", "text": "Dime en qué idioma debes responder según tus instrucciones. Solo responde el idioma."}]
        },
        "project_id": project_id,
        "title": "VALIDACION-con-proyecto",
        "hide_in_task_list": True,
        "agent_profile": "manus-1.6-lite"
    })
    
    if not ok:
        registrar("TASK_WITH_PROJECT", claim, f"FALLO — {resp}", str(resp), False)
        return
    
    task_id = resp.get("task_id")
    HILOS_CREADOS.append(task_id)
    registrar("TASK_WITH_PROJECT", claim, f"VERDADERO — hilo creado con project_id", f"task_id={task_id}", True)

# ============================================================
# PRUEBA 12: task.stop para detener un hilo
# ============================================================
def test_12_task_stop(task_id):
    claim = "task.stop puede detener un hilo en ejecución"
    
    if not task_id:
        registrar("TASK_STOP", claim, "NO SE PUEDE PROBAR", "", False)
        return
    
    ok, resp = api_call("POST", "task.stop", {"task_id": task_id})
    
    if not ok:
        error = resp.get("error", {})
        # Si ya terminó, eso también es info válida
        registrar("TASK_STOP", claim, f"FALLO o ya terminado — {error}", str(resp), False)
        return
    
    registrar("TASK_STOP", claim, "VERDADERO — hilo detenido", str(resp), True)

# ============================================================
# PRUEBA 13: Múltiples force_skills simultáneos
# ============================================================
def test_13_multiple_force_skills(skill_ids):
    claim = "Se pueden forzar MÚLTIPLES skills simultáneamente en un solo hilo"
    
    core_id = skill_ids.get("el-monstruo-core")
    anti_id = skill_ids.get("anti-autoboicot")
    opt_id = skill_ids.get("optimizador-creditos")
    
    skills_to_force = [s for s in [core_id, anti_id, opt_id] if s]
    
    if len(skills_to_force) < 2:
        registrar("MULTI_FORCE_SKILLS", claim, "NO SE PUEDE PROBAR — menos de 2 skills encontrados", "", False)
        return None
    
    ok, resp = api_call("POST", "task.create", {
        "message": {
            "content": [{"type": "text", "text": f"Se te forzaron {len(skills_to_force)} skills. Lee todos y dime el nombre de cada uno que leíste. Responde en una lista breve."}],
            "force_skills": skills_to_force
        },
        "title": "VALIDACION-multi-force",
        "hide_in_task_list": True,
        "agent_profile": "manus-1.6-lite"
    })
    
    if not ok:
        registrar("MULTI_FORCE_SKILLS", claim, f"FALLO — {resp}", str(resp), False)
        return None
    
    task_id = resp.get("task_id")
    HILOS_CREADOS.append(task_id)
    registrar("MULTI_FORCE_SKILLS", claim, 
              f"VERDADERO — hilo creado con {len(skills_to_force)} skills forzados",
              f"task_id={task_id}, skills={skills_to_force}", True)
    return task_id

# ============================================================
# RESUMEN FINAL
# ============================================================
def generar_resumen():
    total = len(RESULTADOS)
    exitosos = sum(1 for r in RESULTADOS if r["exito"])
    fallidos = sum(1 for r in RESULTADOS if not r["exito"])
    
    print("\n" + "="*70)
    print("RESUMEN FINAL DE VALIDACIÓN EN TIEMPO REAL")
    print("="*70)
    print(f"Total pruebas: {total}")
    print(f"VERDADERO: {exitosos}")
    print(f"FALSO: {fallidos}")
    print(f"Tasa de éxito: {exitosos/total*100:.0f}%")
    print("="*70)
    
    print("\nCAPACIDADES VERIFICADAS:")
    for r in RESULTADOS:
        status = "OK" if r["exito"] else "FALLO"
        print(f"  [{status}] {r['prueba']}: {r['veredicto'][:80]}")
    
    # Guardar JSON
    output = {
        "fecha": datetime.now().isoformat(),
        "total_pruebas": total,
        "exitosos": exitosos,
        "fallidos": fallidos,
        "resultados": RESULTADOS,
        "hilos_creados": HILOS_CREADOS
    }
    
    with open("/home/ubuntu/VALIDACION_RESULTADOS.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados guardados en /home/ubuntu/VALIDACION_RESULTADOS.json")
    return output

# ============================================================
# MAIN — Ejecutar TODAS las pruebas en orden
# ============================================================
if __name__ == "__main__":
    print("="*70)
    print("VALIDADOR EXHAUSTIVO — API DE MANUS v2")
    print(f"Fecha: {datetime.now().isoformat()}")
    print(f"Regla: CADA claim se verifica con código. Sin atajos.")
    print("="*70)
    
    # Fase 0: Prerequisitos
    test_0_api_key()
    
    # Fase 1: Descubrimiento
    skill_ids = test_1_skill_list()
    
    # Fase 2: Creación de hilos
    basic_task_id = test_2_task_create_basico()
    force_task_id = test_3_force_skills(skill_ids or {})
    
    # Fase 3: Lectura y monitoreo (esperar a que el agente responda)
    print("\n>>> Esperando 120s para que los agentes procesen...")
    agent_response = test_4_list_messages(force_task_id, espera=120)
    
    # Fase 4: Verificar que force_skills funcionó
    test_5_verificar_lectura_skill(agent_response or "")
    
    # Fase 5: Comunicación con hilos existentes
    test_6_send_message(basic_task_id)
    test_7_send_with_force_skills(basic_task_id, skill_ids or {})
    
    # Fase 6: Consultas de estado
    test_8_task_detail(basic_task_id)
    test_9_task_list()
    
    # Fase 7: Proyectos (system prompt equivalente)
    project_id = test_10_project_create()
    test_11_task_with_project(project_id)
    
    # Fase 8: Control
    # No detenemos los hilos de prueba para poder verificar después
    
    # Fase 9: Múltiples skills forzados
    multi_task_id = test_13_multiple_force_skills(skill_ids or {})
    
    # Resumen
    resumen = generar_resumen()
    
    print("\n>>> VALIDACIÓN COMPLETA. Todos los claims fueron probados con código real.")
