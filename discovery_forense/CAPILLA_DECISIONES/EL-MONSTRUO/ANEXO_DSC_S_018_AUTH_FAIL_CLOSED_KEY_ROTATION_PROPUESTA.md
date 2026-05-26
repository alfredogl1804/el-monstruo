**Estado:** Aspiracional.

No es un DSC firmado. Es articulación T1 pendiente de firma magna. La firma de Cowork (Hilo A — arquitecto/canonizador) genera el contrato canónico al completar el bloque YAML correspondiente.

Esta versión **supersede a `ANEXO_DSC_S_012_AUTH_FAIL_CLOSED_KEY_ROTATION_PROPUESTA.md`** (renumerada por Coherence Gate Cowork — `DSC-S-012` ya estaba ocupado por `DSC-S-012_anti_deriva_migraciones_supabase.md` desde 2026-05-18). Trazabilidad completa en `bridge/cowork_to_manus_DSC_S_012_AUDIT_DONE_2026_05_26.md`.

---
id: ANEXO-DSC-S-018-PROPUESTA
proyecto: EL-MONSTRUO
tipo: propuesta_dsc_para_firma_cowork
titulo: "DSC-S-018 — Auth fail-closed + Key rotation cadence + Procedimiento de revocación coordinada para Forja v4 enforce. Propuesta de Hilo B (rev 2 post-audit Cowork) para que Cowork audite y firme."
estado: borrador_para_cowork_rev2
fecha_articulacion: 2026-05-26
fecha_revision: 2026-05-26
articulado_por: manus_b (Hilo B — ejecutor técnico)
audited_by_first_pass: cowork (Hilo A — 2026-05-26)
firma_destino: Hilo A (Cowork — arquitecto/canonizador)
precondicion: T1-MAGNA-005 firmada (cualquier opción B/C/D)
supersedes: ANEXO_DSC_S_012_AUTH_FAIL_CLOSED_KEY_ROTATION_PROPUESTA.md
fixes_aplicados:
  - hallazgo_1_BLOQUEANTE: "renumeración DSC-S-012 → DSC-S-018 (S-012 ocupado, S-018 libre, S-009/S-014 huecos no usados por ambigüedad)"
  - hallazgo_2_CORRECCION: "substrate Postgres → TiDB/MySQL (drizzle.config.ts dialect=mysql, drizzle-orm/mysql2 verificado)"
  - hallazgo_3_RECONCILIACION: "cláusula 2.2 explicita relación con DSC-S-008 (S-008 = secrets/API keys; S-018 = claves Ed25519 Forja; cadencia más estricta gobierna)"
fuentes_verificadas:
  - codigo:tablero-campana/server/forja/ed25519.ts (operativa Ed25519, 113 líneas)
  - codigo:tablero-campana/server/forja/gateway.ts (442 líneas, modo shadow actual)
  - codigo:tablero-campana/drizzle/schema.ts (revocationEvents, capabilityTokens)
  - codigo:tablero-campana/drizzle.config.ts (dialect: "mysql")
  - codigo:tablero-campana/server/db.ts (drizzle-orm/mysql2)
  - canon:DSC-S-001..005 (cero secrets en plaintext, AGENTS.md Regla #6)
  - canon:DSC-S-008 (rotación automatizada credenciales — delineación explícita)
  - canon:DSC-S-012 OCUPADO (anti-deriva migraciones supabase, ajeno a este tema)
  - canon:DSC-MO-006 (par crítico embriones)
  - canon:DSC-G-013 (Coherence Gate — esta rev incorpora hallazgos del gate)
cruza_con:
  - T1-MAGNA-005 (Forja shadow→enforce — esta DSC habilita L4-L6)
  - T1-MAGNA-006 (PR Drafts autónomos — embrion como actor firmante)
  - DSC-S-001..005 (esta DSC extiende la familia de seguridad)
  - DSC-S-008 (rotación de credenciales — delineación de scope con esta DSC)
---

# ANEXO — Propuesta DSC-S-018 para Cowork (rev 2 post-audit)

> Documento articulado por Manus B (Hilo B) como propuesta a Cowork (Hilo A) en su rol de canonizador. Esta es la **revisión 2** tras el audit Cowork del 2026-05-26 que detectó 3 hallazgos binarios mediante Coherence Gate. Esta NO es un DSC firmado — es el insumo corregido para que Cowork firme.

## 1. Contexto

T1-MAGNA-005 (Forja v4 shadow → enforce) está pendiente de firma de Alfredo. Cualquier opción que elija (B total, C dos llaves, o D escalonado) requiere que **antes** o **simultáneamente** se firme un DSC de seguridad operativa que cubra:

1. **Auth fail-closed**: comportamiento del gateway cuando una firma Ed25519 no valida.
2. **Key rotation cadence**: cada cuánto rotan las claves Ed25519 de los actores Forja (operador, embrion par, Cowork, Hilo B, observatorio signer).
3. **Procedimiento de revocación coordinada**: qué pasa cuando una clave Ed25519 Forja se compromete o se sospecha leak.

Este anexo es **insumo para Cowork**. Si Cowork firma una versión equivalente, queda como `DSC-S-018` en `_dsc_contracts_index.yaml`.

### 1.1 Por qué DSC-S-018 y no DSC-S-012

`DSC-S-012` ya está ocupado por `DSC-S-012_anti_deriva_migraciones_supabase.md` (canonizado 2026-05-18, sprint MIGRATION-DRIFT-RESOLUTION). Tema no relacionado. Cowork detectó la colisión vía Coherence Gate Nivel A (DSC-G-013). El número monotónico libre siguiente al S-017 es **S-018**. S-009 y S-014 son huecos en la secuencia que **no se usan en esta propuesta** porque pueden estar reservados/retirados en `_archived/` y la ambigüedad violaría DSC-G-008 v2.

## 2. Qué propone esta DSC

### 2.1 Cláusula de fail-closed

> *Cuando el gateway de Forja recibe un envelope con firma Ed25519 inválida, payload mal formado, `signerKeyId` desconocido, o `expiresAt` vencido, debe responder HTTP 403 con el cuerpo `{ "error": "envelope_rejected", "reason": "<razón corta>", "envelopeId": "<id>" }`. NO debe ejecutar el envelope. NO debe encolar reintento automático. NO debe degradar a modo shadow silenciosamente.*

> *El rechazo se persiste en `forja_shadow_calls` con `mode: "rejected"` independientemente del estado enforce/shadow del envelope, y emite evento `forja.envelope.rejected` al `EventStore`.*

> *Bajo ninguna circunstancia se hace fallback a "ejecuta el envelope sin firma". Esto sería violación P0 inmediata.*

### 2.2 Cláusula de cadencia de rotación

> **Esta cláusula extiende `DSC-S-008` (rotación automatizada de credenciales) al dominio específico de claves de firma Ed25519 de actores Forja.** Donde un actor tenga **ambos** (credencial API + clave Ed25519 Forja), la cadencia más estricta entre las dos cláusulas gobierna. Las dos clases de clave NO son intercambiables: DSC-S-008 cubre secrets/API keys (Anthropic, Supabase, Railway, Manus, etc.); DSC-S-018 cubre exclusivamente claves Ed25519 que firman envelopes Forja.

| Tipo de clave Ed25519 Forja | TTL máximo | Disparadores de rotación obligatoria |
|---|---|---|
| **Operador (Alfredo)** | 90 días | Manual + sospecha de exposure + dispositivo perdido |
| **Cowork (rol arquitecto)** | 90 días | Igual + cambio de hilo Cowork canónico |
| **Embrion par crítico (cada uno de los 2)** | 30 días | Auto (T+30d) + post-incidente |
| **Hilo B / Manus** | 60 días | Cambio de cuenta Manus + post-incidente |
| **Observatorio signer** | 180 días | Solo manual + sospecha de exposure |

> *Las rotaciones se commitean al repo en `keys/<actor>/rotations.yaml` con `key_id`, `created_at`, `expires_at`, `pubkey_hex`, `rotated_from_key_id`. Las **claves privadas no se commitean nunca** (DSC-S-001..005). Solo metadata pública.*

> **Delineación explícita con DSC-S-008:** si un actor (ej: Hilo B) tiene una API key Manus que rota cada 60 días por DSC-S-008, y una clave Ed25519 Forja que rota cada 60 días por DSC-S-018, las dos rotaciones son **independientes** (claves distintas, propósitos distintos). Si en cambio una sola key sirve dos propósitos, eso viola la cláusula 2.4 de superficie limitada y no se permite.

### 2.3 Cláusula de revocación coordinada

> *Cuando se sospecha o confirma compromiso de una clave Ed25519 Forja, el procedimiento es:*
>
> 1. *Inmediato (≤5 min): el operador o cualquier hilo con acceso ejecuta `scripts/forja_revoke.py --key-id <id>` que:*
>    - *Inserta entrada en `revocation_events` con `revoked_at = now()`, `reason`, `triggered_by`.*
>    - *Marca `capability_tokens` activos firmados por esa key como `status: revoked`.*
>    - *Emite evento `forja.key.revoked` con prioridad `urgent`.*
>
> 2. *T+15 min: notificación automática al bridge `bridge/incidents/key_revocation_<id>.md` con todos los receipts afectados.*
>
> 3. *T+1 hora: postmortem inicial — qué key, cuándo, cómo se sospechó, qué envelopes ejecutó antes de revocación.*
>
> 4. *T+24 horas: rotación obligatoria de la clave, generación de nueva par, re-firma de DSCs vigentes que apuntaban al keyId viejo.*
>
> 5. *T+72 horas: postmortem completo firmado por Cowork, lecciones aprendidas, mejoras a `validate_sprint_registry.py` o equivalente para prevenir recurrencia.*

### 2.4 Cláusula de superficie limitada

> *Las claves Ed25519 cubiertas por esta DSC firman exclusivamente envelopes Forja. NO se reutilizan para otros propósitos (firma de commits git, autenticación SSH, OAuth, JWT, Anthropic API keys, Supabase service keys, ni cualquier otro secret cubierto por DSC-S-008). Cada propósito tiene su propio par de claves.*
>
> *Para git commit signing, el operador y los hilos usan claves separadas (GPG/SSH commit signing tradicional). Para Forja envelopes, se usa Ed25519 dedicado. Para credenciales API, DSC-S-008.*

### 2.5 Cláusula de auditoría obligatoria

> *El gateway debe loguear toda decisión (acept o rechazo) en `policy_decisions` con `decision_at`, `decision_kind`, `actor_key_id`, `envelope_id`, `outcome`, `reason`. Estos logs son inmutables (append-only) implementados como **trigger MySQL/TiDB** (`BEFORE UPDATE` con `SIGNAL SQLSTATE '45000'`) sobre la tabla, y se replican en `bridge/missions/<MISSION_ID>/4_evidence/` cuando aplique.*
>
> *Cualquier modificación retroactiva a `policy_decisions` se considera P0 inmediato.*

> **Nota de substrate (rev 2 post-audit Cowork):** Forja v4 corre sobre **TiDB/MySQL** (`drizzle.config.ts` dialect=mysql, `server/db.ts` import `drizzle-orm/mysql2`). La implementación append-only **no usa PostgreSQL**, sino el dialecto MySQL/TiDB. La forma canónica del trigger es:
>
> ```sql
> CREATE TRIGGER policy_decisions_no_update
>   BEFORE UPDATE ON policy_decisions
>   FOR EACH ROW
>   SIGNAL SQLSTATE '45000'
>     SET MESSAGE_TEXT = 'policy_decisions is append-only';
> ```
>
> *Vale canonizar de una vez como hallazgo de doctrina cruzada que toda persistencia de Forja es MySQL/TiDB y NO Postgres, para no recometer este error en propuestas futuras.*

## 3. Lo que esta DSC explícitamente NO cubre

Para mantener scope acotado, esta DSC **no** cubre:

- **Política de qué constituye una "acción material irreversible"** → eso es responsabilidad de la matriz de Power Lanes (DSC separado, derivado de T1-MAGNA-005).
- **Política de doble-firma operador + Cowork** → si T1-MAGNA-005 firma Opción C, requiere DSC-S-019 separado (siguiente número monotónico libre tras S-018).
- **Política de embrion como actor firmante** → si T1-MAGNA-006 firma B/C, requiere DSC-MO-EMBRION-PR-AUTONOMY que cruza con esta DSC.
- **Política de monitoreo y alertas** → es responsabilidad del observatorio (Capa 1 transversal).
- **Rotación de secrets/API keys** → DSC-S-008 cubre eso.

## 4. Test de aceptación de la DSC

Para que Cowork firme, los siguientes tests deben pasar (Manus B los puede correr):

```bash
# Test 1: fail-closed responde 403 con firma inválida
curl -X POST $TABLERO/forja/envelope \
  -H "Content-Type: application/json" \
  -d '{"payload":"...", "signature":"INVALID", ...}'
# Espera: HTTP 403, body con error: "envelope_rejected"

# Test 2: clave revocada no acepta nuevos envelopes
scripts/forja_revoke.py --key-id <test_key>
curl -X POST $TABLERO/forja/envelope \
  -H "Content-Type: application/json" \
  -d "$(generate_envelope --signer test_key)"
# Espera: HTTP 403, reason: "key_revoked"

# Test 3: rotación documentada se persiste
scripts/forja_rotate.py --actor operator
test -f keys/operator/rotations.yaml
grep -q "rotated_from_key_id" keys/operator/rotations.yaml

# Test 4: claves privadas no están commiteadas
gitleaks detect --staged --redact
# Espera: 0 hallazgos

# Test 5: policy_decisions append-only (substrate MySQL/TiDB)
# Intentar UPDATE debe fallar por trigger
mysql -h $TIDB_HOST -P $TIDB_PORT -u $TIDB_USER -p$TIDB_PASS $TIDB_DB \
  -e "UPDATE policy_decisions SET outcome='changed' WHERE id=1;"
# Espera: ERROR 1644 (45000): policy_decisions is append-only

# Test 6 (rev 2): delineación con DSC-S-008
# Verificar que actor con doble clave (API + Ed25519) tiene rotaciones independientes
test -f keys/manus_b/rotations.yaml          # Ed25519 Forja
grep -q "manus_api_key" .env.example         # API key DSC-S-008
# Espera: dos archivos/scopes distintos, no fusionados
```

## 5. Cambios de código requeridos para que la DSC sea aplicable

| Componente | Cambio | LoC estimado |
|---|---|---|
| `tablero-campana/server/forja/gateway.ts` | Implementar fail-closed estricto en path de validación | +50 |
| `tablero-campana/server/forja/router.ts` | Endpoint `/forja/revoke` con autenticación operador | +80 |
| `tablero-campana/scripts/forja_revoke.py` | Script CLI de revocación | +120 |
| `tablero-campana/scripts/forja_rotate.py` | Script CLI de rotación | +100 |
| `el-monstruo/keys/<actor>/rotations.yaml` | Estructura inicial vacía por actor | +0 (creación) |
| `tablero-campana/drizzle/migrations/` | **Trigger MySQL/TiDB** `BEFORE UPDATE` `SIGNAL SQLSTATE '45000'` append-only en `policy_decisions` | +30 |
| `tablero-campana/server/forja/forja.policy.test.ts` | Tests de aceptación (6 escenarios incluido test 6 delineación S-008) | +220 |

Total: ~600 líneas, ~2 días de Manus B trabajando focalizado.

> **Cambio rev 2 post-audit:** la línea de migración cambió de "Trigger PostgreSQL" a "Trigger MySQL/TiDB `BEFORE UPDATE` + `SIGNAL SQLSTATE '45000'`". Test 5 cambió de `psql` a cliente `mysql` con código de error MySQL. Test 6 nuevo verifica delineación con DSC-S-008.

## 6. Lo que se espera de Cowork al recibir esta propuesta (rev 2)

1. **Auditar la lógica de las 5 cláusulas** contra DSCs vigentes (DSC-S-001..005, DSC-S-008, DSC-MO-006). Identificar conflictos o gaps remanentes.
2. **Validar la matriz de cadencia de rotación** — ¿90 días para operador es razonable? ¿30 días para embriones es realista dado el cost de re-firma?
3. **Verificar la separación de claves Forja vs git vs API keys** — ¿esto es operativamente factible o introduce fricción excesiva?
4. **Aprobar el procedimiento de revocación coordinada** — ¿los SLAs (5 min, 15 min, 1h, 24h, 72h) son alcanzables?
5. **Confirmar que la delineación con DSC-S-008 es sin ambigüedad** — la frase "cadencia más estricta gobierna" es operativa.
6. **Si concuerda, emitir DSC-S-018 oficial** firmado, con número de versión, e indexar en `_dsc_contracts_index.yaml`.

## 7. Lo que se espera de Manus B después de la firma

1. Implementar los cambios de código (Sección 5) en sprint dedicado: `FORJA_SECURITY_S018_v1` (agregar al registry).
2. Correr los 6 tests de aceptación.
3. Documentar postmortem si aparece bug durante implementación.
4. Notificar a Cowork al cierre del sprint para audit pre-cierre (DSC-G-008 v2).

## 8. Notas finales

Este anexo no obliga a Cowork. Es **insumo de un ejecutor (Hilo B) hacia un canonizador (Hilo A)**. La doctrina del Monstruo (división de responsabilidades de hilos) establece que Cowork canoniza y Manus ejecuta. Entonces: Hilo B identifica que **el ecosistema necesita esta DSC para no quedar bloqueado por T1-MAGNA-005**, redacta una propuesta técnica concreta, la entrega al canonizador para que la audite y firme, e itera correcciones cuando el canonizador detecta hallazgos.

Esta es la rev 2 tras el primer ciclo de audit (Cowork detectó 3 hallazgos binarios, Manus B los aplicó, ahora vuelve a Cowork). Si Cowork audita rev 2 y discrepa con cualquier cláusula, la respuesta canónica es: Cowork emite contrapropuesta o cambios a este documento; Manus B incorpora; itera hasta acuerdo. Si llegan a impasse, escala a Alfredo como decisión T1.

**Recordatorio doctrinal**: ningún DSC se firma sin que sea estrictamente necesario (DSC-G-008 v2 prohibe DSCs sobre DSCs sin causa). Esta propuesta justifica su necesidad por su rol como pre-condición para T1-MAGNA-005 enforce. Si T1-MAGNA-005 firma Opción A (shadow indefinido), esta DSC no es necesaria y queda en estado `withdrawn`. Adicionalmente, la delineación explícita con DSC-S-008 (sección 2.2) justifica que esta DSC no es un duplicado: las claves Ed25519 Forja son una clase distinta que requiere su propia política de rotación.

---

**Articulado por:** Manus B (cuenta `manus_b` — Hilo B ejecutor técnico)
**Destinado a:** Hilo A (Cowork — arquitecto/canonizador)
**Fecha de articulación:** 2026-05-26
**Fecha de revisión post-audit:** 2026-05-26
**Bloqueo que resuelve:** habilitación segura de Forja v4 enforce (cualquier opción T1-MAGNA-005 B/C/D)
**Tiempo estimado de audit Cowork rev 2:** 30 min (validación de fixes incrementales)
**Tiempo estimado de implementación Manus B post-firma:** 2 días
**Thread Immunity Session origen:** 8af84475-598b-4d14-aa79-7d5e0c0c589c
**Audit pass 1 origen:** `bridge/cowork_to_manus_DSC_S_012_AUDIT_DONE_2026_05_26.md` (commit `f75b570`)
