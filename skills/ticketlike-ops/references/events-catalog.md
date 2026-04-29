# Catálogo de Eventos — ticketlike.mx

Última actualización: 2026-04-18

## Eventos activos

| eventId | Título | Fecha | Hora | isActive | Ventas (pagadas) | Revenue |
|---------|--------|-------|------|----------|-------------------|---------|
| 1 | J1 BRAVOS VS LEONES | 2026-04-17 | 20:00 | **0 (oculto)** | 104 órdenes | $80,375 |
| 2 | J2 BRAVOS VS LEONES | 2026-04-18 | 20:00 | 1 | 16 órdenes | $15,000 |
| 3 | J3 BRAVOS VS LEONES | 2026-04-19 | 18:00 | 1 | 5 órdenes | $2,660 |
| 4 | J1 DIABLOS VS LEONES | 2026-04-21 | 20:00 | 1 | 1 orden | $2,000 |
| 5 | J2 DIABLOS VS LEONES | 2026-04-22 | 20:00 | 1 | 0 | $0 |
| 6 | J3 DIABLOS VS LEONES | 2026-04-23 | 20:00 | 1 | 2 órdenes | $5,000 |
| 7 | J1 ÁGUILAS VS LEONES | 2026-04-24 | 20:00 | 1 | 0 | $0 |
| 8 | J2 ÁGUILAS VS LEONES | 2026-04-25 | 20:00 | 1 | 0 | $0 |

**Total acumulado:** $105,035 MXN (128 órdenes pagadas)

## Notas

- J1 Bravos vs Leones fue el primer evento vendido. Tuvo el problema de ventas duplicadas (Bug #1). Fue ocultado de la página pública después del evento.
- Los eventIds son strings (UUIDs internos), pero en la DB actual se usan como enteros secuenciales (1-8) para esta temporada.
- Cada evento comparte el mismo layout de 136 ubicaciones.
- Los límites de capacidad (maxButacas, maxGlobal, etc.) se configuraron el 2026-04-18 y aplican a todos los eventos.

## Query para actualizar este catálogo

```sql
SELECT e.id, e.title, e.date, e.time, e.isActive,
       COUNT(CASE WHEN o.status = 'paid' THEN 1 END) as ordenes_pagadas,
       COALESCE(SUM(CASE WHEN o.status = 'paid' THEN o.amountCents END), 0)/100 as revenue_mxn
FROM events e
LEFT JOIN ticket_orders o ON e.id = o.eventId
GROUP BY e.id
ORDER BY e.date;
```
