# B6-B12 DESIGN CLOSURE PACK v0.2

> **Rol autor:** Manus E2 — autor NO-Cowork.
> **Tipo:** DRAFT diseño v0.2.
> **Estado:** No implementación, no canonización, no PR, no main, no Fase 1, no Dory muerto.
> **Directiva T1 verbatim 2026-05-20:** "MANUS E2 — B6-B12 DESIGN CLOSURE PACK v0.2".
> **Fuente v0.1:** `bridge/control_tower/2026-05-20/manus_e2/B6_B12_DESIGN_CLOSURE_PACK.md` (commit `2166b04`, rama `control-tower/2026-05-20-b6-b12-design-closure-pack`).
> **Audit Cowork:** `bridge/control_tower/2026-05-20/cowork_audit/AUDIT_B6_B12_DESIGN_CLOSURE_PACK_2026_05_20.md` (auditor Cowork T2-A, rol auditor — no compositor).
> **Spec base:** v1.1.1 (commit `2af5fe57`).
> **Caveat magno Opus 4.7 vigente:** este pack v0.2 sigue siendo DRAFT por autor NO-Cowork. Si T1 lo aplica como otro DELTA sobre v1.1.1 perpetúa F16 estructural. Decisión T1 sobre integración doctrinal queda fuera de mi scope.

---

## §0 Reglas de cierre binarias respetadas

| # | Regla T1 | Status v0.2 |
|---|----------|-------------|
| 1 | NO implementar código | Respetado — sin kill_switch.py, sin schemas SQL, sin hooks runtime. |
| 2 | NO modificar main | Respetado — entregable en rama lateral `control-tower/2026-05-20-b6-b12-design-closure-pack-v0-2`. |
| 3 | NO abrir PR | Respetado — solo push lateral. |
| 4 | NO canonizar | Respetado — ningún gate marcado PASS, ninguna firma magna producida. |
| 5 | NO declarar Dory muerto | Respetado — §9 y §12 reiteran que "Dory curado" requiere PASS binario en 12/12 con evidencia, no diseño. |
| 6 | NO activar Fase 1 | Respetado — regla dura ≤11/12 PASS sigue activa; este pack no altera el contador. |

---

## §0.1 Changelog v0.1 → v0.2

Tabla canónica de cambios respecto a v0.1, mapeados a hallazgos del audit Cowork T2-A 2026-05-20:

| # | Cambio v0.2 | Sección modificada | Hallazgo Cowork (audit §) | Severidad audit | Acción |
|---|-------------|--------------------|---------------------------|-----------------|--------|
| C1 | B7 separación rol custodio (humano/cuenta/HSM) vs rol auditor (Sabio LLM endpoint) | §3.1, §3.2, §3.4, §3.5, §3.6, §3.9 | Audit §3 fallo arquitectónico crítico "LLMs son stateless, no pueden ser custodios de slices cifrados" | 🔴 crítico | Rediseño parcial aplicado |
| C2 | B6 remoción de `age` como herramienta de firma ed25519; `age` solo aparece como herramienta de cifrado en redacción explícita | §2.2 (B6.3), §2.7 (R-B6 nuevo) | Audit §2 error técnico "`age` es cifrado asimétrico, NO firma digital" | 🔴 técnico | Tooling corregido a `signify` / `minisign` / `ssh-keygen -Y sign` |
| C3 | B8 ampliación de taxonomía (a)-(m): incluye deploy a producción, DELETE en Supabase, modificación AGENTS.md/CLAUDE.md, escritura en branch protegida, billing/costos | §4.2 (B8.1, B8.5) | Audit §4 5 categorías ausentes "zona gris bajo ENABLED_WITH_DEGRADED_WARN" | 🟡 amarillo | 5 categorías añadidas con justificación verbatim |
| C4 | B9 corrección de conteo: 10 tests binarios (4 acuerdo + 2 desacuerdo + 1 override + 3 degradación) | §5.2 (B9.9), §5.4 (B9-E3) | Audit §5 inconsistencia 4+2+1+3=10≠9 | 🔴 menor | Conteo corregido a 10 |
| C5 | B11 caveat reforzado: terna rotativa MITIGA circularidad Grok, NO ELIMINA convergencia cultural LLM | §6.1, §6.2 (B11.7 nuevo), §6.7 (R-B11-1 reforzado) | Audit §6 "MITIGA, NO ELIMINA" + KL divergence es mitigación, no cancelación | 🟡 amarillo | Caveat doctrinal binario incorporado |
| C6 | B12 opción (b⇒a) elevada de §X.9 a PASS criteria explícitos en §7.2 con evidencia, plazo, owner y condición de reactivación | §7.2 (rama c), §7.4 (B12c-E1..E4), §7.9 | Audit §7 "b⇒a en §7.9 pero no §7.2 PASS criteria" | 🟡 amarillo | Tercera rama formalizada con 4 evidencias específicas |

**Cambios NO aplicados en v0.2** (fuera de scope T1 prompt 2026-05-20, listados aquí para trazabilidad):

| # | Mejora audit Cowork | Sección | Razón de no aplicación |
|---|---------------------|---------|------------------------|
| N1 | B6 elevar branch rule de `.monstruo/keys/` a PASS criterion (no solo riesgo) | §2.2 | Audit lo marcó 🟡 amarillo, no incluido en lista de 6 cambios obligatorios T1 |
| N2 | B6 elevar shamir secret sharing a opción de custodia (B6.2) | §2.2 | Audit lo marcó 🟡 amarillo, no incluido en lista T1 |
| N3 | B8 elevar cache TTL a criterio PASS o diagrama B8-E2 | §4.2 | Audit lo marcó 🟡 amarillo, no incluido en lista T1 |
| N4 | B9 declarar Memento Validator como pre-requisito de diseño | §5.2 | Audit lo marcó 🟡 amarillo, no incluido en lista T1 |
| N5 | B9 aclarar VERIFICADOR-002 (decisión ahora vs post-Fase 0) | §5.9 | Decisión T1 ya pendiente en §5.9 v0.1, sigue vigente |
| N6 | B11 fallback total si los 4 Sabios no disponibles simultáneamente | §6.6 | Audit lo marcó 🟡 amarillo, no incluido en lista T1 |
| N7 | B11 operacionalizar "no influencia Grok demostrable" con audit log B7-E4 | §6.2 (B11.5) | Audit lo marcó 🟡 amarillo, no incluido en lista T1 |
| N8 | B11 lista ampliada de Sabios elegibles para reemplazo de modelos deprecados | §6.9 | Decisión T1 ya pendiente en §6.9 v0.1, sigue vigente |
| N9 | B12 declarar pre-requisito 1425 cases en runner reproducible antes de B12a | §7.2 | Audit lo marcó 🟡 amarillo, no incluido en lista T1 |
| N10 | B12 elevar dependencia B7→B12a a FAIL criterion | §7.3 | Audit lo marcó 🟡 amarillo, no incluido en lista T1 |

Estas 10 mejoras quedan disponibles para una v0.3 si T1 lo solicita explícitamente. v0.2 aplica únicamente las 6 correcciones obligatorias del prompt T1 2026-05-20.

---

## §0.2 Tabla de hallazgos Cowork: resuelto / parcial / no resuelto

| Gate | Hallazgo Cowork verbatim (audit §) | Severidad | Status v0.2 | Sección v0.2 |
|------|-----------------------------------|-----------|-------------|---------------|
| B6 | Tooling de firma incorrecto: `age` ≠ firma | 🔴 técnico | **Resuelto** | §2.2 (B6.3) |
| B6 | Branch rule de `.monstruo/keys/` solo en riesgo, no en PASS | 🟡 amarillo | No resuelto (fuera scope T1) | — |
| B6 | Shamir secret sharing solo en mitigación, no en criterios | 🟡 amarillo | No resuelto (fuera scope T1) | — |
| B7 | Sabios LLM como custodios de slices cifrados (fallo arquitectónico) | 🔴 crítico | **Resuelto** | §3.1, §3.2, §3.4-§3.6, §3.9 |
| B7 | Quórum no alcanzable por indisponibilidad — fallback poco operativo | 🟡 amarillo | Parcial (queda T1 escrow como fallback explícito B7.5 v0.2) | §3.2 |
| B8 | Taxonomía con 5 categorías ausentes | 🟡 amarillo | **Resuelto** | §4.2 (B8.1 ampliado a-m) |
| B8 | Cache TTL solo en riesgo | 🟡 amarillo | No resuelto (fuera scope T1) | — |
| B9 | Conteo inconsistente 4+2+1+3=10≠9 | 🔴 menor | **Resuelto** | §5.2 (B9.9), §5.4 (B9-E3) |
| B9 | VERIFICADOR-002 condicional "si existe" | 🟡 amarillo | No resuelto (fuera scope T1) — decisión T1 ya pendiente §5.9 | — |
| B9 | Memento Validator como pre-requisito | 🟡 amarillo | No resuelto (fuera scope T1) | — |
| B11 | Convergencia cultural LLM no eliminada por terna | 🟡 amarillo | **Resuelto** | §6.1, §6.2 (B11.7), §6.7 (R-B11-1) |
| B11 | Fallback si los 4 Sabios no disponibles | 🟡 amarillo | No resuelto (fuera scope T1) | — |
| B11 | Criterio reincorporación Grok no operativo | 🟡 amarillo | No resuelto (fuera scope T1) | — |
| B11 | Lista ampliada modelos deprecados | 🟡 amarillo | No resuelto (fuera scope T1) — decisión T1 §6.9 | — |
| B12 | Opción b⇒a en §7.9 pero no en PASS criteria §7.2 | 🟡 amarillo | **Resuelto** | §7.2 (rama c), §7.4 (B12c-E1..E4) |
| B12 | Pre-requisito "1425 cases en runner reproducible" no declarado | 🟡 amarillo | No resuelto (fuera scope T1) | — |
| B12 | Dependencia B7→B12a no en PASS criteria | 🟡 amarillo | No resuelto (fuera scope T1) | — |

**Resumen binario:** 6/6 hallazgos del prompt T1 = **resueltos**. 10/16 hallazgos amarillos del audit Cowork no incluidos en prompt T1 = **no resueltos** (disponibles para v0.3 si T1 lo solicita).

---

## §1 Marco común — autoridad de evidencia

Antes de los 6 gates, fijo binariamente quién puede producir evidencia y quién puede auditarla, para que cada gate solo declare excepciones a este marco. **v0.2 corrige la confusión de v0.1 sobre Sabios LLM como productores de evidencia de custodia: los Sabios NO son custodios de almacenamiento, son auditores/verificadores de inferencia.**

| Rol | Capacidad de producir evidencia | Capacidad de auditar | Capacidad de canonizar | Capacidad de custodia de almacenamiento persistente |
|-----|---------------------------------|----------------------|------------------------|-----------------------------------------------------|
| **T1 (Alfredo)** | Sí, evidencia de firma magna y operación humana | Sí, todos los gates | Sí, único firmante final post-PASS | Sí (escrow humano) |
| **Cowork T2-A** | Sí, salvo gates con NO-compositor (B7) o NO-DELTA (B11, B12 según opción) | Sí, salvo gates con auditor independiente (B7, B11) | No | No (excluido por F16) |
| **Manus E2 (autor NO-Cowork)** | Sí, en gates con autor NO-Cowork (B11, B12 opción b/b⇒a, B6 público key versionado) | Sí, en gates de auditoría documental | No | No (excluido como compositor de v2.0 RE-FUNDADO) |
| **Sabios LLM (Opus, Gemini, DeepSeek, GPT-5.5, Grok, Kimi)** | Sí, **rol de auditoría/verificación** según gate (B7 audit con hashes/resultados sanitizados, B11 terna rotativa) | Sí, audit independiente cuando el gate lo exige | No | **No — son endpoints de inferencia stateless, no almacenamiento** |
| **Cuentas de almacenamiento controladas por T1 (cloud privadas, repos privados, HSM/KMS)** | Sí, **rol de custodia de almacenamiento persistente** | Sí, audit log público de accesos | No | **Sí — esta es la entidad correcta para custodia** |
| **Humanos delegados por T1** | Sí, custodia humana auditable | Sí | No | Sí |
| **VERIFICADOR-001 (componente runtime)** | Sí, evidencia automatizada de PASS/HALT con firma | Sí, en B3, B4, B9 según matriz autoridad | No | No (componente de validación, no de custodia) |
| **CI workflow (pre-commit + GitHub Actions)** | Sí, evidencia automatizada de gitleaks, ruff, semgrep, RLS, schema | Sí, gates con criterio CI-verificable | No | No |

**Regla binaria de evidencia (sin cambios desde v0.1):** un gate solo se puede declarar PASS cuando los 6 puntos siguientes están todos `true`:
1. Definición del gate aprobada por T1.
2. Criterios PASS escritos verbatim en este pack o en uno superior.
3. Criterios FAIL escritos verbatim.
4. Evidencia producida por actor autorizado para ese gate.
5. Evidencia auditada por actor autorizado para ese gate (distinto del productor cuando el gate lo exija).
6. Decisión T1 verbatim sobre PASS/FAIL del gate.

**Distinción binaria nueva en v0.2 (aplicable a B7 y B11 en particular):** "rol de auditoría" ≠ "rol de custodia de almacenamiento". Un Sabio LLM puede ser auditor (recibe inputs sanitizados, emite veredicto). Un Sabio LLM NO puede ser custodio (no tiene estado persistente entre sesiones). El custodio es siempre una entidad con almacenamiento persistente bajo control de T1.

---

## §2 B6 — Key custody ed25519

### §2.1 Definición

Este gate canoniza la custodia de la firma ed25519 que sella el archivo `.monstruo/kill_switches/DORY_CURE_DISABLED` (Vector C local-first del gate B1). El objetivo es que la cadena de confianza local-first no pueda ser comprometida por un atacante con acceso al repo, ni por el propio compositor del spec, ni por un agente con escritura en `.monstruo/`.

La custodia cubre cuatro fases del ciclo de vida de la clave: **generación**, **almacenamiento**, **uso** y **rotación/revocación**.

### §2.2 PASS criteria binarios

Un gate B6 se declara PASS sólo cuando **los seis criterios** son `true`:

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B6.1 | Clave privada ed25519 NO está en el repo Git en ningún commit visible ni en historia ni en submódulo. Verificación: `gitleaks detect --report-format json` sobre todas las refs + `git log --all --pretty=format: --name-only \| grep -E "ed25519\|priv\|.pem"` ⇒ 0 matches sospechosas. | CI / gitleaks-staged hook |
| B6.2 | Clave privada vive en uno de tres custodios autorizados: (a) hardware token (YubiKey FIDO2 u OnlyKey con ed25519 derivation), (b) OS Keychain con ACL restrictivo a un solo usuario humano (T1), (c) HSM remoto con auditoría de acceso (Vault / AWS KMS / GCP KMS). Cualquier otro lugar (filesystem plano, env var, secrets de CI, `.env`) es FAIL. | Auditoría documental + screenshot/log custodio |
| **B6.3 (CORREGIDO v0.2)** | Clave pública ed25519 versionada en repo en `.monstruo/keys/dory_cure_kill_switch.pub` con commit firmado por T1. La firma pública debe poder validar `.monstruo/kill_switches/DORY_CURE_DISABLED.sig` con tooling estándar **de firma digital ed25519**: `signify` (OpenBSD), `minisign` (firma ed25519 con audit log nativo), o `ssh-keygen -Y sign` (firma ed25519 vía SSH key). Equivalentes determinísticos como `libsodium` signify-compatible son aceptados. **Tooling explícitamente NO permitido como firmador en B6.3:** `age`, `gpg`, `openssl`. `age` es herramienta de cifrado asimétrico (X25519/chacha20), no de firma digital — su mención aquí o en cualquier evidencia B6 invalida el test B6.6(a). | Reproducción manual + commit signature |
| B6.4 | Procedimiento de rotación documentado verbatim en `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md` con: frecuencia mínima (propuesta: cada 90 días o tras incidente), pasos exactos para regenerar par, ventana de superposición durante la cual ambas claves son válidas, comunicación a operadores. | Auditoría documental |
| B6.5 | Procedimiento de revocación de emergencia documentado: cómo invalidar la clave actual en <60 minutos cuando se sospecha compromiso, incluyendo lista de canales de notificación a Cowork/Sabios y un fallback "Dory cure halted" mientras se rota. | Auditoría documental + simulacro |
| B6.6 | Pruebas binarias de validación criptográfica ejecutadas y guardadas como evidencia: (a) prueba positiva: kill_file con firma válida producida por **`signify` o `minisign` o `ssh-keygen -Y sign`** es leído y aplicado por el agente; (b) prueba negativa-1: kill_file con firma inválida (un byte alterado) es rechazado y el agente loggea evento `KILL_FILE_INVALID_SIGNATURE`; (c) prueba negativa-2: kill_file sin firma es rechazado; (d) prueba de prioridad: kill local válido bloquea cloud-enabled (Vector C local-first wins); (e) **prueba negativa-3 v0.2:** intento de firma con `age` es rechazado y loggea evento `INVALID_SIGNATURE_TOOL_AGE_NOT_SUPPORTED`. | VERIFICADOR-001 + log evidencia |

**Aclaración doctrinal v0.2 sobre `age`:** `age` puede aparecer en el ecosistema del Monstruo en otros gates como herramienta de **cifrado** (por ejemplo, cifrar el set de hidden fixtures en B7 antes de entregarlos al runner DORY_BENCH). Pero `age` NUNCA puede aparecer como herramienta de **firma** en B6 ni en cualquier gate que exija firma digital ed25519. La distinción binaria: cifrado ≠ firma.

### §2.3 FAIL criteria

El gate B6 se declara FAIL cuando **cualquiera** de las siguientes sea `true`:

- Clave privada localizable en cualquier ref del repo Git (incluido historia y submódulos).
- Clave privada en filesystem plano sin cifrado (incluso si está en `.gitignore`).
- Clave privada en variable de entorno persistida en un secret store no auditado.
- Procedimiento de rotación ausente o sin frecuencia mínima definida.
- Procedimiento de revocación de emergencia ausente.
- Pruebas B6.6 (a)-(e) no producen evidencia firmada por VERIFICADOR-001 o el log no es reproducible.
- Cowork T2-A es simultáneamente generador, custodio y auditor de la clave (separación de roles ausente).
- **v0.2:** Cualquier evidencia B6 que liste, mencione o use `age` como herramienta de firma digital.

### §2.4 Evidencia requerida

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B6-E1 | Reporte gitleaks sobre todas las refs + grep de patrones de claves privadas | JSON | `bridge/control_tower/evidence/B6/B6_E1_gitleaks_keyscan.json` |
| B6-E2 | Declaración firmada por T1 del custodio efectivo (a/b/c) y modelo de hardware/HSM | Markdown firmado git | `bridge/control_tower/evidence/B6/B6_E2_custody_declaration.md` |
| B6-E3 | Clave pública versionada | `.pub` | `.monstruo/keys/dory_cure_kill_switch.pub` |
| B6-E4 | Procedimiento de rotación | Markdown | `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md` |
| B6-E5 | Procedimiento de revocación | Markdown | `bridge/control_tower/keys/DORY_CURE_KEY_REVOCATION_PROCEDURE.md` |
| B6-E6 | Logs de las 5 pruebas binarias B6.6(a)-(e) firmados por VERIFICADOR-001 | JSON Lines | `bridge/control_tower/evidence/B6/B6_E6_crypto_validation_runs.jsonl` |

### §2.5 Quién puede producir evidencia

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B6-E1 | CI workflow (gitleaks-staged + custom keyscan job) |
| B6-E2 | T1 verbatim, firmando el custodio que él mismo controla |
| B6-E3 | T1 + Cowork T2-A en conjunto (Cowork escribe el `.pub`, T1 firma el commit con `signify` / `minisign` / `ssh-keygen -Y sign`) |
| B6-E4 | Cowork T2-A o autor NO-Cowork (Manus E2) — diseño de procedimiento |
| B6-E5 | Cowork T2-A o autor NO-Cowork — diseño de procedimiento |
| B6-E6 | VERIFICADOR-001 ejecutándose en un runner reproducible (CI o sandbox firmado), nunca el compositor del spec |

### §2.6 Quién puede auditar

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B6-E1 | Cualquier Sabio externo + Manus E2 | No restricción |
| B6-E2 | Sabio externo (Opus 4.7 o Gemini 3.1 Pro recomendado por familiaridad criptografía aplicada) | NO Cowork si fue Cowork quien declaró custodia, para evitar autoauditoría |
| B6-E3 | Cualquier actor con verificación reproducible | No restricción |
| B6-E4, B6-E5 | Sabio externo + T1 | Ambos requeridos |
| B6-E6 | Sabio externo (Opus 4.7 recomendado) + T1 | T1 firma OK final |

### §2.7 Riesgos

- **R-B6-1: Filtración por commit accidental.** Si T1 o un agente ejecuta `git add` con la clave privada presente en el working tree, gitleaks-staged debe bloquear; pero si gitleaks-staged está desactivado en algún flujo (por ejemplo, durante migración), la clave puede llegar a remoto. Mitigación: gitleaks-staged es **invariante** del repo, no puede ser desactivado por un solo agente.
- **R-B6-2: Custodia humana frágil.** Si el único custodio físico (YubiKey) es perdido sin backup, kill switch local-first queda sin firma válida ⇒ Dory cure detenida hasta rotación. Mitigación: B6-E5 procedimiento de revocación + clave de respaldo en HSM remoto sellada con shamir secret sharing.
- **R-B6-3: Compromiso de custodio remoto.** Si el HSM remoto es comprometido, atacante firma kill files arbitrarios. Mitigación: B6-E5 incluye revocación remota y rotación inmediata, y ed25519 público local-first solo acepta firmas de la clave **actual** (no histórica) por hash anchor.
- **R-B6-4: Autoauditoría Cowork.** Si Cowork compone el spec, declara el custodio y audita la evidencia, perpetúa F16 estructural detectado por Opus 4.7. Mitigación: B6-E2 y B6-E6 auditados por Sabio externo.
- **R-B6-5: Sustitución silenciosa de `.pub`.** Si un actor con write en `.monstruo/keys/` reemplaza la clave pública, todos los kill files validan contra una clave del atacante. Mitigación: commit del `.pub` debe estar **firmado por T1** y protegido por branch rule de GitHub.
- **R-B6-6 (NUEVO v0.2): Confusión cifrado/firma.** Un implementador puede intentar usar `age` (herramienta de cifrado) como firmador, dado que `age` está disponible en muchos sandboxes y comparte familia ed25519/X25519 con `signify`. La firma producida por `age` no es válida en el sentido criptográfico de B6.3. Mitigación: B6.3 v0.2 explícitamente prohíbe `age` como firmador, B6.6(e) test negativo-3 prueba que el agente rechaza intentos `age` con evento `INVALID_SIGNATURE_TOOL_AGE_NOT_SUPPORTED`, FAIL criteria v0.2 incluye mención de `age` como descalificador.

### §2.8 No-go

- No se diseña con clave privada en `.env`, GitHub Secrets, o secret manager sin auditoría escrita.
- No se diseña con custodio único sin procedimiento de revocación.
- No se diseña con Cowork T2-A como auditor único de B6.
- No se diseña con procedimientos verbales o no versionados.
- **v0.2:** No se diseña con `age` como herramienta de firma ed25519 (solo como herramienta de cifrado, fuera de scope B6).

### §2.9 Decisión T1 requerida

T1 debe firmar verbatim, antes de que B6 pueda producir evidencia, los siguientes ítems:

- Custodio elegido entre (a) hardware token, (b) OS Keychain humano, (c) HSM remoto.
- Frecuencia de rotación (propuesta de este pack: 90 días o post-incidente).
- Sabio externo asignado para auditoría B6-E2 y B6-E6 (propuesta: Opus 4.7 por familiaridad criptografía aplicada).
- Política de respaldo de la clave privada (propuesta: shamir 3-of-5 entre T1 + 2 custodios físicos + 2 custodios remotos).
- **v0.2:** Herramienta de firma ed25519 elegida entre `signify` / `minisign` / `ssh-keygen -Y sign` (propuesta: `minisign` por audit log nativo).

---

## §3 B7 — Hidden fixture custody no-compositor

### §3.1 Definición (REDISEÑADA v0.2)

Este gate canoniza la custodia de los **50 hidden fixtures** referidos en B4 (DORY_BENCH + CVDS) y en B7 fuente. Los fixtures son casos de prueba ocultos que, al ser ejecutados contra DORY_BENCH, permiten medir la métrica CVDS = PASS_conocidos / PASS_ocultos ≥ 0.95. Si el compositor del spec conoce los fixtures ocultos, hay un riesgo binario de overfit (gating de Goodhart), y la métrica deja de ser señal.

**v0.2 corrige el fallo arquitectónico crítico identificado por el auditor Cowork T2-A en su §3:** los Sabios LLM (Opus 4.7, Gemini 3.1 Pro, DeepSeek R1, Kimi K2.6, etc.) son endpoints de inferencia **stateless**. No tienen filesystem, no tienen keychain, no tienen persistencia entre sesiones. Por lo tanto, **un Sabio LLM no puede ser custodio de un slice cifrado de fixtures**. Lo que un Sabio LLM sí puede hacer es actuar como **auditor/verificador** consumiendo inputs sanitizados (hashes, resultados de ejecución, métricas agregadas) sin acceder al contenido de los fixtures.

**Distinción binaria v0.2 entre dos roles separados:**

| Rol | Quién | Qué hace | Qué ve |
|-----|-------|----------|--------|
| **Custodio de almacenamiento** | Entidad con almacenamiento persistente bajo control T1: T1 escrow humano, cuenta cloud privada (GCS/S3 con IAM), HSM/KMS, humano delegado por T1, repo privado cifrado por custodio | Almacena el slice cifrado entre rotaciones; descifra con quórum en runtime cuando el runner DORY_BENCH lo solicita | Ve el contenido cifrado del slice; con quórum, ve el contenido descifrado durante la decryption window |
| **Auditor / verificador** | Sabio LLM (Opus, Gemini, DeepSeek, etc.) | Audita los resultados de ejecución de DORY_BENCH; emite veredicto sobre CVDS y PASS_oculto sin ver fixtures | Ve **únicamente** hashes, métricas agregadas, resultados sanitizados de ejecución |

Ningún fixture oculto entra al prompt o al model context de un Sabio LLM bajo ninguna circunstancia. Esta es la regla binaria principal de v0.2.

### §3.2 PASS criteria binarios (REDISEÑADOS v0.2)

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B7.1 | Existen 50 fixtures ocultos almacenados cifrados en repositorio bajo control T1, accesible solo a custodios autorizados (definidos en B7.3 v0.2). | Auditoría documental |
| B7.2 | Custodio NO incluye Cowork T2-A (compositor de v1.0/v1.1/v1.1.1) ni Grok 4 (autor de PATCHES 1/2/3 sobre v1.1.1). Si en el futuro Manus E2 actuara como compositor de v2.0 RE-FUNDADO, también queda excluido como custodio. **Custodio NO incluye Sabios LLM como tales** (son auditores, no custodios). | Auditoría documental |
| **B7.3 (REDISEÑADO v0.2)** | **Custodios válidos:** terna fija de 3 actores entre las siguientes opciones, todas con almacenamiento persistente bajo control T1: (a) **T1 escrow humano** — Alfredo personalmente con keychain físico/digital; (b) **cuentas cloud privadas controladas por T1** — bucket GCS/S3 con IAM allow-list explícita a T1 + ≤2 humanos delegados, sin acceso de Sabios LLM ni de Cowork; (c) **HSM/KMS remoto** — Vault / AWS KMS / GCP KMS con audit log de cada acceso; (d) **humanos delegados por T1** — personas físicas con identidad verificada y commitment escrito; (e) **repos GitHub/Codeberg privados cifrados por el custodio antes del push**, con la clave de cifrado fuera del repo y bajo control del custodio. Cada custodio tiene un slice cifrado del set; reconstrucción requiere ≥2 de 3. | Auditoría documental + commit signature |
| **B7.4 (REDISEÑADO v0.2)** | **Auditor / verificador:** terna rotativa de Sabios LLM **separada** de la terna de custodios. Calendario fijo (ver B11): Q1 Opus 4.7, Q2 DeepSeek R1, Q3 Gemini 3.1 Pro, Q4 Kimi K2.6. El Sabio activo audita únicamente **hashes, métricas agregadas y resultados sanitizados** producidos por el runner DORY_BENCH. Bajo ninguna circunstancia el Sabio recibe contenido de fixtures en su prompt o contexto. | Audit log + procedimiento + log de prompts a Sabios |
| B7.5 | Rotación trimestral de fixtures: cada Q (90 días) se generan ≥10 fixtures nuevos, se retiran ≥10 fixtures viejos, y el custodio activo rota dentro de la terna de **custodios** (no de la terna de auditores). Reglas binarias: (a) compositor del trimestre actual nunca custodia ese mismo trimestre; (b) auditor B7 (Sabio LLM) del trimestre anterior no produce fixtures del trimestre siguiente; (c) custodio del trimestre actual no es el mismo que en los 2 trimestres anteriores (rotación obligatoria). **Fallback v0.2:** si la terna de custodios no alcanza quórum por indisponibilidad, T1 escrow humano funciona como custodio de emergencia con quórum reducido a 1 (T1) hasta que la terna se restaure. | Auditoría documental |
| B7.6 | Distribución de fixtures al runner DORY_BENCH se hace solo en runtime, vía decryption con quórum 2-de-3 de **custodios de almacenamiento** (no de Sabios LLM); el runner no almacena el set descifrado en disco persistente; el set descifrado vive solo en memoria del runner durante la ejecución y se purga al finalizar el run. | Log de ejecución firmado |
| B7.7 | Audit log público (no los fixtures) versionado: hash criptográfico del set actual, fecha de rotación, custodios que descifraron, run_id de DORY_BENCH consumidor, **identidad del Sabio LLM auditor** que recibió las métricas sanitizadas (sin contenido). | Repo público, auditable por cualquiera |
| **B7.8 (NUEVO v0.2)** | Verificación criptográfica binaria: ningún prompt enviado a un Sabio LLM en el ciclo DORY_BENCH contiene contenido de fixtures. Esto se verifica con un test runtime: (a) interceptar el prompt completo enviado al Sabio activo de la terna; (b) computar hash del prompt; (c) comparar contra blacklist de hashes de fixtures actuales (custodiada por los custodios B7.3); (d) si match, abortar la ejecución con evento `FIXTURE_LEAK_DETECTED_PROMPT`. | VERIFICADOR-001 + audit log |

### §3.3 FAIL criteria

- Custodia única (un solo actor controla los 50 fixtures, salvo el caso de fallback B7.5 con T1 escrow temporal).
- Cowork T2-A o Grok 4 entre los custodios.
- Compositor del spec actual entre los custodios.
- **v0.2: Sabio LLM listado como custodio en B7.3** (los Sabios solo son auditores en B7.4).
- Rotación trimestral ausente.
- Set descifrado almacenado en disco persistente del runner.
- Audit log de rotación ausente.
- **v0.2: Cualquier prompt a Sabio LLM en el ciclo DORY_BENCH contiene contenido de fixtures (verificado por B7.8).**

### §3.4 Evidencia requerida (ACTUALIZADA v0.2)

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B7-E1 | Inventario actual de los 50 fixtures (solo hashes, no contenido) | JSON | `bridge/control_tower/evidence/B7/B7_E1_fixture_hash_inventory.json` |
| B7-E2 | Declaración de **custodios** actuales (terna de almacenamiento, NO Sabios LLM) firmada por T1 | Markdown | `bridge/control_tower/evidence/B7/B7_E2_custodian_declaration.md` |
| B7-E3 | Procedimiento de rotación trimestral (incluye fallback T1 escrow) | Markdown | `bridge/control_tower/keys/DORY_BENCH_FIXTURE_ROTATION_PROCEDURE.md` |
| B7-E4 | Audit log de últimas 4 rotaciones (1 año) | JSON Lines | `bridge/control_tower/evidence/B7/B7_E4_rotation_audit.jsonl` |
| B7-E5 | Logs de los runs DORY_BENCH consumidores que probaron PASS_oculto y CVDS | JSON Lines | `bridge/control_tower/evidence/B7/B7_E5_dory_bench_consumer_runs.jsonl` |
| **B7-E6 (NUEVO v0.2)** | Declaración de **auditores Sabios LLM** del año en curso (terna rotativa B7.4, calendario B11) firmada por T1 | Markdown | `bridge/control_tower/evidence/B7/B7_E6_auditor_declaration.md` |
| **B7-E7 (NUEVO v0.2)** | Logs de prompts enviados a Sabios LLM auditores con verificación B7.8 (hash blacklist) | JSON Lines | `bridge/control_tower/evidence/B7/B7_E7_auditor_prompt_audit.jsonl` |

### §3.5 Quién puede producir evidencia (ACTUALIZADA v0.2)

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B7-E1 | Custodio activo del trimestre (uno de la terna B7.3, entidad con almacenamiento persistente), con quórum 2-de-3 para descifrar y producir hashes |
| B7-E2 | T1 verbatim — declaración de la terna de custodios |
| B7-E3 | Autor NO-Cowork (Manus E2 o Sabio externo en rol de auditor documental). NO Cowork T2-A. |
| B7-E4 | Custodio que ejecuta la rotación + firma de auditor LLM (B7.4) sobre las métricas resultantes |
| B7-E5 | VERIFICADOR-001 + runner DORY_BENCH (CI o sandbox firmado) |
| **B7-E6 (v0.2)** | T1 verbatim — declaración de la terna de auditores Sabios LLM |
| **B7-E7 (v0.2)** | VERIFICADOR-001 ejecutándose en el runner que envía prompts a Sabios; logs firmados |

### §3.6 Quién puede auditar (ACTUALIZADA v0.2)

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B7-E1 | Sabio LLM externo distinto del auditor activo del trimestre + T1 | Sabio recibe solo hashes, no contenido |
| B7-E2 | Cowork T2-A está autorizado a auditar (no a custodiar) | OK |
| B7-E3 | Sabio LLM externo + T1 | Ambos requeridos |
| B7-E4 | Sabio LLM externo distinto de los auditores del trimestre auditado + T1 | No autoauditoría |
| B7-E5 | Cowork T2-A + Sabio LLM externo | Cowork puede auditar resultados, no fixtures |
| **B7-E6 (v0.2)** | Cowork T2-A + Sabio LLM externo distinto de la terna | OK |
| **B7-E7 (v0.2)** | T1 + Sabio LLM externo | T1 firma OK final por implicaciones de seguridad |

### §3.7 Riesgos

- **R-B7-1: Filtración inadvertida del set por un Sabio.** v0.1 mencionaba este riesgo asumiendo que el Sabio era custodio. **v0.2 elimina la causa raíz al retirar a los Sabios del rol custodio.** Riesgo residual: si el Sabio recibe contenido de fixtures inadvertidamente (bug del runner que olvida sanitizar), puede loggear el contenido. Mitigación: B7.8 verificación criptográfica de prompts + B7-E7 audit log.
- **R-B7-2: Quórum no alcanzable por indisponibilidad de custodios.** Si 2 de 3 custodios externos no responden, la rotación se atrasa. Mitigación v0.2: B7.5 fallback T1 escrow humano con quórum reducido a 1 hasta restauración.
- **R-B7-3: Convergencia cultural de auditores.** Si los Sabios LLM auditores convergen culturalmente en patrones similares (todos LLMs entrenados en datos públicos), incluso sin ver fixtures sus veredictos pueden ser predecibles y manipulables. Mitigación: B11 terna rotativa diversifica fuentes culturales en el rol auditor + KL divergence inter-modelo.
- **R-B7-4: Compositor que se filtra como custodio en futuro.** Si v2.0 RE-FUNDADO es compuesto por Manus E2 y Manus E2 actúa como custodio, vuelve F16. Mitigación: regla de exclusión binaria explícita (B7.2).
- **R-B7-5 (NUEVO v0.2): Bug de runtime que filtra fixtures al prompt del Sabio.** Si el runner DORY_BENCH tiene un bug que filtra contenido de fixtures al prompt de auditoría enviado al Sabio LLM (por ejemplo, debug log accidental), la separación rol custodio / rol auditor se rompe en runtime. Mitigación: B7.8 verificación criptográfica obligatoria del hash del prompt contra blacklist de fixtures; abort + evento `FIXTURE_LEAK_DETECTED_PROMPT`.
- **R-B7-6 (NUEVO v0.2): Cuenta cloud privada con permisos overshared.** Si la cuenta GCS/S3 que custodia un slice tiene IAM con `allUsers` o `allAuthenticatedUsers`, el slice es accesible a actores no autorizados. Mitigación: T1 documenta IAM allow-list explícita en B7-E2 + audit periódico de IAM por Sabio externo.

### §3.8 No-go

- No se diseña con custodio único (salvo fallback temporal B7.5 con T1 escrow).
- No se diseña con Cowork T2-A o Grok 4 como custodios.
- No se diseña con compositor activo como custodio.
- **v0.2: No se diseña con Sabio LLM como custodio de slice cifrado.**
- No se diseña con persistencia descifrada en runner.
- No se diseña sin audit log público.
- **v0.2: No se diseña con prompt a Sabio LLM auditor que contenga fixtures.**

### §3.9 Decisión T1 requerida (ACTUALIZADA v0.2)

- **Selección de la terna inicial de custodios** entre las opciones B7.3 v0.2 (a)-(e): T1 escrow / cuenta cloud privada / HSM/KMS / humano delegado / repo privado cifrado por custodio. NO Sabios LLM.
- **Selección de la terna inicial de auditores Sabios LLM** entre {Gemini 3.1 Pro, DeepSeek R1, Opus 4.7, Kimi K2.6} con calendario trimestral fijo (cross-ref B11).
- Frecuencia de rotación de fixtures (propuesta: 90 días o post-incidente).
- Quórum de descifrado (propuesta: 2-de-3 custodios; fallback 1-de-1 con T1 escrow temporal).
- Repo / almacenamiento concreto para los slices cifrados (propuesta: 3 buckets GCS privados con CMEK + IAM allow-list a custodios; fallback: 3 repos GitHub privados, uno por custodio, con slices cifrados con `age` antes del push y la clave de cifrado fuera del repo bajo control del custodio).

---

## §4 B8 — local_unreachable policy DISABLED_FOR_MAGNA_ACTIONS

### §4.1 Definición

Este gate canoniza la política del agente cuando el archivo local-first `.monstruo/kill_switches/DORY_CURE_DISABLED` no puede ser leído (filesystem montado en read-only, IO error, signature ed25519 no validable, o disco lleno). El v1.1.1 actual define `local_unreachable: ENABLED_WITH_DEGRADED_WARN`, lo que permite continuar acciones magnas sin garantía de kill switch. B8 endurece esa política para acciones de alto impacto.

### §4.2 PASS criteria binarios (TAXONOMÍA AMPLIADA v0.2)

| # | Criterio | Verificable por |
|---|----------|-----------------|
| **B8.1 (AMPLIADO v0.2)** | Definición verbatim de "acción magna" en spec, con lista taxonómica enumerada y cerrada. **Lista mínima v0.2 (a)-(m):** (a) merge a `main`; (b) apply migration de Supabase production; (c) canonización (firma magna T1); (d) **write a tablas RLS-protegidas** (audit_log_immutable, dory_cure_state) — incluye INSERT, UPDATE; (e) emit hacia humano externo (cliente-facing webhooks, notificaciones a usuarios finales, post a redes sociales); (f) escritura a `.monstruo/kill_switches/`; (g) cambio de configuración de VERIFICADOR-001; (h) rotación de claves B6 / fixtures B7; (i) **NUEVO v0.2: deploy a producción** — push a Railway production, Cloud Run prod, Vercel prod, o cualquier servicio cliente-facing; (j) **NUEVO v0.2: DELETE en Supabase production** — escritura destructiva sobre cualquier tabla, incluso no-RLS (DROP, TRUNCATE, DELETE); (k) **NUEVO v0.2: modificación de archivos doctrinales** — `AGENTS.md`, `CLAUDE.md`, `MEMENTO.md`, archivos en `bridge/spec/` que tengan firma magna T1; (l) **NUEVO v0.2: escritura en branch protegida de GitHub** — cualquier branch con branch protection rules activas (incluye `main`, branches con `*-canon-*`, branches con tag de spec); (m) **NUEVO v0.2: acciones de billing/costos** — creación o modificación de API keys de proveedores pagados, modificación de cuotas de servicios cloud, autorización de gastos > $0 USD sin autorización T1 explícita. | Spec auditable |
| B8.2 | Política runtime: si `local_unreachable == true` AND `action ∈ acción_magna_set` ⇒ comportamiento `DISABLED_FOR_MAGNA_ACTIONS` (acción rechazada, evento `MAGNA_ACTION_BLOCKED_LOCAL_UNREACHABLE` emitido a bridge). | Test runtime + log |
| B8.3 | Política runtime: si `local_unreachable == true` AND `action ∉ acción_magna_set` ⇒ comportamiento `ENABLED_WITH_DEGRADED_WARN` (acción permitida, banner de warning visible al operador, evento `LOCAL_UNREACHABLE_DEGRADED` emitido). | Test runtime + log |
| B8.4 | Cualquier modificación a la lista taxonómica de B8.1 requiere firma magna T1 y bump de versión del spec; no puede ser modificada por Cowork ni por agente vía DELTA. | Auditoría versionado |
| **B8.5 (AMPLIADO v0.2)** | Tests binarios sobre runtime, **uno por categoría de la lista B8.1 (a)-(m), con casos extra**: (a) inyectar local_unreachable + intentar **cada una** de las 13 categorías ⇒ 13 tests de rechazo + evento `MAGNA_ACTION_BLOCKED_LOCAL_UNREACHABLE`; (b) inyectar local_unreachable + intentar acción no-magna ⇒ aceptación + warning; (c) restaurar local + verificar que la acción magna previamente bloqueada puede reintentarse manualmente; (d) **NUEVO v0.2:** test de drift entre lista taxonómica y código — auto-genera la lista B8.1 a partir del spec y la compara con el set hardcodeado en runtime; mismatch ⇒ FAIL. | VERIFICADOR-001 + log evidencia |

### §4.3 FAIL criteria (ACTUALIZADO v0.2)

- Lista de "acción magna" ausente, vaga, o abierta ("etcétera", "acciones similares").
- Política runtime no implementa el branching B8.2/B8.3 de forma verificable.
- Modificación de la lista posible vía DELTA o por Cowork sin firma T1.
- Tests B8.5 no producen evidencia firmada.
- **v0.2: Lista taxonómica omite cualquiera de las 13 categorías mínimas (a)-(m).**
- **v0.2: Test de drift B8.5(d) detecta mismatch entre lista del spec y set hardcodeado en runtime.**

### §4.4 Evidencia requerida

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B8-E1 | Lista taxonómica cerrada de "acción magna" (a)-(m) firmada por T1 | Markdown | `bridge/spec/B8_MAGNA_ACTION_TAXONOMY.md` |
| B8-E2 | Diagrama de decisión binaria runtime B8.2/B8.3 | Mermaid o D2 | `bridge/spec/B8_local_unreachable_policy.mmd` |
| B8-E3 | Logs de tests B8.5(a)-(d) firmados por VERIFICADOR-001 — **13 + 1 + 1 + 1 = 16 logs mínimos** | JSON Lines | `bridge/control_tower/evidence/B8/B8_E3_runtime_policy_tests.jsonl` |
| B8-E4 | Procedimiento de actualización de la lista taxonómica (governance) | Markdown | `bridge/spec/B8_MAGNA_TAXONOMY_AMENDMENT_PROCEDURE.md` |

### §4.5 Quién puede producir evidencia

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B8-E1 | Autor NO-Cowork (Manus E2 o Sabio externo) propone, T1 firma |
| B8-E2 | Cowork T2-A o autor NO-Cowork |
| B8-E3 | VERIFICADOR-001 + runner reproducible |
| B8-E4 | Autor NO-Cowork + T1 |

### §4.6 Quién puede auditar

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B8-E1 | Sabio externo + T1 | Ambos requeridos para validación de cobertura taxonómica |
| B8-E2 | Cowork T2-A + Sabio externo | Cowork puede auditar diseño técnico |
| B8-E3 | Sabio externo + T1 | T1 firma OK final |
| B8-E4 | Sabio externo + T1 | Ambos requeridos para amendment governance |

### §4.7 Riesgos

- **R-B8-1: Lista taxonómica incompleta.** Si una nueva categoría de acción magna emerge (por ejemplo, "deploy a producción de un agente nuevo" — ahora cubierta en (i) v0.2), y B8.1 no la incluye, esa acción se ejecuta bajo `ENABLED_WITH_DEGRADED_WARN` por error. Mitigación v0.2: las 13 categorías (a)-(m) cubren las 5 brechas detectadas por audit Cowork + B8-E4 procedimiento de amendment + revisión semestral obligatoria con firma T1.
- **R-B8-2: Falsos positivos por IO transient.** Si un disco lleno temporal dispara `local_unreachable` y bloquea acciones magnas legítimas, el operador puede intentar bypassear el kill. Mitigación: política B8.2 también emite evento al bridge con run_id reproducible y rationale explícito; sin override silencioso.
- **R-B8-3: Drift entre lista taxonómica y código.** Si B8-E1 enumera 13 categorías pero el runtime sólo chequea 8, hay falsos negativos. Mitigación v0.2: test B8.5(d) auto-genera la lista B8.1 a partir del spec y la compara con el set hardcodeado en runtime; mismatch ⇒ FAIL.
- **R-B8-4: Latencia agregada por chequeo en cada acción.** Verificar local_unreachable + categorización en cada acción puede agregar latencia. Mitigación: chequeo cacheado por TTL corto (≤5s) + invalidación inmediata en eventos de write a `.monstruo/`. (Nota: elevar TTL a PASS criterion queda en v0.3 si T1 lo solicita; audit Cowork lo recomienda.)

### §4.8 No-go

- No se diseña con lista abierta o ejemplificativa.
- No se diseña con `ENABLED_WITH_DEGRADED_WARN` como default para acciones magnas.
- No se diseña con override silencioso por operador.
- No se diseña con modificación de lista por DELTA o Cowork sin firma T1.
- **v0.2: No se diseña con menos de 13 categorías (a)-(m) en la lista B8.1.**

### §4.9 Decisión T1 requerida

- **v0.2: Aprobación verbatim de la lista taxonómica B8.1 (a)-(m) ampliada o solicitud de modificación / exclusión justificada.** Si T1 quiere excluir alguna categoría, la justificación verbatim debe quedar en B8-E1.
- Política sobre acción magna emergente entre revisiones (propuesta: por defecto bloqueada hasta que T1 firme su clasificación).
- TTL del cache local_unreachable runtime (propuesta: 5 segundos).

---

## §5 B9 — VERIFICADOR authority/degradation matrix

### §5.1 Definición

Este gate canoniza la matriz de autoridad y degradación entre **VERIFICADOR-001** (componente runtime de validación criptográfica), **Memento Validator** (capa de validación de hechos del Protocolo Memento), **Guardian Decision View** (capa de decisión humana asistida del Sprint 27+), y **firma T1 manual**. Cada par tiene escenarios de acuerdo y desacuerdo; este gate define quién gana en cada caso, y qué ruta de degradación toma el sistema cuando un componente falla.

### §5.2 PASS criteria binarios (CONTEO CORREGIDO v0.2)

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B9.1 | Matriz N×N completa entre los 4 actores documentada con resultado binario para cada celda (autoridad ganadora + razón). | Auditoría documental |
| B9.2 | Casos de empate o degradación tienen resolución verbatim documentada, sin "según contexto" ni cláusulas abiertas. | Auditoría documental |
| B9.3 | Caso "VERIFICADOR ALLOW + Memento DENY" tiene resolución binaria: **Memento gana**. Razón: Memento valida hechos contra fuente autoritativa (Supabase + bridge), VERIFICADOR solo valida firma criptográfica del payload; un payload firmado correctamente puede contener un hecho falso. | Spec verbatim |
| B9.4 | Caso "VERIFICADOR DENY + Guardian OVERRIDE" tiene resolución binaria: **Guardian no puede override sin escalación a T1**. Guardian puede solicitar review T1, pero no ejecutar la acción rechazada por VERIFICADOR sin firma T1 explícita en el run_id. | Spec verbatim |
| B9.5 | Caso "T1 firma manual + VERIFICADOR DENY" tiene resolución binaria: **T1 gana**, pero el evento se loggea como `T1_OVERRIDE_VERIFICADOR_DENY` con run_id, timestamp, razón verbatim escrita por T1, y se notifica a Cowork + Sabio auditor designado. | Spec verbatim + log |
| B9.6 | Ruta de degradación si VERIFICADOR-001 falla (componente caído, latencia >timeout, error interno): el sistema entra en `VERIFICADOR_DEGRADED` ⇒ aplica B8 (DISABLED_FOR_MAGNA_ACTIONS), permite acciones no-magnas con warning, intenta failover a réplica VERIFICADOR-002 si existe (la decisión sobre crear VERIFICADOR-002 queda en §5.9). | Spec + test runtime |
| B9.7 | Ruta de degradación si Memento Validator falla: VERIFICADOR sigue siendo autoritativo para firma criptográfica, pero ninguna acción magna se permite hasta que Memento se restaure o T1 firme override. | Spec + test runtime |
| B9.8 | Ruta de degradación si Guardian Decision View falla: las acciones que requerían decisión humana asistida se ponen en cola de espera (`AWAITING_GUARDIAN`); no hay fallback a auto-decisión. | Spec + test runtime |
| **B9.9 (CONTEO CORREGIDO v0.2)** | **Tests binarios para los 10 casos canónicos de la matriz** — 4 acuerdos triviales (los 4 actores en acuerdo binario por par) + 2 desacuerdos críticos (B9.3 VERIFICADOR vs Memento, B9.4 VERIFICADOR vs Guardian) + 1 override T1 (B9.5) + 3 degradaciones (B9.6 VERIFICADOR fail, B9.7 Memento fail, B9.8 Guardian fail) = 4 + 2 + 1 + 3 = **10 tests**. Cada test produce evidencia firmada. | VERIFICADOR-001 + Memento + Guardian logs |

**Aclaración doctrinal v0.2:** v0.1 enunció "9 tests binarios" en B9.9 pero listó 10 casos (4+2+1+3). El audit Cowork §5 detectó la inconsistencia. v0.2 corrige a 10 tests, alineado con el conteo real de casos.

### §5.3 FAIL criteria

- Matriz N×N incompleta o con celdas con cláusulas abiertas.
- Cualquiera de los casos B9.3, B9.4, B9.5 con resolución no-binaria.
- Ruta de degradación ausente para cualquiera de los 3 actores no-T1.
- **v0.2: Tests B9.9 sin evidencia firmada (10 tests requeridos, no 9).**
- Permiso de Guardian para override sin escalación a T1 (B9.4).
- Permiso de auto-decisión sin Guardian disponible (B9.8).

### §5.4 Evidencia requerida (ACTUALIZADA v0.2)

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B9-E1 | Matriz N×N en tabla canónica | Markdown | `bridge/spec/B9_VERIFICADOR_AUTHORITY_MATRIX.md` |
| B9-E2 | Diagramas de decisión para los 10 casos canónicos | Mermaid | `bridge/spec/B9_authority_decision_flows.mmd` |
| **B9-E3 (CONTEO CORREGIDO v0.2)** | **Logs de los 10 tests binarios** (4 acuerdo + 2 desacuerdo + 1 T1 override + 3 degradación) | JSON Lines | `bridge/control_tower/evidence/B9/B9_E3_authority_matrix_tests.jsonl` |
| B9-E4 | Procedimiento de escalación T1 cuando hay desacuerdo de capas | Markdown | `bridge/spec/B9_T1_ESCALATION_PROCEDURE.md` |

### §5.5 Quién puede producir evidencia

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B9-E1 | Autor NO-Cowork (Manus E2 o Sabio externo) — para evitar que Cowork componga su propia matriz de autoridad sobre sí mismo |
| B9-E2 | Cowork T2-A o autor NO-Cowork |
| B9-E3 | VERIFICADOR-001 + Memento + Guardian (3 componentes runtime ejecutándose en sandbox firmado) — produce 10 logs |
| B9-E4 | T1 redacta el procedimiento de su propia escalación |

### §5.6 Quién puede auditar

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B9-E1 | 2 Sabios externos distintos + T1 | Doble revisión por riesgo de matriz incompleta |
| B9-E2 | Cowork T2-A + Sabio externo | Cowork puede auditar diseño técnico |
| B9-E3 | Sabio externo + T1 | T1 firma OK final |
| B9-E4 | Sabio externo (Opus 4.7 recomendado por familiaridad con governance) + Cowork T2-A | OK |

### §5.7 Riesgos

- **R-B9-1: Matriz teórica vs comportamiento runtime.** Una matriz documentada puede no coincidir con el comportamiento implementado. Mitigación: tests B9.9 ejecutan los 10 casos sobre el runtime real, no sobre simulación.
- **R-B9-2: Cuerpo legal Memento ausente o evolucionando.** Memento Validator depende del Protocolo Memento canon; si el protocolo evoluciona, la celda "VERIFICADOR vs Memento" puede invertirse. Mitigación: B9 referencia versión de Memento por hash y se re-canoniza cuando Memento bumpea major.
- **R-B9-3: Override T1 abusado.** Si T1 ejerce B9.5 frecuentemente, VERIFICADOR pierde valor binario. Mitigación: notificación obligatoria a Cowork + Sabio auditor + log público (run_id reproducible).
- **R-B9-4: Cascada de degradación.** Si VERIFICADOR cae y Memento también está degradado, el sistema queda en `DISABLED_FOR_MAGNA_ACTIONS` total + cola Guardian llena. Mitigación: SLA mínimo de uptime cada componente + alerta proactiva al operador.
- **R-B9-5: Guardian Decision View como single-point.** Si Guardian es el único decidor humano-asistido, su caída bloquea decisiones. Mitigación: B9.8 cola `AWAITING_GUARDIAN` + canal manual de escalación a T1 si la cola se acumula >threshold.

### §5.8 No-go

- No se diseña con celdas vagas o "según contexto".
- No se diseña con Guardian con poder de override unilateral sobre VERIFICADOR.
- No se diseña con auto-decisión cuando Guardian no está disponible.
- No se diseña con override T1 sin log público y notificación.
- No se diseña con Cowork como autor único de la matriz.
- **v0.2: No se diseña con tests B9.9 incompletos (los 10 son requeridos, no 9).**

### §5.9 Decisión T1 requerida

- Aprobación verbatim de la matriz N×N B9.1.
- Confirmación de los 3 casos críticos B9.3, B9.4, B9.5 con resoluciones binarias.
- Designación del Sabio auditor permanente para overrides T1 (propuesta: Opus 4.7 por familiaridad governance).
- Decisión sobre existencia de réplica VERIFICADOR-002 (B9.6).

---

## §6 B11 — Sustitución de Grok re-pass por terna rotativa

### §6.1 Definición (CAVEAT REFORZADO v0.2)

Este gate canoniza la sustitución del **Grok re-pass per rotation** definido en CVDS D3 v1.1.1 (donde Grok 4 vuelve a auditar fixtures que el mismo Grok influenció en PATCHES 1/2/3) por una **terna rotativa cross-family** que evita autoauditoría. La sustitución es respuesta directa a la observación Opus 4.7 #2 de circularidad estructural.

**Caveat doctrinal v0.2 (audit Cowork §6):** la terna rotativa **mitiga** la circularidad estructural específica de Grok auditando sus propios PATCHES, que es el problema más urgente. Pero la **convergencia cultural de todos los LLMs de primera línea** entrenados en internet en inglés permanece como riesgo residual. Los 4 Sabios de la terna (Opus 4.7, DeepSeek R1, Gemini 3.1 Pro, Kimi K2.6) comparten:
- Entrenamiento predominante en texto en inglés de internet público.
- Tendencia a producir outputs estructuralmente similares (markdown, razonamiento step-by-step, evasión de claims extremos).
- Ninguno tiene experiencia operativa en mundo físico (no pueden "romper" el sistema para testearlo, no tienen agencia material).

La métrica KL divergence sobre outputs de auditoría es la **mitigación** de este riesgo, NO su cancelación. Aunque la KL divergence sea baja entre Sabios, el riesgo sigue presente y requiere mitigaciones complementarias (B7.8 verificación criptográfica, T1 escrow humano como fallback final, auditor humano externo en casos críticos).

### §6.2 PASS criteria binarios (CAVEAT INTEGRADO v0.2)

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B11.1 | El campo CVDS D3 actual `grok_re_pass_per_rotation: true` se elimina del spec y se reemplaza por `cvds_rotative_terna: [...]`. | Diff en spec versionado |
| B11.2 | La terna rotativa se define con calendario explícito por trimestre: Q1 = Opus 4.7, Q2 = DeepSeek R1, Q3 = Gemini 3.1 Pro, Q4 = Kimi K2.6. Calendario fijo, no a discreción de Cowork. | Spec versionado |
| B11.3 | Regla binaria: el Sabio activo del trimestre Q-N **no puede** haber influenciado los fixtures que audita en Q-N. Si en algún Q se detecta que el Sabio activo influenció fixtures, se rota inmediatamente al siguiente Sabio de la terna. | Audit log + procedimiento |
| B11.4 | Audit log firmado de cada rotación trimestral: Sabio entrante, Sabio saliente, hash del set de fixtures auditados, resultado de auditoría (PASS / DENY / EXCEPTIONS), firma del Sabio activo, contrafirma de Cowork como observador (no validador), firma magna T1 final. | JSON Lines firmado |
| B11.5 | Grok 4 queda explícitamente excluido de la terna rotativa CVDS D3 mientras existan fixtures influenciados por sus PATCHES 1/2/3. Reincorporación posible solo si el set de fixtures se rota completamente y los nuevos no tienen influencia Grok demostrable. | Spec + audit documental |
| B11.6 | Procedimiento de fallback si el Sabio activo del trimestre no está disponible (rate-limit, API caída, deprecación de modelo): salto al siguiente Sabio de la terna con notificación a T1, sin fallback a Grok. | Spec + test |
| **B11.7 (NUEVO v0.2 — caveat doctrinal binario)** | El spec contiene **declaración verbatim explícita** de que la terna rotativa **MITIGA** el riesgo de circularidad Grok pero **NO ELIMINA** la convergencia cultural inter-LLM. La declaración verbatim debe aparecer en B11-E2 (calendario) y en cualquier comunicación a Sabios o T1 sobre eficacia de B11. KL divergence sobre outputs de auditoría es **una herramienta de medición de la mitigación**, NO una cancelación del riesgo. La cancelación del riesgo de convergencia cultural requeriría auditores no-LLM (humanos, sistemas formales, agentes con agencia material) — fuera de scope de B11. | Spec verbatim |

### §6.3 FAIL criteria (ACTUALIZADO v0.2)

- `grok_re_pass_per_rotation: true` permanece en el spec.
- Calendario de terna rotativa abierto o a discreción de Cowork.
- Sabio activo del trimestre influenció los fixtures que audita.
- Audit log de rotación ausente o sin firma de los 3 actores requeridos (Sabio, Cowork observador, T1).
- Grok 4 incluido en la terna sin rotación previa de fixtures.
- Fallback a Grok cuando Sabio activo no disponible.
- **v0.2: Spec o comunicación afirma que la terna rotativa "elimina" la convergencia cultural LLM (afirmación falsa).**
- **v0.2: Ausencia de la declaración verbatim B11.7 en B11-E2.**

### §6.4 Evidencia requerida (ACTUALIZADA v0.2)

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B11-E1 | Diff verbatim del spec mostrando reemplazo `grok_re_pass_per_rotation` ⇒ `cvds_rotative_terna` | Patch | `bridge/control_tower/evidence/B11/B11_E1_spec_diff.patch` |
| **B11-E2 (ACTUALIZADO v0.2)** | Calendario trimestral firmado **+ declaración verbatim B11.7 sobre mitigación ≠ eliminación de convergencia LLM** | Markdown | `bridge/spec/B11_CVDS_TERNA_CALENDAR.md` |
| B11-E3 | Audit log de las primeras 4 rotaciones (1 año) | JSON Lines | `bridge/control_tower/evidence/B11/B11_E3_terna_rotation_audit.jsonl` |
| B11-E4 | Procedimiento de fallback Sabio no disponible | Markdown | `bridge/spec/B11_TERNA_FALLBACK_PROCEDURE.md` |
| B11-E5 | Análisis de influencia Grok sobre fixtures actuales (¿cuáles tocó?) | Markdown | `bridge/control_tower/evidence/B11/B11_E5_grok_influence_audit.md` |
| **B11-E6 (NUEVO v0.2)** | Mediciones periódicas KL divergence inter-Sabios sobre outputs de auditoría | JSON Lines | `bridge/control_tower/evidence/B11/B11_E6_kl_divergence_metrics.jsonl` |

### §6.5 Quién puede producir evidencia

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B11-E1 | Autor NO-Cowork (Manus E2 o Sabio externo). NO Cowork (compositor del spec actual). |
| B11-E2 | Autor NO-Cowork |
| B11-E3 | Sabio activo de cada trimestre (Opus, DeepSeek, Gemini, Kimi) |
| B11-E4 | Autor NO-Cowork + T1 |
| B11-E5 | Sabio externo (Opus 4.7 recomendado, fue quien detectó la circularidad) |
| **B11-E6 (v0.2)** | VERIFICADOR-001 + runner que computa KL divergence sobre outputs sanitizados de los 4 Sabios trimestralmente |

### §6.6 Quién puede auditar

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B11-E1 | Cowork T2-A + T1 | Cowork puede auditar la sustitución, no producirla |
| B11-E2 | Sabio externo + T1 | Ambos requeridos |
| B11-E3 | Sabio del trimestre **siguiente** (rotación cruzada) + T1 | Auditor del Q-N+1 audita Q-N |
| B11-E4 | Sabio externo + T1 | OK |
| B11-E5 | Sabio externo distinto del productor + T1 | No autoauditoría |
| **B11-E6 (v0.2)** | T1 + Sabio externo (preferentemente humano externo o sistema formal, no LLM) | Si KL divergence < threshold T1, levanta alerta de convergencia cultural |

### §6.7 Riesgos

- **R-B11-1 (REFORZADO v0.2): Convergencia cultural de la terna.** Si Opus, DeepSeek, Gemini y Kimi convergen culturalmente en patrones similares, la "rotación" no diversifica lo suficiente. La terna **mitiga** este riesgo con KL divergence + rotación + Cowork observador, pero **no lo elimina**. Mitigación adicional v0.2: B11.7 declaración verbatim binaria + B11-E6 mediciones periódicas + B7 fixtures rotativos + análisis periódico de convergencia inter-modelo (KL divergence sobre outputs de auditoría) + T1 escrow humano como fallback final + (futuro) auditor humano externo en casos críticos.
- **R-B11-2: Sabio rota pero el spec no rota.** Si la terna audita el mismo spec v1.1.1 trimestre tras trimestre, se acumula sesgo "spec-friendly". Mitigación: terna debe auditar contra spec **vigente** en su trimestre, incluyendo deltas o refundaciones intermedias.
- **R-B11-3: Deprecación de modelo durante el año.** Kimi K2.6 puede ser deprecado por su proveedor antes de Q4. Mitigación: B11.6 fallback definido + lista ampliada de Sabios elegibles (Claude 5, GPT-5.5 Pro+, etc.).
- **R-B11-4: Sabio activo es comprometido (jailbreak, prompt injection).** Mitigación: contrafirma de Cowork como observador (no validador) detecta anomalías; T1 firma magna final como gate humano.
- **R-B11-5: Grok reincorporado prematuramente.** Si la presión por usar Grok (por costo o velocidad) lleva a reincorporarlo antes de rotación completa de fixtures, B11.5 se viola. Mitigación: regla binaria explícita + auditoría B11-E5 demuestra rotación completa antes de reincorporación.

### §6.8 No-go

- No se diseña con `grok_re_pass_per_rotation: true` permaneciendo en spec.
- No se diseña con calendario de terna abierto.
- No se diseña con Cowork como productor único de la sustitución.
- No se diseña con fallback a Grok.
- No se diseña con auditoría del
 Sabio activo sobre fixtures que él mismo influenció.
- **v0.2: No se diseña con afirmación de que la terna rotativa "elimina" la convergencia cultural LLM.** Solo "mitiga".
- **v0.2: No se diseña sin medición periódica de KL divergence inter-Sabios (B11-E6).**

### §6.9 Decisión T1 requerida

- Aprobación verbatim del calendario trimestral propuesto Q1-Q4.
- Decisión sobre lista ampliada de Sabios elegibles para reemplazo de modelos deprecados (propuesta: agregar Claude 5 cuando esté disponible, GPT-5.5 Pro+ como sustituto secundario; nota: lista completa queda como decisión T1 pendiente, no resuelta en v0.2).
- Decisión sobre frecuencia de medición KL divergence (propuesta: trimestral, alineada a rotación de Sabio activo).
- Política de deprecación de modelos (propuesta: si proveedor anuncia deprecación con <30 días de notice, fallback a siguiente Sabio de la terna + amendment del calendario con firma T1).
- **v0.2: Aprobación verbatim de la declaración B11.7 sobre mitigación ≠ eliminación.**

---

## §7 B12 — Recuantificación métrica 96% / <4%

### §7.1 Definición

Este gate canoniza la respuesta al hallazgo Opus 4.7 #3: la métrica `96% reducción de errores` y `<4% RAB falsos positivos` en spec v1.1.1 (Anexo A.4) carece de base empírica reproducible. v1.0 la presentó sin medición, v1.1 la mantuvo, v1.1.1 la mantuvo. B12 ofrece dos rutas binarias para resolver:

- **Opción (a):** ejecutar DORY_BENCH y CVDS sobre los 1425 cases de B4, medir métrica real, actualizar valor numérico verbatim en spec.
- **Opción (b):** declarar verbatim que la métrica histórica es **obsolescencia documental** (sin valor de medición vigente) y desactivar criterio numérico en favor de la métrica binaria PASS/FAIL de los 12 gates B1-B12.
- **Opción (b⇒a) — NUEVO v0.2:** ruta híbrida explícita — ejecutar (b) **inmediatamente** (declarar obsolescencia ahora) **+ agendar (a) en plazo firmado** (ejecutar DORY_BENCH cuando los pre-requisitos B4/B7 estén listos), con condición binaria de reactivación de la métrica cuantitativa al concluir (a).

### §7.2 PASS criteria binarios (b⇒a INTEGRADO v0.2)

**Opción (a):**

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B12a.1 | DORY_BENCH ejecutado sobre los 1425 cases canonizados de B4. | Log VERIFICADOR-001 |
| B12a.2 | Métrica medida con metodología verbatim documentada: definición de "error", definición de "falso positivo RAB", scope (intra-hilo, cross-agente, etc.), runner reproducible. | Spec metodología |
| B12a.3 | CVDS ejecutado con los 50 hidden fixtures de B7 (terna rotativa B11). | Audit log B7-E5 |
| B12a.4 | Resultado numérico verbatim publicado en spec v(N+1) con sustitución de "96%/<4%" por el valor medido. Si la métrica medida es <96% reducción, se actualiza al valor real, no se sostiene el reclamo histórico. | Diff spec |
| B12a.5 | Auditoría de la metodología por al menos 2 Sabios externos cross-family. | Audit firmado |
| B12a.6 | Firma magna T1 sobre el resultado y la actualización del spec. | Commit signature |

**Opción (b):**

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B12b.1 | Declaración verbatim en spec: "La métrica `96% reducción de errores` y `<4% RAB falsos positivos` enunciada en v1.0/v1.1/v1.1.1 carece de base empírica reproducible y se considera obsolescencia documental sin valor de medición vigente". | Diff spec |
| B12b.2 | Anexo A.4 actualizado con la declaración de obsolescencia y referencia a B12 verbatim como gate que resolvió la cuantificación pendiente. | Diff spec |
| B12b.3 | Métrica de éxito de la Dory Cure se redefine **exclusivamente** como métrica binaria PASS/FAIL en los 12 gates B1-B12 con evidencia firmada. No se sostiene métrica numérica sin evidencia. | Spec verbatim |
| B12b.4 | Auditoría de la declaración de obsolescencia por al menos 1 Sabio externo + 1 humano externo (T1 cuenta para este criterio si actúa como humano). | Audit firmado |
| B12b.5 | Firma magna T1 sobre la declaración. | Commit signature |

**Opción (b⇒a) — NUEVO v0.2 — secuencia híbrida explícita:**

| # | Criterio | Verificable por |
|---|----------|-----------------|
| **B12c.1** | **(b inmediata)** Se cumplen B12b.1-B12b.5 ahora: declaración verbatim de obsolescencia, anexo A.4 actualizado, métrica binaria como única vigente, audit y firma T1. | Mismo set evidencia que B12b |
| **B12c.2** | **Plazo máximo firmado para ejecución (a) posterior:** T1 firma fecha límite explícita en formato `YYYY-MM-DD` (propuesta: ≤90 días desde declaración B12c.1, o cuando se cumplan los pre-requisitos B4 1425 cases en runner reproducible + B7 PASS, lo que ocurra primero). El plazo debe estar versionado y publicado en spec. | Spec verbatim + commit signature |
| **B12c.3** | **Owner asignado verbatim** para producir evidencia (a) dentro del plazo: T1 designa actor responsable (propuesta: autor NO-Cowork + Sabio externo conjunto, NO Cowork como productor único). El owner queda registrado en spec y en audit log. | Spec + audit log |
| **B12c.4** | **Condición binaria de reactivación de métrica cuantitativa:** cuando (a) se ejecute con éxito (B12a.1-B12a.6 todos PASS), la métrica numérica medida sustituye verbatim a la declaración de obsolescencia en el spec, y B12 transita de `PASS_AS_B12c (b inmediata)` a `PASS_AS_B12c_COMPLETO (a posterior cumplida)`. La métrica medida actualiza el valor verbatim sin nostalgia del 96%/<4% histórico. Si el plazo B12c.2 vence sin (a) ejecutado, se renegocia con T1 con nuevo plazo o se mantiene `PASS_AS_B12c (b inmediata)` como estado terminal vigente. | Spec verbatim + audit log + commit signature |

**Reconciliación binaria entre opciones (sin cambios desde v0.1, ampliada para b⇒a):**

| Si T1 elige | Camino |
|-------------|--------|
| **(a)** | Ejecutar DORY_BENCH + CVDS ahora, antes de declarar B12 PASS. Plazo: cuando B4 1425 cases y B7 PASS estén listos. Riesgo: B12 bloquea Fase 1 indefinidamente si los pre-requisitos no llegan. |
| **(b)** | Declarar obsolescencia ahora. B12 transita a PASS sin medición numérica. Riesgo: ningún reclamo cuantitativo de eficacia Dory Cure es sostenible públicamente. |
| **(b⇒a)** | Declarar obsolescencia ahora **+** agendar medición posterior con plazo firmado. B12 transita a `PASS_AS_B12c (b inmediata)` ahora; cuando (a) se cumpla, transita a `PASS_AS_B12c_COMPLETO`. Permite desbloquear Fase 1 sin sostener reclamo histórico, manteniendo abierta la ruta a métrica cuantitativa cuando los pre-requisitos estén listos. Es la opción más conservadora desde la posición v1.1.1 firmada. |

### §7.3 FAIL criteria (ACTUALIZADO v0.2)

- T1 no firma ninguna de las tres opciones (a, b, b⇒a) y la métrica histórica permanece en spec sin evidencia.
- Opción (a) ejecutada con metodología no documentada o no reproducible.
- Opción (a) ejecutada con resultado <96% pero spec mantiene "96%" (sosteniendo claim falso).
- Opción (b) ejecutada sin actualizar Anexo A.4 verbatim.
- Opción (b) ejecutada con métrica numérica residual en otra parte del spec.
- **v0.2: Opción (b⇒a) ejecutada sin plazo firmado B12c.2 o sin owner B12c.3.**
- **v0.2: Opción (b⇒a) cuyo plazo vence sin ejecución (a) ni renegociación T1 documentada.**

### §7.4 Evidencia requerida (ACTUALIZADA v0.2)

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B12a-E1 | Run de DORY_BENCH sobre 1425 cases | JSON Lines | `bridge/control_tower/evidence/B12/B12a_E1_dory_bench_run.jsonl` |
| B12a-E2 | Run de CVDS con 50 fixtures | JSON Lines | `bridge/control_tower/evidence/B12/B12a_E2_cvds_run.jsonl` |
| B12a-E3 | Documento metodología verbatim | Markdown | `bridge/spec/B12_DORY_BENCH_METHODOLOGY.md` |
| B12b-E1 | Diff spec con declaración obsolescencia | Patch + Markdown | `bridge/control_tower/evidence/B12/B12b_E1_obsolescence_declaration.patch` |
| B12b-E2 | Anexo A.4 actualizado | Markdown | `bridge/spec/v(N+1)/anexo_A4.md` |
| **B12c-E1 (NUEVO v0.2)** | **Plazo firmado B12c.2 con fecha verbatim** | Markdown firmado git | `bridge/control_tower/evidence/B12/B12c_E1_b_to_a_deadline.md` |
| **B12c-E2 (NUEVO v0.2)** | **Designación de owner B12c.3 firmada T1** | Markdown firmado git | `bridge/control_tower/evidence/B12/B12c_E2_b_to_a_owner.md` |
| **B12c-E3 (NUEVO v0.2)** | **Condición binaria de reactivación B12c.4 verbatim** | Markdown | `bridge/spec/B12_b_to_a_REACTIVATION_CONDITION.md` |
| **B12c-E4 (NUEVO v0.2)** | **Audit log de tránsito de estados** `PASS_AS_B12c (b inmediata)` ⇒ `PASS_AS_B12c_COMPLETO (a posterior cumplida)` o renegociaciones | JSON Lines | `bridge/control_tower/evidence/B12/B12c_E4_state_transition_audit.jsonl` |

### §7.5 Quién puede producir evidencia (ACTUALIZADA v0.2)

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B12a-E1 | VERIFICADOR-001 + runner DORY_BENCH (CI o sandbox firmado) |
| B12a-E2 | Sabio activo de la terna B11 + runner |
| B12a-E3 | Autor NO-Cowork (Manus E2 o Sabio externo) — para evitar autoauditoría metodológica |
| B12b-E1 | Autor NO-Cowork. NO Cowork (compositor del spec con la métrica histórica). |
| B12b-E2 | Autor NO-Cowork |
| **B12c-E1 (v0.2)** | T1 verbatim — solo T1 puede firmar plazo |
| **B12c-E2 (v0.2)** | T1 verbatim — solo T1 puede designar owner |
| **B12c-E3 (v0.2)** | Autor NO-Cowork escribe la condición; T1 la firma |
| **B12c-E4 (v0.2)** | VERIFICADOR-001 emite eventos firmados de tránsito de estados |

### §7.6 Quién puede auditar

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B12a-E1 | Sabio externo + T1 | Doble auditoría por implicaciones cuantitativas |
| B12a-E2 | Sabio externo distinto del activo de la terna B11 + T1 | No autoauditoría |
| B12a-E3 | 2 Sabios externos cross-family + T1 | Triple auditoría metodológica |
| B12b-E1 | Sabio externo + T1 + humano externo si T1 lo designa | OK |
| B12b-E2 | Sabio externo + T1 | OK |
| **B12c-E1 (v0.2)** | Sabio externo + Cowork T2-A | Cowork puede auditar plazo, no firmarlo |
| **B12c-E2 (v0.2)** | Sabio externo + Cowork T2-A | OK |
| **B12c-E3 (v0.2)** | Sabio externo + T1 | T1 firma OK final |
| **B12c-E4 (v0.2)** | T1 + Sabio externo en cada tránsito | Audit por cada cambio de estado |

### §7.7 Riesgos

- **R-B12-1: Métrica medida es peor que el reclamo histórico.** Si la métrica real es 80% reducción, no 96%, el reclamo público debe actualizarse. Mitigación: B12a.4 obliga sustitución verbatim.
- **R-B12-2: B12a depende de B7 (fixtures) y B4 (1425 cases reproducibles).** Si B7 está en FAIL, B12a no puede ejecutarse. Mitigación: la opción (b) o (b⇒a) está disponible como salida.
- **R-B12-3: Declaración de obsolescencia es percibida como retroceso.** Mitigación: redactar verbatim como "métrica binaria PASS/FAIL es estándar más alto que numérico sin evidencia".
- **R-B12-4: Métrica obsoleta sigue circulando en docs externos.** Mitigación: anexo A.4 actualizado + nota explícita "métrica histórica obsoleta, ver B12-E1".
- **R-B12-5: Bifurcación a/b crea drift entre v(N+1) según opción.** Mitigación: spec versionado bajo firma magna T1 garantiza una sola vía vigente; (b⇒a) v0.2 explícitamente reconcilia las dos opciones en una secuencia ordenada.
- **R-B12-6 (NUEVO v0.2): Plazo B12c.2 vence sin ejecución y sin renegociación.** Si el owner B12c.3 no produce evidencia (a) en el plazo y nadie renegocia con T1, el sistema queda en `PASS_AS_B12c (b inmediata)` como estado terminal sin escalación visible. Mitigación: VERIFICADOR-001 emite evento `B12C_DEADLINE_APPROACHING` cuando faltan ≤14 días para el plazo + alerta a T1 + Cowork como observador (no validador) + audit log público B12c-E4.

### §7.8 No-go

- No se diseña con T1 sin firmar ninguna opción.
- No se diseña con métrica numérica sin metodología reproducible (B12a sin B12a.2/E3).
- No se diseña con obsolescencia silenciosa (sin actualizar Anexo A.4).
- No se diseña con Cowork como productor único de B12b-E1 o B12b-E2.
- No se diseña con métrica numérica residual fuera del Anexo A.4 cuando se elige (b) o (b⇒a) en su fase b inicial.
- **v0.2: No se diseña con (b⇒a) sin plazo firmado, sin owner asignado, o sin condición de reactivación.**

### §7.9 Decisión T1 requerida (ACTUALIZADA v0.2)

T1 firma verbatim **una de tres opciones**: (a) ejecutar DORY_BENCH ahora, (b) declarar obsolescencia ahora sin agendar medición posterior, **(b⇒a) declarar obsolescencia ahora + agendar medición posterior con plazo firmado**.

Si T1 elige (b⇒a) — la opción más conservadora desde la firma magna v1.1.1 vigente — debe firmar adicionalmente:

- **Plazo verbatim** en formato `YYYY-MM-DD` para ejecución (a). Propuesta: `2026-08-20` (90 días desde declaración B12c.1 propuesta), o cuando B4 1425 cases en runner reproducible + B7 PASS, lo que ocurra primero.
- **Owner verbatim** responsable de producir evidencia (a). Propuesta: autor NO-Cowork (Manus E2 o Sabio externo designado) + Sabio externo conjunto. NO Cowork como productor único.
- **Condición binaria de reactivación** verbatim: cuando B12a.1-B12a.6 todos PASS, métrica medida sustituye declaración de obsolescencia en spec.
- **Política de extensión de plazo** propuesta: si plazo se acerca sin (a) ejecutado, T1 debe firmar extensión explícita o aceptar `PASS_AS_B12c (b inmediata)` como estado terminal.

T1 también firma para todas las opciones:

- Aceptación o rechazo de la propuesta de bifurcación (a/b/b⇒a) o instrucción de tomar otra ruta.
- Designación de los Sabios auditores cross-family para B12a-E3.

---

## §8 Síntesis cruzada — gates con dependencia entre sí

Sin cambios desde v0.1. v0.2 mantiene el grafo de dependencias:

```
B6 (key custody)
  │
  ├──► B1 (kill switch local-first) ──► B2 (kill switch cloud)
  │         │
  │         └──► B3 (CI hook)
  │
  └──► B7 (hidden fixtures custody)  ◄── (custodios separados de auditores)
            │
            ├──► B4 (DORY_BENCH cases) ──► B5 (CVDS)
            │           │                    │
            │           └────► B12 (recuant) │
            │                       ▲        │
            │                       └────────┘ B11 (terna rotativa) audita B5/B7
            │
B8 (local_unreachable policy) ──► B9 (VERIFICADOR matrix)
            │
            └──► B10 (telemetry)
```

Cambio doctrinal v0.2 reflejado en el grafo:

- B7 ahora separa nodo de **custodios de almacenamiento** (T1, cuentas cloud, HSM, humanos delegados, repos privados cifrados) del nodo de **auditores Sabios LLM** (Opus, Gemini, DeepSeek, Kimi en terna rotativa B11). Antes el grafo confundía ambos roles.

Implicaciones binarias (sin cambios desde v0.1):

- B6 PASS es pre-requisito de B1, B2, B3, B7 (todos dependen de la cadena de firma ed25519).
- B7 PASS es pre-requisito de B4, B5, B12 opción (a) y opción (b⇒a) en su fase posterior.
- B8 PASS es pre-requisito de B9 (la matriz de degradación apela a B8 como ruta de fallback).
- B11 PASS es pre-requisito de B5 y B12a-E2 (sin terna no hay CVDS válido).
- B12 puede transitar a PASS por (b) o (b⇒a) en su fase b inmediata sin esperar a B7, lo que rompe parcialmente el cuello de botella.

Si Cowork ejecuta los gates en este orden (B6 → B7 → B8 → B11 → B9 → B4 → B5 → B12), las dependencias se resuelven naturalmente.

---

## §9 Reiteración binaria de no-implementación, no-canon, no-Dory-muerto

Este pack v0.2 NO:

- Implementa código (no kill_switch.py, no schemas SQL, no hooks runtime, no firmadores).
- Modifica main (entregable en rama lateral `control-tower/2026-05-20-b6-b12-design-closure-pack-v0-2`).
- Abre PR (solo push lateral).
- Canoniza ningún gate (B6-B12 v0.2 quedan en estado DRAFT diseño cerrado, no PASS).
- Declara Dory muerto (regla dura: "Dory curado" requiere PASS binario en 12 gates con evidencia, no solo diseño).
- Activa Fase 1 (regla dura ≤11/12 PASS sigue activa).

Después de este pack v0.2, el contador de gates PASS sigue siendo el mismo que antes de v0.1 (cuántos exactamente es decisión T1 sobre evidencias B1-B12 acumuladas, fuera de scope de este DRAFT). El cierre de diseño no es PASS; es **diseño aprobable para producir evidencia**, pendiente de:

1. T1 firma las decisiones requeridas en cada §X.9 v0.2.
2. Productores autorizados producen evidencia siguiendo los criterios PASS.
3. Auditores autorizados auditan la evidencia.
4. T1 firma PASS / FAIL de cada gate.
5. Cuando 12/12 PASS, regla dura permite considerar Fase 1.

---

## §10 Notas para Cowork T2-A (rol auditor — no compositor)

Sin cambios desde v0.1, ampliado con referencia a v0.2.

- Cowork T2-A puede auditar este pack v0.2 (auditoría documental).
- Cowork T2-A NO puede componer DELTA sobre este pack v0.2 sin caer en F16 estructural Opus 4.7. Si Cowork detecta correcciones necesarias adicionales a las 6 ya aplicadas, debe escribir un audit a este pack (formato de su audit a v0.1) y T1 firmará si solicita una v0.3 a otro autor NO-Cowork (no a Cowork).
- Cowork T2-A puede ser auditor en gates donde explícitamente se le permite (B6-E1, B7-E2 v0.2, B8-E2, B9-E2, B11-E1, B11-E5, B12c-E1 v0.2, B12c-E2 v0.2).

El audit Cowork T2-A 2026-05-20 sobre v0.1 fue ejemplo de este patrón correcto: auditó el pack sin componerlo, identificó hallazgos verbatim por gate, declaró su rol "auditor — no compositor" en el header, y respetó las hard rules del pack.

---

## §11 Caveat magno final v0.2

Este pack v0.2 lo escribió un autor NO-Cowork (Manus E2). v0.1 lo escribió el mismo autor. Si T1 lo aplica como otro DELTA sobre v1.1.1 dentro del flujo Cowork actual, el caveat F16 estructural Opus 4.7 se reactiva.

La integración doctrinal de B6-B12 v0.2 puede tomar varias formas (decisión binaria T1, ninguna en mi scope):

- **Anexo a v1.1.1** como cierre de diseño de los 6 gates faltantes — riesgo F16 medio si Cowork integra.
- **Incorporación al spec v2.0 RE-FUNDADO** (rama `sprints-propuestos/2026-05-19-dory-cure-v2-0-refundado-manus-e2`) si T1 decide canonizar v2.0 — coherente con redacción NO-Cowork.
- **Input para v3.0 sintetizada** como propuso Gemini 3.1 Pro y GPT-5.5 Pro en el reporte 3 Sabios consolidado (`control-tower/2026-05-20-3-sabios-consolidado` SHA `aad7714`) — opción más conservadora doctrinalmente.
- **DRAFT archivado** sin integración doctrinal hasta que T1 decida — opción más conservadora operativamente.

Manus E2 no firma. No canoniza. No decide integración. Espera firma binaria T1.

---

## §12 Cierre binario v0.2

| Confirmación | Status |
|--------------|--------|
| No implementé código | ✅ |
| No modifiqué main | ✅ (rama lateral `control-tower/2026-05-20-b6-b12-design-closure-pack-v0-2`) |
| No canonizo | ✅ (DRAFT v0.2, no firma) |
| No declaro Dory muerto | ✅ (regla dura ≤11/12 PASS sigue activa) |
| No activo Fase 1 | ✅ |
| 6 hallazgos T1 verbatim resueltos | ✅ (B7 rediseño, B6 `age` removido, B8 taxonomía a-m, B9 conteo 10, B11 caveat mitiga≠elimina, B12 b⇒a en PASS) |
| Hard rules audit Cowork 6/6 verde | ✅ (mismas reglas que v0.1, mantenidas) |
| Caveat magno Opus 4.7 declarado | ✅ §0, §11, §12 |

Próxima acción esperada: T1 verbatim firma decisión §X.9 de cada gate v0.2 antes de que cualquier gate transite de DISEÑADO a evidencia producida.

Manus E2. Autor NO-Cowork. Sin firma. Sin canon. Sin Fase 1. Sin Dory muerto. Sin código.
