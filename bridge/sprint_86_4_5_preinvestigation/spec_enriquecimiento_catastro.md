# Sprint 86.4.5 — Enriquecimiento Catastro v1.1 · Pre-investigación

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-04 ~23:55 CST
> **Estado:** Spec firmado, listo para arranque
> **Sprint asignado:** Hilo Manus Ejecutor
> **Dependencia:** Ninguna (Catastro v1.0 production-ready)
> **Bloquea:** Sprint 87 NUEVO E2E NO depende de este sprint, pero se beneficia cuando cierre

---

## Contexto

Sprint 86 cerró Catastro v1.0 production-ready: 37 modelos persistidos, 3/3 fuentes, Quorum 2-de-3 operando. Pero la Fase 2 del Audit del Roadmap reveló que la **estructura está completa pero la data semánticamente subdesarrollada**:

- Campos métricos (`quality_score`, `reliability_score`, `cost_efficiency`, `speed_score`, `precio_input/output`) mayormente NULL
- `casos_uso_recomendados_monstruo` vacío en 37/37 modelos
- `recommend` endpoint con bug bootstrap que impide consultas
- Slugs lmarena no normalizados → fragmentación de Quorum

**Consecuencia:** Cowork no puede consultar Catastro para decisiones tecnológicas finas (Trono Score plano = 50 para todos). Knowledge cutoff de Cowork sigue parcialmente sin cubrir.

Sprint 86.4.5 cierra esta deuda con 4 sub-bloques.

## Objetivo del Sprint

Catastro v1.1 con campos métricos poblados desde fuentes ya disponibles + recommend endpoint funcional + casos de uso clasificados por LLM. ETA total: 2-3 días.

## Bloques

### Bloque 1 — Bug fix bootstrap recommend endpoint (~2h, prerequisito)

**Síntoma:** `POST /v1/catastro/recommend` retorna error o lista vacía aún con modelos persistidos.

**Diagnóstico esperado:**
- Singleton `RecommendationEngine` no se inicializa correctamente al startup
- O cache LRU no carga datos desde Supabase al primer request
- O filtros `quorum_alcanzado=true` y otros excluyen accidentalmente todos

**Tarea:**
1. Reproducir bug con curl directo a producción
2. Trazar con logs el flujo recommend
3. Fix quirúrgico
4. Smoke test: `recommend` retorna ≥ 5 modelos para use_case genérico
5. Test E2E con TestClient FastAPI

**Zona primaria:** `kernel/catastro/recommendation.py`, `kernel/catastro/catastro_routes.py`, `tests/test_sprint86_bloque5.py`

### Bloque 2 — Enriquecimiento de campos métricos (~1-2 días)

**Objetivo:** poblar `quality_score`, `reliability_score`, `cost_efficiency`, `speed_score`, `precio_input_per_million`, `precio_output_per_million` desde data ya disponible en las 3 fuentes.

**Sub-tareas:**
1. **Auditar shape de cada fuente** — qué campos exponen Artificial Analysis API, OpenRouter `/api/v1/models`, LMArena dataset HF
2. **Mapping declarativo** — crear `kernel/catastro/sources/field_mapping.yaml` con reglas de extracción y normalización (ej. AA `intelligence_score` → `quality_score` con scaling 0-100)
3. **Modificar pipeline** — el paso `normalize` ahora pobla campos métricos directamente
4. **Re-run del pipeline** — primer run productivo enriquecido, esperado >5 modelos con campos completos
5. **Tests** — verificar shape esperado en producción

**Zona primaria:** `kernel/catastro/sources/*.py`, `kernel/catastro/pipeline.py`, `kernel/catastro/sources/field_mapping.yaml` (nuevo), tests.

**Criterio de éxito:** después del run, ≥ 80% de los modelos persistidos tienen al menos 4 de 6 campos métricos poblados.

### Bloque 3 — Normalización de slugs lmarena (~1 día)

**Síntoma:** lmarena reporta modelos como `claude-opus-4-7` mientras Artificial Analysis usa `claude-opus-4.7`. Quorum NO matchea → fragmentación.

**Tarea:**
1. Crear función `normalize_slug(raw_slug: str, source: str) -> str` en `kernel/catastro/sources/base.py`
2. Reglas: lowercase + reemplazar `_` y `.` por `-` + remover sufijos comunes (`-instruct`, `-chat`, `-base`)
3. Aplicar normalización en cada fuente al momento de fetch
4. Re-run pipeline y validar que modelos antes fragmentados ahora coinciden
5. Tests con casos sintéticos (50+ pares de slugs)

**Criterio de éxito:** modelos top de cada fuente coinciden en ≥ 70% (vs ≤ 30% antes).

### Bloque 4 — LLM-as-classifier para `casos_uso_recomendados_monstruo` (~1 día)

**Síntoma:** campo vacío en 37/37 modelos. Sin esto, no puedo hacer queries semánticas tipo "¿qué modelo es bueno para X?".

**Diseño:**
1. Catálogo cerrado de **20-30 casos de uso canónicos** definidos en `kernel/catastro/casos_uso_canonicos.yaml`:
   - `chat_general`, `coding_typescript`, `coding_python`, `agentic_long_horizon`, `vision_image_understanding`, `vision_video`, `embeddings_semantic_search`, `summarization_long_doc`, `function_calling`, `multi_step_reasoning`, etc.
2. **Classifier component** `kernel/catastro/casos_uso_classifier.py`:
   - Input: `ModeloIA` con todos sus campos enriquecidos
   - Output: `list[str]` con casos de uso del catálogo cerrado
   - Implementación: prompt a Gemini 3.1 Pro o GPT-5.5 con prompt estructurado + JSON response strict
3. **Disciplina anti-hallucination:** modelo solo puede retornar casos de uso del catálogo cerrado. Validación con Pydantic post-LLM.
4. **Cache:** evitar re-clasificar modelos sin cambios. Hash de campos relevantes → skip si igual.
5. **Pipeline integration:** correr classifier post-quorum, antes de persistencia, en paralelo (asyncio.gather).

**Criterio de éxito:** ≥ 90% de modelos persistidos tienen ≥ 1 caso de uso clasificado.

**Costo estimado:** 37 modelos × ~500 tokens × 30 USD/M tokens ≈ $0.55 USD por run. Trivial.

### Bloque 5 — Smoke E2E + reporte (~1h)

Validación final post-enriquecimiento:
- `recommend` con use_case=`coding_typescript` retorna Top 5 con Trono Score diferenciado (NO 50 plano)
- `get_modelo` con id de top retorna ficha completa con campos métricos poblados
- Dashboard `/dashboard/summary` muestra métricas saludables
- Trono Scores ahora son distintos entre sí (no plano)

## Tests acumulados esperados al cierre

Sprint 86 v1.0: 230 PASS + 4 opt-in
Sprint 86.4.5 nuevos: ~25-35 tests adicionales
**Total esperado:** 255+ PASS

## Capa Memento aplicada

- Pre-flight obligatorio en `field_mapping.yaml` antes de modificar pipeline
- Disciplina anti-Dory en classifier (lectura fresh de catálogo, no caching boot)
- Tests con casos sintéticos del incidente Falso Positivo TiDB para regression

## Caveat operativo

Este sprint es **independiente del Sprint 87 NUEVO** (E2E). Pueden ejecutarse en paralelo. Sprint 87 NO depende de campos métricos enriquecidos porque usa el patrón "consultar Catastro en runtime para elegir modelo" — funciona con Catastro v1.0 (Trono plano = elige primer match) y mejora cuando 86.4.5 cierre (Trono diferenciado = elige óptimo).

— Cowork (Hilo B)
