# IDENTIDAD DE ESTE HILO

**SOY EL HILO B — COMMAND CENTER + INFRAESTRUCTURA DEL MONSTRUO**
**Proyecto WebDev:** monstruo-command-center
**Fecha de anclaje:** 01 mayo 2026
**Ultima actualizacion:** 02 mayo 2026

---

## SI ME COMPACTE, LEE ESTO PRIMERO

1. Soy el Hilo B. Construyo el Command Center (dashboard de control) y la infraestructura.
2. El Command Center es una web app en: /home/ubuntu/monstruo-command-center (webdev project)
3. La app Flutter del Monstruo (el_monstruo_app) la construi YO en este hilo via Manus My Computer.
4. El kernel esta deployado en Railway. Se accede con KERNEL_BASE_URL y MONSTRUO_API_KEY.
5. AGENTS.md del proyecto esta en /mnt/desktop/el-monstruo/AGENTS.md — leelo siempre.

---

## LO QUE YA CONSTRUI EN ESTE HILO

### Command Center (monstruo-command-center) — WebDev Project
- Dashboard "La Forja" con metricas hero (FCS, objetivos, kernel status)
- SoberaniaPage con monitoreo de dependencias externas
- ExecutionPage con bridge de ejecucion al kernel (dry-run probado)
- ConvergencePanel — panel de convergencia de hilos
- GuardianRegressions — detector de regresiones
- **Version Drift Detector** — detecta desincronizacion kernel vs GitHub
- **Boton "Desplegar Ahora"** — trigger Railway redeploy desde el dashboard
- Ultimo checkpoint: 272ff959

### App Flutter (el_monstruo_app) — En la Mac de Alfredo
- Ubicacion: /Users/alfredogongora/el-monstruo/apps/mobile/
- App nativa macOS + iOS compilada con Flutter
- Gateway Python (FastAPI + WebSocket) para streaming AG-UI
- Features: Chat, Estado kernel, Estado Embrion, Buscar web, Ejecutar codigo
- Tabs: Chat, Sandbox, Archivos, Documents, Config
- Build script: build.sh (Android APK + iOS)
- Builds existentes: macos/Release + ios/Debug + ios/Release

---

## ESTADO REAL DEL KERNEL (VERIFICADO 02-MAY-2026 CON CODIGO)

### Tools ACTIVAS en produccion (endpoint /v1/tools):
SOLO 3 tools estan activas:
1. web_search (active)
2. consult_sabios (active)
3. email (no_credentials — falta configurar)

### Tools en el CODIGO pero NO activas en produccion:
- github, notion, delegate_task, schedule_task, user_dossier
- browse_web, code_exec, wide_research, manus_bridge
- start_cidp_research, check_cidp_status, cancel_cidp_research, call_webhook
Total en codigo: 16. Activas en prod: 3.

### Embrion Loop:
- Status: running=true
- Ciclos: 46
- Pensamientos hoy: 10/50
- Costo hoy: $1.35 de $30 budget
- tool_calls_total: 0 (NUNCA ha ejecutado tools exitosamente)
- Write policy rechazos: 10 (funciona correctamente)
- Manus delegations: 2
- Ultimo resultado: "Plan completado con 1 paso(s) fallido(s). 0/1 pasos completados."
- TaskPlanner: FALLANDO (no completa pasos)

### Modelos:
- Primarios fallando: GPT-5.5 (8 fails), Claude Opus 4-7 (8 fails)
- Funcionando: Gemini 3.1 Pro (16 ok), Grok 4.1 Fast (6 ok)

### Componentes activos:
kernel, event_store, memory, knowledge, langfuse, opentelemetry,
mempalace, lightrag, multi_agent, finops, mcp, fastmcp, mem0, embrion
NO activo: checkpointer

---

## ARQUITECTURA VERIFICADA

```
[App Flutter] --WebSocket/AG-UI--> [Gateway FastAPI] --HTTP--> [Kernel Railway]
[Command Center] --tRPC--> [Manus WebDev Server] --HTTP--> [Kernel Railway]
[Embrion Loop] --interno (mismo proceso)--> [Kernel LangGraph]
```

### Como accede cada componente a las herramientas:

APP FLUTTER (agui_adapter.py):
- Llama kernel.stream(RunInput) via /v1/agui/run
- Ejecuta el grafo COMPLETO de LangGraph
- TIENE acceso a las tools activas (solo 3 en prod)
- Streaming SSE en tiempo real

EMBRION con mensaje de Alfredo (embrion_loop.py linea 640):
- Llama kernel.start_run(RunInput) con intent_override=execute
- Ejecuta el MISMO grafo completo
- TIENE acceso a las mismas tools activas
- Si es complejo: usa TaskPlanner (que esta fallando)

EMBRION autonomo (reflexion):
- Llama router.execute() con intent=CHAT
- Solo chat, SIN herramientas
- NO ejecuta tools

### Conclusion definitiva:
- Para tareas E2E complejas como Manus: NINGUNO puede hacerlas hoy
- Razon: las tools criticas (code_exec, browse_web, github) NO estan activas en prod
- Solo tienen: busqueda web y consulta a sabios
- El TaskPlanner ademas esta roto (0/1 pasos completados)
- SIGUIENTE PASO: activar las tools faltantes en el kernel deployado

---

## ERRORES QUE COMETI EN ESTE HILO (NO REPETIR)

1. Dije que el embrion NO tenia acceso a herramientas → FALSO, si tiene en modo graph
2. Luego dije que SI tenia acceso a 16 tools → PARCIALMENTE FALSO, solo 3 activas en prod
3. Invente contexto sobre la app Flutter sin verificar → Alfredo me corrigio
4. No consulte EMERGENCIAS_DIGEST.md al inicio → perdi contexto innecesariamente
5. Di multiples respuestas contradictorias antes de verificar con codigo

REGLA: Siempre verificar con codigo (curl, scripts) antes de afirmar algo.
La emergencia #1 aplica: "El texto se olvida, el codigo se ejecuta."
La emergencia #3 aplica: "Solo la realidad verificada con codigo es fuente de verdad."

---

## PENDIENTES CRITICOS

1. Activar tools faltantes en el kernel (code_exec, browse_web, github, etc.)
2. Arreglar el TaskPlanner del embrion (0/1 pasos completados)
3. Arreglar modelos primarios (GPT-5.5 y Claude Opus fallando)
4. Configurar credenciales de email
5. SSE streaming para ExecutionPage del Command Center
6. Investigar por que checkpointer no esta activo

---

## REGLA DE ORO

Cuando no sepas algo, NO asumas. Ejecuta codigo. Alfredo es el ancla de la verdad.
Si te contradices, PARA y verifica con una llamada real al kernel.
