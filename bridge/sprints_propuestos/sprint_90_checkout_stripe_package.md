# Sprint 90 — `@monstruo/checkout-stripe` package extraído

**Owner:** Hilo Ejecutor (Manus)
**Zona protegida:** `packages/checkout-stripe/` (nuevo) + lectura de `like-kukulkan-tickets` (repo separado)
**ETA estimada:** 6-10h reales con Apéndice 1.3 factor velocity
**Bloqueos:** ninguno
**Prerequisito:** Sprint 88 cerrado verde (porque queremos validar el patrón completo en producción antes de extraerlo)
**Dependencias:** acceso al repo `alfredogl1804/like-kukulkan-tickets` (existe y está en producción)

---

## 1. Contexto

DSC-X-002 firmado en `_GLOBAL/`: el módulo de checkout Stripe + webhook + DB confirmation está probado exitosamente en LikeTickets (`alfredogl1804/like-kukulkan-tickets` corriendo en Railway). Es **patrón replicable** que debe ser reutilizado como estándar en:

- LikeTickets (donde ya vive — origen)
- Marketplace Muebles (cuando arranque autónomo per DSC-X-006)
- CIP (cuando se desbloqueen DSC-CIP-PEND-001 + DSC-CIP-PEND-002)
- El Mundo de Tata (cuando llegue a monetización)
- Futuras empresas-hijas con motor económico de pago único o suscripción

La directiva: **construirlo una sola vez y consumirlo en múltiples proyectos** del ecosistema, con un solo lugar para mantener cuando Stripe actualice su API.

Estado actual: el código vive enredado en el repo de LikeTickets. Para reutilizarlo en otra empresa-hija habría que copiar archivos a mano — antipatrón de duplicación.

---

## 2. Objetivo único del sprint

Extraer el módulo de checkout Stripe del repo `like-kukulkan-tickets` y publicarlo como **package npm interno** `@monstruo/checkout-stripe` en el monorepo `el-monstruo` (bajo `packages/checkout-stripe/`), con interface uniforme + documentación + tests + LikeTickets migrado para consumirlo.

Cuando Sprint 90 cierra:
- LikeTickets sigue funcionando idéntico, pero importando el package en lugar de tener el código local
- El package está listo para que Sprint Marketplace-1 (cuando arranque) lo importe sin escribir nada nuevo
- Un solo punto de mantenimiento para futuros updates de Stripe API

---

## 3. Bloques del sprint

### 3.A — Auditoría del módulo actual en LikeTickets

**3.A.1 — Identificar el código relevante**

Lectura del repo `alfredogl1804/like-kukulkan-tickets` para identificar:
- Componentes UI del checkout
- Endpoints backend que procesan el flow (create-checkout-session, webhook handler, confirmation)
- Schema de DB de `transactions` o equivalente
- Configuración de Stripe (env vars, productos, precios)
- Tests existentes

Mapear lo que es **genérico** (reutilizable) vs lo que es **específico de LikeTickets** (tickets de butacas, productos preconfigurados, etc.).

**3.A.2 — Definir la interface del package**

El package expone una interface uniforme que cualquier empresa-hija puede consumir. Ejemplo de API:

```typescript
import { createCheckoutSession, handleWebhook, confirmTransaction } from '@monstruo/checkout-stripe';

// Frontend (Next.js / Vite / etc.)
const session = await createCheckoutSession({
  empresa_hija_id: 'liketickets',
  product_id: 'butaca-zona-like-313',
  unit_price_cents: 25000,
  quantity: 1,
  customer_email: 'cliente@ejemplo.com',
  success_url: 'https://...',
  cancel_url: 'https://...',
  metadata: { /* libre */ }
});

// Backend webhook
await handleWebhook({
  rawBody: req.body,
  signature: req.headers['stripe-signature'],
  onSuccess: async (event) => { /* persistir transaction */ },
  onFailure: async (event) => { /* alertar */ }
});
```

Lo específico de cada empresa-hija (qué producto, qué precio, qué hacer al confirmar) lo pasa cada caller — el package no asume nada del producto.

### 3.B — Construcción del package

**3.B.1 — Estructura del directorio**

```
packages/checkout-stripe/
├── package.json (name: "@monstruo/checkout-stripe", version: "0.1.0")
├── README.md
├── tsconfig.json
├── src/
│   ├── index.ts (re-exporta API pública)
│   ├── createCheckoutSession.ts
│   ├── handleWebhook.ts
│   ├── confirmTransaction.ts
│   ├── types.ts (interfaces TS)
│   └── errors.ts (error classes con Brand DNA — naming canónico)
├── tests/
│   ├── createCheckoutSession.test.ts
│   ├── handleWebhook.test.ts
│   ├── confirmTransaction.test.ts
│   └── fixtures/
└── dist/ (build output, gitignored)
```

**3.B.2 — Implementación con Brand DNA**

Errors siguen formato `{module}_{action}_{failure_type}`:
- `checkout_stripe_create_session_invalid_price`
- `checkout_stripe_webhook_signature_mismatch`
- `checkout_stripe_confirm_transaction_db_failure`
- `checkout_stripe_init_missing_api_key`

NUNCA: "Internal server error", "Something went wrong", "Failed to do X".

Naming de funciones internas con identidad: `forgeCheckoutSession()`, no `createSession()` genérico. Mantener estética industrial brutalista canónica.

**3.B.3 — Schema de DB compartido**

El package incluye una migración SQL canónica para la tabla `transactions` que las empresas-hijas adoptan:

```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_hija_id TEXT NOT NULL,
    stripe_session_id TEXT UNIQUE,
    stripe_payment_intent_id TEXT,
    customer_email TEXT,
    product_id TEXT NOT NULL,
    unit_price_cents INT NOT NULL,
    quantity INT NOT NULL,
    total_cents INT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'mxn',
    status TEXT NOT NULL CHECK (status IN ('pending','confirmed','failed','refunded')),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ
);

CREATE INDEX idx_transactions_empresa ON transactions(empresa_hija_id, status);
CREATE INDEX idx_transactions_stripe_session ON transactions(stripe_session_id);
```

Migración exportada como `packages/checkout-stripe/migrations/001_create_transactions.sql` para que cualquier empresa-hija la corra en su propio Supabase.

### 3.C — Migración de LikeTickets al package

**3.C.1 — Sustituir código local por import del package**

En `like-kukulkan-tickets`:
- Borrar archivos de checkout local
- `npm install @monstruo/checkout-stripe` (o link local del monorepo)
- Reemplazar invocaciones por API del package
- Mantener LikeTickets-specific logic en wrappers thin (`buy-butaca.ts` que llama `createCheckoutSession` del package con sus parámetros)

**3.C.2 — Tests de regresión**

LikeTickets debe seguir funcionando idéntico. Tests E2E que vendían butacas en producción siguen pasando.

**3.C.3 — Smoke productivo**

Comprar 1 butaca real en `ticketlike.mx` desde browser. Verificar que el flow funciona idéntico (session se crea, redirect a Stripe, pago test, webhook recibido, transaction confirmada en DB).

### 3.D — Documentación

**3.D.1 — README del package**

`packages/checkout-stripe/README.md` con:
- Quick start (instalación + primer checkout en 30 segundos)
- API reference completa
- Schema de DB canónico
- Cómo correr la migración
- Configuración de env vars Stripe (test + live)
- Webhook setup en Stripe Dashboard
- Errors con explicación de cuándo ocurre cada uno
- Ejemplos de uso desde Next.js, Vite, Express

**3.D.2 — Skill canónico**

Crear `skills/checkout-stripe-pattern/SKILL.md` que documenta el patrón replicable para futuras empresas-hijas. Cuando un sprint nuevo necesite checkout, lee el skill antes de escribir código.

### 3.E — Publicación

**3.E.1 — Si hay registry npm interno (Verdaccio o similar):** publicar `@monstruo/checkout-stripe@0.1.0`

**3.E.2 — Si no hay registry:** consumir vía workspaces del monorepo (npm/pnpm workspaces o yarn workspaces). Las empresas-hijas dentro del monorepo importan via `"@monstruo/checkout-stripe": "workspace:*"`. Empresas-hijas en repos separados (como LikeTickets actualmente) consumen vía git URL en `package.json` o se mueven al monorepo.

Decisión arquitectónica delegada a Manus durante el sprint según viabilidad.

---

## 4. Magnitudes esperadas

- ~1,000 LOC nuevas en el package
- ~500 LOC borradas en LikeTickets (sustituidas por imports)
- 1 migración SQL canónica (reusable por empresas-hijas)
- ~15 tests del package + tests de regresión LikeTickets
- 1 README magna del package + 1 skill nuevo

---

## 5. Disciplina aplicada

- ✅ Brand DNA en errors (formato `{module}_{action}_{failure_type}`)
- ✅ Anti-Dory: verificar versión actual de Stripe SDK contra registry oficial antes de pin
- ✅ Validación realtime: probar con account de Stripe test antes de tocar producción
- ✅ Capa Memento: si webhook falla, no se pierde la transaction (queda en estado `pending` con audit log para reintentar)
- ✅ Tests con prod real: smoke productivo en `ticketlike.mx` antes de declarar cierre

---

## 6. Cierre formal

Cuando los 5 bloques cierren verde, Hilo Ejecutor declara:

> 🏛️ **`@monstruo/checkout-stripe` v0.1.0 — DECLARADO**

Y reporta al bridge con: package path, ejemplo de uso, smoke productivo en LikeTickets verificado, skill canónico publicado.

---

## 7. Próximos consumidores del package

Una vez cerrado, el package queda listo para:

- **Sprint Marketplace-1** (cuando arranque autónomo per DSC-X-006): adoptar package directamente
- **Sprint CIP-1** (cuando se desbloqueen DSC-CIP-PEND-001 + 002): adoptar package + extender con casos específicos de microinversión
- **Sprint Mundo Tata** (cuando llegue a monetización): adoptar package
- Futuras empresas-hijas: importar y usar

Esto es el patrón Convergencia Diferida (DSC-X-006) materializado: las empresas-hijas comparten infra crítica desde día 1.

---

— Cowork (Hilo A), spec preparada 2026-05-06.