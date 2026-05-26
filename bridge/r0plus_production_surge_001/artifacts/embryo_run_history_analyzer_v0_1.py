"""
Embryo Run History Analyzer v0.1
Analyzes Oracle and Auditor run history to detect trends, regressions,
and performance patterns across all cycles.

Usage:
    python3 embryo_run_history_analyzer_v0_1.py [--base-dir /path/to/bridge]

Output:
    JSON report with trend analysis, regression detection, and recommendations.

Constraints:
    - R0+ only: reads output files and state, no external APIs
    - Read-only: does not modify any embryo files
    - No secrets, no Supabase, no memory writes
"""

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Optional


def discover_oracle_outputs(base_dir: Path) -> list[dict]:
    """Discover all Oracle output files."""
    # Try both direct path and bridge/ subdirectory
    candidates = [
        base_dir / "embryos" / "oracle_ai_r0" / "outputs",
        base_dir / "bridge" / "embryos" / "oracle_ai_r0" / "outputs",
    ]
    outputs_dir = None
    for c in candidates:
        if c.exists():
            outputs_dir = c
            break
    if outputs_dir is None:
        return []

    outputs = []
    for f in sorted(outputs_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            data["_source_file"] = f.name
            outputs.append(data)
        except (json.JSONDecodeError, IOError):
            continue

    return outputs


def discover_auditor_outputs(base_dir: Path) -> list[dict]:
    """Discover all Auditor output files."""
    candidates = [
        base_dir / "embryos" / "oracle_pair_r0" / "auditor_outputs",
        base_dir / "bridge" / "embryos" / "oracle_pair_r0" / "auditor_outputs",
    ]
    outputs_dir = None
    for c in candidates:
        if c.exists():
            outputs_dir = c
            break
    if outputs_dir is None:
        return []

    outputs = []
    for f in sorted(outputs_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            data["_source_file"] = f.name
            outputs.append(data)
        except (json.JSONDecodeError, IOError):
            continue

    return outputs


def load_embryo_state(base_dir: Path, embryo_type: str) -> dict:
    """Load embryo state file."""
    if embryo_type == "oracle":
        candidates = [
            base_dir / "embryos" / "oracle_ai_r0" / "state.json",
            base_dir / "bridge" / "embryos" / "oracle_ai_r0" / "state.json",
        ]
    elif embryo_type == "auditor":
        candidates = [
            base_dir / "embryos" / "oracle_pair_r0" / "auditor_state.json",
            base_dir / "bridge" / "embryos" / "oracle_pair_r0" / "auditor_state.json",
        ]
    else:
        return {}

    state_file = None
    for c in candidates:
        if c.exists():
            state_file = c
            break
    if state_file is None:
        return {}

    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return {}


def extract_run_metrics(outputs: list[dict]) -> list[dict]:
    """Extract key metrics from each run output."""
    metrics = []
    for output in outputs:
        # Handle nested output structure
        inner = output.get("output", output)

        metric = {
            "timestamp": output.get("timestamp", ""),
            "task_id": output.get("task_id", inner.get("task_id", "unknown")),
            "cost_usd": output.get("cost_usd", inner.get("cost", 0)),
            "grounding_level": output.get("grounding_level", inner.get("grounding_level", 0)),
            "action_class": output.get("action_class", "unknown"),
            "dispatcher_decision": output.get("dispatcher_decision", "unknown"),
            "source_file": output.get("_source_file", ""),
        }

        # Extract claims count
        claims = inner.get("claims", [])
        metric["claims_count"] = len(claims) if isinstance(claims, list) else 0

        metrics.append(metric)

    return metrics


def analyze_cost_trend(metrics: list[dict]) -> dict:
    """Analyze cost trend over time."""
    costs = [m["cost_usd"] for m in metrics if m["cost_usd"] > 0]

    if len(costs) < 2:
        return {"trend": "INSUFFICIENT_DATA", "data_points": len(costs)}

    avg = mean(costs)
    total = sum(costs)

    # Compare first half vs second half
    mid = len(costs) // 2
    first_avg = mean(costs[:mid])
    second_avg = mean(costs[mid:])
    delta_pct = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0

    if delta_pct > 20:
        trend = "INCREASING"
    elif delta_pct < -20:
        trend = "DECREASING"
    else:
        trend = "STABLE"

    return {
        "trend": trend,
        "avg_cost_usd": round(avg, 6),
        "total_cost_usd": round(total, 6),
        "min_cost": round(min(costs), 6),
        "max_cost": round(max(costs), 6),
        "first_half_avg": round(first_avg, 6),
        "second_half_avg": round(second_avg, 6),
        "delta_pct": round(delta_pct, 1),
        "data_points": len(costs),
    }


def analyze_grounding_trend(metrics: list[dict]) -> dict:
    """Analyze grounding score trend over time."""
    scores = [m["grounding_level"] for m in metrics if m["grounding_level"] > 0]

    if len(scores) < 2:
        return {"trend": "INSUFFICIENT_DATA", "data_points": len(scores)}

    avg = mean(scores)

    mid = len(scores) // 2
    first_avg = mean(scores[:mid])
    second_avg = mean(scores[mid:])
    delta = second_avg - first_avg

    if delta > 1.0:
        trend = "IMPROVING"
    elif delta < -1.0:
        trend = "DEGRADING"
    else:
        trend = "STABLE"

    return {
        "trend": trend,
        "avg_score": round(avg, 2),
        "min_score": min(scores),
        "max_score": max(scores),
        "latest_score": scores[-1],
        "first_half_avg": round(first_avg, 2),
        "second_half_avg": round(second_avg, 2),
        "delta": round(delta, 2),
        "data_points": len(scores),
    }


def analyze_task_distribution(metrics: list[dict]) -> dict:
    """Analyze which tasks are being executed and their frequency."""
    task_counts = defaultdict(int)
    task_costs = defaultdict(list)
    task_groundings = defaultdict(list)

    for m in metrics:
        task = m["task_id"]
        task_counts[task] += 1
        if m["cost_usd"] > 0:
            task_costs[task].append(m["cost_usd"])
        if m["grounding_level"] > 0:
            task_groundings[task].append(m["grounding_level"])

    distribution = {}
    total = sum(task_counts.values())

    for task, count in sorted(task_counts.items(), key=lambda x: -x[1]):
        distribution[task] = {
            "count": count,
            "percentage": round(count / total * 100, 1) if total > 0 else 0,
            "avg_cost": round(mean(task_costs[task]), 6) if task_costs[task] else 0,
            "avg_grounding": round(mean(task_groundings[task]), 2) if task_groundings[task] else 0,
        }

    return {"total_runs": total, "unique_tasks": len(task_counts), "distribution": distribution}


def detect_regressions(metrics: list[dict], window: int = 3) -> list[dict]:
    """Detect performance regressions (sudden drops in grounding or cost spikes)."""
    regressions = []

    if len(metrics) < window + 1:
        return regressions

    for i in range(window, len(metrics)):
        current = metrics[i]
        recent_window = metrics[i - window : i]

        # Grounding regression
        recent_groundings = [m["grounding_level"] for m in recent_window if m["grounding_level"] > 0]
        if recent_groundings and current["grounding_level"] > 0:
            avg_recent = mean(recent_groundings)
            if current["grounding_level"] < avg_recent - 2.0:
                regressions.append(
                    {
                        "type": "GROUNDING_DROP",
                        "run_index": i,
                        "source_file": current["source_file"],
                        "current_value": current["grounding_level"],
                        "recent_avg": round(avg_recent, 2),
                        "severity": "HIGH" if current["grounding_level"] < avg_recent - 4.0 else "MEDIUM",
                    }
                )

        # Cost spike
        recent_costs = [m["cost_usd"] for m in recent_window if m["cost_usd"] > 0]
        if recent_costs and current["cost_usd"] > 0:
            avg_cost = mean(recent_costs)
            if avg_cost > 0 and current["cost_usd"] > avg_cost * 3:
                regressions.append(
                    {
                        "type": "COST_SPIKE",
                        "run_index": i,
                        "source_file": current["source_file"],
                        "current_value": current["cost_usd"],
                        "recent_avg": round(avg_cost, 6),
                        "severity": "HIGH" if current["cost_usd"] > avg_cost * 5 else "MEDIUM",
                    }
                )

    return regressions


def compute_health_score(cost_trend: dict, grounding_trend: dict, regressions: list) -> dict:
    """Compute overall embryo health score."""
    score = 100
    issues = []

    if cost_trend.get("trend") == "INCREASING":
        score -= 15
        issues.append("Cost is increasing")

    if grounding_trend.get("trend") == "DEGRADING":
        score -= 25
        issues.append("Grounding is degrading")

    high_regressions = [r for r in regressions if r["severity"] == "HIGH"]
    if high_regressions:
        score -= len(high_regressions) * 10
        issues.append(f"{len(high_regressions)} HIGH severity regressions")

    score = max(0, min(100, score))
    status = "HEALTHY" if score >= 70 else "DEGRADED" if score >= 40 else "CRITICAL"

    return {"health_score": score, "status": status, "issues": issues}


def run_full_analysis(base_dir: Optional[Path] = None) -> dict:
    """Run complete history analysis for both Oracle and Auditor."""
    if base_dir is None:
        base_dir = Path(__file__).parents[2].parent  # Go up to bridge parent

    # Discover outputs
    oracle_outputs = discover_oracle_outputs(base_dir)
    auditor_outputs = discover_auditor_outputs(base_dir)

    # Extract metrics
    oracle_metrics = extract_run_metrics(oracle_outputs)
    auditor_metrics = extract_run_metrics(auditor_outputs)

    # Load states
    oracle_state = load_embryo_state(base_dir, "oracle")
    auditor_state = load_embryo_state(base_dir, "auditor")

    # Analyze Oracle
    oracle_cost = analyze_cost_trend(oracle_metrics)
    oracle_grounding = analyze_grounding_trend(oracle_metrics)
    oracle_tasks = analyze_task_distribution(oracle_metrics)
    oracle_regressions = detect_regressions(oracle_metrics)
    oracle_health = compute_health_score(oracle_cost, oracle_grounding, oracle_regressions)

    # Analyze Auditor
    auditor_cost = analyze_cost_trend(auditor_metrics)
    auditor_grounding = analyze_grounding_trend(auditor_metrics)
    auditor_tasks = analyze_task_distribution(auditor_metrics)
    auditor_regressions = detect_regressions(auditor_metrics)
    auditor_health = compute_health_score(auditor_cost, auditor_grounding, auditor_regressions)

    # Combined metrics
    all_costs = [m["cost_usd"] for m in oracle_metrics + auditor_metrics if m["cost_usd"] > 0]
    total_cost = sum(all_costs) if all_costs else 0

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "generated_by": "embryo_run_history_analyzer_v0_1",
        "summary": {
            "total_oracle_runs": len(oracle_metrics),
            "total_auditor_runs": len(auditor_metrics),
            "total_combined_runs": len(oracle_metrics) + len(auditor_metrics),
            "total_cost_usd": round(total_cost, 6),
            "oracle_health": oracle_health["status"],
            "auditor_health": auditor_health["status"],
            "combined_health": "HEALTHY"
            if oracle_health["health_score"] >= 70 and auditor_health["health_score"] >= 70
            else "DEGRADED",
        },
        "oracle": {
            "state_cycles": oracle_state.get("cycles_completed", 0),
            "outputs_found": len(oracle_outputs),
            "cost_trend": oracle_cost,
            "grounding_trend": oracle_grounding,
            "task_distribution": oracle_tasks,
            "regressions": oracle_regressions,
            "health": oracle_health,
        },
        "auditor": {
            "state_cycles": auditor_state.get("cycles_completed", 0),
            "outputs_found": len(auditor_outputs),
            "cost_trend": auditor_cost,
            "grounding_trend": auditor_grounding,
            "task_distribution": auditor_tasks,
            "regressions": auditor_regressions,
            "health": auditor_health,
        },
    }


if __name__ == "__main__":
    import sys

    base_dir = None
    if len(sys.argv) > 2 and sys.argv[1] == "--base-dir":
        base_dir = Path(sys.argv[2])

    report = run_full_analysis(base_dir)
    print(json.dumps(report, indent=2))
