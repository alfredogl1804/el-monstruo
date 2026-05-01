"""
El Monstruo — Causal Seeder Pipeline (Sprint 56.1)
===================================================
Pipeline autónomo que alimenta la Causal Knowledge Base.

Ejecuta ciclos:
  1. Selecciona un dominio/tema del backlog por prioridad ponderada
  2. Investiga eventos significativos (Perplexity Sonar API)
  3. Descompone cada evento en factores causales (CausalDecomposer via OpenAI/Gemini)
  4. Almacena en Causal KB con embeddings (Supabase)
  5. Reporta progreso y métricas

Dominios prioritarios (para predicción de negocios):
  - Startups: éxitos y fracasos de startups tech (2010-2026)
  - Mercados: movimientos significativos de mercado
  - Tecnología: adopción masiva de tecnologías
  - Regulación: cambios regulatorios con impacto económico
  - Geopolítica: eventos geopolíticos con impacto en negocios
  - AI: hitos de AI que cambiaron industrias

Budget: ~$0.50-1.00 por ciclo (embedding + decomposition)
Target: 10-15 eventos por ciclo, 3-4 ciclos por día = 30-60 eventos/día

Nota Sprint 56.1: CausalDecomposer está integrado aquí (no como módulo separado)
porque Sprint 55.4 no fue implementado. Se puede refactorizar en Sprint 57+.

Validated: Perplexity Sonar (ya en stack), OpenAI GPT-4o-mini (bajo costo),
           APScheduler 3.11.2 (MIT), wikipedia-api 0.7.1 (MIT)
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

import httpx
import structlog

logger = structlog.get_logger("kernel.causal_seeder")


# ── Dominios de Seeding ──────────────────────────────────────────────────────

SEED_DOMAINS = [
    {
        "name": "startup_successes",
        "description": "Startups que alcanzaron unicorn status o IPO exitosa",
        "query_template": (
            "List {n} significant startup successes from {year_range} with their key factors. "
            "For each startup: name, what caused their success, market timing, team composition, "
            "funding strategy, competitive advantages. Format as numbered list."
        ),
        "category": "business",
        "priority": 1,
    },
    {
        "name": "startup_failures",
        "description": "Startups que fracasaron a pesar de tener funding significativo",
        "query_template": (
            "List {n} notable startup failures from {year_range} that had significant funding but failed. "
            "For each: company name, root causes of failure, market timing issues, execution problems, "
            "competitive pressure. Format as numbered list."
        ),
        "category": "business",
        "priority": 1,
    },
    {
        "name": "market_crashes",
        "description": "Caídas significativas de mercado y sus causas",
        "query_template": (
            "Describe {n} significant market crashes or corrections from {year_range}. "
            "For each: what triggered it, underlying causes, early warning signs, recovery factors. "
            "Format as numbered list."
        ),
        "category": "economic",
        "priority": 2,
    },
    {
        "name": "tech_adoption",
        "description": "Tecnologías que alcanzaron adopción masiva",
        "query_template": (
            "List {n} technologies that achieved mass adoption in {year_range}. "
            "For each: technology name, what drove adoption, barriers overcome, network effects, "
            "timing factors. Format as numbered list."
        ),
        "category": "technological",
        "priority": 2,
    },
    {
        "name": "regulatory_shifts",
        "description": "Cambios regulatorios con impacto económico masivo",
        "query_template": (
            "Describe {n} major regulatory changes from {year_range} that significantly impacted businesses. "
            "For each: regulation name, what caused it, economic impact, winners and losers. "
            "Format as numbered list."
        ),
        "category": "political",
        "priority": 3,
    },
    {
        "name": "geopolitical_disruptions",
        "description": "Eventos geopolíticos que disrumpieron mercados",
        "query_template": (
            "List {n} geopolitical events from {year_range} that significantly disrupted global markets "
            "or supply chains. For each: event name, root causes, cascading effects, recovery timeline. "
            "Format as numbered list."
        ),
        "category": "political",
        "priority": 3,
    },
    {
        "name": "ai_milestones",
        "description": "Hitos de AI que cambiaron industrias",
        "query_template": (
            "Describe {n} AI milestones from {year_range} that transformed industries. "
            "For each: milestone name, technical breakthrough, market impact, adoption speed, "
            "enabling factors. Format as numbered list."
        ),
        "category": "technological",
        "priority": 1,
    },
]

YEAR_RANGES = ["2010-2015", "2015-2020", "2020-2023", "2023-2026"]

# Prompt del CausalDecomposer para descomponer eventos en factores
DECOMPOSER_SYSTEM_PROMPT = """You are a causal analysis expert. Given a historical event, 
decompose it into its root causal factors. Each factor should be:
- Atomic (one specific cause, not a bundle)
- Causal (not just correlated)
- Weighted by contribution (0.0-1.0)
- Directional (positive=contributed to outcome, negative=prevented/delayed it)

Return ONLY valid JSON with this exact structure:
{
  "title": "Event title (concise)",
  "description": "What happened and why it matters",
  "outcome": "The final result/impact",
  "factors": [
    {
      "description": "Specific causal factor",
      "category": "economic|political|social|technological|cultural|environmental|business",
      "weight": 0.8,
      "confidence": 0.9,
      "direction": "positive|negative|neutral",
      "evidence": ["evidence point 1", "evidence point 2"]
    }
  ],
  "tags": ["tag1", "tag2"]
}
Return 3-7 factors per event. Weights should sum approximately to 1.0."""


# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class SeedingCycle:
    """Registro de un ciclo de seeding."""
    cycle_id: str = field(default_factory=lambda: str(uuid4()))
    domain: str = ""
    year_range: str = ""
    events_discovered: int = 0
    events_decomposed: int = 0
    events_stored: int = 0
    cost_estimate_usd: float = 0.0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "domain": self.domain,
            "year_range": self.year_range,
            "events_discovered": self.events_discovered,
            "events_decomposed": self.events_decomposed,
            "events_stored": self.events_stored,
            "cost_estimate_usd": round(self.cost_estimate_usd, 4),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "errors": self.errors,
        }


# ── CausalDecomposer (integrado en Sprint 56.1, refactorizar en Sprint 57+) ──

class CausalDecomposer:
    """
    Descompone eventos históricos en factores causales usando LLM.
    Usa OpenAI GPT-4o-mini (bajo costo) o Gemini Flash como fallback.
    Integrado en CausalSeeder para Sprint 56.1.
    Se puede extraer como módulo independiente en Sprint 57+.
    """

    COST_PER_DECOMPOSITION_USD = 0.003  # ~$0.003 por evento con gpt-4o-mini

    def __init__(self, causal_kb=None):
        self._causal_kb = causal_kb
        self._openai_key = os.environ.get("OPENAI_API_KEY")
        self._gemini_key = os.environ.get("GEMINI_API_KEY")
        self._openai_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")

    async def decompose(
        self,
        title: str,
        context: str,
        category: str = "general",
        event_date: Optional[str] = None,
        sources: Optional[list[str]] = None,
        enrich_with_research: bool = False,
    ) -> Optional[str]:
        """
        Descomponer un evento en factores causales y almacenar en CausalKB.
        Retorna el event_id si fue exitoso, None si falló.
        """
        if not title:
            return None

        # Construir prompt
        user_prompt = f"""Event to analyze:
Title: {title}
Category: {category}
Context: {context[:2000] if context else 'No additional context provided'}
{f'Approximate date: {event_date}' if event_date else ''}

Decompose this event into its root causal factors."""

        # Intentar con OpenAI primero, Gemini como fallback
        decomposed = await self._call_llm(user_prompt)
        if not decomposed:
            logger.warning("causal_decomposer_llm_failed", title=title[:80])
            return None

        # Parsear respuesta JSON
        try:
            data = json.loads(decomposed)
        except json.JSONDecodeError:
            # Intentar extraer JSON del texto
            import re
            json_match = re.search(r'\{.*\}', decomposed, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.warning("causal_decomposer_json_parse_failed", title=title[:80])
                    return None
            else:
                return None

        # Construir CausalEvent
        if not self._causal_kb:
            logger.warning("causal_decomposer_no_kb")
            return None

        from memory.causal_kb import CausalEvent, CausalFactor

        factors = []
        for f_data in data.get("factors", []):
            factor = CausalFactor(
                description=f_data.get("description", ""),
                category=f_data.get("category", category),
                weight=float(f_data.get("weight", 0.5)),
                confidence=float(f_data.get("confidence", 0.7)),
                direction=f_data.get("direction", "positive"),
                evidence=f_data.get("evidence", []),
            )
            factors.append(factor)

        event = CausalEvent(
            title=data.get("title", title),
            description=data.get("description", context[:500] if context else ""),
            category=category,
            date=event_date,
            outcome=data.get("outcome", ""),
            factors=factors,
            sources=sources or ["causal_seeder"],
            tags=data.get("tags", []),
            decomposed_by="embrion",
            decomposed_at=datetime.now(timezone.utc).isoformat(),
            validation_score=0.6,  # Score inicial — mejora con validación
        )

        event_id = await self._causal_kb.store_event(event)
        logger.info(
            "causal_event_stored",
            event_id=event_id,
            title=title[:80],
            factors=len(factors),
        )
        return event_id

    async def _call_llm(self, user_prompt: str) -> Optional[str]:
        """Llamar al LLM para descomposición causal. OpenAI primero, Gemini fallback."""
        # Intentar OpenAI
        if self._openai_key:
            result = await self._call_openai(user_prompt)
            if result:
                return result

        # Fallback: Gemini
        if self._gemini_key:
            result = await self._call_gemini(user_prompt)
            if result:
                return result

        return None

    async def _call_openai(self, user_prompt: str) -> Optional[str]:
        """Llamar a OpenAI GPT-4o-mini para descomposición."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self._openai_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._openai_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": DECOMPOSER_SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1500,
                        "response_format": {"type": "json_object"},
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning("openai_decompose_error", status=resp.status_code)
        except Exception as e:
            logger.warning("openai_decompose_exception", error=str(e))
        return None

    async def _call_gemini(self, user_prompt: str) -> Optional[str]:
        """Llamar a Gemini Flash como fallback para descomposición."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                    params={"key": self._gemini_key},
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {"text": DECOMPOSER_SYSTEM_PROMPT + "\n\n" + user_prompt}
                                ]
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0.3,
                            "maxOutputTokens": 1500,
                            "responseMimeType": "application/json",
                        },
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    logger.warning("gemini_decompose_error", status=resp.status_code)
        except Exception as e:
            logger.warning("gemini_decompose_exception", error=str(e))
        return None


# ── CausalSeeder ─────────────────────────────────────────────────────────────

class CausalSeeder:
    """
    Pipeline autónomo de alimentación de la Causal KB.
    Ejecuta ciclos de seeding que descubren, descomponen, y almacenan eventos.

    Integración:
      - EmbrionScheduler: ejecuta run_cycle() cada 6 horas via tarea causal_seeding
      - CausalKB: almacena eventos descompuestos con embeddings
      - Perplexity Sonar: descubre eventos históricos relevantes
      - CausalDecomposer (integrado): descompone eventos en factores causales
    """

    MAX_EVENTS_PER_CYCLE = 15
    COST_PER_EVENT_USD = 0.05  # Estimado: embedding + decomposition
    DAILY_BUDGET_USD = float(os.environ.get("CAUSAL_SEEDER_DAILY_BUDGET", "5.0"))

    def __init__(
        self,
        decomposer: Optional[CausalDecomposer] = None,
        search_fn=None,
        db=None,
        causal_kb=None,
    ):
        """
        Args:
            decomposer: CausalDecomposer instance (se crea automáticamente si no se provee)
            search_fn: Función async de búsqueda web (Perplexity) — fn(query) -> str
            db: Supabase client para tracking de ciclos
            causal_kb: CausalKnowledgeBase instance
        """
        self._causal_kb = causal_kb
        self._decomposer = decomposer or CausalDecomposer(causal_kb=causal_kb)
        self._search = search_fn
        self._db = db
        self._sonar_key = os.environ.get("SONAR_API_KEY")
        self._daily_spend: float = 0.0
        self._daily_reset: Optional[str] = None
        self._cycles_completed: int = 0
        self._total_events_seeded: int = 0

    async def run_cycle(self, domain_name: Optional[str] = None) -> SeedingCycle:
        """
        Ejecutar un ciclo completo de seeding.
        Si no se especifica dominio, selecciona uno por prioridad + rotación.
        Retorna SeedingCycle con métricas del ciclo.
        """
        self._check_daily_budget()

        cycle = SeedingCycle(started_at=datetime.now(timezone.utc).isoformat())

        # Seleccionar dominio
        domain = self._select_domain(domain_name)
        year_range = random.choice(YEAR_RANGES)
        cycle.domain = domain["name"]
        cycle.year_range = year_range

        logger.info(
            "seeding_cycle_start",
            domain=domain["name"],
            year_range=year_range,
            cycle_id=cycle.cycle_id,
        )

        try:
            # Paso 1: Descubrir eventos via Perplexity
            events_raw = await self._discover_events(domain, year_range)
            cycle.events_discovered = len(events_raw)

            if not events_raw:
                logger.warning("seeding_no_events_discovered", domain=domain["name"])
                cycle.errors.append("No events discovered from search")
            else:
                # Paso 2: Descomponer y almacenar cada evento
                for event_data in events_raw[:self.MAX_EVENTS_PER_CYCLE]:
                    try:
                        event_id = await self._decompose_and_store(event_data, domain, year_range)
                        if event_id:
                            cycle.events_decomposed += 1
                            cycle.events_stored += 1
                            cycle.cost_estimate_usd += self.COST_PER_EVENT_USD
                            self._daily_spend += self.COST_PER_EVENT_USD
                        # Pequeña pausa para no saturar la API
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        err_msg = f"Decompose failed for '{event_data.get('title', 'unknown')[:60]}': {str(e)}"
                        cycle.errors.append(err_msg)
                        logger.warning("seeding_event_failed", error=str(e))

        except RuntimeError as e:
            # Budget exceeded
            cycle.errors.append(str(e))
            logger.warning("seeding_budget_exceeded", error=str(e))
        except Exception as e:
            cycle.errors.append(f"Cycle failed: {str(e)}")
            logger.error("seeding_cycle_failed", error=str(e), exc_info=True)

        cycle.completed_at = datetime.now(timezone.utc).isoformat()
        self._cycles_completed += 1
        self._total_events_seeded += cycle.events_stored

        # Persistir ciclo en Supabase si hay DB disponible
        await self._persist_cycle(cycle)

        logger.info(
            "seeding_cycle_complete",
            domain=domain["name"],
            year_range=year_range,
            discovered=cycle.events_discovered,
            stored=cycle.events_stored,
            cost=round(cycle.cost_estimate_usd, 4),
            total_seeded=self._total_events_seeded,
            errors=len(cycle.errors),
        )

        return cycle

    def _select_domain(self, domain_name: Optional[str] = None) -> dict:
        """Seleccionar dominio por nombre o por rotación ponderada por prioridad."""
        if domain_name:
            for d in SEED_DOMAINS:
                if d["name"] == domain_name:
                    return d

        # Selección ponderada: priority 1 = más probable (peso 1.0), priority 3 = menos (peso 0.33)
        weights = [1.0 / d["priority"] for d in SEED_DOMAINS]
        total = sum(weights)
        weights = [w / total for w in weights]

        return random.choices(SEED_DOMAINS, weights=weights, k=1)[0]

    async def _discover_events(self, domain: dict, year_range: str) -> list[dict[str, Any]]:
        """Descubrir eventos usando Perplexity Sonar API."""
        query = domain["query_template"].format(
            n=self.MAX_EVENTS_PER_CYCLE,
            year_range=year_range,
        )

        # Intentar con search_fn inyectada primero
        if self._search:
            try:
                result = await self._search(query)
                return self._parse_discovered_events(result, domain, year_range)
            except Exception as e:
                logger.warning("seeder_search_fn_failed", error=str(e))

        # Fallback: llamar Perplexity directamente
        if self._sonar_key:
            try:
                result = await self._call_perplexity(query)
                return self._parse_discovered_events(result, domain, year_range)
            except Exception as e:
                logger.warning("seeder_perplexity_failed", error=str(e))

        logger.warning("seeder_no_search_available", domain=domain["name"])
        return []

    async def _call_perplexity(self, query: str) -> str:
        """Llamar directamente a Perplexity Sonar API."""
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._sonar_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a historical research assistant. "
                                "Provide factual, well-structured lists of historical events. "
                                "Be concise but include key causal factors for each event."
                            ),
                        },
                        {"role": "user", "content": query},
                    ],
                    "max_tokens": 3000,
                    "temperature": 0.2,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def _parse_discovered_events(
        self, raw_result: str, domain: dict, year_range: str
    ) -> list[dict[str, Any]]:
        """Parsear resultado de búsqueda en eventos estructurados."""
        events = []

        if not raw_result or not isinstance(raw_result, str):
            return events

        # Intentar parsear como JSON primero
        try:
            data = json.loads(raw_result)
            if isinstance(data, list):
                return data
            if "events" in data:
                return data["events"]
        except (json.JSONDecodeError, TypeError):
            pass

        # Parsear texto libre: split por líneas numeradas o bullets
        lines = raw_result.split("\n")
        current_event: Optional[dict] = None

        for line in lines:
            line = line.strip()
            if not line:
                if current_event and current_event.get("title"):
                    events.append(current_event)
                    current_event = None
                continue

            # Detectar inicio de nuevo evento (línea numerada o con bullet)
            is_new_event = False
            for prefix in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.",
                           "11.", "12.", "13.", "14.", "15.", "- ", "* ", "• "]:
                if line.startswith(prefix):
                    is_new_event = True
                    if current_event and current_event.get("title"):
                        events.append(current_event)
                    # Limpiar el prefijo del título
                    clean_title = line
                    for p in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.",
                              "11.", "12.", "13.", "14.", "15.", "- ", "* ", "• "]:
                        if clean_title.startswith(p):
                            clean_title = clean_title[len(p):].strip()
                            break
                    # Limpiar bold markdown
                    clean_title = clean_title.replace("**", "").strip()
                    current_event = {
                        "title": clean_title[:200],
                        "context": "",
                        "category": domain["category"],
                        "year_range": year_range,
                    }
                    break

            if not is_new_event and current_event is not None:
                current_event["context"] += " " + line

        # Agregar el último evento si quedó pendiente
        if current_event and current_event.get("title"):
            events.append(current_event)

        # Limpiar contextos
        for ev in events:
            ev["context"] = ev.get("context", "").strip()

        return events

    async def _decompose_and_store(
        self, event_data: dict, domain: dict, year_range: str
    ) -> Optional[str]:
        """Descomponer un evento y almacenarlo en la Causal KB."""
        title = event_data.get("title", "").strip()
        context = event_data.get("context", "").strip()

        if not title:
            return None

        # Enriquecer contexto con year_range si es muy corto
        if len(context) < 50:
            context = f"Historical event from {year_range}. {context}"

        return await self._decomposer.decompose(
            title=title,
            context=context,
            category=domain["category"],
            event_date=None,  # Fecha aproximada del year_range
            sources=["perplexity_sonar", f"domain:{domain['name']}"],
            enrich_with_research=False,
        )

    def _check_daily_budget(self) -> None:
        """Verificar que no excedemos el budget diario."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._daily_reset != today:
            self._daily_spend = 0.0
            self._daily_reset = today

        if self._daily_spend >= self.DAILY_BUDGET_USD:
            raise RuntimeError(
                f"Daily seeding budget exceeded: "
                f"${self._daily_spend:.2f} >= ${self.DAILY_BUDGET_USD:.2f}"
            )

    async def _persist_cycle(self, cycle: SeedingCycle) -> None:
        """Persistir métricas del ciclo en Supabase."""
        if not self._db:
            return
        try:
            await self._db.upsert("seeding_cycles", {
                "id": cycle.cycle_id,
                "domain": cycle.domain,
                "year_range": cycle.year_range,
                "events_discovered": cycle.events_discovered,
                "events_stored": cycle.events_stored,
                "cost_usd": cycle.cost_estimate_usd,
                "errors": json.dumps(cycle.errors),
                "started_at": cycle.started_at,
                "completed_at": cycle.completed_at,
            })
        except Exception as e:
            logger.warning("seeding_cycle_persist_failed", error=str(e))

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas del seeder para el EmbrionScheduler."""
        return {
            "cycles_completed": self._cycles_completed,
            "total_events_seeded": self._total_events_seeded,
            "daily_spend_usd": round(self._daily_spend, 4),
            "daily_budget_usd": self.DAILY_BUDGET_USD,
            "budget_remaining_usd": round(
                max(0.0, self.DAILY_BUDGET_USD - self._daily_spend), 4
            ),
            "budget_exhausted": self._daily_spend >= self.DAILY_BUDGET_USD,
        }


# ── Singleton factory ─────────────────────────────────────────────────────────

_causal_seeder_instance: Optional[CausalSeeder] = None


def get_causal_seeder() -> Optional[CausalSeeder]:
    """Obtener la instancia singleton del CausalSeeder."""
    return _causal_seeder_instance


def init_causal_seeder(
    causal_kb=None,
    search_fn=None,
    db=None,
) -> CausalSeeder:
    """Inicializar el singleton del CausalSeeder."""
    global _causal_seeder_instance
    decomposer = CausalDecomposer(causal_kb=causal_kb)
    _causal_seeder_instance = CausalSeeder(
        decomposer=decomposer,
        search_fn=search_fn,
        db=db,
        causal_kb=causal_kb,
    )
    return _causal_seeder_instance
