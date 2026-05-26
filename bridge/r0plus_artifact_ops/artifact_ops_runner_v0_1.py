"""
Artifact Ops Runner v0.1
Integrates and orchestrates all R0+ artifact analyzers into a unified operational layer.

Executes:
  1. r0plus_artifact_indexer_v0_1.py
  2. memory_palace_pattern_detector_v0_1.py
  3. embryo_run_history_analyzer_v0_1.py

Consolidates outputs into a single health dashboard, detects untested artifacts,
generates a remediation queue, and produces actionable recommendations.

Usage:
    python3 artifact_ops_runner_v0_1.py [--base-dir /path/to/repo]

Output:
    JSON consolidated report to stdout.

Constraints:
    - R0+ only: pure local computation, no external APIs
    - Read-only: does not modify any source files
    - No secrets, no Supabase, no memory writes
    - Kill-switch state read but never modified
"""

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Resolve artifact paths
ARTIFACTS_DIR = Path(__file__).parents[1] / "r0plus_production_surge_001" / "artifacts"
sys.path.insert(0, str(ARTIFACTS_DIR))


def load_config(base_dir: Path) -> dict:
    """Load runner configuration from base directory context."""
    config = {
        "base_dir": str(base_dir),
        "bridge_dir": str(base_dir / "bridge") if (base_dir / "bridge").exists() else str(base_dir),
        "artifacts_dir": str(ARTIFACTS_DIR),
        "kill_switch_path": str(base_dir / "bridge" / "kill_switch.json"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1",
        "runner": "artifact_ops_runner_v0_1",
    }
    return config


def read_kill_switch(config: dict) -> dict:
    """Read kill-switch state (never modify)."""
    ks_path = Path(config["kill_switch_path"])
    if not ks_path.exists():
        return {"exists": False, "state": "NOT_FOUND", "read_only": True}
    try:
        data = json.loads(ks_path.read_text(encoding="utf-8"))
        return {"exists": True, "state": data.get("state", "UNKNOWN"), "read_only": True}
    except (json.JSONDecodeError, IOError):
        return {"exists": True, "state": "READ_ERROR", "read_only": True}


def run_artifact_indexer(config: dict) -> dict:
    """Execute R0+ Artifact Indexer and return results."""
    try:
        from r0plus_artifact_indexer_v0_1 import build_index

        bridge_dir = Path(config["bridge_dir"])
        index = build_index(bridge_dir)
        return {
            "status": "SUCCESS",
            "total_artifacts": index["summary"]["total_artifacts"],
            "total_with_tests": index["summary"]["total_with_tests"],
            "total_without_tests": index["summary"]["total_without_tests"],
            "test_coverage_pct": index["summary"]["test_coverage_pct"],
            "total_test_count": index["summary"]["total_test_count"],
            "source_distribution": index["summary"]["source_type_distribution"],
            "artifacts": index["artifacts"],
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}


def run_pattern_detector(config: dict) -> dict:
    """Execute Memory Palace Pattern Detector and return results."""
    try:
        from memory_palace_pattern_detector_v0_1 import run_full_analysis

        report = run_full_analysis()
        return {
            "status": "SUCCESS" if report["status"] != "EMPTY_MEMORY_PALACE" else "EMPTY",
            "entries_analyzed": report.get("entries_analyzed", 0),
            "health_score": report.get("health_score", 0),
            "health_status": report.get("health_status", "UNKNOWN"),
            "issues": report.get("issues", []),
            "patterns": report.get("patterns", {}),
            "recommendations": report.get("recommendations", []),
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}


def run_history_analyzer(config: dict) -> dict:
    """Execute Embryo Run History Analyzer and return results."""
    try:
        from embryo_run_history_analyzer_v0_1 import run_full_analysis

        base_dir = Path(config["base_dir"])
        report = run_full_analysis(base_dir)
        return {
            "status": "SUCCESS",
            "total_oracle_runs": report["summary"]["total_oracle_runs"],
            "total_auditor_runs": report["summary"]["total_auditor_runs"],
            "total_cost_usd": report["summary"]["total_cost_usd"],
            "oracle_health": report["oracle"]["health"]["status"],
            "auditor_health": report["auditor"]["health"]["status"],
            "combined_health": report["summary"]["combined_health"],
            "oracle_regressions": report["oracle"]["regressions"],
            "auditor_regressions": report["auditor"]["regressions"],
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}


def detect_untested_artifacts(indexer_result: dict) -> list[dict]:
    """Identify artifacts without tests from indexer results."""
    if indexer_result["status"] != "SUCCESS":
        return []

    untested = []
    for art in indexer_result.get("artifacts", []):
        if not art.get("has_tests", False):
            untested.append(
                {
                    "artifact_id": art["artifact_id"],
                    "name": art["name"],
                    "path": art["path"],
                    "source_type": art["source_type"],
                    "function_count": art["function_count"],
                    "lines_of_code": art["lines_of_code"],
                    "risk_if_untested": "HIGH" if art["function_count"] >= 3 else "MEDIUM",
                }
            )

    return untested


def detect_cost_anomalies(pattern_result: dict) -> list[dict]:
    """Extract cost anomalies from pattern detector results."""
    if pattern_result["status"] != "SUCCESS":
        return []

    patterns = pattern_result.get("patterns", {})
    return patterns.get("cost_anomalies", [])


def detect_task_overspecialization(pattern_result: dict) -> dict:
    """Check for task over-specialization from pattern detector."""
    if pattern_result["status"] != "SUCCESS":
        return {"detected": False}

    patterns = pattern_result.get("patterns", {})
    task_conc = patterns.get("task_concentration", {})
    dominant = task_conc.get("dominant_tasks", [])

    return {
        "detected": len(dominant) > 0,
        "dominant_tasks": dominant,
        "unique_tasks": task_conc.get("unique_tasks", 0),
        "total_runs": task_conc.get("total_runs", 0),
    }


def detect_regression_flags(history_result: dict) -> list[dict]:
    """Extract regression flags from history analyzer."""
    if history_result["status"] != "SUCCESS":
        return []

    regressions = []
    regressions.extend(history_result.get("oracle_regressions", []))
    regressions.extend(history_result.get("auditor_regressions", []))
    return regressions


def generate_remediation_queue(untested: list[dict]) -> list[dict]:
    """Generate a prioritized remediation queue for untested artifacts."""
    queue = []
    for i, art in enumerate(sorted(untested, key=lambda x: -x["function_count"])):
        queue.append(
            {
                "priority": i + 1,
                "artifact_id": art["artifact_id"],
                "artifact_path": art["path"],
                "has_tests": False,
                "test_path_expected": art["path"]
                .replace(".py", "")
                .replace(art["name"].replace(".py", ""), f"test_{art['name']}"),
                "risk_if_untested": art["risk_if_untested"],
                "value_if_tested": "Prevents silent regressions, enables CI validation",
                "recommended_action": "WRITE_TESTS",
                "status": "READY_R0PLUS",
                "forbidden_actions": ["R1", "main", "deploy", "Supabase"],
                "source_ref": f"artifact_ops_runner_v0_1 @ {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
            }
        )
    return queue


def determine_next_action(indexer_result: dict, pattern_result: dict, history_result: dict) -> str:
    """Determine the next recommended action based on all analysis."""
    # Priority 1: If there are regressions, address them
    regressions = detect_regression_flags(history_result)
    if any(r.get("severity") == "HIGH" for r in regressions):
        return "INVESTIGATE_HIGH_REGRESSION"

    # Priority 2: If test coverage is low, remediate
    if indexer_result["status"] == "SUCCESS":
        coverage = indexer_result.get("test_coverage_pct", 0)
        if coverage < 50:
            return "EXECUTE_TEST_REMEDIATION_TOP3"

    # Priority 3: If memory palace health is degrading
    if pattern_result["status"] == "SUCCESS":
        if pattern_result.get("health_score", 100) < 50:
            return "INVESTIGATE_MEMORY_PALACE_HEALTH"

    # Priority 4: Default — produce next surge
    return "PRODUCE_NEXT_SURGE"


def consolidate_output(
    config: dict, indexer_result: dict, pattern_result: dict, history_result: dict, kill_switch: dict
) -> dict:
    """Consolidate all results into a single output."""
    untested = detect_untested_artifacts(indexer_result)
    cost_anomalies = detect_cost_anomalies(pattern_result)
    task_overspec = detect_task_overspecialization(pattern_result)
    regression_flags = detect_regression_flags(history_result)
    remediation_queue = generate_remediation_queue(untested)
    next_action = determine_next_action(indexer_result, pattern_result, history_result)

    return {
        "runner_version": "0.1",
        "timestamp": config["timestamp"],
        "base_dir": config["base_dir"],
        "kill_switch": kill_switch,
        "external_api_calls": 0,
        "secrets_used": 0,
        "r1_operations": 0,
        "results": {
            "indexer": {
                "status": indexer_result["status"],
                "artifact_count": indexer_result.get("total_artifacts", 0),
                "artifact_test_coverage": indexer_result.get("test_coverage_pct", 0),
                "artifacts_without_tests": len(untested),
            },
            "pattern_detector": {
                "status": pattern_result["status"],
                "memory_health": pattern_result.get("health_status", "UNKNOWN"),
                "memory_health_score": pattern_result.get("health_score", 0),
                "cost_anomalies": len(cost_anomalies),
                "task_overspecialization": task_overspec["detected"],
            },
            "history_analyzer": {
                "status": history_result["status"],
                "embryo_health": history_result.get("combined_health", "UNKNOWN"),
                "oracle_health": history_result.get("oracle_health", "UNKNOWN"),
                "auditor_health": history_result.get("auditor_health", "UNKNOWN"),
                "regression_flags": len(regression_flags),
                "total_cost_usd": history_result.get("total_cost_usd", 0),
            },
        },
        "consolidated": {
            "artifact_count": indexer_result.get("total_artifacts", 0),
            "artifact_test_coverage": indexer_result.get("test_coverage_pct", 0),
            "memory_health": pattern_result.get("health_status", "UNKNOWN"),
            "embryo_health": history_result.get("combined_health", "UNKNOWN"),
            "cost_anomalies": cost_anomalies,
            "task_overspecialization": task_overspec,
            "regression_flags": regression_flags,
            "next_recommended_action": next_action,
        },
        "remediation_queue": remediation_queue,
        "untested_artifacts": untested,
    }


def run(base_dir: Optional[Path] = None) -> dict:
    """Main entry point: run all artifacts and consolidate."""
    if base_dir is None:
        base_dir = Path(__file__).parents[2]  # repo root

    config = load_config(base_dir)
    kill_switch = read_kill_switch(config)

    # Execute all 3 artifacts
    indexer_result = run_artifact_indexer(config)
    pattern_result = run_pattern_detector(config)
    history_result = run_history_analyzer(config)

    # Consolidate
    output = consolidate_output(config, indexer_result, pattern_result, history_result, kill_switch)

    return output


if __name__ == "__main__":
    base_dir = None
    if len(sys.argv) > 2 and sys.argv[1] == "--base-dir":
        base_dir = Path(sys.argv[2])

    result = run(base_dir)
    print(json.dumps(result, indent=2))
