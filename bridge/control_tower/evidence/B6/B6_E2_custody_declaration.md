# B6-E2 — CUSTODY DECLARATION (T1 COMPLETED — AUDIT PENDING)

**Gate:** B6 — Key custody ed25519 del kill switch local-first `DORY_CURE_DISABLED`.
**Sub-criterio:** B6.2 + B6-E2 (definido en `B6_KEY_CUSTODY_SPEC.md`, commit `0b00d1f`).
**Estado:** `CUSTODY_DECLARATION_T1_COMPLETED_AUDIT_PENDING`.
**Co-producción:** T1 (Alfredo Góngora) declaró verbatim + Cowork T2-A redactó estructura.
**Rol Cowork:** redactor. NO auditor de este documento (anti-F16).
**Fecha estructura:** 2026-05-20. **Fecha declaración T1 verbatim:** 2026-05-20.
**Spec base:** v1.1.1 (commit `2af5fe57`) firmado Fase 0 DRAFT magna T1.

---

## §0 Nota de honestidad estructural

Este documento lo redactó Cowork T2-A; los campos de declaración los completó **T1 verbatim** (instrucción "COWORK T2-A — COMPLETAR B6-E2 CON DECLARACIÓN T1", 2026-05-20). Cowork NO auditó este documento (rol redactor). El auditor designado es Sabio externo (§7), conforme regla anti-autoauditoría del spec B6.

---

## §1 Custodio elegido (D-B6-1 — DECLARADO T1)

La clave privada ed25519 vive en **uno** de los tres custodios autorizados por B6.2. Cualquier otro lugar (filesystem plano, env var, secrets de CI, `.env`) es FAIL.

**Custodio efectivo declarado por T1 verbatim:**

> **OS Keychain en mi Mac principal, controlado exclusivamente por T1 Alfredo Góngora.**

Corresponde a la opción **(b) OS Keychain** de B6.2, con ACL restrictivo a un solo usuario humano (T1).

**Nota Cowork (redactor):** la recomendación previa Cowork era (a) hardware token; T1 eligió (b) OS Keychain. Decisión T1 soberana, registrada verbatim. El caveat de soberanía de (b) (dependencia del OS vendor) queda mitigado por el backup Shamir §3 y por la naturaleza local-first del kill switch.

---

## §2 Política de acceso

### §2.1 Quién puede acceder a la clave privada

**Delegados declarados por T1 verbatim:**

> **Ninguno por ahora. Solo T1 puede acceder a la clave privada.**

| Actor | Acceso a clave privada | Condición |
|-------|------------------------|-----------|
| T1 (Alfredo) | SÍ — **único acceso directo** | Posesión del Mac principal + credencial OS Keychain (PIN/biométrico) |
| Cowork T2-A | NO | Jamás. Solo usa la clave **pública** para verificar firmas |
| Manus E1/E2/Catastro | NO | Jamás |
| Sabios LLM | NO | Stateless, no custodian (regla B7 v0.2) |
| VERIFICADOR-001 (runtime) | NO a privada; SÍ a pública | Verifica firmas con `.pub`, nunca firma |
| Humanos delegados | NO | **Ninguno designado** (declaración T1 §2.1) |

### §2.2 Qué requiere autorización T1 explícita

- Cualquier operación de **firma** de un nuevo `DORY_CURE_DISABLED.sig` (acción magna B8(f)+B8(h)).
- Cualquier **rotación** de la clave (§4).
- Cualquier **revocación** (§5).
- Cualquier **exportación** de la clave privada fuera del OS Keychain.
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

## §3 Política de backup (D-B6-4 — DECLARADO T1)

**Declaración T1 verbatim:**

> Política aprobada: **Shamir 3-de-5**. Ejecución física de los slices queda **pendiente para etapa posterior antes de B6-E6**. Mientras no exista backup físico ejecutado, la clave **no debe usarse para Fase 1 ni runtime crítico**.

| Slice | Custodio | Tipo | Estado físico |
|-------|----------|------|---------------|
| 1 | T1 (Alfredo) | Físico personal | PENDIENTE ejecución |
| 2 | Custodio físico secundario | ⟦pendiente designación pre-B6-E6⟧ | PENDIENTE |
| 3 | Custodio físico terciario | ⟦pendiente designación pre-B6-E6⟧ | PENDIENTE |
| 4 | HSM/KMS remoto A | Vault / AWS KMS | PENDIENTE |
| 5 | HSM/KMS remoto B | GCP KMS (proveedor distinto a slice 4) | PENDIENTE |

**Reconstrucción:** ≥3 de 5 slices. Ningún actor individual reconstruye la clave solo.

**🔴 CAVEAT OPERATIVO BINARIO (declaración T1):** Mientras el backup físico Shamir 3-de-5 NO esté ejecutado, **la clave NO debe usarse para Fase 1 ni runtime crítico**. Esto es un gate adicional: B6-E6 (validación criptográfica completa) NO puede declararse PASS hasta que los 5 slices estén físicamente ejecutados. La política está aprobada; la ejecución física es etapa posterior.

---

## §4 Política de rotación (D-B6-2 — DECLARADO T1)

**Declaración T1 verbatim:** **90 días o post-incidente, lo que ocurra primero.**

| Campo | Valor |
|-------|-------|
| Frecuencia mínima | **Cada 90 días** O tras incidente (lo que ocurra primero) |
| Procedimiento | `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md` (DRAFT B6 pack) |
| Ventana de superposición | Ambas claves (vieja + nueva) válidas durante ventana documentada |
| Anclaje | El `.pub` local-first solo acepta firmas de la clave **actual** (hash anchor), no histórica (R-B6-3) |
| Clasificación | Rotación = acción magna B8(h) → bloqueada bajo `local_unreachable` |
| Ventana operativa | Rotaciones fuera de estados degradados (coherencia B8/B9) |

---

## §5 Política de revocación (DECLARADO T1)

**Declaración T1 verbatim:** **<60 minutos ante sospecha de compromiso.**

| Campo | Valor |
|-------|-------|
| Trigger | Sospecha de compromiso de la clave privada |
| SLA | Invalidar la clave actual en **<60 minutos** |
| Procedimiento | `bridge/control_tower/keys/DORY_CURE_KEY_REVOCATION_PROCEDURE.md` (DRAFT B6 pack) |
| Acciones | (1) marcar `KEY_REVOKED`; (2) notificar Cowork + Sabio auditor; (3) fallback "Dory cure halted"; (4) rotación de emergencia |
| Efecto cross-gate | `KEY_REVOKED` → VERIFICADOR-001 no valida firmas → degradación B9.6 → `DISABLED_FOR_MAGNA_ACTIONS` (B8) |

---

## §5bis Herramienta de firma (D-B6-5 — DECLARADO T1)

**Declaración T1 verbatim:** **minisign.**

Firma ed25519 con audit log nativo. Conforme B6.3 (tooling de firma digital permitido: `signify` / `minisign` / `ssh-keygen -Y sign`). Prohibido `age` / `gpg` / `openssl` como firmadores (B6.3 v0.2).

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
> La clave privada vive **exclusivamente** en el OS Keychain del Mac principal de T1 (§1), con backup Shamir 3-de-5 §3 (ejecución física pendiente). Solo la clave **pública** (`.pub`) se versiona en el repo (B6-E3, artefacto separado, aún NO generado).

Verificación "NO va al repo": **B6-E1 gitleaks keyscan PASS** (commit `c13af34`, 0 leaks en 123 commits, auditado Cowork 2026-05-20).

---

## §7 Auditor recomendado (DECLARADO T1)

**Declaración T1 verbatim:** **Opus 4.7 como auditor principal bajo caveat 2026. DeepSeek R1 como suplente.**

| Rol | Sabio | Caveat |
|-----|-------|--------|
| Auditor B6-E2 primario | **Opus 4.7** | Caveat 2026: calendario rotativo B11 formaliza Q1-2027; para el remanente 2026 Opus 4.7 actúa como auditor designado directo |
| Suplente | **DeepSeek R1** | Si Opus 4.7 no disponible |
| Restricción | **NO Cowork T2-A** | Cowork redactó este DRAFT → no puede auto-auditar (anti-F16, spec B6) |

---

## §8 Estado y firma pendiente

| Variable | Estado |
|----------|--------|
| B6-E2 status | `CUSTODY_DECLARATION_T1_COMPLETED_AUDIT_PENDING` |
| Campos T1-declara | ✅ COMPLETADOS verbatim por T1 |
| Custodio efectivo | OS Keychain Mac principal T1 (opción b) |
| Herramienta firma | minisign |
| Backup | Shamir 3-de-5 aprobado; ejecución física PENDIENTE pre-B6-E6 |
| Clave generada | NO (este documento NO genera claves) |
| Clave pública publicada | NO (B6-E3 separado, aún no generado) |
| main modificado | NO (branch lateral) |
| PR | NO abierto |
| Runtime | NO ejecutado |
| Fase 1 | NO activada (+ bloqueada adicionalmente hasta backup físico Shamir, caveat §3) |
| R1 | NO tocado |
| Dory | NO declarado muerto |
| Firma magna T1 | PENDIENTE (post-auditoría Opus 4.7) |

---

## §9 Próximo paso

1. **Auditoría:** Opus 4.7 (o DeepSeek R1 suplente) audita este B6-E2 completado — **NO Cowork** (anti-F16).
2. **Firma:** T1 firma magna verbatim B6-E2 post-auditoría verde.
3. **Pendiente operativo:** ejecución física de los 5 slices Shamir antes de B6-E6 (caveat §3). Hasta entonces, la clave NO se usa para Fase 1 ni runtime crítico.
4. **B6-E3 (separado):** generar par ed25519 con minisign + publicar `.pub` — requiere par criptográfico real, NO en este documento.

---

**Soy Cowork T2-A, rol redactor.** Sustituí los campos T1-declara por la declaración verbatim de T1. NO audité este documento. NO generé claves. NO publiqué clave pública. NO toqué main. NO abrí PR. NO ejecuté runtime. NO activé Fase 1. NO toqué R1. NO declaré Dory muerto. Estado: `CUSTODY_DECLARATION_T1_COMPLETED_AUDIT_PENDING`. Espera auditoría Sabio externo NO-Cowork + firma magna T1.
