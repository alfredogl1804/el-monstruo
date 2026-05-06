---
id: DSC-X-002
proyecto: GLOBAL
tipo: patron_replicable
titulo: "Componente compartido del Mounstro: módulo de checkout Stripe + webhook + DB confirmation. Reutilizable en LikeTickets (probado), Marketplace, CIP. Construir 1 vez, usar 3+."
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:ticketlike-ops
cruza_con: [LikeTickets, Marketplace, CIP]
---

# Componente compartido del Mounstro: módulo de checkout Stripe

## Decisión

Se establece como patrón replicable el uso de un módulo único y centralizado para el checkout de Stripe, que incluye el manejo de webhooks y la confirmación en base de datos. Este componente, ya probado exitosamente en LikeTickets, debe ser reutilizado como estándar para Marketplace y CIP. La directiva es construirlo una sola vez y consumirlo en múltiples proyectos del ecosistema.

## Por qué

Centralizar el flujo de pagos reduce la duplicación de código, minimiza la superficie de errores en transacciones financieras críticas y facilita el mantenimiento. Al haber sido validado en producción con LikeTickets, ofrece garantías de estabilidad para los demás proyectos del ecosistema.

## Implicaciones

Cualquier actualización en la API de Stripe o en la lógica de webhooks se realizará en un solo lugar, afectando positivamente a LikeTickets, Marketplace y CIP. Los nuevos proyectos deben integrarse a este módulo en lugar de crear implementaciones propias.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)