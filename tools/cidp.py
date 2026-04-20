"""
El Monstruo — CIDP Tool (Ciclo de Investigación y Descubrimiento Perpetuo)
==========================================================================
Gives El Monstruo the ability to launch deep, multi-iteration research cycles
via the CIDP microservice (sidecar).

This tool is invoked by the LLM via native function calling when:
    - User asks for deep research on a topic
    - User asks to investigate a technology/platform
    - User explicitly requests a "CIDP cycle" or "investigación profunda"

The CIDP runs asynchronously — this tool starts the job and returns
the job_id for tracking. The LLM can then poll status or wait.

Architecture:
    LLM → tool_dispatch → cidp.py → CIDPClient → CIDP microservice (Railway)

Anti-autoboicot: aiohttp>=3.13.4 (CVE-2026-22815)
"""

from __future__ import annotations

from typing import Any, Dict

import structlog

logger = structlog.get_logger("tools.cidp")


async def start_cidp_research(
    target: str,
    objective: str,
    max_iterations: int = 5,
    budget_usd: float = 25.0,
    research_only: bool = False,
) -> Dict[str, Any]:
    """
    Start a CIDP research cycle on a target.

    Args:
        target: The software, platform, or topic to investigate.
        objective: The 10x objective (what we want to achieve/discover).
        max_iterations: Max research iterations (default 5 for tool calls).
        budget_usd: Max budget in USD (default $25 for tool calls).
        research_only: If True, only research — no build/prototype.

    Returns:
        Dict with job_id, status, and instructions for polling.
    """
    try:
        from cidp.client import CIDPClient

        client = CIDPClient()

        # Check service health first
        try:
            health = await client.health()
            if health.get("status") != "healthy":
                return {
                    "error": "CIDP service is not healthy",
                    "health": health,
                    "suggestion": "The CIDP microservice may be down. Check Railway logs.",
                }
        except Exception as e:
            return {
                "error": f"Cannot reach CIDP service: {str(e)}",
                "suggestion": (
                    "The CIDP microservice is not reachable. "
                    "Verify CIDP_SERVICE_URL env var and that the service is deployed on Railway."
                ),
            }

        # Start the job
        job_id = await client.start_job(
            target=target,
            objective=objective,
            max_iterations=max_iterations,
            budget_usd=budget_usd,
            research_only=research_only,
        )

        logger.info(
            "cidp_research_started",
            job_id=job_id,
            target=target,
            objective=objective[:80],
            budget=budget_usd,
        )

        return {
            "job_id": job_id,
            "status": "started",
            "target": target,
            "objective": objective,
            "budget_usd": budget_usd,
            "max_iterations": max_iterations,
            "message": (
                f"CIDP research cycle started for '{target}'. "
                f"Job ID: {job_id}. "
                f"The cycle will run up to {max_iterations} iterations with a ${budget_usd} budget. "
                f"Use check_cidp_status with this job_id to monitor progress."
            ),
        }

    except Exception as e:
        logger.error("cidp_start_failed", target=target, error=str(e))
        return {"error": str(e), "target": target}


async def check_cidp_status(job_id: str) -> Dict[str, Any]:
    """
    Check the status of a running CIDP research cycle.

    Args:
        job_id: The CIDP job ID returned by start_cidp_research.

    Returns:
        Dict with current status, iteration, stage, score, cost.
    """
    try:
        from cidp.client import CIDPClient

        client = CIDPClient()
        status = await client.get_status(job_id)

        # Format a human-readable summary
        state = status.get("status", "unknown")
        iteration = status.get("current_iteration", 0)
        stage = status.get("current_stage", "unknown")
        score = status.get("score", 0.0)
        cost = status.get("cost_usd", 0.0)

        summary = (
            f"Job {job_id}: {state} | "
            f"Iteration {iteration} | Stage: {stage} | "
            f"10x Score: {score:.1f}/100 | Cost: ${cost:.2f}"
        )

        if state == "completed":
            summary += " | Research cycle completed successfully!"
        elif state == "failed":
            error = status.get("error", "Unknown error")
            summary += f" | FAILED: {error}"
        elif state == "cancelled":
            summary += " | Job was cancelled."

        return {
            **status,
            "summary": summary,
        }

    except Exception as e:
        logger.error("cidp_status_check_failed", job_id=job_id, error=str(e))
        return {"error": str(e), "job_id": job_id}


async def cancel_cidp_research(job_id: str) -> Dict[str, Any]:
    """
    Cancel a running CIDP research cycle.

    Args:
        job_id: The CIDP job ID to cancel.

    Returns:
        Dict with cancellation confirmation.
    """
    try:
        from cidp.client import CIDPClient

        client = CIDPClient()
        result = await client.cancel_job(job_id)

        logger.info("cidp_research_cancelled", job_id=job_id)

        return {
            **result,
            "message": f"CIDP job {job_id} has been cancelled. Resources released.",
        }

    except Exception as e:
        logger.error("cidp_cancel_failed", job_id=job_id, error=str(e))
        return {"error": str(e), "job_id": job_id}
