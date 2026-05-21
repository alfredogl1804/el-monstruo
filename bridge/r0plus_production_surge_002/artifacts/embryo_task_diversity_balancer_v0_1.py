"""
Embryo Task Diversity Balancer v0.1

Reduces task over-specialization in embryos by analyzing run history,
counting task diversity, detecting excessive repetition, calculating
diversity scores, and proposing scoring adjustments.

Never forces a task. Never skips Dispatcher. Generates R0+ recommendations only.

No external API calls. No state modification. Pure local computation.

Usage:
    python3 embryo_task_diversity_balancer_v0_1.py [--base-dir /path]
"""
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def load_run_history(base_dir: Path) -> dict:
    """Load embryo run history from outputs and Memory Palace."""
    runs = {"oracle": [], "auditor": []}

    # Read embryo output files
    embryo_output_dir = base_dir / "bridge" / "embryos_output"
    if embryo_output_dir.exists():
        for f in sorted(embryo_output_dir.iterdir()):
            if f.suffix == ".json":
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    embryo_type = "oracle" if "oracle" in f.name else "auditor" if "auditor" in f.name else None
                    if embryo_type:
                        runs[embryo_type].append({
                            "file": f.name,
                            "task": data.get("task_selected", data.get("task", "unknown")),
                            "timestamp": data.get("timestamp", ""),
                        })
                except (json.JSONDecodeError, IOError):
                    continue

    # Read Memory Palace for task entries
    mp_path = base_dir / "embryos" / "memory_palace" / "memory_palace_state.json"
    if mp_path.exists():
        try:
            mp_data = json.loads(mp_path.read_text(encoding="utf-8"))
            for entry in mp_data.get("entries", []):
                embryo_id = entry.get("embryo_id", "")
                task = entry.get("task_selected", entry.get("task", "unknown"))
                if "oracle" in embryo_id:
                    runs["oracle"].append({"task": task, "source": "memory_palace"})
                elif "auditor" in embryo_id:
                    runs["auditor"].append({"task": task, "source": "memory_palace"})
        except (json.JSONDecodeError, IOError):
            pass

    return runs


def count_task_diversity(runs: list) -> dict:
    """Count unique tasks and their frequencies."""
    if not runs:
        return {"unique_tasks": 0, "total_runs": 0, "frequencies": {}, "most_common": None}

    tasks = [r.get("task", "unknown") for r in runs]
    counter = Counter(tasks)
    most_common = counter.most_common(1)[0] if counter else None

    return {
        "unique_tasks": len(counter),
        "total_runs": len(tasks),
        "frequencies": dict(counter),
        "most_common": {"task": most_common[0], "count": most_common[1]} if most_common else None,
    }


def detect_excessive_repetition(diversity: dict, threshold: float = 0.5) -> dict:
    """Detect if any single task dominates more than threshold of total runs."""
    if diversity["total_runs"] == 0:
        return {"detected": False, "dominant_task": None, "ratio": 0}

    most_common = diversity.get("most_common")
    if not most_common:
        return {"detected": False, "dominant_task": None, "ratio": 0}

    ratio = most_common["count"] / diversity["total_runs"]
    return {
        "detected": ratio > threshold,
        "dominant_task": most_common["task"],
        "ratio": round(ratio, 4),
        "threshold": threshold,
    }


def calculate_diversity_score(diversity: dict) -> float:
    """Calculate diversity score (0-100). Higher = more diverse."""
    total = diversity["total_runs"]
    unique = diversity["unique_tasks"]
    if total == 0:
        return 0.0
    if unique == 0:
        return 0.0
    # Shannon entropy normalized
    freqs = list(diversity["frequencies"].values())
    if len(freqs) <= 1:
        return 100.0 if unique == total else 50.0
    import math
    entropy = -sum((f / total) * math.log2(f / total) for f in freqs if f > 0)
    max_entropy = math.log2(unique) if unique > 1 else 1
    normalized = (entropy / max_entropy) * 100 if max_entropy > 0 else 0
    # Bonus for having many unique tasks relative to runs
    variety_bonus = min(20, (unique / total) * 40)
    return round(min(100, normalized + variety_bonus), 2)


def propose_scoring_adjustment(diversity: dict, repetition: dict) -> dict:
    """Propose scoring adjustment for the embryo task selection.
    Never forces a task. Only suggests score modifiers."""
    if not repetition["detected"]:
        return {"adjustment_needed": False, "modifiers": []}

    dominant = repetition["dominant_task"]
    modifiers = []

    # Penalize dominant task
    modifiers.append({
        "task": dominant,
        "modifier": -0.15,
        "reason": f"Over-represented ({repetition['ratio']:.0%} of runs)",
        "type": "PENALTY",
    })

    # Boost underrepresented tasks
    freqs = diversity["frequencies"]
    avg_freq = diversity["total_runs"] / diversity["unique_tasks"] if diversity["unique_tasks"] > 0 else 0
    for task, count in freqs.items():
        if task != dominant and count < avg_freq * 0.5:
            modifiers.append({
                "task": task,
                "modifier": 0.10,
                "reason": f"Under-represented ({count}/{diversity['total_runs']} runs)",
                "type": "BOOST",
            })

    return {"adjustment_needed": True, "modifiers": modifiers}


def run_balancer(base_dir: Optional[Path] = None) -> dict:
    """Main entry point: run the full task diversity balancer."""
    if base_dir is None:
        base_dir = Path(__file__).parents[3]

    run_history = load_run_history(base_dir)
    results = {}

    for embryo_type, runs in run_history.items():
        diversity = count_task_diversity(runs)
        repetition = detect_excessive_repetition(diversity)
        score = calculate_diversity_score(diversity)
        adjustment = propose_scoring_adjustment(diversity, repetition)
        results[embryo_type] = {
            "diversity": diversity,
            "repetition": repetition,
            "diversity_score": score,
            "adjustment": adjustment,
        }

    overall_score = sum(r["diversity_score"] for r in results.values()) / max(len(results), 1)

    return {
        "artifact": "embryo_task_diversity_balancer_v0_1",
        "version": "0.1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "embryos": results,
        "overall_diversity_score": round(overall_score, 2),
        "recommendation": "DIVERSIFY" if overall_score < 60 else "HEALTHY",
        "external_api_calls": 0,
        "secrets_used": 0,
        "state_modified": False,
        "forces_task": False,
        "skips_dispatcher": False,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Embryo Task Diversity Balancer v0.1")
    parser.add_argument("--base-dir", default=None)
    args = parser.parse_args()
    base = Path(args.base_dir) if args.base_dir else None
    result = run_balancer(base)
    print(json.dumps(result, indent=2, default=str))
