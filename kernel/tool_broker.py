"""
El Monstruo — Tool Broker (ADR Sprint 10b)
============================================
Centralized tool execution with:
  - JIT secret resolution (secrets never enter LangGraph state)
  - Per-execution audit trail (tool_executions table)
  - Request-scoped BrokeredTool wrappers
  - Output sanitization (untrusted marking)
  - Rate limiting per binding

ADR Reference: ADR_SPRINT_10_Tool_Registry.md
Anti-autoboicot: validated 2026-04-18
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

from kernel.output_sanitizer import sanitize_tool_output, sanitize_tool_output_dict

logger = structlog.get_logger("kernel.tool_broker")


# ── Data Classes ──────────────────────────────────────────────────────


@dataclass
class ToolBinding:
    """Represents a tool binding for a specific tenant."""

    binding_id: str
    tool_name: str
    tenant_id: str
    is_enabled: bool = True
    capabilities: dict = field(default_factory=dict)
    rate_limit: int = 100
    secret_env_var: Optional[str] = None
    risk_level: str = "low"
    requires_hitl: bool = False


@dataclass
class ExecutionRecord:
    """Tracks a single tool execution."""

    execution_id: str
    run_id: str
    thread_id: str
    tenant_id: str
    tool_name: str
    status: str = "pending"  # pending, running, success, failed
    input_args: dict = field(default_factory=dict)
    output_summary: Optional[str] = None
    error_message: Optional[str] = None
    wall_ms: int = 0
    api_calls: int = 1
    cost_usd: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


# ── Tool Broker ───────────────────────────────────────────────────────


class ToolBroker:
    """
    Centralized tool execution broker.

    Security guarantees:
    1. Real adapters never injected into LangGraph state
    2. Secrets resolved JIT — never enter the StateGraph
    3. Tool output marked as untrusted
    4. Execution audit trail per-tool-call in Supabase
    """

    # ── Circuit Breaker Configuration ──────────────────────────────
    MAX_CALLS_PER_RUN = int(os.environ.get("BROKER_MAX_CALLS_PER_RUN", "50"))
    INPUT_HASH_REPEAT_LIMIT = 3  # Same input_hash repeated N times = loop

    def __init__(self, db=None, bindings: Optional[list[ToolBinding]] = None):
        self._db = db
        self._bindings: dict[str, ToolBinding] = {}
        self._execution_cache: dict[str, ExecutionRecord] = {}
        self._call_counts: dict[str, int] = {}  # tool_name -> calls this request
        # Circuit breaker state (per-run)
        self._run_call_count: int = 0  # total calls in current run
        self._input_hashes: dict[str, int] = {}  # hash -> count
        self._circuit_breaker_trips: int = 0

        if bindings:
            for b in bindings:
                self._bindings[b.tool_name] = b

    # ── Public API ────────────────────────────────────────────────────

    async def initialize(self, tenant_id: str = "alfredo"):
        """Load bindings from Supabase for the given tenant."""
        if not self._db:
            logger.warning("broker_no_db", msg="No DB — using static bindings")
            return

        try:
            rows = await self._db.select(
                "tool_bindings",
                columns="id, tool_name, tenant_id, is_enabled, capabilities, rate_limit",
                filters={"tenant_id": tenant_id, "is_enabled": True},
            )

            # Also get secret_env_var from tool_registry
            registry_rows = await self._db.select(
                "tool_registry",
                columns="tool_name, secret_env_var, risk_level, requires_hitl",
                filters={"is_active": True},
            )
            registry_map = {r["tool_name"]: r for r in (registry_rows or [])}

            for row in rows or []:
                tool_name = row["tool_name"]
                reg = registry_map.get(tool_name, {})
                self._bindings[tool_name] = ToolBinding(
                    binding_id=str(row["id"]),
                    tool_name=tool_name,
                    tenant_id=row["tenant_id"],
                    is_enabled=row["is_enabled"],
                    capabilities=row.get("capabilities", {}),
                    rate_limit=row.get("rate_limit", 100),
                    secret_env_var=reg.get("secret_env_var"),
                    risk_level=reg.get("risk_level", "low"),
                    requires_hitl=reg.get("requires_hitl", False),
                )

            logger.info("broker_initialized", tenant=tenant_id, bindings=len(self._bindings))
        except Exception as e:
            logger.error("broker_init_failed", error=str(e))

    def is_allowed(self, tool_name: str) -> bool:
        """Check if a tool is allowed for the current tenant."""
        binding = self._bindings.get(tool_name)
        if not binding:
            return True  # If no binding exists, allow (backward compat)
        return binding.is_enabled

    def check_rate_limit(self, tool_name: str) -> bool:
        """Check if the tool has exceeded its rate limit for this request batch."""
        binding = self._bindings.get(tool_name)
        if not binding:
            return True
        count = self._call_counts.get(tool_name, 0)
        return count < binding.rate_limit

    # ── JIT Secret Resolution ─────────────────────────────────────────

    def resolve_secret(self, tool_name: str) -> Optional[str]:
        """
        Resolve the secret for a tool Just-In-Time.

        SECURITY: The secret is resolved from env vars at execution time,
        never stored in LangGraph state, and never passed to the LLM.
        """
        binding = self._bindings.get(tool_name)
        if not binding or not binding.secret_env_var:
            return None

        secret = os.environ.get(binding.secret_env_var)
        if not secret:
            logger.warning(
                "broker_secret_missing",
                tool=tool_name,
                env_var=binding.secret_env_var,
            )
        return secret

    # ── Execute with Broker ───────────────────────────────────────────

    async def execute(
        self,
        tool_name: str,
        args: dict[str, Any],
        run_id: str = "",
        thread_id: str = "",
        tenant_id: str = "alfredo",
        executor_fn=None,
    ) -> dict[str, Any]:
        """
        Execute a tool through the broker.

        Flow:
        1. Validate binding and rate limit
        2. Create execution record (pending)
        3. Resolve secret JIT
        4. Execute via adapter
        5. Record result (success/failed)
        6. Sanitize output (mark as untrusted)
        7. Return result
        """
        exec_id = str(uuid.uuid4())
        record = ExecutionRecord(
            execution_id=exec_id,
            run_id=run_id,
            thread_id=thread_id,
            tenant_id=tenant_id,
            tool_name=tool_name,
            status="running",
            input_args=args,
            started_at=time.monotonic(),
        )

        # 1. Check binding
        if not self.is_allowed(tool_name):
            record.status = "failed"
            record.error_message = f"Tool '{tool_name}' is disabled for tenant '{tenant_id}'"
            await self._persist_execution(record)
            return {"error": record.error_message, "_untrusted": True}

        # 2. Circuit breaker: max calls per run
        self._run_call_count += 1
        if self._run_call_count > self.MAX_CALLS_PER_RUN:
            record.status = "failed"
            record.error_message = f"Circuit breaker: max {self.MAX_CALLS_PER_RUN} tool calls per run exceeded"
            self._circuit_breaker_trips += 1
            await self._persist_execution(record)
            await self._log_circuit_breaker(
                run_id=run_id,
                thread_id=thread_id,
                tool_name=tool_name,
                reason="max_calls_per_run",
                call_count=self._run_call_count,
            )
            return {"error": record.error_message, "_untrusted": True}

        # 3. Circuit breaker: input_hash loop detection
        input_hash = hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode()).hexdigest()[:16]
        self._input_hashes[input_hash] = self._input_hashes.get(input_hash, 0) + 1
        if self._input_hashes[input_hash] > self.INPUT_HASH_REPEAT_LIMIT:
            record.status = "failed"
            record.error_message = (
                f"Circuit breaker: identical input repeated {self._input_hashes[input_hash]} times (loop detected)"
            )
            self._circuit_breaker_trips += 1
            await self._persist_execution(record)
            await self._log_circuit_breaker(
                run_id=run_id,
                thread_id=thread_id,
                tool_name=tool_name,
                reason="input_hash_loop",
                call_count=self._input_hashes[input_hash],
                input_hash=input_hash,
            )
            return {"error": record.error_message, "_untrusted": True}

        # 4. Check rate limit (per-tool daily)
        if not self.check_rate_limit(tool_name):
            record.status = "failed"
            record.error_message = f"Rate limit exceeded for '{tool_name}'"
            await self._persist_execution(record)
            return {"error": record.error_message, "_untrusted": True}

        # 3. Resolve secret JIT
        self.resolve_secret(tool_name)

        # 4. Execute
        start_time = time.monotonic()
        try:
            if executor_fn:
                result = await executor_fn(tool_name, args)
            else:
                result = {"error": f"No executor for '{tool_name}'"}

            wall_ms = int((time.monotonic() - start_time) * 1000)

            # 5. Record success
            record.status = "success" if "error" not in result else "failed"
            record.wall_ms = wall_ms
            record.output_summary = str(result)[:500]
            if "error" in result:
                record.error_message = str(result["error"])[:500]

            # Track call count
            self._call_counts[tool_name] = self._call_counts.get(tool_name, 0) + 1

        except Exception as e:
            wall_ms = int((time.monotonic() - start_time) * 1000)
            record.status = "failed"
            record.wall_ms = wall_ms
            record.error_message = str(e)[:500]
            result = {"error": str(e)}
            logger.error("broker_execution_failed", tool=tool_name, error=str(e))

        # 6. Sanitize output before it enters LLM context
        if isinstance(result, dict):
            result = sanitize_tool_output_dict(result, tool_name=tool_name)
        elif isinstance(result, str):
            result = sanitize_tool_output(result, tool_name=tool_name)

        # 7. Persist execution record
        await self._persist_execution(record)

        # 8. Mark output as untrusted (ADR requirement)
        result["_untrusted"] = True
        result["_broker_exec_id"] = exec_id

        logger.info(
            "broker_executed",
            tool=tool_name,
            status=record.status,
            wall_ms=record.wall_ms,
            exec_id=exec_id,
        )

        return result

    # ── Persistence ───────────────────────────────────────────────────

    async def _persist_execution(self, record: ExecutionRecord):
        """Persist execution record to Supabase tool_executions table."""
        if not self._db:
            self._execution_cache[record.execution_id] = record
            return

        try:
            await self._db.insert(
                "tool_executions",
                {
                    "id": record.execution_id,
                    "run_id": record.run_id or str(uuid.uuid4()),
                    "thread_id": record.thread_id,
                    "tenant_id": record.tenant_id,
                    "tool_name": record.tool_name,
                    "status": record.status,
                    "input_args": record.input_args,
                    "output_summary": record.output_summary,
                    "error_message": record.error_message,
                    "wall_ms": record.wall_ms,
                    "api_calls": record.api_calls,
                    "cost_usd": float(record.cost_usd),
                },
            )
        except Exception as e:
            logger.error("broker_persist_failed", exec_id=record.execution_id, error=str(e))
            self._execution_cache[record.execution_id] = record

    # ── Circuit Breaker Logging ────────────────────────────────────

    async def _log_circuit_breaker(
        self,
        *,
        run_id: str,
        thread_id: str = "",
        tool_name: str,
        reason: str,
        call_count: int = 0,
        input_hash: str = "",
    ) -> None:
        """Log a circuit breaker trip to Supabase and structlog."""
        logger.warning(
            "circuit_breaker_tripped",
            tool=tool_name,
            reason=reason,
            call_count=call_count,
            input_hash=input_hash,
        )
        if not self._db:
            return
        try:
            await self._db.insert(
                "circuit_breaker_log",
                {
                    "run_id": run_id or str(uuid.uuid4()),
                    "thread_id": thread_id,
                    "tool_name": tool_name,
                    "trigger_reason": reason,
                    "call_count": call_count,
                    "input_hash": input_hash,
                },
            )
        except Exception as e:
            logger.error("circuit_breaker_log_failed", error=str(e))

    def reset_run_state(self) -> None:
        """Reset per-run circuit breaker state. Call at the start of each new run."""
        self._run_call_count = 0
        self._input_hashes.clear()

    # ── Stats ─────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Return broker stats for health endpoint."""
        return {
            "bindings_loaded": len(self._bindings),
            "tools_available": [
                {
                    "name": b.tool_name,
                    "enabled": b.is_enabled,
                    "risk": b.risk_level,
                    "rate_limit": b.rate_limit,
                    "secret_configured": b.secret_env_var is not None and os.environ.get(b.secret_env_var) is not None,
                }
                for b in self._bindings.values()
            ],
            "calls_this_session": dict(self._call_counts),
            "cached_executions": len(self._execution_cache),
            "circuit_breaker": {
                "max_calls_per_run": self.MAX_CALLS_PER_RUN,
                "input_hash_repeat_limit": self.INPUT_HASH_REPEAT_LIMIT,
                "current_run_calls": self._run_call_count,
                "total_trips": self._circuit_breaker_trips,
            },
        }


# ── BrokeredTool (Request-Scoped Wrapper) ─────────────────────────────


class BrokeredTool:
    """
    Request-scoped tool wrapper that the LLM interacts with.

    ADR Pattern: The LLM never sees the real adapter. It only sees
    BrokeredTool instances which route execution through the ToolBroker.

    This wrapper is created fresh for each request in the execute node,
    ensuring request isolation.
    """

    def __init__(
        self,
        name: str,
        broker: ToolBroker,
        run_id: str = "",
        thread_id: str = "",
        tenant_id: str = "alfredo",
        executor_fn=None,
    ):
        self.name = name
        self._broker = broker
        self._run_id = run_id
        self._thread_id = thread_id
        self._tenant_id = tenant_id
        self._executor_fn = executor_fn

    async def invoke(self, args: dict[str, Any]) -> dict[str, Any]:
        """Execute the tool through the broker."""
        return await self._broker.execute(
            tool_name=self.name,
            args=args,
            run_id=self._run_id,
            thread_id=self._thread_id,
            tenant_id=self._tenant_id,
            executor_fn=self._executor_fn,
        )


# ── Factory Function ──────────────────────────────────────────────────


def create_brokered_tools(
    broker: ToolBroker,
    tool_names: list[str],
    run_id: str = "",
    thread_id: str = "",
    tenant_id: str = "alfredo",
    executor_fn=None,
) -> dict[str, BrokeredTool]:
    """
    Create request-scoped BrokeredTool instances for the execute node.

    Called at the start of each tool_dispatch execution to create
    fresh wrappers that route through the broker.
    """
    tools = {}
    for name in tool_names:
        if broker.is_allowed(name):
            tools[name] = BrokeredTool(
                name=name,
                broker=broker,
                run_id=run_id,
                thread_id=thread_id,
                tenant_id=tenant_id,
                executor_fn=executor_fn,
            )
    return tools
