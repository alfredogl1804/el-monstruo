#!/usr/bin/env python3.11
"""
cidp_infra.py — Infrastructure Management.

Deploy, monitor costs, teardown. Manages GPU instances
and tracks infrastructure spending.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent


class InfraManager:
    """Manages infrastructure resources for CIDP."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.active_instances = []
        self.cost_log = []

    def register_instance(self, instance: dict):
        """Register a new active instance."""
        instance["registered_at"] = datetime.now().isoformat()
        instance["status"] = "active"
        self.active_instances.append(instance)
        self._save_state()

    def log_cost(self, provider: str, amount_usd: float, description: str):
        """Log an infrastructure cost."""
        entry = {
            "provider": provider,
            "amount_usd": amount_usd,
            "description": description,
            "timestamp": datetime.now().isoformat(),
        }
        self.cost_log.append(entry)

        # Append to persistent cost tracking
        cost_path = SKILL_DIR / "data" / "cost_tracking.jsonl"
        cost_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cost_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_total_cost(self) -> float:
        """Get total infrastructure cost."""
        return sum(e["amount_usd"] for e in self.cost_log)

    def teardown_all(self) -> list:
        """Teardown all active instances."""
        results = []
        for instance in self.active_instances:
            if instance.get("status") == "active":
                instance["status"] = "torn_down"
                instance["torn_down_at"] = datetime.now().isoformat()
                results.append({
                    "instance": instance.get("instance_id", "unknown"),
                    "provider": instance.get("provider", "unknown"),
                    "status": "torn_down",
                })
        self._save_state()
        return results

    def check_budget(self, budget_usd: float) -> dict:
        """Check if budget is within limits."""
        total = self.get_total_cost()
        remaining = budget_usd - total
        return {
            "total_spent": total,
            "budget": budget_usd,
            "remaining": remaining,
            "percent_used": (total / budget_usd * 100) if budget_usd > 0 else 0,
            "alert": remaining < budget_usd * 0.2,
        }

    def _save_state(self):
        """Save current state to disk."""
        state_path = self.output_dir / "infra_state.json"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({
                "active_instances": self.active_instances,
                "cost_log": self.cost_log,
                "total_cost": self.get_total_cost(),
                "updated_at": datetime.now().isoformat(),
            }, f, indent=2, ensure_ascii=False)
