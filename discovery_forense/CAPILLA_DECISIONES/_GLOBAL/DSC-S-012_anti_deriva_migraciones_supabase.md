---
id: DSC-S-012
proyecto: GLOBAL
tipo: restriccion_dura
titulo: "Prohibido aplicar migraciones SQL a Supabase prod sin PR previo a main. Toda migración aplicada inadvertidamente requiere PR retroactivo del .sql con marca [DERIVA-RESUELTA] en el body del PR."
estado: firme
fecha: 2026-05-11
fecha_firma_T1: 2026-05-11
autor_borrador: Cowork T2 (Sprint SPECS-FIRMA-001 ampliado bajo autorización T1 directa)
autor_propuesta_original: Hilo Ejecutor 1 (durante investigación del gap Migration 0010, PR #95)
autorización_T1: Alfredo, firmada explícitamente en chat 2026-05-11
fuentes:
  - bridge/manus_to_cowork_RESOLUCION_GAP_MIGRATION_0010_2026_05_11.md
  - PR #95 (commit a0f4b1cb) body — sección "Hallazgos laterales"
  - audit memory/cowork/audits/AUDIT_4_CAPAS_3A_2026_05_10.md §2 H2 (audit_middleware.py fuente perdida — patrón similar de deriva)
  - audit memory/cowork/audits/CARTOGRAFIA_1B_KERNEL_NUCLEO_2026_05_10.md §3.10 (.pyc huérfano)
cruza_con: [DSC-S-006 v1.1, DSC-G-008 v2, DSC-G-017, DSC-S-002, DSC-S-007]
contrato_ejecutable_propuesto: tools/_check_migration_drift.py + pre-commit hook + workflow CI
contrato_ejecutable_estado: pendiente — sprint Cowork ~2-3h en próxima sesión (sin esto el DSC degrada a aspirational en 30 días per DSC-G-017)
---

# DSC-S-012 — Anti-deriva migraciones SQL ↔ Supabase producción

## Decisión

**Ninguna migración SQL (`migrations/sql/*.sql`) se aplica a Supabase producción sin estar primero pusheada a la rama `main` del repo.**

Reglas duras derivadas:

1. **Orden obligatorio:** crear archivo `.sql` en feature branch → PR a `main` → review + audit DSC-G-008 v2 → merge a `main` → ejecutar `scripts/_apply_migration_NNNN.py` o `sb_sql.py` contra producción.

2. **Migraciones aplicadas inadvertidamente requieren PR retroactivo** con:
   - El archivo `.sql` añadido a `migrations/sql/` en el mismo número que se aplicó (o renumerado si hay colisión).
   - Header del archivo con marca verbatim `-- [DERIVA-RESUELTA] aplicada en prod el YYYY-MM-DD antes de canonización en main`.
   - Body del PR con sección verbatim `## Deriva resuelta` declarando: (a) qué objeto SQL ya está en prod, (b) cuándo se aplicó, (c) por qué se aplicó antes del PR, (d) cómo asegurar que re-aplicar sea no-op (idempotencia obligatoria via `CREATE TABLE IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`, `DROP TRIGGER IF EXISTS ... ; CREATE TRIGGER ...`).

3. **Cowork mergea estos PRs retroactivos bajo regla evolucionada 2026-05-11** (audit DSC-G-008 v2 verde + autorización T1) — porque revertir la deriva no es opción (la DB ya tiene los objetos, eliminarlos crearía deriva inversa).

4. **Prohibido `sb_sql.py` / `psql` / Management API directo desde una feature branch sin merge previo**, salvo excepción declarada por Alfredo en chat con sello horario explícito.

5. **Slots numéricos de migración son irrevocables una vez ocupados en main.** Si dos branches de feature usan el mismo slot N, el que llega a `main` primero gana el número; el otro renumera al siguiente slot libre (DSC-G-017 enforcement aplicado a numeración de migraciones).

---

## Por qué

### Evidencia binaria de la necesidad (verificada vía Supabase Management API el 2026-05-11)

**3 derivas DB↔repo detectadas simultáneamente** durante investigación del gap Migration 0010 por Hilo Ejecutor 1:

| Deriva | Objeto en Supabase prod | Archivo en main | Cuándo se aplicó |
|---|---|---|---|
| 1 | Tabla `kernel_audit_log` + 3 triggers (`kal_no_update`, `kal_no_delete`, `kal_no_truncate`) | ❌ NO existe (archivo solo en branch `sprint/s-003-b-audit-middleware-pentest` no mergeada) | Durante Sprint S-003.B audit middleware, sin completar merge |
| 2 | Tabla `embrion_inbox` (19 columnas + RLS + 3 CHECK constraints) | ✅ Resuelta hoy via merge PR #94 (commit `aaf4b298` 2026-05-11 15:27 UTC) | Durante implementación del Sprint EMBRION-NEEDS-002 T5, antes del PR. Deriva CERRADA con la firma de este DSC. |
| 3 | Tabla `cowork_sesiones` SIN columnas KPI (`interceptaciones_count`, etc.) | ✅ Archivo en main via PR #95 (commit `a0f4b1cb`) — falta aplicar | Caso INVERSO: archivo en repo, NO en DB. Hilo Ejecutor 1 ejecuta `scripts/_apply_migration_0010.py` post-merge. |

**Patrón paralelo (no SQL pero similar):** `audit_middleware.py` con fuente perdida (`__pycache__/.pyc` huérfano sin `.py` correspondiente — audit cartografía 1B §3.10). El bytecode existe en producción Railway pero el código fuente no llegó a main. Mismo antipatrón estructural: ejecución desincronizada del repo.

### Costo de la deriva

1. **Replay imposible:** si un nuevo ambiente intenta aplicar las migraciones desde main (ej. staging fresh, recovery de DR), `kernel_audit_log` no existiría porque su migración no está en main (PR S-003.B pendiente).

2. **Síndrome-Dory operacional canonizado:** un hilo futuro (humano o agente) que mire `migrations/sql/` en main NO sabría que `kernel_audit_log` existe en prod. Si necesita modificarla, podría crear migración duplicada → colisión → corrupción de datos.

3. **DSC-G-008 v2 violado:** "validar codebase antes de specs" se vuelve imposible cuando la DB y el repo divergen — la fuente de verdad sobre qué existe en prod queda solo en la mente del ejecutor que aplicó la migración.

4. **Re-elaboración costosa:** cada deriva detectada requiere investigación de 30-60 min por audit Cowork (medido empíricamente en PR #95 — Hilo Ejecutor 1 invirtió tiempo magna en triangular las 3 derivas).

### Por qué este DSC ahora (no antes)

Las 3 derivas son **convergencia evidencial de un patrón sistémico que ya operaba**. Sin el PR #95 que detectó las 3 simultáneamente, cada deriva habría sido tratada como caso aislado. La verificación binaria via Management API del 2026-05-11 reveló que NO es caso aislado — es modus operandi peligroso del proyecto.

DSC-S-012 canoniza retroactivamente la regla que las 3 derivas violaban, y previene que futuras derivas se acumulen.

---

## Implicaciones

### Para Manus Ejecutor (T3)

- Antes de aplicar cualquier migración: confirmar que el archivo `.sql` está en `main` con `git log --oneline -1 origin/main -- migrations/sql/NNNN_*.sql`. Si no aparece, NO aplicar.
- Si por urgencia operacional se aplicó antes del merge (ej. P0 fix que no puede esperar review), reportar inmediatamente al bridge con `manus_to_cowork_DERIVA_APLICADA_NNNN_<fecha>.md` declarando: cuándo, por qué, idempotencia garantizada, PR de resolución preparado.
- Todas las migraciones nuevas deben ser **idempotentes por diseño** (DSC-S-006 v1.1 ya lo exige para RLS; este DSC lo extiende a CREATE TABLE, ALTER COLUMN, CREATE TRIGGER).

### Para Cowork (T2)

- Audit DSC-G-008 v2 sobre PRs de migraciones SQL **debe incluir verificación binaria** (`SELECT FROM information_schema.tables` vía MCP Supabase) de si el objeto ya existe en prod antes del merge.
- Si existe deriva detectada, exigir PR retroactivo con marca `[DERIVA-RESUELTA]` y firma del ejecutor admitiendo el orden incorrecto.
- Cowork NO mergea PRs de migración SQL sin pre-flight de "objeto ya en prod sí/no" + análisis de idempotencia.

### Para Alfredo (T1)

- Excepciones a esta regla las firma Alfredo explícitamente en chat con sello horario.
- Una excepción aceptable: P0 critical fix donde esperar al PR introduce riesgo magna (ej. ataque activo, datos corruptos). Alfredo decide caso por caso.

### Para la doctrina

- Refuerza DSC-S-006 v1.1 (RLS por defecto) — extiende la idempotencia desde RLS a todos los objetos SQL.
- Refuerza DSC-G-017 (DSC-as-Contract) — los slots numéricos de migración son contrato; ocuparlos sin pushear viola el contrato.
- Crea precedente para futuros sprints S- (security/sistema) que canonicen prohibiciones derivadas de derivas detectadas binariamente.

---

## Contrato ejecutable propuesto

Para que este DSC pase de `aspiracional` (estado actual en `_dsc_contracts_index.yaml`) a `enforced` con contrato adjunto (DSC-G-017 requirement), se propone:

### 1. `tools/_check_migration_drift.py` (script de detección)

Función: para cada archivo `migrations/sql/*.sql` en main, ejecutar `SELECT to_regclass('public.<tabla_implicada>')` vía Supabase. Si el archivo es CREATE TABLE pero la tabla NO existe en prod → drift inverso (repo > DB, pendiente aplicar). Si la tabla existe pero el archivo NO está en main → drift original (DB > repo, deriva).

Output: JSON con tabla de drift detectado por archivo.

### 2. Pre-commit hook `migration-drift-check`

Hook nuevo en `.pre-commit-config.yaml` que corre `tools/_check_migration_drift.py --strict` antes de cada commit que toque `migrations/sql/`. Si detecta drift activo NO declarado con `[DERIVA-RESUELTA]`, bloquea el commit.

### 3. Workflow CI semanal `migration-drift-audit.yml`

Cron lunes 12:00 UTC (alineado con `rls-audit-weekly`). Corre `_check_migration_drift.py --json`, abre issue automático si detecta drift no resuelto. Linker al DSC-S-012 en el body del issue.

### 4. Migraciones de canonización retroactiva pendientes

Identificadas durante la sesión del 2026-05-11:

- `migrations/sql/0013_kernel_audit_log.sql` (renumerado desde 0009 en branch S-003.B — pendiente PR del Hilo Ejecutor 2)
- `migrations/sql/0014_kernel_audit_log_truncate_guard.sql` (renumerado desde 0010 — pendiente PR del Hilo Ejecutor 2)
- ~~`migrations/sql/0012_embrion_inbox.sql`~~ — ✅ deriva resuelta vía merge PR #94 (commit `aaf4b298`).
- ~~`migrations/sql/0010_cowork_sesiones_metricas.sql`~~ — ✅ deriva inversa resuelta: archivo en main via PR #95. Aplicación post-merge pendiente Hilo Ejecutor 1.

Los 2 primeros bloquean cumplimiento total de DSC-S-012 hasta que Hilo Ejecutor 2 renumere y abra PR. El aviso ya está enviado en `bridge/manus_to_ejecutor2_RENUMERAR_SPRINT_S003B_2026_05_11.md`.

---

## Estado de validación

**estado:** `firme` — Alfredo firmó como T1 el 2026-05-11.

**Estado en `_dsc_contracts_index.yaml`:** `aspirational` con reason — el contrato ejecutable §1-3 no está implementado todavía. Pendiente sprint Cowork de ~2-3h para crear `tools/_check_migration_drift.py` + pre-commit hook + workflow CI. **Sin contrato ejecutable adjunto en 30 días, el DSC degrada formalmente a aspirational permanente (DSC-G-017 enforcement).**

**Severidad si se viola:** **alta**. Cada deriva nueva agrega Síndrome-Dory operacional al proyecto. Patrón sistémico ya documentado en 3 casos — repetirlo es F2 conocido (afirmar sin verificar) o F22 (pedirle a Alfredo lo que el ejecutor SÍ puede hacer: hacer PR primero antes de aplicar).

---

## Trazabilidad

- **Origen:** Hilo Ejecutor 1 sugirió canonización durante PR #95 (resolución del gap Migration 0010) tras detectar 3 derivas DB↔repo simultáneas.
- **Audits que respaldan:** cartografía 1B §3.10 (audit_middleware.py fuente perdida — patrón paralelo no-SQL), audit 3A §2 H2 (riesgo de Síndrome-Dory operacional en redeploy).
- **Sprint que materializa contrato ejecutable:** Cowork puro de ~2-3h (tools/script + pre-commit hook + workflow CI). Pendiente asignación a próxima sesión Cowork.
- **DSCs derivados potenciales:** DSC-S-013 candidato — "Anti-deriva código compilado vs fuente" (extender principio del .py vs .pyc detectado en audit 1B §3.10).

---

## Para Alfredo — qué firmaste el 2026-05-11

Firmaste:
1. ✅ Que la regla del §"Decisión" aplica desde el momento de tu firma a futuro.
2. ✅ Que las derivas pre-existentes (las 3 detectadas el 2026-05-11) requieren resolución vía PR retroactivo, no se ignoran. 2 ya resueltas (PR #94 y PR #95), 1 pendiente (Ejecutor 2 renumeración).
3. ✅ Que Cowork audita PRs de migración SQL con verificación binaria contra Supabase antes de mergear.
4. ✅ Que excepciones requieren tu firma explícita en chat con sello horario.
5. ✅ Que el contrato ejecutable propuesto §1-3 se implementará en próximos 30 días (sin esto, DSC degrada a aspirational permanente per DSC-G-017).

**NO firmaste todavía:**
- El sprint de implementación del contrato ejecutable §1-3 — ese sprint queda separado y se levanta como Cowork puro próximo.
- La canonización retroactiva de las 2 migraciones pendientes (0013 + 0014 de S-003.B) — esas las firma Hilo Ejecutor 2 cuando abra su PR renumerado.

---

**estado:** firme — Alfredo firmó como T1 el 2026-05-11. Canonizado en `_INDEX` de Capilla y `_dsc_contracts_index.yaml` con status `aspirational` hasta que el contrato ejecutable §1-3 esté implementado (deadline DSC-G-017: 30 días = 2026-06-10).
