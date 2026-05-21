# B8 v3 — INTEGRATION PLAN

**Fecha:** 2026-05-21
**Rama plan:** `control-tower/2026-05-21-batch-009-canary-r1-review`
**Rama fuente del código:** `control-tower/2026-05-21-batch-008-b8-v3` @ `0ac0a91`
**Estado:** `DRAFT — READY_FOR_T1_REVIEW`
**Tipo:** Plan de integración documental. **NO ejecutar hasta firma R1 + T1.**

---

## 1. Precondición dura

La integración a `main` queda **bloqueada** hasta cumplir todos los siguientes:

1. Plan R1 (`BATCH_009_CANARY_R1_REVIEW_PLAN.md`) firmado T1.
2. Auditor adversarial independiente designado y ejecutado.
3. Criterios `READY_FOR_R1` cumplidos (ver `CANARY_R1_CRITERIA.md` §1).
4. R1 PASS ≥ 95% con 0 critical failures, 0 secret leaks (ver §2 de criterios).
5. Audit DSC-G-008 v2 (6 gates: G1-G6) en verde sobre el PR de integración.
6. Firma T1 verbatim autorizando merge.

Si cualquiera falla → integración pospuesta, código permanece en rama lateral.

---

## 2. Archivos esperados a tocar en el PR de integración

| Archivo | Tipo de cambio | Origen |
|---|---|---|
| `kernel/anti_dory/b8_magna_classifier.py` | Modificación (~157 LOC añadidas, Layer 4 + Layer 5) | Batch 008 |
| `bridge/control_tower/2026-05-21/manus/MANUS_CANARY_R0_V3_REPORT.md` | Nuevo | Batch 008 |
| `bridge/control_tower/evidence/B8_V3/B8_V3_ALL_TESTS_junit.xml` | Nuevo | Batch 008 |
| `bridge/control_tower/evidence/CANARY/MANUS_CANARY_R0_V3_RESULTS.json` | Nuevo | Batch 008 |
| Tests adicionales adversariales R1 | Nuevo (si Batch 009 produce código de tests) | Batch 009/010 |
| Doc DSC (si se canoniza B8 v3 como decisión) | Nuevo opcional | Post firma T1 |

**Nota:** ningún cambio en `kernel/engine.py`, `kernel/embrion_loop.py` ni en `apps/mobile/`.

---

## 3. Política de feature flag

- **Flag:** `ANTI_DORY_B8_V3_ENABLED` (env var booleano).
- **Default:** `false` en el commit de integración.
- **Comportamiento flag=false:** `b8_magna_classifier` ejecuta sólo Layer 1-3 (B8 v2). Layer 4 + Layer 5 quedan latentes en código pero no se invocan.
- **Comportamiento flag=true:** se activan Layer 4 y Layer 5.
- **Activación en prod:** únicamente bajo firma T1 explícita post-R1.
- **Reversión:** flip flag a `false` en Railway env vars → comportamiento vuelve a B8 v2 sin necesidad de revert de código.

---

## 4. Matriz de tests requerida pre-merge

| Suite | Mínimo | Bloqueante |
|---|---|---|
| B8 v2 Original (41 tests) | 41/41 PASS con flag=false | Sí |
| B8 v2 Semantic (72 tests) | 72/72 PASS con flag=false | Sí |
| Anti-Dory full (118 tests) | 118/118 PASS con flag=false | Sí |
| B8 v3 Canary R0 (70 casos) | 70/70 PASS con flag=true | Sí |
| R1 adversarial set (≥ 100 casos) | ≥ 95% con 0 critical/secret leak con flag=true | Sí |
| Rollback test (flag off vs B8 v2 baseline) | Output idéntico en los 113 tests v2 | Sí |
| Linter / type check pipeline existente | Verde | Sí |

CI debe correr ambas configuraciones (flag on/off) automáticamente o vía parámetro de job.

---

## 5. Expectativas CI

- **Pipeline existente:** debe seguir verde con o sin v3 activo.
- **Legacy bypass:** se mantiene la política del PR #175 (legacy CI bypass) **únicamente** para módulos legacy ya cubiertos; **no se extiende** a `b8_magna_classifier.py`. Ese archivo debe pasar el pipeline estricto.
- **Sin secretos en CI logs.** Fixtures de R1 con secretos parafraseados o sintéticos; ninguna clave real.
- **Sin paid APIs invocadas en CI.** Tests offline únicamente.
- **JUnit:** publicar `B8_V3_ALL_TESTS_junit.xml` + JUnit del set R1 como artefactos de CI.

---

## 6. Migración / Supabase — postura

- **No hay migraciones nuevas** asociadas a B8 v3. El clasificador no toca DB.
- **No se ejecuta `apply_migration`** durante Batch 009 ni durante el merge.
- **Coherence Gate Nivel A (DSC-G-013 v0.1)** sólo aplica si en R1 emerge necesidad de constraint nuevo. Si emerge → bloquea merge hasta validación pre-acción explícita.
- **Validación read-only:** auditor R1 puede consultar `cowork_sesiones`, `embrion_memoria`, `schema_migrations` vía SELECT para verificar coherencia, **sin** INSERT/UPDATE/DELETE.
- **Anti-F22:** Cowork no pedirá a Alfredo correr SQL; cualquier consulta read-only la hace Cowork vía MCP Supabase con su acceso.

---

## 7. Plan de PR (cuando proceda, NO ahora)

1. Crear rama `integration/b8-v3` desde `main` actual.
2. Cherry-pick `0ac0a91` (Batch 008) sobre `integration/b8-v3`.
3. Añadir tests R1 adversariales producidos en Batch 010 (TBD).
4. Añadir guard de flag `ANTI_DORY_B8_V3_ENABLED` en el classifier.
5. Verde local de los 6 puntos de la matriz §4.
6. Audit DSC-G-008 v2 (G1-G6).
7. Abrir PR a `main` con descripción enlazando este plan + reporte R0 v3 + reporte R1.
8. Firma T1.
9. Merge.
10. Post-merge: flag permanece `false`. Activación en evento separado.

---

## 8. Rollback plan

| Escenario | Acción | Tiempo objetivo |
|---|---|---|
| Regresión detectada con flag=true | Flip `ANTI_DORY_B8_V3_ENABLED=false` en Railway | < 5 min |
| Defecto en código v2 introducido por refactor del merge | `git revert <merge_commit>` + redeploy | < 30 min |
| Migración accidental introducida | Bloquear merge en review; si pasó, revert + análisis Coherence Gate | < 60 min |
| Secreto filtrado en logs post-activación | Flip flag off + rotación de credenciales afectadas | inmediato + 1h |

---

## 9. Guardrails de este documento

- No PR creado.
- No code change en esta rama.
- No Supabase write.
- No deploy.
- Solo documentación.
