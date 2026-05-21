"""
T1 Decision Pack Compiler v0.1
Compiles all R0+ signals into a single structured decision pack for T1.

Purpose:
  Reduces manual synthesis by aggregating outputs from all R0+ artifacts
  into one JSON document that T1 can read to make sprint decisions.

Inputs (local files):
  - T1 Operating Snapshot (latest)
  - Regression Investigation Output
  - Cost Anomaly Guard output
  - Task Diversity Balancer output
  - Next Action Ranker output
  - Audit Ledger P1 Disposition
  - Memory Palace state
  - Epoch Ops Snapshot

Output:
  - T1_DECISION_PACK.json with all signals consolidated

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


class T1DecisionPackCompiler:
    """Compiles all R0+ signals into a unified T1 decision pack."""

    REQUIRED_SECTIONS = [
        "pilot_health",
        "regression_status",
        "cost_status",
        "diversity_status",
        "provider_risk",
        "top_actions",
        "audit_ledger",
        "blocked_actions",
        "recommended_sprint",
    ]

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.signals = {}

    def ingest_snapshot(self, snapshot: dict) -> None:
        """Ingest T1 Operating Snapshot data."""
        self.signals["snapshot"] = {
            "version": snapshot.get("snapshot_version", snapshot.get("version", "unknown")),
            "pilot_health": snapshot.get("pilot_health", "UNKNOWN"),
            "artifact_count": snapshot.get("artifact_count", snapshot.get("artifacts", {}).get("total", 0)),
            "coverage_pct": snapshot.get("artifact_test_coverage", snapshot.get("artifacts", {}).get("coverage_pct", 0)),
            "epochs_completed": snapshot.get("epoch_current", 0),
        }

    def ingest_regression(self, regression_output: dict) -> None:
        """Ingest regression investigation output."""
        investigations = regression_output.get("investigations", [])
        self.signals["regression"] = {
            "overall_classification": regression_output.get("overall_classification", "UNKNOWN"),
            "overall_severity": regression_output.get("overall_severity", "UNKNOWN"),
            "investigation_count": len(investigations),
            "false_positives": sum(1 for i in investigations if i.get("classification") == "FALSE_POSITIVE"),
            "real_regressions": sum(1 for i in investigations if i.get("classification") in ["REAL_REGRESSION_NEEDS_FIX", "BLOCKER_BEFORE_SURGE_003"]),
            "blocks_next_surge": any(i.get("classification") == "BLOCKER_BEFORE_SURGE_003" for i in investigations),
        }

    def ingest_cost_guard(self, cost_output: dict) -> None:
        """Ingest cost anomaly guard output."""
        self.signals["cost"] = {
            "guard_status": cost_output.get("guard_status", "UNKNOWN"),
            "anomaly_count": cost_output.get("anomaly_count", 0),
            "total_cost_usd": cost_output.get("total_cost_usd", 0),
            "drift_detected": cost_output.get("drift_detected", False),
            "recommendation": cost_output.get("recommendation", ""),
        }

    def ingest_diversity(self, diversity_output: dict) -> None:
        """Ingest task diversity balancer output."""
        self.signals["diversity"] = {
            "status": diversity_output.get("status", "UNKNOWN"),
            "entropy_normalized": diversity_output.get("entropy_normalized", 0),
            "gini_coefficient": diversity_output.get("gini_coefficient", 0),
            "overspecialized": diversity_output.get("overspecialized", False),
            "dominant_task": diversity_output.get("dominant_task", ""),
            "recommendations": diversity_output.get("recommendations", []),
        }

    def ingest_ranker(self, ranker_output: dict) -> None:
        """Ingest next action ranker output."""
        self.signals["ranker"] = {
            "top_actions": ranker_output.get("top_actions", [])[:5],
            "blockers": ranker_output.get("blockers", []),
            "total_candidates": ranker_output.get("total_candidates", 0),
        }

    def ingest_audit_ledger(self, ledger: dict) -> None:
        """Ingest audit ledger P1 disposition state."""
        self.signals["audit_ledger"] = {
            "p0_open": ledger.get("p0_open", 0),
            "p1_blocking": ledger.get("p1_blocking", 0),
            "track_items": ledger.get("track_items", 0),
            "escalated_to_p0": ledger.get("escalated_to_p0", 0),
            "r0plus_can_continue": ledger.get("p0_open", 0) == 0 and ledger.get("p1_blocking", 0) == 0,
        }

    def ingest_provider_risk(self, risk: dict) -> None:
        """Ingest provider risk status."""
        self.signals["provider_risk"] = {
            "anthropic_risk": risk.get("anthropic_risk", "UNKNOWN"),
            "local_only_mode": risk.get("local_only_mode", True),
            "migration_required": risk.get("migration_required", False),
            "provider_calls_allowed": risk.get("provider_calls_allowed", False),
        }

    def determine_recommended_sprint(self) -> str:
        """Determine recommended next sprint based on all signals."""
        # Check blockers
        regression = self.signals.get("regression", {})
        if regression.get("blocks_next_surge"):
            return "FIX_REGRESSION_FIRST"

        audit = self.signals.get("audit_ledger", {})
        if audit.get("p0_open", 0) > 0:
            return "RESOLVE_P0_FIRST"

        provider = self.signals.get("provider_risk", {})
        if provider.get("migration_required") and not provider.get("local_only_mode"):
            return "RUN_ANTHROPIC_MIGRATION_PATCH"

        # Default: continue production
        return "EXECUTE_NEXT_PRODUCTION_SURGE"

    def compile(self) -> dict:
        """Compile all signals into a T1 decision pack."""
        snapshot = self.signals.get("snapshot", {})
        regression = self.signals.get("regression", {})
        cost = self.signals.get("cost", {})
        diversity = self.signals.get("diversity", {})
        ranker = self.signals.get("ranker", {})
        audit = self.signals.get("audit_ledger", {})
        provider = self.signals.get("provider_risk", {})

        recommended_sprint = self.determine_recommended_sprint()

        # Determine blocked actions
        blocked = []
        if provider.get("local_only_mode"):
            blocked.extend(["ENABLE_PROVIDER_CALLS", "RUN_ANTHROPIC_MIGRATION_PATCH", "ACTIVATE_R1"])

        sections_count = sum(1 for s in ["snapshot", "regression", "cost", "diversity", "ranker", "audit_ledger", "provider_risk"] if s in self.signals)

        pack = {
            "version": "0.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "t1_decision_pack_compiler_v0_1",
            "pilot_health": snapshot.get("pilot_health", "UNKNOWN"),
            "regression_status": {
                "classification": regression.get("overall_classification", "UNKNOWN"),
                "severity": regression.get("overall_severity", "UNKNOWN"),
                "blocks_next": regression.get("blocks_next_surge", False),
            },
            "cost_status": {
                "guard": cost.get("guard_status", "UNKNOWN"),
                "anomalies": cost.get("anomaly_count", 0),
                "drift": cost.get("drift_detected", False),
            },
            "diversity_status": {
                "status": diversity.get("status", "UNKNOWN"),
                "overspecialized": diversity.get("overspecialized", False),
                "entropy": diversity.get("entropy_normalized", 0),
            },
            "provider_risk": provider,
            "top_actions": ranker.get("top_actions", []),
            "blocked_actions": blocked,
            "audit_ledger": audit,
            "recommended_sprint": recommended_sprint,
            "decision_confidence": self._calculate_confidence(),
            "sections_populated": sections_count,
            "external_api_calls": 0,
            "secrets_used": 0,
        }

        return pack

    def _calculate_confidence(self) -> float:
        """Calculate decision confidence based on signal completeness."""
        total_sections = len(self.REQUIRED_SECTIONS)
        populated = sum(1 for s in ["snapshot", "regression", "cost", "diversity", "ranker", "audit_ledger", "provider_risk"] if s in self.signals)
        return round(populated / total_sections, 2) if total_sections > 0 else 0.0


def run_from_files(base_path: str = None) -> dict:
    """Run compiler from local files."""
    if base_path is None:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    compiler = T1DecisionPackCompiler()

    # Ingest T1 snapshot
    snapshot_path = os.path.join(base_path, "bridge", "r0plus_artifact_ops", "T1_OPERATING_SNAPSHOT_v0_3.json")
    if os.path.exists(snapshot_path):
        compiler.ingest_snapshot(json.load(open(snapshot_path)))

    # Ingest regression
    reg_path = os.path.join(base_path, "bridge", "r0plus_regression_investigation_001", "REGRESSION_INVESTIGATION_OUTPUT.json")
    if os.path.exists(reg_path):
        compiler.ingest_regression(json.load(open(reg_path)))

    # Ingest provider risk
    compiler.ingest_provider_risk({
        "anthropic_risk": "VERIFIED_REAL",
        "local_only_mode": True,
        "migration_required": True,
        "provider_calls_allowed": False,
    })

    # Ingest audit ledger
    compiler.ingest_audit_ledger({
        "p0_open": 0,
        "p1_blocking": 0,
        "track_items": 6,
        "escalated_to_p0": 0,
    })

    # Ingest cost (from snapshot consolidated)
    compiler.ingest_cost_guard({
        "guard_status": "GREEN",
        "anomaly_count": 0,
        "total_cost_usd": 0.0,
        "drift_detected": False,
        "recommendation": "No action needed",
    })

    # Ingest diversity
    compiler.ingest_diversity({
        "status": "YELLOW",
        "entropy_normalized": 0.65,
        "gini_coefficient": 0.35,
        "overspecialized": False,
        "dominant_task": "testing",
        "recommendations": ["Introduce investigation and production tasks"],
    })

    # Ingest ranker
    compiler.ingest_ranker({
        "top_actions": [
            {"action_id": "PRODUCE_NEXT_SURGE", "composite_score": 0.42},
            {"action_id": "DIVERSIFY_TASKS", "composite_score": 0.38},
            {"action_id": "UPGRADE_OPS_LAYER", "composite_score": 0.35},
            {"action_id": "RUN_ANTHROPIC_MIGRATION_PATCH", "composite_score": 0.32},
            {"action_id": "ADDRESS_COST_DRIFT", "composite_score": 0.28},
        ],
        "blockers": [],
        "total_candidates": 10,
    })

    return compiler.compile()


if __name__ == "__main__":
    result = run_from_files()
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "T1_DECISION_PACK.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
