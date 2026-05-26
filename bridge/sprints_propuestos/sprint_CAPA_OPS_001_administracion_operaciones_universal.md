<!-- lint_strict -->
# Sprint CAPA-OPS-001 — Administración y Operaciones Universal

**Estado:** Propuesto — Canonizado sin ejecutar
**Hilo:** TBD
**ETA:** estimación pendiente
**Objetivo Maestro:** #9 (Transversalidad Universal — Capa 5) + #1 (Crear Empresas Digitales Completas)
**Capa Transversal:** C5 Administración y Operaciones
**Bloqueos:** ninguno técnico
**Resultado esperado:** Cada empresa hija opera con procesos automatizados desde día 1: customer support, inventory, compliance, fulfillment.

---

## 0. Procedencia

OM-09 v3.0 línea 458-462:

> **CAPA 5 — Administración y Operaciones:**
> - Procesos operativos automatizados desde día 1
> - Customer support inteligente
> - Inventory management
> - Legal compliance automático

Auditoría 2026-05-26: 0 sprints en backlog cubren C5.

---

## 1. Audit pre-sprint

Lo que existe:
- Webdev template con DB + auth + storage
- WhatsApp Gateway P0 (canonizado, no ejecutado) — base para support
- Stripe MCP, PayPal MCP — integraciones de pago disponibles

Lo que falta:
- Capability `customer_support` end-to-end
- Inventory tracking si el negocio es físico o tiene SKUs
- Legal compliance automático (privacy policy, terms, cookie banners, GDPR/LGPD)
- Order fulfillment workflow

---

## 2. Tareas (MVP)

### MVP-1: Customer support tier 1 automático
- Bot conversacional sobre WhatsApp + email + web chat
- KB construida automáticamente desde docs del proyecto
- Escalation a humano si confidence < 0.6 o detecta enojo
- SLA tracking: tiempo primera respuesta, tiempo resolución

### MVP-2: Inventory management
- Schema `inventory_items`, `stock_movements`, `stock_alerts`
- Hooks: cuando stock < threshold, alerta + propone reorder
- Multi-warehouse support
- Sync bidireccional con plataformas e-commerce (Shopify, WooCommerce, MercadoLibre)

### MVP-3: Legal compliance auto
- Generador de privacy policy, terms of service, cookie policy basado en jurisdicción
- Cookie banner automático con consent management
- GDPR/LGPD/CCPA compliance toggle por geo
- Audit trail de consents

### MVP-4: Order fulfillment
- Workflow: order received → payment confirmed → fulfillment triggered → tracking → delivered
- Integración con shipping APIs (DHL, FedEx, locales LATAM como Estafeta/Correios)
- Customer notifications automáticas en cada step
- Returns workflow

### MVP-5: Reporting operacional
- Dashboard `monstruo/dashboards/ops/` con KPIs: response time, resolution rate, NPS, inventory turnover, fulfillment time
- Alertas proactivas

### MVP-6: Integration con otras capas
- Customer issues → señal a CAPA_TENDENCIAS para detectar patterns
- Compliance updates → trigger automático de re-deploy de policies
- Inventory low → CAPA_VENTAS pausa promociones de ese SKU

---

## 3. Dependencias

- `WHATSAPP_GATEWAY_P0` para canal de support
- `MOBILE_0_SMP` para guardar credenciales de plataformas (Shopify, shipping)
- `CAPA_VENTAS_001` para coordinar pricing con stock
- Stripe/PayPal MCPs ya disponibles

---

## 4. Criterios de Cierre y Métricas de Éxito

- Tiempo primera respuesta support ≤ 5 minutos (24/7)
- Resolution rate tier-1 sin escalation ≥ 70%
- Inventory accuracy ≥ 99%
- Compliance audit pass rate 100%

---

## 5. Anti-doctrina

- NO automatizar 100% de support (escala emocional necesita humano)
- NO acoplar a una sola plataforma e-commerce
- NO operar legal compliance sin firma de abogado humano en el primer setup
- NO procesar PII sin encryption at rest + in transit

---

## 6. Notas de canonización

Sprint canonizado sin ejecutar. Auto-promote al detectar commits en `kernel/operations/`.

Firmado: **Manus B — 2026-05-26**
