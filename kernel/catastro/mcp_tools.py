"""
El Catastro · FastMCP Sub-Server (Sprint 86 Bloque 5).

Expone las 4 herramientas del Catastro vía Model Context Protocol (MCP)
para que cualquier cliente compatible (Claude Desktop, Cowork, Embriones)
pueda invocarlas como tools nativas.

Patrón canónico FastMCP 3.x (validado en tiempo real 2026):
  · Este archivo construye un FastMCP standalone llamado `catastro_mcp`.
  · `kernel/fastmcp_server.py` (existente) lo importa y lo monta vía
    `main_mcp.mount("catastro", catastro_mcp)` — los tools quedan
    accesibles como `catastro_recommend`, `catastro_get_modelo`, etc.
  · Si FastMCP no está instalado, el archivo expone `catastro_mcp = None`
    y el mount es no-op (graceful degradation).

Auth:
  · MCP transport usa el token del cliente; la validación dura del
    MONSTRUO_API_KEY se hace en los endpoints REST de catastro_routes.py.
  · El sub-server MCP es de SOLO LECTURA — no muta nada en Supabase.

Doctrina anti-Dory:
  · El engine se obtiene vía `get_engine()` que lee `_engine_singleton`
    inyectado al startup desde el lifespan del kernel.
  · `os.environ` no se usa aquí (delegado al engine).

[Hilo Manus Catastro] · Sprint 86 Bloque 5 · 2026-05-04 · v0.86.5
"""
from __future__ import annotations

from typing import Any, Optional

import structlog

from kernel.catastro.recommendation import (
    DEFAULT_TOP_N,
    MAX_TOP_N,
    CatastroRecommendInvalidArgs,
    RecommendationEngine,
)

logger = structlog.get_logger("kernel.catastro.mcp")

# Engine singleton compartido entre tools MCP
_engine_singleton: Optional[RecommendationEngine] = None


def set_mcp_engine(engine: RecommendationEngine) -> None:
    """Inyecta el engine. Llamar una sola vez en lifespan."""
    global _engine_singleton
    _engine_singleton = engine


def _get_engine() -> Optional[RecommendationEngine]:
    return _engine_singleton


def build_catastro_mcp() -> Any:
    """
    Construye el FastMCP sub-server `catastro_mcp` con 4 tools.

    Returns:
        FastMCP instance, o None si fastmcp no está instalado.
    """
    try:
        from fastmcp import FastMCP
    except ImportError:
        logger.warning(
            "catastro_mcp_fastmcp_not_installed",
            hint="pip install fastmcp==3.2.4",
        )
        return None

    mcp = FastMCP(
        name="Catastro",
        instructions=(
            "El Catastro es la fuente de verdad de El Monstruo sobre modelos "
            "de IA, sus métricas (Trono Score con z-scores intra-dominio), "
            "macroáreas y dominios. Usa estas herramientas para recomendar "
            "modelos, consultar fichas detalladas, listar dominios o auditar "
            "el estado del Catastro."
        ),
    )

    @mcp.tool(
        name="recommend",
        description=(
            "Top N modelos del Catastro recomendados para un caso de uso. "
            "Filtros opcionales por dominio o macroárea. Ordenados por "
            "Trono Score descendente con bandas de confianza."
        ),
    )
    async def catastro_recommend(
        use_case: str,
        dominio: Optional[str] = None,
        macroarea: Optional[str] = None,
        top_n: int = DEFAULT_TOP_N,
    ) -> dict[str, Any]:
        engine = _get_engine()
        if engine is None:
            return {
                "degraded": True,
                "degraded_reason": "engine_not_initialized",
                "modelos": [],
            }
        try:
            top_n_clamped = max(1, min(int(top_n), MAX_TOP_N))
            resp = engine.recommend(
                use_case=use_case,
                dominio=dominio,
                macroarea=macroarea,
                top_n=top_n_clamped,
            )
        except CatastroRecommendInvalidArgs as exc:
            return {
                "degraded": True,
                "degraded_reason": exc.code,
                "modelos": [],
            }
        return resp.model_dump(mode="json")

    @mcp.tool(
        name="get_modelo",
        description=(
            "Ficha detallada de un modelo del Catastro por id canónico. "
            "Incluye subcapacidades, sovereignty, velocity, estado, precios."
        ),
    )
    async def catastro_get_modelo(modelo_id: str) -> dict[str, Any]:
        engine = _get_engine()
        if engine is None:
            return {"error": "catastro_recommend_engine_not_initialized"}
        try:
            modelo = engine.get_modelo(modelo_id)
        except CatastroRecommendInvalidArgs as exc:
            return {"error": exc.code}
        if modelo is None:
            return {"error": "catastro_recommend_modelo_not_found", "modelo_id": modelo_id}
        return modelo.model_dump(mode="json")

    @mcp.tool(
        name="list_dominios",
        description=(
            "Lista todas las macroáreas y dominios del Catastro con el conteo "
            "de modelos en cada uno. Útil para descubrir qué cubre el Catastro."
        ),
    )
    async def catastro_list_dominios() -> dict[str, Any]:
        engine = _get_engine()
        if engine is None:
            return {
                "degraded": True,
                "degraded_reason": "engine_not_initialized",
                "macroareas": {},
                "total_dominios": 0,
            }
        return engine.list_dominios().model_dump(mode="json")

    @mcp.tool(
        name="status",
        description=(
            "Snapshot de salud del Catastro: trust_level, last_update, "
            "conteos de modelos/dominios/macroáreas, entradas en cache, "
            "flag de modo degraded."
        ),
    )
    async def catastro_status() -> dict[str, Any]:
        engine = _get_engine()
        if engine is None:
            return {
                "trust_level": "down",
                "degraded": True,
                "degraded_reason": "engine_not_initialized",
                "modelos_count": 0,
                "dominios_count": 0,
            }
        return engine.status().model_dump(mode="json")

    logger.info("catastro_mcp_built", tools=4, version="0.86.5")
    return mcp


# Singleton público para que kernel/fastmcp_server.py lo monte
catastro_mcp = build_catastro_mcp()
