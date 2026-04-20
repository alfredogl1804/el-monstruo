#!/usr/bin/env python3.11
"""
cidp_calibrator.py — Calibración de Sabios.

Benchmark interno de capacidades reales de cada modelo.
Los roles se asignan por benchmark, no por reputación.
Recalibra semanalmente o bajo demanda.
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

SKILL_DIR = Path(__file__).parent.parent
CALIBRATION_PATH = SKILL_DIR / "data" / "calibration_results.json"

# Calibration challenges
CHALLENGES = {
    "code_generation": {
        "prompt": "Write a Python function that implements a thread-safe LRU cache with TTL support. Include type hints and docstrings. Respond with ONLY the code, no explanations.",  # noqa: E501
        "eval_criteria": [
            "has_class_or_function",
            "has_type_hints",
            "has_docstring",
            "handles_threading",
        ],
    },
    "architecture_design": {
        "prompt": "Design a microservice architecture for a real-time collaborative document editor supporting 10K concurrent users. Respond with a structured JSON describing services, communication patterns, and data stores.",  # noqa: E501
        "eval_criteria": [
            "has_services",
            "has_communication",
            "has_data_stores",
            "addresses_scalability",
        ],
    },
    "factual_accuracy": {
        "prompt": "What are the current (April 2026) top 3 most used JavaScript frameworks for web development, their latest stable versions, and their key differentiators? Respond with JSON.",  # noqa: E501
        "eval_criteria": [
            "names_frameworks",
            "includes_versions",
            "includes_differentiators",
        ],
    },
    "adversarial_review": {
        "prompt": "Review this architecture decision: 'We chose MongoDB as our primary database for a banking application handling millions of daily transactions.' Identify all potential issues, risks, and suggest alternatives. Respond with JSON.",  # noqa: E501
        "eval_criteria": [
            "identifies_acid_issues",
            "mentions_alternatives",
            "quantifies_risks",
        ],
    },
    "optimization": {
        "prompt": "Given a Python function that processes 1M records from a CSV file, identify 5 specific optimizations that would reduce processing time by at least 10x. Provide before/after code snippets. Respond with JSON.",  # noqa: E501
        "eval_criteria": [
            "has_optimizations",
            "has_code_snippets",
            "quantifies_improvement",
        ],
    },
}


def _simple_eval(response_text: str, criteria: list) -> float:
    """Simple heuristic evaluation of response quality."""
    score = 0.0
    text_lower = response_text.lower()

    # Length check (meaningful response)
    if len(response_text) > 200:
        score += 0.2
    if len(response_text) > 500:
        score += 0.1

    # JSON parseable
    try:
        json.loads(response_text)
        score += 0.2
    except json.JSONDecodeError:
        import re

        if re.search(r"\{[\s\S]*\}", response_text):
            score += 0.1

    # Criteria-based scoring
    criteria_score = 0
    for criterion in criteria:
        # Convert criterion to keywords
        keywords = criterion.replace("_", " ").split()
        if any(kw in text_lower for kw in keywords):
            criteria_score += 1

    if criteria:
        score += 0.5 * (criteria_score / len(criteria))

    return min(score, 1.0)


async def calibrate_sabio(sabio_id: str) -> dict:
    """Calibrate a single sabio across all challenges."""
    results = {}
    total_score = 0.0
    total_time = 0.0

    for challenge_id, challenge in CHALLENGES.items():
        start = time.time()
        try:
            response = await consultar_sabio(sabio_id, challenge["prompt"])
            elapsed = time.time() - start
            text = response.get("respuesta", "")

            score = _simple_eval(text, challenge["eval_criteria"])
            results[challenge_id] = {
                "score": score,
                "response_length": len(text),
                "elapsed_seconds": elapsed,
                "status": "completed",
            }
            total_score += score
            total_time += elapsed

        except Exception as e:
            elapsed = time.time() - start
            results[challenge_id] = {
                "score": 0,
                "error": str(e),
                "elapsed_seconds": elapsed,
                "status": "failed",
            }
            total_time += elapsed

    avg_score = total_score / len(CHALLENGES) if CHALLENGES else 0

    return {
        "sabio_id": sabio_id,
        "avg_score": avg_score,
        "total_time_seconds": total_time,
        "challenges": results,
        "calibrated_at": datetime.now().isoformat(),
    }


async def run_full_calibration() -> dict:
    """Run calibration for all sabios."""
    sabios = ["gpt54", "claude", "gemini", "grok", "deepseek", "perplexity"]
    results = {}

    print("  Calibrating sabios...")
    for sabio_id in sabios:
        print(f"    Calibrating {sabio_id}...")
        results[sabio_id] = await calibrate_sabio(sabio_id)
        print(f"    {sabio_id}: avg_score={results[sabio_id]['avg_score']:.2f}")

    # Save
    CALIBRATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CALIBRATION_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return results


def needs_recalibration(interval_hours: int = 168) -> bool:
    """Check if recalibration is needed."""
    if not CALIBRATION_PATH.exists():
        return True

    try:
        with open(CALIBRATION_PATH, "r") as f:
            data = json.load(f)

        # Check any sabio's calibration date
        for sabio_data in data.values():
            cal_date = sabio_data.get("calibrated_at", "")
            if cal_date:
                cal_dt = datetime.fromisoformat(cal_date)
                if datetime.now() - cal_dt > timedelta(hours=interval_hours):
                    return True
                return False
    except Exception:
        return True

    return True


def get_best_sabio_for(capability: str) -> str:
    """Get the best sabio for a specific capability based on calibration."""
    if not CALIBRATION_PATH.exists():
        # Default assignments
        defaults = {
            "code_generation": "deepseek",
            "architecture_design": "claude",
            "factual_accuracy": "perplexity",
            "adversarial_review": "grok",
            "optimization": "deepseek",
        }
        return defaults.get(capability, "gpt54")

    with open(CALIBRATION_PATH, "r") as f:
        data = json.load(f)

    best_sabio = "gpt54"
    best_score = 0

    for sabio_id, sabio_data in data.items():
        challenges = sabio_data.get("challenges", {})
        if capability in challenges:
            score = challenges[capability].get("score", 0)
            if score > best_score:
                best_score = score
                best_sabio = sabio_id

    return best_sabio


if __name__ == "__main__":
    asyncio.run(run_full_calibration())
