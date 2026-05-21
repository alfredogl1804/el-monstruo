# B11 Evidence Pack Index — Terna Rotativa Sabios

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Rama:** `control-tower/2026-05-20-b11-evidence-pack`
**Lote:** ANTI_DORY_PARALLEL_GATES_BATCH_001
**Fecha:** 2026-05-20

---

## §1 Propósito

Este pack consolida los artefactos diseñados por Manus E2 para el gate B11 según el closure pack v0.2 firmado (`B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §6). NO canoniza B11, NO modifica main, NO ejecuta runtime, NO declara B11 PASS. Es input directo para firma magna T1.

B11 define la rotación trimestral de la terna de Sabios LLM externos que auditan el sistema Anti-Dory. La rotación previene captura cultural por un único modelo y diversifica fuentes de auditoría.

---

## §2 Artefactos incluidos en esta rama

| Artefacto | Path | Tipo | Estado |
|-----------|------|------|--------|
| Spec design | `bridge/spec/B11_SABIOS_ROTATION_SPEC.md` | Markdown | DRAFT_T1_PENDING |
| B11-E1 — Calendario anual 2027 (DRAFT) | `bridge/control_tower/evidence/B11/B11_E1_annual_calendar.md` | Markdown | DRAFT_T1_PENDING |
| B11-E6 — Procedimiento de rotación | `bridge/spec/B11_SABIOS_ROTATION_PROCEDURE.md` | Markdown | DRAFT_T1_PENDING |
| Index (este archivo) | `bridge/control_tower/2026-05-20/manus_e2/B11_EVIDENCE_PACK_INDEX.md` | Markdown | DRAFT_T1_PENDING |

---

## §3 Artefactos NO incluidos (requieren runtime o firma humana)

| ID | Razón |
|----|-------|
| B11-E2 (declaraciones de scope por trimestre) | Requiere firma T1 + firma Sabio activo del trimestre |
| B11-E3 (audit logs de transición trimestral) | Requiere 4 transiciones reales con 3 firmas cada una |
| B11-E4 (reporte KL divergence trimestral) | Requiere los 4 Sabios procesando set de calibración, runtime real |
| B11-E5 (reporte anual adversarial Grok) | Requiere 1 año de auditorías completadas + Grok 4 procesando logs sanitizados |

---

## §4 Decisiones T1 pendientes (bloquean producción de B11-E2..E5)

- **D-B11-1:** Aprobación verbatim del calendario anual base (Q1 Opus, Q2 DeepSeek, Q3 Gemini, Q4 Kimi) y de los Sabios suplentes.
- **D-B11-2:** Confirmación del scope de auditoría inicial (B6-E2/E6, B7-E1/E4/E5/E7, B9-E3) para el Sabio activo del trimestre en curso.
- **D-B11-3:** Aprobación del threshold KL divergence ≥ 0.15 (propuesta) o definición alternativa.
- **D-B11-4:** Designación del set de calibración (propuesta: 20 fixtures canónicos DORY_BENCH congelados).
- **D-B11-5:** Aprobación del rol adversarial de Grok 4 con scope anual (B11-E5).

---

## §5 Restricciones aplicadas (verbatim AGENTS.md + closure v0.2)

- NO se implementa runtime.
- NO se modifica `main`.
- NO se abre PR.
- NO se canoniza B11.
- NO se declara B11 PASS.
- NO se ejecutan transiciones reales (requieren 3 firmas reales).
- Manus E2 actúa como autor NO-Cowork.
- Cowork T2-A NO puede ser Sabio activo primario (regla binaria spec §7).

---

## §6 Riesgos cruzados con otros gates del BATCH_001

La narrativa de acoplamiento con los demás gates del lote es la siguiente. B11 es el calendario maestro del cual dependen las designaciones de auditores de B6, B7 y B9. La sincronización entre estos gates es crítica: si T1 modifica el calendario B11, debe actualizar simultáneamente las designaciones D-B6-3 (Sabio auditor de key custody), D-B7-2 (terna de auditores de fixtures), y D-B9-3 (Sabio auditor de overrides T1). El index maestro del lote propone que estas 4 decisiones T1 (D-B11-1, D-B6-3, D-B7-2, D-B9-3) se firmen como bloque indivisible para evitar desincronización.

El gate B11 también interactúa con B7 en la dimensión arquitectónica de v0.2: el rediseño de B7 separa el rol de custodio (entidad con almacenamiento persistente) del rol de auditor (Sabio LLM stateless). El calendario B11 cubre exclusivamente el rol de auditor; los custodios B7.3 viven en una terna distinta (T1 escrow, cloud privada, HSM/KMS) que NO rota trimestralmente sino según la regla B7.5c (custodio actual ≠ custodio últimos 2 trimestres).

Con B9, B11 garantiza que el Sabio que audita los overrides T1 (B9.5) es trimestralmente diferente, lo que evita que un mismo Sabio establezca patrones de validación predecibles sobre las decisiones magnas de T1.

Con B6, el Sabio activo del trimestre audita los procedimientos de rotación y revocación de la clave ed25519, lo que garantiza que la cadena de firmas criptográfica nunca sea auditada por una única perspectiva cultural a lo largo del año.

---

## §7 Próximo paso

T1 firma decisiones D-B11-1..D-B11-5 en un receipt separado (idealmente como parte del bloque maestro D-B6-3 + D-B7-2 + D-B9-3 + D-B11-1) ⇒ Sabio activo del trimestre actual firma B11-E2 scope ⇒ bridge ejecuta transiciones trimestrales (B11-E3) ⇒ Sabio independiente calcula KL divergence (B11-E4) ⇒ Grok 4 ejecuta análisis adversarial anual (B11-E5) ⇒ T1 firma magna PASS.

Hasta entonces, el estado del gate permanece `DRAFT_T1_PENDING`.

---

**Firma magna pendiente.**
