"""Tests for Embryo Run History Analyzer v0.1"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from embryo_run_history_analyzer_v0_1 import (
    discover_oracle_outputs,
    discover_auditor_outputs,
    extract_run_metrics,
    analyze_cost_trend,
    analyze_grounding_trend,
    analyze_task_distribution,
    detect_regressions,
    compute_health_score,
    run_full_analysis,
)


def _create_test_structure(tmp_dir: Path):
    """Create realistic output directory structure."""
    # Oracle outputs
    oracle_dir = tmp_dir / "embryos" / "oracle_ai_r0" / "outputs"
    oracle_dir.mkdir(parents=True)
    
    for i in range(5):
        output = {
            "embryo_id": "oracle_ai_embryo_r0",
            "task_id": "map_capability" if i % 2 == 0 else "detect_candidates",
            "action_class": "A1_ANALYZE",
            "dispatcher_decision": "ALLOW",
            "timestamp": f"2026-05-{15+i}T10:00:00Z",
            "cost_usd": 0.0003 + (i * 0.00005),
            "grounding_level": 7 + (i * 0.5),
            "output": {
                "claims": [{"claim_id": str(j)} for j in range(3 + i)],
                "grounding_level": 7 + (i * 0.5),
                "cost": 0.0003 + (i * 0.00005)
            }
        }
        (oracle_dir / f"task_{i}_2026051{5+i}T100000.json").write_text(json.dumps(output))
    
    # Oracle state
    state_dir = tmp_dir / "embryos" / "oracle_ai_r0"
    (state_dir / "state.json").write_text(json.dumps({"cycles_completed": 5}))
    
    # Auditor outputs
    auditor_dir = tmp_dir / "embryos" / "oracle_pair_r0" / "auditor_outputs"
    auditor_dir.mkdir(parents=True)
    
    for i in range(4):
        output = {
            "embryo_id": "oracle_auditor_embryo_r0",
            "task_id": "audit_oracle_latest_output",
            "action_class": "A1_ANALYZE",
            "dispatcher_decision": "ALLOW",
            "timestamp": f"2026-05-{15+i}T10:05:00Z",
            "cost_usd": 0.0002 + (i * 0.00003),
            "grounding_level": 6 + i,
            "output": {
                "claims": [{"claim_id": str(j)} for j in range(2)],
                "grounding_level": 6 + i,
                "cost": 0.0002 + (i * 0.00003)
            }
        }
        (auditor_dir / f"audit_{i}_2026051{5+i}T100500.json").write_text(json.dumps(output))
    
    # Auditor state
    auditor_state_dir = tmp_dir / "embryos" / "oracle_pair_r0"
    (auditor_state_dir / "auditor_state.json").write_text(json.dumps({"cycles_completed": 4}))
    
    return tmp_dir


def test_discover_oracle_outputs():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        outputs = discover_oracle_outputs(base)
        assert len(outputs) == 5


def test_discover_auditor_outputs():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        outputs = discover_auditor_outputs(base)
        assert len(outputs) == 4


def test_extract_run_metrics_has_required_fields():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        outputs = discover_oracle_outputs(base)
        metrics = extract_run_metrics(outputs)
        required = ["timestamp", "task_id", "cost_usd", "grounding_level", "claims_count"]
        for m in metrics:
            for field in required:
                assert field in m, f"Missing {field}"


def test_analyze_cost_trend_stable():
    metrics = [{"cost_usd": 0.0003, "grounding_level": 8} for _ in range(5)]
    result = analyze_cost_trend(metrics)
    assert result["trend"] == "STABLE"


def test_analyze_cost_trend_increasing():
    metrics = [
        {"cost_usd": 0.0001, "grounding_level": 8},
        {"cost_usd": 0.0001, "grounding_level": 8},
        {"cost_usd": 0.001, "grounding_level": 8},
        {"cost_usd": 0.001, "grounding_level": 8},
    ]
    result = analyze_cost_trend(metrics)
    assert result["trend"] == "INCREASING"


def test_analyze_grounding_trend_improving():
    metrics = [
        {"cost_usd": 0.0003, "grounding_level": 5},
        {"cost_usd": 0.0003, "grounding_level": 5},
        {"cost_usd": 0.0003, "grounding_level": 9},
        {"cost_usd": 0.0003, "grounding_level": 9},
    ]
    result = analyze_grounding_trend(metrics)
    assert result["trend"] == "IMPROVING"


def test_analyze_grounding_trend_degrading():
    metrics = [
        {"cost_usd": 0.0003, "grounding_level": 9},
        {"cost_usd": 0.0003, "grounding_level": 9},
        {"cost_usd": 0.0003, "grounding_level": 4},
        {"cost_usd": 0.0003, "grounding_level": 4},
    ]
    result = analyze_grounding_trend(metrics)
    assert result["trend"] == "DEGRADING"


def test_analyze_task_distribution():
    metrics = [
        {"task_id": "analyze", "cost_usd": 0.0003, "grounding_level": 8},
        {"task_id": "analyze", "cost_usd": 0.0003, "grounding_level": 8},
        {"task_id": "detect", "cost_usd": 0.0002, "grounding_level": 7},
    ]
    result = analyze_task_distribution(metrics)
    assert result["unique_tasks"] == 2
    assert result["total_runs"] == 3
    assert "analyze" in result["distribution"]


def test_detect_regressions_grounding_drop():
    metrics = [
        {"grounding_level": 9, "cost_usd": 0.0003, "source_file": "f1.json"},
        {"grounding_level": 9, "cost_usd": 0.0003, "source_file": "f2.json"},
        {"grounding_level": 9, "cost_usd": 0.0003, "source_file": "f3.json"},
        {"grounding_level": 3, "cost_usd": 0.0003, "source_file": "f4.json"},  # regression
    ]
    regressions = detect_regressions(metrics, window=3)
    assert len(regressions) >= 1
    assert regressions[0]["type"] == "GROUNDING_DROP"


def test_detect_regressions_cost_spike():
    metrics = [
        {"grounding_level": 8, "cost_usd": 0.0003, "source_file": "f1.json"},
        {"grounding_level": 8, "cost_usd": 0.0003, "source_file": "f2.json"},
        {"grounding_level": 8, "cost_usd": 0.0003, "source_file": "f3.json"},
        {"grounding_level": 8, "cost_usd": 0.01, "source_file": "f4.json"},  # spike
    ]
    regressions = detect_regressions(metrics, window=3)
    assert len(regressions) >= 1
    assert regressions[0]["type"] == "COST_SPIKE"


def test_detect_regressions_no_regression():
    metrics = [{"grounding_level": 8, "cost_usd": 0.0003, "source_file": f"f{i}.json"} for i in range(6)]
    regressions = detect_regressions(metrics, window=3)
    assert len(regressions) == 0


def test_compute_health_score_healthy():
    cost = {"trend": "STABLE"}
    grounding = {"trend": "IMPROVING"}
    regressions = []
    result = compute_health_score(cost, grounding, regressions)
    assert result["status"] == "HEALTHY"
    assert result["health_score"] == 100


def test_compute_health_score_degraded():
    cost = {"trend": "INCREASING"}
    grounding = {"trend": "DEGRADING"}
    regressions = [{"severity": "HIGH"}]
    result = compute_health_score(cost, grounding, regressions)
    assert result["status"] in ["DEGRADED", "CRITICAL"]
    assert result["health_score"] < 70


def test_run_full_analysis_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        result = run_full_analysis(base)
        assert "summary" in result
        assert "oracle" in result
        assert "auditor" in result
        assert result["summary"]["total_oracle_runs"] == 5
        assert result["summary"]["total_auditor_runs"] == 4


def test_run_full_analysis_empty():
    with tempfile.TemporaryDirectory() as tmp:
        result = run_full_analysis(Path(tmp))
        assert result["summary"]["total_combined_runs"] == 0


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"  PASS: {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {t.__name__} — {e}")
    print(f"\n{'='*60}")
    print(f"Embryo Run History Analyzer Tests: {passed}/{passed+failed} PASS")
    if failed:
        sys.exit(1)
