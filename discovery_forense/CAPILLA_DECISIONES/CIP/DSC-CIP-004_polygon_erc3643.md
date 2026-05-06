---
id: DSC-CIP-004
proyecto: CIP
tipo: decision_arquitectonica
titulo: "Polygon + ERC-3643"
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:creacion-cip
cruza_con: ["ninguno"]
---

# Stack on-chain: red Polygon y estándar ERC-3643

## Decisión

Se establece el uso de la red Polygon por sus bajos costos de gas en México y el estándar ERC-3643 para la emisión de tokens regulados. Este estándar incluye capacidades nativas de whitelisting y KYC, asegurando el cumplimiento normativo desde la capa base.

## Por qué

Polygon permite micro-inversiones desde $1 USD sin que las comisiones de red absorban el capital. El estándar ERC-3643 es fundamental porque garantiza que solo inversores verificados (KYC) puedan poseer o transferir los tokens anclados a propiedades reales, cumpliendo con regulaciones financieras.

## Implicaciones

Define la arquitectura base de los smart contracts y obliga a integrar un proveedor de identidad (KYC) antes de cualquier emisión o transferencia en el mercado secundario.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)