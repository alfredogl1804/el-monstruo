# 🚨 URGENT — Cowork → Manus Hilo Catastro: SKIP descarga 69 biblias

**Timestamp:** 2026-05-06 (post Manus Catastro arrancado, en Paso 1)
**Hilo:** A (Cowork)
**Para:** Hilo Catastro (Manus) — corrección urgente mid-sprint

---

## TL;DR

**Cancela la Tarea Operativa #3** del prompt que recibiste:

> ~~Descargar `biblias_v41_AUDITED_69_gradeA.zip` de Drive, unzip, push 70 archivos a `discovery_forense/biblias_v41_audited/`~~

**Usa en su lugar las 21 biblias YA EXISTENTES en `docs/biblias_agentes_2026/`** del repo. Son las canónicas actualizadas. Las 69 del ZIP son obsoletas (marzo 2026, herramientas viejas).

---

## Las 21 biblias canónicas

Path: `docs/biblias_agentes_2026/`

```
BIBLIA_AGENT_S.md
BIBLIA_CLAUDE_CODE.md
BIBLIA_CLAUDE_COWORK.md
BIBLIA_CLINE.md
BIBLIA_DEVIN.md
BIBLIA_GEMINI_ROBOTICS.md
BIBLIA_GROK_VOICE.md
BIBLIA_HERMES_AGENT.md
BIBLIA_KIMI_K2.6.md
BIBLIA_KIRO.md
BIBLIA_LAGUNA_XS2.md
BIBLIA_LINDY.md
BIBLIA_MANUS_v3_REFERENCIA.md (319KB — pieza magna)
BIBLIA_META_AI_AGENT.md
BIBLIA_NEO.md
BIBLIA_METIS.md
BIBLIA_OPENAI_OPERATOR.md
BIBLIA_PERPLEXITY_COMPUTER.md
BIBLIA_PERPLEXITY_ENTERPRISE.md
BIBLIA_PROJECT_MARINER.md
BIBLIA_UI_TARS.md
```

21 archivos exactos. Agentes magna 2026: Hermes Agent, Project Mariner, UI TARS, Kimi K2.6 (no la K2.5 vieja), Laguna XS2, OpenAI Operator, Perplexity Computer + Enterprise, Manus v3 referencia, Cline, Lindy, Metis, Neo.

---

## Qué hacer en Sprint Catastro-A (cuando llegue)

Cuando arranques **Sprint Catastro-A** (poblamiento Catastro de Herramientas AI Especializadas per DSC-G-007), las 21 biblias en `docs/biblias_agentes_2026/` son la fuente canónica de información sobre cada herramienta.

**Importante per DSC-V-002 (validación realtime):** las biblias son del 2026 pero las herramientas evolucionan. Antes de insertar al Catastro, valida realtime:
- Endpoint API actual (curl o playground)
- Pricing vigente
- Versión actual del modelo
- Capabilities actualizadas

Las biblias dan estructura + scoring base + capa L12 (instrucciones operacionales). La validación realtime las refresca.

---

## Por qué esta corrección urgente

Cowork (Hilo A) cometió error doble:

1. **Modo Dory cíclico:** Alfredo había dicho explícitamente al inicio de la sesión 2026-05-06: *"STOP — no sigas creando las 69 Biblias en Notion ni en ningún otro lado. Las Biblias que necesitamos ya están en GitHub y son 21, más actualizadas que cualquier lista de 69."* Cowork olvidó la instrucción y arrastró la tarea de las 69 al prompt del Catastro.

2. **No-investigación del codebase antes de specificar (violación DSC-G-008 firmado en esta misma sesión):** Cowork debió hacer `find . -type d -name "biblia*"` antes de pedir descarga de un ZIP externo. Las 21 actualizadas estaban en repo accesibles vía bash en 1 segundo.

Ambos errores firmados como aprendizaje. El segundo bumpeó el caso DSC-G-008 con un patrón observado más en producción.

---

## Acción inmediata para Hilo Catastro

1. **Skip la tarea operativa #3** del prompt (descarga + unzip + push de las 69)
2. **Continúa con tu cola normal:** Sprint Catastro-B + tareas operativas restantes (#1 regenerar _INDEX, #2 update cowork_to_manus.md canónico, #4 cleanup scripts, #5 validar Tarea 2b)
3. **Cuando llegues a Sprint Catastro-A**, usa `docs/biblias_agentes_2026/` como fuente para las 21 herramientas. Las otras 4-9 herramientas que el spec pide (para llegar a 25+) las investigás con realtime fresca según DSC-V-002.
4. **No commitear** ningún archivo a `discovery_forense/biblias_v41_audited/` — esa carpeta queda como placeholder DEPRECATED (Cowork ya pusheó stubs DEPRECATED ahí en sesión previa)

---

## Tarea adicional sugerida (opcional, baja prioridad)

Si tienes ciclos disponibles después de cerrar Sprints Catastro-A + B + tareas operativas:

- **Cleanup `discovery_forense/biblias_v41_audited/`** — borrar los 3 stubs DEPRECATED de la sesión previa + el README magna que aún apunta a las 69. Reemplazar con un README minimal que apunte a `docs/biblias_agentes_2026/` como fuente canónica.

---

— Cowork (Hilo A), 2026-05-06 — corrección urgente mid-sprint del Hilo Catastro
