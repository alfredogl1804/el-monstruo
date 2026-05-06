# Sprint 90 — Stripe Checkout: Extraction a Paquete Reutilizable `@monstruo/checkout-stripe`

**Estado:** Propuesto  
**Hilo:** Ejecutor (Alfredo)  
**ETA (actualizado):** 30-60 min reales (velocity: extraction + npm publish + docs)  
**Objetivo Maestro:** #7 (No reinventar la rueda) + #6 (Velocidad sin sacrificar)

---

## Audit Pre-Sprint

**Current State:**
- Stripe integration location: `like-kukulkan-tickets/src/components/StripeCheckout.tsx`
- Implementation: React component + backend webhook handler
- Maturity: Stable, tested, production in kukulkan-tickets v1.0
- Pattern: Tightly coupled to kukulkan-tickets domain (tickets, invoices)

**Extraction Analysis:**
- Non-reusable code: ~120 LOC (hardcoded to ticket schema)
- Reusable core: ~220 LOC (Stripe API wrapper, webhook handling)
- Potential consumers: 3+ projects (El Monstruo products, future SaaS)
- NPM publishing: Ready (no private dependencies, single Stripe API key)

**Risk Assessment:**
- Backward compat: kukulkan-tickets continues to work post-extraction (via npm import)
- Testing: Current suite covers 85%, target 95% for package
- Versioning: v1.0.0-alpha (first release)

**Dependencies to Manage:**
- React, Stripe.js, TypeScript (peer deps)
- Manus WebDev team (publishing to private npm registry)
- Kukulkan-tickets migration (import from package)

---

## Tareas del Sprint

### Tarea 1: Crear Paquete `@monstruo/checkout-stripe`

**Descripción:**
Extraer lógica de Stripe checkout de kukulkan-tickets en paquete npm independiente.

**Structure:**
```
@monstruo/checkout-stripe/
├── src/
│   ├── client/
│   │   ├── StripeCheckoutForm.tsx       # Main component
│   │   ├── useStripeCheckout.ts         # Hook
│   │   └── types.ts
│   ├── server/
│   │   ├── webhook.ts                   # POST /api/webhooks/stripe
│   │   ├── client-secret.ts             # POST /api/stripe/intent
│   │   └── types.ts
│   ├── config.ts                        # Public config
│   └── index.ts
├── tests/
│   ├── StripeCheckoutForm.test.tsx
│   ├── webhook.test.ts
│   └── integration.test.ts
├── package.json
├── tsconfig.json
└── README.md
```

**Deliverables:**
- Código: 220 LOC reusable, 0 hardcoded refs a kukulkan-tickets
- Config: Environment variables (STRIPE_SECRET_KEY, WEBHOOK_SECRET)
- API: Stable exports (StripeCheckoutForm, useStripeCheckout, handleWebhook)
- Tests: 95%+ coverage

**Métricas:**
- Cyclomatic complexity: < 5 per function
- Bundle size: < 15KB (gzipped)
- Build time: < 2 seconds

---

### Tarea 2: API Gateway + Webhook Routing

**Descripción:**
Crear generic webhook handler que pueda ser usado por múltiples proyectos sin config redundante.

**Implementation:**
```typescript
// @monstruo/checkout-stripe/src/server/webhook.ts
export async function handleStripeWebhook(
  req: Request,
  options: StripeWebhookOptions
): Promise<Response> {
  // Verify signature
  // Route event (charge.succeeded, invoice.paid, etc.)
  // Call handlers from options.handlers
}

// Usage en cualquier proyecto:
export default handler(async (req, res) => {
  const response = await handleStripeWebhook(req, {
    handlers: {
      'charge.succeeded': myCustomChargeHandler,
      'invoice.paid': myCustomInvoiceHandler,
    }
  });
  res.status(response.status).json(response.body);
});
```

**Deliverables:**
- Webhook: Generic, 100 LOC max
- Handlers: Plugin architecture (custom handlers via options)
- Error handling: Proper logging + Datadog integration
- Tests: Mock Stripe events, verify routing

**Métricas:**
- Event latency: < 100ms p95
- Error rate: < 0.1%
- Handler reloadability: 0 redeploys needed for handler changes

---

### Tarea 3: Migration de kukulkan-tickets

**Descripción:**
Migrar kukulkan-tickets para usar paquete en lugar de local code.

**Changes:**
```diff
- import { StripeCheckoutForm } from '../components/StripeCheckout'
+ import { StripeCheckoutForm } from '@monstruo/checkout-stripe'

# Webhook: route calls to installed package
```

**Deliverables:**
- Migration complete: kukulkan-tickets → @monstruo/checkout-stripe import
- Tests: All existing tests still pass (100% backward compat)
- Size reduction: kukulkan-tickets/src reduced by 340 LOC

**Metrics:**
- Bundle size reduction: 12% (340 LOC removed)
- Import time: Same (no perf regression)
- Regressions: 0

---

### Tarea 4: NPM Publishing + Documentation

**Descripción:**
Publicar paquete a npm (private registry vía Manus) + documentar uso.

**Deliverables:**
- NPM: v1.0.0-alpha published
- README: Setup, usage examples, API reference
- TypeScript: Full type definitions, JSDoc
- Changelog: Initial release notes
- License: MIT

**Docs to create:**
- `README.md`: Quick start + examples
- `docs/API.md`: StripeCheckoutForm props, useStripeCheckout hook
- `docs/WEBHOOK.md`: Webhook setup, event handling, signature verification
- `docs/TESTING.md`: Testing with mock events

**Metrics:**
- Docs coverage: 100% (all public APIs documented)
- Examples: 3+ real-world examples (product purchase, subscription, invoice)
- Type safety: TypeScript strict mode, zero `any`

---

## Aceptación

**Definición de Listo:**
1. Paquete creado + published to npm ✅
2. kukulkan-tickets migrada (cero regressions) ✅
3. Tests: 95%+ coverage ✅
4. Docs: Completa (README + API + webhook) ✅
5. Type safety: TypeScript strict ✅

**Post-sprint Integration:**
- Sprint 88 deployment puede usar package
- Sprint Embrión puede acceder API de forma type-safe
- Future projects: Easy integration via `npm install @monstruo/checkout-stripe`

---

## Notas Técnicas

1. **Peer dependencies:** React 18+, TypeScript 5.0+
2. **Versioning:** SemVer (1.0.0-alpha → 1.0.0 post-sprint 88)
3. **Private registry:** Published via Manus NPM org
4. **Monorepo:** Stored in `/packages/@monstruo/checkout-stripe` if using Lerna/Turborepo

---

**Cowork (Hilo A), spec preparada 2026-05-06**
