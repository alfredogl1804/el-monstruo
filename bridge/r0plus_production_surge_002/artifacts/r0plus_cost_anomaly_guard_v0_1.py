"""
R0+ Cost Anomaly Guard v0.1

Detects cost anomalies and regressions in runs/epochs/embryos.
Reads local snapshots and chain logs. Calculates z-score, delta vs baseline,
cost_per_run, cost_per_artifact. Detects cost spikes. Marks severity.
Recommends action: TRACK / REVIEW / FREEZE_CANDIDATE.

No external API calls. No state modification. Pure local computation.

Usage:
    python3 r0plus_cost_anomaly_guard_v0_1.py [--base-dir /path]
"""
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def load_cost_data(base_dir: Path) -> dict:
    """Load cost data from chain logs and snapshots."""
    costs = []
    # Scan epoch chain logs for cost entries
    reactor_dir = base_dir / "bridge" / "reactor_limited_active_r0"
    if reactor_dir.exists():
        for epoch_dir in sorted(reactor_dir.iterdir()):
            if epoch_dir.is_dir() and "epoch" in epoch_dir.name:
                chain_log = epoch_dir / f"{epoch_dir.name.upper().replace('LIVE_UPGRADE_', '')}_CHAIN_LOG.jsonl"
                if chain_log.exists():
                    for line in chain_log.read_text(encoding="utf-8").strip().split("\n"):
                        try:
                            entry = json.loads(line)
                            if "cost" in entry.get("event", "").lower() or entry.get("event") in [
                                "EPOCH_005_COMPLETED", "EPOCH_006_COMPLETED", "EPOCH_007_COMPLETED",
                                "EPOCH_008_COMPLETED", "EPOCH_009_COMPLETED"
                            ]:
                                cost = entry.get("cost_usd", entry.get("cost", 0))
                                if cost is not None:
                                    costs.append({"epoch": epoch_dir.name, "cost_usd": float(cost), "event": entry.get("event")})
                        except (json.JSONDecodeError, ValueError):
                            continue

    # Read Memory Palace for cost entries
    mp_path = base_dir / "embryos" / "memory_palace" / "memory_palace_state.json"
    if mp_path.exists():
        try:
            mp_data = json.loads(mp_path.read_text(encoding="utf-8"))
            for entry in mp_data.get("entries", []):
                if "cost" in str(entry.get("metrics", {})):
                    cost = entry.get("metrics", {}).get("cost_usd", 0)
                    if cost:
                        costs.append({"epoch": entry.get("epoch", "unknown"), "cost_usd": float(cost), "event": "MEMORY_PALACE_ENTRY"})
        except (json.JSONDecodeError, IOError):
            pass

    return {"costs": costs, "total_entries": len(costs)}


def calculate_statistics(costs: list) -> dict:
    """Calculate mean, std, z-scores for cost data."""
    if not costs:
        return {"mean": 0, "std": 0, "count": 0, "z_scores": []}

    values = [c["cost_usd"] for c in costs]
    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n if n > 1 else 0
    std = math.sqrt(variance)

    z_scores = []
    for i, c in enumerate(costs):
        z = (c["cost_usd"] - mean) / std if std > 0 else 0
        z_scores.append({
            "index": i,
            "epoch": c["epoch"],
            "cost_usd": c["cost_usd"],
            "z_score": round(z, 4),
        })

    return {"mean": round(mean, 6), "std": round(std, 6), "count": n, "z_scores": z_scores}


def detect_anomalies(stats: dict, threshold: float = 2.0) -> list:
    """Detect cost anomalies based on z-score threshold."""
    anomalies = []
    for entry in stats.get("z_scores", []):
        if abs(entry["z_score"]) >= threshold:
            anomalies.append({
                "epoch": entry["epoch"],
                "cost_usd": entry["cost_usd"],
                "z_score": entry["z_score"],
                "direction": "SPIKE" if entry["z_score"] > 0 else "DROP",
            })
    return anomalies


def detect_cost_spike(costs: list, spike_multiplier: float = 3.0) -> list:
    """Detect cost spikes (run N is spike_multiplier times more expensive than average of previous runs)."""
    spikes = []
    if len(costs) < 2:
        return spikes

    for i in range(1, len(costs)):
        prev_costs = [c["cost_usd"] for c in costs[:i]]
        prev_avg = sum(prev_costs) / len(prev_costs) if prev_costs else 0
        current = costs[i]["cost_usd"]
        if prev_avg > 0 and current > prev_avg * spike_multiplier:
            spikes.append({
                "index": i,
                "epoch": costs[i]["epoch"],
                "cost_usd": current,
                "prev_avg": round(prev_avg, 6),
                "multiplier": round(current / prev_avg, 2),
            })
    return spikes


def calculate_cost_per_run(costs: list) -> float:
    """Calculate average cost per run."""
    if not costs:
        return 0.0
    return round(sum(c["cost_usd"] for c in costs) / len(costs), 6)


def calculate_cost_per_artifact(total_cost: float, artifact_count: int) -> float:
    """Calculate cost per artifact."""
    if artifact_count <= 0:
        return 0.0
    return round(total_cost / artifact_count, 6)


def determine_severity(anomalies: list, spikes: list) -> str:
    """Determine overall severity."""
    if not anomalies and not spikes:
        return "LOW"
    max_z = max((abs(a["z_score"]) for a in anomalies), default=0)
    max_mult = max((s["multiplier"] for s in spikes), default=0)
    if max_z >= 3.0 or max_mult >= 5.0:
        return "HIGH"
    if max_z >= 2.0 or max_mult >= 3.0:
        return "MEDIUM"
    return "LOW"


def recommend_action(severity: str, anomalies: list, spikes: list) -> str:
    """Recommend action based on findings."""
    if severity == "HIGH":
        return "FREEZE_CANDIDATE"
    if severity == "MEDIUM":
        return "REVIEW"
    return "TRACK"


def run_guard(base_dir: Optional[Path] = None) -> dict:
    """Main entry point: run the full cost anomaly guard."""
    if base_dir is None:
        base_dir = Path(__file__).parents[3]

    cost_data = load_cost_data(base_dir)
    stats = calculate_statistics(cost_data["costs"])
    anomalies = detect_anomalies(stats)
    spikes = detect_cost_spike(cost_data["costs"])
    cost_per_run = calculate_cost_per_run(cost_data["costs"])
    total_cost = sum(c["cost_usd"] for c in cost_data["costs"])
    cost_per_artifact = calculate_cost_per_artifact(total_cost, 11)
    severity = determine_severity(anomalies, spikes)
    action = recommend_action(severity, anomalies, spikes)

    return {
        "artifact": "r0plus_cost_anomaly_guard_v0_1",
        "version": "0.1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cost_data": {
            "total_entries": cost_data["total_entries"],
            "mean_cost_usd": stats["mean"],
            "std_cost_usd": stats["std"],
            "cost_per_run": cost_per_run,
            "cost_per_artifact": cost_per_artifact,
            "total_cost_usd": round(total_cost, 6),
        },
        "anomalies": anomalies,
        "spikes": spikes,
        "severity": severity,
        "recommended_action": action,
        "external_api_calls": 0,
        "secrets_used": 0,
        "state_modified": False,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="R0+ Cost Anomaly Guard v0.1")
    parser.add_argument("--base-dir", default=None)
    args = parser.parse_args()
    base = Path(args.base_dir) if args.base_dir else None
    result = run_guard(base)
    print(json.dumps(result, indent=2, default=str))
