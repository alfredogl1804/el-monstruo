"""
Epoch Next Action Ranker v0.1
Ranks and prioritizes next actions for the R0+ pilot based on
multi-signal scoring: health state, risks, directives, coverage gaps,
and operational maturity.

Responsibilities:
  1. Ingest signals from epoch ops snapshot, cost guard, diversity balancer
  2. Score each candidate action using weighted multi-criteria
  3. Rank actions by composite score
  4. Produce top-N ranked action list with justification
  5. Detect blocking dependencies between actions

Constraints:
  - R0+ only: pure local computation
  - No external API calls
  - No Supabase, no DB, no secrets
  - No network
  - Budget: $0.00

Usage:
    from epoch_next_action_ranker_v0_1 import NextActionRanker
    ranker = NextActionRanker(signals)
    ranked = ranker.rank()
"""
import json
from datetime import datetime, timezone
from typing import Optional


# Canonical action catalog
ACTION_CATALOG = {
    "PRODUCE_NEXT_SURGE": {
        "description": "Produce new R0+ artifacts in next production surge",
        "base_priority": 5,
        "category": "PRODUCTION",
    },
    "INVESTIGATE_REGRESSION": {
        "description": "Investigate regression flags in embryo history",
        "base_priority": 7,
        "category": "INVESTIGATION",
    },
    "REMEDIATE_COVERAGE": {
        "description": "Add tests for untested artifacts",
        "base_priority": 8,
        "category": "TESTING",
    },
    "ADDRESS_COST_DRIFT": {
        "description": "Investigate and mitigate cost drift trend",
        "base_priority": 6,
        "category": "MONITORING",
    },
    "DIVERSIFY_TASKS": {
        "description": "Introduce new task categories to reduce overspecialization",
        "base_priority": 4,
        "category": "OPTIMIZATION",
    },
    "MONITOR_PROVIDER_EOL": {
        "description": "Monitor provider deprecation and plan migration",
        "base_priority": 3,
        "category": "MONITORING",
    },
    "UPGRADE_OPS_LAYER": {
        "description": "Upgrade artifact ops layer with new capabilities",
        "base_priority": 4,
        "category": "INFRASTRUCTURE",
    },
    "MERGE_TO_MAIN": {
        "description": "Prepare and execute merge to main branch",
        "base_priority": 2,
        "category": "GOVERNANCE",
    },
    "SECURITY_AUDIT": {
        "description": "Run security audit on all artifacts",
        "base_priority": 6,
        "category": "SECURITY",
    },
    "MEMORY_PALACE_CLEANUP": {
        "description": "Clean up Memory Palace patterns and optimize storage",
        "base_priority": 3,
        "category": "OPTIMIZATION",
    },
}

# Scoring weights
WEIGHTS = {
    "health_urgency": 0.30,
    "risk_severity": 0.25,
    "directive_alignment": 0.20,
    "coverage_impact": 0.15,
    "maturity_contribution": 0.10,
}


class NextActionRanker:
    """Ranks next actions based on multi-signal scoring."""

    def __init__(self, signals: dict, config: Optional[dict] = None):
        """
        Args:
            signals: Dict with keys:
                - epoch_health: dict (overall, artifact_health, etc.)
                - risks: list of risk dicts
                - directives: list of active directive dicts
                - coverage_pct: float
                - cost_guard_status: str (GREEN/YELLOW/RED)
                - diversity_status: str (GREEN/YELLOW/RED)
                - epochs_completed: int
            config: Optional overrides for weights
        """
        self.signals = signals or {}
        self.config = config or {}
        self.weights = self.config.get("weights", WEIGHTS)

    def _health_urgency_score(self, action_id: str) -> float:
        """Score based on current health state urgency."""
        health = self.signals.get("epoch_health", {})
        overall = health.get("overall", "GREEN")

        # Map health to urgency multiplier
        urgency_map = {"RED": 1.0, "YELLOW": 0.6, "GREEN": 0.2}
        urgency = urgency_map.get(overall, 0.2)

        # Actions that address health issues get higher scores
        health_actions = {"INVESTIGATE_REGRESSION", "REMEDIATE_COVERAGE", "SECURITY_AUDIT"}
        if action_id in health_actions and overall != "GREEN":
            return urgency * 1.5
        return urgency * 0.5

    def _risk_severity_score(self, action_id: str) -> float:
        """Score based on how well action addresses current risks."""
        risks = self.signals.get("risks", [])
        if not risks:
            return 0.1

        # Map actions to risk types they address
        action_risk_map = {
            "INVESTIGATE_REGRESSION": ["regression"],
            "ADDRESS_COST_DRIFT": ["cost", "anomaly", "drift"],
            "DIVERSIFY_TASKS": ["overspecialization", "diversity"],
            "REMEDIATE_COVERAGE": ["coverage", "untested"],
            "SECURITY_AUDIT": ["security", "secrets"],
            "MONITOR_PROVIDER_EOL": ["provider", "deprecation"],
        }

        addressed_keywords = action_risk_map.get(action_id, [])
        if not addressed_keywords:
            return 0.1

        # Check if any risk matches
        severity_scores = {"HIGH": 1.0, "MEDIUM": 0.6, "LOW": 0.3, "NONE": 0.0}
        max_match_score = 0.0

        for risk in risks:
            risk_text = risk.get("risk", "").lower()
            risk_severity = severity_scores.get(risk.get("severity", "NONE"), 0.0)
            if any(kw in risk_text for kw in addressed_keywords):
                max_match_score = max(max_match_score, risk_severity)

        return max_match_score

    def _directive_alignment_score(self, action_id: str) -> float:
        """Score based on alignment with active T1 directives."""
        directives = self.signals.get("directives", [])
        if not directives:
            return 0.3  # Neutral if no directives

        # Map directive types to actions
        type_action_map = {
            "STRATEGIC_GUIDANCE": {"PRODUCE_NEXT_SURGE", "MERGE_TO_MAIN", "UPGRADE_OPS_LAYER"},
            "PRODUCTIVITY": {"PRODUCE_NEXT_SURGE", "DIVERSIFY_TASKS", "UPGRADE_OPS_LAYER"},
            "SAFETY": {"SECURITY_AUDIT", "INVESTIGATE_REGRESSION", "REMEDIATE_COVERAGE"},
            "MONITORING": {"MONITOR_PROVIDER_EOL", "ADDRESS_COST_DRIFT"},
        }

        max_alignment = 0.0
        for directive in directives:
            d_type = directive.get("directive_type", "")
            aligned_actions = type_action_map.get(d_type, set())
            if action_id in aligned_actions:
                priority = directive.get("priority", 5) / 10.0
                max_alignment = max(max_alignment, priority)

        return max_alignment

    def _coverage_impact_score(self, action_id: str) -> float:
        """Score based on coverage improvement potential."""
        coverage = self.signals.get("coverage_pct", 100.0)

        if coverage >= 100:
            # Coverage is perfect, testing actions less valuable
            if action_id == "REMEDIATE_COVERAGE":
                return 0.0
            return 0.3
        else:
            # Coverage gap exists
            gap = 100 - coverage
            if action_id == "REMEDIATE_COVERAGE":
                return min(gap / 50.0, 1.0)
            return 0.2

    def _maturity_contribution_score(self, action_id: str) -> float:
        """Score based on contribution to operational maturity."""
        epochs = self.signals.get("epochs_completed", 0)

        # Early epochs: infrastructure and testing more valuable
        # Later epochs: production and optimization more valuable
        if epochs < 5:
            early_actions = {"REMEDIATE_COVERAGE", "UPGRADE_OPS_LAYER", "SECURITY_AUDIT"}
            return 0.8 if action_id in early_actions else 0.3
        else:
            late_actions = {"PRODUCE_NEXT_SURGE", "DIVERSIFY_TASKS", "MERGE_TO_MAIN"}
            return 0.8 if action_id in late_actions else 0.4

    def score_action(self, action_id: str) -> dict:
        """Compute composite score for a single action."""
        scores = {
            "health_urgency": self._health_urgency_score(action_id),
            "risk_severity": self._risk_severity_score(action_id),
            "directive_alignment": self._directive_alignment_score(action_id),
            "coverage_impact": self._coverage_impact_score(action_id),
            "maturity_contribution": self._maturity_contribution_score(action_id),
        }

        # Weighted composite
        composite = sum(
            scores[dim] * self.weights[dim]
            for dim in scores
        )

        # Add base priority bonus (normalized 0-1)
        base_priority = ACTION_CATALOG.get(action_id, {}).get("base_priority", 5) / 10.0
        composite = composite * 0.7 + base_priority * 0.3

        return {
            "action_id": action_id,
            "composite_score": round(composite, 4),
            "dimension_scores": {k: round(v, 4) for k, v in scores.items()},
            "base_priority": ACTION_CATALOG.get(action_id, {}).get("base_priority", 5),
            "category": ACTION_CATALOG.get(action_id, {}).get("category", "UNKNOWN"),
            "description": ACTION_CATALOG.get(action_id, {}).get("description", ""),
        }

    def detect_blockers(self, ranked_actions: list) -> list:
        """Detect blocking dependencies between actions."""
        blockers = []

        # Define blocking relationships
        blocking_rules = {
            "MERGE_TO_MAIN": ["REMEDIATE_COVERAGE", "SECURITY_AUDIT"],
            "PRODUCE_NEXT_SURGE": [],
            "INVESTIGATE_REGRESSION": [],
        }

        action_ids = [a["action_id"] for a in ranked_actions]

        for action_id, prerequisites in blocking_rules.items():
            if action_id in action_ids:
                for prereq in prerequisites:
                    if prereq in action_ids:
                        action_rank = action_ids.index(action_id)
                        prereq_rank = action_ids.index(prereq)
                        if action_rank < prereq_rank:
                            blockers.append({
                                "action": action_id,
                                "blocked_by": prereq,
                                "reason": f"{prereq} should complete before {action_id}",
                            })

        return blockers

    def rank(self, top_n: int = 5) -> dict:
        """Rank all candidate actions and return top N."""
        scored_actions = []
        for action_id in ACTION_CATALOG:
            scored = self.score_action(action_id)
            scored_actions.append(scored)

        # Sort by composite score descending
        scored_actions.sort(key=lambda x: x["composite_score"], reverse=True)

        top_actions = scored_actions[:top_n]
        blockers = self.detect_blockers(top_actions)

        return {
            "version": "0.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "epoch_next_action_ranker_v0_1",
            "signals_used": list(self.signals.keys()),
            "top_actions": top_actions,
            "blockers": blockers,
            "total_candidates": len(ACTION_CATALOG),
            "ranking_weights": self.weights,
        }


def run(signals: dict, config: Optional[dict] = None, top_n: int = 5) -> dict:
    """Convenience function to run the ranker."""
    ranker = NextActionRanker(signals, config)
    return ranker.rank(top_n)


if __name__ == "__main__":
    sample_signals = {
        "epoch_health": {"overall": "GREEN"},
        "risks": [
            {"risk": "1 regression flag in embryo history", "severity": "MEDIUM"},
            {"risk": "1 cost anomaly detected", "severity": "LOW"},
            {"risk": "task overspecialization in Memory Palace", "severity": "LOW"},
        ],
        "directives": [
            {"directive_type": "STRATEGIC_GUIDANCE", "priority": 8},
            {"directive_type": "PRODUCTIVITY", "priority": 5},
        ],
        "coverage_pct": 100.0,
        "cost_guard_status": "GREEN",
        "diversity_status": "YELLOW",
        "epochs_completed": 9,
    }
    result = run(sample_signals)
    print(json.dumps(result, indent=2))
