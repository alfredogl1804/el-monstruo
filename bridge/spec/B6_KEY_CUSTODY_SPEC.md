# B6 — Key Custody ed25519 (Design Spec)

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Fuente normativa:** `bridge/control_tower/2026-05-20/manus_e2/B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §2
**Rama:** `control-tower/2026-05-20-b6-evidence-pack`
**Fecha:** 2026-05-20
**Lote:** ANTI_DORY_PARALLEL_GATES_BATCH_001

> Este documento NO canoniza B6. Es un design pack derivado y consolidado desde el closure v0.2 firmado, listo para firma magna T1. No implementa runtime. No modifica main. No declara Dory muerto.

---

## §1 Definición (verbatim closure v0.2 §2.1)

Este gate canoniza la custodia de la firma ed25519 que sella el archivo `.monstruo/kill_switches/DORY_CURE_DISABLED` (Vector C local-first del gate B1). El objetivo es que la cadena de confianza local-first no pueda ser comprometida por un atacante con acceso al repo, ni por el propio compositor del spec, ni por un agente con escritura en `.monstruo/`.

La custodia cubre cuatro fases del ciclo de vida de la clave: **generación**, **almacenamiento**, **uso** y **rotación/revocación**.

---

## §2 PASS criteria binarios (los seis deben ser `true`)

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B6.1 | Clave privada ed25519 NUNCA presente en el repo Git ni en historia ni en submódulo. Verificación: `gitleaks detect --report-format json` sobre todas las refs + `git log --all --pretty=format: --name-only \| grep -E "ed25519\|priv\|.pem"` ⇒ 0 matches sospechosas. | CI / gitleaks-staged hook |
| B6.2 | Clave privada vive en uno de tres custodios autorizados: (a) hardware token (YubiKey FIDO2 u OnlyKey con ed25519 derivation), (b) OS Keychain con ACL restrictivo a un solo usuario humano (T1), (c) HSM remoto con auditoría de acceso (Vault / AWS KMS / GCP KMS). Cualquier otro lugar (filesystem plano, env var, secrets de CI, `.env`) es FAIL. | Auditoría documental + screenshot/log custodio |
| **B6.3 (CORREGIDO v0.2)** | Clave pública ed25519 versionada en repo en `.monstruo/keys/dory_cure_kill_switch.pub` con commit firmado por T1. La firma pública debe poder validar `.monstruo/kill_switches/DORY_CURE_DISABLED.sig` con tooling estándar **de firma digital ed25519**: `signify` (OpenBSD), `minisign` (firma ed25519 con audit log nativo), o `ssh-keygen -Y sign` (firma ed25519 vía SSH key). Equivalentes determinísticos como `libsodium` signify-compatible son aceptados. **Tooling explícitamente NO permitido como firmador en B6.3:** `age`, `gpg`, `openssl`. `age` es herramienta de cifrado asimétrico (X25519/chacha20), no de firma digital — su mención aquí o en cualquier evidencia B6 invalida el test B6.6(a). | Reproducción manual + commit signature |
| B6.4 | Procedimiento de rotación documentado verbatim en `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md` con: frecuencia mínima (propuesta: cada 90 días o tras incidente), pasos exactos para regenerar par, ventana de superposición durante la cual ambas claves son válidas, comunicación a operadores. | Auditoría documental |
| B6.5 | Procedimiento de revocación de emergencia documentado: cómo invalidar la clave actual en <60 minutos cuando se sospecha compromiso, incluyendo lista de canales de notificación a Cowork/Sabios y un fallback "Dory cure halted" mientras se rota. | Auditoría documental + simulacro |
| B6.6 | Pruebas binarias de validación criptográfica ejecutadas y guardadas como evidencia: (a) prueba positiva: kill_file con firma válida producida por **`signify` o `minisign` o `ssh-keygen -Y sign`** es leído y aplicado por el agente; (b) prueba negativa-1: kill_file con firma inválida (un byte alterado) es rechazado y el agente loggea evento `KILL_FILE_INVALID_SIGNATURE`; (c) prueba negativa-2: kill_file sin firma es rechazado; (d) prueba de prioridad: kill local válido bloquea cloud-enabled (Vector C local-first wins); (e) **prueba negativa-3 v0.2:** intento de firma con `age` es rechazado y loggea evento `INVALID_SIGNATURE_TOOL_AGE_NOT_SUPPORTED`. | VERIFICADOR-001 + log evidencia |

**Aclaración doctrinal v0.2 sobre `age`:** `age` puede aparecer en el ecosistema del Monstruo en otros gates como herramienta de **cifrado** (por ejemplo, cifrar el set de hidden fixtures en B7 antes de entregarlos al runner DORY_BENCH). Pero `age` NUNCA puede aparecer como herramienta de **firma** en B6 ni en cualquier gate que exija firma digital ed25519. La distinción binaria: cifrado ≠ firma.

---

## §3 FAIL criteria (cualquiera ⇒ FAIL)

- Clave privada localizable en cualquier ref del repo Git (incluido historia y submódulos).
- Clave privada en filesystem plano sin cifrado (incluso si está en `.gitignore`).
- Clave privada en variable de entorno persistida en un secret store no auditado.
- Procedimiento de rotación ausente o sin frecuencia mínima definida.
- Procedimiento de revocación de emergencia ausente.
- Pruebas B6.6 (a)-(e) no producen evidencia firmada por VERIFICADOR-001 o el log no es reproducible.
- Cowork T2-A es simultáneamente generador, custodio y auditor de la clave (separación de roles ausente).
- **v0.2:** Cualquier evidencia B6 que liste, mencione o use `age` como herramienta de firma digital.

---

## §4 Evidencia requerida

| ID | Artefacto | Formato | Path o ubicación | Estado |
|----|-----------|---------|------------------|--------|
| B6-E1 | Reporte gitleaks sobre todas las refs + grep de patrones de claves privadas | JSON | `bridge/control_tower/evidence/B6/B6_E1_gitleaks_keyscan.json` | PENDIENTE — runtime CI |
| B6-E2 | Declaración firmada por T1 del custodio efectivo (a/b/c) y modelo de hardware/HSM | Markdown firmado git | `bridge/control_tower/evidence/B6/B6_E2_custody_declaration.md` | PENDIENTE — T1 |
| B6-E3 | Clave pública versionada | `.pub` | `.monstruo/keys/dory_cure_kill_switch.pub` | PENDIENTE — T1 + Cowork |
| B6-E4 | Procedimiento de rotación | Markdown | `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md` | DRAFT (este pack) |
| B6-E5 | Procedimiento de revocación | Markdown | `bridge/control_tower/keys/DORY_CURE_KEY_REVOCATION_PROCEDURE.md` | DRAFT (este pack) |
| B6-E6 | Logs de las 5 pruebas binarias B6.6(a)-(e) firmados por VERIFICADOR-001 | JSON Lines | `bridge/control_tower/evidence/B6/B6_E6_crypto_validation_runs.jsonl` | PENDIENTE — runtime |

---

## §5 Productores autorizados de evidencia

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B6-E1 | CI workflow (gitleaks-staged + custom keyscan job) |
| B6-E2 | T1 verbatim, firmando el custodio que él mismo controla |
| B6-E3 | T1 + Cowork T2-A en conjunto (Cowork escribe el `.pub`, T1 firma el commit con `signify` / `minisign` / `ssh-keygen -Y sign`) |
| B6-E4 | Cowork T2-A o autor NO-Cowork (Manus E2) — diseño de procedimiento |
| B6-E5 | Cowork T2-A o autor NO-Cowork — diseño de procedimiento |
| B6-E6 | VERIFICADOR-001 ejecutándose en un runner reproducible (CI o sandbox firmado), nunca el compositor del spec |

---

## §6 Auditores autorizados

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B6-E1 | Cualquier Sabio externo + Manus E2 | No restricción |
| B6-E2 | Sabio externo (Opus 4.7 o Gemini 3.1 Pro recomendado por familiaridad criptografía aplicada) | NO Cowork si fue Cowork quien declaró custodia, para evitar autoauditoría |
| B6-E3 | Cualquier actor con verificación reproducible | No restricción |
| B6-E4, B6-E5 | Sabio externo + T1 | Ambos requeridos |
| B6-E6 | Sabio externo (Opus 4.7 recomendado) + T1 | T1 firma OK final |

---

## §7 Riesgos identificados

- **R-B6-1: Filtración por commit accidental.** Si T1 o un agente ejecuta `git add` con la clave privada presente en el working tree, gitleaks-staged debe bloquear; pero si gitleaks-staged está desactivado en algún flujo (por ejemplo, durante migración), la clave puede llegar a remoto. Mitigación: gitleaks-staged es **invariante** del repo, no puede ser desactivado por un solo agente.
- **R-B6-2: Custodia humana frágil.** Si el único custodio físico (YubiKey) es perdido sin backup, kill switch local-first queda sin firma válida ⇒ Dory cure detenida hasta rotación. Mitigación: B6-E5 procedimiento de revocación + clave de respaldo en HSM remoto sellada con shamir secret sharing.
- **R-B6-3: Compromiso de custodio remoto.** Si el HSM remoto es comprometido, atacante firma kill files arbitrarios. Mitigación: B6-E5 incluye revocación remota y rotación inmediata, y ed25519 público local-first solo acepta firmas de la clave **actual** (no histórica) por hash anchor.
- **R-B6-4: Autoauditoría Cowork.** Si Cowork compone el spec, declara el custodio y audita la evidencia, perpetúa F16 estructural detectado por Opus 4.7. Mitigación: B6-E2 y B6-E6 auditados por Sabio externo.
- **R-B6-5: Sustitución silenciosa de `.pub`.** Si un actor con write en `.monstruo/keys/` reemplaza la clave pública, todos los kill files validan contra una clave del atacante. Mitigación: commit del `.pub` debe estar **firmado por T1** y protegido por branch rule de GitHub.
- **R-B6-6 (NUEVO v0.2): Confusión cifrado/firma.** Un implementador puede intentar usar `age` (herramienta de cifrado) como firmador, dado que `age` está disponible en muchos sandboxes y comparte familia ed25519/X25519 con `signify`. La firma producida por `age` no es válida en el sentido criptográfico de B6.3. Mitigación: B6.3 v0.2 explícitamente prohíbe `age` como firmador, B6.6(e) test negativo-3 prueba que el agente rechaza intentos `age` con evento `INVALID_SIGNATURE_TOOL_AGE_NOT_SUPPORTED`, FAIL criteria v0.2 incluye mención de `age` como descalificador.

---

## §8 No-go binarios

- No se diseña con clave privada en `.env`, GitHub Secrets, o secret manager sin auditoría escrita.
- No se diseña con custodio único sin procedimiento de revocación.
- No se diseña con Cowork T2-A como auditor único de B6.
- No se diseña con procedimientos verbales o no versionados.
- **v0.2:** No se diseña con `age` como herramienta de firma ed25519 (solo como herramienta de cifrado, fuera de scope B6).

---

## §9 Decisión T1 requerida (verbatim closure v0.2 §2.9)

T1 debe firmar verbatim, antes de que B6 pueda producir evidencia, los siguientes ítems:

- **D-B6-1:** Custodio elegido entre (a) hardware token, (b) OS Keychain humano, (c) HSM remoto.
- **D-B6-2:** Frecuencia de rotación (propuesta de este pack: 90 días o post-incidente).
- **D-B6-3:** Sabio externo asignado para auditoría B6-E2 y B6-E6 (propuesta: Opus 4.7 por familiaridad criptografía aplicada).
- **D-B6-4:** Política de respaldo de la clave privada (propuesta: shamir 3-of-5 entre T1 + 2 custodios físicos + 2 custodios remotos).
- **D-B6-5 (v0.2):** Herramienta de firma ed25519 elegida entre `signify` / `minisign` / `ssh-keygen -Y sign` (propuesta: `minisign` por audit log nativo).

---

## §10 Estado actual del gate

- **Veredicto:** `DRAFT_T1_PENDING`
- **Bloqueado por:** D-B6-1, D-B6-2, D-B6-3, D-B6-4, D-B6-5 (firma magna T1).
- **No-runtime:** este pack es solo diseño documental; no produce B6-E1, B6-E3, B6-E6 (estos requieren runtime CI + custodia real).
- **Productores no-runtime cubiertos:** B6-E4 y B6-E5 incluidos en este pack como DRAFT.
- **Próximo paso:** T1 firma decisiones D-B6-1..D-B6-5 ⇒ Cowork + autor NO-Cowork producen B6-E2..B6-E5 firmados ⇒ CI ejecuta B6-E1 y B6-E6 ⇒ Sabio externo audita ⇒ T1 firma magna PASS.

---

## §11 Cross-refs

- **B1** depende de B6 (cadena de firma ed25519 sobre kill switch local-first).
- **B7** depende de B6 (slices cifrados pueden requerir firma del custodio sobre el slice).
- **B8** define la política `local_unreachable` que aplica si `.monstruo/kill_switches/DORY_CURE_DISABLED.sig` es ilegible.
- **B11** Sabio auditor recomendado (Opus 4.7) coincide con auditor B6-E2 y B6-E6.

---

**Firma magna pendiente.** Este documento es DRAFT y NO canoniza B6.
