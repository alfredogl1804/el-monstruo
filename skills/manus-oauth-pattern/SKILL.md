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

`v0.1.0` — Initial release. Skill Catastro-B 2026-05-06.

Cualquier cambio breaking (nuevo scope, nuevo tipo de token, etc.) requiere:
1. Bump del skill (0.x.0)
2. DSC actualizado de DSC-X-003
3. Migration guide en `references/migration-from-vXY.md`

---

— Hilo Catastro, Sprint Catastro-B 2026-05-06
