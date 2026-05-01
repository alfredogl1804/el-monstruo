# Cruce Sprint 55 vs 13 Objetivos Maestros — Modo Detractor

**Fecha:** 1 mayo 2026
**Sprint:** 55 — "El Tejido Causal y la Red de Protocolos"
**Método:** Cada objetivo se evalúa como DETRACTOR — buscando debilidades, omisiones, y riesgos.

---

## Matriz de Cobertura

| # | Objetivo | Cobertura Sprint 55 | Veredicto |
|---|----------|---------------------|-----------|
| 1 | Crear empresas digitales completas | Indirecta — MCP Hub (Notion, Gmail, Calendar) habilita automatización de operaciones de negocio | ⚠️ PARCIAL |
| 2 | Todo nivel Apple/Tesla | NO CUBIERTO — Sprint 55 es infraestructura pura, sin output visual | ❌ NO APLICA |
| 3 | Máximo poder, mínima complejidad | MCP Hub simplifica integraciones (zero-config si env vars presentes). Simulador es complejo internamente pero simple de invocar | ✅ ALINEADO |
| 4 | Nunca se equivoca dos veces | Causal KB alimenta pattern recognition. Simulador valida predicciones vs realidad | ✅ ALINEADO |
| 5 | Gasolina Magna vs Premium | Causal Decomposer usa investigación en tiempo real (Perplexity). MCP servers son datos validados en tiempo real | ✅ ALINEADO |
| 6 | Vanguardia perpetua | FastMCP 3.2.4 (Apr 2026), a2a-sdk 1.0.2 (Apr 2026) — tecnología de última generación | ✅ ALINEADO |
| 7 | No inventar la rueda | MCP servers oficiales adoptados (Notion, Gmail, Slack). A2A SDK de Google adoptado. DoWhy/PyMC para causal | ✅ FUERTE |
| 8 | Inteligencia emergente colectiva | A2A Registry permite que Embriones se descubran y comuniquen dinámicamente. Causal Decomposer usa multi-modelo | ✅ FUERTE |
| 9 | Transversalidad universal | MCP Hub es transversal (cualquier proyecto se beneficia de Notion/Gmail/Calendar) | ⚠️ PARCIAL |
| 10 | Simulador predictivo causal | ÉPICAS 55.3, 55.4, 55.5 — primer prototipo completo del simulador | ✅ OBJETIVO PRIMARIO |
| 11 | Multiplicación de Embriones | A2A Registry permite registro y discovery de múltiples Embriones | ✅ ALINEADO |
| 12 | Ecosistema de Monstruos | A2A + MCP Hub = interoperabilidad con agentes externos. `.well-known/agent.json` = discovery estándar | ✅ ALINEADO |
| 13 | Del mundo | Infraestructura causal es fundacional para predicción que beneficie a la humanidad | ⚠️ LARGO PLAZO |

**Cobertura directa:** 9/13 objetivos
**No aplica en este sprint:** 2 (#2 diseño visual, #13 largo plazo)
**Parcial:** 2 (#1 empresas, #9 transversalidad)

---

## Análisis Detractor por Épica

### Épica 55.1 — MCP Hub

**Crítica 1: Dependencia de npm packages de terceros**

> Los MCP servers de productividad (@notionhq, @techsend, Slack) son mantenidos por terceros. Si alguno se depreca o tiene breaking changes, El Monstruo pierde funcionalidad.

**Severidad:** Media
**Mitigación:** Esto es exactamente el Principio de Soberanía Progresiva (Obj #12 Fase 1). Hoy usamos lo mejor disponible. Si un package muere, lo reemplazamos o construimos propio. El `MCPClientManager` abstrae la implementación — cambiar un server es cambiar una línea de config.

**Crítica 2: Hot-plug sin validación de seguridad**

> `MCPHub.add_server()` permite agregar servidores dinámicamente. Un servidor malicioso podría inyectarse y ejecutar código arbitrario.

**Severidad:** Alta
**Corrección C1:** Agregar validación en `add_server()`:
- Whitelist de servidores permitidos (configurable)
- Timeout estricto en conexión (ya existe: 30s)
- Sandboxing de herramientas descubiertas (marcar como `untrusted` hasta aprobación HITL)

### Épica 55.2 — A2A Registry

**Crítica 3: Agent Cards sin autenticación fuerte**

> El endpoint `POST /v1/a2a/register` permite que cualquiera registre un agente. Sin autenticación, un atacante podría registrar agentes falsos.

**Severidad:** Alta
**Corrección C2:** Agregar middleware de autenticación:
- Bearer token requerido para registro externo
- Embriones internos se auto-registran con token de servicio
- Rate limiting en endpoint de registro (max 10/hora)

**Crítica 4: Heartbeat sin consecuencias**

> Si un agente deja de enviar heartbeat, solo se marca como "offline" pero no hay cleanup ni notificación.

**Severidad:** Baja
**Corrección C3:** Agregar:
- Cron job que revisa heartbeats cada 5 minutos
- Si heartbeat > 10 min: marcar `degraded`
- Si heartbeat > 30 min: marcar `offline` + notificar a Embrión-0
- Si heartbeat > 24h: auto-deregister

### Épica 55.3 — Causal Knowledge Base

**Crítica 5: Embedding model hardcodeado**

> Se usa `text-embedding-3-small` hardcodeado. Si OpenAI depreca el modelo o sale uno mejor, hay que cambiar código.

**Severidad:** Baja
**Corrección C4:** Hacer configurable via env var `CAUSAL_EMBEDDING_MODEL` con fallback a `text-embedding-3-small`. Mismo patrón que `memory/thoughts.py`.

**Crítica 6: Sin validación de calidad de datos**

> Cualquier evento puede almacenarse sin validación de que la descomposición sea razonable. Garbage in = garbage out para el simulador.

**Severidad:** Alta
**Corrección C5:** Agregar `validation_gate` antes de persistir:
- Mínimo 3 factores por evento
- Al menos 2 categorías diferentes de factores
- Ningún factor con weight > 0.95 (nada es 100% determinante)
- `validation_score` mínimo de 0.3 para persistir
- Eventos con score < 0.5 se marcan como `draft` (no alimentan simulador)

### Épica 55.4 — Causal Decomposer

**Crítica 7: Fallback a GPT-4o en vez de GPT 5.2**

> El código tiene fallback a `gpt-4o` cuando los Sabios fallan. Esto viola el principio de usar siempre el modelo más potente.

**Severidad:** Media
**Corrección C6:** Cambiar fallback de `gpt-4o` a `gpt-5.2-turbo` (o el modelo más potente disponible). Agregar cascada: Sabios → GPT 5.2 → Gemini 3 Pro → error (nunca modelos inferiores).

**Crítica 8: Sin mecanismo de feedback loop**

> El decomposer produce factores pero nunca valida si fueron correctos. No hay ciclo de "predicción → realidad → corrección".

**Severidad:** Alta
**Corrección C7:** Agregar campo `validated_at` y `actual_outcome` en `causal_events`. Crear job periódico del Embrión-Causal que:
1. Busca eventos con `event_date` en el pasado
2. Investiga qué realmente pasó
3. Compara factores predichos vs factores reales
4. Ajusta pesos de factores que fueron sobre/sub-estimados
5. Esto es exactamente el "Ciclo de Validación Perpetua" del Obj #10

### Épica 55.5 — Monte Carlo Simulator

**Crítica 9: Modelo Beta demasiado simplista**

> Usar distribuciones Beta para todos los factores es una simplificación excesiva. Factores económicos pueden tener distribuciones bimodales, fat tails, o correlaciones entre sí.

**Severidad:** Media
**Mitigación:** Esto es v1 — "semi-exacto es infinitamente mejor que intuición humana" (Obj #10). El modelo Beta es un punto de partida razonable. Corrección futura: PyMC para modelos jerárquicos Bayesianos que capturen correlaciones y distribuciones arbitrarias. No bloquear v1 por perfeccionismo.

**Crítica 10: Sin correlación entre factores**

> Los factores se sampleen independientemente. En realidad, "tasas de interés bajas" y "inversión en startups alta" están correlacionados.

**Severidad:** Media
**Corrección C8:** Agregar en v1.1 (no bloquear v1):
- Matriz de correlación entre factores (calculada de eventos históricos)
- Usar `numpy.random.multivariate_normal` para samplear factores correlacionados
- Documentar como limitación conocida en v1

**Crítica 11: 10,000 simulaciones puede ser insuficiente**

> Para distribuciones con fat tails o eventos raros, 10,000 simulaciones puede no capturar la cola de la distribución.

**Severidad:** Baja
**Mitigación:** Configurable via parámetro `n_simulations`. Default 10,000 es estándar para Monte Carlo básico. Para escenarios de alta importancia, se puede subir a 100,000 o 1M sin costo adicional (es CPU puro).

---

## Correcciones Aplicadas al Plan

| ID | Corrección | Épica | Impacto |
|---|---|---|---|
| C1 | Whitelist + sandboxing para servidores MCP dinámicos | 55.1 | Seguridad |
| C2 | Bearer token + rate limiting para registro A2A | 55.2 | Seguridad |
| C3 | Cron de heartbeat con escalamiento (degraded → offline → deregister) | 55.2 | Robustez |
| C4 | Embedding model configurable via env var | 55.3 | Flexibilidad |
| C5 | Validation gate con mínimos de calidad antes de persistir | 55.3 | Calidad de datos |
| C6 | Fallback a GPT 5.2 (no GPT-4o) en decomposer | 55.4 | Obj #5 (Magna) |
| C7 | Feedback loop: predicción → realidad → corrección de pesos | 55.4 | Obj #10 (Ciclo perpetuo) |
| C8 | Documentar correlación entre factores como limitación v1, planear para v1.1 | 55.5 | Transparencia |

---

## Veredicto Final

**Sprint 55 es APROBADO con las 8 correcciones aplicadas.**

El sprint avanza significativamente dos de los objetivos más ambiciosos (#8 y #10) mientras mantiene alineamiento con los principios fundacionales (#3, #5, #6, #7). Las correcciones de seguridad (C1, C2) son críticas y deben implementarse desde el día 1, no como "mejora futura".

La mayor debilidad estructural es la ausencia de feedback loop (C7) — sin él, el simulador nunca mejora. Esto DEBE estar en la implementación de Sprint 55, no posponerse.

**Riesgo residual aceptable:** El modelo Beta simplista (Crítica 9) es una limitación conocida y documentada. No bloquea el valor del prototipo. La evolución a PyMC se planifica para Sprint 57-58 cuando haya datos suficientes.

---

*Documento generado el 1 de mayo de 2026. Modo detractor aplicado rigurosamente. Las correcciones C1-C8 son MANDATORIAS para la implementación.*
