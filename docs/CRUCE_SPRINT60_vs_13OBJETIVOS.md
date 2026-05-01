# Cruce Sprint 60 vs 13 Objetivos Maestros — Modo Detractor

**Fecha:** 1 mayo 2026
**Autor:** Manus AI (modo detractor activado)
**Metodología:** Cada objetivo se evalúa como si un inversionista escéptico preguntara: "¿Esto realmente mueve la aguja o es feature creep?"
**Contexto especial:** Sprint de cierre de la serie 51-60. Evaluación más estricta que sprints anteriores.

---

## Matriz de Impacto

| # | Objetivo | Impacto Sprint 60 | Cobertura Pre-60 | Cobertura Post-60 | Veredicto |
|---|---|---|---|---|---|
| 1 | Crear Empresas Digitales | BAJO — No crea empresas, habilita infraestructura | 85% | 85% | Sin avance directo |
| 2 | Todo Nivel Apple/Tesla | NULO — No toca calidad visual | 65% | 65% | Gap persiste |
| 3 | Máximo Poder, Mínima Complejidad | BAJO — Simulator UI ayuda pero no es UX principal | 70% | 72% | Marginal |
| 4 | Nunca Se Equivoca Dos Veces | MEDIO — Calibración del simulador aprende de errores | 70% | 73% | Indirecto |
| 5 | Gasolina Magna vs Premium | BAJO — Sovereignty mode es tier routing extremo | 75% | 77% | Marginal |
| 6 | Vanguardia Perpetua | **ALTO** — Tech Radar + Auto-Updater + OSV.dev | **50%** | **80%** | Salto significativo |
| 7 | No Inventar la Rueda | ALTO — GlitchTip, Umami, Renovate, scipy | 90% | 92% | Consistente |
| 8 | Inteligencia Emergente | BAJO — No agrega nuevos mecanismos | 70% | 70% | Sin avance |
| 9 | Transversalidad Universal | NULO — Ya completo | 100% | 100% | N/A |
| 10 | Simulador Predictivo | **ALTO** — v2 con 6 distribuciones + calibración + API | **65%** | **85%** | Salto significativo |
| 11 | Multiplicación de Embriones | **MÁXIMO** — 7/7 COMPLETO | **71%** | **100%** | MILESTONE |
| 12 | Ecosistema / Soberanía | **ALTO** — Sovereignty Engine + health checks + sovereign mode | **40%** | **75%** | Salto significativo |
| 13 | Del Mundo | NULO — No toca i18n | 60% | 60% | Sin avance |

---

## Análisis Detractor por Épica

### Épica 60.1 — Sovereignty Engine

**Lo que funciona:** Inventario completo de 8 dependencias con alternativas, migration paths, y health checks. Sovereignty score cuantificable. Sovereign mode activable con un comando. Tabla de costos mensuales.

**Lo que no funciona:**

1. **"Sovereign mode" es un kill switch, no una migración real.** Activar sovereign mode pone `SOVEREIGN_MODE=true` y redirige a Ollama. Pero ¿se ha probado que Ollama realmente puede manejar la carga? ¿Qué pasa con la calidad de las respuestas? El plan dice "degraded features" pero no cuantifica CUÁNTO se degrada.

2. **Health checks son superficiales.** Verificar que Supabase responde a un SELECT no significa que esté sano. ¿Qué pasa con latencia alta? ¿Conexiones agotadas? ¿Disk space? Los health checks necesitan métricas, no solo up/down.

3. **No hay drill de sovereign mode.** ¿Cuándo fue la última vez que se activó sovereign mode y se verificó que TODO funciona? Sin drills periódicos, sovereign mode es una promesa vacía. Necesita un "chaos engineering" schedule.

4. **Migration paths son teóricos.** "pg_dump → pg_restore on self-hosted PG" suena simple pero ¿quién lo ha probado? ¿Cuánto tiempo toma? ¿Se pierden datos durante la migración? Sin runbooks probados, los migration paths son fantasía.

5. **Falta el costo de self-hosting.** El plan lista costos de SaaS pero no los costos de self-hosting (servidor, mantenimiento, DevOps time). Self-hosted no es gratis — puede ser más caro que SaaS para equipos pequeños.

### Épica 60.2 — Tech Radar & Auto-Updater

**Lo que funciona:** Escaneo real de PyPI via JSON API. OSV.dev para CVEs. GitHub trending para tendencias. Reporte estilo ThoughtWorks (Adopt/Trial/Assess/Hold).

**Lo que no funciona:**

1. **No genera PRs automáticos.** El plan dice "genera PRs de actualización" en el contexto pero la implementación solo genera REPORTES. ¿Quién aplica las actualizaciones? Renovate Bot se menciona en el stack pero no se integra en el código.

2. **Scan de dependencias es lento.** Iterar sobre ~50 paquetes en requirements.txt haciendo HTTP requests secuenciales a PyPI toma ~50 segundos. Necesita async batch o caching.

3. **GitHub trending API no existe oficialmente.** El endpoint `api.github.com/search/repositories` con filtro de fecha NO es "trending" — es "recently created with most stars." GitHub no tiene API oficial de trending. Los resultados serán diferentes a lo que aparece en github.com/trending.

4. **LLM enrichment de trends es circular.** Usar el LLM para evaluar relevancia de trends que ya fueron filtrados por el LLM es redundante. Necesita señales objetivas (downloads, stars, adoption rate) no opiniones de LLM.

5. **No hay rollback automático si un update rompe algo.** Detecta que hay updates pero no tiene mecanismo para revertir si un update causa regresión.

### Épica 60.3 — Simulator UI & Calibration

**Lo que funciona:** 6 distribuciones (Beta, Normal, Triangular, Uniform, Poisson, Lognormal) + Custom. Sensitivity analysis via correlación. Calibración con scipy.stats.fit. API endpoints para frontend.

**Lo que no funciona:**

1. **No hay UI.** El plan dice "Simulator UI" pero solo implementa el backend (Python). ¿Dónde está el componente React? ¿Los charts de Recharts? El título promete UI pero no la entrega.

2. **Calibración con scipy.stats.beta.fit es frágil.** Beta fit con `floc=0, fscale=1` asume datos normalizados a [0,1]. Si los datos reales son revenue ($0-$100K), la normalización puede perder información. Necesita distribución-aware normalization.

3. **Sensitivity analysis por correlación es simplista.** Correlación de Pearson solo captura relaciones lineales. Si un factor tiene efecto no-lineal (threshold effect), la correlación será baja pero el impacto real alto. Necesita al menos Spearman o SHAP values.

4. **10K simulaciones es arbitrario.** ¿Por qué 10K? Para distribuciones con colas pesadas (lognormal), 10K puede ser insuficiente. Para distribuciones simples (uniform), 1K basta. Debería ser adaptativo.

5. **Downsampling a 500 puntos para visualización pierde información.** `raw_outcomes[::max(1, len(outcomes)//500)]` es un stride uniforme que puede perder outliers. Mejor usar percentile-based sampling que preserva la distribución.

### Épica 60.4 — Embrión-Financiero

**Lo que funciona:** Unit economics con LTV/CAC/payback. Proyecciones con 3 escenarios. Burn rate con runway y alerts. Tax calendar como tarea autónoma.

**Lo que no funciona:**

1. **Proyecciones financieras son naive.** Crecimiento lineal con `growth_rate_monthly` constante no refleja realidad. Los negocios tienen curvas S, no líneas rectas. Necesita modelos más sofisticados (logistic growth, cohort-based).

2. **"Costs grow slower than revenue (economies of scale)" es un assumption peligroso.** En la realidad, muchos startups tienen costos que crecen MÁS rápido que revenue (hiring, infrastructure). El factor 0.6 es arbitrario y optimista.

3. **Tax obligations sin jurisdicción específica.** "Verificar obligaciones fiscales" es genérico. ¿México? ¿USA? ¿EU? Cada jurisdicción tiene reglas completamente diferentes. Sin especificar jurisdicción, el consejo fiscal es inútil.

4. **No integra con datos financieros reales.** ¿De dónde vienen las métricas? `metrics.get("total_marketing_spend")` asume que alguien las ingresa manualmente. No hay integración con Stripe, PayPal, o contabilidad real.

5. **Disclaimer de "consulte con un contador" es insuficiente.** Si el embrión da consejo fiscal incorrecto y el usuario lo sigue, el disclaimer no protege. Mejor: NO dar consejo fiscal específico, solo alertas de deadlines.

### Épica 60.5 — Embrión-Investigador

**Lo que funciona:** Deep research con Perplexity como fuente real. Fact-checking con confidence levels. Competitive analysis estructurado. Daily briefing autónomo.

**Lo que no funciona:**

1. **Budget de $2.50/día es insuficiente para research real.** Una sola query a Perplexity Pro cuesta ~$0.05-0.10. 25-50 queries/día no alcanza para "deep research" de múltiples competidores en múltiples nichos.

2. **Competitive analysis sin acceso a datos reales.** Pedir al LLM "market share" de competidores produce datos inventados. Sin acceso a SimilarWeb, Crunchbase, o SEC filings, el análisis competitivo es ficción.

3. **Daily briefing es genérico.** "Top AI and digital business news" no está personalizado al contexto del usuario. Debería filtrar por nichos activos, competidores monitoreados, y tecnologías en uso.

4. **Fact-checking con LLM es un oxímoron.** Usar un LLM para verificar claims es como pedirle a un testigo que se verifique a sí mismo. El LLM puede confirmar claims falsos con alta confianza. Solo Perplexity (web-grounded) tiene valor real aquí.

5. **No hay deduplicación de research.** Si el usuario pide research sobre "AI SaaS market" hoy y mañana, el embrión hace la misma investigación dos veces. Necesita cache de research con TTL.

---

## Correcciones Mandatorias

### C1: Sovereignty Engine necesita drills periódicos

**Problema:** Sovereign mode nunca se prueba, es promesa vacía.
**Corrección:** Agregar tarea autónoma al Embrión-Vigía que ejecuta sovereign mode drill mensual.

```python
"sovereignty_drill": {
    "description": "Activar sovereign mode por 5 minutos, verificar que todo funciona, desactivar",
    "interval_hours": 720,  # Monthly
    "handler": "run_sovereignty_drill",
}
```

### C2: Tech Radar debe generar PRs reales (o al menos diffs)

**Problema:** Solo genera reportes, nadie aplica las actualizaciones.
**Corrección:** Generar archivo `requirements.txt.proposed` con las actualizaciones y un diff legible.

```python
def generate_update_diff(self, current_content: str, updates: list[DependencyUpdate]) -> str:
    """Generar diff de requirements.txt con actualizaciones propuestas."""
    proposed = current_content
    for update in updates:
        if update.recommendation in ("update", "evaluate"):
            proposed = proposed.replace(
                f"{update.package}=={update.current_version}",
                f"{update.package}=={update.latest_version}  # AUTO-UPDATE from {update.current_version}"
            )
    return proposed
```

### C3: Simulator DEBE incluir UI React (no solo backend)

**Problema:** El título dice "Simulator UI" pero solo hay Python backend.
**Corrección:** Agregar componente React mínimo viable con Recharts.

```tsx
// client/src/components/SimulatorChart.tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export function SimulatorChart({ histogramData, stats }) {
  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={histogramData}>
          <XAxis dataKey="bin_start" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#4f46e5" />
        </BarChart>
      </ResponsiveContainer>
      <div className="grid grid-cols-4 gap-4 mt-4">
        <StatCard label="P5 (Pessimistic)" value={stats.p5} />
        <StatCard label="Mean" value={stats.mean} />
        <StatCard label="Median" value={stats.median} />
        <StatCard label="P95 (Optimistic)" value={stats.p95} />
      </div>
    </div>
  );
}
```

### C4: Embrión-Financiero debe usar modelos de crecimiento realistas

**Problema:** Crecimiento lineal constante es naive.
**Corrección:** Implementar logistic growth model.

```python
def _logistic_growth(self, t: int, carrying_capacity: int, 
                      growth_rate: float, midpoint: int) -> int:
    """Modelo de crecimiento logístico (curva S)."""
    import math
    return int(carrying_capacity / (1 + math.exp(-growth_rate * (t - midpoint))))
```

### C5: Embrión-Investigador necesita cache de research

**Problema:** Misma investigación se repite sin cache.
**Corrección:** Cache en Supabase con TTL de 24h.

```python
async def deep_research(self, topic: str, depth: str = "standard") -> ResearchReport:
    # Check cache first
    cache_key = f"research:{hashlib.sha256(topic.encode()).hexdigest()[:12]}"
    cached = await self._get_cache(cache_key, ttl_hours=24)
    if cached:
        logger.info("research_cache_hit", topic=topic[:50])
        return ResearchReport(**cached)
    
    # ... do research ...
    
    # Cache result
    await self._set_cache(cache_key, result.__dict__)
    return result
```

### C6: Sensitivity analysis debe usar Spearman, no Pearson

**Problema:** Pearson solo captura relaciones lineales.
**Corrección:** Usar Spearman rank correlation.

```python
from scipy.stats import spearmanr

# En MonteCarloSimulatorV2.simulate()
sensitivities = {}
for factor in factors:
    corr, p_value = spearmanr(factor_samples[factor.name], outcomes)
    sensitivities[factor.name] = {
        "correlation": round(float(corr), 4),
        "p_value": round(float(p_value), 6),
        "significant": p_value < 0.05,
    }
```

### C7: Health checks necesitan métricas, no solo up/down

**Problema:** Binary health check pierde información de degradación.
**Corrección:** Agregar latencia y response time.

```python
async def _check_single(self, dep: ExternalDependency) -> tuple[HealthStatus, dict]:
    """Retorna status + métricas."""
    import time
    start = time.monotonic()
    
    try:
        status = await self._run_check(dep)
        latency_ms = (time.monotonic() - start) * 1000
        
        metrics = {"latency_ms": round(latency_ms, 1), "timestamp": datetime.now(timezone.utc).isoformat()}
        
        # Degrade if latency > 5s
        if latency_ms > 5000 and status == HealthStatus.HEALTHY:
            status = HealthStatus.DEGRADED
            metrics["degradation_reason"] = "high_latency"
        
        return status, metrics
    except Exception as e:
        return HealthStatus.DOWN, {"error": str(e)}
```

### C8: Simulator debe tener n_simulations adaptativo

**Problema:** 10K fijo es arbitrario.
**Corrección:** Adaptar según distribución y convergencia.

```python
def _adaptive_n_simulations(self, factors: list[SimulationFactor]) -> int:
    """Determinar n_simulations basado en complejidad."""
    has_heavy_tails = any(
        f.distribution in (DistributionType.LOGNORMAL, DistributionType.CUSTOM)
        for f in factors
    )
    n_factors = len(factors)
    
    if has_heavy_tails or n_factors > 5:
        return 50_000
    elif n_factors > 3:
        return 20_000
    return 10_000
```

---

## Resumen de Correcciones

| ID | Corrección | Severidad | Épica Afectada |
|---|---|---|---|
| C1 | Sovereignty drills periódicos | ALTA | 60.1 |
| C2 | Generar diffs de requirements.txt (no solo reportes) | MEDIA | 60.2 |
| C3 | UI React con Recharts para simulador | ALTA | 60.3 |
| C4 | Logistic growth model (no lineal) | MEDIA | 60.4 |
| C5 | Cache de research con TTL | MEDIA | 60.5 |
| C6 | Spearman correlation (no Pearson) | MEDIA | 60.3 |
| C7 | Health checks con métricas de latencia | ALTA | 60.1 |
| C8 | n_simulations adaptativo | BAJA | 60.3 |

---

## Veredicto Final del Sprint 60

Sprint 60 como sprint de cierre es **sólido pero con gaps de ejecución.** Los conceptos son correctos — sovereignty, auto-update, simulador maduro, colmena completa — pero la implementación tiene huecos que un sprint de cierre no debería tener.

**Fortalezas:**
- **Obj #11 al 100%** — la colmena de 7 embriones es un milestone real y tangible
- **Sovereignty Engine** es el primer paso serio hacia independencia de SaaS
- **Tech Radar** con datos reales (PyPI, GitHub, OSV.dev) es genuinamente útil
- **Simulator v2** con 6 distribuciones y calibración es un upgrade significativo

**Debilidades:**
- **Simulator UI prometida pero no entregada** — solo backend Python
- **Sovereignty es teórica** — sin drills, sin runbooks probados, sin costos de self-hosting
- **Embrión-Financiero es naive** — crecimiento lineal, sin datos reales, consejo fiscal genérico
- **Embrión-Investigador depende de Perplexity** — sin Perplexity, es solo otro LLM wrapper

**Recomendación:** Implementar C1, C3, C6, y C7 como parte del sprint (son P0). C2, C4, C5, C8 pueden ser Sprint 61.

---

## Estado FINAL de los 13 Objetivos (Post Serie 51-60)

| # | Objetivo | Cobertura Final | Sprints que contribuyen | Status |
|---|---|---|---|---|
| 1 | Crear Empresas Digitales | 85% | 51, 52, 53, 57, 58 | Falta demo E2E |
| 2 | Todo Nivel Apple/Tesla | 65% | 53, 57, 59 | Falta calibración real |
| 3 | Máximo Poder, Mínima Complejidad | 72% | 52, 53, 59, 60 | Falta onboarding |
| 4 | Nunca Se Equivoca Dos Veces | 73% | 53, 54, 58, 60 | Falta error learning |
| 5 | Gasolina Magna vs Premium | 77% | 52, 55, 56, 57, 60 | Bien cubierto |
| 6 | Vanguardia Perpetua | **80%** | 55, 56, **60** | Falta auto-apply |
| 7 | No Inventar la Rueda | 92% | 52, 55-60 | Excelente |
| 8 | Inteligencia Emergente | 70% | 54, 55, 56, 59 | Falta evidencia real |
| 9 | Transversalidad Universal | **100%** | 57, 58 | COMPLETO |
| 10 | Simulador Predictivo | **85%** | 55, 56, **60** | Falta UI frontend |
| 11 | Multiplicación de Embriones | **100%** | 54, 56-60 | **COMPLETO** |
| 12 | Ecosistema / Soberanía | **75%** | 56, **60** | Falta drill real |
| 13 | Del Mundo | 60% | 59 | Falta quality assurance |

### Resumen de la Serie 51-60

**Objetivos completados (100%):** 2 de 13 (#9 Transversalidad, #11 Embriones)
**Objetivos >80%:** 5 de 13 (#1, #6, #7, #10, #11)
**Objetivos >70%:** 10 de 13
**Objetivos <70%:** 3 de 13 (#2 Apple/Tesla 65%, #13 Del Mundo 60%, #8 Emergencia 70%)

**Promedio general:** 77.2%

**Prioridades para Serie 61-70:**
1. Obj #13 (Del Mundo, 60%) — i18n quality assurance, más locales, RTL real
2. Obj #2 (Apple/Tesla, 65%) — calibración real, design system enforcement
3. Obj #8 (Emergencia, 70%) — evidencia demostrable de comportamiento emergente
4. Obj #1 (Empresas, 85%) — demo end-to-end de creación de empresa completa
