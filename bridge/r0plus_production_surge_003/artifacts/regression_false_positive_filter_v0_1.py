"""
Regression False Positive Filter v0.1
Filters out known false positive patterns from regression flags.

Purpose:
  Reduces noise in the regression detection pipeline by identifying
  fixture ceiling values, known placeholder costs, and recovered spikes
  before they reach the investigator or T1.

Inputs:
  - List of regression flags (from history analyzer)
  - Run history (for baseline computation)
  - Optional: known ceiling values config

Output:
  - Filtered flags list (real regressions only)
  - Filter report JSON with classification per flag

Constraints:
  - No provider calls
  - No Supabase / DB
  - No secrets
  - No network
  - Pure local computation
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional


class RegressionFalsePositiveFilter:
    """Filters known false positive patterns from regression flags."""

    DEFAULT_CONFIG = {
        "ceiling_values": [0.001, 0.01, 0.1, 1.0],
        "ceiling_occurrence_threshold": 2,
        "recovery_window": 3,
        "recovery_tolerance_pct": 50.0,
        "min_baseline_runs": 5,
        "placeholder_patterns": ["0.001", "0.01", "0.1"],
    }

    FILTER_REASONS = [
        "FIXTURE_CEILING",
        "RECOVERED_SPIKE",
        "INSUFFICIENT_BASELINE",
        "KNOWN_PLACEHOLDER",
        "SINGLE_OCCURRENCE_NOISE",
    ]

    def __init__(self, config: Optional[dict] = None):
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}

    def filter(self, flags: list, run_history: list) -> dict:
        """Filter regression flags and classify each as real or false positive."""
        results = []
        real_flags = []
        filtered_flags = []

        for flag in flags:
            classification = self._classify_flag(flag, run_history)
            results.append(classification)
            if classification["is_false_positive"]:
                filtered_flags.append(classification)
            else:
                real_flags.append(classification)

        report = {
            "version": "0.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "regression_false_positive_filter_v0_1",
            "total_flags_input": len(flags),
            "real_regressions": len(real_flags),
            "false_positives_filtered": len(filtered_flags),
            "filter_rate_pct": round(len(filtered_flags) / max(len(flags), 1) * 100, 1),
            "classifications": results,
            "real_flags": real_flags,
            "filtered_flags": filtered_flags,
            "external_api_calls": 0,
            "secrets_used": 0,
        }

        return report

    def _classify_flag(self, flag: dict, run_history: list) -> dict:
        """Classify a single flag as real regression or false positive."""
        flag.get("type", "UNKNOWN")
        current_value = flag.get("current_value", 0)
        flag.get("metric", flag.get("type", "unknown"))

        classification = {
            "flag": flag,
            "is_false_positive": False,
            "filter_reason": None,
            "confidence": 0.0,
            "details": {},
        }

        # Check 1: Fixture ceiling value
        if self._is_ceiling_value(current_value, run_history):
            classification["is_false_positive"] = True
            classification["filter_reason"] = "FIXTURE_CEILING"
            classification["confidence"] = 0.95
            classification["details"] = {
                "ceiling_value": current_value,
                "occurrences": self._count_ceiling_occurrences(current_value, run_history),
            }
            return classification

        # Check 2: Recovered spike
        if self._is_recovered_spike(flag, run_history):
            classification["is_false_positive"] = True
            classification["filter_reason"] = "RECOVERED_SPIKE"
            classification["confidence"] = 0.85
            classification["details"] = {
                "recovery_confirmed": True,
                "recovery_runs": self._count_recovery_runs(flag, run_history),
            }
            return classification

        # Check 3: Insufficient baseline
        if len(run_history) < self.config["min_baseline_runs"]:
            classification["is_false_positive"] = True
            classification["filter_reason"] = "INSUFFICIENT_BASELINE"
            classification["confidence"] = 0.70
            classification["details"] = {
                "runs_available": len(run_history),
                "min_required": self.config["min_baseline_runs"],
            }
            return classification

        # Check 4: Known placeholder
        if self._is_known_placeholder(current_value):
            classification["is_false_positive"] = True
            classification["filter_reason"] = "KNOWN_PLACEHOLDER"
            classification["confidence"] = 0.80
            classification["details"] = {
                "value": current_value,
                "matches_pattern": True,
            }
            return classification

        # Check 5: Single occurrence noise (value appears only once and is within 3x stddev)
        if self._is_single_noise(current_value, run_history):
            classification["is_false_positive"] = True
            classification["filter_reason"] = "SINGLE_OCCURRENCE_NOISE"
            classification["confidence"] = 0.60
            classification["details"] = {
                "occurrences": 1,
                "within_3x_stddev": True,
            }
            return classification

        # Not a false positive — real regression
        classification["confidence"] = 0.90
        return classification

    def _is_ceiling_value(self, value: float, run_history: list) -> bool:
        """Check if value is a known fixture ceiling that appears multiple times."""
        if value not in self.config["ceiling_values"]:
            return False
        occurrences = self._count_ceiling_occurrences(value, run_history)
        return occurrences >= self.config["ceiling_occurrence_threshold"]

    def _count_ceiling_occurrences(self, value: float, run_history: list) -> int:
        """Count how many times a ceiling value appears in run history."""
        count = 0
        for run in run_history:
            cost = run.get("cost_usd", run.get("cost", 0))
            if abs(cost - value) < 1e-10:
                count += 1
        return count

    def _is_recovered_spike(self, flag: dict, run_history: list) -> bool:
        """Check if the spike recovered in subsequent runs."""
        run_index = flag.get("run_index", -1)
        if run_index < 0 or run_index >= len(run_history):
            return False

        window = self.config["recovery_window"]
        subsequent = run_history[run_index + 1 : run_index + 1 + window]
        if len(subsequent) == 0:
            return False

        # Calculate baseline from runs before the spike
        before = run_history[:run_index]
        if len(before) < 2:
            return False

        costs_before = [r.get("cost_usd", r.get("cost", 0)) for r in before]
        mean_before = sum(costs_before) / len(costs_before)

        costs_after = [r.get("cost_usd", r.get("cost", 0)) for r in subsequent]
        mean_after = sum(costs_after) / len(costs_after)

        # Recovery: subsequent mean is within tolerance of pre-spike mean
        tolerance = mean_before * (self.config["recovery_tolerance_pct"] / 100.0)
        return abs(mean_after - mean_before) <= tolerance

    def _count_recovery_runs(self, flag: dict, run_history: list) -> int:
        """Count runs after the spike that returned to normal."""
        run_index = flag.get("run_index", -1)
        if run_index < 0:
            return 0
        return len(run_history[run_index + 1 :])

    def _is_known_placeholder(self, value: float) -> bool:
        """Check if value matches known placeholder patterns."""
        value_str = f"{value:.3f}"
        return value_str in self.config["placeholder_patterns"]

    def _is_single_noise(self, value: float, run_history: list) -> bool:
        """Check if value is a single occurrence within statistical noise.
        Only classifies as noise if the value is within 3x stddev of the
        baseline (excluding the spike itself)."""
        costs = [r.get("cost_usd", r.get("cost", 0)) for r in run_history]
        if len(costs) < 3:
            return False

        occurrences = sum(1 for c in costs if abs(c - value) < 1e-10)
        if occurrences > 1:
            return False

        # Calculate baseline excluding the spike value itself
        baseline_costs = [c for c in costs if abs(c - value) > 1e-10]
        if len(baseline_costs) < 2:
            return False

        mean = sum(baseline_costs) / len(baseline_costs)
        variance = sum((c - mean) ** 2 for c in baseline_costs) / len(baseline_costs)
        stddev = variance**0.5

        # Only noise if within 3x stddev of baseline
        return abs(value - mean) <= 3 * stddev


def run_from_files(base_path: str = None) -> dict:
    """Run filter from local files."""
    if base_path is None:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    filter_instance = RegressionFalsePositiveFilter()

    # Load regression investigation output for flags
    reg_path = os.path.join(
        base_path, "bridge", "r0plus_regression_investigation_001", "REGRESSION_INVESTIGATION_OUTPUT.json"
    )
    flags = []
    run_history = []

    if os.path.exists(reg_path):
        reg_data = json.load(open(reg_path))
        for inv in reg_data.get("investigations", []):
            flag = inv.get("analysis", {}).get("flag", {})
            if flag:
                flags.append(flag)

    # Load run history from fixtures
    fixtures_path = os.path.join(base_path, "bridge", "r0plus_production_surge_001", "fixtures")
    if os.path.exists(fixtures_path):
        for fname in sorted(os.listdir(fixtures_path)):
            if fname.endswith(".json") and "oracle" not in fname.lower():
                try:
                    data = json.load(open(os.path.join(fixtures_path, fname)))
                    if "cost_usd" in data or "cost" in data:
                        run_history.append(data)
                except (json.JSONDecodeError, IOError):
                    pass

    # If no run history from fixtures, use synthetic from investigation
    if not run_history and os.path.exists(reg_path):
        reg_data = json.load(open(reg_path))
        baseline = reg_data.get("baseline", {})
        # Create synthetic history from baseline stats
        count = baseline.get("count", 13)
        mean = baseline.get("mean", 0.000451)
        for i in range(count):
            run_history.append({"cost_usd": mean, "run_index": i})

    result = filter_instance.filter(flags, run_history)
    return result


if __name__ == "__main__":
    result = run_from_files()
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "FALSE_POSITIVE_FILTER_OUTPUT.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
