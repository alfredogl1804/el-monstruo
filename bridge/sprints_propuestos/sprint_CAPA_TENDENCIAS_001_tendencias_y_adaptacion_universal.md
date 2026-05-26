<!-- lint_strict -->
# Sprint CAPA-TENDENCIAS-001 — Tendencias y Adaptación Universal

**Estado:** Propuesto — Canonizado sin ejecutar
**Hilo:** TBD
**ETA:** estimación pendiente
**Objetivo Maestro:** #9 (Transversalidad Universal — Capa 4) + #5 (Validación Tiempo Real) + #6 (Vanguardia Perpetua)
**Capa Transversal:** C4 Tendencias y Adaptación
**Bloqueos:** ninguno técnico
**Resultado esperado:** Cada empresa hija detecta cambios de mercado en tiempo real y pivotea automáticamente antes que la competencia.

---

## 0. Procedencia

OM-09 v3.0 línea 452-456:

> **CAPA 4 — Tendencias y Adaptación:**
> - Monitoreo de tendencias del mercado en tiempo real
> - Detección de oportunidades antes que la competencia
> - Pivoting inteligente cuando el mercado cambia
> - Competitor monitoring perpetuo

Esta capa es la materialización operativa de OM-05 (validación tiempo real) y OM-06 (vanguardia perpetua) aplicada al mercado del usuario, no al stack tecnológico.

---

## 1. Audit pre-sprint

Lo que existe:
- Perplexity Sonar configurado (`SONAR_API_KEY`) — puede consultar mercado real-time
- Skill `validacion-tiempo-real` (Manus internal) — mismo principio aplicado a IA
- Sin pipeline de monitoreo de mercado para empresas hijas

Lo que falta:
- Capability `invoke_market_scan(project_id, vertical, geo)` con frecuencia diaria
- Schema `market_signals`, `competitor_movements`, `trend_alerts`
- Sistema de alertas: cambio detectado → notificación + propuesta de pivot
- Histórico de tendencias para analytics longitudinal

---

## 2. Tareas (MVP)

### MVP-1: Market scan diario
- Cron diario por vertical: query a Perplexity + scrape competitor pages
- Output: `market_signals` con `signal_type`, `strength`, `direction`, `evidence_urls`
- Hooks: si `strength > 0.7`, dispara alerta

### MVP-2: Competitor monitoring
- Lista de competidores configurable por proyecto
- Tracking semanal: pricing, copy, features, social mentions
- Diff diario reportado al Embrión Daddy del proyecto

### MVP-3: Trend detection
- Análisis multi-señal: search trends + social mentions + news + APIs específicas (Trends API, Reddit, X)
- Score compuesto de tendencia
- Filtro de relevancia para el vertical

### MVP-4: Pivot recommendations
- Capability `propose_pivot(project_id, signal_id)` que retorna 3 opciones de respuesta
- Cada opción con scoring: cost, time, expected_lift, risk
- Decisión final HITL siempre

### MVP-5: Histórico longitudinal
- Tabla `trend_history` con todas las señales detectadas
- Dashboard con líneas de tiempo por vertical
- Detección de patrones cíclicos

### MVP-6: Integration con CAPA_ADS_001
- Cuando hay trend rising, propone campaign para capturar atención
- Cuando hay competitor moves, propone defensive ads

---

## 3. Dependencias

- Perplexity Sonar disponible (ya está)
- `STACK_REFRESH_001` valida APIs de Trends/Reddit/X siguen vigentes
- `CAPA_ADS_001` para ejecutar respuestas pagadas
- `CAPA_VENTAS_001` para ajustar pricing en respuesta

---

## 4. Criterios de Cierre y Métricas de Éxito

- Detección de tendencias relevantes ≥ 80% precision (humano valida)
- Tiempo medio entre señal detectada y respuesta ejecutada ≤ 48h
- ROI de pivots ejecutados ≥ 2x el costo del scan

---

## 5. Anti-doctrina

- NO confundir ruido con señal — usar threshold de strength
- NO pivotar más de 1 vez por mes en un mismo proyecto (whiplash mata)
- NO usar entrenamiento del LLM para análisis de mercado (datos viejos)
- NO scrapear sin respetar robots.txt y rate limits

---

## 6. Notas de canonización

Sprint canonizado sin ejecutar. Auto-promote al detectar commits en `kernel/trends/` o `monstruo/capabilities/market_scan/`.

Firmado: **Manus B — 2026-05-26**
