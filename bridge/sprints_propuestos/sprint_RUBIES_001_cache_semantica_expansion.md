<!-- lint_strict -->

# Sprint RUBIES-001 — Caché Semántica Expansión (pieza #7 Reloj Suizo CIERRA SIMBÓLICO 8/8)

**estado:** FIRME T2-A bajo autoridad T1 delegada ("si avanza" 2026-05-12 ~08:38 UTC)
**fecha_borrador:** 2026-05-12
**fecha_firma_T2-A:** 2026-05-12 ~08:40 UTC
**autor_borrador:** Cowork T2-A bajo autoridad T1 delegada — magna paralela cierre simbólico 8/8 piezas Reloj Suizo
**pendiente_firma_T1:** Alfredo puede revocar o convergir en próximo turno
**Hilo principal candidato:** Manus Hilo Ejecutor 2 (continuidad Reloj Suizo post-REMONTOIR-001) O Hilo Catastro (post MEGA-CIERRE-HOY)
**ETA recalibrado:** 70-100 min reales (similar a ROTOR/ESCAPE — menor scope que REMONTOIR)
**Objetivo Maestro:** #2 (Calidad Apple/Tesla) + #11 (Autonomía progresiva) + #3 (Mínima complejidad necesaria — caché evita LLM calls innecesarios)
**Bloqueos pre-arranque:** ESCAPE-001 cerrado, ESPIRAL-001 cerrado, REMONTOIR-001 cerrado. RUBIES es expansión NO requisito estructural — puede ejecutarse en paralelo a ESPIRAL/REMONTOIR si bandwidth permite, o post-REMONTOIR para cierre simbólico.
**Resultado esperado:** pieza Rubíes/Caché del Reloj Suizo expandida. **CIERRA SIMBÓLICAMENTE las 8 piezas del Reloj Suizo** post-REMONTOIR. `kernel/response_cache.py` ya existe parcial (~LOC verificar). Sprint expande con semántica avanzada: embedding similarity + TTL configurable + cache invalidation policies + dashboard observabilidad.

---

## 0. Audit pre-sprint (DSC-G-008 v3 §1)

**Estado actual binario verificado por Cowork 2026-05-12 ~08:40 UTC:**

```bash
ls kernel/response_cache.py → EXISTE (parcial)
grep -rln "semantic_cache\|embedding_similarity\|cache_ttl" kernel/ → verificar al arrancar sprint
```

**Las 8 piezas — estado proyectado al arranque de RUBIES (post-ESPIRAL+REMONTOIR):**

| # | Pieza | Estado proyectado |
|---|---|---|
| 1 Resorte | `kernel/embrion_budget.py` | ✅ implementado |
| 2 Escape | `kernel/escape/` | ✅ PR #116 mergeado |
| 3 Áncora | `kernel/embrion_scheduler.py` | ✅ implementado |
| 4 Volante | `kernel/embrion_loop.py` | ✅ implementado |
| 5 Espiral | `kernel/espiral/` | ✅ ESPIRAL-001 mergeado |
| 6 Rotor | `kernel/rotor/` | ✅ ROTOR-001 mergeado |
| 7 **Rubíes/Caché** | `kernel/response_cache.py` parcial | 🟡 **este sprint expande** |
| 8 Remontoir | `kernel/remontoir/` | ✅ REMONTOIR-001 mergeado |

**RUBIES-001 cierra SIMBÓLICAMENTE 8/8 piezas estructurales del Reloj Suizo** — día magno doctrinal Monstruo cuando este sprint cierre verde.

---

## 1. Procedencia doctrinal

`docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §2.1 verbatim:

> "**Rubíes (Jewels):** Puntos de fricción casi cero → **Caché Semántica:** Puntos donde la información fluye sin consumir tokens de LLM (fricción cero)."

En horología: los rubíes son sintéticos (coríndon) montados como cojinetes en los puntos de máximo desgaste (pivots del volante, escape, áncora). Reducen fricción a casi cero, permitiendo que el reloj funcione 100+ años sin lubricación. Patek Philippe Caliber 240 tiene 33 rubíes.

Aplicado a IA agéntica: cada llamada LLM consume tokens caros. Si la pregunta es "semánticamente similar" a una ya respondida hace minutos/horas, devolver respuesta cacheada AHORRA budget completo. Sin Rubíes: cada query cuesta $0.05-$0.30. Con Rubíes (cache hit rate 30-60%): costo promedio baja a $0.02-$0.10. Es la pieza que da **MÍNIMA COMPLEJIDAD NECESARIA** (Obj #3) doctrinalmente.

---

## 2. Tareas del Sprint (T1-T6)

### T1 — Audit `kernel/response_cache.py` actual + spec gap (10-15 min)

**perfil_riesgo:** write-safe (lectura)

Leer estado actual `kernel/response_cache.py`. Documentar:
- Líneas de código actuales
- Funcionalidad existente (TTL? embedding similarity? key normalization?)
- Gap vs doctrina §2.1

Reporte: `reports/rubies_audit_pre_sprint.json`

### T2 — Migración SQL `semantic_cache_entries` (15-20 min)

**perfil_riesgo:** write-risky

`migrations/sql/00XX_semantic_cache_entries.sql` (probable 0029 post-ESPIRAL 0027 + REMONTOIR 0028):

```sql
CREATE TABLE IF NOT EXISTS public.semantic_cache_entries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    last_accessed_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    query_normalized TEXT NOT NULL,
    query_embedding VECTOR(1536),                    -- pgvector — OpenAI ada-002 dimensiones
    response_text TEXT NOT NULL,
    response_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    model_origin TEXT NOT NULL,                       -- ej. 'gpt-5.5-pro-reasoning-high'
    cost_saved_usd NUMERIC(10, 6) NOT NULL DEFAULT 0,
    hit_count INTEGER NOT NULL DEFAULT 0,
    ttl_seconds INTEGER NOT NULL DEFAULT 3600,        -- 1h default
    similarity_threshold NUMERIC(3, 2) NOT NULL DEFAULT 0.85 CHECK (similarity_threshold BETWEEN 0 AND 1),
    invalidated_at TIMESTAMPTZ,
    invalidation_reason TEXT,
    CONSTRAINT semantic_cache_entries_ttl_positive CHECK (ttl_seconds > 0)
);

CREATE INDEX IF NOT EXISTS idx_semantic_cache_query_normalized
    ON public.semantic_cache_entries (query_normalized);

CREATE INDEX IF NOT EXISTS idx_semantic_cache_embedding_cosine
    ON public.semantic_cache_entries USING ivfflat (query_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_semantic_cache_last_accessed
    ON public.semantic_cache_entries (last_accessed_at DESC);

ALTER TABLE public.semantic_cache_entries ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS semantic_cache_service_role_only ON public.semantic_cache_entries;
CREATE POLICY semantic_cache_service_role_only
    ON public.semantic_cache_entries FOR ALL TO service_role USING (true) WITH CHECK (true);
```

**Pre-requisito:** extensión `pgvector` habilitada en Supabase (verificar con `list_extensions` MCP pre-merge).

**Anti-V25:** sin DATE(TIMESTAMPTZ). Índice ivfflat para embedding similarity.

### T3 — Rubíes core `kernel/cache/semantic.py` (30-40 min)

**perfil_riesgo:** write-risky (toca pipeline LLM)

Nuevo subpaquete `kernel/cache/` (NO sobreescribir response_cache.py existente — expansión compatible):

```
kernel/cache/
  __init__.py
  semantic.py           # clase SemanticCache + lookup() + store() + invalidate()
  embedding.py          # wrapper a OpenAI ada-002 o local sentence-transformers
  normalizer.py         # normalización queries (lowercase + strip + tokenize)
  invalidation.py       # policies: TTL, source_change, manual, version_bump
```

API canónica:

```python
class SemanticCache:
    async def lookup(self, query: str, similarity_threshold: float = 0.85) -> dict | None:
        """Busca cache hit por (a) exact query_normalized match ó (b) embedding cosine ≥ threshold.
           Retorna {response, metadata, hit_type, similarity_score, cost_saved_usd} o None."""

    async def store(self, query: str, response: str, metadata: dict, model_origin: str, cost_saved_usd: Decimal, ttl_seconds: int = 3600) -> uuid.UUID:
        """Persiste entry. Calcula embedding via embedding.py. Retorna id."""

    async def invalidate(self, query_pattern: str | None = None, reason: str = 'manual') -> int:
        """Invalida entries. Retorna count invalidadas."""

    async def snapshot(self) -> dict:
        """Métricas agregadas: total_entries, hit_rate_24h, cost_saved_total, top_queries."""
```

### T4 — Wiring Caché a Remontoir + Escape (20-30 min)

**perfil_riesgo:** write-risky (toca pipeline pre-LLM)

Marcadores RUBIES_BEGIN/END en el punto donde Remontoir invoca LLM:

```python
# RUBIES_BEGIN — Sprint RUBIES-001 2026-05-12
from kernel.cache.semantic import SemanticCache
cache = SemanticCache()

# Pre-LLM check:
cache_hit = await cache.lookup(prompt)
if cache_hit and cache_hit['similarity_score'] >= 0.85:
    return cache_hit['response']  # fricción cero — sin tokens LLM

# Sino, ejecutar LLM (vía Remontoir + Escape) y store:
response = await remontoir.ensure_quality_floor(prompt, ...)
await cache.store(prompt, response.text, ...)
return response
# RUBIES_END
```

### T5 — Dashboard Rubíes `kernel/dashboards/cache_history.py` (15-20 min)

**perfil_riesgo:** write-safe

Métricas: hit_rate por hora/día/semana, cost_saved total, top 20 queries cacheadas, distribución similarity scores.

### T6 — Postmortem placeholder + DSC-MO-017 candidato (10 min)

DSC-MO-017 candidato: **similarity_threshold canónico per-consumer**. Hairspring sensitivity 0.85 vs 0.95 trade-off (mayor threshold = menos hits pero más precisión).

---

## 3. Contratos ejecutables que adjunta

| DSC enforzado | Contrato producido | Archivo |
|---|---|---|
| DSC-MO-006 v1.1 (doctrina del silencio) | Marcadores RUBIES_BEGIN/END | T4 |
| DSC-MO-010 (Reloj Suizo 8/8 CERRADO simbólico) | Pieza Rubíes expandida → todas las 8 piezas con implementación estructural | `kernel/cache/` T3 |
| DSC-G-008 v3 (deducir consecuencias) | §4 deducción aplicada | §0 + §3 + §4 |
| DSC-S-006 v1.1 | semantic_cache_entries RLS | T2 |
| DSC-S-012 (anti-deriva migraciones) | Migración main pre-prod | T2 |
| DSC-MO-011 (Embryo Patch Lane) | Marcadores reversibles | T4 |

---

## 4. Criterios de cierre verde

- 6 tareas exit 0 + artifacts + tests verde
- 25+ tests passing sin DB ni red
- Tabla creada en prod + pgvector habilitado
- Dashboard HTML generado contra prod
- Wiring marcado RUBIES_BEGIN/END
- Cowork audita DSC-G-008 v3 + T2-B PBA convergente
- Frase canónica: `💎 RUBIES-001 — DECLARADO (6/6 verde) — Reloj Suizo 8/8 piezas CERRADO SIMBÓLICO`

**Cuando RUBIES-001 cierra verde, el Monstruo tiene las 8 piezas canónicas del Reloj Suizo implementadas estructuralmente.** Marca cierre de doctrina Capa 2 Tiempo+Energía.

---

## 5. Owner candidato y timing

**Owner técnico:** Manus Hilo Ejecutor 2 (continuidad post-REMONTOIR) O Hilo Catastro (post MEGA-CIERRE-HOY si bandwidth)
**Owner arquitectónico:** Cowork T2-A (DSC-G-008 v3 audit) + Perplexity T2-B (PBA convergencia)
**Owner humano final:** Alfredo T1 (firma + celebración doctrinal 8/8 piezas Reloj Suizo)
**Timing:** post-REMONTOIR-001 cerrado. Estimado 2026-05-14/15 si velocity mantiene.

---

## 6. Trazabilidad

- Origen: `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §2.1 fila Rubíes/Jewels
- Predecesores: las 7 piezas previas (Resorte/Escape/Áncora/Volante/Espiral/Rotor/Remontoir)
- Sucesor: ninguno estructural — RUBIES cierra Capa 2 Tiempo+Energía; siguiente magna será Capa 3 Soberanía
- Delta esperado Obj global: +2 pts (Obj #3 + #11)

---

## 7. Pre-flight check (Ejecutor al arrancar)

```bash
cd ~/el-monstruo && git status && git pull origin main

# Verificar piezas previas mergeadas:
gh pr view 116 --json state,merged  # ESCAPE-001 esperado MERGED
ls kernel/escape kernel/espiral kernel/remontoir kernel/rotor  # todos existen

# Verificar response_cache.py actual:
wc -l kernel/response_cache.py

# Verificar pgvector extension:
python3 -c "import psycopg; conn=psycopg.connect(...); cur=conn.cursor(); cur.execute(\"SELECT extname FROM pg_extension WHERE extname='vector'\"); print(cur.fetchone())"
# Esperado: ('vector',). Si NULL, T1 spec o T2 expande para habilitar la extensión primero.
```

Si pre-flight rojo, reportar al bridge.

---

**Estado:** FIRME T2-A 2026-05-12 ~08:40 UTC. Pendiente ratificación T1 explícita en próximo turno. Spec armado paralelo a PR #116 audit con autorización T1 "si avanza". Kickoff PENDIENTE — espera Reloj Suizo cadena ROTOR→ESCAPE→ESPIRAL→REMONTOIR cerrada o paralelo bandwidth Ejecutor/Catastro.
