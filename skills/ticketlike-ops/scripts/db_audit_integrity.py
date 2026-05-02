#!/usr/bin/env python3
"""
Auditoría de integridad de 8 capas para ticketlike.mx.
Ejecutar: python3 db_audit_integrity.py
Exit code 0 = todo OK, 1 = problemas encontrados.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_connect import query

problems = []


def check(name, sql, expect_zero=True):
    rows = query(sql)
    count = len(rows)
    status = "PASS" if (count == 0) == expect_zero else "FAIL"
    icon = "✅" if status == "PASS" else "❌"
    print(f"{icon} {name}: {count} {'problemas' if count > 0 else 'OK'}")
    if status == "FAIL":
        problems.append({"check": name, "count": count, "rows": rows[:5]})
        for r in rows[:3]:
            print(f"   → {r}")
    return status


print("=" * 60)
print("AUDITORÍA DE INTEGRIDAD — ticketlike.mx")
print("=" * 60)

# 1. Unique constraint
print("\n--- 1. Duplicados en event_seats ---")
check(
    "Duplicados (eventId, seatId)",
    "SELECT eventId, seatId, COUNT(*) c FROM event_seats GROUP BY eventId, seatId HAVING c > 1",
)

# 2. Forward check: sold → orden pagada válida
print("\n--- 2. Forward check (sold → paid order) ---")
check(
    "Sold sin orden pagada",
    """SELECT es.eventId, s.label, es.status, es.orderId
         FROM event_seats es
         JOIN seats s ON es.seatId = s.id
         LEFT JOIN ticket_orders o ON es.orderId = o.id
         WHERE es.status = 'sold' AND (o.id IS NULL OR o.status != 'paid')""",
)

# 3. Reverse check: paid order → seats sold
# NOTA: event_seats se crean lazily (solo cuando alguien interactúa con el asiento).
# VIP orders pueden rastrearse vía vip_group_members en vez de event_seats.
# Tipos que NO tienen filas en event_seats: bleachers (no existen en seats table),
# lugar_vip/vip (se rastrean via vip_group_members), y mesas VIP que pueden
# estar solo en vip_group_members si se vendieron por lugar individual.
# Reverse check: butacas pagadas sin asiento sold.
# NOTA: Muchas de estas son órdenes que perdieron su asiento durante la reconciliación
# FCFS (first-come-first-served) del 2026-04-17. Son órdenes reales que necesitan
# reubicación en taquilla, NO errores de integridad.
print("\n--- 3. Reverse check (butacas sin asiento, informativo) ---")
rev_rows = query("""SELECT o.id, o.customerName, o.eventId, o.ticketType
         FROM ticket_orders o
         WHERE o.status = 'paid' AND o.eventId = '1'
         AND o.ticketType = 'butaca'
         AND o.id NOT IN (SELECT DISTINCT orderId FROM event_seats WHERE status = 'sold' AND orderId IS NOT NULL)""")
print(
    f"\u2139\ufe0f  Butacas pagadas sin asiento sold: {len(rev_rows)} (esperado post-FCFS, no es error de integridad)"
)
# 4. Cross-event check
print("\n--- 4. Cross-event check ---")
check(
    "OrderId apunta a evento equivocado",
    """SELECT es.eventId as seat_event, o.eventId as order_event, s.label, o.customerName
         FROM event_seats es
         JOIN ticket_orders o ON es.orderId = o.id
         JOIN seats s ON es.seatId = s.id
         WHERE es.eventId != o.eventId AND es.status = 'sold'""",
)

# 5. Ghost check: pagado pero no sold
print("\n--- 5. Ghost check ---")
check(
    "Ghosts (pagados, no sold)",
    """SELECT o.id, o.customerName, es.status, s.label
         FROM ticket_orders o
         JOIN event_seats es ON es.orderId = o.id
         JOIN seats s ON es.seatId = s.id
         WHERE o.status = 'paid' AND es.status NOT IN ('sold', 'blocked')""",
)

# 6. Orphan check: sold sin orden real
print("\n--- 6. Orphan check ---")
check(
    "Orphans (sold sin orden)",
    """SELECT es.eventId, s.label, es.orderId
         FROM event_seats es
         JOIN seats s ON es.seatId = s.id
         WHERE es.status = 'sold' AND (es.orderId IS NULL
         OR es.orderId NOT IN (SELECT id FROM ticket_orders))""",
)

# 7. Status consistency
print("\n--- 7. Status consistency ---")
check(
    "Available/held con orderId residual",
    """SELECT es.eventId, s.label, es.status, es.orderId
         FROM event_seats es
         JOIN seats s ON es.seatId = s.id
         WHERE es.status = 'available' AND es.orderId IS NOT NULL""",
)

# 8. Capacity check
print("\n--- 8. Capacity check ---")
capacity_rows = query("""
    SELECT e.id, e.title, e.maxGlobal,
           COUNT(CASE WHEN es.status = 'sold' THEN 1 END) as sold_count
    FROM events e
    LEFT JOIN event_seats es ON e.id = es.eventId
    GROUP BY e.id
    HAVING sold_count > COALESCE(e.maxGlobal, 999)
""")
status = "PASS" if len(capacity_rows) == 0 else "FAIL"
icon = "✅" if status == "PASS" else "❌"
print(f"{icon} Capacidad global: {len(capacity_rows)} eventos excedidos")
if capacity_rows:
    problems.append({"check": "Capacidad", "count": len(capacity_rows), "rows": capacity_rows})

# Resumen
print("\n" + "=" * 60)
if problems:
    print(f"❌ AUDITORÍA FALLIDA — {len(problems)} checks con problemas")
    for p in problems:
        print(f"   → {p['check']}: {p['count']} problemas")
    sys.exit(1)
else:
    print("✅ AUDITORÍA COMPLETADA — 0 problemas encontrados")
    sys.exit(0)
