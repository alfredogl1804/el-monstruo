"""
R0+ Cost Anomaly Guard v0.1
Detects, classifies, and reports cost anomalies in embryo run history.

Responsibilities:
  1. Ingest embryo run cost data (from local JSON fixtures)
  2. Compute rolling statistics (mean, stddev, z-score)
  3. Classify anomalies: NORMAL, WARNING, SPIKE, CRITICAL
  4. Produce guard report with actionable recommendations
  5. Detect cost drift trends (increasing baseline)

Constraints:
  - R0+ only: pure local computation
  - No external API calls
  - No Supabase, no DB, no secrets
  - No network
  - Budget: $0.00

Usage:
    from r0plus_cost_anomaly_guard_v0_1 import CostAnomalyGuard
    guard = CostAnomalyGuard(cost_history)
    report = guard.analyze()
"""
import json
import math
from datetime import datetime, timezone
from typing import Optional


class CostAnomalyGuard:
    """Detects and classifies cost anomalies in embryo run history."""

    # Thresholds (z-score based)
    THRESHOLD_WARNING = 1.5
    THRESHOLD_SPIKE = 2.0
    THRESHOLD_CRITICAL = 3.0

    # Drift detection: if rolling mean increases by this factor over window
    DRIFT_FACTOR = 1.5
    DRIFT_WINDOW = 5

    def __init__(self, cost_history: list, config: Optional[dict] = None):
        """
        Args:
            cost_history: List of dicts with at least {"cost_usd": float, "timestamp": str}
            config: Optional overrides for thresholds
        """
        self.cost_history = cost_history or []
        self.config = config or {}
        self.threshold_warning = self.config.get("threshold_warning", self.THRESHOLD_WARNING)
        self.threshold_spike = self.config.get("threshold_spike", self.THRESHOLD_SPIKE)
        self.threshold_critical = self.config.get("threshold_critical", self.THRESHOLD_CRITICAL)

    @property
    def costs(self) -> list:
        """Extract cost values from history."""
        return [entry.get("cost_usd", 0.0) for entry in self.cost_history]

    def compute_statistics(self) -> dict:
        """Compute rolling statistics on cost data."""
        costs = self.costs
        if not costs:
            return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0, "count": 0}

        n = len(costs)
        mean = sum(costs) / n
        variance = sum((c - mean) ** 2 for c in costs) / n if n > 1 else 0.0
        stddev = math.sqrt(variance)

        return {
            "mean": round(mean, 6),
            "stddev": round(stddev, 6),
            "min": round(min(costs), 6),
            "max": round(max(costs), 6),
            "count": n,
            "total": round(sum(costs), 6),
        }

    def compute_z_scores(self) -> list:
        """Compute z-score for each cost entry."""
        stats = self.compute_statistics()
        mean = stats["mean"]
        stddev = stats["stddev"]

        if stddev == 0:
            return [{"index": i, "cost_usd": c, "z_score": 0.0} for i, c in enumerate(self.costs)]

        return [
            {
                "index": i,
                "cost_usd": round(c, 6),
                "z_score": round((c - mean) / stddev, 4),
            }
            for i, c in enumerate(self.costs)
        ]

    def classify_anomaly(self, z_score: float) -> str:
        """Classify a z-score into anomaly category."""
        abs_z = abs(z_score)
        if abs_z >= self.threshold_critical:
            return "CRITICAL"
        elif abs_z >= self.threshold_spike:
            return "SPIKE"
        elif abs_z >= self.threshold_warning:
            return "WARNING"
        return "NORMAL"

    def detect_anomalies(self) -> list:
        """Detect all anomalies in cost history."""
        z_scores = self.compute_z_scores()
        anomalies = []

        for entry in z_scores:
            classification = self.classify_anomaly(entry["z_score"])
            if classification != "NORMAL":
                anomaly = {
                    "index": entry["index"],
                    "cost_usd": entry["cost_usd"],
                    "z_score": entry["z_score"],
                    "classification": classification,
                }
                # Add timestamp if available
                if entry["index"] < len(self.cost_history):
                    ts = self.cost_history[entry["index"]].get("timestamp")
                    if ts:
                        anomaly["timestamp"] = ts
                anomalies.append(anomaly)

        return anomalies

    def detect_drift(self) -> dict:
        """Detect upward cost drift trend."""
        costs = self.costs
        window = self.DRIFT_WINDOW

        if len(costs) < window * 2:
            return {"detected": False, "reason": "insufficient_data", "data_points": len(costs)}

        early_window = costs[:window]
        late_window = costs[-window:]

        early_mean = sum(early_window) / window
        late_mean = sum(late_window) / window

        if early_mean == 0:
            drift_ratio = 0.0 if late_mean == 0 else float("inf")
        else:
            drift_ratio = late_mean / early_mean

        detected = drift_ratio >= self.DRIFT_FACTOR

        return {
            "detected": detected,
            "early_mean": round(early_mean, 6),
            "late_mean": round(late_mean, 6),
            "drift_ratio": round(drift_ratio, 4),
            "threshold": self.DRIFT_FACTOR,
            "window_size": window,
        }

    def generate_recommendations(self, anomalies: list, drift: dict) -> list:
        """Generate actionable recommendations based on findings."""
        recommendations = []

        critical_count = sum(1 for a in anomalies if a["classification"] == "CRITICAL")
        spike_count = sum(1 for a in anomalies if a["classification"] == "SPIKE")
        warning_count = sum(1 for a in anomalies if a["classification"] == "WARNING")

        if critical_count > 0:
            recommendations.append({
                "priority": "HIGH",
                "action": "INVESTIGATE_CRITICAL_COSTS",
                "detail": f"{critical_count} critical cost anomaly(ies) detected. Investigate root cause immediately.",
            })

        if spike_count > 0:
            recommendations.append({
                "priority": "MEDIUM",
                "action": "REVIEW_SPIKE_PATTERNS",
                "detail": f"{spike_count} cost spike(s) detected. Review if caused by legitimate workload changes.",
            })

        if drift.get("detected"):
            recommendations.append({
                "priority": "MEDIUM",
                "action": "ADDRESS_COST_DRIFT",
                "detail": f"Cost drift detected (ratio {drift['drift_ratio']}x). Baseline is increasing.",
            })

        if warning_count > 0 and not recommendations:
            recommendations.append({
                "priority": "LOW",
                "action": "MONITOR_WARNINGS",
                "detail": f"{warning_count} warning-level anomaly(ies). Continue monitoring.",
            })

        if not recommendations:
            recommendations.append({
                "priority": "NONE",
                "action": "CONTINUE_NORMAL",
                "detail": "No anomalies detected. Cost behavior is within normal bounds.",
            })

        return recommendations

    def analyze(self) -> dict:
        """Run full cost anomaly analysis and produce guard report."""
        statistics = self.compute_statistics()
        anomalies = self.detect_anomalies()
        drift = self.detect_drift()
        recommendations = self.generate_recommendations(anomalies, drift)

        # Determine overall guard status
        critical_count = sum(1 for a in anomalies if a["classification"] == "CRITICAL")
        spike_count = sum(1 for a in anomalies if a["classification"] == "SPIKE")

        if critical_count > 0:
            guard_status = "RED"
        elif spike_count > 0 or drift.get("detected"):
            guard_status = "YELLOW"
        else:
            guard_status = "GREEN"

        return {
            "version": "0.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "r0plus_cost_anomaly_guard_v0_1",
            "guard_status": guard_status,
            "statistics": statistics,
            "anomalies": anomalies,
            "anomaly_counts": {
                "critical": critical_count,
                "spike": spike_count,
                "warning": sum(1 for a in anomalies if a["classification"] == "WARNING"),
                "total": len(anomalies),
            },
            "drift": drift,
            "recommendations": recommendations,
            "config": {
                "threshold_warning": self.threshold_warning,
                "threshold_spike": self.threshold_spike,
                "threshold_critical": self.threshold_critical,
                "drift_factor": self.DRIFT_FACTOR,
                "drift_window": self.DRIFT_WINDOW,
            },
        }


def run(cost_history: list, config: Optional[dict] = None) -> dict:
    """Convenience function to run the guard."""
    guard = CostAnomalyGuard(cost_history, config)
    return guard.analyze()


if __name__ == "__main__":
    # Example with sample data
    sample_history = [
        {"cost_usd": 0.001, "timestamp": "2026-05-01T00:00:00Z"},
        {"cost_usd": 0.0012, "timestamp": "2026-05-02T00:00:00Z"},
        {"cost_usd": 0.0009, "timestamp": "2026-05-03T00:00:00Z"},
        {"cost_usd": 0.0011, "timestamp": "2026-05-04T00:00:00Z"},
        {"cost_usd": 0.005, "timestamp": "2026-05-05T00:00:00Z"},  # spike
        {"cost_usd": 0.001, "timestamp": "2026-05-06T00:00:00Z"},
        {"cost_usd": 0.0013, "timestamp": "2026-05-07T00:00:00Z"},
        {"cost_usd": 0.0008, "timestamp": "2026-05-08T00:00:00Z"},
    ]
    result = run(sample_history)
    print(json.dumps(result, indent=2))
