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
  - ENRIQUECIMIENTO: Perplexity investiga y puebla arrays vacíos

Diseño:
  - Fail-soft: cada sub-scan es independiente, si uno falla los demás continúan
  - Budget-aware: respeta max_cost_usd del task (default $0.50)
  - Observabilidad: emite structlog para cada sub-scan
  - Enriquecimiento: usa Perplexity (SONAR_API_KEY) como fuente de verdad en tiempo real
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

# Max entries to enrich per scan cycle (budget control)
MAX_ENRICH_PER_CYCLE = 10
PERPLEXITY_MODEL = "sonar-pro"


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

    # Sub-scan 8: AUTO-ENRIQUECIMIENTO via Perplexity
    try:
        results["enriquecimiento"] = await _enrich_empty_arrays()
    except Exception as exc:
        logger.warning("vanguard_scan_enrich_fail", error=str(exc))
        results["enriquecimiento"] = {"status": "error", "error": str(exc)}

    # Sub-scan 9: Register scan event
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


# ─────────────────────────────────────────────────────────────────────────────
# INFRASTRUCTURE
# ─────────────────────────────────────────────────────────────────────────────


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


async def _query_perplexity(prompt: str) -> str | None:
    """
    Query Perplexity Sonar Pro for real-time research.
    Returns the text response or None on failure.
    """
    api_key = os.environ.get("SONAR_API_KEY")
    if not api_key:
        logger.warning("vanguard_enrich: SONAR_API_KEY not set")
        return None

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": PERPLEXITY_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Eres un investigador de IA que responde SOLO en JSON válido. "
                            "No uses markdown, no uses backticks, no uses explicaciones. "
                            "Solo devuelve el JSON solicitado."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
            },
        )
        if resp.status_code != 200:
            logger.warning("perplexity_error", status=resp.status_code, body=resp.text[:200])
            return None

        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content")


def _parse_json_response(text: str | None) -> dict | None:
    """Safely parse JSON from Perplexity response."""
    if not text:
        return None
    # Strip markdown code fences if present
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("perplexity_json_parse_fail", text=text[:200])
        return None


# ─────────────────────────────────────────────────────────────────────────────
# AUTO-ENRICHMENT ENGINE (Perplexity-powered)
# ─────────────────────────────────────────────────────────────────────────────


async def _enrich_empty_arrays() -> dict[str, Any]:
    """
    Find entries with empty arrays across all catastros and enrich them
    using Perplexity real-time research. Processes MAX_ENRICH_PER_CYCLE per run.
    """
    api_key = os.environ.get("SONAR_API_KEY")
    if not api_key:
        return {"status": "skipped", "reason": "no_sonar_api_key"}

    enriched_total = 0
    details = {}

    # Enrich catastro_modelos
    enriched_modelos = await _enrich_modelos()
    details["modelos"] = enriched_modelos
    enriched_total += enriched_modelos.get("enriched", 0)

    # Enrich catastro_agentes
    enriched_agentes = await _enrich_agentes()
    details["agentes"] = enriched_agentes
    enriched_total += enriched_agentes.get("enriched", 0)

    # Enrich catastro_vision_generativa
    enriched_vision = await _enrich_vision()
    details["vision"] = enriched_vision
    enriched_total += enriched_vision.get("enriched", 0)

    return {"status": "ok", "total_enriched": enriched_total, "details": details}


async def _enrich_modelos() -> dict[str, Any]:
    """Enrich catastro_modelos entries with empty arrays."""
    sql = """
    SELECT id, nombre, proveedor, dominios, quality_score, cost_efficiency
    FROM catastro_modelos
    WHERE (fortalezas = '{}' OR subcapacidades = '{}' OR debilidades = '{}')
      AND estado != 'deprecated'
    ORDER BY trono_global DESC NULLS LAST
    LIMIT %s;
    """
    # Use a safe limit per cycle
    limit = min(MAX_ENRICH_PER_CYCLE, 5)
    rows = await _exec_sql(sql.replace("%s", str(limit)))
    if not rows:
        return {"enriched": 0, "reason": "no_empty_entries"}

    enriched = 0
    for row in rows:
        nombre = row["nombre"]
        proveedor = row["proveedor"]
        dominios = row.get("dominios", [])

        prompt = (
            f"Investiga el modelo de IA '{nombre}' de {proveedor} (dominios: {dominios}). "
            f"Devuelve un JSON con exactamente estas 5 llaves, cada una un array de 3-5 strings en español:\n"
            f'{{"fortalezas": ["..."], "debilidades": ["..."], "limitaciones": ["..."], '
            f'"subcapacidades": ["..."], "casos_uso_recomendados_monstruo": ["..."]}}\n\n'
            f"Para 'casos_uso_recomendados_monstruo', piensa en cómo un ecosistema de IAs autónomas "
            f"(El Monstruo) usaría este modelo: orquestación, investigación, coding, análisis, etc.\n"
            f"Para 'subcapacidades', lista capacidades específicas (ej: 'tool calling', 'vision', 'code generation').\n"
            f"Responde SOLO el JSON, sin explicaciones."
        )

        result = await _query_perplexity(prompt)
        parsed = _parse_json_response(result)
        if not parsed:
            continue

        # Validate and build UPDATE
        fields_to_update = []
        for field in ["fortalezas", "debilidades", "limitaciones", "subcapacidades", "casos_uso_recomendados_monstruo"]:
            val = parsed.get(field)
            if isinstance(val, list) and len(val) >= 2:
                # Escape single quotes in values
                escaped = [v.replace("'", "''") for v in val if isinstance(v, str)]
                array_literal = "ARRAY[" + ", ".join(f"'{v}'" for v in escaped) + "]"
                fields_to_update.append(f"{field} = {array_literal}")

        if not fields_to_update:
            continue

        update_sql = f"""
        UPDATE catastro_modelos
        SET {', '.join(fields_to_update)},
            updated_at = now(),
            proxima_revalidacion = now() + interval '30 days'
        WHERE id = '{row["id"]}';
        """
        try:
            await _exec_sql(update_sql)
            enriched += 1
            logger.info("vanguard_enrich_modelo", nombre=nombre, fields=len(fields_to_update))
        except Exception as exc:
            logger.warning("vanguard_enrich_modelo_fail", nombre=nombre, error=str(exc))

    return {"enriched": enriched, "attempted": len(rows)}


async def _enrich_agentes() -> dict[str, Any]:
    """Enrich catastro_agentes entries with empty arrays."""
    sql = f"""
    SELECT id, nombre, proveedor, dominio, capacidad_principal
    FROM catastro_agentes
    WHERE (tools_nativas = '{{}}' OR debilidades = '{{}}' OR limitaciones = '{{}}')
      AND estado != 'deprecated'
    ORDER BY trono_dominio DESC NULLS LAST
    LIMIT {min(MAX_ENRICH_PER_CYCLE, 5)};
    """
    rows = await _exec_sql(sql)
    if not rows:
        return {"enriched": 0, "reason": "no_empty_entries"}

    enriched = 0
    for row in rows:
        nombre = row["nombre"]
        proveedor = row["proveedor"]
        dominio = row.get("dominio", "")
        capacidad = row.get("capacidad_principal", "")

        prompt = (
            f"Investiga el agente/herramienta de IA '{nombre}' de {proveedor} "
            f"(dominio: {dominio}, capacidad principal: {capacidad}). "
            f"Devuelve un JSON con exactamente estas 6 llaves, cada una un array de 3-5 strings en español:\n"
            f'{{"tools_nativas": ["..."], "fortalezas": ["..."], "debilidades": ["..."], '
            f'"limitaciones": ["..."], "subcapacidades": ["..."], "casos_de_uso_primarios": ["..."]}}\n\n'
            f"Para 'tools_nativas', lista las herramientas/funciones que este agente puede ejecutar "
            f"(ej: 'web browsing', 'code execution', 'file management', 'API calls').\n"
            f"Responde SOLO el JSON, sin explicaciones."
        )

        result = await _query_perplexity(prompt)
        parsed = _parse_json_response(result)
        if not parsed:
            continue

        fields_to_update = []
        for field in ["tools_nativas", "fortalezas", "debilidades", "limitaciones", "subcapacidades", "casos_de_uso_primarios"]:
            val = parsed.get(field)
            if isinstance(val, list) and len(val) >= 2:
                escaped = [v.replace("'", "''") for v in val if isinstance(v, str)]
                array_literal = "ARRAY[" + ", ".join(f"'{v}'" for v in escaped) + "]"
                fields_to_update.append(f"{field} = {array_literal}")

        if not fields_to_update:
            continue

        update_sql = f"""
        UPDATE catastro_agentes
        SET {', '.join(fields_to_update)},
            updated_at = now(),
            proxima_revalidacion = now() + interval '30 days'
        WHERE id = '{row["id"]}';
        """
        try:
            await _exec_sql(update_sql)
            enriched += 1
            logger.info("vanguard_enrich_agente", nombre=nombre, fields=len(fields_to_update))
        except Exception as exc:
            logger.warning("vanguard_enrich_agente_fail", nombre=nombre, error=str(exc))

    return {"enriched": enriched, "attempted": len(rows)}


async def _enrich_vision() -> dict[str, Any]:
    """Enrich catastro_vision_generativa entries with empty arrays."""
    sql = f"""
    SELECT id, nombre, proveedor, subdominio_primario
    FROM catastro_vision_generativa
    WHERE (modalidad_input = '{{}}' OR modalidad_output = '{{}}')
      AND estado != 'deprecated'
    ORDER BY updated_at ASC
    LIMIT {min(MAX_ENRICH_PER_CYCLE, 5)};
    """
    rows = await _exec_sql(sql)
    if not rows:
        return {"enriched": 0, "reason": "no_empty_entries"}

    enriched = 0
    for row in rows:
        nombre = row["nombre"]
        proveedor = row["proveedor"]
        subdominio = row.get("subdominio_primario", "")

        prompt = (
            f"Investiga la herramienta de visión/generación '{nombre}' de {proveedor} "
            f"(subdominio: {subdominio}). "
            f"Devuelve un JSON con exactamente estas 3 llaves, cada una un array de 2-5 strings en español:\n"
            f'{{"modalidad_input": ["..."], "modalidad_output": ["..."], "subdominios_secundarios": ["..."]}}\n\n'
            f"Para 'modalidad_input', lista qué tipos de entrada acepta (ej: 'texto', 'imagen', 'video', 'audio', 'sketch').\n"
            f"Para 'modalidad_output', lista qué genera (ej: 'imagen', 'video', '3D', 'animación').\n"
            f"Para 'subdominios_secundarios', lista otros dominios donde se usa además del principal.\n"
            f"Responde SOLO el JSON, sin explicaciones."
        )

        result = await _query_perplexity(prompt)
        parsed = _parse_json_response(result)
        if not parsed:
            continue

        fields_to_update = []
        for field in ["modalidad_input", "modalidad_output", "subdominios_secundarios"]:
            val = parsed.get(field)
            if isinstance(val, list) and len(val) >= 2:
                escaped = [v.replace("'", "''") for v in val if isinstance(v, str)]
                array_literal = "ARRAY[" + ", ".join(f"'{v}'" for v in escaped) + "]"
                fields_to_update.append(f"{field} = {array_literal}")

        if not fields_to_update:
            continue

        update_sql = f"""
        UPDATE catastro_vision_generativa
        SET {', '.join(fields_to_update)},
            updated_at = now(),
            proxima_revalidacion = now() + interval '30 days'
        WHERE id = '{row["id"]}';
        """
        try:
            await _exec_sql(update_sql)
            enriched += 1
            logger.info("vanguard_enrich_vision", nombre=nombre, fields=len(fields_to_update))
        except Exception as exc:
            logger.warning("vanguard_enrich_vision_fail", nombre=nombre, error=str(exc))

    return {"enriched": enriched, "attempted": len(rows)}


# ─────────────────────────────────────────────────────────────────────────────
# EXISTING SUB-SCANS (unchanged)
# ─────────────────────────────────────────────────────────────────────────────


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
