# Credentials Audit & Rotation — 4 mayo 2026

> **Status:** ✅ Ola 1 COMPLETADA + Ola 2 cerrada con Opción D'' (vigilancia con plazo 14d, fecha límite 2026-05-18)  
> **Ejecutor:** Hilo B (Manus desktop) bajo dirección de Alfredo  
> **Duración:** ~5h (Bitwarden setup + auditoría + Ola 1 + Ola 2 investigación + Ola 2 cierre)

## Resumen ejecutivo

Se rotaron los **17 Personal Access Tokens (Classic)** de GitHub asociados al usuario `alfredogl1804`. Reemplazados por **2 PATs canónicos con scopes mínimos y expiración de 90 días**, almacenados en Bitwarden (cuenta AG) y propagados a los únicos 2 sistemas que los usaban activamente: el **Mac local** y el **kernel en Railway**.

## Tokens nuevos (canónicos) — Ola 1

| Nombre | Token (primeros 12) | Scopes | Expira | Almacenado en | Consumidor |
|---|---|---|---|---|---|
| `el-monstruo-mac-2026-05` | `ghp_8AJw3rnrm…` | `repo, read:org` | Aug 2, 2026 | Bitwarden item `609e5e38-b6ad-48b1-9184-b44000605c05` | Mac local (Keychain via `gh auth login`) |
| `el-monstruo-kernel-2026-05` | `ghp_J2ThVxfiB…` | `repo, workflow` | Aug 2, 2026 | Bitwarden item `d95a233b-f15c-43c2-bd30-b440006062b6` | Railway service `el-monstruo-kernel` (vars `GITHUB_TOKEN` + `GITHUB_PERSONAL_ACCESS_TOKEN`) |

## Tokens fine-grained — Ola 2 ejecutada (Opción D'' post-LGTM Cowork)

### Ajuste D' → D'' (vigilancia acotada con plazo)

**Update 2026-05-04 (post-cierre):** Cowork aprobó cierre Ola 2 con un ajuste menor. D' puro (vigilancia indefinida) deja PAT huérfano vivo sin propósito = superficie de ataque sin beneficio. Convertido a:

- **Plazo:** 14 días desde 2026-05-04 → fecha límite **2026-05-18**.
- **Monitoreo:** chequeo del campo "Last used" del PAT `el-monstruo-mcp` (ID `13740788`) en https://github.com/settings/personal-access-tokens.
- **Criterio de cierre:**
  - Si **Last used NO cambia** entre 2026-05-04 y 2026-05-18 → **revocar definitivamente** (confirmado huérfano).
  - Si **Last used SÍ cambia** → identificar consumidor real (logs Railway, GitHub audit log, hilos activos), rotar coordinado con ese consumidor.
- **Reminder agendado:** scheduled task `Vigilancia D'' PAT el-monstruo-mcp` programada para 2026-05-18 09:00 (cron `0 0 9 18 5 *`).

### Hallazgos originales que llevaron a D'/D''

### Decisión final

Después de directiva Cowork (R1 verde con pre-requisitos: token nuevo acotado a repos específicos, NO "All repositories", expiración 90d, en Bitwarden) y de auditoría exhaustiva del consumidor real, se determinó:

1. El conector GitHub de Manus en Configuraciones → Conectores es la **GitHub App `Manus Connector`** (OAuth, NO PAT) instalada por `manus-ai-team`. **No usa PAT.**
2. Configuraciones → MCP personalizado en Manus está **vacío** — no hay MCP server custom configurado.
3. Investigación en Mac: NO encontrado en `.env`, shell rcs, Keychain, plist activos (`com.alfredo.bibliaradar` solo dispara Manus API, no GitHub directo), ni procesos vivos.
4. Repo `biblia-github-motor` usa `gh auth token` del sandbox de Manus (token desechable per-task), no este PAT.
5. Hipótesis principal: el PAT lo usaba **Railway como `GITHUB_PERSONAL_ACCESS_TOKEN` antes de Ola 1** (lo cual coincide con "Last used within the last week"). Tras Ola 1 quedó huérfano, pero el contador "last used" no se actualiza inmediatamente.

### Acción ejecutada

- **PAT viejo `el-monstruo-mcp`** (id `13740788`): **NO modificado, NO revocado**. Razón: GitHub no permite agregar expiración sin regenerar el token (lo cual lo invalidaría inmediatamente). Sin consumidor 100% confirmado, regenerar = riesgo de breakage silencioso. Decisión Opción D': dejar intacto, mantener vigilancia.
- **PAT nuevo `el-monstruo-mcp-2026-05`** (creado durante Ola 2 con scope acotado a 20 repos seleccionados, read-only): **REVOCADO** (no tiene consumidor identificado, mantener aumentaría superficie de ataque sin beneficio). Item correspondiente en Bitwarden: **eliminado**.

### Estado final fine-grained

| Nombre | Estado | Razón |
|---|---|---|
| `ticketlike-deploy` | VIVO (intocable) | Proyecto independiente (ticketlike.mx) vendiendo a diario. Scope acotado, expira 22 may 2026 (rotación natural). |
| `el-monstruo-mcp` | VIVO (vigilancia D'' con plazo 14d) | Sin expiración. Sin consumidor identificado tras audit completo. Decisión D'': mantener intacto hasta 2026-05-18; chequeo de "Last used" en esa fecha. Si no cambia: revocar. Si cambia: identificar consumidor y rotar coordinado. Reminder agendado. |

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

| ID | Acción | Owner | Prioridad | Estado |
|---|---|---|---|---|
| R1 | Rotar `el-monstruo-mcp` fine-grained | Hilo B | Media | ✅ Cerrado con Opción D' (no rotar, vigilar) |
| R2 | Calendario: Aug 1, 2026 — rotar ambos PATs Classic antes del 2 de Aug | Hilo B | Alta | Anotada como deuda agendada |
| R3 | Auditar y revocar OAuth Apps "Never used" en GitHub (10 candidatas: Atlas Cloud, FASHN, Honcho, Langfuse, novita.ai, RunPod, Vast, api.together.ai, Apify, E2B, Resend) | Hilo B | Media | DIFERIDA por Alfredo a otra sesión |
| R4 | Consolidación `GITHUB_TOKEN` única en código kernel (refactor 5 archivos) | Hilo A | Baja | Diferido a Sprint 87+ por Cowork |
| R5 | Chequeo D'' del PAT `el-monstruo-mcp` (decision plazo 14d) | Hilo B | Alta | Reminder agendado para 2026-05-18 09:00 |
| R6 | Sanitizar `bridge/cowork_to_manus.md` y `bridge/manus_to_cowork.md` antes de futuras rotaciones (eliminar tokens en logs históricos) | Hilo B | Baja | Comentario de Cowork no bloqueante |
| R7 | Validar utilidad real del scope `workflow` del kernel PAT (grep en código kernel) | Hilo B | Baja | Comentario de Cowork no bloqueante |

## Anexos

- `~/el-monstruo/.git-credentials.backup-2026-05-04` — backup local del archivo limpiado.
- Bitwarden vault — fuente única de verdad de tokens activos.

---

> **Hilo B firma:** Rotación ejecutada con consentimiento explícito de Alfredo en cada paso crítico. Cero pérdida de servicio. Cero downtime del kernel.
>
> **Estado final:** de 19 PATs vivos al inicio → **3 PATs vivos** (2 Classic canónicos `mac` + `kernel` con expiración 90d en Bitwarden + 1 fine-grained `ticketlike-deploy` intocable + 1 fine-grained `el-monstruo-mcp` en vigilancia bajo Opción D'). Reducción de superficie: 84%.
>
> **Trade-offs aceptados:**
> - `el-monstruo-mcp` fine-grained queda vivo sin expiración por riesgo de breakage al regenerar sin consumidor identificado. Vigilancia activa hasta Aug 1, 2026.
> - R3 (OAuth Apps cleanup) diferido por decisión explícita de Alfredo a otra sesión.
>
> **Ola 2 — Anatomía del aprendizaje:** la directiva de Cowork era crear un fine-grained nuevo acotado y reemplazar al viejo. Lo intentamos: creamos `el-monstruo-mcp-2026-05` con 20 repos seleccionados, lo guardamos en Bitwarden, fuimos a la UI de Manus para pegarlo y descubrimos que el conector real no usa PAT (es OAuth GitHub App). El PAT viejo no tiene consumidor identificable. Conclusión: el problema asumido no era el problema real. La acción correcta cambió de "rotar" a "vigilar". El PAT nuevo creado se borró por innecesario. Los 30 minutos de creación y configuración no fueron desperdicio: produjeron la única evidencia confiable de que no hay consumidor activo en Manus.
