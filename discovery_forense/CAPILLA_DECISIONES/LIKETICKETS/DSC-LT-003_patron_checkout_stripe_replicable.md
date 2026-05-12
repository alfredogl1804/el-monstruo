---
id: DSC-LT-003
proyecto: LIKETICKETS
tipo: patron_replicable
titulo: "El checkout Stripe + webhook + DB confirmation de LikeTickets es plantilla replicable a Marketplace, CIP y Mundo de Tata"
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:ticketlike-ops
cruza_con: [Marketplace, CIP, Mundo de Tata]
---

# Patrón checkout Stripe replicable

## Decisión

Se establece el flujo de checkout de LikeTickets (Stripe Session -> Webhook `checkout.session.completed` -> `confirmSeatsForOrder` en DB -> Email Resend) como el patrón arquitectónico estándar y replicable para procesamiento de pagos en Marketplace, CIP y Mundo de Tata. El manejo de conflictos post-pago (marcar orden con conflicto y resolver operativamente) es parte integral del patrón.

## Por qué

El patrón ha demostrado ser robusto en LikeTickets, separando la intención de compra (hold) de la confirmación asíncrona vía webhook. Esto previene condiciones de carrera en inventarios limitados y centraliza la lógica de confirmación, asegurando que la base de datos sea la única fuente de verdad sin depender de la respuesta síncrona del cliente.

## Implicaciones

Cualquier nuevo proyecto del ecosistema (Marketplace, CIP, Mundo de Tata) que requiera procesamiento de pagos debe implementar este mismo flujo asíncrono con webhooks. No se permite confirmación síncrona post-redirección del cliente.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)