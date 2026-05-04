"""
El Catastro · Cron entrypoint (Railway scheduled task).

Ejecutado diariamente a las 07:00 CST (13:00 UTC) por Railway via:
  railway.json -> services -> catastro-cron -> startCommand:
    "python -m kernel.catastro.cron"

Este módulo:
  1. Configura logging estructurado (stdout JSON-friendly)
  2. Verifica disciplina os.environ — secretos requeridos
  3. Ejecuta `CatastroPipeline().run()` con asyncio
  4. Imprime el summary del run (que Railway captura en logs)
  5. Sale con exit code distinto según resultado:
     - 0: success (>=2 fuentes OK)
     - 1: degradado (<2 fuentes)
     - 2: error fatal (excepción no controlada)

Disciplina os.environ verificada en runtime:
  - SUPABASE_URL                    (obligatorio para persistir; Bloque 3+)
  - SUPABASE_SERVICE_ROLE_KEY       (obligatorio para persistir; Bloque 3+)
  - ARTIFICIAL_ANALYSIS_API_KEY     (recomendado; AA falla si falta)
  - OPENROUTER_API_KEY              (opcional; OR funciona sin auth)
  - HF_TOKEN                        (opcional; LMArena via HF es público)

[Hilo Manus Catastro] · Sprint 86 Bloque 2 · 2026-05-04
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone

from kernel.catastro.pipeline import CatastroPipeline


# ============================================================================
# LOGGING SETUP
# ============================================================================

def _configure_logging() -> None:
    """Configura logging para Railway (stdout, formato simple legible)."""
    level_str = os.environ.get("CATASTRO_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


# ============================================================================
# ENV VAR CHECKS
# ============================================================================

REQUIRED_ENV_VARS_PERSISTENCE = ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
RECOMMENDED_ENV_VARS_FETCH = ("ARTIFICIAL_ANALYSIS_API_KEY",)
OPTIONAL_ENV_VARS_FETCH = ("OPENROUTER_API_KEY", "HF_TOKEN")


def _check_env() -> dict[str, list[str]]:
    """
    Verifica qué env vars están configuradas.

    Returns:
        dict con claves: required_missing, recommended_missing, optional_missing
    """
    return {
        "required_missing": [v for v in REQUIRED_ENV_VARS_PERSISTENCE if not os.environ.get(v)],
        "recommended_missing": [v for v in RECOMMENDED_ENV_VARS_FETCH if not os.environ.get(v)],
        "optional_missing": [v for v in OPTIONAL_ENV_VARS_FETCH if not os.environ.get(v)],
    }


# ============================================================================
# MAIN
# ============================================================================

async def _run_async(*, dry_run: bool) -> int:
    """Ejecuta el pipeline async y retorna exit code."""
    logger = logging.getLogger("kernel.catastro.cron")

    env_status = _check_env()
    logger.info(f"env check: {env_status}")

    if env_status["required_missing"]:
        logger.warning(
            f"Persistencia BLOQUEADA: faltan env vars {env_status['required_missing']}. "
            "El pipeline correrá en modo dry-fetch (sin persistir a Supabase)."
        )
        # En Bloque 2 todavía no hay persistencia real, así que esto es solo info

    pipeline = CatastroPipeline(dry_run=dry_run)

    try:
        result = await pipeline.run()
    except Exception as e:  # noqa: BLE001
        logger.exception(f"Pipeline crashed: {e}")
        return 2

    summary = result.summary()
    print(json.dumps({"catastro_pipeline_summary": summary}, default=str, indent=2))

    if not result.is_success:
        logger.error("Run DEGRADED: <2 fuentes respondieron")
        return 1

    return 0


def main() -> int:
    """Entrypoint sync para Railway / CLI."""
    _configure_logging()
    logger = logging.getLogger("kernel.catastro.cron")

    logger.info(
        f"Catastro cron starting at {datetime.now(timezone.utc).isoformat()} "
        f"(host={os.environ.get('RAILWAY_SERVICE_NAME', 'local')})"
    )

    dry_run = os.environ.get("CATASTRO_DRY_RUN", "false").lower() in ("true", "1", "yes")
    if dry_run:
        logger.warning("CATASTRO_DRY_RUN=true — usando snapshots fake (NO red)")

    return asyncio.run(_run_async(dry_run=dry_run))


if __name__ == "__main__":
    sys.exit(main())
