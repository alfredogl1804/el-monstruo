# B6-E2 — CUSTODY DECLARATION (DRAFT T1-PENDING)

**Gate:** B6 — Key custody ed25519 del kill switch local-first `DORY_CURE_DISABLED`.
**Sub-criterio:** B6.2 + B6-E2 (definido en `B6_KEY_CUSTODY_SPEC.md`, commit `0b00d1f`).
**Estado:** `CUSTODY_DECLARATION_DRAFT_T1_PENDING`.
**Co-producción:** T1 (Alfredo Góngora) + Cowork T2-A.
**Rol Cowork:** redactor de estructura + propuestas; **NO declara el custodio efectivo** (eso es acto exclusivo T1 verbatim).
**Fecha:** 2026-05-20.
**Spec base:** v1.1.1 (commit `2af5fe57`) firmado Fase 0 DRAFT magna T1.

---

## §0 Nota de honestidad estructural (anti-F2/F19)

Este DRAFT lo redactó Cowork T2-A bajo instrucción T1 directa "T1 / COWORK — B6-E2 CUSTODY DECLARATION". Pero la **declaración del custodio efectivo** (qué hardware token, qué cuenta HSM, qué Keychain real controla T1) es información que **solo T1 posee**. Cowork NO la inventa. Los campos marcados `⟦T1-DECLARA⟧` deben ser completados verbatim por T1 antes de firma magna. Las políticas (acceso, backup, rotación, revocación) se proponen con los valores del spec B6 + decisión batch 001 (D-B6-1..5); T1 las ratifica o corrige.

**Caveat F16:** Cowork produjo este DRAFT → Cowork NO puede auditarlo. El auditor designado es Sabio externo (§7), conforme regla anti-autoauditoría del spec B6.

---

## §1 Custodio elegido (D-B6-1 — decisión T1)

La clave privada ed25519 vive en **uno** de los tres custodios autorizados por B6.2. Cualquier otro lugar (filesystem plano, env var, secrets de CI, `.env`) es FAIL.

| Opción | Descripción | Recomendación Cowork |
|--------|-------------|----------------------|
| (a) hardware token | YubiKey FIDO2 u OnlyKey con ed25519 derivation | Más soberano (Obj 12); requiere backup B6-E5 por riesgo pérdida física |
| (b) OS Keychain | Apple Keychain con ACL restrictivo a un solo usuario humano (T1) | Operacionalmente simple; menos soberano (depende de OS vendor) |
| (c) HSM remoto | Vault / AWS KMS / GCP KMS con audit log de acceso | Mejor para rotación + audit; introduce dependencia cloud (mitigar Vector C) |

**Custodio efectivo declarado por T1:** ⟦T1-DECLARA: (a) / (b) / (c) + modelo concreto⟧

**Recomendación Cowork (no vinculante):** (a) hardware token YubiKey como custodio primario + (c) HSM remoto como respaldo sellado Shamir (ver §3). Combina soberanía local-first con recuperabilidad.

---

## §2 Política de acceso

### §2.1 Quién puede acceder a la clave privada

| Actor | Acceso a clave privada | Condición |
|-------|------------------------|-----------|
| T1 (Alfredo) | SÍ — único acceso directo | Posesión física del custodio + PIN/biométrico |
| Cowork T2-A | NO | Jamás. Solo usa la clave **pública** para verificar firmas |
| Manus E1/E2/Catastro | NO | Jamás |
| Sabios LLM | NO | Stateless, no custodian (regla B7 v0.2 aplicada) |
| VERIFICADOR-001 (runtime) | NO a privada; SÍ a pública | Verifica firmas con `.pub`, nunca firma |
| Humanos delegados por T1 | Solo si custodio = (c) HSM con IAM allow-list explícita | ⟦T1-DECLARA lista de delegados, si aplica⟧ |

### §2.2 Qué requiere autorización T1 explícita

- Cualquier operación de **firma** de un nuevo `DORY_CURE_DISABLED.sig` (acción magna categoría B8(f) + B8(h)).
- Cualquier **rotación** de la clave (§4).
- Cualquier **revocación** (§5).
- Cualquier **exportación** de la clave privada fuera del custodio.
- Cualquier cambio de la política de acceso de este documento (vía amendment firmado T1).

### §2.3 Qué queda prohibido absolutamente

| # | Prohibición |
|---|-------------|
| P1 | Clave privada en el repo Git (cualquier ref, historia, submódulo) — verificado por B6-E1 gitleaks |
| P2 | Clave privada en GitHub Secrets / CI secrets |
| P3 | Clave privada en `.env` o cualquier archivo de entorno |
| P4 | Clave privada en prompts a cualquier LLM (Cowork, Sabios, Manus) |
| P5 | Clave privada en logs (bridge, audit, runtime, stdout) |
| P6 | Firma con herramienta de cifrado (`age`, `gpg`, `openssl`) en lugar de firma ed25519 (B6.3) |
| P7 | Acceso a la privada por cualquier agente automatizado |

---

## §3 Política de backup (D-B6-4)

**Propuesta spec:** Shamir Secret Sharing **3-de-5**.

| Slice | Custodio propuesto | Tipo |
|-------|--------------------|------|
| 1 | T1 (Alfredo) | Físico personal |
| 2 | Custodio físico secundario | ⟦T1-DECLARA⟧ humano de confianza / segundo hardware token |
| 3 | Custodio físico terciario | ⟦T1-DECLARA⟧ |
| 4 | HSM/KMS remoto A | Vault / AWS KMS |
| 5 | HSM/KMS remoto B | GCP KMS (proveedor distinto a slice 4, anti-correlación) |

**Reconstrucción:** requiere ≥3 de 5 slices. Ningún actor individual reconstruye la clave solo.
**Alternativa firmada (si T1 prefiere):** ⟦T1-DECLARA alternativa + razón verbatim⟧.
**Regla binaria:** sin backup operativo, el custodio único es SPOF (R-B6-2). Backup obligatorio antes de generar la clave real.

---

## §4 Política de rotación (D-B6-2)

| Campo | Valor propuesto |
|-------|-----------------|
| Frecuencia mínima | **Cada 90 días** O tras incidente (lo que ocurra primero) |
| Procedimiento | `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md` (DRAFT B6 pack) |
| Ventana de superposición | Ambas claves (vieja + nueva) válidas durante ventana documentada para evitar gap de cobertura |
| Anclaje | El `.pub` local-first solo acepta firmas de la clave **actual** (hash anchor), no histórica (R-B6-3) |
| Clasificación | Rotación = acción magna B8(h) → bloqueada bajo `local_unreachable` |
| Ventana operativa | Rotaciones se programan fuera de estados degradados (coherencia B8/B9) |

T1 ratifica frecuencia: ⟦T1-DECLARA: 90 días / otra + razón⟧.

---

## §5 Política de revocación

| Campo | Valor |
|-------|-------|
| Trigger | Sospecha de compromiso de la clave privada |
| SLA | Invalidar la clave actual en **<60 minutos** |
| Procedimiento | `bridge/control_tower/keys/DORY_CURE_KEY_REVOCATION_PROCEDURE.md` (DRAFT B6 pack) |
| Acciones | (1) marcar `KEY_REVOKED`; (2) notificar Cowork + Sabio auditor; (3) fallback "Dory cure halted" mientras se rota; (4) rotación de emergencia con nueva clave |
| Efecto cross-gate | `KEY_REVOKED` → VERIFICADOR-001 no valida firmas → degradación B9.6 `VERIFICADOR_DEGRADED` → `DISABLED_FOR_MAGNA_ACTIONS` (B8) |
| Revocación remota | Si custodio = (c) HSM, incluye revocación remota inmediata |

---

## §6 Declaración explícita negativa (obligatoria)

> La clave privada ed25519 del kill switch `DORY_CURE_DISABLED`:
>
> - **NO** va al repositorio Git (ninguna ref, historia, submódulo).
> - **NO** va a GitHub Secrets ni a secrets de CI.
> - **NO** va a `.env` ni a ningún archivo de entorno.
> - **NO** va a prompts de ningún LLM (Cowork, Sabios LLM, Manus).
> - **NO** va a logs (bridge, audit, runtime, stdout, stderr).
>
> La clave privada vive **exclusivamente** en el custodio declarado en §1, con backup Shamir §3. Solo la clave **pública** (`.pub`) se versiona en el repo (B6-E3, artefacto separado, aún NO generado).

Verificación de cumplimiento de la parte "NO va al repo": **B6-E1 gitleaks keyscan PASS** (commit `c13af34`, 0 leaks en 123 commits, auditado Cowork 2026-05-20).

---

## §7 Auditor recomendado

| Rol | Sabio | Caveat |
|-----|-------|--------|
| Auditor B6-E2 primario | **Opus 4.7** | Recomendado por familiaridad criptografía aplicada; caveat 2026: calendario rotativo B11 formaliza Q1-2027, para el remanente 2026 Opus 4.7 actúa como auditor designado directo (resuelve gap temporal del batch 001) |
| Suplente | **DeepSeek R1** | Si Opus 4.7 no disponible |
| Restricción | **NO Cowork T2-A** | Cowork redactó este DRAFT → no puede auto-auditar (anti-F16, spec B6 regla anti-autoauditoría) |

---

## §8 Estado y firma pendiente

| Variable | Estado |
|----------|--------|
| B6-E2 status | `CUSTODY_DECLARATION_DRAFT_T1_PENDING` |
| Campos `⟦T1-DECLARA⟧` | PENDIENTES — T1 completa verbatim |
| Custodio efectivo | NO declarado por Cowork (acto exclusivo T1) |
| Clave generada | NO (este DRAFT NO genera claves) |
| Clave pública publicada | NO (B6-E3 separado, aún no generado) |
| main modificado | NO (branch lateral `control-tower/2026-05-20-b6-e2-custody-declaration`) |
| PR | NO abierto |
| Runtime | NO ejecutado |
| Fase 1 | NO activada |
| Dory | NO declarado muerto |
| Firma magna T1 | PENDIENTE |

---

## §9 Próximo paso

1. T1 completa los campos `⟦T1-DECLARA⟧` (custodio efectivo, delegados si aplica, slices Shamill 2/3, ratificación frecuencias).
2. Opus 4.7 (o DeepSeek R1 suplente) audita el DRAFT completado — NO Cowork.
3. T1 firma magna verbatim B6-E2.
4. Recién entonces se procede a B6-E3 (generar par + publicar `.pub`) — gate separado, requiere par criptográfico real (no en este DRAFT).

---

**Soy Cowork T2-A.** Redacté la estructura del B6-E2 DRAFT bajo instrucción T1 directa. NO declaré el custodio efectivo (acto exclusivo T1). NO generé claves. NO publiqué clave pública. NO toqué main. NO abrí PR. NO ejecuté runtime. NO activé Fase 1. NO declaré Dory muerto. Espera completado `⟦T1-DECLARA⟧` + auditoría Sabio externo NO-Cowork + firma magna T1.
