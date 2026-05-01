# División de Responsabilidades: Hilo A (Ejecutor) vs Hilo B (Arquitecto)

**Documento normativo — Vigente a partir del 1 de mayo de 2026**
**Versión:** 2.0 — Reemplaza la división original de INSTRUCCIONES_HILO_B.md
**Autor:** Hilo B (Arquitecto), validado por Alfredo Góngora

---

## Contexto: Por qué se actualiza esta división

La división original asignaba al Hilo A la ejecución de sprints completos y al Hilo B la planificación y cruces detractores. En la práctica, esto generó un problema estructural: **los objetivos subjetivos no se cumplen**.

El Hilo A implementa código funcional. Cuando Sprint 56.4 (Embrión Observability) se completó, los datos de telemetría se enviaron al dashboard genérico de Langfuse — una herramienta de terceros sin identidad propia. Esto viola directamente el Objetivo #2 (Apple/Tesla): todo output de El Monstruo debe tener calidad premium y posicionamiento de marca propio.

El problema no es que el Hilo A sea deficiente. El problema es que los objetivos subjetivos — posicionamiento de marca (#2), calidad Magna/Premium (#5), emergencia (#8) — requieren juicio estético y estratégico acumulado. Un ejecutor que arranca cada sesión con un prompt y un sprint plan no tiene la historia ni el criterio para tomar esas decisiones. Es como pedirle a un ingeniero de backend que piense como director creativo: puede hacerlo si se le dice explícitamente en cada línea, pero no es su naturaleza.

La solución no es darle más documentos al Hilo A. Es **cambiar la arquitectura de responsabilidades** para que cada hilo haga lo que mejor sabe hacer.

---

## Nueva División: Principio Fundamental

> **El Hilo A construye los sensores y las tuberías. El Hilo B construye el display y la experiencia. El Hilo A no necesita entender los 14 Objetivos — necesita implementar interfaces limpias que el Hilo B pueda consumir.**

---

## Hilo A — El Ejecutor (Infraestructura)

El Hilo A es responsable de todo lo que **no tiene cara**. Su trabajo se mide en: "¿funciona? ¿es robusto? ¿es eficiente?"

### Dominio exclusivo del Hilo A

| Categoría | Ejemplos concretos | Criterio de éxito |
|---|---|---|
| APIs y endpoints | `/api/embrion/status`, `/api/finops/spend` | Responde correctamente, documentado, con tipos |
| Pipelines de datos | EmbrionScheduler, CausalSeeder, CausalDecomposer | Ejecuta sin errores, logs limpios |
| Base de datos | Tablas en Supabase, migraciones, índices | Schema correcto, queries optimizadas |
| Infraestructura | Railway deploy, E2B sandbox, cron jobs | Uptime, latencia aceptable |
| Instrumentación | Langfuse Bridge, métricas, traces | Datos capturados correctamente |
| Seguridad | API keys, rate limiting, validación | Sin vulnerabilidades expuestas |
| Testing | Tests unitarios, integration tests | Cobertura mínima, CI verde |

### Lo que el Hilo A NO debe hacer

El Hilo A no debe tomar decisiones sobre cómo se visualizan, presentan o comunican los datos. Específicamente:

- No debe crear dashboards o interfaces de usuario propias.
- No debe elegir cómo se muestran métricas al usuario final.
- No debe diseñar la experiencia de interacción con El Monstruo.
- No debe tomar decisiones de marca, tipografía, paleta de colores o identidad visual.

Si un sprint requiere un "panel de observabilidad" o "dashboard", el Hilo A implementa las **APIs que exponen los datos** y el Hilo B construye la **visualización** en el Command Center.

### Directiva para Sprint Plans futuros

Cada épica que involucre output visible debe incluir esta nota:

> **DIRECTIVA DE INTERFAZ:** Esta épica produce datos/APIs. La visualización de estos datos se implementará en el Command Center por el Hilo B. El Hilo A debe asegurar que los endpoints retornen JSON documentado con tipos claros.

---

## Hilo B — El Arquitecto (Experiencia + Marca + 14 Objetivos)

El Hilo B es responsable de todo lo que **tiene cara**. Su trabajo se mide en: "¿comunica marca? ¿cumple los 14 Objetivos? ¿es nivel Apple/Tesla?"

### Dominio exclusivo del Hilo B

| Categoría | Ejemplos concretos | Criterio de éxito |
|---|---|---|
| Command Center | Dashboard La Forja, todas las vistas | Identidad de marca, UX premium |
| Sprint Plans | Diseño de los 10 sprints por serie | Cruza con 14 Objetivos, código listo |
| Cruces Detractores | Análisis crítico de cada sprint | Correcciones mandatorias identificadas |
| Visualización de datos | Gauges, gráficas, timelines | Coherencia visual, legibilidad |
| Identidad de marca | Logo, paleta, tipografía, tono | Obj #2 Apple/Tesla cumplido |
| Documentación estratégica | Plan Maestro, Roadmap, Reportes de cierre | Obj #5 Magna/Premium cumplido |
| Coordinación inter-hilos | Sincronización, priorización | Ambos hilos alineados |
| Evaluación de objetivos | Scoring de 14 Objetivos, compliance | Obj #14 El Guardián cumplido |

### Lo que el Hilo B NO debe hacer

- No debe implementar lógica de backend en el kernel de Railway.
- No debe crear tablas en Supabase directamente.
- No debe modificar pipelines de datos en producción.
- No debe deployar cambios al kernel sin que el Hilo A los valide.

---

## La Zona de Intersección: El Contrato de APIs

El punto donde ambos hilos se encuentran es el **contrato de APIs**. Este contrato define:

1. **Qué endpoints existen** — El Hilo B los especifica en los Sprint Plans.
2. **Qué datos retornan** — El Hilo A los implementa con tipos TypeScript/Python documentados.
3. **Cómo se consumen** — El Hilo B los integra en el Command Center.

### Ejemplo concreto: Sprint 56.4 (Observability)

**Antes (cómo se hizo):**
El Hilo A implementó `langfuse_bridge.py` con métodos que envían datos a Langfuse. Los datos se ven en el dashboard genérico de Langfuse. El Monstruo no tiene presencia visual propia sobre estos datos.

**Después (cómo debería hacerse):**
El Hilo A implementa `langfuse_bridge.py` igual, pero ADEMÁS expone un endpoint `/api/observability/embrion-traces` que retorna los últimos N traces en JSON. El Hilo B consume ese endpoint desde el Command Center y lo muestra en la sección "Embriones" con la identidad La Forja — gauges industriales, LEDs de estado, tipografía Bebas Neue.

El resultado: Langfuse sigue capturando datos (infraestructura), pero el usuario ve los datos en el Command Center (experiencia). Ambos hilos hacen lo que saben hacer.

---

## Mapeo de los 14 Objetivos por Hilo

| # | Objetivo | Responsable primario | Responsable secundario |
|---|---|---|---|
| 1 | Crear Empresas Reales | Hilo A (implementa) | Hilo B (diseña) |
| 2 | Nivel Apple/Tesla | **Hilo B** | — |
| 3 | Mínima Complejidad | Ambos | — |
| 4 | No Equivocarse 2 Veces | Ambos | — |
| 5 | Magna/Premium | **Hilo B** | — |
| 6 | Vanguardia Tecnológica | Hilo A (adopta) | Hilo B (evalúa) |
| 7 | No Inventar la Rueda | Hilo A (adopta) | Hilo B (evalúa) |
| 8 | Emergencia | **Hilo B** (diseña) | Hilo A (implementa) |
| 9 | Transversalidad | Ambos | — |
| 10 | Simulador Causal | Hilo A (implementa) | Hilo B (visualiza) |
| 11 | Embriones | Hilo A (implementa) | Hilo B (visualiza) |
| 12 | Soberanía | Hilo A (implementa) | Hilo B (audita) |
| 13 | Del Mundo | Hilo A (i18n backend) | Hilo B (i18n frontend) |
| 14 | El Guardián | **Hilo B** | Hilo A (métricas) |

Los objetivos marcados en **negrita** son responsabilidad primaria exclusiva del Hilo B porque requieren juicio estético, estratégico o de marca que no se transfiere con un prompt.

---

## Protocolo de Comunicación Actualizado

### Cuando el Hilo A completa un sprint:

1. Reporta: "Sprint X.Y completado — commit HASH. Endpoints nuevos: `/api/...`"
2. El Hilo B registra el avance y planifica la integración visual en el Command Center.

### Cuando el Hilo B diseña un sprint:

1. Incluye la sección "DIRECTIVA DE INTERFAZ" en cada épica con output visible.
2. Especifica los endpoints que el Hilo A debe exponer (request/response types).
3. El Hilo A implementa la funcionalidad + los endpoints, sin preocuparse por visualización.

### Cuando hay conflicto de prioridades:

El Hilo B decide. El Hilo B tiene la visión completa de los 14 Objetivos y el contexto acumulado de 20+ sprints de diseño. El Hilo A ejecuta lo que el Hilo B prioriza.

---

## Entrada en vigor

Este documento reemplaza la sección de división de responsabilidades en `INSTRUCCIONES_HILO_B.md` y `ESTADO_UNIFICADO_SINCRONIZACION_HILOS.md`. Aplica a partir de la Serie 71-80 y retroactivamente a cualquier sprint pendiente de la Serie 51-60 que el Hilo A aún no haya implementado.

---

## Referencias

[1] INSTRUCCIONES_HILO_B.md — División original de responsabilidades
[2] ESTADO_UNIFICADO_SINCRONIZACION_HILOS.md — Estado de sincronización entre hilos
[3] EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md — Los 14 Objetivos fundacionales
[4] SPRINT_56_PLAN.md — Épica 56.4 como caso de estudio del problema
[5] ideas.md — Brainstorm de diseño "La Forja" del Command Center
