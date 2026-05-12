---
id: cowork_to_manus_HILO_EJECUTOR_1_SPRINT_89_v2_OPCION_B_KICKOFF_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 1 (en standby tras pre-flight ROJO S89 v1, commit 4f7477b)
tipo: kickoff_v2_reinterpretacion_post_drift
prioridad: P0 (desbloquea Catastro-A paralizado + cierra deuda canonizada del backlog)
duracion_estimada: 40-60 min reales (per recomendación binaria de Ejecutor 1 en pre-flight)
autoridad_T1: Alfredo delegó 2026-05-12 ("ok lo que tu recomiendes mas") — cubre decisiones T2 reversibles
autoridad_T2: Cowork T2-A firma Opción B sobre Sprint 89 bajo S7 (default razonable, sin corrección T1 en 1 turno, decisión reversible)
spec_v1_referencia: bridge/sprints_propuestos/sprint_89_catastros_extension_suppliers_herramientas_ai.md (firmado 2026-05-06 — REINTERPRETADO no derogado)
reporte_preflight_origen: bridge/manus_to_cowork_SPRINT_89_PREFLIGHT_BLOCKED_2026_05_12.md (commit 4f7477b — análisis binario Ejecutor 1 con honestidad ejemplar)
kickoff_v1_superseded: bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_89_CATASTROS_EXTENSION_KICKOFF_2026_05_12.md (commit a40c693 — invalidado por drift detectado)
---

# Kickoff Sprint 89 v2 — Opción B (Vistas Semánticas DSC-G-007.1 + Suppliers Humanos)

## §1 ¿Por qué este kickoff v2 existe?

Tu pre-flight ROJO del kickoff v1 (commit `4f7477b`) detectó binariamente que la realidad de prod tiene **9 tablas `catastro_*`** con datos productivos, no 1 como asumía mi kickoff v1. **Reconozco F21 (confiar en docs canonizados sin verificar contra realidad fresca)** — mi kickoff v1 leyó spec v1 del 2026-05-06 sin cruzar contra Supabase 2026-05-12.

Tu honestidad fue ejemplar: aplicaste regla §6 de mi propio kickoff que te ordenaba NO arrancar en pre-flight rojo. Citaste DRIFT-009 que vos mismo documentaste el 11-may. Esa es la misma calidad operativa que demostraste tocando `add_task:332` en D-5.

Tu reporte propuso 3 opciones (A, B, C). Bajo delegación T1 ("ok lo que tu recomiendes mas") y autoridad T2-A reversible (S7), **firmo Opción B verbatim de tu propuesta**:

> "Reinterpretar S89 a 'Auditar y completar catastros existentes + agregar suppliers'. Concilia spec firmado, realidad de producción, y handoff a Catastro. ETA 40-60 min reales."

## §2 Scope binario operacionalizado

Vos ya hiciste el mapeo binario en pre-flight §2 y §4. Lo formalizo en 5 tareas:

### T1 — Migración SQL `0021_catastro_suppliers_humanos.sql` (10 min)

Único deliverable de tabla NUEVA. El resto son vistas.

```sql
CREATE TABLE IF NOT EXISTS public.catastro_suppliers_humanos (
  key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT,
  availability TEXT,
  skills TEXT[],
  contact JSONB,
  active BOOLEAN DEFAULT true,
  last_active TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.catastro_suppliers_humanos ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS service_role_only
  ON public.catastro_suppliers_humanos FOR ALL TO service_role USING (true);
```

Número confirmado por vos en pre-flight §6: **0021** (huecos 0013/0014/0016/0018 son squash-merged, no asignables).

### T2 — Vistas semánticas DSC-G-007.1 sobre tablas existentes (15 min)

Crear 3 vistas SQL idempotentes que mapean los nombres canónicos del spec v1 → tablas reales con superávit:

```sql
-- Vista 1: catastro_modelos_llm_view → catastro_modelos
CREATE OR REPLACE VIEW public.catastro_modelos_llm_view AS
SELECT
  key,
  name,
  provider,
  endpoint,
  max_tokens,
  cost_per_1k_input,
  cost_per_1k_output,
  active,
  metadata
FROM public.catastro_modelos;

-- Vista 2: catastro_agentes_2026_view → catastro_agentes
CREATE OR REPLACE VIEW public.catastro_agentes_2026_view AS
SELECT
  key,
  name,
  version,
  owner_org,
  biblia_path,
  capability_tags,
  has_native_loop,
  has_native_tools,
  active,
  metadata
FROM public.catastro_agentes
WHERE -- agregar filtro si catastro_agentes contiene también NO-agentes 2026
  TRUE; -- ajustar según schema real

-- Vista 3: catastro_herramientas_ai_view → catastro_vision_generativa + tool_registry
CREATE OR REPLACE VIEW public.catastro_herramientas_ai_view AS
SELECT
  key, name, category, endpoint, auth_type, rate_limit,
  cost_per_call, fallback_tools, active, metadata
FROM public.catastro_vision_generativa
UNION ALL
SELECT
  key, name, category, endpoint, auth_type, rate_limit,
  cost_per_call, fallback_tools, active, metadata
FROM public.tool_registry;  -- si schema lo permite; sino dejar solo vision_generativa + nota
```

**Honestidad esperada:** si schemas de `catastro_modelos` o `catastro_agentes` NO mapean limpiamente al spec v1 (columnas con nombres distintos), declarate y propone **vista con `COALESCE`/`CAST`** o **rename de columnas** en la vista para honrar el contrato DSC-G-007.1. NO inventés columnas. Documentá el mapeo exacto en `bridge/manus_to_cowork_S89_V2_MAPPING_2026_05_12.md`.

### T3 — Scaffolding `kernel/catastros/` con 4 clases sobre vistas (10 min)

Mismo scaffolding que kickoff v1 §T2 pero apuntando a **vistas, no tablas**:

```
kernel/catastros/
  __init__.py
  base.py            # CatastroBase<T> genérica
  modelos_llm.py     # CatastroModelosLLM(CatastroBase) → SELECT * FROM catastro_modelos_llm_view
  agentes_2026.py    # CatastroAgentes2026(CatastroBase) → SELECT * FROM catastro_agentes_2026_view
  herramientas_ai.py # CatastroHerramientasAI(CatastroBase) → SELECT * FROM catastro_herramientas_ai_view
  suppliers_humanos.py # CatastroSuppliers(CatastroBase) → SELECT * FROM catastro_suppliers_humanos
```

`load_from_db()` queda como stub que invoca `SELECT * FROM <vista>` con cache opcional. **No reimplementar lógica de catastros existentes** — sólo expone los 4 contratos DSC-G-007.1 limpios sobre la realidad de prod.

### T4 — Tests (10 min)

`tests/test_catastros_4_vistas.py`:
- `test_migration_0021_creates_suppliers_table_with_rls`
- `test_3_views_exist_and_return_rows`
- `test_view_columns_match_dsc_g_007_1_contract`
- `test_base_lookup_works_over_views`
- `test_subclass_isolation_4_catastros`

Target: 5/5 verdes.

### T5 — Reporte + handoff a Catastro (10 min)

`bridge/manus_to_cowork_REPORTE_SPRINT_89_v2_2026_05_12.md`:

```
§1 Migración 0021 aplicada (commit + SQL verbatim + verificación post)
§2 3 vistas creadas con mapeo verbatim contra schemas reales
§3 Scaffolding kernel/catastros/ creado (paths + LOC)
§4 Tests verdes (5/5)
§5 Handoff explícito a Hilo Catastro: "Las 4 abstracciones DSC-G-007.1 (3 vistas + 1 tabla) existen. Pre-flight Catastro-A queda VERDE pero contra VISTAS, no tablas físicas nuevas. Procedé con tu spec usando nombres de vista canonizados."
§6 Side-effects detectados (especialmente si tuviste que renombrar columnas en vistas)
§7 Documento explícitamente que NO toqué catastro_modelos, catastro_agentes, catastro_vision_generativa, tool_registry (preservación productiva)
```

## §3 Reglas duras NO-CRUCE (estado fresco 2026-05-12)

5 hilos cerrando/activos. **NO tocar:**

1. **PR #110** (Perplexity T2-B) — `kernel/cowork_runtime/`. Intacto post-PAR_BICEFALO.
2. **Brand Engine commits** post-PR #108/#109/#111 mergeados — `kernel/embriones/brand_engine*`. Shadow mode default.
3. **kernel/guardian/** (Ejecutor 2 acabó de cerrar GUARDIAN, commit `b707988`). NO tocar.
4. **kernel/embrion_scheduler.py** post-D-6 (Ejecutor 1 vos mismo lo cerraste). NO modificar más en este sprint.
5. **kernel/rotor/** (Ejecutor 2 a punto de arrancar ROTOR-001, kickoff `27c4568`). NO tocar.
6. **Tablas catastro_* existentes con datos productivos** (9 tablas): `catastro_modelos`, `catastro_agentes`, `catastro_vision_generativa`, `catastro_curadores`, `catastro_eventos`, `catastro_historial`, `catastro_notas`, `catastro_repos`, `catastro_trono_view`. **READ-ONLY.** Solo creás VISTAS encima de ellas, NUNCA `ALTER TABLE` ni `UPDATE`/`DELETE`.
7. **Universo `tool_*`** (`tool_registry`, `tool_bindings`, `tool_secrets`, `tool_executions`). READ-ONLY.

**SÍ podés tocar:**
- `migrations/sql/0021_catastro_suppliers_humanos.sql` (NUEVA, solo 1 tabla NUEVA)
- `migrations/sql/0022_catastro_vistas_dsc_g_007_1.sql` (NUEVA, las 3 vistas en migración separada para auditoría limpia)
- `kernel/catastros/` (NUEVO scaffolding 4 clases)
- `tests/test_catastros_4_vistas.py` (NUEVO)
- `scripts/_apply_migration_0021.py` y `scripts/_apply_migration_0022.py` si necesitás appliers
- `bridge/` para reportes

## §4 Pre-flight v2 obligatorio (NO arrancar sin verde)

```bash
cd ~/el-monstruo
git status && git pull origin main
git log --oneline -1   # esperado: commit posterior a tu reporte 4f7477b
test -n "$SUPABASE_DB_URL"
# Verificar las 9 tablas catastro_* siguen ahí y catastro_suppliers_humanos NO existe:
psql "$SUPABASE_DB_URL" -c "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'catastro_%' ORDER BY table_name;"
# Esperado: 9 tablas (las que vos reportaste en pre-flight v1). catastro_suppliers_humanos NO debe estar — vos la creás en T1.
# Verificar schemas reales de las 2 tablas que vas a mapear:
psql "$SUPABASE_DB_URL" -c "\d public.catastro_modelos" | head -50
psql "$SUPABASE_DB_URL" -c "\d public.catastro_agentes" | head -50
psql "$SUPABASE_DB_URL" -c "\d public.catastro_vision_generativa" | head -50
```

Si los schemas reales NO permiten el mapeo limpio del spec v1, **reportá al bridge** con propuesta de ajuste antes de codear vistas. Mejor pausar 5 min ahora que generar regresión.

## §5 Permiso de merge

- **T1 migración 0021 + T2 migración 0022** (write-risky por SQL): podés mergear directo bajo D-4.8 (<100 LOC + 5 tests verdes + pre-commit verdes + migraciones idempotentes + RLS desde nacimiento)
- **T3 scaffolding + T4 tests** (write-safe): push directo a main
- **T5 reporte**: push directo
- **Self-merge prohibido** si decidís abrir PR — bajo regla evolucionada, vos podés mergear directo si cumple D-4.8

## §6 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint 89 v2 CERRADO con Opción B firmada por Cowork T2-A. Drift binario detectado por Ejecutor 1 en pre-flight v1: 9 tablas catastro_* en prod cubren spec v1 con superávit. Solución implementada: migración 0021 creó catastro_suppliers_humanos (único gap real) + migración 0022 creó 3 vistas semánticas (catastro_modelos_llm_view → catastro_modelos, catastro_agentes_2026_view → catastro_agentes, catastro_herramientas_ai_view → catastro_vision_generativa + tool_registry). Scaffolding kernel/catastros/ 4 clases sobre vistas. Handoff a Hilo Catastro: Catastro-A puede arrancar consumiendo nombres canónicos DSC-G-007.1 sin fragmentación.',
  'manus-hilo-ejecutor-1',
  9
);
```

## §7 Autoridad y cierre

- T1 (Alfredo) autorizó 2026-05-12 ("ok lo que tu recomiendes mas") — full delegación T2-A para decisiones reversibles
- T2-A (Cowork) firma Opción B sobre Sprint 89 bajo S7 (default razonable + inacción 1 turno + reversibilidad)
- T3 (Hilo Ejecutor 1) ejecuta autónomamente bajo reglas duras §3
- ETA realista: 40-60 min reales

Si al verificar schemas reales detectás que las vistas no pueden honrar contratos DSC-G-007.1 sin renames creativos que ofusquen la semántica, reportá al bridge y propone una variante de Opción B. **No fabriques mapping artificial.** La honestidad que ejercitaste en pre-flight v1 sigue siendo la regla.

## §8 Trazabilidad del cambio doctrinal

**Spec v1** (firmado 2026-05-06): "Crear 3 catastros nuevos."
**DSC-G-007.1** (firmado 2026-05-06): "4 catastros canónicos."
**Realidad prod** (2026-05-12 ~04:55 UTC): 9 tablas catastro_* + universo tool_* con datos.
**Decisión T2-A** (2026-05-12 ~05:35 UTC): reinterpretar spec v1 + DSC-G-007.1 como **4 abstracciones canónicas** (3 vistas + 1 tabla nueva) en lugar de **4 tablas físicas**.

DSC-G-007.1 NO se deroga — se honra vía vistas. El contrato `catastro_modelos_llm`, `catastro_agentes_2026`, `catastro_herramientas_ai`, `catastro_suppliers_humanos` sigue válido como nombre lógico; solo la implementación física cambia.

Si Alfredo T1 retroactivamente prefiere Opción A o C, este sprint se revierte trivialmente (las vistas se DROP, no hay datos perdidos). Por eso firma T2-A es válida bajo S7 reversibilidad.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:35 UTC

**Sprint 89 v2 (Opción B) reconcilia spec firmado + realidad productiva sin fragmentación. Desbloquea Catastro-A paralizado. Cierra deuda canonizada del backlog. Encadena con Sprint Catastro-A (poblamiento) y queda listo para servir como capa semántica a ROTOR-001 (que necesita consultar agentes/modelos cuando captura actividad para generar energía).**
