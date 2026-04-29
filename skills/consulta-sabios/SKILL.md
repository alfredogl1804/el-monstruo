---
name: consulta-sabios
description: Infraestructura permanente para consultar al Consejo de 6 Sabios (GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, DeepSeek R1, Perplexity Sonar Reasoning Pro) con capa de investigación en tiempo real y validación post-síntesis. Use when consulting the 6 sabios, querying AI models from semilla v7.3, running enjambre/swarm consultations, or when any task requires multi-model AI consensus with real-time data validation.
---

# consulta-sabios v3.0

Infraestructura permanente para consultar al Consejo de 6 Sabios con investigación en tiempo real, validación post-síntesis, routing adaptativo, mejora perpetua y telemetría completa. 26 scripts, ~7,600 líneas de código.

**Última validación en producción:** 24 abril 2026 — **6/6 sabios OK** (verificado via `conector_sabios.py ping`).

## Reglas Inquebrantables

1. **PROHIBIDO** escribir código de conexión a APIs. Todo está en `conector_sabios.py`.
2. **OBLIGATORIO** usar `run_consulta_sabios.py` como entrypoint (orquesta los 7 pasos automáticamente).
3. Verificar modelos contra esta tabla (verificada por código) antes de cada consulta.
4. Cada run genera telemetría automática en `data/`.
5. **NUNCA** omitir Paso 7 en consultas de producción (solo `--skip-paso7` para debug).
6. **NUNCA** usar `temperature` con GPT-5.5 Pro ni Claude Opus 4.7 (deprecated/unsupported, verificado 24 abril 2026).
7. **NUNCA** usar `/v1/chat/completions` con modelos `gpt-5.x-pro` — requieren `/v1/responses`.

## Los 6 Sabios — Verificados por Código contra APIs Reales

> Cada modelo fue validado ejecutando `conector_sabios.py ping` el 24 abril 2026.
> Los modelos, endpoints y restricciones fueron descubiertos por código, no por entrenamiento.

| ID | Sabio | Modelo Exacto | Proveedor | API Endpoint | Contexto | Grupo |
|----|-------|---------------|-----------|-------------|----------|-------|
| gpt55 | GPT-5.5 Pro | `gpt-5.5-pro` | OpenAI | `/v1/responses` (Responses API) | 1.05M | completo |
| claude | Claude Opus 4.7 | `claude-opus-4-7` | Anthropic directo | `/v1/messages` | 1M | completo |
| gemini | Gemini 3.1 Pro | `gemini-3.1-pro-preview` | Google GenAI SDK | `generate_content()` | 1M | completo |
| grok | Grok 4 | `grok-4-0709` | xAI | `/v1/chat/completions` | 2M | completo |
| deepseek | DeepSeek R1 | `deepseek/deepseek-r1` | OpenRouter | `/v1/chat/completions` | 128K | condensado |
| perplexity | Sonar Reasoning Pro | `sonar-reasoning-pro` | Perplexity | `/v1/chat/completions` | 128K | condensado |

**Alias de compatibilidad:** `gpt54` → `gpt55` (el sabio OpenAI se actualizó de GPT-5.4 a GPT-5.5 Pro).

GPT-5.5 Pro tiene doble rol: sabio individual Y orquestador/sintetizador final (con fallback a Claude y Grok).

## Restricciones Críticas Descubiertas por Validación en Tiempo Real

> Estos errores se descubrieron ejecutando código contra las APIs reales.
> Cada uno causaba fallos silenciosos en versiones anteriores del skill.

| Restricción | Descubierta | Impacto |
|-------------|-------------|---------|
| `gpt-5.5-pro` NO soporta `temperature` | 24 abril 2026 | HTTP 400 si se envía |
| `claude-opus-4-7` NO soporta `temperature` | 24 abril 2026 | HTTP 400 "deprecated" |
| `gpt-5.x-pro` NO funciona con `/v1/chat/completions` | 24 abril 2026 | HTTP 404 |
| `gpt-5.x-pro` REQUIERE `/v1/responses` con `output_text` | 24 abril 2026 | Respuesta en `output_text`, no `choices[0]` |
| `sonar-reasoning` está DEPRECATED | 24 abril 2026 | HTTP 400, usar `sonar-reasoning-pro` |
| Claude 3.x modelos ya NO existen | 24 abril 2026 | HTTP 404, solo Claude 4.x+ |
| Anthropic SDK directo es más confiable que OpenRouter para Claude | 24 abril 2026 | Menos latencia, menos errores |

## Credenciales Requeridas

| Variable | Servicio | Sabio | Usado en Paso 7 |
|----------|----------|-------|-----------------|
| `OPENAI_API_KEY` | OpenAI Responses API | GPT-5.5 Pro | Corrector |
| `ANTHROPIC_API_KEY` | Anthropic Messages API | Claude Opus 4.7 | Cross-validator |
| `GEMINI_API_KEY` | Google GenAI SDK | Gemini 3.1 Pro | Verificador primario |
| `XAI_API_KEY` | xAI Chat API | Grok 4 | Extractor, Segunda opinión |
| `OPENROUTER_API_KEY` | OpenRouter | DeepSeek R1 | Extractor fallback |
| `SONAR_API_KEY` | Perplexity API | Sonar Reasoning Pro | NO usado en Paso 7 (anti-circular) |

## Ejecución Estándar (Entrypoint Oficial)

All commands run from `/home/ubuntu/skills/consulta-sabios/scripts/`.

```bash
python3.11 run_consulta_sabios.py \
    --prompt /ruta/prompt.md \
    --output-dir /ruta/salida/ \
    --modo enjambre \
    --profundidad-pre normal \
    --profundidad-post normal \
    --profundidad-paso7 normal
```

Esto ejecuta automáticamente los 7 pasos: pre-vuelo, investigación, preparar contexto, consultar sabios, quality gate + validación, síntesis final, **validación post-síntesis**.

Opciones adicionales: `--skip-investigacion`, `--skip-validacion`, `--skip-paso7`, `--no-corregir`, `--sabios gpt55,claude,gemini`.

## Los 7 Pasos (ejecutados por run_consulta_sabios.py)

**Paso 1 — Pre-vuelo.** Valida 6 APIs con ping. Si <3 responden, aborta.

**Paso 2 — Investigar (PRE-CONSULTA).** GPT-5.5 Pro identifica temas sensibles al tiempo, Perplexity investiga en tiempo real. Genera "Dossier de Realidad".

**Paso 3 — Preparar contexto.** Combina prompt + dossier. Condensa automáticamente para sabios de 128K si excede umbral.

**Paso 4 — Consultar sabios.** Envía a los 6 en paralelo con prompt completo/condensado según grupo. Smart Router asigna roles por tipo de consulta.

**Paso 5 — Quality Gate + Validación.** Evalúa calidad de cada respuesta (6 dimensiones). Luego verifica afirmaciones contra realidad actual con Perplexity. Fallback Manager reintenta con reemplazos si un sabio primario falla.

**Paso 6 — Síntesis final.** GPT-5.5 Pro sintetiza con informe de validación inyectado. Judge evalúa calidad de la síntesis. Fallback a Claude y Grok si GPT-5.5 Pro falla.

**Paso 7 — Validación POST-SÍNTESIS.** Cierra el ciclo de verificación. Tres capas:

> **Capa 1 — Extracción:** Grok (no GPT-5.5, para evitar auto-evaluación) extrae afirmaciones verificables de la síntesis final.
>
> **Capa 2 — Verificación independiente:** Gemini (con Google Search grounding) verifica cada afirmación. Para riesgo alto con problemas, Grok da segunda opinión. NO usa Perplexity (evita dependencia circular con Paso 5).
>
> **Capa 3 — Cross-validation:** Claude compara la síntesis contra el informe de validación del Paso 5. Detecta correcciones que GPT-5.5 Pro ignoró al sintetizar.
>
> **Corrección automática:** Si hay 3+ problemas factuales, 1+ corrección grave ignorada, o score de incorporación <0.6, GPT-5.5 Pro corrige la síntesis (con fallback a Claude). Genera `sintesis_corregida.md`.

**Diseño anti-dependencia circular del Paso 7:**

| Rol | Modelo | Razón |
|-----|--------|-------|
| Extractor | Grok 4 (`grok-4-0709`) | Evita que GPT-5.5 evalúe su propia síntesis |
| Verificador primario | Gemini 3.1 Pro (`gemini-3.1-pro-preview`) | Google Search grounding (independiente de Perplexity) |
| Segunda opinión | Grok 4 (`grok-4-0709`) | Solo para riesgo alto con problemas detectados |
| Cross-validator | Claude Opus 4.7 (`claude-opus-4-7`) | Neutral — no participó en síntesis ni verificación |
| Corrector | GPT-5.5 Pro (`gpt-5.5-pro`) | Mejor editor de precisión (con fallback a Claude) |

## Routing Adaptativo (smart_router.py)

Clasifica automáticamente cada consulta y optimiza la configuración:

| Tipo | Sabios Primarios | Investigación | Timeout |
|------|------------------|---------------|---------|
| tecnica | gpt55, gemini, deepseek | media | 1.0x |
| estrategica | gpt55, claude, grok | profunda | 1.2x |
| legal | claude, gpt55 | profunda | 1.5x |
| creativa | grok, gpt55, gemini | basica | 0.8x |
| investigacion | todos (6) | profunda | 1.5x |
| operativa | gpt55, claude, deepseek | basica | 1.0x |

Uso: `from smart_router import route, describe_route`

## Fallbacks Automáticos (fallback_manager.py)

Si un sabio primario falla, el sistema selecciona automáticamente un reemplazo basado en capacidades por rol (8 dimensiones: orquestación, estrategia, código, legal, creatividad, investigación, documentación, análisis de riesgo).

Uso: `from fallback_manager import get_fallback, evaluate_coverage`

## Juez de Síntesis (judge_synthesis.py)

Evalúa la síntesis final en 6 dimensiones: fidelidad, cobertura, coherencia, accionabilidad, equilibrio, valor agregado. Usa un modelo diferente al orquestador (Gemini por defecto) para evitar auto-evaluación.

```bash
python3.11 judge_synthesis.py --sintesis sintesis.md --respuestas SALIDA/ --output evaluacion.json
```

## Ejecución Manual (scripts individuales)

Solo usar si se necesita control granular:

```bash
python3.11 ping_sabios.py
python3.11 investigar_contexto.py --prompt P.md --output dossier.md
python3.11 condensar_contexto.py --input contexto.md --output resumen.md
python3.11 consultar_paralelo.py --prompt P.md --output SALIDA/ --modo enjambre
python3.11 validar_respuestas.py --respuestas SALIDA/resp_combinadas.md --output SALIDA/informe.md
python3.11 sintetizar_gpt54.py --input SALIDA/resp_combinadas.md --output SALIDA/sintesis.md --informe-validacion SALIDA/informe.md
python3.11 validar_sintesis.py --sintesis SALIDA/sintesis_final.md --informe-validacion SALIDA/informe_validacion.md --output SALIDA/validacion_sintesis.md --corregir
```

## Componentes (26 scripts)

### Core (7)
| Script | Función |
|--------|---------|
| conector_sabios.py | Conectores verificados por código, retry, errores normalizados |
| ping_sabios.py | Pre-vuelo: valida 6 APIs en <10s |
| consultar_paralelo.py | Motor: enjambre, consejo, iterativo |
| investigar_contexto.py | Investigación pre-consulta con Perplexity Sonar |
| validar_respuestas.py | Validación post-consulta contra realidad |
| sintetizar_gpt54.py | Síntesis final con fallback chain |
| validar_sintesis.py | **Paso 7: Validación post-síntesis (Gemini+Grok+Claude)** |

### Inteligencia (5)
| Script | Función |
|--------|---------|
| smart_router.py | Routing adaptativo (6 tipos de consulta) |
| fallback_manager.py | Fallbacks por rol y capacidad |
| judge_synthesis.py | Juez automático de síntesis (6 dimensiones) |
| quality_gate.py | Evaluación de respuestas individuales |
| score_consulta.py | Scoring: factualidad, cobertura, consenso |

### Infraestructura (6)
| Script | Función |
|--------|---------|
| context_budget.py | Estimación de tokens y presupuesto por sabio |
| condensar_contexto.py | Condensación para sabios de 128K |
| json_parser.py | Parser JSON robusto (4 estrategias) |
| config_loader.py | Carga centralizada de YAML |
| telemetry.py | Métricas por run: tokens, duración, JSONL |
| run_consulta_sabios.py | Entrypoint unificado end-to-end (7 pasos) |

### Mejora Perpetua (5)
| Script | Función |
|--------|---------|
| db_store.py | Persistencia SQLite + prep Supabase sync |
| analyze_history.py | Detección de degradaciones y tendencias |
| propose_improvements.py | Propone mejoras basadas en historial |
| run_experiments.py | Experimentos A/B controlados |
| apply_improvement.py | Aplica mejoras con backup y rollback |

### Operaciones (3)
| Script | Función |
|--------|---------|
| dashboard.py | Dashboard operativo con métricas |
| data_retention.py | Retención, anonimización, exclusión PII |
| dossier_cache.py | Caché de dossier con fingerprint y TTL |

## Ciclo de Verificación Completo

```
Investigación PRE (Perplexity)
    ↓
Consulta 6 Sabios
    ↓
Validación POST (Perplexity verifica afirmaciones)
    ↓
Síntesis (GPT-5.5 Pro con informe inyectado)
    ↓
Validación POST-SÍNTESIS (Gemini+Grok verifican, Claude cross-valida)
    ↓
Corrección automática si hay problemas graves
    ↓
Documento final verificado en 3 capas
```

## Ciclo de Mejora Perpetua

```
Medir (telemetry) → Evaluar (analyze_history) → Proponer (propose_improvements) → Experimentar (run_experiments) → Aplicar (apply_improvement) → Medir...
```

Dashboard: `python3.11 dashboard.py --output dashboard.md`

## Configuración

- `config/skill_config.yaml` — Configuración centralizada (incluye sección `paso7`)
- `config/model_registry.yaml` — Registro versionado de modelos
- `config/prompt_versions/` — Prompts versionados

## Quality Gate

Cada respuesta se evalúa en 6 dimensiones: length, structure, evasion, density, alignment, repetition. Score 0-1. Grados: excellent (>0.85), ok (>0.6), poor (>0.4), reject (<0.4). Respuestas "reject" se excluyen de la síntesis.

## Modos y Profundidad

| Modo | Sabios | Velocidad | Uso |
|------|--------|-----------|-----|
| enjambre | 6 en paralelo | Rápido | Default |
| consejo | 4 de 1M+ | Medio | Contexto masivo |
| iterativo | 6 secuenciales | Lento | Decisiones críticas |

| Profundidad | Temas pre | Afirmaciones post | Afirmaciones Paso 7 | Uso |
|-------------|-----------|-------------------|---------------------|-----|
| rapida | 8 | 10 | 8 | Temas conocidos |
| normal | 15 | 20 | 15 | Estándar |
| profunda | 25 | 35 | 25 | Regulatorio, crítico |

## Archivos de Salida

| Archivo | Contenido |
|---------|-----------|
| dossier_realidad.md | Datos frescos pre-consulta |
| resp_{id}.md / .json | Respuesta individual + metadata |
| respuestas_combinadas.md | Todas las respuestas |
| quality_gate.md | Evaluación de calidad por sabio |
| informe_validacion.md | Verificación post-consulta |
| sintesis_final.md | Documento sintetizado por GPT-5.5 Pro |
| evaluacion_juez.json | Evaluación del juez de síntesis |
| validacion_sintesis.md | Informe post-síntesis (Paso 7) |
| sintesis_corregida.md | Síntesis corregida (si aplica) |
| paso7_metadata.json | Scores y metadata del Paso 7 |

## Uso Programático

```python
import sys
sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio, consultar_todos, ping_todos
from smart_router import route, describe_route
from fallback_manager import get_fallback, evaluate_coverage
from validar_sintesis import ejecutar_paso_7
import asyncio

# Ping rápido — verifica 6 APIs en <30s
resultados = asyncio.run(ping_todos())

# Consultar un sabio específico
resultado = asyncio.run(consultar_sabio("gpt55", "Pregunta"))
# NOTA: "gpt54" es alias de "gpt55" (backward compatible)

# Consultar todos en paralelo
resultados = asyncio.run(consultar_todos(
    prompt_completo="Contexto largo...",
    prompt_condensado="Resumen para DeepSeek/Perplexity...",
))

# Routing inteligente
config = route("Mi consulta sobre arquitectura")

# Paso 7 standalone
paso7 = asyncio.run(ejecutar_paso_7(
    sintesis_path="sintesis.md",
    informe_validacion_path="informe.md",
    output_path="validacion.md",
    corregir=True,
    profundidad="normal",
))
```

## Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| v3.0 | 24 abril 2026 | Modelos verificados por código contra APIs reales. GPT-5.4→GPT-5.5 Pro. Claude via Anthropic directo (no OpenRouter). Grok 4.20→Grok 4. Restricciones temperature descubiertas. Responses API obligatoria para GPT-5.x-pro. |
| v2.2 | 11 marzo 2026 | Paso 7 validación post-síntesis, routing adaptativo, fallbacks |
| v2.1 | Febrero 2026 | Quality gate, juez de síntesis |
| v2.0 | Enero 2026 | 26 scripts, telemetría, mejora perpetua |

## Referencias

Read `references/lecciones_aprendidas.md` for known errors and permanent fixes (Brotli, Unicode, Claude via OpenRouter). Read `references/modelos_capacidades.md` for model specs and limits.
