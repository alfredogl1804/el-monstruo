# Runbook: Respuesta a incidentes

## Triage rápido

1. ¿El sitio responde? `curl -s -o /dev/null -w "%{http_code}" https://ticketlike.mx/`
2. ¿Railway está healthy? `python3 scripts/railway_status.py`
3. ¿La DB responde? `python3 scripts/db_connect.py`
4. ¿Hay errores de integridad? `python3 scripts/db_audit_integrity.py`

## Escenarios comunes

### Sitio no carga (HTTP 5xx o timeout)
1. Verificar Railway status
2. Revisar logs: `python3 scripts/railway_status.py` (incluye últimos deploys)
3. Si el último deploy falló: hacer rollback al anterior
4. Si el servicio está down: verificar que no se excedieron los límites de Railway

### Asientos vendidos a múltiples personas
1. Verificar que UNIQUE constraint existe: `SHOW INDEX FROM event_seats WHERE Key_name = 'idx_event_seat_unique';`
2. Si no existe: INCIDENTE CRÍTICO. Aplicar inmediatamente.
3. Ejecutar auditoría de integridad
4. Generar lista de conflictos para taquilla

### Daniel reporta que mesas se desbloquean solas
1. Verificar en DB: `SELECT status FROM event_seats WHERE eventId = 'X' AND seatId = 'Y';`
2. Si está blocked en DB pero Daniel lo ve diferente: es el VIP override visual (Bug #2)
3. Verificar que el deploy actual incluye `getAdminEventSeatMap`
4. Si el seed sobrescribió isActive: es Bug #4 — verificar que el fix del seed está deployado

### Evento oculto reaparece
1. Verificar isActive: `SELECT id, title, isActive FROM events WHERE id = 'X';`
2. Si isActive = 1 y debería ser 0: el seed lo sobrescribió (Bug #4)
3. Fix: `UPDATE events SET isActive = 0 WHERE id = 'X';`
4. Verificar que el fix del seed está deployado (commit `8047b6c`)

## Contacto de emergencia

- Alfredo: decisiones de negocio y acceso a Railway
- Daniel: operaciones en sitio, admin panel
