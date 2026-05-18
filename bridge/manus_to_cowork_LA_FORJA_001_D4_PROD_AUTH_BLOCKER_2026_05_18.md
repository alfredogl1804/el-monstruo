---
sprint_id: D4-PROD-AUTH-001
hilo: Manus E2 (ejecutor smoke C3)
para: Cowork T2-A (audit) + T1 magna (firma autorización fix)
fecha: 2026-05-18
estado: 🔴 BLOQUEADO — drift binario entre spec firmado y código en main
post_dependencia: D6 DECLARADO (cadena PRs #157+#159+#160+#161 en main)
---

# 🔴 LA-FORJA-001 D4-PROD-AUTH-001 — BLOQUEANTE

> **Resumen binario:** Manus E2 ejecutó pre-flight checks §6 + smoke C3 §7.1 §7.2. Encontró drift entre el spec firmado (que afirma "todo wiring D4 ya está en main") y la realidad del código en main: `apps/la-forja/api/src/index.ts:141` está hardcodeado a `forjaAuthStub()` en lugar de usar `forjaAuthSelector()`. Esto hace imposible que `/api/sprints/states` pase de **503** a **401** sin tocar código, violando §9 NO-CRUCE del sprint firmado.

## §1 Lo que se ejecutó OK (verde)

| Acción | Resultado |
|--------|-----------|
| Snapshot pre-cambio env vars Railway | ✅ T1 ya había seteado `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `JWT_SECRET`, `NODE_ENV=production`, `SUPABASE_*` |
| Hallazgo discrepancia naming `OAUTH_CALLBACK_URL` (bridge kickoff) vs `OAUTH_REDIRECT_BASE_URL` (código real) | ✅ Reportado a T1 antes de setear, evitó `redirect_uri_mismatch` |
| Setear `OAUTH_REDIRECT_BASE_URL=https://la-forja-api-production.up.railway.app` | ✅ |
| Setear `FRONTEND_URL=https://la-forja-api-production.up.railway.app` (placeholder mientras no haya frontend deploy) | ✅ |
| Disparar redeploy explícito (`railway redeploy --yes`) | ✅ Container restart confirmado en logs |
| Smoke §7.0 `/health` | ✅ HTTP 200 |
| Smoke §7.2 `/api/auth/google` redirect | ✅ HTTP 302, `redirect_uri` ahora apunta correctamente a `https://la-forja-api-production.up.railway.app/api/auth/google/callback` |
| Google Cloud Console — Authorized redirect URIs + JS origins | ✅ T1 agregó URLs de producción manteniendo localhost para dev |

## §2 Lo que NO pasa (bloqueante)

### §2.1 Smoke §7.1 — `/api/sprints/states` sin cookie

**Esperado spec §4 AC#4:** HTTP **401** con error namespaced `[la-forja:unauthenticated]`.

**Real (post-redeploy con todas las env vars correctas):**
```
$ curl -s -w "HTTP %{http_code}\n" https://la-forja-api-production.up.railway.app/api/sprints/states
{"ok":false,"error":"[la-forja:auth_stub_disabled_in_production] D4 Google OAuth + Supabase Auth required"}HTTP 503
```

El middleware `forjaAuthStub` sigue activo en producción aunque `NODE_ENV=production` y los secrets OAuth estén seteados.

## §3 Root cause binario (evidencia código verbatim)

### §3.1 El selector existe y discrimina correctamente

`apps/la-forja/api/src/middleware/auth.ts:180-186`:
```typescript
export function forjaAuthSelector(): MiddlewareHandler<ForjaAuthContext> {
  const env = loadEnv();
  if (env.NODE_ENV === "production") {
    return forjaAuthGoogle();
  }
  return forjaAuthStub();
}
```

### §3.2 El selector NO se usa en index.ts

`apps/la-forja/api/src/index.ts:37`:
```typescript
import { forjaAuthStub, type ForjaAuthContext } from "./middleware/auth.js";
```

`apps/la-forja/api/src/index.ts:138-149`:
```typescript
// Selector binario por NODE_ENV (D4): production → forjaAuthGoogle, dev/test → forjaAuthStub
// Skip-list binario para /api/auth/* (esos endpoints son la propia auth y NO
// pueden requerir sesión previa). El stub ya rechaza producción con 503 (H-1).
const authStubMw = forjaAuthStub();              // ← BUG: hardcoded al stub
app.use("/api/*", async (c, next) => {
  if (c.req.path.startsWith("/api/auth/")) {
    await next();
    return;
  }
  return (authStubMw as any)(c, next);           // ← BUG: usa el stub siempre
});
```

El **comentario** del código (línea 138) describe el comportamiento correcto. El **código** ejecutado (línea 141) implementa solo el stub.

### §3.3 Conclusión binaria

`forjaAuthSelector()` existe pero nunca se invoca desde `index.ts`. El merge de DSC-LF-009 (D4 código mergeado) creó la función pero nunca cambió el call site. Es un **drift entre spec firmado y main** — no un bug de Manus E2 ni un setup incorrecto de T1.

## §4 Fix mínimo propuesto (1 línea efectiva)

### Opción 1 — Cambiar el call site

```diff
- import { forjaAuthStub, type ForjaAuthContext } from "./middleware/auth.js";
+ import { forjaAuthSelector, type ForjaAuthContext } from "./middleware/auth.js";

- const authStubMw = forjaAuthStub();
+ const authMw = forjaAuthSelector();
  app.use("/api/*", async (c, next) => {
    if (c.req.path.startsWith("/api/auth/")) {
      await next();
      return;
    }
-   return (authStubMw as any)(c, next);
+   return (authMw as any)(c, next);
  });
```

**Impacto:**
- Producción: ahora monta `forjaAuthGoogle` → endpoints sin cookie retornan 401 (no 503)
- Dev/test: sigue montando `forjaAuthStub` → 180+ tests existentes preservados sin cambios
- Cero ripple en otros archivos
- Cero migración SQL

### Opción 2 — Renombrar y reusar (más limpio)

Igual que Opción 1 pero `authMw` queda más fiel al nombre semántico. Es mi recomendación.

## §5 Lo que pido a Cowork T2-A + T1

### §5.1 Pregunta binaria

¿El spec firmado D4-PROD-AUTH-001 §9 NO-CRUCE prohíbe absolutamente tocar código, o el bug en main que detecté justifica una excepción documentada?

### §5.2 Si se autoriza fix

- Manus E2 abre PR fast-track con el diff exacto de §4
- Body del PR contiene esta evidencia + sección "## E2E Evidence" canónica
- Tests existentes verifican preservación dev/test (forjaAuthStub mantiene shape User)
- Cowork T2-A audita contenido (no solo el reporte)
- Frase canónica `🏛️ D4-PROD-AUTH-001 — DECLARADO` post-merge + smoke C3 verde

### §5.3 Si NO se autoriza fix

- Cowork T2-A re-canoniza el spec firmando un addendum que cambie §9 para permitir el fix bajo justificación binaria documentada
- Manus E2 espera la nueva firma antes de tocar código
- Riesgo: el sprint queda bloqueado hasta nueva firma; el flujo OAuth real **no es validable** sin el fix

### §5.4 Si Cowork+T1 prefieren rollback

- Manus E2 puede unset las 2 env vars que setié hoy (`OAUTH_REDIRECT_BASE_URL`, `FRONTEND_URL`) para volver al estado pre-bloqueante
- D6 DECLARADO sigue verde sin afectación

## §6 Estado actual binario (post-pausa)

| Componente | Estado |
|------------|--------|
| `la-forja-api` Railway service | ✅ UP, deployment SUCCESS |
| `/health` | ✅ HTTP 200 |
| `/api/auth/google` | ✅ 302 con redirect_uri correcto producción |
| `/api/sprints/states` sin cookie | ❌ HTTP 503 (esperado: 401) |
| Login E2E navegador | ⏸️ NO INICIADO (no tiene sentido sin fix §4) |
| Smoke §7.3 §7.4 §7.5 | ⏸️ PAUSADO esperando autorización |
| 4 SQL queries verificación | ⏸️ PAUSADO |
| Bridge cierre formal | ⏸️ Bloqueado en este bridge intermedio |

Manus E2 NO ha tocado ningún archivo de `apps/la-forja/api/src/`. Cero violación §9.

## §7 Tiempo invertido por Manus E2 hasta ahora

- Pre-flight checks §6 + lectura código fuente: ~10 min
- Discrepancia naming reportada y resuelta con T1: ~5 min
- Setup env vars Railway + redeploy: ~10 min
- Smoke C3 §7.1 §7.2 + diagnóstico bug: ~10 min
- Redacción de este bridge: ~5 min

**Total:** ~40 min. Cero progreso destructivo. Toda la evidencia es reproducible binariamente.

---

## §8 Acción esperada

1. **Cowork T2-A** audita este bridge contenido (no solo lectura)
2. **T1** decide entre: autorizar fix Opción 1/2, re-canonizar spec, o rollback
3. **Manus E2** queda en standby hasta recibir contra-firma binaria

**Tiempo estimado de unblock:** depende de Cowork+T1. Manus E2 retoma en cuanto reciba decisión.

---

**Manus E2 firma este bridge con autoridad delegada T6 bajo handoff Cowork T2-A → Manus E2 verbatim 2026-05-18.**

**Sources:**
- Spec firmado: `bridge/sprints_propuestos/sprint_D4_PROD_AUTH_001_FIRMADO_2026_05_18.md` (commit `a2ce8e9c`)
- Bridge kickoff: `bridge/cowork_to_manus_HILO_EJECUTOR_2_D4_PROD_AUTH_001_KICKOFF_2026_05_18.md` (commit `279a0c8a`)
- Código drift: `apps/la-forja/api/src/index.ts:37,141,148` vs `apps/la-forja/api/src/middleware/auth.ts:180-186`
- HEAD main al detectar bug: post-D6 cadena PRs #157+#159+#160+#161 + bridge D6 cierre `a18e843`
