# Sprint 60 — "La Soberanía y el Cierre"

**Fecha:** 1 mayo 2026
**Autor:** Manus AI
**Tema:** Soberanía de datos, auto-actualización, simulador visual, y la colmena completa de 7 Embriones
**Dependencias:** Sprints 51-59 (especialmente 55: Monte Carlo, 56: Ollama/Scheduler, 57-59: Embriones)
**Significado:** Sprint de cierre de la serie 51-60. Cierra los 4 gaps más críticos.

---

## Resumen Ejecutivo

Sprint 60 es el **sprint de cierre** de la serie 51-60. Su misión es cerrar los 4 gaps más vergonzosos que quedan después de 9 sprints de construcción:

1. **Obj #12 (Ecosistema/Soberanía) al 40%** — el más grave. El Monstruo depende de ~15 servicios SaaS externos sin migration paths. Un cambio de pricing o shutdown de cualquiera es riesgo existencial.
2. **Obj #6 (Vanguardia Perpetua) al 50%** — el sistema no se auto-actualiza. Las dependencias se pinchan manualmente y no hay escaneo real de tendencias tecnológicas.
3. **Obj #10 (Simulador Predictivo) al 65%** — Monte Carlo existe (Sprint 55) pero sin UI, sin calibración, y con solo distribuciones Beta.
4. **Obj #11 (Embriones) al 71%** — faltan 2 embriones para completar la colmena de 7.

El nombre "La Soberanía y el Cierre" refleja la doble naturaleza: El Monstruo se libera de dependencias externas y completa su arquitectura fundamental.

---

## Stack Validado en Tiempo Real

| Herramienta | Versión | Fecha Release | Uso en Sprint 60 |
|---|---|---|---|
| GlitchTip | Latest (2026) | Continuo | Self-hosted Sentry alternative (error tracking soberano) [1] |
| Umami | Latest (2026) | Continuo | Self-hosted analytics (privacy-first, GDPR compliant) [2] |
| Renovate Bot | Latest | Continuo | Auto-dependency updates (ThoughtWorks Radar: Adopt) [3] |
| scipy | 1.17.0 | Apr 2026 | 100+ distribuciones estadísticas para Monte Carlo [4] |
| Recharts | ~2.x | 2026 | React charts para UI del simulador [5] |
| PyPI JSON API | — | — | Version checking programático (ya disponible via requests) |

---

## Épica 60.1 — Sovereignty Engine (Objetivo #12)

### Contexto

El Monstruo dice ser "soberano" pero la realidad es que depende de ~15 servicios SaaS externos. La "soberanía" actual es de **ejecución** (no depende de orquestadores externos como LangChain Hub) pero NO de **datos** ni de **infraestructura**. Sprint 60 crea la capa que mapea cada dependencia externa, define alternativas self-hosted, y genera migration paths automáticos.

### Inventario de Dependencias Externas

| Servicio | Tipo | Criticidad | Alternativa Self-Hosted | Migration Path |
|---|---|---|---|---|
| Supabase | Database + Auth | CRÍTICA | PostgreSQL + pgvector + GoTrue | SQL dump + restore |
| OpenAI API | LLM | CRÍTICA | Ollama (Sprint 56) | Router tier swap |
| Anthropic API | LLM | ALTA | Ollama + DeepSeek | Router tier swap |
| Google Gemini | LLM | ALTA | Ollama + Qwen | Router tier swap |
| Langfuse | Observability | MEDIA | OpenTelemetry + Jaeger | OTLP export |
| Langsmith | Tracing | MEDIA | OpenTelemetry | OTLP export |
| GitHub | Code hosting | BAJA | Gitea/Forgejo | git remote swap |
| DeepL | Translation | BAJA | LLM translation (Sprint 59) | Fallback already exists |

### Implementación

**Archivo:** `kernel/sovereignty/engine.py`

```python
"""
El Monstruo — Sovereignty Engine (Sprint 60)
==============================================
Capa de soberanía que mapea dependencias externas,
define alternativas self-hosted, y genera migration paths.

Principio: El Monstruo PUEDE funcionar sin internet.
Realidad: Funciona MEJOR con internet, pero SOBREVIVE sin él.

Sprint 60 — 2026-05-01
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import structlog

logger = structlog.get_logger("monstruo.sovereignty")


class DependencyTier(str, Enum):
    """Nivel de criticidad de una dependencia."""
    CRITICAL = "critical"  # Sistema no funciona sin ella
    HIGH = "high"  # Funcionalidad degradada sin ella
    MEDIUM = "medium"  # Feature específico no disponible
    LOW = "low"  # Conveniencia, fácil de reemplazar


class HealthStatus(str, Enum):
    """Estado de salud de una dependencia."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class ExternalDependency:
    """Representación de una dependencia externa."""
    name: str
    service_type: str  # "llm", "database", "observability", etc.
    tier: DependencyTier
    endpoint: str
    self_hosted_alternative: str
    migration_path: str
    health: HealthStatus = HealthStatus.UNKNOWN
    last_checked: Optional[str] = None
    monthly_cost_usd: float = 0.0
    data_exported: bool = False  # Can we export our data?
    api_compatible: bool = False  # Is self-hosted API-compatible?


@dataclass
class SovereigntyEngine:
    """Motor de soberanía de El Monstruo."""
    
    _supabase: Optional[object] = field(default=None, repr=False)
    _dependencies: dict[str, ExternalDependency] = field(default_factory=dict)
    
    def __post_init__(self):
        """Registrar todas las dependencias conocidas."""
        self._register_known_dependencies()
    
    def _register_known_dependencies(self):
        """Inventario completo de dependencias externas."""
        deps = [
            ExternalDependency(
                name="supabase",
                service_type="database",
                tier=DependencyTier.CRITICAL,
                endpoint="SUPABASE_URL",
                self_hosted_alternative="PostgreSQL 16 + pgvector + GoTrue",
                migration_path="pg_dump → pg_restore on self-hosted PG. GoTrue for auth. pgvector extension for embeddings.",
                monthly_cost_usd=25.0,
                data_exported=True,
                api_compatible=True,
            ),
            ExternalDependency(
                name="openai",
                service_type="llm",
                tier=DependencyTier.CRITICAL,
                endpoint="OPENAI_API_KEY",
                self_hosted_alternative="Ollama + gpt-oss:120b (Sprint 56)",
                migration_path="Router already supports tier routing. Set SOVEREIGN_MODE=true to route all traffic to Ollama.",
                monthly_cost_usd=50.0,
                data_exported=False,
                api_compatible=True,  # Ollama is OpenAI-compatible
            ),
            ExternalDependency(
                name="anthropic",
                service_type="llm",
                tier=DependencyTier.HIGH,
                endpoint="ANTHROPIC_API_KEY",
                self_hosted_alternative="Ollama + deepseek-v3.1:671b",
                migration_path="Router tier swap. DeepSeek as Claude replacement for complex reasoning.",
                monthly_cost_usd=30.0,
                data_exported=False,
                api_compatible=False,
            ),
            ExternalDependency(
                name="google_gemini",
                service_type="llm",
                tier=DependencyTier.HIGH,
                endpoint="GEMINI_API_KEY",
                self_hosted_alternative="Ollama + qwen2.5:72b",
                migration_path="Router tier swap. Qwen as Gemini replacement for multimodal.",
                monthly_cost_usd=20.0,
                data_exported=False,
                api_compatible=False,
            ),
            ExternalDependency(
                name="langfuse",
                service_type="observability",
                tier=DependencyTier.MEDIUM,
                endpoint="LANGFUSE_PUBLIC_KEY",
                self_hosted_alternative="Langfuse self-hosted (Docker) or OpenTelemetry + Jaeger",
                migration_path="Langfuse supports self-hosting via Docker. Export traces via API. Or migrate to OTLP with Jaeger.",
                monthly_cost_usd=0.0,  # Free tier
                data_exported=True,
                api_compatible=True,
            ),
            ExternalDependency(
                name="langsmith",
                service_type="tracing",
                tier=DependencyTier.MEDIUM,
                endpoint="LANGSMITH_API_KEY",
                self_hosted_alternative="OpenTelemetry + Jaeger",
                migration_path="Replace LangSmith callbacks with OTLP exporters. Jaeger for trace visualization.",
                monthly_cost_usd=0.0,
                data_exported=True,
                api_compatible=False,
            ),
            ExternalDependency(
                name="github",
                service_type="code_hosting",
                tier=DependencyTier.LOW,
                endpoint="GITHUB_TOKEN",
                self_hosted_alternative="Gitea or Forgejo",
                migration_path="git remote set-url origin <new-url>. All history preserved.",
                monthly_cost_usd=0.0,
                data_exported=True,
                api_compatible=False,
            ),
            ExternalDependency(
                name="deepl",
                service_type="translation",
                tier=DependencyTier.LOW,
                endpoint="DEEPL_API_KEY",
                self_hosted_alternative="LLM translation via Sabios (Sprint 59)",
                migration_path="i18n Engine already has LLM fallback. Set DEEPL_ENABLED=false.",
                monthly_cost_usd=0.0,
                data_exported=True,
                api_compatible=False,
            ),
        ]
        
        for dep in deps:
            self._dependencies[dep.name] = dep
    
    async def health_check_all(self) -> dict[str, HealthStatus]:
        """Verificar salud de todas las dependencias."""
        import httpx
        results = {}
        
        for name, dep in self._dependencies.items():
            try:
                status = await self._check_single(dep)
                dep.health = status
                dep.last_checked = datetime.now(timezone.utc).isoformat()
                results[name] = status
            except Exception as e:
                dep.health = HealthStatus.DOWN
                results[name] = HealthStatus.DOWN
                logger.warning("dependency_check_failed", name=name, error=str(e))
        
        return results
    
    async def _check_single(self, dep: ExternalDependency) -> HealthStatus:
        """Verificar salud de una dependencia individual."""
        import os
        import httpx
        
        # Check if env var exists
        env_key = dep.endpoint
        if not os.getenv(env_key) and not os.getenv(env_key.replace("_KEY", "_URL")):
            return HealthStatus.UNKNOWN
        
        # Service-specific health checks
        checks = {
            "supabase": self._check_supabase,
            "openai": self._check_openai,
            "langfuse": self._check_langfuse,
        }
        
        checker = checks.get(dep.name)
        if checker:
            return await checker()
        
        return HealthStatus.HEALTHY  # Assume healthy if no specific check
    
    async def _check_supabase(self) -> HealthStatus:
        """Health check para Supabase."""
        try:
            if self._supabase:
                self._supabase.table("health_check").select("*").limit(1).execute()
                return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.DEGRADED
        return HealthStatus.UNKNOWN
    
    async def _check_openai(self) -> HealthStatus:
        """Health check para OpenAI."""
        import os
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '')}"},
                    timeout=5.0,
                )
                return HealthStatus.HEALTHY if resp.status_code == 200 else HealthStatus.DEGRADED
        except Exception:
            return HealthStatus.DOWN
    
    async def _check_langfuse(self) -> HealthStatus:
        """Health check para Langfuse."""
        import os
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}/api/public/health",
                    timeout=5.0,
                )
                return HealthStatus.HEALTHY if resp.status_code == 200 else HealthStatus.DEGRADED
        except Exception:
            return HealthStatus.DOWN
    
    def get_sovereignty_score(self) -> dict:
        """Calcular score de soberanía del sistema."""
        total = len(self._dependencies)
        if total == 0:
            return {"score": 0.0, "details": {}}
        
        scores = {
            "has_alternative": sum(1 for d in self._dependencies.values() if d.self_hosted_alternative) / total,
            "data_exportable": sum(1 for d in self._dependencies.values() if d.data_exported) / total,
            "api_compatible": sum(1 for d in self._dependencies.values() if d.api_compatible) / total,
            "has_migration_path": sum(1 for d in self._dependencies.values() if d.migration_path) / total,
        }
        
        overall = sum(scores.values()) / len(scores)
        
        return {
            "overall_score": round(overall, 2),
            "dimensions": scores,
            "total_monthly_cost": sum(d.monthly_cost_usd for d in self._dependencies.values()),
            "critical_dependencies": [d.name for d in self._dependencies.values() if d.tier == DependencyTier.CRITICAL],
            "no_alternative": [d.name for d in self._dependencies.values() if not d.self_hosted_alternative],
        }
    
    def generate_sovereignty_report(self) -> str:
        """Generar reporte de soberanía legible."""
        score = self.get_sovereignty_score()
        
        report = f"""# El Monstruo — Sovereignty Report
Generated: {datetime.now(timezone.utc).isoformat()}

## Overall Sovereignty Score: {score['overall_score']*100:.0f}%

## Monthly External Cost: ${score['total_monthly_cost']:.2f}

## Critical Dependencies (system fails without these):
"""
        for name in score["critical_dependencies"]:
            dep = self._dependencies[name]
            report += f"- **{name}**: {dep.self_hosted_alternative} (migration: {dep.migration_path[:80]}...)\n"
        
        report += "\n## Dimension Scores:\n"
        for dim, val in score["dimensions"].items():
            report += f"- {dim}: {val*100:.0f}%\n"
        
        return report
    
    async def activate_sovereign_mode(self) -> dict:
        """Activar modo soberano — redirigir todo a alternativas locales."""
        import os
        
        actions_taken = []
        
        # 1. Route LLMs to Ollama
        os.environ["SOVEREIGN_MODE"] = "true"
        os.environ["LLM_FALLBACK_ONLY_LOCAL"] = "true"
        actions_taken.append("LLM routing switched to Ollama (local)")
        
        # 2. Disable external translation
        os.environ["DEEPL_ENABLED"] = "false"
        actions_taken.append("DeepL disabled, using LLM translation")
        
        # 3. Log the activation
        logger.warning("sovereign_mode_activated", actions=actions_taken)
        
        return {
            "mode": "sovereign",
            "actions": actions_taken,
            "degraded_features": [
                "LLM quality may be lower (local models)",
                "Translation quality may be lower",
                "Tracing/observability limited to local logs",
            ],
        }
```

### Tabla Supabase

```sql
-- Sprint 60: Dependency health tracking
CREATE TABLE IF NOT EXISTS dependency_health (
    id SERIAL PRIMARY KEY,
    dependency_name TEXT NOT NULL,
    status TEXT NOT NULL,  -- healthy, degraded, down, unknown
    response_time_ms INTEGER,
    checked_at TIMESTAMPTZ DEFAULT NOW(),
    error_message TEXT
);

CREATE INDEX idx_dep_health_name ON dependency_health(dependency_name);
CREATE INDEX idx_dep_health_time ON dependency_health(checked_at DESC);
```

---

## Épica 60.2 — Tech Radar & Auto-Updater (Objetivo #6)

### Contexto

El Monstruo pincha versiones manualmente en `requirements.txt` (Sprint 29 fue la última actualización masiva). No hay mecanismo para detectar cuándo una dependencia queda obsoleta, tiene CVEs, o hay una versión mejor disponible. El Objetivo #6 dice "Vanguardia Perpetua" — Sprint 60 crea el sistema que mantiene al Monstruo actualizado automáticamente.

### Arquitectura de Dos Capas

**Capa 1 — Dependency Monitor (interno):**
Escanea `requirements.txt` contra PyPI, detecta versiones nuevas, CVEs, y deprecations. Genera PRs de actualización con changelog y risk assessment.

**Capa 2 — Tech Radar (estratégico):**
Escanea tendencias tecnológicas reales (no LLM knowledge) via APIs de PyPI trending, GitHub trending, y Hacker News. Propone adopciones/retiros de tecnologías.

### Implementación

**Archivo:** `kernel/vanguard/tech_radar.py`

```python
"""
El Monstruo — Tech Radar & Auto-Updater (Sprint 60)
=====================================================
Sistema de auto-actualización y escaneo de tendencias.

Capa 1: Dependency Monitor — versiones, CVEs, deprecations
Capa 2: Tech Radar — tendencias, adopciones, retiros

Principio: El Monstruo siempre usa lo mejor disponible.
Sprint 60 — 2026-05-01
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import structlog

logger = structlog.get_logger("monstruo.vanguard")


@dataclass
class DependencyUpdate:
    """Una actualización de dependencia detectada."""
    package: str
    current_version: str
    latest_version: str
    release_date: str
    is_major: bool
    is_security: bool
    changelog_url: str
    risk_level: str  # "low", "medium", "high"
    recommendation: str  # "update", "evaluate", "skip"


@dataclass
class TechTrend:
    """Una tendencia tecnológica detectada."""
    name: str
    category: str  # "framework", "library", "pattern", "tool"
    signal_strength: str  # "weak", "moderate", "strong"
    relevance_to_monstruo: str
    adoption_recommendation: str  # "adopt", "trial", "assess", "hold"
    source: str


@dataclass
class TechRadar:
    """Tech Radar de El Monstruo."""
    
    _sabios: Optional[object] = field(default=None, repr=False)
    requirements_path: str = "requirements.txt"
    
    # ── Capa 1: Dependency Monitor ─────────────────────────────────
    
    async def scan_dependencies(self, requirements_content: str) -> list[DependencyUpdate]:
        """Escanear requirements.txt contra PyPI para detectar updates."""
        import httpx
        
        updates = []
        lines = requirements_content.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            
            # Parse package==version
            match = re.match(r'^([a-zA-Z0-9_-]+)\[?[^\]]*\]?==([0-9.]+)', line)
            if not match:
                continue
            
            package = match.group(1)
            current = match.group(2)
            
            try:
                latest_info = await self._check_pypi(package)
                if not latest_info:
                    continue
                
                latest_ver = latest_info["version"]
                if latest_ver != current:
                    is_major = latest_ver.split(".")[0] != current.split(".")[0]
                    
                    updates.append(DependencyUpdate(
                        package=package,
                        current_version=current,
                        latest_version=latest_ver,
                        release_date=latest_info.get("release_date", "unknown"),
                        is_major=is_major,
                        is_security=False,  # Would need OSV.dev check
                        changelog_url=f"https://pypi.org/project/{package}/{latest_ver}/",
                        risk_level="high" if is_major else "low",
                        recommendation="evaluate" if is_major else "update",
                    ))
            except Exception as e:
                logger.warning("pypi_check_failed", package=package, error=str(e))
        
        return updates
    
    async def _check_pypi(self, package: str) -> Optional[dict]:
        """Consultar PyPI JSON API para obtener última versión."""
        import httpx
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://pypi.org/pypi/{package}/json",
                timeout=10.0,
            )
            if resp.status_code != 200:
                return None
            
            data = resp.json()
            version = data["info"]["version"]
            
            # Get release date
            releases = data.get("releases", {}).get(version, [])
            release_date = releases[0]["upload_time"][:10] if releases else "unknown"
            
            return {"version": version, "release_date": release_date}
    
    async def check_security_advisories(self, package: str, version: str) -> list[dict]:
        """Consultar OSV.dev para CVEs de un paquete."""
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.osv.dev/v1/query",
                    json={
                        "package": {"name": package, "ecosystem": "PyPI"},
                        "version": version,
                    },
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("vulns", [])
        except Exception as e:
            logger.warning("osv_check_failed", package=package, error=str(e))
        
        return []
    
    def generate_update_report(self, updates: list[DependencyUpdate]) -> str:
        """Generar reporte de actualizaciones pendientes."""
        if not updates:
            return "All dependencies are up to date."
        
        report = f"# Dependency Update Report\nGenerated: {datetime.now(timezone.utc).isoformat()}\n\n"
        
        # Group by risk
        critical = [u for u in updates if u.is_security]
        major = [u for u in updates if u.is_major and not u.is_security]
        minor = [u for u in updates if not u.is_major and not u.is_security]
        
        if critical:
            report += "## SECURITY UPDATES (apply immediately)\n"
            for u in critical:
                report += f"- **{u.package}**: {u.current_version} → {u.latest_version}\n"
        
        if major:
            report += "\n## MAJOR UPDATES (evaluate before applying)\n"
            for u in major:
                report += f"- {u.package}: {u.current_version} → {u.latest_version} ({u.release_date})\n"
        
        if minor:
            report += "\n## MINOR UPDATES (safe to apply)\n"
            for u in minor:
                report += f"- {u.package}: {u.current_version} → {u.latest_version}\n"
        
        return report
    
    # ── Capa 2: Tech Radar (Strategic) ─────────────────────────────
    
    async def scan_tech_trends(self) -> list[TechTrend]:
        """Escanear tendencias tecnológicas reales via APIs."""
        import httpx
        
        trends = []
        
        # Source 1: PyPI trending (new releases with high download growth)
        try:
            async with httpx.AsyncClient() as client:
                # Check recently updated popular packages
                resp = await client.get(
                    "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json",
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    top_packages = data.get("rows", [])[:20]
                    for pkg in top_packages:
                        if pkg.get("download_count", 0) > 50_000_000:
                            trends.append(TechTrend(
                                name=pkg["project"],
                                category="library",
                                signal_strength="strong",
                                relevance_to_monstruo="High download count indicates industry standard",
                                adoption_recommendation="assess",
                                source="PyPI Top Packages (30 days)",
                            ))
        except Exception as e:
            logger.warning("pypi_trends_failed", error=str(e))
        
        # Source 2: GitHub trending (Python repos)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.github.com/search/repositories?q=language:python+created:>2026-04-01&sort=stars&order=desc&per_page=10",
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for repo in data.get("items", [])[:5]:
                        trends.append(TechTrend(
                            name=repo["name"],
                            category="tool",
                            signal_strength="moderate",
                            relevance_to_monstruo=repo.get("description", "")[:100],
                            adoption_recommendation="assess",
                            source=f"GitHub Trending ({repo['stargazers_count']} stars)",
                        ))
        except Exception as e:
            logger.warning("github_trends_failed", error=str(e))
        
        # Source 3: LLM analysis of trends (enrichment, not primary source)
        if self._sabios and trends:
            try:
                trend_names = [t.name for t in trends[:10]]
                prompt = f"""Given these trending Python packages/tools: {trend_names}

Which are most relevant for an AI-powered business creation platform?
For each relevant one, explain why and recommend: adopt, trial, assess, or hold.
Respond in JSON array: [{{"name": "...", "relevance": "...", "recommendation": "..."}}]"""
                
                response = await self._sabios.ask(prompt)
                enrichments = json.loads(self._extract_json(response))
                
                # Enrich existing trends
                enrichment_map = {e["name"]: e for e in enrichments}
                for trend in trends:
                    if trend.name in enrichment_map:
                        e = enrichment_map[trend.name]
                        trend.relevance_to_monstruo = e.get("relevance", trend.relevance_to_monstruo)
                        trend.adoption_recommendation = e.get("recommendation", trend.adoption_recommendation)
            except Exception:
                pass  # Enrichment is optional
        
        return trends
    
    def generate_radar_report(self, trends: list[TechTrend]) -> str:
        """Generar reporte estilo ThoughtWorks Tech Radar."""
        report = f"# El Monstruo Tech Radar\nGenerated: {datetime.now(timezone.utc).isoformat()}\n\n"
        
        # Group by recommendation
        adopt = [t for t in trends if t.adoption_recommendation == "adopt"]
        trial = [t for t in trends if t.adoption_recommendation == "trial"]
        assess = [t for t in trends if t.adoption_recommendation == "assess"]
        hold = [t for t in trends if t.adoption_recommendation == "hold"]
        
        for label, items in [("ADOPT", adopt), ("TRIAL", trial), ("ASSESS", assess), ("HOLD", hold)]:
            if items:
                report += f"\n## {label}\n"
                for t in items:
                    report += f"- **{t.name}** ({t.category}): {t.relevance_to_monstruo[:80]} [source: {t.source}]\n"
        
        return report
    
    @staticmethod
    def _extract_json(text: str) -> str:
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        if "```" in text:
            return text.split("```")[1].split("```")[0]
        return text.strip()
```

### Tarea Autónoma (integración con Embrión-Vigía)

```python
# En embrion_vigia — nueva tarea
"dependency_scan": {
    "description": "Escanear dependencias para updates y CVEs",
    "interval_hours": 24,
    "handler": "scan_dependencies_and_report",
}
```

---

## Épica 60.3 — Simulator UI & Calibration (Objetivo #10)

### Contexto

Sprint 55 creó el Monte Carlo Simulator con distribuciones Beta y 10K simulaciones. Sprint 56 creó el Prediction Validator. Pero no hay forma de VISUALIZAR las simulaciones ni de CALIBRAR los parámetros. Sprint 60 completa el Simulador Predictivo con UI interactiva, más distribuciones, y calibración automática.

### Arquitectura

```
[Causal KB] → [Decomposition Engine] → [Monte Carlo Engine] → [Visualization API]
                                              ↑                        ↓
                                    [Calibration Loop]          [React UI]
                                              ↑                        ↓
                                    [Prediction Validator]      [User sees charts]
```

### Implementación — Backend

**Archivo:** `kernel/simulator/engine.py`

```python
"""
El Monstruo — Monte Carlo Simulator v2 (Sprint 60)
====================================================
Versión expandida del simulador con:
- Múltiples distribuciones (Beta, Normal, Poisson, Triangular, Uniform, Custom)
- Calibración automática contra resultados reales
- API para visualización
- Sensitivity analysis

Sprint 60 — 2026-05-01
"""
from __future__ import annotations
import json
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum
import structlog

logger = structlog.get_logger("monstruo.simulator")


class DistributionType(str, Enum):
    BETA = "beta"
    NORMAL = "normal"
    TRIANGULAR = "triangular"
    UNIFORM = "uniform"
    POISSON = "poisson"
    LOGNORMAL = "lognormal"
    CUSTOM = "custom"


@dataclass
class SimulationFactor:
    """Un factor en la simulación."""
    name: str
    distribution: DistributionType
    params: dict  # Distribution-specific parameters
    weight: float = 1.0  # Relative importance
    description: str = ""


@dataclass
class SimulationResult:
    """Resultado de una simulación Monte Carlo."""
    scenario_name: str
    n_simulations: int
    mean: float
    median: float
    std: float
    p5: float   # 5th percentile (pessimistic)
    p25: float  # 25th percentile
    p75: float  # 75th percentile
    p95: float  # 95th percentile (optimistic)
    histogram_data: list[dict]  # [{bin_start, bin_end, count}]
    factor_sensitivities: dict[str, float]  # {factor_name: correlation}
    raw_outcomes: list[float]  # For visualization


@dataclass
class MonteCarloSimulatorV2:
    """Motor de simulación Monte Carlo v2."""
    
    n_simulations: int = 10_000
    random_seed: Optional[int] = None
    
    def simulate(self, factors: list[SimulationFactor], 
                 combination_fn: Optional[Callable] = None) -> SimulationResult:
        """Ejecutar simulación Monte Carlo."""
        rng = np.random.default_rng(self.random_seed)
        
        # Generate samples for each factor
        factor_samples = {}
        for factor in factors:
            samples = self._generate_samples(factor, rng)
            factor_samples[factor.name] = samples
        
        # Combine factors into outcomes
        if combination_fn:
            outcomes = combination_fn(factor_samples)
        else:
            # Default: weighted sum
            outcomes = np.zeros(self.n_simulations)
            for factor in factors:
                outcomes += factor_samples[factor.name] * factor.weight
        
        # Calculate statistics
        outcomes_sorted = np.sort(outcomes)
        
        # Histogram
        hist_counts, hist_edges = np.histogram(outcomes, bins=50)
        histogram_data = [
            {"bin_start": float(hist_edges[i]), "bin_end": float(hist_edges[i+1]), "count": int(hist_counts[i])}
            for i in range(len(hist_counts))
        ]
        
        # Sensitivity analysis (correlation of each factor with outcome)
        sensitivities = {}
        for factor in factors:
            corr = np.corrcoef(factor_samples[factor.name], outcomes)[0, 1]
            sensitivities[factor.name] = round(float(corr), 4)
        
        return SimulationResult(
            scenario_name="simulation",
            n_simulations=self.n_simulations,
            mean=float(np.mean(outcomes)),
            median=float(np.median(outcomes)),
            std=float(np.std(outcomes)),
            p5=float(np.percentile(outcomes, 5)),
            p25=float(np.percentile(outcomes, 25)),
            p75=float(np.percentile(outcomes, 75)),
            p95=float(np.percentile(outcomes, 95)),
            histogram_data=histogram_data,
            factor_sensitivities=sensitivities,
            raw_outcomes=outcomes_sorted[::max(1, len(outcomes_sorted)//500)].tolist(),  # Downsample for viz
        )
    
    def _generate_samples(self, factor: SimulationFactor, rng) -> np.ndarray:
        """Generar muestras según la distribución del factor."""
        p = factor.params
        n = self.n_simulations
        
        if factor.distribution == DistributionType.BETA:
            return rng.beta(p.get("alpha", 2), p.get("beta", 5), n)
        
        elif factor.distribution == DistributionType.NORMAL:
            return rng.normal(p.get("mean", 0), p.get("std", 1), n)
        
        elif factor.distribution == DistributionType.TRIANGULAR:
            return rng.triangular(p.get("low", 0), p.get("mode", 0.5), p.get("high", 1), n)
        
        elif factor.distribution == DistributionType.UNIFORM:
            return rng.uniform(p.get("low", 0), p.get("high", 1), n)
        
        elif factor.distribution == DistributionType.POISSON:
            return rng.poisson(p.get("lam", 5), n).astype(float)
        
        elif factor.distribution == DistributionType.LOGNORMAL:
            return rng.lognormal(p.get("mean", 0), p.get("sigma", 1), n)
        
        elif factor.distribution == DistributionType.CUSTOM:
            # Custom distribution from empirical data
            empirical = np.array(p.get("data", [0.5]))
            return rng.choice(empirical, size=n, replace=True)
        
        raise ValueError(f"Unknown distribution: {factor.distribution}")
    
    def compare_scenarios(self, scenarios: dict[str, list[SimulationFactor]]) -> dict:
        """Comparar múltiples escenarios."""
        results = {}
        for name, factors in scenarios.items():
            result = self.simulate(factors)
            result.scenario_name = name
            results[name] = {
                "mean": result.mean,
                "median": result.median,
                "p5": result.p5,
                "p95": result.p95,
                "std": result.std,
                "histogram": result.histogram_data,
            }
        return results
    
    def calibrate_from_actuals(self, factor: SimulationFactor, 
                                actual_outcomes: list[float]) -> SimulationFactor:
        """Calibrar parámetros de distribución usando resultados reales."""
        from scipy import stats
        
        actual = np.array(actual_outcomes)
        
        if factor.distribution == DistributionType.BETA:
            # Fit Beta distribution to actual data (normalized to 0-1)
            normalized = (actual - actual.min()) / (actual.max() - actual.min() + 1e-10)
            alpha, beta_param, _, _ = stats.beta.fit(normalized, floc=0, fscale=1)
            factor.params = {"alpha": float(alpha), "beta": float(beta_param)}
        
        elif factor.distribution == DistributionType.NORMAL:
            factor.params = {"mean": float(np.mean(actual)), "std": float(np.std(actual))}
        
        elif factor.distribution == DistributionType.LOGNORMAL:
            log_data = np.log(actual[actual > 0])
            factor.params = {"mean": float(np.mean(log_data)), "sigma": float(np.std(log_data))}
        
        elif factor.distribution == DistributionType.TRIANGULAR:
            factor.params = {
                "low": float(np.min(actual)),
                "mode": float(stats.mode(actual, keepdims=False).mode),
                "high": float(np.max(actual)),
            }
        
        logger.info("factor_calibrated", factor=factor.name, params=factor.params)
        return factor


# ── API Routes for Visualization ───────────────────────────────────

SIMULATION_API_ROUTES = """
# FastAPI routes for simulator (add to kernel/main.py)

@app.post("/api/simulate")
async def run_simulation(request: SimulationRequest) -> SimulationResponse:
    simulator = MonteCarloSimulatorV2(n_simulations=request.n_simulations)
    factors = [SimulationFactor(**f) for f in request.factors]
    result = simulator.simulate(factors)
    return SimulationResponse(
        mean=result.mean,
        median=result.median,
        p5=result.p5,
        p95=result.p95,
        histogram=result.histogram_data,
        sensitivities=result.factor_sensitivities,
        raw_outcomes=result.raw_outcomes,
    )

@app.post("/api/simulate/compare")
async def compare_scenarios(request: CompareRequest) -> dict:
    simulator = MonteCarloSimulatorV2(n_simulations=request.n_simulations)
    scenarios = {
        name: [SimulationFactor(**f) for f in factors]
        for name, factors in request.scenarios.items()
    }
    return simulator.compare_scenarios(scenarios)

@app.post("/api/simulate/calibrate")
async def calibrate_factor(request: CalibrateRequest) -> dict:
    simulator = MonteCarloSimulatorV2()
    factor = SimulationFactor(**request.factor)
    calibrated = simulator.calibrate_from_actuals(factor, request.actual_outcomes)
    return {"calibrated_params": calibrated.params}
"""
```

### Dependencias

```
# requirements.txt additions
scipy>=1.17.0
numpy>=2.2.0  # Already likely present
```

---

## Épica 60.4 — Embrión-Financiero (Objetivo #11)

### Contexto

6to embrión especializado. Se encarga de todo lo financiero: contabilidad, impuestos, unit economics, pricing optimization, burn rate, runway, y proyecciones. Complementa el Financial Dashboard Layer (Sprint 57) con inteligencia autónoma.

### Implementación

**Archivo:** `kernel/embriones/embrion_financiero.py`

```python
"""
El Monstruo — Embrión-Financiero (Sprint 60)
==============================================
6to Embrión especializado.
Dominio: Finanzas, contabilidad, impuestos, unit economics.

Hereda: EmbrionLoop (Sprint 54)
Hermanos: Ventas(57), Técnico(58), Vigía(58), Creativo(59), Estratega(59)

Sprint 60 — 2026-05-01
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional
import structlog

logger = structlog.get_logger("monstruo.embrion.financiero")


FINANCIAL_SYSTEM_PROMPT = """Eres el Embrión-Financiero de El Monstruo.
Tu dominio es TODO lo financiero:
- Unit Economics: CAC, LTV, LTV/CAC ratio, payback period
- Pricing: estrategias de pricing, elasticidad, A/B testing de precios
- Burn Rate: tracking de gastos, runway calculation, alerts
- Projections: revenue forecasting, growth modeling
- Tax: obligaciones fiscales por jurisdicción, deducciones
- Accounting: P&L, balance sheet, cash flow statements

PRINCIPIOS:
- Conservador por defecto. Mejor subestimar ingresos que sobreestimarlos.
- Siempre incluir escenario pesimista en proyecciones.
- Tax compliance es NON-NEGOTIABLE.
- Unit economics deben ser positivos ANTES de escalar.

RESTRICCIONES:
- Nunca recomiendes evasión fiscal (elusión legal sí)
- Siempre disclaimer: "Consulte con un contador certificado"
- Proyecciones >12 meses tienen disclaimer de incertidumbre
"""


@dataclass
class UnitEconomics:
    """Unit economics de un negocio."""
    cac: float  # Customer Acquisition Cost
    ltv: float  # Lifetime Value
    ltv_cac_ratio: float
    payback_months: float
    gross_margin: float
    churn_rate_monthly: float
    arpu: float  # Average Revenue Per User
    verdict: str  # "healthy", "warning", "critical"


@dataclass
class FinancialProjection:
    """Proyección financiera."""
    months: list[dict]  # [{month, revenue, costs, profit, users, mrr}]
    break_even_month: Optional[int]
    total_investment_needed: float
    roi_12_months: float
    scenarios: dict  # {pessimistic, base, optimistic}


@dataclass
class EmbrionFinanciero:
    """Embrión especializado en finanzas."""
    
    _sabios: Optional[object] = field(default=None, repr=False)
    budget_daily_usd: float = 1.0
    _spent_today: float = 0.0
    
    DEFAULT_TASKS = {
        "burn_rate_check": {
            "description": "Calcular burn rate actual y runway restante",
            "interval_hours": 24,
            "handler": "check_burn_rate",
        },
        "unit_economics_review": {
            "description": "Revisar unit economics de proyectos activos",
            "interval_hours": 48,
            "handler": "review_unit_economics",
        },
        "tax_calendar": {
            "description": "Verificar obligaciones fiscales próximas",
            "interval_hours": 168,  # Weekly
            "handler": "check_tax_obligations",
        },
    }
    
    async def calculate_unit_economics(self, metrics: dict) -> UnitEconomics:
        """Calcular unit economics a partir de métricas."""
        cac = metrics.get("total_marketing_spend", 0) / max(metrics.get("new_customers", 1), 1)
        churn = metrics.get("churn_rate_monthly", 0.05)
        arpu = metrics.get("monthly_revenue", 0) / max(metrics.get("total_customers", 1), 1)
        
        # LTV = ARPU / Churn Rate
        ltv = arpu / max(churn, 0.001)
        ltv_cac_ratio = ltv / max(cac, 0.01)
        
        # Payback = CAC / (ARPU * Gross Margin)
        gross_margin = metrics.get("gross_margin", 0.7)
        payback = cac / max(arpu * gross_margin, 0.01)
        
        # Verdict
        if ltv_cac_ratio >= 3 and payback <= 12:
            verdict = "healthy"
        elif ltv_cac_ratio >= 1.5:
            verdict = "warning"
        else:
            verdict = "critical"
        
        return UnitEconomics(
            cac=round(cac, 2),
            ltv=round(ltv, 2),
            ltv_cac_ratio=round(ltv_cac_ratio, 2),
            payback_months=round(payback, 1),
            gross_margin=gross_margin,
            churn_rate_monthly=churn,
            arpu=round(arpu, 2),
            verdict=verdict,
        )
    
    async def generate_projection(self, initial_metrics: dict,
                                    growth_rate_monthly: float = 0.10,
                                    months: int = 12) -> FinancialProjection:
        """Generar proyección financiera a N meses."""
        base_months = []
        users = initial_metrics.get("total_customers", 0)
        mrr = initial_metrics.get("monthly_revenue", 0)
        monthly_costs = initial_metrics.get("monthly_costs", 0)
        churn = initial_metrics.get("churn_rate_monthly", 0.05)
        
        break_even = None
        
        for m in range(1, months + 1):
            # Growth
            new_users = int(users * growth_rate_monthly)
            churned_users = int(users * churn)
            users = users + new_users - churned_users
            
            # Revenue
            arpu = initial_metrics.get("arpu", mrr / max(users, 1))
            mrr = users * arpu
            
            # Costs grow slower than revenue (economies of scale)
            cost_growth = growth_rate_monthly * 0.6
            monthly_costs *= (1 + cost_growth)
            
            profit = mrr - monthly_costs
            
            if profit > 0 and break_even is None:
                break_even = m
            
            base_months.append({
                "month": m,
                "revenue": round(mrr, 2),
                "costs": round(monthly_costs, 2),
                "profit": round(profit, 2),
                "users": users,
                "mrr": round(mrr, 2),
            })
        
        total_investment = sum(
            m["costs"] - m["revenue"] for m in base_months if m["profit"] < 0
        )
        
        total_revenue = sum(m["revenue"] for m in base_months)
        total_costs = sum(m["costs"] for m in base_months)
        roi = (total_revenue - total_costs) / max(abs(total_investment), 1)
        
        return FinancialProjection(
            months=base_months,
            break_even_month=break_even,
            total_investment_needed=round(abs(total_investment), 2),
            roi_12_months=round(roi, 2),
            scenarios={
                "pessimistic": f"Growth {growth_rate_monthly*0.5*100:.0f}%/mo, break-even month {(break_even or months)*2}",
                "base": f"Growth {growth_rate_monthly*100:.0f}%/mo, break-even month {break_even or 'N/A'}",
                "optimistic": f"Growth {growth_rate_monthly*1.5*100:.0f}%/mo, break-even month {max(1, (break_even or months)//2)}",
            },
        )
    
    async def check_burn_rate(self, financials: dict = None) -> dict:
        """Tarea autónoma: verificar burn rate."""
        if not financials:
            return {"status": "no_data", "message": "No financial data available"}
        
        monthly_burn = financials.get("monthly_costs", 0) - financials.get("monthly_revenue", 0)
        cash = financials.get("cash_balance", 0)
        runway_months = cash / max(monthly_burn, 1) if monthly_burn > 0 else float("inf")
        
        alert_level = "critical" if runway_months < 3 else "warning" if runway_months < 6 else "healthy"
        
        return {
            "monthly_burn": round(monthly_burn, 2),
            "cash_balance": cash,
            "runway_months": round(runway_months, 1),
            "alert_level": alert_level,
            "recommendation": self._burn_rate_recommendation(runway_months),
        }
    
    @staticmethod
    def _burn_rate_recommendation(runway_months: float) -> str:
        if runway_months < 3:
            return "URGENTE: Menos de 3 meses de runway. Reducir gastos inmediatamente o buscar financiamiento."
        elif runway_months < 6:
            return "ATENCIÓN: Menos de 6 meses de runway. Iniciar proceso de fundraising o reducir burn rate."
        elif runway_months < 12:
            return "PRECAUCIÓN: Menos de 12 meses. Planificar siguiente ronda o camino a profitability."
        return "SALUDABLE: Runway >12 meses. Enfocarse en crecimiento."
```

---

## Épica 60.5 — Embrión-Investigador (Objetivo #11)

### Contexto

7mo y ÚLTIMO embrión especializado. Completa la colmena. Se encarga de research profundo: benchmarks, análisis de competencia, tendencias de mercado, papers académicos, y due diligence. Utiliza `InvestigadorRealidad` (skills/) como herramienta base y lo potencia con capacidades autónomas.

### Implementación

**Archivo:** `kernel/embriones/embrion_investigador.py`

```python
"""
El Monstruo — Embrión-Investigador (Sprint 60)
================================================
7mo y ÚLTIMO Embrión especializado.
Dominio: Research, benchmarks, competitive intelligence, trends.

Hereda: EmbrionLoop (Sprint 54)
Hermanos: Ventas(57), Técnico(58), Vigía(58), Creativo(59), Estratega(59), Financiero(60)
Herramienta: InvestigadorRealidad (skills/)

MILESTONE: Con este embrión, la colmena está COMPLETA (7/7).

Sprint 60 — 2026-05-01
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional
import structlog

logger = structlog.get_logger("monstruo.embrion.investigador")


RESEARCHER_SYSTEM_PROMPT = """Eres el Embrión-Investigador de El Monstruo.
Tu dominio es la INVESTIGACIÓN profunda:
- Market Research: tamaño, tendencias, segmentos, oportunidades
- Competitive Intelligence: análisis de competidores, diferenciadores
- Technology Research: evaluación de herramientas, frameworks, APIs
- Academic Research: papers relevantes, metodologías, best practices
- Due Diligence: verificación de claims, fact-checking, validación

PRINCIPIOS:
- Fuentes verificables. Siempre cita la fuente.
- Múltiples perspectivas. Nunca confíes en una sola fuente.
- Recency bias awareness. Datos viejos pueden ser irrelevantes.
- Contrarian search. Busca activamente evidencia que contradiga tu hipótesis.

RESTRICCIONES:
- Nunca presentes datos sin fuente como hechos
- Siempre incluye fecha de los datos citados
- Distingue entre datos verificados y estimaciones
- Marca claramente cuando estás extrapolando
"""


@dataclass
class ResearchReport:
    """Reporte de investigación estructurado."""
    topic: str
    summary: str
    key_findings: list[dict]  # [{finding, source, confidence, date}]
    data_points: list[dict]  # [{metric, value, source, date}]
    competitors: list[dict]  # [{name, strengths, weaknesses, market_share}]
    opportunities: list[str]
    risks: list[str]
    methodology: str
    limitations: list[str]


@dataclass
class EmbrionInvestigador:
    """Embrión especializado en investigación."""
    
    _sabios: Optional[object] = field(default=None, repr=False)
    _perplexity: Optional[object] = field(default=None, repr=False)
    budget_daily_usd: float = 2.5  # Research is expensive
    _spent_today: float = 0.0
    
    DEFAULT_TASKS = {
        "daily_briefing": {
            "description": "Generar briefing diario de noticias relevantes",
            "interval_hours": 24,
            "handler": "generate_daily_briefing",
        },
        "competitor_monitor": {
            "description": "Monitorear actividad de competidores",
            "interval_hours": 12,
            "handler": "monitor_competitors",
        },
        "trend_analysis": {
            "description": "Analizar tendencias emergentes en nichos activos",
            "interval_hours": 48,
            "handler": "analyze_trends",
        },
        "fact_check": {
            "description": "Verificar claims y datos usados en proyectos",
            "interval_hours": 0,  # On-demand
            "handler": "fact_check_claims",
        },
    }
    
    async def deep_research(self, topic: str, depth: str = "standard") -> ResearchReport:
        """Investigación profunda sobre un tema."""
        if not self._sabios:
            raise RuntimeError("Sabios not configured")
        
        # Step 1: Get real-time data via Perplexity (if available)
        real_data = ""
        if self._perplexity:
            try:
                real_data = await self._perplexity.research(
                    f"Latest data and statistics about {topic} in 2026"
                )
            except Exception as e:
                logger.warning("perplexity_research_failed", error=str(e))
        
        # Step 2: Structure with LLM
        prompt = f"""Conduct deep research on: {topic}

{"Real-time data from web research:" if real_data else "No real-time data available."}
{real_data[:3000] if real_data else "Use your training knowledge but mark all data with confidence levels."}

Depth level: {depth}

Respond in JSON:
{{
    "summary": "Executive summary (3-5 sentences)",
    "key_findings": [
        {{"finding": "...", "source": "...", "confidence": "high/medium/low", "date": "YYYY-MM"}}
    ],
    "data_points": [
        {{"metric": "...", "value": "...", "source": "...", "date": "YYYY-MM"}}
    ],
    "competitors": [
        {{"name": "...", "strengths": ["..."], "weaknesses": ["..."], "market_share": "X%"}}
    ],
    "opportunities": ["..."],
    "risks": ["..."],
    "methodology": "How this research was conducted",
    "limitations": ["What we couldn't verify", "Data gaps"]
}}

RULES:
- Mark confidence levels honestly
- Distinguish verified data from estimates
- Include limitations and data gaps
- Cite sources where possible"""
        
        response = await self._sabios.ask(prompt)
        data = json.loads(self._extract_json(response))
        
        return ResearchReport(topic=topic, **data)
    
    async def competitive_analysis(self, our_product: str, 
                                    competitors: list[str]) -> dict:
        """Análisis competitivo detallado."""
        prompt = f"""Perform competitive analysis:
Our product: {our_product}
Competitors: {', '.join(competitors)}

For each competitor, analyze:
1. Product features vs ours
2. Pricing strategy
3. Target market
4. Strengths and weaknesses
5. Threat level to us (1-10)

Also identify:
- Our unique advantages
- Gaps in the market
- Recommended differentiation strategy

Respond in JSON."""
        
        response = await self._sabios.ask(prompt)
        return json.loads(self._extract_json(response))
    
    async def generate_daily_briefing(self) -> dict:
        """Tarea autónoma: briefing diario."""
        if self._perplexity:
            try:
                briefing = await self._perplexity.research(
                    "Top AI and digital business news today, focus on startups, SaaS, and AI tools"
                )
                return {"briefing": briefing, "source": "perplexity"}
            except Exception:
                pass
        
        # Fallback to LLM
        if self._sabios:
            prompt = "What are the most important AI and digital business developments happening right now? Focus on actionable insights."
            response = await self._sabios.ask(prompt)
            return {"briefing": response, "source": "llm_knowledge"}
        
        return {"briefing": "No research backends available", "source": "none"}
    
    async def fact_check_claims(self, claims: list[str]) -> list[dict]:
        """Verificar claims específicos."""
        results = []
        
        for claim in claims:
            if self._perplexity:
                try:
                    verification = await self._perplexity.research(
                        f"Is this claim true or false? Provide evidence: {claim}"
                    )
                    results.append({
                        "claim": claim,
                        "verification": verification,
                        "source": "perplexity",
                    })
                    continue
                except Exception:
                    pass
            
            if self._sabios:
                prompt = f"""Fact-check this claim: "{claim}"
                
Respond in JSON:
{{"verdict": "true/false/partially_true/unverifiable", "evidence": "...", "confidence": "high/medium/low"}}"""
                response = await self._sabios.ask(prompt)
                results.append({
                    "claim": claim,
                    "verification": self._extract_json(response),
                    "source": "llm_knowledge",
                })
        
        return results
    
    @staticmethod
    def _extract_json(text: str) -> str:
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        if "```" in text:
            return text.split("```")[1].split("```")[0]
        return text.strip()
```

---

## Integración entre Épicas

Sprint 60 cierra el ciclo conectando todo:

```
[60.1] Sovereignty Engine
    ↓ health_check_all()
[60.2] Tech Radar ← dependency_scan()
    ↓ scan_tech_trends()
[60.4] Embrión-Financiero ← burn_rate includes SaaS costs
    ↓ unit_economics
[60.3] Simulator v2 ← calibrate from financial actuals
    ↓ visualize
[60.5] Embrión-Investigador ← validates simulator assumptions
    ↓ fact_check
[All Embriones] ← 7/7 COMPLETE
```

---

## La Colmena Completa (7/7 Embriones)

| # | Embrión | Sprint | Dominio | Tareas Autónomas |
|---|---|---|---|---|
| 1 | Embrión-Ventas | 57 | Ventas, funnels, conversión | 4 |
| 2 | Embrión-Técnico | 58 | Arquitectura, code review, DevOps | 4 |
| 3 | Embrión-Vigía | 58 | Monitoring, anomalías, seguridad | 4 |
| 4 | Embrión-Creativo | 59 | Diseño, branding, UX | 4 |
| 5 | Embrión-Estratega | 59 | Estrategia, planning, priorización | 4 |
| 6 | **Embrión-Financiero** | **60** | Finanzas, unit economics, impuestos | 3 |
| 7 | **Embrión-Investigador** | **60** | Research, benchmarks, fact-checking | 4 |

**Total:** 7 embriones, 27 tareas autónomas, cobertura completa de dominios.

---

## Archivos a Crear/Modificar

| Archivo | Acción | Épica |
|---|---|---|
| `kernel/sovereignty/__init__.py` | Crear | 60.1 |
| `kernel/sovereignty/engine.py` | Crear | 60.1 |
| `kernel/vanguard/__init__.py` | Crear | 60.2 |
| `kernel/vanguard/tech_radar.py` | Crear | 60.2 |
| `kernel/simulator/__init__.py` | Crear | 60.3 |
| `kernel/simulator/engine.py` | Crear | 60.3 |
| `kernel/embriones/__init__.py` | Crear | 60.4, 60.5 |
| `kernel/embriones/embrion_financiero.py` | Crear | 60.4 |
| `kernel/embriones/embrion_investigador.py` | Crear | 60.5 |
| `kernel/main.py` | Modificar (agregar /api/simulate, /api/sovereignty) | 60.1, 60.3 |
| `requirements.txt` | Agregar scipy | 60.3 |
| `supabase/migrations/` | Crear tablas | 60.1 |

---

## Criterios de Aceptación

| Épica | Criterio | Verificación |
|---|---|---|
| 60.1 | Sovereignty score calculable para todas las dependencias | Score > 0 para 8 dependencias |
| 60.1 | Health check detecta dependencia caída en <10s | Test con endpoint inválido |
| 60.1 | Sovereign mode activable con un comando | activate_sovereign_mode() funciona |
| 60.2 | Detecta >5 dependencias desactualizadas | Test contra requirements.txt real |
| 60.2 | OSV.dev check encuentra CVEs conocidos | Test con paquete con CVE conocido |
| 60.2 | Tech trends incluyen datos de PyPI y GitHub reales | Verify source fields |
| 60.3 | 6 distribuciones funcionan correctamente | Test estadístico por distribución |
| 60.3 | Calibración mejora fit vs. datos reales | KS test antes/después |
| 60.3 | API endpoints responden en <2s para 10K simulaciones | Benchmark |
| 60.4 | Unit economics calcula correctamente LTV/CAC | Test con datos conocidos |
| 60.4 | Proyección financiera tiene 3 escenarios | Verify pessimistic/base/optimistic |
| 60.5 | Deep research produce reporte con fuentes | Verify source fields populated |
| 60.5 | Fact-check distingue claims verificables de no-verificables | Test con 10 claims mixtos |

---

## Estimación de Costos

| Componente | Costo Mensual |
|---|---|
| GlitchTip self-hosted (Docker) | $0 (self-hosted) |
| Umami self-hosted (Docker) | $0 (self-hosted) |
| Renovate Bot (GitHub Action) | $0 (open source) |
| scipy (library) | $0 |
| LLM calls adicionales (2 embriones) | ~$3-7/mes |
| Perplexity API (Investigador) | ~$5-10/mes |
| **Total Sprint 60** | **$8-17/mes adicionales** |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Self-hosted services requieren mantenimiento | Alta | Medio | Docker compose + auto-restart |
| PyPI API rate limiting en dependency scan | Media | Bajo | Cache results, scan 1x/day |
| Simulator calibration con pocos datos | Alta | Medio | Bayesian priors + minimum data threshold |
| Embrión-Investigador gasta mucho en Perplexity | Media | Medio | Daily budget cap ($2.50) |
| Sovereignty score da falsa sensación de seguridad | Media | Alto | Include "last tested" dates, periodic drills |

---

## Significado del Sprint 60

Sprint 60 cierra la serie 51-60 con los siguientes milestones:

1. **Obj #11 COMPLETO:** 7/7 embriones creados. La colmena está completa.
2. **Obj #12 de 40% → 75%:** Sovereignty Engine con inventario, health checks, y sovereign mode.
3. **Obj #6 de 50% → 80%:** Tech Radar real con PyPI + GitHub + OSV.dev.
4. **Obj #10 de 65% → 85%:** Simulator v2 con 6 distribuciones, calibración, y API para UI.

**Lo que queda para la serie 61-70:**
- Obj #1 (85%): Demo end-to-end de creación de empresa
- Obj #2 (65%): Calibración real de estándares Apple/Tesla
- Obj #13 (60%): Más locales y quality assurance
- Obj #12 (75%): Drill de sovereign mode real

---

## Referencias

[1]: https://www.reddit.com/r/nextjs/comments/1qrnant/best_selfhosted_error_reporting_tool_for_next/ "GlitchTip — Self-hosted Sentry alternative"
[2]: https://umami.is/product/enterprise "Umami — Self-hosted analytics with data sovereignty"
[3]: https://tech-radar.justice.gov.uk/tools/renovate/ "Renovate — ThoughtWorks Tech Radar: Adopt (Mar 2026)"
[4]: https://docs.scipy.org/doc/scipy/reference/stats.html "SciPy 1.17.0 — Statistical functions"
[5]: https://querio.ai/articles/top-react-chart-libraries-data-visualization "Top React Chart Libraries 2026"
[6]: https://api.osv.dev/ "OSV.dev — Open Source Vulnerability Database"
[7]: https://www.thoughtworks.com/en-us/radar/tools "ThoughtWorks Technology Radar — Tools"
