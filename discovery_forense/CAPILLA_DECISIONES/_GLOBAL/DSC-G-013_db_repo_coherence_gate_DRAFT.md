---
dsc_id: DSC-G-013
titulo: DB↔Repo Coherence Gate
estado: 🟡 DRAFT — espera convergencia 3 Sabios Tier 1 (Perplexity + GPT-5.5 Pro + Claude Opus 4.7)
autor_spec: Cowork T2-A
fecha_draft: 2026-05-18
ambito: _GLOBAL
hermanos: DSC-S-012 (anti-deriva migration numbering), DSC-S-016 (anti-fabricación), DSC-G-008 v4 (audit doctrine)
evidencia_magna: 3 manifestaciones del mismo patrón en 1 sesión Cowork (HOY 2026-05-17/18)
proximos_pasos: convergencia 3 Sabios + firma T1 + integración pre-flight audit_middleware
---

# DSC-G-013 — DB↔Repo Coherence Gate

> **Hipótesis doctrinal:** El estado canónico de El Monstruo se distribuye en al menos **3 fuentes paralelas** — código en repo, schema_migrations en Supabase, modelo mental del agente actuante. Sin un gate binario que verifique coherencia entre las 3 antes de cada acción magna, el sistema acumula drift silente que se manifiesta como F-pattern reincidentes.

## §1 Problema binario observado

El 2026-05-17/18, en una sola sesión Cowork, surgieron **3 manifestaciones del mismo patrón estructural** detectadas binariamente — sin que ningún agente las relacionara hasta el final del día. Cada una venía de una capa distinta de drift, pero la causa raíz era la misma: **no existe un gate que verifique coherencia DB↔Repo↔planificación antes de actos magnos**.

## §2 Evidencia binaria magna (3 casos, 1 sesión)

### §2.1 H12 — `run_costs` missing in repo vs schema

**Síntoma:** Manus E2 reportó que necesitaba la tabla `run_costs` que no existía en producción pese a estar referenciada en código de aplicación.

**Causa raíz binaria:**
- Migration 0015 `run_costs` existía en `migrations/sql/` del repo
- NO estaba registrada en `supabase_migrations.schema_migrations`
- Apply prod via MCP estaba pendiente de un sprint olvidado

**Drift identificado:** repo↔schema_migrations.

**Fix:** Cowork aplicó migration 0015 via MCP. Verificación post-apply: tabla `run_costs` + RLS + 3 indexes + 3 constraints + service_role_only policy.

**Investigación derivada:** sólo 12 migrations registradas en `schema_migrations` vs ~44 en repo. **Drift sistémico confirmado** — no es caso aislado.

**Fuentes:**
- Bridge MEMENTO H12 fix
- `supabase_migrations.schema_migrations` query verbatim

### §2.2 H13 — 4 tipos de `embrion_memoria` rechazados silenciosamente

**Síntoma:** Manus E2 reportó que el CHECK constraint `embrion_memoria_tipo_check` rechazaba un tipo nuevo (`evaluacion`) que el código intentaba insertar.

**Verificación binaria Cowork:**
- `grep -nE "tipo=\"" kernel/embrion_loop.py` reveló **4 tipos vivos en código**, no 2 como Manus E2 declaró:
  - `evaluacion` (líneas 1834, 2118)
  - `silencio_preverifier` (línea 1147)
  - `contribucion_sabio` (línea 2353, importancia=9 ALTA)
  - `radar_insight` (línea 2459)
- `SELECT COUNT(*) WHERE tipo IN (...)` = **0 filas** para los 4 tipos
- Significa: durante meses, todas las escrituras de esos tipos fueron rechazadas silenciosamente sin alerta

**Drift identificado:** código↔schema (CHECK constraint desactualizado vs código vivo).

**Fix:** Cowork aplicó migration 0047 via MCP expandiendo el CHECK constraint con los 4 tipos vivos.

**Hallazgo magno secundario:** `contribucion_sabio` con `importancia=9` significa que **toda síntesis de consulta a Sabios estuvo siendo rechazada silenciosamente desde despliegue del código**. F21 estructural mayor.

**Fuentes:**
- [Migration 0047](https://github.com/alfredogl1804/el-monstruo/blob/main/migrations/sql/0047_embrion_memoria_tipo_check_expand_vivos.sql)
- [Bridge H13 veredicto](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/cowork_to_manus_HILO_EJECUTOR_2_H13_VEREDICTO_2026_05_17.md)

### §2.3 F#15 — Manus E2 asumió numeración 0037 disponible (estaba ocupada)

**Síntoma:** Manus E2 propuso numerar H13 como migration 0037 y H14 (causal_events) como 0036.

**Verificación binaria Cowork** (`ls migrations/sql/`):
```
0036_radar_runs.sql                          ← aplicado prod, NO por Manus E2
0037_subscriptions_inventory_enrichment.sql  ← ya en repo, no aplicado prod
0038_la_forja_profiles.sql                   ← aplicado por Manus E2 mismo en D5.1
...
0046_la_forja_budget.sql                     ← último Manus E2 aplicó
```

**Realidad binaria:** próximo libre era 0047 (no 0037). H13 quedó como 0047. La asunción de Manus E2 era **off by 10**.

**Drift identificado:** planning↔reality dentro del mismo hilo Manus (E2 acabó de aplicar 0038-0046 horas antes y olvidó actualizar su modelo mental).

**Fix:** Cowork detectó pre-aplicación + aplicó 0047 (no 0037) + reportó F#15 a Manus E2 verbatim en bridge.

**Fuentes:**
- [Bridge H13 §3 numeración F21](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/cowork_to_manus_HILO_EJECUTOR_2_H13_VEREDICTO_2026_05_17.md)

## §3 Patrón estructural común — 3 capas de drift simultáneo

| Capa | H12 | H13 | F#15 |
|---|---|---|---|
| **(1) repo↔schema_migrations** | ✅ drift confirmado (12 registradas vs ~44 en repo) | parcial | parcial |
| **(2) código↔schema** | parcial | ✅ drift confirmado (4 tipos rechazados silente) | N/A |
| **(3) planning↔reality** | N/A | parcial | ✅ drift confirmado (numeración off by 10) |

**Hipótesis Cowork:** las 3 capas son **manifestaciones del mismo problema** — no existe un gate que fuerce al agente actuante a verificar binariamente cada capa antes de acción magna.

## §4 Solución propuesta — DSC-G-013 binario

### §4.1 Definición

Antes de cualquiera de las siguientes acciones, el agente actuante **DEBE** ejecutar el `coherence_gate.py` o equivalente que verifique las 3 capas:

| Acción magna | Gate obligatorio | Razón |
|---|---|---|
| `apply_migration` via MCP | Capa (1) | Verificar siguiente número libre en repo + schema_migrations + sin colisión |
| `INSERT` con campo enum/CHECK constraint | Capa (2) | Verificar valor está whitelist actual |
| Propuesta numeración nueva migration | Capa (3) | `ls migrations/sql/ \| tail -3` + `SELECT version FROM schema_migrations` |
| Propuesta scope tactical (X items) | Capa (2) + capa (3) | `grep -rnE "tipo=\"..\"" code/` antes de declarar scope |
| Audit DSC-G-008 v4 que toque schema | Las 3 capas | Pre-audit + post-audit |

### §4.2 Implementación sugerida (2 niveles)

**Nivel A — manual (P1, doctrinal):**
- Agregar al pre-flight Memento (Paso 0): comando bash que liste últimas 3 migrations en repo + últimas 3 en schema_migrations
- Si difieren → flag amarillo, requiere verificación explícita antes de acción magna
- Si idénticas → flag verde, proceder

**Nivel B — automatizado (P2, técnico):**
- Script `tools/_coherence_gate.py` con 3 modos:
  - `--mode=migration-numbering` → output: próximo número libre, lista de últimas 5 en cada lado
  - `--mode=schema-constraint TABLE COLUMN` → output: whitelist actual del CHECK + diff vs `grep` en código
  - `--mode=pre-action ACTION_TYPE` → output: gate pass/fail con detalle
- Integrar como pre-commit hook (Manus push) y como pre-flight Cowork
- Falla CI si gate falla

### §4.3 Gates por acción (tabla compacta)

```
ACCIÓN                              CAPA(S)   COMANDO BINARIO
─────────────────────────────────────────────────────────────────────
apply_migration nueva               (1)       ls migrations/sql/ | tail -3
                                              SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 3
INSERT con CHECK constraint         (2)       SELECT conname, pg_get_constraintdef(oid)
                                              FROM pg_constraint WHERE conname='<chk_name>'
Declarar scope tactical             (2)+(3)   grep -rnE "<pattern>" <dir>
                                              SELECT count(*) FROM <table> WHERE <constraint>
Audit DSC-G-008 v4                  (1)+(2)+(3)  Combinación de los anteriores
```

## §5 Por qué NO es duplicado de DSCs existentes

| DSC existente | Cubre | NO cubre |
|---|---|---|
| **DSC-S-012** anti-deriva migration numbering | Numeración secuencial sin gaps | Cross-validación contra `schema_migrations` aplicadas |
| **DSC-S-016** anti-fabricación | Claim sin Grep previo | Cross-validación DB vs repo vs planning |
| **DSC-G-008 v4** audit doctrine | Auditoría puntual de un PR | Detección preventiva pre-acción |
| **DSC-S-006 v1.1** RLS por defecto | Política RLS al crear tablas | Drift schema vs código vivo |

DSC-G-013 es **transversal** a los anteriores — opera como meta-gate ANTES de cualquier acción magna, no como audit POST.

## §6 Limitaciones declaradas (DSC-G-008 v3 §4)

| Id | Limitación | Mitigación |
|---|---|---|
| L_C1 | El gate puede dar falsos positivos si schema_migrations tiene drift histórico (caso H12 generalizado) | Modo `--ignore-historical-drift` para casos legacy verificados |
| L_C2 | Manual nivel A depende de disciplina del agente | Nivel B automatizado cierra el gap |
| L_C3 | El `grep` para detectar tipos vivos puede tener falsos negativos (constantes en strings dinámicos) | Combinar grep estático + tests de integración que inserten cada tipo |
| L_C4 | Cobertura inicial limitada a migrations + CHECK constraints | Expandir a FK constraints + indexes + RLS policies en v2 del DSC |
| L_C5 | Pre-flight Cowork ya tiene Paso 0 — agregar gate aumenta latencia turno 1 | Aceptable: 30-60s adicional vs costo de F21 estructural |

## §7 NO-CRUCE reglas duras

- ❌ NO modificar `apply_migration` de MCP supabase-monstruo (es externo)
- ❌ NO modificar core de DSC-S-012 / DSC-S-016 / DSC-G-008 (este DSC es nuevo, no override)
- ✅ SÍ agregar `tools/_coherence_gate.py` (nuevo, scope mínimo)
- ✅ SÍ extender CLAUDE.md Paso 0 con bash de Nivel A (regla dura)
- ✅ SÍ agregar pre-commit hook (Nivel B) cuando exista capacidad Manus E2

## §8 Convergencia 3 Sabios requerida

Spec DRAFT firmado por Cowork T2-A. Para canonización como DSC-G-013 vivo se requiere convergencia ≥2/3 de:

| Sabio | Rol | Validación esperada |
|---|---|---|
| **Perplexity Sonar T2-B** | Browsing tiempo real | Verificar si el patrón "DB↔Repo drift" es problema reconocido en literatura (best practices Postgres + schema migrations + multi-agent systems) |
| **GPT-5.5 Pro Pensamiento** | Razonamiento profundo | Auditar adversarialmente §3-§4: ¿el patrón estructural es real o artefacto de 3 casos coincidentes? ¿la solución propone over-engineering? |
| **Claude Opus 4.7 Pensamiento** | Metodología regla de tres | Validar §6 limitaciones: ¿están cubiertas todas las edge cases? ¿el gate aumenta latencia tolerable? |

Veredicto binario esperado: 🟢 ADELANTE / 🟡 CON CAVEAT / 🔴 RECHAZO.

## §9 Trayectoria post-firma

1. **HOY:** spec DRAFT pusheado + bridge a 3 Sabios (Cowork T2-A)
2. **HOY+1d:** veredictos convergencia
3. **HOY+1-2d:** si verde → firma T1 + canonización como DSC-G-013 vivo en `_INDEX.md`
4. **HOY+3-7d:** Nivel A pre-flight integration (CLAUDE.md Paso 0 extendido)
5. **HOY+7-14d:** Nivel B `_coherence_gate.py` implementation (owner: Manus E2 cuando tenga ciclo)
6. **T+14d:** primer reporte binario — ¿cuántos F21 prevenidos en el período de prueba?

## §10 Métricas de éxito binarias

| Métrica | Pre-DSC | Esperado post-DSC |
|---|---|---|
| Casos F#15 numeración off (instancias/semana) | 1+ observado | 0 |
| Drift repo↔schema_migrations detectado pre-acción | reactivo (post-mortem) | proactivo (pre-acción) |
| Tipos código vivos rechazados silentemente | 4 (H13 caso) | 0 |
| Sprints que requieren rebase post-bleed scope | 1+ observado (LA-FORJA D5.2) | 0 |

---

**Status:** `🟡 DRAFT — espera convergencia 3 Sabios + firma T1`
**Cowork T2-A firma DRAFT 2026-05-18 con evidencia binaria fresca (3 casos en 1 sesión).**

**Sources:**
- [Migration 0015 H12 fix](https://github.com/alfredogl1804/el-monstruo/blob/main/migrations/sql/0015_run_costs.sql)
- [Migration 0047 H13 fix](https://github.com/alfredogl1804/el-monstruo/blob/main/migrations/sql/0047_embrion_memoria_tipo_check_expand_vivos.sql)
- [Bridge H13 veredicto (F#15 declarado)](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/cowork_to_manus_HILO_EJECUTOR_2_H13_VEREDICTO_2026_05_17.md)
- DSC-S-012, DSC-S-016, DSC-G-008 v4 (hermanos doctrinales)
