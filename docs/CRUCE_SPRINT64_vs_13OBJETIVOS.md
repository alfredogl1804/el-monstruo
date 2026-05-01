# Cruce Sprint 64 vs. 13 Objetivos Maestros — Modo Detractor

**Fecha:** 1 mayo 2026
**Autor:** Manus AI (Modo Detractor Activado)
**Metodologia:** Analisis critico no complaciente. Cada epica se evalua buscando debilidades, riesgos, y areas de oportunidad.

---

## Score de Confianza del Plan

**7.0/10** (antes de correcciones)

Justificacion: Sprint 64 es conceptualmente solido — el cambio de "construir" a "validar" es correcto. Sin embargo, hay un riesgo fundamental: las validaciones dependen de features que aun NO estan implementadas (son de sprints 55-63 que solo estan PLANIFICADOS). El E2E demo no puede funcionar si el zero-config inferrer no existe todavia.

---

## Analisis por Objetivo

### Obj #1 — Crear Empresas Reales (89% → 92%)

**Impacto directo:** Epica 64.1 (E2E Demo Pipeline)
**Avance declarado:** +3%

**Critica SEVERA:**

1. **El E2E demo ASUME que los endpoints existen.** `/api/infer-intent`, `/api/configure-project`, `/api/generate-design`, `/api/generate-code`, `/api/deploy` — NINGUNO de estos endpoints existe actualmente. El demo runner es un test para un sistema que aun no esta construido.

2. **Los scenarios son demasiado optimistas.** "Crea una tienda online" en <300 segundos con $0.50 de costo es una fantasia sin evidencia. Ningun sistema actual logra esto. Shopify tarda minutos solo en el onboarding humano.

3. **No hay mecanismo de retry.** Si Step 3 (design) falla, todo el demo falla. No hay retry parcial ni checkpoint intermedio.

4. **Quality audit sin criterios definidos.** `_audit_quality` llama a un endpoint pero no define QUE se audita. Lighthouse? LLM review? Ambos?

---

### Obj #2 — Nivel Apple/Tesla (88% → 88%)

**Impacto directo:** NULO.

**Critica:** El E2E demo DEBERIA incluir un quality score visual (del Visual Quality Gate, Sprint 57). Sin esto, "crear una empresa" no garantiza que sea nivel Apple/Tesla.

---

### Obj #3 — Minima Complejidad (87% → 89%)

**Impacto directo:** Epica 64.1 (E2E Demo — demuestra simplicidad)
**Avance declarado:** +2%

**Critica MODERADA:** El demo mide TIEMPO, no COMPLEJIDAD percibida. Un sistema puede ser rapido pero confuso. La metrica real deberia incluir "pasos requeridos del usuario" (en este caso, 1 frase = 1 paso = excelente).

---

### Obj #4 — Nunca Equivocarse 2 Veces (85% → 90%)

**Impacto directo:** Epica 64.2 (Predictive Error Prevention)
**Avance declarado:** +5%

**Critica SEVERA:**

1. **Trigger keywords matching es fragil.** `any(kw.lower() in context_str for kw in trigger_keywords)` — esto genera falsos positivos masivos. Si un error tuvo keyword "deploy" y el usuario quiere deployar algo completamente diferente, se bloquea innecesariamente.

2. **Risk score formula es naive.** `warning_count * 0.15 + len(similar_errors) * 0.25` — con 4 warnings y 2 similar errors, el score es 1.1 (capped a 0.95). Esto significa que 4 warnings triviales bloquean la accion. No hay ponderacion por severidad de los warnings.

3. **Confidence Gate tiene circular dependency.** `_get_historical_success` consulta `preflight_logs.proceed` — pero `proceed` es el output del preflight, no del resultado real. Deberia consultar si la accion TUVO EXITO despues de proceder, no si fue permitida.

4. **No hay override mechanism.** Si el preflight bloquea una accion valida, no hay forma de que el usuario o el sistema override la decision. Esto puede crear deadlocks.

---

### Obj #5 — Gasolina Magna/Premium (86% → 90%)

**Impacto directo:** Epica 64.3 (Dynamic Tier Routing v2)
**Avance declarado:** +4%

**Critica MODERADA:**

1. **MODEL_COSTS hardcoded.** Los precios de APIs cambian frecuentemente. Hardcodear precios es un anti-pattern. Deberia consultarse una fuente actualizada o al menos tener un mecanismo de update.

2. **DEFAULT_QUALITY scores son inventados.** 0.92 para GPT-4o, 0.93 para Claude — de donde salen estos numeros? Sin datos reales, el optimizer toma decisiones basadas en suposiciones.

3. **Budget pressure formula favorece modelos baratos demasiado agresivamente.** Con budget_pressure de 0.8 (80% gastado), el formula penaliza tanto el costo que siempre selecciona el modelo mas barato, incluso para tareas criticas.

4. **No hay "minimum tier" por task criticality.** Un deployment NUNCA deberia usar el modelo mas barato solo porque queda poco budget. Hay tareas donde la calidad es non-negotiable.

---

### Obj #6 — Vanguardia Perpetua (88% → 88%)

**Impacto directo:** NULO.

**Critica:** Sprint 64 no avanza vanguardia. Esto es aceptable dado que el sprint es de validacion, no de nuevas capacidades.

---

### Obj #7 — No Inventar la Rueda (93% → 93%)

**Impacto directo:** NULO (ya esta alto).

**Critica positiva:** Sprint 64 correctamente reutiliza fallback_engine, usage_tracker, y cidp_calibrator en lugar de recrearlos.

---

### Obj #8 — Inteligencia Emergente (88% → 88%)

**Impacto directo:** NULO.

**Critica:** El Backtester podria detectar patrones emergentes en las predicciones (predicciones que mejoran sin intervencion humana = emergencia). Esta conexion no esta en el plan.

---

### Obj #9 — Transversalidad Universal (100%)

**Ya cerrado.** No aplica.

---

### Obj #10 — Simulador Predictivo (86% → 90%)

**Impacto directo:** Epica 64.4 (Simulator Validation Framework)
**Avance declarado:** +4%

**Critica MODERADA:**

1. **Brier Score requiere outcomes BINARIOS.** El backtester usa `hit` (CI contains actual) como outcome binario, pero las predicciones son CONTINUAS (predicted_value). Deberia usar CRPS (Continuous Ranked Probability Score) para predicciones continuas, no Brier.

2. **Minimum 5 predictions para report es demasiado bajo.** Con 5 datapoints, cualquier metrica estadistica es insignificante. Deberia ser minimo 20 para un report valido.

3. **Reliability bins de 10% son demasiado finos.** Con pocas predicciones, la mayoria de bins estaran vacios. Usar 5 bins (0-20%, 20-40%, etc.) seria mas robusto.

4. **No hay mecanismo para GENERAR predictions automaticamente.** El backtester valida predictions, pero quien las genera? El Monte Carlo Simulator (Sprint 55). La integracion entre ambos no esta definida.

---

### Obj #11 — Embriones Autonomos (100%)

**Ya cerrado.** No aplica.

---

### Obj #12 — Ecosistema/Soberania (86% → 90%)

**Impacto directo:** Epica 64.5 (Sovereignty Activation Test)
**Avance declarado:** +4%

**Critica SEVERA:**

1. **`_kill_service` y `_restore_service` son STUBS.** Los metodos criticos del test estan vacios (`pass`). Sin implementacion real, el test no prueba nada.

2. **Supabase kill es CATASTROFICO.** Si se desactiva Supabase, TODA la persistencia se pierde. No hay "degradacion menor" — es fallo total. El fallback "Local SQLite cache" no existe actualmente.

3. **El test no puede correr en produccion.** Desactivar env vars en produccion causa downtime real. Necesita un entorno de staging aislado que no existe.

4. **Binary degradation measurement.** El test solo mide "funciona/no funciona" (status 200 vs error). La degradacion real es un espectro: latencia, calidad, features parciales.

---

### Obj #13 — Del Mundo (87% → 87%)

**Impacto directo:** NULO.

**Critica:** Los demo scenarios incluyen uno en ingles ("Build a SaaS analytics dashboard") — esto es un mini-test de i18n. Pero no hay validacion de que el output sea correcto en el idioma del input.

---

## Correcciones Mandatorias

### C1: E2E Demo debe tener prerequisite check (Obj #1)

**Problema:** El demo asume endpoints que no existen.
**Correccion:** Agregar prerequisite validation que verifica que cada endpoint responde antes de correr el demo.

```python
async def _validate_prerequisites(self) -> list[str]:
    """Verify all required endpoints exist before running demo."""
    required_endpoints = [
        "/api/infer-intent",
        "/api/configure-project",
        "/api/generate-design",
        "/api/generate-code",
        "/api/deploy",
    ]
    missing = []
    for endpoint in required_endpoints:
        try:
            resp = await self.kernel.options(endpoint)
            if resp.status_code == 404:
                missing.append(endpoint)
        except Exception:
            missing.append(endpoint)
    return missing
```

### C2: Risk scoring debe ponderar por severidad (Obj #4)

**Problema:** Todos los warnings tienen el mismo peso.
**Correccion:** Ponderar por severidad y recency.

```python
def _calculate_risk(self, blockers: list, warnings: list, similar_errors: list) -> float:
    if blockers:
        return 0.95
    score = 0.0
    # Weight warnings by severity
    for w in warnings:
        if "CRITICAL" in w.upper():
            score += 0.3
        elif "budget" in w.lower():
            score += 0.2
        else:
            score += 0.1
    # Weight errors by recency (newer = more relevant)
    for i, error in enumerate(similar_errors):
        recency_weight = 1.0 / (i + 1)  # First = most recent
        score += 0.2 * recency_weight
    return min(score, 0.95)
```

### C3: Override mechanism para preflight (Obj #4)

**Problema:** Sin override, el sistema puede crear deadlocks.
**Correccion:** Agregar `force=True` parameter con audit trail.

```python
async def check(self, action: str, context: dict, force: bool = False) -> PreflightResult:
    result = await self._run_checks(action, context)
    if not result.proceed and force:
        result.proceed = True
        result.forced = True
        logger.warning("preflight_forced", action=action, risk=result.risk_level)
        # Log forced override for audit
        await self._log_forced_override(result, context)
    return result
```

### C4: Minimum tier por criticality (Obj #5)

**Problema:** Budget pressure puede seleccionar modelos demasiado baratos para tareas criticas.
**Correccion:** Definir minimum tier por task criticality.

```python
MINIMUM_TIER = {
    "deployment": "gpt-4o-mini",        # Never below standard
    "financial_calculation": "gpt-4o",   # Always premium
    "code_generation": "gpt-4o-mini",    # Standard minimum
    "design_generation": "gpt-4o-mini",  # Standard minimum
    "internal_task": "groq-llama-3.3-70b",  # Economy OK
    "user_communication": "gpt-4o-mini",    # Standard minimum
}

async def select_optimal_model(self, task_type: str, ...):
    min_model = self.MINIMUM_TIER.get(task_type, "groq-llama-3.3-70b")
    min_quality = self.DEFAULT_QUALITY.get(min_model, 0.5)
    # Ensure selected model is at least as good as minimum
    ...
```

### C5: Use CRPS for continuous predictions (Obj #10)

**Problema:** Brier Score es para outcomes binarios, no continuos.
**Correccion:** Agregar CRPS (Continuous Ranked Probability Score) para predicciones numericas.

```python
from scipy.stats import norm

def _calculate_crps(self, predictions: list[dict]) -> float:
    """CRPS for continuous predictions."""
    crps_scores = []
    for p in predictions:
        predicted = p["predicted_value"]
        actual = p["actual_outcome"]
        # Assume normal distribution with CI-derived sigma
        sigma = (p["confidence_upper"] - p["confidence_lower"]) / 3.92  # 95% CI
        if sigma <= 0:
            sigma = 1.0
        # CRPS for normal distribution
        z = (actual - predicted) / sigma
        crps = sigma * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))
        crps_scores.append(crps)
    return sum(crps_scores) / len(crps_scores) if crps_scores else float('inf')
```

### C6: Sovereignty test needs staging environment (Obj #12)

**Problema:** No se puede correr en produccion.
**Correccion:** Definir que el test corre en un entorno aislado con variables de entorno duplicadas.

```python
class SovereigntyActivationTest:
    """MUST run in staging environment, NEVER in production."""

    def __init__(self, kernel_client, environment: str = "staging"):
        if environment == "production":
            raise ValueError("Sovereignty tests CANNOT run in production. Use staging.")
        self.kernel = kernel_client
        self.environment = environment
        # Store original env vars for restoration
        self._original_env: dict[str, str] = {}

    async def _kill_service(self, service: dict) -> None:
        """Temporarily unset env vars (staging only)."""
        import os
        for var in service["env_vars"]:
            self._original_env[var] = os.environ.get(var, "")
            os.environ.pop(var, None)

    async def _restore_service(self, service: dict) -> None:
        """Restore env vars after test."""
        import os
        for var in service["env_vars"]:
            if var in self._original_env:
                os.environ[var] = self._original_env[var]
```

### C7: Minimum predictions for valid report raised to 20 (Obj #10)

**Problema:** 5 predictions es estadisticamente insignificante.
**Correccion:** Raise minimum to 20, use 5 bins instead of 10.

```python
async def generate_calibration_report(self) -> CalibrationReport:
    records = await self.supabase.table("prediction_records")...
    
    MIN_FOR_REPORT = 20
    if not records.data or len(records.data) < MIN_FOR_REPORT:
        return CalibrationReport(
            ...
            overall_grade="INSUFFICIENT_DATA",
            note=f"Need {MIN_FOR_REPORT} resolved predictions, have {len(records.data or [])}",
        )
```

### C8: Confidence Gate must use OUTCOME success, not preflight proceed (Obj #4)

**Problema:** Circular dependency — consulta si fue permitido, no si tuvo exito.
**Correccion:** Consultar tabla de resultados reales.

```python
async def _get_historical_success(self, action_type: str) -> Optional[float]:
    """Get historical SUCCESS rate (not permission rate) for this action type."""
    result = await self.supabase.table("action_outcomes")\
        .select("success")\
        .eq("action_type", action_type)\
        .order("created_at", desc=True)\
        .limit(20)\
        .execute()

    if not result.data or len(result.data) < 5:
        return None
    successes = sum(1 for r in result.data if r["success"])
    return successes / len(result.data)
```

---

## Tabla Adicional Requerida (de C8)

```sql
-- Action outcomes (for confidence gate feedback)
CREATE TABLE action_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_type TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    quality_score FLOAT,
    duration_seconds FLOAT,
    model_used TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## Resumen de Impacto Post-Correcciones

| Objetivo | Pre-Sprint 64 | Post-Sprint 64 (con correcciones) | Delta |
|---|---|---|---|
| #1 Crear Empresas | 89% | 91% | +2% (reduced from +3 due to prerequisite gap) |
| #2 Nivel Apple/Tesla | 88% | 88% | 0% |
| #3 Minima Complejidad | 87% | 89% | +2% |
| #4 Nunca Equivocarse 2x | 85% | 90% | +5% |
| #5 Gasolina Magna/Premium | 86% | 90% | +4% |
| #6 Vanguardia Perpetua | 88% | 88% | 0% |
| #7 No Inventar Rueda | 93% | 93% | 0% |
| #8 Inteligencia Emergente | 88% | 88% | 0% |
| #9 Transversalidad | 100% | 100% | 0% |
| #10 Simulador Predictivo | 86% | 90% | +4% |
| #11 Embriones | 100% | 100% | 0% |
| #12 Ecosistema/Soberania | 86% | 89% | +3% (reduced from +4 due to staging gap) |
| #13 Del Mundo | 87% | 87% | 0% |

**Promedio post-Sprint 64:** 91.0% (vs. 89.5% pre = +1.5%)

**Score de confianza post-correcciones:** 8.0/10

---

## Veredicto Final

Sprint 64 es **conceptualmente correcto pero prematuramente ambicioso**. El problema fundamental es que valida features que aun no estan implementadas (Sprints 55-63 son planes, no codigo). Las 8 correcciones son mandatorias, especialmente:

1. **C1 (Prerequisite check):** Sin esto, el E2E demo falla en el primer paso.
2. **C5 (CRPS):** Usar Brier Score para predicciones continuas es un error estadistico.
3. **C6 (Staging):** Correr sovereignty tests en produccion es suicidio operacional.
4. **C3 (Override):** Sin override, el preflight puede crear deadlocks irrecuperables.

**Recomendacion:** Sprint 64 deberia ejecutarse DESPUES de implementar al menos Sprints 55-57. De lo contrario, es un framework de validacion sin nada que validar.
