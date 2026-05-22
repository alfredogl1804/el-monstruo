# 01 - ENTITY MATRIX (Tabla Periodica del Monstruo)

> Auto-generado desde MONSTRUO_GENOME.yaml (2026-05-22T06:52:42Z)
> Total entidades: 48
> Regenerar: `python3 scripts/generate_reality_kernel.py`

---

## CREATURE
*Criaturas y productos con vida propia*

| ID | Path | Files | Source | Status |
|---|---|---|---|---|
| like-kukulkan-tickets | `alfredogl1804/like-kukulkan-tickets` | 0 | satellite | active |

## FUTURE_VISION
*Visiones futuras no implementadas*

| ID | Path | Files | Source | Status |
|---|---|---|---|---|
| el-mundo-de-tata | `alfredogl1804/el-mundo-de-tata` | 0 | satellite | in_development |

## GOVERNANCE
*Gobierno, seguridad y validacion*

| ID | Path | Files | Source | Status |
|---|---|---|---|---|
| guardian_runner | `kernel/guardian_runner/` | 3 | kernel | production |
| security | `kernel/security/` | 1 | kernel | production |
| sovereignty | `kernel/sovereignty/` | 1 | kernel | production |
| validation | `kernel/validation/` | 2 | kernel | production |

## INTELLIGENCE_SYSTEM
*Sistemas de inteligencia y registro*

| ID | Path | Files | Source | Status |
|---|---|---|---|---|
| catastro | `kernel/catastro/` | 27 | kernel | production |
| catastros | `kernel/catastros/` | 6 | kernel | production |
| learning | `kernel/learning/` | 1 | kernel | production |
| vanguard | `kernel/vanguard/` | 4 | kernel | production |

## INVISIBLE_INFRA
*Infraestructura invisible que sostiene todo*

| ID | Path | Files | Source | Status |
|---|---|---|---|---|
| alerts | `kernel/alerts/` | 2 | kernel | production |
| auth | `kernel/auth.py` | 1 | kernel | production |
| background_store | `kernel/background_store.py` | 1 | kernel | production |
| critic_visual | `kernel/embriones/critic_visual.py` | 1 | embrion | production |
| dashboards | `kernel/dashboards/` | 3 | kernel | production |
| forja-mcp | `alfredogl1804/forja-mcp` | 0 | satellite | healthy |
| main | `kernel/main.py` | 1 | kernel | production |
| milestones | `kernel/milestones/` | 1 | kernel | production |
| motion | `kernel/motion/` | 2 | kernel | production |
| product_architect | `kernel/embriones/product_architect.py` | 1 | embrion | production |
| rotor | `kernel/rotor/` | 10 | kernel | production |
| runner | `kernel/runner/` | 4 | kernel | production |

## MAGIC_CAPABILITY
*Capacidades magicas de alto nivel*

| ID | Path | Files | Source | Status |
|---|---|---|---|---|
| adaptive_model_selector | `kernel/adaptive_model_selector.py` | 1 | kernel | production |
| brand | `kernel/brand/` | 3 | kernel | production |
| brand_engine | `kernel/embriones/brand_engine/brand_engine.py` | 1 | embrion | production |
| causal_decomposer | `kernel/causal_decomposer.py` | 1 | kernel | production |
| cost_optimizer | `kernel/cost_optimizer.py` | 1 | kernel | production |
| design | `kernel/design/` | 1 | kernel | production |

## MEMORY_SYSTEM
*Sistemas de memoria y persistencia cognitiva*

| ID | Path | Files | Source | Status |
|---|---|---|---|---|
| anti_dory | `kernel/anti_dory/` | 15 | kernel | production |
| memento | `kernel/memento/` | 4 | kernel | production |
| memory | `kernel/memory/` | 7 | kernel | production |

## PROTOCOL_SPEC
*Protocolos e interfaces de comunicacion*

| ID | Path | Files | Source | Status |
|---|---|---|---|---|
| a2ui | `kernel/a2ui/` | 1 | kernel | production |
| agui_adapter | `kernel/agui_adapter.py` | 1 | kernel | production |
| browser | `kernel/browser/` | 1 | kernel | production |
| critic_visual_browserless_fallback | `kernel/embriones/critic_visual_browserless_fallback.py` | 1 | embrion | production |
| el-monstruo-bot | `alfredogl1804/el-monstruo-bot` | 0 | satellite | offline |
| plugins | `kernel/plugins/` | 2 | kernel | production |

## WORKER_ROLE
*Agentes especialistas que ejecutan tareas*

| ID | Path | Files | Source | Status |
|---|---|---|---|---|
| collective | `kernel/collective/` | 3 | kernel | production |
| embrion_creativo | `kernel/embriones/embrion_creativo.py` | 1 | embrion | production |
| embrion_estratega | `kernel/embriones/embrion_estratega.py` | 1 | embrion | production |
| embrion_financiero | `kernel/embriones/embrion_financiero.py` | 1 | embrion | production |
| embrion_investigador | `kernel/embriones/embrion_investigador.py` | 1 | embrion | production |
| embrion_loop | `kernel/embrion_loop.py` | 1 | kernel | production |
| embrion_specializations | `kernel/embrion_specializations/` | 0 | kernel | production |
| embrion_tecnico | `kernel/embriones/tecnico/embrion_tecnico.py` | 1 | embrion | production |
| embrion_ventas | `kernel/embriones/ventas/embrion_ventas.py` | 1 | embrion | production |
| embrion_vigia | `kernel/embrion_vigia.py` | 1 | kernel | production |
| embriones | `kernel/embriones/` | 17 | kernel | production |

---

## Clases Ontologicas (Leyenda)

| Clase | Significado | Regla de Veto |
|---|---|---|
| MEMORY_SYSTEM | Persistencia cognitiva | No crear nuevos stores sin conectar a SMS |
| WORKER_ROLE | Agentes que ejecutan | No crear embriones sin verificar existentes |
| INTELLIGENCE_SYSTEM | Registros y RAGs | No crear catastros/indexes paralelos |
| MAGIC_CAPABILITY | Capacidades de alto nivel | No duplicar optimizadores/selectores |
| GOVERNANCE | Gobierno y seguridad | No crear guardianes paralelos |
| PROTOCOL_SPEC | Interfaces y protocolos | No crear adapters sin verificar MCP/A2UI |
| INVISIBLE_INFRA | Infraestructura base | No crear runners/rotors paralelos |
| CREATURE | Productos con vida propia | No crear productos sin firma T1 |
| FUTURE_VISION | Aspirantes no implementados | Existen como concepto, no duplicar |

