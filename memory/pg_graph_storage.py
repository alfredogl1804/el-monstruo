"""
PGNetworkXStorage — NetworkX graph con persistencia en PostgreSQL.

Sprint 31 | El Monstruo

Problema: LightRAG usa NetworkXStorage que guarda el graph como .graphml
en el filesystem. En Railway el filesystem es efímero — el graph se pierde
en cada deploy, causando que los queries devuelvan "no-context".

Solución: Subclase de NetworkXStorage que sobreescribe load/write para
usar PostgreSQL (Supabase) como backend en vez del filesystem.

Estrategia:
  - El graph se serializa como GraphML (texto XML) y se guarda en una
    tabla PostgreSQL como TEXT
  - Al startup, se carga desde PG → NetworkX en memoria (rápido)
  - En index_done_callback, se guarda de memoria → PG (persistente)
  - También se guarda en filesystem como fallback (para multiprocess sync)
  - Cero dependencias nuevas: usa asyncpg que ya está instalado por PGKVStorage

Basado en recomendación de Claude Opus 4.7 (serializar graph a PG).
Adaptado a la interfaz real de LightRAG v1.4.15 NetworkXStorage.
"""

from __future__ import annotations

import io
import logging
import os
from typing import Any

import networkx as nx

logger = logging.getLogger("monstruo.memory.pg_graph")

# ── Tabla en PostgreSQL ──────────────────────────────────────────────
TABLE_NAME = "monstruo_graph_snapshots"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id TEXT PRIMARY KEY,
    graphml_data TEXT NOT NULL,
    nodes_count INTEGER DEFAULT 0,
    edges_count INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
"""


def _get_db_url() -> str | None:
    """Obtener la URL de conexión a PostgreSQL."""
    url = os.getenv("SUPABASE_DB_URL", "")
    if url:
        return url
    # Construir desde POSTGRES_* env vars (que lightrag_bridge inyecta)
    host = os.getenv("POSTGRES_HOST")
    if not host:
        return None
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    database = os.getenv("POSTGRES_DATABASE", "postgres")
    ssl_mode = os.getenv("POSTGRES_SSL_MODE", "require")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode={ssl_mode}"


async def _ensure_table(db_url: str) -> bool:
    """Crear la tabla si no existe."""
    try:
        import ssl as _ssl

        import asyncpg

        ssl_ctx = _ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = _ssl.CERT_NONE

        conn = await asyncpg.connect(db_url, ssl=ssl_ctx)
        try:
            await conn.execute(CREATE_TABLE_SQL)
            logger.info("pg_graph_table_ready", extra={"table": TABLE_NAME})
            return True
        finally:
            await conn.close()
    except Exception as exc:
        logger.error("pg_graph_table_create_failed", extra={"error": str(exc)})
        return False


async def save_graph_to_pg(
    graph: nx.Graph,
    graph_id: str = "main",
    db_url: str | None = None,
) -> bool:
    """Serializar y guardar un NetworkX graph en PostgreSQL."""
    db_url = db_url or _get_db_url()
    if not db_url:
        logger.warning("pg_graph_save_skipped: no DB URL")
        return False

    try:
        import ssl as _ssl

        import asyncpg

        # Serializar a GraphML (texto XML)
        buf = io.BytesIO()
        nx.write_graphml(graph, buf)
        graphml_text = buf.getvalue().decode("utf-8")

        ssl_ctx = _ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = _ssl.CERT_NONE

        conn = await asyncpg.connect(db_url, ssl=ssl_ctx)
        try:
            await _ensure_table(db_url)
            await conn.execute(
                f"""
                INSERT INTO {TABLE_NAME} (id, graphml_data, nodes_count, edges_count, updated_at)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    graphml_data = EXCLUDED.graphml_data,
                    nodes_count = EXCLUDED.nodes_count,
                    edges_count = EXCLUDED.edges_count,
                    updated_at = NOW()
                """,
                graph_id,
                graphml_text,
                graph.number_of_nodes(),
                graph.number_of_edges(),
            )
            logger.info(
                "pg_graph_saved",
                extra={
                    "graph_id": graph_id,
                    "nodes": graph.number_of_nodes(),
                    "edges": graph.number_of_edges(),
                    "graphml_size_kb": len(graphml_text) // 1024,
                },
            )
            return True
        finally:
            await conn.close()

    except Exception as exc:
        logger.error("pg_graph_save_failed", extra={"error": str(exc)})
        return False


async def load_graph_from_pg(
    graph_id: str = "main",
    db_url: str | None = None,
) -> nx.Graph | None:
    """Cargar un NetworkX graph desde PostgreSQL."""
    db_url = db_url or _get_db_url()
    if not db_url:
        logger.warning("pg_graph_load_skipped: no DB URL")
        return None

    try:
        import ssl as _ssl

        import asyncpg

        ssl_ctx = _ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = _ssl.CERT_NONE

        conn = await asyncpg.connect(db_url, ssl=ssl_ctx)
        try:
            await _ensure_table(db_url)
            row = await conn.fetchrow(
                f"SELECT graphml_data, nodes_count, edges_count FROM {TABLE_NAME} WHERE id = $1",
                graph_id,
            )
            if not row:
                logger.info("pg_graph_not_found", extra={"graph_id": graph_id})
                return None

            graphml_text = row["graphml_data"]
            buf = io.BytesIO(graphml_text.encode("utf-8"))
            graph = nx.read_graphml(buf)

            logger.info(
                "pg_graph_loaded",
                extra={
                    "graph_id": graph_id,
                    "nodes": graph.number_of_nodes(),
                    "edges": graph.number_of_edges(),
                    "stored_nodes": row["nodes_count"],
                    "stored_edges": row["edges_count"],
                },
            )
            return graph
        finally:
            await conn.close()

    except Exception as exc:
        logger.error("pg_graph_load_failed", extra={"error": str(exc)})
        return None


async def get_graph_stats(
    graph_id: str = "main",
    db_url: str | None = None,
) -> dict[str, Any]:
    """Obtener estadísticas del graph almacenado."""
    db_url = db_url or _get_db_url()
    if not db_url:
        return {"status": "unavailable", "reason": "no_db_url"}

    try:
        import ssl as _ssl

        import asyncpg

        ssl_ctx = _ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = _ssl.CERT_NONE

        conn = await asyncpg.connect(db_url, ssl=ssl_ctx)
        try:
            row = await conn.fetchrow(
                f"SELECT nodes_count, edges_count, updated_at, length(graphml_data) as size_bytes FROM {TABLE_NAME} WHERE id = $1",
                graph_id,
            )
            if not row:
                return {"status": "empty", "graph_id": graph_id}
            return {
                "status": "active",
                "graph_id": graph_id,
                "nodes": row["nodes_count"],
                "edges": row["edges_count"],
                "size_kb": row["size_bytes"] // 1024,
                "updated_at": str(row["updated_at"]),
                "storage": "postgresql",
            }
        finally:
            await conn.close()
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
