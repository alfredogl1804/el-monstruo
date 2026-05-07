# Sprint 90 — Stripe Checkout: Extraction a Paquete Reutilizable `@monstruo/checkout-stripe`

**Estado:** Propuesto
**Hilo:** Ejecutor (Manus)
**ETA (actualizado):** 45-75 min reales (audit pre-extracción + extraction + npm publish + docs)
**Objetivo Maestro:** #7 (No reinventar la rueda) + #6 (Velocidad sin sacrificar) + #11 (Seguridad adversarial)

---

## 0. Audit pre-extracción OBLIGATORIO (post-incidente P0 — DSC-G-008 v2)

**Antes de extraer código, Manus DEBE auditar `like-kukulkan-tickets` por secrets hardcoded.** El incidente P0 del 2026-05-06 demostró que repos del ecosistema pueden contener secrets en plaintext (crisol-8 + biblia-github-motor confirmados). `like-kukulkan-tickets` toca código de pagos (Stripe = secrets de alta sensibilidad: `sk_live_*`, `whsec_*`, `pk_live_*`) y NUNCA fue auditado contra esos patrones.

### Comandos de audit (orden obligatorio)

```bash
# 1. Clone limpio para audit aislado
gh repo clone alfredogl1804/like-kukulkan-tickets /tmp/audit-likekukulkan-2026-05-06
cd /tmp/audit-likekukulkan-2026-05-06

# 2. Gitleaks histórico
gitleaks detect --source . --report-path /tmp/audit-likekukulkan-gitleaks.json --verbose

# 3. Trufflehog filesystem
trufflehog filesystem /tmp/audit-likekukulkan-2026-05-06 --no-update --json > /tmp/audit-likekukulkan-trufflehog.json

# 4. Grep dirigido por patrones Stripe
grep -rn "sk_live_\|sk_test_\|whsec_\|pk_live_\|pk_test_\|rk_live_\|rk_test_" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  --include="*.env*" --include="*.json" --include="*.yml" \
  --exclude-dir=.git --exclude-dir=node_modules .

# 5. Anti-patrón DSC-S-004 (default values con secrets reales)
grep -rn "process\.env\.[A-Z_]*\s*||\s*['\"]\(sk_\|whsec_\|pk_\|rk_\)" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" .

# 6. DSN hardcoded (TiDB, Supabase, otros)
grep -rn "mysql://\|postgresql://\|postgres://\|mongodb://" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  --include="*.env*" --exclude-dir=.git --exclude-dir=node_modules .
```

### Decision tree post-audit

| Resultado | Acción |
|---|---|
| Cero hits | Proceder con Tarea 1 (extraction). |
| 1+ hits Stripe keys hardcoded | **STOP.** Aplicar mismo flujo que incidente P0: rotar Stripe keys (Dashboard Stripe → API keys → Roll), refactor con env vars (DSC-S-003 + S-004), commit fix, después arrancar Tarea 1. |
| 1+ hits DSN hardcoded | Mismo flujo: rotar credenciales de DB, refactor, después extraction. |
| Hits que parecen legítimos (placeholders en `.env.example`, tests con `sk_test_dummy`) | Documentar en bridge + proceder con Tarea 1. |

### Reporte obligatorio al bridge ANTES de Tarea 1

`bridge/manus_to_cowork_AUDIT_LIKEKUKULKAN_PRE_SPRINT_90_<fecha>.md` con:
- Output de los 6 comandos de audit
- Clasificación de cada hit (real secret / placeholder / test fixture)
- Acciones tomadas si hubo hits reales
- Confirmación: "audit verde, proceder con Tarea 1" o "audit con hits — rotación + refactor antes de proceder"

**Sin este reporte, Sprint 90 NO arranca.** Aplica DSC-G-008 v2.

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
