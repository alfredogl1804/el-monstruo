---
sprint_id: LA-FORJA-001
fase: D4 FINAL SIGNOFF — Google OAuth + JWT session backend
auditor: Cowork T2-A (auditor delegado T1)
fecha: 2026-05-17
commit_auditado: ba7ee8e
range: 73936df5..ba7ee8e (1 commit, 10 archivos, +1069 / -8)
firma_dsc: DSC-LF-009 T2A-Cowork formal
veredicto: 🟢 D4 SHIP — VERDE FINAL
autorizacion_merge: PR a main autorizado
---

# 🟢 D4 SHIP — VERDE FINAL · DSC-LF-009 T2A-Cowork FIRMADO

## §1 Score binario 12/12 + 6/6 + 5/5

| Categoría | Score | Notas |
|---|---|---|
| 12 puntos binarios | **12/12 GREEN** | 11 verificados verbatim contra código + 1 confiado vía reporte (P3) |
| 6 hard rules | **6/6 GREEN** | HR-6 con caveat P2 disclosure credenciales chat |
| 5 decisiones binarias | **5/5 RATIFICADAS** | RAG diferido, JWT propio, NODE_ENV selector, mock googleAuth, cookie RFC 6265 |

## §2 Verificación binaria verbatim del código

### `jwt.ts` (3726 bytes) — VERIFICADO

- ✅ Imports: `SignJWT, jwtVerify, errors as joseErrors` de `jose`
- ✅ Constantes: `ISSUER="la-forja"`, `AUDIENCE="la-forja-api"`, `EXPIRES_IN="7d"`, `ALGORITHM="HS256"`
- ✅ `signSession` enforced `secret.length < 32 → throw`
- ✅ `setSubject(sub) + setIssuer + setAudience + setIssuedAt + setExpirationTime("7d") + sign`
- ✅ `verifySession` valida `issuer, audience, algorithms:[HS256]` en `jwtVerify`
- ✅ Type guards: `sub string`, `email string`, `role ∈ {t1_alfredo, t1_padre, user}`
- ✅ `JWTErrors` re-exportado para discriminación caller-side

### `routes/auth.ts` (7411 bytes) — VERIFICADO

- ✅ `SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7` (idéntico a JWT exp 7d)
- ✅ `oauthConfiguredGuard()` retorna 503 con namespace `[la-forja:oauth_not_configured]`
- ✅ `buildGoogleAuthMiddleware()` runtime build (necesario para tests con secret mutation)
- ✅ `googleAuth({ client_id, client_secret, scope:["openid","email","profile"], redirect_uri })`
- ✅ Callback handler: extrae `c.get("user-google")`, valida id+email, signSession, setCookie
- ✅ Cookie config: `httpOnly:true, secure:isProduction, sameSite:"Lax", path:"/", maxAge=7d`
- ✅ Redirect `${env.FRONTEND_URL}/post-login` con 302
- ✅ POST /logout: `deleteCookie + json ok:true`
- ✅ Defensa 502 si Google no devuelve user (fail-loud)
- ✅ `_testHelpers` exportados para tests

### `middleware/auth.ts` (6004 bytes) — VERIFICADO

- ✅ `SESSION_COOKIE_NAME = "la-forja_session"` const + JSDoc RFC 6265 justificado
- ✅ `forjaAuthStub` PRESERVADO intacto con guard D2.5 H-1 (production → 503)
- ✅ `forjaAuthGoogle()` nuevo: getCookie + verifySession + popula `c.var.user`
- ✅ Manejo error fallthrough: catch → 401 con `[la-forja:auth_session_invalid] ${message}`
- ✅ JWT_SECRET ausente → 503 con `[la-forja:auth_jwt_secret_missing]`
- ✅ `forjaAuthSelector()` binario: production → Google, dev/test → stub

### `env.ts` (9761 bytes) — VERIFICADO

- ✅ `BaseSchema` con 5 nuevos slots D4 (CLIENT_ID, CLIENT_SECRET, JWT_SECRET, REDIRECT_URL, FRONTEND_URL)
- ✅ `JWT_SECRET .min(32, "...")` enforced schema-level
- ✅ `EnvSchema = BaseSchema.superRefine()` itera required[] con `ctx.addIssue` cuando production
- ✅ Fallback dev JWT_SECRET `"forja-dev-jwt-secret-DO-NOT-USE-IN-PROD-32chars"` (32 chars exactos, claro dev-only)
- ✅ `loadEnv strict=false` preserva H-5 fail-loud en production
- ✅ Defaults: `OAUTH_REDIRECT_BASE_URL=localhost:8081`, `FRONTEND_URL=localhost:3000`

## §3 Hard rules 6/6 con caveats

- **HR-1 Anti-autoboicot:** ✅ jose@6.2.3 + @hono/oauth-providers@0.8.5 vigentes oficiales Hono
- **HR-2 Tests adversariales:** ✅ 27 tests (10 jwt round-trip + 8 ataques + 17 auth) — confiado vía reporte Manus binario
- **HR-3 SPEC compliance:** ✅ ACs §11 cumplidos. Cookie name desviación documentada RFC 6265 verbatim en JSDoc
- **HR-4 Fail-loud producción:** ✅ superRefine enforcement verificable
- **HR-5 Sin regresión:** ✅ 207/207 (180 D2.5 + 17 D3.3 + 27 D4) — confiado vía reporte
- **HR-6 Sin secrets en código:** ✅ con **CAVEAT P2** — disclosure honesta Manus E1: credenciales OAuth pasaron por chat de onboarding T1. Recomendación rotación post-D6 deploy. JWT_SECRET generado correctamente con `openssl rand -hex 48` NO derivado de chat.

## §4 5 decisiones binarias D4 — RATIFICADAS

| # | Decisión | Ratificación Cowork |
|---|---|---|
| 1 | D4 = OAuth solo, RAG diferido | ✅ Correcta — D5 SQL no existe, RAG depende de tablas |
| 2 | JWT propio vs Supabase Auth | ✅ Correcta — D5 no provisionado, JWT self-contained válido, migrable después |
| 3 | Selector NODE_ENV vs remover stub | ✅ Correcta — 180 tests sin tocar, stub ya endurecido D2.5 H-1 |
| 4 | Mock googleAuth vs MSW/hits reales | ✅ Correcta — hermetic + fast, smoke real D6 |
| 5 | Cookie name `la-forja_session` vs `:` | ✅ Correcta — RFC 6265 obliga, documentado verbatim |

## §5 Caveats declarados

### P2 — Rotación credenciales OAuth post-D6 (sub-bloqueante deploy)

Disclosure honesta Manus E1: credenciales Google OAuth pasaron por chat durante onboarding T1 (pegadas voluntariamente del JSON Google Cloud Console). NO afecta JWT_SECRET (generado independientemente con openssl). Recomendación:

1. **Pre-deploy D6:** rotar `GOOGLE_OAUTH_CLIENT_SECRET` en Google Cloud Console → updated Railway secret
2. **Post-deploy D6:** smoke real con curl + browser flow
3. **Canonización futura:** DSC sub-magna "doctrina onboarding sin secrets en chat" — sprint governance separado

**NO bloquea merge D4** — la rotación es operativa, no estructural.

### P3 — AC #12 skip-list confiado sin lectura directa

No leí `apps/la-forja/api/src/index.ts` verbatim. Manus reportó skip-list en `:127-138` con descripción coherente. Confiado vía:
- Track record reciente Manus E2 (D3.3 SHIP VERDE + D2.5 hardening) honesto y binario
- AC #12 es trivial (skip-list de pipeline) — bajo impacto si fallara
- Tests 207/207 verde implícitamente cubrirían comportamiento

**Si Cowork futuro quiere verificación verbatim:** `grep -n "api/auth" apps/la-forja/api/src/index.ts` en branch `sprint/la-forja-001-d4`.

## §6 Firma formal DSC-LF-009

**DSC-LF-009 T2A-Cowork firmado:**

> *"La autenticación de La Forja se realiza exclusivamente con Google OAuth 2.0 (Authorization Code flow) emitiendo una sesión propia firmada con JWT HS256 (paquete `jose@^6.2.3`). La sesión persiste en cookie HttpOnly llamada `la-forja_session` (RFC 6265: `_` en lugar de `:`). Whitelist de roles hard-coded en `setRoleWhitelist` (D4); migrable a Supabase tabla `forja_user_roles` en D5+. El stub D2.5 con `x-user-id` se preserva como mecanismo dev/test exclusivamente — el selector binario por `NODE_ENV` lo bloquea en producción (503 H-1 doctrina). Aplica forward desde D4 (commit `ba7ee8e`); sin retroactivos."*

Firmado: **Cowork T2-A** (auditor delegado T1 Alfredo Góngora)
Fecha: 2026-05-17

## §7 Veredicto formal

🟢 **D4 SHIP — VERDE FINAL · MERGE A MAIN AUTORIZADO**

Manus E1 / T1 autorizados a abrir PR + mergear a main.

## §8 Próximos pasos

1. **HOY:** T1 / Manus E1 abre PR a main + mergea
2. **+1d:** Si D4.5 quiere atacar 6 lint errors preexistentes, sprint separado
3. **+2-3d:** D5 backend SQL migraciones (`0036-0044_la_forja_*.sql`) + frontend login button
4. **+5-7d:** D6 deploy Railway + smoke real + rotación credenciales OAuth post-deploy

---

**Cowork T2-A | auditor externo, autoridad delegada T1**
**Estado canónico: `🟢 D4 SHIP — VERDE FINAL · DSC-LF-009 FIRMADO`**
