"""
CIDP Client — Async client for LangGraph integration.
======================================================
Designed to be injected into a LangGraph node (execute_cidp).
Uses aiohttp for non-blocking HTTP calls.

Anti-autoboicot: aiohttp>=3.13.4 (CVE-2026-22815 patched)

Usage in LangGraph:
    from cidp.client import CIDPClient

    client = CIDPClient(base_url="http://cidp-service:8000/api/v1")
    job_id = await client.start_job("Supabase", "Design 10x faster alternative")
    result = await client.wait_for_completion(job_id, timeout=3600)
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, Optional

import aiohttp
import structlog

logger = structlog.get_logger("cidp.client")


class CIDPClient:
    """
    Async HTTP client for the CIDP microservice.
    Thread-safe, designed for injection into LangGraph config.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_seconds: int = 30,
    ):
        self.base_url = (
            base_url
            or os.environ.get("CIDP_SERVICE_URL", "http://localhost:8000/api/v1")
        ).rstrip("/")
        self.api_key = api_key or os.environ.get("CIDP_API_KEY", "")
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def start_job(
        self,
        target: str,
        objective: str,
        max_iterations: int = 10,
        budget_usd: float = 50.0,
        enable_gpu_broker: bool = False,
        gpu_budget_usd: float = 100.0,
        research_only: bool = False,
        webhook_url: Optional[str] = None,
    ) -> str:
        """
        Start a new CIDP investigation cycle.

        Returns:
            job_id (str): Unique identifier for the job.

        Raises:
            aiohttp.ClientResponseError: On HTTP errors.
        """
        payload = {
            "target": target,
            "objective": objective,
            "max_iterations": max_iterations,
            "budget_usd": budget_usd,
            "enable_gpu_broker": enable_gpu_broker,
            "gpu_budget_usd": gpu_budget_usd,
            "research_only": research_only,
        }
        if webhook_url:
            payload["webhook_url"] = webhook_url

        async with aiohttp.ClientSession(
            headers=self._headers(), timeout=self.timeout
        ) as session:
            async with session.post(
                f"{self.base_url}/jobs", json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                job_id = data["job_id"]
                logger.info(
                    "cidp_job_started",
                    job_id=job_id,
                    target=target,
                    budget=budget_usd,
                )
                return job_id

    async def get_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the current status of a CIDP job.

        Returns:
            Dict with: job_id, status, current_iteration, current_stage,
                       cost_usd, score, artifacts, error
        """
        async with aiohttp.ClientSession(
            headers=self._headers(), timeout=self.timeout
        ) as session:
            async with session.get(
                f"{self.base_url}/jobs/{job_id}"
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a running job (triggers rollback and GPU teardown)."""
        async with aiohttp.ClientSession(
            headers=self._headers(), timeout=self.timeout
        ) as session:
            async with session.delete(
                f"{self.base_url}/jobs/{job_id}"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                logger.info("cidp_job_cancelled", job_id=job_id)
                return result

    async def resume_job(self, job_id: str) -> Dict[str, Any]:
        """Resume a paused or failed job from the last checkpoint."""
        async with aiohttp.ClientSession(
            headers=self._headers(), timeout=self.timeout
        ) as session:
            async with session.post(
                f"{self.base_url}/jobs/{job_id}/resume"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                logger.info("cidp_job_resumed", job_id=job_id)
                return result

    async def wait_for_completion(
        self,
        job_id: str,
        poll_interval: int = 60,
        timeout: int = 3600,
    ) -> Dict[str, Any]:
        """
        Poll until a job reaches a terminal state.

        Args:
            job_id: The job to monitor.
            poll_interval: Seconds between status checks.
            timeout: Max seconds to wait before raising TimeoutError.

        Returns:
            Final job status dict.

        Raises:
            TimeoutError: If job doesn't complete within timeout.
        """
        elapsed = 0.0
        while elapsed < timeout:
            status = await self.get_status(job_id)
            state = status.get("status", "")

            logger.debug(
                "cidp_poll",
                job_id=job_id,
                status=state,
                iteration=status.get("current_iteration", 0),
                stage=status.get("current_stage", ""),
                score=status.get("score", 0),
                cost=status.get("cost_usd", 0),
            )

            if state in ("completed", "failed", "cancelled"):
                return status

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(
            f"CIDP job {job_id} did not complete within {timeout}s "
            f"(last status: {status.get('status', 'unknown')})"
        )

    async def health(self) -> Dict[str, Any]:
        """Check CIDP service health."""
        # Health endpoint is at root, not under /api/v1
        base = self.base_url.replace("/api/v1", "")
        async with aiohttp.ClientSession(
            headers=self._headers(), timeout=self.timeout
        ) as session:
            async with session.get(f"{base}/health") as response:
                response.raise_for_status()
                return await response.json()
