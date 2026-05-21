# BATCH 002 — SIGNATURE RECEIPT

## Metadata
- agente: manus_c
- rol real: redactor de receipt
- fecha/hora: 2026-05-20 CST
- rama: control-tower/2026-05-20-batch-002-signature-receipt
- PR: N/A
- commit: (this)
- estado fuente: SIGNATURE_RECEIPT
- tocó código: no
- tocó main: no

## 1. Firma T1 verbatim

> T1 firma magna Batch 002 como diseño/prep, no runtime.

## 2. Estado resultante

**DESIGN_PREP_SIGNED_RUNTIME_PENDING**

## 3. Ramas firmadas

| Célula | Rama | Commit | Estado |
|---|---|---|---|
| B6-E3 | `control-tower/2026-05-20-b6-e3-public-key-prep` | `71fccc8` | DESIGN_SIGNED |
| B7-E1/E2 | `control-tower/2026-05-20-b7-custody-prep` | `a6dd23a` | DESIGN_SIGNED |
| B9-E3 v0.2 | `control-tower/2026-05-20-b9-e3-test-plan-v0-2` | `11bff4b` | DESIGN_SIGNED |
| B11-E2/E4 | `control-tower/2026-05-20-b11-kl-plan` | `0183ba8` | DESIGN_SIGNED |
| Index | `control-tower/2026-05-20-batch-002-index` | `414110f` | DESIGN_SIGNED |

## 4. Caveats firmados

| # | Caveat | Implicación |
|---|---|---|
| 1 | B6-E3 no push directo a main | La clave pública se publica en rama lateral; merge a main requiere autorización separada |
| 2 | B6-E3 manifest pending_backup | El backup de la clave privada (USB/papel) debe completarse ANTES de publicar la pública |
| 3 | B7 fallback custodio único T1 | Si no hay segundo custodio designado, T1 es custodio único de los fixtures; riesgo de single-point-of-failure aceptado temporalmente |
| 4 | B9-E3 plan no ejecución | Los 10 tests son plan documental; la ejecución runtime requiere VERIFICADOR + Memento + Guardian operativos + autorización separada |
| 5 | B9 NO_OP/ALLOW interpretación | En el caso T4, si Memento no emite veredicto explícito, se interpreta como no-bloqueo (equivalente funcional a ALLOW); esta interpretación requiere confirmación cuando Memento esté implementado |
| 6 | B9 MEMENTO_DEGRADED nombre inferido | El estado `MEMENTO_DEGRADED` es nombre propuesto por Manus C; no está canonizado en código ni en doctrina firmada; el nombre final se define cuando se implemente |
| 7 | B11 KL >=0.15 meta de diseño | El threshold de divergencia 0.15 es meta aspiracional de diseño; el valor real se calibrará con datos empíricos cuando se ejecute la medición |

## 5. Confirmaciones

| Restricción | Respetada | Evidencia |
|---|---|---|
| No main | YES | Branch lateral creada desde main, sin merge |
| No PR | YES | Cero PRs abiertos |
| No runtime | YES | Cero ejecución de tests, APIs, o servicios |
| No Fase 1 | YES | Anti-Dory permanece en estado documental |
| No Dory muerto | YES | No se declaró cura completada |
| No R1 | YES | Nightly Builder R1 sigue bloqueado para estos gates |
| No secrets | YES | Cero credenciales, tokens, o material sensible |
| No clave privada | YES | No se generó, solicitó, ni manejó material criptográfico privado |
| No fixtures secretos reales | YES | Solo inventario de estructura; fixtures reales pendientes de sesión T1 local |

## 6. Próximo paso recomendado

**B6-E3 real** solo procede si T1 autoriza sesión criptográfica local. Los pasos exactos están documentados en `B6_E3_PUBLIC_KEY_PREP.md` (commit `71fccc8`). Requiere:

1. T1 ejecuta `minisign -G` en su máquina local.
2. T1 guarda clave privada en USB + papel (caveat #2).
3. T1 publica clave pública en rama lateral.
4. Manus C registra el hash de la clave pública.

Hasta que T1 no inicie la sesión criptográfica, el batch permanece en estado `DESIGN_PREP_SIGNED_RUNTIME_PENDING`.

## Cierre

Este receipt documenta la firma magna de T1 sobre Batch 002 en modo diseño/prep. No constituye autorización de runtime, ejecución, merge, ni canonización. El batch avanza a runtime solo con autorización explícita separada por célula.
