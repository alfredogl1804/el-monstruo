# Historial de Bugs y Fixes — ticketlike.mx

## Bug #1: Venta duplicada de asientos (CRÍTICO)

- **Fecha:** 2026-04-17
- **Síntoma:** Múltiples órdenes pagadas apuntando al mismo asiento en el mismo evento. 33 asientos con 2-4 compradores cada uno.
- **Causa raíz:** No existía UNIQUE constraint en `event_seats(eventId, seatId)`. Race condition en `confirmSeatsForOrder` permitía insertar filas duplicadas.
- **Fix:** `ALTER TABLE event_seats ADD UNIQUE KEY idx_event_seat_unique (eventId, seatId);` + eliminación de filas duplicadas.
- **Commit:** `33d2faa`
- **Invariante derivado:** NUNCA eliminar `idx_event_seat_unique`.
- **Cómo verificar:** `SELECT eventId, seatId, COUNT(*) c FROM event_seats GROUP BY eventId, seatId HAVING c > 1;` debe retornar 0 filas.

## Bug #2: VIP override visual en admin panel

- **Fecha:** 2026-04-17
- **Síntoma:** Admin panel mostraba mesas VIP vendidas como "disponibles" si no estaban llenas.
- **Causa raíz:** `getEventSeatMap()` en `seatmap-db.ts` (líneas 232-235) aplicaba regla: "si mesa VIP vendida pero no llena → mostrar como available". Admin y público usaban la misma función.
- **Fix:** Crear `getAdminEventSeatMap()` que retorna estado real sin override. Actualizar `routers.ts` y `seatmap-router.ts` para que admin use la nueva función.
- **Commit:** `33d2faa`
- **Invariante derivado:** `getAdminEventSeatMap != getEventSeatMap`. Admin siempre ve la verdad cruda.

## Bug #3: Blocked seats no protegidos en checkout

- **Fecha:** 2026-04-17
- **Síntoma:** Asientos bloqueados por Daniel podían ser comprados si alguien mandaba la request correcta a la API.
- **Causa raíz:** `confirmSeatsForOrder()` en `seatmap-db.ts` (línea 556) usaba `ne(status, "sold")` como condición, lo que incluía `blocked`.
- **Fix:** Cambiar condición a `inArray(status, ["available", "held"])`. Si el asiento es `blocked`, se registra como conflicto y se rechaza.
- **Commit:** `33d2faa`
- **Invariante derivado:** `confirmSeatsForOrder` NUNCA debe aceptar status='blocked'.

## Bug #4: Seed sobrescribe isActive en cada restart

- **Fecha:** 2026-04-18
- **Síntoma:** Evento oculto (isActive=0) reaparecía después de cada restart del servidor.
- **Causa raíz:** `seedEventsIfNeeded()` en `routers.ts` hacía `upsertEvent` con `isActive: true` para TODOS los eventos en cada startup.
- **Fix:** Cambiar seed para que solo INSERTE eventos nuevos (check si existe primero) y nunca haga UPDATE de eventos existentes.
- **Commit:** `8047b6c`
- **Invariante derivado:** Seed solo INSERTA, nunca UPDATE. Para cambiar isActive, usar admin panel o query directa.

## Bug #5: Cross-event contamination en reconciliación

- **Fecha:** 2026-04-17
- **Síntoma:** Script de reconciliación cambió orderIds de asientos en eventos 2, 3, 4, 6 (no solo evento 1).
- **Causa raíz:** Queries de UPDATE en event_seats no filtraban por eventId. Un UPDATE a "A-01" afectaba A-01 en TODOS los eventos.
- **Fix:** Agregar `WHERE eventId = X` a todas las queries. Revertir cambios incorrectos en otros eventos.
- **Invariante derivado:** TODA query a event_seats DEBE incluir `WHERE eventId = X`.

## Bug #6: Pending zombies en VIP groups

- **Fecha:** 2026-04-18 (detectado en E2E test)
- **Síntoma:** Mesas M4-04 y M4-05 muestran todos los lugares como "Ocupado" en el frontend a pesar de estar 100% disponibles en la DB.
- **Causa raíz:** Órdenes abandonadas dejaron registros `pending` en `vip_group_members`. El frontend los interpreta como lugares ocupados.
- **Fix:** Pendiente — requiere cleanup de vip_group_members con status='pending' de órdenes que nunca se completaron.
- **Estado:** ABIERTO

---

## Invariantes activos (consolidado)

1. UNIQUE `idx_event_seat_unique (eventId, seatId)` — NUNCA eliminar
2. Seed solo INSERTA, nunca UPDATE
3. `confirmSeatsForOrder` rechaza `blocked`
4. TODA query a `event_seats` incluye `WHERE eventId = X`
5. `getAdminEventSeatMap != getEventSeatMap`
6. Stripe en TEST mode
7. A-44 y B-44 con `isBookable = 0`
8. Límites de capacidad: 86/92/102/32/312
