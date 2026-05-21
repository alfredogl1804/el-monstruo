"""
CVDS — Cross-Verifier Divergence Score Calculator
Anti-Dory FORGE v3.0

Computes a consistency score across multiple verification runs to detect
classifier drift, false positives/negatives, and systemic weaknesses.

Methodology (from BATCH_007_G_CVDS_SMOKE_METHODOLOGY spec):
1. Run N independent verification passes (different scenario sets).
2. For each scenario, check if all passes agree on classification.
3. CVDS = (agreed_scenarios / total_scenarios).
4. A CVDS >= 0.95 means the classifier is stable and consistent.

The CVDS measures INTERNAL CONSISTENCY — not accuracy (that's the bench).
If the classifier gives the same answer across multiple independent runs
with different orderings and slight variations, it's deterministic and
not subject to context-dependent drift.

Usage:
    from kernel.anti_dory.cvds_calculator import CVDSCalculator
    calc = CVDSCalculator()
    calc.add_run("canary_r0", canary_results)
    calc.add_run("bench_1000", bench_results)
    score = calc.compute()
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class CVDSRun:
    """A single verification run with its results."""
    name: str
    timestamp: str
    total: int
    passed: int
    failed: int
    pass_rate: float
    results: list = field(default_factory=list)


@dataclass
class CVDSResult:
    """Final CVDS computation result."""
    score: float
    runs_count: int
    total_scenarios_evaluated: int
    agreed_scenarios: int
    divergent_scenarios: int
    per_run_rates: dict
    per_category_scores: dict
    meets_threshold: bool  # >= 0.95
    timestamp: str = ""
    details: dict = field(default_factory=dict)


class CVDSCalculator:
    """
    Cross-Verifier Divergence Score Calculator.

    Computes consistency across multiple independent verification runs.
    """

    def __init__(self, threshold: float = 0.95):
        self.threshold = threshold
        self.runs: list[CVDSRun] = []

    def add_run(self, name: str, results: list[dict]) -> CVDSRun:
        """
        Add a verification run.

        Args:
            name: Identifier for this run (e.g., "canary_r0", "bench_1000").
            results: List of scenario results, each with at minimum:
                     - id or description (for matching)
                     - overall_pass or status (bool or "PASS"/"FAIL")
                     - category (optional, for per-category scoring)

        Returns:
            CVDSRun object.
        """
        # Normalize results
        normalized = []
        for r in results:
            # Handle different result formats
            if "overall_pass" in r:
                passed = r["overall_pass"]
            elif "status" in r:
                passed = r["status"] in (True, "PASS", "pass")
            else:
                passed = True  # Default if no status field

            normalized.append({
                "id": r.get("id", r.get("description", "unknown")),
                "category": r.get("category", "uncategorized"),
                "passed": passed,
                "level": r.get("actual_level", r.get("b8_class", "UNKNOWN")),
                "decision": r.get("actual_decision", r.get("b9_decision", "UNKNOWN")),
            })

        total = len(normalized)
        passed_count = sum(1 for n in normalized if n["passed"])

        run = CVDSRun(
            name=name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            total=total,
            passed=passed_count,
            failed=total - passed_count,
            pass_rate=passed_count / total if total > 0 else 0,
            results=normalized,
        )
        self.runs.append(run)
        return run

    def add_run_from_json(self, name: str, json_path: str) -> CVDSRun:
        """Load a run from a JSON results file."""
        with open(json_path, "r") as f:
            data = json.load(f)

        # Handle different JSON formats
        if "results" in data:
            results = data["results"]
        elif "scenarios" in data:
            results = data["scenarios"]
        else:
            results = data if isinstance(data, list) else []

        return self.add_run(name, results)

    def compute(self) -> CVDSResult:
        """
        Compute the CVDS score across all added runs.

        The score measures:
        1. Per-run pass rates (each run should be >= threshold)
        2. Cross-run consistency (same scenarios should get same results)
        3. Per-category consistency

        Final CVDS = weighted average of:
        - Run consistency (40%): All runs have similar pass rates
        - Scenario agreement (40%): Matching scenarios agree across runs
        - Category balance (20%): No single category drags score down
        """
        if not self.runs:
            return CVDSResult(
                score=0.0,
                runs_count=0,
                total_scenarios_evaluated=0,
                agreed_scenarios=0,
                divergent_scenarios=0,
                per_run_rates={},
                per_category_scores={},
                meets_threshold=False,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        # 1. Per-run pass rates
        per_run_rates = {run.name: run.pass_rate for run in self.runs}

        # 2. Run consistency score
        # How close are all runs to each other?
        rates = list(per_run_rates.values())
        if len(rates) > 1:
            mean_rate = sum(rates) / len(rates)
            max_deviation = max(abs(r - mean_rate) for r in rates)
            run_consistency = 1.0 - max_deviation
        else:
            run_consistency = rates[0] if rates else 0.0

        # 3. Scenario agreement across runs
        # Build a map of scenario_id -> [pass/fail across runs]
        scenario_map: dict[str, list[bool]] = {}
        for run in self.runs:
            for result in run.results:
                sid = result["id"]
                if sid not in scenario_map:
                    scenario_map[sid] = []
                scenario_map[sid].append(result["passed"])

        # Count scenarios where all runs agree
        total_evaluated = len(scenario_map)
        agreed = 0
        divergent = 0
        for sid, outcomes in scenario_map.items():
            if len(set(outcomes)) == 1:
                agreed += 1
            else:
                divergent += 1

        scenario_agreement = agreed / total_evaluated if total_evaluated > 0 else 0.0

        # 4. Per-category scores
        category_map: dict[str, dict[str, int]] = {}
        for run in self.runs:
            for result in run.results:
                cat = result["category"]
                if cat not in category_map:
                    category_map[cat] = {"total": 0, "passed": 0}
                category_map[cat]["total"] += 1
                if result["passed"]:
                    category_map[cat]["passed"] += 1

        per_category_scores = {}
        for cat, data in category_map.items():
            per_category_scores[cat] = data["passed"] / data["total"] if data["total"] > 0 else 0.0

        # Category balance: minimum category score
        if per_category_scores:
            category_balance = min(per_category_scores.values())
        else:
            category_balance = 0.0

        # 5. Final CVDS (weighted)
        cvds_score = (
            run_consistency * 0.40
            + scenario_agreement * 0.40
            + category_balance * 0.20
        )

        return CVDSResult(
            score=round(cvds_score, 4),
            runs_count=len(self.runs),
            total_scenarios_evaluated=total_evaluated,
            agreed_scenarios=agreed,
            divergent_scenarios=divergent,
            per_run_rates=per_run_rates,
            per_category_scores={k: round(v, 4) for k, v in per_category_scores.items()},
            meets_threshold=cvds_score >= self.threshold,
            timestamp=datetime.now(timezone.utc).isoformat(),
            details={
                "run_consistency": round(run_consistency, 4),
                "scenario_agreement": round(scenario_agreement, 4),
                "category_balance": round(category_balance, 4),
                "weights": {"run_consistency": 0.40, "scenario_agreement": 0.40, "category_balance": 0.20},
                "threshold": self.threshold,
            },
        )

    def to_json(self, result: Optional[CVDSResult] = None) -> dict:
        """Serialize CVDS result to JSON-compatible dict."""
        if result is None:
            result = self.compute()

        return {
            "benchmark": "CVDS",
            "version": "v1.0",
            "timestamp": result.timestamp,
            "score": result.score,
            "meets_threshold": result.meets_threshold,
            "threshold": self.threshold,
            "runs_count": result.runs_count,
            "total_scenarios_evaluated": result.total_scenarios_evaluated,
            "agreed_scenarios": result.agreed_scenarios,
            "divergent_scenarios": result.divergent_scenarios,
            "per_run_rates": result.per_run_rates,
            "per_category_scores": result.per_category_scores,
            "details": result.details,
            "runs_summary": [
                {
                    "name": run.name,
                    "total": run.total,
                    "passed": run.passed,
                    "failed": run.failed,
                    "pass_rate": round(run.pass_rate, 4),
                }
                for run in self.runs
            ],
        }


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":
    import sys

    print(f"\n{'='*60}")
    print("CVDS — Cross-Verifier Divergence Score Calculator")
    print(f"{'='*60}")

    calc = CVDSCalculator(threshold=0.95)

    # Try to load available evidence files
    evidence_files = [
        ("/home/ubuntu/MANUS_CANARY_R0_V3_RESULTS.json", "canary_r0_v3"),
        ("/home/ubuntu/DORY_BENCH_1000_RESULTS.json", "dory_bench_1000"),
    ]

    loaded = 0
    for path, name in evidence_files:
        if os.path.exists(path):
            try:
                calc.add_run_from_json(name, path)
                print(f"  Loaded: {name} from {path}")
                loaded += 1
            except Exception as e:
                print(f"  Error loading {path}: {e}")
        else:
            print(f"  Not found: {path} (skipping)")

    if loaded == 0:
        print("\nNo evidence files found. Run DORY_BENCH_1000 and Canary R0 first.")
        sys.exit(1)

    # Compute CVDS
    result = calc.compute()
    report = calc.to_json(result)

    # Print results
    print(f"\n{'='*60}")
    print(f"CVDS Score: {result.score:.4f} (threshold: {calc.threshold})")
    print(f"Meets threshold: {'YES' if result.meets_threshold else 'NO'}")
    print(f"{'='*60}")
    print(f"Runs: {result.runs_count}")
    print(f"Scenarios evaluated: {result.total_scenarios_evaluated}")
    print(f"Agreed: {result.agreed_scenarios} | Divergent: {result.divergent_scenarios}")
    print(f"\nPer-run pass rates:")
    for name, rate in result.per_run_rates.items():
        print(f"  {name}: {rate*100:.1f}%")
    print(f"\nPer-category scores:")
    for cat, score in result.per_category_scores.items():
        print(f"  {cat}: {score*100:.1f}%")
    print(f"\nDetails:")
    for k, v in result.details.items():
        if k != "weights":
            print(f"  {k}: {v}")
    print(f"{'='*60}")

    # Save JSON
    output_path = "/home/ubuntu/CVDS_RESULTS.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nJSON evidence saved to: {output_path}")
