"""
El Monstruo — Execution Verifier (SP5: ACI Repair)
====================================================
Post-execution verification node that ensures plans actually executed
rather than just completing with tool_calls = 0.

The Problem:
    The ACI (Autonomous Capability Infrastructure) is broken — plans
    complete with status=DONE even when no tools were actually called.
    Claude says "done" without having done anything real.

The Solution:
    A verification layer that runs AFTER each step completes and BEFORE
    marking it as DONE. It checks for concrete evidence of execution:
    - Were tools actually called? (tool_calls > 0)
    - Is there concrete output? (file created, API response, test passed)
    - Does the result match the step's objective?

Three Verdicts:
    SUCCESS  — Step genuinely completed with evidence
    CONTINUE — Step partially done, needs more work
    PIVOT    — Step approach is wrong, needs replanning

Each verdict requires concrete evidence, not just LLM text.

Persistence:
    Results stored in Supabase table: verification_results
    (task_id, step_id, verdict, evidence, cost_usd, verified_at)

Integration:
    Called from TaskPlanner._execute_step_with_react() BEFORE marking
    step.status = StepStatus.DONE.

Sprint SP5 — ACI Repair (Execution Verification)
Author: Hilo C (Orquestador)
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("kernel.execution_verifier")


# ── Configuration ────────────────────────────────────────────────────

VERIFIER_MODEL = os.environ.get("VERIFIER_MODEL", "gpt-5.5")
VERIFIER_BUDGET_USD = float(os.environ.get("VERIFIER_BUDGET_USD", "0.10"))
VERIFIER_TIMEOUT_S = int(os.environ.get("VERIFIER_TIMEOUT_S", "30"))

# Minimum tool calls required for a step to be considered "executed"
MIN_TOOL_CALLS_FOR_SUCCESS = int(os.environ.get("MIN_TOOL_CALLS_FOR_SUCCESS", "1"))


# ── Data Models ──────────────────────────────────────────────────────


class Verdict(str, Enum):
    """Post-execution verification verdict."""

    SUCCESS = "success"  # Step genuinely completed with evidence
    CONTINUE = "continue"  # Step partially done, needs more work
    PIVOT = "pivot"  # Step approach is wrong, needs replanning


class EvidenceType(str, Enum):
    """Types of concrete evidence that prove execution happened."""

    TOOL_OUTPUT = "tool_output"  # Tool returned a result
    FILE_CREATED = "file_created"  # A file was created/modified
    API_RESPONSE = "api_response"  # An API call returned data
    CODE_EXECUTED = "code_executed"  # Code ran and produced output
    SEARCH_RESULTS = "search_results"  # Web search returned results
    KNOWLEDGE_STORED = "knowledge_stored"  # Knowledge was ingested
    MESSAGE_SENT = "message_sent"  # A message was delivered
    MANUS_DELEGATED = "manus_delegated"  # Task delegated to Manus
    TEST_PASSED = "test_passed"  # A test/validation passed
    NONE = "none"  # No evidence found


class VerificationResult:
    """Result of verifying a single step's execution."""

    def __init__(
        self,
        task_id: str,
        step_id: str,
        step_index: int,
        verdict: Verdict,
        evidence: list[dict[str, Any]],
        reasoning: str,
        tool_calls_count: int,
        cost_usd: float = 0.0,
        verified_at: Optional[str] = None,
    ):
        self.verification_id = str(uuid4())
        self.task_id = task_id
        self.step_id = step_id
        self.step_index = step_index
        self.verdict = verdict
        self.evidence = evidence
        self.reasoning = reasoning
        self.tool_calls_count = tool_calls_count
        self.cost_usd = cost_usd
        self.verified_at = verified_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "verification_id": self.verification_id,
            "task_id": self.task_id,
            "step_id": self.step_id,
            "step_index": self.step_index,
            "verdict": self.verdict.value,
            "evidence": self.evidence,
            "reasoning": self.reasoning,
            "tool_calls_count": self.tool_calls_count,
            "cost_usd": self.cost_usd,
            "verified_at": self.verified_at,
        }


# ── Core Verification Logic ─────────────────────────────────────────


class ExecutionVerifier:
    """
    Post-execution verifier for the Task Planner.

    Analyzes step results to determine if real execution happened,
    not just LLM text generation pretending to have done work.

    Usage:
        verifier = ExecutionVerifier(db=supabase_client)
        result = await verifier.verify_step(
            plan_id="...",
            step=task_step,
            tool_call_history=[(tool_name, args_hash), ...],
            step_tool_calls=5,
            final_response="...",
        )
        if result.verdict == Verdict.SUCCESS:
            step.status = StepStatus.DONE
        elif result.verdict == Verdict.CONTINUE:
            # Re-execute with more guidance
        elif result.verdict == Verdict.PIVOT:
            # Trigger plan revision
    """

    def __init__(self, db: Any = None):
        self._db = db
        self._total_verifications = 0
        self._verdicts_count = {v: 0 for v in Verdict}

    async def verify_step(
        self,
        plan_id: str,
        step_id: str,
        step_index: int,
        step_description: str,
        tool_call_history: list[tuple[str, str]],
        step_tool_calls: int,
        final_response: str,
        plan_total_tool_calls: int = 0,
    ) -> VerificationResult:
        """
        Verify whether a step actually executed or just pretended to.

        This is the core SP5 logic. It runs three checks:
        1. Structural check: Were tools actually called?
        2. Evidence extraction: What concrete outputs exist?
        3. Semantic check: Does the response match the objective?

        Returns a VerificationResult with verdict and evidence.
        """
        start_time = time.monotonic()
        evidence: list[dict[str, Any]] = []
        cost_usd = 0.0

        logger.info(
            "verification_start",
            plan_id=plan_id,
            step_index=step_index,
            tool_calls=step_tool_calls,
            response_len=len(final_response),
        )

        # ── Check 1: Structural — Were tools actually called? ────────
        structural_pass = step_tool_calls >= MIN_TOOL_CALLS_FOR_SUCCESS

        if not structural_pass:
            # CRITICAL: No tools were called. This is the exact ACI bug.
            # A step that claims completion without tool execution is suspect.
            logger.warning(
                "verification_no_tools",
                plan_id=plan_id,
                step_index=step_index,
                tool_calls=step_tool_calls,
                description=step_description[:100],
            )

        # ── Check 2: Evidence Extraction ─────────────────────────────
        evidence = self._extract_evidence(
            tool_call_history=tool_call_history,
            final_response=final_response,
            step_tool_calls=step_tool_calls,
        )

        has_concrete_evidence = any(e["type"] != EvidenceType.NONE.value for e in evidence)

        # ── Check 3: Semantic — Does the response match the objective? ──
        # Only use LLM verification for ambiguous cases (tools called but
        # unclear if they achieved the objective). For clear cases
        # (no tools = CONTINUE, tools + evidence = SUCCESS), skip LLM.
        semantic_verdict = None
        if structural_pass and has_concrete_evidence:
            # Clear SUCCESS — tools called + evidence exists
            semantic_verdict = Verdict.SUCCESS
        elif not structural_pass and not has_concrete_evidence:
            # Clear CONTINUE — nothing happened
            semantic_verdict = Verdict.CONTINUE
        else:
            # Ambiguous — use LLM to judge
            semantic_verdict, llm_reasoning, llm_cost = await self._semantic_verify(
                step_description=step_description,
                final_response=final_response,
                tool_call_history=tool_call_history,
                step_tool_calls=step_tool_calls,
                evidence=evidence,
            )
            cost_usd += llm_cost
            evidence.append(
                {
                    "type": "llm_verification",
                    "reasoning": llm_reasoning,
                    "model": VERIFIER_MODEL,
                }
            )

        # ── Check for PIVOT signals ──────────────────────────────────
        # If the response contains explicit failure signals, override to PIVOT
        pivot_signals = [
            "[STUCK]",
            "[CAP]",
            "no se puede",
            "imposible",
            "error irrecuperable",
            "approach is wrong",
            "need to change strategy",
        ]
        response_lower = final_response.lower()
        for signal in pivot_signals:
            if signal.lower() in response_lower:
                semantic_verdict = Verdict.PIVOT
                evidence.append(
                    {
                        "type": "pivot_signal",
                        "signal": signal,
                        "context": final_response[:200],
                    }
                )
                break

        # ── Build reasoning ──────────────────────────────────────────
        elapsed_ms = (time.monotonic() - start_time) * 1000
        reasoning = self._build_reasoning(
            structural_pass=structural_pass,
            has_evidence=has_concrete_evidence,
            verdict=semantic_verdict,
            step_tool_calls=step_tool_calls,
            evidence_count=len(evidence),
            elapsed_ms=elapsed_ms,
        )

        result = VerificationResult(
            task_id=plan_id,
            step_id=step_id,
            step_index=step_index,
            verdict=semantic_verdict,
            evidence=evidence,
            reasoning=reasoning,
            tool_calls_count=step_tool_calls,
            cost_usd=cost_usd,
        )

        # ── Persist to Supabase ──────────────────────────────────────
        await self._persist_result(result)

        # ── Update stats ─────────────────────────────────────────────
        self._total_verifications += 1
        self._verdicts_count[semantic_verdict] += 1

        logger.info(
            "verification_complete",
            plan_id=plan_id,
            step_index=step_index,
            verdict=semantic_verdict.value,
            tool_calls=step_tool_calls,
            evidence_count=len(evidence),
            cost_usd=cost_usd,
            elapsed_ms=f"{elapsed_ms:.0f}",
        )

        return result

    def _extract_evidence(
        self,
        tool_call_history: list[tuple[str, str]],
        final_response: str,
        step_tool_calls: int,
    ) -> list[dict[str, Any]]:
        """
        Extract concrete evidence from tool call history and response.

        Maps tool names to evidence types and extracts relevant signals
        from the response text.
        """
        evidence: list[dict[str, Any]] = []

        # Map tool names to evidence types
        tool_evidence_map = {
            "web_search": EvidenceType.SEARCH_RESULTS,
            "browse_web": EvidenceType.API_RESPONSE,
            "code_exec": EvidenceType.CODE_EXECUTED,
            "github": EvidenceType.FILE_CREATED,
            "send_message": EvidenceType.MESSAGE_SENT,
            "manus_bridge": EvidenceType.MANUS_DELEGATED,
            "query_knowledge": EvidenceType.TOOL_OUTPUT,
            "ingest_knowledge": EvidenceType.KNOWLEDGE_STORED,
            "consult_sabios": EvidenceType.TOOL_OUTPUT,
            "web_dev": EvidenceType.FILE_CREATED,
            "file_ops": EvidenceType.FILE_CREATED,
        }

        # Extract evidence from tool call history
        tools_used = set()
        for tool_name, args_hash in tool_call_history:
            evidence_type = tool_evidence_map.get(tool_name, EvidenceType.TOOL_OUTPUT)
            tools_used.add(tool_name)
            evidence.append(
                {
                    "type": evidence_type.value,
                    "tool": tool_name,
                    "args_hash": args_hash,
                }
            )

        # If no tools were called, add NONE evidence
        if not evidence:
            evidence.append(
                {
                    "type": EvidenceType.NONE.value,
                    "reason": "No tools were called during step execution",
                }
            )

        # Add summary evidence
        evidence.append(
            {
                "type": "summary",
                "total_tool_calls": step_tool_calls,
                "unique_tools": list(tools_used),
                "response_length": len(final_response),
            }
        )

        return evidence

    async def _semantic_verify(
        self,
        step_description: str,
        final_response: str,
        tool_call_history: list[tuple[str, str]],
        step_tool_calls: int,
        evidence: list[dict[str, Any]],
    ) -> tuple[Verdict, str, float]:
        """
        Use LLM to verify if the step result matches the objective.

        Only called for ambiguous cases where structural checks alone
        can't determine the verdict.

        Returns: (verdict, reasoning, cost_usd)
        """
        import asyncio

        prompt = (
            "Eres un verificador de ejecución autónoma. "
            "Tu trabajo es determinar si un paso de un plan "
            "realmente se ejecutó o solo se simuló con texto."
        )
        prompt += f"""

PASO A VERIFICAR:
Descripción: {step_description}

EVIDENCIA:
- Herramientas llamadas: {step_tool_calls}
- Herramientas usadas: {[t[0] for t in tool_call_history]}
- Respuesta del agente (primeros 500 chars): {final_response[:500]}

REGLAS DE VERIFICACIÓN:
1. Si tool_calls > 0 Y la respuesta describe resultados concretos de esas herramientas → SUCCESS
2. Si tool_calls = 0 PERO la respuesta es una reflexión válida que no requería herramientas → SUCCESS
3. Si tool_calls > 0 PERO la respuesta no refleja los resultados esperados → CONTINUE
4. Si tool_calls = 0 Y el paso claramente requería acción → CONTINUE
5. Si hay señales de que el enfoque es fundamentalmente incorrecto → PIVOT

Responde SOLO con un JSON:
{{"verdict": "success|continue|pivot", "reasoning": "explicación concisa de máximo 100 palabras"}}"""

        try:
            import openai

            client = openai.AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

            resp = await asyncio.wait_for(
                client.chat.completions.create(
                    model=VERIFIER_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.0,
                    response_format={"type": "json_object"},
                ),
                timeout=VERIFIER_TIMEOUT_S,
            )

            result_text = resp.choices[0].message.content or "{}"
            result_json = json.loads(result_text)

            verdict_str = result_json.get("verdict", "continue").lower()
            reasoning = result_json.get("reasoning", "No reasoning provided")

            # Map string to Verdict enum
            verdict_map = {
                "success": Verdict.SUCCESS,
                "continue": Verdict.CONTINUE,
                "pivot": Verdict.PIVOT,
            }
            verdict = verdict_map.get(verdict_str, Verdict.CONTINUE)

            # Estimate cost: gpt-5.5 ~$2/M input + $8/M output
            tokens = (resp.usage.prompt_tokens or 0) + (resp.usage.completion_tokens or 0)
            cost = tokens * 0.000005  # rough average

            return verdict, reasoning, cost

        except Exception as e:
            logger.warning(
                "semantic_verify_failed",
                error=str(e),
            )
            # On failure, default to CONTINUE (conservative)
            return Verdict.CONTINUE, f"Verification failed: {str(e)[:100]}", 0.0

    def _build_reasoning(
        self,
        structural_pass: bool,
        has_evidence: bool,
        verdict: Verdict,
        step_tool_calls: int,
        evidence_count: int,
        elapsed_ms: float,
    ) -> str:
        """Build human-readable reasoning for the verification result."""
        parts = []

        if structural_pass:
            parts.append(f"Structural: PASS ({step_tool_calls} tool calls)")
        else:
            parts.append(f"Structural: FAIL (0 tool calls, minimum required: {MIN_TOOL_CALLS_FOR_SUCCESS})")

        if has_evidence:
            parts.append(f"Evidence: {evidence_count} items found")
        else:
            parts.append("Evidence: NONE")

        parts.append(f"Verdict: {verdict.value.upper()}")
        parts.append(f"Verification time: {elapsed_ms:.0f}ms")

        return " | ".join(parts)

    async def _persist_result(self, result: VerificationResult) -> None:
        """Persist verification result to Supabase."""
        if not self._db:
            logger.debug("verification_persist_skipped", reason="no_db")
            return

        try:
            row = {
                "verification_id": result.verification_id,
                "task_id": result.task_id,
                "step_id": result.step_id,
                "step_index": result.step_index,
                "verdict": result.verdict.value,
                "evidence": json.dumps(result.evidence, ensure_ascii=False),
                "reasoning": result.reasoning,
                "tool_calls_count": result.tool_calls_count,
                "cost_usd": result.cost_usd,
                "verified_at": result.verified_at,
            }
            await self._db.insert("verification_results", row)
            logger.info(
                "verification_persisted",
                verification_id=result.verification_id,
                task_id=result.task_id,
                step_index=result.step_index,
            )
        except Exception as e:
            logger.warning(
                "verification_persist_failed",
                error=str(e),
                verification_id=result.verification_id,
            )

    def get_stats(self) -> dict[str, Any]:
        """Return verification statistics."""
        return {
            "total_verifications": self._total_verifications,
            "verdicts": {v.value: self._verdicts_count[v] for v in Verdict},
            "success_rate": (
                self._verdicts_count[Verdict.SUCCESS] / self._total_verifications
                if self._total_verifications > 0
                else 0.0
            ),
        }


# ── Singleton ────────────────────────────────────────────────────────

_verifier: Optional[ExecutionVerifier] = None


def get_verifier() -> Optional[ExecutionVerifier]:
    """Get the global ExecutionVerifier instance."""
    return _verifier


def init_verifier(db: Any = None) -> ExecutionVerifier:
    """Initialize the global ExecutionVerifier."""
    global _verifier
    _verifier = ExecutionVerifier(db=db)
    logger.info("execution_verifier_initialized")
    return _verifier
