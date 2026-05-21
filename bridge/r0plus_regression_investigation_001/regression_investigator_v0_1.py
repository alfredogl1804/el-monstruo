"""
Regression Investigator v0.1
Investigates regression flags from embryo run history and determines
if they represent real regressions or false positives.

Responsibilities:
  1. Load run history from local JSON fixtures
  2. Calculate baseline statistics
  3. Detect false positives (fixture ceiling values, data artifacts)
  4. Detect real regressions (persistent degradation, grounding drops)
  5. Differentiate: cost spike, task repetition, grounding drop, audit fail, health drop
  6. Classify severity
  7. Produce structured investigation report
  8. Do NOT modify any state

Constraints:
  - R0+ only: pure local computation
  - No external API calls
  - No Supabase, no DB, no secrets
  - No network
  - Budget: $0.00

Usage:
    from regression_investigator_v0_1 import RegressionInvestigator
    investigator = RegressionInvestigator(run_history, regression_flags)
    report = investigator.investigate()
"""
import json
import math
import os
from datetime import datetime, timezone
from typing import Optional


class RegressionInvestigator:
    """Investigates regression flags and classifies them."""

    # Known fixture ceiling values (common placeholders)
    FIXTURE_CEILING_VALUES = {0.001, 0.01, 0.1, 1.0}

    # Thresholds
    COST_SPIKE_Z_THRESHOLD = 2.0
    GROUNDING_DROP_THRESHOLD = 5  # score below this = drop
    REPETITION_THRESHOLD = 0.7  # if one task > 70% of runs = repetition

    # Classification
    CLASSIFICATIONS = [
        "FALSE_POSITIVE",
        "LOW_RISK_TRACK",
        "REAL_REGRESSION_NEEDS_FIX",
        "BLOCKER_BEFORE_SURGE_003",
    ]

    def __init__(self, run_history: list, regression_flags: list,
                 memory_palace: Optional[list] = None, config: Optional[dict] = None):
        """
        Args:
            run_history: List of run dicts with cost_usd, task_id, timestamp, etc.
            regression_flags: List of flag dicts from history analyzer
            memory_palace: Optional memory palace entries for grounding analysis
            config: Optional overrides
        """
        self.run_history = run_history or []
        self.regression_flags = regression_flags or []
        self.memory_palace = memory_palace or []
        self.config = config or {}

    def calculate_baseline(self) -> dict:
        """Calculate cost baseline statistics from run history."""
        costs = [r.get("cost_usd", 0) for r in self.run_history]
        if not costs:
            return {"mean": 0.0, "stddev": 0.0, "median": 0.0, "count": 0}

        n = len(costs)
        mean = sum(costs) / n
        variance = sum((c - mean) ** 2 for c in costs) / n if n > 1 else 0.0
        stddev = math.sqrt(variance)
        sorted_costs = sorted(costs)
        median = sorted_costs[n // 2] if n % 2 else (sorted_costs[n // 2 - 1] + sorted_costs[n // 2]) / 2

        return {
            "mean": round(mean, 6),
            "stddev": round(stddev, 6),
            "median": round(median, 6),
            "count": n,
            "min": round(min(costs), 6),
            "max": round(max(costs), 6),
        }

    def detect_fixture_ceiling(self, cost: float) -> bool:
        """Detect if a cost value is a known fixture ceiling/placeholder."""
        return cost in self.FIXTURE_CEILING_VALUES

    def count_ceiling_occurrences(self, cost: float) -> int:
        """Count how many runs have this exact ceiling value."""
        return sum(1 for r in self.run_history if r.get("cost_usd") == cost)

    def detect_cost_spike(self, flag: dict) -> dict:
        """Analyze a cost spike flag."""
        current_value = flag.get("current_value", 0)
        recent_avg = flag.get("recent_avg", 0)
        run_index = flag.get("run_index", -1)

        # Check if it's a fixture ceiling
        is_ceiling = self.detect_fixture_ceiling(current_value)
        ceiling_count = self.count_ceiling_occurrences(current_value) if is_ceiling else 0

        # Check if runs after the spike returned to normal
        subsequent_costs = [
            r.get("cost_usd", 0) for r in self.run_history[run_index + 1:]
        ] if run_index >= 0 and run_index < len(self.run_history) else []

        recovered = False
        if subsequent_costs:
            subsequent_mean = sum(subsequent_costs) / len(subsequent_costs)
            recovered = subsequent_mean < current_value * 0.5

        return {
            "type": "COST_SPIKE",
            "is_fixture_ceiling": is_ceiling,
            "ceiling_occurrences": ceiling_count,
            "recovered_after": recovered,
            "subsequent_runs": len(subsequent_costs),
            "subsequent_mean": round(sum(subsequent_costs) / len(subsequent_costs), 6) if subsequent_costs else None,
        }

    def detect_grounding_drop(self) -> dict:
        """Detect grounding score drops in memory palace."""
        if not self.memory_palace:
            return {"detected": False, "reason": "no_memory_palace_data"}

        scores = [e.get("grounding_score", 10) for e in self.memory_palace]
        if not scores:
            return {"detected": False, "reason": "no_scores"}

        low_scores = [s for s in scores if s < self.GROUNDING_DROP_THRESHOLD]
        return {
            "detected": len(low_scores) > 0,
            "low_score_count": len(low_scores),
            "total_entries": len(scores),
            "min_score": min(scores),
            "mean_score": round(sum(scores) / len(scores), 2),
        }

    def detect_repeated_task(self) -> dict:
        """Detect task repetition / overspecialization."""
        tasks = [r.get("task_id", "unknown") for r in self.run_history]
        if not tasks:
            return {"detected": False, "reason": "no_tasks"}

        from collections import Counter
        counter = Counter(tasks)
        total = len(tasks)
        dominant_task, dominant_count = counter.most_common(1)[0]
        dominant_pct = dominant_count / total

        return {
            "detected": dominant_pct >= self.REPETITION_THRESHOLD,
            "dominant_task": dominant_task,
            "dominant_pct": round(dominant_pct, 4),
            "unique_tasks": len(counter),
            "total_runs": total,
        }

    def classify_severity(self, analysis: dict) -> str:
        """Classify overall severity based on analysis results."""
        # If fixture ceiling and recovered → false positive
        cost_analysis = analysis.get("cost_spike_analysis", {})
        if cost_analysis.get("is_fixture_ceiling") and cost_analysis.get("recovered_after"):
            return "NONE"

        # If grounding drop detected → medium
        grounding = analysis.get("grounding_analysis", {})
        if grounding.get("detected") and grounding.get("low_score_count", 0) > 2:
            return "HIGH"
        if grounding.get("detected"):
            return "MEDIUM"

        # If cost spike but not ceiling and not recovered → medium
        if not cost_analysis.get("is_fixture_ceiling") and not cost_analysis.get("recovered_after"):
            return "MEDIUM"

        return "LOW"

    def determine_classification(self, severity: str, analysis: dict) -> str:
        """Determine final classification (A/B/C/D)."""
        cost_analysis = analysis.get("cost_spike_analysis", {})

        if severity == "NONE" or (cost_analysis.get("is_fixture_ceiling") and cost_analysis.get("recovered_after")):
            return "FALSE_POSITIVE"
        elif severity == "LOW":
            return "LOW_RISK_TRACK"
        elif severity == "MEDIUM":
            return "REAL_REGRESSION_NEEDS_FIX"
        else:  # HIGH
            return "BLOCKER_BEFORE_SURGE_003"

    def generate_recommendation(self, classification: str) -> str:
        """Generate recommended action based on classification."""
        recommendations = {
            "FALSE_POSITIVE": "No action needed. Update history analyzer to recognize fixture ceiling values as non-anomalous.",
            "LOW_RISK_TRACK": "Track in next epoch. No blocking action required.",
            "REAL_REGRESSION_NEEDS_FIX": "Investigate root cause and produce fix artifact before Surge 003.",
            "BLOCKER_BEFORE_SURGE_003": "HALT. Do not proceed to Surge 003 until regression is resolved.",
        }
        return recommendations.get(classification, "Unknown classification.")

    def investigate(self) -> dict:
        """Run full regression investigation."""
        baseline = self.calculate_baseline()

        # Analyze each regression flag
        investigations = []
        for flag in self.regression_flags:
            flag_type = flag.get("type", "UNKNOWN")

            analysis = {
                "flag": flag,
                "baseline": baseline,
            }

            if flag_type == "COST_SPIKE":
                analysis["cost_spike_analysis"] = self.detect_cost_spike(flag)

            analysis["grounding_analysis"] = self.detect_grounding_drop()
            analysis["repetition_analysis"] = self.detect_repeated_task()

            severity = self.classify_severity(analysis)
            classification = self.determine_classification(severity, analysis)
            recommendation = self.generate_recommendation(classification)

            investigations.append({
                "regression_id": f"REG-{flag.get('run_index', 0):03d}-{flag_type}",
                "source": flag.get("source_file", "unknown"),
                "affected_embryo": "oracle_ai_embryo_r0",
                "affected_metric": "cost_usd",
                "baseline_mean": baseline["mean"],
                "observed_value": flag.get("current_value", 0),
                "delta": round(flag.get("current_value", 0) - baseline["mean"], 6),
                "severity": severity,
                "classification": classification,
                "root_cause_candidate": "fixture_ceiling_value" if analysis.get("cost_spike_analysis", {}).get("is_fixture_ceiling") else "unknown_cost_increase",
                "confidence": 0.95 if analysis.get("cost_spike_analysis", {}).get("is_fixture_ceiling") else 0.5,
                "recommended_action": recommendation,
                "analysis": analysis,
            })

        # Overall verdict
        classifications = [inv["classification"] for inv in investigations]
        if "BLOCKER_BEFORE_SURGE_003" in classifications:
            overall = "BLOCKER_BEFORE_SURGE_003"
        elif "REAL_REGRESSION_NEEDS_FIX" in classifications:
            overall = "REAL_REGRESSION_NEEDS_FIX"
        elif "LOW_RISK_TRACK" in classifications:
            overall = "LOW_RISK_TRACK"
        else:
            overall = "FALSE_POSITIVE"

        return {
            "version": "0.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "regression_investigator_v0_1",
            "investigation_count": len(investigations),
            "overall_classification": overall,
            "overall_severity": max(
                (inv["severity"] for inv in investigations),
                key=lambda s: ["NONE", "LOW", "MEDIUM", "HIGH"].index(s),
                default="NONE"
            ),
            "investigations": investigations,
            "baseline": baseline,
            "external_api_calls": 0,
            "secrets_used": 0,
        }


def run_from_files(run_history_path: str = None, flags_path: str = None,
                   memory_palace_path: str = None) -> dict:
    """Run investigation from file paths."""
    # Default paths relative to repo root
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if run_history_path is None:
        # Build run history from oracle outputs
        oracle_dir = os.path.join(base, "bridge", "embryos", "oracle_ai_r0", "outputs")
        run_history = []
        if os.path.isdir(oracle_dir):
            for f in sorted(os.listdir(oracle_dir)):
                if f.endswith(".json"):
                    with open(os.path.join(oracle_dir, f)) as fh:
                        data = json.load(fh)
                        run_history.append({
                            "cost_usd": data.get("cost_usd", 0),
                            "task_id": data.get("task_id", "unknown"),
                            "timestamp": data.get("timestamp", ""),
                            "file": f,
                        })
    else:
        with open(run_history_path) as fh:
            run_history = json.load(fh)

    # Load regression flags from snapshot
    if flags_path is None:
        snapshot_path = os.path.join(base, "bridge", "reactor_limited_active_r0",
                                     "live_upgrade_epoch_009", "EPOCH_009_OPS_SNAPSHOT.json")
        if os.path.exists(snapshot_path):
            with open(snapshot_path) as fh:
                snapshot = json.load(fh)
                flags = snapshot.get("runner_output", {}).get("consolidated", {}).get("regression_flags", [])
        else:
            flags = []
    else:
        with open(flags_path) as fh:
            flags = json.load(fh)

    # Load memory palace
    memory_palace = []
    if memory_palace_path is None:
        mp_path = os.path.join(base, "embryos", "memory_palace", "memory_palace_state.json")
        if os.path.exists(mp_path):
            with open(mp_path) as fh:
                mp_data = json.load(fh)
                memory_palace = mp_data.get("entries", [])
    else:
        with open(memory_palace_path) as fh:
            memory_palace = json.load(fh)

    investigator = RegressionInvestigator(run_history, flags, memory_palace)
    return investigator.investigate()


if __name__ == "__main__":
    result = run_from_files()
    # Write output
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "REGRESSION_INVESTIGATION_OUTPUT.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
