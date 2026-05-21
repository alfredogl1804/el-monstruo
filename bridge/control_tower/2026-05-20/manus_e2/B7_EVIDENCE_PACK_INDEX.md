# B7 Evidence Pack Index — Hidden Fixture Custody no-compositor

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Rama:** `control-tower/2026-05-20-b7-evidence-pack`
**Lote:** ANTI_DORY_PARALLEL_GATES_BATCH_001
**Fecha:** 2026-05-20

---

## §1 Propósito

Este pack consolida los artefactos diseñados por Manus E2 para el gate B7 según el closure pack v0.2 firmado (`B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §3). NO canoniza B7, NO modifica main, NO ejecuta runtime, NO declara B7 PASS. Es input directo para firma magna T1.

B7 v0.2 corrige el fallo arquitectónico F16-derivado detectado por Cowork T2-A §3: los Sabios LLM **no pueden ser custodios** (son stateless, sin filesystem persistente), solo auditores.

---

## §2 Artefactos incluidos en esta rama

| Artefacto | Path | Tipo | Estado |
|-----------|------|------|--------|
| Spec design | `bridge/spec/B7_FIXTURE_CUSTODY_SPEC.md` | Markdown | DRAFT_T1_PENDING |
| B7-E3 — Procedimiento de rotación trimestral | `bridge/control_tower/keys/DORY_BENCH_FIXTURE_ROTATION_PROCEDURE.md` | Markdown | DRAFT_T1_PENDING |
| Index (este archivo) | `bridge/control_tower/2026-05-20/manus_e2/B7_EVIDENCE_PACK_INDEX.md` | Markdown | DRAFT_T1_PENDING |

---

## §3 Artefactos NO incluidos (requieren runtime o firma humana)

| ID | Razón |
|----|-------|
| B7-E1 (inventario hashes 50 fixtures) | Requiere decryption por quórum de custodios reales + runner DORY_BENCH |
| B7-E2 (declaración custodios firmada T1) | Requiere firma magna T1 |
| B7-E4 (audit log 4 rotaciones) | Requiere 1 año de operación runtime |
| B7-E5 (logs DORY_BENCH consumidores) | Requiere VERIFICADOR-001 + runner en sandbox firmado |
| B7-E6 (declaración auditores Sabios LLM) | Requiere firma magna T1 cross-ref B11 |
| B7-E7 (logs prompts a Sabios con verificación B7.8) | Requiere VERIFICADOR-001 ejecutándose en el runner |

---

## §4 Decisiones T1 pendientes (bloquean producción de B7-E1..E7)

- **D-B7-1:** Terna inicial de custodios entre (a)-(e). NO Sabios LLM.
- **D-B7-2:** Terna inicial de auditores Sabios LLM (cross-ref D-B11-1, calendario trimestral fijo).
- **D-B7-3:** Frecuencia de rotación de fixtures (propuesta: 90 días o post-incidente).
- **D-B7-4:** Quórum de descifrado (propuesta: 2-de-3 custodios; fallback 1-de-1 con T1 escrow).
- **D-B7-5:** Repo / almacenamiento concreto para slices cifrados (propuesta: 3 buckets GCS privados con CMEK + IAM allow-list).

---

## §5 Restricciones aplicadas (verbatim AGENTS.md + closure v0.2)

- NO se implementa runtime.
- NO se modifica `main`.
- NO se abre PR.
- NO se canoniza B7.
- NO se declara B7 PASS.
- NO Sabios LLM como custodios (regla binaria v0.2).
- NO Cowork T2-A ni Grok 4 como custodios.
- NO compositor activo del spec como custodio.
- Manus E2 actúa como autor NO-Cowork (diseña spec, no compone runtime).

---

## §6 Riesgos cruzados con otros gates del BATCH_001

- **B7 ↔ B6:** custodios B7 pueden compartir infraestructura criptográfica con B6, pero claves distintas (slice B7 cifrado con clave del custodio B7, no con clave kill switch B6). **Mitigación:** documentado en B6_KEY_CUSTODY_SPEC.md §6.
- **B7 ↔ B9:** matriz autoridad cubre VERIFICADOR-001 ⇒ Sabio auditor B7 actúa como capa adicional, no sustituye a VERIFICADOR. Si VERIFICADOR cae (B9.6), Sabio auditor B7 sigue operable.
- **B7 ↔ B11:** calendario de auditores Sabios LLM B7.4 (Q1 Opus, Q2 DeepSeek, Q3 Gemini, Q4 Kimi) es **el mismo** que el calendario B11. Cross-ref D-B7-2 ↔ D-B11-1. Si T1 modifica una decisión, debe actualizar la otra.
- **B7 ↔ B8:** rotación B7 = acción magna B8 categoría h ⇒ bloqueada por `local_unreachable: DISABLED_FOR_MAGNA_ACTIONS`. Mitigación: documentado en B7-E3 §4.1 pre-condición 4.

---

## §7 Próximo paso

T1 firma decisiones D-B7-1..D-B7-5 en un receipt separado (formato análogo a B8 Signature Receipt) ⇒ custodios producen slices cifrados ⇒ runner DORY_BENCH produce B7-E1, E4, E5, E7 ⇒ Sabio externo audita ⇒ T1 firma magna PASS.

Hasta entonces, el estado del gate permanece `DRAFT_T1_PENDING`.

---

**Firma magna pendiente.**
