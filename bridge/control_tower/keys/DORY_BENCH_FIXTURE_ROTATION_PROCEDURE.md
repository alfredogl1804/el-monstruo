# DORY_BENCH Fixture Rotation Procedure (B7-E3)

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Gate:** B7 — Hidden Fixture Custody no-compositor
**Fuente normativa:** closure pack v0.2 §3.2 (B7.5)
**Aplica a:** los 50 hidden fixtures de DORY_BENCH consumidos por CVDS

> Este procedimiento NO se ejecuta hasta que T1 firme decisiones D-B7-1..D-B7-5. No implementa runtime.

---

## §1 Alcance

Define el ciclo de vida trimestral (cada 90 días) de rotación de los 50 hidden fixtures que alimentan a DORY_BENCH y a la métrica CVDS = PASS_conocidos / PASS_ocultos ≥ 0.95. Cubre **generación**, **distribución a custodios**, **uso por el runner**, **retiro de fixtures viejos** y **fallback de emergencia**.

---

## §2 Frecuencia (propuesta T1-pending D-B7-3)

- **Programada:** cada 90 días naturales (alineada con calendario trimestral B11 de Sabios auditores).
- **Post-incidente:** dentro de las 24 horas siguientes a la detección de cualquiera de los eventos en §3.
- **No-go:** rotaciones a discreción de un solo agente sin orden T1 explícita.

---

## §3 Triggers de rotación post-incidente

| Trigger | Detector | Severidad |
|---------|----------|-----------|
| Filtración inadvertida de uno o más fixtures detectada (audit B7-E7 con `FIXTURE_LEAK_DETECTED_PROMPT`) | VERIFICADOR-001 | crítico |
| Bug del runner que escribe fixtures a log persistente | Audit log B7-E5 | crítico |
| Compromiso de un custodio (acceso no autorizado a un slice) | Audit cloud + reporte humano | crítico |
| Sabio auditor influenció fixtures (detectado por análisis B11-E5 estilo Grok) | Sabio externo | alto |
| Cambio de tooling de cifrado D-B6 / D-B7-5 firmado por T1 | Decisión T1 | medio |

---

## §4 Pasos de la rotación programada

### §4.1 Pre-condiciones

Antes de iniciar:

1. Quórum 2-de-3 de custodios B7.3 confirma disponibilidad (D-B7-4).
2. Sabio auditor del trimestre saliente (B11) completó auditoría B7-E4 firmada.
3. Inventario actual B7-E1 (hashes) coincide con los slices cifrados en posesión de los custodios.
4. `local_unreachable: DISABLED_FOR_MAGNA_ACTIONS` no está activo (rotación es acción magna categoría h del B8).
5. T1 disponible para firma magna del audit log de rotación.

### §4.2 Generación de los nuevos fixtures (mínimo 10)

1. **Productor autorizado:** autor NO-Cowork (Manus E2 o Sabio externo en rol de auditor documental). NO Cowork T2-A. NO el Sabio auditor del trimestre saliente (regla B7.5b).
2. El productor diseña ≥10 fixtures nuevos cubriendo casos de Síndrome de Dory no representados en el set actual.
3. Cada fixture incluye: prompt detonador, expected behavior (PASS criterion), tolerance, taxonomía Dory aplicable.
4. Los fixtures se generan en un sandbox firmado (CI o sandbox con identidad ed25519) y se cifran inmediatamente con la clave pública de cada custodio (D-B7-5).
5. El productor **nunca** persiste los fixtures en plaintext en filesystem propio.

### §4.3 Distribución a custodios (Shamir 2-de-3 sobre el set)

1. El set de fixtures se divide en 3 slices usando Shamir Secret Sharing con quórum 2-de-3.
2. Cada slice se cifra con la clave pública del custodio correspondiente.
3. Cada custodio recibe su slice por canal de su elección (D-B7-5):
   - **(a) T1 escrow:** Alfredo guarda el slice en keychain personal.
   - **(b) Cuenta cloud privada T1:** bucket GCS/S3 con CMEK + IAM allow-list a T1.
   - **(c) HSM/KMS remoto:** Vault / AWS KMS / GCP KMS.
   - **(d) Humano delegado:** persona física con commitment escrito.
   - **(e) Repo GitHub/Codeberg privado:** custodio descifra con clave fuera del repo.
4. Cada custodio confirma recepción y verifica que su slice descifra correctamente. Confirmación se loggea en B7-E4.

### §4.4 Retiro de fixtures viejos (mínimo 10)

1. Sabio auditor del trimestre saliente identifica fixtures con sospecha de leak, overfit detectado, o influencia del Sabio activo (auto-auditoría).
2. Los fixtures retirados se marcan en B7-E1 con `retired_at` y `retirement_reason`.
3. Los slices viejos NO se destruyen; se archivan cifrados en `bridge/control_tower/fixtures/archived/` con prefijo de fecha. Razón: forensics en caso de futuro incidente.
4. El runner DORY_BENCH actualiza su inventario de fixtures activos vía decryption de los nuevos slices.

### §4.5 Rotación del custodio activo

Aplica regla binaria B7.5c: el custodio del trimestre actual no puede ser el mismo que en los 2 trimestres anteriores. Plan rotativo propuesto (T1-pending D-B7-1):

| Trimestre | Custodio principal | Quórum 2-de-3 |
|-----------|--------------------|-----------|
| Q1 | (a) T1 escrow | (a) + (b) o (a) + (c) |
| Q2 | (b) Cuenta cloud privada T1 | (b) + (c) o (b) + (a) |
| Q3 | (c) HSM/KMS remoto | (c) + (a) o (c) + (b) |
| Q4 | (d) Humano delegado o (e) Repo cifrado | quórum con dos de los anteriores |

El custodio "principal" del trimestre coordina la decryption durante runs DORY_BENCH; los otros dos del quórum participan firmando la decryption.

### §4.6 Designación del nuevo Sabio auditor (cross-ref B11)

El Sabio auditor del trimestre entrante se designa según calendario B11 fijo:

| Trimestre | Sabio auditor (B11) |
|-----------|-----|
| Q1 | Opus 4.7 |
| Q2 | DeepSeek R1 |
| Q3 | Gemini 3.1 Pro |
| Q4 | Kimi K2.6 |

El Sabio recibe únicamente **hashes, métricas agregadas, resultados sanitizados** (no contenido).

### §4.7 Audit log

Cada rotación produce una entrada en `bridge/control_tower/evidence/B7/B7_E4_rotation_audit.jsonl` con los campos:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `rotation_id` | uuid | Identificador único de la rotación |
| `quarter` | string | `Q1-2026`, `Q2-2026`, etc. |
| `timestamp_iso` | string ISO 8601 | Fecha/hora de inicio |
| `trigger` | enum | `scheduled_90d`, `incident_<tipo>` |
| `fixtures_added_hashes` | array of sha256 | Hashes de los nuevos fixtures |
| `fixtures_retired_hashes` | array of sha256 | Hashes retirados |
| `fixtures_retired_reasons` | array of string | Razón verbatim por retiro |
| `set_hash_before` | sha256 | Merkle root del set anterior |
| `set_hash_after` | sha256 | Merkle root del nuevo set |
| `custodian_quorum` | array of string | IDs de los 2-3 custodios que firmaron decryption |
| `producer_id` | string | Identidad firmada del productor de los nuevos fixtures (NO-Cowork, NO Sabio saliente) |
| `sabio_auditor_outgoing_id` | string | Sabio activo del trimestre saliente que firmó auditoría B7-E4 |
| `sabio_auditor_incoming_id` | string | Sabio activo del trimestre entrante |
| `t1_signature` | string | Firma magna T1 |
| `notes` | string | Observaciones |

---

## §5 Fallback de emergencia (B7.5 v0.2)

Si la terna de custodios no alcanza quórum 2-de-3 por indisponibilidad (>72 h sin respuesta de 2 de 3):

1. T1 escrow humano funciona como custodio de emergencia con quórum reducido a 1 (T1 firma sola la decryption).
2. La rotación se completa con la firma única de T1; los otros custodios reciben sus slices en cuanto se restauren.
3. El audit log B7-E4 marca el campo `fallback_t1_solo: true` con razón verbatim.
4. Plazo de restauración: 30 días. Si pasados 30 días no se restaura la terna, T1 designa nuevos custodios firmando una decisión adicional.

---

## §6 No-go

- No se rota con Cowork T2-A o Grok 4 como custodios (regla binaria B7.2).
- No se rota con Sabio LLM como custodio (regla binaria v0.2).
- No se rota con productor de fixtures que sea simultáneamente Sabio auditor del trimestre actual (regla B7.5a/b).
- No se persiste el set descifrado en disco del runner (regla B7.6).
- No se omite el audit log B7-E4.
- No se descarta `local_unreachable: DISABLED_FOR_MAGNA_ACTIONS` (rotación = acción magna B8 categoría h).
- No se envía contenido de fixtures al prompt del Sabio auditor (regla B7.4 + B7.8).

---

**Firma magna pendiente.** Este procedimiento entra en operación cuando T1 firme D-B7-1..D-B7-5.
