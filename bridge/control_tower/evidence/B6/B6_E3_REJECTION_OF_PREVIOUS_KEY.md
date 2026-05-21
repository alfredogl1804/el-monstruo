# B6-E3 Rejection of Previous Key

## Veredicto

**REJECTED_DUE_TO_NO_PASSPHRASE**

## Key rechazada

| Campo | Valor |
|---|---|
| key_id | (v0.1 — quarantined) |
| generation_method | `minisign -G -W` (sin passphrase) |
| generation_date | 2026-05-20T22:26:00-06:00 |
| branch_published | control-tower/2026-05-20-b6-e3-public-key-real @ 6d1d615 |
| rejection_date | 2026-05-20T22:31:00-06:00 |
| rejected_by | Gemini audit + T1 confirmation |

## Motivo de rechazo

Gemini auditó B6-E3 y determinó que el flag `-W` genera una clave privada **sin cifrado at-rest**. Esto viola el requisito de custodia segura del kill-switch Anti-Dory:

> La clave privada debe estar cifrada con passphrase (KDF scrypt) para que incluso si el archivo `.key` es exfiltrado, no sea utilizable sin la passphrase.

## Acciones tomadas

1. Clave privada v0.1 movida a quarantine local: `~/.monstruo/keys/rejected_2026_05_20/dory_cure_kill_switch.key`
2. Clave pública v0.1 movida a quarantine local: `~/.monstruo/keys/rejected_2026_05_20/dory_cure_kill_switch.pub`
3. Carpeta quarantine NO subida al repo.
4. Branch `control-tower/2026-05-20-b6-e3-public-key-real` queda como evidencia histórica (no borrar).
5. Nueva clave v0.2 generada con passphrase interactiva (sin `-W`).

## Implicaciones

- La clave pública publicada en commit `6d1d615` es OBSOLETA.
- La nueva clave pública (v0.2) la reemplaza en esta rama (`control-tower/2026-05-20-b6-e3-public-key-real-v0-2`).
- Cualquier firma hecha con v0.1 es inválida.
- No se hicieron firmas con v0.1 (la clave nunca se usó en producción).
