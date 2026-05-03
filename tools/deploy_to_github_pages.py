"""
El Monstruo — Deploy to GitHub Pages (Sprint 84, Bloque 1)
==========================================================
Tool para que El Monstruo publique sitios estáticos end-to-end.
Cierra el gap detectado en la primera tarea real (Prueba 2):
generaba código completo pero no lo publicaba.

Soberanía: usa GITHUB_TOKEN ya activa, sin nuevas dependencias.
Diseño: Cowork (Hilo B). Validación magna: Manus Paso 0 confirmó
        endpoint POST /repos/{owner}/{repo}/pages, API version
        2026-03-10, sin cambios respecto al diseño original.

Brand:
- Errores: GitHubPagesDeployFalla, GitHubPagesBuildTimeout
- Logs:    deploy_pages_started, deploy_pages_completed,
           deploy_pages_build_timeout
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

import structlog

from tools.github import _request, create_or_update_file

logger = structlog.get_logger("tools.deploy_to_github_pages")

GH_USER = os.environ.get("GITHUB_USERNAME", "alfredogl1804")
PAGES_POLL_INTERVAL_S = 5
PAGES_POLL_MAX_S = 300  # 5 minutos


# ── Errores con identidad ────────────────────────────────────────────────────


class GitHubPagesDeployFalla(Exception):
    """Falla irrecuperable en deploy a GitHub Pages."""


class GitHubPagesBuildTimeout(Exception):
    """El build de GitHub Pages no confirmó status='built' en el tiempo límite."""


# ── Implementación ───────────────────────────────────────────────────────────


async def deploy_to_github_pages(
    repo_name: str,
    files: dict[str, str],
    description: str = "Sitio publicado por El Monstruo",
    private: bool = False,
    branch: str = "main",
) -> dict[str, Any]:
    """
    Crea o actualiza un repo, escribe archivos, activa Pages y espera el build.

    Args:
        repo_name: nombre del repo (sin owner). Ej: "leoncio-landing"
        files: dict de path → contenido. Ej: {"index.html": "<html>...", "style.css": "..."}
        description: descripción del repo (visible en GitHub)
        private: True para repo privado (Pages requiere paid plan en privado)
        branch: branch a usar para Pages (default 'main')

    Returns:
        {
          "url": "https://user.github.io/repo/",
          "repo": "owner/repo",
          "files_committed": 3,
          "files_paths": ["index.html", "style.css", ...],
          "build_confirmed": True | False
        }

    Raises:
        GitHubPagesDeployFalla: si el repo no se puede crear ni reusar.
    """
    if not files:
        raise GitHubPagesDeployFalla(
            "deploy_pages_files_vacios: el dict 'files' está vacío. "
            "Sugerencia: pasa al menos {'index.html': '<html>...'}'"
        )

    logger.info(
        "deploy_pages_started",
        repo=repo_name,
        files_count=len(files),
        private=private,
    )

    # 1. Crear repo (idempotente: si existe, GitHub responde 422 y seguimos)
    create_resp = await _request(
        "POST",
        "/user/repos",
        body={
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": True,  # crea README inicial para que el branch exista
        },
    )

    repo_full = f"{GH_USER}/{repo_name}"
    repo_already_existed = False
    if isinstance(create_resp, dict) and "error" in create_resp:
        detail = str(create_resp.get("detail", ""))
        if "already exists" in detail or "name already exists" in detail:
            repo_already_existed = True
            logger.info("deploy_pages_repo_existente_reusado", repo=repo_full)
        else:
            raise GitHubPagesDeployFalla(
                f"deploy_pages_repo_create_fallido: {create_resp}. "
                f"Sugerencia: verificar que GITHUB_TOKEN tiene scope 'repo' y que "
                f"'{repo_name}' es un nombre válido (kebab-case, sin espacios)."
            )

    # 2. Escribir todos los archivos
    committed: list[str] = []
    write_errors: list[dict] = []
    for path, content in files.items():
        # Si el archivo existe, necesitamos el sha actual para hacer update.
        sha: str | None = None
        existing = await _request("GET", f"/repos/{repo_full}/contents/{path}?ref={branch}")
        if isinstance(existing, dict) and existing.get("sha"):
            sha = existing["sha"]

        result = await create_or_update_file(
            repo=repo_full,
            path=path,
            content=content,
            message=f"deploy: {path}",
            sha=sha,
            branch=branch,
        )
        if isinstance(result, dict) and "error" not in result:
            committed.append(path)
        else:
            write_errors.append({"path": path, "error": result})
            logger.warning("deploy_pages_file_write_warning", path=path, error=result)

    # 3. Activar Pages (idempotente: 409/422 si ya estaba activado)
    pages_resp = await _request(
        "POST",
        f"/repos/{repo_full}/pages",
        body={"source": {"branch": branch, "path": "/"}},
    )
    if isinstance(pages_resp, dict) and "error" in pages_resp:
        detail = str(pages_resp.get("detail", "")).lower()
        if "already exists" in detail or "already enabled" in detail or "409" in str(pages_resp.get("error", "")):
            logger.info("deploy_pages_already_enabled", repo=repo_full)
        else:
            logger.warning("deploy_pages_enable_warning", resp=pages_resp)

    # 4. Polling del build hasta status='built'
    expected_url = f"https://{GH_USER.lower()}.github.io/{repo_name}/"
    url = expected_url
    build_confirmed = False
    poll_attempts = PAGES_POLL_MAX_S // PAGES_POLL_INTERVAL_S
    for _attempt in range(poll_attempts):
        status = await _request("GET", f"/repos/{repo_full}/pages")
        if isinstance(status, dict) and status.get("status") == "built":
            url = status.get("html_url") or expected_url
            build_confirmed = True
            break
        await asyncio.sleep(PAGES_POLL_INTERVAL_S)

    if not build_confirmed:
        logger.warning(
            "deploy_pages_build_timeout",
            repo=repo_full,
            expected_url=expected_url,
            timeout_s=PAGES_POLL_MAX_S,
        )

    logger.info(
        "deploy_pages_completed",
        repo=repo_full,
        url=url,
        files_committed=len(committed),
        build_confirmed=build_confirmed,
        repo_already_existed=repo_already_existed,
    )

    return {
        "url": url,
        "repo": repo_full,
        "files_committed": len(committed),
        "files_paths": committed,
        "build_confirmed": build_confirmed,
        "repo_already_existed": repo_already_existed,
        "write_errors": write_errors or None,
    }


# ── Dispatch entry point ─────────────────────────────────────────────────────


async def execute_deploy_to_github_pages(params: dict[str, Any]) -> dict[str, Any]:
    """Adapter para tool_dispatch.py — recibe params dict y retorna dict serializable."""
    repo_name = params.get("repo_name")
    files = params.get("files")
    if not repo_name or not isinstance(files, dict):
        return {
            "error": "deploy_pages_params_invalidos",
            "detail": "Se requieren 'repo_name' (str) y 'files' (dict[str, str]).",
        }
    try:
        result = await deploy_to_github_pages(
            repo_name=repo_name,
            files=files,
            description=params.get("description", "Sitio publicado por El Monstruo"),
            private=bool(params.get("private", False)),
            branch=params.get("branch", "main"),
        )
        return result
    except GitHubPagesDeployFalla as e:
        return {"error": "GitHubPagesDeployFalla", "detail": str(e)}
    except Exception as e:  # noqa: BLE001
        logger.exception("deploy_pages_unexpected_error", error=str(e))
        return {"error": "deploy_pages_unexpected_error", "detail": str(e)}
