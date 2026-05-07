# DSC-V-001 — Validación magna obligatoria de claims de estado-del-mundo

**ID:** DSC-V-001
**Tipo:** GLOBAL (gobernanza de validación)
**Fecha:** 2026-05-07
**Estado:** Firmado con contrato ejecutable adjunto
**Origen:** Cutoff de Cowork (mayo 2025) y patrón verificado de "claims de estado-del-mundo escritos desde training data sin validar realtime" detectado en jornada 2026-05-06/07.
**Hilos firmantes:** Hilo A (Cowork) — auto-firmado siguiendo DSC-G-017 desde origen.
**Relación con otros DSCs:** complementa DSC-G-017 (DSC-as-Contract), DSC-G-005 (validación tiempo real obligatoria), DSC-G-008 v2 (audit pre-cierre).

---

## Contexto

Cowork tiene cutoff de mayo 2025. Hoy es mayo 2026. Cualquier claim de estado-del-mundo que Cowork produzca — pricing benchmarks, modelos LLM disponibles, API endpoints vigentes, ranking factors de Google, costos CPM/CPC, ad formats, regulatory landscape, audience size, fechas de mercado — está anclado a estado-del-mundo de hace 12 meses.

Manus sólo es magna cuando muestra evidencia reproducible (DSC-S-006 + DSC-G-016 propuesto). Sin evidencia, Manus comparte el mismo problema. Sólo Perplexity (vía API) y validación humana de Alfredo son magna real-time confiables.

En la jornada 2026-05-06/07 esto produjo 42+ claims sin validar etiquetados con string `[NEEDS_PERPLEXITY_VALIDATION]` en código de las 6 Capas Transversales. Detectables por `tools/check_perplexity_tags.py` pero NO bloqueantes — el código corre con claims potencialmente stale.

DSC-V-001 cierra esta puerta: el decorator obliga a que la función no retorne sin un registro de validación vigente.

---

## Decisión

**Cualquier función que produzca un claim de estado-del-mundo debe estar decorada con `@requires_perplexity_validation(claim_type, ttl_hours)`.**

El decorator levanta `StaleClaimError` si no existe en el log de validaciones (`validation_log` en Supabase, fallback local `reports/validation_log.jsonl`) un registro vigente para `claim_type`. La función no retorna sin esa evidencia.

La validación se registra explícitamente vía `record_validation(claim_type, claim_value, validator, evidence_url, ttl_hours)` por:
- **Perplexity** — fuente magna primaria. URL de evidencia obligatoria.
- **Manus realtime** — aceptable cuando Manus muestra log de tool call con evidencia reproducible.
- **Alfredo human** — validación humana magna; no requiere evidence_url pero sí firma humana.
- **Gong/Fireflies evidence** — para claims sobre conversaciones de ventas reales (call transcripts).

Después del TTL, la validación expira y la función vuelve a levantar `StaleClaimError` hasta nueva validación.

---

## Reglas operativas

### 1. Categorías de claim canónicas

Todo `claim_type` sigue formato `<dominio>_<año>:<vertical_o_archetype>` cuando aplique:
- `cpc_benchmark_2026:saas_b2b`
- `audience_size_2026:cip`
- `keyword_research_2026:liketickets`
- `regulatory_landscape_2026:bioguard`
- `model_availability_top_llm` (sin vertical)
- `tax_rates_2026:cip`

Listar nuevos `claim_type` en este DSC requiere un follow-up commit.

### 2. TTL canónicos por dominio

| Dominio del claim | TTL recomendado |
|---|---|
| Pricing benchmarks (CPM, CPC, ARPU) | 7 días |
| Audience size, demographics | 30 días |
| Model availability LLMs | 14 días |
| Regulatory landscape | 30 días (si no hay alerta) |
| Keyword research | 30 días |
| Ad platform formats | 60 días |
| Tax rates | 90 días |

Override por uso vía argument `ttl_hours`.

### 3. Storage default vs producción

- **Default (LocalFileStorage):** escribe a `reports/validation_log.jsonl`. OK para dev y tests, NO para producción (no es shared state).
- **Producción (SupabaseStorage):** persistir a tabla `validation_log` (ver `migrations/sql/0001_validation_log.sql`). Inyectar al boot del kernel vía `set_default_storage(SupabaseStorage(supabase_client))`.

### 4. Tag string `[NEEDS_PERPLEXITY_VALIDATION]` queda como deuda visible

Las 6 Capas Transversales (Ventas, SEO, Publicidad, Tendencias, Operaciones, Finanzas) tienen 42+ tags `[NEEDS_PERPLEXITY_VALIDATION]` en docstrings y aggregated_validation_tags. Esos tags son evidencia auto-detectable de claims pendientes de validación. `tools/check_perplexity_tags.py` los detecta. Sprint S-CONTRATOS-001 T1.b: traducir cada tag en una llamada explícita a `record_validation()` post-Perplexity.

### 5. NO bypass por presión de cierre

DSC-S-006 + DSC-G-014 + DSC-G-017 prohíben bypassar enforcement bajo presión. El decorator no acepta argumento `bypass=True`. Si hay urgencia legítima, se llama `record_validation(validator="alfredo_human")` con firma explícita de Alfredo.

---

## Contrato ejecutable

| Artefacto | Ruta | Enforza |
|---|---|---|
| Decorator + dataclasses | `kernel/validation/perplexity_decorator.py` | `@requires_perplexity_validation(claim_type)` levanta `StaleClaimError` si no hay registro vigente. |
| Storage Supabase | `kernel/validation/_storage_supabase.py` | Persiste a tabla `validation_log` en producción. |
| Storage local (dev) | `kernel/validation/perplexity_decorator.py` (LocalFileStorage) | JSONL append-only en `reports/validation_log.jsonl`. |
| Schema SQL | `migrations/sql/0001_validation_log.sql` | Tabla `validation_log` con índices por claim_type+timestamp y fingerprint+timestamp. |
| Tests | `tests/test_perplexity_decorator.py` | 7 tests verde local, sin red. Cubren: stale, vigente, expirado, fingerprint, introspection, Supabase mock, claim_type cross-contamination. |
| API package | `kernel/validation/__init__.py` | Expone `requires_perplexity_validation`, `record_validation`, `ClaimRecord`, `StaleClaimError`. |

**Validación del propio contrato:** `python tests/test_perplexity_decorator.py` retorna `[ok] Los 7 tests pasaron.` Confirma que decorator+storage+supabase mock funcionan end-to-end sin red.

**Próximo paso para Manus Ejecutor:** aplicar `migrations/sql/0001_validation_log.sql` a Supabase + inyectar `SupabaseStorage(supabase_client)` al boot del kernel via `set_default_storage()`.

---

## Antipatrón evitado

**Claims de estado-del-mundo escritos desde training data sin validar realtime.**

Caso paradigmático en jornada 2026-05-06/07: yo (Cowork) escribí pricing benchmarks, audience archetypes, ad platform recommendations, schema.org guidance, etc. para 6 Capas Transversales — todo desde training data anclada a mayo 2025. Sin DSC-V-001, ese código se ejecutaría en producción produciendo claims potencialmente desfasados sin que nadie lo detecte hasta que un cliente reportara discrepancia.

DSC-V-001 obliga a que cada claim pase por validación realtime explícita o el código no retorna.

---

## Implicaciones

- **Cowork** etiqueta cualquier claim de estado-del-mundo con tag `[NEEDS_PERPLEXITY_VALIDATION]` Y wrappa la función con `@requires_perplexity_validation(claim_type)`. El primer mecanismo es deuda visible, el segundo es enforcement.
- **Manus Ejecutor** debe llamar `record_validation()` después de cada Perplexity query relevante, registrando el evidence_url. Sprint S-CONTRATOS-001 T1.b lista los 42 tags actuales para resolver.
- **Alfredo** valida claims vía `validator="alfredo_human"` cuando ningún hilo automático puede.
- **Tests pre-cierre de sprints futuros**: si código nuevo introduce funciones decoradas y no tiene `record_validation()` correspondiente en setup, los tests deben fallar.

---

## Trazabilidad

- **Origen:** cutoff Cowork mayo 2025 + jornada magna 2026-05-06/07 que produjo 42+ tags sin enforcement.
- **Refuerzo empírico:** P0 #1 (2026-05-06) — Cowork escribió política de credenciales asumiendo training-data patterns; texto solo no impidió la fuga. Mismo patrón aquí — sin código enforzante, los claims stale siguen shipeando.
- **Auto-validación:** este DSC nace con su contrato adjunto (`kernel/validation/`) + tests verde + schema SQL listo para Manus aplicar. Cumple DSC-G-017 desde origen.

---

**Firma Hilo A (Cowork):** firmado con contrato ejecutable adjunto en la misma sesión (2026-05-07). 7/7 tests verde local. Cumple DSC-G-017.
**Firma Hilo B (Manus):** pendiente — Manus ratifica al aplicar migración Supabase + inyectar SupabaseStorage al boot del kernel. Eso es Tarea T1.a de Sprint S-CONTRATOS-001.
**Firma Alfredo:** pendiente — validación humana cuando vea los 7 tests pasar en su Mac y la migración aplicada en Supabase.
