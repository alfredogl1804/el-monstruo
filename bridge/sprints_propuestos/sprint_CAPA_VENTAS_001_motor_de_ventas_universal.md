<!-- lint_strict -->
# Sprint CAPA-VENTAS-001 — Motor de Ventas Universal

**Estado:** Propuesto — Canonizado sin ejecutar
**Hilo:** TBD (no asignado)
**ETA:** estimación pendiente — bloqueado por T1-MAGNA-001 (paradigma de UI) y prerequisito MOBILE_REALIGNMENT_001
**Objetivo Maestro:** #9 (Transversalidad Universal — Capa 1) + #1 (Crear Empresas Digitales Completas)
**Capa Transversal:** C1 Motor de Ventas
**Bloqueos:** ninguno técnico — sprint canonizado para registrar la deuda doctrinal
**Resultado esperado:** Cada empresa digital creada por El Monstruo nace con un motor de ventas activo desde el día uno, no después.

**Origen del sprint:** Auditoría del backlog 2026-05-26 por Manus B reveló que de las 8 capas transversales del Objetivo Maestro #9, solo C8 (Memento) y parcialmente C7 (Resiliencia) tienen sprints asociados. Las 6 capas comerciales (Ventas, SEO, Ads, Tendencias, Operaciones, Finanzas) están descubiertas. Sin estas capas, El Monstruo construye negocios pero no los empuja al mercado.

---

## 0. Procedencia

El Objetivo Maestro #9 (`docs/EL_MONSTRUO_15_OBJETIVOS_MAESTROS.md` v3.0, 4 may 2026, sección "Las Capas Transversales Universales", líneas 430-437) define textualmente:

> **CAPA 1 — Motor de Ventas:**
> - Estrategia de pricing óptima basada en datos reales
> - Funnels de conversión pre-diseñados y optimizados
> - Copywriting de venta generado con inteligencia emergente
> - A/B testing automático perpetuo
> - Upsell/cross-sell inteligente
> - Retención y churn prevention

Estos 6 componentes hoy no existen como capability invocable, ni como módulo del kernel, ni como sprint en backlog. Este sprint registra la deuda y propone scope mínimo viable.

---

## 1. Audit pre-sprint — Estado actual

Lo que ya existe en el repo:
- `tools/` — herramientas de tooling interno, ninguna comercial
- `kernel/` — kernel del Monstruo, sin módulo de ventas
- `bridge/sprints_propuestos/` — 49 sprints, ninguno aborda C1
- `interfaces_context_fabric/maps/SPRINT_REGISTRY.yaml` — sin sprint C1

Lo que falta (gaps):
- Definición del módulo `monstruo/capabilities/ventas/` o equivalente
- Schema de `pricing_strategy`, `conversion_funnel`, `ab_test_config` en Supabase
- Capability invocable desde el kernel: `invoke_sales_engine(project_id, action)`
- Conexión a Stripe/PayPal para pricing tests
- Integración con motor de copywriting (LLM con prompts canónicos de venta)
- Dashboard de métricas: CAC, LTV, conversion rate, churn
- A/B testing perpetuo con scoring estadístico
- Sistema de upsell/cross-sell basado en clustering de comportamiento

---

## 2. Tareas (Scope mínimo viable - MVP)

Para no construir todo de una vez, el MVP define el contrato mínimo:

### MVP-1: Pricing dinámico
- Tabla `pricing_strategies` en Supabase con columnas: `project_id`, `tier`, `price`, `currency`, `valid_from`, `valid_until`, `experiment_id`
- API `POST /v1/sales/pricing/propose` que dado un proyecto y datos del mercado retorna 3 estrategias candidatas (penetración, premium, freemium)
- Decisión final HITL: el dueño firma una

### MVP-2: Funnel pre-diseñado
- Tabla `conversion_funnels` con steps canónicos (landing → opt-in → trial → paid)
- Plantilla genérica que se inyecta a cada empresa hija nueva
- Métricas de paso a paso vía Plausible/PostHog

### MVP-3: Copywriting de venta
- Endpoint `POST /v1/sales/copy/generate` con `purpose=hero|cta|email|ad`
- Prompts canónicos en `kernel/sales/prompts/`
- Output guardado en `sales_copy_versions` para A/B testing

### MVP-4: A/B testing perpetuo
- Wrapper sobre PostHog feature flags o equivalente
- Selección automática del ganador con confidence ≥ 95%
- Hooks de evento: experiment_started, variant_won, experiment_concluded

### MVP-5: Upsell/cross-sell
- Tabla `customer_segments` con clustering automático
- Reglas de invocación: si cluster=X y trigger=Y, propón Z
- Integración con motor de notificaciones

### MVP-6: Churn prevention
- Tabla `churn_signals` con eventos predictivos
- Job que escanea cada 6h y dispara intervenciones (email, WhatsApp, descuento)

---

## 3. Dependencias

- **MOBILE_REALIGNMENT_001** debe ejecutarse antes (brand DNA define tono del copywriting)
- **WHATSAPP_GATEWAY_P0** desbloquea canal de retención
- **MOBILE_0_SMP** desbloquea Vault para guardar pricing experiments confidenciales
- **STACK_REFRESH_001** asegura que A/B testing usa la mejor herramienta disponible

---

## 4. Criterios de Cierre y Métricas de Éxito

- Cada empresa hija creada por El Monstruo tiene pricing publicado en ≤ 5 minutos del init
- A/B test perpetuo activo en al menos 1 dimensión (precio, copy, funnel) en cada empresa hija
- Churn rate de empresas hijas ≤ 5% mensual a los 90 días
- Conversion rate landing → trial ≥ 8% promedio

---

## 5. Anti-doctrina (qué NO hacer)

- NO construir el motor antes de que MOBILE_REALIGNMENT_001 defina el brand DNA — el copywriting necesita el tono firmado
- NO acoplar a un único proveedor de pricing (no asumir Stripe; abstraer la capa)
- NO ejecutar A/B tests sin contrato claro de N mínimo (estadística no significativa = ruido)
- NO bloquear este sprint en T1-MAGNA-001 si la salida es por chat o WhatsApp en vez de UI propia (la capa es agnóstica de transport)

---

## 6. Notas de canonización

Este sprint se inyecta al backlog como `Estado: Propuesto — Canonizado sin ejecutar`. Aparecerá en el Tablero de Campaña como nodo del distrito **backlog_canonizado** con `paradigm: capa_transversal_comercial`. Su status se actualizará automáticamente al `EJECUCION` cuando aparezca un commit en main que toque `kernel/sales/` o `monstruo/capabilities/ventas/`.

Firmado: **Manus B — 2026-05-26**
Auditor pendiente: Cowork (T2)
