---
id: DSC-LF-013
proyecto: LA-FORJA
tipo: sprint_closure
titulo: "D4 SIGNOFF — Google OAuth + JWT auth canónica con `forjaAuthGoogle` + `forjaAuthSelector()` discriminado por NODE_ENV. Cookie `la-forja_session` HttpOnly+secure+SameSite=Lax+maxAge=7d. Firmado Cowork T2-A 2026-05-17 + fix call site post-PR #166 commit `82f580ac` (renumerado desde LF-009 por DSC-DRIFT-CLEANUP)."
estado: firmado
fecha_decision: 2026-05-17 (audit + signoff original como LF-009)
fecha_renumeracion: 2026-05-18 (Sprint DSC-DRIFT-CLEANUP, Opción E refinement Cowork T2-A)
fecha_fix_call_site: 2026-05-18 (PR #166 fast-track fix Opción 2, mergeado commit `82f580ac`)
autoridad_firma: Cowork T2-A bajo autoridad delegada T1
sprint_cerrado: LA-FORJA-001 D4 (Google OAuth + JWT auth canónica)
prs_referencia: ["#133", "#166 (fast-track fix)"]
cruza_con: [DSC-LF-001, DSC-LF-005, DSC-G-008, DSC-G-013]
---

# D4 SIGNOFF — Google OAuth + JWT Auth Canónica (DSC-LF-013)

## Decisión canónica

> **D4 LA-FORJA-001 cerrado VERDE FINAL** — Google OAuth + JWT auth canónica. `forjaAuthGoogle()` para production (Google ID token + JWT verification), `forjaAuthStub()` para test/dev (x-user-id header). Selector binario `forjaAuthSelector()` discrimina por `NODE_ENV`. Cookie de sesión `la-forja_session` HttpOnly + secure + SameSite=Lax + maxAge=7d. Firmado Cowork T2-A 2026-05-17 post-audit DSC-G-008 v4 sobre PR #133. **Fix call site aplicado post-PR #166 (2026-05-18 commit `82f580ac`)**: `index.ts` usaba `forjaAuthStub()` hardcoded en lugar de `forjaAuthSelector()` (drift Categoría 4 DSC-G-013 v0.1 código↔código).

## Contexto de renumeración

Firmado originalmente como **DSC-LF-009** el 2026-05-17 en `_INDEX.md` durante MAGNA-CIERRE-002 / DRIFT-013. Archivo físico nunca creado (F2 estructural).

Detectado por Manus E2 2026-05-18 + resuelto via Sprint DSC-DRIFT-CLEANUP-2026-05-18 (Opción E refinement T2-A autorización T1 "la firmo"). Renumerado retroactivamente a LF-013.

## Adicional: F2 Cowork sobre call site

Mi audit DSC-LF-009 original (2026-05-17) verificó:
- ✅ Función `forjaAuthSelector()` definida en `apps/la-forja/api/src/middleware/auth.ts` L180-187
- ❌ NO verificó binariamente que `apps/la-forja/api/src/index.ts` USE `forjaAuthSelector()`

Manus E2 detectó durante smoke C3 §7.1 (2026-05-18) que `index.ts:141` montaba `forjaAuthStub()` hardcoded. Drift Categoría 4 DSC-G-013 v0.1 (código↔código).

Fix Opción 2 (3 líneas) autorizado via addendum `bridge/cowork_to_manus_HILO_EJECUTOR_2_D4_PROD_AUTH_001_ADDENDUM_FIX_AUTORIZADO_2026_05_18.md` commit `cd4d35f`. PR #166 mergeado a main commit `82f580ac` 2026-05-18 ~09:30 UTC. 242/242 vitest verde + 3 tests regresión §5 anti-F2.

## Cumplimiento DSC-G-008 v4 (audit original D4 2026-05-17 + audit PR #166 2026-05-18)

| Punto | Status |
|---|---|
| G1 diff línea por línea | ✅ original + ✅ PR #166 (ZERO drift vs addendum §2) |
| G2 feature flags | ✅ Selector binario NODE_ENV |
| G3 cero secrets | ✅ (PR #166 fakes test placeholders explícitos non-prod) |
| G4 tests presentes | ✅ + 3 nuevos regresión §5 |
| G5 scope limpio | ✅ |
| G6 no-duplicate de main | ✅ |

## Cláusula de revisión

Este signoff se revisa cuando:
- Google OAuth API breaking changes
- JWT library security advisory
- Cookie SameSite policy change (browser defaults)
- Smoke C3 §7.1-§7.5 falla post-redeploy producción

## Pendiente operativo (Manus E2)

1. ⏭️ Railway redeploy --yes (post-merge PR #166)
2. ⏭️ Smoke C3 §7.1-§7.5 contra `https://la-forja-api-production.up.railway.app`
3. ⏭️ Login E2E manual T1 (`Alfredogl1.gongora@gmail.com`)
4. ⏭️ 4 SQL queries verificación Supabase M1/M2/M3/M4
5. ⏭️ Bridge cierre + frase canónica final 🏛️ D4-PROD-AUTH-001 — DECLARADO

## Cierre binario

D4 LA-FORJA-001 ESTABLECIDO + bug call site cerrado. Google OAuth + JWT + selector NODE_ENV son la frontera canónica de auth para todos los sprints posteriores. DSC-LF-001 (cinco puertas inviolables §3 anti-IDOR ensureThread) opera sobre este sustrato.
