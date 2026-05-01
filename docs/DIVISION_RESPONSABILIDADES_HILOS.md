# División de Responsabilidades: Hilo A (Ejecutor) vs Hilo B (Arquitecto)

**Documento normativo — Vigente a partir del 1 de mayo de 2026**
**Versión:** 2.1 — Corrige el error de v2.0 que separaba infraestructura de marca
**Autor:** Hilo B (Arquitecto), validado por Alfredo Góngora

---

## Corrección Crítica (v2.1)

La versión 2.0 de este documento contenía un error fundamental: separaba "infraestructura" de "experiencia y marca", como si fueran mundos distintos. Decía que "el Hilo A construye los sensores y las tuberías, el Hilo B construye el display y la experiencia".

**Esto es incorrecto.** Los sensores y las tuberías SON parte de la experiencia y la marca. Cuando un endpoint retorna un error genérico `{"error": "internal server error"}` en lugar de `{"error": "embrion_heartbeat_timeout", "embrion_id": "alpha-01", "suggestion": "verificar scheduler"}`, eso no es solo un problema técnico — es un problema de marca. Apple no tiene "backend sin marca". Tesla no tiene "firmware sin identidad".

La corrección: **los 14 Objetivos Maestros aplican a TODA decisión, incluyendo infraestructura**. Ambos hilos deben internalizarlos.

---

## Principio Fundamental (Corregido)

> **Ambos hilos operan bajo los 14 Objetivos Maestros. El Hilo A no está exento de marca, calidad premium, o documentación exhaustiva solo porque trabaja en backend. Cada línea de código, cada nombre de endpoint, cada schema de base de datos ES la marca de El Monstruo.**

---

## Hilo A — El Ejecutor

El Hilo A implementa la funcionalidad técnica del kernel. Su dominio principal es código Python, APIs, pipelines, base de datos, y deploys en Railway.

### Responsabilidades

| Categoría | Ejemplos | Criterio de éxito |
|---|---|---|
| APIs y endpoints | `/api/embrion/status`, `/api/finops/spend` | Funcional, documentado, con tipos, naming con identidad |
| Pipelines de datos | EmbrionScheduler, CausalSeeder, CausalDecomposer | Sin errores, logs con contexto, trazabilidad |
| Base de datos | Tablas en Supabase, migraciones, índices | Schema correcto, naming consistente, documentado |
| Infraestructura | Railway deploy, E2B sandbox, cron jobs | Uptime, latencia, configuración documentada |
| Instrumentación | Langfuse Bridge, métricas, traces | Datos capturados Y expuestos via API para el Command Center |
| Seguridad | API keys, rate limiting, validación | Sin vulnerabilidades, fail-closed |
| Testing | Tests unitarios, integration tests | Cobertura mínima, CI verde |

### Directivas de los 14 Objetivos para el Hilo A

Estas directivas aplican a CADA sprint que el Hilo A implemente:

**Obj #2 (Apple/Tesla) en infraestructura:**
- Los nombres de endpoints deben ser descriptivos y consistentes, no genéricos (`/api/embrion/heartbeat` no `/api/data/get`)
- Los mensajes de error deben tener personalidad y contexto, no solo status codes
- Los schemas de respuesta deben ser auto-documentados con campos descriptivos
- Los logs deben ser legibles por humanos, no solo por máquinas

**Obj #5 (Magna/Premium) en infraestructura:**
- Cada endpoint debe tener docstring con descripción, parámetros, y ejemplo de respuesta
- Cada tabla nueva debe tener comentario explicando su propósito
- Cada decisión de diseño debe quedar documentada en el commit message o en un comentario

**Obj #9 (Transversalidad) en infraestructura:**
- Todo módulo que genere datos debe exponer un endpoint para que el Command Center los consuma
- No crear silos: si Langfuse captura datos, debe existir también un endpoint propio que los exponga
- Los datos del kernel deben ser consumibles sin necesidad de acceder a herramientas de terceros

**Obj #12 (Soberanía) en infraestructura:**
- Cada dependencia externa debe tener una alternativa documentada
- No crear lock-in con un solo proveedor sin plan de migración

---

## Hilo B — El Arquitecto

El Hilo B diseña la estrategia, planifica los sprints, evalúa el cumplimiento de los 14 Objetivos, y construye todo lo que tiene interfaz visual.

### Responsabilidades

| Categoría | Ejemplos | Criterio de éxito |
|---|---|---|
| Sprint Plans | Diseño de sprints con código listo | Cruza con 14 Objetivos, directivas de marca en cada épica |
| Cruces Detractores | Análisis crítico de cada sprint | Correcciones mandatorias identificadas y accionables |
| Command Center | Dashboard La Forja, todas las vistas | Identidad de marca, UX premium, datos reales |
| Documentación estratégica | Plan Maestro, Roadmap, Reportes | Obj #5 Magna/Premium cumplido |
| Evaluación de objetivos | Scoring de 14 Objetivos, compliance | Obj #14 El Guardián cumplido |
| Coordinación inter-hilos | Sincronización, priorización | Ambos hilos alineados |

### Directiva adicional para el Hilo B

Cada Sprint Plan que el Hilo B diseñe debe incluir, dentro de cada épica (no solo al final como cruce):

1. **Checklist de marca** — Preguntas concretas que el Hilo A debe responder antes de dar por cerrada la épica
2. **Ejemplo de naming** — Cómo deben llamarse los endpoints, tablas, y variables de esta épica
3. **Formato de respuesta** — Cómo debe verse el JSON de respuesta (no solo los campos, sino el estilo)
4. **Endpoint para Command Center** — Qué endpoint debe exponerse para que el Hilo B lo consuma visualmente

---

## El Contrato entre Hilos

El punto de encuentro sigue siendo el contrato de APIs, pero ahora con una dimensión adicional: **el contrato incluye estándares de marca**.

### Ejemplo: Sprint 56.4 (Observability) — Cómo debería haberse hecho

**Lo que se hizo (v1):**
El Hilo A implementó `langfuse_bridge.py` con métodos que envían datos a Langfuse. Los datos se ven en el dashboard genérico de Langfuse. El Monstruo no tiene presencia visual propia.

**Lo que debería hacerse (v2):**
El Hilo A implementa `langfuse_bridge.py` igual, pero ADEMÁS:
1. Expone `/api/observability/embrion-traces` que retorna los últimos N traces en JSON con naming de marca
2. Expone `/api/observability/embrion-health` que retorna el estado de salud de cada embrión
3. Cada trace incluye campos descriptivos: `embrion_name`, `action_display_name`, `quality_score_label`
4. Los errores retornan mensajes con contexto: `"El embrión alpha-01 no respondió al heartbeat en 30s. Última actividad: seeding cycle #12"`

El Hilo B consume esos endpoints desde el Command Center y los muestra con identidad La Forja.

El resultado: Langfuse sigue capturando datos (está bien como backend de instrumentación), pero el usuario NUNCA necesita ir a Langfuse. Ve todo en el Command Center, con la marca de El Monstruo.

---

## Mapeo de los 14 Objetivos por Hilo

| # | Objetivo | Hilo A | Hilo B |
|---|---|---|---|
| 1 | Crear Empresas Reales | Implementa funcionalidad | Diseña estrategia |
| 2 | Nivel Apple/Tesla | **Naming, errores, schemas con identidad** | **Visualización, UX, identidad visual** |
| 3 | Mínima Complejidad | Código simple y limpio | Diseño simple y claro |
| 4 | No Equivocarse 2 Veces | Tests, validación, logs | Cruces detractores, reviews |
| 5 | Magna/Premium | **Docstrings, comments, commit messages** | **Documentación estratégica** |
| 6 | Vanguardia Tecnológica | Adopta herramientas modernas | Evalúa y recomienda |
| 7 | No Inventar la Rueda | Busca antes de construir | Audita decisiones build vs buy |
| 8 | Emergencia | Implementa comportamiento emergente | Diseña las condiciones |
| 9 | Transversalidad | **Expone APIs para todo módulo** | **Consume APIs en Command Center** |
| 10 | Simulador Causal | Implementa motor | Visualiza predicciones |
| 11 | Embriones | Implementa colmena | Visualiza estado |
| 12 | Soberanía | **Documenta alternativas** | **Audita dependencias** |
| 13 | Del Mundo | i18n en backend | i18n en frontend |
| 14 | El Guardián | Expone métricas de compliance | Evalúa y reporta |

Los campos en **negrita** son las directivas específicas que cada hilo debe cumplir para ese objetivo.

---

## Protocolo de Comunicación

### Cuando el Hilo A completa un sprint:

1. Reporta: "Sprint X.Y completado — commit HASH"
2. Lista endpoints nuevos con ejemplo de respuesta
3. Confirma que el checklist de marca de la épica está cumplido

### Cuando el Hilo B diseña un sprint:

1. Incluye checklist de marca en cada épica
2. Especifica endpoints que el Hilo A debe exponer (con ejemplo de naming y respuesta)
3. Incluye directivas de los 14 Objetivos relevantes dentro del código, no solo como texto

### Cuando hay conflicto de prioridades:

El Hilo B decide la prioridad estratégica. El Hilo A decide la implementación técnica. Si hay conflicto entre "funciona" y "tiene marca", se resuelve haciendo ambas cosas — no sacrificando una por la otra.

---

## Entrada en vigor

Este documento v2.1 reemplaza la v2.0. Aplica a partir de la Serie 71-80 y retroactivamente a cualquier sprint pendiente. La regla de que los 14 Objetivos aplican a TODO está también en `~/AGENTS.md` para sobrevivir compactaciones de memoria.

---

## Referencias

[1] EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md — Los 14 Objetivos fundacionales
[2] SPRINT_56_PLAN.md — Épica 56.4 como caso de estudio del problema
[3] AGENTS.md — Reglas duras que sobreviven compactación
[4] ideas.md — Brainstorm de diseño "La Forja" del Command Center
