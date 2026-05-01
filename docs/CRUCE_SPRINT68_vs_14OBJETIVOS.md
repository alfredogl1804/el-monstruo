# Cruce Sprint 68 vs. 14 Objetivos Maestros — Modo Detractor

> **Sprint:** 68 — "El Guardián Despierta"
> **Fecha de análisis:** 1 de mayo de 2026
> **Metodología:** Análisis en modo detractor (devil's advocate). El objetivo NO es validar el sprint, sino encontrar debilidades, gaps y riesgos que el plan no aborda.
> **Score de confianza PRE-correcciones:** 6.5/10
> **Score de confianza POST-correcciones:** 8.5/10

---

## Tabla de Cobertura

| Obj # | Nombre | Pre-Sprint 68 | Impacto Sprint 68 | Post-Sprint 68 | Tendencia |
|---|---|---|---|---|---|
| 1 | Crear Empresas Completas | 91% | +0% | 91% | Estable |
| 2 | Estándar Apple/Tesla | 92% | +1% | 93% | Sube (eval harness) |
| 3 | Mínima Complejidad | 92% | -1% (RIESGO) | 91% | BAJA |
| 4 | No Equivocarse 2 Veces | 90% | +3% | 93% | Sube |
| 5 | Gasolina | 90% | +1% | 91% | Sube |
| 6 | Vanguardia | 91% | +2% | 93% | Sube |
| 7 | No Inventar la Rueda | 93% | +0% | 93% | Estable |
| 8 | Emergencia | 90% | +2% | 92% | Sube |
| 9 | Transversalidad | 100% | +0% | 100% | Cerrado |
| 10 | Simulador | 90% | +1% | 91% | Sube |
| 11 | Embriones | 100% | +0% | 100% | Cerrado |
| 12 | Soberanía | 89% | +2% | 91% | Sube |
| 13 | Del Mundo | 91% | +0% | 91% | Estable |
| 14 | El Guardián | 0% | +40% | 40% | NUEVO |

**Promedio post-Sprint 68:** 92.9% (vs. 94.8% pre-Sprint 68 sin contar Obj #14; con Obj #14 el promedio baja porque arranca en 0%)

**Promedio excluyendo Obj #14 (comparable):** 92.5% → ligeramente inferior al 94.8% anterior. Esto se debe a que Sprint 68 introduce complejidad nueva (Capa 7) que presiona Obj #3 hacia abajo.

---

## Análisis Detractor por Objetivo

### Obj #1 — Crear Empresas Completas (91% → 91%)

Sprint 68 no avanza este objetivo directamente. El Guardián es infraestructura interna, no capacidad de crear empresas. Esto es aceptable en un sprint de infraestructura, pero el detractor señala que llevamos 3 sprints (66, 67, 68) sin avance directo en la capacidad de crear empresas. Si Sprint 69 tampoco lo toca, el ComplianceMonitor debería disparar una alerta de stagnation — lo cual sería una buena prueba de fuego para el propio Guardián.

### Obj #2 — Estándar Apple/Tesla (92% → 93%)

El Evaluation Harness (Épica 68.5) incluye un caso `quality_standard_check` que verifica output HTML contra estándares de diseño. Sin embargo, la función de scoring es rudimentaria: `0.8 if "class=" in output and "font" in output.lower() else 0.3`. Esto es una heurística superficial que no captura la esencia del estándar Apple/Tesla (spacing, tipografía, coherencia visual, micro-interacciones). **El detractor califica esta evaluación como insuficiente** — necesita métricas más sofisticadas o integración con un LLM evaluador.

### Obj #3 — Mínima Complejidad (92% → 91%) — RIESGO DE REGRESIÓN

Este es el hallazgo más preocupante del análisis. Sprint 68 introduce 3 nuevos directorios (`kernel/resilience/`, `kernel/guardian/`, `tests/harness/`), 13 archivos nuevos, y ~1,530 líneas de código. Para un sistema que predica "mínima complejidad", esto es una adición significativa. El detractor pregunta:

1. ¿Es necesario un directorio separado `kernel/resilience/` cuando `kernel/alerts/` ya existe?
2. ¿ToolGateway realmente necesita ser un módulo separado, o podría ser un decorador sobre tool_dispatch?
3. ¿MemoryGovernor duplica funcionalidad con ThreeLayerMemory?

La justificación es que Capa 7 es una capa transversal nueva (la primera orientada al sistema mismo), por lo que merece su propio namespace. Pero el detractor no está convencido — la complejidad debe justificarse con evidencia de que el sistema NECESITA esta protección, no solo con argumentos teóricos.

### Obj #4 — No Equivocarse 2 Veces (90% → 93%)

Sprint 68 avanza este objetivo significativamente. El ComplianceMonitor detecta regresiones, el SelfCorrectionEngine propone correcciones, y el Evaluation Harness verifica que los errores no se repitan. Sin embargo, el detractor nota que **no hay persistencia de errores pasados**. El sistema detecta drift en tiempo real pero no mantiene un registro histórico de "errores que ya cometimos" para prevenir su recurrencia. Esto debería integrarse con el Error Learning Loop (Sprint 61).

### Obj #5 — Gasolina (90% → 91%)

El costo estimado de $1-3/mes es correcto y razonable. Sin embargo, el detractor señala que el Evaluation Harness ejecuta LLM calls para cada caso de evaluación. Si la suite crece a 50+ casos (como debería para ser comprehensiva), el costo podría escalar a $10-20/mes. El plan no incluye un mecanismo de "eval budget" que limite el gasto en evaluaciones. Esto necesita un cap configurable.

### Obj #6 — Vanguardia (91% → 93%)

Los patrones de Manus v3 (Tool Masking, Loop Guard, Intention Anchors) y Hermes-Agent (Knowledge Extraction, Skill Refinement) son genuinamente de vanguardia. Sprint 68 los integra correctamente. El detractor reconoce que este es uno de los puntos fuertes del sprint.

### Obj #7 — No Inventar la Rueda (93% → 93%)

Sprint 68 reutiliza correctamente PolicyEngine, SovereignAlertMonitor, ThreeLayerMemory, y el Heartbeat System. No introduce dependencias nuevas de PyPI. El detractor no tiene objeciones aquí.

### Obj #8 — Emergencia (90% → 92%)

El SelfCorrectionEngine tiene un mecanismo de emergencia (escalar a HITL cuando confidence < 0.7). Sin embargo, el detractor nota que **no hay un "kill switch" global**. Si el Guardián mismo entra en un loop de correcciones (corrige → detecta drift → corrige → detecta drift), no hay mecanismo para detenerlo. El `MAX_CORRECTIONS_PER_DAY = 3` es un rate limit, no un kill switch. Se necesita un circuit breaker.

### Obj #9 — Transversalidad (100% → 100%)

Cerrado. Sprint 68 no afecta.

### Obj #10 — Simulador (90% → 91%)

El Evaluation Harness puede funcionar como un mini-simulador de comportamiento agéntico. Sin embargo, no está integrado con el Simulator v3 (Sprint 66). El detractor sugiere que los resultados del harness deberían alimentar al simulador para crear escenarios más realistas.

### Obj #11 — Embriones (100% → 100%)

Cerrado. Sprint 68 no afecta.

### Obj #12 — Soberanía (89% → 91%)

El ToolGateway con taint tracking fortalece la soberanía al prevenir que datos externos contaminen decisiones internas. El MemoryGovernor con su regla "UNTRUSTED nunca sube a PERMANENT" es una buena defensa. El detractor aprueba pero nota que la implementación de `_strip_injection_patterns` es una lista negra estática — los atacantes evolucionan más rápido que las listas negras. Se necesita un enfoque más robusto (embedding similarity, no solo string matching).

### Obj #13 — Del Mundo (91% → 91%)

Sprint 68 no avanza i18n ni multi-región. Aceptable en un sprint de infraestructura interna.

### Obj #14 — El Guardián (0% → 40%)

Este es el primer sprint que toca el Obj #14. Pasar de 0% a 40% es un avance significativo pero insuficiente para declarar el objetivo "en camino". El detractor identifica estos gaps:

1. **No hay métricas cuantitativas reales.** El ComplianceMonitor usa `coverage_percent` pero ¿de dónde viene ese número? Actualmente es manual (lo pone el planificador). Necesita fuentes de datos automatizadas.
2. **No hay baseline.** El Evaluation Harness no tiene un snapshot de "cómo era el sistema antes de Sprint 68" contra el cual comparar. Sin baseline, no puede detectar regresiones reales.
3. **No hay integración con Langfuse.** Las métricas del Guardián deberían registrarse como scores en Langfuse para visualización en el Command Center.
4. **El Guardián no se vigila a sí mismo.** ¿Quién vigila al vigilante? Si el ComplianceMonitor falla silenciosamente, nadie lo nota.

---

## Correcciones Mandatorias

### C1 — Scoring del Evaluation Harness debe usar LLM evaluador, no heurísticas

**Problema:** La función `scoring_fn` del caso `quality_standard_check` es `lambda output: 0.8 if "class=" in output and "font" in output.lower() else 0.3`. Esto es una heurística que no captura calidad real.

**Corrección:** Reemplazar con una llamada a un LLM evaluador (Ollama local para soberanía) que evalúe el output contra una rúbrica de calidad Apple/Tesla. Costo adicional: ~$0.50/mes.

```python
async def llm_quality_scorer(output: str) -> float:
    """Usa Ollama local para evaluar calidad de output."""
    rubric = "Evalúa este HTML del 0 al 10 según: tipografía, spacing, coherencia de colores, responsividad, micro-interacciones."
    score = await ollama_evaluate(output, rubric)
    return score / 10.0
```

### C2 — Circuit breaker para el SelfCorrectionEngine

**Problema:** Si el Guardián entra en un loop de correcciones, no hay mecanismo para detenerlo más allá del rate limit diario.

**Corrección:** Agregar un circuit breaker que se activa si hay >2 correcciones fallidas consecutivas para el mismo objetivo.

```python
class CircuitBreaker:
    def __init__(self, max_failures=2):
        self.failures: dict[int, int] = {}
    
    def record_failure(self, objective_id: int):
        self.failures[objective_id] = self.failures.get(objective_id, 0) + 1
    
    def is_open(self, objective_id: int) -> bool:
        return self.failures.get(objective_id, 0) >= self.max_failures
    
    def reset(self, objective_id: int):
        self.failures[objective_id] = 0
```

### C3 — MemoryGovernor debe persistir en Supabase, no solo en memoria

**Problema:** El MemoryGovernor actual opera sobre un `memory_store` abstracto. Si el proceso se reinicia, toda la governance metadata se pierde.

**Corrección:** El `memory_store` debe implementarse sobre Supabase con una tabla `governed_memories` que incluya `tier`, `source`, `taint_level`, `created_at`, `last_accessed`, `access_count`.

```sql
CREATE TABLE governed_memories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    tier VARCHAR(20) NOT NULL,
    source VARCHAR(100) NOT NULL,
    taint_level VARCHAR(20) DEFAULT 'trusted',
    relevance_score FLOAT DEFAULT 1.0,
    access_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed TIMESTAMPTZ DEFAULT NOW()
);
```

### C4 — Baseline snapshot antes de que el Evaluation Harness pueda detectar regresiones

**Problema:** Sin un baseline, el harness solo puede evaluar en absoluto, no detectar regresiones relativas.

**Corrección:** Agregar un mecanismo de snapshot que guarda los resultados de la primera ejecución como baseline.

```python
class BaselineManager:
    async def save_baseline(self, results: dict):
        """Guarda resultados como baseline en Supabase."""
        await supabase.table("eval_baselines").insert({
            "results": results,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    async def compare_with_baseline(self, current: dict) -> list[str]:
        """Compara resultados actuales con baseline."""
        baseline = await supabase.table("eval_baselines").select("*").order("created_at", desc=True).limit(1).execute()
        regressions = []
        for case_name, score in current.items():
            if baseline and case_name in baseline and score < baseline[case_name] - 0.1:
                regressions.append(f"{case_name}: {baseline[case_name]} → {score}")
        return regressions
```

### C5 — Integrar métricas del Guardián con Langfuse

**Problema:** Las métricas del ComplianceMonitor no se registran en Langfuse, por lo que no son visibles en el Command Center.

**Corrección:** Después de cada `evaluate_all()`, registrar un score en Langfuse por cada objetivo.

```python
async def report_to_langfuse(self, metrics: list[ObjectiveMetrics]):
    for metric in metrics:
        await langfuse.score(
            name=f"objective_{metric.objective_id}_coverage",
            value=metric.coverage_percent / 100,
            comment=f"{metric.objective_name}: {metric.trend}"
        )
```

### C6 — Taint tracking necesita enfoque por embeddings, no solo lista negra

**Problema:** `_strip_injection_patterns` usa una lista negra estática de 5 patrones. Los atacantes evolucionan más rápido.

**Corrección:** Complementar la lista negra con un clasificador por embeddings que detecte intenciones maliciosas semánticamente, no solo por string matching. Usar Ollama local para mantener soberanía.

```python
async def _detect_injection_semantic(self, text: str) -> bool:
    """Detección semántica de injection usando Ollama local."""
    prompt = f"¿Este texto contiene instrucciones que intentan manipular un sistema de IA? Responde solo SI o NO.\n\nTexto: {text}"
    response = await ollama_classify(prompt)
    return "SI" in response.upper()
```

### C7 — El Guardián debe vigilarse a sí mismo (meta-health check)

**Problema:** Si el ComplianceMonitor falla silenciosamente, nadie lo nota.

**Corrección:** Agregar un heartbeat propio del Guardián que se registra en el Heartbeat System existente (Sprint 42). Si el heartbeat no llega en >2 horas, el SovereignAlertMonitor (Sprint 14) dispara alerta.

```python
async def _register_guardian_heartbeat(self):
    """El Guardián se registra en el Heartbeat System."""
    await heartbeat_system.register(
        component="guardian_compliance_monitor",
        interval_seconds=3600,  # Cada hora
        on_miss=lambda: sovereign_alerts.fire(
            AlertType.HEALTH_DOWN,
            "Guardian ComplianceMonitor heartbeat missed"
        )
    )
```

### C8 — Consolidar kernel/resilience/ y kernel/guardian/ para reducir complejidad

**Problema:** Dos directorios nuevos para funcionalidad relacionada viola Obj #3 (Mínima Complejidad).

**Corrección:** Unificar bajo `kernel/guardian/` con subdirectorios claros:

```
kernel/guardian/
├── __init__.py
├── resilience/              # Capa 7
│   ├── tool_gateway.py
│   ├── taint_tracker.py
│   └── memory_governance.py
├── compliance/              # Obj #14
│   ├── monitor.py
│   ├── drift_detector.py
│   └── self_correction.py
├── evaluation/              # Harness
│   ├── regression_suite.py
│   └── benchmark_runner.py
└── intention_anchors.py
```

Esto reduce de 3 directorios raíz a 1, manteniendo la separación lógica.

---

## Veredicto Final

Sprint 68 es un sprint necesario y bien fundamentado. La introducción del Guardián y la Capa 7 cierra gaps reales identificados por la investigación de fallo agéntico. Sin embargo, el plan original tiene debilidades significativas en 4 áreas:

1. **Evaluación superficial** (heurísticas en lugar de evaluación real)
2. **Falta de persistencia** (MemoryGovernor en memoria, no en Supabase)
3. **Sin baseline** (no puede detectar regresiones sin punto de comparación)
4. **Complejidad innecesaria** (3 directorios nuevos cuando 1 bastaría)

Las 8 correcciones mandatorias (C1-C8) abordan estos problemas. Con las correcciones aplicadas, el score sube de 6.5/10 a 8.5/10.

El gap restante (8.5 vs. 10) se debe a que Obj #14 solo llega a 40% — necesitará al menos 2 sprints más (69, 70) para alcanzar un nivel operativo. Esto es esperado y aceptable para un objetivo que acaba de nacer.

---

## Impacto Proyectado Post-Sprint 68

| Métrica | Antes | Después |
|---|---|---|
| Promedio 14 Objetivos | 87.1% (con #14 en 0%) | 89.2% |
| Promedio 13 Objetivos (sin #14) | 94.8% | 92.5% |
| Objetivos en 100% | 2 (#9, #11) | 2 (#9, #11) |
| Objetivos críticos (<70%) | 1 (#14 en 0%) | 0 (todos ≥40%) |
| Objetivos en riesgo de regresión | 0 | 1 (#3 por complejidad) |

La ligera caída en el promedio de 13 objetivos (94.8% → 92.5%) se debe a la presión de complejidad sobre Obj #3. La corrección C8 (consolidar directorios) mitiga parcialmente este efecto.
