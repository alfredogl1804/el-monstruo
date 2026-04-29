# Schema TiDB — ticketlike

## events

Un evento = un partido. Actualmente 8 eventos.

| Columna | Tipo | Notas |
|---------|------|-------|
| id | VARCHAR(36) PK | UUID |
| title | VARCHAR | "J1 BRAVOS VS LEONES" |
| date | DATE | |
| time | TIME | |
| location | VARCHAR | "Estadio Kukulkán Alamo" |
| isActive | BOOLEAN | Controla visibilidad pública. Seed NO sobrescribe (Bug #4) |
| maxBleachers | INT | Límite bleachers por evento |
| maxVip | INT | Límite VIP genérico |
| maxButacas | INT | Límite butacas (86) |
| maxMesaVip4 | INT | Límite personas en mesas VIP 4 (92) |
| maxMesaVip6 | INT | Límite personas en mesas VIP 6 (102) |
| maxSalaVip | INT | Límite personas en salas VIP (32) |
| maxGlobal | INT | Límite total (312) |
| layoutId | VARCHAR | FK a layout de asientos |
| createdAt | TIMESTAMP | |

Query útil: `SELECT id, title, date, isActive FROM events ORDER BY date;`

## seats

Catálogo maestro de ubicaciones físicas. NO cambia por evento.

| Columna | Tipo | Notas |
|---------|------|-------|
| id | VARCHAR(36) PK | UUID |
| label | VARCHAR | "A-01", "M4-01", "M6-01", "S-01" |
| section | VARCHAR | "Butaca", "Mesa VIP 4", "Mesa VIP 6", "Sala VIP" |
| row | VARCHAR | "A", "B", "M4", "M6", "S" |
| seatNumber | INT | Número dentro de la fila |
| isBookable | BOOLEAN | A-44 y B-44 tienen `isBookable = 0` |
| capacity | INT | Personas por ubicación (1 para butacas, 4/6 para mesas) |
| layoutId | VARCHAR | FK a layout |

Prefijos de label: `A-` = fila A butacas, `B-` = fila B butacas, `M4-` = mesa VIP 4, `M6-` = mesa VIP 6, `S-` = sala VIP

## event_seats (TABLA MÁS CRÍTICA)

Estado POR EVENTO de cada asiento. Cada fila = un asiento en un evento específico.

| Columna | Tipo | Notas |
|---------|------|-------|
| id | VARCHAR(36) PK | UUID |
| eventId | VARCHAR(36) FK | **SIEMPRE filtrar por esto** |
| seatId | VARCHAR(36) FK | FK a seats.id |
| status | ENUM | `available`, `blocked`, `sold`, `held` |
| orderId | VARCHAR(36) FK | FK a ticket_orders.id (NULL si available/blocked sin orden) |
| heldUntil | TIMESTAMP | Expiración del hold |
| heldBySession | VARCHAR | Session ID del cliente que holdea |

**UNIQUE KEY:** `idx_event_seat_unique (eventId, seatId)` — Bug #1 fix. NUNCA eliminar.

**Transiciones válidas:**
```
available → held (cliente selecciona)
held → sold (pago confirmado)
held → available (timeout heldUntil)
available → blocked (admin)
blocked → available (admin)
```

**Anti-patrones:**
- NUNCA consultar sin `WHERE eventId = X` — causa contaminación cross-event
- NUNCA asumir que orderId es NULL en blocked — Daniel bloquea mesas que ya tenían orden
- confirmSeatsForOrder RECHAZA status='blocked' — no relajar

## ticket_orders

| Columna | Tipo | Notas |
|---------|------|-------|
| id | VARCHAR(36) PK | UUID |
| eventId | VARCHAR(36) FK | |
| status | ENUM | `pending`, `paid`, `refunded`, `conflict` |
| customerName | VARCHAR | |
| customerEmail | VARCHAR | |
| customerPhone | VARCHAR | |
| ticketType | VARCHAR | "Butaca", "Mesa VIP 4", "Mesa VIP 6", "Sala VIP", "VIP", "Lugar VIP", "Bleachers" |
| quantity | INT | Número de asientos en la orden |
| amountCents | INT | **EN CENTAVOS**. Dividir /100 para MXN. Cortesías = 0 |
| stripeSessionId | VARCHAR | ID de sesión de Stripe Checkout |
| confirmationCode | VARCHAR | "LIKE-XXXX-XXXX" |
| createdAt | TIMESTAMP | Fecha de creación |

Query de revenue: `SELECT SUM(amountCents)/100 FROM ticket_orders WHERE eventId = 'X' AND status = 'paid';`

## vip_group_members

Lugares individuales dentro de mesas VIP compartidas.

| Columna | Tipo | Notas |
|---------|------|-------|
| id | VARCHAR(36) PK | |
| eventId | VARCHAR(36) FK | |
| seatId | VARCHAR(36) FK | FK a seats.id (la mesa) |
| orderId | VARCHAR(36) FK | FK a ticket_orders.id |
| place | INT | Número de lugar (1-4 o 1-6) |
| status | ENUM | `pending`, `confirmed`, `cancelled` |

## customers

| Columna | Tipo | Notas |
|---------|------|-------|
| id | VARCHAR(36) PK | |
| name | VARCHAR | |
| email | VARCHAR | |
| phone | VARCHAR | |

## coupons / coupon_usage

Tablas de cupones de descuento. Estructura estándar.

## Relaciones

```
events 1——N event_seats N——1 seats
events 1——N ticket_orders
ticket_orders 1——N vip_group_members N——1 seats
events 1——N vip_group_members
```

## Joins típicos

Asientos vendidos con datos del cliente:
```sql
SELECT es.status, s.label, s.section, o.customerName, o.customerEmail, o.amountCents/100 as mxn
FROM event_seats es
JOIN seats s ON es.seatId = s.id
LEFT JOIN ticket_orders o ON es.orderId = o.id
WHERE es.eventId = 'X' AND es.status = 'sold'
ORDER BY s.label;
```

Resumen de inventario por evento:
```sql
SELECT es.status, COUNT(*) as total
FROM event_seats es
WHERE es.eventId = 'X'
GROUP BY es.status;
```
