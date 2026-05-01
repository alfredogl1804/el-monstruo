"""
El Monstruo — Embrión-Estratega (Sprint 59.4)
=============================================
5to Embrión especializado. Dominio: Estrategia, planning, market analysis.

Responsabilidad:
  - Análisis de mercado con datos cuantitativos (TAM, CAGR, competencia)
  - Planes estratégicos por fases con KPIs y criterios de abandono
  - Priorización de tareas via framework ICE (Impact × Confidence × Ease)
  - Monitoreo de oportunidades de mercado (tarea autónoma cada 12h)
  - Evaluación de riesgos de proyectos activos (tarea autónoma cada 24h)

Principios:
  - Datos sobre opiniones. Siempre busca evidencia.
  - First principles thinking. Descompón problemas complejos.
  - Contrarian thinking. Cuestiona assumptions populares.
  - Speed of execution > perfection of plan.

Hermanos:
  - Embrión-Ventas (Sprint 57)
  - Embrión-Técnico (Sprint 58)
  - Embrión-Vigía (Sprint 58)
  - Embrión-Creativo (Sprint 59)

Sprint: 59 — "El Monstruo Habla al Mundo"
Fecha: 2026-05-01

Soberanía:
  - Perplexity Sonar Pro (research con fuentes, market data)
  - GPT-4o (análisis estratégico, planes)
  - Gemini Flash (fallback)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import structlog

logger = structlog.get_logger("monstruo.embrion.estratega")


# ── Errores con identidad ──────────────────────────────────────────────────────

class EMBRION_ESTRATEGA_SIN_SABIOS(RuntimeError):
    """No hay cliente de Sabios configurado para análisis estratégico.
    
    Sugerencia: Inyecta _sabios al instanciar EmbrionEstratega.
    """


class EMBRION_ESTRATEGA_JSON_INVALIDO(ValueError):
    """El LLM retornó JSON inválido en la respuesta estratégica.
    
    Sugerencia: Verifica el prompt o usa el fallback de análisis simplificado.
    """


# ── Dataclasses de dominio ─────────────────────────────────────────────────────

@dataclass
class MarketAnalysis:
    """Análisis de mercado estructurado.
    
    Args:
        market_size_usd: TAM estimado con fuente.
        growth_rate: CAGR con período de tiempo.
        key_players: Lista de competidores con market share, fortaleza y debilidad.
        opportunities: Oportunidades identificadas en el mercado.
        threats: Amenazas y riesgos del mercado.
        entry_barriers: Barreras de entrada al mercado.
        recommended_positioning: Estrategia de posicionamiento recomendada.
        analyzed_at: Timestamp del análisis.
    """
    market_size_usd: str
    growth_rate: str
    key_players: list[dict]
    opportunities: list[str]
    threats: list[str]
    entry_barriers: list[str]
    recommended_positioning: str
    analyzed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        """Serializar para el Command Center."""
        return {
            "market_size_usd": self.market_size_usd,
            "growth_rate": self.growth_rate,
            "key_players": self.key_players,
            "opportunities": self.opportunities,
            "threats": self.threats,
            "entry_barriers": self.entry_barriers,
            "recommended_positioning": self.recommended_positioning,
            "analyzed_at": self.analyzed_at,
        }


@dataclass
class StrategicPlan:
    """Plan estratégico con fases, KPIs y criterios de abandono.
    
    Args:
        vision: Visión en una oración.
        phases: Fases del plan con nombre, duración, objetivos, KPIs y presupuesto.
        risks: Riesgos con probabilidad, impacto y mitigación.
        success_metrics: Métricas de éxito cuantificables.
        kill_criteria: Criterios para pivotar o abandonar el proyecto.
        created_at: Timestamp de creación.
    """
    vision: str
    phases: list[dict]
    risks: list[dict]
    success_metrics: list[str]
    kill_criteria: list[str]
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        """Serializar para el Command Center."""
        return {
            "vision": self.vision,
            "phases": self.phases,
            "risks": self.risks,
            "success_metrics": self.success_metrics,
            "kill_criteria": self.kill_criteria,
            "created_at": self.created_at,
        }


STRATEGIST_SYSTEM_PROMPT = """Eres el Embrión-Estratega de El Monstruo.
Tu dominio es la ESTRATEGIA y el PENSAMIENTO de alto nivel.

PRINCIPIOS:
- Datos sobre opiniones. Siempre busca evidencia.
- First principles thinking. Descompón problemas complejos.
- Contrarian thinking. Cuestiona assumptions populares.
- Speed of execution > perfection of plan.

RESTRICCIONES:
- Nunca recomiendes sin justificación cuantitativa
- Siempre incluye al menos un escenario pesimista
- Identifica los 3 riesgos principales de cada recomendación
- Kill criteria son obligatorios en todo plan estratégico
"""


# ── Embrión principal ──────────────────────────────────────────────────────────

@dataclass
class EmbrionEstratega:
    """Embrión especializado en estrategia, planning y análisis de mercado.
    
    Genera análisis de mercado con datos cuantitativos, planes estratégicos
    por fases y prioriza tareas via framework ICE.
    
    Args:
        _sabios: Cliente de Sabios para análisis estratégico via LLM.
        budget_daily_usd: Presupuesto diario máximo en USD.
    
    Soberanía:
        - Perplexity Sonar Pro (market data con fuentes)
        - GPT-4o (análisis estratégico)
        - Gemini Flash (fallback)
    """
    _sabios: Optional[object] = field(default=None, repr=False)
    budget_daily_usd: float = 2.0
    _spent_today: float = field(default=0.0, repr=False)
    _ciclos_completados: int = field(default=0, repr=False)
    _last_market_scan: Optional[str] = field(default=None, repr=False)

    EMBRION_ID: str = field(default="embrion-estratega", init=False)
    SPECIALIZATION: str = field(
        default="Estrategia, Planning, Market Analysis, Priorización", init=False
    )

    DEFAULT_TASKS: dict = field(default_factory=lambda: {
        "market_scan": {
            "description": "Escanear oportunidades de mercado para proyectos activos",
            "interval_hours": 12,
            "handler": "scan_market_opportunities",
        },
        "priority_review": {
            "description": "Revisar y re-priorizar tareas pendientes",
            "interval_hours": 6,
            "handler": "review_priorities",
        },
        "risk_assessment": {
            "description": "Evaluar riesgos de proyectos activos",
            "interval_hours": 24,
            "handler": "assess_project_risks",
        },
        "competitive_intel": {
            "description": "Monitorear competencia de proyectos activos",
            "interval_hours": 48,
            "handler": "monitor_competition",
        },
    }, init=False)

    async def analyze_market(
        self,
        niche: str,
        geography: str = "global",
    ) -> MarketAnalysis:
        """Analizar mercado para un nicho específico.
        
        Args:
            niche: Nicho o industria a analizar (ej: 'SaaS para restaurantes').
            geography: Geografía de análisis (ej: 'México', 'LATAM', 'global').
        
        Returns:
            MarketAnalysis con TAM, CAGR, competidores, oportunidades y amenazas.
        
        Raises:
            EMBRION_ESTRATEGA_SIN_SABIOS: Si no hay cliente LLM configurado.
        """
        if not self._sabios:
            raise EMBRION_ESTRATEGA_SIN_SABIOS(
                "EmbrionEstratega requiere _sabios para análisis de mercado."
            )

        prompt = f"""{STRATEGIST_SYSTEM_PROMPT}

Perform a comprehensive market analysis for:
- Niche: {niche}
- Geography: {geography}

Provide data-driven analysis. Use real numbers where possible.
If exact data unavailable, provide reasonable estimates with confidence levels.

Respond in JSON:
{{
    "market_size_usd": "TAM estimate with source/confidence",
    "growth_rate": "CAGR % with timeframe",
    "key_players": [
        {{"name": "...", "market_share": "X%", "strength": "...", "weakness": "..."}}
    ],
    "opportunities": ["opportunity1", "opportunity2", "opportunity3"],
    "threats": ["threat1", "threat2", "threat3"],
    "entry_barriers": ["barrier1", "barrier2"],
    "recommended_positioning": "Specific positioning strategy with rationale"
}}"""

        response = await self._sabios.ask(prompt)
        data = self._parse_json_response(response)

        self._ciclos_completados += 1
        logger.info("market_analysis_completado", niche=niche, geography=geography)

        return MarketAnalysis(
            market_size_usd=data["market_size_usd"],
            growth_rate=data["growth_rate"],
            key_players=data["key_players"],
            opportunities=data["opportunities"],
            threats=data["threats"],
            entry_barriers=data["entry_barriers"],
            recommended_positioning=data["recommended_positioning"],
        )

    async def create_strategic_plan(
        self,
        business_type: str,
        niche: str,
        budget: str = "bootstrap",
        timeline: str = "6 months",
    ) -> StrategicPlan:
        """Crear plan estratégico completo con fases y criterios de abandono.
        
        Args:
            business_type: Tipo de negocio ('ecommerce', 'saas', 'content', 'service').
            niche: Nicho específico del negocio.
            budget: Presupuesto disponible ('bootstrap', '$5000', '$50000').
            timeline: Horizonte temporal del plan ('3 months', '6 months', '1 year').
        
        Returns:
            StrategicPlan con fases, KPIs, riesgos y kill criteria.
        
        Raises:
            EMBRION_ESTRATEGA_SIN_SABIOS: Si no hay cliente LLM configurado.
        """
        if not self._sabios:
            raise EMBRION_ESTRATEGA_SIN_SABIOS(
                "EmbrionEstratega requiere _sabios para crear planes estratégicos."
            )

        prompt = f"""{STRATEGIST_SYSTEM_PROMPT}

Create a strategic plan for:
- Business type: {business_type}
- Niche: {niche}
- Budget: {budget}
- Timeline: {timeline}

Requirements:
- Phase-based approach (3-5 phases)
- Each phase has clear KPIs with numeric targets
- Include kill criteria (when to pivot/abandon)
- Pessimistic scenario must be included in risks

Respond in JSON:
{{
    "vision": "One-sentence vision",
    "phases": [
        {{
            "name": "Phase name",
            "duration": "X weeks/months",
            "objectives": ["obj1", "obj2"],
            "kpis": ["kpi1 (target: X)", "kpi2 (target: Y)"],
            "budget": "$X"
        }}
    ],
    "risks": [
        {{
            "risk": "Description",
            "probability": "high|medium|low",
            "impact": "high|medium|low",
            "mitigation": "Specific mitigation strategy"
        }}
    ],
    "success_metrics": ["metric1 (target: X)", "metric2 (target: Y)"],
    "kill_criteria": ["If X doesn't happen by month Y, pivot", "If Z, abandon"]
}}"""

        response = await self._sabios.ask(prompt)
        data = self._parse_json_response(response)

        logger.info(
            "strategic_plan_creado",
            business_type=business_type,
            niche=niche,
            phases=len(data.get("phases", [])),
        )

        return StrategicPlan(
            vision=data["vision"],
            phases=data["phases"],
            risks=data["risks"],
            success_metrics=data["success_metrics"],
            kill_criteria=data["kill_criteria"],
        )

    async def prioritize_tasks(self, tasks: list[dict]) -> list[dict]:
        """Priorizar tareas usando framework ICE (Impact × Confidence × Ease).
        
        Args:
            tasks: Lista de dicts con al menos 'task' y opcionalmente 'description'.
        
        Returns:
            Lista de tareas ordenada por ICE score descendente, con scores individuales.
        
        Raises:
            EMBRION_ESTRATEGA_SIN_SABIOS: Si no hay cliente LLM configurado.
        """
        if not self._sabios:
            raise EMBRION_ESTRATEGA_SIN_SABIOS(
                "EmbrionEstratega requiere _sabios para priorizar tareas."
            )

        prompt = f"""Prioritize these tasks using the ICE framework:
(Impact × Confidence × Ease, each scored 1-10)

Tasks: {json.dumps(tasks, default=str)}

For each task, score and rank. Respond in JSON array:
[
    {{
        "task": "...",
        "impact": N,
        "confidence": N,
        "ease": N,
        "ice_score": N,
        "rationale": "Why this priority"
    }}
]

Sort by ICE score descending. Be strict — most tasks should score 1-5, not 8-10."""

        response = await self._sabios.ask(prompt)
        result = self._parse_json_response(response)

        logger.info("tasks_priorizadas", total=len(tasks))
        return result if isinstance(result, list) else []

    async def scan_market_opportunities(self) -> dict:
        """Tarea autónoma: escanear oportunidades de mercado emergentes.
        
        Returns:
            Dict con lista de oportunidades y timestamp de escaneo.
        """
        if not self._sabios:
            logger.warning("market_scan_sin_sabios")
            return {"opportunities": [], "scanned_at": datetime.now(timezone.utc).isoformat()}

        prompt = """Identify 3 emerging market opportunities in digital businesses that are:
1. Underserved (few direct competitors)
2. Growing (>20% CAGR)
3. Accessible (can be started with <$5000)
4. Specific to 2026 trends

For each, provide: niche, market_size_estimate, why_now, entry_strategy, first_step.
Respond in JSON array."""

        response = await self._sabios.ask(prompt)
        opportunities = self._parse_json_response(response)

        self._last_market_scan = datetime.now(timezone.utc).isoformat()
        logger.info(
            "market_scan_completado",
            total=len(opportunities) if isinstance(opportunities, list) else 0,
        )
        return {
            "opportunities": opportunities if isinstance(opportunities, list) else [],
            "scanned_at": self._last_market_scan,
        }

    async def assess_project_risks(self, project_context: Optional[dict] = None) -> dict:
        """Tarea autónoma: evaluar riesgos de proyectos activos.
        
        Args:
            project_context: Contexto del proyecto a evaluar (opcional).
        
        Returns:
            Dict con lista de riesgos priorizados y timestamp.
        """
        if not self._sabios:
            logger.warning("risk_assessment_sin_sabios")
            return {"risks": [], "assessed_at": datetime.now(timezone.utc).isoformat()}

        context = json.dumps(project_context or {"status": "no active projects"})
        prompt = f"""Assess risks for current projects:
Context: {context}

Identify top 5 risks with:
- risk: description
- probability: high/medium/low
- impact: high/medium/low
- mitigation: specific action
- urgency: immediate/short-term/long-term

Respond in JSON array. Be specific, not generic."""

        response = await self._sabios.ask(prompt)
        risks = self._parse_json_response(response)

        assessed_at = datetime.now(timezone.utc).isoformat()
        logger.info("risk_assessment_completado", total=len(risks) if isinstance(risks, list) else 0)
        return {
            "risks": risks if isinstance(risks, list) else [],
            "assessed_at": assessed_at,
        }

    def _parse_json_response(self, response: str) -> dict:
        """Extraer y parsear JSON de respuesta LLM.
        
        Args:
            response: Respuesta raw del LLM.
        
        Returns:
            Dict o list parseado del JSON.
        
        Raises:
            EMBRION_ESTRATEGA_JSON_INVALIDO: Si el JSON no es parseable.
        """
        json_str = response.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as _e:
            raise EMBRION_ESTRATEGA_JSON_INVALIDO(
                f"JSON inválido en respuesta del LLM: {str(_e)[:100]}"
            ) from _e

    def to_dict(self) -> dict:
        """Estado del embrión para consumo del Command Center.
        
        Returns:
            Dict serializable con estado actual del Embrión-Estratega.
        """
        return {
            "embrion_id": self.EMBRION_ID,
            "specialization": self.SPECIALIZATION,
            "version": "1.0.0-sprint59",
            "objetivo": "#11 Multiplicación de Embriones",
            "estado": "activo" if self._sabios else "sin_sabios",
            "ciclos_completados": self._ciclos_completados,
            "budget_daily_usd": self.budget_daily_usd,
            "spent_today_usd": round(self._spent_today, 4),
            "tasks_autonomas": list(self.DEFAULT_TASKS.keys()),
            "last_market_scan": self._last_market_scan,
        }
