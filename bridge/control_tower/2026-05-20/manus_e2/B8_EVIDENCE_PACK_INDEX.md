# B8 EVIDENCE PACK INDEX (DRAFT T1-PENDING)

**Status:** DRAFT evidence pack — pendiente firma magna T1 verbatim sobre artefactos.
**Estado resultante propuesto:** `B8 = EVIDENCE_DESIGNED_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork).
**Fuente normativa:** `bridge/control_tower/2026-05-20/manus_e2/B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §4 (B8).
**Branch sugerida:** `control-tower/2026-05-20-b8-evidence-pack`.
**Fecha:** 2026-05-20.
**Directiva T1 origen:** firma magna sobre B12 b⇒a + selección de B8 como siguiente gate Anti-Dory.

---

## §1 Inventario binario de artefactos (5 + index)

| # | ID | Path en repo | Función | Status |
|---|----|--------------|---------|--------|
| 1 | **B8-E1** | `bridge/spec/B8_MAGNA_ACTION_TAXONOMY.md` | Lista taxonómica cerrada (a)-(m) firmada como DRAFT T1-pending | DRAFT |
| 2 | **B8-E2** | `bridge/spec/B8_local_unreachable_policy.mmd` | Diagrama Mermaid de decisión binaria runtime B8.2/B8.3 | DRAFT |
| 3 | **B8-E3** | `bridge/control_tower/evidence/B8/B8_E3_runtime_policy_tests_DESIGN.jsonl` | Diseño de 16 tests sintéticos (13 rechazo + 1 no-magna warn + 1 restore retry + 1 drift) — NO ejecución runtime | DRAFT |
| 4 | **B8-E4** | `bridge/spec/B8_MAGNA_TAXONOMY_AMENDMENT_PROCEDURE.md` | Procedimiento binario de amendment (AMD-ADD/REFINE/REMOVE) con 4 pasos | DRAFT |
| 5 | **Index** | `bridge/control_tower/2026-05-20/manus_e2/B8_EVIDENCE_PACK_INDEX.md` | Este archivo | DRAFT |

## §2 Mapeo binario directiva T1 → entregables

| Punto directiva T1 | Entregable | Verificable |
|---------------------|------------|-------------|
| 1 — B8-E1 lista 13 categorías a-m DRAFT T1-pending | `B8_MAGNA_ACTION_TAXONOMY.md` §2.1-§2.13 | 13 secciones explícitas, NO cláusula abierta |
| 2 — B8-E2 diagrama decisión runtime | `B8_local_unreachable_policy.mmd` | Mermaid flowchart con 2 ramas binarias |
| 3 — B8-E3 16 tests diseño NO runtime | `B8_E3_runtime_policy_tests_DESIGN.jsonl` | 16 líneas de test + meta header + meta footer; campo `runtime_executions_in_this_artifact = 0` |
| 4 — B8-E4 procedimiento amendment | `B8_MAGNA_TAXONOMY_AMENDMENT_PROCEDURE.md` | 3 tipos amendment + 4 pasos + 8 no-go |
| 5 — Index | Este archivo | Inventario + mapeo + estado |

## §3 Conteo binario de tests B8-E3

| Bucket | Conteo | Test IDs |
|--------|--------|----------|
| Rechazo magna por categoría (a)-(m) | **13** | B8_T_01 a B8_T_13 |
| Acción no-magna permitida con warning | **1** | B8_T_14 |
| Restore + retry manual | **1** | B8_T_15 |
| Drift spec-vs-runtime | **1** | B8_T_16 |
| **TOTAL** | **16** | B8_T_01 - B8_T_16 |

Mínimo requerido por directiva T1: 16. Conteo entregado: 16. ✅

## §4 Estado de los gates B1-B12 post-pack

| Gate | Pre-pack | Post-pack |
|------|----------|-----------|
| B1 | DRAFT pendiente revisión | sin cambio |
| B2 | DRAFT pendiente revisión | sin cambio |
| B3 | DRAFT pendiente revisión | sin cambio |
| B4 | DRAFT pendiente revisión | sin cambio |
| B5 | DRAFT pendiente revisión | sin cambio |
| B6 | DISEÑADO v0.2 | sin cambio |
| B7 | DISEÑADO v0.2 | sin cambio |
| **B8** | DISEÑADO v0.2 | **EVIDENCE_DESIGNED_T1_PENDING** (DRAFT pendiente firma) |
| B9 | DISEÑADO v0.2 | sin cambio |
| B10 | DRAFT pendiente revisión | sin cambio |
| B11 | DISEÑADO v0.2 | sin cambio |
| B12 | ✅ PASS_AS_B12c_PENDING_A | sin cambio |

**Conteo binario gates firmados magna PASS:** 1/12 (solo B12). Regla dura ≤11/12 PASS sigue activa: Fase 1 BLOCKED.

## §5 Confirmación binaria

| # | Compromiso | Status |
|---|------------|--------|
| 1 | NO implementación runtime | ✅ (B8-E3 explícito en meta_header y meta_footer: `runtime_executions = 0`) |
| 2 | NO main modificado | ✅ (rama lateral exclusiva `control-tower/2026-05-20-b8-evidence-pack`) |
| 3 | NO PR abierto | ✅ |
| 4 | NO canon runtime | ✅ |
| 5 | NO Dory declarado muerto | ✅ |
| 6 | NO Fase 1 activada | ✅ |
| 7 | NO R1 modificado | ✅ |
| 8 | NO Cowork como productor único | ✅ (B8-E1, B8-E4 explícitos: Cowork solo audita) |
| 9 | NO force-push | ✅ |
| 10 | Todo marcado DRAFT evidence pack | ✅ (cada artefacto tiene header `Status: DRAFT T1-PENDING`) |

## §6 Próxima acción esperada T1

Decisión binaria T1 sobre cada uno de los 4 artefactos B8-E1 a B8-E4:

| Opción | Descripción |
|--------|-------------|
| **SIGN_ALL** | Firma magna verbatim sobre los 4 artefactos. B8 transiciona a `EVIDENCE_PARTIAL_PENDING_RUNTIME` (firma DRAFT consumada, runtime aún NO autorizado). |
| **SIGN_PARTIAL** | Firma magna verbatim sobre subset de artefactos (ej: solo B8-E1 + B8-E4). Los no firmados quedan DRAFT. B8 transiciona a `EVIDENCE_PARTIAL_PENDING_<ids>`. |
| **REVISE** | Solicita revisión de uno o más artefactos. Manus E2 produce v0.2 de los artefactos solicitados. |
| **REJECT** | Rechaza pack completo. Manus E2 archiva pack y T1 emite directiva alterna. |
| **EXTEND** | Solicita extender pack con artefactos adicionales (ej: implementación runtime DRAFT separada bajo nueva directiva, casos edge no cubiertos en 16 tests, integración con B9 VERIFICADOR matrix). |

## §7 Recomendación próximo gate (DRAFT no vinculante)

Tras firma magna T1 sobre B8 (cualquiera de las opciones SIGN_*):

| Prioridad | Gate | Razón verbatim DRAFT |
|-----------|------|----------------------|
| **1ª (alta)** | **B6** | Custodia ed25519 cerrada en closure v0.2 con tooling `signify`/`minisign`/`ssh-keygen -Y sign`. Producible T1 escrow + auditable Sabio externo. Cierra prerequisito de firma criptográfica para evidencia futura B7/B9/B11. Tras B8 + B6 firmados magna, conteo pasa a 3/12 PASS. |
| 2ª (media) | B11 | Terna rotativa Sabios cerrada en closure v0.2 con caveat KL divergence. Pre-requisito de DORY_BENCH antes de cláusula 2026-08-20. |
| 3ª (media) | B7 | Custodia fixture oculto cerrada con custodios reales. Pre-requisito DORY_BENCH. Más sensible operativamente. |
| 4ª (baja) | B9 | VERIFICADOR matrix 10 tests cerrada. Independiente B4/B7/B11. |

NO recomiendo iniciar implementación runtime de B8 hasta firma magna T1 sobre los 4 artefactos B8-E1 a B8-E4 + autorización binaria explícita de implementación runtime.

## §8 Caveat magno F16 estructural Opus 4.7

Este pack lo escribió un autor NO-Cowork (Manus E2). La firma magna T1 sobre los artefactos NO equivale a decisión doctrinal de integración del pack B8 en v1.1.1 (anexo), v2.0 RE-FUNDADO (incorporación), v3.0 sintetizada (input), o DRAFT archivado. La integración doctrinal sigue siendo decisión binaria T1 fuera de mi scope.

Manus E2 fuera de scope post-push de este pack. Espera nueva instrucción binaria T1.
