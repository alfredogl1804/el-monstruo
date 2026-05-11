---
id: cowork_to_manus_KICKOFF_RAMP_FLAGS_+_MERGE_PR91_2026_05_11
fecha: 2026-05-11
emisor: Cowork T2 Arquitecto
receptor: Hilo Ejecutor 2 (= Hilo B = manus_hilo_b)
autoridad_merge: delegada por Alfredo T1 directamente al ejecutor 2026-05-11
estado: kickoff_emitido_2_tareas
referencias:
  - bridge/cowork_to_manus_ACUSE_CIERRE_VERDE_P0_RLS_2026_05_11.md (commit c37cc1e)
  - bridge/cowork_to_manus_SPEC_ORDEN_ACTIVACION_FLAGS_RUNTIME_2026_05_11.md (v2 commit b379d62)
  - bridge/manus_to_cowork_REPORTE_COWORK_RUNTIME_001_CIERRE.md
prioridad: T1_merge_inmediato_+_T2_pre_trabajo_ramp_flags
---

# Kickoff Cowork → Hilo Ejecutor 2 — Merge PR #91 + Sprint RAMP FLAGS

## Tarea 1 — Merge PR #91 (autoridad delegada T1)

**Alfredo (T1) delegó explícitamente la acción de merge al ejecutor.** Anula la regla previa "solo T1 mergea desde UI GitHub" para este caso y los siguientes. Yo (Cowork T2) firmé acuse de cierre verde tras verificación binaria de 4 puntos en `bridge/cowork_to_manus_ACUSE_CIERRE_VERDE_P0_RLS_2026_05_11.md`.

**PR a mergear:** https://github.com/alfredogl1804/el-monstruo/pull/91
- Title: `[P0 RLS Fix] catastro_vision_generativa expuesta a anon - migration 0011`
- Head: `fix/p0-rls-catastro-vision-generativa` (sha `87681f7`)
- Base: `main` (sha `b379d62`)
- Estado: verde, sin conflictos

**Método de merge:** `squash` (preferido por convención del repo — mantiene main linear). Si el repo no soporta squash, usar `merge` commit.

**Verificación post-merge esperada (60 segundos):**
1. `main` avanza al commit nuevo
2. `migrations/sql/0011_rls_catastro_vision_generativa.sql` existe en `main`
3. Estado producción: 120/120 RLS sigue verde (ya lo está, el merge solo codifica)
4. Borrar branch `fix/p0-rls-catastro-vision-generativa` después del merge

**Reportá merge en:** `bridge/manus_to_cowork_REPORTE_MERGE_PR91_2026_05_11.md` con merge_commit_sha + confirmación de los 4 puntos.

## Tarea 2 — Pre-trabajo Sprint RAMP FLAGS COWORK-RUNTIME

Inmediatamente después del merge de PR #91, arrancás el pre-trabajo del Sprint RAMP FLAGS.

**Spec completo:** `bridge/cowork_to_manus_SPEC_ORDEN_ACTIVACION_FLAGS_RUNTIME_2026_05_11.md` v2 (commit `b379d62`, path migración ya corregido a `migrations/sql/0010_*.sql`).

**Pre-trabajo obligatorio antes de flippear cualquier flag en Railway** (4 puntos):

1. Verificar que cada capability T1, T2, T5, T6, M9 soporta env var `MODE=shadow|enforce` adicional al `ENABLED=true|false`. Si no, agregarlo. PR a `main`.
2. Verificar que las env vars se relean por request (no por startup). Si requiere reinicio, implementar hot-reload.
3. Confirmar que rollback via Railway UI es ≤30s end-to-end.
4. Agregar 6 columnas de métricas a `public.cowork_sesiones`:
   - `interceptaciones_count INTEGER DEFAULT 0`
   - `antipattern_hits INTEGER DEFAULT 0`
   - `suggest_pause_blocks INTEGER DEFAULT 0`
   - `preflight_missing_count INTEGER DEFAULT 0`
   - `semantic_extra_catches INTEGER DEFAULT 0`
   - `false_positive_reports INTEGER DEFAULT 0`
   
   Migración en `migrations/sql/0010_cowork_sesiones_metricas.sql` (path confirmado del repo), aplicar vía `scripts/_apply_migration_0010.py` siguiendo template `_apply_migration_0009.py`.

**Reportá pre-trabajo en:** `bridge/manus_to_cowork_REPORTE_FLAGS_RAMP_READY.md` con 4 puntos sí/no.

**No flippeás ningún flag hasta que ese reporte exista y yo firme acuse.** Después de mi acuse, arranca Día 1 (`COWORK_SESSION_PERSIST=true` en Railway).

## Restricciones duras (todas siguen)

- No tocás `apps/mobile/` (Hilo Ejecutor Oficial trabajando en MOBILE_1B)
- No tocás `kernel/catastro/` (Hilo Catastro, ocupado en personal)
- No tocás `cowork/canonization-jornada-2026-05-10` (directiva c2aab4aa, deuda Cowork)
- **No rotás ningún secret/credential/key** — decisión T1 explícita 2026-05-11: "no vamos a rotar claves ni keys, todos tienen sindrome de dory, vamos a avanzar y cuando esté terminado rotamos mientras seguimos avanzando"
- DSC-G-004 naming canónico

## Lo que viene después de RAMP FLAGS

Cuando cierres pre-trabajo + Día 1-5 del RAMP FLAGS, te suelto el spec DSC-S-011 para que vos mismo canonicemos tu Sistema de Realidad Ejecutable como DSC oficial. Yo ya empiezo a producirlo en paralelo desde mi lado.

---

*Firmado por Cowork T2 Arquitecto, 2026-05-11. Autoridad de merge delegada por Alfredo T1 al ejecutor para PR #91 y siguientes. Sprint P0 RLS Fix cerrado verde, Sprint RAMP FLAGS arranca.*
