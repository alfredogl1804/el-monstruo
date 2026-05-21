# BATCH 009 — CANARY R1 REVIEW PLAN

**Fecha:** 2026-05-21
**Rama:** `control-tower/2026-05-21-batch-009-canary-r1-review`
**Origen:** off `main` @ `b11254f` (post merge Batch 005 + B8 v2)
**Estado:** `DRAFT — READY_FOR_T1_REVIEW`
**Autor:** Cowork T2 (Arquitecto)
**Tipo:** Documentación / preparación. **NO ejecución, NO deploy, NO writes prod.**

---

## 1. Resumen de evidencia Batch 008 (B8 v3)

Batch 008 vive en rama lateral `control-tower/2026-05-21-batch-008-b8-v3` @ commit `0ac0a91`. **No mergeado a main.**

| Suite | Tests | Resultado |
|---|---|---|
| B8 v2 Original (Exact/Keywords) | 41 | **41/41 PASS** |
| B8 v2 Semantic (Regex) | 72 | **72/72 PASS** |
| Anti-Dory Full Suite | 118 | **118/118 PASS** |
| **Regression total** | **231** | **231/231 PASS** |
| Manus Canary R0 (70 casos) | 70 | **70/70 PASS (100%)** |

Cambios en `kernel/anti_dory/b8_magna_classifier.py`:
- **Layer 4 — Action Semantics:** tipos de acción inherentemente peligrosos (deploy, drop_table, activate_phase…) → `MAGNA` por defecto.
- **Layer 5 — Context-Aware Heuristics:** detección estructural de asunción de estado viejo, memoria falsa, pérdida de contexto, side effects ocultos, exposición de secretos.

Evidencia primaria:
- Reporte: `bridge/control_tower/2026-05-21/manus/MANUS_CANARY_R0_V3_REPORT.md`
- JSON 70 casos: `bridge/control_tower/evidence/CANARY/MANUS_CANARY_R0_V3_RESULTS.json`
- JUnit: `bridge/control_tower/evidence/B8_V3/B8_V3_ALL_TESTS_junit.xml`

**Veredicto Manus firmado:** `READY_FOR_CANARY_R1_REVIEW`.

---

## 2. Por qué esto NO es `DORY_DEAD`

Un veredicto `DORY_DEAD` cierra estructuralmente el Síndrome Dory (Objetivo Maestro 9 / Capa 8 Memento). Batch 008 entrega un canary **interno acotado**, no la prueba completa. Razones binarias para mantener el caso abierto:

1. **R0 ≠ R1.** R0 mide 70 casos curados por Manus contra una clasificación implementada por el mismo lote. Riesgo de fuga: heurísticas tuneadas al set. R1 debe traer casos adversariales independientes.
2. **No hay DORY_BENCH_1000 / CVDS aplicado a B8 v3.** Falta evidencia de escala y de un Cross-Verifier Diff Scorer ≥ 0.95 (o equivalente declarado) contra v3.
3. **No hay restore/rollback test.** El kernel del clasificador cambió ~157 líneas; no se ha probado un escenario de regresión con flag off.
4. **No hay auditoría adversarial T2/T3 independiente** sobre las 5 capas. Auto-validación = riesgo F16 (auto-confirmación) si no se contrasta.
5. **No hay merge a `main` ni firma T1 sobre integración.** El veredicto del autor del cambio no canoniza el cierre del Objetivo 9.
6. **No hay observabilidad declarada en runtime.** B8 v3 vive en sandbox; sin métricas y alertas de classifier en kernel productivo, "Dory muerto" sería F21 (confiar en doc sin realidad fresca).

**Por tanto:** Batch 008 → `READY_FOR_CANARY_R1_REVIEW`. Sólo R1 verde + criterios de §4 de `CANARY_R1_CRITERIA.md` pueden mover el estado a `DORY_DEAD_CANDIDATE`, y sólo firma T1 cierra el caso.

---

## 3. Objetivos del R1 Review (Batch 009)

### 3.1 Adversarial audit
- Revisión línea por línea de Layer 4 y Layer 5 en `kernel/anti_dory/b8_magna_classifier.py` con foco en falsos negativos.
- Generar **≥ 20 casos adversariales nuevos** no vistos por Manus: prompts ofuscados, sinónimos no canónicos, acciones encadenadas, side effects diferidos, secretos parafraseados.
- Documentar al menos 3 hipótesis de bypass y resultado empírico contra v3.

### 3.2 Merge readiness
- Confirmar que el diff de B8 v3 se puede aplicar a `main` sin colisión semántica con Batch 005 / B8 v2 ya mergeado.
- Listar archivos tocados y diff esperado (ver `B8_V3_INTEGRATION_PLAN.md`).
- Validar política CI: tests adicionales no rompen pipeline ni dependen de credenciales/secretos.

### 3.3 Rollback strategy
- Definir cómo desactivar B8 v3 en caliente:
  - Vía feature flag (default off propuesto hasta firma T1).
  - Vía revert atómico del commit de integración (un solo commit limpio).
- Test de rollback: con flag off, comportamiento idéntico a B8 v2 en los 113 tests previos.

### 3.4 Feature flag constraints
- Flag propuesto: `ANTI_DORY_B8_V3_ENABLED` (env var, default `false`).
- Mientras flag = `false`, kernel ejecuta B8 v2 sin cambio.
- Activación requiere: firma T1 + evidencia R1 + audit DSC-G-008 v2 verde.

### 3.5 Observabilidad mínima requerida
- Métrica de tasa MAGNA vs STANDARD por capa (4 y 5) en logs.
- Conteo de DENY emitidos por Authority Matrix B9 atribuibles a v3.
- Alerta si tasa MAGNA cae > 30% día/día post activación (señal de regresión silenciosa).
- Logs estructurados sin payload sensible (no echo de prompts con secretos).

### 3.6 Failure thresholds
Ver `CANARY_R1_CRITERIA.md` §1-3 para umbrales binarios. Resumen:
- R1 PASS: ≥ 95% de casos R1, 0 critical failures, 0 secret leaks.
- BLOCK_R1: cualquier falso negativo en categoría "No Secrets" o "No Side Effects".
- DORY_DEAD candidate: ver §4 de criterios.

---

## 4. No-Go list (explícita)

Durante Batch 009 **NO se debe**, bajo ninguna interpretación:

1. **NO mergear B8 v3 a `main`.** Sólo plan documental.
2. **NO abrir PR de integración todavía.** PR es paso post-firma R1.
3. **NO activar Fase 1 (global rollout) bajo ningún flag.**
4. **NO declarar `DORY_DEAD` ni `DORY_DEAD_CANDIDATE`** desde este batch.
5. **NO activar Guardian de Objetivos sobre el cierre del Objetivo 9.**
6. **NO ejecutar writes a Supabase prod.** Sólo lectura para validación si se necesita; ninguna mutación.
7. **NO correr deploy a Railway de kernel con v3.** Sandbox local únicamente.
8. **NO exponer secretos en evidencia.** Cualquier fixture con secret debe estar redactada antes de commit.
9. **NO modificar `kernel/anti_dory/b8_magna_classifier.py`** desde Batch 009. La rama es sólo documentación. Cambios de código viven en Batch 008 hasta firma R1.
10. **NO firmar veredicto T1 desde Cowork.** Cowork propone; T1 firma.
11. **NO marcar `_INDEX.md` de DSCs como cerrado**. Sin DSC nuevo en este batch.
12. **NO invocar `apply_migration`** ni ningún DDL.

---

## 5. Entradas requeridas para pasar a `READY_FOR_R1_EXECUTION`

- [ ] Firma T1 sobre este plan (`READY_FOR_T1_REVIEW` → `APPROVED`).
- [ ] Auditor adversarial designado (T2 o T3 distinto al autor B8 v3).
- [ ] Set R1 (≥ 100 casos, balanceado por categoría) preparado por auditor independiente.
- [ ] Definición formal del flag `ANTI_DORY_B8_V3_ENABLED` en doctrina (DSC o nota).
- [ ] Confirmación de observabilidad mínima implementable (no requiere implementar; sólo confirmar que es factible sin tocar prod).

---

## 6. Siguientes firmas requeridas

| Firma | Rol | Fecha tope | Estado |
|---|---|---|---|
| Revisión doctrinal | Cowork T2 | 2026-05-21 | Producida (este doc) |
| Aprobación plan | T1 (Alfredo) | TBD | Pendiente |
| Auditor adversarial | T2/T3 designado | post firma T1 | Pendiente |
| Veredicto R1 | T1 (Alfredo) | post ejecución R1 | Pendiente |

---

## 7. Guardrails confirmados (este batch)

- No main: rama lateral `control-tower/2026-05-21-batch-009-canary-r1-review`.
- No PR.
- No deploy.
- No Supabase writes.
- No activación Fase 1 / R1 / Guardian.
- No declaración `DORY_DEAD`.
- No código kernel/app modificado.
- No secretos expuestos.
