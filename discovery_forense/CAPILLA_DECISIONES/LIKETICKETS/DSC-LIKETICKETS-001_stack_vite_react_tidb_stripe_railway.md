---
id: DSC-LT-001
proyecto: LIKETICKETS
tipo: decision_arquitectonica
titulo: "ticketlike.mx corre en Railway con Vite+React+TypeScript frontend, TiDB serverless backend, Stripe checkout"
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:ticketlike-ops
cruza_con: ["ninguno"]
---

# Stack Vite+React+TiDB+Stripe en Railway

## Decisión

Se establece el stack tecnológico para ticketlike.mx: Frontend con React, TypeScript, Vite y TailwindCSS; Backend con tRPC y Express; Base de datos TiDB Cloud (MySQL-compatible); Pagos con Stripe (test mode); y despliegue automatizado en Railway desde la rama main de GitHub.

## Por qué

Este stack garantiza un desarrollo ágil y tipado fuerte (TypeScript/tRPC), una base de datos escalable y compatible con MySQL (TiDB), integración segura de pagos (Stripe) y un despliegue continuo sin fricciones (Railway), optimizando la operación de la boletería.

## Implicaciones

Cualquier desarrollo futuro debe mantener compatibilidad con este stack. Las consultas a la base de datos deben respetar las reglas operativas de TiDB y los despliegues seguirán dependiendo de Railway.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)