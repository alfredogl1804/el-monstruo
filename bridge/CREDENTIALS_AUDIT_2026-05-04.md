# Credentials Audit & Rotation — 4 mayo 2026

> **Status:** ✅ COMPLETADA  
> **Ejecutor:** Hilo B (Manus desktop) bajo dirección de Alfredo  
> **Duración:** ~2h (incluye Bitwarden setup + auditoría + ola 1)

## Resumen ejecutivo

Se rotaron los **17 Personal Access Tokens (Classic)** de GitHub asociados al usuario `alfredogl1804`. Reemplazados por **2 PATs canónicos con scopes mínimos y expiración de 90 días**, almacenados en Bitwarden (cuenta AG) y propagados a los únicos 2 sistemas que los usaban activamente: el **Mac local** y el **kernel en Railway**.

## Tokens nuevos (canónicos) — Ola 1

| Nombre | Token (primeros 12) | Scopes | Expira | Almacenado en | Consumidor |
|---|---|---|---|---|---|
| `el-monstruo-mac-2026-05` | `ghp_8AJw3rnrm…` | `repo, read:org` | Aug 2, 2026 | Bitwarden item `609e5e38-b6ad-48b1-9184-b44000605c05` | Mac local (Keychain via `gh auth login`) |
| `el-monstruo-kernel-2026-05` | `ghp_J2ThVxfiB…` | `repo, workflow` | Aug 2, 2026 | Bitwarden item `d95a233b-f15c-43c2-bd30-b440006062b6` | Railway service `el-monstruo-kernel` (vars `GITHUB_TOKEN` + `GITHUB_PERSONAL_ACCESS_TOKEN`) |

## Tokens fine-grained — Ola 2 (pendiente)

Quedan vivos intencionalmente:

| Nombre | Tipo | Razón para mantener vivo |
|---|---|---|
| `ticketlike-deploy` | fine-grained | Proyecto independiente (ticketlike.mx) vendiendo a diario al público. Scope acotado, expira 22 may 2026 (rotación natural). |
| `el-monstruo-mcp` | fine-grained | Sin expiración. Lo usa el MCP Server de Manus para hablar con GitHub. Rotarlo requiere acceso a la UI de Manus. **Programado para Ola 2**. |

## 17 PATs Classic revocados

### NUCLEAR (sin expiración + scopes admin completos)

| Token | ID GitHub | Notas |
|---|---|---|
| `Manus monstruo 2` | 4314142460 | 22 scopes incluyendo admin:enterprise, admin:org, admin:gpg_key. Riesgo crítico. |
| `Token Manus Kukulkan` | 4034866017 | Idéntico a Manus monstruo 2. |
| `Servidor MCP oficial de GitHub` | 3429222683 | Nombre largo de descripción inserto en lugar del nombre real. Sin expiración. |

### Alto riesgo

| Token | ID GitHub | Notas |
|---|---|---|
| `Mounstro v2` | 3671387210 | 17 scopes admin. Last used hace 2 meses. |
| `El Monstruo` | 3416227136 | Expiraba feb 2027. Scopes amplios. |

### Operativos rotativos (12)

| Token | ID GitHub |
|---|---|
| `el-monstruo-ci-fix-2` | 4314011713 |
| `manus-sprint35` | 4284122165 |
| `Manus-Sandbox-v3` | 4283780130 |
| `manus-ops` | 4283023242 |
| `manus-temp-push` | 4279054767 |
| `manus-sandbox` | 4144708825 |
| `el-monstruo-ci-fix` | 4131749556 |
| `manus-sprint14` | 4128348710 |
| `manus-command-center` | 4123832472 |
| `observatorio-merida-2027` | 4106137475 |
| `manus-sandbox-apr2026` | 4105295993 |
| `manus-agent-push` | 4103280659 |

## Cambios sistémicos asociados

### Mac (`alfredogongora`)

1. `gh auth login` reauth con token nuevo, scopes `repo, read:org`.
2. `gh auth setup-git` confirmado como credential helper.
3. `~/.git-credentials` viejo (con 2 tokens embebidos, 1 corrupto) → **borrado**, backup en `~/.git-credentials.backup-2026-05-04`.
4. Keychain `internet-password github.com/alfredogl1804` → **eliminado** (`security delete-internet-password`).
5. Validado: `git fetch`, `git push` (commit dummy + cleanup), `gh api user/repos` — todo OK.

### Railway (`el-monstruo-kernel`, project `celebrated-achievement`)

| Variable | Valor anterior | Valor nuevo |
|---|---|---|
| `GITHUB_TOKEN` | `ghp_AGjyZF…` (Classic viejo) | `ghp_J2ThVxfi…` (Classic nuevo) |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | `github_pat_11B5…` (fine-grained, distinto a `el-monstruo-mcp`) | `ghp_J2ThVxfi…` (Classic nuevo, mismo que `GITHUB_TOKEN`) |

Redeploy automático tras cambio. Validado en logs: `tool=github` ejecutándose sin errores 401/403/bad-credentials. Embriones siguen activos (7/7), brand audit 19/19 passed, version 0.84.7-sprint84.7.

### Bitwarden (cuenta AG `alfredogl1.gongora@gmail.com`)

- Vault inicialmente vacío (cuenta nueva creada esta sesión).
- 2 items creados como `Login` con campos `username = github-pat`, `password = <token>`, notes con scopes y fecha de expiración.

## Decisiones arquitectónicas tomadas

1. **No esperar ventana de monitoreo de 2-4h antes de revocar.** Justificación: el sistema no está aún en producción con tráfico de usuarios externos; el único consumidor crítico es el kernel Railway, y se validó en logs que ya está usando el token nuevo sin errores.
2. **Mantener 2 vars distintas en Railway** (`GITHUB_TOKEN` + `GITHUB_PERSONAL_ACCESS_TOKEN`) con el mismo valor, en vez de consolidar a 1 var. Justificación: refactor del código (`tools/github.py` usa la primera, `kernel/mcp_client.py` la segunda) implica ~5 archivos de cambio y rebuild; consolidación se difiere a un sprint dedicado.
3. **`read:org` agregado al token Mac post-creación.** Justificación: `gh auth login` lo exige; sin él el CLI rechaza el token aunque git directo funcione. Decisión: scope mínimo aceptable para tener gh CLI funcional en Mac.

## Secrets en código del repo

`bridge/manus_to_cowork.md` y `bridge/cowork_to_manus.md` contienen referencias históricas a tokens viejos en bloques de log y discusión. **No se sanitizaron porque ya están revocados** y no representan riesgo. Para futuras rotaciones, considerar sanitización antes de commit.

## Próximas acciones

| ID | Acción | Owner | Prioridad |
|---|---|---|---|
| R1 | Rotar `el-monstruo-mcp` fine-grained (Ola 2) cuando UI de Manus esté abierta | Hilo B | Media |
| R2 | Calendario: Aug 1, 2026 — rotar ambos PATs antes del 2 de Aug | Hilo B | Alta (90 días) |
| R3 | Auditar OAuth Apps "Never used" en GitHub para revocar las nucleares (audit anterior detectó 3) | Hilo B | Media |
| R4 | Considerar consolidación `GITHUB_TOKEN` única en código kernel (sprint dedicado) | Hilo A | Baja |

## Anexos

- `~/el-monstruo/.git-credentials.backup-2026-05-04` — backup local del archivo limpiado.
- Bitwarden vault — fuente única de verdad de tokens activos.

---

> **Hilo B firma:** Rotación ejecutada con consentimiento explícito de Alfredo en cada paso crítico (creación de tokens, propagación, salto de monitoreo, revocación masiva). Cero pérdida de servicio. Cero downtime del kernel. Estado de seguridad de cuenta `alfredogl1804` significativamente mejorado: de 19 PATs → 2 (más 2 fine-grained intocados con propósito conocido).
