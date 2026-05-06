# Arquitectura: cómo funciona Manus-Oauth bajo el capó

> Referencia técnica del flow OAuth 2.0 + OIDC entre el Monstruo y Manus.

---

## Flow visual (sequence)

```
┌──────────┐         ┌──────────────┐         ┌────────────┐         ┌─────────────┐
│  Browser │         │ Tu app web   │         │  Manus     │         │  Tu DB      │
│  (user)  │         │ (Monstruo)   │         │  Oauth     │         │  (TiDB/MySQL)│
└────┬─────┘         └──────┬───────┘         └─────┬──────┘         └──────┬──────┘
     │                      │                       │                       │
     │ 1. click "Sign in"   │                       │                       │
     ├─────────────────────>│                       │                       │
     │                      │                       │                       │
     │ 2. redirect 302 a    │                       │                       │
     │    oauth.manus.im/   │                       │                       │
     │    authorize?...     │                       │                       │
     │<─────────────────────┤                       │                       │
     │                      │                       │                       │
     │ 3. user autentica con Manus (su contraseña/SSO/etc.)                 │
     ├──────────────────────────────────────────────>│                       │
     │                      │                       │                       │
     │ 4. redirect 302 con  │                       │                       │
     │    ?code=xxx         │                       │                       │
     │<──────────────────────────────────────────────┤                       │
     │                      │                       │                       │
     │ 5. GET /api/v1/auth/ │                       │                       │
     │    callback?code=xxx │                       │                       │
     ├─────────────────────>│                       │                       │
     │                      │                       │                       │
     │                      │ 6. POST /token        │                       │
     │                      │    {code, secret}     │                       │
     │                      ├──────────────────────>│                       │
     │                      │                       │                       │
     │                      │ 7. {access_token,     │                       │
     │                      │     id_token, ...}    │                       │
     │                      │<──────────────────────┤                       │
     │                      │                       │                       │
     │                      │ 8. GET /userinfo      │                       │
     │                      │    Bearer: token      │                       │
     │                      ├──────────────────────>│                       │
     │                      │                       │                       │
     │                      │ 9. {sub, email, ...}  │                       │
     │                      │<──────────────────────┤                       │
     │                      │                       │                       │
     │                      │ 10. encrypt + upsert  │                       │
     │                      ├───────────────────────────────────────────────>│
     │                      │                       │                       │
     │                      │ 11. crear session     │                       │
     │                      ├───────────────────────────────────────────────>│
     │                      │                       │                       │
     │ 12. Set-Cookie:      │                       │                       │
     │     monstruo_session │                       │                       │
     │     + redirect 302   │                       │                       │
     │<─────────────────────┤                       │                       │
     │                      │                       │                       │
     │ 13. requests con cookie auto                 │                       │
     │     a rutas protegidas                       │                       │
     ├─────────────────────>│                       │                       │
     │                      │                       │                       │
     │ 14. middleware valida cookie + carga user    │                       │
     │     de DB                                     │                       │
     │     (background: refresh manus_token si      │                       │
     │      cerca de expirar)                        │                       │
     │                      ├──────────────────────────────────────────────>│
     │                      │                       │                       │
```

---

## Componentes

### 1. Manus-Oauth Authorization Server

**Endpoints públicos:**
- `https://oauth.manus.im/authorize` — inicio del flow (redirect del browser)
- `https://oauth.manus.im/token` — intercambio code → token (server-side)
- `https://oauth.manus.im/userinfo` — perfil del user (server-side, Bearer)
- `https://oauth.manus.im/revoke` — revoke token (server-side)
- `https://oauth.manus.im/.well-known/openid-configuration` — discovery OIDC

**Tipo:** OAuth 2.0 Authorization Code Flow + OIDC.  
**Scopes estándar:** `openid`, `profile`, `email`.  
**Scopes extendidos del Monstruo (cuando aplique):** `monstruo:projects:read`, `monstruo:notifications:write`.

### 2. Frontend del proyecto (browser)

- Botón canónico `<SignInWithManusButton />`
- Click → `window.location.assign(authorize_url)`
- NO maneja tokens directamente
- Recibe cookie `monstruo_session` HTTP-only (no la lee desde JS)

### 3. Backend del proyecto (server)

**Endpoints canónicos:**
- `POST /api/v1/auth/callback` — handler del code
- `POST /api/v1/auth/logout` — revoca cookie + opcional revoke en Manus
- `GET /api/v1/auth/me` — devuelve user del request actual

**Middleware:** lee cookie en cada request, valida firma, hidrata `req.user`.

### 4. Base de datos del proyecto

**Tabla `users`:** schema canónico en `templates/user-table-migration.sql`.  
**Tabla `user_sessions`:** sesiones activas con expiración + revoke.  
**Encrypted at rest:** `manus_token_encrypted`, `manus_refresh_token_encrypted`.

---

## Decisiones de seguridad

### Por qué cookie HTTP-only y no localStorage
- localStorage es leíble por XSS, cookie HTTP-only no
- Cookie + SameSite=Lax bloquea CSRF en flows estándar
- Cookie + Secure obliga HTTPS en producción

### Por qué encrypt at rest del manus_token
- Si la DB se filtra, el token no es directamente usable
- Key de encryption en env vars / secrets manager (separado de la DB)
- Algoritmo recomendado: AES-256-GCM con IV random por token

### Por qué firmar el cookie con HMAC
- Detecta tampering del cookie sin necesidad de query a DB en cada request
- HMAC es rápido (microsegundos) — no impacta latencia
- SECRET en env vars (`MONSTRUO_SESSION_SECRET`)

### Por qué session_id separado del user_id
- Permite revocación selectiva (logout en un device sin afectar otros)
- Permite tracking de sesiones activas por user
- Permite invalidación masiva (rotar SECRET → invalida todas las sesiones)

---

## Refresh token flow

Cuando el `manus_token` está cerca de expirar (5 min antes), el middleware dispara un refresh en background:

```
1. Lee manus_refresh_token_encrypted de DB
2. Decrypt
3. POST /token con grant_type=refresh_token
4. Recibe nuevo access_token (y opcionalmente refresh_token)
5. Encrypt + update DB
6. Continúa request actual con el token viejo (todavía válido 5 min)
```

Esto evita que el usuario perciba latencia adicional. Si el refresh falla, el siguiente request fuerza re-login.

---

## Errores canónicos (formato `auth_{action}_{failure_type}`)

| Code | HTTP | Cuándo |
|---|---|---|
| `auth_session_missing` | 401 | No hay cookie |
| `auth_session_invalid` | 401 | Cookie malformado o firma inválida |
| `auth_session_expired` | 401 | Cookie expirado |
| `auth_introspection_failed` | 502 | Manus no responde al introspect |
| `auth_user_suspended` | 403 | User existe pero está suspendido |
| `auth_user_deleted` | 410 | User existe pero está marked as deleted |
| `auth_callback_token_exchange_failed` | 502 | POST /token de Manus falló |
| `auth_callback_userinfo_failed` | 502 | GET /userinfo de Manus falló |
| `auth_callback_state_mismatch` | 400 | CSRF check falló (state inválido) |
| `auth_login_button_misconfigured` | — | Frontend warning, no error HTTP |
| `auth_logout_revoke_failed` | 502 | Manus no respondió al revoke (no fatal, sigue logout) |

---

## Cross-links

- DSC-X-003 / DSC-GLOBAL-003 — restricción dura
- DSC-G-004 — Brand Engine (naming canónico)
- `templates/` — implementaciones reference
- `references/checklist-integracion.md` — qué validar antes de cerrar

— Hilo Catastro, Sprint Catastro-B 2026-05-06
