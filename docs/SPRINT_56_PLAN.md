# Sprint 56 — "El Ciclo Perpetuo"

**Fecha de planificación:** 1 mayo 2026
**Pre-requisito:** Sprints 51-55 completados (Cimientos → Manos → Transversales → Emergencia → Tejido Causal)
**Capa:** 2 — Inteligencia Emergente (consolidación) + 4 — Soberanía Operativa
**Objetivos primarios:** #10 (Simulador Predictivo — feedback loop), #8 (Inteligencia Emergente — autonomía)
**Objetivos secundarios:** #4 (Nunca se equivoca dos veces), #12 (Ecosistema — soberanía)
**Duración estimada:** 8-12 días

---

## Contexto Técnico Actual (Validado contra código real)

Sprint 55 dejó el Simulador Causal como prototipo funcional pero vacío — la Causal KB no tiene datos, el Decomposer no tiene trigger automático, y no hay feedback loop. El Embrión ya respira (Sprint 33C) pero no tiene autonomía para auto-asignarse tareas ni alimentar el sistema causal. Sprint 56 cierra estos ciclos.

| Componente | Estado | Archivo |
|---|---|---|
| Embrión Loop | Ciclo autónomo con budget, silencio, judge | `kernel/embrion_loop.py` (Sprint 33C) |
| Langfuse Bridge | Tracing a Langfuse v4, CallbackHandler | `observability/langfuse_bridge.py` (Sprint 13) |
| Causal KB | Tabla + embeddings + búsqueda semántica | Sprint 55 (vacía, sin datos) |
| Causal Decomposer | Motor multi-modelo para factores | Sprint 55 (sin trigger automático) |
| Monte Carlo Simulator | Distribuciones Beta, 10K sims | Sprint 55 (sin datos históricos) |
| Embrión Routes | CRUD + heartbeat + mensajes | `kernel/embrion_routes.py` |
| A2A Registry | Discovery dinámico entre agentes | Sprint 55 |
| MCP Hub | 5 tools propias + presets externos | Sprint 55 |
| Event Store | Persistencia de eventos soberanos | `memory/event_store.py` |
| Thoughts Store | Pensamientos + embeddings | `memory/thoughts.py` |

**Lo que falta (y Sprint 56 resuelve):**
1. La Causal KB está vacía — necesita un pipeline de alimentación automática
2. El Simulador no tiene feedback loop — predice pero nunca valida
3. El Embrión no puede auto-asignarse tareas — solo reacciona a triggers
4. No hay modelo local como fallback soberano — 100% dependencia de APIs cloud
5. Langfuse existe pero no trackea Embriones individuales ni sus costos

---

## Épica 56.1 — Causal Seeder: Alimentación Automática de la Base Causal

**Objetivo:** Crear un pipeline autónomo que alimenta la Causal Knowledge Base con eventos históricos descompuestos en factores causales. El Embrión-Causal ejecuta este pipeline continuamente, acumulando conocimiento sin intervención humana.

**Meta cuantitativa:** 100+ eventos causales descompuestos en la primera semana de operación.

**Herramientas adoptadas (Obj #7):**
- Perplexity Sonar API — Ya en stack, para investigación en tiempo real
- Wikipedia API (`wikipedia-api` Python package) — Para eventos históricos estructurados
- APScheduler 3.11.2 — Para scheduling del pipeline

**Principio:** El simulador es tan bueno como sus datos. Sin datos históricos, predice en el vacío. El Seeder es la bomba de gasolina que alimenta el motor causal.

### Archivo nuevo: `kernel/causal_seeder.py`

```python
"""
El Monstruo — Causal Seeder Pipeline (Sprint 56)
=================================================
Pipeline autónomo que alimenta la Causal Knowledge Base.
Ejecuta en ciclos:
  1. Selecciona un dominio/tema del backlog
  2. Investiga eventos significativos (Perplexity + Wikipedia)
  3. Descompone cada evento en factores causales (Causal Decomposer)
  4. Almacena en Causal KB con embeddings
  5. Reporta progreso

Dominios prioritarios (para predicción de negocios):
  - Startups: éxitos y fracasos de startups tech (2010-2026)
  - Mercados: movimientos significativos de mercado
  - Tecnología: adopción masiva de tecnologías
  - Regulación: cambios regulatorios con impacto económico
  - Geopolítica: eventos geopolíticos con impacto en negocios

Budget: ~$0.50-1.00 por ciclo (embedding + decomposition)
Target: 10-15 eventos por ciclo, 3-4 ciclos por día = 30-60 eventos/día

Validated: Perplexity Sonar (ya en stack), APScheduler 3.11.2 (MIT)
"""
from __future__ import annotations

import asyncio
import json
import os
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("kernel.causal_seeder")


# ── Dominios de Seeding ──────────────────────────────────────────────

SEED_DOMAINS = [
    {
        "name": "startup_successes",
        "description": "Startups que alcanzaron unicorn status o IPO exitosa",
        "query_template": "List {n} significant startup successes from {year_range} with their key factors. Focus on: what caused their success, market timing, team composition, funding strategy, competitive advantages.",
        "category": "empresarial",
        "priority": 1,
    },
    {
        "name": "startup_failures",
        "description": "Startups que fracasaron a pesar de tener funding significativo",
        "query_template": "List {n} notable startup failures from {year_range} that had significant funding but failed. Focus on: root causes of failure, market timing issues, execution problems, competitive pressure.",
        "category": "empresarial",
        "priority": 1,
    },
    {
        "name": "market_crashes",
        "description": "Caídas significativas de mercado y sus causas",
        "query_template": "Describe {n} significant market crashes or corrections from {year_range}. For each: what triggered it, underlying causes, early warning signs, recovery factors.",
        "category": "economic",
        "priority": 2,
    },
    {
        "name": "tech_adoption",
        "description": "Tecnologías que alcanzaron adopción masiva",
        "query_template": "List {n} technologies that achieved mass adoption in {year_range}. For each: what drove adoption, barriers overcome, network effects, timing factors.",
        "category": "technological",
        "priority": 2,
    },
    {
        "name": "regulatory_shifts",
        "description": "Cambios regulatorios con impacto económico masivo",
        "query_template": "Describe {n} major regulatory changes from {year_range} that significantly impacted businesses. For each: what caused the regulation, economic impact, winners and losers.",
        "category": "political",
        "priority": 3,
    },
    {
        "name": "geopolitical_disruptions",
        "description": "Eventos geopolíticos que disrumpieron mercados",
        "query_template": "List {n} geopolitical events from {year_range} that significantly disrupted global markets or supply chains. For each: root causes, cascading effects, recovery timeline.",
        "category": "political",
        "priority": 3,
    },
    {
        "name": "ai_milestones",
        "description": "Hitos de AI que cambiaron industrias",
        "query_template": "Describe {n} AI milestones from {year_range} that transformed industries. For each: technical breakthrough, market impact, adoption speed, enabling factors.",
        "category": "technological",
        "priority": 1,
    },
]

YEAR_RANGES = ["2010-2015", "2015-2020", "2020-2023", "2023-2026"]


@dataclass
class SeedingCycle:
    """Registro de un ciclo de seeding."""
    cycle_id: str = field(default_factory=lambda: str(uuid4()))
    domain: str = ""
    events_discovered: int = 0
    events_decomposed: int = 0
    events_stored: int = 0
    cost_estimate_usd: float = 0.0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    errors: list[str] = field(default_factory=list)


class CausalSeeder:
    """
    Pipeline autónomo de alimentación de la Causal KB.
    Ejecuta ciclos de seeding que descubren, descomponen, y almacenan eventos.
    """

    MAX_EVENTS_PER_CYCLE = 15
    COST_PER_EVENT_USD = 0.05  # Estimado: embedding + decomposition
    DAILY_BUDGET_USD = float(os.environ.get("CAUSAL_SEEDER_DAILY_BUDGET", "5.0"))

    def __init__(self, decomposer=None, search_fn=None, db=None):
        """
        Args:
            decomposer: CausalDecomposer instance
            search_fn: Función de búsqueda web (Perplexity)
            db: Supabase client para tracking
        """
        self._decomposer = decomposer
        self._search = search_fn
        self._db = db
        self._daily_spend: float = 0.0
        self._daily_reset: Optional[str] = None
        self._cycles_completed: int = 0
        self._total_events_seeded: int = 0

    async def run_cycle(self, domain_name: Optional[str] = None) -> SeedingCycle:
        """
        Ejecutar un ciclo completo de seeding.
        Si no se especifica dominio, selecciona uno por prioridad + rotación.
        """
        self._check_daily_budget()
        
        cycle = SeedingCycle(started_at=datetime.now(timezone.utc).isoformat())
        
        # Seleccionar dominio
        domain = self._select_domain(domain_name)
        cycle.domain = domain["name"]
        
        logger.info("seeding_cycle_start", domain=domain["name"], cycle_id=cycle.cycle_id)

        try:
            # Paso 1: Descubrir eventos
            events_raw = await self._discover_events(domain)
            cycle.events_discovered = len(events_raw)

            # Paso 2: Descomponer cada evento
            for event_data in events_raw[:self.MAX_EVENTS_PER_CYCLE]:
                try:
                    await self._decompose_and_store(event_data, domain)
                    cycle.events_decomposed += 1
                    cycle.events_stored += 1
                    cycle.cost_estimate_usd += self.COST_PER_EVENT_USD
                    self._daily_spend += self.COST_PER_EVENT_USD
                except Exception as e:
                    cycle.errors.append(f"Decompose failed: {event_data.get('title', 'unknown')}: {str(e)}")
                    logger.warning("seeding_event_failed", error=str(e))

        except Exception as e:
            cycle.errors.append(f"Cycle failed: {str(e)}")
            logger.error("seeding_cycle_failed", error=str(e))

        cycle.completed_at = datetime.now(timezone.utc).isoformat()
        self._cycles_completed += 1
        self._total_events_seeded += cycle.events_stored

        logger.info(
            "seeding_cycle_complete",
            domain=domain["name"],
            discovered=cycle.events_discovered,
            stored=cycle.events_stored,
            cost=cycle.cost_estimate_usd,
            total_seeded=self._total_events_seeded,
        )

        return cycle

    def _select_domain(self, domain_name: Optional[str] = None) -> dict:
        """Seleccionar dominio por nombre o por rotación ponderada."""
        if domain_name:
            for d in SEED_DOMAINS:
                if d["name"] == domain_name:
                    return d

        # Selección ponderada por prioridad (priority 1 = más probable)
        weights = [1.0 / d["priority"] for d in SEED_DOMAINS]
        total = sum(weights)
        weights = [w / total for w in weights]
        
        return random.choices(SEED_DOMAINS, weights=weights, k=1)[0]

    async def _discover_events(self, domain: dict) -> list[dict[str, Any]]:
        """Descubrir eventos usando Perplexity."""
        if not self._search:
            logger.warning("seeder_no_search_fn")
            return []

        year_range = random.choice(YEAR_RANGES)
        query = domain["query_template"].format(
            n=self.MAX_EVENTS_PER_CYCLE,
            year_range=year_range,
        )

        result = await self._search(query)
        
        # Parsear resultado en eventos individuales
        events = self._parse_discovered_events(result, domain, year_range)
        return events

    def _parse_discovered_events(
        self, raw_result: str, domain: dict, year_range: str
    ) -> list[dict[str, Any]]:
        """Parsear resultado de búsqueda en eventos estructurados."""
        # El resultado de Perplexity viene como texto libre
        # Lo parseamos en eventos individuales
        events = []
        
        # Intentar parsear como JSON primero
        try:
            data = json.loads(raw_result)
            if isinstance(data, list):
                return data
            if "events" in data:
                return data["events"]
        except (json.JSONDecodeError, TypeError):
            pass

        # Fallback: split por líneas que parecen títulos de eventos
        lines = raw_result.split("\n") if isinstance(raw_result, str) else []
        current_event = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Heurística: líneas que empiezan con número o bullet son eventos
            if any(line.startswith(p) for p in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "- ", "* "]):
                if current_event:
                    events.append(current_event)
                current_event = {
                    "title": line.lstrip("0123456789.-* "),
                    "context": "",
                    "category": domain["category"],
                    "year_range": year_range,
                }
            elif current_event:
                current_event["context"] += " " + line

        if current_event:
            events.append(current_event)

        return events

    async def _decompose_and_store(self, event_data: dict, domain: dict) -> None:
        """Descomponer un evento y almacenarlo en la Causal KB."""
        if not self._decomposer:
            return

        await self._decomposer.decompose(
            title=event_data.get("title", ""),
            context=event_data.get("context", ""),
            category=domain["category"],
            event_date=event_data.get("date"),
            sources=["perplexity_seeder"],
            enrich_with_research=False,  # Ya investigamos, no duplicar
        )

    def _check_daily_budget(self) -> None:
        """Verificar que no excedemos el budget diario."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._daily_reset != today:
            self._daily_spend = 0.0
            self._daily_reset = today

        if self._daily_spend >= self.DAILY_BUDGET_USD:
            raise RuntimeError(
                f"Daily seeding budget exceeded: ${self._daily_spend:.2f} >= ${self.DAILY_BUDGET_USD:.2f}"
            )

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas del seeder."""
        return {
            "cycles_completed": self._cycles_completed,
            "total_events_seeded": self._total_events_seeded,
            "daily_spend_usd": round(self._daily_spend, 2),
            "daily_budget_usd": self.DAILY_BUDGET_USD,
            "budget_remaining_usd": round(self.DAILY_BUDGET_USD - self._daily_spend, 2),
        }
```

### Integración con Embrión Loop:

Agregar en `kernel/embrion_loop.py` un nuevo trigger:

```python
# ── Sprint 56: Causal Seeding Trigger ─────────────────────────────
async def _check_causal_seeding_trigger(self) -> bool:
    """
    Trigger: ejecutar un ciclo de seeding si:
      1. Han pasado >6 horas desde el último ciclo
      2. El budget diario no se ha agotado
      3. No hay tareas de mayor prioridad pendientes
    """
    seeder = getattr(self._app_state, "causal_seeder", None)
    if not seeder:
        return False
    
    stats = seeder.get_stats()
    if stats["budget_remaining_usd"] <= 0:
        return False
    
    # Verificar tiempo desde último ciclo
    last_cycle_time = getattr(self, "_last_seeding_cycle", None)
    if last_cycle_time:
        elapsed = (datetime.now(timezone.utc) - last_cycle_time).total_seconds()
        if elapsed < 6 * 3600:  # Mínimo 6 horas entre ciclos
            return False
    
    return True

async def _execute_causal_seeding(self) -> dict[str, Any]:
    """Ejecutar un ciclo de causal seeding."""
    seeder = getattr(self._app_state, "causal_seeder", None)
    if not seeder:
        return {"error": "Seeder not available"}
    
    cycle = await seeder.run_cycle()
    self._last_seeding_cycle = datetime.now(timezone.utc)
    
    return {
        "action": "causal_seeding",
        "events_stored": cycle.events_stored,
        "domain": cycle.domain,
        "cost": cycle.cost_estimate_usd,
    }
```

### Criterio de éxito:

- **T1:** `run_cycle()` descubre ≥5 eventos y los descompone en factores
- **T2:** Budget diario se respeta (hard stop cuando se agota)
- **T3:** Después de 7 días, Causal KB tiene ≥100 eventos con factores
- **T4:** Dominios rotan por prioridad (startups y AI más frecuentes)
- **T5:** Embrión Loop triggerea seeding automáticamente cada 6 horas

---

## Épica 56.2 — Prediction Validator: El Feedback Loop que Cierra el Ciclo

**Objetivo:** Implementar el ciclo de validación perpetua del Simulador Causal — cada predicción se registra con fecha de vencimiento, y cuando la fecha llega, el sistema investiga qué pasó realmente, compara con la predicción, y ajusta los pesos de los factores causales. Esto es la corrección C7 del cruce de Sprint 55.

**Herramientas adoptadas:**
- APScheduler 3.11.2 — Para cron job de validación diaria
- Perplexity Sonar — Para investigar outcomes reales
- Supabase — Para persistir predicciones y validaciones

**Principio:** Un simulador que nunca valida sus predicciones es un generador de ficción. El feedback loop es lo que convierte el simulador en un sistema que mejora perpetuamente (Obj #10: "precisión que sube perpetuamente").

### Archivo nuevo: `kernel/prediction_validator.py`

```python
"""
El Monstruo — Prediction Validator (Sprint 56)
===============================================
Feedback loop del Simulador Causal.

Ciclo:
  1. Registrar predicción con fecha de vencimiento
  2. Cuando la fecha llega, investigar qué pasó realmente
  3. Comparar predicción vs realidad
  4. Ajustar pesos de factores causales
  5. Registrar lección aprendida

Tabla: `predictions`
  - id, scenario, predicted_probability, predicted_at
  - validation_date, actual_outcome, accuracy_score
  - factors_used, factors_adjusted, lesson_learned

Este es el mecanismo que hace que el Simulador MEJORE con el tiempo.
Sin esto, el simulador es estático y eventualmente obsoleto.

Validated: APScheduler 3.11.2 (MIT), Perplexity Sonar (ya en stack)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("kernel.prediction_validator")


@dataclass
class Prediction:
    """Una predicción registrada para validación futura."""
    prediction_id: str = field(default_factory=lambda: str(uuid4()))
    scenario: str = ""
    predicted_probability: float = 0.5
    confidence_interval: tuple[float, float] = (0.0, 1.0)
    dominant_factors: list[str] = field(default_factory=list)
    factors_used: list[dict[str, Any]] = field(default_factory=list)
    predicted_at: Optional[str] = None
    validation_date: Optional[str] = None  # Cuándo validar
    status: str = "pending"  # pending, validated, expired, cancelled
    
    # Post-validación
    actual_outcome: Optional[str] = None
    outcome_probability: Optional[float] = None  # 0=no ocurrió, 1=ocurrió exactamente
    accuracy_score: Optional[float] = None  # Qué tan cerca estuvo la predicción
    factors_adjusted: list[dict[str, Any]] = field(default_factory=list)
    lesson_learned: Optional[str] = None
    validated_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "scenario": self.scenario,
            "predicted_probability": self.predicted_probability,
            "confidence_interval": list(self.confidence_interval),
            "dominant_factors": self.dominant_factors,
            "factors_used": self.factors_used,
            "predicted_at": self.predicted_at,
            "validation_date": self.validation_date,
            "status": self.status,
            "actual_outcome": self.actual_outcome,
            "outcome_probability": self.outcome_probability,
            "accuracy_score": self.accuracy_score,
            "factors_adjusted": self.factors_adjusted,
            "lesson_learned": self.lesson_learned,
            "validated_at": self.validated_at,
        }


class PredictionValidator:
    """
    Motor de validación de predicciones.
    Cierra el feedback loop del Simulador Causal.
    """

    TABLE = "predictions"

    def __init__(self, db=None, search_fn=None, causal_kb=None):
        self._db = db
        self._search = search_fn
        self._causal_kb = causal_kb
        self._pending_count: int = 0

    async def initialize(self) -> None:
        """Cargar conteo de predicciones pendientes."""
        if self._db:
            try:
                count = await self._db.count(self.TABLE, filters={"status": "pending"})
                self._pending_count = count
                logger.info("prediction_validator_initialized", pending=count)
            except Exception as e:
                logger.warning("prediction_validator_init_partial", error=str(e))

    async def register_prediction(
        self,
        scenario: str,
        probability: float,
        confidence_interval: tuple[float, float],
        dominant_factors: list[str],
        factors_used: list[dict[str, Any]],
        validation_date: Optional[str] = None,
        time_horizon_days: int = 30,
    ) -> str:
        """
        Registrar una predicción para validación futura.
        Si no se especifica validation_date, se calcula del time_horizon.
        """
        if not validation_date:
            val_date = datetime.now(timezone.utc) + timedelta(days=time_horizon_days)
            validation_date = val_date.strftime("%Y-%m-%d")

        prediction = Prediction(
            scenario=scenario,
            predicted_probability=probability,
            confidence_interval=confidence_interval,
            dominant_factors=dominant_factors,
            factors_used=factors_used,
            predicted_at=datetime.now(timezone.utc).isoformat(),
            validation_date=validation_date,
        )

        if self._db:
            await self._db.upsert(self.TABLE, {
                "id": prediction.prediction_id,
                "scenario": prediction.scenario,
                "predicted_probability": prediction.predicted_probability,
                "confidence_interval": json.dumps(list(prediction.confidence_interval)),
                "dominant_factors": prediction.dominant_factors,
                "factors_used": json.dumps(prediction.factors_used),
                "predicted_at": prediction.predicted_at,
                "validation_date": prediction.validation_date,
                "status": "pending",
            })

        self._pending_count += 1
        logger.info(
            "prediction_registered",
            prediction_id=prediction.prediction_id,
            scenario=scenario[:80],
            probability=probability,
            validation_date=validation_date,
        )

        return prediction.prediction_id

    async def validate_due_predictions(self) -> list[dict[str, Any]]:
        """
        Validar todas las predicciones cuya fecha de validación ha llegado.
        Este método se ejecuta diariamente via cron.
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        if not self._db:
            return []

        # Obtener predicciones vencidas
        due_predictions = await self._db.select(
            self.TABLE,
            filters={"status": "pending"},
            # validation_date <= today (implementar con RPC o filter)
        )

        # Filtrar por fecha
        due = [
            p for p in due_predictions
            if p.get("validation_date", "9999-99-99") <= today
        ]

        results = []
        for pred_row in due:
            try:
                result = await self._validate_single(pred_row)
                results.append(result)
            except Exception as e:
                logger.error(
                    "prediction_validation_failed",
                    prediction_id=pred_row.get("id"),
                    error=str(e),
                )

        logger.info("validation_cycle_complete", validated=len(results), remaining=self._pending_count)
        return results

    async def _validate_single(self, pred_row: dict) -> dict[str, Any]:
        """Validar una predicción individual."""
        scenario = pred_row.get("scenario", "")
        predicted_prob = pred_row.get("predicted_probability", 0.5)
        prediction_id = pred_row.get("id", "")

        # Paso 1: Investigar qué pasó realmente
        actual_outcome = await self._research_outcome(scenario)

        # Paso 2: Determinar si el evento ocurrió (0-1)
        outcome_prob = await self._assess_outcome(scenario, actual_outcome)

        # Paso 3: Calcular accuracy
        accuracy = 1.0 - abs(predicted_prob - outcome_prob)

        # Paso 4: Determinar qué factores estuvieron bien/mal
        factors_used = json.loads(pred_row.get("factors_used", "[]"))
        adjustments = self._calculate_factor_adjustments(
            factors_used, predicted_prob, outcome_prob
        )

        # Paso 5: Extraer lección
        lesson = self._extract_lesson(scenario, predicted_prob, outcome_prob, adjustments)

        # Paso 6: Actualizar en DB
        if self._db:
            await self._db.update(
                self.TABLE,
                {
                    "status": "validated",
                    "actual_outcome": actual_outcome,
                    "outcome_probability": outcome_prob,
                    "accuracy_score": accuracy,
                    "factors_adjusted": json.dumps(adjustments),
                    "lesson_learned": lesson,
                    "validated_at": datetime.now(timezone.utc).isoformat(),
                },
                filters={"id": prediction_id},
            )

        # Paso 7: Ajustar pesos en Causal KB
        if self._causal_kb and adjustments:
            await self._apply_adjustments_to_kb(adjustments)

        self._pending_count -= 1

        logger.info(
            "prediction_validated",
            prediction_id=prediction_id,
            predicted=predicted_prob,
            actual=outcome_prob,
            accuracy=accuracy,
            lesson=lesson[:100] if lesson else None,
        )

        return {
            "prediction_id": prediction_id,
            "scenario": scenario,
            "predicted": predicted_prob,
            "actual": outcome_prob,
            "accuracy": accuracy,
            "lesson": lesson,
        }

    async def _research_outcome(self, scenario: str) -> str:
        """Investigar qué pasó realmente con el escenario predicho."""
        if not self._search:
            return "Unable to research: no search function available"

        query = f"What actually happened with: {scenario}? Current status and outcome."
        try:
            result = await self._search(query)
            return result if isinstance(result, str) else json.dumps(result)
        except Exception as e:
            return f"Research failed: {str(e)}"

    async def _assess_outcome(self, scenario: str, actual_outcome: str) -> float:
        """
        Evaluar si el evento predicho ocurrió (0.0 = no ocurrió, 1.0 = ocurrió exactamente).
        Usa LLM para evaluación semántica.
        """
        # Fallback simple: si el outcome menciona éxito/ocurrencia → 0.8+
        # En producción, esto usa un LLM call
        positive_indicators = ["succeeded", "achieved", "happened", "confirmed", "reached", "surpassed"]
        negative_indicators = ["failed", "did not", "hasn't", "unlikely", "cancelled", "abandoned"]
        
        outcome_lower = actual_outcome.lower()
        pos_count = sum(1 for w in positive_indicators if w in outcome_lower)
        neg_count = sum(1 for w in negative_indicators if w in outcome_lower)
        
        if pos_count > neg_count:
            return min(0.9, 0.5 + pos_count * 0.15)
        elif neg_count > pos_count:
            return max(0.1, 0.5 - neg_count * 0.15)
        return 0.5

    def _calculate_factor_adjustments(
        self,
        factors_used: list[dict],
        predicted: float,
        actual: float,
    ) -> list[dict[str, Any]]:
        """
        Calcular ajustes a los factores basado en el error de predicción.
        Si predijimos alto y fue bajo → los factores positivos estaban sobre-estimados.
        Si predijimos bajo y fue alto → los factores positivos estaban sub-estimados.
        """
        error = actual - predicted  # Positivo = sub-estimamos, negativo = sobre-estimamos
        adjustments = []

        for factor in factors_used:
            direction = factor.get("direction", "positive")
            weight = factor.get("weight", 0.5)
            
            # Ajuste proporcional al error
            if direction == "positive":
                new_weight = weight + (error * 0.1)  # Ajuste conservador (10% del error)
            else:
                new_weight = weight - (error * 0.1)
            
            new_weight = max(0.05, min(0.95, new_weight))  # Clamp
            
            if abs(new_weight - weight) > 0.01:  # Solo registrar cambios significativos
                adjustments.append({
                    "description": factor.get("description", ""),
                    "old_weight": round(weight, 3),
                    "new_weight": round(new_weight, 3),
                    "adjustment": round(new_weight - weight, 3),
                    "reason": "over-estimated" if error < 0 else "under-estimated",
                })

        return adjustments

    def _extract_lesson(
        self, scenario: str, predicted: float, actual: float, adjustments: list
    ) -> str:
        """Extraer una lección concisa de la validación."""
        error = abs(predicted - actual)
        
        if error < 0.1:
            return f"Prediction accurate (error={error:.2f}). Model well-calibrated for this type of scenario."
        elif error < 0.3:
            direction = "under" if actual > predicted else "over"
            top_adj = adjustments[0]["description"] if adjustments else "unknown factor"
            return f"Moderate {direction}-estimation (error={error:.2f}). Key factor '{top_adj}' needs weight adjustment."
        else:
            direction = "under" if actual > predicted else "over"
            return f"Significant {direction}-estimation (error={error:.2f}). Model needs recalibration for this scenario type. Consider adding missing factors."

    async def _apply_adjustments_to_kb(self, adjustments: list[dict]) -> None:
        """Aplicar ajustes de peso a eventos similares en la Causal KB."""
        # En v1, solo loguea los ajustes. En v2, actualiza embeddings y pesos.
        for adj in adjustments:
            logger.info(
                "factor_weight_adjusted",
                factor=adj["description"][:50],
                old=adj["old_weight"],
                new=adj["new_weight"],
                reason=adj["reason"],
            )

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas del validador."""
        return {
            "pending_predictions": self._pending_count,
            "status": "active",
        }
```

### Schema SQL (Supabase):

```sql
-- Sprint 56: Predictions table for feedback loop
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario TEXT NOT NULL,
    predicted_probability FLOAT NOT NULL,
    confidence_interval JSONB DEFAULT '[]',
    dominant_factors TEXT[] DEFAULT '{}',
    factors_used JSONB DEFAULT '[]',
    predicted_at TIMESTAMPTZ DEFAULT NOW(),
    validation_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    actual_outcome TEXT,
    outcome_probability FLOAT,
    accuracy_score FLOAT,
    factors_adjusted JSONB DEFAULT '[]',
    lesson_learned TEXT,
    validated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_predictions_status ON predictions(status);
CREATE INDEX idx_predictions_validation_date ON predictions(validation_date);
CREATE INDEX idx_predictions_accuracy ON predictions(accuracy_score);
```

### Criterio de éxito:

- **T1:** `register_prediction()` persiste predicción con validation_date
- **T2:** `validate_due_predictions()` encuentra y valida predicciones vencidas
- **T3:** `accuracy_score` se calcula correctamente (1 - |predicted - actual|)
- **T4:** Factor adjustments se calculan y registran
- **T5:** Cron job diario ejecuta validación automáticamente

---

## Épica 56.3 — Embrión Autonomy Layer: Auto-Assignment y Scheduler

**Objetivo:** Dar a los Embriones la capacidad de auto-asignarse tareas basado en prioridades del sistema, ejecutarlas autónomamente, y reportar resultados. Esto transforma al Embrión de reactivo a proactivo.

**Herramientas adoptadas:**
- APScheduler 3.11.2 — Cron jobs internos para tareas periódicas
- Embrión Loop existente (Sprint 33C) — Base sobre la que se construye

**Principio:** El Embrión ya respira (Sprint 33C) y ya tiene budget + judge + silencio. Lo que falta es que pueda DECIDIR qué hacer sin que Alfredo le diga. El auto-assignment es la diferencia entre un asistente y un agente autónomo.

### Archivo nuevo: `kernel/embrion_scheduler.py`

```python
"""
El Monstruo — Embrión Scheduler (Sprint 56)
============================================
Scheduler interno para tareas autónomas de los Embriones.
Cada Embrión puede tener tareas programadas que se ejecutan
sin intervención humana.

Tipos de tareas:
  - periodic: Se ejecuta cada N horas (e.g., causal seeding cada 6h)
  - daily: Se ejecuta una vez al día a hora fija (e.g., validación de predicciones)
  - triggered: Se ejecuta cuando una condición se cumple (e.g., nuevo evento detectado)
  - one_shot: Se ejecuta una vez y se elimina (e.g., investigar tema específico)

Governance:
  - Cada tarea tiene un budget máximo (tokens/costo)
  - El judge evalúa si la tarea se ejecutó bien
  - Si una tarea falla 3 veces seguidas, se pausa y notifica
  - Budget diario total compartido entre todas las tareas

Validated: APScheduler 3.11.2 (MIT, Dec 2025)
"""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Coroutine, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("kernel.embrion_scheduler")


@dataclass
class ScheduledTask:
    """Una tarea programada para un Embrión."""
    task_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    embrion_id: str = "embrion-0"  # Quién la ejecuta
    
    # Scheduling
    schedule_type: str = "periodic"  # periodic, daily, triggered, one_shot
    interval_hours: float = 6.0  # Para periodic
    daily_hour: int = 3  # Para daily (hora UTC)
    trigger_condition: Optional[str] = None  # Para triggered
    
    # Governance
    max_cost_usd: float = 0.50  # Budget máximo por ejecución
    max_retries: int = 3
    consecutive_failures: int = 0
    paused: bool = False
    
    # Estado
    status: str = "active"  # active, paused, completed, failed
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    total_runs: int = 0
    total_cost_usd: float = 0.0
    
    # Ejecución
    handler: Optional[str] = None  # Nombre del handler async a ejecutar
    handler_args: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "embrion_id": self.embrion_id,
            "schedule_type": self.schedule_type,
            "interval_hours": self.interval_hours,
            "status": self.status,
            "paused": self.paused,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "total_runs": self.total_runs,
            "total_cost_usd": round(self.total_cost_usd, 3),
            "consecutive_failures": self.consecutive_failures,
        }


class EmbrionScheduler:
    """
    Scheduler de tareas autónomas para Embriones.
    Gestiona el ciclo de vida de tareas programadas.
    """

    DAILY_BUDGET_USD = float(os.environ.get("EMBRION_DAILY_BUDGET", "10.0"))

    def __init__(self):
        self._tasks: dict[str, ScheduledTask] = {}
        self._handlers: dict[str, Callable[..., Coroutine]] = {}
        self._daily_spend: float = 0.0
        self._daily_reset: Optional[str] = None
        self._running: bool = False
        self._check_task: Optional[asyncio.Task] = None

    def register_handler(self, name: str, handler: Callable[..., Coroutine]) -> None:
        """Registrar un handler ejecutable."""
        self._handlers[name] = handler
        logger.info("handler_registered", name=name)

    def add_task(self, task: ScheduledTask) -> str:
        """Agregar una tarea al scheduler."""
        # Calcular next_run
        task.next_run = self._calculate_next_run(task)
        self._tasks[task.task_id] = task
        
        logger.info(
            "task_added",
            task_id=task.task_id,
            name=task.name,
            schedule=task.schedule_type,
            next_run=task.next_run,
        )
        return task.task_id

    def remove_task(self, task_id: str) -> bool:
        """Remover una tarea del scheduler."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def pause_task(self, task_id: str) -> bool:
        """Pausar una tarea."""
        if task_id in self._tasks:
            self._tasks[task_id].paused = True
            self._tasks[task_id].status = "paused"
            return True
        return False

    def resume_task(self, task_id: str) -> bool:
        """Reanudar una tarea pausada."""
        if task_id in self._tasks:
            self._tasks[task_id].paused = False
            self._tasks[task_id].status = "active"
            self._tasks[task_id].consecutive_failures = 0
            self._tasks[task_id].next_run = self._calculate_next_run(self._tasks[task_id])
            return True
        return False

    async def start(self) -> None:
        """Iniciar el scheduler loop."""
        self._running = True
        self._check_task = asyncio.create_task(self._scheduler_loop())
        logger.info("embrion_scheduler_started", tasks=len(self._tasks))

    async def stop(self) -> None:
        """Detener el scheduler."""
        self._running = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        logger.info("embrion_scheduler_stopped")

    async def _scheduler_loop(self) -> None:
        """Loop principal del scheduler. Revisa tareas cada 60 segundos."""
        while self._running:
            try:
                await self._check_and_execute_due_tasks()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("scheduler_loop_error", error=str(e))
                await asyncio.sleep(60)

    async def _check_and_execute_due_tasks(self) -> None:
        """Verificar y ejecutar tareas que están listas."""
        self._reset_daily_budget_if_needed()
        
        now = datetime.now(timezone.utc).isoformat()
        
        for task in list(self._tasks.values()):
            if task.paused or task.status != "active":
                continue
            if not task.next_run or task.next_run > now:
                continue
            if self._daily_spend >= self.DAILY_BUDGET_USD:
                logger.warning("daily_budget_exhausted", spend=self._daily_spend)
                break

            # Ejecutar tarea
            await self._execute_task(task)

    async def _execute_task(self, task: ScheduledTask) -> None:
        """Ejecutar una tarea individual."""
        handler = self._handlers.get(task.handler)
        if not handler:
            logger.error("handler_not_found", handler=task.handler, task=task.name)
            return

        logger.info("task_executing", task_id=task.task_id, name=task.name)
        
        try:
            result = await handler(**task.handler_args)
            
            # Éxito
            task.last_run = datetime.now(timezone.utc).isoformat()
            task.total_runs += 1
            task.consecutive_failures = 0
            
            # Estimar costo (simplificado)
            estimated_cost = task.max_cost_usd * 0.5  # Asumir 50% del max
            task.total_cost_usd += estimated_cost
            self._daily_spend += estimated_cost
            
            # Calcular próxima ejecución
            if task.schedule_type == "one_shot":
                task.status = "completed"
            else:
                task.next_run = self._calculate_next_run(task)

            logger.info(
                "task_completed",
                task_id=task.task_id,
                name=task.name,
                cost=estimated_cost,
            )

        except Exception as e:
            task.consecutive_failures += 1
            task.last_run = datetime.now(timezone.utc).isoformat()
            
            if task.consecutive_failures >= task.max_retries:
                task.paused = True
                task.status = "paused"
                logger.error(
                    "task_paused_max_failures",
                    task_id=task.task_id,
                    name=task.name,
                    failures=task.consecutive_failures,
                )
            else:
                task.next_run = self._calculate_next_run(task)
                logger.warning(
                    "task_failed",
                    task_id=task.task_id,
                    name=task.name,
                    failures=task.consecutive_failures,
                    error=str(e),
                )

    def _calculate_next_run(self, task: ScheduledTask) -> str:
        """Calcular próxima ejecución."""
        now = datetime.now(timezone.utc)
        
        if task.schedule_type == "periodic":
            next_time = now + timedelta(hours=task.interval_hours)
        elif task.schedule_type == "daily":
            next_time = now.replace(hour=task.daily_hour, minute=0, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
        elif task.schedule_type == "one_shot":
            next_time = now + timedelta(minutes=1)  # Ejecutar pronto
        else:
            next_time = now + timedelta(hours=1)  # Default: 1 hora
        
        return next_time.isoformat()

    def _reset_daily_budget_if_needed(self) -> None:
        """Reset budget diario si cambió el día."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._daily_reset != today:
            self._daily_spend = 0.0
            self._daily_reset = today

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas del scheduler."""
        active = sum(1 for t in self._tasks.values() if t.status == "active")
        paused = sum(1 for t in self._tasks.values() if t.status == "paused")
        
        return {
            "total_tasks": len(self._tasks),
            "active_tasks": active,
            "paused_tasks": paused,
            "daily_spend_usd": round(self._daily_spend, 2),
            "daily_budget_usd": self.DAILY_BUDGET_USD,
            "running": self._running,
        }

    def get_all_tasks(self) -> list[dict[str, Any]]:
        """Listar todas las tareas."""
        return [t.to_dict() for t in self._tasks.values()]
```

### Tareas Default (se registran al startup):

```python
# ── Sprint 56: Default Scheduled Tasks ────────────────────────────

def register_default_tasks(scheduler: EmbrionScheduler) -> None:
    """Registrar tareas default del sistema."""
    
    # 1. Causal Seeding — cada 6 horas
    scheduler.add_task(ScheduledTask(
        name="causal_seeding",
        description="Feed the Causal KB with new decomposed events",
        embrion_id="embrion-causal",
        schedule_type="periodic",
        interval_hours=6.0,
        max_cost_usd=1.00,
        handler="run_causal_seeding_cycle",
    ))
    
    # 2. Prediction Validation — diaria a las 3am UTC
    scheduler.add_task(ScheduledTask(
        name="prediction_validation",
        description="Validate due predictions and adjust factor weights",
        embrion_id="embrion-causal",
        schedule_type="daily",
        daily_hour=3,
        max_cost_usd=0.50,
        handler="run_prediction_validation",
    ))
    
    # 3. Vanguard Scan — diaria a las 6am UTC
    scheduler.add_task(ScheduledTask(
        name="vanguard_scan",
        description="Scan for new technologies and tools relevant to El Monstruo",
        embrion_id="embrion-0",
        schedule_type="daily",
        daily_hour=6,
        max_cost_usd=0.30,
        handler="run_vanguard_scan",
    ))
    
    # 4. Health Check — cada 2 horas
    scheduler.add_task(ScheduledTask(
        name="system_health_check",
        description="Check health of all subsystems and report anomalies",
        embrion_id="embrion-0",
        schedule_type="periodic",
        interval_hours=2.0,
        max_cost_usd=0.05,
        handler="run_health_check",
    ))
    
    # 5. Memory Consolidation — diaria a las 2am UTC
    scheduler.add_task(ScheduledTask(
        name="memory_consolidation",
        description="Consolidate short-term memories into long-term patterns",
        embrion_id="embrion-0",
        schedule_type="daily",
        daily_hour=2,
        max_cost_usd=0.20,
        handler="run_memory_consolidation",
    ))
```

### Criterio de éxito:

- **T1:** Scheduler loop ejecuta tareas cuando `next_run` llega
- **T2:** Budget diario se respeta (hard stop)
- **T3:** Tareas que fallan 3 veces se pausan automáticamente
- **T4:** 5 tareas default se registran al startup
- **T5:** `get_stats()` muestra estado completo del scheduler

---

## Épica 56.4 — Embrión Observability: Dashboard de Actividad Autónoma

**Objetivo:** Expandir el Langfuse Bridge existente para trackear cada acción de cada Embrión individualmente — costos, latencia, calidad, errores. Esto da visibilidad total sobre qué hacen los Embriones cuando operan autónomamente.

**Herramientas adoptadas:**
- Langfuse 4.5.1 — Ya en stack, ya tiene bridge funcional
- Langfuse v4 SDK — Traces, spans, generations, scores

**Principio:** No expandir Langfuse Bridge con funcionalidad nueva — solo agregar decoradores/wrappers que los Embriones usen automáticamente. La observabilidad debe ser invisible para el código de negocio.

### Archivo a modificar: `observability/langfuse_bridge.py`

Agregar métodos para tracing de Embriones:

```python
# ── Sprint 56: Embrión Observability ──────────────────────────────

def trace_embrion_action(
    self,
    embrion_id: str,
    action_name: str,
    action_type: str = "task",  # task, thinking, seeding, validation
    metadata: Optional[dict] = None,
) -> Optional[Any]:
    """
    Crear un trace para una acción de Embrión.
    Retorna el trace object para agregar spans/generations.
    """
    if not self._enabled or not self._client:
        return None

    try:
        trace = self._client.trace(
            name=f"embrion:{embrion_id}:{action_name}",
            user_id=embrion_id,
            session_id=f"embrion-session-{embrion_id}",
            metadata={
                "embrion_id": embrion_id,
                "action_type": action_type,
                "sprint": "56",
                **(metadata or {}),
            },
            tags=[f"embrion:{embrion_id}", f"type:{action_type}"],
        )
        return trace
    except Exception as e:
        logger.warning("langfuse_trace_embrion_failed", error=str(e))
        return None

def score_embrion_action(
    self,
    trace_id: str,
    name: str,
    value: float,
    comment: Optional[str] = None,
) -> None:
    """Registrar un score para una acción de Embrión."""
    if not self._enabled or not self._client:
        return

    try:
        self._client.score(
            trace_id=trace_id,
            name=name,
            value=value,
            comment=comment,
        )
    except Exception as e:
        logger.warning("langfuse_score_failed", error=str(e))

def track_embrion_cost(
    self,
    embrion_id: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
) -> None:
    """Trackear costo de un LLM call de un Embrión."""
    if not self._enabled or not self._client:
        return

    try:
        # Langfuse v4 genera automáticamente cost tracking
        # pero registramos explícitamente para dashboard custom
        self._client.trace(
            name=f"embrion:{embrion_id}:llm_cost",
            metadata={
                "embrion_id": embrion_id,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost_usd,
            },
            tags=[f"embrion:{embrion_id}", "cost_tracking"],
        )
    except Exception as e:
        logger.warning("langfuse_cost_tracking_failed", error=str(e))
```

### Archivo nuevo: `observability/embrion_metrics.py`

```python
"""
El Monstruo — Embrión Metrics Collector (Sprint 56)
====================================================
Recolecta y agrega métricas de todos los Embriones.
Expone vía API para el Command Center dashboard.

Métricas por Embrión:
  - tasks_completed (counter)
  - tasks_failed (counter)
  - total_cost_usd (gauge)
  - avg_latency_ms (gauge)
  - quality_score (gauge, 0-1)
  - uptime_pct (gauge)
  - last_action_at (timestamp)

Métricas globales:
  - total_embriones_active
  - total_daily_cost_usd
  - predictions_validated_today
  - causal_events_seeded_today
  - scheduler_tasks_active
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("observability.embrion_metrics")


@dataclass
class EmbrionMetrics:
    """Métricas de un Embrión individual."""
    embrion_id: str = ""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_cost_usd: float = 0.0
    latencies_ms: list[float] = field(default_factory=list)
    quality_scores: list[float] = field(default_factory=list)
    last_action_at: Optional[str] = None
    started_at: Optional[str] = None

    @property
    def avg_latency_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        return sum(self.latencies_ms[-100:]) / len(self.latencies_ms[-100:])

    @property
    def avg_quality_score(self) -> float:
        if not self.quality_scores:
            return 0.0
        return sum(self.quality_scores[-50:]) / len(self.quality_scores[-50:])

    @property
    def success_rate(self) -> float:
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 1.0
        return self.tasks_completed / total

    def to_dict(self) -> dict[str, Any]:
        return {
            "embrion_id": self.embrion_id,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "total_cost_usd": round(self.total_cost_usd, 3),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "avg_quality_score": round(self.avg_quality_score, 3),
            "success_rate": round(self.success_rate, 3),
            "last_action_at": self.last_action_at,
        }


class EmbrionMetricsCollector:
    """Recolector central de métricas de Embriones."""

    def __init__(self):
        self._metrics: dict[str, EmbrionMetrics] = {}
        self._global_events_today: int = 0
        self._global_predictions_today: int = 0

    def _get_or_create(self, embrion_id: str) -> EmbrionMetrics:
        if embrion_id not in self._metrics:
            self._metrics[embrion_id] = EmbrionMetrics(
                embrion_id=embrion_id,
                started_at=datetime.now(timezone.utc).isoformat(),
            )
        return self._metrics[embrion_id]

    def record_task_success(
        self, embrion_id: str, latency_ms: float, cost_usd: float = 0.0
    ) -> None:
        """Registrar tarea completada exitosamente."""
        m = self._get_or_create(embrion_id)
        m.tasks_completed += 1
        m.latencies_ms.append(latency_ms)
        m.total_cost_usd += cost_usd
        m.last_action_at = datetime.now(timezone.utc).isoformat()

    def record_task_failure(self, embrion_id: str, latency_ms: float = 0.0) -> None:
        """Registrar tarea fallida."""
        m = self._get_or_create(embrion_id)
        m.tasks_failed += 1
        if latency_ms > 0:
            m.latencies_ms.append(latency_ms)
        m.last_action_at = datetime.now(timezone.utc).isoformat()

    def record_quality_score(self, embrion_id: str, score: float) -> None:
        """Registrar score de calidad (del judge)."""
        m = self._get_or_create(embrion_id)
        m.quality_scores.append(score)

    def record_cost(self, embrion_id: str, cost_usd: float) -> None:
        """Registrar costo."""
        m = self._get_or_create(embrion_id)
        m.total_cost_usd += cost_usd

    def get_embrion_metrics(self, embrion_id: str) -> dict[str, Any]:
        """Obtener métricas de un Embrión específico."""
        m = self._metrics.get(embrion_id)
        if not m:
            return {"embrion_id": embrion_id, "status": "not_found"}
        return m.to_dict()

    def get_global_metrics(self) -> dict[str, Any]:
        """Obtener métricas globales del sistema."""
        total_cost = sum(m.total_cost_usd for m in self._metrics.values())
        total_tasks = sum(m.tasks_completed + m.tasks_failed for m in self._metrics.values())
        active = sum(1 for m in self._metrics.values() if m.last_action_at)

        return {
            "total_embriones": len(self._metrics),
            "active_embriones": active,
            "total_tasks_executed": total_tasks,
            "total_cost_usd": round(total_cost, 3),
            "causal_events_seeded_today": self._global_events_today,
            "predictions_validated_today": self._global_predictions_today,
            "embriones": [m.to_dict() for m in self._metrics.values()],
        }
```

### Criterio de éxito:

- **T1:** Cada acción de Embrión genera un trace en Langfuse con embrion_id
- **T2:** Costos se trackean por Embrión y por acción
- **T3:** `get_global_metrics()` retorna dashboard completo
- **T4:** Quality scores del judge se registran en Langfuse
- **T5:** Command Center puede consumir `/v1/embrion/metrics` para dashboard

---

## Épica 56.5 — Sovereignty Checkpoint: Ollama como Fallback Local

**Objetivo:** Integrar Ollama como proveedor de modelos locales/cloud que sirve como fallback soberano cuando las APIs principales (OpenAI, Anthropic, Google) no están disponibles o para tareas de bajo costo donde un modelo local es suficiente.

**Herramientas adoptadas (Obj #7, #12):**
- `ollama==0.6.2` (PyPI, Apr 29, 2026) — SDK oficial con AsyncClient
- Ollama Cloud — Modelos grandes sin GPU local (gpt-oss:120b, deepseek-v3.1:671b)
- Ollama local — Modelos pequeños para tareas tier 1-2 (gemma3, qwen3)

**Principio:** Soberanía no es todo-o-nada. Es un espectro. Hoy El Monstruo depende 100% de APIs cloud. Con Ollama, las tareas simples (clasificación, resumen, formatting) pueden ejecutarse localmente a costo $0, y las tareas complejas tienen un fallback si OpenAI/Anthropic caen.

### Archivo nuevo: `kernel/sovereign_llm.py`

```python
"""
El Monstruo — Sovereign LLM Layer (Sprint 56)
==============================================
Capa de abstracción para modelos LLM con soberanía progresiva.

Estrategia de routing:
  Tier 1 (Simple): Clasificación, formatting, extracción → Ollama local (gemma3)
  Tier 2 (Medio): Resumen, Q&A, análisis básico → Ollama cloud (gpt-oss:120b)
  Tier 3 (Complejo): Razonamiento profundo, código, causal → GPT 5.2 / Gemini 3 Pro
  Tier 4 (Crítico): Decisiones de negocio, predicciones → Multi-modelo (Sabios)

Fallback chain:
  Primary (cloud API) → Ollama Cloud → Ollama Local → Error

Benefits:
  - Tier 1-2 tasks: $0 cost (local) o ~$0.001 (Ollama cloud)
  - Availability: Si OpenAI cae, Ollama sigue funcionando
  - Privacy: Datos sensibles nunca salen del servidor (Ollama local)
  - Speed: Modelos locales = 0 network latency

Validated: ollama==0.6.2 (MIT, Apr 29, 2026), AsyncClient nativo
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.sovereign_llm")


class TaskTier(IntEnum):
    """Tier de complejidad de tarea."""
    SIMPLE = 1      # Clasificación, formatting, extracción
    MEDIUM = 2      # Resumen, Q&A, análisis básico
    COMPLEX = 3     # Razonamiento profundo, código, causal
    CRITICAL = 4    # Decisiones de negocio, predicciones


@dataclass
class LLMResponse:
    """Respuesta unificada de cualquier proveedor."""
    content: str
    model: str
    provider: str  # openai, anthropic, google, ollama_local, ollama_cloud
    tier: int
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    fallback_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "tier": self.tier,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "latency_ms": round(self.latency_ms, 1),
            "cost_usd": round(self.cost_usd, 6),
            "fallback_used": self.fallback_used,
        }


class SovereignLLM:
    """
    Capa soberana de LLM con routing inteligente y fallback.
    """

    # Modelos por tier
    TIER_MODELS = {
        TaskTier.SIMPLE: [
            {"provider": "ollama_local", "model": "gemma3:8b", "cost_per_1k": 0.0},
            {"provider": "ollama_cloud", "model": "gemma3", "cost_per_1k": 0.0001},
        ],
        TaskTier.MEDIUM: [
            {"provider": "ollama_cloud", "model": "gpt-oss:120b-cloud", "cost_per_1k": 0.001},
            {"provider": "openai", "model": "gpt-4o-mini", "cost_per_1k": 0.00015},
        ],
        TaskTier.COMPLEX: [
            {"provider": "openai", "model": "gpt-5.2-turbo", "cost_per_1k": 0.01},
            {"provider": "google", "model": "gemini-3-pro", "cost_per_1k": 0.007},
            {"provider": "ollama_cloud", "model": "deepseek-v3.1:671b-cloud", "cost_per_1k": 0.003},
        ],
        TaskTier.CRITICAL: [
            # Multi-modelo: se usa consult_sabios, no esta capa
        ],
    }

    def __init__(self):
        self._ollama_local = None
        self._ollama_cloud = None
        self._openai = None
        self._initialized = False
        self._stats = {
            "calls_by_provider": {},
            "calls_by_tier": {},
            "fallbacks_used": 0,
            "total_cost_usd": 0.0,
        }

    async def initialize(self) -> None:
        """Inicializar clientes de LLM."""
        # Ollama local
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        try:
            from ollama import AsyncClient
            self._ollama_local = AsyncClient(host=ollama_host)
            # Test connection
            await self._ollama_local.list()
            logger.info("ollama_local_connected", host=ollama_host)
        except Exception as e:
            logger.info("ollama_local_unavailable", reason=str(e))
            self._ollama_local = None

        # Ollama cloud
        ollama_api_key = os.environ.get("OLLAMA_API_KEY")
        if ollama_api_key:
            try:
                from ollama import AsyncClient
                self._ollama_cloud = AsyncClient(
                    host="https://ollama.com",
                    headers={"Authorization": f"Bearer {ollama_api_key}"},
                )
                logger.info("ollama_cloud_connected")
            except Exception as e:
                logger.info("ollama_cloud_unavailable", reason=str(e))
                self._ollama_cloud = None

        # OpenAI (ya debería estar disponible)
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import AsyncOpenAI
                self._openai = AsyncOpenAI(api_key=openai_key)
                logger.info("openai_connected")
            except Exception:
                pass

        self._initialized = True
        logger.info(
            "sovereign_llm_initialized",
            ollama_local=self._ollama_local is not None,
            ollama_cloud=self._ollama_cloud is not None,
            openai=self._openai is not None,
        )

    async def generate(
        self,
        prompt: str,
        tier: TaskTier = TaskTier.MEDIUM,
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """
        Generar respuesta con routing inteligente por tier.
        Intenta el modelo preferido del tier, con fallback automático.
        """
        import time
        start = time.time()

        models = self.TIER_MODELS.get(tier, self.TIER_MODELS[TaskTier.MEDIUM])
        last_error = None
        fallback_used = False

        for i, model_config in enumerate(models):
            provider = model_config["provider"]
            model = model_config["model"]
            
            try:
                content = await self._call_provider(
                    provider=provider,
                    model=model,
                    prompt=prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                latency = (time.time() - start) * 1000
                
                # Track stats
                self._stats["calls_by_provider"][provider] = self._stats["calls_by_provider"].get(provider, 0) + 1
                self._stats["calls_by_tier"][str(tier.value)] = self._stats["calls_by_tier"].get(str(tier.value), 0) + 1
                if i > 0:
                    self._stats["fallbacks_used"] += 1
                    fallback_used = True

                return LLMResponse(
                    content=content,
                    model=model,
                    provider=provider,
                    tier=tier.value,
                    latency_ms=latency,
                    cost_usd=model_config["cost_per_1k"] * (len(prompt) + len(content)) / 4000,
                    fallback_used=fallback_used,
                )

            except Exception as e:
                last_error = e
                logger.warning(
                    "llm_provider_failed",
                    provider=provider,
                    model=model,
                    error=str(e),
                    trying_next=i < len(models) - 1,
                )
                continue

        # Todos los proveedores fallaron
        raise RuntimeError(f"All LLM providers failed for tier {tier}. Last error: {last_error}")

    async def _call_provider(
        self,
        provider: str,
        model: str,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Llamar a un proveedor específico."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        if provider == "ollama_local":
            if not self._ollama_local:
                raise RuntimeError("Ollama local not available")
            response = await self._ollama_local.chat(
                model=model,
                messages=messages,
                options={"temperature": temperature, "num_predict": max_tokens},
            )
            return response.message.content

        elif provider == "ollama_cloud":
            if not self._ollama_cloud:
                raise RuntimeError("Ollama cloud not available")
            response = await self._ollama_cloud.chat(
                model=model,
                messages=messages,
                options={"temperature": temperature, "num_predict": max_tokens},
            )
            return response.message.content

        elif provider == "openai":
            if not self._openai:
                raise RuntimeError("OpenAI not available")
            response = await self._openai.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        elif provider == "google":
            # Usar Gemini API
            import google.generativeai as genai
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            model_obj = genai.GenerativeModel(model)
            response = await model_obj.generate_content_async(prompt)
            return response.text

        else:
            raise RuntimeError(f"Unknown provider: {provider}")

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas de uso."""
        return {
            **self._stats,
            "providers_available": {
                "ollama_local": self._ollama_local is not None,
                "ollama_cloud": self._ollama_cloud is not None,
                "openai": self._openai is not None,
            },
        }
```

### Variables de entorno nuevas:

| Variable | Descripción | Cuándo activar |
|---|---|---|
| `OLLAMA_HOST` | URL del servidor Ollama local | Cuando se instale Ollama en Railway/VPS |
| `OLLAMA_API_KEY` | API key para Ollama Cloud | Cuando Alfredo active Ollama Cloud |

### Criterio de éxito:

- **T1:** Tier 1 tasks se ejecutan en Ollama local/cloud sin tocar OpenAI
- **T2:** Si Ollama falla, fallback automático a OpenAI funciona
- **T3:** Stats muestran distribución de calls por provider
- **T4:** Costo de Tier 1-2 es $0 (local) o <$0.001 (cloud)
- **T5:** `initialize()` detecta correctamente qué proveedores están disponibles

---

## Integración en `kernel/main.py`

```python
# ── Sprint 56: Embrión Scheduler ─────────────────────────────────
from kernel.embrion_scheduler import EmbrionScheduler, ScheduledTask, register_default_tasks

embrion_scheduler = EmbrionScheduler()
register_default_tasks(embrion_scheduler)

# Register handlers
embrion_scheduler.register_handler("run_causal_seeding_cycle", causal_seeder.run_cycle)
embrion_scheduler.register_handler("run_prediction_validation", prediction_validator.validate_due_predictions)

await embrion_scheduler.start()
app.state.embrion_scheduler = embrion_scheduler
logger.info("embrion_scheduler_started", tasks=len(embrion_scheduler.get_all_tasks()))

# ── Sprint 56: Causal Seeder ─────────────────────────────────────
from kernel.causal_seeder import CausalSeeder

causal_seeder = CausalSeeder(
    decomposer=app.state.causal_decomposer,
    search_fn=web_search_fn,
    db=db,
)
app.state.causal_seeder = causal_seeder

# ── Sprint 56: Prediction Validator ──────────────────────────────
from kernel.prediction_validator import PredictionValidator

prediction_validator = PredictionValidator(
    db=db,
    search_fn=web_search_fn,
    causal_kb=app.state.causal_kb,
)
await prediction_validator.initialize()
app.state.prediction_validator = prediction_validator

# ── Sprint 56: Sovereign LLM ─────────────────────────────────────
from kernel.sovereign_llm import SovereignLLM

sovereign_llm = SovereignLLM()
await sovereign_llm.initialize()
app.state.sovereign_llm = sovereign_llm

# ── Sprint 56: Embrión Metrics ────────────────────────────────────
from observability.embrion_metrics import EmbrionMetricsCollector

embrion_metrics = EmbrionMetricsCollector()
app.state.embrion_metrics = embrion_metrics
```

---

## Dependencias Nuevas (requirements.txt)

```
# Sprint 56 — nuevas dependencias
APScheduler==3.11.2
ollama==0.6.2
wikipedia-api==0.7.1  # Para seeding de eventos históricos
```

**Nota:** `langfuse==4.5.1` ya está en requirements.txt. No se agrega.

---

## Costos Estimados

| Componente | Costo mensual estimado | Notas |
|---|---|---|
| Causal Seeder (4 ciclos/día × 30 días) | ~$15-30/mes | 10-15 eventos/ciclo × $0.05/evento |
| Prediction Validator (1 ciclo/día) | ~$5-10/mes | Depende de predicciones pendientes |
| Embrión Scheduler overhead | ~$2-5/mes | Health checks, consolidation |
| Ollama Cloud (Tier 1-2) | ~$1-3/mes | Muy bajo costo por token |
| Langfuse hosting | $0 (self-hosted) o $25/mes (cloud) | Ya en stack |
| **Total Sprint 56** | **~$23-48/mes** | Sobre costos existentes |

---

## Orden de Implementación

| Orden | Épica | Dependencia | Estimación |
|---|---|---|---|
| 1 | 56.3 — Embrión Scheduler | Ninguna (standalone) | 1-2 días |
| 2 | 56.1 — Causal Seeder | Requiere Scheduler + Causal KB (Sprint 55) | 2-3 días |
| 3 | 56.2 — Prediction Validator | Requiere Scheduler + Causal KB | 2-3 días |
| 4 | 56.4 — Observability | Requiere Langfuse Bridge existente | 1-2 días |
| 5 | 56.5 — Sovereign LLM | Ninguna (standalone) | 2-3 días |

**Total:** 8-13 días (con buffer para testing e integración)

---

## Referencias

[1] Langfuse 4.5.1 — https://pypi.org/project/langfuse/ (Released Apr 24, 2026, MIT)
[2] APScheduler 3.11.2 — https://pypi.org/project/APScheduler/ (Released Dec 22, 2025, MIT)
[3] Ollama Python SDK 0.6.2 — https://pypi.org/project/ollama/ (Released Apr 29, 2026, MIT)
[4] Ollama Cloud Models — gpt-oss:120b-cloud, deepseek-v3.1:671b-cloud, qwen3-coder:480b-cloud
[5] Ollama vs vLLM comparison — 52M monthly downloads Q1 2026, suitable for single-user production [6]
[6] "I Tested Ollama vs vLLM vs llama.cpp" — Towards AI, Apr 14, 2026
[7] Langfuse v4 Migration Guide — SDK rewritten Mar 2026
[8] Grafana Labs AI Observability — GrafanaCON 2026, Apr 21, 2026
[9] Agent Observability 2026 Guide — Digital Applied, Apr 14, 2026
