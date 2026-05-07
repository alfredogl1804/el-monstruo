---
name: manus-oauth-pattern
description: Patrón canónico para integrar Manus-Oauth (Sign-in with Manus) en cualquier proyecto web-db-user del Monstruo. Provee templates, checklist de 10 pasos, ejemplos verificados (Bot Telegram, Command Center, Mundo Tata) y validación contra DSC-X-003. Usar cuando un proyecto nuevo necesite auth de usuario y deba decidir provider, o cuando se migre un proyecto existente a Manus-Oauth.
---

# manus-oauth-pattern — Patrón Canónico de Auth del Monstruo

> **DSC-X-003 (alias DSC-GLOBAL-003):** todo proyecto del Monstruo que necesite auth de usuario final usa **Manus-Oauth** como provider canónico. No SE inventa auth nueva. NO se usa Auth0/Clerk/Supabase Auth/etc. salvo justificación firmada.

---

## Cuándo usar este skill

**SÍ usar:**
- Proyecto web-db-user nuevo que necesita login (CIP frontend, Marketplace Interiorismo, Vivir Sano, futuras empresas-hijas)
- Bot Telegram con linking a cuenta Monstruo del usuario
- Cualquier app móvil/desktop que necesite identidad persistente
- Migración de proyecto existente a Manus-Oauth

**NO usar:**
- Auth de servicio internal del Monstruo (kernel ↔ kernel) — esos son JWT con keys del Vault, otro flow distinto
- Auth de admin con MFA dura (esos son aparte, ver DSC-G-pendiente sobre admin auth)
- Webhooks (firma HMAC, no auth de usuario)

---

## Protocolo de uso (10 pasos)

### Paso 1 — Verificar prerrequisito DSC-X-003

Lee `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-GLOBAL-003*.md` (o la versión renombrada `DSC-X-003*`). Si tu proyecto necesita auth de usuario y no tiene justificación firmada para usar otro provider, Manus-Oauth es la default.

### Paso 2 — Decisión de scaffold

| Stack del proyecto | Recomendación |
|---|---|
| Next.js 15+ App Router | scaffold web-db-user (Vite + React + Drizzle + MySQL/TiDB + Manus-Oauth) |
| Vite + React standalone | usar plantillas de `templates/` directamente |
| Flutter móvil | usar deep-link OAuth + storage seguro |
| Bot Telegram | usar pattern de "linking" (ver `references/ejemplo-bot-telegram.md`) |

### Paso 3 — Variables de entorno

Copiar `templates/env-vars-template.txt` a `.env.local` del proyecto y rellenar:

```
MANUS_OAUTH_CLIENT_ID=...        # provisto por Manus al registrar el proyecto
MANUS_OAUTH_CLIENT_SECRET=...    # NUNCA en frontend
MANUS_OAUTH_REDIRECT_URI=https://tu-app.com/auth/callback
MANUS_OAUTH_SCOPE=openid profile email
NEXT_PUBLIC_MANUS_OAUTH_LOGIN_URL=https://oauth.manus.im/authorize
```

Las variables `NEXT_PUBLIC_*` son públicas. El secret es server-side.

### Paso 4 — Migración SQL canónica de tabla `users`

Aplicar `templates/user-table-migration.sql` a la DB del proyecto (TiDB/MySQL/Postgres compatible). Esquema mínimo:

```sql
CREATE TABLE users (
  id              VARCHAR(64) PRIMARY KEY, -- Manus user_id
  email           VARCHAR(255) UNIQUE NOT NULL,
  name            VARCHAR(255),
  avatar_url      TEXT,
  manus_token     TEXT,                    -- ENCRYPTED at rest
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_login_at   TIMESTAMP NULL,
  metadata_json   JSON
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_last_login ON users(last_login_at);
```

### Paso 5 — Middleware de auth en server

Copiar `templates/auth-middleware-template.ts` y adaptarlo al stack del proyecto. El middleware:
1. Valida el cookie `monstruo_session` en cada request
2. Hace introspection del token contra Manus si está expirado
3. Hidrata `req.user` con el perfil
4. Redirige a login si no hay sesión válida (rutas protegidas)

### Paso 6 — Componente UI "Sign in with Manus"

Usar `templates/sign-in-with-manus-button.tsx`. **Inviolable per DSC-G-004:**
- Botón con paleta forja (no primary/secondary genéricos)
- Importa de `@monstruo/design-tokens`
- Texto exacto: `Sign in with Manus` (nunca `Login with Google` o `Continue with X`)

### Paso 7 — Callback handler

Endpoint canónico: `POST /api/v1/auth/callback`. Naming inviolable per DSC-G-004 — nunca `/api/auth/callback` genérico.

El handler:
1. Recibe `code` del query param de Manus
2. Hace POST a `https://oauth.manus.im/token` con `client_id`, `client_secret`, `code`, `redirect_uri`
3. Obtiene `access_token` + `id_token`
4. Hace GET a `https://oauth.manus.im/userinfo` con el access_token
5. Upsert al user en la tabla `users`
6. Setea cookie `monstruo_session` HTTP-only, SameSite=Lax, Secure
7. Redirige al destino original (`?return_to=`)

### Paso 8 — Logout endpoint

Endpoint canónico: `POST /api/v1/auth/logout`. Borra cookie + opcional revoke token contra Manus.

### Paso 9 — Test de integración

Mínimo 3 tests:
- Flujo happy path (login → callback → cookie → /me)
- Token expirado → introspection
- Sesión inválida → 401 con error code on-brand (`auth_session_invalid`, no `internal server error`)

### Paso 10 — Validación final con checklist

Correr `references/checklist-integracion.md` punto por punto antes de declarar el sprint cerrado.

---

## Anti-patrones

### NUNCA hacer

❌ **Hardcodear el client_secret en frontend** — siempre server-side  
❌ **Guardar el token de Manus en localStorage** — usar cookie HTTP-only  
❌ **Usar naming genérico** — `/api/auth/login` está prohibido. Es `/api/v1/auth/...`  
❌ **Inventar tu propio OAuth flow** — DSC-X-003 lo prohíbe  
❌ **Mezclar Manus-Oauth con otros providers** sin DSC firmado de "auth multi-provider"  
❌ **Botón sin identidad de marca** — siempre paleta forja desde `@monstruo/design-tokens`  
❌ **Error messages genéricos** — `auth_callback_invalid_state`, no `something went wrong`  

### SIEMPRE hacer

✅ **Cookie HTTP-only + Secure + SameSite=Lax**  
✅ **Encrypted at rest** para `manus_token` en DB  
✅ **Naming endpoints `/api/v1/auth/*`**  
✅ **Botón canónico desde `templates/sign-in-with-manus-button.tsx`**  
✅ **Tests para los 3 flows mínimos**  
✅ **Logging on-brand** — `auth_login_success`, `auth_callback_token_exchange_failed`, etc.  

---

## Reglas de credenciales OAuth (DSCs anidados)

Esta sección se añade en respuesta a la P0 del 2026-05-06 (credenciales en repo público) y al post-P0 SECURITY-002 (rotación de keys Supabase). Toda integración OAuth dentro del Monstruo debe respetar estas reglas, no solo Manus-Oauth.

### DSC-S-001 — Política de credenciales (anidado)

> **Las credenciales OAuth (`MANUS_OAUTH_CLIENT_SECRET`, equivalents Google/GitHub/etc.) son secrets de tipo "server-only" y NUNCA pueden:**
> - aparecer en código plaintext (incluso en repos privados),
> - aparecer en archivos `.env*` trackeados por git,
> - aparecer en transcripts de chat, comentarios, issues, ni capturas,
> - aparecer en `NEXT_PUBLIC_*`, `VITE_*`, ni en cualquier prefijo que el bundler exponga al cliente.

**Storage canonical:** Bitwarden (único password manager soportado por el usuario) + variables de entorno del runtime (Railway, Vercel, etc.).  
**Rotación:** 6 meses TTL, inmediata al detectar exposure.

Lee: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-001_politica_de_credenciales.md`.

### DSC-S-003 — Scripts y env vars sin defaults sensibles (anidado)

> **Scripts de migración, callbacks, middleware o cualquier código que consuma `MANUS_OAUTH_CLIENT_SECRET` (u otros secrets) NO puede tener default value con secret real.** El patrón correcto es fail-loud:

```typescript
// ❌ PROHIBIDO
const secret = process.env.MANUS_OAUTH_CLIENT_SECRET || "manus_secret_real_aqui";

// ✅ REQUERIDO (fail-loud)
const secret = process.env.MANUS_OAUTH_CLIENT_SECRET;
if (!secret) throw new Error("MANUS_OAUTH_CLIENT_SECRET env var required");

// ✅ ALTERNATIVA (helper centralizado, recomendado)
import { requireEnv } from "@monstruo/security/env-validator";
const secret = requireEnv("MANUS_OAUTH_CLIENT_SECRET");
```

Lee: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-003_scripts_env_vars_sin_defaults_sensibles.md`.

### DSC-S-004 — Antipatrón: default value con secret real (anidado)

> **El antipatrón más peligroso en OAuth integrations es:**
>
> ```typescript
> const secret = os.environ.get("MANUS_OAUTH_CLIENT_SECRET", "<valor real hardcoded>");
> ```
>
> Aunque parece "usar env var", el secret está en código. Esto fue exactamente lo que rompió BGM y crisol-8 en SECURITY-001. **Cualquier PR que introduzca este patrón debe ser rechazado en pre-commit (gitleaks + trufflehog) y en CI.**

Lee: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-004_antipatron_default_value_con_secret_real.md`.

### DSC-S-006 — Eval pipeline corrupto: criterio humano gobierna (anidado a OAuth)

Aplicado a OAuth: si el helper `requireEnv()` devuelve un valor pero el flow falla con "invalid_client", **no asumas que el secret está bien por solo existir**. Valida con un smoke real (token exchange contra `https://oauth.manus.im/token`) antes de declarar verde. El criterio humano (¿funciona end-to-end?) gobierna sobre el criterio del eval pipeline (¿la env var existe?).

Lee: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-006_eval_pipeline_corrupto_criterio_humano_gobierna.md`.

### Checklist específico de credenciales OAuth

Antes de declarar un sprint cerrado con integración OAuth:

- [ ] Ningún secret OAuth aparece en `git ls-files | xargs grep -lE "MANUS_OAUTH_CLIENT_SECRET="` (debe estar vacío o solo en `.env.example` con placeholder)
- [ ] Pre-commit (`gitleaks detect --staged`) verde
- [ ] CI (`secret-scan.yml`) pasó sin findings
- [ ] Secret está en Bitwarden con item nombrado según convención: `<proyecto>: MANUS_OAUTH_CLIENT_SECRET (rotación YYYY-MM-DD)`
- [ ] Secret está en runtime env vars (Railway/Vercel) y no en código
- [ ] Smoke E2E real ejecutado (login → callback → token exchange → user upsert) — no solo "la env var existe"
- [ ] Si se rota el secret, vieja key revocada en `https://oauth.manus.im/projects/<id>/credentials`

### Recovery si exposure detectada

1. **Inmediato (≤ 5 min):** revocar el client_secret en `https://oauth.manus.im/projects/<id>/credentials` → Generate New Secret
2. **Update env var:** Bitwarden + Railway/Vercel con la nueva
3. **Refactor del código si exposure venia de hardcode:** seguir patrón DSC-S-004 antes de pushear cualquier fix
4. **Postmortem:** archivar incidente en `discovery_forense/INCIDENTES/` siguiendo plantilla canon
5. **Audit transcripts pasados:** ejecutar `scripts/_check_no_tokens.sh` contra todos los chat logs (DSC-S-007 cuando exista)

---

## Cross-links

- **DSC-X-003** (alias DSC-GLOBAL-003) — restricción dura que firma este patrón
- **DSC-G-004** (Brand Engine) — naming + UI compliance
- **`@monstruo/design-tokens`** — paleta forja para botón canónico
- **`references/arquitectura.md`** — cómo funciona Manus-Oauth bajo el capó
- **`references/scaffold-web-db-user.md`** — estructura del scaffold canónico
- **`references/ejemplo-bot-telegram.md`** — pattern de linking para Bot
- **`references/ejemplo-command-center.md`** — uso en Command Center
- **`references/ejemplo-mundo-tata.md`** — uso en Mundo Tata
- **`references/checklist-integracion.md`** — 10 pasos a verificar antes de cerrar

---

## Versionado

`v0.2.0` — 2026-05-07: añadida sección "Reglas de credenciales OAuth" con DSCs S-001/S-003/S-004/S-006 anidados (post-P0 SECURITY-001/002).  
`v0.1.0` — 2026-05-06: Initial release. Skill Catastro-B.

Cualquier cambio breaking (nuevo scope, nuevo tipo de token, etc.) requiere:
1. Bump del skill (0.x.0)
2. DSC actualizado de DSC-X-003
3. Migration guide en `references/migration-from-vXY.md`

---

— Hilo Catastro, Sprint Catastro-B 2026-05-06
