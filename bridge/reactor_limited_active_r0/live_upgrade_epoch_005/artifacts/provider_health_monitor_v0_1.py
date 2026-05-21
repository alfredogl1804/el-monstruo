"""
Provider Health Monitor v0.1
R0+ Artifact — Epoch 005

Purpose: Detect provider drift, latency anomalies, and model deprecation warnings
by analyzing the chain logs produced by the reactor's M2 cycles.

Constraints:
- R0+ only: reads local files, produces local report
- No external API calls
- No Supabase
- No secrets exposure
- Kill-switch aware
"""

import json
import os
import glob
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
CHAIN_LOG_DIRS = [
    BASE_DIR / "bridge" / "reactor_m2_oneshot",
    BASE_DIR / "bridge" / "reactor_m2_stabilization",
    BASE_DIR / "bridge" / "reactor_limited_active_r0" / "live_upgrade_epoch_002",
    BASE_DIR / "bridge" / "reactor_limited_active_r0" / "live_upgrade_epoch_003",
    BASE_DIR / "bridge" / "reactor_limited_active_r0" / "live_upgrade_epoch_004",
    BASE_DIR / "bridge" / "reactor_limited_active_r0" / "live_upgrade_epoch_005",
]
PROVIDER_REGISTRY = BASE_DIR / "bridge" / "provider_ops" / "provider_registry.json"
KILL_SWITCH = BASE_DIR / "bridge" / "reactor_vigilia_foundation" / "reactor_heartbeat_r0" / "scheduler" / "scheduler_kill_switch.json"
OUTPUT_DIR = BASE_DIR / "bridge" / "reactor_limited_active_r0" / "live_upgrade_epoch_005" / "artifacts"


def check_kill_switch():
    """Return True if system is frozen."""
    if KILL_SWITCH.exists():
        data = json.loads(KILL_SWITCH.read_text())
        return data.get("active", True)
    return True


def load_provider_registry():
    """Load the canonical provider registry."""
    if PROVIDER_REGISTRY.exists():
        return json.loads(PROVIDER_REGISTRY.read_text())
    return {}


def scan_chain_logs():
    """Scan all chain log directories for provider execution data."""
    entries = []
    for d in CHAIN_LOG_DIRS:
        for f in d.glob("*.jsonl"):
            with open(f, 'r') as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue
    return entries


def analyze_provider_health(entries, registry):
    """Analyze provider health from chain log entries."""
    provider_stats = {}
    
    for entry in entries:
        provider = entry.get("provider") or entry.get("embryo")
        if not provider:
            continue
            
        if provider not in provider_stats:
            provider_stats[provider] = {
                "total_calls": 0,
                "successes": 0,
                "failures": 0,
                "total_cost": 0.0,
                "latencies": [],
                "last_seen": None,
                "errors": []
            }
        
        stats = provider_stats[provider]
        stats["total_calls"] += 1
        
        if (entry.get("status") == "SUCCESS" or 
            entry.get("verdict") in ["AUTONOMOUS_CYCLE_COMPLETE", "AUTONOMOUS_AUDIT_COMPLETE"] or
            entry.get("dispatcher") == "ALLOW" or
            entry.get("oracle_verdict") == "AUTONOMOUS_CYCLE_COMPLETE"):
            stats["successes"] += 1
        elif entry.get("status") == "FAILED" or entry.get("error"):
            stats["failures"] += 1
            if entry.get("error"):
                stats["errors"].append(entry["error"][:100])
        
        cost = entry.get("cost") or entry.get("cost_usd") or 0
        stats["total_cost"] += cost
        
        latency = entry.get("latency") or entry.get("duration")
        if latency:
            stats["latencies"].append(latency)
        
        ts = entry.get("timestamp")
        if ts:
            stats["last_seen"] = ts
    
    return provider_stats


def generate_health_report(provider_stats, registry):
    """Generate a health report with drift detection."""
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "artifact_id": "provider_health_monitor_v0_1",
        "providers": {},
        "alerts": [],
        "summary": {}
    }
    
    for provider, stats in provider_stats.items():
        avg_latency = sum(stats["latencies"]) / len(stats["latencies"]) if stats["latencies"] else 0
        success_rate = stats["successes"] / stats["total_calls"] if stats["total_calls"] > 0 else 0
        
        health = {
            "total_calls": stats["total_calls"],
            "success_rate": round(success_rate, 3),
            "avg_latency_s": round(avg_latency, 2),
            "total_cost_usd": round(stats["total_cost"], 6),
            "last_seen": stats["last_seen"],
            "status": "HEALTHY" if success_rate >= 0.9 else "DEGRADED" if success_rate >= 0.5 else "UNHEALTHY"
        }
        
        report["providers"][provider] = health
        
        # Alert generation
        if success_rate < 0.9:
            report["alerts"].append({
                "type": "LOW_SUCCESS_RATE",
                "provider": provider,
                "value": success_rate,
                "threshold": 0.9
            })
        
        if avg_latency > 15.0:
            report["alerts"].append({
                "type": "HIGH_LATENCY",
                "provider": provider,
                "value": avg_latency,
                "threshold": 15.0
            })
    
    report["summary"] = {
        "total_providers_monitored": len(provider_stats),
        "healthy": sum(1 for p in report["providers"].values() if p["status"] == "HEALTHY"),
        "degraded": sum(1 for p in report["providers"].values() if p["status"] == "DEGRADED"),
        "unhealthy": sum(1 for p in report["providers"].values() if p["status"] == "UNHEALTHY"),
        "total_alerts": len(report["alerts"])
    }
    
    return report


def run():
    """Main execution."""
    if check_kill_switch():
        print("[ABORT] Kill-switch is active. Provider Health Monitor cannot run.")
        return None
    
    print("=" * 60)
    print("PROVIDER HEALTH MONITOR v0.1 — R0+ Artifact")
    print("=" * 60)
    
    registry = load_provider_registry()
    entries = scan_chain_logs()
    print(f"  Scanned {len(entries)} chain log entries")
    
    provider_stats = analyze_provider_health(entries, registry)
    print(f"  Found {len(provider_stats)} unique providers/embryos")
    
    report = generate_health_report(provider_stats, registry)
    
    # Save report
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = OUTPUT_DIR / "provider_health_report.json"
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"  Report saved to: {output_path}")
    print(f"  Alerts: {report['summary']['total_alerts']}")
    print(f"  Healthy: {report['summary']['healthy']}, Degraded: {report['summary']['degraded']}, Unhealthy: {report['summary']['unhealthy']}")
    print("=" * 60)
    
    return report


if __name__ == "__main__":
    run()
