---
id: DSC-LT-002
proyecto: LIKETICKETS
tipo: restriccion_dura
titulo: "Producto piloto: 313 butacas Zona Like del estadio Kukulkán (Leones de Yucatán)"
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:ticketlike-ops
  - skill:comercializacion-zona-like-313
cruza_con: ["ninguno"]
---

# Producto piloto: 313 butacas Zona Like del estadio Kukulkán (Leones de Yucatán)

## Decisión

El producto inicial de LikeTickets se restringe exclusivamente a la comercialización digital de las 313 butacas premium (Zona Like) del estadio Kukulkán para los 42 juegos de los Leones de Yucatán. No se venderán boletos generales ni otras zonas en esta fase piloto.

## Por qué

Enfocarse en un inventario premium limitado (313 lugares) permite validar el motor de reservas (Ticketlike) y la estrategia de pauta IA-first con escasez real, maximizando el revenue por asiento sin la complejidad operativa de todo el estadio.

## Implicaciones

Toda la arquitectura técnica (TiDB, Stripe) y narrativa (Leoncio) debe optimizarse para este inventario exacto. El límite de capacidad global en la base de datos debe mantenerse estrictamente en 312/314.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)