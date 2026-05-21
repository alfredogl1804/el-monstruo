# B6-E3 Public Key Manifest — v0.2 (Passphrase-Protected)

## Key Identity

| Campo | Valor |
|---|---|
| tool | minisign |
| algorithm | ed25519 |
| key_id | F691851C93B1CA9D |
| generated_without_W | YES |
| passphrase_enabled | YES |
| private_key_encrypted_at_rest | YES |
| generation_date | 2026-05-20T22:35:00-06:00 |
| generated_by | T1 (Alfredo Góngora) interactively on local Mac |
| public_key_path_repo | .monstruo/keys/dory_cure_kill_switch.pub |
| private_key_path_local | ~/.monstruo/keys/dory_cure_kill_switch.key |
| public_key_sha256 | cbdc2cd7f687d27dc450762676f0cc0bf2629d76265daafcf47af941fcb406b3 |

## Status

| Campo | Valor |
|---|---|
| status | pending_backup |
| backup_shamir_physical | PENDING |
| usable_for_fase_1 | NO |
| usable_for_runtime_critical | NO |
| previous_key_status | REJECTED_DUE_TO_NO_PASSPHRASE |
| previous_key_location | ~/.monstruo/keys/rejected_2026_05_20/ (local quarantine, not in repo) |

## Verification Command

```bash
minisign -Vm <file> -P RWSdyrGTHIWR9o0MXjiVZ6zgeT0Y8YB/RFdkGEsPY+hYuqKmZNIT51Qe
```

## Security Assertions

- Private key is encrypted with passphrase (KDF: scrypt).
- Private key NEVER leaves T1's local machine.
- Private key is NOT in this repo.
- Passphrase is NOT stored anywhere digitally.
- Previous key (generated with `-W`, no passphrase) is quarantined locally and rejected.

## Audit Trail

| Evento | Fecha | Evidencia |
|---|---|---|
| v0.1 generated with -W | 2026-05-20T22:26 | REJECTED — no passphrase |
| v0.1 quarantined | 2026-05-20T22:31 | ~/.monstruo/keys/rejected_2026_05_20/ |
| v0.2 generated with passphrase | 2026-05-20T22:35 | This manifest |
| Gemini audit rejection of v0.1 | 2026-05-20 | B6-E3 audit by Gemini |
