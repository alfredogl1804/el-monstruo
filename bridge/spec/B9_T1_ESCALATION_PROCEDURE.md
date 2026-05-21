# B9-E4 — T1 Escalation Procedure (Design)

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Gate:** B9 — VERIFICADOR authority/degradation matrix
**Fuente normativa:** closure pack v0.2 §5.4 (B9-E4)
**Nota productor:** según closure v0.2, B9-E4 es producido por T1 verbatim (T1 redacta el procedimiento de su propia escalación). Este documento es un **borrador propuesto por Manus E2 como input para T1**; T1 puede aceptar, modificar o reescribir antes de firma magna.

> Este procedimiento NO se ejecuta hasta que T1 firme decisiones D-B9-1..D-B9-4. No implementa runtime.

---

## §1 Alcance

Define cuándo y cómo el sistema escala una decisión a T1 (Alfredo Góngora) cuando los actores VERIFICADOR-001, Memento Validator y Guardian Decision View no logran consenso binario o cuando uno o más están en estado degradado.

---

## §2 Triggers de escalación a T1

| Trigger | Origen | Plazo SLA |
|---------|--------|-----------|
| **B9.4 — Guardian solicita override sobre VERIFICADOR DENY** | Guardian Decision View | T+15 min |
| **B9.5 — Acción requiere firma magna T1 sobre VERIFICADOR DENY** | Operador o Guardian | T+15 min |
| **B9.6 — VERIFICADOR_DEGRADED prolongado >24h** | Heartbeat monitor | T+30 min de detección |
| **B9.7 — MEMENTO_DEGRADED y acción magna en cola** | Memento Validator monitor | T+30 min |
| **B9.8 — Cola AWAITING_GUARDIAN supera threshold (24h o 50 items)** | Guardian queue monitor | T+30 min |
| **DUAL_DEGRADED_HALT_MAGNA** (cascada §5.4 spec) | Multi-component monitor | T+15 min |
| **FULL_DEGRADED_AWAITING_T1** (3 no-T1 caídos) | Multi-component monitor | T+5 min |
| **Memento amendment requerido** (B9.3 con resolución que altera cuerpo legal) | Memento Validator + Cowork | T+24h |

---

## §3 Canales de notificación redundantes a T1

Cada escalación debe usar **al menos 2** de los siguientes canales en paralelo:

1. Bot Telegram del Monstruo (canal personal de Alfredo).
2. WhatsApp directo.
3. Email a la dirección personal de T1.
4. Notificación push del Bridge UI / La Forja.
5. SMS (fallback si los anteriores no responden).
6. Llamada telefónica automatizada (último recurso para incidentes críticos con SLA T+5 min).

El `incident_id` debe estar presente en todos los canales con el mismo identificador para evitar duplicación.

---

## §4 Estructura del payload de escalación

Cada escalación a T1 incluye un payload firmado con la siguiente estructura:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `incident_id` | uuid | Identificador único reproducible |
| `timestamp_iso` | string ISO 8601 | Momento de detección |
| `trigger_type` | enum | B9.4 / B9.5 / B9.6 / B9.7 / B9.8 / DUAL / FULL / MEMENTO_AMEND |
| `verificador_state` | enum | ALLOW / DENY / DEGRADED |
| `memento_state` | enum | ALLOW / DENY / DEGRADED |
| `guardian_state` | enum | ALLOW / DENY / DEGRADED / AWAITING |
| `proposed_action` | string | Descripción verbatim de la acción magna |
| `proposed_action_category` | enum | a / b / c / d / e / f / g / h / i / j / k / l / m (taxonomía B8) |
| `proposed_action_payload_hash` | sha256 | Hash del payload de la acción |
| `verificador_deny_reason` | string | Razón verbatim si DENY |
| `memento_deny_reason` | string | Razón verbatim si DENY |
| `guardian_override_reason` | string | Razón verbatim de Guardian si solicita override |
| `sabio_auditor_id` | string | Identidad del Sabio auditor designado |
| `proposed_resolution` | string | Propuesta de Manus E2 o Cowork como input no vinculante a T1 |
| `signature_verificador_001` | string | Firma del payload por VERIFICADOR-001 (si operable) |

---

## §5 Pasos del flujo de decisión T1

### §5.1 Recepción y validación

T1 recibe la notificación en al menos 2 canales. Verifica que el `incident_id` coincida entre canales (anti-spoofing humano).

### §5.2 Decisión binaria

T1 responde por canal firmado (Bridge UI con firma SSH/Yubikey de T1, o commit firmado al repo) con una de las siguientes opciones:

| Opción | Significado | Evento loggeado |
|--------|-------------|-----------------|
| `T1_ALLOW <razón verbatim>` | T1 autoriza la acción a pesar del veto técnico | `T1_OVERRIDE_<COMPONENT>_DENY` |
| `T1_DENY <razón verbatim>` | T1 confirma el veto o lo refuerza | `T1_HONORS_<COMPONENT>_VETO` |
| `T1_ESCALATE_SABIO <Sabio_id> <pregunta>` | T1 consulta al Sabio auditor antes de decidir | `T1_REQUESTS_SABIO_OPINION` |
| `T1_DEFER <razón> <plazo>` | T1 difiere la decisión; acción queda en cola con timeout | `T1_DEFERRED_DECISION` |
| `T1_AMEND_MEMENTO <patch>` | T1 modifica el cuerpo legal Memento como base de la decisión | `T1_MEMENTO_AMENDMENT` |

T1 puede combinar opciones (`T1_DENY` + `T1_AMEND_MEMENTO`) según el caso.

### §5.3 Ejecución de la decisión

1. El bridge propaga la decisión firmada T1 al runtime.
2. VERIFICADOR-001 valida la firma T1 sobre la decisión (cadena de firmas ed25519 B6).
3. La acción magna procede o se bloquea según T1.
4. Notificación obligatoria a Cowork T2-A + Sabio auditor designado (D-B9-3) con copia de la decisión firmada.
5. Entrada inmutable en `audit_log_immutable` (Supabase, RLS estricto) con `incident_id`, `t1_decision`, `t1_signature_hash`, `outcome`.

### §5.4 Cierre del incidente

T1 cierra el `incident_id` cuando la acción se ejecutó (o se rechazó definitivamente) y la cadena de notificación completó. El cierre incluye:

- Lecciones aprendidas (campo `lessons_learned` opcional).
- Si la decisión revela un gap en la matriz B9 o en la taxonomía B8, T1 indica si abre amendment via B8-E4.

---

## §6 Métricas anti-abuso de override T1

Para evitar que B9.5 (T1 override sobre VERIFICADOR DENY) degenere en bypass sistemático:

| Métrica | Threshold | Acción si se supera |
|---------|-----------|---------------------|
| `t1_override_count_30d` | >10 en 30 días | Sabio auditor genera reporte verbatim de análisis de patrones |
| `t1_override_per_category` | >3 en una misma categoría B8 (a-m) en 30 días | Cowork audita la matriz B9 + revisa si el spec necesita amendment |
| `t1_override_no_reason` | 1 (cualquiera) | INMEDIATA: Sabio auditor abre alerta crítica al bridge |
| `t1_override_sla_t30min` | Promedio >30 min en 30 días | Optimización del canal de notificación, no es señal de abuso |

Las métricas se publican mensualmente en el bridge público sanitizado (no contenido del payload, solo conteos y categorías).

---

## §7 No-go

- No se procesa una escalación sin `incident_id` reproducible.
- No se acepta decisión T1 sin firma ed25519 (Bridge UI o commit firmado).
- No se ejecuta `T1_ALLOW` sin razón verbatim.
- No se omite la entrada en `audit_log_immutable`.
- No se permite a Guardian, Memento, VERIFICADOR o Cowork **simular** una decisión T1 (regla binaria; cualquier intento es FAIL del actor).
- No se omiten métricas anti-abuso §6.

---

## §8 Cross-refs

- **B6:** firma T1 sobre la decisión depende de la clave ed25519 custodiada según B6.
- **B8:** acción magna categorías (a)-(m) se referencian en `proposed_action_category`.
- **B11:** Sabio auditor designado en `sabio_auditor_id` proviene del calendario rotativo B11.
- **AGENTS.md Regla Dura #7:** `audit_log_immutable` está bajo RLS estricta con policy explícita.

---

**Firma magna pendiente.** Este procedimiento entra en operación cuando T1 lo apruebe verbatim (B9-E4 es producido por T1; este DRAFT es solo input).
