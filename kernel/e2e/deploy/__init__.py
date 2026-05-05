"""
Sprint 87.2 Bloque 1 — Deploy real para Pipeline E2E.

Cierra deuda #3 del Sprint 87 NUEVO: DEPLOY mock → GitHub Pages real.

Reusa Capa 1 Manos (tools/deploy_to_github_pages, tools/deploy_to_railway).
"""
from kernel.e2e.deploy.real_deploy import (
    DeployTarget,
    RealDeployResult,
    run_real_deploy,
)

__all__ = ["DeployTarget", "RealDeployResult", "run_real_deploy"]
