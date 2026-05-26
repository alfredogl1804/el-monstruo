"""
Memory Palace Pattern Detector v0.1
Analyzes Memory Palace entries to detect recurring patterns, cost anomalies,
grounding drift, and embryo performance trends.

Usage:
    python3 memory_palace_pattern_detector_v0_1.py [--state-file /path/to/state.json]

Output:
    JSON report with detected patterns, anomalies, and recommendations.

Constraints:
    - R0+ only: reads Memory Palace state file, no external APIs
    - Read-only: does not modify Memory Palace
    - No secrets, no Supabase, no memory writes
"""

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev
from typing import Optional

DEFAULT_STATE_FILE = Path(__file__).parents[2].parent / "embryos" / "memory_palace" / "memory_palace_state.json"


def load_entries(state_file: Optional[Path] = None) -> list[dict]:
    """Load all active entries from Memory Palace state."""
    sf = state_file or DEFAULT_STATE_FILE
    if not sf.exists():
        return []
    state = json.loads(sf.read_text(encoding="utf-8"))
    return [e for e in state.get("entries", []) if e.get("status") == "active"]


def detect_recurring_lessons(entries: list[dict], threshold: int = 2) -> list[dict]:
    """Detect lessons that appear multiple times (indicates unresolved pattern)."""
    lesson_counter = Counter()
    lesson_entries = defaultdict(list)

    for entry in entries:
        lesson = entry.get("lesson", "")
        if lesson:
            normalized = lesson.strip().lower()
            lesson_counter[normalized] += 1
            lesson_entries[normalized].append(entry.get("entry_id", "unknown"))

    recurring = []
    for lesson, count in lesson_counter.most_common():
        if count >= threshold:
            recurring.append(
                {
                    "lesson": lesson,
                    "occurrences": count,
                    "entry_ids": lesson_entries[lesson],
                    "severity": "HIGH" if count >= 4 else "MEDIUM" if count >= 3 else "LOW",
                    "recommendation": f"This lesson has appeared {count} times. Consider implementing a fix or accepting as known limitation.",
                }
            )

    return recurring


def detect_cost_anomalies(entries: list[dict], z_threshold: float = 2.0) -> list[dict]:
    """Detect entries with anomalous cost (z-score based)."""
    costs = []
    cost_entries = []

    for entry in entries:
        cost = entry.get("cost_usd", 0)
        if cost > 0:
            costs.append(cost)
            cost_entries.append(entry)

    if len(costs) < 3:
        return []

    avg = mean(costs)
    sd = stdev(costs) if len(costs) > 1 else 0

    anomalies = []
    for i, cost in enumerate(costs):
        if sd > 0:
            z_score = (cost - avg) / sd
            if abs(z_score) > z_threshold:
                anomalies.append(
                    {
                        "entry_id": cost_entries[i].get("entry_id", "unknown"),
                        "cost_usd": cost,
                        "z_score": round(z_score, 2),
                        "mean_cost": round(avg, 6),
                        "direction": "HIGH" if z_score > 0 else "LOW",
                        "recommendation": "Investigate why this cycle cost significantly more/less than average.",
                    }
                )

    return anomalies


def detect_grounding_drift(entries: list[dict], window: int = 3) -> dict:
    """Detect if grounding scores are trending up, down, or stable."""
    scores = []
    for entry in entries:
        gs = entry.get("grounding_score") or entry.get("grounding_level")
        if gs is not None:
            scores.append(float(gs))

    if len(scores) < window:
        return {"trend": "INSUFFICIENT_DATA", "scores": scores, "window": window}

    # Compare first half vs second half
    mid = len(scores) // 2
    first_half_avg = mean(scores[:mid]) if mid > 0 else 0
    second_half_avg = mean(scores[mid:]) if mid < len(scores) else 0

    delta = second_half_avg - first_half_avg

    if delta > 1.0:
        trend = "IMPROVING"
    elif delta < -1.0:
        trend = "DEGRADING"
    else:
        trend = "STABLE"

    return {
        "trend": trend,
        "first_half_avg": round(first_half_avg, 2),
        "second_half_avg": round(second_half_avg, 2),
        "delta": round(delta, 2),
        "total_scores": len(scores),
        "latest_score": scores[-1] if scores else None,
        "recommendation": _grounding_recommendation(trend, delta),
    }


def _grounding_recommendation(trend: str, delta: float) -> str:
    if trend == "IMPROVING":
        return "Grounding is improving. Current approach is working."
    elif trend == "DEGRADING":
        return f"Grounding is degrading (delta={delta}). Review prompt quality and source verification."
    elif trend == "STABLE":
        return "Grounding is stable. No action needed."
    return "Insufficient data for recommendation."


def detect_embryo_performance(entries: list[dict]) -> dict:
    """Analyze performance by embryo_id."""
    embryo_data = defaultdict(lambda: {"costs": [], "groundings": [], "tasks": [], "count": 0})

    for entry in entries:
        eid = entry.get("embryo_id", "unknown")
        embryo_data[eid]["count"] += 1

        cost = entry.get("cost_usd", 0)
        if cost > 0:
            embryo_data[eid]["costs"].append(cost)

        gs = entry.get("grounding_score") or entry.get("grounding_level")
        if gs is not None:
            embryo_data[eid]["groundings"].append(float(gs))

        task = entry.get("task_id", "")
        if task:
            embryo_data[eid]["tasks"].append(task)

    result = {}
    for eid, data in embryo_data.items():
        avg_cost = mean(data["costs"]) if data["costs"] else 0
        avg_grounding = mean(data["groundings"]) if data["groundings"] else 0
        unique_tasks = len(set(data["tasks"]))

        result[eid] = {
            "total_runs": data["count"],
            "avg_cost_usd": round(avg_cost, 6),
            "avg_grounding": round(avg_grounding, 2),
            "unique_tasks": unique_tasks,
            "task_diversity": round(unique_tasks / data["count"], 2) if data["count"] > 0 else 0,
        }

    return result


def detect_task_concentration(entries: list[dict]) -> dict:
    """Detect if certain tasks dominate (potential over-specialization)."""
    task_counter = Counter()
    for entry in entries:
        task = entry.get("task_id", "unknown")
        task_counter[task] += 1

    total = sum(task_counter.values())
    concentration = {}

    for task, count in task_counter.most_common():
        pct = round(count / total * 100, 1) if total > 0 else 0
        concentration[task] = {"count": count, "percentage": pct, "is_dominant": pct > 40}

    dominant_tasks = [t for t, d in concentration.items() if d["is_dominant"]]

    return {
        "total_runs": total,
        "unique_tasks": len(task_counter),
        "distribution": concentration,
        "dominant_tasks": dominant_tasks,
        "recommendation": "Task diversity is healthy."
        if not dominant_tasks
        else f"Tasks {dominant_tasks} dominate. Consider diversifying.",
    }


def detect_value_patterns(entries: list[dict]) -> dict:
    """Detect patterns in value_score field."""
    values = []
    for entry in entries:
        vs = entry.get("value_score")
        if vs is not None:
            values.append(float(vs))

    if not values:
        return {"status": "NO_VALUE_DATA", "recommendation": "Add value_score to Memory Palace entries."}

    avg = mean(values)
    low_value = [v for v in values if v < 4.0]
    high_value = [v for v in values if v >= 8.0]

    return {
        "avg_value": round(avg, 2),
        "low_value_count": len(low_value),
        "high_value_count": len(high_value),
        "total_scored": len(values),
        "low_value_pct": round(len(low_value) / len(values) * 100, 1),
        "recommendation": "High value ratio is good."
        if len(high_value) > len(low_value)
        else "Consider focusing on higher-value tasks.",
    }


def run_full_analysis(state_file: Optional[Path] = None) -> dict:
    """Run all pattern detection analyses and produce consolidated report."""
    entries = load_entries(state_file)

    if not entries:
        return {
            "status": "EMPTY_MEMORY_PALACE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entries_analyzed": 0,
            "patterns": [],
            "recommendation": "Memory Palace is empty. Run more cycles to generate data.",
        }

    recurring = detect_recurring_lessons(entries)
    cost_anomalies = detect_cost_anomalies(entries)
    grounding = detect_grounding_drift(entries)
    embryo_perf = detect_embryo_performance(entries)
    task_conc = detect_task_concentration(entries)
    value_pats = detect_value_patterns(entries)

    # Compute overall health
    issues = []
    if recurring:
        issues.append(f"{len(recurring)} recurring lessons unresolved")
    if cost_anomalies:
        issues.append(f"{len(cost_anomalies)} cost anomalies detected")
    if grounding["trend"] == "DEGRADING":
        issues.append("Grounding is degrading")
    if task_conc.get("dominant_tasks"):
        issues.append("Task over-specialization detected")

    health_score = 100 - (len(issues) * 15)
    health_score = max(0, min(100, health_score))

    return {
        "status": "ANALYSIS_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entries_analyzed": len(entries),
        "health_score": health_score,
        "health_status": "HEALTHY" if health_score >= 70 else "DEGRADED" if health_score >= 40 else "CRITICAL",
        "patterns": {
            "recurring_lessons": recurring,
            "cost_anomalies": cost_anomalies,
            "grounding_drift": grounding,
            "embryo_performance": embryo_perf,
            "task_concentration": task_conc,
            "value_patterns": value_pats,
        },
        "issues": issues,
        "recommendations": [r["recommendation"] for r in recurring[:3]]
        + [grounding["recommendation"]]
        + [task_conc["recommendation"]],
    }


if __name__ == "__main__":
    import sys

    state_file = None
    if len(sys.argv) > 2 and sys.argv[1] == "--state-file":
        state_file = Path(sys.argv[2])

    report = run_full_analysis(state_file)
    print(json.dumps(report, indent=2))
