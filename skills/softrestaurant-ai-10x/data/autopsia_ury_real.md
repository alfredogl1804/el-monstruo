# AUTOPSIA URY — Datos Verificados del Repo Real

**Fecha:** 24 abril 2026
**URL correcta:** https://github.com/ury-erp/ury (NO AkashPawar-hp/ury — ese da 404)
**Organización:** ury-erp

## Datos Duros del Repo
- **Stars:** 262
- **Forks:** 158
- **Watchers:** 12
- **Commits:** 377
- **Branches:** 11
- **Tags/Releases:** 4 (última v0.2.1, Nov 1 2025)
- **Licencia:** AGPL-3.0
- **Issues abiertos:** 8
- **Pull requests abiertos:** 12
- **Último commit:** hace 2 semanas (activo)
- **Contribuidores:** 14+ (visible en sidebar)
- **Desarrollador:** Tridz Technologies Pvt Ltd, soportado por Frappe

## Estructura del Repo
- `ury/` — App principal Frappe
- `pos/` — URY POS (web-based, mobile-first)
- `URYMosaic/` — KDS (Kitchen Display System)
- `urypos/` — Versión anterior del POS
- `AGENTS.MD` — Documentación de AI agents (!)
- `CLAUDE.MD` — Documentación para Claude AI (!)
- `FEATURES.md` — Lista completa de features

## Features Verificadas (del README)
### POS & Billing
- Role-based access
- Pre-billing checklists
- Multi-format: Table service, QSR, takeaway
- Multi-cashier handling
- Shift opening/closing, cash reconciliation

### Menu & Recipe Management
- Centralized menu con control por outlet
- Recipe mapping con BOM
- Combos, modifiers, item bundles
- Integrado con production planning

### Table Order Management
- Mobile-first para meseros
- Live sync con cocina y cajero
- Real-time inventory checks
- Modifiers, course sequencing, notes

### Kitchen Display & KOT
- Múltiples cocinas con printer routing
- KDS interactivo con status en vivo
- Delay, cancellation, modification tracking
- Real-time kitchen analytics

### Red Flags & Alerts
- Delayed orders
- KOT no iniciados
- Bills sin cerrar
- Excessive cancellations
- Dashboard multi-outlet

### Reports & Analytics
- Daily P&L
- Shortage/Excess reporting
- Item-wise performance
- Staff performance tracking
- Branch-wise comparisons
- Customer-wise sales trends

## HALLAZGO CRÍTICO: AGENTS.MD y CLAUDE.MD
URY YA tiene documentación para AI agents. Esto significa que el proyecto ya está pensando en integración con IA. Necesito leer estos archivos.

## Advertencia del Proyecto
> "URY is currently in active development... backward compatibility is not guaranteed"
> "Our system has been successfully running at scale, serving over 10+ outlets for the past 10 months"

## Versión Actual
- v0.2.1 (Nov 1, 2025) — "First Frappe Cloud Release"
- Requiere ERPNext (versión no especificada en README, pero ERPNext v16 es la actual)

## i18n (Internacionalización)
- Último commit incluye "Implement i18n system" — ESTÁN AGREGANDO soporte multi-idioma
- Esto es CRÍTICO para México (español)

## AGENTS.MD — Arquitectura Interna Verificada

URY tiene documentación profesional para AI agents (AGENTS.MD y CLAUDE.MD). Esto revela:

### Stack Técnico Real
- **Backend:** Frappe/ERPNext custom app (Python)
- **POS v2:** React 19 (actual, en producción)
- **KDS (Mosaic):** Vue 3
- **POS v1:** Vue 3 (legacy, soporte termina dic 2025)
- **Real-time:** Socket.io (Frappe nativo)
- **Impresión térmica:** QZ Tray
- **Build:** Yarn workspaces

### 35 Doctypes Personalizados
Los más relevantes para nuestros 19 módulos:
- URY Order / URY Order Item — pedidos
- URY KOT / URY KOT Items — tickets de cocina
- URY Menu / URY Menu Item / URY Menu Course — menú con cursos
- URY Restaurant / URY Table / URY Room — mesas y áreas
- URY Printer Settings — impresoras térmicas
- URY User — meseros/cajeros por sucursal
- Aggregator Settings — Zomato, Swiggy (delivery)
- URY Daily P and L — P&L diario
- URY Cost of Goods — COGS
- Sub POS Closing — cierre de caja por cajero

### API Principal
- `ury/ury_pos/api.py` — 722 líneas, métodos whitelisted
- Endpoints: getRestaurantMenu, getBranch, getModeOfPayment, getPosProfile, getAggregatorItem, createPaymentEntry, getInvoiceForCashier

### Integración con ERPNext
- POS Invoices → Sales Invoices (consolidación)
- Price Lists, Customers, Payment Modes, Tax Templates = objetos estándar ERPNext
- Custom fields en POS Invoice, POS Profile, Branch, Customer, Price List

### Scheduler
- `kotValidationThread` corre cada minuto para validar estado de KOTs

### CONCLUSIÓN: URY es un esqueleto REAL y VIABLE
- 35 doctypes, 722 líneas de API, React 19 POS, Vue 3 KDS
- Documentación profesional para AI agents
- Integración nativa con ERPNext
- Multi-branch de fábrica
- En producción real (10+ outlets)
- ACTIVO: último commit hace 2 semanas, i18n en progreso
