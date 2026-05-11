---
title: "CANON — Metodologías de Productividad y el Corte Epistemológico de los Sabios"
estado: "Válido y Verificado"
version: "1.5"
fecha_validacion: "2026-05-07"
fecha_corte_epistemologico: "2025-01"
autor_hilo: "Manus paralelo (Hilo B – Ejecutor)"
proposito: "Single Source of Truth (SSOT) para inyectar contexto a los Sabios y alinear el diseño arquitectónico de El Monstruo en lo relativo a metodologías de productividad."
clasificacion: "Documento Canónico — Reutilizable como payload"
zonas_prohibidas_respetadas: ["kernel/embriones/*", "kernel/auth.py"]
relacionado_con:
  - "14 Objetivos Maestros (especialmente Obj #2 calidad premium, Obj #4 no equivocarse 2x, Obj #9 transversalidad)"
  - "7 Capas Transversales (especialmente Resiliencia Agéntica)"
  - "Regla Dura #1, #2 y #3 de AGENTS.md"
  - "DSC-G-014 (pipeline técnico vs comercializable)"
proximas_revisiones:
  - "Cuando se valide Esp #11 en caso de uso real"
  - "Cuando un sabio nuevo (post Mayo 2026) cambie su knowledge cutoff"
  - "Cuando aparezca una metodología novedosa que cruce el filtro de los 4 ejes (temporal/cobertura/ratificación/adopción)"
  - "Después de cada validación con enjambre de sabios v7.3"
---

# CANON — Metodologías de Productividad y el Corte Epistemológico de los Sabios

## 1. Resumen Ejecutivo

El Monstruo no puede diseñarse asumiendo que los Sabios (los 6 LLMs frontera) conocen el estado actual del arte en metodologías de productividad. La mayoría tiene cortes de entrenamiento entre Octubre 2023 y Enero 2026, mientras que cuatro frameworks críticos (Context Engineering, AI Second Brain, Vibe Coding/Software 3.0, Agentic Workflows) emergieron o pivotaron entre 2025 y 2026.

Este documento fija una frontera segura — Enero 2025 — para distinguir lo "Histórico" (que los Sabios dominan) de lo "Novedoso" (que requiere inyección de contexto), cataloga ambas familias, traduce los hallazgos en oportunidades concretas para el diseño de El Monstruo, y define un protocolo operativo para consultar a los Sabios sin contaminar las decisiones con respuestas obsoletas.

## 2. El Corte Epistemológico: Enero 2025

Surge del mínimo común denominador entre los cortes de entrenamiento "duros" (sin web search) de los 6 Sabios.

Consecuencias operativas: toda metodología anterior a Enero 2025 puede consultarse directamente con los Sabios. Toda metodología posterior debe inyectarse explícitamente como payload de contexto antes de pedirles que la apliquen. La "novedad" no es solo temporal: una metodología post-2025 con cobertura mediática masiva sí puede llegar a los Sabios vía web search; una nicho permanecerá invisible por meses.

Cuatro ejes de clasificación: temporal, cobertura mediática, ratificación, adopción en herramientas.

## 3. Cortes de Entrenamiento de los 6 Sabios

| Sabio | Cutoff duro | Web Search | Confiabilidad |
|---|---|---|---|
| GPT-5.5 (OpenAI) | Agosto 2025 | Sí | Nivel 2 (Probable) |
| Claude Opus 4.7 (Anthropic) | Enero 2026 | Sí | Nivel 1 (Verificado) |
| Gemini 3.1 Pro (Google) | Enero 2025 | Sí | Nivel 2 (Probable) |
| Grok 4 (xAI) | Nov 2024 / Jul 2025 | Sí | Nivel 3 (Especulativo) |
| DeepSeek R1 | Octubre 2023 | Online sí | Nivel 3 |
| Perplexity Sonar | N/A web-grounded | Sí (core) | Nivel 3 |

Decisiones críticas deben priorizar Sabios Nivel 1 o 2. Aunque 5/6 pueden hacer web search, su comportamiento por defecto privilegia su entrenamiento.

## 4. Las 10+2 Especialidades — Criterio Organizacional

Las metodologías no se eligen por preferencia, **se prescriben por diagnóstico**. Cada metodología nace como respuesta a un dolor-raíz humano específico.

### 4.1 Las 10 Especialidades Verticales

| # | Especialidad | Dolor-raíz | Detectable | Metodologías |
|---|---|---|---|---|
| 1 | Captura cognitiva | Mente se desborda | Alta | GTD, Bullet Journal, BASB, AI Second Brain |
| 2 | Priorización | Más urgente que tiempo | Alta | Eisenhower, Eat the Frog, OKRs |
| 3 | Aislamiento interrupciones | El mundo me interrumpe | Alta | Deep Work, Time Blocking, Task Batching |
| 4 | Visualización flujo | No veo dónde se atasca | Alta | Kanban, Scrum, Shape Up, Cycles |
| 5 | Construcción hábitos | Sin constancia | Alta | Atomic Habits, Don't Break the Chain |
| 6 | Gestión conocimiento conectado | Acumulo sin conectar | Media | Zettelkasten, BASB, AI Second Brain |
| 7 | Regulación emocional [opt-in] | Miedo al fallo paraliza | Media | (Hueco mercado — UMBRAL propietaria) |
| 8 | Ritmo cognitivo interno | Cerebro se cansa | Alta | Pomodoro, Deep Work parcial |
| 9 | Transiciones y límites rol | Trabajo invade vida | Alta | (Hueco — ESCLUSA propietaria) |
| 10 | Curaduría entorno digital | Caos digital | Alta | (Hueco — Curador Monstruo) |
| 11 | Adaptabilidad incertidumbre [req validación] | Cambios erosionan planes | Media | Agentic Workflows |

### 4.2 Transversal T

**Eliminación de fricción operativa** — meta sobre todas. Define el techo de calidad Apple/Tesla del Obj #2. Implementa: Calm Technology, Vibe Coding, Agentic Workflows, Intent-Based Productivity, Context Engineering parcial.

### 4.3 Implicaciones para El Monstruo

El Monstruo deja de ser "herramienta de productividad" y pasa a ser **diagnóstico operativo**. Observa patrón de dolor desde señales objetivas (calendario, comunicación) y prescribe la metodología correcta. Activa Obj #2 (Apple/Tesla — sabe lo que necesitas) y Obj #3 (mínima complejidad — usuario no elige, vive el resultado).

Aparecen huecos de mercado priorizables: Especialidades #7, #9, #10 son **océanos azules preasignados al Monstruo**.

### 4.4 Las 7 dimensiones de Curaduría del Entorno (Esp #10)

| # | Dimensión | Síntoma | Acción Curador |
|---|---|---|---|
| 1 | Sistema de archivos | Downloads con 3,000 archivos | Auto-clasifica, deduplica, renombra |
| 2 | Notas dispersas | Misma idea en 4 apps | Captura → Second Brain único |
| 3 | Email & comm | 47,000 sin leer | Triaje continuo |
| 4 | Calendario | Reuniones traslapadas | Detecta colisiones, prepara |
| 5 | Tabs "leer después" | 200 tabs abiertas | Cierra, guarda con resumen |
| 6 | Media | 70,000 fotos sin clasificar | Auto-álbumes, OCR |
| 7 | Apps y dispositivos | 200 apps sin uso | Audita, sugiere desinstalar |

### 4.5 Matriz de Soberanía

Especialidades #7, #9 y #10 requieren consentimiento granular por `data_surface` × `action_risk`. No basta opt-in general.

## 5. Arquitectura: Embriones × Metodologías × Especialidades

### 5.A 9 Embriones Existentes (Reuso)
Creativo, Estratega, Financiero, Investigador, Técnico, Ventas, Critic Visual, Product Architect, Vigía. `product_architect.py` ya implementa el patrón "diagnosticar → contratar → ejecutar".

### 5.B Embriones de Dominio (Curaduría)

| Embrion | Dominio | Especialidades |
|---|---|---|
| Archivista | Sistema de archivos | #10 + #1 + #6 |
| Bibliotecario | Notas, second brain | #1 + #6 |
| Recepcionista | Email, mensajes | #2 + #9 |
| Concierge | Calendario, reuniones | #2 + #3 + #8 + #9 |
| Curador de Lecturas | Tabs, bookmarks | #6 + T |
| Fotógrafo | Fotos, screenshots | #6 + #10 |
| Conserje de Apps | Apps, notificaciones | #3 + #10 + T |
| Ecónomo | Suscripciones, almacenamiento | #10 |
| Compromisario | Ledger compromisos | #1 + #2 |
| Relacionista | Grafo de personas | #9 + #10 |

### 5.C Servicios Transversales
- **Notario / Guardián de Autoridad**: consentimiento, audit, reversibilidad
- **Ontólogo**: Índice Semántico transversal
- **Auditor de Seguridad**: detecta credenciales/datos sensibles

## 6. Methodology-as-a-Service (MaaS)

Registro en `kernel/methodologies/`. Cada metodología es módulo invocable con esquema YAML obligatorio:
- `canonical_id`, `name`, `kind` (methodology|instrument|design_pattern|execution_architecture|capability)
- `primary_specialty`, `input_contract`, `risk_profile`

**Capacity & Effort Calibration**: componente transversal antes del Auto-Scheduling. Aprende error de estimación del usuario, energía real, coste de cambio de contexto.

Arquitectura:
1. Registro: cada metodología expone `interface(input_context) -> action_plan`
2. Diagnóstico: Embrion Vigía + Especialidades observan proxies observables con confidence
3. Selección: Embrion Estratega evalúa `evaluate_fit()`
4. Invocación: Embrion de Dominio ejecuta
5. Observación: `embrion_metrics.py` mide éxito

## 7. Doctrina de Invocación bajo demanda

El usuario **nunca elige metodología**. El Monstruo invoca la pieza correcta para el momento correcto.
- Dolor "priorización" → Eisenhower Matrix
- Dolor "parálisis perfeccionismo" → Eat the Frog + Vibe Coding
- Dolor "caos archivos" → Curaduría

Acciones de alto impacto requieren `confidence_threshold` ≥ 0.8 o aprobación humana.

## 8. Metodologías Históricas (Pre-2025)

Los Sabios las dominan. IDs canónicos `M-H-{NAME}`.

**Gestión Personal:** GTD (Allen 2001), Pomodoro (Cirillo 80s), Eisenhower Matrix, Eat the Frog (Tracy 2001), Time Blocking (Newport), Bullet Journal (Carroll 2013), Atomic Habits (Clear 2018), Deep Work (Newport 2016).

**Proyectos y Equipos:** Kanban (Toyota 50s), Scrum (Sutherland/Schwaber 1995), Shape Up (Basecamp 2019), OKRs (Grove en Intel).

**Conocimiento:** Zettelkasten (Luhmann 50s-70s), BASB/PARA (Forte 2017-2022 — declarado obsoleto por su creador en marzo 2026).

## 9. Metodologías Novedosas (2025 – Mayo 2026)

Requieren inyección de contexto antes de consultar.

### 9.A Context Engineering (reemplaza Prompt Engineering)
Capas estructuradas: System / Episodic / Semantic / Working memory / Tool. **Riesgo Sabios:** responden con técnicas 2024 (chain-of-thought, few-shot) en vez de arquitectura de contexto.

### 9.B The AI Second Brain (Marzo 2026)
Forte invirtió BASB: "Capture everything, organize nothing". Organización delegada a embeddings + LLM retrieval. **Riesgo:** Sabios usan PARA 2022 obsoleto.

### 9.C Vibe Coding / Software 3.0 (Junio 2025)
Karpathy YC AI School. Humano orquesta "vibra": intención, arquitectura, constraints. Agentes LLM generan, testean, iteran. +40% productividad ingeniería. **Riesgo:** Sabios sugieren Scrum/Agile tradicional.

### 9.D Agentic Workflows (Post-Agile)
Pipelines determinísticos donde agentes IA deciden y ejecutan. HITL solo en puntos críticos. Tablero pasa a vista de auditoría. **Riesgo:** Sabios insisten en Trello/Jira.

### 9.E Intent-Based Productivity
Motion, Reclaim.ai. Usuario declara intención ("reporte listo viernes"), sistema micro-gestiona. **Riesgo:** Sabios sugieren bloques estáticos.

### 9.F Calm Technology / Ambient Productivity (resucitada 2025-2026)
Weiser/Brown Xerox PARC 90s, operacionalizada por ola agéntica. Sistema actúa sin requerir que usuario abra app. **Define el techo de calidad Apple/Tesla del Obj #2.** Si el usuario tiene que abrir dashboard para saber qué pasa, el Monstruo ya falló.

## 10. Herramientas Líderes — Matriz

| Herramienta | Enfoque | Metodologías | Nota |
|---|---|---|---|
| Todoist | Listas minimalistas | GTD, Eisenhower, Pomodoro, Time Blocking | 13 métodos enseñados oficialmente |
| ClickUp | Everything app | Kanban, Gantt, Scrum, OKRs | 10+ vistas |
| Notion | Bases flexibles | Zettelkasten, PARA, Kanban | Templates |
| Asana | Work management | Kanban, Scrum, Waterfall, OKRs | Goals oficial |
| Linear | Engineering | Cycles (Shape Up híbrido) | 1-8 sem + cooldown |
| Sunsama | Daily Rituals | Time Blocking, Deep Work, Pomodoro | Único "ritual-first" |
| Motion | AI Auto-scheduling | Intent-Based | Pioneros del paradigma |
| Obsidian/Roam/Logseq | Second Brain | Zettelkasten | Networked Thought |
| Basecamp | Shape Up | Nativo 6w+2 cooldown | Hogar original |
| Habitica/Streaks | Hábitos | Atomic Habits | Gamificación |

## 11. Doctrina de Reversibilidad

Todo acto destructivo o alto impacto debe cumplir:
1. Cuarentena 30 días antes de borrado definitivo
2. Alias/Symlink antes de renombrar semánticamente
3. Idempotencia en todas las operaciones
4. Audit Log en el `audit_plane`

## 12. Gaps de Mercado y Oportunidades para El Monstruo

La industria está en océano rojo de "más vistas". Océanos azules requieren agente IA permanente.

**[Esp #2 + #3 + T] Auto-Scheduling 2.0** — Más allá de Motion. Inferir prioridad y esfuerzo del contexto, sin preguntar.

**[Esp T] Rituales conversacionales** — Sunsama ritualiza con fricción manual. Monstruo conduce ritual por voz/chat sin abrir app.

**[Esp #1 + #6] Mantenimiento cero Second Brain** — PARA falla cuando usuario deja de clasificar. AI Second Brain elimina el punto de falla.

**[Esp #8] Energy Management vs Time Management** — Casi ninguna herramienta gestiona energía. Cruzar calendario, sueño, comunicación con Deep Work.

**[Esp #4 + Capa 7] AAR auto-generados** — Retrospectivas Agile fallan por disciplina humana. Monstruo genera AAR automático desde Event Store.

**[Esp #7] OCÉANO AZUL — UMBRAL** (Unidad Mínima de Bajo Riesgo para Reanudar Acción / Cognitive Defrosting / STOA). Detecta reescrituras múltiples y tareas estancadas, fragmenta en micro-acciones de 2 minutos (Emotional Momentum Cascade). Requiere Matriz de Soberanía.

**[Esp #9] OCÉANO AZUL — ESCLUSA** (Esclusas de Rol y Límites Contextuales / Airlock Protocol). Defiende límites con buffers automáticos (Role Boundary Flux) y Shutdown Sequence.

**[Esp #10] OCÉANO AZUL MAYOR** — El Monstruo como equipo agéntico de 10 roles condensado. Cura el entorno digital como prerequisito. Cambia el pricing: no SaaS $10/mes, sino fracción de FTE $200-500/mes.

## 13. Protocolo Operativo para Consultar a los Sabios

Reglas duras, no sugerencias.

**R1 Clasificar antes de consultar.** Identificar si concepto está en Histórica (Sec 8) o Novedosa (Sec 9).

**R2 Consulta directa solo para Históricas.** Su entrenamiento es suficiente.

**R3 Inyección obligatoria de payload para Novedosas.** Anexar la subsección 9.X al prompt: *"Basado estrictamente en este payload (no en tu entrenamiento), aplica..."*

**R4 Tabla de Confiabilidad + Validación Cruzada.** Decisiones críticas: ≥2 Sabios, incluyendo uno Nivel 1 o 2. Metodologías nicho: añadir Perplexity Sonar Reasoning Pro.

**R5 Uso semilla v7.3.** Toda consulta dispara lectura previa para versiones correctas.

**R6 Diagnóstico antes de prescripción.** Prohibido pedir "qué metodología usar". Pregunta correcta: *"Dado dolor-raíz [X] de Especialidad [Y], qué metodologías de Sec 8 y 9 aplican, cómo prescribirse desde señales detectables"*.

## 14. Roadmap de Iteraciones

- [x] Iter-00 (v1.2): Las 10+1 Especialidades como criterio organizacional. Cristalizada en Sec 4.
- [ ] Iter-01: Profundización Novedosas como capas de El Monstruo (Context Engineering + AI Second Brain).
- [ ] Iter-02: Mapeo cruzado Especialidad × 7 Capas Transversales.
- [ ] Iter-03: Matriz incompatibilidades — simplificada.
- [ ] Iter-04: Cruce especialidad × arquetipo usuario.
- [ ] Iter-05: Validación con enjambre Sabios v7.3.
- [ ] Iter-06: Refresh trimestral del Corte Epistemológico.
- [ ] Iter-07: Diseño UMBRAL y ESCLUSA (océanos azules #7 y #9).
- [ ] Iter-08: Arquitectura `kernel/methodologies/` + PoC con Eisenhower.

## 15. SMART de este documento

- **Specific:** metodologías productividad personal/equipo, dolores-raíz, herramientas, consultabilidad Sabios.
- **Measurable:** 10 verticales + 1 transversal, 6 Novedosas, 12 Históricas, 10 herramientas, 8 oportunidades, 6 reglas protocolo, 9 ítems roadmap.
- **Achievable:** stack ya disponible (Supabase + LangGraph + Sabios).
- **Relevant:** alineado con AGENTS.md Reglas Duras #1, #2, #3.
- **Time-bound:** validación 2026-05-07, refresh trimestral según Iter-06.

## 16. Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1-1.0 | 2026-05-07 | Investigación inicial → consolidación SMART |
| 1.1 | 2026-05-07 | Tres ajustes anti-autoboicot: Grok/DeepSeek validados, Atomic Habits + Deep Work, 5.F Calm Tech |
| 1.2 | 2026-05-07 | Cambio copernicano: 10+1 Especialidades. 3 tests de estrés. 2 océanos azules. |
| 1.4 | 2026-05-07 | Curaduría, MaaS, Invocación bajo demanda |
| **1.5** | **2026-05-08** | **Validación adversarial Iter-05 con GPT-5.5 Pro + Gemini 3.1 Pro + Grok 4 + Perplexity. 19 cambios: Matriz Soberanía, Refactor Estratega/Dominio, 3 Embriones Dominio, 3 Servicios Transversales, Doctrina Reversibilidad, YAML MaaS, UMBRAL y ESCLUSA formalizadas.** |

## 17. Referencias

Ver bibliografía completa en versión original: cortes epistemológicos verificados con docs oficiales (Anthropic, OpenAI, Google, xAI, DeepSeek), Context Engineering [Medium], Tiago Forte [fortelabs], Karpathy YC [latent.space], Agentic frameworks [Akka], Motion docs, Linear Cycles, Todoist methods, ClickUp views, Vibe Coding [Medium].
