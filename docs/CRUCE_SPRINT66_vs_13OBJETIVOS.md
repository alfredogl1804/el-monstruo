# Cruce Sprint 66 vs. 13 Objetivos Maestros — Modo Detractor

**Fecha:** 1 mayo 2026
**Autor:** Manus AI (Modo Detractor Activado)
**Metodología:** Análisis crítico no complaciente. Cada épica se evalúa buscando debilidades, riesgos, y áreas de oportunidad.

---

## Score de Confianza del Plan

**8.0/10** (antes de correcciones)

Justificación: Sprint 66 es el más sólido de la serie 61-70 hasta ahora. Ataca los 4 objetivos más débiles con soluciones que se integran naturalmente con infraestructura existente (FinOps, Supervisor, Embrión Lessons). El hecho de que AHORRA dinero (Adaptive Quality) en lugar de agregar costos es una señal de madurez arquitectónica. Las correcciones son menores pero importantes para robustez.

---

## Análisis por Objetivo

### Obj #1 — Crear Empresas Reales (91% → 91%)

**Impacto directo:** NULO.

**Impacto indirecto:** El Simulator v3 con portfolio simulation permite evaluar MÚLTIPLES ideas de negocio simultáneamente antes de ejecutar. Esto mejora la selección de qué empresa crear. Impacto indirecto correcto pero no cuantificable como avance directo.

---

### Obj #2 — Nivel Apple/Tesla (92% → 92%)

**Impacto directo:** NULO.

**Crítica:** Aceptable — Obj #2 ya está en 92% y Sprint 66 se enfoca en resiliencia, no estética.

---

### Obj #3 — Mínima Complejidad (92% → 92%)

**Impacto directo:** NULO.

**Crítica positiva:** El Adaptive Quality Engine es TRANSPARENTE para el usuario — degrada sin que el usuario necesite intervenir. Esto es "mínima complejidad" en acción, aunque no se declara como avance directo.

---

### Obj #4 — Nunca Equivocarse 2 Veces (90% → 95%)

**Impacto directo:** Épica 66.3 (Cross-Project Error Intelligence)
**Avance declarado:** +5%

**Crítica MODERADA:**

1. **Generalization threshold de 2 es bajo.** Dos errores similares no necesariamente indican un patrón universal. Podría ser coincidencia. Debería ser 3 para "candidate" y 5 para "confirmed" pattern.

2. **`eval()` en condition matching es un riesgo de seguridad.** Aunque se usa con `{"__builtins__": {}}`, un patrón malformado podría causar problemas. Debería usar un parser de expresiones seguro (ast.literal_eval o un mini-DSL).

3. **Confidence decay de 2%/semana es arbitrario.** ¿Por qué 2%? Sin calibración empírica, podría ser demasiado agresivo (patterns útiles se pierden) o demasiado lento (patterns obsoletos persisten). Debería ser configurable y ajustable.

4. **Límite de 5 reglas por prompt es correcto** pero necesita priorización inteligente. No solo por confidence — también por RELEVANCE al contexto actual. Un pattern de alta confidence pero baja relevancia no debería ocupar un slot.

---

### Obj #5 — Gasolina Magna/Premium (90% → 95%)

**Impacto directo:** Épica 66.2 (Adaptive Quality Engine)
**Avance declarado:** +5%

**Crítica MODERADA:**

1. **Thresholds fijos (60%, 75%, 85%, 95%) no se adaptan al patrón de uso.** Un usuario que gasta 50% del budget en las primeras 2 horas tiene un patrón diferente a uno que gasta uniformemente. Los thresholds deberían ser dinámicos basados en burn rate + hora del día.

2. **No hay mecanismo para "reservar" budget.** Si el usuario sabe que necesita Premium a las 5pm, debería poder reservar $5 del budget para esa hora. Sin reservas, el sistema podría degradar antes de una tarea crítica.

3. **Override sin timeout es peligroso.** Si alguien hace `set_override(PREMIUM)` y se olvida, el budget se agota sin protección. Override debería tener TTL obligatorio.

4. **La predicción de exhaustion asume burn rate constante.** En realidad, el uso es bursty. Debería usar EMA (Exponential Moving Average) del burn rate, no promedio simple.

---

### Obj #6 — Vanguardia Perpetua (91% → 91%)

**Impacto directo:** NULO.

**Crítica:** Aceptable.

---

### Obj #7 — No Inventar la Rueda (93% → 93%)

**Impacto directo:** NULO.

**Crítica positiva:** Sprint 66 reutiliza FinOps (Sprint 15), Supervisor fallbacks (Sprint 33), Embrión Lessons (Sprint 34), y Monte Carlo (Sprint 55). Excelente adherencia a Obj #7.

---

### Obj #8 — Inteligencia Emergente (92% → 92%)

**Impacto directo:** NULO.

**Impacto indirecto:** El Cross-Project Error Intelligence PODRÍA exhibir emergencia si detecta patterns que ningún humano programó explícitamente. Pero esto no se mide ni se reporta al Emergence Evidence Collector (Sprint 65). Oportunidad perdida.

---

### Obj #9 — Transversalidad Universal (100%)

**Ya cerrado.** No aplica.

---

### Obj #10 — Simulador Predictivo (90% → 95%)

**Impacto directo:** Épica 66.4 (Scenario Simulator v3)
**Avance declarado:** +5%

**Crítica MODERADA:**

1. **`eval()` en decision tree navigation es un riesgo de seguridad.** Mismo problema que en Error Intelligence. Necesita sandbox o parser seguro.

2. **Correlation matrix asume normalidad (Gaussian copula).** Esto es una simplificación. Para variables con heavy tails (como ingresos), una t-copula sería más apropiada. Al menos documentar la limitación.

3. **Portfolio simulation asume correlación CONSTANTE entre negocios.** En realidad, la correlación varía por industria, geografía, y tiempo. Un valor fijo de 0.3 es una simplificación fuerte.

4. **No hay persistencia de escenarios.** Los escenarios se definen ad-hoc. Debería haber un catálogo de escenarios guardados para reutilización y comparación temporal.

---

### Obj #11 — Embriones Autónomos (100%)

**Ya cerrado.** No aplica.

---

### Obj #12 — Ecosistema/Soberanía (89% → 95%)

**Impacto directo:** Épicas 66.1 (Sovereignty Playbooks) + 66.5 (Self-Healing)
**Avance declarado:** +6%

**Crítica MODERADA:**

1. **Playbooks son DOCUMENTOS, no CÓDIGO ejecutable.** Los migration_steps son strings descriptivos, no funciones ejecutables. "Validate playbook" solo verifica pre-conditions, no ejecuta la migración real. Para ser realmente validado, necesita un dry-run mode que ejecute pasos 1-3 en un entorno de test.

2. **Self-healing sin observability es ciego.** El engine detecta fallos y ejecuta recovery, pero no hay dashboard ni métricas históricas. ¿Cuántos incidentes hubo este mes? ¿Cuál es el MTTR real? Sin métricas, no se puede mejorar.

3. **Recovery actions son fire-and-forget.** Se ejecuta `action_fn()` pero no se verifica que REALMENTE funcionó. Debería re-ejecutar el health check inmediatamente después del recovery action para confirmar.

4. **Cascade check es unidireccional.** Si A falla y B depende de A, se checa B. Pero si B falla, ¿se checa A como posible root cause? El cascade debería ser bidireccional.

---

### Obj #13 — Del Mundo (91% → 91%)

**Impacto directo:** NULO.

**Crítica:** Aceptable — Sprint 66 se enfoca en resiliencia interna.

---

## Correcciones Mandatorias

### C1: Reemplazar `eval()` con parser seguro (Obj #4, #10)

**Problema:** `eval()` es un vector de ataque, incluso con `__builtins__` vacío.
**Corrección:** Usar `ast.literal_eval` para expresiones simples o un mini-evaluator seguro.

```python
import ast
import operator

SAFE_OPS = {
    ast.Gt: operator.gt,
    ast.Lt: operator.lt,
    ast.GtE: operator.ge,
    ast.LtE: operator.le,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def safe_eval(expression: str, context: dict) -> bool:
    """Safely evaluate a comparison expression with variable substitution."""
    try:
        tree = ast.parse(expression, mode="eval")
        return _eval_node(tree.body, context)
    except Exception:
        return False

def _eval_node(node: ast.AST, ctx: dict) -> Any:
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, ctx)
        for op, comparator in zip(node.ops, node.comparators):
            right = _eval_node(comparator, ctx)
            if not SAFE_OPS[type(op)](left, right):
                return False
        return True
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left, ctx)
        right = _eval_node(node.right, ctx)
        return SAFE_OPS[type(node.op)](left, right)
    elif isinstance(node, ast.Name):
        return ctx.get(node.id, 0)
    elif isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            return all(_eval_node(v, ctx) for v in node.values)
        elif isinstance(node.op, ast.Or):
            return any(_eval_node(v, ctx) for v in node.values)
    raise ValueError(f"Unsupported node: {type(node)}")
```

### C2: Override con TTL obligatorio (Obj #5)

**Problema:** Override sin timeout puede agotar budget sin protección.
**Corrección:** Agregar TTL con auto-clear.

```python
def set_override(self, level: QualityLevel, ttl_minutes: int = 60) -> None:
    """Manual override with mandatory TTL."""
    if ttl_minutes > 240:  # Max 4 hours
        ttl_minutes = 240
    
    self._override = level
    self._override_expires = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    logger.info("quality_override_set", level=level.name, expires_in_minutes=ttl_minutes)

async def get_current_quality(self) -> QualityConfig:
    """Check override expiry before returning quality."""
    if self._override and self._override_expires:
        if datetime.now(timezone.utc) > self._override_expires:
            logger.info("quality_override_expired")
            self._override = None
            self._override_expires = None
    # ... rest of method
```

### C3: Generalization threshold = 3 (Obj #4)

**Problema:** 2 ocurrencias es insuficiente para generalizar con confianza.
**Corrección:** Subir threshold y agregar nivel "candidate".

```python
GENERALIZATION_THRESHOLD = 3       # Need 3+ to create pattern
CONFIRMATION_THRESHOLD = 5         # Need 5+ to mark as "confirmed"

async def observe_error(self, error: dict) -> Optional[ErrorPattern]:
    similar_errors = await self._find_similar_errors(error)
    if len(similar_errors) >= self.CONFIRMATION_THRESHOLD:
        pattern = await self._generalize_pattern(error, similar_errors)
        pattern.confidence = 0.8  # High confidence for confirmed
    elif len(similar_errors) >= self.GENERALIZATION_THRESHOLD:
        pattern = await self._generalize_pattern(error, similar_errors)
        pattern.confidence = 0.5  # Moderate for candidate
    else:
        await self._store_raw_error(error)
        return None
```

### C4: Self-healing debe verificar recovery success (Obj #12)

**Problema:** Recovery action se ejecuta pero no se confirma.
**Corrección:** Re-check después de recovery.

```python
async def _attempt_recovery(self, service_name: str) -> None:
    # ... execute recovery action ...
    
    try:
        await action.action_fn()
        
        # VERIFY recovery worked
        await asyncio.sleep(5)  # Brief wait for service to stabilize
        check = self._health_checks[service_name]
        recovered = await asyncio.wait_for(
            check.check_fn(), timeout=check.timeout_seconds
        )
        
        if recovered:
            logger.info("recovery_verified", service=service_name, action=action.name)
            health.state = ServiceState.HEALTHY
            health.consecutive_failures = 0
        else:
            logger.warning("recovery_not_verified", service=service_name)
            # Will retry on next cycle with backoff
            
    except Exception as e:
        logger.error("recovery_action_failed", service=service_name, error=str(e))
```

### C5: Adaptive thresholds basados en burn rate (Obj #5)

**Problema:** Thresholds fijos no se adaptan al patrón de uso.
**Corrección:** Usar projected exhaustion time en lugar de % consumido.

```python
async def get_current_quality(self) -> QualityConfig:
    """Use projected exhaustion time instead of static thresholds."""
    prediction = await self.predict_exhaustion()
    hours_remaining = prediction["hours_remaining"]
    
    # Dynamic thresholds based on hours remaining in the day
    hours_in_day_remaining = self._hours_until_midnight()
    
    if hours_remaining > hours_in_day_remaining * 1.5:
        new_level = QualityLevel.PREMIUM  # Plenty of budget
    elif hours_remaining > hours_in_day_remaining:
        new_level = QualityLevel.STANDARD  # On track
    elif hours_remaining > hours_in_day_remaining * 0.5:
        new_level = QualityLevel.ECONOMY  # Running low
    elif hours_remaining > 1:
        new_level = QualityLevel.MINIMAL  # Critical
    else:
        new_level = QualityLevel.FREE  # Exhausted
    
    # ... rest of method
```

### C6: Persist scenarios in Supabase (Obj #10)

**Problema:** Escenarios son ad-hoc, no se guardan para comparación temporal.
**Corrección:** Tabla `scenarios` con versionado.

```python
async def save_scenario(self, scenario: Scenario) -> str:
    """Persist scenario for reuse and temporal comparison."""
    scenario_id = f"scn_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    await self._db.table("scenarios").insert({
        "id": scenario_id,
        "name": scenario.name,
        "description": scenario.description,
        "variables": [vars(v) for v in scenario.variables],
        "correlation_matrix": scenario.correlation_matrix.tolist() if scenario.correlation_matrix is not None else None,
        "decision_tree": [vars(n) for n in scenario.decision_tree] if scenario.decision_tree else None,
        "success_condition": scenario.success_condition,
        "time_horizon_months": scenario.time_horizon_months,
    }).execute()
    return scenario_id

async def load_scenario(self, scenario_id: str) -> Optional[Scenario]:
    """Load a previously saved scenario."""
    result = await self._db.table("scenarios").select("*").eq("id", scenario_id).execute()
    if not result.data:
        return None
    # Reconstruct Scenario from stored data
    data = result.data[0]
    return Scenario(
        name=data["name"],
        description=data["description"],
        variables=[Variable(**v) for v in data["variables"]],
        # ... reconstruct rest
    )
```

### C7: Bidirectional cascade check (Obj #12)

**Problema:** Cascade solo va downstream (A falla → check B). No busca root cause upstream.
**Corrección:** Agregar reverse cascade.

```python
async def _cascade_check(self, failed_service: str) -> None:
    """Check both downstream dependents AND upstream dependencies."""
    # Downstream: services that depend on failed_service
    dependents = self._cascade_map.get(failed_service, [])
    for dep in dependents:
        await self._check_single(dep, reason=f"cascade_from_{failed_service}")
    
    # Upstream: services that failed_service depends on (reverse lookup)
    for service, deps in self._cascade_map.items():
        if failed_service in deps:
            # failed_service depends on 'service' — check if it's the root cause
            upstream_healthy = await self._check_single(service, reason="root_cause_search")
            if not upstream_healthy:
                logger.info("root_cause_identified",
                          failed=failed_service, root_cause=service)
```

### C8: Connect Error Intelligence to Emergence Tracker (Obj #8)

**Problema:** Cross-project patterns PODRÍAN ser emergencia pero no se reportan.
**Corrección:** Cuando un pattern se generaliza sin programación explícita, notificar al Emergence Tracker.

```python
async def _generalize_pattern(self, error: dict, similar: list[dict]) -> ErrorPattern:
    pattern = ...  # existing logic
    
    # Check if this generalization is emergent behavior
    if len(set(e.get("project_id") for e in similar)) >= 3:
        # Pattern emerged across 3+ different projects without explicit programming
        await self._notify_emergence_tracker({
            "type": "cross_project_pattern_emergence",
            "description": f"Error pattern '{pattern.pattern_description}' "
                          f"emerged across {len(similar)+1} projects autonomously",
            "evidence": pattern.id,
        })
    
    return pattern
```

---

## Resumen de Impacto Post-Correcciones

| Objetivo | Pre-Sprint 66 | Post-Sprint 66 (con correcciones) | Delta |
|---|---|---|---|
| #1 Crear Empresas | 91% | 91% | 0% |
| #2 Nivel Apple/Tesla | 92% | 92% | 0% |
| #3 Mínima Complejidad | 92% | 92% | 0% |
| #4 Nunca Equivocarse 2x | 90% | 94% | +4% (reduced from +5 due to threshold strictness) |
| #5 Gasolina Magna/Premium | 90% | 95% | +5% |
| #6 Vanguardia Perpetua | 91% | 91% | 0% |
| #7 No Inventar Rueda | 93% | 93% | 0% |
| #8 Inteligencia Emergente | 92% | 93% | +1% (bonus from C8 connection) |
| #9 Transversalidad | 100% | 100% | 0% |
| #10 Simulador Predictivo | 90% | 94% | +4% (reduced from +5 due to copula limitation) |
| #11 Embriones | 100% | 100% | 0% |
| #12 Ecosistema/Soberanía | 89% | 94% | +5% (with verified recovery) |
| #13 Del Mundo | 91% | 91% | 0% |

**Promedio post-Sprint 66:** 93.8% (vs. 92.4% pre = +1.4%)

**Score de confianza post-correcciones:** 9.0/10

---

## Veredicto Final

Sprint 66 es **el sprint más maduro de la serie 61-70**. Razones:

1. **No agrega complejidad innecesaria** — se integra con infraestructura existente (FinOps, Supervisor, Lessons).
2. **AHORRA dinero** — primer sprint con costo neto negativo gracias al Adaptive Quality Engine.
3. **Cierra gaps reales** — los 4 objetivos más débiles reciben avances significativos.
4. **Es testeable** — cada épica tiene criterios de éxito medibles (MTTR, Brier score, etc.).

Las 8 correcciones son menores pero importantes. La más crítica es **C1 (safe_eval)** porque `eval()` en producción es un riesgo de seguridad inaceptable. La más valiosa es **C5 (adaptive thresholds)** porque transforma el engine de "reglas estáticas" a "inteligencia adaptiva".

**Recomendación de ejecución:** Sprint 66 puede ejecutarse INMEDIATAMENTE después de Sprint 55 (Monte Carlo v1) porque expande directamente sobre esa base. No requiere Sprints 56-65 como prerequisito.
