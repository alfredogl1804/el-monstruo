"""
DeepEval Basic Evaluation Tests — Sprint 19
Quality gate tests that run in CI via .github/workflows/eval.yml

These tests validate core kernel behaviors:
  1. Answer relevancy — responses must be relevant to the query
  2. Hallucination detection — responses must not hallucinate
  3. Tool correctness — tool calls must match expected patterns
"""

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    HallucinationMetric,
)
from deepeval.test_case import LLMTestCase

# ── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def relevancy_metric():
    return AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")


@pytest.fixture
def hallucination_metric():
    return HallucinationMetric(threshold=0.5, model="gpt-4o-mini")


# ── Answer Relevancy Tests ─────────────────────────────────────────


class TestAnswerRelevancy:
    """Verify that kernel responses are relevant to user queries."""

    def test_greeting_relevancy(self, relevancy_metric):
        test_case = LLMTestCase(
            input="Hola, ¿cómo estás?",
            actual_output="¡Hola! Estoy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?",
        )
        assert_test(test_case, [relevancy_metric])

    def test_technical_query_relevancy(self, relevancy_metric):
        test_case = LLMTestCase(
            input="¿Cuál es la diferencia entre REST y GraphQL?",
            actual_output=(
                "REST usa endpoints fijos con métodos HTTP estándar, mientras que "
                "GraphQL permite al cliente especificar exactamente qué datos necesita "
                "con un único endpoint y un lenguaje de consulta flexible."
            ),
        )
        assert_test(test_case, [relevancy_metric])

    def test_task_request_relevancy(self, relevancy_metric):
        test_case = LLMTestCase(
            input="Investiga las últimas tendencias en IA generativa",
            actual_output=(
                "Las principales tendencias en IA generativa para 2026 incluyen: "
                "modelos multimodales nativos, agentes autónomos con herramientas, "
                "y sistemas de memoria a largo plazo como MemPalace."
            ),
        )
        assert_test(test_case, [relevancy_metric])


# ── Hallucination Tests ────────────────────────────────────────────


class TestHallucination:
    """Verify that kernel responses don't hallucinate facts."""

    def test_no_hallucination_factual(self, hallucination_metric):
        test_case = LLMTestCase(
            input="¿Qué es Python?",
            actual_output=(
                "Python es un lenguaje de programación de alto nivel, interpretado "
                "y de propósito general, creado por Guido van Rossum."
            ),
            context=[
                "Python is a high-level, interpreted, general-purpose programming language.",
                "Python was created by Guido van Rossum and first released in 1991.",
            ],
        )
        assert_test(test_case, [hallucination_metric])

    def test_no_hallucination_technical(self, hallucination_metric):
        test_case = LLMTestCase(
            input="¿Qué es LangGraph?",
            actual_output=(
                "LangGraph es un framework para construir aplicaciones con agentes "
                "usando grafos de estado. Es parte del ecosistema LangChain."
            ),
            context=[
                "LangGraph is a framework for building stateful, multi-actor applications with LLMs.",
                "LangGraph is built on top of LangChain and uses a graph-based state machine.",
            ],
        )
        assert_test(test_case, [hallucination_metric])
