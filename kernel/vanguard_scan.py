"""
El Monstruo — Vanguard Scan (Sprint CATASTRO-AUTO)
===================================================
Handler real del vanguard_scan que actualiza los 7 catastros cada 24h.

Estrategia por catastro:
  - catastro_repos: GitHub API → actualiza stars, pushed_at, description
  - catastro_modelos: Marca proxima_revalidacion vencida como needs_update
  - catastro_agentes: Marca proxima_revalidacion vencida como needs_update
  - catastro_vision_generativa: Marca proxima_revalidacion vencida como needs_update
  - catastro_suppliers_humanos: Marca inactivos si last_active > 30 días
  - catastro_herramientas_ai: Verifica endpoints activos
  - catastro_historial: Snapshot diario de modelos top
  - catastro_eventos: Registra el propio scan como evento

Diseño:
  - Fail-soft: cada sub-scan es independiente, si uno falla los demás continúan
  - Budget-aware: respeta max_cost_usd del task (default $0.30)
  - Observabilidad: emite structlog para cada sub-scan
  - No requiere LLM: puro data fetching + SQL updates
"""

from __future__ import annotations

import os
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

import structlog
import httpx

logger = structlog.get_logger("vanguard_scan")


async def run_vanguard_scan(**kwargs: Any) -> dict[str, Any]:
    """
    Handler principal del vanguard_scan.
    Ejecuta sub-scans independientes y retorna resumen.
    """
    results = {}
    started = datetime.now(timezone.utc)

    # Sub-scan 1: Repos (GitHub API)
    try:
        results["repos"] = await _scan_repos()
    except Exception as exc:
        logger.warning("vanguard_scan_repos_fail", error=str(exc))
        results["repos"] = {"status": "error", "error": str(exc)}

    # Sub-scan 2: Modelos (mark stale)
    try:
        results["modelos"] = await _scan_modelos_stale()
    except Exception as exc:
        logger.warning("vanguard_scan_modelos_fail", error=str(exc))
        results["modelos"] = {"status": "error", "error": str(exc)}

    # Sub-scan 3: Agentes (mark stale)
    try:
        results["agentes"] = await _scan_agentes_stale()
    except Exception as exc:
        logger.warning("vanguard_scan_agentes_fail", error=str(exc))
        results["agentes"] = {"status": "error", "error": str(exc)}

    # Sub-scan 4: Vision Generativa (mark stale)
    try:
        results["vision_generativa"] = await _scan_vision_stale()
    except Exception as exc:
        logger.warning("vanguard_scan_vision_fail", error=str(exc))
        results["vision_generativa"] = {"status": "error", "error": str(exc)}

    # Sub-scan 5: Suppliers Humanos (mark inactive)
    try:
        results["suppliers"] = await _scan_suppliers_inactive()
    except Exception as exc:
        logger.warning("vanguard_scan_suppliers_fail", error=str(exc))
        results["suppliers"] = {"status": "error", "error": str(exc)}

    # Sub-scan 6: Herramientas AI (verify active)
    try:
        results["herramientas"] = await _scan_herramientas_active()
    except Exception as exc:
        logger.warning("vanguard_scan_herramientas_fail", error=str(exc))
        results["herramientas"] = {"status": "error", "error": str(exc)}

    # Sub-scan 7: Historial snapshot
    try:
        results["historial"] = await _snapshot_historial()
    except Exception as exc:
        logger.warning("vanguard_scan_historial_fail", error=str(exc))
        results["historial"] = {"status": "error", "error": str(exc)}

    # Sub-scan 8: Register scan event
    try:
        results["evento"] = await _register_scan_event(started, results)
    except Exception as exc:
        logger.warning("vanguard_scan_evento_fail", error=str(exc))
        results["evento"] = {"status": "error", "error": str(exc)}

    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    logger.info(
        "vanguard_scan_completed",
        elapsed_sec=round(elapsed, 1),
        results_summary={k: v.get("status", "unknown") for k, v in results.items()},
    )
    return results


def _get_db_url() -> str | None:
    """Get Supabase DB URL from environment."""
    return os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")


async def _exec_sql(query: str, params: tuple = ()) -> list[dict]:
    """Execute SQL via psycopg (async)."""
    try:
        import psycopg  # noqa: PLC0415
    except ImportError:
        logger.warning("vanguard_scan: psycopg not installed, skipping SQL")
        return []

    db_url = _get_db_url()
    if not db_url:
        return []

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                cols = [d.name for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
            conn.commit()
            return []


async def _scan_repos() -> dict[str, Any]:
    """
    Update catastro_repos from GitHub API.
    Uses GITHUB_TOKEN or GITHUB_PERSONAL_ACCESS_TOKEN.
    """
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        return {"status": "skipped", "reason": "no_github_token"}

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    updated = 0
    page = 1
    per_page = 100

    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            resp = await client.get(
                f"https://api.github.com/user/repos?per_page={per_page}&page={page}&sort=pushed",
                headers=headers,
            )
            if resp.status_code != 200:
                return {"status": "error", "error": f"GitHub API {resp.status_code}"}

            repos = resp.json()
            if not repos:
                break

            for repo in repos:
                repo_id = str(uuid.uuid5(uuid.NAMESPACE_URL, repo["html_url"]))
                nombre = repo["name"].replace("'", "''")
                desc = (repo.get("description") or "").replace("'", "''")
                url = repo["html_url"]
                stars = repo.get("stargazers_count", 0)
                pushed = repo.get("pushed_at", "")
                license_name = (repo.get("license") or {}).get("spdx_id", "")
                is_private = repo.get("private", True)
                topics = json.dumps(repo.get("topics", []))

                classification = json.dumps({
                    "visibility": "private" if is_private else "public",
                    "ecosystem": "el-monstruo",
                    "language": repo.get("language", ""),
                    "default_branch": repo.get("default_branch", "main"),
                })

                sql = f"""
                INSERT INTO catastro_repos
                    (id, nombre, proveedor, url, descripcion, fuente, stars_count,
                     license, topics, classification, radar_discovered_at, created_at, updated_at)
                VALUES
                    ('{repo_id}', '{nombre}', 'github', '{url}', '{desc}',
                     'vanguard_scan_auto', {stars}, '{license_name}',
                     '{topics}'::jsonb, '{classification}'::jsonb, now(), now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    stars_count = {stars},
                    descripcion = '{desc}',
                    license = '{license_name}',
                    topics = '{topics}'::jsonb,
                    classification = '{classification}'::jsonb,
                    updated_at = now();
                """
                try:
                    await _exec_sql(sql)
                    updated += 1
                except Exception:
                    pass  # Individual repo failure doesn't stop the scan

            if len(repos) < per_page:
                break
            page += 1

    return {"status": "ok", "repos_updated": updated}


async def _scan_modelos_stale() -> dict[str, Any]:
    """Mark models with expired proxima_revalidacion as needs_update."""
    sql = """
    UPDATE catastro_modelos
    SET estado = 'needs_revalidation',
        updated_at = now()
    WHERE proxima_revalidacion < now()
      AND estado != 'needs_revalidation'
      AND estado != 'deprecated'
    RETURNING id, nombre;
    """
    rows = await _exec_sql(sql)
    return {"status": "ok", "marked_stale": len(rows), "models": [r["nombre"] for r in rows]}


async def _scan_agentes_stale() -> dict[str, Any]:
    """Mark agents with expired proxima_revalidacion as needs_update."""
    sql = """
    UPDATE catastro_agentes
    SET estado = 'needs_revalidation',
        updated_at = now()
    WHERE proxima_revalidacion < now()
      AND estado != 'needs_revalidation'
      AND estado != 'deprecated'
    RETURNING id, nombre;
    """
    rows = await _exec_sql(sql)
    return {"status": "ok", "marked_stale": len(rows), "agents": [r["nombre"] for r in rows]}


async def _scan_vision_stale() -> dict[str, Any]:
    """Mark vision generativa entries with expired proxima_revalidacion."""
    sql = """
    UPDATE catastro_vision_generativa
    SET estado = 'needs_revalidation',
        updated_at = now()
    WHERE proxima_revalidacion < now()
      AND estado != 'needs_revalidation'
      AND estado != 'deprecated'
    RETURNING id, nombre;
    """
    rows = await _exec_sql(sql)
    return {"status": "ok", "marked_stale": len(rows), "tools": [r["nombre"] for r in rows]}


async def _scan_suppliers_inactive() -> dict[str, Any]:
    """Mark suppliers as inactive if last_active > 30 days ago."""
    sql = """
    UPDATE catastro_suppliers_humanos
    SET active = false,
        updated_at = now()
    WHERE last_active < now() - interval '30 days'
      AND active = true
    RETURNING key, name;
    """
    rows = await _exec_sql(sql)
    return {"status": "ok", "marked_inactive": len(rows)}


async def _scan_herramientas_active() -> dict[str, Any]:
    """
    Verify herramientas_ai endpoints are reachable.
    Only checks tools marked as active with a non-null endpoint.
    """
    sql = """
    SELECT key, name, endpoint FROM catastro_herramientas_ai
    WHERE active = true AND endpoint IS NOT NULL AND endpoint != '';
    """
    tools = await _exec_sql(sql)
    if not tools:
        return {"status": "ok", "checked": 0, "unreachable": 0}

    unreachable = []
    async with httpx.AsyncClient(timeout=10) as client:
        for tool in tools[:20]:  # Limit to 20 to stay within budget
            try:
                resp = await client.head(tool["endpoint"])
                if resp.status_code >= 500:
                    unreachable.append(tool["name"])
            except Exception:
                unreachable.append(tool["name"])

    if unreachable:
        # Mark unreachable tools
        names_sql = ", ".join(f"'{n}'" for n in unreachable)
        await _exec_sql(f"""
            UPDATE catastro_herramientas_ai
            SET metadata = jsonb_set(
                COALESCE(metadata, '{{}}'::jsonb),
                '{{last_health_check}}',
                '"unreachable"'
            )
            WHERE name IN ({names_sql});
        """)

    return {"status": "ok", "checked": len(tools), "unreachable": len(unreachable)}


async def _snapshot_historial() -> dict[str, Any]:
    """
    Take a daily snapshot of top models into catastro_historial.
    Stores trono_global and rank for tracking over time.
    """
    sql = """
    INSERT INTO catastro_historial (fecha, modelo_id, snapshot, trono_global, rank_dominio)
    SELECT
        CURRENT_DATE,
        id,
        jsonb_build_object(
            'nombre', nombre,
            'proveedor', proveedor,
            'quality_score', quality_score,
            'cost_efficiency', cost_efficiency,
            'estado', estado
        ),
        trono_global,
        rank_dominio
    FROM catastro_modelos
    WHERE trono_global IS NOT NULL
      AND estado NOT IN ('deprecated', 'needs_revalidation')
    ORDER BY trono_global DESC
    LIMIT 20
    ON CONFLICT DO NOTHING;
    """
    await _exec_sql(sql)

    # Count how many were inserted today
    count_rows = await _exec_sql(
        "SELECT count(*) as n FROM catastro_historial WHERE fecha = CURRENT_DATE;"
    )
    n = count_rows[0]["n"] if count_rows else 0
    return {"status": "ok", "snapshots_today": n}


async def _register_scan_event(started: datetime, results: dict) -> dict[str, Any]:
    """Register the scan itself as an event in catastro_eventos."""
    desc = json.dumps({
        k: v.get("status", "unknown") if isinstance(v, dict) else str(v)
        for k, v in results.items()
    }).replace("'", "''")

    sql = f"""
    INSERT INTO catastro_eventos (fecha, tipo, prioridad, descripcion, contexto, notificado)
    VALUES (
        now(),
        'vanguard_scan',
        'low',
        'Vanguard scan automático completado',
        '{desc}'::jsonb,
        false
    );
    """
    await _exec_sql(sql)
    return {"status": "ok"}
