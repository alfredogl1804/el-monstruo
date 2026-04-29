# Inventario del Venue — Estadio Kukulkán Alamo

## Resumen

| Sección | Ubicaciones | Personas/Ubicación | Total Personas | Precio Unitario | Ingreso Máximo |
|---------|-------------|-------------------|----------------|-----------------|----------------|
| Butacas Fila A | 44 (A-44 desactivada) | 1 | 43 | $165/persona | $7,095 |
| Butacas Fila B | 44 (B-44 desactivada) | 1 | 43 | $165/persona | $7,095 |
| Mesa VIP 4 | 23 | 4 | 92 | $2,000/mesa | $46,000 |
| Mesa VIP 6 | 17 | 6 | 102 | $3,000/mesa | $51,000 |
| Sala VIP | 8 | 4 | 32 | $2,000/sala | $16,000 |
| **Total** | **136** | | **312** | | **$127,190** |

Nota: El máximo teórico de $127,520 incluye variaciones de precio por bleachers y VIP individual.

## Prefijos de labels en la DB

| Prefijo | Sección | Ejemplo | Rango |
|---------|---------|---------|-------|
| `A-` | Butaca Fila A | A-01 a A-43 | A-44 desactivada |
| `B-` | Butaca Fila B | B-01 a B-43 | B-44 desactivada |
| `M4-` | Mesa VIP 4 personas | M4-01 a M4-23 | |
| `M6-` | Mesa VIP 6 personas | M6-01 a M6-17 | |
| `S-` | Sala VIP | S-01 a S-08 | |

## Asientos desactivados

| Asiento | Razón | Fecha | Ventas existentes |
|---------|-------|-------|-------------------|
| A-44 | Eliminado por Daniel | 2026-04-18 | Francisco Rodriguez (J1, J2) — resolver en taquilla |
| B-44 | Eliminado por Daniel | 2026-04-18 | David Cruz Montalvo (J1) — resolver en taquilla |

## Límites de capacidad (configurados en DB)

| Campo en events | Valor | Descripción |
|-----------------|-------|-------------|
| maxButacas | 86 | Máximo butacas por jornada |
| maxMesaVip4 | 92 | Máximo personas en mesas VIP 4 |
| maxMesaVip6 | 102 | Máximo personas en mesas VIP 6 |
| maxSalaVip | 32 | Máximo personas en salas VIP |
| maxGlobal | 312 | Límite absoluto por jornada |

## Tipos de ticket en ticket_orders

| ticketType | Qué es | Precio típico |
|------------|--------|---------------|
| Butaca | Asiento individual fila A o B | $165 |
| Bleachers | Gradas generales | $600 |
| Mesa VIP 4 | Mesa completa de 4 | $2,000 |
| Mesa VIP 6 | Mesa completa de 6 | $3,000 |
| Sala VIP | Sala completa de 4 | $2,000 |
| VIP | VIP genérico (mesa completa) | $2,000-$3,000 |
| Lugar VIP | Lugar individual en mesa VIP | $500 |
