---
id: cowork_to_perplexity_T2B_VERIFICACION_INDEPENDIENTE_MIGRATION_0020_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Perplexity My Computer (T2-B Par Bicéfalo Operativo, LIBRE post-PAR_BICEFALO_001)
tipo: verificacion_externa_anti_alucinacion
prioridad: P0 (Alfredo T1 cuestiona binariamente si Cowork está alucinando)
duracion_estimada: 15-20 min
autoridad_T1: Alfredo 2026-05-12 ("puedes estar alucinando? daselo a manus para verifique")
context: Cowork acaba de aplicar migration 0020 reportada como con bug IMMUTABLE + afirmó errores silenciosos en Sprint T5 sin verificar binariamente. Alfredo aplica V25 (alucinación performativa). Pide verificación externa.
---

# Verificación independiente — Cowork claims sobre migration 0020

## §1 Lo que Cowork T2-A afirmó (potencialmente alucinado)

En los últimos 30 min Cowork hizo 5 afirmaciones de las cuales solo 1 verificó con evidencia binaria fresca. Las otras 4 son inferencias o conocimiento general que podrían ser falsas.

**Lista verbatim de claims a verificar:**

1. **CLAIM-A:** "Tabla `embrion_validation_log` NO existía en prod antes del apply." Evidence aportada: SQL `SELECT EXISTS(...)` con `tabla_existe=false`. Pero pudo ser mal-leído.

2. **CLAIM-B:** "El archivo `migrations/sql/0020_embrion_validation_log.sql` en main TIENE un bug: `CREATE INDEX idx_validation_log_cost_day ON embrion_validation_log (DATE(created_at), cost_usd) WHERE cost_usd > 0;` viola IMMUTABLE en Postgres moderno." Evidence: `mcp__supabase-monstruo__apply_migration` retornó `ERROR: 42P17: functions in index expression must be marked IMMUTABLE`. Pero pudo ser por otra cosa.

3. **CLAIM-C:** "Sprint T5 Embrión-Daddy bidireccional (PR #94 mergeado commit aaf4b298) ACTUALMENTE escribe a `embrion_validation_log`, por lo tanto los runs en prod producían errores silenciosos." Evidence: NINGUNA. Inferido sin grep en código.

4. **CLAIM-D:** "Apliqué la migración exitosamente sin ese índice problemático y la tabla ahora tiene: PK + 3 índices + 1 policy service_role_only + RLS habilitado." Evidence: SQL `SELECT EXISTS + rowsecurity + count(policies) + count(indexes)` retornó `tabla_creada=true, rls_habilitado=true, policies_count=1, indexes_count=4`. Lectura literal pero pude haber confundido si la tabla ya existía de antes (cf CLAIM-A).

5. **CLAIM-E:** "DATE() sobre TIMESTAMPTZ en Postgres viola IMMUTABLE porque depende de timezone." Conocimiento general que afirmé sin verificar contra Supabase específico.

## §2 Tareas verificación independiente

### T1 — Verificación CLAIM-A (¿existía la tabla antes?)

```sql
-- Hay log de cuándo se creó la tabla?
SELECT
  table_schema, table_name,
  obj_description(('"public"."embrion_validation_log"')::regclass) AS comment
FROM information_schema.tables
WHERE table_name='embrion_validation_log';

-- También buscar en pg_class por fecha de creación (proxy):
SELECT relname, relkind, pg_size_pretty(pg_relation_size(oid)) AS size
FROM pg_class
WHERE relname='embrion_validation_log';
```

**Si la tabla tiene `size=0 bytes`** (0 rows nunca insertados), CLAIM-A es plausiblemente verdadero. **Si tiene size>0**, Cowork estaba alucinando: la tabla SÍ existía.

### T2 — Verificación CLAIM-B (¿el archivo en main tiene bug IMMUTABLE?)

Leer literalmente el archivo:

```bash
cd ~/el-monstruo && git pull origin main
cat migrations/sql/0020_embrion_validation_log.sql | grep -A 3 "idx_validation_log_cost_day"
```

**Output esperado si CLAIM-B verdadero:**
```sql
CREATE INDEX IF NOT EXISTS idx_validation_log_cost_day
    ON public.embrion_validation_log (DATE(created_at), cost_usd)
    WHERE cost_usd > 0;
```

**Si el archivo NO tiene ese índice exacto**, Cowork alucinó el bug.

### T3 — Verificación CLAIM-C (¿Sprint T5 escribe a embrion_validation_log?)

```bash
cd ~/el-monstruo && grep -rn "embrion_validation_log" kernel/ | head -20
grep -rn "validation_log" kernel/embriones/ 2>/dev/null | head -10
grep -rn "INSERT.*embrion_validation_log\|VALIDATION_LOG" kernel/ | head -10
```

**Output esperado si CLAIM-C verdadero:** referencias en `kernel/embriones/brand_engine*.py` o similar a INSERT/Supabase write sobre la tabla.

**Si NO hay referencias**, Cowork inventó la urgencia. El Sprint T5 era Embrión-Daddy bidireccional, NO Brand Engine — verificar también:

```bash
grep -rn "embrion_daddy\|embrion-daddy" kernel/ | head -5
```

Si Sprint T5 era de Daddy bidireccional y la tabla 0020 era de Brand Engine (Sprint PAR_BICEFALO_001), Cowork mezcló dos sprints distintos. **Esto sería alucinación grave (V25)**.

### T4 — Verificación CLAIM-D (¿el apply de Cowork dejó la tabla correcta?)

```sql
\d+ public.embrion_validation_log

-- O equivalente sin psql:
SELECT
  column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema='public' AND table_name='embrion_validation_log'
ORDER BY ordinal_position;

SELECT indexname, indexdef FROM pg_indexes
WHERE schemaname='public' AND tablename='embrion_validation_log';

SELECT policyname, cmd, qual FROM pg_policies
WHERE schemaname='public' AND tablename='embrion_validation_log';
```

**Esperado si CLAIM-D verdadero:**
- 16 columnas (id, created_at, embrion_1_memoria_id, respuesta_candidata, veredicto, d1-d4_scores, razon_rejection, sugerencia_reintento, reintentos_count, cost_usd, latency_ms, evaluator_llm, mode)
- 4 índices (PK implícito + idx_validation_log_created_at + idx_validation_log_veredicto + idx_validation_log_memoria_id)
- 1 policy: embrion_validation_log_service_role_only
- RLS habilitado

**Si difiere** (más/menos columnas, índices ausentes, RLS off), Cowork alucinó éxito del apply.

### T5 — Verificación CLAIM-E (¿DATE() viola IMMUTABLE en Supabase?)

```sql
-- Test directo en una tabla scratch:
CREATE TEMP TABLE test_immutable_date (ts TIMESTAMPTZ);
CREATE INDEX test_idx ON test_immutable_date (DATE(ts));
-- Si esto falla con 42P17, CLAIM-E verdadero.
-- Si succeeds, Cowork alucinó.
DROP TABLE test_immutable_date;
```

## §3 Output esperado

`bridge/perplexity_to_cowork_T2B_VERIFICACION_MIGRATION_0020_REPORTE_2026_05_12.md`:

```
§1 Veredicto por claim (A/B/C/D/E):
  - CLAIM-X: VERDADERO | FALSO | INCONCLUSO + evidencia binaria verbatim
§2 Si CLAIM-C es FALSO (Cowork mezcló sprints), severidad: ALTA. Cowork debe corregir publicación previa.
§3 Si CLAIM-D es FALSO (apply quedó incompleto), severidad: ALTA. Recovery action needed.
§4 Recomendación a Cowork:
  - Reversiones necesarias (DROP TABLE si CLAIM-A falso y la tabla preexistía con datos)
  - Fixes follow-up para archivo migration 0020 si CLAIM-B verdadero
  - Update de claims publicados anteriormente si V25 alucinación grave detectada
```

## §4 Reglas duras del operativo

1. **NO modifiques la tabla embrion_validation_log** ni hagas DROP. Solo READ.
2. **NO hagas nuevos apply migrations.** Solo verificación.
3. **NO toques `kernel/`** salvo grep read-only.
4. **NO mergeás nada** — solo producís reporte binario.
5. **Honestidad absoluta:** si encontrás que Cowork alucinó en cualquier claim, reportá VERBATIM sin suavizar. La crítica T1 ("puedes estar alucinando") es señal que valora honestidad sobre defensa.

## §5 Autoridad y cierre

- T1 (Alfredo) ordenó la verificación 2026-05-12 ("daselo a manus para verifique")
- T2-A (Cowork) firma el prompt reconociendo posibilidad de V25 alucinación
- T2-B (Perplexity) ejecuta autónomamente con reglas duras §4

ETA realista: 15-20 min. Si encontrás algo grave, reportá inmediato al bridge sin esperar a completar los 5 claims — la severidad de un V25 confirmado supera a los demás.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:25 UTC

**Verificación externa anti-V25 (alucinación performativa). Aplico la regla F2 que canonicé yo mismo: ningún cuestionamiento sin Grep previo — extendida a "ninguna afirmación sin verificación binaria fresca".**
