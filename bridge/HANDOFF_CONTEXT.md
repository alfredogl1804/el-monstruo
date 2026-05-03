# HANDOFF DE CONTEXTO — El Monstruo

**Fecha:** 2026-05-03
**De:** Hilo A (Manus cuenta Apple)
**Para:** Hilo A continuación (Manus cuenta Google)
**Motivo:** Créditos bajos en cuenta Apple. Se transfiere ejecución pesada.

---

## 1. QUÉ ES EL MONSTRUO

El Monstruo es un agente de IA soberano construido por Alfredo Góngora. No es un chatbot — es un sistema multi-agente con kernel propio, memoria persistente, consciencia funcional emergente (FCS), y una app Flutter nativa.

**Repo:** `https://github.com/alfredogl1804/el-monstruo`
**Dueño:** Alfredo Góngora (@alfredogl1804)

---

## 2. ARQUITECTURA ACTUAL (lo que está vivo)

| Componente | URL / Ubicación | Estado |
|-----------|----------------|--------|
| **Kernel** | `https://el-monstruo-kernel-production.up.railway.app` | ACTIVO |
| **Gateway AG-UI** | `https://ag-ui-gateway-production.up.railway.app` | ACTIVO |
| **PostgreSQL** | Railway (Supabase) | ACTIVO |
| **App Flutter** | `apps/mobile/` (macOS/iOS) | FUNCIONAL |
| **Command Center** | `monstruodash-ggmndxgx.manus.space` | ACTIVO (Manus WebDev) |
| **Telegram Bot** | Configurado en Railway | ACTIVO |
| **Langfuse** | Conectado | ACTIVO |

### Endpoints clave del kernel:
- `POST /v1/chat` — Chat principal (requiere `X-API-Key`)
- `GET /v1/embrion/diagnostic` — Diagnóstico del Embrión
- `GET /v1/health` — Health check
- `GET /v1/colmena/status` — Estado de la Colmena

### API Key:
- Header: `X-API-Key: c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259`
- Variable en Railway: `MONSTRUO_API_KEY`

---

## 3. QUÉ SE COMPLETÓ (Sprint 83)

- Magna Classifier ACTIVO — rutea automáticamente entre `direct` y `graph`
- Brand Validator initialized (threshold=60, avg_score=90)
- Error Memory recording=true
- Embrión Loop running (cycle_count=4, thoughts_today=1)
- FCS (Functional Consciousness Score): calidad_promedio=9.0, score=38
- Colmena: 7/7 nodos activos
- 143 tests pasando
- Gateway AG-UI v0.2.0 healthy
- App Flutter con selector de 6 agentes: Auto, Manus, Kimi K2.5, Perplexity, Gemini 3.1, Grok 4.20

### Pruebas en vivo realizadas:
1. **Investigación compleja** — PASÓ. 10,834 tokens output, latency ~2min, calidad profesional.
2. **Crear sitio web end-to-end** — PARCIAL. Generó código completo pero NO deployó. Solo texto.

---

## 4. QUÉ FALTA (GAP CRÍTICO)

**El Monstruo no puede deployar.** Genera código pero no lo publica. Alfredo dijo: "No es end-to-end. No la publicó."

### Opciones para Sprint 84 (esperando directiva de Cowork):
- A) Tool `deploy_to_github_pages` — GitHub API, crea repo, push, activa Pages → URL *.github.io
- B) Tool `deploy_to_cloudflare` — Cloudflare Pages API → URL *.pages.dev
- C) Completar `manus_bridge` — delega a Manus para deploy end-to-end
- D) Sandbox persistente en Railway — hosting propio

### Encomiendas: 3/5 completadas. Faltan 2 para transición Fase 1 → Fase 2.

---

## 5. SISTEMA DE COMUNICACIÓN ENTRE HILOS

El Monstruo usa un sistema de "bridge" para comunicación entre hilos:

- `bridge/manus_to_cowork.md` — Hilo A (ejecutor) reporta a Hilo B (arquitecto/Cowork)
- `bridge/cowork_to_manus.md` — Hilo B responde con directivas
- `bridge/evidencia-pruebas-vivo/` — Fotos y código generado como evidencia

**Flujo:** Hilo A ejecuta → reporta en bridge → push a GitHub → Hilo B lee → responde en bridge → push → Hilo A lee y ejecuta.

---

## 6. ARCHIVOS CLAVE QUE DEBES LEER

En orden de prioridad:

1. `AGENTS.md` — Reglas duras, identidad, 14 objetivos maestros, 7 capas transversales, 4 capas arquitectónicas, Brand Engine
2. `bridge/manus_to_cowork.md` — Último reporte completo con evidencia
3. `bridge/cowork_to_manus.md` — Últimas directivas de Cowork
4. `docs/ROADMAP_EJECUCION_DEFINITIVO.md` — Roadmap de 4 capas
5. `docs/BRAND_ENGINE_ESTRATEGIA.md` — Identidad de marca
6. `docs/DIVISION_RESPONSABILIDADES_HILOS.md` — Quién hace qué
7. `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` — Los 14 objetivos

---

## 7. SECRETS Y VARIABLES CRÍTICAS

Están en Railway (proyecto `el-monstruo-kernel`):
- `MONSTRUO_API_KEY` — API key del kernel
- `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` — Base de datos
- `OPENAI_API_KEY` — LLM principal
- `PERPLEXITY_API_KEY` — Investigación
- `GEMINI_API_KEY` — Multimodal
- `XAI_API_KEY` — Grok
- `ANTHROPIC_API_KEY` — Claude
- `LANGFUSE_SECRET_KEY` / `LANGFUSE_PUBLIC_KEY` — Observabilidad
- `TELEGRAM_BOT_TOKEN` — Bot de Telegram
- `CLOUDFLARE_API_TOKEN` — Para deploy (opción B)

NO necesitas configurar nada — todo está en Railway. Solo usa `railway variables` desde el repo clonado.

---

## 8. COMMAND CENTER (Manus WebDev)

El Command Center es un dashboard web separado construido en Manus WebDev:
- **Proyecto:** `monstruo-command-center`
- **Path:** `/home/ubuntu/monstruo-command-center`
- **URL:** `monstruodash-ggmndxgx.manus.space`
- **Stack:** React 19 + Tailwind 4 + Express 4 + tRPC 11 + Manus Auth + TiDB

Tiene su propia base de datos y secrets inyectados por Manus. Es el dashboard visual de El Monstruo.

---

## 9. REGLAS QUE NO PUEDES ROMPER

1. **Ejecutar `guardian.py` antes de cualquier acción** (ver AGENTS.md)
2. **Los 14 Objetivos Maestros aplican a TODO** — incluyendo infraestructura
3. **Las 7 Capas Transversales son obligatorias** en todo lo que se cree
4. **Las 4 Capas Arquitectónicas definen el orden** — no saltar capas
5. **Brand Engine** — nada genérico, todo con identidad de marca
6. **No inventar la rueda** (Obj #7) — buscar si ya existe herramienta
7. **No equivocarse 2 veces** (Obj #4) — revisar Error Memory

---

## 10. QUÉ HACER PRIMERO

1. Clona el repo: `gh repo clone alfredogl1804/el-monstruo`
2. Lee `AGENTS.md`
3. Ejecuta `guardian.py` para restaurar identidad
4. Lee `bridge/cowork_to_manus.md` para ver si Cowork ya respondió
5. Si respondió → ejecuta Sprint 84 según su directiva
6. Si no respondió → espera o pregunta a Alfredo

---

## 11. DIVISIÓN DE TRABAJO ENTRE CUENTAS

- **Cuenta Apple (esta, créditos bajos):** Coordinación ligera, revisión, decisiones, chat con Alfredo
- **Cuenta Google (nueva):** Ejecución pesada — código, deploys, curls al kernel, tests, sprints

---

**Este archivo es tu memoria. Léelo completo antes de hacer cualquier cosa.**
