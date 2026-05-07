---
id: DSC-G-007
proyecto: GLOBAL
tipo: restriccion_dura
titulo: "El Monstruo integra herramientas AI verticales líderes; nunca las reinventa. CUATRO Catastros paralelos: Modelos LLM + Agentes 2026 + Herramientas AI Verticales + Suppliers Humanos."
estado: firme (v1.1 ampliado a 4 catastros 2026-05-06)
fecha: 2026-05-06 (v1) / 2026-05-06 (v1.1 ampliación a 4 catastros)
fuentes:
  - repo:docs/EL_MONSTRUO_APP_VISION_v1.md
  - skill:el-monstruo
  - chat:cowork-manus-2026-05-06 (gap conceptual detectado por Manus durante audit pre-Catastro-A)
  - repo:docs/biblias_agentes_2026/ (21 biblias canónicas que detonaron el cuarto catastro)
cruza_con: [TODOS, DSC-S-001, DSC-V-002]
---

# Cuatro Catastros paralelos + integración de herramientas AI verticales

## Decisión

**v1 (original 2026-05-06):** El Monstruo opera con TRES motores de orquestación paralelos: Catastro de Modelos LLM (50+ modelos generales), Catastro de Suppliers Humanos, y Catastro de Herramientas AI Especializadas. Cuando una capability vertical tiene líderes claros en el mercado, el Monstruo SIEMPRE las integra vía el Catastro correspondiente, NUNCA desarrolla competidor interno.

**v1.1 (ampliación 2026-05-06):** Conversación Cowork ↔ Manus durante audit pre-Catastro-A detectó **gap conceptual**: las 21 biblias canónicas en `docs/biblias_agentes_2026/` (Claude Code, Cline, Devin, OpenAI Operator, Manus v3, Project Mariner, UI TARS, Hermes, Lindy, etc.) son **AGENTES** — sistemas autónomos completos con loops propios — no son ni Modelos LLM crudos, ni Tools verticales, ni Suppliers humanos. Necesitan su propio catastro.

**Taxonomía firmada (4 catastros canónicos):**

| Catastro | Definición | Ejemplos | Cantidad inicial |
|---|---|---|---|
| **Modelos LLM** | Endpoint LLM crudo + tokens + cost/1k. Sin loop, sin tools nativas, sin orquestación. | GPT-5.5, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, Kimi K2.5, DeepSeek R1 | 6 actuales (extender a 50+) |
| **Agentes 2026** (NUEVO en v1.1) | Sistemas autónomos completos con loops propios, tools nativas, capability orquestada | Claude Code, Cline, Devin, OpenAI Operator, Manus v3, Project Mariner, UI TARS, Hermes, Lindy, Metis, Neo, Laguna XS2, Perplexity Computer/Enterprise, Grok Voice, Gemini Robotics, Meta AI Agent, Agent S, Kimi K2.6, Kiro | 21 (de biblias canónicas) |
| **Herramientas AI Verticales** | Capability específica orquestable, sin loop autónomo | LlamaParse, Runway Gen-4, ElevenLabs, Spline AI, RoomGPT, Modsy, Luma, Cursor, Codeium, Midjourney, Flux | 16-25 (realtime fresh) |
| **Suppliers Humanos** | Personas que entregan trabajo (servicios profesionales) | Arquitectos, valuadores, fotógrafos, contratistas, abogados (Sureste MX inicial) | 30+ |

## Por qué

### v1 (catastros 1, 3, 4 — Modelos, Tools, Suppliers)

Cumple Obj #7 (no reinventar rueda) + Obj #12 (soberanía agnóstica: si una herramienta cae, el Catastro selecciona otra). Las herramientas AI verticales evolucionan 10x más rápido que un equipo interno. La ventaja del Monstruo es orquestación + contexto del usuario, no generación per se.

### v1.1 (catastro 2 — Agentes 2026, NUEVO)

Los Agentes 2026 cumplen 3 funciones para Manus específicamente:

1. **Catálogo de delegación.** Manus tiene tarea fuera de su zona → consulta `catastro.agentes.find_best(capability)` → delega a agente óptimo (ej: browser autónomo → Project Mariner, voice synthesis premium → Grok Voice, robot control → Gemini Robotics).

2. **Espejo peer (auto-aprendizaje).** Manus consulta `catastro.agentes.peers_of("manus_v3")` → obtiene Claude Code, Cline, Devin, OpenAI Operator → loop semanal: extraer 3 patrones nuevos de cada peer → proponer adopción. Auto-evolución sin reinventar (Obj #7 aplicado al propio agente).

3. **Self-reference (anti-Dory aplicado a Manus).** Antes de operación irreversible, `catastro.agentes.validate_against_spec()` valida decisiones recientes contra `BIBLIA_MANUS_v3_REFERENCIA.md`. Sin esto, Manus en sesión 8 puede olvidar guardrails de Manus v3 y hacer cosas que no debería.

Sin el Catastro de Agentes, las 21 biblias quedan como markdown estático sin estructura consultable — desaprovechadas.

## Implicaciones

### Para empresas-hijas y módulos del kernel

Cada empresa-hija que necesita capability vertical invoca el Catastro correspondiente en runtime — no hardcodea herramientas. Cuando una herramienta nueva supera a una existente en ranking, el Catastro la promueve sin tocar código de empresas-hijas. Cockpit gana superficie de "Salud de los 4 Catastros" + FinOps gana track per-recurso (modelo, agente, tool, supplier).

### Para Manus (consumidor del Catastro de Agentes)

Manus consume el Catastro de Agentes 2026 vía 3 interfaces operativas (definidas en Sprint Catastro-A v2 Tarea D):

```python
catastro.agentes.find_best(task, capability, budget, latency)  # delegación
catastro.agentes.peers_of("manus_v3")                          # auto-aprendizaje
catastro.agentes.my_canonical_spec()                           # anti-Dory self-ref
catastro.agentes.validate_against_spec(recent_decisions)       # pre-flight Capa Memento
```

### Excepciones

- **Modelos propios del Monstruo (Capa 3 Soberanía)** son infraestructura crítica del orquestador, no herramientas verticales. Viven en su propio módulo, no en el Catastro.
- **Manus mismo** está en el Catastro de Agentes 2026 (`BIBLIA_MANUS_v3_REFERENCIA.md`) para self-reference, no para delegación a sí mismo.

### Reglas de credenciales (DSC-S-001 + S-003 + S-004 anidados)

Los 4 archivos JSON (`catastro_models.json`, `catastro_agentes.json`, `catastro_tools.json`, `catastro_suppliers.json`) viven en repo público SIN credenciales. Cada entry contiene SOLO metadata pública (nombre, endpoint, capabilities, scoring, fallbacks). Los secrets viven en env vars resueltas con `os.environ[VAR]` (fail loud) vía helper `kernel/security/credential_resolver.py`.

## Estado de validación

**firme — v1 + v1.1 ampliado.**

v1 fruto de iteración Cowork-Alfredo durante sesión 2026-05-06 detonado por Marketplace de Interiorismo + necesidad de renderizado AI.

v1.1 fruto de gap conceptual detectado por Manus Hilo Catastro durante audit pre-sprint Catastro-A del 2026-05-06: las 21 biblias en `docs/biblias_agentes_2026/` no encajaban en ninguno de los 3 catastros originales. Cowork canonizó la taxonomía Modelos vs Agentes vs Tools vs Suppliers en la misma sesión y ampliamos a 4 catastros antes de que Manus arrancara Catastro-A. Aplicación temprana de DSC-G-008 v2 (validar antes de specs) + DSC-G-009 (recomendaciones firmadas en misma sesión).
