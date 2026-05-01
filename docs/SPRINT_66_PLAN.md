# Sprint 66 — "La Resiliencia Total"

**Fecha:** 1 mayo 2026
**Autor:** Manus AI
**Filosofía:** Un sistema que no puede morir, no puede fallar, y no puede quedarse sin recursos — es un sistema que VIVE.

---

## Contexto Estratégico

Después de 15 sprints (51-65), El Monstruo tiene un promedio de cobertura de 92.4% sobre los 13 Objetivos Maestros. Los 4 objetivos más débiles son:

| Objetivo | Cobertura Actual | Gap Restante | Problema Central |
|----------|-----------------|--------------|------------------|
| #12 Ecosistema/Soberanía | 89% | 11% | Migration paths son teóricos, no probados |
| #5 Gasolina Magna/Premium | 90% | 10% | Hard stop sin degradación graceful |
| #4 Nunca Equivocarse 2x | 90% | 10% | Lessons son per-embrión, no cross-project |
| #10 Simulador Predictivo | 90% | 10% | Solo single-variable, sin decision trees |

Sprint 66 ataca estos 4 gaps con un tema unificador: **resiliencia** — la capacidad de sobrevivir fallos, agotamiento, y dependencias rotas sin intervención humana.

---

## Infraestructura Existente (Validada)

| Componente | Sprint | Archivo | Capacidad Actual | Gap |
|-----------|--------|---------|-----------------|-----|
| FinOps Controller | 15 | `kernel/finops.py` | Budget hard stop ($15/día) | No degradación graceful |
| Supervisor Fallbacks | 33 | `kernel/supervisor.py` | 4 tiers con 3 fallbacks cada uno | Solo model-level |
| Embrión Lessons | 34 | `kernel/embrion_loop.py` | Self-eval + lesson injection | Per-embrión, no global |
| Fallback Engine | 29 | `kernel/fallback_engine.py` | Circuit breaker | No auto-recovery |
| Monte Carlo | 55 (plan) | Pendiente | Single-variable Beta | No multi-variable |

---

## Épica 66.1 — Sovereignty Migration Playbooks

**Objetivo:** Para cada SaaS crítico, un playbook de migración PROBADO que permite operar sin él.

**Dependencia de Obj #12:** Soberanía real = poder migrar, no solo saber que existen alternativas.

### Inventario de Dependencias Críticas

| SaaS | Función | Alternativa Soberana | Complejidad de Migración |
|------|---------|---------------------|-------------------------|
| Supabase | DB + Auth + Realtime | PostgreSQL + Keycloak + SSE | Alta |
| OpenAI/Anthropic | LLM | Ollama (local) | Media |
| ElevenLabs | TTS/STT | Whisper + Coqui TTS | Media |
| Langfuse | Observability | GlitchTip + custom metrics | Baja |
| Telegram | Notifications | SMTP + Ntfy.sh | Baja |
| Perplexity | Web search | SearXNG + scraping | Media |
| DeepL | Translation | Argos Translate (local) | Baja |
| GitHub | Code hosting | Gitea (self-hosted) | Media |

### Estructura de cada Playbook

```python
# kernel/sovereignty/playbooks.py
"""Sprint 66 — Sovereignty Migration Playbooks."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import structlog

logger = structlog.get_logger("kernel.sovereignty.playbooks")


class MigrationComplexity(Enum):
    LOW = "low"          # < 1 día
    MEDIUM = "medium"    # 1-3 días
    HIGH = "high"        # > 3 días


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    MIGRATING = "migrating"


@dataclass
class MigrationPlaybook:
    """Complete migration playbook for a single SaaS dependency."""
    service_name: str
    current_provider: str
    sovereign_alternative: str
    complexity: MigrationComplexity
    degradation_on_migrate: list[str]  # What features are lost/degraded
    pre_migration_checks: list[str]
    migration_steps: list[str]
    rollback_steps: list[str]
    health_check_endpoint: Optional[str] = None
    last_validated: Optional[str] = None
    validation_result: Optional[dict] = None


@dataclass
class SovereigntyEngine:
    """
    Manages sovereignty posture for El Monstruo.
    
    Responsibilities:
    - Maintain inventory of all external dependencies
    - Validate migration playbooks periodically
    - Execute migrations when triggered (manual or auto)
    - Track degradation matrix post-migration
    """
    playbooks: dict[str, MigrationPlaybook] = field(default_factory=dict)
    service_status: dict[str, ServiceStatus] = field(default_factory=dict)
    
    def __post_init__(self):
        self._register_default_playbooks()
    
    def _register_default_playbooks(self) -> None:
        """Register the 8 critical migration playbooks."""
        self.playbooks["supabase"] = MigrationPlaybook(
            service_name="supabase",
            current_provider="Supabase Cloud",
            sovereign_alternative="PostgreSQL 16 + Keycloak + Server-Sent Events",
            complexity=MigrationComplexity.HIGH,
            degradation_on_migrate=[
                "Realtime subscriptions → SSE (higher latency)",
                "Auth magic links → email/password only",
                "Dashboard UI → pgAdmin",
            ],
            pre_migration_checks=[
                "PostgreSQL 16 accessible",
                "All tables schema exported",
                "Row-level security policies documented",
                "Connection string updated in .env",
            ],
            migration_steps=[
                "1. pg_dump from Supabase → local SQL file",
                "2. Create target PostgreSQL database",
                "3. pg_restore to target",
                "4. Update DATABASE_URL in environment",
                "5. Deploy Keycloak for auth",
                "6. Migrate auth users (export/import)",
                "7. Replace realtime subscriptions with SSE",
                "8. Validate all queries work",
            ],
            rollback_steps=[
                "1. Revert DATABASE_URL to Supabase",
                "2. Verify connection",
                "3. Disable local PostgreSQL",
            ],
            health_check_endpoint="/api/health/db",
        )
        
        self.playbooks["llm"] = MigrationPlaybook(
            service_name="llm",
            current_provider="OpenAI + Anthropic + Google + xAI",
            sovereign_alternative="Ollama (local) with deepseek-v3.1:671b",
            complexity=MigrationComplexity.MEDIUM,
            degradation_on_migrate=[
                "Response quality: ~85% of cloud models",
                "Speed: 2-5x slower on consumer hardware",
                "Context window: limited to 32K vs 200K",
            ],
            pre_migration_checks=[
                "Ollama installed and running",
                "Target model pulled (deepseek-v3.1:671b)",
                "GPU memory sufficient (>24GB for 671b)",
                "Router sovereign_mode flag exists",
            ],
            migration_steps=[
                "1. Set SOVEREIGN_MODE=true in environment",
                "2. Router redirects all requests to Ollama",
                "3. Verify response quality with test suite",
                "4. Adjust temperature/top_p for quality",
            ],
            rollback_steps=[
                "1. Set SOVEREIGN_MODE=false",
                "2. Router resumes cloud routing",
            ],
            health_check_endpoint="/api/health/llm",
        )
        
        self.playbooks["elevenlabs"] = MigrationPlaybook(
            service_name="elevenlabs",
            current_provider="ElevenLabs API",
            sovereign_alternative="Whisper (STT) + Coqui TTS (TTS)",
            complexity=MigrationComplexity.MEDIUM,
            degradation_on_migrate=[
                "Voice quality: noticeably worse",
                "Latency: 2-3x slower",
                "Voice cloning: not available",
                "Languages: fewer supported",
            ],
            pre_migration_checks=[
                "Whisper model downloaded",
                "Coqui TTS installed with target voice",
                "Audio pipeline tested end-to-end",
            ],
            migration_steps=[
                "1. Set VOICE_SOVEREIGN_MODE=true",
                "2. STT routes to local Whisper",
                "3. TTS routes to Coqui",
                "4. Validate audio quality acceptable",
            ],
            rollback_steps=[
                "1. Set VOICE_SOVEREIGN_MODE=false",
                "2. Resume ElevenLabs routing",
            ],
            health_check_endpoint="/api/health/voice",
        )
        
        # ... (5 more playbooks for Langfuse, Telegram, Perplexity, DeepL, GitHub)
    
    async def validate_playbook(self, service_name: str) -> dict:
        """
        Validate that a migration playbook actually works.
        Runs pre-migration checks without executing migration.
        """
        playbook = self.playbooks.get(service_name)
        if not playbook:
            return {"valid": False, "error": f"No playbook for {service_name}"}
        
        results = {"service": service_name, "checks": []}
        for check in playbook.pre_migration_checks:
            # Execute each check
            passed = await self._execute_check(check)
            results["checks"].append({"check": check, "passed": passed})
        
        all_passed = all(c["passed"] for c in results["checks"])
        results["ready_to_migrate"] = all_passed
        playbook.last_validated = datetime.now(timezone.utc).isoformat()
        playbook.validation_result = results
        
        logger.info("sovereignty_playbook_validated",
                   service=service_name, ready=all_passed)
        return results
    
    async def validate_all(self) -> dict:
        """Validate all 8 playbooks. Run weekly."""
        results = {}
        for name in self.playbooks:
            results[name] = await self.validate_playbook(name)
        
        ready_count = sum(1 for r in results.values() if r.get("ready_to_migrate"))
        logger.info("sovereignty_full_validation",
                   total=len(results), ready=ready_count)
        return {
            "total_services": len(results),
            "ready_to_migrate": ready_count,
            "sovereignty_score": ready_count / len(results),
            "details": results,
        }
```

### Validación Semanal Automática

El Embrión-Vigía ejecuta `validate_all()` cada domingo a las 3:00 AM. Si algún playbook falla la validación, genera un alerta con el check específico que falló y la acción correctiva sugerida.

---

## Épica 66.2 — Adaptive Quality Engine

**Objetivo:** Cuando el budget se agota, degradar calidad GRACEFULLY en 5 niveles — nunca hard-stop.

**Dependencia de Obj #5:** Gasolina Magna/Premium = poder operar en CUALQUIER nivel de recursos.

### Los 5 Niveles de Calidad

| Nivel | Nombre | Modelo | Max Tokens | Features | Costo Relativo |
|-------|--------|--------|-----------|----------|---------------|
| 5 | Premium | claude-opus-4-7 / gpt-4.1 | 8192 | Full (tools, vision, search) | 100% |
| 4 | Standard | gpt-4.1-mini / gemini-3.1-flash | 4096 | Tools + search, no vision | 40% |
| 3 | Economy | grok-4.1-fast / groq-llama-scout | 2048 | Basic tools, no search | 15% |
| 2 | Minimal | gemini-3.1-flash-lite / gpt-4.1-nano | 1024 | Text only, no tools | 5% |
| 1 | Free | Ollama local (deepseek-v3.1) | 2048 | Text only, local | 0% |

### Implementación

```python
# kernel/adaptive_quality.py
"""Sprint 66 — Adaptive Quality Engine."""
from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Optional
import structlog

logger = structlog.get_logger("kernel.adaptive_quality")


class QualityLevel(IntEnum):
    FREE = 1
    MINIMAL = 2
    ECONOMY = 3
    STANDARD = 4
    PREMIUM = 5


@dataclass
class QualityConfig:
    """Configuration for a specific quality level."""
    level: QualityLevel
    models: list[str]
    max_tokens: int
    tools_enabled: bool
    search_enabled: bool
    vision_enabled: bool
    max_retries: int
    cost_multiplier: float  # Relative to Premium (1.0)


# Quality level configurations
QUALITY_CONFIGS: dict[QualityLevel, QualityConfig] = {
    QualityLevel.PREMIUM: QualityConfig(
        level=QualityLevel.PREMIUM,
        models=["claude-opus-4-7", "gpt-4.1", "gemini-3.1-pro"],
        max_tokens=8192,
        tools_enabled=True,
        search_enabled=True,
        vision_enabled=True,
        max_retries=3,
        cost_multiplier=1.0,
    ),
    QualityLevel.STANDARD: QualityConfig(
        level=QualityLevel.STANDARD,
        models=["gpt-4.1-mini", "gemini-3.1-flash", "grok-4.1-fast"],
        max_tokens=4096,
        tools_enabled=True,
        search_enabled=True,
        vision_enabled=False,
        max_retries=2,
        cost_multiplier=0.4,
    ),
    QualityLevel.ECONOMY: QualityConfig(
        level=QualityLevel.ECONOMY,
        models=["grok-4.1-fast", "groq-llama-scout", "gemini-3.1-flash-lite"],
        max_tokens=2048,
        tools_enabled=True,
        search_enabled=False,
        vision_enabled=False,
        max_retries=1,
        cost_multiplier=0.15,
    ),
    QualityLevel.MINIMAL: QualityConfig(
        level=QualityLevel.MINIMAL,
        models=["gemini-3.1-flash-lite", "gpt-4.1-nano"],
        max_tokens=1024,
        tools_enabled=False,
        search_enabled=False,
        vision_enabled=False,
        max_retries=1,
        cost_multiplier=0.05,
    ),
    QualityLevel.FREE: QualityConfig(
        level=QualityLevel.FREE,
        models=["ollama/deepseek-v3.1:671b", "ollama/llama-4-scout"],
        max_tokens=2048,
        tools_enabled=False,
        search_enabled=False,
        vision_enabled=False,
        max_retries=1,
        cost_multiplier=0.0,
    ),
}


class AdaptiveQualityEngine:
    """
    Dynamically adjusts quality level based on budget consumption.
    
    Integration with FinOps:
    - Reads current daily/monthly spend from FinOpsController
    - Calculates remaining budget and projected exhaustion
    - Degrades quality BEFORE hitting hard stop
    - Notifies user of quality changes
    
    Thresholds (% of daily budget consumed):
    - 0-60%: Premium (Level 5)
    - 60-75%: Standard (Level 4)
    - 75-85%: Economy (Level 3)
    - 85-95%: Minimal (Level 2)
    - 95-100%: Free/Local (Level 1)
    """
    
    DEGRADATION_THRESHOLDS = {
        QualityLevel.PREMIUM: 0.60,   # Up to 60% budget → Premium
        QualityLevel.STANDARD: 0.75,  # 60-75% → Standard
        QualityLevel.ECONOMY: 0.85,   # 75-85% → Economy
        QualityLevel.MINIMAL: 0.95,   # 85-95% → Minimal
        QualityLevel.FREE: 1.00,      # 95-100% → Free
    }
    
    def __init__(self, finops: Any, alerts: Any = None) -> None:
        self._finops = finops
        self._alerts = alerts
        self._current_level = QualityLevel.PREMIUM
        self._override: Optional[QualityLevel] = None  # Manual override
        self._degradation_history: list[dict] = []
    
    async def get_current_quality(self) -> QualityConfig:
        """Calculate current quality level based on budget state."""
        if self._override:
            return QUALITY_CONFIGS[self._override]
        
        budget_state = self._finops.check_budget()
        daily_spent = budget_state.get("daily_cost", 0.0)
        daily_limit = budget_state.get("daily_limit", 15.0)
        consumption_ratio = daily_spent / daily_limit if daily_limit > 0 else 1.0
        
        # Determine quality level from consumption
        new_level = QualityLevel.FREE  # Default to free
        for level in sorted(self.DEGRADATION_THRESHOLDS.keys(), reverse=True):
            threshold = self.DEGRADATION_THRESHOLDS[level]
            if consumption_ratio < threshold:
                new_level = level
                break
        
        # Log degradation events
        if new_level != self._current_level:
            direction = "degraded" if new_level < self._current_level else "upgraded"
            logger.info("quality_level_changed",
                       previous=self._current_level.name,
                       new=new_level.name,
                       direction=direction,
                       consumption_ratio=f"{consumption_ratio:.2%}")
            
            self._degradation_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "from": self._current_level.name,
                "to": new_level.name,
                "consumption": consumption_ratio,
            })
            
            # Alert user on degradation
            if direction == "degraded" and self._alerts:
                await self._alerts.send(
                    f"⚡ Quality degraded: {self._current_level.name} → {new_level.name} "
                    f"(budget at {consumption_ratio:.0%})"
                )
            
            self._current_level = new_level
        
        return QUALITY_CONFIGS[self._current_level]
    
    async def predict_exhaustion(self) -> dict:
        """Predict when budget will be exhausted at current burn rate."""
        budget_state = self._finops.check_budget()
        burn_rate = budget_state.get("burn_rate_per_hour", 0.0)
        remaining = budget_state.get("daily_remaining", 15.0)
        
        if burn_rate <= 0:
            return {"hours_remaining": float("inf"), "exhaustion_time": None}
        
        hours_remaining = remaining / burn_rate
        exhaustion_time = datetime.now(timezone.utc) + timedelta(hours=hours_remaining)
        
        return {
            "hours_remaining": round(hours_remaining, 1),
            "exhaustion_time": exhaustion_time.isoformat(),
            "current_level": self._current_level.name,
            "burn_rate_per_hour": round(burn_rate, 4),
            "recommendation": self._get_recommendation(hours_remaining),
        }
    
    def _get_recommendation(self, hours_remaining: float) -> str:
        if hours_remaining > 8:
            return "Budget healthy. Continue at current quality."
        elif hours_remaining > 4:
            return "Consider reducing non-essential operations."
        elif hours_remaining > 1:
            return "Degradation imminent. Prioritize critical tasks only."
        else:
            return "Budget critical. Operating in minimal/free mode."
    
    def set_override(self, level: QualityLevel) -> None:
        """Manual override for quality level (e.g., force Premium for demo)."""
        self._override = level
        logger.info("quality_override_set", level=level.name)
    
    def clear_override(self) -> None:
        """Remove manual override, return to adaptive mode."""
        self._override = None
        logger.info("quality_override_cleared")
```

### Integración con Router

El `AdaptiveQualityEngine` se inyecta en el `Supervisor`. Antes de cada llamada LLM, el supervisor consulta `get_current_quality()` y selecciona el modelo del tier correspondiente. Esto reemplaza el hard stop actual con degradación progresiva.

---

## Épica 66.3 — Cross-Project Error Intelligence

**Objetivo:** Errores de un proyecto se propagan como prevención a TODOS los proyectos futuros.

**Dependencia de Obj #4:** Nunca equivocarse 2 veces = aprender GLOBALMENTE, no solo por embrión.

### Arquitectura

El sistema actual (Sprint 34) tiene lessons per-embrión almacenadas en Supabase. Sprint 66 agrega una capa de **generalización** que extrae patrones universales y los inyecta preventivamente.

```python
# kernel/error_intelligence.py
"""Sprint 66 — Cross-Project Error Intelligence."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime, timezone, timedelta
import structlog

logger = structlog.get_logger("kernel.error_intelligence")


@dataclass
class ErrorPattern:
    """A generalized error pattern extracted from specific incidents."""
    id: str
    pattern_description: str        # "React useEffect missing dependency"
    trigger_conditions: list[str]   # ["framework=react", "hook=useEffect"]
    prevention_rule: str            # "Always include all referenced variables in deps array"
    confidence: float               # 0.0-1.0, decays over time
    source_projects: list[str]      # Projects where this was observed
    occurrence_count: int
    last_seen: str
    created_at: str


class CrossProjectErrorIntelligence:
    """
    Extracts, generalizes, and injects error prevention across projects.
    
    Pipeline:
    1. OBSERVE: Error occurs in project X
    2. CLASSIFY: What type of error? (syntax, logic, integration, config)
    3. GENERALIZE: Extract universal pattern (remove project-specific details)
    4. STORE: Save pattern with trigger conditions
    5. INJECT: Before generating code for project Y, check if trigger conditions match
    6. PREVENT: Include prevention rule in generation prompt
    7. DECAY: Old patterns lose confidence over time
    """
    
    CONFIDENCE_DECAY_RATE = 0.02  # Lose 2% confidence per week without occurrence
    MIN_CONFIDENCE = 0.3          # Below this, pattern is archived
    GENERALIZATION_THRESHOLD = 2  # Need 2+ occurrences to generalize
    
    def __init__(self, db: Any, llm: Any) -> None:
        self._db = db
        self._llm = llm
        self._patterns: list[ErrorPattern] = []
        self._injection_cache: dict[str, list[str]] = {}  # context_hash -> rules
    
    async def observe_error(self, error: dict) -> Optional[ErrorPattern]:
        """
        Process a new error and potentially create/update a pattern.
        
        Args:
            error: {
                "project_id": str,
                "error_type": str,
                "error_message": str,
                "code_context": str,  # Surrounding code
                "stack_trace": str,
                "framework": str,
                "language": str,
            }
        """
        # Step 1: Check if this matches an existing pattern
        existing = await self._find_matching_pattern(error)
        
        if existing:
            # Update existing pattern
            existing.occurrence_count += 1
            existing.last_seen = datetime.now(timezone.utc).isoformat()
            existing.confidence = min(1.0, existing.confidence + 0.1)
            if error["project_id"] not in existing.source_projects:
                existing.source_projects.append(error["project_id"])
            await self._persist_pattern(existing)
            logger.info("error_pattern_reinforced",
                       pattern_id=existing.id,
                       occurrences=existing.occurrence_count)
            return existing
        
        # Step 2: Check if we have enough similar errors to generalize
        similar_errors = await self._find_similar_errors(error)
        if len(similar_errors) >= self.GENERALIZATION_THRESHOLD:
            # Step 3: Generalize into a new pattern
            pattern = await self._generalize_pattern(error, similar_errors)
            self._patterns.append(pattern)
            await self._persist_pattern(pattern)
            logger.info("error_pattern_created",
                       pattern_id=pattern.id,
                       description=pattern.pattern_description)
            return pattern
        
        # Not enough data yet — store raw error for future generalization
        await self._store_raw_error(error)
        return None
    
    async def get_prevention_rules(self, context: dict) -> list[str]:
        """
        Get applicable prevention rules for a given code generation context.
        
        Args:
            context: {
                "framework": str,
                "language": str,
                "task_type": str,  # "component", "api", "config", etc.
                "libraries": list[str],
            }
        
        Returns:
            List of prevention rules to inject into the generation prompt.
        """
        applicable_rules = []
        
        for pattern in self._patterns:
            if pattern.confidence < self.MIN_CONFIDENCE:
                continue
            
            # Check if trigger conditions match context
            if self._conditions_match(pattern.trigger_conditions, context):
                applicable_rules.append(
                    f"⚠️ PREVENTION [{pattern.confidence:.0%}]: {pattern.prevention_rule}"
                )
        
        # Sort by confidence (highest first)
        applicable_rules.sort(key=lambda r: float(r.split("[")[1].split("%")[0]), reverse=True)
        
        # Limit to top 5 to avoid prompt bloat
        return applicable_rules[:5]
    
    async def decay_confidence(self) -> int:
        """
        Apply confidence decay to all patterns.
        Run weekly by Embrión-Vigía.
        
        Returns:
            Number of patterns archived (below MIN_CONFIDENCE).
        """
        archived = 0
        for pattern in self._patterns:
            weeks_since_seen = self._weeks_since(pattern.last_seen)
            decay = self.CONFIDENCE_DECAY_RATE * weeks_since_seen
            pattern.confidence = max(0.0, pattern.confidence - decay)
            
            if pattern.confidence < self.MIN_CONFIDENCE:
                await self._archive_pattern(pattern)
                archived += 1
        
        self._patterns = [p for p in self._patterns if p.confidence >= self.MIN_CONFIDENCE]
        logger.info("error_patterns_decayed", archived=archived, active=len(self._patterns))
        return archived
    
    async def _generalize_pattern(self, error: dict, similar: list[dict]) -> ErrorPattern:
        """Use LLM to extract universal pattern from specific errors."""
        prompt = f"""Analyze these {len(similar) + 1} similar errors and extract a UNIVERSAL pattern.

Current error:
- Type: {error['error_type']}
- Message: {error['error_message']}
- Framework: {error['framework']}
- Context: {error['code_context'][:500]}

Similar past errors:
{chr(10).join(f"- {e['error_message']} in {e['framework']}" for e in similar[:5])}

Extract:
1. pattern_description: One-line description of the pattern
2. trigger_conditions: List of conditions that predict this error (framework, library, task type)
3. prevention_rule: Clear instruction to PREVENT this error in future code generation

Respond in JSON format."""
        
        response = await self._llm.generate(prompt, response_format="json")
        data = response.parsed
        
        return ErrorPattern(
            id=f"pat_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            pattern_description=data["pattern_description"],
            trigger_conditions=data["trigger_conditions"],
            prevention_rule=data["prevention_rule"],
            confidence=0.6,  # Start at 60% for new patterns
            source_projects=[error["project_id"]] + [e.get("project_id", "") for e in similar],
            occurrence_count=len(similar) + 1,
            last_seen=datetime.now(timezone.utc).isoformat(),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
    
    def _conditions_match(self, conditions: list[str], context: dict) -> bool:
        """Check if pattern trigger conditions match current context."""
        for condition in conditions:
            key, value = condition.split("=", 1)
            if key in context:
                if isinstance(context[key], list):
                    if value not in context[key]:
                        return False
                elif context[key].lower() != value.lower():
                    return False
        return True
```

### Integración con Task Planner

Antes de que el `TaskPlanner` genere código, consulta `get_prevention_rules()` con el contexto del proyecto actual. Las reglas se inyectan como instrucciones adicionales en el prompt de generación, previniendo errores conocidos ANTES de que ocurran.

---

## Épica 66.4 — Scenario Simulator v3

**Objetivo:** Simulador multi-variable con decision trees y portfolio simulation.

**Dependencia de Obj #10:** Simulador Predictivo completo = multi-variable + decisiones + portfolio.

### Expansión sobre Monte Carlo v2 (Sprint 60)

| Feature | v2 (Sprint 60) | v3 (Sprint 66) |
|---------|----------------|----------------|
| Variables | 1 por simulación | N simultáneas (correlacionadas) |
| Distribuciones | 6 (Beta, Normal, etc.) | 6 + custom empirical |
| Decision Trees | No | Sí (if/then branching) |
| Portfolio | No | Sí (N negocios simultáneos) |
| What-If API | No | Sí (endpoint interactivo) |
| Correlation | No | Sí (Copula gaussiana) |

### Implementación

```python
# kernel/simulator/scenario_v3.py
"""Sprint 66 — Scenario Simulator v3: Multi-Variable + Decision Trees."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
import numpy as np
from scipy import stats
import structlog

logger = structlog.get_logger("kernel.simulator.v3")

N_SIMULATIONS = 10_000


@dataclass
class Variable:
    """A single variable in the simulation."""
    name: str
    distribution: str  # "beta", "normal", "lognormal", "empirical", etc.
    params: dict       # Distribution-specific parameters
    description: str = ""


@dataclass
class DecisionNode:
    """A node in a decision tree."""
    id: str
    condition: str          # "revenue > 50000"
    true_branch: str        # Next node ID or "OUTCOME:success"
    false_branch: str       # Next node ID or "OUTCOME:failure"
    probability_override: Optional[float] = None  # If set, use this instead of condition


@dataclass
class Scenario:
    """A complete multi-variable scenario with optional decision tree."""
    name: str
    description: str
    variables: list[Variable]
    correlation_matrix: Optional[np.ndarray] = None  # NxN correlation matrix
    decision_tree: Optional[list[DecisionNode]] = None
    success_condition: str = ""  # Python expression using variable names
    time_horizon_months: int = 12


@dataclass
class SimulationResult:
    """Results from running a scenario simulation."""
    scenario_name: str
    n_simulations: int
    success_probability: float
    expected_value: dict[str, float]  # Variable name -> mean outcome
    percentiles: dict[str, dict[str, float]]  # Variable -> {p5, p25, p50, p75, p95}
    decision_outcomes: Optional[dict[str, float]] = None  # Outcome -> probability
    sensitivity: Optional[dict[str, float]] = None  # Variable -> impact on success
    portfolio_correlation: Optional[float] = None


class ScenarioSimulatorV3:
    """
    Multi-variable scenario simulator with decision trees and portfolio support.
    
    Capabilities:
    - Simulate N correlated variables simultaneously
    - Navigate decision trees based on simulated outcomes
    - Run portfolio simulations (multiple businesses)
    - Sensitivity analysis (which variable matters most)
    - What-if queries (change one variable, see impact)
    """
    
    def __init__(self, causal_kb: Any = None) -> None:
        self._causal_kb = causal_kb  # For loading calibrated distributions
        self._rng = np.random.default_rng(seed=42)
    
    async def simulate(self, scenario: Scenario, n: int = N_SIMULATIONS) -> SimulationResult:
        """Run full multi-variable simulation."""
        # Step 1: Generate correlated samples
        samples = self._generate_correlated_samples(scenario, n)
        
        # Step 2: If decision tree exists, navigate it for each simulation
        if scenario.decision_tree:
            outcomes = self._navigate_decision_tree(scenario, samples)
        else:
            outcomes = None
        
        # Step 3: Evaluate success condition
        successes = self._evaluate_success(scenario, samples)
        success_prob = np.mean(successes)
        
        # Step 4: Calculate statistics
        percentiles = {}
        expected_values = {}
        for i, var in enumerate(scenario.variables):
            col = samples[:, i]
            expected_values[var.name] = float(np.mean(col))
            percentiles[var.name] = {
                "p5": float(np.percentile(col, 5)),
                "p25": float(np.percentile(col, 25)),
                "p50": float(np.percentile(col, 50)),
                "p75": float(np.percentile(col, 75)),
                "p95": float(np.percentile(col, 95)),
            }
        
        # Step 5: Sensitivity analysis
        sensitivity = self._sensitivity_analysis(scenario, samples, successes)
        
        return SimulationResult(
            scenario_name=scenario.name,
            n_simulations=n,
            success_probability=float(success_prob),
            expected_value=expected_values,
            percentiles=percentiles,
            decision_outcomes=outcomes,
            sensitivity=sensitivity,
        )
    
    def _generate_correlated_samples(self, scenario: Scenario, n: int) -> np.ndarray:
        """Generate N samples for all variables with correlations."""
        num_vars = len(scenario.variables)
        
        if scenario.correlation_matrix is not None:
            # Use Gaussian copula for correlated samples
            corr = scenario.correlation_matrix
            # Generate correlated normal samples
            normal_samples = self._rng.multivariate_normal(
                mean=np.zeros(num_vars),
                cov=corr,
                size=n,
            )
            # Transform to uniform via CDF
            uniform_samples = stats.norm.cdf(normal_samples)
        else:
            # Independent samples
            uniform_samples = self._rng.uniform(size=(n, num_vars))
        
        # Transform uniform to target distributions
        samples = np.zeros((n, num_vars))
        for i, var in enumerate(scenario.variables):
            dist = self._get_distribution(var)
            samples[:, i] = dist.ppf(uniform_samples[:, i])
        
        return samples
    
    def _get_distribution(self, var: Variable) -> Any:
        """Get scipy distribution from variable spec."""
        dist_map = {
            "beta": lambda p: stats.beta(p["a"], p["b"], loc=p.get("loc", 0), scale=p.get("scale", 1)),
            "normal": lambda p: stats.norm(p["mean"], p["std"]),
            "lognormal": lambda p: stats.lognorm(p["sigma"], scale=np.exp(p["mu"])),
            "uniform": lambda p: stats.uniform(p["low"], p["high"] - p["low"]),
            "triangular": lambda p: stats.triang((p["mode"] - p["low"]) / (p["high"] - p["low"]),
                                                  loc=p["low"], scale=p["high"] - p["low"]),
            "poisson": lambda p: stats.poisson(p["mu"]),
        }
        return dist_map[var.distribution](var.params)
    
    def _navigate_decision_tree(self, scenario: Scenario, samples: np.ndarray) -> dict[str, float]:
        """Navigate decision tree for each simulation run."""
        outcome_counts: dict[str, int] = {}
        n = samples.shape[0]
        
        for i in range(n):
            # Create variable context for this run
            context = {var.name: samples[i, j] for j, var in enumerate(scenario.variables)}
            
            # Navigate tree
            current_node = scenario.decision_tree[0]
            max_depth = 20  # Prevent infinite loops
            depth = 0
            
            while depth < max_depth:
                # Evaluate condition
                try:
                    condition_met = eval(current_node.condition, {"__builtins__": {}}, context)
                except Exception:
                    condition_met = False
                
                next_id = current_node.true_branch if condition_met else current_node.false_branch
                
                if next_id.startswith("OUTCOME:"):
                    outcome = next_id.replace("OUTCOME:", "")
                    outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
                    break
                
                # Find next node
                current_node = next(
                    (node for node in scenario.decision_tree if node.id == next_id),
                    None,
                )
                if not current_node:
                    outcome_counts["unknown"] = outcome_counts.get("unknown", 0) + 1
                    break
                depth += 1
        
        # Convert to probabilities
        return {k: v / n for k, v in outcome_counts.items()}
    
    def _sensitivity_analysis(self, scenario: Scenario, samples: np.ndarray,
                             successes: np.ndarray) -> dict[str, float]:
        """Calculate which variable has the most impact on success."""
        sensitivity = {}
        
        for i, var in enumerate(scenario.variables):
            # Correlation between variable values and success
            correlation = np.corrcoef(samples[:, i], successes.astype(float))[0, 1]
            sensitivity[var.name] = abs(float(correlation))
        
        # Normalize to sum to 1
        total = sum(sensitivity.values())
        if total > 0:
            sensitivity = {k: v / total for k, v in sensitivity.items()}
        
        return dict(sorted(sensitivity.items(), key=lambda x: x[1], reverse=True))
    
    async def what_if(self, scenario: Scenario, variable_name: str,
                      new_value: float) -> dict:
        """
        What-if query: fix one variable, simulate the rest.
        
        "If my conversion rate is 5% instead of 3%, what happens?"
        """
        # Find variable index
        var_idx = next(
            (i for i, v in enumerate(scenario.variables) if v.name == variable_name),
            None,
        )
        if var_idx is None:
            return {"error": f"Variable {variable_name} not found"}
        
        # Run simulation with fixed variable
        samples = self._generate_correlated_samples(scenario, N_SIMULATIONS)
        samples[:, var_idx] = new_value  # Fix this variable
        
        successes = self._evaluate_success(scenario, samples)
        
        # Compare with baseline
        baseline = await self.simulate(scenario)
        
        return {
            "variable": variable_name,
            "fixed_value": new_value,
            "success_probability": float(np.mean(successes)),
            "baseline_probability": baseline.success_probability,
            "delta": float(np.mean(successes)) - baseline.success_probability,
            "interpretation": self._interpret_what_if(
                variable_name, new_value, float(np.mean(successes)), baseline.success_probability
            ),
        }
    
    async def portfolio_simulate(self, scenarios: list[Scenario],
                                 correlation: float = 0.3) -> dict:
        """
        Simulate multiple businesses simultaneously.
        
        Models the probability that at least 1 out of N businesses succeeds.
        """
        n_businesses = len(scenarios)
        results = []
        
        for scenario in scenarios:
            result = await self.simulate(scenario)
            results.append(result)
        
        # Portfolio success = at least 1 succeeds
        # With correlation, use copula
        individual_probs = [r.success_probability for r in results]
        
        # Simulate correlated Bernoulli outcomes
        corr_matrix = np.full((n_businesses, n_businesses), correlation)
        np.fill_diagonal(corr_matrix, 1.0)
        
        normal_samples = self._rng.multivariate_normal(
            mean=np.zeros(n_businesses), cov=corr_matrix, size=N_SIMULATIONS
        )
        uniform_samples = stats.norm.cdf(normal_samples)
        
        # Convert to binary outcomes based on individual probabilities
        outcomes = np.zeros((N_SIMULATIONS, n_businesses))
        for i, prob in enumerate(individual_probs):
            outcomes[:, i] = (uniform_samples[:, i] < prob).astype(float)
        
        # At least one success
        portfolio_success = np.any(outcomes > 0, axis=1).mean()
        
        return {
            "n_businesses": n_businesses,
            "individual_probabilities": {s.name: p for s, p in zip(scenarios, individual_probs)},
            "portfolio_success_probability": float(portfolio_success),
            "correlation_assumed": correlation,
            "diversification_benefit": float(portfolio_success) - max(individual_probs),
            "results": [r.__dict__ for r in results],
        }
```

### API Endpoint

```python
# En router de FastAPI
@app.post("/api/simulate/scenario")
async def simulate_scenario(request: ScenarioRequest) -> SimulationResult:
    """Run a multi-variable scenario simulation."""
    scenario = Scenario(**request.dict())
    return await simulator_v3.simulate(scenario)

@app.post("/api/simulate/what-if")
async def what_if_query(request: WhatIfRequest) -> dict:
    """Run a what-if query on a scenario."""
    return await simulator_v3.what_if(request.scenario, request.variable, request.value)

@app.post("/api/simulate/portfolio")
async def portfolio_simulation(request: PortfolioRequest) -> dict:
    """Simulate multiple businesses as a portfolio."""
    return await simulator_v3.portfolio_simulate(request.scenarios, request.correlation)
```

---

## Épica 66.5 — Self-Healing Infrastructure

**Objetivo:** Auto-recovery de servicios caídos sin intervención humana.

**Dependencia de Obj #12:** Soberanía operativa = no depender de humanos para recovery.

### Arquitectura de Self-Healing

```python
# kernel/self_healing.py
"""Sprint 66 — Self-Healing Infrastructure."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from datetime import datetime, timezone, timedelta
import asyncio
import structlog

logger = structlog.get_logger("kernel.self_healing")


class ServiceState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    RECOVERING = "recovering"


@dataclass
class HealthCheck:
    """Definition of a health check for a service."""
    name: str
    check_fn: Callable  # async function that returns True/False
    interval_seconds: int = 30
    timeout_seconds: int = 10
    failure_threshold: int = 3  # Consecutive failures before marking DOWN
    recovery_threshold: int = 2  # Consecutive successes before marking HEALTHY


@dataclass
class RecoveryAction:
    """An action to take when a service is down."""
    name: str
    action_fn: Callable  # async function to execute
    max_attempts: int = 3
    backoff_base: float = 2.0  # Exponential backoff base
    cooldown_seconds: int = 300  # Min time between recovery attempts


@dataclass
class ServiceHealth:
    """Current health state of a service."""
    service_name: str
    state: ServiceState = ServiceState.HEALTHY
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_check: Optional[str] = None
    last_recovery_attempt: Optional[str] = None
    recovery_attempts: int = 0
    incidents: list[dict] = field(default_factory=list)


class SelfHealingEngine:
    """
    Autonomous self-healing infrastructure.
    
    Responsibilities:
    - Monitor all critical services via health checks
    - Detect failures (consecutive check failures)
    - Execute recovery actions with exponential backoff
    - Cascade checks (if A fails, check B, C, D)
    - Generate incident timelines
    - Auto-generate post-mortem reports
    """
    
    def __init__(self, alerts: Any = None, db: Any = None) -> None:
        self._alerts = alerts
        self._db = db
        self._health_checks: dict[str, HealthCheck] = {}
        self._recovery_actions: dict[str, list[RecoveryAction]] = {}
        self._service_health: dict[str, ServiceHealth] = {}
        self._cascade_map: dict[str, list[str]] = {}  # service -> dependent services
        self._running = False
        self._tasks: list[asyncio.Task] = []
    
    def register_service(self, name: str, check: HealthCheck,
                        recovery_actions: list[RecoveryAction],
                        depends_on: Optional[list[str]] = None) -> None:
        """Register a service for monitoring."""
        self._health_checks[name] = check
        self._recovery_actions[name] = recovery_actions
        self._service_health[name] = ServiceHealth(service_name=name)
        
        if depends_on:
            for dep in depends_on:
                if dep not in self._cascade_map:
                    self._cascade_map[dep] = []
                self._cascade_map[dep].append(name)
    
    async def start(self) -> None:
        """Start all health check loops."""
        self._running = True
        for name, check in self._health_checks.items():
            task = asyncio.create_task(self._monitor_loop(name, check))
            self._tasks.append(task)
        logger.info("self_healing_started", services=len(self._health_checks))
    
    async def stop(self) -> None:
        """Stop all monitoring."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()
    
    async def _monitor_loop(self, service_name: str, check: HealthCheck) -> None:
        """Continuous monitoring loop for a single service."""
        while self._running:
            try:
                # Execute health check with timeout
                healthy = await asyncio.wait_for(
                    check.check_fn(),
                    timeout=check.timeout_seconds,
                )
            except (asyncio.TimeoutError, Exception) as e:
                healthy = False
                logger.warning("health_check_failed",
                             service=service_name, error=str(e))
            
            health = self._service_health[service_name]
            health.last_check = datetime.now(timezone.utc).isoformat()
            
            if healthy:
                health.consecutive_successes += 1
                health.consecutive_failures = 0
                
                if (health.state != ServiceState.HEALTHY and
                    health.consecutive_successes >= check.recovery_threshold):
                    # Service recovered
                    old_state = health.state
                    health.state = ServiceState.HEALTHY
                    health.recovery_attempts = 0
                    logger.info("service_recovered",
                              service=service_name, from_state=old_state.value)
                    
                    if self._alerts:
                        await self._alerts.send(
                            f"✅ {service_name} recovered (was {old_state.value})"
                        )
                    
                    # Record incident end
                    if health.incidents and not health.incidents[-1].get("resolved_at"):
                        health.incidents[-1]["resolved_at"] = health.last_check
            else:
                health.consecutive_failures += 1
                health.consecutive_successes = 0
                
                if health.consecutive_failures >= check.failure_threshold:
                    if health.state == ServiceState.HEALTHY:
                        # New incident
                        health.state = ServiceState.DOWN
                        health.incidents.append({
                            "started_at": health.last_check,
                            "resolved_at": None,
                            "recovery_actions": [],
                        })
                        
                        logger.error("service_down",
                                   service=service_name,
                                   failures=health.consecutive_failures)
                        
                        if self._alerts:
                            await self._alerts.send(
                                f"🚨 {service_name} is DOWN "
                                f"({health.consecutive_failures} consecutive failures)"
                            )
                        
                        # Cascade check
                        await self._cascade_check(service_name)
                    
                    # Attempt recovery
                    await self._attempt_recovery(service_name)
            
            await asyncio.sleep(check.interval_seconds)
    
    async def _attempt_recovery(self, service_name: str) -> None:
        """Execute recovery actions with exponential backoff."""
        health = self._service_health[service_name]
        actions = self._recovery_actions.get(service_name, [])
        
        if not actions:
            return
        
        # Check cooldown
        if health.last_recovery_attempt:
            last_attempt = datetime.fromisoformat(health.last_recovery_attempt)
            cooldown = actions[0].cooldown_seconds
            elapsed = (datetime.now(timezone.utc) - last_attempt).total_seconds()
            
            # Exponential backoff
            backoff = cooldown * (actions[0].backoff_base ** health.recovery_attempts)
            if elapsed < backoff:
                return  # Still in cooldown
        
        # Select recovery action based on attempt number
        action_idx = min(health.recovery_attempts, len(actions) - 1)
        action = actions[action_idx]
        
        if health.recovery_attempts >= action.max_attempts:
            logger.error("recovery_exhausted",
                       service=service_name,
                       attempts=health.recovery_attempts)
            if self._alerts:
                await self._alerts.send(
                    f"⛔ {service_name}: All recovery attempts exhausted. "
                    f"Manual intervention required."
                )
            return
        
        # Execute recovery
        health.state = ServiceState.RECOVERING
        health.last_recovery_attempt = datetime.now(timezone.utc).isoformat()
        health.recovery_attempts += 1
        
        logger.info("recovery_attempt",
                   service=service_name,
                   action=action.name,
                   attempt=health.recovery_attempts)
        
        try:
            await action.action_fn()
            # Record in incident
            if health.incidents:
                health.incidents[-1]["recovery_actions"].append({
                    "action": action.name,
                    "attempt": health.recovery_attempts,
                    "timestamp": health.last_recovery_attempt,
                    "result": "executed",
                })
        except Exception as e:
            logger.error("recovery_action_failed",
                       service=service_name, action=action.name, error=str(e))
    
    async def _cascade_check(self, failed_service: str) -> None:
        """Check dependent services when a service fails."""
        dependents = self._cascade_map.get(failed_service, [])
        for dep in dependents:
            check = self._health_checks.get(dep)
            if check:
                try:
                    healthy = await asyncio.wait_for(
                        check.check_fn(), timeout=check.timeout_seconds
                    )
                    if not healthy:
                        logger.warning("cascade_failure_detected",
                                     root=failed_service, affected=dep)
                except Exception:
                    logger.warning("cascade_check_failed",
                                 root=failed_service, affected=dep)
    
    async def generate_post_mortem(self, service_name: str,
                                   incident_index: int = -1) -> dict:
        """Generate automatic post-mortem for an incident."""
        health = self._service_health.get(service_name)
        if not health or not health.incidents:
            return {"error": "No incidents found"}
        
        incident = health.incidents[incident_index]
        
        duration = None
        if incident.get("resolved_at"):
            start = datetime.fromisoformat(incident["started_at"])
            end = datetime.fromisoformat(incident["resolved_at"])
            duration = (end - start).total_seconds()
        
        return {
            "service": service_name,
            "started_at": incident["started_at"],
            "resolved_at": incident.get("resolved_at", "ONGOING"),
            "duration_seconds": duration,
            "recovery_actions_taken": incident.get("recovery_actions", []),
            "root_cause": "Auto-detected failure (see health check logs)",
            "impact": f"Service {service_name} unavailable",
            "lessons_learned": [
                f"Recovery action #{i+1} ({a['action']}) "
                f"{'succeeded' if i == len(incident.get('recovery_actions', [])) - 1 else 'failed'}"
                for i, a in enumerate(incident.get("recovery_actions", []))
            ],
        }
    
    def get_status(self) -> dict:
        """Get current health status of all services."""
        return {
            name: {
                "state": health.state.value,
                "consecutive_failures": health.consecutive_failures,
                "last_check": health.last_check,
                "recovery_attempts": health.recovery_attempts,
                "total_incidents": len(health.incidents),
            }
            for name, health in self._service_health.items()
        }
```

### Servicios Registrados por Default

| Servicio | Health Check | Recovery Actions (en orden) |
|----------|-------------|---------------------------|
| Supabase DB | `SELECT 1` query | 1. Reconnect pool, 2. Restart connection, 3. Switch to local SQLite |
| LLM Router | Test completion (1 token) | 1. Retry with fallback model, 2. Clear cache, 3. Switch to Ollama |
| Telegram Bot | `getMe` API call | 1. Recreate webhook, 2. Restart bot loop |
| MCP Server | `/mcp` health endpoint | 1. Restart FastMCP, 2. Reload tools |
| Embrión Loop | Check last heartbeat | 1. Resume loop, 2. Restart with fresh state |

---

## Dependencias Nuevas

| Paquete | Versión | Propósito | Costo |
|---------|---------|-----------|-------|
| networkx | ~3.4 | Decision trees en Simulator v3 | $0 (MIT) |
| tenacity | ~9.0 | Retry patterns en Self-Healing | $0 (Apache 2.0) |

Ambos son lightweight y no agregan dependencias transitivas significativas. `scipy` y `numpy` ya están en el stack.

---

## Costo Estimado

| Componente | Costo Mensual |
|-----------|---------------|
| Sovereignty validation (weekly LLM calls) | ~$1-2 |
| Cross-project error generalization (LLM) | ~$2-5 |
| Simulator v3 (compute, no LLM) | $0 |
| Self-healing (no LLM, just checks) | $0 |
| Adaptive quality (reduces costs!) | -$5 to -$15 (savings) |
| **Total neto** | **-$2 to -$8 (AHORRO)** |

Sprint 66 es el primer sprint que AHORRA dinero — el Adaptive Quality Engine reduce costos netos al degradar gracefully en lugar de consumir Premium siempre.

---

## Criterios de Éxito

| Criterio | Métrica | Target |
|----------|---------|--------|
| Sovereignty readiness | Playbooks validados | 6/8 (75%) |
| Quality degradation | Tiempo sin hard-stop | 0 hard-stops en 7 días |
| Error prevention | Patterns activos | >10 patterns con >60% confidence |
| Simulator accuracy | Brier score (backtested) | <0.25 |
| Self-healing MTTR | Mean time to recovery | <5 minutos |

---

## Referencias

[1]: Sprint 15 — FinOps Controller (`kernel/finops.py`)
[2]: Sprint 29 — Fallback Engine (`kernel/fallback_engine.py`)
[3]: Sprint 34 — Embrión Lesson Learning (`kernel/embrion_loop.py`)
[4]: Sprint 55 — Monte Carlo Simulator v1 (plan)
[5]: Sprint 60 — Simulator v2 + Sovereignty Engine (plan)
[6]: scipy.stats documentation — https://docs.scipy.org/doc/scipy/reference/stats.html
[7]: networkx documentation — https://networkx.org/documentation/stable/
