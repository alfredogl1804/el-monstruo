# B9 Evidence Pack Index — VERIFICADOR Authority/Degradation Matrix

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Rama:** `control-tower/2026-05-20-b9-evidence-pack`
**Lote:** ANTI_DORY_PARALLEL_GATES_BATCH_001
**Fecha:** 2026-05-20

---

## §1 Propósito

Este pack consolida los artefactos diseñados por Manus E2 para el gate B9 según el closure pack v0.2 firmado (`B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §5). NO canoniza B9, NO modifica main, NO ejecuta runtime, NO declara B9 PASS. Es input directo para firma magna T1.

B9 v0.2 corrige el conteo de tests B9.9 de "9" (v0.1) a "10" (v0.2) alineado con los 10 casos canónicos: 4 acuerdos triviales + 2 desacuerdos críticos + 1 override T1 + 3 degradaciones.

---

## §2 Artefactos incluidos en esta rama

| Artefacto | Path | Tipo | Estado |
|-----------|------|------|--------|
| B9-E1 — Matriz N×N en tabla canónica | `bridge/spec/B9_VERIFICADOR_AUTHORITY_MATRIX.md` | Markdown | DRAFT_T1_PENDING |
| B9-E2 — Diagramas de decisión para los 10 casos canónicos | `bridge/spec/B9_authority_decision_flows.mmd` | Mermaid (multi-diagrama) | DRAFT_T1_PENDING |
| B9-E4 — Procedimiento de escalación T1 (DRAFT input para T1) | `bridge/spec/B9_T1_ESCALATION_PROCEDURE.md` | Markdown | DRAFT_T1_PENDING |
| Index (este archivo) | `bridge/control_tower/2026-05-20/manus_e2/B9_EVIDENCE_PACK_INDEX.md` | Markdown | DRAFT_T1_PENDING |

---

## §3 Artefactos NO incluidos (requieren runtime)

| ID | Razón |
|----|-------|
| B9-E3 (10 logs de tests binarios) | Requiere VERIFICADOR-001 + Memento + Guardian ejecutándose en sandbox firmado, produciendo 10 logs firmados (4 acuerdo + 2 desacuerdo + 1 T1 override + 3 degradación) |

---

## §4 Decisiones T1 pendientes (bloquean producción de B9-E3)

- **D-B9-1:** Aprobación verbatim de la matriz N×N B9.1 (§4 del spec).
- **D-B9-2:** Confirmación de los 3 casos críticos B9.3, B9.4, B9.5 con resoluciones binarias.
- **D-B9-3:** Designación del Sabio auditor permanente para overrides T1 (propuesta: Opus 4.7).
- **D-B9-4:** Decisión sobre existencia de réplica VERIFICADOR-002 (propuesta: sí, con failover automático).

Nota sobre B9-E4: según closure v0.2, B9-E4 es producido por T1 verbatim (T1 redacta el procedimiento de su propia escalación). El documento incluido en este pack es un **borrador propuesto por Manus E2 como input para T1**.

---

## §5 Restricciones aplicadas (verbatim AGENTS.md + closure v0.2)

- NO se implementa runtime.
- NO se modifica `main`.
- NO se abre PR.
- NO se canoniza B9.
- NO se declara B9 PASS.
- NO se ejecutan los 10 tests B9.9 (requieren runtime real).
- Manus E2 actúa como autor NO-Cowork (diseña spec, no compone runtime, NO produce B9-E4 final — solo borrador).
- Cowork T2-A NO actúa como autor único de la matriz (regla §5.8 closure v0.2: "No se diseña con Cowork como autor único de la matriz").

---

## §6 Riesgos cruzados con otros gates del BATCH_001

La interacción de B9 con los demás gates del lote es la más densa: B9 es la matriz que coordina la respuesta de todo el sistema ante fallos. La siguiente narrativa describe los acoplamientos críticos.

B9 depende de **B6** porque la firma ed25519 del kill switch local-first es validada por VERIFICADOR-001. Si B6 entra en `KEY_REVOKED` (procedimiento B6-E5), VERIFICADOR-001 deja de poder validar payloads cifrados con la clave revocada, lo que activa automáticamente la ruta B9.6 (`VERIFICADOR_DEGRADED`). El procedimiento B6-E5 §4.2 ya documenta esta consistencia.

B9 depende de **B8** porque la lista taxonómica (a)-(m) define qué acciones quedan bloqueadas cuando el sistema entra en `VERIFICADOR_DEGRADED` o `MEMENTO_DEGRADED`. El payload de escalación T1 (B9-E4 §4) incluye explícitamente el campo `proposed_action_category` con valor en la taxonomía B8.

B9 referencia a **B11** porque el Sabio auditor designado (D-B9-3, propuesta Opus 4.7) coincide con el Sabio activo del trimestre B11 según calendario. Si T1 designa un Sabio distinto en B11, esta designación se propaga automáticamente a B9 para mantener consistencia.

B9 referencia a **B7** porque la matriz N×N cubre el caso de Sabio auditor B7 actuando como capa adicional sobre VERIFICADOR-001: en `VERIFICADOR_DEGRADED`, el Sabio auditor B7 puede recibir métricas sanitizadas pero no sustituye a VERIFICADOR en su rol de validación criptográfica.

---

## §7 Próximo paso

T1 firma decisiones D-B9-1..D-B9-4 en un receipt separado ⇒ T1 redacta versión final de B9-E4 (puede partir del DRAFT incluido) ⇒ VERIFICADOR-001 + Memento + Guardian ejecutan los 10 tests en sandbox firmado ⇒ Sabio externo audita ⇒ T1 firma magna PASS.

Hasta entonces, el estado del gate permanece `DRAFT_T1_PENDING`.

---

**Firma magna pendiente.**
