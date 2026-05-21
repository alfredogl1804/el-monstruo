# DORY_CURE Key Revocation Procedure (B6-E5)

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Gate:** B6 — Key Custody ed25519
**Fuente normativa:** closure pack v0.2 §2.2 (B6.5)
**SLA objetivo:** revocación efectiva en <60 minutos desde detección de compromiso

> Este procedimiento NO se ejecuta hasta que T1 firme decisiones D-B6-1..D-B6-5. No implementa runtime.

---

## §1 Alcance

Define cómo invalidar la clave ed25519 actual del kill switch local-first del gate B1 cuando se sospecha **compromiso**, **filtración**, o **uso no autorizado**. El procedimiento prioriza velocidad (SLA 60 min) sobre la elegancia de la ventana dual-key usada en rotación programada (`DORY_CURE_KEY_ROTATION_PROCEDURE.md`).

---

## §2 Triggers que disparan revocación de emergencia

| Trigger | Detector | Acción inmediata |
|---------|----------|------------------|
| Filtración pública confirmada de la `.sec` | Reporte humano + canal de threat intel | Revocación |
| Sospecha fundada de compromiso del custodio (HSM, keychain, hardware token) | Audit log de accesos anómalos | Revocación |
| Firma válida sobre kill_file no autorizado por T1 detectada en runtime | VERIFICADOR-001 + bridge | Revocación |
| Acceso físico no autorizado al hardware token (extravío + reuso evidente) | Reporte humano | Revocación |
| Empleado / colaborador con acceso pierde autorización (offboarding crítico) | Decisión T1 | Revocación |
| CVE crítico (CVSS ≥ 9.0) del tooling D-B6-5 sin mitigación disponible | CVE feed | Revocación |

---

## §3 Cadena de notificación (T0 = detección)

| T+ | Acción | Responsable |
|----|--------|-------------|
| T+0 min | Detección registrada en bridge con `incident_id` | Detector (humano o VERIFICADOR-001) |
| T+5 min | Notificación push a T1 (Alfredo) por canal redundante: bot Monstruo Telegram + WhatsApp + email | Bridge automation |
| T+10 min | T1 confirma o desestima el incidente | T1 humano |
| T+15 min | Si confirma, T1 firma orden verbatim `REVOKE_DORY_CURE_KEY <key_hash>` en el bridge | T1 humano |
| T+20 min | Cowork T2-A notificado como observador (no firmante) | Bridge automation |
| T+25 min | Sabio externo auditor (D-B6-3, propuesta Opus 4.7) recibe hash + sanitized context | Bridge automation |
| T+30 min | Ejecución técnica de §4 inicia | Operador autorizado (T1 o Cowork según D-B6-1) |
| T+60 min | Estado `KEY_REVOKED` activo, kill switch en modo `DORY_CURE_HALTED` hasta nueva clave promovida | VERIFICADOR-001 |

Si T1 no responde en T+30 min, el bridge eleva a segundo canal humano de respaldo definido por T1 (futura D-B6-6 opcional, no resuelta en v0.2).

---

## §4 Pasos técnicos de revocación

### §4.1 Invalidación inmediata de la clave actual

1. T1 (o Cowork con firma T1 explícita en el `incident_id`) elimina `.monstruo/keys/dory_cure_kill_switch.pub` del repo:

   ```bash
   git mv .monstruo/keys/dory_cure_kill_switch.pub .monstruo/keys/revoked/dory_cure_kill_switch.<incident_id>.pub
   git commit -S -m "B6 revoke dory_cure_kill_switch <incident_id> - <causa>"
   git push origin <branch>
   ```

2. Hash anchor en `.monstruo/keys/CURRENT_KEY_HASH` se vacía o reemplaza por sentinel `REVOKED_<incident_id>`.
3. VERIFICADOR-001 detecta el cambio en su próximo ciclo (≤5s con TTL B8) y entra en estado `KEY_REVOKED`.

### §4.2 Estado del sistema durante la ventana sin clave

- Kill switch local-first (`.monstruo/kill_switches/DORY_CURE_DISABLED`) queda **sin firmador válido**.
- El agente entra en modo `DORY_CURE_HALTED`: las acciones magnas (B8 lista a-m) son automáticamente bloqueadas con evento `KILL_SWITCH_NO_VALID_KEY_BLOCKING_ALL_MAGNA`.
- Acciones no-magnas continúan operando con warning `DORY_CURE_HALTED_DEGRADED`.
- Esta ventana debe cerrarse cuanto antes promoviendo una nueva clave (§5).

### §4.3 Revocación del custodio

Según D-B6-1:

- **(a) Hardware token:** físicamente desactivado o devuelto al inventario sellado por T1. Si la sospecha es extravío, el token se considera comprometido y nunca se reactiva.
- **(b) OS Keychain:** `security delete-keychain` (macOS) o `secret-tool clear` (Linux libsecret). El usuario humano custodio rota su passphrase del OS.
- **(c) HSM remoto:** API de revocación del proveedor (Vault `transit/keys/dory_cure_kill_switch/config -data disable=true`, AWS KMS `ScheduleKeyDeletion --pending-window-in-days 7` con override T1, GCP KMS `cryptoKeyVersions destroy`).

### §4.4 Análisis forense

Antes de generar la nueva clave:

1. Snapshot del audit log del custodio comprometido.
2. Captura de logs de VERIFICADOR-001 desde T-24h hasta T+1h.
3. Inventario de kill_files firmados con la clave comprometida en las últimas 90 días (`bridge/control_tower/evidence/B1/`).
4. Identificación de acciones magnas autorizadas con esa clave en los últimos 90 días (cruce con `audit_log_immutable` de Supabase).

El informe forense queda en `bridge/control_tower/evidence/B6/forensics/<incident_id>.md` y debe ser auditado por el Sabio externo D-B6-3 antes de promover la nueva clave.

---

## §5 Promoción de la nueva clave

Una vez completado §4:

1. Ejecutar `DORY_CURE_KEY_ROTATION_PROCEDURE.md` §5.1 (generación) en un custodio **distinto** del comprometido (o el mismo restablecido, si el análisis forense lo certifica).
2. Saltarse la ventana dual-key §5.2 (no aplica: la clave anterior está revocada).
3. Commit T1-firmado de la nueva `.pub` directamente como `.monstruo/keys/dory_cure_kill_switch.pub`.
4. Actualizar `CURRENT_KEY_HASH` con el hash de la nueva clave.
5. VERIFICADOR-001 sale del modo `KEY_REVOKED` y entra en estado normal.
6. T1 firma cierre de incidente en bridge con `incident_id` cerrado.

---

## §6 Audit log post-revocación

Entrada obligatoria en `bridge/control_tower/evidence/B6/B6_E4_rotation_audit.jsonl` (mismo schema que rotación programada) con:

- `trigger = "incident_<tipo>"`
- `incident_id` referenciado.
- `forensics_path` apuntando al informe §4.4.
- `t1_signature` sobre el commit de revocación **y** sobre el commit de promoción de nueva clave.
- `sabio_auditor_id` que validó el forensics.

---

## §7 Comunicación pública (post-cierre)

Dentro de 7 días naturales después del cierre del incidente, T1 publica un resumen sanitizado en el bridge público `bridge/incidents/<incident_id>.md` con:

- Trigger y momento de detección.
- Tiempo total de la ventana `DORY_CURE_HALTED`.
- Acciones magnas afectadas (anonimizadas si aplica).
- Lecciones aprendidas y cambios al spec B6 si aplica (amendment via B8-E4 si la causa raíz expone gaps).

---

## §8 No-go

- No se revoca sin firma T1 explícita en el `incident_id` (excepción: si T1 está incomunicado >30 min, el segundo canal humano de respaldo puede firmar).
- No se promueve nueva clave sin auditoría forense firmada por Sabio externo.
- No se reutiliza un custodio comprometido sin certificación forense.
- No se omite la entrada en audit log ni la publicación post-cierre.
- No se usa `age` o cualquier tooling no firmado en D-B6-5 para la nueva clave.
- No se intenta "recuperar" una clave comprometida; siempre se rota a una nueva.

---

**Firma magna pendiente.** Este procedimiento entra en operación cuando T1 firme D-B6-1..D-B6-5.
