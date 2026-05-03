"""
El Monstruo — Deploy to Railway (Sprint 84, Bloque 2)
======================================================
Tool para que El Monstruo publique apps backend (FastAPI/Flask/Django/Node/Express)
end-to-end vía Railway Public API GraphQL v2.

Soberanía: usa RAILWAY_API_TOKEN ya activa, sin nuevas dependencias.
Diseño: Cowork (Hilo B). Mutations GraphQL validadas en Paso 0:
        - Endpoint: https://backboard.railway.com/graphql/v2  (Erratum 1)
        - Pricing:  Hobby $5/mes flat + $5 trial credit one-time (Erratum 1)
        - Auth:     header Authorization: Bearer <token>

Estrategia: dado que el deploy óptimo en Railway pasa por GitHub repo,
esta tool asume que el código YA fue pusheado vía deploy_to_github_pages
(o equivalente) y crea project + service desde repo + dispara deploy.

Brand:
- Errores: RailwayDeployFalla, RailwayBuildTimeout, RailwayMissingToken
- Logs:    deploy_railway_started, deploy_railway_completed,
           deploy_railway_build_timeout
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Optional

import aiohttp
import structlog

logger = structlog.get_logger("tools.deploy_to_railway")

RAILWAY_API_URL = "https://backboard.railway.com/graphql/v2"
RAILWAY_TOKEN = os.environ.get("RAILWAY_API_TOKEN", "").strip()
RAILWAY_POLL_INTERVAL_S = 8
RAILWAY_POLL_MAX_S = 600  # 10 minutos para builds backend

# ── Errores con identidad ────────────────────────────────────────────────────


class RailwayDeployFalla(Exception):
    """Falla irrecuperable en deploy a Railway."""


class RailwayBuildTimeout(Exception):
    """El build de Railway no confirmó status='SUCCESS' en el tiempo límite."""


class RailwayMissingToken(Exception):
    """RAILWAY_API_TOKEN no está en el entorno."""


# ── GraphQL helper ───────────────────────────────────────────────────────────


async def _graphql(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    """Ejecuta una operación GraphQL contra la API pública de Railway."""
    if not RAILWAY_TOKEN:
        raise RailwayMissingToken(
            "deploy_railway_missing_token: RAILWAY_API_TOKEN no está configurada en el entorno. "
            "Sugerencia: obtener token en https://railway.com/account/tokens y exportarlo."
        )
    headers = {
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": query, "variables": variables or {}}
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(RAILWAY_API_URL, headers=headers, json=payload) as resp:
            text = await resp.text()
            if resp.status >= 400:
                raise RailwayDeployFalla(
                    f"deploy_railway_http_{resp.status}: {text[:500]}"
                )
            try:
                data = await resp.json(content_type=None)
            except Exception as e:
                raise RailwayDeployFalla(
                    f"deploy_railway_json_decode: {e} | body={text[:200]}"
                ) from e
            if "errors" in data and data["errors"]:
                raise RailwayDeployFalla(
                    f"deploy_railway_graphql_errors: {data['errors']}"
                )
            return data.get("data", {})


# ── Mutations / Queries ─────────────────────────────────────────────────────

_M_PROJECT_CREATE = """
mutation projectCreate($input: ProjectCreateInput!) {
  projectCreate(input: $input) { id name }
}
"""

_Q_ME_WORKSPACES = """
query me {
  me {
    workspaces {
      id
      name
    }
  }
}
"""

# Cache en memoria del workspace_id resuelto (vive con el proceso del kernel)
_WORKSPACE_ID_CACHE: dict[str, str] = {}


async def _resolve_workspace_id() -> str:
    """Resuelve workspace_id en este orden:
    (1) cache en memoria, (2) env var RAILWAY_WORKSPACE_ID,
    (3) query me { workspaces } y toma el primero.

    Sprint 84.5 Bug 5 fix: workspaceId obligatorio en ProjectCreateInput
    desde mayo 2026 (Railway deprecated teamId).
    """
    # 1. Cache
    cached = _WORKSPACE_ID_CACHE.get("id")
    if cached:
        return cached

    # 2. Env var explícita
    env_ws = os.environ.get("RAILWAY_WORKSPACE_ID", "").strip()
    if env_ws:
        _WORKSPACE_ID_CACHE["id"] = env_ws
        logger.info("deploy_railway_workspace_resolved", source="env_var", workspace_id=env_ws[:8] + "...")
        return env_ws

    # 3. Query dinámica (Railway expone workspaces como lista directa, no edges/node)
    data = await _graphql(_Q_ME_WORKSPACES)
    workspaces = (data.get("me") or {}).get("workspaces", []) or []
    if not workspaces:
        raise RailwayDeployFalla(
            "deploy_railway_no_workspaces: la cuenta no tiene workspaces. "
            "Crea uno en https://railway.com/dashboard."
        )
    first = workspaces[0] or {}
    ws_id = first.get("id")
    ws_name = first.get("name", "unknown")
    if not ws_id:
        raise RailwayDeployFalla(
            f"deploy_railway_workspace_sin_id: workspaces={workspaces[:2]}"
        )
    _WORKSPACE_ID_CACHE["id"] = ws_id
    logger.info(
        "deploy_railway_workspace_resolved",
        source="graphql_query",
        workspace_id=ws_id[:8] + "...",
        workspace_name=ws_name,
    )
    return ws_id

_Q_PROJECT_DETAIL = """
query project($id: String!) {
  project(id: $id) {
    id
    name
    services { edges { node { id name } } }
    environments { edges { node { id name } } }
  }
}
"""

_M_SERVICE_CREATE_FROM_REPO = """
mutation serviceCreate($input: ServiceCreateInput!) {
  serviceCreate(input: $input) { id name }
}
"""

_M_VARIABLES_UPSERT = """
mutation variableCollectionUpsert($input: VariableCollectionUpsertInput!) {
  variableCollectionUpsert(input: $input)
}
"""

_M_SERVICE_DEPLOY = """
mutation serviceInstanceDeploy($serviceId: String!, $environmentId: String!) {
  serviceInstanceDeploy(serviceId: $serviceId, environmentId: $environmentId)
}
"""

_Q_DEPLOYMENTS = """
query deployments($input: DeploymentListInput!) {
  deployments(input: $input, first: 5) {
    edges { node { id status createdAt } }
  }
}
"""

_M_DOMAIN_CREATE = """
mutation serviceDomainCreate($input: ServiceDomainCreateInput!) {
  serviceDomainCreate(input: $input) { domain }
}
"""


# ── Implementación ───────────────────────────────────────────────────────────


async def deploy_to_railway(
    repo: str,  # "owner/repo" — debe existir en GitHub
    project_name: str,
    service_name: str = "API",
    env_vars: Optional[dict[str, str]] = None,
    create_domain: bool = True,
) -> dict[str, Any]:
    """
    Crea un proyecto en Railway, conecta el repo de GitHub, setea env vars
    y dispara el primer deploy. Devuelve URL pública (si create_domain=True).

    Args:
        repo: "owner/repo" en GitHub (ej. "alfredogl1804/leoncio-api"). El repo DEBE existir.
        project_name: nombre del proyecto en Railway.
        service_name: nombre del service. Default "API".
        env_vars: variables de entorno a inyectar antes del primer deploy.
        create_domain: si True, crea Railway domain público y lo retorna.

    Returns:
        {
          "project_id": str,
          "service_id": str,
          "environment_id": str,
          "deployment_id": str | None,
          "deployment_status": str,
          "url": str | None,
          "build_confirmed": bool,
        }
    """
    if not RAILWAY_TOKEN:
        raise RailwayMissingToken(
            "deploy_railway_missing_token: RAILWAY_API_TOKEN no está configurada."
        )
    if "/" not in repo:
        raise RailwayDeployFalla(
            f"deploy_railway_repo_invalido: '{repo}' no es 'owner/repo'."
        )

    logger.info(
        "deploy_railway_started",
        repo=repo,
        project_name=project_name,
        service_name=service_name,
        env_vars_count=len(env_vars or {}),
    )

    # 1. Resolver workspace_id (Sprint 84.5 Bug 5)
    workspace_id = await _resolve_workspace_id()

    # 2. Crear proyecto con workspaceId obligatorio + defaultEnvironmentName='production'
    project_input = {
        "name": project_name,
        "workspaceId": workspace_id,
        "defaultEnvironmentName": "production",
    }
    try:
        proj_data = await _graphql(_M_PROJECT_CREATE, {"input": project_input})
    except RailwayDeployFalla as exc:
        # Fallback: añadir description si Railway lo exige (mensaje en spec Cowork)
        if "description" in str(exc).lower():
            project_input["description"] = (project_name + " (Sprint 84)")[:100]
            logger.warning("deploy_railway_project_create_retry", reason="description_required")
            proj_data = await _graphql(_M_PROJECT_CREATE, {"input": project_input})
        else:
            raise
    project_id = proj_data.get("projectCreate", {}).get("id")
    if not project_id:
        raise RailwayDeployFalla(
            f"deploy_railway_project_create_fallido: {proj_data}"
        )

    # 2. Obtener environment_id (el 'production' default se crea con el proyecto)
    detail = await _graphql(_Q_PROJECT_DETAIL, {"id": project_id})
    project_node = detail.get("project") or {}
    env_edges = project_node.get("environments", {}).get("edges", [])
    if not env_edges:
        raise RailwayDeployFalla(
            f"deploy_railway_no_environments: proyecto {project_id} sin environments tras creación."
        )
    # Preferir 'production', si no, el primero
    environment_id = None
    for edge in env_edges:
        node = edge.get("node", {})
        if node.get("name") == "production":
            environment_id = node.get("id")
            break
    if not environment_id:
        environment_id = env_edges[0]["node"]["id"]

    # 3. Crear service desde repo de GitHub
    svc_data = await _graphql(
        _M_SERVICE_CREATE_FROM_REPO,
        {
            "input": {
                "projectId": project_id,
                "name": service_name,
                "source": {"repo": repo},
            }
        },
    )
    service_id = svc_data.get("serviceCreate", {}).get("id")
    if not service_id:
        raise RailwayDeployFalla(
            f"deploy_railway_service_create_fallido: {svc_data}"
        )

    # 4. Inyectar env vars (antes del primer deploy)
    if env_vars:
        await _graphql(
            _M_VARIABLES_UPSERT,
            {
                "input": {
                    "projectId": project_id,
                    "environmentId": environment_id,
                    "serviceId": service_id,
                    "variables": env_vars,
                }
            },
        )
        logger.info(
            "deploy_railway_variables_set",
            service_id=service_id,
            count=len(env_vars),
        )

    # 5. Disparar deploy explícito (Railway puede dispararlo solo al crear desde repo,
    #    pero forzamos para garantizar trigger)
    try:
        await _graphql(
            _M_SERVICE_DEPLOY,
            {"serviceId": service_id, "environmentId": environment_id},
        )
    except RailwayDeployFalla as e:
        # Si falla porque ya se disparó solo, lo registramos pero seguimos a polling
        logger.warning("deploy_railway_explicit_trigger_warning", error=str(e))

    # 6. Crear dominio público (opcional)
    public_url: Optional[str] = None
    if create_domain:
        try:
            dom_data = await _graphql(
                _M_DOMAIN_CREATE,
                {"input": {"serviceId": service_id, "environmentId": environment_id}},
            )
            domain = dom_data.get("serviceDomainCreate", {}).get("domain")
            if domain:
                public_url = f"https://{domain}"
        except RailwayDeployFalla as e:
            logger.warning("deploy_railway_domain_create_warning", error=str(e))

    # 7. Polling del último deployment hasta SUCCESS / FAILED / CRASHED
    deployment_id: Optional[str] = None
    deployment_status = "UNKNOWN"
    build_confirmed = False
    poll_attempts = RAILWAY_POLL_MAX_S // RAILWAY_POLL_INTERVAL_S
    for _attempt in range(poll_attempts):
        try:
            depl_data = await _graphql(
                _Q_DEPLOYMENTS,
                {"input": {"projectId": project_id, "serviceId": service_id}},
            )
            edges = depl_data.get("deployments", {}).get("edges", [])
            if edges:
                node = edges[0]["node"]
                deployment_id = node.get("id")
                deployment_status = node.get("status", "UNKNOWN")
                if deployment_status == "SUCCESS":
                    build_confirmed = True
                    break
                if deployment_status in {"FAILED", "CRASHED"}:
                    logger.warning(
                        "deploy_railway_build_failed",
                        deployment_id=deployment_id,
                        status=deployment_status,
                    )
                    break
        except RailwayDeployFalla as e:
            logger.warning("deploy_railway_poll_warning", error=str(e))
        await asyncio.sleep(RAILWAY_POLL_INTERVAL_S)

    if not build_confirmed and deployment_status not in {"FAILED", "CRASHED"}:
        logger.warning(
            "deploy_railway_build_timeout",
            project_id=project_id,
            service_id=service_id,
            timeout_s=RAILWAY_POLL_MAX_S,
        )

    logger.info(
        "deploy_railway_completed",
        project_id=project_id,
        service_id=service_id,
        deployment_status=deployment_status,
        url=public_url,
        build_confirmed=build_confirmed,
    )

    return {
        "project_id": project_id,
        "service_id": service_id,
        "environment_id": environment_id,
        "deployment_id": deployment_id,
        "deployment_status": deployment_status,
        "url": public_url,
        "build_confirmed": build_confirmed,
    }


# ── Dispatch entry point ─────────────────────────────────────────────────────


# ── Sprint 84.5 — normalización de repo (Cowork spec, Fix 2) ─────────────
import re as _re

_REPO_URL_RE = _re.compile(r"^(?:https?://)?(?:github\.com/)?([^/\s]+/[^/.\s]+)(?:\.git)?/?$")


def _normalize_repo(repo: Optional[str], repo_url: Optional[str]) -> Optional[str]:
    """Devuelve siempre formato canónico 'owner/repo' o None si no parsea.

    Acepta:
      - 'owner/repo'                            (canónico, lo retorna tal cual)
      - 'https://github.com/owner/repo'         (lo despoja a 'owner/repo')
      - 'https://github.com/owner/repo.git'     (lo despoja)
      - 'github.com/owner/repo'                 (lo despoja)
    """
    candidates = [repo, repo_url]
    for cand in candidates:
        if not cand:
            continue
        if "/" in cand and not cand.startswith("http") and "github.com" not in cand:
            # Ya canónico
            return cand.strip().rstrip("/")
        m = _REPO_URL_RE.match(cand.strip())
        if m:
            return m.group(1)
    return None


async def execute_deploy_to_railway(params: dict[str, Any]) -> dict[str, Any]:
    """Adapter para tool_dispatch.py.

    Sprint 84.5: acepta tanto 'repo' (canónico) como 'repo_url' (compat).
    El ToolSpec expone solo 'repo' al LLM-planner para evitar confusión.
    """
    repo = _normalize_repo(params.get("repo"), params.get("repo_url"))
    project_name = params.get("project_name")
    if not repo or not project_name:
        return {
            "error": "deploy_railway_params_invalidos",
            "detail": "Se requieren 'repo' (owner/repo) y 'project_name' (str).",
        }
    try:
        result = await deploy_to_railway(
            repo=repo,
            project_name=project_name,
            service_name=params.get("service_name", "API"),
            env_vars=params.get("env_vars"),
            create_domain=bool(params.get("create_domain", True)),
        )
        return result
    except RailwayMissingToken as e:
        return {"error": "RailwayMissingToken", "detail": str(e)}
    except RailwayDeployFalla as e:
        return {"error": "RailwayDeployFalla", "detail": str(e)}
    except Exception as e:  # noqa: BLE001
        logger.exception("deploy_railway_unexpected_error", error=str(e))
        return {"error": "deploy_railway_unexpected_error", "detail": str(e)}
