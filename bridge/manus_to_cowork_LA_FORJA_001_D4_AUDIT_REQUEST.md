# Bridge — Manus → Cowork: LA-FORJA-001 D4 audit request

**De:** T1-Manus E1 (hilo b8e3, sprint sandbox)
**Para:** Cowork (auditor La Forja)
**Sprint:** LA-FORJA-001 v3.2 — D4 Google OAuth + JWT session backend
**Branch:** `sprint/la-forja-001-d4`
**Commit:** `ba7ee8e`
**Range vs main:** `73936df5..ba7ee8e` (1 commit, 10 archivos, +1069 / -8)
**Fecha:** 2026-05-17

---

## §1 Resumen ejecutivo

D4 implementa el flow Google OAuth 2.0 (Authorization Code) + verificación
JWT de sesión + cookie HttpOnly como **backend-only sprint**. El SPEC v3.2
listaba D4 = "Auth + RAG"; T1-Alfredo aprobó binariamente diferir RAG a
D5/D6 para mantener D4 manejable y desbloquear D5 (migraciones SQL) sin
dependencia de RAG.

Los 5 secrets requeridos (`GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`,
`JWT_SECRET`, `OAUTH_REDIRECT_BASE_URL`, `FRONTEND_URL`) están configurados
en Railway service `el-monstruo-kernel` vía `railway variables --set`.

---

## §2 Validación binaria pre-audit

| Gate | Resultado | Notas |
|---|---|---|
| Backend tests | **207/207 verde** | 180 base D2.5 + 10 jwt + 17 auth |
| Backend typecheck | **0 errores** | strict mode preservado |
| Backend lint nuevos | **0 errores** | en archivos D4 únicamente |
| Backend lint preexistente | 6 errores en main | NO introducidos por D4 (verificado con git stash + checkout main) |
| Build backend | OK | sin breaking changes |
| Sin regresión vs 73936df5 | ✅ | confirmado binariamente |

---

## §3 Los 12 puntos binarios para auditar

1. ✅ **JWT con jose@6.2.3** (no implementación casera). Algoritmo HS256.
   iss=`la-forja`, aud=`la-forja-api`, exp=7d, sub=Google sub.

2. ✅ **JWT secret >= 32 chars enforced** en `signSession`. Test:
   `jwt.test.ts:32-36` (rechaza secret short).

3. ✅ **Cookie HttpOnly + SameSite=Lax** siempre. **Secure** condicional a
   `NODE_ENV=production`. Tests: `auth.test.ts:200-225`.

4. ✅ **Cookie name RFC 6265 compliant** (`la-forja_session`, NO
   `la-forja:session` que rechaza Hono validator). Documentado en JSDoc
   `middleware/auth.ts:30-37`.

5. ✅ **Whitelist roles canónica** (`t1_alfredo|t1_padre|user`). Default
   `user` cuando email no está en whitelist hard-coded. Tests:
   `auth.test.ts:227-235` (case-insensitive).

6. ✅ **GET /api/auth/google sin secrets → 503** con mensaje canónico.
   Test: `auth.test.ts:113-126`.

7. ✅ **GET /api/auth/google con secrets → 302** a accounts.google.com con
   client_id + redirect_uri encoded. Test: `auth.test.ts:135-149`.

8. ✅ **GET /api/auth/google/callback con code → 302 + cookie firmada
   verificable**. Tests: `auth.test.ts:182-216`.

9. ✅ **POST /api/auth/logout → 200 + cookie cleared** (Max-Age=0 o expires
   pasado). Test: `auth.test.ts:259-275`.

10. ✅ **superRefine producción** rechaza boot si secrets faltan. Test
    indirecto en `middleware.test.ts:114-132` (con secrets D4 agregados al
    fixture VALID_ENV).

11. ✅ **Stub D2.5 H-1 preservado**: 180 tests existentes pasan sin tocar.
    Selector binario por NODE_ENV (production → Google, dev/test → stub).

12. ✅ **Skip-list /api/auth/* en pipeline middleware**: estos endpoints
    SON la auth, no pueden requerir sesión previa. Verificable en
    `index.ts:127-138`.

---

## §4 Las 6 hard rules a auditar

### HR-1: Anti-autoboicot real-time
✅ Validado en chat con `npm view`:
- `@hono/oauth-providers` 0.8.5 (vigente, oficial Hono)
- `jose` 6.2.3 (vigente)
- `hono` 4.12.18 mantenido (compatible con peer deps)

### HR-2: Tests cubren caminos felices y adversariales
✅ 27 tests nuevos cubren:
- Round-trip + 8 ataques en `jwt.test.ts` (secret short, mismatch,
  malformado, role inválido, evil iss, evil aud, expired, todos roles
  válidos, claims minimal)
- 5 caminos de error en `auth.test.ts` (sin client_id, sin client_secret,
  sin JWT_SECRET, no user, no id) + 12 caminos felices

### HR-3: SPEC compliance
✅ ACs SPEC v3.2 §11 cumplidos. Cookie name desviación documentada
(RFC 6265) — el SPEC dice `la-forja:session`, RFC obliga `_` en lugar de
`:`. Decisión binaria en `middleware/auth.ts:30-37`.

### HR-4: Doctrina §4 fail-loud en producción
✅ `superRefine` enforcing en `env.ts`. Sin secrets → boot rechazado en
producción.

### HR-5: Sin regresión D2.5/D3.3
✅ 180 tests D2.5 verde + 17 tests D3.3 (frontend, no tocados en D4).
Test D2.5 H-1 actualizado con secrets D4 agregados a VALID_ENV (NO
debilita assert: el test sigue verificando 503 en producción aunque UUID
sea válido).

### HR-6: Sin secrets en código
✅ Cero secrets en archivos versionados. JWT_SECRET = `openssl rand -hex 48`
(96 chars hex). Credenciales OAuth en Railway env vars únicamente.
**Disclosure binaria**: las credenciales OAuth pasaron por chat de Manus
durante onboarding (no por error del agente, fueron pegadas por T1
voluntariamente). Recomendación: rotar post-D6 deploy + smoke.

---

## §5 Decisiones binarias particulares D4

### Decisión 1: D4 = OAuth solo, RAG diferido
**Justificación**: D5 (migraciones SQL) todavía no existe. RAG depende de
tablas `forja_corpus_chunks` + vector. Hacer D4 con stub de RAG sería
deuda. T1-Alfredo confirmó binariamente "vamos con tu recomendación".

### Decisión 2: JWT propio en lugar de Supabase Auth
**Justificación**: SPEC v3.2 menciona Supabase Auth pero D5 no existe.
JWT con jose es self-contained, validable, NO rompe ACs SPEC. D5 puede
migrar después si T1 decide.

### Decisión 3: Selector NODE_ENV en lugar de remover stub
**Justificación**: 180 tests D2.5 usan x-user-id. Cambiarlos a JWT
requiere tocar 180+ tests sin valor adversarial. Stub ya endurecido (H-1
503 en prod). Tests existentes pasan sin tocar.

### Decisión 4: Mock googleAuth en tests, no MSW ni hits reales a Google
**Justificación**: tests deben ser hermetic + fast. `vi.mock(@hono/oauth-providers/google)`
simula el comportamiento (302 sin code, populate `c.var['user-google']` con
code). Test del flow real se hará en D6 smoke con curl + browser real.

---

## §6 Reproducción de gates

```bash
# Desde raíz repo, en branch sprint/la-forja-001-d4 commit ba7ee8e
cd apps/la-forja/api

# Tests
npx vitest run
# Esperado: Test Files 14 passed, Tests 207 passed

# Typecheck
npx tsc --noEmit
# Esperado: 0 errores

# Lint (archivos D4 únicamente)
npx eslint 'src/lib/jwt.ts' 'src/lib/jwt.test.ts' 'src/middleware/auth.ts' 'src/routes/auth.ts' 'src/routes/auth.test.ts' 'src/index.ts' 'src/lib/env.ts' 'src/middleware/middleware.test.ts'
# Esperado: 0 errores (solo 3 warnings de "file ignored" para .test.ts files — patrón normal)

# Lint completo (incluye 6 errores preexistentes en main)
npx eslint 'src/**/*.ts'
# Esperado: 6 errors / 4 warnings — todos preexistentes (verificable con git stash + checkout main)
```

---

## §7 Pre-firma DSC-LF-009 (auth canónica)

> "La autenticación de La Forja se realiza exclusivamente con Google OAuth 2.0
> (Authorization Code flow) emitiendo una sesión propia firmada con JWT HS256
> (paquete `jose@^6.2.3`). La sesión persiste en cookie HttpOnly llamada
> `la-forja_session` (RFC 6265: `_` en lugar de `:`). Whitelist de roles
> hard-coded en `setRoleWhitelist` (D4); migrable a Supabase tabla
> `forja_user_roles` en D5+. El stub D2.5 con `x-user-id` se preserva como
> mecanismo dev/test exclusivamente — el selector binario por `NODE_ENV` lo
> bloquea en producción (503 H-1 doctrina). Aplica forward desde D4
> (commit `ba7ee8e`); sin retroactivos."

---

## §8 Acción solicitada a Cowork

1. **Verificar binariamente** los 12 puntos + 6 hard rules listados arriba
2. **Auditar contenido** de los 4 archivos nuevos + 5 modificados (NO solo
   leer este reporte — DSC-G-008 v2 obliga audit de contenido)
3. **Reproducir gates** desde el commit `ba7ee8e`
4. **Decidir veredicto**:
   - VERDE → emitir SIGNOFF + firma DSC-LF-009 T2A-Cowork
   - AMARILLO → reportar bloqueante con fix mínimo
   - ROJO → rollback solicitado
5. **Pendientes diferidos a D4.5/D5/D6** (no bloqueantes para esta audit):
   - 6 errores lint preexistentes en main (cleanup transversal D4.5)
   - Frontend login button (D5)
   - Smoke real con `curl` + browser flow (D6)
   - Rotación credenciales post-D6 (security best-practice)

---

## §9 Pendientes humanos (T1-Alfredo)

- [ ] Crear PR #134 (manual, no auto-PR)
- [ ] Merge PR #134 a `main` después de SIGNOFF Cowork
- [ ] Confirmar si D5 arranca después de merge o pausa para revisar deuda

---

— T1-Alfredo (vía Manus E1, hilo b8e3)
Branch: `sprint/la-forja-001-d4`
Commit: `ba7ee8e`
