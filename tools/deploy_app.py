"""
El Monstruo — Deploy App Wrapper (Sprint 84, Bloque 2)
=======================================================
Tool unificada que decide entre GitHub Pages (estático) y Railway (backend)
en base a heurísticas magna sobre los archivos del proyecto. La decisión queda
loggeada para auditoría y para alimentar al Embrión (Acto de Orquestación).

Diseño: Cowork (Hilo B). Validación: Manus Paso 0.

Brand:
- Errores: DeployAppMagnaInconcluso, DeployAppFalla
- Logs:    deploy_app_magna_decide, deploy_app_estatico, deploy_app_backend
"""
from __future__ import annotations

from typing import Any, Optional

import structlog

from tools.deploy_to_github_pages import execute_deploy_to_github_pages
from tools.deploy_to_railway import execute_deploy_to_railway

logger = structlog.get_logger("tools.deploy_app")

# Indicadores de backend dinámico (cualquiera fuerza Railway)
BACKEND_INDICATORS = (
    "requirements.txt",
    "pyproject.toml",
    "Pipfile",
    "package.json",
    "Gemfile",
    "go.mod",
    "Cargo.toml",
    "composer.json",
    "Dockerfile",
    "railway.json",
    "Procfile",
    "main.py",
    "app.py",
    "server.py",
    "server.js",
    "index.js",
    "manage.py",
)

# Tipos de archivo claramente estáticos
STATIC_EXTENSIONS = (".html", ".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".md", ".txt", ".json")


class DeployAppMagnaInconcluso(Exception):
    """No se pudo determinar magna entre estático y backend con confianza suficiente."""


class DeployAppFalla(Exception):
    """Falla irrecuperable en deploy_app."""


def _decide_target(files: dict[str, str]) -> tuple[str, str, float]:
    """
    Heurística magna para decidir el destino de deploy.

    Returns:
        (target, motivo, confianza)
        target: 'github_pages' | 'railway'
    """
    if not files:
        raise DeployAppFalla("deploy_app_files_vacios: no hay archivos para deployar.")

    file_names = set(files.keys())

    # Regla 1: si hay CUALQUIER indicador de backend → Railway
    backend_hits = file_names & set(BACKEND_INDICATORS)
    if backend_hits:
        return (
            "railway",
            f"detectados indicadores de backend: {sorted(backend_hits)}",
            0.95,
        )

    # Regla 2: si hay index.html y todos los demás son estáticos → GitHub Pages
    has_index = "index.html" in file_names
    all_static = all(
        any(name.lower().endswith(ext) for ext in STATIC_EXTENSIONS)
        for name in file_names
    )
    if has_index and all_static:
        return (
            "github_pages",
            "todos los archivos son estáticos y existe index.html",
            0.90,
        )

    # Regla 3: si todos son estáticos pero NO hay index.html → estático con warning
    if all_static:
        return (
            "github_pages",
            "todos los archivos son estáticos pero falta index.html (GitHub Pages servirá README como fallback)",
            0.60,
        )

    # Caso ambiguo: dejarlo en estático con confianza baja
    raise DeployAppMagnaInconcluso(
        "deploy_app_magna_inconclusa: no se detectaron indicadores de backend pero "
        f"hay archivos no-estáticos: {sorted(file_names - {n for n in file_names if any(n.lower().endswith(e) for e in STATIC_EXTENSIONS)})}. "
        "Sugerencia: especificar 'target_override' explícito o agregar Dockerfile/requirements.txt."
    )


async def deploy_app(
    project_name: str,
    files: dict[str, str],
    description: str = "App publicada por El Monstruo",
    private: bool = False,
    env_vars: Optional[dict[str, str]] = None,
    target_override: Optional[str] = None,  # 'github_pages' | 'railway' para forzar
    embrion_loop: Optional[Any] = None,  # Para reportar al Acto de Orquestación
) -> dict[str, Any]:
    """
    Wrapper unificado: decide entre GitHub Pages (estático) y Railway (backend),
    luego invoca la tool específica.

    Para Railway, primero crea el repo en GitHub (vía deploy_to_github_pages
    con HTML mínimo bootstrap) y luego conecta el repo en Railway. Esto garantiza
    que el código vive en GitHub primero (auditable) y Railway solo lo hospeda.
    """
    if target_override and target_override not in {"github_pages", "railway"}:
        raise DeployAppFalla(
            f"deploy_app_target_invalido: '{target_override}' no es 'github_pages' ni 'railway'."
        )

    if target_override:
        target = target_override
        motivo = "override explícito por caller"
        confianza = 1.0
    else:
        target, motivo, confianza = _decide_target(files)

    logger.info(
        "deploy_app_magna_decide",
        target=target,
        motivo=motivo,
        confianza=confianza,
        files_count=len(files),
        project_name=project_name,
    )

    # Hook de visibilidad para el Acto de Orquestación
    if embrion_loop and hasattr(embrion_loop, "report_orchestration_step"):
        embrion_loop.report_orchestration_step(
            step_name="deploy_app_magna_decide",
            agent="deploy_app",
            status="done",
        )

    if target == "github_pages":
        if embrion_loop and hasattr(embrion_loop, "report_orchestration_step"):
            embrion_loop.report_orchestration_step(
                step_name="deploy_to_github_pages",
                agent="deploy_to_github_pages",
                status="in_flight",
            )

        result = await execute_deploy_to_github_pages({
            "repo_name": project_name,
            "files": files,
            "description": description,
            "private": private,
        })

        if embrion_loop and hasattr(embrion_loop, "report_orchestration_step"):
            embrion_loop.report_orchestration_step(
                step_name="deploy_to_github_pages",
                agent="deploy_to_github_pages",
                status="done" if not result.get("error") else "failed",
            )

        return {
            "target": "github_pages",
            "magna_motivo": motivo,
            "magna_confianza": confianza,
            **result,
        }

    # target == "railway"
    # Paso 1: subir código a GitHub (Railway requiere GitHub repo conectado)
    if embrion_loop and hasattr(embrion_loop, "report_orchestration_step"):
        embrion_loop.report_orchestration_step(
            step_name="deploy_to_github_pages_bootstrap",
            agent="deploy_to_github_pages",
            status="in_flight",
        )

    pages_result = await execute_deploy_to_github_pages({
        "repo_name": project_name,
        "files": files,
        "description": description,
        "private": private,
    })

    if pages_result.get("error"):
        if embrion_loop and hasattr(embrion_loop, "report_orchestration_step"):
            embrion_loop.report_orchestration_step(
                step_name="deploy_to_github_pages_bootstrap",
                agent="deploy_to_github_pages",
                status="failed",
            )
        return {
            "target": "railway",
            "magna_motivo": motivo,
            "magna_confianza": confianza,
            "error": "deploy_app_github_bootstrap_fallo",
            "github_result": pages_result,
        }

    if embrion_loop and hasattr(embrion_loop, "report_orchestration_step"):
        embrion_loop.report_orchestration_step(
            step_name="deploy_to_github_pages_bootstrap",
            agent="deploy_to_github_pages",
            status="done",
        )
        embrion_loop.report_orchestration_step(
            step_name="deploy_to_railway",
            agent="deploy_to_railway",
            status="in_flight",
        )

    # Paso 2: deploy a Railway desde el repo recién creado
    repo_full = pages_result.get("repo")  # "owner/repo"
    railway_result = await execute_deploy_to_railway({
        "repo": repo_full,
        "project_name": project_name,
        "service_name": "API",
        "env_vars": env_vars,
        "create_domain": True,
    })

    if embrion_loop and hasattr(embrion_loop, "report_orchestration_step"):
        embrion_loop.report_orchestration_step(
            step_name="deploy_to_railway",
            agent="deploy_to_railway",
            status="done" if not railway_result.get("error") else "failed",
        )

    return {
        "target": "railway",
        "magna_motivo": motivo,
        "magna_confianza": confianza,
        "github_repo": repo_full,
        "github_url": pages_result.get("url"),
        **railway_result,
    }


# ── Dispatch entry point ─────────────────────────────────────────────────────


async def execute_deploy_app(params: dict[str, Any], embrion_loop: Optional[Any] = None) -> dict[str, Any]:
    """Adapter para tool_dispatch.py."""
    project_name = params.get("project_name")
    files = params.get("files")
    if not project_name or not isinstance(files, dict):
        return {
            "error": "deploy_app_params_invalidos",
            "detail": "Se requieren 'project_name' (str) y 'files' (dict[str, str]).",
        }
    try:
        result = await deploy_app(
            project_name=project_name,
            files=files,
            description=params.get("description", "App publicada por El Monstruo"),
            private=bool(params.get("private", False)),
            env_vars=params.get("env_vars"),
            target_override=params.get("target_override"),
            embrion_loop=embrion_loop,
        )
        return result
    except DeployAppMagnaInconcluso as e:
        return {"error": "DeployAppMagnaInconcluso", "detail": str(e)}
    except DeployAppFalla as e:
        return {"error": "DeployAppFalla", "detail": str(e)}
    except Exception as e:  # noqa: BLE001
        logger.exception("deploy_app_unexpected_error", error=str(e))
        return {"error": "deploy_app_unexpected_error", "detail": str(e)}
