# ANTI-DORY PARALLEL GATES — BATCH 001 — Index Maestro

**Estado global del lote:** `DRAFT_T1_PENDING`
**Coordinador:** Manus E2 (autor NO-Cowork, sin runtime, sin firma)
**Lote:** ANTI_DORY_PARALLEL_GATES_BATCH_001
**Fecha:** 2026-05-20
**Fuente normativa:** `bridge/control_tower/2026-05-20/manus_e2/B6_B12_DESIGN_CLOSURE_PACK_v0_2.md`

---

## §1 Propósito del lote

Preparar en paralelo los evidence/design packs para 4 gates pendientes del closure pack v0.2 firmado, sin firma magna, sin runtime, sin modificar `main`, sin abrir PRs, sin canonizar, sin declarar Dory muerto, sin activar Fase 1 y sin tocar R1. Cada gate genera una rama lateral independiente con sus artefactos DRAFT.

Este index maestro consolida los 4 packs y proporciona la vista única que T1 necesita para firmar decisiones en bloque.

---

## §2 Estado por gate

| Gate | Tema | Rama lateral | SHA local | Index pack |
|------|------|--------------|-----------|------------|
| **B6** | Key custody ed25519 | `control-tower/2026-05-20-b6-evidence-pack` | `0b00d1f` | `bridge/control_tower/2026-05-20/manus_e2/B6_EVIDENCE_PACK_INDEX.md` |
| **B7** | Hidden fixture custody | `control-tower/2026-05-20-b7-evidence-pack` | `8977a63` | `bridge/control_tower/2026-05-20/manus_e2/B7_EVIDENCE_PACK_INDEX.md` |
| **B9** | VERIFICADOR / Memento / Guardian / T1 authority matrix | `control-tower/2026-05-20-b9-evidence-pack` | `5d9a483` | `bridge/control_tower/2026-05-20/manus_e2/B9_EVIDENCE_PACK_INDEX.md` |
| **B11** | Terna rotativa Sabios | `control-tower/2026-05-20-b11-evidence-pack` | `75e4f87` | `bridge/control_tower/2026-05-20/manus_e2/B11_EVIDENCE_PACK_INDEX.md` |

Los 4 gates están en `DRAFT_T1_PENDING`, sin runtime, sin canonización, sin afectar `main`, sin abrir PRs, sin desbloquear Fase 1 ni R1.

---

## §3 Decisiones T1 pendientes — vista consolidada

| ID | Gate | Decisión |
|----|------|----------|
| D-B6-1 | B6 | Custodio elegido entre (a) hardware token, (b) OS keychain, (c) HSM remoto |
| D-B6-2 | B6 | Frecuencia de rotación (propuesta 90 días o post-incidente) |
| D-B6-3 | B6 | Sabio externo asignado para auditoría (propuesta: Opus 4.7; cross-ref B11) |
| D-B6-4 | B6 | Política de respaldo de la clave privada (propuesta: Shamir 3-de-5) |
| D-B6-5 | B6 | Herramienta de firma elegida (propuesta: minisign) |
| D-B7-1 | B7 | Terna inicial de custodios entre (a)-(e) — NO Sabios LLM |
| D-B7-2 | B7 | Terna inicial de auditores Sabios LLM (cross-ref D-B11-1) |
| D-B7-3 | B7 | Frecuencia de rotación de fixtures (propuesta 90 días o post-incidente) |
| D-B7-4 | B7 | Quórum de descifrado (propuesta: 2-de-3; fallback 1-de-1 T1 escrow) |
| D-B7-5 | B7 | Repo / almacenamiento concreto para slices cifrados |
| D-B9-1 | B9 | Aprobación verbatim de la matriz N×N |
| D-B9-2 | B9 | Confirmación binaria de B9.3, B9.4, B9.5 |
| D-B9-3 | B9 | Sabio auditor permanente para overrides T1 (cross-ref B11) |
| D-B9-4 | B9 | Decisión sobre réplica VERIFICADOR-002 |
| D-B11-1 | B11 | Aprobación verbatim del calendario anual base + Sabios suplentes |
| D-B11-2 | B11 | Scope de auditoría inicial (B6-E2/E6, B7-E1/E4/E5/E7, B9-E3) |
| D-B11-3 | B11 | Threshold KL divergence ≥ 0.15 (propuesta) |
| D-B11-4 | B11 | Designación del set de calibración (20 fixtures DORY_BENCH) |
| D-B11-5 | B11 | Aprobación del rol adversarial de Grok 4 |

**Bloque indivisible recomendado:** D-B6-3, D-B7-2, D-B9-3 y D-B11-1 deben firmarse juntas porque las 4 designan al mismo conjunto de Sabios LLM externos en distintos roles. Firmar una sin las otras crea desincronización en el calendario.

---

## §4 Riesgos cruzados consolidados

El lote presenta acoplamientos entre gates que un coordinador debe vigilar para evitar que la firma de uno deje a otro en estado inconsistente. La narrativa siguiente describe los acoplamientos principales.

El gate B6 (clave ed25519 del kill switch local-first) es la raíz criptográfica del sistema. Si la clave entra en estado `KEY_REVOKED` por el procedimiento B6-E5, VERIFICADOR-001 deja de poder validar firmas y el sistema activa automáticamente la ruta de degradación B9.6 documentada en la matriz N×N. Por esto, B6 y B9 deben firmarse de forma consistente: la matriz B9 asume el funcionamiento de B6, y la rotación B6 asume el comportamiento documentado en B9.

El gate B7 (custodia de los 50 hidden fixtures de DORY_BENCH) sufrió un rediseño crítico en v0.2 que separa el rol de custodio (entidad con almacenamiento persistente) del rol de auditor (Sabio LLM stateless). Esta separación se introdujo después de que el auditor Cowork T2-A identificara, en el closure v0.1, que los Sabios LLM no pueden ser custodios porque no tienen filesystem persistente. La consecuencia es que B7 ahora requiere dos ternas distintas: una para custodios (T1 escrow, cloud privada T1, HSM/KMS, humano delegado, repo privado cifrado) y otra para auditores (el calendario rotativo B11). Cualquier modificación de B11 (calendario de auditores) impacta automáticamente la terna auditora de B7, mientras que la terna custodia de B7 sigue una regla de rotación distinta (B7.5c).

El gate B9 (matriz autoridad/degradación) coordina la respuesta del sistema ante fallos de cualquier componente. Los Sabios designados como auditores en B11 son también auditores de los overrides T1 documentados en B9.5. Si T1 modifica el calendario B11, la designación D-B9-3 debe actualizarse automáticamente, salvo amendment explícito.

El gate B11 (terna rotativa de Sabios) es el calendario maestro del cual dependen las designaciones de auditores de B6, B7 y B9. Esta es la razón por la cual el bloque D-B6-3 + D-B7-2 + D-B9-3 + D-B11-1 debe firmarse como bloque indivisible.

Adicionalmente, todos los gates están subordinados a B8 (taxonomía verbatim a-m de acciones magnas). Cualquier rotación (clave B6, fixtures B7, transición trimestral B11) es una acción magna y por lo tanto queda bloqueada por `local_unreachable: DISABLED_FOR_MAGNA_ACTIONS` cuando el kill switch está activo. Esto significa que las rotaciones deben programarse en ventanas de operación normal, fuera de estados degradados.

---

## §5 Restricciones aplicadas globalmente al lote

El lote completo respeta verbatim las restricciones impuestas por el contexto del usuario y por el closure pack v0.2. Manus E2 no implementa runtime de ningún tipo, no modifica `main`, no abre PRs, no declara Dory muerto, no activa Fase 1 y no toca R1. Cada commit es un add-only a una rama lateral independiente que vive desde `origin/main`.

Manus E2 actúa como autor NO-Cowork (categoría definida por el closure v0.2 para separar generación de spec, generación de runtime y auditoría). Cowork T2-A no es autor único de ningún artefacto de este lote, conforme a la regla §5.8 del closure v0.2. Grok 4 no es Sabio activo primario en B11 (solo adversarial). Los Sabios LLM no son custodios en B7 (solo auditores).

La política de credenciales (Regla Dura #6 de AGENTS.md) se respeta: ningún artefacto contiene secrets en plaintext. Los procedimientos describen workflows que asumen 1Password / Bitwarden / Apple Keychain / HSM como bóveda primaria.

---

## §6 Productores autorizados y auditores por gate (consolidado)

| Gate | Productor de DRAFTs (este lote) | Auditor recomendado |
|------|--------------------------------|---------------------|
| B6 | Manus E2 (autor NO-Cowork) | Sabio activo Q1 (Opus 4.7 propuesta) + T1 |
| B7 | Manus E2 (autor NO-Cowork) | Sabio activo del trimestre (calendario B11) + T1 |
| B9 | Manus E2 (autor NO-Cowork; B9-E4 es DRAFT input para T1) | Sabio activo Q1 (Opus 4.7) + T1 |
| B11 | Manus E2 (autor NO-Cowork) | Sabio independiente (no parte de la terna activa) + Grok 4 adversarial + T1 |

---

## §7 Próximo paso global del lote

T1 revisa los 4 packs individuales (B6, B7, B9, B11). Firma como bloque indivisible las decisiones del cluster Sabios (D-B6-3, D-B7-2, D-B9-3, D-B11-1) más las decisiones específicas de cada gate. Esto desbloquea la siguiente fase, donde los productores autorizados (custodios, runtime, Sabios) generan las evidencias runtime que requieren ejecución real.

Una vez firmadas las decisiones, las 4 ramas laterales pueden mergearse a `main` por la vía estándar de PR + revisión Cowork (no por Manus E2). Manus E2 no abre el PR; lo hará el coordinador autorizado (Cowork o T1) después de la firma.

---

## §8 Si requiere otro agente

Sí. Las siguientes acciones requieren agentes distintos de Manus E2:

| Acción | Agente requerido | Razón |
|--------|------------------|-------|
| Push de las 4 ramas laterales al remote `origin` | Hilo paralelo Manus o T1 desde el desktop | Manus E2 está restringido a NO modificar main; el push de ramas laterales puede ser ejecutado por hilo paralelo con autorización explícita |
| Firma magna T1 de las decisiones D-B6/B7/B9/B11 | T1 (Alfredo Góngora) | Solo T1 puede firmar decisiones magnas |
| Generación de B6-E1 (gitleaks keyscan) | Hilo CI o agente con runtime CI | Manus E2 no implementa runtime |
| Generación de B6-E3 (clave pública versionada) | T1 + Cowork con HSM | Requiere par criptográfico real |
| Generación de B7-E1 (inventario hashes fixtures) | Custodio activo del trimestre con quórum 2-de-3 | Requiere decryption real |
| Generación de B9-E3 (10 tests binarios) | VERIFICADOR-001 + Memento + Guardian en sandbox firmado | Requiere runtime real |
| Generación de B11-E4 (KL divergence trimestral) | GPT-5.4 en rol arquitecto + acceso API a los 4 Sabios | Requiere runtime real |
| Generación de B11-E5 (análisis adversarial Grok anual) | Grok 4 vía API | Requiere ejecución real con logs sanitizados |
| Apertura del PR para merge a main de cada rama | T1 o Cowork autorizado | Manus E2 no abre PRs en este lote |

---

## §9 Lista de archivos producidos en el lote (consolidada)

Esta lista es informativa; cada archivo vive en su rama lateral correspondiente y no en `main`.

| Rama | Archivos |
|------|----------|
| `control-tower/2026-05-20-b6-evidence-pack` | `bridge/spec/B6_KEY_CUSTODY_SPEC.md`, `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md`, `bridge/control_tower/keys/DORY_CURE_KEY_REVOCATION_PROCEDURE.md`, `bridge/control_tower/2026-05-20/manus_e2/B6_EVIDENCE_PACK_INDEX.md` |
| `control-tower/2026-05-20-b7-evidence-pack` | `bridge/spec/B7_FIXTURE_CUSTODY_SPEC.md`, `bridge/control_tower/keys/DORY_BENCH_FIXTURE_ROTATION_PROCEDURE.md`, `bridge/control_tower/2026-05-20/manus_e2/B7_EVIDENCE_PACK_INDEX.md` |
| `control-tower/2026-05-20-b9-evidence-pack` | `bridge/spec/B9_VERIFICADOR_AUTHORITY_MATRIX.md`, `bridge/spec/B9_authority_decision_flows.mmd`, `bridge/spec/B9_T1_ESCALATION_PROCEDURE.md`, `bridge/control_tower/2026-05-20/manus_e2/B9_EVIDENCE_PACK_INDEX.md` |
| `control-tower/2026-05-20-b11-evidence-pack` | `bridge/spec/B11_SABIOS_ROTATION_SPEC.md`, `bridge/spec/B11_SABIOS_ROTATION_PROCEDURE.md`, `bridge/control_tower/evidence/B11/B11_E1_annual_calendar.md`, `bridge/control_tower/2026-05-20/manus_e2/B11_EVIDENCE_PACK_INDEX.md` |
| `control-tower/2026-05-20-batch-001-index` (este pack) | `bridge/control_tower/2026-05-20/manus_e2/ANTI_DORY_PARALLEL_GATES_BATCH_001_INDEX.md` |

---

## §10 Cierre

El lote BATCH_001 entrega 4 evidence packs en estado `DRAFT_T1_PENDING` + 1 index maestro, distribuidos en 5 ramas laterales separadas. Ninguna rama afecta `main`, ningún runtime fue ejecutado, ninguna firma magna fue producida, ninguna canonización fue declarada, Fase 1 no fue activada, R1 no fue tocado, y Dory no fue declarado muerto.

El estado global del sistema Anti-Dory permanece exactamente igual antes y después de este lote desde el punto de vista del repo `main`. El lote solo añade material consultable que T1 puede revisar y firmar cuando decida avanzar.

**Firma magna pendiente.**
