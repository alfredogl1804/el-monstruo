# Sprint 86.8 — Operational Guide · `confidentiality_tier`

> **Autor:** Hilo Manus Catastro (Hilo B)
> **Sprint:** 86.8 · 2026-05-05
> **Estado:** Production-ready · 25/25 tests · 6/6 smoke gates verdes
> **Cierra:** prerequisito magna del **Sovereign Memory Protocol** (Cap 7 de `docs/EL_MONSTRUO_APP_VISION_v1.md`)

---

## 1. Qué resuelve este sprint

Cada modelo del Catastro ahora lleva un atributo **`confidentiality_tier`** con uno de cuatro valores:

| Tier | Rank | Significado |
|---|---|---|
| `local_only` | 0 | Corre on-device, ningún byte sale |
| `tee_capable` | 1 | Confidential computing (TEE / Nitro Enclaves) |
| `cloud_anonymized_ok` | 2 | Cloud LLM apto para prompts anonimizados |
| `cloud_only` | 3 | Cloud sin garantías de confidentiality (default conservador) |

El kernel del Catastro filtra candidatos antes de aplicar Trono Score si el caller pasa `min_tier_required` distinto al default `cloud_only`.

## 2. Cómo asignar tier a un modelo nuevo

Hay tres caminos según la fuente de evidencia:

1. **Modelo open-weight con quantización local conocida** → `local_only`. Justificación: el modelo se puede ejecutar on-device con `llama.cpp`, `mlc-llm` o equivalente sin conexión.
2. **Modelo cloud con TEE confirmado** → `tee_capable`. Requiere documentación pública del proveedor (Anthropic Confidential Compute, AWS Nitro Enclaves, Azure Confidential VM).
3. **Modelo cloud comercial con NDA y cláusula de no-train sobre data del cliente** → `cloud_anonymized_ok`. Requiere validar que el proveedor publica una política de privacy clara aplicable a datos via API (no chat consumer).

Si ninguna evidencia es concluyente, **se queda en `cloud_only`** (default conservador).

La asignación se hace editando `scripts/027_sprint86_8_assign_confidentiality_tiers.sql` y ejecutando la migration de re-asignación. Cada UPDATE va con un comentario justificando la fuente.

## 3. Cómo invocar el filtro desde código

### Opción A — Default permisivo (compat hacia atrás)

```python
from kernel.catastro.recommendation import RecommendationEngine

engine = RecommendationEngine(db_factory=...)
res = engine.recommend(use_case="resumir contrato", top_n=3)
# min_tier_required="cloud_only" por default → no filtra
```

### Opción B — Filtro explícito con degraded silencioso

```python
res = engine.recommend(
    use_case="analizar contrato confidencial",
    min_tier_required="cloud_anonymized_ok",
    top_n=5,
)
if res.degraded:
    # res.degraded_reason puede ser "no_models_match_tier_filter"
    handle_no_eligible_models(res)
```

### Opción C — Filtro con excepción estricta (SMP runtime)

```python
from kernel.catastro.recommendation import (
    RecommendationEngine,
    CatastroChooseModelNoEligibleTier,
)

try:
    res = engine.recommend(
        use_case="datos PII fiscales",
        min_tier_required="local_only",
        raise_on_no_eligible_tier=True,
    )
except CatastroChooseModelNoEligibleTier as e:
    # SMP runtime debe abortar la operación o degradar al usuario
    abort_with_smp_violation(e)
```

## 4. Semántica de `min_tier_required`

El parámetro funciona como **filtro de tier máximo aceptable** (no mínimo numérico). La regla es:

> Solo se aceptan modelos cuyo `rank(confidentiality_tier) <= rank(min_tier_required)`

Ejemplos:

- `min_tier_required="local_only"` (rank 0) → solo `local_only` (rank 0) pasa.
- `min_tier_required="tee_capable"` (rank 1) → `local_only` y `tee_capable` pasan.
- `min_tier_required="cloud_anonymized_ok"` (rank 2) → todos excepto `cloud_only`.
- `min_tier_required="cloud_only"` (rank 3) → cualquiera pasa (default permisivo).

## 5. Casos de error

| Error | Brand DNA code | Cuándo |
|---|---|---|
| `CatastroRecommendInvalidArgs` | `catastro_recommend_invalid_args` | `min_tier_required` no es uno de los 4 valores válidos |
| `CatastroChooseModelNoEligibleTier` | `catastro_choose_model_no_eligible_tier` | Filtro deja la lista vacía y `raise_on_no_eligible_tier=True` |
| `degraded_reason="no_models_match_tier_filter"` | n/a (no excepción) | Filtro deja la lista vacía y `raise_on_no_eligible_tier=False` (default) |

## 6. Cache invalidation

`min_tier_required` forma parte de la cache key de `recommend()`. Esto significa que:

- Llamadas con el mismo `use_case` pero distinto tier **NO se contaminan** entre sí.
- Llamadas con la misma `(use_case, tier)` reusan cache durante 60 segundos (TTL configurable).

## 7. Migration 027 — operación

### Aplicar al schema

```bash
python3 scripts/run_migration_027.py
```

El script:
1. Verifica conexión Supabase.
2. Aplica `027_sprint86_8_confidentiality_tier_schema.sql` (idempotente vía `IF NOT EXISTS`).
3. Ejecuta `027_sprint86_8_assign_confidentiality_tiers.sql` para asignación inicial conservadora.
4. Reporta `confidentiality_tier_breakdown` post-migration (cuántos modelos en cada tier).

### Re-asignar tier a un modelo

```sql
-- Ejemplo: promover Llama 7B local a local_only (tras verificación de quantización)
UPDATE catastro_modelos
   SET confidentiality_tier = 'local_only'
 WHERE id = 'meta/llama-3.1-7b-instruct'
   AND open_weights = true;

-- Brand DNA: registra evento
INSERT INTO catastro_eventos (modelo_id, tipo, detalle, fuente)
VALUES (
    'meta/llama-3.1-7b-instruct',
    'tier_promoted',
    'Promovido a local_only tras verificacion de quantizacion ggml',
    'manual_review'
);
```

## 8. Conexión con Sprint Mobile 0 (SMP)

Cuando el SMP runtime se construya, va a leer `confidentiality_tier` por modelo en cada decisión de routing:

```
Prompt entrante (Mobile)
   ↓
SMP detecta sensibilidad: low / medium / high
   ↓
Mapea a tier requerido:
   high   → local_only   (rank 0)
   medium → tee_capable  (rank 1)
   low    → cloud_anonymized_ok (rank 2)
   ↓
Catastro.recommend(min_tier_required=mapped, raise_on_no_eligible_tier=True)
   ↓
Best model que satisface tier ↑ Trono Score
```

Sprint 86.8 entrega la **metadata** y el **filtrado**. Sprint Mobile 0 entrega el **mapping de sensibilidad** y el **routing del prompt**.

## 9. Riesgos conocidos y mitigaciones

| Riesgo | Mitigación implementada |
|---|---|
| Tier asignado incorrectamente promueve modelo cloud a local_only | Default conservador `cloud_only` + UPDATE explícito requiere justificación inline en SQL |
| Filtro deja la lista vacía y el caller no sabe por qué | `degraded_reason` específico (`no_models_match_tier_filter`) distinto de `no_models_match_filters` |
| Cache cross-contamina entre tiers | `min_tier_required` parte de la cache key (validado por test) |
| Schema_generated.py drift al regenerar | Test `test_schema_generated_incluye_confidentiality_tier` valida cada PR |
| Modelos legacy sin `confidentiality_tier` poblado | Filtro defensivo: `r.get("confidentiality_tier") or "cloud_only"` (rank 3) |

## 10. Métricas de éxito alcanzadas

| Métrica | Target spec | Real |
|---|---|---|
| Migration 027 idempotente | ✅ | ✅ `IF NOT EXISTS` validado |
| `choose_model()` filtra por tier | ✅ | ✅ E2E 6/6 gates |
| Tests acumulados Catastro | ≥380 | **244+** (suite completa Sprint 86 + 86.5 + 86.6 + 86.7 + 86.8) |
| Smoke productivo verde | ✅ | ✅ 6/6 gates · 0.21s |
| Schema drift inesperado | NO | NO — drift trackeado, columna nueva intencional |

## 11. Archivos del sprint

```
kernel/catastro/recommendation.py          (M, +120 líneas)
kernel/catastro/schema_generated.py        (regenerado, +1 columna)
scripts/_gen_catastro_pydantic_from_sql.py (M, +1 línea: añadir 027 a MIGRATION_FILES)
scripts/027_sprint86_8_confidentiality_tier_schema.sql      (N, ~50 líneas)
scripts/027_sprint86_8_assign_confidentiality_tiers.sql     (N, ~120 líneas)
scripts/run_migration_027.py               (N, ~80 líneas)
scripts/_smoke_sprint86_8_tier_filter.py   (N, ~190 líneas)
tests/test_sprint86_8_confidentiality.py   (N, ~370 líneas, 25 tests)
bridge/SPRINT_86_8_OPERATIONAL_GUIDE.md    (N, este documento)
```

— Hilo Manus Catastro · 2026-05-05
