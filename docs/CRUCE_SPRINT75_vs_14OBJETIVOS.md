# Cruce Detractor: Sprint 75 vs. 14 Objetivos Maestros
## "El Monstruo que Vende" — Embrión-2: Motor de Ventas

**Fecha:** 1 de Mayo 2026
**Evaluador:** Hilo B (modo detractor implacable)
**Versión del Sprint:** 75.0

---

## Metodología

Evalúo cada Objetivo del 1 al 10 respondiendo: "¿Este sprint REALMENTE avanza este objetivo o solo lo menciona?" Soy el peor crítico posible. Si algo es humo, lo digo.

---

## Evaluación por Objetivo

### Obj #1 — Crear Empresas que Generen Revenue
**Score: 9/10**

Este sprint ES el Objetivo #1. El Motor de Ventas es literalmente la máquina de generar revenue. Tiene el ciclo completo: detectar oportunidad → diseñar estrategia → ejecutar → medir → optimizar. El A/B testing con significancia estadística real (z-test, no simulado) es serio.

**Pero no es 10 porque:** Falta la conexión con dinero real. El Embrión puede detectar oportunidades y diseñar estrategias, pero no puede cobrar. Sin Stripe/PayPal integrado (Opción C que se pospuso), el ciclo se rompe en el paso de "convertir lead en cliente que paga". Es un motor de ventas que no puede cerrar la venta.

**Corrección mandatoria:** Incluir en el Sprint Plan un stub de `payment_gateway` que defina la interfaz futura. Así cuando llegue el sprint de pagos, el Motor de Ventas ya sabe dónde conectar.

---

### Obj #2 — Posicionamiento Apple/Tesla
**Score: 8/10**

La integración con Brand Engine es correcta — el copy pasa por validación antes de publicarse. El naming es consistente (`ventas_ejecutor`, `ventas_pensador`). Los logs tienen identidad. Los endpoints siguen la convención.

**Pero:** El system prompt del Pensador dice "Eres el Motor de Ventas de El Monstruo" pero luego las instrucciones son genéricas de cualquier agente de ventas. No hay nada que haga que las estrategias que genera SEAN distintivamente "de El Monstruo". Apple no vende como cualquiera — vende como Apple. El Motor de Ventas debería tener un estilo propio de vender.

**Corrección mandatoria:** Agregar al system prompt del Pensador un "Estilo de Venta El Monstruo" — directo, sin manipulación, valor primero, transparencia en pricing, anti-dark-patterns. Esto diferencia de cualquier otro agente de ventas.

---

### Obj #3 — Mínima Complejidad
**Score: 7/10**

La separación Pensador/Ejecutor es elegante. El Ejecutor es puro Python sin LLM. Los modelos son dataclasses limpias. Hasta aquí bien.

**Pero:** 5 tablas SQL + 7 endpoints + 4 archivos Python + tests = mucho para un sprint. El Sprint 73 ya fue criticado por ser demasiado grande. Este tiene el mismo problema. ¿Realmente necesitamos `ExperimentoAB` como tabla separada en el MVP? ¿No podría ser un campo JSONB en `ejecuciones_venta`?

**Corrección mandatoria:** Dividir en 75A (MVP: modelos + ejecutor + 3 endpoints) y 75B (Pensador completo + A/B testing + 7 endpoints). Entregar valor incremental.

---

### Obj #4 — No Equivocarse Dos Veces
**Score: 6/10**

El Pensador consulta memoria antes de diseñar estrategias (`buscar("estrategia venta {tipo} {mercado}")`). Eso es correcto — aprende de lo que funcionó antes.

**Pero:** No hay mecanismo explícito de "anti-patrones de venta". Si una estrategia falla 3 veces con el mismo tipo de producto, ¿el sistema registra "NUNCA hacer X con productos tipo Y"? El `decidir_pivot` solo decide persistir/pivotar/abandonar — no registra el APRENDIZAJE NEGATIVO de forma estructurada.

**Corrección mandatoria:** Agregar tabla `lecciones_venta` con campos: `tipo_leccion` (exito/fracaso), `contexto`, `aprendizaje`, `aplicable_a`. El Pensador DEBE consultar lecciones negativas antes de proponer estrategias.

---

### Obj #5 — Magna/Premium (Investigación Exhaustiva)
**Score: 7/10**

El Pensador busca en memoria antes de diseñar. El Ejecutor calcula TAM, probabilidad, y score de priorización. Hay datos detrás de las decisiones.

**Pero:** ¿De dónde salen los datos de mercado? El `detectar_oportunidades` recibe un `contexto: dict` genérico. No hay integración explícita con Perplexity para research de mercado, ni con APIs de datos financieros para validar TAM. El Pensador "estima" TAM con su conocimiento interno — eso no es Magna/Premium, es adivinanza.

**Corrección mandatoria:** Integrar Perplexity search como paso previo a `detectar_oportunidades`. Antes de que el Pensador evalúe, el Ejecutor debe hacer research automatizado: tamaño de mercado real, competidores con pricing, tendencias de búsqueda.

---

### Obj #6 — Velocidad (Implementar Rápido)
**Score: 8/10**

El Ejecutor es <10ms por operación. El Pensador solo se activa cuando hay juicio. El heartbeat cada 30 min es razonable. La arquitectura permite implementar el MVP en 1-2 días.

**Sin corrección.** Este objetivo está bien cubierto por la separación Pensador/Ejecutor.

---

### Obj #7 — No Inventar la Rueda
**Score: 5/10**

Aquí hay un problema serio. El Sprint reinventa:
- A/B testing (existen herramientas: Optimizely, GrowthBook, Statsig)
- Funnel tracking (existen: Mixpanel, Amplitude, PostHog)
- CRM/Pipeline (existen: HubSpot API, Pipedrive API)
- Email marketing (existen: Resend, SendGrid, Mailchimp API)

El z-test manual es elegante pero ¿por qué no usar una librería estadística (scipy.stats)?

**Corrección mandatoria:** Para cada componente, documentar: "¿Existe herramienta externa que hace esto? Si sí, ¿por qué la reinventamos?" Justificaciones válidas: soberanía, costo, integración. Pero debe ser explícito, no implícito.

---

### Obj #8 — Inteligencia Emergente
**Score: 8/10**

El Embrión-2 recibe contexto del Embrión de Tendencias, detecta oportunidades que ningún humano pidió, y propone estrategias autónomamente. Eso ES emergencia — comportamiento no programado explícitamente que surge de la interacción entre Embriones.

**Pero:** La emergencia solo ocurre si hay un Embrión de Tendencias activo que envíe `contexto_tendencias`. Sin ese Embrión (que aún no existe — es Sprint 76+), el Motor de Ventas solo responde a encomiendas manuales. No es emergente, es reactivo.

**Corrección mandatoria:** Agregar un modo "proactivo" donde el Embrión-2 busca oportunidades por sí solo (usando Perplexity/web) incluso sin input de Tendencias. Así funciona desde el día 1 sin depender de Embriones que aún no existen.

---

### Obj #9 — Transversalidad (7 Capas)
**Score: 9/10**

Este sprint ES la Capa 1 (Motor de Ventas) de las 7 Capas Transversales. Está diseñado para comunicarse con otras capas via el bus de la Colmena. El Brand Engine valida sus outputs. El Command Center consume sus datos.

**Sin corrección mayor.** La transversalidad está bien diseñada.

---

### Obj #10 — Seguridad y Privacidad
**Score: 5/10**

No hay NADA de seguridad en este sprint:
- Los endpoints no tienen autenticación
- Los datos de clientes/leads no están encriptados
- No hay rate limiting en el Pensador (un loop podría gastar $100 en LLM calls)
- No hay validación de input en `crear_encomienda`

**Corrección mandatoria:** Agregar: (1) Auth en todos los endpoints, (2) Rate limit en llamadas al Pensador (máx 10/hora), (3) Validación de input con Pydantic, (4) Nota sobre GDPR/privacidad para datos de leads.

---

### Obj #11 — Seguridad del Sistema
**Score: 5/10**

Mismo problema que Obj #10 pero a nivel sistema. El Pensador puede generar estrategias que incluyan spam, dark patterns, o prácticas ilegales si el LLM alucina. No hay guardrail más allá del Brand Engine (que valida tono, no legalidad).

**Corrección mandatoria:** Agregar un `compliance_check` en el Ejecutor que valide: (1) No spam (frecuencia de emails), (2) No dark patterns (urgencia falsa, escasez artificial), (3) Cumplimiento legal básico (CAN-SPAM, GDPR). Es código determinista, costo $0.

---

### Obj #12 — Soberanía
**Score: 7/10**

El LLM se accede via abstracción (`self.llm.generate()`), no hardcoded a OpenAI. Supabase es reemplazable. El A/B testing es propio (no depende de Optimizely).

**Pero:** Si el LLM falla, todo el Pensador se detiene. No hay fallback. ¿Qué pasa si OpenAI tiene un outage de 4 horas? El Motor de Ventas se paraliza.

**Corrección mandatoria:** Agregar fallback multi-LLM en el Pensador: si el primario falla, intentar con secundario (Claude, Gemini). El Ejecutor ya es soberano (Python puro), pero el Pensador necesita resiliencia.

---

### Obj #13 — Internacionalización
**Score: 4/10**

Todo el código está en español (bien). Pero:
- ¿El Motor de Ventas puede vender en inglés? ¿En otros idiomas?
- El system prompt del Pensador está en español — ¿qué pasa si la oportunidad es en un mercado anglófono?
- Los copy que genera ¿en qué idioma salen?

**Corrección mandatoria:** Agregar campo `idioma_mercado` en Oportunidad. El Pensador debe generar copy en el idioma del mercado objetivo, no siempre en español. El Brand Engine debe validar en ambos idiomas.

---

### Obj #14 — El Guardián
**Score: 6/10**

El Brand Engine valida copy. Los logs son estructurados. Hay alertas con severidad.

**Pero:** No hay integración explícita con el ComplianceMonitor (Sprint 68). El Guardián debería poder auditar: "¿El Motor de Ventas está cumpliendo con los 14 Objetivos?" No solo validar tono de marca.

**Corrección mandatoria:** Agregar hook para que el Guardián pueda auditar el Motor de Ventas: métricas de compliance, frecuencia de violaciones de marca, ratio de pivots vs. persistencias.

---

## Resumen Ejecutivo

| Objetivo | Score | Veredicto |
|----------|-------|-----------|
| #1 Crear Empresas | 9/10 | Excelente — ES el objetivo |
| #2 Apple/Tesla | 8/10 | Bien pero falta estilo propio de venta |
| #3 Mínima Complejidad | 7/10 | Demasiado grande para un sprint |
| #4 No Equivocarse 2x | 6/10 | Falta registro de lecciones negativas |
| #5 Magna/Premium | 7/10 | Falta research automatizado real |
| #6 Velocidad | 8/10 | Bien |
| #7 No Inventar Rueda | 5/10 | Reinventa A/B, CRM, email sin justificar |
| #8 Emergencia | 8/10 | Bien pero depende de Embrión inexistente |
| #9 Transversalidad | 9/10 | Excelente |
| #10 Seguridad/Privacidad | 5/10 | Sin auth, sin encriptación, sin rate limit |
| #11 Seguridad Sistema | 5/10 | Sin compliance check anti-spam/dark-patterns |
| #12 Soberanía | 7/10 | Falta fallback multi-LLM |
| #13 i18n | 4/10 | No puede vender en otros idiomas |
| #14 Guardián | 6/10 | Sin integración con ComplianceMonitor |

**Score promedio: 6.7/10**
**Score post-correcciones estimado: 8.2/10**

---

## Correcciones Mandatorias (Ordenadas por Impacto)

| # | Corrección | Objetivos que mejora | Esfuerzo |
|---|---|---|---|
| 1 | Dividir en 75A (MVP) y 75B (completo) | #3, #6 | Bajo |
| 2 | Agregar auth + rate limit + validación | #10, #11 | Medio |
| 3 | Compliance check anti-spam/dark-patterns | #11, #14 | Medio |
| 4 | Modo proactivo sin depender de Embrión de Tendencias | #8 | Medio |
| 5 | Research automatizado con Perplexity antes de evaluar | #5, #7 | Medio |
| 6 | Tabla `lecciones_venta` + consulta obligatoria | #4 | Bajo |
| 7 | Estilo de Venta El Monstruo en system prompt | #2 | Bajo |
| 8 | Campo `idioma_mercado` + generación multi-idioma | #13 | Medio |
| 9 | Fallback multi-LLM en Pensador | #12 | Bajo |
| 10 | Stub de `payment_gateway` interface | #1 | Bajo |
| 11 | Documentar justificación de "reinventar" vs. adoptar | #7 | Bajo |
| 12 | Hook de auditoría para el Guardián | #14 | Bajo |

---

## Veredicto Final

Sprint 75 es el sprint más importante de la serie 71-80 porque ataca directamente el Obj #1 — el que justifica la existencia de El Monstruo. La arquitectura Pensador/Ejecutor está bien aplicada. El ciclo de ventas es completo.

**El problema principal es la seguridad (Obj #10, #11).** Un Motor de Ventas sin autenticación, sin rate limiting, y sin compliance check es un riesgo. No puedes vender si tu sistema puede ser abusado o si genera spam.

**El segundo problema es Obj #7.** Reinventar A/B testing, CRM, y email marketing sin justificar por qué no usar herramientas existentes es exactamente lo que el Objetivo dice que NO hagamos. La justificación puede ser válida (soberanía, integración, costo) pero DEBE ser explícita.

Con las 12 correcciones aplicadas, este sprint pasa de 6.7 a 8.2 — sólido para implementación.
