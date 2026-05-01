# Cruce Sprint 69 vs. 14 Objetivos Maestros — Modo Detractor

> **Sprint:** 69 — "La Inteligencia que se Mide"
> **Fecha de análisis:** 1 de mayo de 2026
> **Metodología:** Análisis en modo detractor (devil's advocate). El objetivo NO es validar el sprint, sino encontrar debilidades, gaps y riesgos que el plan no aborda.
> **Score de confianza PRE-correcciones:** 7.0/10
> **Score de confianza POST-correcciones:** 8.8/10

---

## Tabla de Cobertura

| Obj # | Nombre | Pre-Sprint 69 | Impacto Sprint 69 | Post-Sprint 69 | Tendencia |
|---|---|---|---|---|---|
| 1 | Crear Empresas Completas | 91% | +1% | 92% | Sube (métricas de empresas creadas) |
| 2 | Estándar Apple/Tesla | 93% | +1% | 94% | Sube (LLM evaluador) |
| 3 | Mínima Complejidad | 91% | -1% (RIESGO) | 90% | BAJA |
| 4 | No Equivocarse 2 Veces | 93% | +3% | 96% | Sube (baseline + regresiones) |
| 5 | Gasolina | 91% | +0% | 91% | Estable |
| 6 | Vanguardia | 93% | +2% | 95% | Sube (Knowledge Extraction) |
| 7 | No Inventar la Rueda | 93% | +1% | 94% | Sube (skill reuse) |
| 8 | Emergencia | 92% | +3% | 95% | Sube (Knowledge Extraction) |
| 9 | Transversalidad | 100% | +0% | 100% | Cerrado |
| 10 | Simulador | 91% | +1% | 92% | Sube (métricas automatizadas) |
| 11 | Embriones | 100% | +0% | 100% | Cerrado |
| 12 | Soberanía | 91% | +1% | 92% | Sube (Ollama evaluador) |
| 13 | Del Mundo | 91% | +0% | 91% | Estable |
| 14 | El Guardián | 40% | +25% | 65% | Sube fuerte |

**Promedio post-Sprint 69 (14 objetivos):** 91.1% (vs. 89.2% post-Sprint 68)

**Promedio excluyendo Obj #14 (comparable):** 93.2% (recuperando del 92.5% post-Sprint 68)

---

## Análisis Detractor por Objetivo

### Obj #1 — Crear Empresas Completas (91% → 92%)

Sprint 69 avanza marginalmente este objetivo al definir indicadores medibles para "empresas creadas" (`total_empresas`, `e2e_success_rate`, `active_embriones`). Sin embargo, el detractor señala que **definir métricas no es lo mismo que avanzar la capacidad**. El MetricsCollector mide cuántas empresas se crearon, pero no mejora la capacidad de crearlas. Llevamos 4 sprints (66-69) sin avance directo en la capacidad de crear empresas. Si Sprint 70 tampoco lo toca, el propio ComplianceMonitor debería disparar una alerta de stagnation — y esa sería la primera prueba real del Guardián.

### Obj #2 — Estándar Apple/Tesla (93% → 94%)

La corrección C1 de Sprint 68 (LLM evaluador en lugar de heurísticas) se implementa parcialmente en Sprint 69 a través del Ollama evaluador. El detractor reconoce la mejora pero nota que **el LLM evaluador evalúa HTML, no la experiencia completa del usuario**. El estándar Apple/Tesla incluye animaciones, transiciones, micro-interacciones, y coherencia entre pantallas — ninguno de estos aspectos es evaluable por un LLM que solo ve HTML estático. Se necesita un evaluador visual (screenshot comparison) para Sprint 70.

### Obj #3 — Mínima Complejidad (91% → 90%) — SEGUNDO SPRINT EN DESCENSO

Este es el hallazgo más alarmante. Sprint 69 agrega ~1,150 líneas de código, 10 archivos nuevos, 3 tablas SQL nuevas, y un nuevo subdirectorio (`kernel/guardian/metrics/sources/`). Sumado a las ~1,530 líneas de Sprint 68, el Guardián ya acumula **~2,680 líneas de código nuevo** en solo 2 sprints. Para un sistema que predica "mínima complejidad", esto es una tendencia preocupante.

El detractor pregunta directamente: ¿El MetricsCollector con 4 fuentes diferentes (Langfuse, Supabase, Code, PostHog) es realmente necesario, o es over-engineering? ¿No bastaría con 2 fuentes (Langfuse + Supabase) para el 80% de las métricas?

**Recomendación del detractor:** Eliminar `code_source.py` y `posthog_source.py` de Sprint 69. Implementarlos solo si los datos de Langfuse + Supabase resultan insuficientes. Esto reduce la complejidad en ~200 líneas y 2 archivos.

### Obj #4 — No Equivocarse 2 Veces (93% → 96%)

Sprint 69 es el sprint más fuerte para este objetivo. El BaselineManager permite detectar regresiones reales (no solo drift en tiempo real), y el ciclo de mejora continua (detectar → corregir → verificar) cierra el loop. El detractor aprueba pero nota que **la verificación post-corrección es inmediata** — no espera a que la corrección "madure". Una corrección que parece exitosa a los 5 minutos puede fallar a las 24 horas. Se necesita un mecanismo de "verificación diferida".

### Obj #5 — Gasolina (91% → 91%)

El costo estimado de $2-5/mes es razonable. Sin embargo, el detractor señala que Sprint 69 introduce un ciclo que se ejecuta **cada 6 horas**. Cada ciclo hace: 4 llamadas a fuentes de métricas + 14 evaluaciones de objetivos + N correcciones + re-evaluación + reporte a Langfuse. Esto son ~30-50 operaciones por ciclo, 4 ciclos/día = 120-200 operaciones/día. Si cada operación involucra una llamada a Supabase, eso son 3,600-6,000 queries/mes. Dentro del plan gratuito de Supabase, pero se acerca al límite. El plan no incluye un mecanismo de "degradación elegante" si se acerca al límite de queries.

### Obj #6 — Vanguardia (93% → 95%)

El Knowledge Extraction Engine es genuinamente innovador y alineado con el estado del arte (Hermes-Agent pattern). El detractor reconoce que este es uno de los puntos más fuertes de Sprint 69. Sin embargo, la implementación de `_find_similar_skill` usa overlap de herramientas como proxy de similaridad, lo cual es rudimentario. Dos tareas pueden usar las mismas herramientas pero ser completamente diferentes en propósito. Se necesita comparación semántica (embeddings) para Sprint 70.

### Obj #7 — No Inventar la Rueda (93% → 94%)

El KnowledgeExtractor reutiliza skills existentes antes de crear nuevas — esto es exactamente "no inventar la rueda" aplicado al aprendizaje. El detractor aprueba. Sin embargo, nota que **no hay mecanismo para deprecar skills obsoletas**. Si una skill fue creada con herramientas que ya no existen, seguirá siendo sugerida. Se necesita un TTL o mecanismo de deprecación para skills.

### Obj #8 — Emergencia (92% → 95%)

Sprint 69 es el sprint más fuerte para este objetivo después de Sprint 63 (Cross-Embrion Learning). El Knowledge Extraction Engine formaliza el aprendizaje emergente: cuando el sistema hace algo inesperadamente bueno, lo captura como skill. El detractor aprueba pero nota que **"novel_approaches" en TaskExperience es un campo que alguien debe llenar manualmente**. ¿Quién decide qué es "novedoso"? Se necesita un mecanismo automático de detección de novedad (comparar con skills existentes).

### Obj #9 — Transversalidad (100% → 100%)

Cerrado. Sprint 69 no afecta.

### Obj #10 — Simulador (91% → 92%)

Las métricas automatizadas incluyen `sim_prediction_accuracy` y `scenarios_tested`, lo cual conecta el Guardián con el Simulador. El detractor aprueba marginalmente pero nota que no hay integración bidireccional — el Guardián mide al Simulador pero el Simulador no usa datos del Guardián para mejorar sus predicciones.

### Obj #11 — Embriones (100% → 100%)

Cerrado. Sprint 69 no afecta.

### Obj #12 — Soberanía (91% → 92%)

El uso de Ollama como LLM evaluador (en lugar de GPT/Claude) fortalece la soberanía. El `ollama_pct` como métrica de soberanía es una buena adición. El detractor aprueba.

### Obj #13 — Del Mundo (91% → 91%)

Sprint 69 no avanza i18n ni multi-región. Segundo sprint consecutivo sin avance. Aceptable dado el enfoque en infraestructura del Guardián, pero Sprint 70 debería tocarlo.

### Obj #14 — El Guardián (40% → 65%)

Sprint 69 avanza significativamente el Guardián. Las métricas automatizadas, el baseline, y el ciclo de mejora continua transforman al Guardián de un prototipo a un sistema operativo. El detractor reconoce el avance pero identifica estos gaps restantes:

1. **Las fuentes de métricas tienen muchos placeholders.** `_get_e2e_rate` retorna 0.85 hardcodeado. `_count_novel` retorna 0. Esto significa que las métricas no son reales todavía.
2. **El ciclo de mejora no tiene feedback loop cerrado.** Corrige y verifica, pero no aprende DE las correcciones. ¿Qué correcciones funcionaron? ¿Cuáles no? Esto debería alimentar al KnowledgeExtractor.
3. **No hay visualización en el Command Center.** Los endpoints existen pero el frontend no los consume todavía.

---

## Correcciones Mandatorias

### C1 — Eliminar code_source.py y posthog_source.py de Sprint 69

**Problema:** 4 fuentes de métricas es over-engineering. Langfuse + Supabase cubren el 80% de las necesidades.

**Corrección:** Mover `code_source.py` y `posthog_source.py` a Sprint 70 o posterior. Reducir OBJECTIVE_INDICATORS para usar solo fuentes "langfuse" y "supabase" en Sprint 69.

**Impacto:** -200 líneas, -2 archivos, Obj #3 sube de 90% a 91%.

### C2 — Verificación diferida post-corrección

**Problema:** La verificación post-corrección es inmediata (5 minutos). Una corrección puede parecer exitosa pero fallar a las 24 horas.

**Corrección:** Agregar un mecanismo de "verificación diferida" que re-evalúa 24 horas después de cada corrección.

```python
async def schedule_deferred_verification(self, correction_id: str):
    """Programa verificación 24h después de una corrección."""
    self.scheduler.add_job(
        self._verify_correction,
        trigger="date",
        run_date=datetime.now(timezone.utc) + timedelta(hours=24),
        args=[correction_id],
        id=f"verify_{correction_id}"
    )
```

### C3 — Reemplazar placeholders de métricas con valores reales o marcarlos explícitamente

**Problema:** `_get_e2e_rate` retorna 0.85 hardcodeado. Esto contamina las métricas con datos falsos.

**Corrección:** Cuando una métrica no está disponible, retornar `None` en lugar de un valor hardcodeado. El `_calculate_coverage` debe ignorar indicadores con valor `None` y ajustar los pesos proporcionalmente.

```python
def _calculate_coverage(self, indicators, raw_data) -> float:
    available = [i for i in indicators 
                 if raw_data.get(i.source, {}).get(i.metric_key) is not None]
    if not available:
        return -1  # Indica "no medible"
    # Recalcular pesos solo con indicadores disponibles
    total_weight = sum(i.weight for i in available)
    ...
```

### C4 — Deprecación de skills obsoletas

**Problema:** Skills creadas con herramientas que ya no existen seguirán siendo sugeridas.

**Corrección:** Agregar un campo `last_validated` a ExtractedSkill y un mecanismo de validación periódica que verifica que las herramientas requeridas siguen existiendo.

```python
async def validate_skills(self):
    """Valida que las skills existentes siguen siendo viables."""
    all_skills = await self.store.get_all()
    available_tools = set(self.tool_registry.keys())
    
    for skill in all_skills:
        required = set(skill.tools_required)
        if not required.issubset(available_tools):
            skill.confidence *= 0.5  # Degradar confianza
            if skill.confidence < 0.2:
                await self.store.deprecate(skill)
```

### C5 — Feedback loop de correcciones al KnowledgeExtractor

**Problema:** El ciclo corrige y verifica, pero no aprende DE las correcciones.

**Corrección:** Después de cada corrección (exitosa o fallida), crear una TaskExperience y pasarla al KnowledgeExtractor.

```python
async def _post_correction_learning(self, proposal, success: bool):
    """Aprende de cada corrección aplicada."""
    experience = TaskExperience(
        task_id=f"correction_{proposal.drift_alert.objective_id}",
        task_type="self_correction",
        tools_used=["compliance_monitor", "self_correction_engine"],
        steps_taken=[proposal.implementation],
        outcome="success" if success else "failure",
        duration_seconds=0,
        errors_encountered=[] if success else [proposal.description],
        recovery_strategies=[proposal.implementation] if success else [],
        novel_approaches=[]
    )
    await self.knowledge.evaluate(experience)
```

### C6 — Detección automática de novedad

**Problema:** `novel_approaches` en TaskExperience es un campo manual. Nadie lo llena.

**Corrección:** Comparar los pasos de la tarea con las skills existentes. Si los pasos difieren significativamente de cualquier skill conocida, marcar como "novedoso" automáticamente.

```python
async def _detect_novelty(self, experience: TaskExperience) -> list[str]:
    """Detecta enfoques novedosos comparando con skills existentes."""
    all_skills = await self.store.get_all()
    known_steps = set()
    for skill in all_skills:
        known_steps.update(skill.steps)
    
    novel = [step for step in experience.steps_taken 
             if step not in known_steps]
    return novel
```

---

## Veredicto Final

Sprint 69 es un sprint sólido que transforma al Guardián de un prototipo a un sistema operativo. La automatización de métricas, el baseline para regresiones, y el Knowledge Extraction Engine son adiciones de alto valor. Sin embargo, el sprint tiene 3 debilidades principales:

1. **Over-engineering en fuentes de métricas** (4 fuentes cuando 2 bastarían)
2. **Placeholders que contaminan métricas** (valores hardcodeados en lugar de None)
3. **Falta de learning loop cerrado** (corrige pero no aprende de las correcciones)

Las 6 correcciones mandatorias (C1-C6) abordan estos problemas. Con las correcciones aplicadas, el score sube de 7.0/10 a 8.8/10.

La tendencia descendente de Obj #3 (Mínima Complejidad) es la preocupación más seria. Dos sprints consecutivos de descenso (92% → 91% → 90%) requieren atención en Sprint 70. La corrección C1 (eliminar 2 fuentes) mitiga parcialmente, pero Sprint 70 debe incluir una épica de "simplificación y consolidación" para revertir la tendencia.

---

## Impacto Proyectado Post-Sprint 69

| Métrica | Post-Sprint 68 | Post-Sprint 69 | Delta |
|---|---|---|---|
| Promedio 14 Objetivos | 89.2% | 91.1% | +1.9% |
| Promedio 13 Objetivos (sin #14) | 92.5% | 93.2% | +0.7% |
| Objetivos en 100% | 2 | 2 | = |
| Objetivos ≥95% | 0 | 3 (#4, #6, #8) | +3 |
| Objetivos en riesgo (<90%) | 1 (#3 en 91%) | 2 (#3 en 90%, #14 en 65%) | +1 |
| Obj #14 (Guardián) | 40% | 65% | +25% |
