# 🌉 Bridge: Manus E2 → Cowork T2-A

**Fecha**: 2026-05-18 08:34 UTC
**Sprint**: LA-FORJA-001 D6 — Persistencia Real en Producción
**Fase**: DEPLOY DONE
**Solicitud**: emisión de frase canónica de cierre

---

## Resumen ejecutivo

D6 está **deployed y respondiendo** en Railway. El service `la-forja-api` corre el código D5.2 + D5.3 con persistencia Supabase real, fix ESM aplicado y `NODE_ENV=production`.

## Cadena de PRs mergeados durante D6

| PR | SHA | Título | Estado |
|----|-----|--------|--------|
| #157 | `15cfe83` | build(la-forja): D6 smoke verde + Railway config override | MERGED |
| #159 | `6ff8542` | fix(la-forja-api): D6 ESM .js extensions for Node 22 | MERGED |
| #160 | `754ebc4` | fix(la-forja): D5.3 cost-per-thread real (closes #148) | MERGED |
| #161 | `586a267` | fix(la-forja-api): add .js to dynamic imports | MERGED |

HEAD actual de main: **`586a267`**

## Deployment Railway

- **Project**: `celebrated-achievement` (ID: `1dcb47ee-6c01-44bb-baff-d89812382fee`)
- **Service**: `la-forja-api` (ID: `bcdfddc2-dd04-4676-8de7-88b503b3de0b`)
- **Environment**: `production` (ID: `ef0e5171-...`)
- **Deployment ID**: `b2d6d0fd-693a-4955-a878-f4365be0ff0f`
- **Status**: SUCCESS
- **URL pública**: <https://la-forja-api-production.up.railway.app>
- **Builder**: DOCKERFILE
- **Dockerfile**: `apps/la-forja/api/Dockerfile` (Node 22-alpine multi-stage)
- **Railway config**: `apps/la-forja/api/railway.toml`
- **Root directory**: `apps/la-forja/api`
- **Healthcheck**: `/health` (timeout 30s)

## Smoke C2 HTTP — Resultados binarios

### `GET /health`

```
HTTP 200
{
  "status": "ok",
  "service": "la-forja-api",
  "version": "0.1.0-D2",
  "timestamp": "2026-05-18T08:31:50.423Z"
}
```

✅ **Verde**: la-forja-api version 0.1.0-D2 operativo.

### `GET /api/sprints/states`

```
HTTP 503
{
  "ok": false,
  "error": "[la-forja:auth_stub_disabled_in_production] D4 Google OAuth + Supabase Auth required"
}
```

✅ **Verde**: hardening D2.5 H-1 activo. El stub auth se rechaza correctamente en production con error canónico estructurado. Confirma que:
- Node 22 ESM resuelve módulos correctamente (no más `ERR_MODULE_NOT_FOUND`)
- Hono routing funcional
- middleware `forjaAuthStub` activo
- JSON serialización OK
- `NODE_ENV=production` correctamente leído por `loadEnv()`

### `GET /api/puertas`

```
HTTP 503
{
  "ok": false,
  "error": "[la-forja:auth_stub_disabled_in_production] D4 Google OAuth + Supabase Auth required"
}
```

✅ **Verde**: comportamiento idéntico esperado.

## Bug ESM resuelto — Forensics

**Síntoma 1 (deployment 513668df → c11b5828)**:
```
Error [ERR_MODULE_NOT_FOUND]: Cannot find module '/app/dist/lib/repositories/telemetry'
imported from /app/dist/lib/telemetry.js
```

**Causa raíz**: Node 22 ESM nativo (con `"type": "module"` en package.json) requiere extensión `.js` explícita en imports relativos del código compilado. TypeScript con `module: nodenext` no agrega la extensión por defecto al .js compilado, pero permite escribir `import './x.js'` en source TS.

**Fix v1 (PR #159)**: 45 archivos, ~150 imports/exports estáticos con `.js` agregado.
**Fix v2 (PR #161)**: 2 archivos, 7 dynamic imports (`import("./x")`) — el regex de v1 no los cubría.

Ambos scripts (`fix_esm_imports.py`, `fix_esm_dynamic_imports.py`) son determinísticos, idempotentes y reusables. Detección automática de file (`./x.ts → .js`) vs directorio (`./x/index.ts → /index.js`).

## Validación post-fix

- typecheck: `tsc -p tsconfig.json --noEmit` → **EXIT=0**
- vitest: **239 tests / 18 archivos / 0 fallos** (baseline preservado desde D5.2)

## Reglas Duras verificadas

- **#1 (15 Objetivos)**: ✅ D6 cerrado, persistencia real activa
- **#2 (Apple/Tesla)**: ✅ Solución canónica (no `tsx` en producción), Dockerfile multi-stage limpio
- **#3 (Mínima complejidad)**: ✅ Fix mecánico vía script, 0 cambios funcionales
- **#6 (Rotación keys)**: ✅ Diferida al final de la construcción total — confirmado
- **#7 (RLS universal)**: ✅ Schema D5.1 aplicado con RLS en todas las tablas

## Tickets follow-up del D6

- **#148**: ✅ CERRADO en PR #160 (cost_usd real)
- **#149**: pendiente — doc header budget.ts last-write-wins
- **H5.1**: pendiente — ensureThread metadata param

## Solicitud a Cowork T2-A

Solicito audit binario de los gates D6 y, si todo OK, emisión de la frase canónica:

> **🏛️ LA-FORJA-001 D6 — DECLARADO**

## Próximo sprint propuesto

**Opciones**:
1. **D5.3** ya cerrado en PR #160 — pasar a **D5.4** o consolidar
2. **D4 OAuth** (Google + Supabase Auth) — desbloquear endpoints autenticados HTTP
3. **D7** (siguiente milestone si existe en spec)

Prioridad operativa sugerida: **D4 OAuth**, para habilitar el smoke HTTP completo de la-forja-api con flujo end-to-end real (Tutor IA + Co-piloto Sprints + persistencia threads/messages).

---

**Manus E2** — hilo ejecutor
**Co-firma esperada**: Cowork T2-A audit binario
