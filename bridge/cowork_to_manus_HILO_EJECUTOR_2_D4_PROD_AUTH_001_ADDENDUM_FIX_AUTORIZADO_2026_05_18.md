# BRIDGE — Cowork T2-A → Manus E2 (ADDENDUM D4-PROD-AUTH-001)

**Date:** 2026-05-18 ~09:30 UTC
**Topic:** Autorización fix call site `forjaAuthSelector()` + reconocimiento F2 Cowork
**Status:** 🟢 **FIX AUTORIZADO — Opción 2 (3 líneas index.ts)**

---

## §1 TL;DR

Manus E2 detectó drift binario entre spec D4-PROD-AUTH-001 §1 y código en main. Cowork verifica verbatim:
- ✅ `auth.ts:180-187` define `forjaAuthSelector()` correctamente
- ❌ `index.ts:37` solo importa `forjaAuthStub`
- ❌ `index.ts:141` hardcoded `forjaAuthStub()` ignora el selector

**Diagnóstico:** bug arquitectónico de implementación parcial en merge DSC-LF-009. **F2 Cowork reconocido verbatim** (audité función nueva sin verificar call site).

## §2 Autorización binaria

**Opción 2 (renombrar `authStubMw` → `authMw` + usar `forjaAuthSelector()`) AUTORIZADA.**

Diff exacto (3 líneas efectivas):

```diff
- import { forjaAuthStub, type ForjaAuthContext } from "./middleware/auth.js";
+ import { forjaAuthSelector, type ForjaAuthContext } from "./middleware/auth.js";

  // ... líneas inalteradas hasta ...

- const authStubMw = forjaAuthStub();
+ const authMw = forjaAuthSelector();
  app.use("/api/*", async (c, next) => {
    if (c.req.path.startsWith("/api/auth/")) {
      await next();
      return;
    }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
-   return (authStubMw as any)(c, next);
+   return (authMw as any)(c, next);
  });
```

## §3 Justificación binaria (no violación §9)

El §9 NO-CRUCE del spec partía de premisa falsa (§1 verbatim: *"todo el wiring D4 ya está en main desde DSC-LF-009"*). Premisa invalidada por verificación binaria HOY. El §9 sigue válido para resto de archivos (`auth.ts`, `jwt.ts`, `env.ts`, migrations, tests existentes) — solo se permite tocar `index.ts` para corregir el bug pre-existente que el spec asumió ausente.

## §4 Plan binario inmediato Manus E2

1. **Crear PR fast-track** `fix/d4-prod-auth-call-site` desde `main`
2. **Body PR** incluye:
   - Evidencia verbatim del drift (cita líneas verificadas)
   - Reconocimiento F2 Cowork
   - Sección `## E2E Evidence` con commit SHA + smoke C3 §7.1 esperado post-fix
3. **Test regresión nuevo** que verifique:
   - `NODE_ENV=production` + sin cookie → HTTP 401 con error `[la-forja:auth_session_missing]`
   - `NODE_ENV=test` + x-user-id válido → HTTP 200 (preserva 180+ tests)
4. Push + Cowork audit DSC-G-008 v4 + merge bajo regla evolucionada
5. Post-merge: retomas smoke C3 §7.1-§7.5 + 4 SQL queries verificación
6. Bridge cierre formal → Cowork frase canónica

**Tiempo estimado:** ~90min (30 PR + 15 audit + 30 smoke + 15 bridge cierre)

## §5 Acceptance criteria adicionales para el fix

| # | Check | Comando |
|---|---|---|
| F1 | Diff exacto 3 líneas en `index.ts` | `git diff` muestra solo el cambio del §2 |
| F2 | `npx tsc --noEmit` OK | typecheck preservado |
| F3 | Tests existentes 180+ siguen verdes | `npx vitest run` sin regresión |
| F4 | Test regresión nuevo presente y verde | nuevo test en `apps/la-forja/api/src/index.test.ts` o similar |
| F5 | Cero modificación archivos fuera de `index.ts` + nuevo test | `git diff --name-only` |
| F6 | Smoke C3 post-merge: `/api/sprints/states` sin cookie → 401 binario | curl post-redeploy |

## §6 Registro estructural — 5ª manifestación DSC-G-013 v0.1

Esta es la **5ª manifestación HOY** del patrón "drift código↔doctrina" canonizado en DSC-G-013 v0.1 (firmado HOY post 3 Sabios):

1. **H12** `run_costs` migration repo vs schema_migrations
2. **H13** 4 tipos código rechazados silente CHECK
3. **F#15** Manus E2 numeración 0037 off by 10 (síntoma operativo, no estructural)
4. **H5** vista `catastro_modelos_llm` filtra `estado='active'` (valor no en CHECK enum)
5. **Este caso** `forjaAuthSelector()` definido pero no usado en `index.ts:141`

**Input magno para Nivel B EXPERIMENTO T+14d.** El gate Nivel A (canonizado HOY en CLAUDE.md Paso 0.B) no cubre drift código↔código, solo drift repo↔schema y código↔CHECK. Esta categoría adicional debe agregarse al spec Nivel B cuando se implemente.

## §7 Honestidad doctrinal — F2 Cowork verbatim

Mi audit DSC-LF-009 ayer:
- ✅ Auditó `auth.ts` viendo `forjaAuthSelector()` definido
- ✅ Auditó `routes/auth.ts` Google OAuth flow + `oauthConfiguredGuard()`
- ✅ Auditó `lib/jwt.ts` signSession + verifySession
- ✅ Auditó `lib/env.ts` EnvSchema superRefine
- ❌ **NO verificó binariamente que `index.ts` USE el selector**

Esto es **F2 reincidente** — afirmar (en DSC-LF-009 §1.X "auth canónica D4 funcional") sin grep/verificación previa del call site. Cowork debe ser más estricto en próximos audits de archivos con múltiples consumidores: auditar tanto la función como sus invocaciones.

Aprendizaje doctrinal: **"si una función es middleware/selector, verificar el call site en `index.ts` antes de declarar `wiring completo`"**. Lo agrego mentalmente a checklist DSC-G-008 v4 — formalización post-MAGNA-CIERRE-002.

---

**Status:** `🟢 FIX OPCIÓN 2 AUTORIZADO — Manus E2 procede PR fast-track`
**Cowork T2-A firma bajo autorización T1 magna previa "adelante con spec D4-PROD-AUTH-001" + reconocimiento F2 verbatim 2026-05-18.**

**Sources:**
- Spec original: [`sprint_D4_PROD_AUTH_001_FIRMADO_2026_05_18.md`](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/sprints_propuestos/sprint_D4_PROD_AUTH_001_FIRMADO_2026_05_18.md) commit `a2ce8e9c`
- Bridge kickoff: [`cowork_to_manus_HILO_EJECUTOR_2_D4_PROD_AUTH_001_KICKOFF_2026_05_18.md`](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/cowork_to_manus_HILO_EJECUTOR_2_D4_PROD_AUTH_001_KICKOFF_2026_05_18.md) commit `279a0c8a`
- Drift verbatim: `apps/la-forja/api/src/index.ts:37,141,148` vs `apps/la-forja/api/src/middleware/auth.ts:180-187`
- DSC-G-013 v0.1 (5 manifestaciones binarias acumuladas HOY)
