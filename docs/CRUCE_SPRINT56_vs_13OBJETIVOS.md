# Cruce Sprint 56 vs 13 Objetivos Maestros — Modo Detractor

**Fecha:** 1 mayo 2026
**Método:** Análisis adversarial — buscar debilidades, gaps, y áreas de oportunidad
**Sprint:** 56 — "El Ciclo Perpetuo"

---

## Matriz de Cobertura

| # | Objetivo | ¿Sprint 56 lo avanza? | Épica(s) | Veredicto Detractor |
|---|---|---|---|---|
| 1 | Crear Empresas Digitales | Indirecto | 56.5 (Sovereign LLM reduce costos de generación) | **DÉBIL** — Sprint 56 no toca capacidad de crear empresas |
| 2 | Todo Nivel Apple/Tesla | No | — | **NO CUBIERTO** — Aceptable, es sprint de infraestructura |
| 3 | Máximo Poder, Mínima Complejidad | Indirecto | 56.3 (autonomía invisible al usuario) | **PARCIAL** — El scheduler es invisible pero no mejora UX directamente |
| 4 | Nunca Se Equivoca Dos Veces | **SÍ** | 56.2 (feedback loop ajusta pesos) | **FUERTE** — El Validator es literalmente "aprender de errores de predicción" |
| 5 | Gasolina Magna vs Premium | Indirecto | 56.1 (Seeder valida datos via Perplexity) | **PARCIAL** — El seeder usa datos validados pero no mejora el clasificador Magna/Premium |
| 6 | Vanguardia Perpetua | **SÍ** | 56.3 (tarea `vanguard_scan` programada) | **MEDIO** — La tarea existe pero no tiene handler implementado |
| 7 | No Inventar la Rueda | **SÍ** | 56.5 (Ollama), 56.3 (APScheduler) | **FUERTE** — Todo adoptado, nada reinventado |
| 8 | Inteligencia Emergente | **SÍ** | 56.1 + 56.2 + 56.3 (ciclo autónomo completo) | **FUERTE** — El ciclo perpetuo ES inteligencia emergente |
| 9 | Transversalidad Universal | No | — | **NO CUBIERTO** — Aceptable, requiere Obj #8 maduro primero |
| 10 | Simulador Predictivo | **SÍ** | 56.1 (datos) + 56.2 (feedback loop) | **FUERTE** — Sprint 56 es el que hace funcionar al simulador |
| 11 | Multiplicación de Embriones | **SÍ** | 56.3 (scheduler multi-embrión) + 56.4 (métricas por embrión) | **MEDIO** — Infraestructura lista pero no hay nuevos embriones creados |
| 12 | Ecosistema / Soberanía | **SÍ** | 56.5 (Ollama como primer paso de soberanía) | **MEDIO** — Primer paso real pero Ollama local requiere GPU |
| 13 | Del Mundo | No | — | **NO CUBIERTO** — Aceptable, es objetivo de largo plazo |

**Resumen:** 8/13 objetivos avanzados directamente. 3 no cubiertos (aceptable por scope). 2 parciales.

---

## Análisis Detractor por Épica

### Épica 56.1 — Causal Seeder

**Fortalezas:**
- Resuelve el problema real de que la Causal KB está vacía
- Budget diario con hard stop es buena governance
- Dominios priorizados por relevancia de negocio

**Debilidades encontradas:**

1. **D1 — Parsing frágil:** El `_parse_discovered_events()` usa heurísticas de texto plano (split por bullets). Si Perplexity cambia su formato de respuesta, el parser se rompe silenciosamente.

2. **D2 — Sin deduplicación:** No hay mecanismo para evitar seedear el mismo evento dos veces. Si el seeder corre 4 veces al día durante 30 días, va a tener duplicados masivos.

3. **D3 — Quality gate ausente:** Los eventos se almacenan sin verificar calidad. Un evento mal parseado contamina la KB y luego afecta predicciones.

4. **D4 — Dependencia de Perplexity:** Si Perplexity cae o cambia pricing, el seeder se detiene completamente. No hay fallback.

### Épica 56.2 — Prediction Validator

**Fortalezas:**
- Cierra el feedback loop (corrección C7 de Sprint 55)
- Ajuste de pesos conservador (10% del error) evita overcorrection
- Lección extraída es útil para el sistema de aprendizaje

**Debilidades encontradas:**

5. **D5 — `_assess_outcome()` es demasiado simplista:** Contar palabras positivas/negativas es un heurístico de los años 2000. Para un sistema que aspira a "precisión creciente", esto es inaceptable. Necesita un LLM call real para evaluación semántica.

6. **D6 — Sin baseline de accuracy:** No hay forma de saber si el sistema MEJORA con el tiempo. Necesita un accuracy tracker histórico que muestre la curva de mejora.

7. **D7 — Validation date fija:** Si un evento se resuelve ANTES de la validation_date, el sistema no se entera. Necesita un mecanismo de early detection.

### Épica 56.3 — Embrión Scheduler

**Fortalezas:**
- Diseño limpio con governance (budget, retries, pause)
- Handlers registrables permiten extensibilidad
- Tareas default cubren los ciclos principales

**Debilidades encontradas:**

8. **D8 — Sin persistencia:** Si Railway reinicia el proceso, TODAS las tareas y su estado se pierden. El scheduler es in-memory. Necesita persistencia en Supabase.

9. **D9 — `vanguard_scan` sin handler:** Se registra la tarea pero no hay implementación del handler `run_vanguard_scan`. Es un placeholder que va a fallar 3 veces y pausarse.

10. **D10 — `memory_consolidation` sin handler:** Mismo problema. Se registra pero no existe.

11. **D11 — Sin priorización entre tareas:** Si hay 5 tareas listas al mismo tiempo y el budget solo alcanza para 3, no hay lógica de priorización. Se ejecutan en orden de iteración del dict.

### Épica 56.4 — Observability

**Fortalezas:**
- Aprovecha Langfuse existente sin reinventar
- Métricas por embrión son útiles para el Command Center
- Quality scores del judge se integran

**Debilidades encontradas:**

12. **D12 — Métricas in-memory:** `EmbrionMetricsCollector` pierde todo en restart. Para un dashboard, necesita persistencia o al menos un flush periódico.

13. **D13 — Sin alertas:** Las métricas se recolectan pero no hay sistema de alertas. Si un embrión tiene success_rate < 50%, nadie se entera automáticamente.

### Épica 56.5 — Sovereign LLM

**Fortalezas:**
- Primer paso real hacia soberanía (Obj #12)
- Fallback chain es robusto
- Tier system es inteligente para routing de costos

**Debilidades encontradas:**

14. **D14 — Ollama local requiere GPU:** Railway no tiene GPU. El Mac de Alfredo sí, pero no está 24/7. El tier 1 "local" es aspiracional hasta que haya infraestructura.

15. **D15 — Ollama Cloud es beta:** Los modelos cloud de Ollama (gpt-oss:120b-cloud) son nuevos y pueden tener disponibilidad inconsistente. No hay SLA.

16. **D16 — Sin benchmark de calidad:** No hay forma de saber si el output de Ollama gemma3:8b es "suficientemente bueno" para una tarea tier 1. Necesita un quality gate que compare output vs expectativa.

---

## Correcciones Mandatorias

Basado en las debilidades encontradas, las siguientes correcciones son **obligatorias** antes de considerar Sprint 56 completo:

### C1 — Deduplicación en Causal Seeder (D2)

**Problema:** Sin deduplicación, la KB se contamina con duplicados.

**Corrección:** Antes de almacenar un evento, hacer búsqueda semántica en la KB existente. Si similarity > 0.92, skip. Usar el embedding que ya se genera para el evento.

```python
async def _is_duplicate(self, title: str, context: str) -> bool:
    """Check if event already exists in KB via semantic similarity."""
    if not self._causal_kb:
        return False
    existing = await self._causal_kb.search_similar(
        query=f"{title} {context}",
        threshold=0.92,
        limit=1,
    )
    return len(existing) > 0
```

**Impacto:** Previene contaminación. Costo: 1 embedding call extra por evento (~$0.0001).

### C2 — LLM-based Outcome Assessment (D5)

**Problema:** Contar palabras positivas/negativas es inadecuado para evaluación semántica.

**Corrección:** Usar `SovereignLLM.generate()` con tier MEDIUM para evaluar outcomes. El prompt pide un score 0-1 con justificación.

```python
async def _assess_outcome(self, scenario: str, actual_outcome: str) -> float:
    """Use LLM to semantically assess if prediction materialized."""
    prompt = f"""Given this prediction scenario and what actually happened,
    rate on a scale of 0.0 to 1.0 how much the predicted outcome materialized.
    0.0 = did not happen at all
    0.5 = partially happened or unclear
    1.0 = happened exactly as predicted
    
    SCENARIO: {scenario}
    ACTUAL OUTCOME: {actual_outcome}
    
    Respond with ONLY a number between 0.0 and 1.0."""
    
    response = await self._sovereign_llm.generate(
        prompt=prompt,
        tier=TaskTier.MEDIUM,
        temperature=0.1,
    )
    try:
        return float(response.content.strip())
    except ValueError:
        return 0.5  # Fallback to uncertain
```

**Impacto:** Evaluación semántica real en lugar de keyword matching. Costo: ~$0.001 por validación.

### C3 — Scheduler Persistence (D8)

**Problema:** Estado del scheduler se pierde en restart.

**Corrección:** Persistir tareas en tabla `embrion_scheduled_tasks` de Supabase. Al startup, cargar tareas activas. Al completar/fallar, actualizar estado.

```sql
CREATE TABLE IF NOT EXISTS embrion_scheduled_tasks (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    embrion_id TEXT NOT NULL DEFAULT 'embrion-0',
    schedule_type TEXT NOT NULL DEFAULT 'periodic',
    interval_hours FLOAT DEFAULT 6.0,
    daily_hour INT DEFAULT 3,
    max_cost_usd FLOAT DEFAULT 0.50,
    max_retries INT DEFAULT 3,
    consecutive_failures INT DEFAULT 0,
    paused BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'active',
    last_run TIMESTAMPTZ,
    next_run TIMESTAMPTZ,
    total_runs INT DEFAULT 0,
    total_cost_usd FLOAT DEFAULT 0.0,
    handler TEXT NOT NULL,
    handler_args JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Impacto:** Scheduler sobrevive restarts. Tareas no se pierden.

### C4 — Accuracy Tracker Histórico (D6)

**Problema:** Sin baseline, no se puede demostrar que el sistema mejora.

**Corrección:** Agregar tabla `prediction_accuracy_history` que registra accuracy promedio por semana/mes. El Command Center muestra la curva.

```sql
CREATE TABLE IF NOT EXISTS prediction_accuracy_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    predictions_validated INT DEFAULT 0,
    avg_accuracy FLOAT,
    median_accuracy FLOAT,
    best_domain TEXT,
    worst_domain TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Impacto:** Demuestra que Obj #10 ("precisión que sube perpetuamente") se está cumpliendo.

### C5 — Implementar handler `run_vanguard_scan` (D9)

**Problema:** Tarea registrada sin handler = falla garantizada.

**Corrección:** Implementar un handler mínimo viable que:
1. Busca en Perplexity "latest AI tools and frameworks released this week"
2. Compara contra el Component Map existente
3. Si encuentra algo potencialmente superior, registra en `vanguard_alerts`

```python
async def run_vanguard_scan(**kwargs) -> dict:
    """Scan for new tools that might be superior to current stack."""
    result = await web_search(
        "latest AI agent tools frameworks released this week 2026",
        context="Scanning for tools superior to current El Monstruo stack",
    )
    # Parse and compare against component_map
    # If superior found → create alert
    return {"scanned": True, "alerts": 0}  # MVP
```

**Impacto:** La tarea no falla. Vanguardia Perpetua (Obj #6) tiene su primer ciclo automático.

### C6 — Task Priority System (D11)

**Problema:** Sin priorización, tareas de bajo valor pueden consumir el budget antes que las importantes.

**Corrección:** Agregar campo `priority: int` (1=highest) a `ScheduledTask`. En `_check_and_execute_due_tasks()`, ordenar por prioridad antes de ejecutar.

```python
async def _check_and_execute_due_tasks(self) -> None:
    """Execute due tasks in priority order."""
    self._reset_daily_budget_if_needed()
    now = datetime.now(timezone.utc).isoformat()
    
    due_tasks = [
        t for t in self._tasks.values()
        if not t.paused and t.status == "active" and t.next_run and t.next_run <= now
    ]
    # Sort by priority (lower number = higher priority)
    due_tasks.sort(key=lambda t: t.priority)
    
    for task in due_tasks:
        if self._daily_spend >= self.DAILY_BUDGET_USD:
            break
        await self._execute_task(task)
```

**Impacto:** Causal seeding y prediction validation (prioridad 1) siempre se ejecutan antes que health checks (prioridad 3).

### C7 — Metrics Flush to Supabase (D12)

**Problema:** Métricas se pierden en restart.

**Corrección:** Agregar método `flush_to_db()` que persiste métricas cada hora. El scheduler puede tener una tarea periódica para esto.

```python
async def flush_to_db(self, db) -> None:
    """Persist current metrics snapshot to Supabase."""
    for embrion_id, metrics in self._metrics.items():
        await db.upsert("embrion_metrics_snapshot", {
            "embrion_id": embrion_id,
            "snapshot_at": datetime.now(timezone.utc).isoformat(),
            **metrics.to_dict(),
        })
```

**Impacto:** Dashboard del Command Center tiene datos históricos, no solo sesión actual.

### C8 — Alertas de Anomalía (D13)

**Problema:** Métricas sin alertas son métricas ignoradas.

**Corrección:** Agregar `check_anomalies()` que evalúa thresholds y notifica via el sistema existente de notificaciones del Embrión.

```python
ALERT_THRESHOLDS = {
    "success_rate_min": 0.5,
    "avg_latency_max_ms": 30000,
    "daily_cost_max_usd": 8.0,
}

def check_anomalies(self) -> list[str]:
    """Check for anomalies across all embriones."""
    alerts = []
    for embrion_id, m in self._metrics.items():
        if m.success_rate < ALERT_THRESHOLDS["success_rate_min"]:
            alerts.append(f"ALERT: {embrion_id} success_rate={m.success_rate:.2f} < 0.5")
        if m.avg_latency_ms > ALERT_THRESHOLDS["avg_latency_max_ms"]:
            alerts.append(f"ALERT: {embrion_id} avg_latency={m.avg_latency_ms:.0f}ms > 30s")
    return alerts
```

**Impacto:** Problemas se detectan automáticamente en lugar de esperar a que Alfredo revise el dashboard.

---

## Resumen de Correcciones

| ID | Debilidad | Corrección | Esfuerzo | Prioridad |
|---|---|---|---|---|
| C1 | Duplicados en KB | Búsqueda semántica pre-store | 30 min | Alta |
| C2 | Outcome assessment simplista | LLM-based evaluation | 1 hora | Alta |
| C3 | Scheduler in-memory | Persistencia en Supabase | 2 horas | Crítica |
| C4 | Sin baseline de accuracy | Tabla de accuracy histórico | 1 hora | Media |
| C5 | Handler vanguard_scan vacío | Implementar MVP | 1 hora | Alta |
| C6 | Sin priorización de tareas | Campo priority + sort | 30 min | Media |
| C7 | Métricas in-memory | Flush periódico a DB | 1 hora | Media |
| C8 | Sin alertas | Thresholds + notificación | 1 hora | Media |

**Esfuerzo total de correcciones:** ~8 horas adicionales sobre el plan base.

---

## Veredicto Final

Sprint 56 es **sólido en concepto pero frágil en implementación**. El diseño del "Ciclo Perpetuo" es correcto — alimentar datos, predecir, validar, ajustar, repetir. Pero los detalles de implementación tienen gaps que, sin las correcciones, producirían un sistema que:

1. Se contamina con duplicados (C1)
2. Evalúa outcomes con heurísticas de 2005 (C2)
3. Pierde todo su estado en cada deploy (C3, C7)
4. No puede demostrar que mejora (C4)
5. Tiene tareas fantasma que fallan silenciosamente (C5)

**Con las 8 correcciones aplicadas**, Sprint 56 se convierte en el sprint más importante desde el 33 (cuando el Embrión empezó a respirar). Es el sprint que transforma al sistema de "reactivo" a "perpetuamente mejorando" — que es exactamente lo que los 13 Objetivos demandan.

**Nota sobre Obj #12 (Soberanía):** La integración de Ollama es un primer paso real pero honesto — sin GPU dedicada, el tier 1 local es aspiracional. La recomendación es activar Ollama Cloud inmediatamente (costo mínimo) y planear GPU dedicada para Sprint 58-60.
