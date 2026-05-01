# Cruce Sprint 58 vs 13 Objetivos Maestros — Modo Detractor

**Fecha:** 1 mayo 2026
**Autor:** Manus AI (modo detractor activado)
**Metodología:** Cada objetivo se evalúa como si un inversionista escéptico preguntara: "¿Esto realmente mueve la aguja o es feature creep?"

---

## Matriz de Impacto

| # | Objetivo | Impacto Sprint 58 | Cobertura | Veredicto |
|---|---|---|---|---|
| 1 | Crear Empresas Digitales | ALTO — Capas completan el "paquete empresa" | 85% acumulado | Las 6 capas hacen que cada empresa nazca completa |
| 2 | Todo Nivel Apple/Tesla | MEDIO — Security/Scalability son invisibles al usuario | 60% acumulado | Calidad técnica sí, pero no visual |
| 3 | Máximo Poder, Mínima Complejidad | BAJO — Agrega complejidad interna sin simplificar UX | 40% acumulado | **GAP CRÍTICO** — más poder, misma complejidad |
| 4 | Nunca Se Equivoca Dos Veces | MEDIO — Embrión-Vigía detecta errores, Técnico los previene | 70% acumulado | Detección sí, pero ¿aprende de ellos? |
| 5 | Gasolina Magna vs Premium | BAJO — No toca tier routing ni cost optimization | 75% acumulado | Ya bien cubierto por sprints anteriores |
| 6 | Vanguardia Perpetua | BAJO — No toca auto-update ni trend scanning | 50% acumulado | Dependency audit es reactivo, no proactivo |
| 7 | No Inventar la Rueda | ALTO — Usa Upstash, Sentry, PostHog en vez de custom | 85% acumulado | Excelente adherencia |
| 8 | Inteligencia Emergente | BAJO — Embriones no demuestran emergencia nueva | 55% acumulado | Más embriones ≠ más emergencia |
| 9 | Transversalidad Universal | **COMPLETO** — 6/6 capas terminadas | **100%** | Milestone cumplido |
| 10 | Simulador Predictivo | NULO — No toca Monte Carlo ni predicciones | 65% acumulado | No es scope de este sprint |
| 11 | Multiplicación de Embriones | ALTO — 3/7 embriones creados | 43% acumulado | Buen progreso, faltan 4 |
| 12 | Ecosistema / Soberanía | BAJO — Sentry es SaaS externo (anti-soberanía) | 35% acumulado | Contradicción con soberanía |
| 13 | Del Mundo | NULO — No toca i18n | 0% acumulado | Nunca tocado en 8 sprints |

---

## Análisis Detractor por Épica

### Épica 58.1 — Security Layer

**Lo que funciona:** Genera configs de seguridad automáticamente por tipo de proyecto. OWASP checklist es útil. Auth templates ahorran horas.

**Lo que no funciona:**
1. **Es un generador de templates, no un enforcement engine.** Genera código pero no verifica que se implemente correctamente. Un proyecto podría ignorar las recomendaciones.
2. **CORS "*" para Public APIs es peligroso.** Debería ser configurable con warnings, no default.
3. **No hay penetration testing automatizado.** Genera configs pero nunca las valida con ataques reales.
4. **CSP policy es demasiado permisiva.** `'unsafe-inline'` en scripts es un vector de XSS.

### Épica 58.2 — Scalability Layer

**Lo que funciona:** Recomendaciones automáticas por escala de usuarios. Código de caching generado listo para usar. CDN configs prácticas.

**Lo que no funciona:**
1. **Los thresholds son arbitrarios.** ¿Por qué Redis a 1000 usuarios y no a 500? No hay data que respalde los cortes.
2. **No hay load testing integrado.** Recomienda escalabilidad pero nunca la prueba.
3. **Upstash free tier tiene 10K commands/day.** Para un proyecto real con 1000+ usuarios, se agota en horas. El plan dice "$0" pero en realidad costará $10-25/mes.
4. **Database optimization es solo texto.** Genera recomendaciones pero no implementa indexes ni queries optimizadas.

### Épica 58.3 — Analytics Layer

**Lo que funciona:** Taxonomía estándar de eventos es excelente. Engagement scoring es útil. Retention query SQL es práctica.

**Lo que no funciona:**
1. **PostHog JS SDK en el frontend expone la API key.** Necesita proxy backend o PostHog reverse proxy.
2. **Engagement scoring es simplista.** Pesos lineales (sessions*10 + features*5) no capturan patrones reales de engagement.
3. **No hay privacy compliance.** GDPR/CCPA requieren consent management antes de tracking. El código trackea sin preguntar.
4. **Retention query asume tabla "events" genérica.** No se adapta al schema real del proyecto.

### Épica 58.4 — Embrión-Técnico

**Lo que funciona:** Auditoría de arquitectura con scoring. Detección de secrets en código. Stack recommendations pragmáticas.

**Lo que no funciona:**
1. **Code review sin LLM es superficial.** Regex para secrets y line length no es "review de calidad." Necesita LLM para entender lógica.
2. **No tiene acceso real al código.** Recibe `project_structure: dict` pero ¿quién le pasa eso? No hay integración con el filesystem.
3. **Scoring es subjetivo.** -20 por falta de tests, -30 por .env... ¿basado en qué? No hay calibración contra proyectos reales.
4. **recommend_stack() es estático.** Siempre recomienda lo mismo. No aprende de qué stacks funcionaron mejor.

### Épica 58.5 — Embrión-Vigía

**Lo que funciona:** Health checks con latencia. Anomaly detection con z-score. Incident reports estructurados.

**Lo que no funciona:**
1. **Z-score asume distribución normal.** Métricas de sistemas (latency, error rates) son heavy-tailed, no normales. Debería usar MAD o IQR.
2. **Health checks cada 1 hora es lento.** Para producción real, debería ser cada 30 segundos. 1 hora significa que un outage puede pasar desapercibido 59 minutos.
3. **dependency_audit() solo parsea requirements.txt.** No consulta advisory databases reales (PyPI advisory, GitHub Security Advisories, OSV).
4. **No hay escalación real.** Detecta problemas pero ¿a quién alerta? No hay integración con Slack, email, o PagerDuty.

---

## Correcciones Mandatorias

### C1: Security Layer debe ser enforcement, no solo generation

**Problema:** Genera templates pero no verifica implementación.
**Corrección:** Agregar `verify_security_config(project_path)` que escanea el proyecto real y reporta gaps entre la config generada y lo implementado.

```python
async def verify_security_config(self, project_path: str, config: SecurityConfig) -> dict:
    """Verificar que la config de seguridad está implementada correctamente."""
    gaps = []
    # Scan for CORS middleware
    # Scan for auth implementation
    # Scan for security headers
    # Compare against config
    return {"compliant": len(gaps) == 0, "gaps": gaps}
```

### C2: Analytics Layer debe incluir consent management

**Problema:** Trackea sin consent = violación GDPR/CCPA.
**Corrección:** Agregar `ConsentManager` que genera banner de cookies y condiciona el tracking.

```python
class ConsentManager:
    """Genera consent banner y condiciona tracking a aceptación."""
    
    def generate_consent_banner(self, framework: str = "react") -> str:
        """Generar código de consent banner."""
        ...
    
    def wrap_tracking_with_consent(self, tracking_code: str) -> str:
        """Envolver tracking code con verificación de consent."""
        ...
```

### C3: Embrión-Vigía debe usar MAD en vez de z-score

**Problema:** Z-score asume normalidad, métricas de sistemas no son normales.
**Corrección:** Reemplazar z-score con Median Absolute Deviation (MAD) que es robusto a outliers.

```python
def detect_anomalies_mad(self, metrics: list[dict], threshold: float = 3.5) -> dict:
    """Detectar anomalías usando MAD (robusto a distribuciones no-normales)."""
    values = sorted([m.get("value", 0) for m in metrics])
    median = values[len(values) // 2]
    mad = sorted([abs(v - median) for v in values])[len(values) // 2]
    modified_z_scores = [0.6745 * (v - median) / max(mad, 0.001) for v in [m.get("value", 0) for m in metrics]]
    # Flag where modified z-score > threshold
    ...
```

### C4: Health checks deben ser configurable (no hardcoded 1h)

**Problema:** 1 hora entre health checks es inaceptable para producción.
**Corrección:** Hacer `interval_hours` configurable con mínimo de 1 minuto para endpoints críticos.

```python
DEFAULT_TASKS = {
    "health_check": {
        "interval_hours": float(os.environ.get("VIGIA_HEALTH_INTERVAL_HOURS", "0.083")),  # 5 min default
        ...
    },
}
```

### C5: Scalability Layer debe justificar thresholds con data

**Problema:** Los cortes (100, 1000, 10000) son arbitrarios.
**Corrección:** Agregar docstring con justificación basada en benchmarks conocidos.

```python
# Thresholds basados en benchmarks de la industria:
# - 100 users: Single server handles easily (< 10 RPS)
# - 1000 users: ~50-100 RPS, in-memory cache insufficient for shared state
# - 10000 users: ~500-1000 RPS, single DB becomes bottleneck
# - 100000 users: ~5000-10000 RPS, horizontal scaling mandatory
# - 1000000 users: ~50000+ RPS, sharding + edge caching required
# Source: "Designing Data-Intensive Applications" (Kleppmann, 2017)
```

### C6: Embrión-Técnico debe usar LLM para code review real

**Problema:** Regex-based review es superficial.
**Corrección:** `review_code_quality()` debe tener dos modos: fast (regex) y deep (LLM-powered).

```python
async def review_code_quality(self, code: str, language: str = "python", 
                               mode: str = "fast") -> dict:
    """Review de calidad. mode='fast' usa regex, mode='deep' usa LLM."""
    if mode == "deep" and self._sabios:
        # Use LLM for semantic analysis
        prompt = f"Review this {language} code for quality issues..."
        response = await self._sabios.ask(prompt)
        ...
    else:
        # Fast regex-based check
        ...
```

### C7: Dependency audit debe consultar advisory databases reales

**Problema:** Solo parsea requirements.txt sin consultar CVEs.
**Corrección:** Integrar con PyPI JSON API para verificar versiones y con OSV.dev para CVEs.

```python
async def audit_dependencies_real(self, requirements_txt: str) -> dict:
    """Auditar dependencias contra advisory databases reales."""
    import httpx
    
    async with httpx.AsyncClient() as client:
        for dep in deps:
            # Check PyPI for latest version
            resp = await client.get(f"https://pypi.org/pypi/{dep['package']}/json")
            # Check OSV for vulnerabilities
            resp = await client.post("https://api.osv.dev/v1/query", json={
                "package": {"name": dep["package"], "ecosystem": "PyPI"},
                "version": dep["version"],
            })
```

### C8: Obj #13 (Del Mundo) sigue en 0% — necesita plan de ataque

**Problema:** 8 sprints (51-58) y el Objetivo #13 (internacionalización) nunca ha sido tocado.
**Corrección:** Sprint 59 DEBE incluir al menos una épica de i18n. Propuesta mínima:

- Tabla `supported_locales` en Supabase
- Template de i18n para React (react-intl o next-intl)
- Embrión que traduce automáticamente contenido generado
- Detección de locale del usuario

---

## Resumen de Correcciones

| ID | Corrección | Severidad | Épica Afectada |
|---|---|---|---|
| C1 | Security enforcement (no solo generation) | ALTA | 58.1 |
| C2 | Consent management para GDPR/CCPA | ALTA | 58.3 |
| C3 | MAD en vez de z-score para anomalías | MEDIA | 58.5 |
| C4 | Health checks configurables (min 1 min) | MEDIA | 58.5 |
| C5 | Justificar thresholds con data | BAJA | 58.2 |
| C6 | LLM-powered code review (modo deep) | MEDIA | 58.4 |
| C7 | Advisory databases reales (OSV.dev) | ALTA | 58.5 |
| C8 | Obj #13 necesita plan en Sprint 59 | ALTA | Meta |

---

## Veredicto Final

Sprint 58 es **sólido pero incompleto en enforcement.** Genera mucho código y configuración pero no verifica que se implemente. Es como un arquitecto que dibuja planos perfectos pero nunca visita la obra.

**Fortalezas:**
- Completa Obj #9 (Transversalidad Universal) al 100% — milestone real
- Usa herramientas externas maduras (Obj #7) en vez de reinventar
- Embriones tienen tareas autónomas bien definidas

**Debilidades:**
- Obj #3 (Mínima Complejidad) retrocede — más capas = más complejidad interna
- Obj #12 (Soberanía) contradice con Sentry SaaS
- Obj #13 sigue en 0% después de 8 sprints

**Recomendación:** Implementar C1, C2, y C7 como parte del sprint (son P0). Las demás pueden ser deuda técnica para Sprint 59.
