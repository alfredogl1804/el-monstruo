# DORY_CURE Key Rotation Procedure (B6-E4)

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Gate:** B6 — Key Custody ed25519
**Fuente normativa:** closure pack v0.2 §2.2 (B6.4)
**Aplica a:** clave ed25519 que firma `.monstruo/kill_switches/DORY_CURE_DISABLED.sig`

> Este procedimiento NO se ejecuta hasta que T1 firme decisiones D-B6-1..D-B6-5. No implementa runtime.

---

## §1 Alcance

Define el ciclo de vida de rotación de la clave ed25519 que sella el kill switch local-first del gate B1. Cubre **rotación programada** (periódica) y **rotación post-incidente** (reactiva). La revocación de emergencia se trata por separado en `DORY_CURE_KEY_REVOCATION_PROCEDURE.md` (B6-E5).

---

## §2 Frecuencia mínima (propuesta T1-pending)

- **Programada:** cada 90 días naturales contados desde la fecha de generación del par actual.
- **Post-incidente:** dentro de las 24 horas siguientes a la detección de cualquiera de los eventos en §4.
- **No-go:** rotaciones a discreción de un solo agente sin orden T1 explícita y sin registro en el audit log público.

T1 puede establecer una frecuencia distinta firmando D-B6-2 (propuesta de este pack: 90 días).

---

## §3 Pre-condiciones

Antes de iniciar la rotación, el operador debe verificar:

1. Custodio activo (D-B6-1 firmado por T1) es operable: hardware token disponible, keychain accesible, o HSM remoto online.
2. La clave pública actual `.monstruo/keys/dory_cure_kill_switch.pub` está versionada en el repo y su commit está firmado por T1.
3. No hay rotación en curso (no existe `.pub.next` en el repo).
4. Herramienta de firma D-B6-5 instalada y verificada (`signify -V`, `minisign -v`, o `ssh-keygen -V`).
5. Backup vigente bajo política D-B6-4 (propuesta: shamir 3-of-5).

Si cualquier pre-condición falla, abortar y reportar a T1.

---

## §4 Triggers de rotación post-incidente

La rotación reactiva es obligatoria cuando ocurra cualquiera de los siguientes:

| Trigger | Detector | Severidad |
|---------|----------|-----------|
| Custodio físico perdido o robado | Reporte humano a T1 | crítico |
| Sospecha de compromiso del HSM/Keychain | Audit log con accesos anómalos | crítico |
| `gitleaks-staged` detecta la clave privada en working tree | CI hook | crítico |
| Falsificación detectada (kill_file con firma válida no autorizado por T1) | VERIFICADOR-001 + audit log | crítico |
| Vulnerabilidad pública conocida en `signify` / `minisign` / `ssh-keygen -Y sign` | CVE feed monitoreado | alto |
| Cambio de tooling D-B6-5 (T1 firma migración) | Decisión T1 | medio |

---

## §5 Pasos exactos de la rotación

### §5.1 Generación del nuevo par

Operador autorizado (Cowork T2-A o T1 personalmente, según D-B6-1):

1. Generar el par en el custodio elegido (D-B6-1):
   - **(a) Hardware token:** seguir manual del fabricante (YubiKey / OnlyKey) para ed25519 derivation.
   - **(b) OS Keychain:** `ssh-keygen -t ed25519 -f ~/.ssh/dory_cure_next -C "dory_cure_kill_switch <fecha>"` + `ssh-add ~/.ssh/dory_cure_next` con ACL solo-T1.
   - **(c) HSM remoto:** Vault `transit/keys/dory_cure_kill_switch/rotate`, AWS KMS `CreateKey --key-spec ECC_NIST_P256` (NB: ed25519 directo si soportado), o GCP KMS equivalente con audit log activado.
2. La clave privada nunca toca filesystem plano. Si el flujo lo requiere temporalmente, debe estar cifrada con `age` (cifrado, no firma) bajo passphrase humana antes de existir en disco, y eliminada con `shred -u` tras la operación.
3. Producir la clave pública: `signify -G -p dory_cure_next.pub -s dory_cure_next.sec` (o equivalente `minisign -G` / `ssh-keygen -y`).

### §5.2 Ventana de superposición (dual-key window)

1. Commit la nueva pública como `.monstruo/keys/dory_cure_kill_switch.pub.next` con commit firmado por T1.
2. Durante 72 horas (3 días naturales) el agente acepta firmas válidas producidas por **cualquiera de las dos claves** (`.pub` actual o `.pub.next`).
3. Operadores y CI workflows deben actualizar su firma de kill_files a usar la nueva clave dentro de esa ventana.
4. Si algún componente downstream falla la migración, abortar la rotación y dejar la nueva clave como reserva sin promover.

### §5.3 Promoción

Después de 72 horas, T1 ejecuta:

```bash
git mv .monstruo/keys/dory_cure_kill_switch.pub .monstruo/keys/archive/dory_cure_kill_switch.<fecha>.pub
git mv .monstruo/keys/dory_cure_kill_switch.pub.next .monstruo/keys/dory_cure_kill_switch.pub
git commit -S -m "B6 rotate dory_cure_kill_switch <fecha>"
```

El agente y VERIFICADOR-001 dejan de aceptar firmas de la clave archivada inmediatamente tras el commit (la verificación se hace por hash anchor de la `.pub` viva, no por historia).

### §5.4 Comunicación a operadores

Notificación obligatoria a:

- T1 (Alfredo Góngora) — firma magna del commit de rotación.
- Cowork T2-A — observador, no firmante.
- Sabio externo auditor designado (D-B6-3, propuesta: Opus 4.7) — recibe hash de la nueva `.pub` y diff del commit por canal sanitizado.
- Operadores humanos del Monstruo (canal interno del bridge).

Plazo: dentro de la ventana de 72 horas, idealmente al iniciar §5.2.

---

## §6 Audit log

Cada rotación produce una entrada en `bridge/control_tower/evidence/B6/B6_E4_rotation_audit.jsonl` con los campos:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `rotation_id` | uuid | Identificador único de la rotación |
| `timestamp_iso` | string ISO 8601 | Fecha/hora de inicio |
| `trigger` | enum | `scheduled_90d`, `incident_<tipo>`, `tooling_migration` |
| `custodian_old_hash` | sha256 | Hash de la `.pub` archivada |
| `custodian_new_hash` | sha256 | Hash de la `.pub` promovida |
| `signing_tool` | enum | `signify`, `minisign`, `ssh-keygen-Y` |
| `operator_id` | string | Identidad firmada del operador (T1 o Cowork con firma SSH) |
| `t1_signature` | string | Firma magna T1 del commit de promoción |
| `sabio_auditor_id` | string | Identidad del Sabio auditor que recibió hash |
| `dual_window_start_iso` | string | Inicio de ventana §5.2 |
| `dual_window_end_iso` | string | Promoción §5.3 |
| `notes` | string | Observaciones |

Este audit log es input obligatorio de B6-E4 (canon B6-E4 cita este archivo).

---

## §7 Fallback si la rotación falla

Si en cualquier punto entre §5.1 y §5.3 ocurre un error que impide completar la rotación:

1. Mantener `.pub` actual operativa (no archivarla).
2. Eliminar `.pub.next` del repo (`git rm` + commit firmado por T1).
3. Reportar a T1 con dump completo del audit log parcial.
4. Si la causa raíz es compromiso de custodia, escalar a `DORY_CURE_KEY_REVOCATION_PROCEDURE.md` (B6-E5) inmediatamente.

---

## §8 No-go

- No se rota con tooling distinto al firmado en D-B6-5.
- No se rota sin la ventana de superposición §5.2 (excepto en revocación de emergencia, que es procedimiento aparte).
- No se rota sin commit T1-firmado del audit log.
- No se rota con `age` como firmador (cifrado ≠ firma).
- No se rota a discreción de Cowork sin firma T1.

---

**Firma magna pendiente.** Este procedimiento entra en operación cuando T1 firme D-B6-1..D-B6-5.
