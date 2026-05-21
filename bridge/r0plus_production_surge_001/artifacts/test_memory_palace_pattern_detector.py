"""Tests for Memory Palace Pattern Detector v0.1"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from memory_palace_pattern_detector_v0_1 import (
    load_entries,
    detect_recurring_lessons,
    detect_cost_anomalies,
    detect_grounding_drift,
    detect_embryo_performance,
    detect_task_concentration,
    detect_value_patterns,
    run_full_analysis,
)


def _make_state_file(entries: list[dict]) -> Path:
    """Create a temporary state file with given entries."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    state = {"entries": entries, "stats": {}}
    json.dump(state, tmp)
    tmp.close()
    return Path(tmp.name)


def _make_entry(entry_id="E1", lesson="test lesson", cost=0.0003, grounding=8.0,
                embryo_id="oracle_ai", task_id="analyze", value_score=7.0):
    return {
        "entry_id": entry_id,
        "status": "active",
        "lesson": lesson,
        "cost_usd": cost,
        "grounding_score": grounding,
        "embryo_id": embryo_id,
        "task_id": task_id,
        "value_score": value_score
    }


def test_load_entries_from_file():
    entries = [_make_entry("E1"), _make_entry("E2")]
    sf = _make_state_file(entries)
    loaded = load_entries(sf)
    assert len(loaded) == 2
    sf.unlink()


def test_load_entries_excludes_archived():
    entries = [_make_entry("E1"), {"entry_id": "E2", "status": "archived", "lesson": "old"}]
    sf = _make_state_file(entries)
    loaded = load_entries(sf)
    assert len(loaded) == 1
    sf.unlink()


def test_detect_recurring_lessons_finds_duplicates():
    entries = [
        _make_entry("E1", lesson="Low grounding"),
        _make_entry("E2", lesson="Low grounding"),
        _make_entry("E3", lesson="Low grounding"),
        _make_entry("E4", lesson="Different lesson"),
    ]
    recurring = detect_recurring_lessons(entries, threshold=2)
    assert len(recurring) == 1
    assert recurring[0]["occurrences"] == 3
    assert recurring[0]["severity"] == "MEDIUM"


def test_detect_recurring_lessons_high_severity():
    entries = [_make_entry(f"E{i}", lesson="Same problem") for i in range(5)]
    recurring = detect_recurring_lessons(entries, threshold=2)
    assert len(recurring) == 1
    assert recurring[0]["severity"] == "HIGH"


def test_detect_cost_anomalies_finds_outlier():
    entries = [
        _make_entry("E1", cost=0.0003),
        _make_entry("E2", cost=0.0003),
        _make_entry("E3", cost=0.0003),
        _make_entry("E4", cost=0.0003),
        _make_entry("E5", cost=0.01),  # outlier
    ]
    anomalies = detect_cost_anomalies(entries, z_threshold=1.5)
    assert len(anomalies) >= 1
    assert anomalies[0]["direction"] == "HIGH"


def test_detect_cost_anomalies_no_anomaly():
    entries = [_make_entry(f"E{i}", cost=0.0003) for i in range(5)]
    anomalies = detect_cost_anomalies(entries)
    assert len(anomalies) == 0


def test_detect_grounding_drift_improving():
    entries = [
        _make_entry("E1", grounding=5.0),
        _make_entry("E2", grounding=5.0),
        _make_entry("E3", grounding=9.0),
        _make_entry("E4", grounding=9.0),
    ]
    result = detect_grounding_drift(entries)
    assert result["trend"] == "IMPROVING"
    assert result["delta"] > 0


def test_detect_grounding_drift_degrading():
    entries = [
        _make_entry("E1", grounding=9.0),
        _make_entry("E2", grounding=9.0),
        _make_entry("E3", grounding=4.0),
        _make_entry("E4", grounding=4.0),
    ]
    result = detect_grounding_drift(entries)
    assert result["trend"] == "DEGRADING"


def test_detect_grounding_drift_stable():
    entries = [_make_entry(f"E{i}", grounding=7.0) for i in range(6)]
    result = detect_grounding_drift(entries)
    assert result["trend"] == "STABLE"


def test_detect_embryo_performance():
    entries = [
        _make_entry("E1", embryo_id="oracle", cost=0.0003, grounding=8.0),
        _make_entry("E2", embryo_id="oracle", cost=0.0004, grounding=9.0),
        _make_entry("E3", embryo_id="auditor", cost=0.0002, grounding=6.0),
    ]
    perf = detect_embryo_performance(entries)
    assert "oracle" in perf
    assert "auditor" in perf
    assert perf["oracle"]["total_runs"] == 2
    assert perf["auditor"]["total_runs"] == 1


def test_detect_task_concentration_dominant():
    entries = [_make_entry(f"E{i}", task_id="same_task") for i in range(8)]
    entries.append(_make_entry("E9", task_id="other_task"))
    result = detect_task_concentration(entries)
    assert "same_task" in result["dominant_tasks"]


def test_detect_task_concentration_diverse():
    entries = [_make_entry(f"E{i}", task_id=f"task_{i}") for i in range(5)]
    result = detect_task_concentration(entries)
    assert len(result["dominant_tasks"]) == 0


def test_detect_value_patterns():
    entries = [
        _make_entry("E1", value_score=9.0),
        _make_entry("E2", value_score=8.0),
        _make_entry("E3", value_score=3.0),
    ]
    result = detect_value_patterns(entries)
    assert result["avg_value"] > 0
    assert result["high_value_count"] == 2
    assert result["low_value_count"] == 1


def test_run_full_analysis_empty():
    sf = _make_state_file([])
    result = run_full_analysis(sf)
    assert result["status"] == "EMPTY_MEMORY_PALACE"
    sf.unlink()


def test_run_full_analysis_complete():
    entries = [
        _make_entry("E1", lesson="Low grounding", cost=0.0003, grounding=6.0, task_id="analyze"),
        _make_entry("E2", lesson="Low grounding", cost=0.0003, grounding=7.0, task_id="analyze"),
        _make_entry("E3", lesson="Good result", cost=0.0004, grounding=9.0, task_id="map"),
        _make_entry("E4", lesson="Good result", cost=0.0003, grounding=9.0, task_id="detect"),
    ]
    sf = _make_state_file(entries)
    result = run_full_analysis(sf)
    assert result["status"] == "ANALYSIS_COMPLETE"
    assert result["entries_analyzed"] == 4
    assert "health_score" in result
    assert "patterns" in result
    assert "recurring_lessons" in result["patterns"]
    assert "grounding_drift" in result["patterns"]
    sf.unlink()


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
    print(f"Memory Palace Pattern Detector Tests: {passed}/{passed+failed} PASS")
    if failed:
        sys.exit(1)
