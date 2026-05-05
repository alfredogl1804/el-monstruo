# Sprint 86.8 — Catastro `confidentiality_tier` por modelo · Pre-investigación

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Estado:** Spec firmado, listo para arranque inmediato en paralelo con Sprint 87.1 (Memento)
> **Sprint asignado:** Hilo Manus Catastro
> **Dependencias:** Sprint 86.5 + 86.6 + 86.7 cerrados; arquitectura del Catastro estable
> **Cierra:** prerequisito magna del SMP (Sovereign Memory Protocol) firmado en `docs/EL_MONSTRUO_APP_VISION_v1.md` Cap 7

---

## Contexto

El documento de visión del Monstruo firmado hoy define el SMP como cimiento inviolable de la app Flutter. Una de las propiedades del SMP es:

> *"El kernel del Monstruo opera sobre los datos sin verlos en claro. El Catastro elige modelos teniendo en cuenta sensibilidad del prompt: nunca se manda data sensible a un modelo que no califica para procesarla."*

Para que esta propiedad sea operacional, **cada modelo del Catastro necesita un atributo `confidentiality_tier`** que el runtime usa para filtrar candidatos según la sensibilidad del prompt entrante.

Sprint 86.8 materializa ese atributo. NO toca crypto, NO toca Mobile, NO toca SMP per se. Solo agrega la metadata necesaria al Catastro para que cuando SMP llegue, el filtrado esté disponible inmediatamente.

## Objetivo del Sprint

Cada modelo del Catastro tiene un atributo `confidentiality_tier` con uno de 4 valores documentados, y el `catastro_service.choose_model()` acepta un parámetro `min_tier_required` que filtra candidatos antes de aplicar Trono Score.

## Decisiones arquitectónicas firmes

### Decisión 1 — 4 tiers de sensibilidad

| Tier | Descripción | Modelos típicos |
|---|---|---|
| `local_only` | Corre on-device, ningún byte sale al exterior | Llama 3.3 7B local, Mistral 7B local, modelo propio futuro del Monstruo |
| `tee_capable` | Corre en confidential computing (Trusted Execution Environment) | Modelos con Anthropic Confidential Compute, AWS Nitro Enclaves |
| `cloud_anonymized_ok` | Cloud LLMs que pueden recibir prompts anonimizados (entidades sensibles sustituidas por placeholders) | Claude API, GPT-4, Gemini |
| `cloud_only` | Cloud LLMs que necesitan datos en claro — NO aceptables para sensibilidad alta | LLMs sin garantías de confidentiality (algunos modelos open source en HuggingFace inference) |

### Decisión 2 — Migration 027 al schema del Catastro

```sql
ALTER TABLE catastro_modelos
  ADD COLUMN confidentiality_tier TEXT NOT NULL DEFAULT 'cloud_only'
  CHECK (confidentiality_tier IN ('local_only','tee_capable','cloud_anonymized_ok','cloud_only'));

CREATE INDEX idx_catastro_modelos_confidentiality
  ON catastro_modelos (confidentiality_tier);
```

Default conservador: `cloud_only`. Modelos individuales se promueven manualmente vía script de migration o vía revisión humana en próximas iteraciones.

### Decisión 3 — Asignación inicial conservadora

Para cada modelo activo en el Catastro hoy, asignación inicial basada en evidencia pública:

- Modelos open source con quantización local conocida (Llama, Mistral, Phi) → `local_only`
- Modelos cloud con TEE confirmado (Anthropic Confidential, AWS Nitro) → `tee_capable`
- Modelos cloud comerciales con NDA confidentiality (Claude, GPT, Gemini) → `cloud_anonymized_ok`
- Resto → `cloud_only` (default conservador hasta verificación)

La asignación se hace en `scripts/027_sprint86_8_assign_confidentiality_tiers.sql` con comentarios justificando cada caso.

### Decisión 4 — `catastro_service.choose_model()` con filtrado

```python
def choose_model(
    task: str,
    macroarea: int = None,
    min_tier_required: str = "cloud_only",  # default permisivo
    ...
) -> ModelChoice:
    """
    Elige modelo del Catastro filtrado por confidentiality_tier mínimo.

    min_tier_required:
      - "local_only" → solo locales
      - "tee_capable" → locales O TEE-capable
      - "cloud_anonymized_ok" → locales, TEE, o cloud-anonymized
      - "cloud_only" → cualquiera (default)
    """
    candidates = filter_by_tier(active_models, min_tier_required)
    if not candidates:
        raise NoEligibleModelError(
            f"No models satisfy min_tier_required={min_tier_required}"
        )
    return apply_trono_score(candidates, task, macroarea)
```

### Decisión 5 — Capa Memento aplicada

Operations registradas:
- `catastro_choose_model_with_tier_filter` — antes de filtrado, valida que el tier requerido sea coherente con el contexto de la operación

### Decisión 6 — Tests + smoke productivo

Tests unitarios:
- 4 casos por tier (1 con candidatos disponibles, 1 con `NoEligibleModelError` esperado por filtro)
- Test de migration con rollback
- Test de asignación inicial coherente

Smoke productivo:
- Pipeline E2E (Sprint 87) con `min_tier_required="cloud_anonymized_ok"` produce resultado distinto a sin filtro
- Verificar que cuando se requiere `local_only` y no hay locales activos, falla con error claro

## Bloques del Sprint

### Bloque 1 — Migration 027 + asignación inicial (30-45 min)
- `scripts/027_sprint86_8_confidentiality_tier_schema.sql`
- `scripts/run_migration_027.py`
- `scripts/027_sprint86_8_assign_confidentiality_tiers.sql` con justificación inline por modelo

### Bloque 2 — `catastro_service.choose_model()` modificado (30 min)
- Nuevo parámetro `min_tier_required`
- Filtrado en runtime
- Error claro si no hay candidatos
- Capa Memento aplicada

### Bloque 3 — Schema_generated.py regenerado + tests drift (15-20 min)
- `scripts/_gen_catastro_pydantic_from_sql.py --check`
- `kernel/catastro/schema_generated.py` regenerado con nueva columna
- `tests/test_catastro_schema_drift.py` actualizado (BASELINE_DRIFT puede crecer)

### Bloque 4 — Tests + smoke (30-45 min)
- Tests unitarios de filtrado por tier (8+ casos)
- Smoke productivo: pipeline E2E con tier filter activo

### Bloque 5 — Bridge + reporte cierre (10-15 min)
- `bridge/SPRINT_86_8_OPERATIONAL_GUIDE.md` con guía de cómo asignar tier a nuevos modelos
- Reporte cierre con file_append (NO heredoc)

## ETA total recalibrada

5 bloques × ~30 min promedio = **1-2 horas reales** según Apéndice 1.3.

## Métricas de éxito

| Métrica | Target |
|---|---|
| Migration 027 corre sin errores | ✅ |
| Cada modelo del Catastro tiene `confidentiality_tier` asignado | ✅ |
| `choose_model()` filtra correctamente por tier | ✅ |
| Tests acumulados Catastro | ≥ 380 PASS |
| Smoke productivo: pipeline E2E con filter funciona | ✅ |
| Schema_generated.py actualizado sin drift inesperado | ✅ |

## Disciplina obligatoria

- Capa Memento aplicada
- Brand DNA en errores: `catastro_choose_model_no_eligible_tier`, `catastro_migration_027_*_failed`
- Anti-Dory: stash → pull rebase → pop antes de cada commit
- NO heredoc al bridge (semilla 40)
- Standby duro: ANULADO por política Cowork

## Zona primaria

```
kernel/catastro/catastro_service.py (modificación)
kernel/catastro/models.py (modificación si aplica)
kernel/catastro/schema_generated.py (regenerado)
scripts/027_sprint86_8_confidentiality_tier_schema.sql (NUEVO)
scripts/run_migration_027.py (NUEVO)
scripts/027_sprint86_8_assign_confidentiality_tiers.sql (NUEVO)
scripts/_smoke_sprint86_8_tier_filter.py (NUEVO)
tests/test_sprint86_8_confidentiality.py (NUEVO)
bridge/SPRINT_86_8_OPERATIONAL_GUIDE.md (NUEVO)
```

## NO TOCÁS

- `kernel/e2e/*` (zona Sprint 87.1 — Memento corriendo en paralelo)
- `kernel/embriones/*` (zona Sprint 87.1)
- `kernel/memento/*` (zona cerrada)
- `apps/mobile/*` (zona Mobile)
- `scripts/_gen_catastro_pydantic_from_sql.py` (script existente, solo se invoca para regenerar)

## Conexión con visión Mobile

Cuando Sprint Mobile 0 (SMP) se implemente, el `confidentiality_tier` de cada modelo va a ser consultado por el SMP runtime para decidir qué modelos pueden procesar qué prompts. Sprint 86.8 es el prerequisito habilitador. Sin él, el SMP no tiene metadata para filtrar.

## Próximo sprint después

Sprint 86.9 — Catastro Macroárea 5 (Embeddings) si Alfredo prioriza expansión de fuentes. O Sprint 91 Capa C2 SEO si prioriza capas transversales sobre macroáreas.

— Cowork (Hilo B)
