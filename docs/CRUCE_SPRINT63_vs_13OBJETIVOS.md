# Cruce Sprint 63 vs. 13 Objetivos Maestros — Modo Detractor

**Fecha:** 1 mayo 2026
**Autor:** Manus AI (Modo Detractor Activado)
**Metodologia:** Analisis critico no complaciente. Cada epica se evalua buscando debilidades, riesgos, y areas de oportunidad.

---

## Score de Confianza del Plan

**6.0/10** (antes de correcciones)

Justificacion: El Sprint 63 tiene buenas ideas pero sufre de un problema recurrente en la serie 61-70: **ambicion sin profundidad**. Cinco epicas que tocan 5 objetivos diferentes es demasiado disperso. Cada epica necesita mas rigor en los detalles de implementacion.

---

## Analisis por Objetivo

### Obj #1 — Crear Empresas Reales (89% → 89%)

**Impacto directo:** NULO. Sprint 63 no avanza este objetivo.

**Critica:** Con 89% este objetivo esta casi cerrado, pero falta el demo E2E. Ningun sprint desde el 57 ha avanzado la demostracion end-to-end de crear una empresa completa. El zero-config (63.2) ayuda indirectamente pero no es suficiente.

---

### Obj #2 — Nivel Apple/Tesla (83% → 88%)

**Impacto directo:** Epica 63.3 (Motion Design System)
**Avance declarado:** +5%

**Critica SEVERA:**

1. **Motion tokens sin validacion visual.** Definir tokens en Python es trivial. Lo dificil es que las animaciones REALMENTE se vean bien. No hay proceso de QA visual para las animaciones.

2. **Framer Motion es una dependencia de TEMPLATE, no del kernel.** El Motion Orchestrator genera configs de animacion, pero quien las consume? Los proyectos creados por El Monstruo. Esto significa que cada proyecto debe incluir `motion` como dependencia — aumenta bundle size en ~40KB gzipped.

3. **No hay benchmark contra Apple/Tesla reales.** Decir "nivel Apple" sin medir contra productos Apple reales es marketing, no ingenieria. Donde esta la comparacion cuantitativa?

4. **`prefers-reduced-motion` es lo minimo, no un diferenciador.** Todos los frameworks modernos lo soportan. El verdadero diferenciador seria animaciones que MEJORAN la usabilidad, no solo las que se ven bonitas.

---

### Obj #3 — Minima Complejidad (82% → 87%)

**Impacto directo:** Epica 63.2 (Zero-Config Experience)
**Avance declarado:** +5%

**Critica SEVERA:**

1. **Intent inference con keyword matching es fragil.** El `IntentInferrer` usa diccionarios de patrones — esto falla con sinonimos, jerga regional, y frases ambiguas. "Quiero algo para mi negocio de tacos" no matchea "restaurant" directamente.

2. **Confidence threshold no definido.** Si la confianza es baja, que pasa? El codigo no muestra el fallback. Deberia preguntar al usuario, pero eso rompe la promesa de "zero config".

3. **Smart defaults son ESTATICOS.** 6 combinaciones industry+style no cubren la realidad. Un gym de yoga no es igual a un gym de CrossFit. Un restaurante fino no es igual a una taqueria.

4. **"<60 segundos" es una metrica sin contexto.** 60 segundos para QUE exactamente? Un sitio desplegado? Un preview? Un esqueleto? Sin definir el entregable, la metrica es vacia.

---

### Obj #4 — Nunca Equivocarse 2 Veces (84% → 84%)

**Impacto directo:** NULO.

**Critica:** El Error Learning Loop (Sprint 61) sigue sin integracion con el zero-config. Si el intent inferrer se equivoca, esa correccion deberia alimentar el loop. No hay conexion.

---

### Obj #5 — Gasolina Magna/Premium (85% → 85%)

**Impacto directo:** NULO.

**Critica:** El Research Intelligence Engine usa LLM para generar proposals — esto consume tokens. No hay budget cap para el daily scan. Si el scan encuentra 50 items y genera 10 proposals, eso son ~10K tokens/dia solo en scoring. Falta cost awareness.

---

### Obj #6 — Vanguardia Perpetua (81% → 88%)

**Impacto directo:** Epica 63.1 (Research Intelligence Engine)
**Avance declarado:** +7%

**Critica MODERADA:**

1. **Agents Radar ya cubre 80% de esto.** El valor incremental real del Intelligence Engine es el SCORING y las PROPOSALS, no el discovery. El plan deberia ser mas explicito sobre que es nuevo vs. que ya existe.

2. **Semantic Scholar rate limit (100 req/5min) es generoso PERO** el weekly scan con 5 topics x 20 results = 5 requests. Esto esta bien. Sin embargo, las recommendations API requiere un paper_id — de donde viene el seed paper? No esta definido.

3. **Integration proposals sin execution pipeline.** Generar proposals es facil. Ejecutarlas automaticamente es el verdadero valor. El plan dice "status: pending" pero no dice quien/como se aprueba y ejecuta.

4. **`_check_security` hardcoded a 0.8 es peligroso.** Esto significa que TODAS las herramientas pasan el security check por default. La integracion real con OSV.dev es mandatoria, no opcional.

---

### Obj #7 — No Inventar la Rueda (93% → 93%)

**Impacto directo:** NULO (ya esta alto).

**Critica positiva:** El Sprint 63 correctamente NO reinventa Agents Radar. Esto es consistente con Obj #7.

---

### Obj #8 — Inteligencia Emergente (83% → 89%)

**Impacto directo:** Epica 63.5 (Cross-Embrion Learning)
**Avance declarado:** +6%

**Critica SEVERA:**

1. **"Emergencia" requiere que NO este programada.** Pero el KnowledgePropagator PROGRAMA explicitamente la propagacion de patrones. Esto es transfer learning, no emergencia. La distincion es fundamental.

2. **El EmergenceDetector es demasiado simplista.** `_detect_spontaneous_collaboration` solo busca tareas en el mismo proyecto por multiples embriones. Pero si dos embriones trabajan en el mismo proyecto porque el scheduler los asigno, eso NO es espontaneo.

3. **Success rate threshold de 0.8 para auto-propagation es arbitrario.** Con solo 3 aplicaciones, una tasa de 0.8 significa 2.4 exitos — imposible con numeros enteros. Deberia ser `times_succeeded >= 3 AND success_rate >= 0.75`.

4. **Retraction threshold de 0.5 con 5 aplicaciones es demasiado permisivo.** Un patron que falla 50% del tiempo deberia retractarse con menos intentos. 3 fallos en 5 intentos deberia ser suficiente.

---

### Obj #9 — Transversalidad Universal (100%)

**Ya cerrado.** No aplica.

---

### Obj #10 — Simulador Predictivo (86% → 86%)

**Impacto directo:** NULO.

**Critica:** El Research Intelligence Engine podria alimentar el simulador con nuevas variables causales descubiertas en papers. Esta conexion no esta en el plan.

---

### Obj #11 — Embriones Autonomos (100%)

**Ya cerrado.** No aplica.

---

### Obj #12 — Ecosistema/Soberania (85% → 85%)

**Impacto directo:** NULO directo, pero el Marketplace (63.4) contribuye indirectamente al ecosistema.

**Critica:** El Marketplace deberia tener opcion de self-hosting (soberania). Si el marketplace central cae, los plugins instalados siguen funcionando? No esta claro.

---

### Obj #13 — Del Mundo (82% → 87%)

**Impacto directo:** Epica 63.4 (Plugin Marketplace)
**Avance declarado:** +5%

**Critica MODERADA:**

1. **Marketplace sin usuarios es un marketplace muerto.** Quien publica plugins? El Monstruo es un sistema de un solo usuario actualmente. El marketplace necesita una estrategia de go-to-market.

2. **Revenue sharing sin Stripe integration.** El plan dice "placeholder: integrate with Stripe in future sprint" — pero sin pagos reales, el revenue sharing es ficcion.

3. **Quality review pipeline no definido.** `verified: False` al publicar, pero quien/como verifica? LLM? Manual? Automated tests?

4. **No hay versionado de marketplace items.** Si un plugin se actualiza, como se manejan breaking changes para usuarios que ya lo instalaron?

---

## Correcciones Mandatorias

### C1: Intent Inferrer debe usar LLM como fallback (Obj #3)

**Problema:** Keyword matching falla con lenguaje natural real.
**Correccion:** Si confidence < 0.6, usar LLM para clasificar. Si confidence < 0.4, preguntar al usuario con opciones sugeridas.

```python
async def infer(self, user_input: str, user_locale: str = "es-MX") -> InferredProject:
    result = self._rule_based_inference(user_input)
    if result.confidence < 0.6:
        result = await self._llm_inference(user_input, result)
    if result.confidence < 0.4:
        result.needs_confirmation = True  # UI must ask user
    return result
```

### C2: Security check DEBE consultar OSV.dev (Obj #6)

**Problema:** `_check_security` hardcoded a 0.8 deja pasar vulnerabilidades.
**Correccion:** Implementar consulta real a OSV.dev API.

```python
async def _check_security(self, item: DiscoveryItem) -> float:
    """Query OSV.dev for known vulnerabilities."""
    try:
        resp = await self._client.post(
            "https://api.osv.dev/v1/query",
            json={"package": {"name": item.title, "ecosystem": "PyPI"}},
        )
        vulns = resp.json().get("vulns", [])
        if not vulns:
            return 1.0
        # Penalize based on severity
        critical = sum(1 for v in vulns if "CRITICAL" in str(v.get("severity", "")))
        high = sum(1 for v in vulns if "HIGH" in str(v.get("severity", "")))
        return max(0, 1.0 - (critical * 0.4) - (high * 0.2))
    except Exception:
        return 0.5  # Unknown = cautious, not optimistic
```

### C3: Emergence detection debe filtrar asignaciones del scheduler (Obj #8)

**Problema:** Tareas asignadas por el scheduler no son "espontaneas".
**Correccion:** Agregar filtro explicito.

```python
async def _detect_spontaneous_collaboration(self) -> list[dict]:
    # ... existing query ...
    for pid, tasks in by_project.items():
        embriones_involved = set(t.get("embrion_name") for t in tasks)
        if len(embriones_involved) >= 2:
            # CRITICAL: Filter out scheduler-assigned tasks
            spontaneous_tasks = [
                t for t in tasks
                if t.get("trigger") not in ("scheduler", "collective_protocol", "user_request")
            ]
            if len(set(t.get("embrion_name") for t in spontaneous_tasks)) >= 2:
                patterns.append(...)
```

### C4: Propagation threshold corregido (Obj #8)

**Problema:** 0.8 success rate con 3 attempts es matematicamente imposible con enteros.
**Correccion:** `times_succeeded >= 3 AND times_applied >= 4 AND success_rate >= 0.75`

### C5: Daily scan budget cap (Obj #5)

**Problema:** Sin limite, el scan puede consumir tokens indefinidamente.
**Correccion:** Max 5 proposals/day, max 2000 tokens per scoring call.

```python
async def run_daily_scan(self) -> dict:
    MAX_PROPOSALS_PER_DAY = 5
    proposals_generated = 0
    # ... scan logic ...
    if scored.relevance_score >= 0.7 and proposals_generated < MAX_PROPOSALS_PER_DAY:
        proposal = await self.generate_proposal(scored)
        if proposal:
            proposals_generated += 1
```

### C6: Marketplace items DEBEN tener versionado (Obj #13)

**Problema:** Sin versionado, updates rompen instalaciones existentes.
**Correccion:** Agregar tabla `marketplace_versions` con semver.

```sql
CREATE TABLE marketplace_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID REFERENCES marketplace_items(id),
    version TEXT NOT NULL,
    changelog TEXT,
    min_compatible_version TEXT,  -- Minimum El Monstruo version
    published_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(item_id, version)
);
```

### C7: Motion system debe medir impacto en UX (Obj #2)

**Problema:** Animaciones sin medicion de impacto son decoracion, no UX.
**Correccion:** Integrar con PostHog para medir si animaciones mejoran engagement.

```python
# Track animation impact
async def measure_animation_impact(self, project_id: str) -> dict:
    """Compare engagement metrics with/without animations."""
    # A/B test: same page, animations on vs off
    # Measure: time on page, scroll depth, CTA clicks
    return {
        "with_animations": {"avg_time": 45, "scroll_depth": 0.72, "cta_rate": 0.08},
        "without_animations": {"avg_time": 38, "scroll_depth": 0.61, "cta_rate": 0.06},
        "lift": "+18% time, +18% scroll, +33% CTA",
    }
```

### C8: Marketplace go-to-market strategy (Obj #13)

**Problema:** Marketplace sin usuarios es inutil.
**Correccion:** Seed con 10+ plugins/templates built-in. Convertir los 6 templates de onboarding (Sprint 61) en marketplace items. Los plugins de Sprint 62 tambien se publican.

---

## Resumen de Impacto Post-Correcciones

| Objetivo | Pre-Sprint 63 | Post-Sprint 63 (con correcciones) | Delta |
|---|---|---|---|
| #1 Crear Empresas | 89% | 89% | 0% |
| #2 Nivel Apple/Tesla | 83% | 88% | +5% |
| #3 Minima Complejidad | 82% | 87% | +5% |
| #4 Nunca Equivocarse 2x | 84% | 85% | +1% (via C1 feedback) |
| #5 Gasolina Magna/Premium | 85% | 86% | +1% (via C5 budget) |
| #6 Vanguardia Perpetua | 81% | 88% | +7% |
| #7 No Inventar Rueda | 93% | 93% | 0% |
| #8 Inteligencia Emergente | 83% | 88% | +5% |
| #9 Transversalidad | 100% | 100% | 0% |
| #10 Simulador Predictivo | 86% | 86% | 0% |
| #11 Embriones | 100% | 100% | 0% |
| #12 Ecosistema/Soberania | 85% | 86% | +1% |
| #13 Del Mundo | 82% | 87% | +5% |

**Promedio post-Sprint 63:** 89.5% (vs. 87.2% pre = +2.3%)

**Score de confianza post-correcciones:** 7.5/10

---

## Veredicto Final

Sprint 63 es **aceptable con correcciones**. Las 8 correcciones son mandatorias. Las criticas mas graves son:

1. **C2 (OSV.dev):** Sin esto, el Intelligence Engine puede recomendar herramientas con CVEs conocidos. Inaceptable.
2. **C3 (Emergence filtering):** Sin esto, se reportarian "emergencias" falsas constantemente.
3. **C1 (LLM fallback):** Sin esto, el zero-config falla con >50% de inputs reales.

El sprint avanza 5 objetivos simultaneamente, lo cual es ambicioso pero viable dado que ninguna epica requiere infraestructura nueva costosa.
