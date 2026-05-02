"""
El Monstruo — SP10: Manus Bridge (Multi-Agent Delegation)
==========================================================
Permite al embrión comunicarse con el Command Center y otros hilos.

Endpoints del Command Center:
  POST /api/bridge/snapshot — envía snapshot de estado
  GET  /api/bridge/snapshot — lee snapshots de otros hilos

Base URL: https://monstruodash-ggmndxgx.manus.space
Auth: x-bridge-key header (JWT_SECRET del proyecto)

Spec (Hilo B):
  - post_bridge_snapshot(hilo_id, status, metrics) → envía snapshot
  - read_bridge_snapshots() → lee snapshots de otros hilos
"""

from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

import httpx
import structlog

logger = structlog.get_logger("kernel.manus_bridge")

# ─── Configuration ────────────────────────────────────────────────────────────

COMMAND_CENTER_URL = os.environ.get(
    "COMMAND_CENTER_URL",
    "https://monstruodash-ggmndxgx.manus.space",
)
BRIDGE_API_KEY = os.environ.get("COMMAND_CENTER_API_KEY", os.environ.get("JWT_SECRET", ""))
SNAPSHOT_ENDPOINT = "/api/bridge/snapshot"
DEFAULT_TIMEOUT = 10.0  # seconds


# ─── Data Models ──────────────────────────────────────────────────────────────


@dataclass
class BridgeSnapshot:
    """Snapshot de estado de un hilo para el Command Center."""

    hilo_id: str
    status: str  # "active", "idle", "error", "completed"
    metrics: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BridgeResponse:
    """Respuesta del Command Center."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    status_code: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "status_code": self.status_code,
        }


# ─── Core Functions ───────────────────────────────────────────────────────────


async def post_bridge_snapshot(
    hilo_id: str,
    status: str,
    metrics: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> BridgeResponse:
    """
    Envía un snapshot de estado al Command Center.

    Args:
        hilo_id: Identificador del hilo (e.g., "hilo_c_ejecutor_python")
        status: Estado actual ("active", "idle", "error", "completed")
        metrics: Métricas opcionales (tasks_completed, cost_usd, etc.)
        metadata: Metadata adicional opcional

    Returns:
        BridgeResponse con el resultado de la operación.
    """
    if not BRIDGE_API_KEY:
        logger.warning("bridge_no_api_key", msg="COMMAND_CENTER_API_KEY not set")
        return BridgeResponse(
            success=False,
            error="COMMAND_CENTER_API_KEY not configured",
            status_code=0,
        )

    snapshot = BridgeSnapshot(
        hilo_id=hilo_id,
        status=status,
        metrics=metrics or {},
        metadata=metadata or {},
    )

    url = f"{COMMAND_CENTER_URL}{SNAPSHOT_ENDPOINT}"
    headers = {
        "x-bridge-key": BRIDGE_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.post(
                url,
                json=snapshot.to_dict(),
                headers=headers,
            )

        logger.info(
            "bridge_snapshot_posted",
            hilo_id=hilo_id,
            status=status,
            status_code=response.status_code,
        )

        return BridgeResponse(
            success=response.status_code in (200, 201),
            data=response.json() if response.status_code in (200, 201) else None,
            error=response.text if response.status_code >= 400 else None,
            status_code=response.status_code,
        )

    except httpx.TimeoutException:
        logger.error("bridge_timeout", url=url, hilo_id=hilo_id)
        return BridgeResponse(
            success=False,
            error="Request timed out",
            status_code=0,
        )
    except httpx.ConnectError as e:
        logger.error("bridge_connect_error", url=url, error=str(e)[:100])
        return BridgeResponse(
            success=False,
            error=f"Connection failed: {str(e)[:100]}",
            status_code=0,
        )
    except Exception as e:
        logger.error("bridge_unexpected_error", error=str(e)[:200])
        return BridgeResponse(
            success=False,
            error=f"Unexpected error: {str(e)[:100]}",
            status_code=0,
        )


async def read_bridge_snapshots(
    hilo_filter: Optional[str] = None,
) -> BridgeResponse:
    """
    Lee snapshots de otros hilos desde el Command Center.

    Args:
        hilo_filter: Filtrar por hilo_id específico (opcional).

    Returns:
        BridgeResponse con lista de snapshots en .data
    """
    if not BRIDGE_API_KEY:
        logger.warning("bridge_no_api_key", msg="COMMAND_CENTER_API_KEY not set")
        return BridgeResponse(
            success=False,
            error="COMMAND_CENTER_API_KEY not configured",
            status_code=0,
        )

    url = f"{COMMAND_CENTER_URL}{SNAPSHOT_ENDPOINT}"
    headers = {
        "x-bridge-key": BRIDGE_API_KEY,
    }
    params: dict[str, str] = {}
    if hilo_filter:
        params["hilo_id"] = hilo_filter

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(
                url,
                headers=headers,
                params=params,
            )

        if response.status_code == 200:
            data = response.json()
            logger.info(
                "bridge_snapshots_read",
                count=len(data) if isinstance(data, list) else 1,
                hilo_filter=hilo_filter,
            )
            return BridgeResponse(
                success=True,
                data=data,
                status_code=200,
            )
        else:
            return BridgeResponse(
                success=False,
                error=response.text,
                status_code=response.status_code,
            )

    except httpx.TimeoutException:
        logger.error("bridge_read_timeout", url=url)
        return BridgeResponse(
            success=False,
            error="Request timed out",
            status_code=0,
        )
    except httpx.ConnectError as e:
        logger.error("bridge_read_connect_error", url=url, error=str(e)[:100])
        return BridgeResponse(
            success=False,
            error=f"Connection failed: {str(e)[:100]}",
            status_code=0,
        )
    except Exception as e:
        logger.error("bridge_read_unexpected_error", error=str(e)[:200])
        return BridgeResponse(
            success=False,
            error=f"Unexpected error: {str(e)[:100]}",
            status_code=0,
        )


# ─── Convenience Helpers ──────────────────────────────────────────────────────


async def report_task_progress(
    hilo_id: str,
    task_id: str,
    step_id: str,
    tools_used: list[str],
    cost_usd: float,
    model_used: str,
) -> BridgeResponse:
    """
    Reporta progreso de una tarea específica al Command Center.

    Convenience wrapper que estructura las métricas para el snapshot.
    """
    return await post_bridge_snapshot(
        hilo_id=hilo_id,
        status="active",
        metrics={
            "task_id": task_id,
            "step_id": step_id,
            "tools_used": tools_used,
            "cost_usd": cost_usd,
            "model_used": model_used,
        },
    )


async def report_error(
    hilo_id: str,
    error_msg: str,
    context: dict[str, Any] | None = None,
) -> BridgeResponse:
    """Reporta un error al Command Center."""
    return await post_bridge_snapshot(
        hilo_id=hilo_id,
        status="error",
        metrics={"error": error_msg},
        metadata=context or {},
    )


async def report_completion(
    hilo_id: str,
    task_id: str,
    total_cost_usd: float,
    total_steps: int,
) -> BridgeResponse:
    """Reporta completación de una tarea al Command Center."""
    return await post_bridge_snapshot(
        hilo_id=hilo_id,
        status="completed",
        metrics={
            "task_id": task_id,
            "total_cost_usd": total_cost_usd,
            "total_steps": total_steps,
        },
    )
