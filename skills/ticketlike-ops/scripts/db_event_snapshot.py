#!/usr/bin/env python3
"""
Snapshot completo de un evento: inventario, órdenes, revenue, anomalías.
Uso: python3 db_event_snapshot.py <eventId>
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_connect import query

if len(sys.argv) < 2:
    print("Uso: python3 db_event_snapshot.py <eventId>")
    print("Ejemplo: python3 db_event_snapshot.py 1")
    sys.exit(1)

event_id = sys.argv[1]

# Datos del evento
event = query("SELECT * FROM events WHERE id = %s", (event_id,))
if not event:
    print(f"Evento {event_id} no encontrado")
    sys.exit(1)
e = event[0]
print(f"{'=' * 60}")
print(f"SNAPSHOT: {e.get('title', 'N/A')}")
print(f"Fecha: {e.get('date', 'N/A')} | Hora: {e.get('time', 'N/A')}")
print(f"isActive: {e.get('isActive', 'N/A')}")
print(f"{'=' * 60}")

# Inventario por status
print("\n--- Inventario de asientos ---")
inv = query(
    """
    SELECT es.status, COUNT(*) as total
    FROM event_seats es WHERE es.eventId = %s
    GROUP BY es.status ORDER BY es.status
""",
    (event_id,),
)
total = 0
for row in inv:
    print(f"  {row['status']}: {row['total']}")
    total += row["total"]
print(f"  TOTAL: {total}")

# Revenue
print("\n--- Revenue ---")
rev = query(
    """
    SELECT COUNT(*) as ordenes, SUM(amountCents)/100 as revenue_mxn,
           COUNT(CASE WHEN amountCents = 0 THEN 1 END) as cortesias,
           COUNT(CASE WHEN amountCents > 0 THEN 1 END) as con_pago
    FROM ticket_orders WHERE eventId = %s AND status = 'paid'
""",
    (event_id,),
)
r = rev[0]
print(f"  Órdenes pagadas: {r['ordenes']}")
print(f"  Cortesías: {r['cortesias']}")
print(f"  Con pago: {r['con_pago']}")
print(f"  Revenue total: ${r['revenue_mxn']:,.2f} MXN")

# Desglose por tipo
print("\n--- Desglose por tipo ---")
tipos = query(
    """
    SELECT ticketType, COUNT(*) as ordenes, SUM(amountCents)/100 as mxn
    FROM ticket_orders WHERE eventId = %s AND status = 'paid'
    GROUP BY ticketType ORDER BY mxn DESC
""",
    (event_id,),
)
for t in tipos:
    print(f"  {t['ticketType']}: {t['ordenes']} órdenes → ${t['mxn']:,.2f}")

# Últimas 5 órdenes
print("\n--- Últimas 5 órdenes ---")
recent = query(
    """
    SELECT confirmationCode, customerName, ticketType, amountCents/100 as mxn, createdAt
    FROM ticket_orders WHERE eventId = %s AND status = 'paid'
    ORDER BY createdAt DESC LIMIT 5
""",
    (event_id,),
)
for o in recent:
    print(f"  {o['confirmationCode']} | {o['customerName']} | {o['ticketType']} | ${o['mxn']:,.2f} | {o['createdAt']}")

# Capacidad
print("\n--- Capacidad ---")
caps = {
    "maxButacas": e.get("maxButacas"),
    "maxMesaVip4": e.get("maxMesaVip4"),
    "maxMesaVip6": e.get("maxMesaVip6"),
    "maxSalaVip": e.get("maxSalaVip"),
    "maxGlobal": e.get("maxGlobal"),
}
sold_count = query("SELECT COUNT(*) as n FROM event_seats WHERE eventId = %s AND status = 'sold'", (event_id,))
sold = sold_count[0]["n"]
max_g = caps.get("maxGlobal") or 312
print(f"  Vendidos: {sold} / {max_g} (global)")
for k, v in caps.items():
    if v is not None:
        print(f"  {k}: {v}")

print(f"\n{'=' * 60}")
print("Snapshot completado.")
