# Tareas pendientes — ticketlike.mx

## P0 (Urgente)

| # | Tarea | Contexto |
|---|-------|----------|
| 1 | Limpiar pending zombies en vip_group_members | Bug #6. M4-04 y M4-05 muestran "Ocupado" en frontend. Limpiar registros pending de órdenes abandonadas. |
| 2 | Agregar seatLabels al PDF descargable del boleto | Solo se agregó al email. El PDF en `generateTicketImage.ts` no muestra número de asiento. |

## P1 (Importante, no urgente)

| # | Tarea | Contexto |
|---|-------|----------|
| 3 | Guest checkout (compra sin registro) | Roadmap original del proyecto. Reducir fricción de compra. |
| 4 | Sticky summary en mobile | El resumen de compra no es visible al scrollear en móvil. |
| 5 | Migrar Stripe a modo LIVE | Cuando se decida ir a producción real con pagos reales. |

## P2 (Nice to have)

| # | Tarea | Contexto |
|---|-------|----------|
| 6 | Cleanup de held seats expirados (cron job) | Actualmente los holds expirados se limpian solo cuando alguien consulta el mapa. Un cron sería más robusto. |
| 7 | Dashboard de analytics para Daniel | Revenue en tiempo real, ocupación por evento, tendencias de venta. |
| 8 | Cupones/códigos de descuento | Tablas coupons/coupon_usage ya existen en el schema pero no están implementadas en el frontend. |
