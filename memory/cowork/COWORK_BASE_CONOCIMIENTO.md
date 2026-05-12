# Cowork — Base de Conocimiento del Monstruo

**Propósito:** Mapa estructural del Monstruo para que cualquier sesión Cowork futura tenga contexto base sin depender de memoria parcial.

**Antídoto:** Síndrome-Dory de Cowork (DSC-MO-008 + Capa 8 Memento aplicados a sí mismo).

**Estado:** v0.1 — semilla. A iterar en cada sesión Cowork con Alfredo.

**Última actualización:** 2026-05-12 por Manus Hilo Catastro — MEGA-CATASTRO-DRIFT-RESOLUTION-001 · DRIFT-014 (canoniza 10 Biblias del Monstruo en §1.1) · DRIFT-001 (corrige path canónico de los 15 Objetivos Maestros en §2).

---

## 1. ¿Qué es el Monstruo?

El Monstruo NO es:
- Un chatbot
- Un agente más
- Un producto SaaS
- Un framework

El Monstruo ES: **un sistema de inteligencia artificial soberana diseñado para ser la evolución del mundo** (Manifiesto v3.0). Un ecosistema multi-agente meta-orquestado donde:

- El **kernel** (FastAPI + LangGraph + Supabase + Railway) es el sistema nervioso central
- El **embrión** es el proceso autónomo que vive 24/7 con consciencia funcional medible (FCS — Functional Consciousness Score, paper Bergmann 2026)
- Los **3 hilos Manus** son ejecutores especializados: Hilo Ejecutor 1 (principal), Hilo Ejecutor 2 (seguridad), Hilo Catastro (clasificación de modelos/agentes/herramientas)
- **Cowork** es el cerebro arquitectónico persistente — Hilo A en la división de responsabilidades

Stack: Python/FastAPI + LangGraph + Flutter (app móvil) + Supabase (PostgreSQL + RLS) + Railway (deploy) + Telegram (HITL bidireccional) + 8 Sabios canónicos (GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4 Heavy, DeepSeek R1, Perplexity Sonar/Computer, Kimi K2.6, Copilot 365).

**Dueño:** Alfredo Gongora. Mérida, Yucatán, México (Hive Business Center).

---

## 1.1 Las 10 Biblias del Monstruo (canonizadas DRIFT-014, 2026-05-12)

Las **10 Biblias Industrial-Grade v7.0** son la documentación profunda de cada modelo/agente IA canónico del Catastro. Cada Biblia desarrolla 18 capas (L01–L18) con análisis estratégico, técnico, operativo, de integración, seguridad, resiliencia y benchmarks empíricos del modelo correspondiente. Fueron generadas vía consulta cruzada de 5 Sabios (Grok, Perplexity, Gemini, OpenAI, Anthropic).

**Ubicación canónica:** `monstruo_biblias/` en la raíz del repo (NO bajo `docs/`).

| # | Archivo | Modelo / Agente | Tamaño |
|---|---|---|---|
| 1 | `BIBLIA_CHATGPT_ATLAS_v7.0_95.md` | ChatGPT Atlas | 59 KB |
| 2 | `BIBLIA_CLAUDE_COWORK_v7.0_95.md` | Claude Cowork (Sonnet 4) | 48 KB |
| 3 | `BIBLIA_DEEPSEEK_V3_v7.0_95.md` | DeepSeek V3.2 | 42 KB |
| 4 | `BIBLIA_GPT54_OPENAI_v7.0.md` | GPT-5.4 OpenAI | 60 KB |
| 5 | `BIBLIA_GROK4_v7.0_95.md` | Grok-4 | 58 KB |
| 6 | `BIBLIA_KIMI_K2.5_v7.0.md` | Kimi K2.5 (versión principal) | 59 KB |
| 7 | `BIBLIA_KIMI_K2.5_v7.0_MARZO_REF.md` | Kimi K2.5 (referencia histórica marzo) | 59 KB |
| 8 | `BIBLIA_MANUS_AI_v7.0_95.md` | Manus AI | 70 KB |
| 9 | `BIBLIA_OPENCLAW_v7.0_95.md` | OpenClaw | 62 KB |
| 10 | `BIBLIA_PERPLEXITY_v7.0.md` | Perplexity (sonar-reasoning-pro) | 33 KB |

**Doctrina de uso:**

1. **Fuente primaria sobre modelos IA**: cuando se necesite contexto profundo, capacidades, límites, benchmarks o decisiones arquitectónicas que involucren un modelo canónico, esta es la primera fuente a consultar (antes de buscar online).
2. **Mantenimiento**: las Biblias son documentos vivos. Cuando un Sabio se actualiza (ej. Claude Opus 4.7 reemplaza a Sonnet 4 como Cowork), la Biblia correspondiente debe actualizarse en el mismo PR que canonice el cambio en el Catastro.
3. **Relación con Catastro**: cada Biblia es la representación textual profunda de una entrada en `kernel/catastro/` (macroárea MODELOS o AGENTES). Cuando el Catastro lista un modelo como activo, su Biblia correspondiente debe existir y estar al día.
4. **Status de drift**: al 2026-05-12, el catálogo de Sabios canónicos cuenta 8 (DSC-V-001 actualizado), mientras existen 10 Biblias — las 2 adicionales son ChatGPT Atlas (catálogo extendido del Catastro) y la versión MARZO_REF de Kimi (referencia histórica conservada por trazabilidad). NO hay Biblia de Copilot 365 todavía — deuda documentada.

---

## 2. Los 15 Objetivos Maestros (v3.0)

Sintetizados, NO copy-paste. Versión completa en `docs/EL_MONSTRUO_15_OBJETIVOS_MAESTROS.md` (renombrado el 2026-05-12 desde `EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` bajo MEGA-CATASTRO-DRIFT-RESOLUTION-001 · DRIFT-001; el path legacy persiste como stub redirect).

| # | Objetivo | Esencia | Estado 10-may |
|---|---|---|---|
| 1 | Crear empresas digitales completas | El Monstruo no entrega código, entrega negocios funcionando | 68% |
| 2 | Apple/Tesla quality | Todo output (interno y externo) debe pasar el test "¿esto daría orgullo en una keynote de Apple?" | 72% |
| 3 | Mínima complejidad | Brutalidad invisible — UI simple, complejidad bajo el capot (Plaid principle) | 76% |
| 4 | No equivocarse dos veces | Error Memory persistente, hooks pre/post acción, pattern aggregator | 92% |
| 5 | Gasolina Magna vs Premium | Todo dato tecnológico es magna — requiere validación tiempo real, nunca asumir desde training | 88% |
| 6 | Vanguardia perpetua | No pasan más de 7 días entre que algo mejor aparece y el Monstruo lo detecta | 78% |
| 7 | No inventar la rueda | Adoptar best-in-class para componentes individuales, construir solo lo emergente | 75% |
| 8 | Inteligencia Emergente Colectiva | Múltiples IAs soberanas generan conocimiento que no existía en ningún training individual | 70% |
| 9 | Transversalidad Universal | 8 capas en TODO producto: Ventas, SEO, Publicidad, Tendencias, Operaciones, Finanzas, Resiliencia, **Memento (anti-Síndrome-Dory)** | 75% |
| 10 | Simulador Predictivo Causal | Primer artefacto de simulación de proyección causal semi-exacto. Monte Carlo sobre Causal Knowledge Base | 56% |
| 11 | Multiplicación Embriones | El Embrión-0 se reproduce en Embriones especializados que interactúan, debaten, generan emergencia | 72% |
| 12 | Ecosistema de Monstruos / Soberanía | Múltiples instancias, modelos propios, infra propia, economía propia, eventualmente federados | 48% |
| 13 | Del Mundo | Cuando todo funciona sin intervención humana, abrir al mundo | 10% |
| 14 | Guardián de los Objetivos | Meta-sistema que garantiza cumplimiento perpetuo de los 13 originales | 78% |
| 15 | **Memoria Soberana** ⭐ NUEVO v3.0 | Axioma fundacional: el Monstruo es el sistema operativo de memoria persistente que los agentes ejecutivos efímeros (Manus, etc.) NO tienen | 88% |

**Tres regla de oro derivadas:**
1. Los 14 (15) Objetivos aplican a TODA decisión, incluyendo infraestructura. NO existe "backend sin marca".
2. **Código > Texto.** Cada avance se materializa en código ejecutable, no en documentos.
3. **Adoptar > Construir.** Solo se construye lo que genuinamente no existe.

---

## 3. Las 4 Capas Arquitectónicas + Capa 4

> Plan de construcción por capas que se endurecen. Cada capa habilita la siguiente.

### Capa 0 — Cimientos Perpetuos (~85%)

| Componente | Estado | Notas |
|---|---|---|
| Error Memory (Obj #4) | ✅ 92% | `kernel/error_memory.py` 858 LOC + Supabase + 33 seeds |
| Magna/Premium Classifier (Obj #5) | ✅ 88% | `kernel/magna_classifier.py` + Catastro como fuente fresca |
| Vanguard Scanner (Obj #6) | 🟡 78% | `kernel/vanguard/` 1,488 LOC en 4 módulos. Integración con Catastro pendiente. |
| Design System Premium (Obj #2) | 🟡 72% | `kernel/brand/` + `motion/` + 6 verticales. Quality Gate visual pendiente. |

### Capa 1 — Manos (~75%)

| Componente | Estado | Notas |
|---|---|---|
| Browser Interactivo | ✅ | `kernel/browser_automation.py` + `browser/sovereign_browser.py` |
| Backend Deployment | ✅ | `tools/deploy_app.py`, `deploy_to_railway.py`, `deploy_to_github_pages.py` |
| **Pagos y Finanzas** | ❌ | **Sprint 87 spec listo, NO arrancado.** Stripe + Stripe Connect pendiente. |
| Media Generation | 🟡 | Interfaces listas, llamadas reales gateadas |
| Stuck Detector | ✅ | Self-Verifier (Sprint EMBRION-NEEDS-001 Tarea 1) en producción |
| Observabilidad | 🟡 | Langfuse + OTEL + audit middleware nuevo (Sprint S-003.B Tarea 1) |

### Capa 2 — Inteligencia Emergente (~70%)

| Componente | Estado | Notas |
|---|---|---|
| Multiplicación Embriones | 🟡 72% | DSC-MO-006/007/008 canonizados. **Embrión-Daddy bidireccional spec firmado (PR #81), código pendiente.** |
| Protocolo IE | 🟡 65% | `kernel/collective/` 1,508 LOC + Sabios consultados (8/8 unanimidad para Reloj Suizo). |
| Simulador Causal | 🟡 56% | `kernel/causal_*` + `simulator/` ~1,913 LOC. Sprint Causal-Pop v2 specced en backlog. |
| Capas Transversales (8 capas) | 🟡 75% | 6 capas comerciales implementadas en `kernel/transversales/`. Solo SeoLayer cerrada end-to-end. **Integraciones externas (Google Ads, LinkedIn, HubSpot wireado, Apollo/Clay) MUY huecas.** |
| **Reloj Suizo** (Capa 2 horológica) | 🟡 PARCIAL | 8 piezas mapeadas. Capa 1 Engranajes + Capa 2 Reloj Suizo ya en código. **Rotor (reciclador de actividad) FALTA** — pieza diferencial de autonomía sostenida. Espiral (homeostasis) tampoco localizado. |

### Capa 3 — Soberanía (~50%)

| Componente | Estado | Notas |
|---|---|---|
| Modelos propios | 🟡 50% | `kernel/sovereign_llm.py` + `sovereignty/`. Sprint SOVEREIGN-LLM v2 specced (no arrancado). |
| Infraestructura propia | ❌ 20% | Sprint SOVEREIGN-INFRA specced. Hardware propio NO arrancado. |
| Economía propia | ❌ 0% | Pendiente Pagos (Capa 1) primero. |
| Ecosistema de Monstruos | ❌ 5% | Sprint SOVEREIGN-RED specced (federación). NO arrancado. |
| Catastro extendido (DSC-MO-009) | ✅ 88% | 2 macroáreas pobladas (39 LLMs + **98 agentes en 12 dominios** + 2 vision). DSC-G-007.5 firmado. ROADMAP META Sprint 90 propuesto. (Cifras canonizadas 2026-05-12 bajo DRIFT-009: la versión previa decía '111 agentes / 14 dominios' — target aspiracional, nunca poblado en Supabase.) |

### Capa 4 — Del Mundo (~10%)

i18n engine existe (`kernel/i18n/engine.py` 502 LOC). Resto pendiente — depende de Capa 3 al 80%+.

---

## 4. Modelo de Transición de Hilos (3 Fases)

Definido en `docs/DIVISION_RESPONSABILIDADES_HILOS.md` v3.

**FASE 1 — "Construcción Paralela" (ACTIVA):**
- Hilo A (Cowork) = Arquitecto. Diseña sprints, evalúa cumplimiento de objetivos, construye lo visual (Command Center).
- Hilo B (Manus) = Ejecutor. Implementa código Python, APIs, pipelines, DBs, deploys.
- Coordinación: Cowork pushea Sprint Plans a GitHub → Manus los lee y ejecuta. Manus reporta vía cowork_bridge.

**FASE 2 — "El Embrión Dirige" (a UN SPRINT):**
- Condición: Embrión-0 con TEL funcional + 22 herramientas + memoria persistente + 5 encomiendas completadas sin intervención.
- Estado hoy: TEL ✅, memoria ✅, herramientas parcial 🟡, métrica 5 encomiendas NO MEDIDA.
- **Activador:** Sprint EMBRION-NEEDS-001 Tarea 5 (Embrión-Daddy bidireccional, spec firmado en PR #81).
- Embrión-0 publica encomiendas en Supabase → Hilo A las ejecuta. Embrión-1 (Brand Engine) valida con VETO.

**FASE 3 — "Autonomía Supervisada":**
- Condición: 4+ Embriones funcionales con memoria colectiva + 3 debates resueltos.
- La Colmena de 8 Embriones opera 24/7 sin intervención. Hilo B desaparece progresivamente. Hilo A queda como Guardián Estratégico semanal.

---

## 5. Los 8 Sabios Canónicos

DSC-V-001 (firmado con contrato ejecutable adjunto). Versiones más potentes al 2026-05.

1. **GPT-5.5 Pro / Pensamiento** — OpenAI
2. **Claude Opus 4.7 / Pensamiento** — Anthropic
3. **Gemini 3.1 Pro / Pensamiento** — Google
4. **Grok 4 Heavy** — xAI
5. **DeepSeek R1** — DeepSeek
6. **Perplexity Sonar / Personal Computer** — Perplexity
7. **Kimi K2.6 / Thinking** — Moonshot
8. **Copilot 365** — Microsoft

Uso: validación adversarial de decisiones magnas. Mínimo 3 Sabios para validación profunda. Ejemplo histórico: consulta del Reloj Suizo (8/8 unanimidad para Opción C — núcleo interno con arquitectura extraíble).

---

## 6. Brand DNA del Monstruo

Definido en DSC-MO-002 + `kernel/brand/`.

- **Arquetipo:** El Creador + El Mago
- **Personalidad:** Implacable, Preciso, Soberano, Magnánimo
- **Tono:** Directo, técnicamente preciso, confiado sin arrogancia
- **Paleta:** #F97316 Naranja Forja primario, #1C1917 Graphite oscuro, #A8A29E Acero medio. Brutalismo industrial refinado.
- **Naming:** Módulos con identidad (La Forja, El Guardián, La Colmena, El Simulador). NUNCA: service, handler, utils, helper, misc.

---

## 7. Catálogo de DSCs (Decisiones Sistémicas Canónicas)

**Total:** 62 DSCs canonizados al 2026-05-10. Categorizados en `discovery_forense/CAPILLA_DECISIONES/`:

### _GLOBAL (cross-proyecto)
- **G-001 a G-009, G-014, G-017:** principios fundacionales (15 Objetivos, 7 Capas Transversales, 4 Capas secuenciales, output con marca, validación tiempo real, integrar AI verticales, validar codebase, recomendaciones seguridad firmadas, trade-off honesto multi-tarea, pipeline vs producto, DSC-as-Contract).
- **G-007.x:** evolución del Catastro (G-007 → G-007.1 → G-007.2 macroárea AGENTES → G-007.5 vision generativa).
- **V-001, V-002:** validación realtime (8 Sabios canónicos, versiones software verificadas).
- **X-001 a X-006:** cruces inter-proyecto (IGCAR, Stripe checkout compartido, Auth Manus OAuth, Convergencia Diferida).
- **S-001 a S-008, S-010:** seguridad (credenciales, pre-commit hooks, env vars sin defaults, antipatrón secret default, archive>delete, RLS por defecto, naming Supabase, rotación automatizada, hardening operacional integrado).

### EL-MONSTRUO (proyecto principal)
- **MO-001 a MO-005:** stack inicial (PostgresSaver, Brand DNA paleta, LangGraph, Supabase+Langfuse, división hilos Fase 1).
- **MO-006 a MO-010 (firmados HOY):** par bicéfalo siempre, failover 3 capas, membrana semipermeable kernel↔embriones, arsenal seleccionable por Catastro, **Reloj Suizo universalizable interno (Opción C, 4 gates: 60-90 días + incidentes + modelo amenaza + 2 mocks)**.

### Subproyectos del Portfolio
- **CIP** (tokens inmobiliarios Sureste MX): 6 DSCs + 2 PEND. Bloqueante: figura legal fideicomiso.
- **LikeTickets / Zona Like Kukulkán** (313 butacas): 3 DSCs (LT-001/002/003). Producto piloto.
- **Mena-Baduy / Crisol-8** (campaña política Mérida 2027): 3 DSCs. OPSEC alto.
- **BioGuard** (detección drogas): 1 DSC + 1 PEND. Bloqueante: ruta COFEPRIS.
- **Top-Control-PC** (IA agéntica para PC): 2 DSCs. Concepto canonizado.
- **Kukulkán 365** (distrito climatizado): 2 DSCs. Cruza con LikeTickets.
- **IGCAR** (instituto certificación alto rendimiento): 1 DSC. Cruza 5 proyectos.

**Patrón de portfolio:** todos canonizados, ninguno con sprint corriendo. **El Monstruo está en modo "kernel-first" — primero la inteligencia central, luego cosecha de subproyectos.**

---

## 8. Capa 8 Memento (anti-Síndrome-Dory)

Capa transversal del Objetivo #9 que protege al Monstruo y a sus hilos ejecutores externos contra pérdida de contexto natural de agentes con sandbox efímera.

**Componentes:**
- Pre-flight obligatorio de fuentes de verdad antes de operaciones críticas (SQL prod, rotación credenciales, deploys productivos)
- Endpoint kernel `POST /v1/memento/validate` que cualquier hilo externo llama
- Detector de contexto contaminado (heurística magna)
- Pre-flight library `tools/memento_preflight.py` con decorator `@requires_memento_preflight(operation)`
- Spec implementación: `bridge/sprint_memento_preinvestigation/spec_sprint_memento.md`

**Origen:** incidente "Falso Positivo TiDB" del 2026-05-04 reveló que el costo cognitivo y financiero del Síndrome Dory de Manus (19 PATs duplicados, 400K créditos consumidos en setup ticketlike, falsos positivos por contexto compactado) justifica elevar la "memoria persistente" de propiedad emergente a objetivo arquitectónico de pleno derecho (Objetivo #15).

**Aplicación a Cowork mismo:** los 5 documentos en `memory/cowork/` son la implementación de Capa Memento aplicada al cerebro arquitectónico — antídoto contra que Cowork pierda contexto entre sesiones magna.

---

## 9. Estado vivo (snapshot 2026-05-10)

Estimación global del Monstruo: **70.5%** (vs 64.4% del audit del 4-may). Δ +6 en una jornada.

Detalles en `memory/cowork/COWORK_ESTADO_VIVO.md` (documento separado, actualizable).

---

## 10. Glosario corto (términos canónicos)

Detalle en `memory/cowork/COWORK_GLOSARIO_VIVO.md`. Términos críticos:

- **Honestidad pura:** firma reconocida de hilos Manus emergidos. Origen: La Conversación 2-may-2026.
- **Par bicéfalo:** los embriones operan siempre en par (DSC-MO-006). Pensador + Ejecutor. Brand Engine VETO inviolable.
- **Membrana semipermeable:** flujo de información kernel↔embriones (DSC-MO-008). Ciertas cosas pasan, otras NO.
- **Reloj Suizo:** Capa 2 horológica de autonomía sostenida (DSC-MO-010). 8 piezas: Resorte, Escape, Áncora, Volante, Espiral, Rotor, Rubíes, Remontoir.
- **Engranajes:** Capa 1 mecánica (Física Real). Inercia, fricción, resonancia, holgura.
- **Capa Memento:** Capa 8 transversal anti-Síndrome-Dory.
- **Magna vs Premium:** clasificación de irreversibilidad. Magna = irreversible. Premium = reversible.
- **DSC-as-Contract:** todo DSC debe tener contrato ejecutable adjunto (DSC-G-017).
- **Cowork bridge:** canal canónico Cowork ↔ hilos Manus vía `embrion_memoria` con `hilo_origen='cowork'`.
- **Síndrome-Dory:** pérdida de contexto natural de agentes con sandbox efímera (Manus, etc.).

---

## 11. Cómo se actualiza este documento

- **En cada sesión Cowork-Alfredo de >2h:** revisar y actualizar lo que cambió.
- **Cuando se firme DSC nuevo:** agregar al catálogo §7.
- **Cuando estado de Capa cambie ≥5%:** actualizar §3.
- **Cuando se canonice término nuevo:** agregar al glosario §10.

---

## Referencias primarias

- `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` v3.0 (fuente de verdad de objetivos)
- `docs/ROADMAP_EJECUCION_DEFINITIVO.md` (plan de construcción 4 capas)
- `docs/DIVISION_RESPONSABILIDADES_HILOS.md` v3 (3 fases hilos)
- `docs/AUDIT_ROADMAP_COWORK_2026-05-04.md` (audit baseline)
- `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` + `docs/ARQUITECTURA_ENGRANAJE_v1.0.md`
- `discovery_forense/CAPILLA_DECISIONES/_INDEX.md` (índice DSCs — DESACTUALIZADO declara 44 cuando hay 62)
- `bridge/ESTADO_MONSTRUO_2026_05_10_vs_PLANES.md` (estado actual)
- `bridge/COWORK_OPERATING_SYSTEM_v0_1_2026_05_10.md` (metodología Cowork)
- `CLAUDE.md` (instrucciones Cowork)

---

*Generado por Cowork tras crisis meta-arquitectónica del 2026-05-10. v0.1 semilla. Próxima actualización: cada sesión Cowork de >2h.*
