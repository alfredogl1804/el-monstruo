"""
El Monstruo — Ragas RAG Evaluation Configuration (Sprint 16)
============================================================
Configures Ragas v0.4.3 for evaluating RAG pipeline quality.
Metrics: faithfulness, answer_relevancy, context_precision, context_recall.

Usage:
    python -m evaluation.ragas_config --run

Requires: pip install ragas==0.4.3

DEFERRED Sprint 29+: ragflow evaluation (78K+ stars). LightRAG covers current needs.
    as complement/replacement for the RAG knowledge engine.
    ragflow provides a more robust end-to-end RAG pipeline.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RagasConfig:
    """Configuration for Ragas evaluation runs."""

    # Metrics to evaluate
    metrics: list[str] = field(
        default_factory=lambda: [
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall",
        ]
    )

    # LLM for evaluation (uses same key as kernel)
    eval_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # Thresholds for pass/fail
    thresholds: dict = field(
        default_factory=lambda: {
            "faithfulness": 0.7,
            "answer_relevancy": 0.7,
            "context_precision": 0.6,
            "context_recall": 0.6,
        }
    )

    # Output path
    output_dir: str = "evaluation/results"

    def to_dict(self) -> dict:
        return {
            "metrics": self.metrics,
            "eval_model": self.eval_model,
            "embedding_model": self.embedding_model,
            "thresholds": self.thresholds,
            "output_dir": self.output_dir,
        }


# Sample test dataset for RAG evaluation
RAGAS_TEST_CASES = [
    {
        "question": "¿Cuáles son las misiones activas de Alfredo?",
        "contexts": [
            "Alfredo tiene 3 misiones activas: Sprint 15 del Monstruo, CIP tokenización, y TicketLike operaciones."
        ],
        "ground_truth": "Las misiones activas son Sprint 15 del Monstruo, CIP tokenización, y TicketLike operaciones.",
    },
    {
        "question": "¿Qué herramientas tiene disponible El Monstruo?",
        "contexts": [
            "El Monstruo tiene acceso a: búsqueda web, ejecución de código, gestión de archivos, base de datos Supabase, y APIs de múltiples LLMs."  # noqa: E501
        ],
        "ground_truth": "El Monstruo tiene búsqueda web, ejecución de código, gestión de archivos, Supabase, y APIs de LLMs.",  # noqa: E501
    },
    {
        "question": "¿Cuál es el presupuesto diario del kernel?",
        "contexts": [
            "El FinOps Soberano establece un hard limit de $5.00 USD diarios para el kernel, con alertas al 80% ($4.00)."  # noqa: E501
        ],
        "ground_truth": "El presupuesto diario es $5.00 USD con alertas al 80%.",
    },
    {
        "question": "¿Qué modelo de IA usa el kernel por defecto?",
        "contexts": [
            "El router del kernel usa GPT-4o como modelo principal con fallback a GPT-4o-mini para tareas simples."
        ],
        "ground_truth": "GPT-4o como principal con fallback a GPT-4o-mini.",
    },
    {
        "question": "¿Cómo funciona el sistema de alertas?",
        "contexts": [
            "El sistema de Alertas Soberanas monitorea 5 tipos: cost_spike, error_rate, latency_spike, eval_failure, health_down. Las alertas se envían a Telegram vía @MounstroOC_bot."  # noqa: E501
        ],
        "ground_truth": "Monitorea 5 tipos de alertas y las envía a Telegram vía @MounstroOC_bot.",
    },
]


async def run_ragas_evaluation(
    config: Optional[RagasConfig] = None,
    test_cases: Optional[list] = None,
) -> dict:
    """
    Run Ragas evaluation on test cases.
    Returns evaluation results with per-metric scores.
    """
    config = config or RagasConfig()
    test_cases = test_cases or RAGAS_TEST_CASES

    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )

        # Build dataset
        dataset = Dataset.from_dict(
            {
                "question": [tc["question"] for tc in test_cases],
                "contexts": [tc["contexts"] for tc in test_cases],
                "ground_truth": [tc["ground_truth"] for tc in test_cases],
                "answer": [tc.get("answer", "") for tc in test_cases],
            }
        )

        # Select metrics
        metric_map = {
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
            "context_precision": context_precision,
            "context_recall": context_recall,
        }
        selected_metrics = [metric_map[m] for m in config.metrics if m in metric_map]

        # Run evaluation
        result = evaluate(dataset, metrics=selected_metrics)

        # Check thresholds
        passed = True
        details = {}
        for metric_name, threshold in config.thresholds.items():
            score = result.get(metric_name, 0)
            metric_passed = score >= threshold
            details[metric_name] = {
                "score": round(score, 4),
                "threshold": threshold,
                "passed": metric_passed,
            }
            if not metric_passed:
                passed = False

        output = {
            "status": "passed" if passed else "failed",
            "metrics": details,
            "config": config.to_dict(),
            "num_test_cases": len(test_cases),
        }

        # Save results
        os.makedirs(config.output_dir, exist_ok=True)
        output_path = os.path.join(config.output_dir, "ragas_results.json")
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)

        return output

    except ImportError:
        return {
            "status": "skipped",
            "error": "ragas not installed. Run: pip install ragas==0.2.16",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(run_ragas_evaluation())
    print(json.dumps(result, indent=2))
