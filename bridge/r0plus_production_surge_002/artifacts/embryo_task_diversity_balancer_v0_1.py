"""
Embryo Task Diversity Balancer v0.1
Detects task overspecialization in embryo/Memory Palace history and
recommends diversification strategies.

Responsibilities:
  1. Ingest task history (from local JSON fixtures)
  2. Compute task category distribution (entropy-based)
  3. Detect overspecialization (low entropy, dominant category)
  4. Compute Gini coefficient for task distribution
  5. Recommend diversification actions
  6. Produce structured JSON report

Constraints:
  - R0+ only: pure local computation
  - No external API calls
  - No Supabase, no DB, no secrets
  - No network
  - Budget: $0.00

Usage:
    from embryo_task_diversity_balancer_v0_1 import TaskDiversityBalancer
    balancer = TaskDiversityBalancer(task_history)
    report = balancer.analyze()
"""
import json
import math
from collections import Counter
from datetime import datetime, timezone
from typing import Optional


class TaskDiversityBalancer:
    """Detects task overspecialization and recommends diversification."""

    # Entropy thresholds (normalized 0-1)
    ENTROPY_HEALTHY = 0.7  # Above this = healthy diversity
    ENTROPY_WARNING = 0.4  # Between warning and healthy = moderate
    # Below warning = overspecialized

    # Dominance threshold: if any single category > this % = overspecialized
    DOMINANCE_THRESHOLD = 0.6

    # Minimum categories for healthy diversity
    MIN_CATEGORIES = 3

    def __init__(self, task_history: list, config: Optional[dict] = None):
        """
        Args:
            task_history: List of dicts with at least {"category": str, "timestamp": str}
            config: Optional overrides for thresholds
        """
        self.task_history = task_history or []
        self.config = config or {}
        self.entropy_healthy = self.config.get("entropy_healthy", self.ENTROPY_HEALTHY)
        self.entropy_warning = self.config.get("entropy_warning", self.ENTROPY_WARNING)
        self.dominance_threshold = self.config.get("dominance_threshold", self.DOMINANCE_THRESHOLD)

    @property
    def categories(self) -> list:
        """Extract category values from history."""
        return [entry.get("category", "UNKNOWN") for entry in self.task_history]

    def compute_distribution(self) -> dict:
        """Compute category frequency distribution."""
        cats = self.categories
        if not cats:
            return {"categories": {}, "total": 0, "unique_count": 0}

        counter = Counter(cats)
        total = len(cats)
        distribution = {
            cat: {"count": count, "pct": round(count / total, 4)}
            for cat, count in counter.most_common()
        }

        return {
            "categories": distribution,
            "total": total,
            "unique_count": len(counter),
        }

    def compute_entropy(self) -> dict:
        """Compute Shannon entropy (normalized) of task distribution."""
        cats = self.categories
        if not cats:
            return {"raw": 0.0, "normalized": 0.0, "max_possible": 0.0}

        counter = Counter(cats)
        total = len(cats)
        n_categories = len(counter)

        if n_categories <= 1:
            return {"raw": 0.0, "normalized": 0.0, "max_possible": 0.0}

        # Shannon entropy
        entropy = -sum(
            (count / total) * math.log2(count / total)
            for count in counter.values()
        )

        # Max entropy for this number of categories
        max_entropy = math.log2(n_categories)

        # Normalized (0-1)
        normalized = entropy / max_entropy if max_entropy > 0 else 0.0

        return {
            "raw": round(entropy, 4),
            "normalized": round(normalized, 4),
            "max_possible": round(max_entropy, 4),
        }

    def compute_gini(self) -> float:
        """Compute Gini coefficient for task distribution inequality."""
        cats = self.categories
        if not cats:
            return 0.0

        counter = Counter(cats)
        values = sorted(counter.values())
        n = len(values)

        if n <= 1:
            return 0.0

        total = sum(values)
        cumulative = 0
        gini_sum = 0

        for i, v in enumerate(values):
            cumulative += v
            gini_sum += (2 * (i + 1) - n - 1) * v

        gini = gini_sum / (n * total) if total > 0 else 0.0
        return round(gini, 4)

    def detect_overspecialization(self) -> dict:
        """Detect if task distribution indicates overspecialization."""
        distribution = self.compute_distribution()
        entropy = self.compute_entropy()
        gini = self.compute_gini()

        cats = distribution["categories"]
        total = distribution["total"]
        unique = distribution["unique_count"]

        if total == 0:
            return {
                "detected": False,
                "reason": "no_data",
                "severity": "NONE",
            }

        # Check dominance
        dominant_category = None
        dominant_pct = 0.0
        if cats:
            top_cat = list(cats.keys())[0]
            dominant_pct = cats[top_cat]["pct"]
            if dominant_pct >= self.dominance_threshold:
                dominant_category = top_cat

        # Check entropy
        norm_entropy = entropy["normalized"]

        # Determine severity
        if norm_entropy < self.entropy_warning or dominant_pct >= 0.8:
            severity = "HIGH"
            detected = True
        elif norm_entropy < self.entropy_healthy or dominant_category:
            severity = "MEDIUM"
            detected = True
        elif unique < self.MIN_CATEGORIES:
            severity = "LOW"
            detected = True
        else:
            severity = "NONE"
            detected = False

        return {
            "detected": detected,
            "severity": severity,
            "dominant_category": dominant_category,
            "dominant_pct": dominant_pct,
            "normalized_entropy": norm_entropy,
            "gini_coefficient": gini,
            "unique_categories": unique,
            "min_categories_threshold": self.MIN_CATEGORIES,
        }

    def recommend_diversification(self, overspec: dict, distribution: dict) -> list:
        """Generate diversification recommendations."""
        recommendations = []

        if not overspec["detected"]:
            recommendations.append({
                "priority": "NONE",
                "action": "MAINTAIN_CURRENT_MIX",
                "detail": "Task diversity is healthy. Continue current distribution.",
            })
            return recommendations

        severity = overspec["severity"]
        dominant = overspec.get("dominant_category")

        if severity == "HIGH":
            recommendations.append({
                "priority": "HIGH",
                "action": "IMMEDIATE_DIVERSIFICATION",
                "detail": f"Critical overspecialization. {'Category ' + dominant + ' dominates at ' + str(round(overspec['dominant_pct'] * 100, 1)) + '%.' if dominant else 'Entropy critically low.'}",
            })
            recommendations.append({
                "priority": "HIGH",
                "action": "INTRODUCE_NEW_CATEGORIES",
                "detail": "Add at least 2 new task categories in next epoch.",
            })

        if severity == "MEDIUM":
            recommendations.append({
                "priority": "MEDIUM",
                "action": "GRADUAL_REBALANCING",
                "detail": f"Moderate overspecialization detected. Reduce {dominant or 'dominant category'} share below {int(self.dominance_threshold * 100)}%.",
            })

        if severity == "LOW":
            recommendations.append({
                "priority": "LOW",
                "action": "EXPAND_CATEGORY_RANGE",
                "detail": f"Only {overspec['unique_categories']} categories active. Target at least {self.MIN_CATEGORIES}.",
            })

        # Suggest underrepresented categories
        all_possible = {"INFRASTRUCTURE", "TESTING", "PRODUCTION", "ANALYSIS",
                        "DOCUMENTATION", "MONITORING", "SECURITY", "OPTIMIZATION"}
        existing = set(distribution.get("categories", {}).keys())
        missing = all_possible - existing
        if missing:
            recommendations.append({
                "priority": "LOW",
                "action": "EXPLORE_MISSING_CATEGORIES",
                "detail": f"Consider adding: {', '.join(sorted(list(missing)[:3]))}",
            })

        return recommendations

    def analyze(self) -> dict:
        """Run full diversity analysis and produce balancer report."""
        distribution = self.compute_distribution()
        entropy = self.compute_entropy()
        gini = self.compute_gini()
        overspec = self.detect_overspecialization()
        recommendations = self.recommend_diversification(overspec, distribution)

        # Determine overall balancer status
        severity = overspec.get("severity", "NONE")
        if severity == "HIGH":
            balancer_status = "RED"
        elif severity == "MEDIUM":
            balancer_status = "YELLOW"
        else:
            balancer_status = "GREEN"

        return {
            "version": "0.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "embryo_task_diversity_balancer_v0_1",
            "balancer_status": balancer_status,
            "distribution": distribution,
            "entropy": entropy,
            "gini_coefficient": gini,
            "overspecialization": overspec,
            "recommendations": recommendations,
            "config": {
                "entropy_healthy": self.entropy_healthy,
                "entropy_warning": self.entropy_warning,
                "dominance_threshold": self.dominance_threshold,
                "min_categories": self.MIN_CATEGORIES,
            },
        }


def run(task_history: list, config: Optional[dict] = None) -> dict:
    """Convenience function to run the balancer."""
    balancer = TaskDiversityBalancer(task_history, config)
    return balancer.analyze()


if __name__ == "__main__":
    sample_history = [
        {"category": "TESTING", "timestamp": "2026-05-01T00:00:00Z"},
        {"category": "TESTING", "timestamp": "2026-05-02T00:00:00Z"},
        {"category": "TESTING", "timestamp": "2026-05-03T00:00:00Z"},
        {"category": "INFRASTRUCTURE", "timestamp": "2026-05-04T00:00:00Z"},
        {"category": "TESTING", "timestamp": "2026-05-05T00:00:00Z"},
        {"category": "TESTING", "timestamp": "2026-05-06T00:00:00Z"},
    ]
    result = run(sample_history)
    print(json.dumps(result, indent=2))
