"""
El Monstruo — Embrión-Investigador (Sprint 60)
===============================================
7mo y ÚLTIMO Embrión especializado. Completa la colmena.

Dominio: Research profundo, benchmarks, competitive intelligence,
         tendencias de mercado, papers académicos, due diligence.

Hereda: EmbrionLoop (Sprint 54)
Hermanos: Ventas(57), Técnico(58), Vigía(58), Creativo(59), Estratega(59), Financiero(60)

MILESTONE: Con este embrión, la colmena está COMPLETA (7/7).

Objetivo cubierto: #7 — No Inventar la Rueda (investigar antes de construir)
Sprint 60 — 2026-05-01

Soberanía: Usa Perplexity para research en tiempo real.
           Alternativa: DuckDuckGo API + Sabios para síntesis.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import structlog

logger = structlog.get_logger("monstruo.embrion.investigador")


# ── Errores con identidad ────────────────────────────────────────────────────


class EmbrionInvestigadorError(Exception):
    """Error base del Embrión-Investigador."""


EMBRION_INVESTIGADOR_SIN_BACKENDS = (
    "EMBRION_INVESTIGADOR_SIN_BACKENDS: "
    "No hay backends de investigación disponibles (Sabios ni Perplexity). "
    "Sugerencia: Configura OPENAI_API_KEY o SONAR_API_KEY para habilitar el research."
)

EMBRION_INVESTIGADOR_BUDGET_AGOTADO = (
    "EMBRION_INVESTIGADOR_BUDGET_AGOTADO: "
    "Budget diario de ${budget:.2f} agotado (gastado: ${spent:.2f}). "
    "Sugerencia: El research se reanudará mañana o aumenta INVESTIGADOR_DAILY_BUDGET."
)


# ── Dataclasses ──────────────────────────────────────────────────────────────


@dataclass
class ResearchReport:
    """
    Reporte de investigación estructurado.

    Args:
        topic: Tema investigado.
        summary: Resumen ejecutivo (3-5 oraciones).
        key_findings: Hallazgos clave con fuente y nivel de confianza.
        data_points: Métricas y datos cuantitativos verificados.
        competitors: Análisis de competidores (si aplica).
        opportunities: Oportunidades identificadas.
        risks: Riesgos identificados.
        methodology: Cómo se condujo la investigación.
        limitations: Gaps y limitaciones del research.
        generated_at: ISO timestamp de generación.
        cost_usd: Costo del research en USD.
    """

    topic: str
    summary: str
    key_findings: list[dict]
    data_points: list[dict]
    competitors: list[dict]
    opportunities: list[str]
    risks: list[str]
    methodology: str
    limitations: list[str]
    generated_at: str
    cost_usd: float = 0.0

    def to_dict(self) -> dict:
        """Serializar para el Command Center."""
        return {
            "topic": self.topic,
            "summary": self.summary,
            "key_findings_count": len(self.key_findings),
            "data_points_count": len(self.data_points),
            "competitors_analyzed": len(self.competitors),
            "opportunities_count": len(self.opportunities),
            "risks_count": len(self.risks),
            "methodology": self.methodology,
            "limitations": self.limitations,
            "generated_at": self.generated_at,
            "cost_usd": round(self.cost_usd, 4),
        }

    def to_markdown(self) -> str:
        """Generar reporte en formato Markdown."""
        md = f"# Research Report: {self.topic}\n"
        md += f"*Generado: {self.generated_at}*\n\n"
        md += f"## Resumen Ejecutivo\n{self.summary}\n\n"

        if self.key_findings:
            md += "## Hallazgos Clave\n"
            for f in self.key_findings:
                conf = f.get("confidence", "unknown")
                source = f.get("source", "unknown")
                md += f"- [{conf}] {f.get('finding', '')} *(Fuente: {source})*\n"

        if self.data_points:
            md += "\n## Datos Cuantitativos\n"
            for dp in self.data_points:
                md += f"- **{dp.get('metric', '')}**: {dp.get('value', '')} *(Fuente: {dp.get('source', '')})*\n"

        if self.competitors:
            md += "\n## Análisis Competitivo\n"
            for c in self.competitors:
                md += f"### {c.get('name', 'Competidor')}\n"
                md += f"- Fortalezas: {', '.join(c.get('strengths', []))}\n"
                md += f"- Debilidades: {', '.join(c.get('weaknesses', []))}\n"

        if self.opportunities:
            md += "\n## Oportunidades\n"
            for o in self.opportunities:
                md += f"- {o}\n"

        if self.risks:
            md += "\n## Riesgos\n"
            for r in self.risks:
                md += f"- {r}\n"

        md += f"\n## Metodología\n{self.methodology}\n"

        if self.limitations:
            md += "\n## Limitaciones\n"
            for l in self.limitations:
                md += f"- {l}\n"

        return md


@dataclass
class EmbrionInvestigador:
    """
    Embrión especializado en investigación profunda.

    7mo y último Embrión — completa la colmena de 7 especialistas.

    Capacidades:
    - Deep research sobre cualquier tema
    - Competitive intelligence
    - Fact-checking de claims
    - Daily briefing de noticias relevantes
    - Trend analysis en nichos activos

    Args:
        _sabios: Interfaz a los Sabios para síntesis (opcional).
        _supabase: Cliente Supabase para persistencia (opcional).
        budget_daily_usd: Presupuesto diario máximo en USD.

    Soberanía: Funciona sin Perplexity usando solo Sabios.
               Alternativa: DuckDuckGo API + Sabios para síntesis.
    """

    _sabios: Optional[object] = field(default=None, repr=False)
    _supabase: Optional[object] = field(default=None, repr=False)
    budget_daily_usd: float = float(os.getenv("INVESTIGADOR_DAILY_BUDGET", "2.5"))
    _spent_today: float = 0.0
    _reports_generados: int = 0
    _ciclos_ejecutados: int = 0

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

    def _check_budget(self) -> None:
        """
        Verificar que hay budget disponible antes de hacer research.

        Raises:
            EmbrionInvestigadorError: Si el budget diario está agotado.
        """
        if self._spent_today >= self.budget_daily_usd:
            raise EmbrionInvestigadorError(
                EMBRION_INVESTIGADOR_BUDGET_AGOTADO.format(
                    budget=self.budget_daily_usd,
                    spent=self._spent_today,
                )
            )

    async def deep_research(
        self,
        topic: str,
        depth: str = "standard",
        include_competitors: bool = True,
    ) -> ResearchReport:
        """
        Investigación profunda sobre un tema.

        Args:
            topic: Tema a investigar.
            depth: Nivel de profundidad ('quick', 'standard', 'deep').
            include_competitors: Si incluir análisis competitivo.

        Returns:
            ResearchReport estructurado.

        Raises:
            EmbrionInvestigadorError: Si no hay backends o budget agotado.
        """
        self._check_budget()

        if not self._sabios:
            raise EmbrionInvestigadorError(EMBRION_INVESTIGADOR_SIN_BACKENDS)

        # Intentar enriquecer con Perplexity si está disponible
        real_data = ""
        try:
            import httpx

            sonar_key = os.getenv("SONAR_API_KEY")
            if sonar_key:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        "https://api.perplexity.ai/chat/completions",
                        headers={"Authorization": f"Bearer {sonar_key}"},
                        json={
                            "model": "sonar-pro",
                            "messages": [
                                {"role": "user", "content": f"Latest data and statistics about {topic} in 2026"}
                            ],
                        },
                        timeout=30.0,
                    )
                    if resp.status_code == 200:
                        real_data = resp.json()["choices"][0]["message"]["content"]
                        self._spent_today += 0.01
        except Exception as e:
            logger.warning("perplexity_research_fallido", error=str(e))

        # Síntesis con Sabios
        prompt = f"""Conduct deep research on: {topic}

{"Real-time data from web research:" if real_data else "No real-time data available."}
{real_data[:3000] if real_data else "Use your training knowledge but mark all data with confidence levels."}

Depth level: {depth}
Include competitors: {include_competitors}

Respond ONLY in JSON (no markdown wrapper):
{{
    "summary": "Executive summary (3-5 sentences)",
    "key_findings": [
        {{"finding": "...", "source": "...", "confidence": "high|medium|low", "date": "YYYY-MM"}}
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
        self._spent_today += 0.02

        try:
            raw = self._extract_json(response)
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {
                "summary": response[:500],
                "key_findings": [],
                "data_points": [],
                "competitors": [],
                "opportunities": [],
                "risks": [],
                "methodology": "LLM synthesis (JSON parse failed)",
                "limitations": ["JSON parsing failed — raw response used"],
            }

        report = ResearchReport(
            topic=topic,
            generated_at=datetime.now(timezone.utc).isoformat(),
            cost_usd=self._spent_today,
            **data,
        )

        self._reports_generados += 1

        # Persistir en Supabase si disponible
        if self._supabase:
            try:
                self._supabase.table("research_reports").insert(
                    {
                        "topic": topic,
                        "summary": report.summary,
                        "findings_count": len(report.key_findings),
                        "generated_at": report.generated_at,
                        "cost_usd": report.cost_usd,
                    }
                ).execute()
            except Exception:
                pass

        logger.info(
            "deep_research_completado",
            topic=topic,
            findings=len(report.key_findings),
            cost_usd=round(self._spent_today, 4),
        )

        return report

    async def competitive_analysis(
        self,
        our_product: str,
        competitors: list[str],
    ) -> dict:
        """
        Análisis competitivo detallado.

        Args:
            our_product: Descripción de nuestro producto.
            competitors: Lista de competidores a analizar.

        Returns:
            Dict con análisis competitivo estructurado.
        """
        self._check_budget()

        if not self._sabios:
            raise EmbrionInvestigadorError(EMBRION_INVESTIGADOR_SIN_BACKENDS)

        prompt = f"""Perform competitive analysis:
Our product: {our_product}
Competitors: {", ".join(competitors)}

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
        self._spent_today += 0.02

        try:
            return json.loads(self._extract_json(response))
        except json.JSONDecodeError:
            return {"analysis": response, "parse_error": True}

    async def generate_daily_briefing(self) -> dict:
        """
        Tarea autónoma: briefing diario de noticias relevantes.

        Returns:
            Dict con briefing del día.
        """
        self._ciclos_ejecutados += 1

        # Intentar con Perplexity primero
        try:
            import httpx

            sonar_key = os.getenv("SONAR_API_KEY")
            if sonar_key:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        "https://api.perplexity.ai/chat/completions",
                        headers={"Authorization": f"Bearer {sonar_key}"},
                        json={
                            "model": "sonar-pro",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": "Top AI and digital business news today, focus on startups, SaaS, and AI tools. Be concise.",
                                }
                            ],
                        },
                        timeout=30.0,
                    )
                    if resp.status_code == 200:
                        briefing = resp.json()["choices"][0]["message"]["content"]
                        self._spent_today += 0.01
                        return {
                            "briefing": briefing,
                            "source": "perplexity",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
        except Exception as e:
            logger.warning("perplexity_briefing_fallido", error=str(e))

        # Fallback a Sabios
        if self._sabios:
            try:
                prompt = "What are the most important AI and digital business developments happening right now? Focus on actionable insights for a startup building AI-powered SaaS products."
                response = await self._sabios.ask(prompt)
                self._spent_today += 0.01
                return {
                    "briefing": response,
                    "source": "llm_knowledge",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            except Exception as e:
                logger.warning("sabios_briefing_fallido", error=str(e))

        return {
            "briefing": "No research backends available",
            "source": "none",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def fact_check_claims(self, claims: list[str]) -> list[dict]:
        """
        Verificar claims específicos contra evidencia disponible.

        Args:
            claims: Lista de claims a verificar.

        Returns:
            Lista de resultados con veredicto y evidencia.
        """
        results = []

        for claim in claims:
            self._check_budget()

            if self._sabios:
                try:
                    prompt = f"""Fact-check this claim: "{claim}"

Respond in JSON (no markdown wrapper):
{{"verdict": "true|false|partially_true|unverifiable", "evidence": "...", "confidence": "high|medium|low", "sources": ["..."]}}"""
                    response = await self._sabios.ask(prompt)
                    self._spent_today += 0.01

                    try:
                        verification = json.loads(self._extract_json(response))
                    except json.JSONDecodeError:
                        verification = {"verdict": "unverifiable", "evidence": response[:200], "confidence": "low"}

                    results.append(
                        {
                            "claim": claim,
                            "verification": verification,
                            "source": "llm_knowledge",
                        }
                    )
                except Exception as e:
                    logger.warning("fact_check_fallido", claim=claim[:50], error=str(e))
                    results.append({"claim": claim, "verification": {"verdict": "error"}, "source": "error"})

        return results

    async def analyze_trends(self, nichos: Optional[list[str]] = None) -> list[dict]:
        """
        Analizar tendencias emergentes en nichos activos.

        Args:
            nichos: Lista de nichos a analizar. Si None, usa nichos genéricos de AI/SaaS.

        Returns:
            Lista de tendencias detectadas.
        """
        self._check_budget()

        if not self._sabios:
            return []

        nichos = nichos or ["AI tools", "SaaS", "no-code platforms", "developer tools", "B2B automation"]

        prompt = f"""Analyze emerging trends in these niches: {", ".join(nichos)}

For each niche, identify:
1. Top 3 emerging trends (with evidence)
2. Opportunities for new products
3. Declining patterns to avoid

Respond in JSON array:
[{{"niche": "...", "trends": [{{"name": "...", "evidence": "...", "opportunity": "..."}}], "declining": ["..."]}}]"""

        response = await self._sabios.ask(prompt)
        self._spent_today += 0.02

        try:
            return json.loads(self._extract_json(response))
        except json.JSONDecodeError:
            return [{"niche": "parse_error", "raw": response[:200]}]

    def to_dict(self) -> dict:
        """
        Serializar estado para el Command Center.

        Returns:
            Dict con estado del Embrión-Investigador y milestone de colmena completa.
        """
        return {
            "modulo": "embrion_investigador",
            "sprint": "60.5",
            "objetivo": "Obj #7 — No Inventar la Rueda",
            "milestone": "COLMENA_COMPLETA_7_DE_7",
            "embriones_activos": ["ventas", "tecnico", "vigia", "creativo", "estratega", "financiero", "investigador"],
            "ciclos_ejecutados": self._ciclos_ejecutados,
            "reports_generados": self._reports_generados,
            "budget_diario_usd": self.budget_daily_usd,
            "gastado_hoy_usd": round(self._spent_today, 4),
            "budget_restante_usd": round(max(0, self.budget_daily_usd - self._spent_today), 4),
        }

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extraer JSON de respuesta de LLM."""
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        if "```" in text:
            return text.split("```")[1].split("```")[0]
        return text.strip()


# ── Singleton ────────────────────────────────────────────────────────────────

_embrion_investigador: Optional[EmbrionInvestigador] = None


def get_embrion_investigador() -> Optional[EmbrionInvestigador]:
    """Obtener la instancia singleton del EmbrionInvestigador."""
    return _embrion_investigador


def init_embrion_investigador(sabios=None, supabase=None) -> EmbrionInvestigador:
    """
    Inicializar el EmbrionInvestigador como singleton.

    MILESTONE: Inicializar este Embrión completa la colmena de 7 especialistas.

    Args:
        sabios: Interfaz a los Sabios para síntesis (opcional).
        supabase: Cliente Supabase para persistencia (opcional).

    Returns:
        Instancia inicializada del EmbrionInvestigador.
    """
    global _embrion_investigador
    _embrion_investigador = EmbrionInvestigador(_sabios=sabios, _supabase=supabase)
    logger.info(
        "embrion_investigador_inicializado",
        milestone="COLMENA_COMPLETA_7_DE_7",
        embriones=["ventas", "tecnico", "vigia", "creativo", "estratega", "financiero", "investigador"],
    )
    return _embrion_investigador
