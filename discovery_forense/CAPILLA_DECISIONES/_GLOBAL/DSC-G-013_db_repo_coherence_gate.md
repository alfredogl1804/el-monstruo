---
dsc_id: DSC-G-013
version: v0.1
titulo: DB↔Repo Coherence Gate (Nivel A firmable + Nivel B experimental)
estado: 🟡 ESPERANDO FIRMA T1 — Nivel A solamente
autor_spec: Cowork T2-A
fecha_v0_1: 2026-05-18
ambito: _GLOBAL
hermanos: DSC-S-012 (anti-deriva migration numbering), DSC-S-016 (anti-fabricación), DSC-G-008 v4 (audit doctrine)
historial:
  - v1 DRAFT 2026-05-18 — archived a _archived/DSC-G-013_v1_pre_sabios_2026_05_18.md
  - v0.1 2026-05-18 — post-convergencia 3 Sabios CON CAVEAT (refactor estructural)
veredictos_sabios:
  - Opus 4.7 → 🟡 CON CAVEAT (3 ajustes técnicos)
  - Perplexity Sonar T2-B → 🟡 CON CAVEAT (Atlas/Flyway/Liquibase referencia)
  - GPT-5.5 Pro → 🟡 DEGRADADO (re-hipótesis + Nivel B → experimento + 2 L nuevas)
caveat_titulo: "Guardrail pre-acción contra drift DB↔Repo↔Código. No patrón universal probado."
---

# DSC-G-013 v0.1 — DB↔Repo Coherence Gate

> ⚠️ **Caveat doctrinal explícito:** Guardrail pre-acción contra familia de drift DB↔Repo↔Código. **No es patrón universal probado** — refactorizado post-adversarial 3 Sabios. Nivel A firmable; Nivel B en experimento T+14d con métricas binarias.

## §1 Hipótesis degradada (post-GPT-5.5)

**De v1:** "Mismo problema en 3 capas estructurales (repo↔schema_migrations, código↔schema, planning↔reality)"

**A v0.1:** **"Familia de drift pre-acción entre DB, repo, schema y código, con posible síntoma adicional de modelo mental desactualizado."**

Razón refactor: F#15 (numeración Manus E2 off by 10) NO es evidencia estructural equivalente a H12/H13. Es **síntoma operativo**, no drift DB↔Repo. Honestidad doctrinal: 2 capas evidenciadas + 1 capa síntoma observado.

## §2 Evidencia magna binaria

### §2.1 H12 — `run_costs` missing repo↔schema_migrations

Migration 0015 existía en `migrations/sql/` repo pero NO registrada en `supabase_migrations.schema_migrations`. Apply prod via MCP pendiente. Investigación derivada: **drift sistémico** — sólo 12 migrations registradas vs ~44 en repo. **Fuerte evidencia capa repo↔schema_migrations.**

Fix: [migration 0015 H12 fix](https://github.com/alfredogl1804/el-monstruo/blob/main/migrations/sql/0015_run_costs.sql).

### §2.2 H13 — 4 tipos código↔CHECK constraint rechazados silente

`grep -nE 'tipo="' kernel/embrion_loop.py` reveló 4 tipos vivos. `SELECT COUNT(*) WHERE tipo IN (...)` = 0 filas. Significa: durante meses, escrituras rechazadas sin alerta. `contribucion_sabio` (importancia=9) = F21 estructural mayor. **Fuerte evidencia capa código↔schema.**

Fix: [migration 0047 H13 expand](https://github.com/alfredogl1804/el-monstruo/blob/main/migrations/sql/0047_embrion_memoria_tipo_check_expand_vivos.sql).

### §2.3 Caveat F#15 — síntoma operativo (NO evidencia equivalente)

Manus E2 asumió numeración 0037 disponible — estaba ocupada (off by 10). Es **modelo mental desactualizado de un agente en una sesión**, no drift DB↔Repo. **Síntoma operativo observado**, no tercera capa estructural.

Detalle: [bridge H13 veredicto §3](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/cowork_to_manus_HILO_EJECUTOR_2_H13_VEREDICTO_2026_05_17.md).

## §3 Nivel A — firmable T1 hoy

**Pre-flight check obligatorio antes de las siguientes acciones magnas:**

| Acción magna | Check Nivel A | Comando binario |
|---|---|---|
| `apply_migration` nueva via MCP | Siguiente número libre coherente | `ls migrations/sql/ \| tail -3` + `SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 3` |
| `INSERT` con CHECK constraint | Valor está en whitelist actual | `SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='<chk>'` |
| `DROP/ALTER TABLE` directo prod | **Magna destructiva — gate obligatorio** | Capa 1 + capa 2 + branch/HEAD/PR awareness |
| Declarar scope tactical (N items) | Coherencia código↔schema | `grep -rnE "<pattern>"` + `SELECT count(*)` |

**Acción si check falla:** flag amarillo → verificación explícita pre-acción. Si confirma incoherencia → **bloquear acción** hasta resolver.

**Latencia Nivel A:** **+2-5s** por turno (verificado contra Paso 0 Pre-flight existente). Costo aceptable vs F21 estructural H13 (rechazo silente por meses).

## §4 Nivel B — EXPERIMENTO T+14D (NO canoniza ahora)

Spec movido a [`EXPERIMENTOS_T14D/DSC-G-013_nivel_B_experimento.md`](../../../EXPERIMENTOS_T14D/DSC-G-013_nivel_B_experimento.md).

Métricas obligatorias durante el experimento:
- Falsos positivos del gate (count/semana)
- Errores prevenidos vs detectados post-acción
- Tiempo agregado real por turno
- Frecuencia de drift detectado pre-acción
- Cobertura multi-branch (L_C6)
- Hotfix manual DDL detectado (L_C7)

Si experimento verde T+14d → canonizar Nivel B en v0.2.

## §5 Por qué NO es duplicado de DSCs existentes

| DSC | Cubre | NO cubre |
|---|---|---|
| DSC-S-012 | Numeración secuencial repo | Cross-validación contra schema_migrations |
| DSC-S-016 | Claim sin Grep previo | Cross-validación DB vs repo vs planning |
| DSC-G-008 v4 | Audit post-PR | Detección preventiva pre-acción |
| DSC-S-006 v1.1 | RLS al crear tablas | Drift schema vs código vivo |

DSC-G-013 es **transversal/preventivo**, no override de los hermanos.

## §6 Limitaciones declaradas (7 — DSC-G-008 v3 §4)

| Id | Limitación | Mitigación |
|---|---|---|
| L_C1 | Falsos positivos si schema_migrations tiene drift histórico (H12 generalizado) | `--ignore-historical-drift` para legacy verificado |
| L_C2 | Nivel A depende de disciplina del agente | Nivel B (experimento T+14d) cierra el gap |
| L_C3 | `grep` puede tener falsos negativos en strings dinámicos (f-strings, dict updates, lookups) | **Pipeline test integración** que inserte cada tipo whitelist (no aspiracional — operacional con runner asignado) |
| L_C4 | Cobertura limitada a migrations + CHECK | Expandir FK/indexes/RLS en v0.2 post-experimento |
| L_C5 | Latencia +2-5s Nivel A / +30-60s Nivel B | Tolerable: costo H12+H13 fue días debugging |
| **L_C6** | **Multi-branch / PR divergence** — gate puede pasar en main y fallar en branch activa. Dos agentes pueden crear migrations paralelas y colisionar al merge. | Comparar base branch + HEAD + PR abierto + remote en check pre-acción |
| **L_C7** | **DB state fuera de schema_migrations** — Supabase puede tener hotfix manual, trigger, function, policy, enum, extension o constraint aplicado fuera de migrations. Gate puede creer coherencia falsamente. | `liquibase diff --format=json` o equivalente; tracking explícito de DDL out-of-band |

## §7 NO-CRUCE reglas duras

- ❌ NO modificar `apply_migration` de MCP supabase-monstruo (externo)
- ❌ NO modificar core de DSC-S-012 / DSC-S-016 / DSC-G-008 (este DSC es nuevo, no override)
- ✅ SÍ extender CLAUDE.md Paso 0 Pre-flight Memento con comandos Nivel A
- ✅ SÍ documentar L_C6 + L_C7 como edge cases conocidos
- ✅ SÍ referenciar herramientas industria (Atlas, Flyway, Liquibase) como **referencia comparada**, sin commitment de adopción

## §8 Referencia industria (Perplexity — informativa, no adopt)

Herramientas que cubren porciones del problema:
- **Atlas** — `migrate/lint`, `migrate/apply`, `migrate/test`, `migrate/autorebase` (cubre L_C6) ([atlasgo.io](https://atlasgo.io/integrations/github-actions))
- **Flyway** — `check -drift`, snapshots inmutables, rollback workflow ([redgate flyway](https://www.red-gate.com/hub/product-learning/flyway/how-to-detect-database-drift-using-flyway-snapshots/))
- **Liquibase** — `diff --format=json`, drift reports ([liquibase blog](https://www.liquibase.com/blog/database-drift))

**Decisión Cowork:** mantener custom Nivel A doctrinal (scope mínimo). **Adoptar Atlas/Flyway = sprint separado** con audit propio (NO incluido en este DSC).

---

**Status:** `🟡 ESPERANDO FIRMA T1 — Nivel A solamente`
**Cowork T2-A firma v0.1 con caveat doctrinal explícito** bajo autorización T1 "procede x" verbatim 2026-05-18.

**Sources:**
- v1 archivado: [`_archived/DSC-G-013_v1_pre_sabios_2026_05_18.md`](_archived/DSC-G-013_v1_pre_sabios_2026_05_18.md)
- Nivel B experimento: [`EXPERIMENTOS_T14D/DSC-G-013_nivel_B_experimento.md`](../../../EXPERIMENTOS_T14D/DSC-G-013_nivel_B_experimento.md)
- Veredictos 3 Sabios: [`bridge/veredictos_dsc_g_013/`](../../../bridge/veredictos_dsc_g_013/)
- Evidencia magna H12: migration 0015
- Evidencia magna H13: migration 0047
- Caveat F#15 síntoma: bridge H13 veredicto §3
