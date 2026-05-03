# Datos de Producción — Kernel El Monstruo
**Ejecutado por:** Manus (curl directo)
**Timestamp:** 2026-05-02 ~17:35 CST

---

## /health — Estado del Kernel

| Campo | Valor |
|---|---|
| Status | healthy |
| Versión | 0.50.0-sprint50 |
| Motor | langgraph |
| Uptime | ~2542s (~42 min desde último restart) |
| Modelos disponibles | gpt-5.5, claude-opus-4-7, gemini-3.1-pro-preview, sonar-reasoning-pro |
| Observabilidad | active (langfuse + opentelemetry) |

### Componentes activos confirmados:
kernel, event_store, memory, knowledge, langfuse, opentelemetry, checkpointer (AsyncPostgresSaver), mempalace, lightrag, multi_agent, finops, mcp, fastmcp, mem0, embrion

### Estado del Embrión Loop (desde /health):
- Running: true
- Pensamientos hoy: 4 de 50 máx
- Costo hoy: $5.249 de $30.00 budget
- Ciclos completados: 20
- Tool calls total (FCS): **0** — confirma lo que Cowork dijo
- Calidad promedio: 3.0
- Evaluaciones totales: 2
- Manus delegations: 1
- Consolidaciones: 0
- Consultas a Sabios: 1
- Radar checks: 0
- Último trigger: "mensaje_alfredo" sobre necesidades urgentes del Embrión
- Último resultado: "Plan completado con 1 paso(s) fallido(s). 4/7 pasos completados. Costo: $1.2854"

### Lo que el Embrión pidió (su último resultado):
- write_policy.py **no existe** — confirmado por el propio Embrión
- No hay sistema de métricas propias
- manus_bridge nunca se completó

---

## /v1/tools — Tools en Producción

**Solo 3 tools registradas en el endpoint:**

| Tool | Status | Descripción |
|---|---|---|
| web_search | active | Perplexity Sonar API |
| consult_sabios | active | Multi-model AI consultation |
| email | no_credentials | Gmail SMTP |

**Las otras 13 tools que Cowork encontró en el código (tool_dispatch.py) NO aparecen en el endpoint /v1/tools.** Esto confirma la hipótesis de Cowork: están en código pero no registradas/activas en la DB.

---

## /v1/embrion/status — NOT FOUND
## /v1/embrion/latidos — NOT FOUND
## /v1/embrion/heartbeat — NOT FOUND

El estado del Embrión solo se expone vía /health, no tiene endpoints dedicados.

---

## Cruce con Análisis de Cowork

Cowork tenía razón en todo:
1. Solo 3 tools activas en prod (no 16)
2. Las 13 restantes existen en código pero no en el registry de prod
3. El Embrión tiene 0 tool_calls exitosas
4. write_policy.py no existe (confirmado por el propio Embrión)

**Pendiente:** Cowork está analizando tool_registry.py para confirmar si activar es solo un UPDATE en Supabase o hay algo más sutil.
