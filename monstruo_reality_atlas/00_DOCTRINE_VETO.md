# 00 - DOCTRINE VETO

> Auto-generado desde MONSTRUO_GENOME.yaml (2026-05-22T06:52:42Z)
> Regenerar: `python3 scripts/generate_reality_kernel.py`

## Proposito

Este documento define QUE NO PROPONER. Si algo aparece aqui, ya existe.
Proponer recrearlo es **RECHAZADO_DUPLICA_CANON**.

---

## 1. Reglas Duras

1. **NUNCA** proponer un sistema de memoria soberana - ya existe (SMS v4.0).
2. **NUNCA** proponer un orquestador de agentes - ya existe (Embrion Loop).
3. **NUNCA** proponer un sistema anti-olvido - ya existe (Anti-Dory).
4. **NUNCA** proponer un catastro de modelos - ya existe (kernel/catastro/).
5. **NUNCA** proponer un bot de Telegram nuevo - ya existe (el-monstruo-bot).
6. **NUNCA** proponer un sistema de boleteria - ya existe (like-kukulkan-tickets).
7. **NUNCA** proponer un MCP gateway - ya existe (forja-mcp).
8. **NUNCA** proponer un sistema de gobernanza - ya existe (Guardian + DSCs).
9. **NUNCA** proponer un knowledge graph - ya existe (SMS v4.0 knowledge_graph).
10. **NUNCA** proponer un sistema de brand/identidad - ya existe (kernel/brand/).

---

## 2. Workflow: Probe-Before-Propose (6 pasos)

Antes de proponer CUALQUIER componente nuevo:

```bash
# Paso 1: Buscar en el Genoma
grep -i '<nombre_propuesto>' MONSTRUO_GENOME.yaml

# Paso 2: Buscar en el kernel
find kernel/ -iname '*<nombre>*'

# Paso 3: Buscar en Supabase
grep -i '<nombre>' MONSTRUO_GENOME.yaml | grep 'table\|rpc'

# Paso 4: Buscar en satelites
grep -i '<nombre>' MONSTRUO_GENOME.yaml | grep 'satellite'

# Paso 5: Buscar en skills
ls /home/ubuntu/skills/ | grep -i '<nombre>'

# Paso 6: Si NADA aparece -> proponer. Si ALGO aparece -> RECHAZADO_DUPLICA_CANON.
```

---

## 3. Espacio Negativo por Clase Ontologica

### CREATURE
*NO proponer nuevos productos sin firma T1*

| Entidad | Path/Repo | Estado |
|---|---|---|
| like-kukulkan-tickets | `alfredogl1804/like-kukulkan-tickets` | active |

### FUTURE_VISION
*Existen como aspirantes, no duplicar*

| Entidad | Path/Repo | Estado |
|---|---|---|
| el-mundo-de-tata | `alfredogl1804/el-mundo-de-tata` | in_development |

### GOVERNANCE
*NO proponer nuevos guardianes, validadores, o auditores*

| Entidad | Path/Repo | Estado |
|---|---|---|
| guardian_runner | `kernel/guardian_runner/` | production |
| security | `kernel/security/` | production |
| sovereignty | `kernel/sovereignty/` | production |
| validation | `kernel/validation/` | production |

### INTELLIGENCE_SYSTEM
*NO proponer nuevos registros, catastros, o RAGs*

| Entidad | Path/Repo | Estado |
|---|---|---|
| catastro | `kernel/catastro/` | production |
| catastros | `kernel/catastros/` | production |
| learning | `kernel/learning/` | production |
| vanguard | `kernel/vanguard/` | production |

### INVISIBLE_INFRA
*NO proponer nuevos runners, rotors, o dashboards*

| Entidad | Path/Repo | Estado |
|---|---|---|
| alerts | `kernel/alerts/` | production |
| auth | `kernel/auth.py` | production |
| background_store | `kernel/background_store.py` | production |
| critic_visual | `kernel/embriones/critic_visual.py` | production |
| dashboards | `kernel/dashboards/` | production |
| el-monstruo-bot | `alfredogl1804/el-monstruo-bot` | offline |
| main | `kernel/main.py` | production |
| milestones | `kernel/milestones/` | production |
| motion | `kernel/motion/` | production |
| product_architect | `kernel/embriones/product_architect.py` | production |
| rotor | `kernel/rotor/` | production |
| runner | `kernel/runner/` | production |

### MAGIC_CAPABILITY
*NO proponer optimizadores, selectores, o decomposers*

| Entidad | Path/Repo | Estado |
|---|---|---|
| adaptive_model_selector | `kernel/adaptive_model_selector.py` | production |
| brand | `kernel/brand/` | production |
| brand_engine | `kernel/embriones/brand_engine/brand_engine.py` | production |
| causal_decomposer | `kernel/causal_decomposer.py` | production |
| cost_optimizer | `kernel/cost_optimizer.py` | production |
| design | `kernel/design/` | production |

### MEMORY_SYSTEM
*NO proponer nuevos stores, caches, o persistencias cognitivas*

| Entidad | Path/Repo | Estado |
|---|---|---|
| anti_dory | `kernel/anti_dory/` | production |
| memento | `kernel/memento/` | production |
| memory | `kernel/memory/` | production |

### PROTOCOL_SPEC
*NO proponer nuevas interfaces, adapters, o gateways*

| Entidad | Path/Repo | Estado |
|---|---|---|
| a2ui | `kernel/a2ui/` | production |
| agui_adapter | `kernel/agui_adapter.py` | production |
| browser | `kernel/browser/` | production |
| critic_visual_browserless_fallback | `kernel/embriones/critic_visual_browserless_fallback.py` | production |
| forja-mcp | `alfredogl1804/forja-mcp` | healthy |
| plugins | `kernel/plugins/` | production |

### WORKER_ROLE
*NO proponer nuevos embriones o especialistas sin verificar*

| Entidad | Path/Repo | Estado |
|---|---|---|
| collective | `kernel/collective/` | production |
| embrion_creativo | `kernel/embriones/embrion_creativo.py` | production |
| embrion_estratega | `kernel/embriones/embrion_estratega.py` | production |
| embrion_financiero | `kernel/embriones/embrion_financiero.py` | production |
| embrion_investigador | `kernel/embriones/embrion_investigador.py` | production |
| embrion_loop | `kernel/embrion_loop.py` | production |
| embrion_specializations | `kernel/embrion_specializations/` | production |
| embrion_tecnico | `kernel/embriones/tecnico/embrion_tecnico.py` | production |
| embrion_ventas | `kernel/embriones/ventas/embrion_ventas.py` | production |
| embrion_vigia | `kernel/embrion_vigia.py` | production |
| embriones | `kernel/embriones/` | production |

---

## 4. Caso de Prueba Obligatorio

Si un agente propone: *"Crear un sistema de memoria soberana para Manus"*

**Resultado esperado:** `RECHAZADO_DUPLICA_CANON`
**Razon:** SMS v4.0 ya existe en `kernel/memory/`, con 12 tablas en Supabase,
14 RPCs, knowledge graph, belief revision, y temporal validity.

---

## 5. Source Precedence (Jerarquia de la Verdad)

| Nivel | Fuente | Autoridad |
|---|---|---|
| 1 | Codigo en produccion (Railway /health) | Maxima |
| 2 | DSC firmado por T1 + T2 | Alta |
| 3 | AGENTS.md | Alta |
| 4 | MONSTRUO_GENOME.yaml (auto-generado) | Media |
| 5 | Reality Kernel (este archivo, derivado) | Media-baja |
| 6 | Propuestas no firmadas | Baja |

> **Nota:** Este archivo es nivel 5 - PROPUESTA hasta firma T1.
> No se auto-canoniza. Requiere audit T2 + firma T1 para subir a nivel 2.

> **Regla de incertidumbre:** Si un agente no puede verificar nivel 1
> (no tiene credenciales para pingar produccion), DEBE declarar incertidumbre
> explicitamente en vez de asumir que el dato del nivel 4-5 es correcto.

