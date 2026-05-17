# 01 — CONTEXT INDEX

> **Iteración 001** — mapa completo del Fabric. Actualizar al inicio de cada iteración.

---

## Estructura

```
interfaces_context_fabric/
├── 00_START_HERE_FOR_CHATGPT.md            ← punto de entrada para ChatGPT
├── 01_CONTEXT_INDEX.md                      ← este archivo
├── 02_SOURCE_LEDGER.jsonl                   ← inventario JSONL de 32 fuentes
├── 03_GAPS_AND_UNKNOWN_UNKNOWNS.md          ← lo que falta + lo que no sabemos que no sabemos
├── 04_DECISION_LEDGER.md                    ← decisiones T1 magna pendientes + nuevas
├── 05_CHATGPT_REQUESTS_TO_MANUS.md          ← bandeja para que ChatGPT pida cosas a Manus
│
├── context_packs/
│   ├── PACK_00_BOOTSTRAP.md                 ← narrativa magna 1-pager
│   ├── PACK_01_ACTO_1_INTERFACES.md         ← Acto 1 (20 superficies, paleta, Realignment)
│   ├── PACK_02_ACTO_2_CALM_TECH.md          ← Acto 2 (Engranaje + Reloj Suizo + Calm Tech)
│   ├── PACK_03_AI_FIRST_LIVING.md           ← Hipótesis naciente AGT-001 (NO canon)
│   ├── PACK_04_CRONOS_RIO_DE_VIDA.md        ← 5 acepciones disjuntas de Cronos
│   ├── PACK_05_METODOLOGIAS_PRODUCTIVIDAD.md ← 10+2 especialidades + MaaS
│   ├── PACK_06_RELOJ_SUIZO_ENGRANAJE.md     ← 8 piezas Patek + topología engranaje
│   ├── PACK_07_TRANSPORTS_UI.md             ← Telegram, Flutter, AG-UI, Web CC, WhatsApp, Watch
│   ├── PACK_08_SPRINTS_PENDIENTES.md        ← inventario sprints UI + estado
│   ├── PACK_09_REFLEXIONES_ALFREDO_COWORK.md ← citas verbatim densas
│   └── PACK_10_REALIDAD_CODIGO_ACTUAL.md    ← drift código vs doctrina
│
├── maps/
│   ├── SURFACE_REGISTRY.yaml                ← 20 superficies + Command Center 7
│   ├── TRANSPORT_REGISTRY.yaml              ← 6 transports + Transport Cero
│   ├── SPRINT_REGISTRY.yaml                 ← sprints UI con estado
│   ├── CANON_REGISTRY.yaml                  ← qué está canonizado
│   ├── HYPOTHESIS_REGISTRY.yaml             ← hipótesis nacientes
│   ├── CONTRADICTIONS_MAP.md                ← contradicciones internas
│   └── TIMELINE_INTERFACES.md               ← cronología 6-may a 17-may
│
├── raw_rescues/                             ← (vacío en iteración 001)
│
├── schemas/                                 ← (vacío en iteración 001)
│
├── prompts/
│   ├── PROMPT_COWORK_EXTERNAL_AUDITOR.md    ← prompt para Cowork como auditor
│   ├── PROMPT_PERPLEXITY_EXTERNAL_AUDITOR.md ← prompt para Perplexity como auditor
│   └── PROMPT_CHATGPT_NEXT_ITERATION.md     ← prompt para iteración 002
│
├── reports/
│   ├── ITERATION_001_REPORT.md              ← reporte de cierre de esta iteración
│   └── fabric_grep_results.md               ← output del grep transversal (1442 líneas)
│
└── scripts/
    └── fabric_grep.sh                       ← script de grep mantenible
```

---

## Convenciones

### Estados de verdad por item

- **CANON_VIGENTE** — firmado, vigente, aplicable hoy
- **CANON_HISTORICO** — fue canónico, ya no aplica, preservado por trazabilidad
- **HIPOTESIS_NACIENTE** — articulado pero NO firmado por T1, ChatGPT NO debe canonizar
- **PENDIENTE_T1** — espera firma de Alfredo
- **CONTRADICCION** — choca con otro canon vigente
- **INVALIDADO** — explícitamente rechazado
- **SOLO_TRAZABILIDAD** — preservar la huella histórica, no actuable
- **REQUIERE_VERIFICACION** — falta evidencia binaria

### Niveles de evidencia

- **E1** — código en repo (path:line)
- **E2** — doc canónico firmado (markdown, audit Cowork)
- **E3** — chat verbatim
- **E4** — relato/memoria

---

## Mapa de fuentes magna por área

| Área | Fuente magna |
|---|---|
| Filosofía Acto 1 | SRC-001 (`docs/EL_MONSTRUO_APP_VISION_v1.md`) |
| Realidad código vs doctrina | SRC-002 (`memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md`) |
| Filosofía Acto 2 | SRC-003 + SRC-004 + SRC-005 |
| Realignment Mobile | SRC-006 |
| A2UI canon | SRC-014 (spec firmado) + SRC-015 (código real) |
| Brand DNA canon | SRC-016 (Python) + SRC-018 (mirror multi-lenguaje) + SRC-022 (DSC) |
| Capabilities backend | derivado de SRC-002 §1 |
| Skill curado | SRC-021 (interfaces-monstruo-doctrina) |

---

## Cómo updatear este index

Al inicio de cada iteración:
1. Verificar lista de archivos vs reales
2. Updatear conteo de fuentes en SOURCE_LEDGER
3. Marcar archivos vaciados o reescritos
4. Si se agrega un context_pack o map nuevo, agregarlo aquí con descripción de 1 línea
