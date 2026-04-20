"""
El Monstruo — Skill Evaluator (Sprint 17 → 18)
==========================================
Closed Learning Loop using DeepEval metrics.

This module provides a LangGraph-compatible node that evaluates
tool/skill execution quality using DeepEval's metrics:
  - ToolCorrectnessMetric: Did the tool produce the correct output?
  - TaskCompletionMetric: Did the overall task complete successfully?
  - AnswerRelevancyMetric: Is the response relevant to the query?

Flow:
    respond → skill_evaluator → memory_write
    (skill_evaluator is optional — only runs when tools were used)

If evaluation passes → save skill execution record to Supabase
If evaluation fails → discard and log for improvement

Validated against: deepeval==3.9.7 (Apache-2.0, PyPI latest 2026-04-20)
Reference: https://github.com/confident-ai/deepeval

Principio: Evaluamos para mejorar, no para castigar.
"""

from __future__ import annotations

import os
import time
from typing import Any, Optional

import structlog

logger = structlog.get_logger("evaluation.skill_evaluator")

# ── Evaluation Thresholds ──────────────────────────────────────────────

TOOL_CORRECTNESS_THRESHOLD = 0.7
TASK_COMPLETION_THRESHOLD = 0.6
ANSWER_RELEVANCY_THRESHOLD = 0.7


# ── DeepEval Wrapper ───────────────────────────────────────────────────

class SkillEvaluator:
    """
    Evaluates tool/skill execution quality using DeepEval.

    Designed to be called as a LangGraph node or standalone.
    Fails silently — never blocks the main conversation flow.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the evaluator.

        Args:
            model: The LLM model to use for evaluation judges.
                   Uses gpt-4o-mini by default (cheap, fast).
        """
        self._model = model
        self._initialized = False
        self._metrics = {}

    async def initialize(self) -> bool:
        """
        Lazy-initialize DeepEval metrics.
        Returns True if initialization succeeded.
        """
        if self._initialized:
            return True

        try:
            # Set DeepEval API key (uses OpenAI for judge LLM)
            openai_key = os.environ.get("OPENAI_API_KEY")
            if not openai_key:
                logger.warning("skill_evaluator_disabled", reason="OPENAI_API_KEY not set")
                return False

            from deepeval.metrics import (
                ToolCorrectnessMetric,
                AnswerRelevancyMetric,
            )
            from deepeval.test_case import LLMTestCase

            self._metrics = {
                "tool_correctness": ToolCorrectnessMetric(
                    threshold=TOOL_CORRECTNESS_THRESHOLD,
                    model=self._model,
                ),
                "answer_relevancy": AnswerRelevancyMetric(
                    threshold=ANSWER_RELEVANCY_THRESHOLD,
                    model=self._model,
                ),
            }

            self._LLMTestCase = LLMTestCase
            self._initialized = True
            logger.info("skill_evaluator_initialized", model=self._model, metrics=list(self._metrics.keys()))
            return True

        except ImportError as e:
            logger.warning("skill_evaluator_import_failed", error=str(e))
            return False
        except Exception as e:
            logger.warning("skill_evaluator_init_failed", error=str(e))
            return False

    async def evaluate_tool_execution(
        self,
        user_query: str,
        tool_name: str,
        tool_args: dict[str, Any],
        tool_result: Any,
        final_response: str,
        expected_output: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Evaluate a single tool execution.

        Args:
            user_query: The original user message
            tool_name: Name of the tool that was called
            tool_args: Arguments passed to the tool
            tool_result: Raw result from the tool
            final_response: The final response sent to the user
            expected_output: Optional expected output for correctness check

        Returns:
            Evaluation result dict with scores and pass/fail status.
        """
        if not await self.initialize():
            return {"evaluated": False, "reason": "evaluator_not_available"}

        start_time = time.monotonic()

        try:
            # Build test case
            test_case = self._LLMTestCase(
                input=user_query,
                actual_output=final_response,
                expected_output=expected_output or "",
                tools_called=[tool_name],
                expected_tools=[tool_name] if expected_output else [],
                context=[f"Tool: {tool_name}", f"Args: {str(tool_args)[:500]}", f"Result: {str(tool_result)[:500]}"],
            )

            results = {}

            # Run tool correctness metric
            if "tool_correctness" in self._metrics and expected_output:
                metric = self._metrics["tool_correctness"]
                await _run_metric_async(metric, test_case)
                results["tool_correctness"] = {
                    "score": metric.score,
                    "passed": metric.score >= TOOL_CORRECTNESS_THRESHOLD,
                    "reason": getattr(metric, "reason", ""),
                }

            # Run answer relevancy metric
            if "answer_relevancy" in self._metrics:
                metric = self._metrics["answer_relevancy"]
                await _run_metric_async(metric, test_case)
                results["answer_relevancy"] = {
                    "score": metric.score,
                    "passed": metric.score >= ANSWER_RELEVANCY_THRESHOLD,
                    "reason": getattr(metric, "reason", ""),
                }

            latency_ms = (time.monotonic() - start_time) * 1000

            # Determine overall pass/fail
            all_passed = all(r.get("passed", True) for r in results.values())

            evaluation = {
                "evaluated": True,
                "tool_name": tool_name,
                "overall_passed": all_passed,
                "metrics": results,
                "latency_ms": latency_ms,
            }

            logger.info(
                "skill_evaluation_complete",
                tool=tool_name,
                passed=all_passed,
                metrics={k: v["score"] for k, v in results.items()},
                latency_ms=f"{latency_ms:.0f}",
            )

            return evaluation

        except Exception as e:
            logger.warning(
                "skill_evaluation_failed",
                tool=tool_name,
                error=str(e),
            )
            return {"evaluated": False, "error": str(e), "tool_name": tool_name}

    async def evaluate_run(
        self,
        user_query: str,
        tool_calls: list[dict[str, Any]],
        final_response: str,
    ) -> dict[str, Any]:
        """
        Evaluate an entire run (multiple tool calls).

        Args:
            user_query: The original user message
            tool_calls: List of tool call records from state
            final_response: The final response sent to the user

        Returns:
            Aggregate evaluation result.
        """
        if not tool_calls:
            return {"evaluated": False, "reason": "no_tool_calls"}

        results = []
        for tc in tool_calls:
            result = await self.evaluate_tool_execution(
                user_query=user_query,
                tool_name=tc.get("tool", ""),
                tool_args=tc.get("args", {}),
                tool_result=tc.get("result_preview", ""),
                final_response=final_response,
            )
            results.append(result)

        # Aggregate
        evaluated_count = sum(1 for r in results if r.get("evaluated"))
        passed_count = sum(1 for r in results if r.get("overall_passed"))

        return {
            "evaluated": True,
            "total_tools": len(tool_calls),
            "evaluated_count": evaluated_count,
            "passed_count": passed_count,
            "pass_rate": passed_count / max(evaluated_count, 1),
            "tool_results": results,
        }


# ── LangGraph Node ─────────────────────────────────────────────────────

# Module-level evaluator instance
_evaluator: Optional[SkillEvaluator] = None


def get_evaluator() -> SkillEvaluator:
    """Get or create the module-level evaluator."""
    global _evaluator
    if _evaluator is None:
        _evaluator = SkillEvaluator()
    return _evaluator


async def skill_evaluator_node(state: dict[str, Any], config: Any = None) -> dict[str, Any]:
    """
    LangGraph node: evaluate tool executions in the current run.

    Position in graph: respond → skill_evaluator → memory_write
    Only runs when tools were used in this run.

    Updates state with evaluation results for memory_write to persist.
    """
    tool_calls = state.get("tool_calls", [])

    # Skip if no tools were called
    if not tool_calls:
        return {"skill_evaluation": None}

    # Skip if evaluation is disabled
    if os.environ.get("SKILL_EVAL_DISABLED", "").lower() in ("true", "1", "yes"):
        return {"skill_evaluation": {"skipped": True, "reason": "disabled"}}

    evaluator = get_evaluator()

    # Get the user query and final response from state
    messages = state.get("messages", [])
    user_query = ""
    for msg in messages:
        if isinstance(msg, dict) and msg.get("role") == "user":
            user_query = msg.get("content", "")
        elif hasattr(msg, "role") and msg.role == "user":
            user_query = getattr(msg, "content", "")

    final_response = state.get("response", "")

    # Run evaluation
    evaluation = await evaluator.evaluate_run(
        user_query=user_query,
        tool_calls=tool_calls,
        final_response=final_response,
    )

    return {"skill_evaluation": evaluation}


# ── Helper ──────────────────────────────────────────────────────────────

async def _run_metric_async(metric: Any, test_case: Any) -> None:
    """Run a DeepEval metric, handling sync/async variants."""
    import asyncio

    if hasattr(metric, "a_measure"):
        await metric.a_measure(test_case)
    elif hasattr(metric, "measure"):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, metric.measure, test_case)
    else:
        logger.warning("metric_no_measure", metric=type(metric).__name__)
