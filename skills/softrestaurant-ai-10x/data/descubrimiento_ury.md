# DESCUBRIMIENTO CRÍTICO: URY — ERP Open Source para Restaurantes

## Esto cambia RADICALMENTE el plan

URY es exactamente lo que buscamos: un ERP completo para restaurantes, 100% open source, basado en ERPNext (el competidor de Odoo), con POS, KDS, analytics, multi-sucursal, y en producción real (10+ outlets, 6 marcas F&B, incluyendo internacional).

## Features verificadas de URY (abril 2026)

### POS & Billing
- Role-based access con controles operacionales estrictos
- Pre-billing checklists (compliance)
- Linked con stock y accounting
- Multi-format: Table service, QSR, takeaway
- Multi-cashier handling y terminal controls
- Shift opening/closing y cash reconciliation
- Modern, fast UI con guided flow

### Menu & Recipe Management
- Centralized menu con outlet-level control
- Recipe mapping usando Bill of Materials (BOM)
- Control de pricing, availability, portions por outlet
- Combos, modifiers, item bundles
- Integrado con production planning para daily prep

### Table Order Management
- Mobile-first order taking para meseros
- Live sync con cocina y cajero
- Real-time inventory checks antes de tomar orden
- Modifiers, course sequencing, notas
- Integración con billing y KDS

### Kitchen Display & KOT Management (MOSAIC)
- Múltiples cocinas con advanced printer routing
- Interactive KDS con live status (Preparing, Ready, Served)
- Delay, cancellation, modification tracking
- Real-time kitchen analytics
- Seamless flow from order to service

### Operational Red Flags & Alerts
- Delayed orders y preparation time breaches
- KOT not started alerts
- Unclosed bills y prolonged table occupancy
- Excessive cancellations/modifications
- Dashboard para quick issue resolution across outlets

### Reports & Analytics (PULSE)
- Daily P&L
- Shortage y Excess reporting
- Course-wise y item-wise performance
- Captain y staff performance tracking
- Branch-wise y outlet-wise comparisons
- Customer-wise sales trends
- Real-time operational insights

## Datos de producción
- 10+ outlets activos
- 6 marcas F&B
- Primer deployment internacional
- Backed by Frappe (empresa detrás de ERPNext)
- Frappe Cloud hosting disponible

## Por qué URY > Odoo para nuestro caso
1. ESPECÍFICO para restaurantes (Odoo es genérico)
2. KDS incluido (Odoo no tiene)
3. POS diseñado para restaurantes (Odoo POS es genérico)
4. Red Flags & Alerts (proto-IA operacional)
5. Multi-outlet nativo
6. ERPNext debajo = inventario, compras, contabilidad, HR completos
7. 100% open source (MIT license)
8. En producción real, no demo
9. Mobile-first para meseros

## Lo que URY NO tiene (y necesitamos agregar)
1. IA proactiva (cerebro inteligente)
2. Reservaciones (necesita integración con OpenTable)
3. Delivery hub (necesita integración)
4. CRM/Fidelización avanzada
5. Menú digital QR para clientes
6. Interfaz en español mexicano


---

# DESCUBRIMIENTO: Corely-AI — ERP Kernel AI-native

## Evaluación: INTERESANTE PERO INMADURO

Corely es un concepto brillante: un kernel ERP AI-native con packs modulares (restaurant, hotel, factory). Sin embargo:

**A favor:**
- AI-native by design (copilot con tool schemas, audit trails)
- Arquitectura hexagonal, DDD, CQRS-lite — muy bien diseñado
- POS offline-first incluido
- TypeScript/NestJS/Prisma/Redis — stack moderno
- 1,078 commits — desarrollo activo

**En contra:**
- Solo 1 estrella, 0 forks — nadie lo usa
- No releases publicados
- Restaurant pack está "coming soon" (booking, production)
- AGPL-3.0 (restrictivo para comercialización)
- No hay evidencia de uso en producción

**Veredicto:** Monitorear pero NO usar como esqueleto. Demasiado inmaduro. La arquitectura es inspiración, no base.

---

# DESCUBRIMIENTO: Oracle NetSuite para Restaurantes (31 marzo 2026)

Oracle lanzó una solución AI-powered para restaurant operations. Esto confirma que los grandes players están entrando al espacio de IA para restaurantes. Nuestro enfoque open source + IA es la respuesta para SMBs que no pueden pagar Oracle.

---

# RESUMEN DE CANDIDATOS A ESQUELETO (actualizado)

| Candidato | Stars | Producción | Módulos Restaurant | IA | Veredicto |
|---|---|---|---|---|---|
| URY + ERPNext | 262 | 10+ outlets | POS, KDS, Menu, Kitchen, Alerts, P&L | No (oportunidad) | **GANADOR** |
| TastyIgniter | 3,600 | Sí | Online ordering, reservas, multi-location | No | Bueno para ordering, NO es ERP |
| Odoo Community 19 | N/A | Masivo | POS genérico, inventario, compras, HR | No | Genérico, no restaurant-specific |
| Corely-AI | 1 | No | Coming soon | Sí (copilot) | Inmaduro, solo inspiración |
| Enatega | 1,200 | Sí | Delivery multi-vendor | No | Solo delivery |

**DECISIÓN: URY + ERPNext es el esqueleto superior a Odoo para nuestro caso.**

Razones:
1. Diseñado ESPECÍFICAMENTE para restaurantes (no genérico como Odoo)
2. KDS incluido (Odoo no tiene)
3. POS restaurant-specific con mobile-first para meseros
4. Red Flags & Alerts (proto-IA)
5. Multi-outlet nativo
6. ERPNext debajo = todo el ERP completo
7. En producción real (10+ outlets, 6 marcas)
8. Frappe-backed (empresa seria)
