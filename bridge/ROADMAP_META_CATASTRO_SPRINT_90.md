# ROADMAP META-CATASTRO (Sprint 90+)

**Documento:** Roadmap del Catastro post-MEGA-CATASTRO (Sprint 88.3 cerrado)
**Fecha:** 2026-05-10
**Hilo origen:** Hilo Catastro (Manus B)
**Predecesor:** DSC-G-007.5 (cierre Sprint MEGA-CATASTRO 88.1+88.2+88.3)
**Estado:** 📋 Propuesta — pendiente de revisión Cowork + aprobación Alfredo

---

## Contexto

Con MEGA-CATASTRO cerrado, el Catastro contiene **3 macroáreas activas y 173 entidades clasificadas**:

| Macroárea | Tabla | Entidades | Tronos |
|---|---|---|---|
| `inteligencia` | `catastro_modelos` | 37 LLMs | 4 dominios |
| `agentes` | `catastro_agentes` | 98 productos | 12 dominios |
| `vision_generativa` | `catastro_vision_generativa` | 38 productos | 12 subdominios |

**24 tronos firmes** disponibles para la lógica de selección del Monstruo. Pero quedan macroáreas sin catalogar y capacidades sin explotar.

---

## Estructura del roadmap

El roadmap META-CATASTRO se divide en **5 bloques temáticos** con 10 sprints propuestos. Cada sprint requiere DSC firmado y validación adversarial.

### Bloque A — Macroáreas pendientes (4 sprints)

#### Sprint 90 — Macroárea `voz_inteligencia`

Distinto de TTS porque integra **STT/ASR + voicebots + diarización + cloning ético**. ~25 productos seed.

**Subdominios canónicos propuestos:**
- `asr_transcripcion_premium` (Whisper-Turbo, AssemblyAI, Deepgram)
- `voicebots_realtime` (Vapi, Retell, Bland)
- `voice_cloning_etico` (ElevenLabs Cloning, OpenVoice)
- `diarizacion_multi_speaker` (Pyannote, AssemblyAI Speaker Diarization)
- `traduccion_voz_realtime` (HeyGen Translate, Speechify)

#### Sprint 91 — Macroárea `infraestructura_ai`

Plataformas de hosting + serverless GPUs + vector DBs + orchestration. ~30 productos seed.

**Subdominios canónicos propuestos:**
- `vector_dbs` (Pinecone, Weaviate, Qdrant, Chroma)
- `serverless_gpus` (Modal, Replicate, RunPod, Together)
- `model_hosting_inference` (Together AI, Fireworks, Anyscale, Groq)
- `agentic_runtimes` (LangGraph Cloud, Temporal Cloud, OpenAI Threads)
- `embedded_db_local` (LMDB, DuckDB, SQLite con vss)

#### Sprint 92 — Macroárea `apis_publicas_y_skills`

Catálogo de APIs externas (no-AI) y skills agénticas. ~50 productos seed.

**Subdominios canónicos propuestos:**
- `comunicacion` (Twilio, Sendgrid, Resend, Stripe Voice)
- `pagos` (Stripe, MercadoPago, PayPal, Conekta)
- `geolocalizacion` (Mapbox, Google Maps API, OpenStreetMap)
- `email_calendar` (Gmail API, Outlook API, Cal.com)
- `crm_marketing` (HubSpot API, Mailchimp, Brevo)
- `tools_devops` (GitHub API, Vercel API, Railway API, Supabase API)

#### Sprint 93 — Macroárea `automation_no_ai`

Herramientas de automatización clásicas usadas en el stack del Monstruo. ~20 productos seed.

**Subdominios canónicos propuestos:**
- `workflow_engines_visuales` (Zapier, Make, n8n no-AI)
- `etl_pipelines` (Airbyte, Fivetran, dbt)
- `cron_orchestration` (Temporal, Apache Airflow, GitHub Actions)
- `monitoring_observability` (Datadog, Grafana, Sentry)

### Bloque B — Capa de búsqueda semántica (2 sprints)

#### Sprint 94 — Embeddings + búsqueda híbrida

Generar embeddings semánticos para los 173+ productos catalogados (texto: nombre + descripción + casos_uso) usando `text-embedding-3-large` o `voyage-3`. Crear índice vectorial en Supabase pgvector.

**Capacidad clave:** SQL híbrido `WHERE macroarea=X AND embedding <-> $query_emb < threshold ORDER BY trono_score DESC`.

**Endpoints nuevos:**
- `/catastro/buscar` con query semántica + filtros de capacidades
- `/catastro/recomendar` que recibe descripción de tarea → devuelve top-3 productos con razón documentada

#### Sprint 95 — Catastro Recomendador 2.0

Reescribir `kernel/catastro/recommendation.py` para usar:
1. Búsqueda híbrida (Sprint 94)
2. Multi-criteria scoring (capacidades técnicas requeridas + costo + licensing_risk + soberanía)
3. Justificación legible para humano y para Monstruo

### Bloque C — Auto-recalibración y vida (2 sprints)

#### Sprint 96 — Auto-recalibración mensual

Job programado mensual que:
1. Re-ejecuta validación adversarial Perplexity + 4 sabios sobre tronos críticos (24 actuales)
2. Detecta drift en tronos (producto que ya no es trono → genera evento `top3_change`)
3. Actualiza scores y bonus_curador con razón nueva
4. Notifica al bridge si trono cambia (decisión humana antes de aplicar)

#### Sprint 97 — Catastro Eventos cross-macroárea

Extender `catastro_eventos` para emitir eventos cuando:
- Un trono cambia (cualquier macroárea)
- Un producto pasa de production → deprecated
- Aparece un nuevo producto con score > trono actual
- Cambia el licensing_risk de un producto en uso

### Bloque D — Integración con kernel del Monstruo (2 sprints)

#### Sprint 98 — Catastro como Tool MCP

Exponer Catastro como tool MCP nativo del kernel:
- `catastro.buscar(macroarea, capacidades, top_k)` → JSON con productos
- `catastro.trono(dominio_o_subdominio)` → metadata del trono actual
- `catastro.justificar(producto_id, dominio)` → razón canónica del bonus_curador

Esto permite que cualquier sub-agente del Monstruo (Cowork, Devin, Manus) consulte el Catastro vía MCP en lugar de hardcodear preferencias.

#### Sprint 99 — Telemetría de uso

Cada vez que el Monstruo selecciona un producto del Catastro, emitir evento de uso con:
- Producto seleccionado
- Tarea original
- Resultado (éxito/fracaso/parcial)
- Costo real vs costo estimado

Después de N usos, recalibrar trono empíricamente.

---

## Priorización recomendada

**Sprint 90** (voz_inteligencia) → primero, porque desbloquea voicebots y traducción real-time.

**Sprint 94** (embeddings) → segundo, porque mejora 10x la utilidad de los 173 productos ya catalogados.

**Sprint 98** (MCP tool) → tercero, porque cierra el bucle: el Monstruo consulta el Catastro de forma dinámica.

Sprints 91, 92, 93 (otras macroáreas) en paralelo si hay capacidad. Sprints 95, 96, 97, 99 dependen de los tres anteriores.

---

## Métricas de éxito (fin del Sprint 99)

- ≥ **300 entidades catalogadas** (vs 173 actuales)
- ≥ **50 tronos firmes** (vs 24 actuales)
- Catastro disponible como **tool MCP nativo** del kernel
- Auto-recalibración mensual operando sin intervención humana
- ≥ **100 eventos de telemetría** registrados con tasa de éxito > 80%

---

## Pre-requisitos antes de iniciar Sprint 90

1. ✅ DSC-G-007.5 firmado (este sprint)
2. ⏳ Cowork audit content de los archivos del Sprint 88.3
3. ⏳ Aprobación Alfredo del orden de prioridad (90 → 94 → 98)
4. ⏳ Validación de capacidad: budget Perplexity + 4 sabios sobre voz_inteligencia (~$15-25)

---

**FIN ROADMAP META-CATASTRO**
