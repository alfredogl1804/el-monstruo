#!/usr/bin/env python3
"""
Memory Analytics v0.1 — Second R0+ Artifact
Produced autonomously from Epoch 006 Memory-Guided Cycle.

Analyzes Memory Palace entries to extract:
- Learning velocity (lessons per cycle)
- Cost efficiency trend
- Grounding score progression
- Cross-embryo interaction patterns
- Recommendations for next epoch

Constraints:
- READ-ONLY: never modifies Memory Palace
- LOCAL-ONLY: no external calls
- Zero cost: pure computation
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
MEMORY_PALACE_PATH = BASE_DIR / "embryos" / "memory_palace" / "memory_palace_state.json"
KILL_SWITCH_PATH = BASE_DIR / "bridge" / "reactor_vigilia_foundation" / "reactor_heartbeat_r0" / "scheduler" / "scheduler_kill_switch.json"
OUTPUT_DIR = Path(__file__).resolve().parent


def check_kill_switch():
    """Respect kill-switch supremacy."""
    if KILL_SWITCH_PATH.exists():
        ks = json.loads(KILL_SWITCH_PATH.read_text())
        if ks.get("active", True):
            return True
    return False


def load_memory_palace():
    """Load Memory Palace state."""
    if not MEMORY_PALACE_PATH.exists():
        return None
    return json.loads(MEMORY_PALACE_PATH.read_text())


def analyze_learning_velocity(entries):
    """Calculate lessons learned per cycle."""
    if not entries:
        return {"lessons_per_cycle": 0, "total_lessons": 0, "unique_lessons": 0}
    
    all_lessons = []
    for e in entries:
        all_lessons.extend(e.get("lessons", []))
    
    unique = list(set(all_lessons))
    cycles = len(entries)
    
    return {
        "lessons_per_cycle": round(len(all_lessons) / max(cycles, 1), 2),
        "total_lessons": len(all_lessons),
        "unique_lessons": len(unique),
        "lesson_list": unique
    }


def analyze_cost_efficiency(entries):
    """Analyze cost per entry and trends."""
    if not entries:
        return {"avg_cost": 0, "total_cost": 0, "min_cost": 0, "max_cost": 0}
    
    costs = [e.get("cost_usd", 0) for e in entries]
    return {
        "avg_cost": round(sum(costs) / len(costs), 6),
        "total_cost": round(sum(costs), 6),
        "min_cost": round(min(costs), 6),
        "max_cost": round(max(costs), 6),
        "cost_trend": "STABLE" if max(costs) - min(costs) < 0.001 else "VARIABLE"
    }


def analyze_grounding_progression(entries):
    """Track grounding score over time."""
    if not entries:
        return {"avg_grounding": 0, "trend": "NO_DATA"}
    
    scores = [e.get("grounding_score", 0) for e in entries]
    avg = round(sum(scores) / len(scores), 1)
    
    if len(scores) >= 2:
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        trend = "IMPROVING" if sum(second_half)/len(second_half) > sum(first_half)/len(first_half) else "STABLE"
    else:
        trend = "INSUFFICIENT_DATA"
    
    return {
        "avg_grounding": avg,
        "min_grounding": min(scores),
        "max_grounding": max(scores),
        "trend": trend,
        "scores": scores
    }


def analyze_cross_embryo_patterns(entries):
    """Detect interaction patterns between embryos."""
    if not entries:
        return {"pattern": "NO_DATA"}
    
    embryo_map = {}
    for e in entries:
        src = e.get("source_embryo_id", "unknown")
        if src not in embryo_map:
            embryo_map[src] = []
        embryo_map[src].append(e)
    
    patterns = {
        "embryo_count": len(embryo_map),
        "embryos": list(embryo_map.keys()),
        "entries_per_embryo": {k: len(v) for k, v in embryo_map.items()},
        "shared_artifacts": [],
        "interaction_type": "INDEPENDENT"
    }
    
    # Check for shared artifact refs
    all_artifacts = {}
    for e in entries:
        for ref in e.get("artifact_refs", []):
            if ref not in all_artifacts:
                all_artifacts[ref] = []
            all_artifacts[ref].append(e.get("source_embryo_id"))
    
    shared = {k: v for k, v in all_artifacts.items() if len(set(v)) > 1}
    if shared:
        patterns["shared_artifacts"] = list(shared.keys())
        patterns["interaction_type"] = "COLLABORATIVE"
    
    return patterns


def generate_recommendations(learning, cost, grounding, patterns):
    """Generate actionable recommendations for next epoch."""
    recs = []
    
    if grounding["avg_grounding"] < 8:
        recs.append("IMPROVE_GROUNDING: Average grounding below 8 — Oracle should prioritize VERIFIED_LOCAL and VERIFIED_PROVIDER evidence")
    
    if cost["cost_trend"] == "VARIABLE":
        recs.append("STABILIZE_COST: Cost variance detected — consider capping per-cycle budget")
    
    if learning["lessons_per_cycle"] < 1:
        recs.append("INCREASE_LEARNING: Less than 1 lesson per cycle — tasks may be too repetitive")
    
    if patterns["interaction_type"] == "INDEPENDENT":
        recs.append("INCREASE_COLLABORATION: Embryos operating independently — consider shared task queues")
    
    if not recs:
        recs.append("HEALTHY: All metrics within expected ranges — continue current trajectory")
    
    return recs


def run_analytics():
    """Main analytics run."""
    if check_kill_switch():
        print("[ABORT] Kill-switch active. Memory Analytics cannot run.")
        return {"status": "ABORTED", "reason": "kill_switch_active"}
    
    palace = load_memory_palace()
    if palace is None:
        print("[ERROR] Memory Palace not found.")
        return {"status": "ERROR", "reason": "memory_palace_not_found"}
    
    entries = palace.get("entries", [])
    
    learning = analyze_learning_velocity(entries)
    cost = analyze_cost_efficiency(entries)
    grounding = analyze_grounding_progression(entries)
    patterns = analyze_cross_embryo_patterns(entries)
    recommendations = generate_recommendations(learning, cost, grounding, patterns)
    
    report = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artifact": "memory_analytics_v0_1",
        "memory_palace_version": palace.get("version", "unknown"),
        "total_entries_analyzed": len(entries),
        "analysis": {
            "learning_velocity": learning,
            "cost_efficiency": cost,
            "grounding_progression": grounding,
            "cross_embryo_patterns": patterns
        },
        "recommendations": recommendations,
        "status": "COMPLETE",
        "cost_of_this_analysis": 0.0
    }
    
    # Write report
    output_path = OUTPUT_DIR / "memory_analytics_report.json"
    output_path.write_text(json.dumps(report, indent=2))
    print(f"[SUCCESS] Memory Analytics Report: {output_path}")
    print(f"  Entries analyzed: {len(entries)}")
    print(f"  Learning velocity: {learning['lessons_per_cycle']} lessons/cycle")
    print(f"  Avg grounding: {grounding['avg_grounding']}/10")
    print(f"  Total cost tracked: ${cost['total_cost']}")
    print(f"  Recommendations: {len(recommendations)}")
    for r in recommendations:
        print(f"    → {r}")
    
    return report


if __name__ == "__main__":
    run_analytics()
