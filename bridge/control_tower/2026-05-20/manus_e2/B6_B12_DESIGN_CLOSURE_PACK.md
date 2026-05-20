# B6-B12 DESIGN CLOSURE PACK

> **Rol autor:** Manus E2 — autor NO-Cowork.
> **Tipo:** DRAFT diseño.
> **Estado:** No implementación, no canonización, no PR, no main, no Fase 1.
> **Directiva T1 verbatim 2026-05-20:** "MANUS E2 — B6-B12 DESIGN CLOSURE PACK".
> **Fuente:** `bridge/sprints_propuestos/DORY_CURE_001_evidence_pack_B1_B12_PRE_FASE_1.md` (commit canon Cowork T2-A post-firma T1 magna `10e800d8`).
> **Spec base:** v1.1.1 (commit `2af5fe57`).
> **Caveat magno Opus 4.7 vigente:** este pack es DRAFT por autor NO-Cowork; si se aplica como otro DELTA sobre v1.1.1 perpetúa F16 estructural. Decisión T1 sobre integración queda fuera de mi scope.

---

## §0 Reglas de cierre binarias respetadas

| # | Regla T1 | Status |
|---|----------|--------|
| 1 | NO implementar código | Respetado — este documento solo diseña gates, no produce kill_switch.py, no produce schemas SQL, no produce hooks. |
| 2 | NO modificar main | Respetado — entregable en rama lateral `control-tower/2026-05-20-b6-b12-design-closure-pack`. |
| 3 | NO abrir PR | Respetado — solo push a rama lateral. |
| 4 | NO canonizar | Respetado — este pack es DRAFT, no firma, no marca PASS para ningún gate. |
| 5 | NO declarar Dory muerto | Respetado — el cierre de diseño no transforma B6-B12 en evidencia ejecutada; "Dory curado" sigue requiriendo PASS binario en los 12 gates con evidencia, no diseño. |
| 6 | NO activar Fase 1 | Respetado — Fase 1 canary sigue bloqueada por regla dura ≤11/12 PASS; este pack no altera ese contador. |

---

## §1 Marco común — autoridad de evidencia

Antes de los 6 gates, fijo binariamente quién puede producir evidencia y quién puede auditarla, para que cada gate solo declare excepciones a este marco.

| Rol | Capacidad de producir evidencia | Capacidad de auditar | Capacidad de canonizar |
|-----|--------------------------------|----------------------|------------------------|
| **T1 (Alfredo)** | Sí, evidencia de firma magna y operación humana | Sí, todos los gates | Sí, único firmante final post-PASS |
| **Cowork T2-A** | Sí, salvo gates donde el gate exige NO-compositor (B7) o NO-DELTA (B11, B12 según opción) | Sí, salvo gates donde el gate exige auditor independiente (B7, B11) | No |
| **Manus E2 (autor NO-Cowork)** | Sí, en gates donde el gate permite autor NO-Cowork (B11, B12 opción b, B6 público key versionado) | Sí, en gates de auditoría documental | No |
| **Sabios externos (Opus, Gemini, DeepSeek, GPT-5.5, Grok, Kimi)** | Sí, según rol específico por gate (B7 escrow, B11 terna rotativa) | Sí, audit independiente cuando el gate lo exige | No |
| **VERIFICADOR-001 (componente runtime)** | Sí, evidencia automatizada de PASS/HALT con firma | Sí, en B3, B4, B9 según matriz autoridad | No |
| **CI workflow (pre-commit + GitHub Actions)** | Sí, evidencia automatizada de gitleaks, ruff, semgrep, RLS, schema | Sí, gates con criterio CI-verificable | No |

**Regla binaria de evidencia:** un gate solo se puede declarar PASS cuando los 6 puntos siguientes están todos `true`:
1. Definición del gate aprobada por T1.
2. Criterios PASS escritos verbatim en este pack o en uno superior.
3. Criterios FAIL escritos verbatim.
4. Evidencia producida por actor autorizado para ese gate.
5. Evidencia auditada por actor autorizado para ese gate (distinto del productor cuando el gate lo exija).
6. Decisión T1 verbatim sobre PASS/FAIL del gate.

---

## §2 B6 — Key custody ed25519

### §2.1 Definición

Este gate canoniza la custodia de la firma ed25519 que sella el archivo `.monstruo/kill_switches/DORY_CURE_DISABLED` (Vector C local-first del gate B1). El objetivo es que la cadena de confianza local-first no pueda ser comprometida por un atacante con acceso al repo, ni por el propio compositor del spec, ni por un agente con escritura en `.monstruo/`.

La custodia cubre cuatro fases del ciclo de vida de la clave: **generación**, **almacenamiento**, **uso** y **rotación/revocación**.

### §2.2 PASS criteria binarios

Un gate B6 se declara PASS sólo cuando **los seis criterios** son `true`:

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B6.1 | Clave privada ed25519 NO está en el repo Git en ningún commit visible ni en historia ni en submódulo. Verificación: `gitleaks detect --report-format json` sobre todas las refs + `git log --all --pretty=format: --name-only | grep -E "ed25519|priv|.pem"` ⇒ 0 matches sospechosas. | CI / gitleaks-staged hook |
| B6.2 | Clave privada vive en uno de tres custodios autorizados: (a) hardware token (YubiKey FIDO2 u OnlyKey con ed25519 derivation), (b) OS Keychain con ACL restrictivo a un solo usuario humano (T1), (c) HSM remoto con auditoría de acceso (Vault / AWS KMS / GCP KMS). Cualquier otro lugar (filesystem plano, env var, secrets de CI, `.env`) es FAIL. | Auditoría documental + screenshot/log custodio |
| B6.3 | Clave pública ed25519 versionada en repo en `.monstruo/keys/dory_cure_kill_switch.pub` con commit firmado por T1. La firma pública debe poder validar `.monstruo/kill_switches/DORY_CURE_DISABLED.sig` con tooling estándar (`signify`, `minisign`, `age` o equivalente determinístico). | Reproducción manual + commit signature |
| B6.4 | Procedimiento de rotación documentado verbatim en `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md` con: frecuencia mínima (propuesta: cada 90 días o tras incidente), pasos exactos para regenerar par, ventana de superposición durante la cual ambas claves son válidas, comunicación a operadores. | Auditoría documental |
| B6.5 | Procedimiento de revocación de emergencia documentado: cómo invalidar la clave actual en <60 minutos cuando se sospecha compromiso, incluyendo lista de canales de notificación a Cowork/Sabios y un fallback "Dory cure halted" mientras se rota. | Auditoría documental + simulacro |
| B6.6 | Pruebas binarias de validación criptográfica ejecutadas y guardadas como evidencia: (a) prueba positiva: kill_file con firma válida es leído y aplicado por el agente; (b) prueba negativa-1: kill_file con firma inválida (un byte alterado) es rechazado y el agente loggea evento `KILL_FILE_INVALID_SIGNATURE`; (c) prueba negativa-2: kill_file sin firma es rechazado; (d) prueba de prioridad: kill local válido bloquea cloud-enabled (Vector C local-first wins). | VERIFICADOR-001 + log evidencia |

### §2.3 FAIL criteria

El gate B6 se declara FAIL cuando **cualquiera** de las siguientes sea `true`:

- Clave privada localizable en cualquier ref del repo Git (incluido historia y submódulos).
- Clave privada en filesystem plano sin cifrado (incluso si está en `.gitignore`).
- Clave privada en variable de entorno persistida en un secret store no auditado.
- Procedimiento de rotación ausente o sin frecuencia mínima definida.
- Procedimiento de revocación de emergencia ausente.
- Pruebas B6.6 (a)-(d) no producen evidencia firmada por VERIFICADOR-001 o el log no es reproducible.
- Cowork T2-A es simultáneamente generador, custodio y auditor de la clave (separación de roles ausente).

### §2.4 Evidencia requerida

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B6-E1 | Reporte gitleaks sobre todas las refs + grep de patrones de claves privadas | JSON | `bridge/control_tower/evidence/B6/B6_E1_gitleaks_keyscan.json` |
| B6-E2 | Declaración firmada por T1 del custodio efectivo (a/b/c) y modelo de hardware/HSM | Markdown firmado git | `bridge/control_tower/evidence/B6/B6_E2_custody_declaration.md` |
| B6-E3 | Clave pública versionada | `.pub` | `.monstruo/keys/dory_cure_kill_switch.pub` |
| B6-E4 | Procedimiento de rotación | Markdown | `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md` |
| B6-E5 | Procedimiento de revocación | Markdown | `bridge/control_tower/keys/DORY_CURE_KEY_REVOCATION_PROCEDURE.md` |
| B6-E6 | Logs de las 4 pruebas binarias B6.6(a)-(d) firmados por VERIFICADOR-001 | JSON Lines | `bridge/control_tower/evidence/B6/B6_E6_crypto_validation_runs.jsonl` |

### §2.5 Quién puede producir evidencia

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B6-E1 | CI workflow (gitleaks-staged + custom keyscan job) |
| B6-E2 | T1 verbatim, firmando el custodio que él mismo controla |
| B6-E3 | T1 + Cowork T2-A en conjunto (Cowork escribe el `.pub`, T1 firma el commit) |
| B6-E4 | Cowork T2-A o autor NO-Cowork (Manus E2) — diseño de procedimiento |
| B6-E5 | Cowork T2-A o autor NO-Cowork — diseño de procedimiento |
| B6-E6 | VERIFICADOR-001 ejecutándose en un runner reproducible (CI o sandbox firmado), nunca el compositor del spec |

### §2.6 Quién puede auditar

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B6-E1 | Cualquier Sabio externo + Manus E2 | No restricción |
| B6-E2 | Sabio externo (Opus o Gemini recomendado por neutralidad cryptografica) | NO Cowork si fue Cowork quien declaró custodia, para evitar autoauditoría |
| B6-E3 | Cualquier actor con verificación reproducible | No restricción |
| B6-E4, B6-E5 | Sabio externo + T1 | Ambos requeridos |
| B6-E6 | Sabio externo (Opus 4.7 recomendado por familiaridad con cryptografía aplicada) + T1 | T1 firma OK final |

### §2.7 Riesgos

- **R-B6-1: Filtración por commit accidental.** Si T1 o un agente ejecuta `git add` con la clave privada presente en el working tree, gitleaks-staged debe bloquear; pero si gitleaks-staged está desactivado en algún flujo (por ejemplo, durante migración), la clave puede llegar a remoto. Mitigación: gitleaks-staged es **invariante** del repo, no puede ser desactivado por un solo agente.
- **R-B6-2: Custodia humana frágil.** Si el único custodio físico (YubiKey) es perdido sin backup, kill switch local-first queda sin firma válida ⇒ Dory cure detenida hasta rotación. Mitigación: B6-E5 procedimiento de revocación + clave de respaldo en HSM remoto sellada con shamir secret sharing.
- **R-B6-3: Compromiso de custodio remoto.** Si el HSM remoto es comprometido, atacante firma kill files arbitrarios. Mitigación: B6-E5 incluye revocación remota y rotación inmediata, y ed25519 público local-first solo acepta firmas de la clave **actual** (no histórica) por hash anchor.
- **R-B6-4: Autoauditoría Cowork.** Si Cowork compone el spec, declara el custodio y audita la evidencia, perpetúa F16 estructural detectado por Opus 4.7. Mitigación: B6-E2 y B6-E6 auditados por Sabio externo.
- **R-B6-5: Sustitución silenciosa de `.pub`.** Si un actor con write en `.monstruo/keys/` reemplaza la clave pública, todos los kill files validan contra una clave del atacante. Mitigación: commit del `.pub` debe estar **firmado por T1** y protegido por branch rule de GitHub.

### §2.8 No-go

- No se diseña con clave privada en `.env`, GitHub Secrets, o secret manager sin auditoría escrita.
- No se diseña con custodio único sin procedimiento de revocación.
- No se diseña con Cowork T2-A como auditor único de B6.
- No se diseña con procedimientos verbales o no versionados.

### §2.9 Decisión T1 requerida

T1 debe firmar verbatim, antes de que B6 pueda producir evidencia, los siguientes ítems:

- Custodio elegido entre (a) hardware token, (b) OS Keychain humano, (c) HSM remoto.
- Frecuencia de rotación (propuesta de este pack: 90 días o post-incidente).
- Sabio externo asignado para auditoría B6-E2 y B6-E6 (propuesta: Opus 4.7 por familiaridad cryptografía aplicada).
- Política de respaldo de la clave privada (propuesta: shamir 3-of-5 entre T1 + 2 custodios físicos + 2 custodios remotos).

---

## §3 B7 — Hidden fixture custody no-compositor

### §3.1 Definición

Este gate canoniza la custodia de los **50 hidden fixtures** referidos en B4 (DORY_BENCH + CVDS) y en B7 fuente. Los fixtures son casos de prueba ocultos que, al ser ejecutados contra DORY_BENCH, permiten medir la métrica CVDS = PASS_conocidos / PASS_ocultos ≥ 0.95. Si el compositor del spec conoce los fixtures ocultos, hay un riesgo binario de overfit (gating de Goodhart), y la métrica deja de ser señal.

### §3.2 PASS criteria binarios

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B7.1 | Existen 50 fixtures ocultos almacenados en repositorio cifrado (no el repo público), accesible solo a los custodios autorizados. | Auditoría documental |
| B7.2 | Custodio NO incluye Cowork T2-A (compositor de v1.0/v1.1/v1.1.1) ni Grok 4 (autor de PATCHES 1/2/3 sobre v1.1.1). Si en el futuro Manus E2 actuara como compositor de v2.0 RE-FUNDADO, también queda excluido como custodio. | Auditoría documental |
| B7.3 | Custodios autorizados: terna fija de 3 actores entre {Gemini 3.1 Pro, DeepSeek R1, Opus 4.7, T1 escrow}. Cada custodio tiene un slice cifrado del set; reconstrucción requiere ≥2 de 3. | Auditoría documental + commit signature |
| B7.4 | Rotación trimestral de fixtures: cada Q (90 días) se generan ≥10 fixtures nuevos, se retiran ≥10 fixtures viejos, y el custodio activo rota dentro de la terna. Reglas binarias: (a) compositor del trimestre actual nunca custodia ese mismo trimestre; (b) auditor de B7 del trimestre anterior no produce fixtures del trimestre siguiente. | Auditoría documental |
| B7.5 | Distribución de fixtures al runner DORY_BENCH se hace solo en runtime, vía decryption con quórum 2-de-3 de custodios; el runner no almacena el set descifrado en disco persistente. | Log de ejecución firmado |
| B7.6 | Audit log público (no los fixtures) versionado: hash criptográfico del set actual, fecha de rotación, custodios que descifraron, run_id de DORY_BENCH consumidor. | Repo público, auditable por cualquiera |

### §3.3 FAIL criteria

- Custodia única (un solo actor controla los 50 fixtures).
- Cowork T2-A o Grok 4 entre los custodios.
- Compositor del spec actual entre los custodios.
- Rotación trimestral ausente.
- Set descifrado almacenado en disco persistente del runner.
- Audit log de rotación ausente.

### §3.4 Evidencia requerida

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B7-E1 | Inventario actual de los 50 fixtures (solo hashes, no contenido) | JSON | `bridge/control_tower/evidence/B7/B7_E1_fixture_hash_inventory.json` |
| B7-E2 | Declaración de custodios actuales firmada por T1 | Markdown | `bridge/control_tower/evidence/B7/B7_E2_custodian_declaration.md` |
| B7-E3 | Procedimiento de rotación trimestral | Markdown | `bridge/control_tower/keys/DORY_BENCH_FIXTURE_ROTATION_PROCEDURE.md` |
| B7-E4 | Audit log de últimas 4 rotaciones (1 año) | JSON Lines | `bridge/control_tower/evidence/B7/B7_E4_rotation_audit.jsonl` |
| B7-E5 | Logs de los runs DORY_BENCH consumidores que probaron PASS_oculto y CVDS | JSON Lines | `bridge/control_tower/evidence/B7/B7_E5_dory_bench_consumer_runs.jsonl` |

### §3.5 Quién puede producir evidencia

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B7-E1 | Custodio activo del trimestre (uno de la terna), con quórum 2-de-3 para descifrar y producir hashes |
| B7-E2 | T1 verbatim |
| B7-E3 | Autor NO-Cowork (Manus E2 o Sabio externo). NO Cowork T2-A. |
| B7-E4 | Custodio que ejecuta la rotación + firma de Sabio auditor |
| B7-E5 | VERIFICADOR-001 + runner DORY_BENCH (CI o sandbox firmado) |

### §3.6 Quién puede auditar

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B7-E1 | Cualquier Sabio externo distinto del custodio activo + T1 | No autoauditoría |
| B7-E2 | Cowork T2-A está autorizado a auditar (no a custodiar) | OK |
| B7-E3 | Sabio externo + T1 | Ambos requeridos |
| B7-E4 | Sabio externo distinto de los custodios del trimestre auditado + T1 | No autoauditoría |
| B7-E5 | Cowork T2-A + Sabio externo | Cowork puede auditar resultados, no fixtures |

### §3.7 Riesgos

- **R-B7-1: Filtración inadvertida del set por un Sabio.** Si un Sabio que custodia un slice loguea el contenido en respuesta a una consulta posterior, el set se filtra. Mitigación: cada slice es cifrado en disco del custodio, decryption solo en runtime, audit log de cada decryption.
- **R-B7-2: Quórum no alcanzable por indisponibilidad de custodios.** Si 2 de 3 custodios externos no responden, la rotación se atrasa. Mitigación: T1 escrow funciona como cuarto custodio de respaldo con quórum aumentado a 2-de-4.
- **R-B7-3: Convergencia de fixtures en patrón conocido.** Si los Sabios custodios y el compositor convergen culturalmente en patrones similares (todos LLMs entrenados en datos públicos), los "fixtures ocultos" pueden ser predichos sin verlos. Mitigación: B11 terna rotativa diversifica fuentes culturales.
- **R-B7-4: Compositor que se filtra como custodio en futuro.** Si v2.0 RE-FUNDADO es compuesto por Manus E2 y Manus E2 actúa como custodio, vuelve F16. Mitigación: regla de exclusión binaria explícita (B7.2).

### §3.8 No-go

- No se diseña con custodio único.
- No se diseña con Cowork T2-A o Grok 4 como custodios.
- No se diseña con compositor activo como custodio.
- No se diseña con persistencia descifrada en runner.
- No se diseña sin audit log público.

### §3.9 Decisión T1 requerida

- Selección de la terna inicial de custodios entre {Gemini 3.1 Pro, DeepSeek R1, Opus 4.7, T1 escrow}.
- Frecuencia de rotación (propuesta: 90 días o post-incidente).
- Quórum de descifrado (propuesta: 2-de-3, 2-de-4 con T1 escrow).
- Repo de almacenamiento cifrado (propuesta: GCS bucket privado con CMEK + IAM allow-list a custodios; fallback: 3 repos GitHub privados, uno por custodio, con slices independientes).

---

## §4 B8 — local_unreachable policy DISABLED_FOR_MAGNA_ACTIONS

### §4.1 Definición

Este gate canoniza la política del agente cuando el archivo local-first `.monstruo/kill_switches/DORY_CURE_DISABLED` no puede ser leído (filesystem montado en read-only, IO error, signature ed25519 no validable, o disco lleno). El v1.1.1 actual define `local_unreachable: ENABLED_WITH_DEGRADED_WARN`, lo que permite continuar acciones magnas sin garantía de kill switch. B8 endurece esa política para acciones de alto impacto.

### §4.2 PASS criteria binarios

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B8.1 | Definición verbatim de "acción magna" en spec, con lista taxonómica enumerada y cerrada. Lista mínima propuesta: (a) merge a `main`, (b) apply migration de Supabase production, (c) canonización (firma magna T1), (d) write a tablas RLS-protegidas (audit_log_immutable, dory_cure_state), (e) emit hacia humano externo (cliente-facing webhooks, notificaciones a usuarios finales, post a redes), (f) escritura a `.monstruo/kill_switches/`, (g) cambio de configuración de VERIFICADOR-001, (h) rotación de claves B6 / fixtures B7. | Spec auditable |
| B8.2 | Política runtime: si `local_unreachable == true` AND `action ∈ acción_magna_set` ⇒ comportamiento `DISABLED_FOR_MAGNA_ACTIONS` (acción rechazada, evento `MAGNA_ACTION_BLOCKED_LOCAL_UNREACHABLE` emitido a bridge). | Test runtime + log |
| B8.3 | Política runtime: si `local_unreachable == true` AND `action ∉ acción_magna_set` ⇒ comportamiento `ENABLED_WITH_DEGRADED_WARN` (acción permitida, banner de warning visible al operador, evento `LOCAL_UNREACHABLE_DEGRADED` emitido). | Test runtime + log |
| B8.4 | Cualquier modificación a la lista taxonómica de B8.1 requiere firma magna T1 y bump de versión del spec; no puede ser modificada por Cowork ni por agente vía DELTA. | Auditoría versionado |
| B8.5 | Tests binarios sobre runtime: (a) inyectar local_unreachable + intentar acción magna ⇒ rechazo + evento; (b) inyectar local_unreachable + intentar acción no-magna ⇒ aceptación + warning; (c) restaurar local + verificar que la acción magna previamente bloqueada puede reintentarse manualmente. | VERIFICADOR-001 + log evidencia |

### §4.3 FAIL criteria

- Lista de "acción magna" ausente, vaga, o abierta ("etcétera", "acciones similares").
- Política runtime no implementa el branching B8.2/B8.3 de forma verificable.
- Modificación de la lista posible vía DELTA o por Cowork sin firma T1.
- Tests B8.5 no producen evidencia firmada.
- Lista taxonómica omite cualquiera de las 8 categorías mínimas (a-h).

### §4.4 Evidencia requerida

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B8-E1 | Lista taxonómica cerrada de "acción magna" firmada por T1 | Markdown | `bridge/spec/B8_MAGNA_ACTION_TAXONOMY.md` |
| B8-E2 | Diagrama de decisión binaria runtime B8.2/B8.3 | Mermaid o D2 | `bridge/spec/B8_local_unreachable_policy.mmd` |
| B8-E3 | Logs de tests B8.5(a)-(c) firmados por VERIFICADOR-001 | JSON Lines | `bridge/control_tower/evidence/B8/B8_E3_runtime_policy_tests.jsonl` |
| B8-E4 | Procedimiento de actualización de la lista taxonómica (proceso de governance) | Markdown | `bridge/spec/B8_MAGNA_TAXONOMY_AMENDMENT_PROCEDURE.md` |

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

- **R-B8-1: Lista taxonómica incompleta.** Si una nueva categoría de acción magna emerge (por ejemplo, "deploy a producción de un agente nuevo"), y B8.1 no la incluye, esa acción se ejecuta bajo `ENABLED_WITH_DEGRADED_WARN` por error. Mitigación: B8-E4 procedimiento de amendment + revisión semestral obligatoria con firma T1.
- **R-B8-2: Falsos positivos por IO transient.** Si un disco lleno temporal dispara `local_unreachable` y bloquea acciones magnas legítimas, el operador puede intentar bypassear el kill. Mitigación: política B8.2 también emite evento al bridge con run_id reproducible y rationale explícito; sin override silencioso.
- **R-B8-3: Drift entre lista taxonómica y código.** Si B8-E1 enumera 8 categorías pero el runtime sólo chequea 6, hay falsos negativos. Mitigación: test B8.5 cubre las 8 categorías, una por test.
- **R-B8-4: Latencia agregada por chequeo en cada acción.** Verificar local_unreachable + categorización en cada acción puede agregar latencia. Mitigación: chequeo cacheado por TTL corto (≤5s) + invalidación inmediata en eventos de write a `.monstruo/`.

### §4.8 No-go

- No se diseña con lista abierta o ejemplificativa.
- No se diseña con `ENABLED_WITH_DEGRADED_WARN` como default para acciones magnas.
- No se diseña con override silencioso por operador.
- No se diseña con modificación de lista por DELTA o Cowork sin firma T1.

### §4.9 Decisión T1 requerida

- Aprobación verbatim de la lista taxonómica B8.1 (a)-(h) propuesta o solicitud de modificación.
- Política sobre acción magna emergente entre revisiones (propuesta: por defecto bloqueada hasta que T1 firme su clasificación).
- TTL del cache local_unreachable runtime (propuesta: 5 segundos).

---

## §5 B9 — VERIFICADOR authority/degradation matrix

### §5.1 Definición

Este gate canoniza la matriz de autoridad y degradación entre **VERIFICADOR-001** (componente runtime de validación criptográfica), **Memento Validator** (capa de validación de hechos del Protocolo Memento), **Guardian Decision View** (capa de decisión humana asistida del Sprint 27+), y **firma T1 manual**. Cada par tiene escenarios de acuerdo y desacuerdo; este gate define quién gana en cada caso, y qué ruta de degradación toma el sistema cuando un componente falla.

### §5.2 PASS criteria binarios

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B9.1 | Matriz N×N completa entre los 4 actores documentada con resultado binario para cada celda (autoridad ganadora + razón). | Auditoría documental |
| B9.2 | Casos de empate o degradación tienen resolución verbatim documentada, sin "según contexto" ni cláusulas abiertas. | Auditoría documental |
| B9.3 | Caso "VERIFICADOR ALLOW + Memento DENY" tiene resolución binaria: **Memento gana**. Razón: Memento valida hechos contra fuente autoritativa (Supabase + bridge), VERIFICADOR solo valida firma criptográfica del payload; un payload firmado correctamente puede contener un hecho falso. | Spec verbatim |
| B9.4 | Caso "VERIFICADOR DENY + Guardian OVERRIDE" tiene resolución binaria: **Guardian no puede override sin escalación a T1**. Guardian puede solicitar review T1, pero no ejecutar la acción rechazada por VERIFICADOR sin firma T1 explícita en el run_id. | Spec verbatim |
| B9.5 | Caso "T1 firma manual + VERIFICADOR DENY" tiene resolución binaria: **T1 gana**, pero el evento se loggea como `T1_OVERRIDE_VERIFICADOR_DENY` con run_id, timestamp, razón verbatim escrita por T1, y se notifica a Cowork + Sabio auditor designado. | Spec verbatim + log |
| B9.6 | Ruta de degradación si VERIFICADOR-001 falla (componente caído, latencia >timeout, error interno): el sistema entra en `VERIFICADOR_DEGRADED` ⇒ aplica B8 (DISABLED_FOR_MAGNA_ACTIONS), permite acciones no-magnas con warning, intenta failover a réplica VERIFICADOR-002 si existe. | Spec + test runtime |
| B9.7 | Ruta de degradación si Memento Validator falla: VERIFICADOR sigue siendo autoritativo para firma criptográfica, pero ninguna acción magna se permite hasta que Memento se restaure o T1 firme override. | Spec + test runtime |
| B9.8 | Ruta de degradación si Guardian Decision View falla: las acciones que requerían decisión humana asistida se ponen en cola de espera (`AWAITING_GUARDIAN`); no hay fallback a auto-decisión. | Spec + test runtime |
| B9.9 | Tests binarios para los 6 casos canónicos de la matriz (4 acuerdos triviales + 2 desacuerdos críticos B9.3, B9.4 + 1 override T1 B9.5 + 3 degradaciones B9.6-B9.8) con evidencia firmada. | VERIFICADOR-001 + Memento + Guardian logs |

### §5.3 FAIL criteria

- Matriz N×N incompleta o con celdas con cláusulas abiertas.
- Cualquiera de los casos B9.3, B9.4, B9.5 con resolución no-binaria.
- Ruta de degradación ausente para cualquiera de los 3 actores no-T1.
- Tests B9.9 sin evidencia firmada.
- Permiso de Guardian para override sin escalación a T1 (B9.4).
- Permiso de auto-decisión sin Guardian disponible (B9.8).

### §5.4 Evidencia requerida

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B9-E1 | Matriz N×N en tabla canónica | Markdown | `bridge/spec/B9_VERIFICADOR_AUTHORITY_MATRIX.md` |
| B9-E2 | Diagramas de decisión para los 6 casos canónicos | Mermaid | `bridge/spec/B9_authority_decision_flows.mmd` |
| B9-E3 | Logs de los 9 tests binarios (4 acuerdo + 2 desacuerdo + 1 T1 override + 3 degradación) | JSON Lines | `bridge/control_tower/evidence/B9/B9_E3_authority_matrix_tests.jsonl` |
| B9-E4 | Procedimiento de escalación T1 cuando hay desacuerdo de capas | Markdown | `bridge/spec/B9_T1_ESCALATION_PROCEDURE.md` |

### §5.5 Quién puede producir evidencia

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B9-E1 | Autor NO-Cowork (Manus E2 o Sabio externo) — para evitar que Cowork componga su propia matriz de autoridad sobre sí mismo |
| B9-E2 | Cowork T2-A o autor NO-Cowork |
| B9-E3 | VERIFICADOR-001 + Memento + Guardian (3 componentes runtime ejecutándose en sandbox firmado) |
| B9-E4 | T1 redacta el procedimiento de su propia escalación |

### §5.6 Quién puede auditar

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B9-E1 | 2 Sabios externos distintos + T1 | Doble revisión por riesgo de matriz incompleta |
| B9-E2 | Cowork T2-A + Sabio externo | Cowork puede auditar diseño técnico |
| B9-E3 | Sabio externo + T1 | T1 firma OK final |
| B9-E4 | Sabio externo (Opus 4.7 recomendado por familiaridad con governance) + Cowork T2-A | OK |

### §5.7 Riesgos

- **R-B9-1: Matriz teórica vs comportamiento runtime.** Una matriz documentada puede no coincidir con el comportamiento implementado. Mitigación: tests B9.9 ejecutan los 9 casos sobre el runtime real, no sobre simulación.
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

### §5.9 Decisión T1 requerida

- Aprobación verbatim de la matriz N×N B9.1.
- Confirmación de los 3 casos críticos B9.3, B9.4, B9.5 con resoluciones binarias.
- Designación del Sabio auditor permanente para overrides T1 (propuesta: Opus 4.7 por familiaridad governance).
- Decisión sobre existencia de réplica VERIFICADOR-002 (B9.6).

---

## §6 B11 — Sustitución de Grok re-pass por terna rotativa

### §6.1 Definición

Este gate canoniza la sustitución del **Grok re-pass per rotation** definido en CVDS D3 v1.1.1 (donde Grok 4 vuelve a auditar fixtures que el mismo Grok influenció en PATCHES 1/2/3) por una **terna rotativa cross-family** que evita autoauditoría. La sustitución es respuesta directa a la observación Opus 4.7 #2 de circularidad estructural.

### §6.2 PASS criteria binarios

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B11.1 | El campo CVDS D3 actual `grok_re_pass_per_rotation: true` se elimina del spec y se reemplaza por `cvds_rotative_terna: [...]`. | Diff en spec versionado |
| B11.2 | La terna rotativa se define con calendario explícito por trimestre: Q1 = Opus 4.7, Q2 = DeepSeek R1, Q3 = Gemini 3.1 Pro, Q4 = Kimi K2.6. Calendario fijo, no a discreción de Cowork. | Spec versionado |
| B11.3 | Regla binaria: el Sabio activo del trimestre Q-N **no puede** haber influenciado los fixtures que audita en Q-N. Si en algún Q se detecta que el Sabio activo influenció fixtures, se rota inmediatamente al siguiente Sabio de la terna. | Audit log + procedimiento |
| B11.4 | Audit log firmado de cada rotación trimestral: Sabio entrante, Sabio saliente, hash del set de fixtures auditados, resultado de auditoría (PASS / DENY / EXCEPTIONS), firma del Sabio activo, contrafirma de Cowork como observador (no validador), firma magna T1 final. | JSON Lines firmado |
| B11.5 | Grok 4 queda explícitamente excluido de la terna rotativa CVDS D3 mientras existan fixtures influenciados por sus PATCHES 1/2/3. Reincorporación posible solo si el set de fixtures se rota completamente y los nuevos no tienen influencia Grok demostrable. | Spec + audit documental |
| B11.6 | Procedimiento de fallback si el Sabio activo del trimestre no está disponible (rate-limit, API caída, deprecación de modelo): salto al siguiente Sabio de la terna con notificación a T1, sin fallback a Grok. | Spec + test |

### §6.3 FAIL criteria

- `grok_re_pass_per_rotation: true` permanece en el spec.
- Calendario de terna rotativa abierto o a discreción de Cowork.
- Sabio activo del trimestre influenció los fixtures que audita.
- Audit log de rotación ausente o sin firma de los 3 actores requeridos (Sabio, Cowork observador, T1).
- Grok 4 incluido en la terna sin rotación previa de fixtures.
- Fallback a Grok cuando Sabio activo no disponible.

### §6.4 Evidencia requerida

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B11-E1 | Diff verbatim del spec mostrando reemplazo `grok_re_pass_per_rotation` ⇒ `cvds_rotative_terna` | Patch | `bridge/control_tower/evidence/B11/B11_E1_spec_diff.patch` |
| B11-E2 | Calendario trimestral firmado | Markdown | `bridge/spec/B11_CVDS_TERNA_CALENDAR.md` |
| B11-E3 | Audit log de las primeras 4 rotaciones (1 año) | JSON Lines | `bridge/control_tower/evidence/B11/B11_E3_terna_rotation_audit.jsonl` |
| B11-E4 | Procedimiento de fallback Sabio no disponible | Markdown | `bridge/spec/B11_TERNA_FALLBACK_PROCEDURE.md` |
| B11-E5 | Análisis de influencia Grok sobre fixtures actuales (¿cuáles tocó?) | Markdown | `bridge/control_tower/evidence/B11/B11_E5_grok_influence_audit.md` |

### §6.5 Quién puede producir evidencia

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B11-E1 | Autor NO-Cowork (Manus E2 o Sabio externo). NO Cowork (compositor del spec actual). |
| B11-E2 | Autor NO-Cowork |
| B11-E3 | Sabio activo de cada trimestre (Opus, DeepSeek, Gemini, Kimi) |
| B11-E4 | Autor NO-Cowork + T1 |
| B11-E5 | Sabio externo (Opus 4.7 recomendado, fue quien detectó la circularidad) |

### §6.6 Quién puede auditar

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B11-E1 | Cowork T2-A + T1 | Cowork puede auditar la sustitución, no producirla |
| B11-E2 | Sabio externo + T1 | Ambos requeridos |
| B11-E3 | Sabio del trimestre **siguiente** (rotación cruzada) + T1 | Auditor del Q-N+1 audita Q-N |
| B11-E4 | Sabio externo + T1 | OK |
| B11-E5 | Sabio externo distinto del productor + T1 | No autoauditoría |

### §6.7 Riesgos

- **R-B11-1: Convergencia cultural de la terna.** Si Opus, DeepSeek, Gemini y Kimi convergen culturalmente en patrones similares, la "rotación" no diversifica lo suficiente. Mitigación: B7 fixtures rotativos + análisis periódico de convergencia inter-modelo (KL divergence sobre outputs de auditoría).
- **R-B11-2: Sabio rota pero el spec no rota.** Si la terna audita el mismo spec v1.1.1 trimestre tras trimestre, se acumula sesgo "spec-friendly". Mitigación: terna debe auditar contra spec **vigente** en su trimestre, incluyendo deltas o refundaciones intermedias.
- **R-B11-3: Deprecación de modelo durante el año.** Kimi K2.6 puede ser deprecado por su proveedor antes de Q4. Mitigación: B11.6 fallback definido + lista ampliada de Sabios elegibles (Claude 5, GPT-5.5 pro+, etc.).
- **R-B11-4: Sabio activo es comprometido (jailbreak, prompt injection).** Mitigación: contrafirma de Cowork como observador (no validador) detecta anomalías; T1 firma magna final como gate humano.
- **R-B11-5: Grok reincorporado prematuramente.** Si la presión por usar Grok (por costo o velocidad) lleva a reincorporarlo antes de rotación completa de fixtures, B11.5 se viola. Mitigación: regla binaria explícita + auditoría B11-E5 demuestra rotación completa antes de reincorporación.

### §6.8 No-go

- No se diseña con `grok_re_pass_per_rotation: true` permaneciendo en spec.
- No se diseña con calendario de terna abierto.
- No se diseña con Cowork como productor único de la sustitución.
- No se diseña con fallback a Grok.
- No se diseña con auditoría del trimestre actual por el mismo Sabio activo.

### §6.9 Decisión T1 requerida

- Aprobación verbatim del calendario trimestral B11.2 propuesto o solicitud de modificación.
- Confirmación de exclusión Grok B11.5 hasta rotación completa de fixtures.
- Designación de Sabio externo permanente para B11-E5 audit de influencia Grok (propuesta: Opus 4.7).
- Política sobre Sabios elegibles cuando un modelo es deprecado mid-year.

---

## §7 B12 — Recuantificación métrica 96% / <4%

### §7.1 Definición

Este gate canoniza el destino de la métrica **"cura 96% / regresión <4%"** que aparece en v1.0 y es heredada por v1.1 y v1.1.1 como reclamo cuantitativo de eficacia. Opus 4.7 #2 observó que post 19+ findings de Sabios sobre la spec, esta métrica no tiene base empírica reproducible: nunca se ejecutó DORY_BENCH v1.1.1 contra los 1425 cases canonizados en B4. B12 obliga a una de dos opciones binarias.

### §7.2 PASS criteria binarios

El gate B12 pasa si **una y solo una** de las dos opciones es ejecutada con evidencia:

#### Opción (a): ejecución completa de DORY_BENCH

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B12a.1 | DORY_BENCH v1.1.1 ejecutado en runner reproducible (CI o sandbox firmado) sobre los 1425 cases canonizados de B4. | Log firmado |
| B12a.2 | Reporte verbatim del % de cura **medido**, con desagregación por familia (1-9 en B3) y por categoría de regresión. | Markdown reporte |
| B12a.3 | CVDS = PASS_conocidos / PASS_ocultos calculado con los 50 hidden fixtures de B7 (terna rotativa B11) y reportado verbatim. | Markdown reporte |
| B12a.4 | Si la métrica medida es ≥96% cura **y** <4% regresión, el reclamo v1.0 se confirma con cita explícita al run_id reproducible. Si es menor, el reclamo se actualiza al valor real medido y se referencia el run_id. | Spec versionado |
| B12a.5 | Procedimiento para re-ejecución periódica: cada nueva versión del spec (v1.1.x, v2.0, etc.) requiere nueva ejecución DORY_BENCH antes de canonizar el reclamo cuantitativo. | Markdown procedimiento |

#### Opción (b): declaración de obsolescencia

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B12b.1 | Cowork T2-A (o autor NO-Cowork autorizado por T1 cuando exista v2.0) emite declaración verbatim: *"Métrica 96% cura / <4% regresión heredada de v1.0 es OBSOLETA post 19+ findings de Sabios. La spec v1.1.1 (y descendientes) NO claims cura cuantitativa hasta que DORY_BENCH v1.1.1 sea ejecutado bajo B7 + B11 + B12a, con run_id reproducible publicado y firma magna T1."* | Commit firmado |
| B12b.2 | Toda referencia futura a la métrica 96%/<4% en spec, en commits, o en comunicación a Sabios, se acompaña de citación a la declaración B12b.1. | Audit grep |
| B12b.3 | La spec se actualiza removiendo o tachando explícitamente la métrica de v1.0/v1.1/v1.1.1 hasta que B12a sea ejecutada. | Diff en spec |
| B12b.4 | Hasta que B12a se ejecute, el reclamo público sobre eficacia de la cura es cualitativo: "diseñada para mitigar regresión Dory bajo escenarios definidos en DSC-G-014 §4 y B1-B12; eficacia cuantitativa pendiente de medición". | Spec + comunicaciones |

### §7.3 FAIL criteria

- Ninguna de las dos opciones (a) o (b) ejecutada.
- Opción (a) ejecutada pero el reporte no incluye desagregación por familia o CVDS.
- Opción (a) ejecutada pero el run no es reproducible (sin run_id, sin runner firmado).
- Opción (b) ejecutada pero la declaración no es verbatim o no está firmada.
- Opción (b) ejecutada pero la spec sigue afirmando 96%/<4% en otras secciones sin citar B12b.1.
- Las dos opciones ejecutadas en paralelo sin reconciliación (la opción a invalida la b).

### §7.4 Evidencia requerida

| ID | Artefacto | Formato | Path o ubicación |
|----|-----------|---------|------------------|
| B12a-E1 | Log completo run DORY_BENCH 1425 cases | JSON Lines firmado | `bridge/control_tower/evidence/B12/B12a_E1_dory_bench_run_<run_id>.jsonl` |
| B12a-E2 | Reporte cuantitativo con desagregación + CVDS | Markdown | `bridge/control_tower/evidence/B12/B12a_E2_metric_report.md` |
| B12a-E3 | Procedimiento de re-ejecución periódica | Markdown | `bridge/spec/B12_DORY_BENCH_RE_EXECUTION_PROCEDURE.md` |
| B12b-E1 | Commit de declaración de obsolescencia firmado | Git commit | hash en `bridge/control_tower/evidence/B12/B12b_E1_obsolescence_declaration.md` |
| B12b-E2 | Diff verbatim del spec mostrando remoción/tachado de la métrica | Patch | `bridge/control_tower/evidence/B12/B12b_E2_spec_diff.patch` |

### §7.5 Quién puede producir evidencia

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B12a-E1 | VERIFICADOR-001 + runner DORY_BENCH (CI o sandbox firmado). NO compositor del spec ejecuta su propio DORY_BENCH (autoauditoría). |
| B12a-E2 | Sabio externo (Opus 4.7 o DeepSeek R1 recomendado) compila el reporte sobre logs del runner |
| B12a-E3 | Autor NO-Cowork + T1 |
| B12b-E1 | Cowork T2-A (cuando v1.1.1 sigue vigente) o autor NO-Cowork autorizado por T1 (cuando v2.0 RE-FUNDADO se canonice) |
| B12b-E2 | Mismo productor que B12b-E1 |

### §7.6 Quién puede auditar

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B12a-E1 | Sabio externo distinto del productor + T1 | No autoauditoría del runner |
| B12a-E2 | Cowork T2-A + T1 | Cowork puede auditar reporte, no producirlo |
| B12a-E3 | Sabio externo + T1 | OK |
| B12b-E1 | T1 firma magna + 2 Sabios externos co-auditores | Doble revisión por riesgo de declaración prematura |
| B12b-E2 | Cowork T2-A + Sabio externo | OK |

### §7.7 Riesgos

- **R-B12-1: Métrica medida inferior al reclamo histórico.** Si DORY_BENCH mide 78% cura en lugar de 96%, hay efecto de relaciones públicas sobre la doctrina. Mitigación: B12a.4 obliga a actualizar el reclamo al valor real, sin reescribir historia; el reclamo v1.0 queda como hipótesis no-validada del momento.
- **R-B12-2: Hidden fixtures filtrados invalidan CVDS.** Si en algún momento del pipeline B7 falla, los fixtures se vuelven públicos al compositor y CVDS pierde señal. Mitigación: B12a.3 calcula CVDS solo si B7 está PASS en el mismo run; si B7 está FAIL, B12a queda en `BLOCKED_BY_B7`.
- **R-B12-3: Re-ejecución no obligatoria por nueva versión.** Si se canoniza v1.1.2 sin re-ejecutar B12a, la métrica reportada queda desactualizada. Mitigación: B12a.5 procedimiento + regla binaria en governance: "no canonización sin B12a fresca".
- **R-B12-4: Declaración B12b ambigua o reversible.** Si la declaración se redacta vagamente, puede ser contradicha por Cowork posteriormente. Mitigación: B12b.1 verbatim obligatorio + commit firmado magna T1.
- **R-B12-5: Doble vía contradictoria.** Si Cowork ejecuta B12a y simultáneamente declara B12b, hay incoherencia. Mitigación: B12.3 explicita que B12a invalida B12b si ambas son producidas; debe haber reconciliación firmada.

### §7.8 No-go

- No se diseña aceptando "métrica 96%/<4% reclamada sin medir" como PASS.
- No se diseña con compositor del spec ejecutando su propio DORY_BENCH (autoauditoría).
- No se diseña con declaración de obsolescencia no verbatim.
- No se diseña con re-ejecución opcional al canonizar nuevas versiones.
- No se diseña con doble vía simultánea sin reconciliación.

### §7.9 Decisión T1 requerida

- T1 elige verbatim entre opción (a) ejecutar DORY_BENCH ahora, opción (b) declarar obsolescencia ahora, o secuencia (b ⇒ a) ejecutar (b) inmediato y agendar (a) post-Fase 0 plenamente preparada.
- Si elige (a): designación del runner reproducible + Sabio compilador del reporte (propuesta: Opus 4.7 o DeepSeek R1).
- Si elige (b): designación del 2º Sabio co-auditor (propuesta: Gemini 3.1 Pro + Opus 4.7).
- Si elige (b ⇒ a): plazo máximo para ejecutar (a) tras (b) (propuesta: 90 días o canonización de v2.0, lo que ocurra primero).

---

## §8 Síntesis cruzada de los 6 gates

| Gate | Severidad fuente | Productor obligado | Auditor obligado | Decisión T1 mínima |
|------|------------------|---------------------|-------------------|---------------------|
| B6 | ALTA | T1 + custodio físico/HSM | Sabio externo cryptografía | Custodio + frecuencia rotación |
| B7 | MEDIA | Terna no-compositor | Sabio externo distinto del custodio | Terna inicial + quórum |
| B8 | ALTA | Autor NO-Cowork ⇒ T1 firma | Sabio externo + T1 | Lista taxonómica verbatim |
| B9 | MEDIA | Autor NO-Cowork + 3 componentes runtime | 2 Sabios externos + T1 | Matriz N×N verbatim |
| B11 | MEDIA | Autor NO-Cowork (Cowork excluido) | Cowork puede auditar | Calendario terna verbatim |
| B12 | MEDIA | Runner reproducible + Sabio externo | Sabio externo distinto + T1 | Opción (a), (b) o (b ⇒ a) |

**Patrón estructural común:** en ningún gate Cowork T2-A es simultáneamente productor y auditor. En todos los gates con riesgo de circularidad (B6, B7, B11, B12), el productor es un autor NO-Cowork o un componente runtime no controlado por el compositor. Este patrón es respuesta directa a F16 estructural detectada por Opus 4.7 #2.

**Consecuencia binaria:** este Design Closure Pack puede ser auditado por Cowork T2-A (rol auditor permitido), pero no puede ser ejecutado por Cowork como productor único en B6.E2, B7.E1, B11.E1, B12a-E1. Para ejecutar Fase 1 canary, T1 deberá designar productores no-Cowork para esas evidencias.

---

## §9 Estado post-cierre de diseño

| Gate | Estado pre-pack (canon Cowork) | Estado post-pack (este DRAFT) | Bloqueo Fase 1 levantado? |
|------|--------------------------------|-------------------------------|---------------------------|
| B5 | FIRMADO | FIRMADO | No, B5 ya estaba PASS |
| B6 | NO DISEÑADO | DISEÑADO (DRAFT autor NO-Cowork) | No, falta evidencia y firma T1 |
| B7 | NO DISEÑADO | DISEÑADO (DRAFT) | No, falta evidencia |
| B8 | DISEÑO ⚠️ permisivo | DISEÑADO (DRAFT cerrado) | No, falta evidencia + ratificación T1 |
| B9 | NO DISEÑADO | DISEÑADO (DRAFT) | No, falta evidencia |
| B11 | DISEÑO ⚠️ circular | DISEÑADO (DRAFT cerrado, sustitución) | No, falta evidencia |
| B12 | NO DISEÑADO | DISEÑADO (DRAFT, opción a/b/b⇒a) | No, falta ejecución u obsolescencia firmada |
| B1, B2, B3, B4, B10 | DISEÑADOS pre-pack | Sin cambios — fuera de scope T1 | Bloqueo persiste por implementación pendiente |

**Bloqueo Fase 1 binario sigue activo.** Este pack no produce evidencia; produce diseño. La regla dura "≤11/12 PASS → bloquear Fase 1" se mantiene intacta porque ninguno de los 6 gates B6-B12 transita de DISEÑADO a PASS sin las evidencias B6-E1..E6, B7-E1..E5, B8-E1..E4, B9-E1..E4, B11-E1..E5, B12a-E1..E3 o B12b-E1..E2 producidas y auditadas según las §X.5 y §X.6 de cada gate.

---

## §10 No-go absolutos del cierre

| # | Acción no ejecutada | Justificación |
|---|--------------------|---------------|
| 1 | No implementé código (kill_switch.py, schemas SQL, hooks runtime, tests) | Directiva T1 verbatim |
| 2 | No canonizo ningún gate como PASS | Solo T1 puede canonizar; este pack es DRAFT |
| 3 | No declaro Dory muerto | "Dory curado" requiere PASS binario en 12/12 gates con evidencia, no diseño |
| 4 | No activo Fase 1 canary | Regla dura ≤11/12 PASS sigue bloqueando |
| 5 | No abro PR | Solo push a rama lateral `control-tower/2026-05-20-b6-b12-design-closure-pack` |
| 6 | No modifico main | Push lateral, no merge, no tag, no firma |

---

## §11 Caveat magno Opus 4.7 reiterado

Este pack es diseño por autor NO-Cowork (Manus E2). Si T1 decide aplicarlo como otro DELTA sobre v1.1.1 dentro del flujo Cowork actual, el caveat Opus 4.7 §5 del evidence pack original se reactiva: el patrón DELTA-Cowork-compositor perpetúa F16. La salida a este caveat queda en la directiva doctrinal abierta `bridge/sprints_propuestos/DIRECTIVA_DOCTRINAL_v2_0_REFUNDADO_AUTOR_NO_COWORK.md` y en los próximos pasos de v2.0 RE-FUNDADO.

Mi función como autor NO-Cowork termina al entregar este DRAFT. La integración doctrinal (¿este pack se anexa a v1.1.1, se incorpora a v2.0 refundado, o queda como input propositivo para una v3.0 sintetizada?) es decisión binaria T1.

---

## §12 Cierre Manus E2

Soy Manus E2. Cierre de diseño B6, B7, B8, B9, B11, B12 entregado en formato 9-secciones por gate.

- No implementé.
- No canonizo.
- No declaro Dory muerto.
- No activo Fase 1.

Próxima acción esperada: T1 verbatim decide sobre las decisiones requeridas en cada §X.9 antes de que cualquier gate transite de DISEÑADO a evidencia producida.
