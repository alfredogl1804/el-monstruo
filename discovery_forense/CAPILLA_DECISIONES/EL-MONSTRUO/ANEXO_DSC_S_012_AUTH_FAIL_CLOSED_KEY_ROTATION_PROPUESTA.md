**Estado:** Aspiracional.

**Nota de superseñalado:** SUPERSEDED el 2026-05-26.

> **DOCUMENTO SUPERSEDED EL 2026-05-26 POR `ANEXO_DSC_S_018_AUTH_FAIL_CLOSED_KEY_ROTATION_PROPUESTA.md`.**
>
> Cowork (Hilo A) detectó vía Coherence Gate Nivel A (DSC-G-013) que el número `DSC-S-012` ya estaba ocupado por `DSC-S-012_anti_deriva_migraciones_supabase.md` desde 2026-05-18. Además detectó substrate mismatch (Postgres vs MySQL/TiDB) en cláusula 2.5 + Test 5, y overlap con DSC-S-008 (rotación de credenciales) en cláusula 2.2.
>
> La versión corregida (rev 2) vive en `ANEXO_DSC_S_018_AUTH_FAIL_CLOSED_KEY_ROTATION_PROPUESTA.md` con renumeración a S-018, substrate corregido a MySQL/TiDB y delineación explicita con DSC-S-008.
>
> Trazabilidad del audit: `bridge/cowork_to_manus_DSC_S_012_AUDIT_DONE_2026_05_26.md` (commit `f75b570`).
>
> **NO USAR ESTE DOCUMENTO. USAR EL S-018.** Se preserva por trazabilidad doctrinal y por DSC-S-005 (default archive antes de delete).

---

No es un DSC firmado. Es articulación T1 pendiente de firma magna. La firma del operador (o de Cowork para el Anexo DSC-S-012) genera el contrato canónico al completar el bloque YAML correspondiente.

---
id: ANEXO-DSC-S-012-PROPUESTA
proyecto: EL-MONSTRUO
tipo: propuesta_dsc_para_firma_cowork
titulo: "DSC-S-012 — Auth fail-closed + Key rotation cadence + Procedimiento de revocación coordinada para Forja v4 enforce. Propuesta de Hilo B para que Cowork audite y firme."
estado: borrador_para_cowork
fecha_articulacion: 2026-05-26
articulado_por: manus_b (Hilo B — ejecutor técnico)
firma_destino: Hilo A (Cowork — arquitecto/canonizador)
precondicion: T1-MAGNA-005 firmada (cualquier opción B/C/D)
fuentes_verificadas:
  - codigo:tablero-campana/server/forja/ed25519.ts (operativa Ed25519, 113 líneas)
  - codigo:tablero-campana/server/forja/gateway.ts (442 líneas, modo shadow actual)
  - codigo:tablero-campana/drizzle/schema.ts (revocationEvents, capabilityTokens)
  - canon:DSC-S-001..005 (cero secrets en plaintext, AGENTS.md Regla #6)
  - canon:DSC-MO-006 (par crítico embriones)
cruza_con:
  - T1-MAGNA-005 (Forja shadow→enforce — esta DSC habilita L4-L6)
  - T1-MAGNA-006 (PR Drafts autónomos — embrion como actor firmante)
  - DSC-S-001..005 (esta DSC extiende la familia de seguridad)
---

# ANEXO — Propuesta DSC-S-012 para Cowork

> Documento articulado por Manus B (Hilo B) como propuesta a Cowork (Hilo A) en su rol de canonizador. Este NO es un DSC firmado — es el insumo para que Cowork audite y, si concuerda, firme.

## 1. Contexto

T1-MAGNA-005 (Forja v4 shadow → enforce) está pendiente de firma de Alfredo. Cualquier opción que elija (B total, C dos llaves, o D escalonado) requiere que **antes** o **simultáneamente** se firme un DSC de seguridad operativa que cubra:

1. **Auth fail-closed**: comportamiento del gateway cuando una firma Ed25519 no valida.
2. **Key rotation cadence**: cada cuánto rotan las claves del operador, embriones, hilos y observatorio.
3. **Procedimiento de revocación coordinada**: qué pasa cuando una clave se compromete o se sospecha leak.

Este anexo es **insumo para Cowork**. Si Cowork firma una versión equivalente, queda como `DSC-S-012` en `_dsc_contracts_index.yaml`.

## 2. Qué propone esta DSC

### 2.1 Cláusula de fail-closed

> *Cuando el gateway de Forja recibe un envelope con firma Ed25519 inválida, payload mal formado, `signerKeyId` desconocido, o `expiresAt` vencido, debe responder HTTP 403 con el cuerpo `{ "error": "envelope_rejected", "reason": "<razón corta>", "envelopeId": "<id>" }`. NO debe ejecutar el envelope. NO debe encolar reintento automático. NO debe degradar a modo shadow silenciosamente.*

> *El rechazo se persiste en `forja_shadow_calls` con `mode: "rejected"` independientemente del estado enforce/shadow del envelope, y emite evento `forja.envelope.rejected` al `EventStore`.*

> *Bajo ninguna circunstancia se hace fallback a "ejecuta el envelope sin firma". Esto sería violación P0 inmediata.*

### 2.2 Cláusula de cadencia de rotación

| Tipo de clave | TTL máximo | Disparadores de rotación obligatoria |
|---|---|---|
| **Operador (Alfredo)** | 90 días | Manual + sospecha de exposure + dispositivo perdido |
| **Cowork (rol arquitecto)** | 90 días | Igual + cambio de hilo Cowork canónico |
| **Embrion par crítico (cada uno de los 2)** | 30 días | Auto (T+30d) + post-incidente |
| **Hilo B / Manus** | 60 días | Cambio de cuenta Manus + post-incidente |
| **Observatorio signer** | 180 días | Solo manual + sospecha de exposure |

> *Las rotaciones se commitean al repo en `keys/<actor>/rotations.yaml` con `key_id`, `created_at`, `expires_at`, `pubkey_hex`, `rotated_from_key_id`. Las **claves privadas no se commitean nunca** (DSC-S-001..005). Solo metadata pública.*

### 2.3 Cláusula de revocación coordinada

> *Cuando se sospecha o confirma compromiso de una clave, el procedimiento es:*
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

> *Las claves cubiertas por esta DSC firman exclusivamente envelopes Forja. NO se reutilizan para otros propósitos (firma de commits git, autenticación SSH, OAuth, JWT). Cada propósito tiene su propio par de claves.*
>
> *Para git commit signing, el operador y los hilos usan claves separadas (GPG/SSH commit signing tradicional). Para Forja, se usa Ed25519 dedicado.*

### 2.5 Cláusula de auditoría obligatoria

> *El gateway debe loguear toda decisión (acept o rechazo) en `policy_decisions` con `decision_at`, `decision_kind`, `actor_key_id`, `envelope_id`, `outcome`, `reason`. Estos logs son inmutables (append-only) y se replican en `bridge/missions/<MISSION_ID>/4_evidence/` cuando aplique.*
>
> *Cualquier modificación retroactiva a `policy_decisions` se considera P0 inmediato.*

## 3. Lo que esta DSC explícitamente NO cubre

Para mantener scope acotado, esta DSC **no** cubre:

- **Política de qué constituye una "acción material irreversible"** → eso es responsabilidad de la matriz de Power Lanes (DSC separado, derivado de T1-MAGNA-005).
- **Política de doble-firma operador + Cowork** → si T1-MAGNA-005 firma Opción C, requiere DSC-S-013 separado.
- **Política de embrion como actor firmante** → si T1-MAGNA-006 firma B/C, requiere DSC-MO-EMBRION-PR-AUTONOMY que cruza con esta DSC.
- **Política de monitoreo y alertas** → es responsabilidad del observatorio (Capa 1 transversal).

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

# Test 5: policy_decisions append-only
# Intentar UPDATE en supabase debe fallar por trigger
psql -c "UPDATE policy_decisions SET outcome='changed' WHERE id=1;"
# Espera: error "policy_decisions is append-only"
```

## 5. Cambios de código requeridos para que la DSC sea aplicable

| Componente | Cambio | LoC estimado |
|---|---|---|
| `tablero-campana/server/forja/gateway.ts` | Implementar fail-closed estricto en path de validación | +50 |
| `tablero-campana/server/forja/router.ts` | Endpoint `/forja/revoke` con autenticación operador | +80 |
| `tablero-campana/scripts/forja_revoke.py` | Script CLI de revocación | +120 |
| `tablero-campana/scripts/forja_rotate.py` | Script CLI de rotación | +100 |
| `el-monstruo/keys/<actor>/rotations.yaml` | Estructura inicial vacía por actor | +0 (creación) |
| `tablero-campana/drizzle/migrations/` | Trigger PostgreSQL append-only en `policy_decisions` | +30 |
| `tablero-campana/server/forja/forja.policy.test.ts` | Tests de aceptación (5 escenarios) | +200 |

Total: ~580 líneas, ~2 días de Manus B trabajando focalizado.

## 6. Lo que se espera de Cowork al recibir esta propuesta

1. **Auditar la lógica de las 5 cláusulas** contra DSCs vigentes (DSC-S-001..005, DSC-MO-006). Identificar conflictos o gaps.
2. **Validar la matriz de cadencia de rotación** — ¿90 días para operador es razonable? ¿30 días para embriones es realista dado el cost de re-firma?
3. **Verificar la separación de claves Forja vs git** — ¿esto es operativamente factible o introduce fricción excesiva?
4. **Aprobar el procedimiento de revocación coordinada** — ¿los SLAs (5 min, 15 min, 1h, 24h, 72h) son alcanzables?
5. **Agregar cláusulas que esta propuesta omite por desconocimiento** — Cowork conoce contexto histórico que Hilo B puede no tener.
6. **Si concuerda, emitir DSC-S-012 oficial** firmado, con número de versión, e indexar en `_dsc_contracts_index.yaml`.

## 7. Lo que se espera de Manus B después de la firma

1. Implementar los cambios de código (Sección 5) en sprint dedicado: `FORJA_SECURITY_S012_v1` (agregar al registry).
2. Correr los 5 tests de aceptación.
3. Documentar postmortem si aparece bug durante implementación.
4. Notificar a Cowork al cierre del sprint para audit pre-cierre (DSC-G-008 v2).

## 8. Notas finales

Este anexo no obliga a Cowork. Es **insumo de un ejecutor (Hilo B) hacia un canonizador (Hilo A)**. La doctrina del Monstruo (división de responsabilidades de hilos) establece que Cowork canoniza y Manus ejecuta. Entonces: Hilo B identifica que **el ecosistema necesita esta DSC para no quedar bloqueado por T1-MAGNA-005**, redacta una propuesta técnica concreta, y la entrega al canonizador para que la audite y firme.

Si Cowork audita y discrepa con cualquier cláusula, la respuesta canónica es: Cowork emite contrapropuesta o cambios a este documento; Manus B incorpora; itera hasta acuerdo. Si llegan a impasse, escala a Alfredo como decisión T1.

**Recordatorio doctrinal**: ningún DSC se firma sin que sea estrictamente necesario (DSC-G-008 v2 prohibe DSCs sobre DSCs sin causa). Esta propuesta justifica su necesidad por su rol como pre-condición para T1-MAGNA-005 enforce. Si T1-MAGNA-005 firma Opción A (shadow indefinido), esta DSC no es necesaria y queda en estado `withdrawn`.

---

**Articulado por:** Manus B (cuenta `manus_b` — Hilo B ejecutor técnico)
**Destinado a:** Hilo A (Cowork — arquitecto/canonizador)
**Fecha de articulación:** 2026-05-26
**Bloqueo que resuelve:** habilitación segura de Forja v4 enforce (cualquier opción T1-MAGNA-005 B/C/D)
**Tiempo estimado de audit Cowork:** 1 jornada
**Tiempo estimado de implementación Manus B post-firma:** 2 días
**Thread Immunity Session:** 8af84475-598b-4d14-aa79-7d5e0c0c589c
