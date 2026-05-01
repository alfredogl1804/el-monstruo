"""kernel/vanguard/semantic_scholar.py

Cliente de Semantic Scholar — Sprint 63.1
Objetivo #6: Vanguardia Perpetua

Búsqueda de papers académicos para inteligencia de investigación profunda.
Complementa el Agents Radar con fuentes académicas de alta calidad.

Soberanía:
    - Semantic Scholar API: alternativa → arXiv API (https://arxiv.org/help/api)
    - httpx: alternativa → requests (sync) o aiohttp (async)
"""

import structlog
from typing import Optional

logger = structlog.get_logger("vanguard.semantic_scholar")

BASE_URL = "https://api.semanticscholar.org/graph/v1"
RELEVANT_FIELDS = "title,abstract,year,citationCount,url,authors,fieldsOfStudy"

# Tópicos relevantes para El Monstruo
DEFAULT_TOPICS = [
    "multi-agent systems autonomous",
    "LLM cost optimization routing",
    "causal inference prediction",
    "AI code generation quality",
    "emergent behavior artificial intelligence",
    "agentic AI systems",
    "retrieval augmented generation",
]


class SemanticScholarClient:
    """Buscar papers académicos para inteligencia de investigación profunda.

    Args:
        (sin argumentos — usa httpx.AsyncClient interno)

    Returns:
        Cliente listo para búsquedas y recomendaciones

    Raises:
        ImportError: Si httpx no está instalado

    Soberanía:
        Semantic Scholar API: alternativa → arXiv API
        httpx: alternativa → requests + asyncio.run_in_executor
    """

    def __init__(self):
        try:
            import httpx
            self._client = httpx.AsyncClient(timeout=30)
            self._httpx_available = True
        except ImportError:
            self._httpx_available = False
            logger.warning("httpx_no_disponible", alternativa="requests sync")

    async def search_papers(
        self,
        query: str,
        year_from: int = 2024,
        min_citations: int = 5,
        limit: int = 20,
    ) -> list:
        """Buscar papers relevantes en Semantic Scholar.

        Args:
            query: Consulta de búsqueda
            year_from: Año mínimo de publicación
            min_citations: Mínimo de citas para filtrar
            limit: Máximo de resultados

        Returns:
            Lista de papers filtrados por citas

        Raises:
            Exception: Si la API falla (retorna lista vacía)

        Soberanía:
            Fallback: arXiv API con parámetros equivalentes
        """
        if not self._httpx_available:
            return await self._arxiv_fallback(query, limit)

        params = {
            "query": query,
            "fields": RELEVANT_FIELDS,
            "limit": limit,
            "year": f"{year_from}-",
        }
        try:
            resp = await self._client.get(f"{BASE_URL}/paper/search", params=params)
            resp.raise_for_status()
            data = resp.json()
            papers = data.get("data", [])
            filtered = [p for p in papers if (p.get("citationCount") or 0) >= min_citations]
            logger.info("papers_found", query=query, total=len(papers), filtered=len(filtered))
            return filtered
        except Exception as exc:
            logger.error("semantic_scholar_error", query=query, error=str(exc))
            return await self._arxiv_fallback(query, limit)

    async def get_recommendations(self, paper_id: str, limit: int = 10) -> list:
        """Obtener recomendaciones basadas en un paper semilla.

        Args:
            paper_id: ID del paper semilla en Semantic Scholar
            limit: Máximo de recomendaciones

        Returns:
            Lista de papers recomendados

        Raises:
            Exception: Si la API falla (retorna lista vacía)

        Soberanía:
            Sin recomendaciones: usar búsqueda por keywords del paper original
        """
        if not self._httpx_available:
            return []
        try:
            resp = await self._client.get(
                f"{BASE_URL}/recommendations",
                params={"paperId": paper_id, "fields": RELEVANT_FIELDS, "limit": limit},
            )
            resp.raise_for_status()
            return resp.json().get("recommendedPapers", [])
        except Exception as exc:
            logger.error("recommendations_error", paper_id=paper_id, error=str(exc))
            return []

    async def weekly_scan(self, topics: list = None) -> list:
        """Escaneo semanal de todos los tópicos relevantes.

        Args:
            topics: Lista de tópicos a escanear (usa DEFAULT_TOPICS si None)

        Returns:
            Lista deduplicada de papers ordenados por citas

        Raises:
            Exception: Si todos los tópicos fallan

        Soberanía:
            Rate limit: cache de 7 días en Supabase tabla weekly_digests
        """
        topics = topics or DEFAULT_TOPICS
        all_papers = []

        for topic in topics:
            papers = await self.search_papers(topic, year_from=2025, min_citations=3)
            all_papers.extend(papers)

        # Deduplicar por paper ID
        seen = set()
        unique = []
        for p in all_papers:
            pid = p.get("paperId")
            if pid and pid not in seen:
                seen.add(pid)
                unique.append(p)

        sorted_papers = sorted(unique, key=lambda x: x.get("citationCount", 0), reverse=True)
        logger.info("weekly_scan_complete", topics=len(topics), unique_papers=len(sorted_papers))
        return sorted_papers

    async def _arxiv_fallback(self, query: str, limit: int = 10) -> list:
        """Fallback a arXiv API cuando Semantic Scholar no está disponible.

        Args:
            query: Consulta de búsqueda
            limit: Máximo de resultados

        Returns:
            Lista de papers de arXiv en formato compatible

        Soberanía:
            arXiv API: completamente gratuita, sin rate limits agresivos
        """
        try:
            import urllib.request
            import urllib.parse
            import xml.etree.ElementTree as ET

            encoded_query = urllib.parse.quote(query)
            url = (
                f"http://export.arxiv.org/api/query?"
                f"search_query=all:{encoded_query}&max_results={limit}&sortBy=submittedDate"
            )
            with urllib.request.urlopen(url, timeout=15) as resp:
                xml_content = resp.read().decode("utf-8")

            root = ET.fromstring(xml_content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)

            papers = []
            for entry in entries:
                title_el = entry.find("atom:title", ns)
                summary_el = entry.find("atom:summary", ns)
                id_el = entry.find("atom:id", ns)
                papers.append({
                    "paperId": id_el.text if id_el is not None else "",
                    "title": title_el.text.strip() if title_el is not None else "",
                    "abstract": summary_el.text.strip() if summary_el is not None else "",
                    "citationCount": 0,
                    "url": id_el.text if id_el is not None else "",
                    "source": "arxiv",
                })

            logger.info("arxiv_fallback_success", query=query, count=len(papers))
            return papers
        except Exception as exc:
            logger.error("arxiv_fallback_error", error=str(exc))
            return []

    def to_dict(self) -> dict:
        """Serializar estado para Command Center."""
        return {
            "module": "SemanticScholarClient",
            "sprint": "63.1",
            "objetivo": "#6 Vanguardia Perpetua",
            "httpx_available": self._httpx_available,
            "default_topics": len(DEFAULT_TOPICS),
            "base_url": BASE_URL,
        }


# ── Singleton ──────────────────────────────────────────────────────────────────

_scholar_client: Optional[SemanticScholarClient] = None


def get_scholar_client() -> Optional[SemanticScholarClient]:
    """Obtener instancia singleton del cliente Semantic Scholar."""
    return _scholar_client


def init_scholar_client() -> SemanticScholarClient:
    """Inicializar cliente Semantic Scholar.

    Returns:
        SemanticScholarClient inicializado

    Soberanía:
        Sin httpx: usa arXiv API como fallback automático
    """
    global _scholar_client
    _scholar_client = SemanticScholarClient()
    logger.info("scholar_client_ready", httpx=_scholar_client._httpx_available)
    return _scholar_client
