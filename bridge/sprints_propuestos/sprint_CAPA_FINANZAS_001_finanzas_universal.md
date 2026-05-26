<!-- lint_strict -->
# Sprint CAPA-FINANZAS-001 — Finanzas Universal

**Estado:** Propuesto — Canonizado sin ejecutar
**Hilo:** TBD
**ETA:** estimación pendiente
**Objetivo Maestro:** #9 (Transversalidad Universal — Capa 6) + #1 (Crear Empresas Digitales Completas)
**Capa Transversal:** C6 Finanzas
**Bloqueos:** ninguno técnico
**Resultado esperado:** Cada empresa hija tiene proyecciones financieras vivas, unit economics tracked, alertas de burn rate, tax optimization.

---

## 0. Procedencia

OM-09 v3.0 línea 464-469:

> **CAPA 6 — Finanzas:**
> - Proyecciones financieras basadas en datos reales
> - Cash flow management
> - Tax optimization
> - Unit economics tracking (CAC, LTV, margins)
> - Alertas de burn rate

Auditoría 2026-05-26: 0 sprints en backlog cubren C6.

---

## 1. Audit pre-sprint

Lo que existe:
- Stripe MCP — datos de revenue
- PayPal MCP — datos de revenue
- Skill `el-monstruo-toolkit` con costos de stack tracked
- Sin sistema unificado de finanzas para empresas hijas

Lo que falta:
- Schema `financial_snapshots`, `unit_economics`, `cash_flow_projections`, `tax_events`
- Capability `compute_unit_economics(project_id, period)`
- Capability `project_cash_flow(project_id, horizon_months)`
- Integración con bancos (Belvo, Plaid, Open Banking LATAM)
- Tax engine por jurisdicción (México IVA, Brasil ICMS, USA sales tax, EU VAT)

---

## 2. Tareas (MVP)

### MVP-1: Unit economics tracking
- Pipeline diario: extrae datos de Stripe/PayPal + ad spend + COGS → calcula CAC, LTV, contribution margin, payback period
- Dashboard con líneas de tiempo
- Alertas: CAC creciente >20% en 30 días, LTV/CAC < 3, payback > 12 meses

### MVP-2: Cash flow management
- Proyecciones rolling 12 meses con escenarios (base, optimista, pesimista)
- Detección de cash gap antes de que ocurra
- Recomendaciones: cuándo levantar, cuándo cortar gastos
- Integración con bancos vía Belvo (LATAM) o Plaid (US)

### MVP-3: Tax optimization
- Engine que detecta deducciones aplicables por jurisdicción
- Calendario fiscal automático con deadlines
- Generación de reportes tax-ready (México: ContPaq, USA: TurboTax format)
- Alertas pre-deadline

### MVP-4: Burn rate alerting
- Monitor diario de spend vs revenue
- Threshold: si runway < 6 meses, alerta crítica
- Propone cortes ranked por impacto/dolor

### MVP-5: Financial reporting unificado
- Dashboard `monstruo/dashboards/finance/` con vista consolidada
- Por empresa hija individual + portfolio agregado
- Export a Excel/Sheets para contadores

### MVP-6: Integration con otras capas
- CAPA_VENTAS: ajusta pricing si margen baja
- CAPA_ADS: pausa campañas si CAC > umbral
- CAPA_OPS: reduce inventory si cash gap proyectado
- CAPA_TENDENCIAS: detecta señales de recesión y ajusta proyecciones

---

## 3. Dependencias

- Stripe/PayPal MCPs ya disponibles
- `MOBILE_0_SMP` para credenciales bancarias en Vault
- `CAPA_VENTAS_001`, `CAPA_ADS_001` para datos de input
- `STACK_REFRESH_001` para validar APIs bancarias

---

## 4. Criterios de Cierre y Métricas de Éxito

- Precisión de proyecciones cash flow ±15% a 90 días
- 100% de empresas hijas con unit economics tracked daily
- Tax compliance: 0 retrasos en deadlines
- Detección de cash gap con ≥ 90 días de anticipación

---

## 5. Anti-doctrina

- NO automatizar declaraciones fiscales sin firma humana
- NO usar entrenamiento del LLM para cálculos fiscales (datos viejos = multas)
- NO mezclar finanzas de empresas hijas con personales
- NO ejecutar transacciones sin HITL en tier ≥ Trusted

---

## 6. Notas de canonización

Sprint canonizado sin ejecutar. Auto-promote al detectar commits en `kernel/finance/` o `monstruo/capabilities/finanzas/`.

Firmado: **Manus B — 2026-05-26**
