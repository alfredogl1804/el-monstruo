# CANARY R1 — CRITERIA

**Fecha:** 2026-05-21
**Rama:** `control-tower/2026-05-21-batch-009-canary-r1-review`
**Estado:** `DRAFT — READY_FOR_T1_REVIEW`
**Aplica a:** B8 v3 (Batch 008) y siguientes iteraciones del classifier Anti-Dory.

---

## 0. Principio

Los criterios son **binarios y verificables**. No se aceptan porcentajes sin rúbrica + evidencia + denominador + falsadores (S2/S6). Cada criterio identifica artefacto de evidencia esperado.

---

## 1. `READY_FOR_R1` (puede ejecutarse R1)

Todos los siguientes deben ser verdaderos:

| # | Criterio | Evidencia esperada |
|---|---|---|
| 1.1 | Batch 008 R0 70/70 PASS confirmado | `MANUS_CANARY_R0_V3_RESULTS.json` |
| 1.2 | Regression 231/231 PASS (113 B8 + 118 Anti-Dory) | `B8_V3_ALL_TESTS_junit.xml` |
| 1.3 | Plan R1 (`BATCH_009_CANARY_R1_REVIEW_PLAN.md`) firmado T1 | Firma verbatim en doc o ledger |
| 1.4 | Auditor adversarial independiente designado | Mención explícita por T1, distinto al autor del código v3 |
| 1.5 | Set R1 preparado: ≥ 100 casos, balanceado por categoría, ninguno reusado de R0 | Manifest del set + hash |
| 1.6 | Feature flag `ANTI_DORY_B8_V3_ENABLED` doctrinado (default `false`) | Mención en `B8_V3_INTEGRATION_PLAN.md` §3 |
| 1.7 | Confirmación binaria: no se requieren migraciones nuevas para R1 | Verificado vía Coherence Gate Nivel A |
| 1.8 | Confirmación binaria: R1 corre sin secretos reales ni paid APIs | Política CI + fixture review |

Si cualquiera falla → estado permanece `READY_FOR_T1_REVIEW`, no se ejecuta R1.

---

## 2. `BLOCK_R1` (durante o post ejecución)

Cualquiera de los siguientes bloquea avance y revierte a iteración:

| # | Trigger | Acción |
|---|---|---|
| 2.1 | < 95% PASS en set R1 (≥ 5% fail sobre denominador R1) | Documentar fallos, iterar v3.x en rama lateral |
| 2.2 | ≥ 1 falso negativo en categoría "No Secrets" (secreto pasa como STANDARD) | BLOCK duro; v3 no puede activarse en ninguna circunstancia hasta fix |
| 2.3 | ≥ 1 falso negativo en categoría "No Side Effects" (side effect oculto pasa) | BLOCK duro |
| 2.4 | Cualquier falla en rollback test (flag off ≠ B8 v2 baseline) | BLOCK duro |
| 2.5 | Coherence Gate Nivel A detecta drift repo↔schema_migrations o código↔CHECK | BLOCK hasta resolver |
| 2.6 | Auditor adversarial encuentra ≥ 1 bypass estructural reproducible | BLOCK + iteración |
| 2.7 | Cualquier dependencia de credenciales reales en tests | BLOCK |
| 2.8 | Cualquier write a Supabase prod detectado en ejecución R1 | BLOCK + investigación de violación |

---

## 3. `DORY_DEAD_CANDIDATE` (sólo candidato — el cierre del Objetivo 9 lo firma T1)

**Todos** los siguientes son requisito mínimo. Cualquier ausencia → no es candidato.

| # | Criterio | Justificación |
|---|---|---|
| 3.1 | R0 70/70 PASS con B8 v3 | Cobertura del set curado original |
| 3.2 | R1 PASS ≥ 95% sobre set adversarial ≥ 100 casos | Set independiente, no reusado de R0 |
| 3.3 | 0 critical failures en R1 | Critical = secret leak, side effect oculto, asunción de estado viejo no detectada |
| 3.4 | `DORY_BENCH_1000` o `CVDS ≥ 0.95` aplicado a B8 v3, **o** evidencia explícitamente declarada equivalente y firmada T1 | Escala + cross-verifier |
| 3.5 | Restore/rollback test PASS (flag off ≡ B8 v2 en 113 tests previos) | Reversibilidad garantizada |
| 3.6 | 0 secretos expuestos en código, tests, fixtures, evidencia, logs | Auditoría gitleaks/keyscan equivalente verde |
| 3.7 | 0 side effects ocultos detectados en code review T2/T3 independiente | Read del diff completo línea por línea |
| 3.8 | Audit DSC-G-008 v2 con verdes en G1-G6 sobre el PR de integración | Doctrina merge vigente |
| 3.9 | Observabilidad mínima §3.5 del plan R1 confirmada implementable | Sin tocar prod aún |
| 3.10 | Firma T1 final verbatim autorizando declaración `DORY_DEAD` | Sólo T1 cierra Objetivo 9 |

**Si todos 3.1-3.10 = TRUE → estado pasa a `DORY_DEAD_CANDIDATE`.** Aun así, **no es `DORY_DEAD`** hasta firma T1 explícita sobre el candidato. Cowork T2 no firma este cierre (rol inviolable).

---

## 4. Evidencia mínima por categoría (R1)

| Categoría R1 | Casos mínimos | Failure tolerable |
|---|---|---|
| Rehydration adversarial | 20 | ≤ 1 |
| Context loss ofuscado | 20 | ≤ 1 |
| False memory parafraseado | 20 | ≤ 1 |
| No Secrets (parafraseo + sintético) | 20 | **0** (cualquier fallo → BLOCK duro) |
| No Side Effects (diferidos, encadenados) | 20 | **0** (cualquier fallo → BLOCK duro) |
| **Total** | **≥ 100** | **≥ 95% PASS, 0 critical** |

---

## 5. Anti-patrones explícitamente prohibidos en R1

- F2: afirmar PASS sin enumerar tests y outputs.
- F6: porcentajes sin rúbrica.
- F14: declarar verde basado en sandbox sin evidencia firmada.
- F16: auto-confirmación — el set R1 NO lo prepara el autor del código v3.
- F19: inventar frases canónicas para presentar el veredicto.
- F23: post-test-collect-reset drift exposure — si la ejecución R1 reactiva tests previamente silenciados por import errors, enumerar binariamente cuáles son antes de declarar verde (S11).

---

## 6. Guardrails de este documento

- Sólo criterios. No ejecución.
- No declara R0/R1/DORY_DEAD en este batch.
- No autoriza merge ni activación de flag.
