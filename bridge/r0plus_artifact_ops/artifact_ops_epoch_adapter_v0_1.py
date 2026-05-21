"""
Artifact Ops Epoch Adapter v0.1

Wraps the Artifact Ops Runner to integrate it as a standard epoch stage.
Adds epoch metadata, reads kill-switch without modifying it, generates
epoch-specific ops snapshots, detects health/risks/next actions, and
writes local reports.

Usage:
    python3 artifact_ops_epoch_adapter_v0_1.py [--epoch-id EPOCH_009] [--base-dir /path]

Output:
    JSON epoch ops snapshot to stdout.

Constraints:
    - R0+ only: pure local computation
    - No external API calls
    - No secrets
    - No provider calls
    - No scheduler policy changes
    - Kill-switch: read-only
"""
import json
import sys
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Paths
SELF_DIR = Path(__file__).parent
RUNNER_PATH = SELF_DIR / "artifact_ops_runner_v0_1.py"
KILL_SWITCH_PATH = Path(__file__).parents[1] / "reactor_vigilia_foundation" / "reactor_heartbeat_r0" / "scheduler" / "scheduler_kill_switch.json"
DIRECTIVE_QUEUE_PATH = Path(__file__).parents[1] / "state_fabric" / "t1_directive_queue.v0_1.json"


def load_config(epoch_id: str = "EPOCH_009", base_dir: Optional[Path] = None) -> dict:
    """Load adapter configuration."""
    if base_dir is None:
        base_dir = Path(__file__).parents[2]
    return {
        "epoch_id": epoch_id,
        "base_dir": str(base_dir),
        "runner_path": str(RUNNER_PATH),
        "kill_switch_path": str(KILL_SWITCH_PATH),
        "directive_queue_path": str(DIRECTIVE_QUEUE_PATH),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "adapter_version": "0.1",
        "external_api_calls": 0,
        "secrets_used": 0,
        "r1_operations": 0,
    }


def read_kill_switch(config: dict) -> dict:
    """Read kill-switch state without modifying it."""
    ks_path = Path(config["kill_switch_path"])
    if not ks_path.exists():
        return {"exists": False, "state": "NOT_FOUND", "active": None, "read_only": True}
    try:
        data = json.loads(ks_path.read_text(encoding="utf-8"))
        return {
            "exists": True,
            "state": "ACTIVE" if data.get("active", False) else "INACTIVE",
            "active": data.get("active", False),
            "read_only": True,
        }
    except (json.JSONDecodeError, IOError):
        return {"exists": True, "state": "ERROR", "active": None, "read_only": True}


def invoke_runner(config: dict) -> dict:
    """Invoke the Artifact Ops Runner and capture its output."""
    runner_path = Path(config["runner_path"])
    if not runner_path.exists():
        return {"status": "ERROR", "error": "Runner not found", "path": str(runner_path)}

    try:
        spec = importlib.util.spec_from_file_location("artifact_ops_runner", str(runner_path))
        module = importlib.util.module_from_spec(spec)

        # Capture stdout
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            spec.loader.exec_module(module)
            # The runner prints JSON to stdout when run as __main__
            # But when imported, we need to call its functions directly
            sys.stdout = old_stdout

            # Call runner functions directly
            base_dir = Path(config["base_dir"])
            # Use the runner's main entry point
            run_result = module.run(base_dir)
            consolidated = run_result.get("consolidated", {})
            runner_ks = run_result.get("kill_switch", {})
            indexer_result = run_result.get("results", {}).get("indexer", {})
            pattern_result = run_result.get("results", {}).get("pattern_detector", {})
            history_result = run_result.get("results", {}).get("history_analyzer", {})

            return {
                "status": "SUCCESS",
                "runner_version": run_result.get("runner_version", "0.1"),
                "kill_switch": runner_ks,
                "results": {
                    "indexer": indexer_result,
                    "pattern_detector": pattern_result,
                    "history_analyzer": history_result,
                },
                "consolidated": consolidated,
                "external_api_calls": 0,
                "secrets_used": 0,
                "r1_operations": 0,
            }
        except Exception as e:
            sys.stdout = old_stdout
            return {"status": "ERROR", "error": str(e)}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


def read_directive_summary(config: dict) -> dict:
    """Read directive queue summary without modifying."""
    dq_path = Path(config["directive_queue_path"])
    if not dq_path.exists():
        return {"exists": False, "total": 0, "active": 0}
    try:
        data = json.loads(dq_path.read_text(encoding="utf-8"))
        directives = data.get("directives", [])
        active = [d for d in directives if d.get("status") == "ACTIVE"]
        return {
            "exists": True,
            "total": len(directives),
            "active": len(active),
            "directive_ids": [d.get("directive_id") for d in active],
        }
    except (json.JSONDecodeError, IOError):
        return {"exists": True, "total": 0, "active": 0, "error": "PARSE_ERROR"}


def detect_top_risks(runner_output: dict) -> list:
    """Detect top risks from runner output."""
    risks = []
    consolidated = runner_output.get("consolidated", {})

    # Cost anomalies
    anomalies = consolidated.get("cost_anomalies", [])
    if anomalies:
        risks.append({
            "risk_id": "RISK_COST_ANOMALY",
            "severity": "MEDIUM",
            "description": f"{len(anomalies)} cost anomaly(ies) detected",
            "source": "memory_palace_pattern_detector",
        })

    # Regression flags
    regressions = consolidated.get("regression_flags", [])
    if regressions:
        for r in regressions[:2]:
            risks.append({
                "risk_id": f"RISK_REGRESSION_{r.get('type', 'UNKNOWN')}",
                "severity": r.get("severity", "MEDIUM"),
                "description": f"Regression: {r.get('type')} at run {r.get('run_index')}",
                "source": "embryo_run_history_analyzer",
            })

    # Task overspecialization
    overspec = consolidated.get("task_overspecialization", {})
    if isinstance(overspec, dict) and overspec.get("detected"):
        risks.append({
            "risk_id": "RISK_TASK_OVERSPECIALIZATION",
            "severity": "LOW",
            "description": f"Only {overspec.get('unique_tasks', 0)} unique tasks in {overspec.get('total_runs', 0)} runs",
            "source": "memory_palace_pattern_detector",
        })

    return risks[:3]


def detect_next_action(runner_output: dict, kill_switch: dict) -> str:
    """Determine next recommended action."""
    if kill_switch.get("active"):
        return "HALT_KILL_SWITCH_ACTIVE"

    consolidated = runner_output.get("consolidated", {})
    coverage = consolidated.get("artifact_test_coverage", 0)

    if coverage < 80:
        return "EXECUTE_TEST_REMEDIATION"

    regressions = consolidated.get("regression_flags", [])
    critical = [r for r in regressions if r.get("severity") == "HIGH"]
    if critical:
        return "PAUSE_AND_AUDIT"

    return consolidated.get("next_recommended_action", "PRODUCE_NEXT_SURGE")


def generate_epoch_ops_snapshot(config: dict, runner_output: dict, kill_switch: dict, directive_summary: dict) -> dict:
    """Generate the epoch-specific ops snapshot."""
    consolidated = runner_output.get("consolidated", {})
    top_risks = detect_top_risks(runner_output)
    next_action = detect_next_action(runner_output, kill_switch)

    return {
        "epoch_id": config["epoch_id"],
        "adapter_version": config["adapter_version"],
        "timestamp": config["timestamp"],
        "artifact_ops_health": "HEALTHY" if runner_output.get("status") == "SUCCESS" else "DEGRADED",
        "artifact_count": consolidated.get("artifact_count", 0),
        "artifact_test_coverage": consolidated.get("artifact_test_coverage", 0),
        "memory_palace_health": consolidated.get("memory_health", "UNKNOWN"),
        "embryo_health": consolidated.get("embryo_health", "UNKNOWN"),
        "kill_switch": kill_switch,
        "directive_summary": directive_summary,
        "cost_summary": {
            "epoch_cost_usd": 0.0,
            "provider_calls": 0,
            "budget_remaining": 0.0,
        },
        "top_risks": top_risks,
        "next_recommended_action": next_action,
        "external_api_calls": 0,
        "secrets_used": 0,
        "r1_operations": 0,
    }


def run_epoch_adapter(epoch_id: str = "EPOCH_009", base_dir: Optional[Path] = None) -> dict:
    """Main entry point: run the full epoch adapter pipeline."""
    config = load_config(epoch_id, base_dir)
    kill_switch = read_kill_switch(config)
    runner_output = invoke_runner(config)
    directive_summary = read_directive_summary(config)
    snapshot = generate_epoch_ops_snapshot(config, runner_output, kill_switch, directive_summary)

    return {
        "epoch_id": epoch_id,
        "adapter_version": "0.1",
        "timestamp": config["timestamp"],
        "config": config,
        "kill_switch": kill_switch,
        "runner_output": runner_output,
        "directive_summary": directive_summary,
        "epoch_ops_snapshot": snapshot,
        "external_api_calls": 0,
        "secrets_used": 0,
        "r1_operations": 0,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Artifact Ops Epoch Adapter v0.1")
    parser.add_argument("--epoch-id", default="EPOCH_009", help="Epoch identifier")
    parser.add_argument("--base-dir", default=None, help="Base directory of the repo")
    args = parser.parse_args()

    base = Path(args.base_dir) if args.base_dir else None
    result = run_epoch_adapter(args.epoch_id, base)
    print(json.dumps(result, indent=2, default=str))
