# Comparativa: Odoo 19 vs URY + ERPNext — Módulo por Módulo

## Para los 19 módulos de SoftRestaurant (sin facturación)

| # | Módulo SR | Odoo 19 Community | URY + ERPNext | Ganador |
|---|---|---|---|---|
| 1 | Punto de Venta (POS) | POS genérico, no restaurant-specific | POS restaurant-specific: mesas, meseros, mobile-first | **URY** |
| 2 | Comandas/KDS | NO tiene KDS nativo | MOSAIC KDS interactivo, multi-cocina, live status | **URY** |
| 3 | Mesas y Salones | Módulo restaurant básico en POS | Mesas con color-coding, time tracking, table transfer | **URY** |
| 4 | Menú/Carta | Productos genéricos | Menú restaurant con BOM, combos, modifiers, room-wise | **URY** |
| 5 | Inventario | Módulo inventario completo | ERPNext Stock module completo (heredado) | **Empate** |
| 6 | Compras | Módulo compras completo | ERPNext Procurement module completo | **Empate** |
| 7 | Recetas/Costos | No nativo, requiere módulo MRP | BOM integrado con menú, production planning | **URY** |
| 8 | Control de Mermas | No nativo | Shortage & Excess reporting en Pulse | **URY** |
| 9 | Empleados/Turnos | HR module básico en Community | ERPNext HR module + captain/staff tracking | **URY** |
| 10 | Reportes/Analytics | Reporting básico | Pulse: Daily P&L, branch-wise, item-wise, captain performance | **URY** |
| 11 | Cuentas por Cobrar | Accounting module | ERPNext Accounting module | **Empate** |
| 12 | Cuentas por Pagar | Accounting module | ERPNext Accounting module | **Empate** |
| 13 | Promociones/Descuentos | Pricing rules | No documentado específicamente | **Odoo** |
| 14 | Delivery | No nativo | Soporta order types: delivery, takeaway, aggregator | **URY** |
| 15 | Reservaciones | No nativo | No nativo (necesita integración) | **Empate** (ninguno) |
| 16 | Fidelización/CRM | CRM module | ERPNext CRM module | **Empate** |
| 17 | Multi-sucursal | Multi-company support | Multi-outlet nativo, branch-wise comparisons | **URY** |
| 18 | Alertas Operativas | No tiene | Red Flags & Alerts: delays, unclosed bills, cancellations | **URY** |
| 19 | Dashboard Gerencial | Dashboards básicos | Pulse dashboards operativos, real-time insights | **URY** |

## Resultado: URY gana 10/19, Empate 6/19, Odoo gana 1/19

## ERPNext módulos que URY hereda automáticamente:
- Accounting (contabilidad completa)
- Stock/Inventory (inventario)
- Procurement/Purchasing (compras)
- HR & Payroll (recursos humanos)
- CRM (gestión de clientes)
- Projects (gestión de proyectos)
- Manufacturing/BOM (recetas/producción)
- Point of Sale (base POS que URY extiende)
- Website (portal web)
- Asset Management
- Quality Management

## Conclusión: URY + ERPNext es OBJETIVAMENTE superior a Odoo para restaurantes
- URY tiene todo lo restaurant-specific que Odoo no tiene
- ERPNext debajo provee todo lo ERP que necesitamos
- El único gap es reservaciones (integración OpenTable) y IA (nuestro cerebro)
