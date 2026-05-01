# INSTRUCCIONES PARA HILO B — Sprint 46-47 Browser + Observabilidad

**Branch:** `feature/sprint-46-47-browser-obs` (ya creado y pusheado)  
**Regla:** NO mergear a main hasta que el Hilo Principal (yo) lo confirme.  
**Repo:** `git clone https://github.com/alfredogl1804/el-monstruo.git && git checkout feature/sprint-46-47-browser-obs`

---

## CONTEXTO

El Monstruo es un agente AI autónomo con:
- Kernel en Python 3.12 (FastAPI, desplegado en Railway)
- App Flutter iOS como frontend
- Gateway AG-UI (SSE→WebSocket bridge)
- E2B sandbox para code execution
- 6 agentes especializados, Task Planner ReAct, Embrión autónomo
- Memoria: LightRAG + Mem0 + pgvector sobre Supabase

El Hilo Principal (main) está implementando:
- 46.1 Conexión Usuario-Agente
- 46.2 File Ops en E2B
- 46.3 Stuck Detector
- 47.2 Web Dev Tool

Tú implementas lo siguiente en tu branch:

---

## TAREA 1: Sprint 46.4 — Observabilidad FCS + Langfuse

**Objetivo:** El Embrión calcula su Functional Consciousness Score y envía trazas a Langfuse.

**Archivos a crear/modificar:**
- `observability/langfuse_client.py` (NUEVO) — Cliente singleton de Langfuse
- `kernel/embrion_loop.py` — Agregar cálculo de FCS y envío de trazas

**Implementación:**
1. Instalar `langfuse` en `requirements.txt`
2. Crear `observability/langfuse_client.py` con:
   - Singleton `LangfuseClient` que lee `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` del env
   - Métodos: `trace_tool_call(tool_name, input, output, duration)`, `trace_llm_call(model, messages, response, tokens, duration)`, `trace_embrion_cycle(cycle_data)`
3. En `kernel/embrion_loop.py`:
   - Crear método `_calculate_fcs()` que compute: `FCS = (tool_calls_exitosos / total) * 0.3 + (lecciones_aprendidas / target) * 0.3 + (delegaciones_exitosas / total) * 0.2 + (uptime_ratio) * 0.2`
   - Guardar FCS en Supabase tabla `embrion_metrics` cada N latidos
   - Enviar traza a Langfuse en cada ciclo

**Variables de entorno necesarias en Railway:**
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`  
- `LANGFUSE_HOST` (default: `https://cloud.langfuse.com`)

**Criterio de éxito:** El Embrión calcula su FCS y las trazas aparecen en el dashboard de Langfuse.

---

## TAREA 2: Sprint 46.5 — Fix manus_bridge

**Objetivo:** Reparar la delegación a Manus que falla silenciosamente.

**Archivos a modificar:**
- `tools/manus_bridge.py`

**Implementación:**
1. Leer el archivo actual — el bug reportado en Latido 16 es que la delegación falla silenciosamente (no reporta errores al usuario)
2. Agregar:
   - Retry con backoff exponencial (3 intentos)
   - Timeout explícito (120s para create_and_wait)
   - Logging detallado de cada paso
   - Si falla después de 3 retries, retornar error explícito al usuario con el motivo
3. Verificar que `MANUS_API_KEY_GOOGLE` y `MANUS_API_KEY_APPLE` están configuradas correctamente

**Criterio de éxito:** El Embrión delega una tarea a Manus y recibe el resultado (o un error explícito si falla).

---

## TAREA 3: Sprint 47.1 — Browser Interactivo

**Objetivo:** El Monstruo puede navegar web interactivamente (clicks, forms, screenshots).

**Archivos a crear/modificar:**
- `tools/interactive_browser.py` (NUEVO)
- `requirements.txt` (agregar dependencias)

**Implementación:**
1. Investigar `browser-use/browser-harness` (8.8K stars, 13 días) — es un headless browser harness para AI agents
2. Si browser-harness no es viable como pip package, usar `playwright` como fallback:
   - `pip install playwright && playwright install chromium`
3. Crear `tools/interactive_browser.py` con acciones:
   - `navigate(url)` — ir a URL
   - `click(selector)` — click en elemento
   - `type(selector, text)` — escribir en input
   - `screenshot()` — captura de pantalla (retornar base64)
   - `get_text(selector)` — extraer texto
   - `scroll(direction)` — scroll up/down
   - `wait(selector, timeout)` — esperar elemento
   - `evaluate(js)` — ejecutar JavaScript
4. El browser debe correr en un proceso persistente (no abrir/cerrar por cada acción)
5. Registrar el tool en `kernel/tool_dispatch.py` con spec:
   ```python
   ToolSpec(
       name="interactive_browser",
       description="Navigate and interact with web pages: click buttons, fill forms, take screenshots, extract data.",
       parameters={...}
   )
   ```

**Criterio de éxito:** Claude navega a un sitio, hace login con credenciales, extrae datos de una tabla, y reporta resultados.

---

## TAREA 4: Sprint 47.3 — Media Generation

**Objetivo:** El Monstruo puede generar imágenes, audio, y presentaciones.

**Archivos a crear/modificar:**
- `tools/media_gen.py` (NUEVO)
- `requirements.txt`

**Implementación:**
1. Crear `tools/media_gen.py` con sub-acciones:
   - `generate_image(prompt, style, size)` — Usar OpenAI DALL-E 3 API (`OPENAI_API_KEY` ya existe)
   - `generate_speech(text, voice)` — Usar ElevenLabs API (`ELEVENLABS_API_KEY` ya existe en el entorno)
   - `generate_presentation(title, slides_content)` — Crear HTML slides con reveal.js en E2B, servir como URL
2. Para imágenes: llamar a `client.images.generate(model="dall-e-3", prompt=..., size=..., quality="hd")`
3. Para audio: llamar a ElevenLabs TTS API
4. Para presentaciones: generar HTML con reveal.js, guardar en E2B, servir via HTTP
5. Registrar en `kernel/tool_dispatch.py`

**Criterio de éxito:** "Genera un logo para mi empresa" → devuelve URL de imagen. "Crea una presentación de 5 slides sobre X" → devuelve URL.

---

## REGLAS GENERALES

1. **NO tocar estos archivos** (los toca el Hilo Principal):
   - `kernel/nodes.py`
   - `kernel/engine.py`
   - `kernel/agui_adapter.py`
   - `kernel/task_planner.py`
   - `tools/file_ops.py`
   - `tools/web_dev.py`

2. **Commits frecuentes** con mensajes descriptivos tipo: `feat(browser): add interactive browser tool with Playwright`

3. **Tests básicos** para cada tool: crear un archivo `tests/test_<tool>.py` con al menos 1 test que valide la interfaz.

4. **NO mergear a main.** Cuando termines, avisa y el Hilo Principal revisará y mergeará.

---

## ORDEN DE EJECUCIÓN RECOMENDADO

1. Tarea 2 (Fix manus_bridge) — más rápida, 30 min
2. Tarea 1 (FCS + Langfuse) — 1-2 horas
3. Tarea 4 (Media Gen) — 1-2 horas
4. Tarea 3 (Browser Interactivo) — 2-3 horas (la más compleja)
