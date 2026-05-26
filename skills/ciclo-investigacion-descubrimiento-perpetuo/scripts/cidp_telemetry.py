#!/usr/bin/env python3.11
"""
cidp_telemetry.py — Métricas por iteración.

Trackea tokens, costo, convergencia, tiempo por cada stage y iteración.
Persiste en JSONL para análisis posterior.
"""

import json
import time
from datetime import datetime
from pathlib import Path


class CIDPTelemetry:
    """Telemetry tracking for CIDP runs."""

    def __init__(self, output_dir: Path):
        """Initialize telemetry."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = None
        self.start_time = None
        self.stages = []
        self.total_tokens = 0
        self.total_cost = 0.0

    def start_run(self, run_id: str, target: str, objective: str):
        """Start tracking a new run."""
        self.run_id = run_id
        self.start_time = time.time()
        self._append_event(
            {
                "event": "run_start",
                "run_id": run_id,
                "target": target,
                "objective": objective,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def log_stage(self, stage_name: str, result: dict):
        """Log a stage completion."""
        cost = result.get("cost_usd", 0)
        self.total_cost += cost

        event = {
            "event": "stage_complete",
            "run_id": self.run_id,
            "stage": stage_name,
            "cost_usd": cost,
            "total_cost_usd": self.total_cost,
            "elapsed_seconds": time.time() - self.start_time if self.start_time else 0,
            "timestamp": datetime.now().isoformat(),
        }

        # Extract key metrics based on stage
        if stage_name == "research":
            event["evidence_count"] = result.get("evidence_count", 0)
            event["dimensions_researched"] = result.get("dimensions_researched", 0)
        elif stage_name == "swarm":
            event["responses_count"] = result.get("responses_count", 0)
            event["avg_quality"] = result.get("avg_quality", 0)
        elif stage_name == "validation":
            event["claims_verified"] = result.get("claims_verified", 0)
            event["claims_rejected"] = result.get("claims_rejected", 0)
            event["contradictions"] = result.get("contradictions_found", 0)
        elif stage_name == "convergence":
            event["decision"] = result.get("decision", "unknown")
            event["score"] = result.get("current_score", 0)
            event["score_delta"] = result.get("score_delta", 0)

        self.stages.append(event)
        self._append_event(event)

    def end_run(self, final_report: dict):
        """End tracking for the current run."""
        elapsed = time.time() - self.start_time if self.start_time else 0

        event = {
            "event": "run_end",
            "run_id": self.run_id,
            "status": final_report.get("status", "unknown"),
            "iterations": final_report.get("iterations", 0),
            "final_score": final_report.get("final_score", 0),
            "total_cost_usd": final_report.get("total_cost_usd", 0),
            "elapsed_seconds": elapsed,
            "elapsed_minutes": elapsed / 60,
            "stages_count": len(self.stages),
            "timestamp": datetime.now().isoformat(),
        }

        self._append_event(event)

        # Save summary
        summary_path = self.output_dir / "run_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "run_id": self.run_id,
                    "elapsed_minutes": elapsed / 60,
                    "total_cost_usd": self.total_cost,
                    "stages": self.stages,
                    "final": event,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

    def _append_event(self, event: dict):
        """Append an event to the telemetry log."""
        log_path = self.output_dir / "events.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
