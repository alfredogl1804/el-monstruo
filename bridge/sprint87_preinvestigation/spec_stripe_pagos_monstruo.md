# Sprint 87 — Stripe Pagos del Monstruo · Pre-investigación

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-04
> **Estado:** Pre-investigación arquitectónica · pendiente de aprobación de Alfredo

---

## Contexto

Cuando Sprint 85 (Critic Visual + Product Architect) cierre, El Monstruo va a poder generar sitios y backends comercializables. Pero NO los puede MONETIZAR sin pagos. Sprint 87 cierra la brecha: capacidad de cobrar a clientes empresa/individuo por productos digitales generados por el Monstruo.

**Diferencia con ticketlike.mx:**
- **ticketlike.mx:** boletera de Leones de Yucatán. Cobra a fans por boletos. Cuenta merchant `51TJwea`. Cuenta operativa de Alfredo como producto separado.
- **Pagos del Monstruo (este Sprint):** El Monstruo cobra a clientes (empresas o individuos) que compran servicios de generación de productos digitales (landings, backends, mobile apps). Cierra Objetivo #8 — Monetización desde día 1.

## Hallazgo magna del 2026 que simplifica el Sprint

**Stripe partnered oficialmente con Facturapi en 2026.** Plugin oficial en Stripe Marketplace genera CFDIs automáticos sin código de integración manual. Activar con un click en el dashboard.

Esto elimina ~30% del trabajo de implementación que originalmente requería webhook custom → Facturapi API. Ahora el flujo es:

```
Cliente paga → Stripe procesa → Stripe webhook → Plugin Facturapi (no-code) → CFDI emitido + email al cliente
```

**Implicación:** Sprint 87 se enfoca en la capa de aplicación del Monstruo (productos, portal cliente, webhooks de negocio), no en la integración fiscal.

## Decisiones arquitectónicas firmes

### Decisión 1 — Stripe estándar, NO Stripe Connect

**Voto Cowork:** Stripe estándar, una sola merchant account.

Razones:
- El Monstruo es un solo SaaS de Alfredo. NO es marketplace multi-merchant.
- Stripe Connect agrega complejidad enorme (Connect Accounts, transferencias, payouts a terceros). Innecesario para el caso actual.
- Si en el futuro el Monstruo se vuelve marketplace donde otros operadores monetizan via tu plataforma, migrar a Connect — pero eso es Sprint 100+.

### Decisión 2 — ¿Misma cuenta Stripe que ticketlike o cuenta separada?

**Voto Cowork:** **Cuenta Stripe SEPARADA del Monstruo.**

Razones a favor de cuenta nueva:
- **Soberanía operativa:** ticketlike y el Monstruo son negocios distintos con clientes distintos. Mezclar billing complica reporting fiscal y dashboard.
- **Blast radius reducido:** si el Monstruo es compromised (algún cliente abusa, dispute mass), ticketlike NO se ve afectado y viceversa.
- **Categorías fiscales distintas:** boletería de eventos vs servicios de software pueden tener regímenes SAT distintos. Separar facilita el accounting.
- **Pricing strategy distinto:** ticketlike puede tener fees de boleto, el Monstruo puede tener subscriptions / one-time / freemium. Mezclados confunden análisis.

Razones a favor de misma cuenta:
- Una sola integración Facturapi
- Un solo dashboard que monitorear
- Menos credenciales que rotar trimestralmente

**Decisión final:** cuenta separada justifica la complejidad operativa adicional. Dos cuentas Stripe ≠ deuda magna.

### Decisión 3 — API principal: Checkout Sessions vs Payment Intents

**Voto Cowork:** **Checkout Sessions** como API principal. Payment Intents como API low-level si caso especial.

Razones:
- **UI hosted por Stripe:** menos código del Monstruo a mantener
- **Mobile-friendly:** Stripe optimiza el flow para móviles
- **Más rápido de implementar:** ~80% menos código que custom checkout
- **PCI compliance automático:** Stripe maneja tarjetas, el Monstruo nunca toca números de tarjeta
- **Apple Pay / Google Pay nativo:** sin trabajo adicional

Excepción: si en el futuro Sprint 90+ el Monstruo necesita custom UI 3D Secure manejada en su frontend (raro), Payment Intents.

### Decisión 4 — Restricted keys con scope mínimo

**Misma política del Sprint 84.X:**
- `rk_live_monstruo_main` con scope: Checkout Sessions write, Customers write, Payment Intents write, Subscriptions write, Invoices read, Refunds read, Webhooks read
- `rk_live_monstruo_admin` con scope ampliado: Customers admin, Refunds write — solo para operaciones manuales del dashboard
- Webhook signing secret separado (`whsec_*`)

### Decisión 5 — Productos: Catálogo dinámico vs hardcoded

**Voto Cowork:** **Catálogo dinámico en Supabase** con sync a Stripe Products + Prices.

Razones:
- El Monstruo va a generar productos a velocidad (cada landing/backend/app es un producto)
- Hardcoded `PRODUCT_ID_LANDING_BASIC` en código no escala
- Tabla `monstruo_products` en Supabase con productos + precios + descripciones
- Sync bidireccional: cuando se crea producto en Monstruo, se replica en Stripe via API

## Stack técnico

| Componente | Stack |
|---|---|
| Backend del Monstruo | Python/FastAPI + módulo nuevo `kernel/payments/` |
| Cliente Stripe | `stripe` npm/pip oficial (mismo que ticketlike usa: stripe-python) |
| API version pinned | `2026-03-25.dahlia` (igual que ticketlike — consistencia) |
| Webhook signature verification | `stripe.webhooks.construct_event()` con `STRIPE_WEBHOOK_SECRET` |
| Productos catálogo | Tabla nueva `monstruo_products` en Supabase |
| Customers | Tabla nueva `monstruo_customers` en Supabase + Stripe Customer ID FK |
| Orders / Subscriptions | Tablas nuevas `monstruo_orders` y `monstruo_subscriptions` |
| Frontend portal cliente | Reuso del Command Center (Next.js) — agregar sección "Mis productos / Mis facturas / Datos fiscales" |
| CFDI emission | Plugin oficial Stripe + Facturapi (no-code) |
| Métodos de pago | Tarjeta, OXXO, SPEI (via Stripe Mexico nativo) |

## Bloques de implementación

### Bloque 1 — Setup cuenta Stripe del Monstruo

1. Alfredo crea cuenta Stripe nueva con email del Monstruo (no `alfredogl1@hivecom.mx` que es ticketlike — usar email distinto tipo `monstruo@elmonstruo.dev`)
2. Activar live mode después de KYC
3. Configurar Mexico como país base + MXN como currency principal (aceptar USD como secondary)
4. Activar OXXO y SPEI como métodos de pago
5. Activar plugin Facturapi en Stripe Marketplace
6. Configurar Facturapi con datos fiscales del Monstruo (RFC del emisor, régimen, certificados CSD)

### Bloque 2 — Schema Supabase del Monstruo (migration `017_sprint87_payments.sql`)

```sql
CREATE TABLE monstruo_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    type TEXT CHECK (type IN ('landing', 'backend', 'webapp', 'mobile_app', 'subscription_service', 'consulting')),
    price_mxn_cents INTEGER NOT NULL,
    price_usd_cents INTEGER,
    stripe_product_id TEXT UNIQUE,
    stripe_price_id_mxn TEXT,
    stripe_price_id_usd TEXT,
    is_recurring BOOLEAN DEFAULT FALSE,
    interval TEXT CHECK (interval IN ('day','week','month','year') OR interval IS NULL),
    metadata JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE monstruo_customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stripe_customer_id TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    name TEXT,
    rfc TEXT,
    razon_social TEXT,
    regimen_fiscal TEXT,
    uso_cfdi TEXT DEFAULT 'G03',
    cp_fiscal TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE monstruo_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES monstruo_customers(id),
    stripe_session_id TEXT UNIQUE,
    stripe_payment_intent_id TEXT,
    product_id UUID REFERENCES monstruo_products(id),
    deployment_id UUID,
    amount_cents INTEGER NOT NULL,
    currency TEXT NOT NULL CHECK (currency IN ('mxn','usd')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending','paid','failed','refunded','cancelled')),
    cfdi_uuid TEXT,
    cfdi_pdf_url TEXT,
    cfdi_xml_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE monstruo_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES monstruo_customers(id),
    stripe_subscription_id TEXT UNIQUE NOT NULL,
    product_id UUID REFERENCES monstruo_products(id),
    status TEXT NOT NULL,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_monstruo_orders_status ON monstruo_orders(status);
CREATE INDEX idx_monstruo_orders_customer ON monstruo_orders(customer_id);
CREATE INDEX idx_monstruo_orders_deployment ON monstruo_orders(deployment_id);
CREATE INDEX idx_monstruo_subs_status ON monstruo_subscriptions(status);
```

### Bloque 3 — Módulo `kernel/payments/`

```
kernel/payments/
├── __init__.py
├── stripe_client.py          # Wrapper Stripe SDK con env vars dinámicas
├── checkout_service.py       # Lógica de Checkout Sessions
├── customer_service.py       # CRUD customers + datos fiscales
├── product_catalog.py        # CRUD productos + sync a Stripe
├── webhook_handler.py        # Handler de eventos Stripe
└── routes.py                 # FastAPI router /v1/payments/*
```

Endpoints expuestos:
- `POST /v1/payments/checkout` — crear Checkout Session, retorna URL de Stripe
- `POST /v1/payments/webhook` — recibir eventos de Stripe (signature verified)
- `GET /v1/payments/orders/{id}` — consultar estado de orden
- `POST /v1/payments/customers` — crear/actualizar customer con datos fiscales
- `GET /v1/payments/customers/{id}/invoices` — listar facturas del cliente
- `POST /v1/payments/products` — admin: crear producto en catálogo
- `GET /v1/payments/products` — público: listar productos activos

### Bloque 4 — Webhook handler

Eventos críticos:
- `checkout.session.completed` → Crear orden + asociar a deployment + trigger Facturapi (automático via plugin)
- `payment_intent.succeeded` → Confirmar pago
- `customer.subscription.created/updated/deleted` → Actualizar `monstruo_subscriptions`
- `invoice.payment_failed` → Alerta a Alfredo + email a cliente con link de retry
- `charge.refunded` → Actualizar status de orden + reversa CFDI vía Facturapi

Patrón de handler **igual al de ticketlike** (ya validado en producción):
- Idempotencia por `stripe_session_id`
- Verificación de signature antes de procesar
- Rechazo de test events en production
- Logging estructurado con `structlog`
- Procesamiento async non-blocking de side effects (email, alertas)

### Bloque 5 — Portal cliente (Command Center extension)

Sección nueva en el Command Center existente (Next.js):

**Vistas:**
- `/account/products` — productos comprados por el cliente
- `/account/invoices` — facturas CFDI con descarga PDF/XML
- `/account/fiscal-data` — formulario de datos fiscales (RFC, razón social, régimen, uso CFDI, CP)
- `/account/subscriptions` — gestión de suscripciones (cancelar, upgrade, etc.)

**Validaciones de datos fiscales:**
- RFC validado contra regex SAT (RFC personas físicas: 13 chars, morales: 12 chars)
- Régimen fiscal: dropdown con catálogo SAT actualizado (601, 603, 612, 626, etc.)
- Uso CFDI: dropdown con catálogo SAT (G01, G03, P01, etc.)
- Validación opcional contra API SAT (si Facturapi expone — verificar)

### Bloque 6 — Tests

- **Test 1 — Checkout one-time:** crear sesión, mock card, verificar webhook llega, orden marca paid, CFDI emitido por Facturapi
- **Test 2 — Subscription:** crear sub mensual, mock card, verificar primer cobro, verificar renewal después de 30 días (Stripe test clock)
- **Test 3 — Refund:** ejecutar refund desde dashboard, verificar webhook actualiza orden, CFDI reversado
- **Test 4 — OXXO:** crear sesión OXXO, simular pago en Stripe test mode, verificar `async_payment_succeeded` webhook actualiza orden
- **Test 5 — Datos fiscales mal:** customer sin RFC válido, verificar fallback a "Público en general" + warning visible
- **Test 6 — Subscription cancellation:** customer cancela, verificar `cancel_at_period_end=true`, verificar acceso continúa hasta fin del periodo

## Pre-requisitos antes de arrancar Sprint 87

| # | Pre-requisito | Owner |
|---|---|---|
| 1 | Sprint 85 cerrado verde con Critic Visual generando sitios comercializables | Hilo Catastro |
| 2 | Sprint 86 (Catastro) cerrado o avanzado a Bloque 4+ | Hilo Catastro |
| 3 | Sprint 84.7 cerrado (refactor substring matching) | Hilo Ejecutor |
| 4 | Cuenta Stripe nueva del Monstruo creada y verificada KYC live mode | Alfredo |
| 5 | Plugin Facturapi activado en Stripe Marketplace + datos fiscales del Monstruo configurados (RFC emisor, certificados CSD, etc.) | Alfredo |
| 6 | Restricted keys del Monstruo en Bitwarden + Railway env vars (`STRIPE_SECRET_KEY_MONSTRUO`, `STRIPE_WEBHOOK_SECRET_MONSTRUO`) | Hilo Ejecutor (rotación coordinada) |
| 7 | Decisión de Alfredo sobre primer catálogo de productos (qué cobrar, a cuánto, mensualidad o one-time) | Alfredo |
| 8 | Migración SQL aprobada por Cowork antes de aplicar a producción | Cowork audit |

## Hard limits Sprint 87

- **5-7 días calendar** total
- Si Bloque 1 (setup Stripe + Facturapi) excede 1 día por trámites SAT/KYC, parar y reportar — no es trabajo del Hilo Ejecutor sino de Alfredo
- Bloque 5 (portal cliente Next.js) puede diferirse a Sprint 87.5 si tiempo apremia — el portal mínimo viable es enviar emails con links a Stripe Customer Portal nativo

## Open questions (verificar al arrancar Sprint 87)

1. ¿Plugin Facturapi para Stripe es gratuito o tiene fee mensual? Verificar pricing actual en facturapi.io
2. ¿Stripe Mexico permite OXXO + SPEI con restricted keys o requiere full secret keys?
3. ¿Hay límite de productos en Stripe sin tier business? Verificar
4. ¿API SAT pública para validación de RFC sigue activa en 2026? Si no, Facturapi tiene su propio validador
5. ¿Algún cambio relevante en CFDI 4.0 → 4.1 o 5.0 que el Monstruo tenga que adoptar?

## Decisiones que necesito firmadas por Alfredo antes de spec definitivo

1. **Cuenta Stripe separada vs misma de ticketlike** — mi voto firme es separada
2. **Pricing inicial del catálogo** — necesito 3-5 productos con precios en MXN para arrancar Bloque 2 con seed real
3. **Email del Monstruo para cuenta Stripe** — `monstruo@elmonstruo.dev`? `alfredo+monstruo@hivecom.mx`?
4. **Currency principal** — MXN único o MXN + USD?
5. **Subscriptions vs one-time vs ambas** — qué modelo de monetización primero

---

> **Estado:** pre-investigación lista. Cuando los pre-requisitos cumplan + Alfredo firme las 5 decisiones, Cowork emite SPEC SPRINT 87 v1 final con todos los detalles para que el Hilo Ejecutor (o el hilo asignado) arranque.

— Cowork
