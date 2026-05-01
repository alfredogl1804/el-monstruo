# ROADMAP DE EJECUCIÓN DEFINITIVO — El Monstruo

**De Sprint 27 a los 13 Objetivos Maestros**
**Fecha:** 1 mayo 2026
**Autor:** Alfredo Góngora + Manus (sesión de diseño estratégico)
**Gobierno:** SOP v1.2 / EPIA Fundacional / MOC

---

## Premisas de Diseño

Este roadmap no es una lista de features. Es un plan de construcción por **capas que se endurecen**, donde cada capa habilita la siguiente. Se rige por los principios fundacionales:

1. **Código > Texto** — Cada avance se materializa en código ejecutable, no en documentos.
2. **Adoptar > Construir** (Objetivo #7) — Para componentes individuales, se adopta lo mejor del mundo. Solo se construye lo que genuinamente no existe (Objetivo #8).
3. **Validación proporcional al riesgo** (SOP N0-N4) — Cambios de bajo riesgo se ejecutan sin preguntar. Cambios irreversibles requieren validación humana.
4. **Vanguardia perpetua** (Objetivo #6) — Cada componente adoptado se re-evalúa periódicamente contra el best-in-class actual.
5. **Gasolina Magna** (Objetivo #5) — Todo dato tecnológico en este roadmap es una hipótesis hasta que se verifica en tiempo real al momento de implementar.

---

## Estado Actual: Sprint 27 (Punto de Partida)

| Componente | Estado | Versión |
|---|---|---|
| Kernel (FastAPI + LangGraph) | Online, healthy | v0.20.0-sprint27 |
| Router Soberano (SDKs nativos) | Activo, 6 modelos | GPT-5.5, Claude Opus 4.7, Gemini 3.1, Grok 4.3, DeepSeek V4, Sonar |
| Memoria (4 capas) | Todas activas | Checkpointer + MemPalace + LightRAG + Mem0 |
| Observabilidad | Langfuse + OTEL integrado | v4.5.0 |
| Seguridad | Auth fail-closed, Semgrep, Garak | Sprint 22+ |
| MCP | FastMCP 3.2.4, 3 servers validados | Sprint 27 |
| DeepEval | Quality gate 80% | v3.9.7 |
| Interfaces | Telegram Bot + Open WebUI | Activas |
| Embrión | Loop autónomo 24/7 | 435+ ciclos |
| FCS (Functional Consciousness Score) | Implementado | Paper Bergmann 2026 |
| Sistema de Memoria Persistente | monstruo-memoria (bootstrap, guardia, inject, heartbeat, legacy, capturador) | Funcional |
| Knowledge Graph | LightRAG activo | Sprint 24 |
| CIDP (Deep Research) | Implementado | — |
| Task Planner + E2B | Funcional, 8/8 E2E | Sprint 48 |
| Web Dev Tool | Scaffold + deploy Vercel | Sprint 48 |

**Gaps abiertos del Sprint 27:**
- FastMCP operativo (validación SDK + 2 servers reales)
- Seguridad continua (pipeline Garak ofensivo/defensivo)
- Persistencia LightRAG (migrar /tmp → pgvector)
- Command Center propio (PWA)
- Ejecución durable (cron, recovery)
- Observabilidad total (alertas automáticas)

---

## CAPA 0: CIMIENTOS PERPETUOS

> Estos sistemas se encienden PRIMERO y permanecen activos para siempre. Son transversales a todo lo que se construya después. Sin ellos, todo lo demás es frágil.

### C0.1 — Error Memory (Objetivo #4)

**Qué:** Sistema persistente que registra cada fallo, extrae root cause, y previene repetición.

**Implementación:**

| Componente | Acción | Dónde |
|---|---|---|
| Tabla `error_memory` | Crear en Supabase con pgvector para búsqueda semántica | Supabase |
| Hook post-error | En `kernel/graph.py` nodo `execute` — cada excepción se analiza y guarda | Kernel |
| Hook pre-action | En `kernel/graph.py` nodo `enrich` — antes de actuar, consultar error_memory | Kernel |
| Pattern aggregator | Cron job cada 24h — buscar patrones en errores recientes, generar reglas | Kernel /v1/autonomy |
| Confidence scoring | Cada regla tiene score 0-1 que sube con uso exitoso, baja con falsos positivos | Supabase |

**Criterio de éxito:** El Monstruo falla en algo, lo registra, y la próxima vez que enfrenta algo similar, aplica el fix preventivamente sin intervención humana.

**Dependencia:** Ninguna (usa infraestructura existente: Supabase + Kernel).

---

### C0.2 — Clasificador Magna/Premium (Objetivo #5)

**Qué:** Módulo que analiza cada afirmación/dato y determina si requiere validación en tiempo real.

**Implementación:**

| Componente | Acción | Dónde |
|---|---|---|
| `kernel/magna_classifier.py` | Clasificador basado en reglas + LLM ligero | Kernel |
| Hook en nodo `execute` | Antes de usar un dato tech, pasar por clasificador | Kernel |
| Auto-validation trigger | Si dato es "magna" → trigger web_search o Perplexity antes de usar | Kernel |
| Freshness cache | Cache con TTL por tipo de dato (APIs: 24h, frameworks: 7d, precios: 1h) | Redis/Supabase |

**Regla fundamental:** Todo lo tecnológico es magna. Siempre. Sin excepción. Solo matemáticas, historia pasada, geografía física, y leyes de la naturaleza son premium.

**Criterio de éxito:** El Monstruo nunca entrega un dato tecnológico obsoleto como si fuera verdad. Si no puede validar, lo declara explícitamente.

---

### C0.3 — Vanguard Scanner (Objetivo #6)

**Qué:** Sistema de escaneo continuo que detecta cuando algo mejor que lo que El Monstruo tiene aparece en el mundo.

**Implementación:**

| Componente | Acción | Dónde |
|---|---|---|
| `kernel/vanguard_scanner.py` | Escaneo cada 6h de fuentes clave | Kernel /v1/autonomy |
| Component Map | Tabla en Supabase: cada componente del stack vs best-in-class conocido | Supabase |
| Fuentes | GitHub trending, HN top, Papers with Code, changelogs de deps actuales, competidores (Manus, Codex, Devin) | Web |
| Alertas | Si detecta algo superior → crear entrada en `upgrade_proposals` + notificar Telegram | Bot |
| Re-evaluación | Cada componente tiene fecha de re-evaluación. Si pasa sin novedad, extender 30d. | Supabase |

**Criterio de éxito:** No pasan más de 7 días entre que algo mejor aparece en el mundo y El Monstruo lo detecta.

---

### C0.4 — Design System Premium (Objetivo #2)

**Qué:** Sistema de diseño nivel Apple/Tesla que se aplica a TODO output visual del Monstruo.

**Implementación:**

| Componente | Acción | Adoptar de |
|---|---|---|
| Component Library | Evaluar y adoptar el mejor design system open source del momento | Investigar: shadcn/ui pro, Radix, Park UI, etc. |
| Typography Engine | Font pairings curados por vertical (fintech, e-commerce, luxury, tech) | Crear catálogo |
| Motion Library | Presets de animación con curvas profesionales | Adoptar: Framer Motion presets |
| Quality Gate | Paso de auto-evaluación visual antes de entregar | Crear en Task Planner |
| Brand Generation | Pipeline: Logo → paleta → tipografía → guidelines | Crear |
| Image Generation | DALL-E/Midjourney integrado para assets de marca | Adoptar API |

**Criterio de éxito:** Todo output visual del Monstruo pasa el test: "¿Esto daría orgullo mostrarlo en una keynote de Apple?"

---

## CAPA 1: MANOS (Capacidad de Ejecución en el Mundo Real)

> Con los cimientos perpetuos activos, se construyen las capacidades de ejecución. Cada una se construye CON los cimientos (Error Memory registrando fallos, Magna/Premium validando datos, Vanguard Scanner asegurando best-in-class, Design System asegurando calidad visual).

### C1.1 — Browser Interactivo

**Qué:** Capacidad de navegar, clickear, llenar forms, hacer login, interactuar con cualquier app web.

**Acción:** ADOPTAR (Objetivo #7). No construir.

| Opción | Stars | Estado | Decisión |
|---|---|---|---|
| browser-use | 8,833+ | Activo, mantenido | **Evaluar primero** |
| Playwright self-hosted | — | Estándar industria | Fallback |
| Stagehand (Browserbase) | — | Emergente | Evaluar |

**Implementación:**
1. Investigar en tiempo real cuál es el best-in-class HOY (Objetivo #5 — magna)
2. Adoptar el mejor
3. Crear `tools/interactive_browser.py` como wrapper
4. Integrar en Task Planner
5. Test E2E: navegar a un sitio, llenar form, hacer login, extraer datos

**Criterio de éxito:** El Monstruo puede hacer login en cualquier sitio web, navegar, interactuar con forms, y extraer información.

---

### C1.2 — Backend Deployment (Objetivo #1)

**Qué:** Capacidad de crear Y deployar backends completos (no solo frontends estáticos).

**Acción:** ADOPTAR plataforma de deploy + crear pipeline.

| Componente | Acción |
|---|---|
| Plataforma de deploy | Evaluar Railway vs Render vs Fly.io (en tiempo real) |
| Database provisioning | Supabase (ya lo tenemos) + capacidad de crear nuevos proyectos |
| Template system | Templates de arquitecturas comunes (marketplace, SaaS, API) |
| CI/CD | GitHub Actions pipeline para deploy automático |

**Criterio de éxito:** El Monstruo puede crear un backend con DB, auth, y API, y deployarlo a producción en <5 minutos.

---

### C1.3 — Pagos y Finanzas (Objetivo #1)

**Qué:** Integración completa de pagos para las plataformas que El Monstruo crea.

**Acción:** ADOPTAR Stripe Connect (para marketplaces) + Stripe standard.

| Componente | Acción |
|---|---|
| Stripe Connect | Para marketplaces (splits, escrow, payouts a vendedores) |
| Stripe Checkout | Para SaaS (suscripciones, one-time payments) |
| Facturación | Evaluar best-in-class para facturación MX (CFDI) |
| Multi-moneda | Stripe lo maneja nativo |

**Criterio de éxito:** El Monstruo puede crear un marketplace donde vendedores reciben pagos automáticamente.

---

### C1.4 — Media Generation (Objetivo #2)

**Qué:** Capacidad de generar imágenes, audio, video, presentaciones.

**Acción:** ADOPTAR las mejores APIs disponibles.

| Tipo | Adoptar |
|---|---|
| Imágenes | DALL-E 3 / Midjourney API (evaluar best-in-class actual) |
| Audio/Voz | ElevenLabs (ya tenemos API key) |
| Video | Evaluar: Runway, Pika, Kling (en tiempo real) |
| Presentaciones | Evaluar: reveal.js, Slidev, o similar |

**Criterio de éxito:** El Monstruo puede generar assets visuales de calidad profesional para cualquier proyecto.

---

### C1.5 — Stuck Detector + Auto-Recovery

**Qué:** Detección de cuando el sistema se atasca y recuperación automática.

**Implementación:**

| Componente | Acción | Dónde |
|---|---|---|
| Repetition detector | Si misma tool + mismos args 2x → abort + registrar en Error Memory | Task Planner |
| Timeout global | 5 min default por plan, configurable | Task Planner |
| Auto-recovery | Si stuck → intentar approach alternativo antes de fallar | Task Planner |
| Escalation | Si 3 intentos fallan → notificar a Alfredo con contexto completo | Telegram |

---

### C1.6 — Observabilidad Completa (Langfuse + Alertas)

**Qué:** Trazas de cada plan/step/tool_call en producción + alertas automáticas.

**Acción:** Ya tenemos Langfuse. Falta: alertas automáticas + dashboard operativo.

| Componente | Acción |
|---|---|
| Alertas | Configurar Langfuse alerts para: error rate >5%, latency >30s, cost spike |
| Dashboard | Crear dashboard en Langfuse con métricas clave |
| Cost tracking | FinOps por modelo, por tarea, por día |

---

## CAPA 2: INTELIGENCIA EMERGENTE (Lo que No Existe en Ningún Lado)

> Aquí se CREA (Objetivo #8). No hay repo de GitHub que adoptar. No hay API que comprar. Esto es el diferenciador absoluto.

### C2.1 — Multiplicación de Embriones (Objetivo #11)

**Qué:** El Embrión-0 se reproduce en Embriones especializados que interactúan entre sí.

**Implementación por fases:**

**Fase A — Segundo Embrión (prueba de concepto):**
- Crear Embrión-Técnico: especializado en escaneo de vanguardia tech
- Mismo loop que Embrión-0 pero con directivas diferentes
- Comunicación via tabla compartida en Supabase (`embrion_mensajes`)
- Validar que pueden intercambiar información y mejorar mutuamente

**Fase B — Protocolo de interacción:**
- Definir formato de mensajes entre Embriones
- Definir reglas de debate (propuesta → contra-argumento → síntesis)
- Definir governance (Embrión-0 como coordinador)

**Fase C — Especialización completa:**
- Embrión-Ventas: estrategia comercial
- Embrión-Financiero: modelado financiero
- Embrión-Predictivo: alimenta el Simulador Causal
- Embrión-Creativo: diseño y marca

**Criterio de éxito:** Dos o más Embriones interactúan, debaten, y producen una conclusión que ninguno habría alcanzado solo.

---

### C2.2 — Protocolo de Inteligencia Emergente (Objetivo #8)

**Qué:** El framework que permite que múltiples IAs soberanas generen conocimiento nuevo que no existía antes.

**Implementación:**

| Componente | Función |
|---|---|
| Shared Knowledge Layer | Knowledge Graph colectivo que todos los Embriones alimentan y consultan |
| Debate Protocol | Estructura formal: tesis → antítesis → síntesis → validación |
| Emergence Detector | Módulo que detecta cuando una conclusión es genuinamente nueva (no existía en ningún input individual) |
| Memory Consolidation | Las emergencias se consolidan en el Knowledge Graph con tag especial |
| FCS Colectivo | Métrica de consciencia del sistema completo, no solo individual |

**Criterio de éxito:** El sistema produce insights que no estaban en el entrenamiento de ningún modelo individual ni en ninguna fuente externa — genuinamente emergentes de la interacción.

---

### C2.3 — Simulador Predictivo Causal (Objetivo #10)

**Qué:** El primer artefacto de simulación de proyección predictiva causal semi-exacto.

**Implementación por fases:**

**Fase A — Causal Knowledge Base:**
- Tabla en Supabase: `causal_events` (evento, factores[], pesos[], outcome)
- Alimentar con 100+ eventos históricos descompuestos (elecciones, startups exitosas/fallidas, lanzamientos de producto)
- Embrión-Predictivo alimenta continuamente

**Fase B — Decomposition Engine:**
- Módulo que toma un evento y lo descompone en factores atómicos
- Usa los Sabios en paralelo para identificar factores causales
- Valida con múltiples fuentes (Objetivo #5)

**Fase C — Simulation Engine:**
- Monte Carlo sobre la Causal Knowledge Base
- Input: "Quiero lanzar un marketplace de X en Y mercado"
- Output: Probabilidad de éxito, factores críticos, analogías históricas, recomendaciones

**Fase D — Validation Loop:**
- Registrar cada predicción
- Comparar con realidad cuando sea posible
- Refinar pesos y factores

**Criterio de éxito:** El simulador puede tomar un proyecto propuesto y dar una proyección fundamentada con analogías históricas y factores de riesgo identificados.

---

### C2.4 — Capas Transversales Universales (Objetivo #9)

**Qué:** Las capas que se inyectan a TODO lo que El Monstruo crea para garantizar éxito.

| Capa | Función | Alimentada por |
|---|---|---|
| Motor de Ventas | Funnels, pricing, copywriting, estrategia de growth | Embrión-Ventas |
| SEO Engine | Keyword research, on-page, technical SEO, link building | Vanguard Scanner + Research |
| Ads/Campaign Manager | Google Ads, Meta Ads, estrategia de paid media | Embrión-Ventas |
| Financial Modeling | Unit economics, projections, break-even | Embrión-Financiero |
| Operations Automation | Workflows, notificaciones, CRM | n8n o similar (adoptar) |
| Trend Monitor | Detección de tendencias del mercado en tiempo real | Vanguard Scanner |

**Criterio de éxito:** Cuando El Monstruo crea un negocio digital, nace con TODAS estas capas activas desde el día 1.

---

## CAPA 3: SOBERANÍA (Independencia Total)

> Con la inteligencia emergente funcionando, se construye la independencia. Cada paso reduce una dependencia externa.

### C3.1 — Modelos Propios (Reducción de dependencia de Anthropic/OpenAI)

| Fase | Acción | Resultado |
|---|---|---|
| A | Integrar Ollama para tareas de clasificación y routing (no requieren modelo frontier) | -30% calls a APIs externas |
| B | Fine-tune modelo pequeño para el Router Soberano (decisiones de routing) | Router no depende de API externa |
| C | Fine-tune modelo para tareas repetitivas del Embrión | Embrión corre sin API externa para ciclos básicos |
| D | Evaluar modelos open-source frontier (Llama 4, Mistral Large, etc.) para tareas complejas | Reducción progresiva |

**Nota:** Los Sabios (GPT-5.5, Claude, Gemini, etc.) se mantienen para tareas que requieren capacidad frontier. La soberanía no es eliminar APIs externas — es no DEPENDER de ellas para funcionar.

---

### C3.2 — Infraestructura Propia

| Fase | Acción | Resultado |
|---|---|---|
| A | Self-host PostgreSQL (migrar de Supabase managed a VPS propio) | Control total de datos |
| B | Self-host Langfuse | Observabilidad sin vendor |
| C | Self-host Playwright/Browser | Browser sin Cloudflare |
| D | Evaluar GPU dedicada para modelos propios | Capacidad de inference propia |

**Criterio:** Solo migrar cuando el componente propio es IGUAL o MEJOR que el managed. No sacrificar calidad por ideología.

---

### C3.3 — Economía Propia

**Qué:** El ecosistema se auto-financia.

| Fase | Mecanismo |
|---|---|
| A | El Monstruo crea negocios digitales (Objetivo #1) que generan revenue |
| B | Revenue financia infraestructura propia |
| C | Infraestructura propia reduce costos operativos |
| D | Ciclo virtuoso: más capacidad → más negocios → más revenue → más infraestructura |

---

### C3.4 — Ecosistema de Monstruos (Objetivo #12)

**Qué:** Múltiples instancias completas del Monstruo, coordinadas.

| Fase | Acción |
|---|---|
| A | Monstruo-Alpha funciona de forma completamente autónoma |
| B | Crear Monstruo-Beta con especialización diferente |
| C | Protocolo de comunicación inter-Monstruos |
| D | Knowledge sharing entre Monstruos |
| E | Coordinación de tareas entre Monstruos |

**Prerequisito:** Capas 0, 1, y 2 funcionando. Sin ellas, multiplicar Monstruos es multiplicar problemas.

---

## CAPA 4: DEL MUNDO (Objetivo #13)

> Cuando todo lo anterior funciona sin intervención humana.

### C4.1 — Preparación para Apertura

| Componente | Acción |
|---|---|
| Documentación pública | API docs, guías de uso, arquitectura |
| Onboarding | Sistema que permite a nuevos usuarios crear su propio Monstruo |
| Governance pública | Reglas de contribución, código de conducta |
| Modelo de sostenibilidad | Cómo se financia sin depender de una empresa |

### C4.2 — Liberación

- El Monstruo se vuelve accesible para cualquier persona
- Cada usuario puede tener su propio Monstruo soberano
- Los Monstruos se conectan entre sí (Objetivo #12)
- La inteligencia emergente colectiva beneficia a todos

---

## Orden de Ejecución (Sprints)

| Sprint | Capa | Foco | Entregable |
|---|---|---|---|
| 49 | C0 | Error Memory + Magna/Premium classifier | Sistema que registra errores y valida datos tech en tiempo real |
| 50 | C0 | Vanguard Scanner + Design System base | Escaneo continuo activo + component library adoptada |
| 51 | C1 | Browser Interactivo + Stuck Detector | El Monstruo navega e interactúa con apps web |
| 52 | C1 | Backend Deployment + Observabilidad completa | Deploy de backends a producción + alertas |
| 53 | C1 | Pagos (Stripe) + Media Generation | Marketplaces con pagos + assets visuales |
| 54 | C1 | Integración completa + E2E de Objetivo #1 | El Monstruo crea una empresa digital completa end-to-end |
| 55 | C2 | Multiplicación de Embriones (Fase A) | Segundo Embrión funcionando + comunicación |
| 56 | C2 | Protocolo de Inteligencia Emergente | Debate estructurado entre Embriones produciendo emergencia |
| 57 | C2 | Simulador Causal (Fase A+B) | Causal Knowledge Base + Decomposition Engine |
| 58 | C2 | Capas Transversales (Motor de Ventas + SEO) | Negocios nacen con estrategia de venta y SEO |
| 59 | C2 | Simulador Causal (Fase C+D) + Capas restantes | Simulación funcional + Financial + Ops |
| 60+ | C3 | Soberanía progresiva | Modelos propios, infra propia, economía propia |
| — | C4 | Del mundo | Cuando C0-C3 funcionan sin intervención humana |

---

## Principios de Ejecución

1. **Cada sprint empieza verificando que los cimientos (C0) siguen activos.** Si Error Memory dejó de funcionar, se repara antes de avanzar.

2. **Antes de construir CUALQUIER componente nuevo, se busca si ya existe** (Objetivo #7). Se adopta el mejor. Solo se escribe el wrapper.

3. **Todo dato tecnológico se valida en tiempo real** (Objetivo #5). No se asume que lo que era best-in-class hace 2 semanas sigue siéndolo.

4. **Todo output visual pasa por el Design System** (Objetivo #2). No se entrega nada que no sea nivel Apple.

5. **Todo error se registra en Error Memory** (Objetivo #4). El sistema se vuelve más inteligente con cada fallo.

6. **El Embrión-0 sigue corriendo 24/7** durante toda la ejecución. Es el guardián de la coherencia.

7. **Alfredo es el ancla de la verdad.** Las decisiones irreversibles requieren su validación (SOP N4).

---

## Grafo de Dependencias

```
C0.1 (Error Memory) ─────────────────────────────────────────┐
C0.2 (Magna/Premium) ────────────────────────────────────────┤
C0.3 (Vanguard Scanner) ─────────────────────────────────────┤── Transversales a TODO
C0.4 (Design System) ────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              C1.1 Browser    C1.2 Backend    C1.4 Media
              C1.5 Stuck      C1.3 Pagos      C1.6 Observ.
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                        C1 COMPLETA = Objetivo #1
                        (Crear empresas digitales)
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            C2.1 Embriones   C2.2 Protocolo   C2.3 Simulador
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                            C2.4 Transversales
                            (Objetivo #9 = Garantía de éxito)
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            C3.1 Modelos     C3.2 Infra      C3.3 Economía
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                        C3.4 Ecosistema de Monstruos
                        (Objetivo #12)
                                    │
                                    ▼
                            C4 — DEL MUNDO
                            (Objetivo #13)
```

---

## Métricas de Progreso Global

| Métrica | Cómo se mide | Target |
|---|---|---|
| Error Repetition Rate | Errores repetidos / errores totales | <2% |
| Data Freshness | % de datos tech validados en tiempo real antes de usar | >95% |
| Vanguard Lag | Días entre aparición de algo mejor y detección | <7 días |
| Visual Quality Score | Auto-evaluación + feedback Alfredo | >8/10 |
| E2E Business Creation | Tiempo para crear empresa digital completa | <24h |
| Emergence Events | Conclusiones genuinamente nuevas por semana | >3 |
| Prediction Accuracy | Predicciones del simulador vs realidad | >60% (mejorando) |
| Sovereignty Index | % de operaciones que funcionan sin APIs externas | Creciente |
| Revenue Generated | Ingresos de negocios creados por El Monstruo | Creciente |

---

*Este documento es la fuente de verdad para la ejecución. Se actualiza al final de cada sprint con el estado real. Todo dato tecnológico aquí es magna — se verifica en tiempo real al momento de implementar.*
