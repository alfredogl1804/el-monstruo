"""
El Monstruo — Command Center Bridge (SP10)
===========================================
Extends the Manus Bridge to integrate with the Command Center dashboard.
Provides bidirectional communication between the Embrión and the Command Center.

Capabilities:
  - POST /api/bridge/snapshot → Send execution state to Command Center
  - Delegate tasks to Manus agents with Command Center tracking
  - Report task progress and results back to the dashboard

Command Center URL: monstruodash-ggmndxgx.manus.space

Integration points:
  - TaskPlanner sends snapshots after each step completion
  - ExecutionVerifier sends verification results
  - AdaptiveModelSelector sends model performance data
  - Manus Bridge reports delegation status

Sprint: SP10 (Embrión Superpowers)
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.command_center_bridge")

# ── Configuration ────────────────────────────────────────────────────

COMMAND_CENTER_URL = os.environ.get(
    "COMMAND_CENTER_URL",
    "https://monstruodash-ggmndxgx.manus.space"
)
COMMAND_CENTER_API_KEY = os.environ.get("COMMAND_CENTER_API_KEY", "")
SNAPSHOT_ENDPOINT = "/api/bridge/snapshot"
DELEGATION_ENDPOINT = "/api/bridge/delegate"
STATUS_ENDPOINT = "/api/bridge/status"

# Rate limiting
MAX_SNAPSHOTS_PER_MINUTE = 10
_snapshot_timestamps: list[float] = []


# ── Data Models ──────────────────────────────────────────────────────

@dataclass
class ExecutionSnapshot:
    """Snapshot of current execution state for the Command Center."""
    snapshot_id: str
    timestamp: float = field(default_factory=time.time)
    source: str = "embrion"  # embrion, planner, verifier, selector

    # Task context
    task_id: Optional[str] = None
    plan_id: Optional[str] = None
    step_index: Optional[int] = None

    # Execution state
    status: str = "running"  # running, completed, failed, delegated
    progress_pct: float = 0.0
    current_action: str = ""

    # Metrics
    tool_calls: int = 0
    tokens_used: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0

    # Model info
    model_used: Optional[str] = None
    model_provider: Optional[str] = None

    # Verification (SP5)
    verification_verdict: Optional[str] = None
    verification_evidence: Optional[list] = None

    # Delegation (SP10)
    delegated_to: Optional[str] = None  # manus_google, manus_apple
    delegation_task_id: Optional[str] = None

    # Extra context
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "source": self.source,
            "task_id": self.task_id,
            "plan_id": self.plan_id,
            "step_index": self.step_index,
            "status": self.status,
            "progress_pct": round(self.progress_pct, 1),
            "current_action": self.current_action,
            "tool_calls": self.tool_calls,
            "tokens_used": self.tokens_used,
            "cost_usd": round(self.cost_usd, 6),
            "latency_ms": round(self.latency_ms, 1),
            "model_used": self.model_used,
            "model_provider": self.model_provider,
            "verification_verdict": self.verification_verdict,
            "verification_evidence": self.verification_evidence,
            "delegated_to": self.delegated_to,
            "delegation_task_id": self.delegation_task_id,
            "metadata": self.metadata,
        }


@dataclass
class DelegationRequest:
    """Request to delegate a task to a Manus agent."""
    prompt: str
    account: str = "google"  # google, apple
    priority: str = "normal"  # low, normal, high, critical
    timeout_s: float = 300.0
    context: dict = field(default_factory=dict)
    track_in_command_center: bool = True


@dataclass
class DelegationResult:
    """Result of a delegation to Manus."""
    task_id: str
    status: str  # created, running, completed, failed, timeout
    output: Optional[str] = None
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "output": self.output,
            "cost_usd": round(self.cost_usd, 6),
            "latency_ms": round(self.latency_ms, 1),
            "error": self.error,
        }


# ── Command Center Bridge ────────────────────────────────────────────

class CommandCenterBridge:
    """
    Bridge between the Embrión and the Command Center dashboard.
    Sends execution snapshots and manages task delegations.
    """

    def __init__(self):
        self._http_client = None
        self._initialized = False
        self._stats = {
            "snapshots_sent": 0,
            "snapshots_failed": 0,
            "delegations_created": 0,
            "delegations_completed": 0,
            "delegations_failed": 0,
        }

    async def initialize(self) -> None:
        """Initialize the HTTP client."""
        try:
            import httpx
            self._http_client = httpx.AsyncClient(
                base_url=COMMAND_CENTER_URL,
                timeout=10.0,
                headers={
                    "Content-Type": "application/json",
                    "X-Bridge-Key": COMMAND_CENTER_API_KEY,
                    "X-Source": "embrion-kernel",
                },
            )
            self._initialized = True
            logger.info(
                "command_center_bridge_initialized",
                url=COMMAND_CENTER_URL,
            )
        except Exception as e:
            logger.warning("command_center_bridge_init_failed", error=str(e)[:100])

    async def send_snapshot(self, snapshot: ExecutionSnapshot) -> bool:
        """
        Send an execution snapshot to the Command Center.
        Rate limited to MAX_SNAPSHOTS_PER_MINUTE.
        Returns True if sent successfully.
        """
        # Rate limiting
        now = time.time()
        _snapshot_timestamps[:] = [t for t in _snapshot_timestamps if now - t < 60]
        if len(_snapshot_timestamps) >= MAX_SNAPSHOTS_PER_MINUTE:
            logger.debug("command_center_snapshot_rate_limited")
            return False
        _snapshot_timestamps.append(now)

        if not self._initialized or not self._http_client:
            # Silently skip if not configured
            return False

        try:
            response = await self._http_client.post(
                SNAPSHOT_ENDPOINT,
                json=snapshot.to_dict(),
            )

            if response.status_code in (200, 201, 202):
                self._stats["snapshots_sent"] += 1
                logger.debug(
                    "command_center_snapshot_sent",
                    snapshot_id=snapshot.snapshot_id,
                    status=snapshot.status,
                )
                return True
            else:
                self._stats["snapshots_failed"] += 1
                logger.warning(
                    "command_center_snapshot_rejected",
                    status_code=response.status_code,
                    body=response.text[:200],
                )
                return False

        except Exception as e:
            self._stats["snapshots_failed"] += 1
            logger.warning(
                "command_center_snapshot_error",
                error=str(e)[:100],
            )
            return False

    async def delegate_task(self, request: DelegationRequest) -> DelegationResult:
        """
        Delegate a task to a Manus agent and optionally track in Command Center.

        Uses the existing manus_bridge tool under the hood, but adds:
        - Command Center tracking
        - Priority-based timeout adjustment
        - Context injection
        """
        from tools.manus_bridge import (
            create_task,
            wait_for_completion,
            ManusBridgeError,
            ManusTimeoutError,
            ManusTaskFailedError,
        )

        start = time.time()

        # Adjust timeout based on priority
        timeout = request.timeout_s
        if request.priority == "critical":
            timeout = max(timeout, 600.0)
        elif request.priority == "high":
            timeout = max(timeout, 450.0)

        # Build enhanced prompt with context
        enhanced_prompt = request.prompt
        if request.context:
            context_str = json.dumps(request.context, ensure_ascii=False, indent=2)
            enhanced_prompt = f"{request.prompt}\n\n[CONTEXT]\n{context_str}"

        try:
            # Create task via Manus API
            task = create_task(
                enhanced_prompt,
                account=request.account,
            )
            task_id = task.get("task_id", "")

            if not task_id:
                return DelegationResult(
                    task_id="",
                    status="failed",
                    error="create_task did not return a task_id",
                )

            self._stats["delegations_created"] += 1

            # Send snapshot to Command Center
            if request.track_in_command_center:
                from uuid import uuid4
                await self.send_snapshot(ExecutionSnapshot(
                    snapshot_id=str(uuid4()),
                    source="bridge",
                    status="delegated",
                    current_action=f"Delegated to Manus ({request.account})",
                    delegated_to=f"manus_{request.account}",
                    delegation_task_id=task_id,
                    metadata={"priority": request.priority, "prompt_preview": request.prompt[:200]},
                ))

            # Wait for completion
            result = wait_for_completion(
                task_id,
                account=request.account,
                timeout=timeout,
            )

            latency = (time.time() - start) * 1000
            status = result.get("status", "unknown")
            output = result.get("output", "")

            if status == "completed":
                self._stats["delegations_completed"] += 1
            else:
                self._stats["delegations_failed"] += 1

            return DelegationResult(
                task_id=task_id,
                status=status,
                output=output,
                latency_ms=latency,
            )

        except ManusTimeoutError as e:
            self._stats["delegations_failed"] += 1
            return DelegationResult(
                task_id=task_id if 'task_id' in dir() else "",
                status="timeout",
                error=str(e),
                latency_ms=(time.time() - start) * 1000,
            )

        except ManusTaskFailedError as e:
            self._stats["delegations_failed"] += 1
            return DelegationResult(
                task_id=task_id if 'task_id' in dir() else "",
                status="failed",
                error=str(e),
                latency_ms=(time.time() - start) * 1000,
            )

        except ManusBridgeError as e:
            self._stats["delegations_failed"] += 1
            return DelegationResult(
                task_id="",
                status="failed",
                error=str(e),
                latency_ms=(time.time() - start) * 1000,
            )

    async def report_completion(
        self,
        plan_id: str,
        status: str,
        summary: str,
        metrics: dict,
    ) -> bool:
        """Report task completion to Command Center."""
        from uuid import uuid4
        return await self.send_snapshot(ExecutionSnapshot(
            snapshot_id=str(uuid4()),
            source="planner",
            plan_id=plan_id,
            status=status,
            current_action="Plan completed",
            tool_calls=metrics.get("tool_calls", 0),
            tokens_used=metrics.get("tokens_used", 0),
            cost_usd=metrics.get("cost_usd", 0.0),
            latency_ms=metrics.get("latency_ms", 0.0),
            model_used=metrics.get("model_used"),
            metadata={"summary": summary[:500]},
        ))

    def get_stats(self) -> dict[str, Any]:
        """Get bridge statistics."""
        return {
            **self._stats,
            "initialized": self._initialized,
            "command_center_url": COMMAND_CENTER_URL,
            "configured": bool(COMMAND_CENTER_API_KEY),
        }

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()


# ── Singleton ────────────────────────────────────────────────────────

_bridge_instance: Optional[CommandCenterBridge] = None


def get_command_center_bridge() -> Optional[CommandCenterBridge]:
    """Get the singleton CommandCenterBridge."""
    return _bridge_instance


async def init_command_center_bridge() -> CommandCenterBridge:
    """Initialize and return the singleton CommandCenterBridge."""
    global _bridge_instance
    _bridge_instance = CommandCenterBridge()
    await _bridge_instance.initialize()
    return _bridge_instance
