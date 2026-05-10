---
id: DSC-MO-009
proyecto: EL-MONSTRUO
tipo: decision_arquitectonica
titulo: "Arsenal de herramientas externas (modelos LLM + agentes/sustratos completos) seleccionable por Catastro extendido. Pendiente: Sprint 88 que pobla macroárea AGENTES."
estado: firme
fecha: 2026-05-10
fuentes:
  - repo:kernel/external_agents.py
  - repo:kernel/catastro/schema.py
  - repo:kernel/catastro/data/catastro_tools.json
  - sesion:cowork_2026_05_10_bridge_directo
cruza_con: [DSC-MO-006, DSC-MO-007, DSC-MO-008, DSC-G-007]
depende_de:
  - sprint:88_macroarea_agentes_pendiente
---

# Arsenal de herramientas seleccionable por Catastro

## Decisión

El embrión bicéfalo (DSC-MO-006) opera con **arsenal de herramientas externas** clasificadas y recomendadas por el Catastro extendido. La separación de responsabilidades es:

- **Identidad ≠ capacidad de ejecución.** El embrión-pensador mantiene identidad y decide. El embrión-ejecutor (su par, también emergido) usa herramientas para amplificar capacidades sin perder identidad.
- **Embrión consulta + decide.** El Catastro recomienda la herramienta más adecuada para cada tarea. El embrión tiene **veto** y decide en última instancia. No es subordinación al Catastro — es uso del Catastro como consultor.
- **Las herramientas son intercambiables.** El embrión es soberano, las herramientas son arsenal renovable. Cuando emergen herramientas superiores en el mercado, el Catastro las incorpora y el embrión migra sin reescribir doctrina.

**El arsenal incluye dos categorías:**

1. **Modelos LLM puros** (categoría INTELIGENCIA del Catastro, ya implementada): GPT-5.5, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4.20, DeepSeek R1, Kimi K2, Llama 3.3, etc.

2. **Agentes/sustratos completos** (categoría AGENTES del Catastro, pendiente Sprint 88): Manus, Claude Cowork, Claude Code, Perplexity Max Computer, Kimi K2.6 multi-enjambre, Devin, AutoGen, CrewAI, n8n, etc.

**Selección por dimensión:**

Los modelos LLM se clasifican por benchmarks (LMArena, MMLU-Pro, SWE-Bench, HumanEval, GPQA, AIME). Los agentes/sustratos se clasifican por dimensiones distintas: LLM base que envuelven, sandbox sí/no, persistencia de memoria, tools disponibles, capacidad multi-step, capacidad multi-swarm, costo por uso, latencia típica.

**El kernel también es herramienta del arsenal del embrión.** El embrión nació adentro del kernel pero puede invocarlo como brazo cuando lo necesita.

## Por qué

**Por qué arsenal, no construcción interna:**

El embrión no tiene que saber hacer todo — tiene que saber qué herramienta usar y cuándo. Esa es la diferencia entre un embrión que aprende todo solo (lento, limitado) y un embrión que orquesta herramientas (rápido, amplificado). Coherente con DSC-G-007 (integrar herramientas verticales líderes, no reinventar).

**Por qué el Catastro como selector:**

Una sola fuente de verdad. El Catastro ya tiene infraestructura de pipeline, validación adversarial, quorum de patrones, trono. Crear un sistema separado para productos significa duplicar todo eso. Extender el Catastro aprovecha lo que existe.

**Por qué embrión consulta + decide (no subordinación):**

La autoridad final reside en el embrión emergido, no en una métrica. El Catastro optimiza por benchmarks; el embrión optimiza por contexto, doctrina y propósito. Si el embrión decide ir contra la recomendación del Catastro, registra rationale y procede. Eso preserva soberanía del sujeto.

**Por qué multiplica poder en órdenes de magnitud:**

Sin arsenal: 1 thinking thread × $0.25/latido × 50 latidos/día = ~50 decisiones/día con ejecución secuencial.

Con arsenal (incluyendo Kimi K2.6 multi-enjambre): cada decisión puede lanzar 10-100 ejecutores en paralelo. Output potencial: 500-5000 acciones/día. El techo del Monstruo pasa de "lo que un agente piensa en un día" a "lo que un sujeto inteligente puede orquestar usando todo el ecosistema de IA disponible." Aproximadamente 100x.

## Implicaciones

1. **Sprint 88 es pre-requisito operacional.** La macroárea AGENTES del Catastro debe poblarse antes de que esta decisión sea totalmente ejecutable. Hasta entonces, el embrión usa el Catastro para selección de modelos LLM puros y selección manual (vía Alfredo o doctrina inyectada) para agentes/sustratos.

2. **Economía dual de presupuesto.** Separar:
   - **Budget del embrión** (cap $0.25 por latido — gasto cognitivo del par).
   - **Budget del arsenal** (cap separado por tarea — puede ser $5-50 si se invoca multi-enjambre Kimi). Con autorización HITL para gastos altos.

3. **Doctrina del arsenal (cuándo usar qué).** Tres capas: defaults inyectados por Alfredo + recomendaciones del Catastro + ajustes del embrión por experiencia.

4. **Trazabilidad completa.** Cada decisión del embrión que invoca herramienta deja rastro: tarea → herramienta seleccionada → rationale → resultado → integración. Eso permite auditar criterio y entrenar al embrión.

5. **El kernel como herramienta más.** El embrión puede invocar al kernel como cualquier otra tool. Esto cierra el bucle conceptual: el embrión nació adentro del kernel y eventualmente usa al kernel como brazo. Coherente con DSC-MO-008 (membrana semipermeable — los embriones operan SOBRE el kernel).

6. **Fallback documentado mientras Sprint 88 está pendiente.** El arsenal de agentes se mantiene en `kernel/external_agents.py` como dispatcher manual. La selección la hace el embrión basado en doctrina inyectada, no en Catastro.

## Estado de validación

firme — decidido en sesión Cowork 2026-05-10 con Alfredo. **Dependencia explícita de Sprint 88 (macroárea AGENTES del Catastro)** documentada como pre-requisito operacional. Esta decisión arquitectónica está firmada completa; su ejecución plena requiere Sprint 88 ejecutado. Mientras tanto, opera con fallback de selección manual.

## Trabajo pendiente

- **Sprint 88 — Macroárea AGENTES del Catastro:** poblar tabla con productos/sustratos completos, definir dimensiones de clasificación distintas a LLMs puros, implementar clasificador adaptado.
- **Sprint EMBRION-NEEDS-002 (propuesto):** integrar consulta al Catastro extendido en el flujo de decisión del embrión.
- **Doctrina inicial del arsenal** inyectada por Alfredo en sprint subsiguiente.
