# Checklist de integración Manus-Oauth — 10 puntos

> Verificar punto por punto antes de declarar el sprint cerrado.
> Si algún punto falla, NO se firma el sprint. Es ley.

---

## Pre-integración

- [ ] **1.** Existe DSC-X-003 (o DSC-GLOBAL-003) firmado en `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/`. Si el proyecto justifica usar OTRO provider en lugar de Manus-Oauth, hay un DSC nuevo firmado que lo justifica.

- [ ] **2.** Variables de entorno copiadas desde `templates/env-vars-template.txt` a `.env.local`. Las `MANUS_OAUTH_CLIENT_*` provienen de Manus al registrar el proyecto. `MONSTRUO_SESSION_SECRET` y `MONSTRUO_TOKEN_ENCRYPTION_KEY` generados con `openssl rand -hex 32`.

- [ ] **3.** El `client_secret` NO aparece en ningún archivo committeado. Verificado con `git grep MANUS_OAUTH_CLIENT_SECRET` — solo debe aparecer en docs/templates con valor vacío.

## Schema de DB

- [ ] **4.** Tabla `users` aplicada con schema canónico de `templates/user-table-migration.sql`. Verificado con `DESCRIBE users` — debe tener todas las columnas: `id`, `email`, `email_verified`, `name`, `avatar_url`, `manus_token_encrypted`, `manus_token_expires_at`, `manus_refresh_token_encrypted`, `created_at`, `updated_at`, `last_login_at`, `last_login_ip`, `last_login_user_agent`, `status`, `suspended_reason`, `suspended_at`, `metadata_json`.

- [ ] **5.** Tabla `user_sessions` aplicada. Foreign key a `users(id)` con `ON DELETE CASCADE` confirmado.

## Endpoints canónicos

- [ ] **6.** Existe `POST /api/v1/auth/callback` (NUNCA `/api/auth/callback` genérico). Implementado siguiendo `templates/auth-callback-handler.ts`.

- [ ] **7.** Existe `POST /api/v1/auth/logout` que borra cookie + opcional revoke en Manus. NO falla el logout si el revoke falla — se loggea como warning `auth_logout_revoke_failed` y sigue.

- [ ] **8.** Existe `GET /api/v1/auth/me` que retorna el user actual basado en cookie. 401 si no hay cookie válida.

## UI compliance

- [ ] **9.** Botón canónico `<SignInWithManusButton />` desde `templates/sign-in-with-manus-button.tsx`. Texto exacto: `Sign in with Manus`. Paleta forja desde `@monstruo/design-tokens`. NO usa `primary`/`secondary` ni colores genéricos.

## Tests

- [ ] **10.** Mínimo 3 tests pasan verde:
  - **10a.** Happy path: login → callback con code válido → cookie seteada → GET /me retorna user
  - **10b.** Token expirado: middleware detecta, dispara refresh background, request actual sigue
  - **10c.** Sesión inválida: cookie tampered → 401 con error code `auth_session_invalid` (no genérico)

---

## Verificación final con bash

```bash
# Endpoints existen y responden
curl -i https://tu-app.com/api/v1/auth/me        # esperado: 401 sin cookie
curl -i https://tu-app.com/api/v1/auth/logout    # esperado: 200 + Set-Cookie clear

# Naming canónico (no aparece /api/auth/ genérico en código)
grep -r "/api/auth/" src/ && echo "FAIL: naming genérico" || echo "OK: naming canónico"

# Secret no committeado
git grep "MANUS_OAUTH_CLIENT_SECRET=" -- ':!*.template' ':!*.env.example' && echo "FAIL: secret en repo" || echo "OK: secret protegido"
```

---

## Cierre del sprint

Cuando los 10 puntos verde + verificación bash verde:

```
🔒 MANUS-OAUTH INTEGRADO — VERIFICADO

| # | Check | Estado |
|---|---|---|
| 1 | DSC-X-003 | ✅ |
| 2 | Env vars | ✅ |
| 3 | Secret no committeado | ✅ |
| 4 | Tabla users | ✅ |
| 5 | Tabla user_sessions | ✅ |
| 6 | POST callback | ✅ |
| 7 | POST logout | ✅ |
| 8 | GET me | ✅ |
| 9 | Botón canónico | ✅ |
| 10 | 3 tests verde | ✅ |
```

— Hilo Catastro, Sprint Catastro-B 2026-05-06
