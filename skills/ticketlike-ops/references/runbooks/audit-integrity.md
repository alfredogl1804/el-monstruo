# Runbook: Auditar integridad de la DB

## Auditoría rápida (1 comando)

```bash
python3 /home/ubuntu/skills/ticketlike-ops/scripts/db_audit_integrity.py
```

Ejecuta 8 capas de validación sobre toda la DB. Exit code 0 = todo OK.

## Las 8 capas

1. **Unique constraint:** Verifica que no hay duplicados en `(eventId, seatId)`
2. **Forward check:** Cada `event_seats.status='sold'` tiene un orderId válido con `ticket_orders.status='paid'`
3. **Reverse check:** Cada `ticket_orders.status='paid'` tiene sus asientos marcados como `sold`
4. **Cross-event check:** Ningún orderId apunta a un evento diferente al del asiento
5. **Ghost check:** No hay asientos pagados pero no marcados como sold
6. **Orphan check:** No hay asientos sold sin orden real
7. **Status consistency:** No hay asientos `available` o `blocked` con orderId residual
8. **Capacity check:** Ningún evento excede sus límites de capacidad

## Auditoría manual (queries individuales)

Duplicados:
```sql
SELECT eventId, seatId, COUNT(*) c FROM event_seats GROUP BY eventId, seatId HAVING c > 1;
```

Ghosts (pagados pero no sold):
```sql
SELECT o.id, o.customerName, s.label FROM ticket_orders o
JOIN event_seats es ON es.orderId = o.id
JOIN seats s ON es.seatId = s.id
WHERE o.status = 'paid' AND es.status != 'sold';
```

Cross-event:
```sql
SELECT es.eventId as seat_event, o.eventId as order_event, s.label
FROM event_seats es
JOIN ticket_orders o ON es.orderId = o.id
JOIN seats s ON es.seatId = s.id
WHERE es.eventId != o.eventId;
```

## Qué hacer si la auditoría falla

1. NO hacer cambios masivos sin filtrar por eventId
2. Identificar las filas problemáticas con las queries manuales
3. Verificar en el admin panel si Daniel hizo cambios manuales
4. Documentar el hallazgo en `references/bug-history.md`
5. Aplicar fix quirúrgico (fila por fila si es necesario)
