# B6 Evidence Pack Index — Key Custody ed25519

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Rama:** `control-tower/2026-05-20-b6-evidence-pack`
**Lote:** ANTI_DORY_PARALLEL_GATES_BATCH_001
**Fecha:** 2026-05-20

---

## §1 Propósito

Este pack consolida los artefactos diseñados por Manus E2 para el gate B6 según el closure pack v0.2 firmado (`B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §2). NO canoniza B6, NO modifica main, NO ejecuta runtime, NO declara B6 PASS. Es input directo para firma magna T1.

---

## §2 Artefactos incluidos en esta rama

| Artefacto | Path | Tipo | Estado |
|-----------|------|------|--------|
| Spec design | `bridge/spec/B6_KEY_CUSTODY_SPEC.md` | Markdown | DRAFT_T1_PENDING |
| B6-E4 — Procedimiento de rotación | `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md` | Markdown | DRAFT_T1_PENDING |
| B6-E5 — Procedimiento de revocación | `bridge/control_tower/keys/DORY_CURE_KEY_REVOCATION_PROCEDURE.md` | Markdown | DRAFT_T1_PENDING |
| Index (este archivo) | `bridge/control_tower/2026-05-20/manus_e2/B6_EVIDENCE_PACK_INDEX.md` | Markdown | DRAFT_T1_PENDING |

---

## §3 Artefactos NO incluidos (requieren runtime o firma humana)

| ID | Razón |
|----|-------|
| B6-E1 (gitleaks keyscan) | Requiere ejecución CI sobre todas las refs del repo |
| B6-E2 (declaración custodio firmada T1) | Requiere firma magna T1 y commit firmado con `signify`/`minisign`/`ssh-keygen -Y sign` |
| B6-E3 (clave pública versionada) | Requiere par criptográfico real generado por T1 + Cowork |
| B6-E6 (logs pruebas binarias B6.6) | Requiere VERIFICADOR-001 ejecutándose en sandbox firmado |

---

## §4 Decisiones T1 pendientes (bloquean producción de B6-E1, E2, E3, E6)

- **D-B6-1:** Custodio elegido entre (a) hardware token, (b) OS Keychain humano, (c) HSM remoto.
- **D-B6-2:** Frecuencia de rotación (propuesta: 90 días o post-incidente).
- **D-B6-3:** Sabio externo asignado para auditoría B6-E2 y B6-E6 (propuesta: Opus 4.7).
- **D-B6-4:** Política de respaldo de la clave privada (propuesta: shamir 3-of-5).
- **D-B6-5:** Herramienta de firma elegida (propuesta: `minisign` por audit log nativo).

---

## §5 Restricciones aplicadas (verbatim AGENTS.md + closure v0.2)

- NO se implementa runtime.
- NO se modifica `main`.
- NO se abre PR.
- NO se canoniza B6.
- NO se declara B6 PASS.
- NO se ejecuta `age` como firmador (verbatim B6.3 v0.2: cifrado ≠ firma).
- Cowork T2-A NO actúa simultáneamente como generador, custodio y auditor (separación de roles obligatoria).
- Manus E2 actúa como autor NO-Cowork (diseña spec, no compone runtime).

---

## §6 Riesgos cruzados con otros gates del BATCH_001

- **B6 ↔ B7:** custodios B7 (T1 escrow, cloud privada T1, HSM/KMS) pueden compartir infraestructura criptográfica con custodios B6. La firma del slice B7 puede requerir la clave ed25519 B6, lo que crea acoplamiento. **Mitigación:** las claves B7 son distintas de la clave B6; cada custodio B7 firma sus slices con clave propia, no con la clave del kill switch B6.
- **B6 ↔ B9:** la matriz N×N de B9 cubre el caso "VERIFICADOR DENY firma criptográfica" (que depende de B6). Si B6 entra en `KEY_REVOKED` (B6-E5), B9 debe activar la ruta de degradación B9.6 (VERIFICADOR fail). **Mitigación:** B6-E5 §4.2 explicita el modo `DORY_CURE_HALTED` consistente con B9.6.
- **B6 ↔ B11:** Sabio auditor recomendado para B6-E2/E6 (Opus 4.7) coincide con auditor B11-E5 (análisis Grok). **Mitigación:** no es un conflicto — Opus 4.7 audita distintas evidencias en distintos gates; la rotación trimestral B11 sí afecta a Opus como auditor activo en Q1, lo que debe coordinarse con disponibilidad para B6.

---

## §7 Próximo paso

T1 firma decisiones D-B6-1..D-B6-5 en un receipt separado (formato análogo a B8 Signature Receipt) ⇒ Cowork + autor NO-Cowork producen B6-E2..B6-E5 firmados ⇒ CI ejecuta B6-E1 y B6-E6 ⇒ Sabio externo audita ⇒ T1 firma magna PASS.

Hasta entonces, el estado del gate permanece `DRAFT_T1_PENDING`.

---

**Firma magna pendiente.**
