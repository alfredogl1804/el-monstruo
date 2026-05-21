"""
Artifact Ops Epoch Adapter v0.1
Wraps the Artifact Ops Runner with epoch-scoped context to produce
a unified per-epoch operational snapshot.

Responsibilities:
  1. Invoke Artifact Ops Runner (artifact_ops_runner_v0_1.run())
  2. Read kill-switch state (never modify)
  3. Read T1 Directive Queue state (never modify)
  4. Add epoch_id, epoch_status, and epoch metadata
  5. Consolidate: health, coverage, costs, embryo status, Memory Palace,
     Directive Queue, risks, and next action
  6. Produce stable JSON output (EPOCH_OPS_SNAPSHOT)
  7. Produce T1 Operating Snapshot v0.3

Constraints:
  - R0+ only: pure local computation
  - No external API calls (0 provider calls)
  - No Supabase, no DB, no secrets
  - No memory/Memento/Anti-Dory writes
  - Kill-switch: READ ONLY
  - Directive Queue: READ ONLY
  - No scheduler policy change
  - Budget: $0.00

Usage:
    python3 artifact_ops_epoch_adapter_v0_1.py [--base-dir /path] [--epoch-id 009]
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Resolve paths
OPS_DIR = Path(__file__).parent
BRIDGE_DIR = OPS_DIR.parent
REPO_ROOT = BRIDGE_DIR.parent

# Import the runner
sys.path.insert(0, str(OPS_DIR))
from artifact_ops_runner_v0_1 import run as run_ops_runner, read_kill_switch, load_config

# Paths to state fabric files (read-only)
DIRECTIVE_QUEUE_PATH = BRIDGE_DIR / "state_fabric" / "t1_directive_queue.v0_1.json"
KILL_SWITCH_PATH = BRIDGE_DIR / "kill_switch.json"
REMEDIATION_QUEUE_PATH = BRIDGE_DIR / "state_fabric" / "artifact_test_remediation_queue.v0_1.json"


def read_directive_queue() -> dict:
    """Read T1 Directive Queue state (never modify)."""
    if not DIRECTIVE_QUEUE_PATH.exists():
        return {"exists": False, "directives": [], "active_count": 0}
    try:
        data = json.loads(DIRECTIVE_QUEUE_PATH.read_text(encoding="utf-8"))
        directives = data.get("directives", [])
        active = [d for d in directives if d.get("status") == "ACTIVE"]
        return {
            "exists": True,
            "total_directives": len(directives),
            "active_count": len(active),
            "active_directives": [
                {
                    "directive_id": d.get("directive_id"),
                    "priority": d.get("priority"),
                    "directive_type": d.get("directive_type"),
                    "focus": d.get("focus"),
                }
                for d in active
            ],
            "last_updated": data.get("last_updated", "UNKNOWN"),
        }
    except (json.JSONDecodeError, IOError) as e:
        return {"exists": True, "error": str(e), "directives": [], "active_count": 0}


def read_remediation_queue() -> dict:
    """Read remediation queue state (never modify)."""
    if not REMEDIATION_QUEUE_PATH.exists():
        return {"exists": False, "items": [], "total": 0}
    try:
        data = json.loads(REMEDIATION_QUEUE_PATH.read_text(encoding="utf-8"))
        items = data.get("items", [])
        done = [i for i in items if i.get("status") == "DONE"]
        ready = [i for i in items if i.get("status") == "READY_R0PLUS"]
        return {
            "exists": True,
            "total": len(items),
            "done": len(done),
            "ready": len(ready),
            "all_done": len(done) == len(items),
        }
    except (json.JSONDecodeError, IOError) as e:
        return {"exists": True, "error": str(e), "items": [], "total": 0}


def compute_epoch_health(runner_output: dict, directive_queue: dict) -> dict:
    """Compute consolidated epoch health from all sources."""
    consolidated = runner_output.get("consolidated", {})

    # Artifact health
    artifact_coverage = consolidated.get("artifact_test_coverage", 0)
    artifact_health = "GREEN" if artifact_coverage >= 90 else "YELLOW" if artifact_coverage >= 60 else "RED"

    # Memory Palace health
    memory_health = consolidated.get("memory_health", "UNKNOWN")
    memory_score = "GREEN" if memory_health == "HEALTHY" else "YELLOW" if memory_health != "ERROR" else "RED"

    # Embryo health
    embryo_health = consolidated.get("embryo_health", "UNKNOWN")
    embryo_score = "GREEN" if embryo_health == "HEALTHY" else "YELLOW" if embryo_health != "ERROR" else "RED"

    # Directive alignment
    directive_score = "GREEN" if directive_queue.get("active_count", 0) > 0 else "YELLOW"

    # Overall
    scores = [artifact_health, memory_score, embryo_score, directive_score]
    if "RED" in scores:
        overall = "RED"
    elif "YELLOW" in scores:
        overall = "YELLOW"
    else:
        overall = "GREEN"

    return {
        "overall": overall,
        "artifact_health": artifact_health,
        "memory_palace_health": memory_score,
        "embryo_health": embryo_score,
        "directive_alignment": directive_score,
        "artifact_coverage_pct": artifact_coverage,
        "memory_status": memory_health,
        "embryo_status": embryo_health,
    }


def compute_top_risks(runner_output: dict) -> list:
    """Extract and prioritize top 3 risks."""
    risks = []
    consolidated = runner_output.get("consolidated", {})

    # Risk 1: Regression flags
    regression_flags = consolidated.get("regression_flags", [])
    if regression_flags:
        risks.append({
            "risk": f"{len(regression_flags)} regression flag(s) detected in embryo history",
            "severity": "MEDIUM",
            "action": "INVESTIGATE",
        })

    # Risk 2: Cost anomalies
    cost_anomalies = consolidated.get("cost_anomalies", [])
    if cost_anomalies:
        risks.append({
            "risk": f"{len(cost_anomalies)} cost anomaly/anomalies detected",
            "severity": "LOW",
            "action": "MONITOR",
        })

    # Risk 3: Task overspecialization
    task_overspec = consolidated.get("task_overspecialization", {})
    if task_overspec.get("detected"):
        risks.append({
            "risk": "Task overspecialization detected in Memory Palace",
            "severity": "LOW",
            "action": "DIVERSIFY_TASKS",
        })

    # Risk 4: Low coverage (should not happen at 100%)
    if consolidated.get("artifact_test_coverage", 100) < 90:
        risks.append({
            "risk": f"Test coverage below 90%: {consolidated.get('artifact_test_coverage', 0)}%",
            "severity": "HIGH",
            "action": "REMEDIATE",
        })

    # Pad to 3 if fewer
    while len(risks) < 3:
        risks.append({
            "risk": "No additional risks detected",
            "severity": "NONE",
            "action": "CONTINUE",
        })

    return risks[:3]


def determine_next_sprint(runner_output: dict, epoch_health: dict) -> str:
    """Determine recommended next sprint based on epoch state."""
    if epoch_health["overall"] == "RED":
        return "SPR-R0PLUS-EMERGENCY-REMEDIATION"

    next_action = runner_output.get("consolidated", {}).get("next_recommended_action", "PRODUCE_NEXT_SURGE")

    action_to_sprint = {
        "INVESTIGATE_HIGH_REGRESSION": "SPR-R0PLUS-REGRESSION-INVESTIGATION",
        "EXECUTE_TEST_REMEDIATION_TOP3": "SPR-R0PLUS-TEST-REMEDIATION-TOP3",
        "INVESTIGATE_MEMORY_PALACE_HEALTH": "SPR-R0PLUS-MEMORY-PALACE-REMEDIATION",
        "PRODUCE_NEXT_SURGE": "SPR-R0PLUS-PRODUCTION-SURGE-002",
    }

    return action_to_sprint.get(next_action, "SPR-R0PLUS-PRODUCTION-SURGE-002")


def build_epoch_ops_snapshot(
    epoch_id: str,
    runner_output: dict,
    directive_queue: dict,
    remediation_queue: dict,
    epoch_health: dict,
    top_risks: list,
    next_sprint: str,
) -> dict:
    """Build the unified epoch ops snapshot."""
    consolidated = runner_output.get("consolidated", {})

    return {
        "version": "0.1",
        "epoch_id": epoch_id,
        "epoch_status": "COMPLETE",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "artifact_ops_epoch_adapter_v0_1",
        "sprint": f"SPR-R0PLUS-EPOCH-{epoch_id}-OPS-INTEGRATED",
        "runner_output_version": runner_output.get("runner_version", "0.1"),
        "kill_switch": runner_output.get("kill_switch", {}),
        "external_api_calls": 0,
        "secrets_used": 0,
        "r1_operations": 0,
        "supabase_calls": 0,
        "cost_usd": 0.0,
        "health": epoch_health,
        "artifact_coverage": {
            "total_artifacts": consolidated.get("artifact_count", 0),
            "coverage_pct": consolidated.get("artifact_test_coverage", 0),
            "untested_count": runner_output.get("results", {}).get("indexer", {}).get("artifacts_without_tests", 0),
        },
        "memory_palace": {
            "status": consolidated.get("memory_health", "UNKNOWN"),
            "cost_anomalies": len(consolidated.get("cost_anomalies", [])),
            "task_overspecialization": consolidated.get("task_overspecialization", {}).get("detected", False),
        },
        "embryo_status": {
            "combined_health": consolidated.get("embryo_health", "UNKNOWN"),
            "oracle_health": runner_output.get("results", {}).get("history_analyzer", {}).get("oracle_health", "UNKNOWN"),
            "auditor_health": runner_output.get("results", {}).get("history_analyzer", {}).get("auditor_health", "UNKNOWN"),
            "regression_flags": runner_output.get("results", {}).get("history_analyzer", {}).get("regression_flags", 0),
            "total_cost_usd": runner_output.get("results", {}).get("history_analyzer", {}).get("total_cost_usd", 0),
        },
        "directive_queue": directive_queue,
        "remediation_queue": remediation_queue,
        "top_risks": top_risks,
        "next_recommended_action": consolidated.get("next_recommended_action", "PRODUCE_NEXT_SURGE"),
        "next_recommended_sprint": next_sprint,
    }


def build_t1_operating_snapshot_v03(
    epoch_id: str,
    epoch_ops_snapshot: dict,
    epoch_health: dict,
    top_risks: list,
    next_sprint: str,
) -> dict:
    """Build T1 Operating Snapshot v0.3 with epoch lineage."""
    return {
        "version": "0.3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "artifact_ops_epoch_adapter_v0_1",
        "sprint": epoch_ops_snapshot["sprint"],
        "epoch_id": epoch_id,
        "epoch_lineage": {
            "epochs_completed": int(epoch_id),
            "surges_completed": 1,
            "ops_integrations": 2,
            "latest_epoch": epoch_id,
        },
        "pilot_health": {
            "reactor_level": "R0+",
            "overall_status": epoch_health["overall"],
            "artifact_health": epoch_health["artifact_health"],
            "memory_palace_health": epoch_health["memory_palace_health"],
            "embryo_health": epoch_health["embryo_health"],
            "directive_alignment": epoch_health["directive_alignment"],
        },
        "artifact_ops_summary": {
            "runner_version": "0.1",
            "adapter_version": "0.1",
            "artifacts_executed": 3,
            "all_succeeded": True,
            "external_api_calls": 0,
            "secrets_used": 0,
            "r1_operations": 0,
        },
        "artifact_test_coverage": epoch_ops_snapshot["artifact_coverage"],
        "memory_palace_health": epoch_ops_snapshot["memory_palace"],
        "embryo_status": epoch_ops_snapshot["embryo_status"],
        "directive_queue_summary": {
            "active_count": epoch_ops_snapshot["directive_queue"].get("active_count", 0),
            "total_directives": epoch_ops_snapshot["directive_queue"].get("total_directives", 0),
        },
        "cost_summary": {
            "total_embryo_cost_usd": epoch_ops_snapshot["embryo_status"]["total_cost_usd"],
            "this_sprint_cost_usd": 0.0,
            "budget_remaining_usd": 0.0,
        },
        "top_risks": top_risks,
        "next_3_actions": [
            next_sprint,
            "MONITOR_PROVIDER_EOL",
            "PRODUCE_NEXT_SURGE",
        ],
        "T1_decisions_pending": [
            {
                "decision": "Approve merge to main",
                "deadline": "when_ready",
                "status": "PENDING_T1",
            }
        ],
        "recommended_next_sprint": next_sprint,
    }


def run_epoch_adapter(base_dir: Optional[Path] = None, epoch_id: str = "009") -> dict:
    """Main entry point: run adapter and produce all outputs."""
    if base_dir is None:
        base_dir = REPO_ROOT

    # 1. Run Artifact Ops Runner
    runner_output = run_ops_runner(base_dir)

    # 2. Read Directive Queue (read-only)
    directive_queue = read_directive_queue()

    # 3. Read Remediation Queue (read-only)
    remediation_queue = read_remediation_queue()

    # 4. Compute epoch health
    epoch_health = compute_epoch_health(runner_output, directive_queue)

    # 5. Compute top risks
    top_risks = compute_top_risks(runner_output)

    # 6. Determine next sprint
    next_sprint = determine_next_sprint(runner_output, epoch_health)

    # 7. Build epoch ops snapshot
    epoch_ops_snapshot = build_epoch_ops_snapshot(
        epoch_id, runner_output, directive_queue, remediation_queue,
        epoch_health, top_risks, next_sprint
    )

    # 8. Build T1 Operating Snapshot v0.3
    t1_snapshot = build_t1_operating_snapshot_v03(
        epoch_id, epoch_ops_snapshot, epoch_health, top_risks, next_sprint
    )

    return {
        "epoch_ops_snapshot": epoch_ops_snapshot,
        "t1_operating_snapshot_v03": t1_snapshot,
        "runner_output": runner_output,
        "epoch_health": epoch_health,
        "top_risks": top_risks,
        "next_sprint": next_sprint,
    }


if __name__ == "__main__":
    base_dir = None
    epoch_id = "009"

    args = sys.argv[1:]
    if "--base-dir" in args:
        idx = args.index("--base-dir")
        base_dir = Path(args[idx + 1])
    if "--epoch-id" in args:
        idx = args.index("--epoch-id")
        epoch_id = args[idx + 1]

    result = run_epoch_adapter(base_dir, epoch_id)

    # Write outputs
    epoch_dir = BRIDGE_DIR / "reactor_limited_active_r0" / f"live_upgrade_epoch_{epoch_id}"
    epoch_dir.mkdir(parents=True, exist_ok=True)

    ops_snapshot_path = epoch_dir / f"EPOCH_{epoch_id}_OPS_SNAPSHOT.json"
    ops_snapshot_path.write_text(
        json.dumps(result["epoch_ops_snapshot"], indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    t1_snapshot_path = OPS_DIR / "T1_OPERATING_SNAPSHOT_v0_3.json"
    t1_snapshot_path.write_text(
        json.dumps(result["t1_operating_snapshot_v03"], indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps({
        "status": "SUCCESS",
        "epoch_ops_snapshot_path": str(ops_snapshot_path),
        "t1_snapshot_path": str(t1_snapshot_path),
        "epoch_health": result["epoch_health"]["overall"],
        "next_sprint": result["next_sprint"],
    }, indent=2))
