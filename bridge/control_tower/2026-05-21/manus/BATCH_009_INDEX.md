# BATCH 009 — INDEX

**Fecha:** 2026-05-21
**Rama:** `control-tower/2026-05-21-batch-009-canary-r1-review`
**Commit base:** `b11254f` (main HEAD al momento de la creación)
**Commit Batch 009:** `<PENDIENTE — se llena tras commit final>`
**Estado:** `DRAFT — READY_FOR_T1_REVIEW`
**Tipo:** Documentación / planificación. No código, no PR, no deploy.

---

## 1. Propósito

Preparar la revisión R1 (Canary Round 1) del clasificador Anti-Dory B8 v3 producido en Batch 008. Definir criterios, plan de integración y guardrails antes de cualquier acción magna.

---

## 2. Documentos canonizados en este batch

| # | Documento | Propósito | Estado |
|---|---|---|---|
| 1 | `BATCH_009_CANARY_R1_REVIEW_PLAN.md` | Plan R1, objetivos audit, no-go list | `READY_FOR_T1_REVIEW` |
| 2 | `B8_V3_INTEGRATION_PLAN.md` | Plan merge condicional B8 v3 → main | `READY_FOR_T1_REVIEW` |
| 3 | `CANARY_R1_CRITERIA.md` | Criterios `READY_FOR_R1`, `BLOCK_R1`, `DORY_DEAD_CANDIDATE` | `READY_FOR_T1_REVIEW` |
| 4 | `BATCH_009_INDEX.md` | Este índice maestro | `READY_FOR_T1_REVIEW` |

Todos bajo `bridge/control_tower/2026-05-21/manus/`.

---

## 3. Evidencia de Batch 008 referenciada (no producida aquí)

| Artefacto | Path | Rama origen |
|---|---|---|
| Reporte Manus R0 v3 | `bridge/control_tower/2026-05-21/manus/MANUS_CANARY_R0_V3_REPORT.md` | `control-tower/2026-05-21-batch-008-b8-v3` @ `0ac0a91` |
| Resultados 70 casos | `bridge/control_tower/evidence/CANARY/MANUS_CANARY_R0_V3_RESULTS.json` | idem |
| JUnit suite 231 tests | `bridge/control_tower/evidence/B8_V3/B8_V3_ALL_TESTS_junit.xml` | idem |
| Código v3 | `kernel/anti_dory/b8_magna_classifier.py` (Δ ~157 LOC) | idem |

---

## 4. Estado actual del Objetivo Maestro 9 (Capa 8 Memento)

- R0 v3 (70/70): **PASS**.
- R1: **no ejecutado**.
- DORY_BENCH_1000 / CVDS: **no aplicado a v3**.
- Restore/rollback test: **no ejecutado**.
- Firma T1 sobre integración: **pendiente**.
- Estado oficial: **`READY_FOR_CANARY_R1_REVIEW`** (no `DORY_DEAD`, no candidato).

---

## 5. Próximas firmas requeridas (orden)

1. **T1 (Alfredo)** — revisión y aprobación de los 4 docs de este batch.
2. **T1** — designación de auditor adversarial independiente (T2/T3 distinto al autor B8 v3).
3. **Auditor designado** — preparación de set R1 (≥ 100 casos) + ejecución.
4. **T1** — veredicto sobre resultados R1.
5. **T2 Cowork** — audit DSC-G-008 v2 sobre PR de integración (cuando proceda).
6. **T1** — firma final de merge.
7. **T1** — firma `DORY_DEAD` (sólo si todos los criterios 3.1-3.10 de `CANARY_R1_CRITERIA.md` están verdes).

---

## 6. Guardrails confirmados

- Rama lateral: `control-tower/2026-05-21-batch-009-canary-r1-review`.
- `main` no tocado.
- No PR.
- No deploy.
- No writes a Supabase prod.
- No `apply_migration`.
- No activación de Fase 1, R1, Guardian.
- No declaración `DORY_DEAD`.
- No modificación de código kernel/app.
- No exposición de secretos.
- No firma T1 emitida por Cowork.

---

## 7. Trazabilidad

| Campo | Valor |
|---|---|
| Origen del batch | Veredicto Manus R0 v3 firmado `READY_FOR_CANARY_R1_REVIEW` (2026-05-21) |
| Autor docs | Cowork T2 (Arquitecto) |
| Batch previo | 008 (B8 v3) en rama `control-tower/2026-05-21-batch-008-b8-v3` @ `0ac0a91` |
| Batch siguiente esperado | 010 — ejecución R1 (sólo tras firma T1) |
