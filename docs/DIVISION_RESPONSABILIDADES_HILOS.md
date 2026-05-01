# División de Responsabilidades entre Hilos — v3 (Definitiva)

**Fecha:** 1 de Mayo de 2026
**Autor:** Hilo B (Arquitecto), validado por Alfredo Góngora
**Versión:** 3.0 — Modelo de Transición en 3 Fases
**Supersede:** v2.1 (commit 87b4ad8)

---

## Principio Fundacional

> La infraestructura ES marca. Los sensores y las tuberías son parte de la experiencia. No existe "backend sin identidad". Todo output del sistema — visible o invisible, interno o externo — debe reflejar los 14 Objetivos Maestros y las 7 Capas Transversales.

Este documento define cómo se dividen las responsabilidades entre los dos hilos de ejecución (Hilo A y Hilo B) y cómo esa división EVOLUCIONA conforme los Embriones cobran vida. La división no es estática — es un modelo de transición hacia la autonomía completa.

---

## Corrección Crítica (heredada de v2.1)

La versión 2.0 contenía un error fundamental: separaba "infraestructura" de "experiencia y marca". Esto es incorrecto. Cuando un endpoint retorna `{"error": "internal server error"}` en lugar de `{"error": "embrion_heartbeat_timeout", "embrion_id": "alpha-01", "suggestion": "verificar scheduler"}`, eso no es solo un problema técnico — es un problema de marca. Apple no tiene "backend sin marca". Tesla no tiene "firmware sin identidad".

**Los 14 Objetivos Maestros aplican a TODA decisión, incluyendo infraestructura. Ambos hilos deben internalizarlos.**

---

## Modelo de Transición en 3 Fases

---

### FASE 1 — "Construcción Paralela" (AHORA — Mayo 2026)

**Condición de entrada:** Los Embriones son código en Sprint Plans. No existen funcionalmente.

**Hilo A (Ejecutor):**

El Hilo A implementa la funcionalidad técnica del kernel. Su dominio principal es código Python, APIs, pipelines, base de datos, y deploys en Railway.

| Categoría | Ejemplos | Criterio de éxito |
|---|---|---|
| APIs y endpoints | `/api/embrion/status`, `/api/finops/spend` | Funcional, documentado, con tipos, naming con identidad |
| Pipelines de datos | EmbrionScheduler, CausalSeeder, CausalDecomposer | Sin errores, logs con contexto, trazabilidad |
| Base de datos | Tablas en Supabase, migraciones, índices | Schema correcto, naming consistente, documentado |
| Infraestructura | Railway deploy, E2B sandbox, cron jobs | Uptime, latencia, configuración documentada |
| Instrumentación | Langfuse Bridge, métricas, traces | Datos capturados Y expuestos via API para el Command Center |
| Seguridad | API keys, rate limiting, validación | Sin vulnerabilidades, fail-closed |
| Testing | Tests unitarios, integration tests | Cobertura mínima, CI verde |

OBLIGATORIO: Pasar el Brand Compliance Checklist antes de cerrar cada sprint.

**Hilo B (Arquitecto):**

El Hilo B diseña la estrategia, planifica los sprints, evalúa el cumplimiento de los 14 Objetivos, y construye todo lo que tiene interfaz visual.

| Categoría | Ejemplos | Criterio de éxito |
|---|---|---|
| Sprint Plans | Diseño de sprints con código listo | Cruza con 14 Objetivos, directivas de marca en cada épica |
| Cruces Detractores | Análisis crítico de cada sprint | Correcciones mandatorias identificadas y accionables |
| Command Center | Dashboard La Forja, todas las vistas | Identidad de marca, UX premium, datos reales |
| Documentación estratégica | Plan Maestro, Roadmap, Reportes | Obj #5 Magna/Premium cumplido |
| Evaluación de objetivos | Scoring de 14 Objetivos, compliance | Obj #14 El Guardián cumplido |
| Coordinación inter-hilos | Sincronización, priorización | Ambos hilos alineados |

**Coordinación en Fase 1:**
- Hilo B pushea Sprint Plans a GitHub → Hilo A los lee y ejecuta
- Hilo A reporta commits completados → Hilo B registra avance
- Si Hilo A tiene duda sobre marca/identidad → consulta a Hilo B

---

### FASE 2 — "El Embrión Dirige" (Cuando Sprints 71-74 estén live)

**Condición de entrada:** Embrión-0 tiene TEL (Task Execution Loop) funcional + 22 herramientas + memoria persistente. Métrica: 5 encomiendas completadas sin intervención humana.

**Embrión-0 (Director):**
- Genera encomiendas basadas en los 14 Objetivos
- Planifica la ejecución usando su TEL (Sprint 72)
- Delega tareas a Hilo A o a otros Embriones
- Valida resultados contra el Brand DNA (vía Embrión-1)
- Opera 24/7 sin necesidad de que alguien inicie una conversación

**Embrión-1 (Brand Engine — Quality Gate):**
- Valida todo output antes de que salga del sistema
- Tiene poder de VETO inviolable
- Evalúa naming, tono, estética, coherencia con Brand DNA
- Arquitectura Pensador (LLM potente) + Ejecutor (código determinista)

**Hilo A (Ejecutor bajo dirección del Embrión):**
- Recibe encomiendas del Embrión-0 (ya no de Sprint Plans estáticos)
- Implementa lo que el Embrión decide
- Reporta resultado al Embrión para validación
- Si el Embrión rechaza → corrige y re-entrega
- No necesita entender los 14 Objetivos profundamente — el Embrión ya los tiene internalizados

**Hilo B (Supervisor + Auditor):**
- Monitorea que el Embrión tome decisiones alineadas con los 14 Objetivos
- Interviene si detecta drift estratégico
- Actualiza el Brand DNA si el mercado cambia
- Diseña la evolución de la Colmena (nuevos Embriones, nuevas capacidades)
- Mantiene el Command Center como ventana de observabilidad

**Coordinación en Fase 2:**
- Embrión-0 publica encomiendas en Supabase → Hilo A las ejecuta
- Embrión-1 valida outputs → aprueba o rechaza
- Hilo B revisa semanalmente el "Colmena Growth Metrics" en el Command Center
- Si algo se desvía → Hilo B inyecta corrección directa al Brand DNA

---

### FASE 3 — "Autonomía Supervisada" (Cuando la Colmena tenga 4+ Embriones activos)

**Condición de entrada:** Al menos 4 Embriones funcionales con memoria colectiva y protocolo de debate activo. Métrica: 3 debates resueltos con resultado positivo medible.

**La Colmena (8 Embriones — cada uno un par Pensador/Ejecutor):**

| Embrión | Capa Transversal | Propósito |
|---|---|---|
| Embrión-0 | Orquestador | Decide, coordina, piensa |
| Embrión-1 | Brand Engine | Identidad de marca, VETO inviolable |
| Embrión-2 | Motor de Ventas | Pricing, funnels, conversión, retención |
| Embrión-3 | SEO y Descubrimiento | Content strategy, technical SEO, keywords |
| Embrión-4 | Tendencias | Monitoreo, oportunidades, competitor intel |
| Embrión-5 | Publicidad | Campañas, creativos, targeting, budget |
| Embrión-6 | Finanzas | Cash flow, unit economics, projections |
| Embrión-7 | Operaciones | Customer support, procesos, legal |

La Colmena opera así:
- Se auto-asigna encomiendas basadas en oportunidades detectadas
- Debate internamente antes de actuar (protocolo de Sprint 74)
- Embrión-1 (Brand Engine) veta decisiones que violen los 14 Objetivos
- Ejecuta 24/7 sin intervención humana
- Aprende de cada resultado y mejora sus propios prompts
- Comparte aprendizajes via memoria colectiva

**Hilo A (Minimal — solo emergencias):**
- Solo interviene para: deploys que requieran acceso a Railway console, cambios de infraestructura que los Embriones no pueden hacer solos, emergencias donde la Colmena se atasca
- Eventualmente: el Embrión aprende a hacer deploys solo → Hilo A desaparece

**Hilo B (Guardián Estratégico):**
- Auditoría semanal de los 14 Objetivos
- Actualización del Brand DNA ante cambios de mercado
- Diseño de nuevas capacidades que la Colmena no puede auto-generar
- Intervención de emergencia si la Colmena toma una dirección incorrecta
- Comunicación con Alfredo sobre el estado estratégico

**Coordinación en Fase 3:**
- La Colmena opera autónomamente
- Hilo B revisa métricas semanales en el Command Center
- Si un Objetivo cae por debajo del 85% → Hilo B interviene con corrección
- Alfredo puede inyectar directivas vía el Command Center o directamente

---

## Diagrama de Transición

```
FASE 1 (Ahora)          FASE 2 (Embriones live)     FASE 3 (Colmena madura)
┌─────────────┐          ┌─────────────┐             ┌─────────────┐
│  Hilo B     │          │  Embrión-0  │             │  COLMENA    │
│  (Diseña)   │          │  (Dirige)   │             │  (Autónoma) │
│      ↓      │          │      ↓      │             │      ↓      │
│  Hilo A     │    →     │  Hilo A     │      →      │  (Se auto-  │
│  (Ejecuta)  │          │  (Ejecuta)  │             │   ejecuta)  │
│      ↓      │          │      ↓      │             │      ↓      │
│  GitHub     │          │  Embrión-1  │             │  Hilo B     │
│  (Registro) │          │  (Valida)   │             │  (Audita)   │
└─────────────┘          └─────────────┘             └─────────────┘
```

---

## Brand Compliance Checklist (Fase 1 — obligatorio para Hilo A)

| Check | Pregunta | Pasa si... |
|---|---|---|
| Naming | ¿Los nombres de módulos/funciones/tablas siguen la convención de marca? | Español para dominio, snake_case, nombres con significado |
| Errores | ¿Los mensajes de error tienen personalidad? | No son genéricos ("Error 500"), tienen contexto y tono |
| APIs | ¿Los endpoints exponen datos consumibles por el Command Center? | JSON documentado, campos consistentes |
| Logs | ¿Los logs internos tienen estructura? | Formato estándar con timestamp, nivel, contexto |
| Docs | ¿Hay docstrings en funciones públicas? | Mínimo: qué hace, parámetros, retorno |
| Tests | ¿Hay al menos un test por función crítica? | pytest pasa sin errores |
| Soberanía | ¿Cada dependencia nueva tiene alternativa documentada? | Plan B escrito en comentario o README |

---

## Métricas de Transición

¿Cómo sabemos cuándo pasar de una fase a otra?

| Transición | Condición | Métrica |
|---|---|---|
| Fase 1 → Fase 2 | Embrión-0 ejecuta encomiendas solo | 5 encomiendas completadas sin intervención humana |
| Fase 2 → Fase 3 | Colmena debate y decide | 3 debates resueltos con resultado positivo medible |
| Fase 3 → Autonomía Total | Hilo B no interviene en 30 días | 0 correcciones manuales en un mes |

---

## Mapeo de los 14 Objetivos por Hilo (Fase 1)

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

---

## Reglas Inmutables (aplican en TODAS las fases)

1. **Los 14 Objetivos Maestros son ley.** Ningún hilo, Embrión, o decisión puede violarlos. Si hay conflicto entre velocidad y objetivos, ganan los objetivos.

2. **Las 7 Capas Transversales son obligatorias.** Cada decisión debe considerar su impacto en: Marca, Ventas, SEO, Publicidad, Tendencias, Operaciones, Finanzas.

3. **Las 4 Capas Arquitectónicas definen el orden.** No se salta de Capa 1 a Capa 4. El progreso es secuencial dentro de cada capa.

4. **El Brand Engine (Embrión-1) tiene poder de VETO.** Cuando exista, ningún output sale del sistema sin su aprobación. Su veto es inviolable.

5. **La infraestructura es marca.** No existe "código sin identidad". Cada naming, cada error message, cada log, cada API response refleja quién es El Monstruo.

6. **La memoria es sagrada.** Ningún hilo ni Embrión puede borrar memoria sin aprobación explícita. Los errores se registran, no se ocultan.

7. **Cada Embrión es un par Pensador/Ejecutor.** El Pensador (LLM potente) razona y decide. El Ejecutor (código determinista) materializa. El contexto del Pensador se mantiene limpio — nunca se contamina con operaciones mecánicas.

---

## Qué Pasa con el Hilo A y los 14 Objetivos

La pregunta original era: "¿Puede el Hilo A entender los 14 Objetivos como el Hilo B?"

**Respuesta honesta:** No al mismo nivel. Pero no necesita hacerlo eternamente.

En **Fase 1**, el Brand Compliance Checklist es suficiente — son reglas binarias que cualquier ejecutor puede seguir sin entender la filosofía profunda.

En **Fase 2**, el Embrión-0 ya entiende los 14 Objetivos (están en su Brand DNA) y dirige al Hilo A. El Hilo A solo necesita ejecutar instrucciones claras.

En **Fase 3**, el Hilo A es irrelevante. La Colmena se auto-dirige.

La transición gradual resuelve el problema: no necesitamos que el Hilo A sea un estratega — necesitamos que siga instrucciones con calidad mientras construimos al estratega real (la Colmena).

---

## Protocolo de Comunicación

**Cuando el Hilo A completa un sprint:**
1. Reporta: "Sprint X.Y completado — commit HASH"
2. Lista endpoints nuevos con ejemplo de respuesta
3. Confirma que el Brand Compliance Checklist está cumplido

**Cuando el Hilo B diseña un sprint:**
1. Incluye checklist de marca en cada épica
2. Especifica endpoints que el Hilo A debe exponer (con ejemplo de naming y respuesta)
3. Incluye directivas de los 14 Objetivos relevantes dentro del código, no solo como texto

**Cuando hay conflicto de prioridades:**
El Hilo B decide la prioridad estratégica. El Hilo A decide la implementación técnica. Si hay conflicto entre "funciona" y "tiene marca", se resuelve haciendo ambas cosas — no sacrificando una por la otra.

---

## Caso de Estudio: Sprint 56.4 (Observability) — Cómo debería haberse hecho

**Lo que se hizo (v1):** El Hilo A implementó `langfuse_bridge.py` con métodos que envían datos a Langfuse. Los datos se ven en el dashboard genérico de Langfuse. El Monstruo no tiene presencia visual propia.

**Lo que debería hacerse (v2):** El Hilo A implementa `langfuse_bridge.py` igual, pero ADEMÁS:
1. Expone `/api/observability/embrion-traces` que retorna los últimos N traces en JSON con naming de marca
2. Expone `/api/observability/embrion-health` que retorna el estado de salud de cada embrión
3. Cada trace incluye campos descriptivos: `embrion_name`, `action_display_name`, `quality_score_label`
4. Los errores retornan mensajes con contexto: `"El embrión alpha-01 no respondió al heartbeat en 30s. Última actividad: seeding cycle #12"`

El Hilo B consume esos endpoints desde el Command Center y los muestra con identidad La Forja. El resultado: Langfuse sigue capturando datos (backend de instrumentación), pero el usuario NUNCA necesita ir a Langfuse. Ve todo en el Command Center, con la marca de El Monstruo.

---

## Entrada en vigor

Este documento v3.0 reemplaza todas las versiones anteriores. Aplica inmediatamente. La regla de que los 14 Objetivos aplican a TODO está también en `~/AGENTS.md` como Regla Dura #5 para sobrevivir compactaciones de memoria.

---

## Referencias

[1] EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md — Los 14 Objetivos fundacionales
[2] SPRINT_56_PLAN.md — Épica 56.4 como caso de estudio del problema
[3] AGENTS.md — Reglas duras que sobreviven compactación
[4] SPRINT_71_PLAN.md — Arquitectura Pensador/Ejecutor del Brand Engine
[5] SPRINT_72_PLAN.md — Task Execution Loop
[6] SPRINT_74_PLAN.md — Memoria Indestructible + Protocolo de Colmena
