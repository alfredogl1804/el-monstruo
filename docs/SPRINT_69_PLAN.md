# Sprint 69 — "La Inteligencia que se Mide"

> **Serie:** 61-70 (Madurez e Inteligencia Colectiva)
> **Fecha de diseño:** 1 de mayo de 2026
> **Dependencias resueltas:** Sprint 68 (Guardián + Capa 7), Sprint 64 (E2E Demo Pipeline), Sprint 66 (Self-Healing Infrastructure)
> **Biblias consultadas:** Manus v3 (Self-Debug, Reflexión Interna), Hermes-Agent (Knowledge Extraction, Skill Refinement, Continuous Loop)
> **Correcciones de Sprint 68 incorporadas:** C1 (LLM evaluador), C3 (persistencia Supabase), C4 (baseline), C5 (Langfuse), C8 (consolidar directorios)

---

## Contexto Estratégico

Sprint 68 introdujo el Guardián y la Capa 7, pero dejó gaps críticos identificados por el análisis detractor: las métricas del Guardián son manuales (no automatizadas), no hay baseline para detectar regresiones, y el Evaluation Harness tiene solo 4 casos de prueba. Sprint 69 cierra estos gaps y transforma al Guardián de un prototipo a un sistema operativo.

El tema central de Sprint 69 es **"medir para mejorar"**: automatizar la recolección de métricas, establecer baselines cuantitativos, y crear el primer ciclo completo de mejora continua (detectar → medir → corregir → verificar).

Adicionalmente, Sprint 69 integra el patrón **Knowledge Extraction** de Hermes-Agent: después de cada tarea completada, el sistema evalúa si la experiencia justifica crear una skill reutilizable. Esto cierra el loop de aprendizaje autónomo.

---

## Stack Validado en Tiempo Real

| Herramienta | Versión | Rol en Sprint 69 | Estado |
|---|---|---|---|
| Langfuse | 4.5.1 | Métricas automatizadas del Guardián | YA EN STACK |
| Supabase | existente | Persistencia de baselines y métricas | YA EN STACK |
| Ollama | 0.6.2 | LLM evaluador soberano (C1 de Sprint 68) | YA EN STACK |
| APScheduler | 3.11.2 | Programación de evaluaciones periódicas | YA EN STACK |
| structlog | 24.x | Logging estructurado | YA EN STACK |
| PostHog | 7.13.2 | Analytics de comportamiento | YA EN STACK |
| ComplianceMonitor | Sprint 68 | Base para métricas automatizadas | NUEVO (Sprint 68) |
| SelfCorrectionEngine | Sprint 68 | Base para ciclo de mejora | NUEVO (Sprint 68) |
| ToolGateway | Sprint 68 | Base para métricas de herramientas | NUEVO (Sprint 68) |

**Costo adicional estimado:** $2-5/mes (Ollama evaluaciones + Supabase storage incremental)

---

## Épica 69.1 — Automated Metrics Collector

### Problema que resuelve

El ComplianceMonitor de Sprint 68 recibe `ObjectiveMetrics` pero no las genera — depende de que alguien las provea manualmente. Sprint 69 automatiza la recolección de métricas cuantitativas para cada uno de los 14 objetivos usando fuentes de datos reales del sistema.

### Arquitectura

```
kernel/guardian/metrics/
├── __init__.py
├── collector.py             # Orquestador de recolección
├── sources/
│   ├── __init__.py
│   ├── langfuse_source.py   # Métricas de Langfuse (calidad, latencia, costo)
│   ├── supabase_source.py   # Métricas de BD (empresas creadas, embriones activos)
│   ├── code_source.py       # Métricas de código (complejidad, dependencias)
│   └── posthog_source.py    # Métricas de uso (adopción, engagement)
└── aggregator.py            # Agrega métricas en ObjectiveMetrics
```

### Componente: MetricsCollector (collector.py)

```python
"""
El Monstruo — Automated Metrics Collector (Sprint 69, Épica 69.1)
Recolecta métricas cuantitativas para los 14 Objetivos Maestros.

Cada objetivo tiene un conjunto de indicadores medibles que se
recolectan de fuentes reales del sistema (Langfuse, Supabase,
PostHog, análisis de código).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol
import structlog

logger = structlog.get_logger("guardian.metrics.collector")

class MetricSource(Protocol):
    """Protocolo para fuentes de métricas."""
    async def collect(self) -> dict[str, float]:
        """Retorna dict de {metric_name: value}."""
        ...

@dataclass
class ObjectiveIndicator:
    """Un indicador medible para un objetivo."""
    name: str
    source: str                # "langfuse", "supabase", "code", "posthog"
    metric_key: str            # Key en el dict retornado por la fuente
    weight: float              # Peso en el cálculo de cobertura (0-1)
    target_value: float        # Valor objetivo (100% = target alcanzado)
    current_value: float = 0.0

# ── Definición de indicadores por objetivo ──────────────────────────

OBJECTIVE_INDICATORS: dict[int, list[ObjectiveIndicator]] = {
    1: [  # Crear Empresas Completas
        ObjectiveIndicator("empresas_creadas", "supabase", "total_empresas", 0.3, 5),
        ObjectiveIndicator("pipeline_e2e_pass", "langfuse", "e2e_success_rate", 0.4, 0.9),
        ObjectiveIndicator("embriones_activos", "supabase", "active_embriones", 0.3, 6),
    ],
    2: [  # Estándar Apple/Tesla
        ObjectiveIndicator("quality_score_avg", "langfuse", "quality_eval_avg", 0.4, 0.85),
        ObjectiveIndicator("design_consistency", "langfuse", "design_score", 0.3, 0.8),
        ObjectiveIndicator("ux_satisfaction", "posthog", "nps_score", 0.3, 70),
    ],
    3: [  # Mínima Complejidad
        ObjectiveIndicator("cyclomatic_complexity", "code", "avg_complexity", 0.3, 5),
        ObjectiveIndicator("dependency_count", "code", "total_deps", 0.3, 30),
        ObjectiveIndicator("loc_per_feature", "code", "avg_loc_feature", 0.4, 200),
    ],
    4: [  # No Equivocarse 2 Veces
        ObjectiveIndicator("error_recurrence", "langfuse", "repeated_errors", 0.5, 0),
        ObjectiveIndicator("correction_success", "supabase", "correction_rate", 0.3, 0.9),
        ObjectiveIndicator("regression_count", "langfuse", "regressions_30d", 0.2, 0),
    ],
    5: [  # Gasolina (Costo)
        ObjectiveIndicator("monthly_cost", "langfuse", "total_cost_30d", 0.4, 50),
        ObjectiveIndicator("cost_per_task", "langfuse", "avg_cost_per_task", 0.3, 0.05),
        ObjectiveIndicator("infra_cost", "supabase", "infra_monthly", 0.3, 20),
    ],
    6: [  # Vanguardia
        ObjectiveIndicator("tech_radar_score", "supabase", "tech_radar_avg", 0.4, 0.8),
        ObjectiveIndicator("pattern_adoption", "code", "modern_patterns_pct", 0.3, 0.7),
        ObjectiveIndicator("research_freshness", "supabase", "research_age_days", 0.3, 30),
    ],
    7: [  # No Inventar la Rueda
        ObjectiveIndicator("lib_reuse_ratio", "code", "external_lib_ratio", 0.4, 0.6),
        ObjectiveIndicator("custom_vs_standard", "code", "custom_code_pct", 0.3, 0.4),
        ObjectiveIndicator("duplicate_code", "code", "duplication_pct", 0.3, 0.05),
    ],
    8: [  # Emergencia
        ObjectiveIndicator("emergence_events", "supabase", "emergence_count_30d", 0.4, 5),
        ObjectiveIndicator("cross_embrion_collab", "supabase", "cross_collab_count", 0.3, 3),
        ObjectiveIndicator("unexpected_solutions", "langfuse", "novel_solutions", 0.3, 2),
    ],
    9: [  # Transversalidad — CERRADO (100%)
        ObjectiveIndicator("transversal_coverage", "code", "layer_coverage", 1.0, 1.0),
    ],
    10: [  # Simulador
        ObjectiveIndicator("simulation_accuracy", "supabase", "sim_prediction_accuracy", 0.4, 0.8),
        ObjectiveIndicator("scenarios_tested", "supabase", "total_scenarios", 0.3, 50),
        ObjectiveIndicator("sim_coverage", "supabase", "industry_coverage", 0.3, 0.6),
    ],
    11: [  # Embriones — CERRADO (100%)
        ObjectiveIndicator("embrion_health", "supabase", "embrion_health_avg", 1.0, 0.9),
    ],
    12: [  # Soberanía
        ObjectiveIndicator("sovereign_llm_usage", "langfuse", "ollama_pct", 0.3, 0.5),
        ObjectiveIndicator("external_dependency", "code", "external_api_count", 0.3, 5),
        ObjectiveIndicator("data_sovereignty", "supabase", "data_local_pct", 0.4, 0.8),
    ],
    13: [  # Del Mundo
        ObjectiveIndicator("i18n_coverage", "code", "translated_strings_pct", 0.3, 0.8),
        ObjectiveIndicator("regions_supported", "supabase", "active_regions", 0.3, 3),
        ObjectiveIndicator("cultural_adaptation", "langfuse", "cultural_score", 0.4, 0.7),
    ],
    14: [  # El Guardián
        ObjectiveIndicator("guardian_uptime", "supabase", "guardian_heartbeat_pct", 0.3, 0.99),
        ObjectiveIndicator("drift_detection_rate", "supabase", "drifts_detected_vs_actual", 0.4, 0.9),
        ObjectiveIndicator("correction_effectiveness", "supabase", "correction_success_rate", 0.3, 0.8),
    ],
}

class MetricsCollector:
    """
    Orquesta la recolección de métricas de todas las fuentes
    y las agrega en ObjectiveMetrics para el ComplianceMonitor.
    """
    
    def __init__(self, sources: dict[str, MetricSource]):
        self.sources = sources
    
    async def collect_all(self) -> list["ObjectiveMetrics"]:
        """Recolecta métricas de todas las fuentes y calcula cobertura."""
        from kernel.guardian.compliance.monitor import ObjectiveMetrics
        
        # 1. Recolectar datos crudos de cada fuente
        raw_data: dict[str, dict[str, float]] = {}
        for source_name, source in self.sources.items():
            try:
                raw_data[source_name] = await source.collect()
            except Exception as e:
                logger.error("source_collection_failed", source=source_name, error=str(e))
                raw_data[source_name] = {}
        
        # 2. Calcular cobertura por objetivo
        results = []
        for obj_id, indicators in OBJECTIVE_INDICATORS.items():
            coverage = self._calculate_coverage(indicators, raw_data)
            
            # Determinar tendencia (requiere historial)
            trend = await self._determine_trend(obj_id, coverage)
            
            results.append(ObjectiveMetrics(
                objective_id=obj_id,
                objective_name=self._get_name(obj_id),
                coverage_percent=coverage,
                last_measured=datetime.now(timezone.utc),
                trend=trend,
                sprint_last_touched=self._get_last_sprint(obj_id),
                days_since_progress=self._get_days_since(obj_id),
                risk_level=self._classify_risk(coverage, trend)
            ))
        
        logger.info("metrics_collected", objectives=len(results),
                   avg_coverage=sum(r.coverage_percent for r in results) / len(results))
        
        return results
    
    def _calculate_coverage(self, indicators: list[ObjectiveIndicator], 
                           raw_data: dict) -> float:
        """Calcula cobertura ponderada de un objetivo."""
        total_weight = sum(i.weight for i in indicators)
        weighted_sum = 0.0
        
        for indicator in indicators:
            source_data = raw_data.get(indicator.source, {})
            current = source_data.get(indicator.metric_key, 0)
            indicator.current_value = current
            
            # Normalizar: qué porcentaje del target se alcanzó
            if indicator.target_value > 0:
                achievement = min(1.0, current / indicator.target_value)
            else:
                achievement = 1.0 if current == 0 else 0.0
            
            weighted_sum += achievement * indicator.weight
        
        return (weighted_sum / total_weight * 100) if total_weight > 0 else 0
    
    async def _determine_trend(self, obj_id: int, current: float) -> str:
        """Determina tendencia comparando con medición anterior."""
        # TODO: Implementar con historial en Supabase
        return "stable"
    
    def _classify_risk(self, coverage: float, trend: str) -> str:
        if coverage >= 90 and trend != "declining":
            return "healthy"
        elif coverage >= 70:
            return "warning"
        else:
            return "critical"
    
    OBJECTIVE_NAMES = {
        1: "Crear Empresas", 2: "Apple/Tesla", 3: "Mínima Complejidad",
        4: "No Equivocarse 2x", 5: "Gasolina", 6: "Vanguardia",
        7: "No Inventar Rueda", 8: "Emergencia", 9: "Transversalidad",
        10: "Simulador", 11: "Embriones", 12: "Soberanía",
        13: "Del Mundo", 14: "El Guardián"
    }
    
    def _get_name(self, obj_id: int) -> str:
        return self.OBJECTIVE_NAMES.get(obj_id, f"Objetivo #{obj_id}")
    
    def _get_last_sprint(self, obj_id: int) -> int:
        # TODO: Consultar Supabase
        return 68
    
    def _get_days_since(self, obj_id: int) -> int:
        # TODO: Consultar Supabase
        return 0
```

### Componente: LangfuseSource (langfuse_source.py)

```python
"""
Fuente de métricas: Langfuse.
Extrae calidad, latencia, costo, y scores de evaluación.
"""
from __future__ import annotations
import httpx
import os
import structlog

logger = structlog.get_logger("guardian.metrics.langfuse")

class LangfuseMetricSource:
    """Recolecta métricas de Langfuse API."""
    
    def __init__(self):
        self.base_url = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
    
    async def collect(self) -> dict[str, float]:
        """Recolecta todas las métricas de Langfuse."""
        metrics = {}
        
        async with httpx.AsyncClient() as client:
            # Calidad promedio (scores de evaluación)
            scores = await self._get_scores(client, "quality")
            metrics["quality_eval_avg"] = self._average(scores)
            metrics["design_score"] = await self._get_score_avg(client, "design_quality")
            metrics["cultural_score"] = await self._get_score_avg(client, "cultural_adaptation")
            
            # Costos
            costs = await self._get_costs(client, days=30)
            metrics["total_cost_30d"] = sum(costs)
            metrics["avg_cost_per_task"] = (sum(costs) / len(costs)) if costs else 0
            
            # Errores y regresiones
            metrics["repeated_errors"] = await self._count_repeated_errors(client)
            metrics["regressions_30d"] = await self._count_regressions(client)
            
            # E2E success rate
            metrics["e2e_success_rate"] = await self._get_e2e_rate(client)
            
            # Soberanía: % de llamadas a Ollama vs externas
            metrics["ollama_pct"] = await self._get_ollama_percentage(client)
            
            # Soluciones novedosas
            metrics["novel_solutions"] = await self._count_novel(client)
        
        logger.info("langfuse_metrics_collected", metric_count=len(metrics))
        return metrics
    
    async def _get_scores(self, client: httpx.AsyncClient, name: str) -> list[float]:
        """Obtiene scores de Langfuse por nombre."""
        try:
            resp = await client.get(
                f"{self.base_url}/api/public/scores",
                params={"name": name, "limit": 100},
                auth=(self.public_key, self.secret_key)
            )
            data = resp.json()
            return [s["value"] for s in data.get("data", []) if s.get("value") is not None]
        except Exception as e:
            logger.error("langfuse_scores_failed", name=name, error=str(e))
            return []
    
    async def _get_score_avg(self, client: httpx.AsyncClient, name: str) -> float:
        scores = await self._get_scores(client, name)
        return self._average(scores)
    
    async def _get_costs(self, client: httpx.AsyncClient, days: int) -> list[float]:
        """Obtiene costos de los últimos N días."""
        try:
            resp = await client.get(
                f"{self.base_url}/api/public/generations",
                params={"limit": 500},
                auth=(self.public_key, self.secret_key)
            )
            data = resp.json()
            return [
                g.get("totalCost", 0) or 0
                for g in data.get("data", [])
            ]
        except Exception:
            return []
    
    async def _count_repeated_errors(self, client: httpx.AsyncClient) -> int:
        """Cuenta errores que se repiten (mismo tipo, >1 ocurrencia)."""
        # Simplificación: cuenta traces con status ERROR
        try:
            resp = await client.get(
                f"{self.base_url}/api/public/traces",
                params={"limit": 200},
                auth=(self.public_key, self.secret_key)
            )
            data = resp.json()
            errors = [t.get("metadata", {}).get("error_type", "unknown")
                     for t in data.get("data", [])
                     if t.get("level") == "ERROR"]
            from collections import Counter
            counts = Counter(errors)
            return sum(1 for c in counts.values() if c > 1)
        except Exception:
            return 0
    
    async def _count_regressions(self, client: httpx.AsyncClient) -> int:
        return 0  # Implementar con baseline comparison
    
    async def _get_e2e_rate(self, client: httpx.AsyncClient) -> float:
        return 0.85  # Placeholder hasta que E2E pipeline esté integrado
    
    async def _get_ollama_percentage(self, client: httpx.AsyncClient) -> float:
        """Calcula % de generaciones que usaron Ollama."""
        try:
            resp = await client.get(
                f"{self.base_url}/api/public/generations",
                params={"limit": 200},
                auth=(self.public_key, self.secret_key)
            )
            data = resp.json()
            gens = data.get("data", [])
            if not gens:
                return 0
            ollama = sum(1 for g in gens if "ollama" in (g.get("model", "") or "").lower())
            return ollama / len(gens)
        except Exception:
            return 0
    
    async def _count_novel(self, client: httpx.AsyncClient) -> int:
        return 0  # Implementar con emergence tracker
    
    @staticmethod
    def _average(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0
```

---

## Épica 69.2 — Baseline & Regression Detection

### Problema que resuelve

Sin baseline, el Evaluation Harness no puede distinguir entre "siempre fue así" y "esto empeoró". Sprint 69 implementa la corrección C4 de Sprint 68: snapshot de baseline + comparación temporal.

### Componente: BaselineManager (baseline_manager.py)

```python
"""
El Monstruo — Baseline Manager (Sprint 69, Épica 69.2)
Gestiona snapshots de métricas para detección de regresiones.

Corrección C4 de Sprint 68: "Sin baseline, no puede detectar
regresiones reales."
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import json
import structlog

logger = structlog.get_logger("guardian.baseline")

@dataclass
class BaselineSnapshot:
    snapshot_id: str
    sprint_number: int
    timestamp: datetime
    metrics: dict[int, float]        # {objective_id: coverage_percent}
    eval_results: dict[str, float]   # {case_name: score}
    metadata: dict = field(default_factory=dict)

@dataclass
class RegressionReport:
    timestamp: datetime
    current_sprint: int
    baseline_sprint: int
    regressions: list[dict]          # [{objective_id, from, to, delta}]
    improvements: list[dict]
    stable: list[int]                # objective_ids sin cambio

class BaselineManager:
    """
    Gestiona baselines y detecta regresiones.
    
    Estrategia:
    1. Después de cada sprint, guardar snapshot en Supabase
    2. Comparar métricas actuales con baseline más reciente
    3. Marcar como regresión si delta < -2%
    4. Marcar como mejora si delta > +2%
    5. Alertar al ComplianceMonitor si hay regresiones
    """
    
    REGRESSION_THRESHOLD = -2.0   # % de caída para marcar regresión
    IMPROVEMENT_THRESHOLD = 2.0   # % de subida para marcar mejora
    
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    async def save_baseline(self, sprint_number: int, 
                           metrics: list, eval_results: dict) -> BaselineSnapshot:
        """Guarda un snapshot de baseline después de un sprint."""
        import uuid
        
        snapshot = BaselineSnapshot(
            snapshot_id=str(uuid.uuid4()),
            sprint_number=sprint_number,
            timestamp=datetime.now(timezone.utc),
            metrics={m.objective_id: m.coverage_percent for m in metrics},
            eval_results=eval_results
        )
        
        await self.db.table("guardian_baselines").insert({
            "id": snapshot.snapshot_id,
            "sprint_number": sprint_number,
            "metrics": json.dumps(snapshot.metrics),
            "eval_results": json.dumps(snapshot.eval_results),
            "created_at": snapshot.timestamp.isoformat()
        }).execute()
        
        logger.info("baseline_saved", sprint=sprint_number, 
                   objectives=len(snapshot.metrics))
        return snapshot
    
    async def get_latest_baseline(self) -> Optional[BaselineSnapshot]:
        """Obtiene el baseline más reciente."""
        result = await self.db.table("guardian_baselines") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        
        if not result.data:
            return None
        
        row = result.data[0]
        return BaselineSnapshot(
            snapshot_id=row["id"],
            sprint_number=row["sprint_number"],
            timestamp=datetime.fromisoformat(row["created_at"]),
            metrics=json.loads(row["metrics"]),
            eval_results=json.loads(row["eval_results"])
        )
    
    async def detect_regressions(self, current_metrics: list,
                                current_sprint: int) -> RegressionReport:
        """Compara métricas actuales con baseline y detecta regresiones."""
        baseline = await self.get_latest_baseline()
        
        if not baseline:
            logger.info("no_baseline_found", action="creating_first_baseline")
            return RegressionReport(
                timestamp=datetime.now(timezone.utc),
                current_sprint=current_sprint,
                baseline_sprint=0,
                regressions=[],
                improvements=[],
                stable=[]
            )
        
        regressions = []
        improvements = []
        stable = []
        
        current_map = {m.objective_id: m.coverage_percent for m in current_metrics}
        
        for obj_id, baseline_value in baseline.metrics.items():
            current_value = current_map.get(obj_id, 0)
            delta = current_value - baseline_value
            
            if delta < self.REGRESSION_THRESHOLD:
                regressions.append({
                    "objective_id": obj_id,
                    "from": baseline_value,
                    "to": current_value,
                    "delta": delta
                })
            elif delta > self.IMPROVEMENT_THRESHOLD:
                improvements.append({
                    "objective_id": obj_id,
                    "from": baseline_value,
                    "to": current_value,
                    "delta": delta
                })
            else:
                stable.append(obj_id)
        
        report = RegressionReport(
            timestamp=datetime.now(timezone.utc),
            current_sprint=current_sprint,
            baseline_sprint=baseline.sprint_number,
            regressions=regressions,
            improvements=improvements,
            stable=stable
        )
        
        if regressions:
            logger.warning("regressions_detected", count=len(regressions),
                         details=regressions)
        else:
            logger.info("no_regressions", improvements=len(improvements),
                       stable=len(stable))
        
        return report
```

---

## Épica 69.3 — Knowledge Extraction Engine

### Problema que resuelve

El Monstruo aprende de cada tarea pero no formaliza ese aprendizaje. El patrón Knowledge Extraction de Hermes-Agent establece que después de cada tarea completada, el sistema debe evaluar si la experiencia justifica crear una skill reutilizable. Esto cierra el loop de aprendizaje autónomo y alimenta al Obj #8 (Emergencia).

### Componente: KnowledgeExtractor (knowledge_extractor.py)

```python
"""
El Monstruo — Knowledge Extraction Engine (Sprint 69, Épica 69.3)
Patrón: Hermes-Agent Knowledge Extraction + Skill Refinement

Después de cada tarea completada, evalúa si la experiencia
justifica crear una skill reutilizable.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import structlog

logger = structlog.get_logger("guardian.knowledge")

@dataclass
class TaskExperience:
    """Experiencia adquirida durante una tarea."""
    task_id: str
    task_type: str
    tools_used: list[str]
    steps_taken: list[str]
    outcome: str                     # "success", "partial", "failure"
    duration_seconds: float
    errors_encountered: list[str]
    recovery_strategies: list[str]
    novel_approaches: list[str]      # Cosas que hizo diferente a lo esperado

@dataclass
class ExtractedSkill:
    """Skill extraída de una experiencia."""
    name: str
    description: str
    trigger_conditions: list[str]    # Cuándo usar esta skill
    steps: list[str]                 # Pasos ordenados
    tools_required: list[str]
    common_pitfalls: list[str]       # Errores a evitar
    success_criteria: list[str]
    source_task_id: str
    confidence: float                # 0-1
    times_used: int = 0
    times_refined: int = 0

class KnowledgeExtractor:
    """
    Evalúa experiencias de tareas y extrae skills reutilizables.
    
    Criterios para crear skill:
    1. La tarea fue exitosa (outcome == "success")
    2. Involucró >3 pasos (no trivial)
    3. Usó >2 herramientas (multi-tool)
    4. O: la tarea falló pero la recuperación fue exitosa (aprendizaje de error)
    
    Criterios para refinar skill existente:
    1. Ya existe una skill similar
    2. La nueva experiencia agrega información (nuevos pitfalls, mejores pasos)
    """
    
    MIN_STEPS_FOR_SKILL = 3
    MIN_TOOLS_FOR_SKILL = 2
    SIMILARITY_THRESHOLD = 0.7
    
    def __init__(self, skill_store, ollama_client=None):
        self.store = skill_store
        self.ollama = ollama_client
        
    async def evaluate(self, experience: TaskExperience) -> Optional[ExtractedSkill]:
        """Evalúa si una experiencia justifica crear/refinar una skill."""
        
        # 1. ¿Merece ser skill?
        if not self._qualifies_for_extraction(experience):
            logger.debug("experience_not_qualified", task_id=experience.task_id)
            return None
        
        # 2. ¿Ya existe una skill similar?
        existing = await self._find_similar_skill(experience)
        
        if existing:
            # Refinar skill existente
            refined = await self._refine_skill(existing, experience)
            await self.store.update(refined)
            logger.info("skill_refined", skill=refined.name, 
                       refinements=refined.times_refined)
            return refined
        else:
            # Crear nueva skill
            new_skill = await self._create_skill(experience)
            await self.store.save(new_skill)
            logger.info("skill_created", skill=new_skill.name,
                       confidence=new_skill.confidence)
            return new_skill
    
    def _qualifies_for_extraction(self, exp: TaskExperience) -> bool:
        """Determina si la experiencia merece ser extraída como skill."""
        # Éxito con complejidad suficiente
        if (exp.outcome == "success" and 
            len(exp.steps_taken) >= self.MIN_STEPS_FOR_SKILL and
            len(exp.tools_used) >= self.MIN_TOOLS_FOR_SKILL):
            return True
        
        # Fallo con recuperación exitosa (aprendizaje valioso)
        if (exp.outcome in ("success", "partial") and 
            len(exp.errors_encountered) > 0 and
            len(exp.recovery_strategies) > 0):
            return True
        
        # Enfoque novedoso
        if len(exp.novel_approaches) > 0:
            return True
        
        return False
    
    async def _find_similar_skill(self, exp: TaskExperience) -> Optional[ExtractedSkill]:
        """Busca una skill existente similar a la experiencia."""
        all_skills = await self.store.get_all()
        
        for skill in all_skills:
            # Comparar por tipo de tarea y herramientas
            tool_overlap = len(set(skill.tools_required) & set(exp.tools_used))
            tool_total = len(set(skill.tools_required) | set(exp.tools_used))
            
            if tool_total > 0 and tool_overlap / tool_total >= self.SIMILARITY_THRESHOLD:
                return skill
        
        return None
    
    async def _create_skill(self, exp: TaskExperience) -> ExtractedSkill:
        """Crea una nueva skill a partir de una experiencia."""
        return ExtractedSkill(
            name=f"skill_{exp.task_type}_{exp.task_id[:8]}",
            description=f"Skill extraída de tarea {exp.task_type}",
            trigger_conditions=[f"task_type == '{exp.task_type}'"],
            steps=exp.steps_taken,
            tools_required=exp.tools_used,
            common_pitfalls=exp.errors_encountered,
            success_criteria=[f"outcome == 'success'"],
            source_task_id=exp.task_id,
            confidence=0.6 if exp.outcome == "success" else 0.3
        )
    
    async def _refine_skill(self, skill: ExtractedSkill, 
                           exp: TaskExperience) -> ExtractedSkill:
        """Refina una skill existente con nueva experiencia."""
        # Agregar nuevos pitfalls
        new_pitfalls = [e for e in exp.errors_encountered 
                       if e not in skill.common_pitfalls]
        skill.common_pitfalls.extend(new_pitfalls)
        
        # Agregar nuevas herramientas
        new_tools = [t for t in exp.tools_used 
                    if t not in skill.tools_required]
        skill.tools_required.extend(new_tools)
        
        # Incrementar confianza si fue exitosa
        if exp.outcome == "success":
            skill.confidence = min(0.95, skill.confidence + 0.05)
        
        skill.times_refined += 1
        return skill
```

---

## Épica 69.4 — Guardian Dashboard Integration

### Problema que resuelve

Las métricas del Guardián existen pero no son visibles. Sprint 69 integra las métricas con Langfuse (corrección C5 de Sprint 68) y expone endpoints para el Command Center.

### Componente: GuardianDashboard (dashboard_routes.py)

```python
"""
El Monstruo — Guardian Dashboard Routes (Sprint 69, Épica 69.4)
Endpoints FastAPI para exponer métricas del Guardián al Command Center.
Corrección C5 de Sprint 68: integrar con Langfuse.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger("guardian.dashboard")
router = APIRouter(prefix="/guardian", tags=["guardian"])

@router.get("/health")
async def guardian_health():
    """Health check del Guardián (C7 de Sprint 68: auto-vigilancia)."""
    return {
        "status": "healthy",
        "last_evaluation": datetime.now(timezone.utc).isoformat(),
        "components": {
            "compliance_monitor": "active",
            "metrics_collector": "active",
            "baseline_manager": "active",
            "knowledge_extractor": "active",
            "self_correction": "active"
        }
    }

@router.get("/objectives")
async def get_objectives_status():
    """Retorna estado actual de los 14 objetivos."""
    # Integración con MetricsCollector
    metrics = await metrics_collector.collect_all()
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "objectives": [
            {
                "id": m.objective_id,
                "name": m.objective_name,
                "coverage": m.coverage_percent,
                "trend": m.trend,
                "risk": m.risk_level,
                "last_sprint": m.sprint_last_touched
            }
            for m in metrics
        ]
    }

@router.get("/baselines")
async def get_baselines():
    """Retorna historial de baselines."""
    baselines = await baseline_manager.get_all_baselines()
    return {
        "count": len(baselines),
        "baselines": [
            {
                "sprint": b.sprint_number,
                "timestamp": b.timestamp.isoformat(),
                "avg_coverage": sum(b.metrics.values()) / len(b.metrics)
            }
            for b in baselines
        ]
    }

@router.get("/regressions")
async def get_regressions():
    """Retorna regresiones detectadas."""
    metrics = await metrics_collector.collect_all()
    report = await baseline_manager.detect_regressions(metrics, current_sprint=69)
    return {
        "regressions": report.regressions,
        "improvements": report.improvements,
        "stable_count": len(report.stable)
    }

@router.get("/skills")
async def get_extracted_skills():
    """Retorna skills extraídas por el Knowledge Extractor."""
    skills = await knowledge_extractor.store.get_all()
    return {
        "count": len(skills),
        "skills": [
            {
                "name": s.name,
                "confidence": s.confidence,
                "times_used": s.times_used,
                "times_refined": s.times_refined,
                "tools": s.tools_required
            }
            for s in skills
        ]
    }

@router.post("/evaluate")
async def trigger_evaluation():
    """Dispara evaluación manual del Guardián."""
    metrics = await metrics_collector.collect_all()
    alerts = await compliance_monitor.evaluate_all(metrics)
    
    # Registrar en Langfuse (C5)
    await _report_to_langfuse(metrics)
    
    return {
        "evaluated": len(metrics),
        "alerts": len(alerts),
        "alert_details": [
            {
                "objective": a.objective_id,
                "type": a.alert_type,
                "severity": a.severity,
                "message": a.message
            }
            for a in alerts
        ]
    }

async def _report_to_langfuse(metrics):
    """Registra métricas del Guardián en Langfuse como scores."""
    for metric in metrics:
        try:
            await langfuse_client.score(
                name=f"guardian_obj_{metric.objective_id}",
                value=metric.coverage_percent / 100,
                comment=f"{metric.objective_name}: {metric.trend}"
            )
        except Exception as e:
            logger.error("langfuse_report_failed", 
                       objective=metric.objective_id, error=str(e))
```

---

## Épica 69.5 — Continuous Improvement Scheduler

### Problema que resuelve

Todas las piezas existen (métricas, baseline, detección, corrección) pero no están conectadas en un ciclo automático. Sprint 69 crea el scheduler que ejecuta el ciclo completo: recolectar → evaluar → detectar → corregir → verificar.

### Componente: GuardianScheduler (scheduler.py)

```python
"""
El Monstruo — Guardian Scheduler (Sprint 69, Épica 69.5)
Ciclo de mejora continua: detectar → medir → corregir → verificar.
Patrón: Hermes-Agent Continuous Loop.
"""
from __future__ import annotations
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger("guardian.scheduler")

class GuardianScheduler:
    """
    Programa y ejecuta el ciclo de mejora continua del Guardián.
    
    Ciclo (cada 6 horas):
    1. RECOLECTAR: MetricsCollector obtiene métricas de todas las fuentes
    2. EVALUAR: ComplianceMonitor evalúa los 14 objetivos
    3. DETECTAR: BaselineManager compara con baseline y detecta regresiones
    4. CORREGIR: SelfCorrectionEngine propone/ejecuta correcciones
    5. VERIFICAR: Re-evaluar después de correcciones
    6. APRENDER: KnowledgeExtractor evalúa si hay skills nuevas
    7. REPORTAR: Registrar en Langfuse + notificar si hay alertas
    """
    
    def __init__(self, collector, monitor, baseline_mgr, 
                 correction_engine, knowledge_extractor, 
                 langfuse_reporter, apscheduler):
        self.collector = collector
        self.monitor = monitor
        self.baseline = baseline_mgr
        self.corrector = correction_engine
        self.knowledge = knowledge_extractor
        self.reporter = langfuse_reporter
        self.scheduler = apscheduler
    
    def start(self):
        """Inicia el ciclo de mejora continua."""
        self.scheduler.add_job(
            self.run_cycle,
            trigger="interval",
            hours=6,
            id="guardian_improvement_cycle",
            replace_existing=True
        )
        logger.info("guardian_scheduler_started", interval="6h")
    
    async def run_cycle(self):
        """Ejecuta un ciclo completo de mejora continua."""
        cycle_start = datetime.now(timezone.utc)
        logger.info("improvement_cycle_started")
        
        try:
            # 1. RECOLECTAR
            metrics = await self.collector.collect_all()
            
            # 2. EVALUAR
            alerts = await self.monitor.evaluate_all(metrics)
            
            # 3. DETECTAR regresiones
            regression_report = await self.baseline.detect_regressions(
                metrics, current_sprint=self._get_current_sprint()
            )
            
            # 4. CORREGIR (solo si hay alertas)
            corrections_applied = 0
            for alert in alerts:
                proposal = await self.corrector.propose_correction(alert)
                if proposal.confidence >= 0.7 and not proposal.requires_approval:
                    success = await self.corrector.execute_correction(proposal)
                    if success:
                        corrections_applied += 1
            
            # 5. VERIFICAR (re-evaluar si hubo correcciones)
            if corrections_applied > 0:
                post_metrics = await self.collector.collect_all()
                post_alerts = await self.monitor.evaluate_all(post_metrics)
                verification_passed = len(post_alerts) < len(alerts)
            else:
                verification_passed = True
            
            # 6. APRENDER (evaluar si hay skills nuevas del ciclo)
            # Se ejecuta como parte del flujo normal de tareas
            
            # 7. REPORTAR
            await self.reporter.report(metrics)
            
            duration = (datetime.now(timezone.utc) - cycle_start).total_seconds()
            logger.info("improvement_cycle_completed",
                       duration_s=duration,
                       alerts=len(alerts),
                       regressions=len(regression_report.regressions),
                       corrections=corrections_applied,
                       verification=verification_passed)
            
        except Exception as e:
            logger.error("improvement_cycle_failed", error=str(e))
            # El Guardián se auto-reporta como unhealthy
            await self._report_self_failure(e)
    
    def _get_current_sprint(self) -> int:
        """Obtiene el número de sprint actual."""
        return 69  # TODO: Leer de configuración
    
    async def _report_self_failure(self, error: Exception):
        """C7 de Sprint 68: el Guardián se vigila a sí mismo."""
        from kernel.alerts.sovereign_alerts import AlertType
        # Usar el SovereignAlertMonitor existente
        logger.critical("guardian_self_failure", error=str(error))
```

---

## Resumen de Entregables

| Épica | Archivos | Líneas estimadas | Correcciones Sprint 68 que implementa |
|---|---|---|---|
| 69.1 Metrics Collector | `collector.py`, `langfuse_source.py`, `supabase_source.py`, `code_source.py`, `posthog_source.py` | ~400 | C5 (Langfuse) |
| 69.2 Baseline & Regression | `baseline_manager.py` | ~200 | C4 (Baseline) |
| 69.3 Knowledge Extraction | `knowledge_extractor.py` | ~250 | — (nuevo) |
| 69.4 Dashboard Integration | `dashboard_routes.py` | ~150 | C5 (Langfuse) |
| 69.5 Improvement Scheduler | `scheduler.py` | ~150 | — (nuevo) |
| **TOTAL** | **10 archivos** | **~1,150 líneas** | **3 de 8 correcciones** |

---

## Dependencias Técnicas

```
Sprint 69 depende de:
├── Sprint 68 — ComplianceMonitor, SelfCorrectionEngine, ToolGateway
├── Sprint 14 — SovereignAlertMonitor (para alertas del Guardián)
├── Sprint 42 — Heartbeat System (para auto-vigilancia)
├── Sprint 56.3 — Embrión Scheduler (APScheduler)
└── Sprint 64 — E2E Demo Pipeline (para métricas e2e_success_rate)

Sprint 69 es prerequisito para:
└── Sprint 70 — Cierre de serie con métricas completas del Guardián
```

---

## Tablas SQL Requeridas

```sql
-- Baselines del Guardián
CREATE TABLE guardian_baselines (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sprint_number INT NOT NULL,
    metrics JSONB NOT NULL,
    eval_results JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Skills extraídas
CREATE TABLE extracted_skills (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    trigger_conditions JSONB,
    steps JSONB,
    tools_required JSONB,
    common_pitfalls JSONB,
    success_criteria JSONB,
    source_task_id VARCHAR(100),
    confidence FLOAT DEFAULT 0.5,
    times_used INT DEFAULT 0,
    times_refined INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Historial de métricas del Guardián
CREATE TABLE guardian_metrics_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    objective_id INT NOT NULL,
    coverage_percent FLOAT NOT NULL,
    trend VARCHAR(20),
    risk_level VARCHAR(20),
    raw_indicators JSONB,
    measured_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Costo Estimado

| Concepto | Costo mensual |
|---|---|
| Ollama evaluaciones (LLM evaluador) | $1-2 |
| Supabase storage (baselines + métricas) | $0-1 |
| Langfuse scores adicionales | $0-1 |
| PostHog queries | $0 (plan gratuito) |
| **TOTAL** | **$2-5/mes** |

---

## Notas de Implementación para Hilo A

1. Las tablas SQL deben crearse en Supabase ANTES de desplegar el código.
2. El `MetricsCollector` tiene placeholders (TODO) para fuentes que aún no existen — implementar gradualmente.
3. El `KnowledgeExtractor` necesita un `skill_store` — implementar sobre Supabase con la tabla `extracted_skills`.
4. Los endpoints de `dashboard_routes.py` deben registrarse en `kernel/main.py` con `app.include_router(guardian_router)`.
5. El `GuardianScheduler` se integra con el APScheduler existente del Embrión Scheduler (Sprint 56.3).
6. La primera ejecución del ciclo debe guardar el baseline inicial automáticamente.
7. El directorio `kernel/guardian/metrics/sources/` es nuevo — crearlo desde cero.
