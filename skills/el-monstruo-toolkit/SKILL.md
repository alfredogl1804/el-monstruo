---
name: el-monstruo-toolkit
description: Arsenal operativo pre-configurado para El Monstruo. Contiene todas las herramientas, APIs, secrets, configuraciones y patrones de conexión listos para inyectar en cualquier hilo que trabaje en El Monstruo. Usar cuando se construya, modifique, despliegue o debuggee cualquier componente del Monstruo. Elimina el tiempo de descubrimiento — todo el stack está aquí.
---

# El Monstruo Toolkit — Arsenal Operativo Listo para Inyectar

Activar en CUALQUIER tarea que involucre construir, modificar, desplegar o debuggear El Monstruo.

## Decisión Rápida

1. **Necesito conectar un cerebro** → Sección 2 (Cerebros) + `references/brain_configs.yaml`
2. **Necesito inyectar secrets** → Sección 3 (Secrets) + `templates/monstruo_manifest.yaml`
3. **Necesito configurar un servicio** → Sección 4 (Servicios) + `references/service_configs.yaml`
4. **Necesito desplegar** → Sección 5 (Deploy)
5. **Necesito los MCPs** → Sección 6 (MCPs)
6. **Algo falla** → Sección 7 (Fallbacks)
7. **Quiero el código de conexión** → `references/connection_snippets.py`

## 1. Stack Técnico del Monstruo

### Estado Actual (Producción — Railway)

| Componente | Herramienta | Estado |
|-----------|-------------|--------|
| Interface | Telegram Bot API (`python-telegram-bot`) | Activo |
| Clasificador | GPT-4o (via OpenAI SDK) | Activo |
| Investigación | Perplexity Sonar Pro (via requests) | Activo |
| Código/Creativo | Grok 4.20 (via xAI SDK) | Activo |
| Análisis | DeepSeek R1 (via OpenRouter) | Activo |
| Estrategia | GPT-5.4 (via OpenAI SDK) | Activo |
| Memoria | Supabase pgvector + OpenAI embeddings | Activo |
| Leads DB | Notion API | Activo |
| Deploy | Railway | Activo |
| Repo | github.com/alfredogl1804/el-monstruo-bot (privado) | Activo |

### Estado Objetivo (Sprint 1)

| Componente | Herramienta | Versión | Estado |
|-----------|-------------|---------|--------|
| Kernel | LangGraph | 1.1.6 | Pendiente |
| Router | LiteLLM | 1.83.3 (ANCLAR) | Pendiente |
| Memoria | Mem0 OSS + Supabase pgvector | latest | Pendiente |
| Estado | Supabase Postgres | pgvector 0.8.2 | Parcial |
| Observabilidad | Langfuse | latest | Pendiente |
| Consola | Next.js 16 + shadcn/ui + Vercel AI SDK | 16.2.2 | Pendiente |
| Backend | Railway | - | Activo |

### Alerta de Seguridad

**LiteLLM**: Versiones 1.82.7 y 1.82.8 comprometidas (CVE-2026-35030). ANCLAR `litellm==1.83.3` en requirements.txt. Verificar hash post-instalación.

## 2. Los 6 Cerebros — Configuración Exacta

### GPT-5.4 (Estratega + Sintetizador + Clasificador)

```python
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
# Para chat/estrategia:
response = client.chat.completions.create(
    model="gpt-5.4",
    messages=[...],
    max_completion_tokens=4000  # NUNCA usar max_tokens con GPT-5.4
)
# Para embeddings (memoria):
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input=text[:8000]
)
```

- **Env var**: `OPENAI_API_KEY`
- **Contexto**: 1.05M tokens
- **Usa para**: Estrategia, síntesis, clasificación de tareas, extracción de datos, embeddings
- **Anti-error**: NUNCA `max_tokens`, solo `max_completion_tokens`
- **Modelo actual en bot**: `gpt-4o` (clasificador + plan). Migrar a `gpt-5.4` en Sprint 1

### Claude Opus 4.6 (Arquitecto + Crítico)

```python
import anthropic
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    system="...",
    messages=[...]
)
```

- **Env var**: `ANTHROPIC_API_KEY`
- **Contexto**: 1M tokens
- **Usa para**: Arquitectura, code review, análisis profundo, documentación técnica
- **Anti-error**: El model_id es `claude-opus-4-6`, NO `claude-4-20250514`
- **Estado en bot**: NO integrado aún. Agregar como fallback de GPT-5.4

### Gemini 3.1 Pro (Creativo + Multimodal)

```python
from google import genai
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="..."
)
```

- **Env var**: `GEMINI_API_KEY`
- **Contexto**: 1M tokens
- **Usa para**: Contenido creativo, análisis multimodal (imágenes/video), grounding con búsqueda
- **Estado en bot**: NO integrado. Agregar para tareas creativas y multimodales

### Grok 4.20 (Código + Creativo + Tiempo Real)

```python
from openai import OpenAI
client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1"
)
response = client.chat.completions.create(
    model="grok-4.20-0309-reasoning",
    messages=[...],
    max_tokens=2000
)
```

- **Env var**: `XAI_API_KEY`
- **Contexto**: 2M tokens (el más largo)
- **Usa para**: Código, creatividad, información en tiempo real, crítica
- **Anti-error**: Model_id es `grok-4.20-0309-reasoning`, NO `grok-4-latest`
- **Estado en bot**: Activo pero usa `grok-3-latest`. Actualizar a `grok-4.20-0309-reasoning`

### DeepSeek R1 (Razonador + Analista)

```python
from openai import OpenAI
client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)
response = client.chat.completions.create(
    model="deepseek/deepseek-r1",
    messages=[...],
    max_tokens=2000
)
```

- **Env var**: `OPENROUTER_API_KEY` (va por OpenRouter, NO directo)
- **Contexto**: 128K tokens
- **Usa para**: Matemáticas, optimización, análisis técnico profundo, razonamiento
- **Anti-error**: SIEMPRE via OpenRouter. No tiene API directa accesible
- **Estado en bot**: Activo y correcto

### Perplexity Sonar Pro (Investigador)

```python
import requests
headers = {
    "Authorization": f"Bearer {os.environ['SONAR_API_KEY']}",
    "Content-Type": "application/json"
}
data = {
    "model": "sonar-reasoning-pro",
    "messages": [...]
}
resp = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers=headers, json=data, timeout=120
)
```

- **Env var**: `SONAR_API_KEY`
- **Contexto**: 128K tokens
- **Usa para**: Investigación en tiempo real, verificación de hechos, leads
- **Anti-error**: NUNCA usar SDK de OpenAI. Solo `requests` directo
- **Estado en bot**: Activo con `sonar-pro`. Actualizar a `sonar-reasoning-pro`

## 3. Secrets — Manifiesto Completo

### Secrets Obligatorios (el bot NO funciona sin estos)

| Secret | Env Var | Servicio | Disponible en Sandbox |
|--------|---------|----------|----------------------|
| Telegram Bot Token | `TELEGRAM_BOT_TOKEN` | Telegram Bot API | NO — solo en Railway |
| OpenAI API Key | `OPENAI_API_KEY` | GPT-5.4 + Embeddings | SI |
| Perplexity API Key | `SONAR_API_KEY` | Investigación | SI |
| xAI API Key | `XAI_API_KEY` | Grok 4.20 | SI |
| OpenRouter API Key | `OPENROUTER_API_KEY` | DeepSeek R1 + modelos gratis | SI |
| Supabase URL | `SUPABASE_URL` | Memoria semántica | Parcial (hardcoded en bot) |
| Supabase Service Key | `SUPABASE_SERVICE_KEY` | Memoria semántica | NO — solo en Railway |

### Secrets Opcionales (funcionalidad extendida)

| Secret | Env Var | Servicio | Disponible en Sandbox |
|--------|---------|----------|----------------------|
| Notion API Key | `NOTION_API_KEY` | Leads DB | Via MCP (no env var directa) |
| Anthropic API Key | `ANTHROPIC_API_KEY` | Claude Opus 4.6 | SI |
| Gemini API Key | `GEMINI_API_KEY` | Gemini 3.1 Pro | SI |
| ElevenLabs API Key | `ELEVENLABS_API_KEY` | Voz/Audio | SI |
| HeyGen API Key | `HEYGEN_API_KEY` | Video con avatares | SI |
| Dropbox API Key | `DROPBOX_API_KEY` | Almacenamiento | SI |
| Cloudflare Token | `CLOUDFLARE_API_TOKEN` | Workers/CDN | SI |

### Secrets de Sprint 1 (necesarios para la evolución)

| Secret | Env Var | Servicio | Notas |
|--------|---------|----------|-------|
| Langfuse Public Key | `LANGFUSE_PUBLIC_KEY` | Observabilidad | Crear en langfuse.com |
| Langfuse Secret Key | `LANGFUSE_SECRET_KEY` | Observabilidad | Crear en langfuse.com |
| Langfuse Host | `LANGFUSE_HOST` | Observabilidad | `https://cloud.langfuse.com` |

### Inyección Rápida

```bash
# Generar manifiesto para el Monstruo:
python3.11 /home/ubuntu/skills/api-context-injector/scripts/inject_secrets.py \
    --generate-manifest /home/ubuntu/monstruo-deploy

# Inyectar en sandbox (desarrollo):
python3.11 /home/ubuntu/skills/api-context-injector/scripts/inject_secrets.py \
    --project /home/ubuntu/monstruo-deploy --target sandbox

# Inyectar en Vercel (consola web Sprint 1):
python3.11 /home/ubuntu/skills/api-context-injector/scripts/inject_secrets.py \
    --project /path/to/consola --target vercel --dry-run
```

→ Manifiesto pre-configurado: `templates/monstruo_manifest.yaml`

## 4. Servicios de Infraestructura

### Supabase (Memoria + Estado + Vector Search)

- **Project ID**: `xsumzuhwmivjgftsneov`
- **URL**: `https://xsumzuhwmivjgftsneov.supabase.co`
- **Dashboard**: https://supabase.com/dashboard/project/xsumzuhwmivjgftsneov
- **Tablas activas**: `monstruo_memory` (memoria semántica)
- **Funciones RPC**: `match_memories` (búsqueda vectorial)
- **Corpus El Monstruo**: 578 docs, 25,573 chunks, 23,473 embeddings
- **Acceso**: Via MCP (`manus-mcp-cli --server supabase`) o REST API

```python
# Conexión directa REST:
headers = {
    "apikey": os.environ["SUPABASE_SERVICE_KEY"],
    "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_KEY']}",
    "Content-Type": "application/json"
}
# Guardar memoria:
requests.post(f"{SUPABASE_URL}/rest/v1/monstruo_memory", headers=headers, json=payload)
# Buscar memorias:
requests.post(f"{SUPABASE_URL}/rest/v1/rpc/match_memories", headers=headers, json=query)
```

### Notion (Leads + Dashboard + Conocimiento)

- **Dashboard Monstruo**: https://www.notion.so/33a14c6f8bba813d998dcbb1bf88bdd9
- **API Keys DB**: `54b9d97704bc408d8453c1524fbfec9b`
- **Acceso**: Via MCP (`manus-mcp-cli --server notion`)
- **Usa para**: Leads DB, dashboard operativo, almacén de conocimiento

### Railway (Deploy Backend)

- **Project ID**: `1dcb47ee-6c01-44bb-baff-d89812382fee`
- **Repo**: `github.com/alfredogl1804/el-monstruo-bot` (privado)
- **Branch**: `master`
- **Auto-deploy**: SI (push → deploy automático)
- **Límite**: 15 min en conexiones HTTP/WS (usar SSE, no WebSockets)
- **Deploy manual**: `cd /home/ubuntu/monstruo-deploy && git push origin master`

### Vercel (Consola Web — Sprint 1)

- **Usa para**: Consola PWA del Monstruo (Next.js 16 + shadcn/ui)
- **Acceso**: Via MCP (`manus-mcp-cli --server vercel`)
- **Runtime**: Edge Runtime para streaming
- **Secrets**: Via MCP o `inject_secrets.py --target vercel`

## 5. Deploy — Flujo Completo

### Deploy actual (bot Telegram):

```bash
# 1. Matar instancia local si existe
pkill -f "python.*bot.py" 2>/dev/null

# 2. Hacer cambios
cd /home/ubuntu/monstruo-deploy
# ... editar bot.py ...

# 3. Commit y push
git add . && git commit -m "descripción del cambio"
git push origin master
# Railway redeploya automáticamente
```

### Deploy Sprint 1 (consola + backend):

```bash
# Backend (Railway) — mismo flujo de arriba
# Consola (Vercel) — via MCP o CLI
manus-mcp-cli tool call vercel_deploy --server vercel --input '{"project": "monstruo-consola"}'
```

## 6. MCPs Disponibles para El Monstruo

| MCP | Uso en El Monstruo | Comando |
|-----|---------------------|---------|
| notion | Leads DB, dashboard, conocimiento | `manus-mcp-cli tool call notion-search --server notion` |
| supabase | Memoria, estado, vector search | `manus-mcp-cli tool call ... --server supabase` |
| gmail | Enviar emails desde el bot | `manus-mcp-cli tool call ... --server gmail` |
| google-calendar | Gestionar agenda de Alfredo | `manus-mcp-cli tool call ... --server google-calendar` |
| asana | Gestión de tareas/proyectos | `manus-mcp-cli tool call ... --server asana` |
| zapier | Automatizaciones cross-app | `manus-mcp-cli tool call ... --server zapier` |
| vercel | Deploy consola web | `manus-mcp-cli tool call ... --server vercel` |
| instagram | Publicar contenido | `manus-mcp-cli tool call ... --server instagram` |
| outlook-mail | Email corporativo | `manus-mcp-cli tool call ... --server outlook-mail` |
| paypal-for-business | Pagos y facturas | `manus-mcp-cli tool call ... --server paypal-for-business` |
| revenuecat | Suscripciones | `manus-mcp-cli tool call ... --server revenuecat` |

## 7. Cadenas de Fallback por Rol

| Rol | Primario | Fallback 1 | Fallback 2 |
|-----|----------|------------|------------|
| Estratega | GPT-5.4 | Claude Opus 4.6 | Grok 4.20 |
| Investigador | Perplexity Sonar Pro | Grok 4.20 | GPT-5.4 + web search |
| Razonador | DeepSeek R1 | GPT-5.4 | Claude Opus 4.6 |
| Sintetizador | GPT-5.4 | Claude Opus 4.6 | Gemini 3.1 Pro |
| Crítico | Grok 4.20 | DeepSeek R1 | Claude Opus 4.6 |
| Creativo | Gemini 3.1 Pro | GPT-5.4 | Claude Opus 4.6 |
| Código | Grok 4.20 | DeepSeek R1 | Claude Opus 4.6 |
| Embeddings | OpenAI text-embedding-3-small | — | — |
| Voz | ElevenLabs | AWS Polly (via OpenRouter) | OpenAI TTS |
| Video | HeyGen | — | — |

**ALTO TOTAL si < 3 cerebros disponibles.**

## 8. Modelos Gratuitos via OpenRouter (Ahorro)

Para tareas de bajo riesgo o prototipos, usar modelos gratuitos:

| Modelo | Contexto | Mejor para |
|--------|----------|-----------|
| NVIDIA Nemotron 3 Super | 1M | Finanzas, código (Prog #9) |
| Gemma 4 26B A4B | 256K | Multimodal, tool calling |
| Gemma 4 31B | 256K | Código, 140+ idiomas |
| Llama 4 Scout | 512K | Contexto largo gratis |
| Cohere Rerank 4 Pro | 33K | Reranking RAG (100+ idiomas) |

```python
# Conexión a modelos gratis via OpenRouter:
client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)
response = client.chat.completions.create(
    model="nvidia/nemotron-3-super:free",  # GRATIS
    messages=[...]
)
```

## 9. Bugs Conocidos y Workarounds

| Bug | Workaround |
|-----|-----------|
| 409 Conflict en Telegram | Matar instancia local: `pkill -f "python.*bot.py"` |
| Mem0 `.single()` bug #4596 | Usar workaround documentado en Mem0 issues |
| Railway 15 min timeout | Usar SSE en vez de WebSockets |
| Bot usa `gpt-4o` en vez de `gpt-5.4` | Actualizar model_id en bot.py |
| Bot usa `grok-3-latest` en vez de `grok-4.20` | Actualizar model_id en bot.py |
| Bot usa `sonar-pro` en vez de `sonar-reasoning-pro` | Actualizar model_id en bot.py |

## Reglas Inquebrantables

1. **NUNCA** desplegar sin matar la instancia local primero
2. **NUNCA** usar `max_tokens` con GPT-5.4 — solo `max_completion_tokens`
3. **NUNCA** usar SDK OpenAI para Perplexity — solo `requests`
4. **NUNCA** exponer `SUPABASE_SERVICE_KEY` en frontend
5. **SIEMPRE** anclar `litellm==1.83.3` (CVE-2026-35030)
6. **SIEMPRE** verificar hash de LiteLLM post-instalación
7. **SIEMPRE** usar `deepseek/deepseek-r1` via OpenRouter, no directo
8. **SIEMPRE** consultar `el-monstruo` skill para contexto del corpus antes de decisiones arquitectónicas
9. **SIEMPRE** consultar `el-monstruo-plan` skill para el blueprint de Sprint 1

## Metadata

```yaml
version: "1.0"
last_verified: "2026-04-09"
ttl_days: 30
depends_on:
  - api-context-injector  # Fuente de verdad de APIs y secrets
  - el-monstruo           # Contexto del corpus
  - el-monstruo-plan      # Blueprint Sprint 1
  - el-monstruo-bot       # Estado del bot en producción
feeds_into:
  - Cualquier hilo que trabaje en El Monstruo
```
