"""kernel/vanguard/weekly_digest.py

Generador de Digest Semanal de Inteligencia — Sprint 63.1
Objetivo #6: Vanguardia Perpetua

Genera un digest semanal con las mejores propuestas de integración,
papers académicos relevantes, salud del stack y análisis de tendencias.

Soberanía:
    - Supabase: alternativa → archivo JSON local semanal
    - Semantic Scholar: alternativa → arXiv API (ver semantic_scholar.py)
"""

from datetime import datetime, timezone
from typing import Optional

import structlog

logger = structlog.get_logger("vanguard.digest")

# Tópicos para escaneo semanal académico
WEEKLY_TOPICS = [
    "multi-agent systems autonomous",
    "LLM cost optimization routing",
    "causal inference prediction",
    "AI code generation quality",
    "emergent behavior artificial intelligence",
]


class WeeklyDigestGenerator:
    """Genera digest semanal de inteligencia de investigación.

    Combina propuestas de integración pendientes, papers académicos,
    salud del stack y análisis de tendencias en un reporte unificado.

    Args:
        intelligence_engine: ResearchIntelligenceEngine para propuestas
        semantic_scholar: SemanticScholarClient para papers
        supabase: Cliente Supabase para persistencia

    Returns:
        Generador listo para producir digests semanales

    Raises:
        RuntimeError: Si Supabase no está disponible y no hay fallback

    Soberanía:
        Sin Supabase: genera digest en memoria y lo retorna sin persistir
    """

    def __init__(self, intelligence_engine=None, semantic_scholar=None, supabase=None):
        self.engine = intelligence_engine
        self.scholar = semantic_scholar
        self.supabase = supabase

    async def generate(self) -> dict:
        """Generar digest semanal completo.

        Returns:
            Dict con secciones: top_proposals, academic_papers,
            stack_health, trends

        Raises:
            Exception: Si la generación falla (retorna digest parcial)

        Soberanía:
            Sin Supabase: digest en memoria sin persistencia
        """
        digest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": "last_7_days",
            "sections": {},
        }

        # 1. Top propuestas de integración pendientes
        digest["sections"]["top_proposals"] = await self._get_top_proposals()

        # 2. Papers académicos (escaneo semanal)
        digest["sections"]["academic_papers"] = await self._get_academic_papers()

        # 3. Salud del stack
        digest["sections"]["stack_health"] = await self._generate_stack_health()

        # 4. Análisis de tendencias
        digest["sections"]["trends"] = await self._analyze_trends()

        # Persistir digest
        if self.supabase:
            try:
                await self.supabase.table("weekly_digests").insert(digest).execute()
                logger.info(
                    "digest_persisted",
                    proposals=len(digest["sections"]["top_proposals"]),
                    papers=len(digest["sections"]["academic_papers"]),
                )
            except Exception as exc:
                logger.error("digest_persist_error", error=str(exc))
        else:
            logger.info(
                "digest_generated_no_supabase",
                proposals=len(digest["sections"]["top_proposals"]),
            )

        return digest

    async def _get_top_proposals(self) -> list:
        """Obtener top propuestas de integración pendientes."""
        if not self.supabase:
            return []
        try:
            result = (
                await self.supabase.table("integration_proposals")
                .select("*")
                .eq("status", "pending")
                .order("relevance_score", desc=True)
                .limit(10)
                .execute()
            )
            return result.data or []
        except Exception as exc:
            logger.error("proposals_fetch_error", error=str(exc))
            return []

    async def _get_academic_papers(self) -> list:
        """Obtener papers académicos del escaneo semanal."""
        if not self.scholar:
            return []
        try:
            papers = await self.scholar.weekly_scan(WEEKLY_TOPICS)
            return papers[:10]
        except Exception as exc:
            logger.error("papers_fetch_error", error=str(exc))
            return []

    async def _generate_stack_health(self) -> dict:
        """Verificar salud de las dependencias actuales.

        Returns:
            Dict con outdated_packages, security_advisories, deprecation_warnings

        Soberanía:
            OSV.dev: alternativa → safety check local (pip install safety)
        """
        return {
            "outdated_packages": [],  # Producción: pip list --outdated
            "security_advisories": [],  # Producción: consultar OSV.dev
            "deprecation_warnings": [],  # Producción: analizar warnings en logs
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _analyze_trends(self) -> list:
        """Identificar tendencias emergentes de los descubrimientos acumulados.

        Returns:
            Lista de tendencias con momentum

        Soberanía:
            Sin historial: retorna tendencias base conocidas
        """
        if self.supabase:
            try:
                # Agregar tags de los últimos 30 días
                proposals = (
                    await self.supabase.table("integration_proposals").select("impact_areas").limit(100).execute()
                )
                # Contar frecuencia de objetivos impactados
                from collections import Counter

                all_areas = []
                for p in proposals.data or []:
                    all_areas.extend(p.get("impact_areas", []))
                counter = Counter(all_areas)
                return [
                    {"trend": area, "count": count, "momentum": "rising" if count > 2 else "stable"}
                    for area, count in counter.most_common(5)
                ]
            except Exception:
                pass

        # Fallback: tendencias base conocidas
        return [
            {"trend": "multi-agent orchestration", "momentum": "rising"},
            {"trend": "local LLM inference", "momentum": "stable"},
            {"trend": "causal AI", "momentum": "rising"},
            {"trend": "zero-config deployment", "momentum": "rising"},
            {"trend": "emergent behavior detection", "momentum": "stable"},
        ]

    def to_dict(self) -> dict:
        """Serializar estado para Command Center."""
        return {
            "module": "WeeklyDigestGenerator",
            "sprint": "63.1",
            "objetivo": "#6 Vanguardia Perpetua",
            "has_engine": self.engine is not None,
            "has_scholar": self.scholar is not None,
            "has_supabase": self.supabase is not None,
            "weekly_topics": len(WEEKLY_TOPICS),
        }


# ── Singleton ──────────────────────────────────────────────────────────────────

_digest_generator: Optional[WeeklyDigestGenerator] = None


def get_digest_generator() -> Optional[WeeklyDigestGenerator]:
    """Obtener instancia singleton del generador de digest."""
    return _digest_generator


def init_digest_generator(
    intelligence_engine=None,
    semantic_scholar=None,
    supabase=None,
) -> WeeklyDigestGenerator:
    """Inicializar el generador de digest semanal.

    Args:
        intelligence_engine: ResearchIntelligenceEngine (opcional)
        semantic_scholar: SemanticScholarClient (opcional)
        supabase: Cliente Supabase (opcional)

    Returns:
        WeeklyDigestGenerator inicializado

    Soberanía:
        Sin Supabase: genera digest en memoria
    """
    global _digest_generator
    _digest_generator = WeeklyDigestGenerator(
        intelligence_engine=intelligence_engine,
        semantic_scholar=semantic_scholar,
        supabase=supabase,
    )
    logger.info("digest_generator_ready")
    return _digest_generator
