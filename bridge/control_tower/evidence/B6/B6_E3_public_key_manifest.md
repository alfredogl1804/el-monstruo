# B6-E3 PUBLIC KEY MANIFEST

## Key Material

| Campo | Valor |
|---|---|
| tool | minisign 0.12 |
| algorithm | Ed25519 |
| public_key_path | `.monstruo/keys/dory_cure_kill_switch.pub` |
| public_key_sha256 | `5a45a48a6f4ab97f43a77e25e3b12a2b78683fd68f840261ad5a59abaace6a5d` |
| public_key_minisign_id | `RWRrHGh+f+qRhsNZzut4E8XbYXhXYHur2CpqaOUFh2oxLQtXxHvDUgQt` |
| private_key_location | `~/.monstruo/keys/dory_cure_kill_switch.key` (Mac local de T1) |
| private_key_in_repo | **NO** |
| private_key_seen_by_agent | **NO** |
| private_key_printed | **NO** |
| private_key_uploaded | **NO** |
| private_key_password | empty (flag `-W` used) |

## Status

| Campo | Valor |
|---|---|
| status | pending_backup |
| backup_shamir_physical | PENDING |
| usable_for_fase_1 | **NO** |
| usable_for_runtime_critical | **NO** |

## Verification Command

```bash
minisign -Vm <file> -P RWRrHGh+f+qRhsNZzut4E8XbYXhXYHur2CpqaOUFh2oxLQtXxHvDUgQt
```

## Generation Context

| Campo | Valor |
|---|---|
| generated_by | T1 (Alfredo Góngora) via Manus C executor |
| generated_on | Mac local de T1 |
| generated_at | 2026-05-20 22:26 CST |
| generation_method | `minisign -G -W` (no password) |
| permissions_key | `600` (owner read/write only) |
| permissions_pub | `644` (world readable) |

## Next Steps (Pending T1 Authorization)

1. Backup clave privada a USB físico.
2. Opcionalmente: Shamir split para segundo custodio.
3. Una vez backup confirmado: status → `ready_for_signing`.
4. Fase 1 activation requiere autorización separada.
