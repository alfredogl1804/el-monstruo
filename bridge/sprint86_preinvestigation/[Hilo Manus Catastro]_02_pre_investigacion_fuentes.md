# [Hilo Manus Catastro] · Tarea 2 — Pre-investigación de fuentes de scraping

**Hilo:** `[Hilo Manus Catastro]`
**Fecha:** 2026-05-04
**Estado:** COMPLETADA
**Método:** Validación en tiempo real vía búsqueda web + lectura directa de docs oficiales (no entrenamiento)

---

## Hallazgo crítico (cambia la arquitectura del Sprint 86)

**El Diseño Maestro v1.0 asume que la mayoría de fuentes primarias requieren scraping HTML. La validación en tiempo real demuestra que NO: 6 de 8 fuentes primarias tienen API REST oficial pública o dataset oficial accesible programáticamente.**

Esto reduce drásticamente la complejidad del Sprint 86: pasamos de "construir scrapers HTML que se rompen cada vez que cambia el site" a "consumir APIs estables con SDKs maduros". Reducción estimada: **~70% de la deuda de mantenimiento del pipeline diario** y eliminación de la categoría "scrapers que se rompen" como fuente recurrente de errores.

---

## Inventario validado de fuentes primarias

### 1. Artificial Analysis — API REST OFICIAL GRATUITA (no scraping)

| Atributo | Valor |
|---|---|
| URL | https://artificialanalysis.ai/api-reference |
| Auth | Header `x-api-key` |
| Cómo obtener key | Crear cuenta gratis en Insights Platform |
| Rate limit | 1,000 requests/día (más que suficiente: necesitamos ~10) |
| Atribución | Obligatoria (link a artificialanalysis.ai) |
| Cobertura | LLMs, T2I, image editing, TTS, T2V, I2V — **6 dominios** |

**Endpoints validados:**

```
GET /data/llms/models               # LLMs con pricing, speed, evaluations
GET /data/media/text-to-image       # Elo + categorías
GET /data/media/image-editing       # Elo
GET /data/media/text-to-speech      # Elo
GET /data/media/text-to-video       # Elo + categorías
GET /data/media/image-to-video      # Elo + categorías
```

**Response shape (LLMs):** `id`, `name`, `slug`, `model_creator`, `evaluations`, `pricing`, `median_output_tokens_per_second`, `median_time_to_first_token_seconds`.

**Implicación:** la fuente más rica del catálogo (cubre 4 de las 10 macroáreas) es API REST plana. Cliente Python ~50 LOC.

### 2. LMArena (Chatbot Arena) — Dataset oficial en Hugging Face

| Atributo | Valor |
|---|---|
| URL principal | https://lmarena.ai (UI) |
| Acceso programático | https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset |
| ToS | **Prohíbe scraping del site web**. Pero el dataset oficial es la vía aprobada. |
| Acceso | `from datasets import load_dataset; load_dataset("lmarena-ai/leaderboard-dataset")` |
| Rate limit | Ilimitado (descarga directa de Parquet) |
| Cobertura | LLMs (text), Vision arena, Image arena, Video arena, Search arena |

**Backups validados:**
- `https://github.com/fboulnois/llm-leaderboard-csv` (auto-genera CSVs)
- `https://oolong-tea-2026.github.io/...` (auto-fetcha 10 leaderboards diarios)
- HF Space `lmarena-ai/arena-leaderboard` (UI iframe)

**Decisión:** Usar el HuggingFace dataset oficial. Legal, oficial, snapshots históricos incluidos.

### 3. Hugging Face Open LLM Leaderboard — API REST oficial

| Atributo | Valor |
|---|---|
| Hub org | https://huggingface.co/open-llm-leaderboard |
| Dataset server REST | `/parquet`, `/rows`, `/search` (sin auth para datasets públicos) |
| SDK Python | `huggingface_hub` + `datasets` (ya en requirements del kernel) |
| Documentación | https://huggingface.co/docs/hub/leaderboard-data-guide |
| Cobertura | Open-weights LLMs (296+ modelos canónicos según `llm-stats.com`) |

**Decisión:** Mismo patrón que LMArena: `load_dataset()` + REST API si necesitamos slicing.

### 4. Replicate — API REST oficial

| Atributo | Valor |
|---|---|
| URL | https://replicate.com/docs/reference/http |
| Auth | API token Bearer |
| Endpoints relevantes | `GET /v1/models`, `GET /v1/models/{owner}/{name}` |
| Rate limit | Documentado (varía por plan) |
| Cobertura | Catálogo masivo (visión, video, audio, LLMs), pricing por segundo de GPU |

### 5. FAL.ai — API REST oficial

| Atributo | Valor |
|---|---|
| URL | https://fal.ai/docs/platform-apis/v1/models |
| Auth | API key |
| Endpoints relevantes | List Mode (paginado, todos los modelos), Find Mode (por endpoint_id) |
| Cobertura | 1,000+ modelos de imagen/video/audio/música/speech/3D/realtime |

### 6. Together.ai — API REST oficial

| Atributo | Valor |
|---|---|
| URL | https://docs.together.ai/docs/serverless-models + https://api.together.ai |
| Auth | API key |
| Endpoints relevantes | `GET /models` |
| Cobertura | 200+ modelos open-source serverless con pricing por 1M tokens |

### 7. Anuncios de proveedores — RSS + scraping selectivo (sigue siendo necesario)

OpenAI/Anthropic/Google/xAI/Meta no exponen API de "what changed today". Se mantiene como fuente que requiere scraping ligero de blog posts + RSS feeds. Estimado: ~10% del esfuerzo total. Mitigación: usar Curador-LLM que lee los anuncios en lenguaje natural y emite diff estructurado (paso 1 del pipeline diario del Diseño Maestro).

### 8. Vendor pricing pages — scraping selectivo (semanal, no diario)

Fallback cuando los catálogos de los hosts (Replicate/FAL/Together) no exponen el precio actualizado. Usar Playwright o Browser-use con heurística de extracción.

---

## Reformulación del Pipeline diario (paso a paso)

```
07:00 CST — launchd dispara forja_catastro_daily_job
  │
  ├─ 1. Curador-LLM (gpt-5.5-mini) → lee anuncios últimas 24h via RSS
  │     OUTPUT: diff de releases/deprecations
  │
  ├─ 2. Clientes API en paralelo (NO scrapers):
  │     ├─ artificial_analysis.client → 6 endpoints
  │     ├─ huggingface.datasets → load_dataset(lmarena-ai/leaderboard-dataset)
  │     ├─ huggingface.datasets → load_dataset(open-llm-leaderboard/...)
  │     ├─ replicate.client.models.list()
  │     ├─ fal.client.models.list()
  │     └─ together.client.models.list()
  │
  ├─ 3. QUORUM VALIDATOR (kernel/catastro/quorum_validator.py)
  │     Para cada métrica crítica (precio, Elo, latencia):
  │       Requerir cuórum 2-de-3 entre fuentes independientes
  │       Si quórum falla → marcar para HITL, NO actualizar
  │
  ├─ 4. Validador (Claude Opus 4.7) revisa diffs estructurados
  │     Decisión: confirmar / descartar / HITL
  │
  ├─ 5. Trust Score recalculado por curador-LLM
  │     Si Trust Score < 0.7 → todos sus updates van a HITL automático
  │
  ├─ 6. Re-cálculo Trono Score
  │     Trono = 0.40*Q + 0.25*CE + 0.15*S + 0.10*R + 0.10*BF
  │
  ├─ 7. Persistencia (Supabase)
  │     catastro_modelos / catastro_historial / catastro_eventos
  │
  ├─ 8. Detección de eventos importantes
  │     Top 3 cambia / deprecation / nuevo modelo en Top 5
  │
  └─ 9. Notificación
        Telegram al bot del Monstruo (resumen 3 viñetas)
        + Drive snapshot YYYY-MM-DD.json
```

**Costo recalculado del pipeline diario:**
- API calls: 0 (todas las APIs son free tier suficiente)
- LLM tokens: Curador-LLM (1 paso) + Validador (1 paso) ≈ 50K tokens/día
- Cost/día: ~$0.30 USD (50% menos que estimación original del Diseño Maestro de $0.70)
- Cost/mes: ~$10 USD APIs externas + ~3K créditos Manus

---

## Nuevas credenciales requeridas (input para [Hilo Manus Credenciales])

| Servicio | Variable env | Categoría | Justificación |
|---|---|---|---|
| Artificial Analysis | `ARTIFICIAL_ANALYSIS_API_KEY` | C (infra crítica) | Fuente principal del Catastro (6 dominios) |
| Replicate | `REPLICATE_API_TOKEN` | C (infra crítica) | Catálogo de modelos y precios reales |
| FAL.ai | `FAL_API_KEY` | C (infra crítica) | 1,000+ modelos de visión/video/audio |
| Together.ai | `TOGETHER_API_KEY` | C (infra crítica) | 200+ modelos open-source serverless |
| Hugging Face | `HF_TOKEN` (read scope) | C (infra crítica) | Dataset server, leaderboards. Probablemente ya existe en Bitwarden |

**Nota para [Hilo Manus Credenciales]:** las 4 primeras NO existen aún en el ecosistema. La 5ta (HF) verificar si ya existe — si sí, basta con propagar al kernel service en Railway. Si no, crear cuenta y agregar.

**No bloqueante para arrancar Sprint 86 si:** se agrega como Ola 6 después de Ola 5 (LLM providers). Es decir, antes de codear scrapers/clientes en Sprint 86 deben estar las 5 credenciales.

---

## Conclusión Tarea 2

**El Sprint 86 cambia de "Sprint de Scrapers" a "Sprint de Clientes API + Quorum Validator + Trust Score":**

1. ~70% del catálogo se obtiene vía APIs REST oficiales o datasets HF oficiales.
2. ~10% requiere scraping ligero de blogs/RSS (anuncios de proveedores).
3. ~20% requiere validación cruzada vía Curador-LLM (BrandFit, Sovereignty, casos de uso del Monstruo — datos derivados que no publican los benchmarks).

**Beneficios de este descubrimiento:**

- Reducción de 70% en código de scraping (mantenimiento)
- Eliminación de la dependencia frágil de "estructura HTML estable"
- Refactor de la macroárea "Visión generativa" del Catastro: rastreará Elo de Artificial Analysis Image Arena como fuente única autoritativa (no inventar)
- Refactor del Sprint 1-2 internos del Diseño Maestro: ya no hay "implementar scraper de Artificial Analysis" — es "implementar cliente API de Artificial Analysis" (10x más simple)

**Recomendación a Cowork:** actualizar el SPEC SPRINT 86 reemplazando todas las menciones de "scraper" por "cliente API" cuando aplique, agregar la sección "Credenciales requeridas" como pre-requisito antes del kickoff, y considerar mover la fuente "anuncios de proveedores" a Sprint 87 (no es bloqueante para MVP).

— [Hilo Manus Catastro]
