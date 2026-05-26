"""Tests for R0+ Artifact Indexer v0.1"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r0plus_artifact_indexer_v0_1 import (
    build_index,
    discover_artifacts,
    filter_by_has_tests,
    filter_by_source_type,
    find_artifact_by_name,
    get_artifact_health_report,
    get_untested_artifacts,
)


def _create_test_structure(tmp_dir: Path):
    """Create a realistic test directory structure."""
    # Epoch artifact
    epoch_dir = tmp_dir / "reactor_limited_active_r0" / "live_upgrade_epoch_005" / "artifacts"
    epoch_dir.mkdir(parents=True)
    (epoch_dir / "provider_health_monitor_v0_1.py").write_text(
        '"""Provider Health Monitor v0.1\\nMonitors provider health.\\n"""\n\ndef check_health():\n    return True\n\ndef get_status():\n    return "OK"\n'
    )
    (epoch_dir / "test_provider_health_monitor.py").write_text(
        "def test_check_health():\n    pass\n\ndef test_get_status():\n    pass\n\ndef test_returns_dict():\n    pass\n"
    )

    # Epoch 007 artifact
    epoch7_dir = tmp_dir / "reactor_limited_active_r0" / "live_upgrade_epoch_007" / "artifacts"
    epoch7_dir.mkdir(parents=True)
    (epoch7_dir / "t1_cockpit_data_injector_v0_1.py").write_text(
        '"""T1 Cockpit Data Injector v0.1\\nGenerates cockpit fixture data.\\n"""\n\ndef generate_fixture():\n    return {}\n\ndef validate_fixture(f):\n    return True\n'
    )
    (epoch7_dir / "test_t1_cockpit_data_injector.py").write_text(
        "def test_generate():\n    pass\n\ndef test_validate():\n    pass\n"
    )

    # Surge artifact (no test)
    surge_dir = tmp_dir / "r0plus_production_surge_001" / "artifacts"
    surge_dir.mkdir(parents=True)
    (surge_dir / "some_tool_v0_1.py").write_text('"""Some Tool v0.1"""\n\ndef do_thing():\n    pass\n')

    # Provider ops
    prov_dir = tmp_dir / "provider_ops"
    prov_dir.mkdir(parents=True)
    (prov_dir / "provider_migration_guard.py").write_text(
        '"""Provider Migration Guard"""\n\ndef check_eol():\n    return []\n\ndef get_alternatives():\n    return []\n\ndef validate_migration():\n    return True\n'
    )
    (prov_dir / "test_provider_migration_guard.py").write_text(
        "def test_check_eol():\n    pass\n\ndef test_alternatives():\n    pass\n\ndef test_validate():\n    pass\n\ndef test_empty():\n    pass\n"
    )

    # State fabric
    sf_dir = tmp_dir / "state_fabric"
    sf_dir.mkdir(parents=True)
    (sf_dir / "t1_directive_resolver.py").write_text(
        '"""T1 Directive Resolver"""\n\ndef resolve_directives_for_embryo(eid):\n    return []\n'
    )
    (sf_dir / "test_t1_directive_resolver.py").write_text("def test_resolve():\n    pass\n")

    return tmp_dir


def test_discover_artifacts_finds_epoch_artifacts():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        artifacts = discover_artifacts(base)
        epoch_arts = [a for a in artifacts if a["source_type"] == "epoch"]
        assert len(epoch_arts) == 2, f"Expected 2 epoch artifacts, got {len(epoch_arts)}"


def test_discover_artifacts_finds_surge_artifacts():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        artifacts = discover_artifacts(base)
        surge_arts = [a for a in artifacts if a["source_type"] == "surge"]
        assert len(surge_arts) == 1, f"Expected 1 surge artifact, got {len(surge_arts)}"


def test_discover_artifacts_finds_provider_ops():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        artifacts = discover_artifacts(base)
        prov_arts = [a for a in artifacts if a["source_type"] == "provider_ops"]
        assert len(prov_arts) == 1


def test_discover_artifacts_finds_state_fabric():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        artifacts = discover_artifacts(base)
        sf_arts = [a for a in artifacts if a["source_type"] == "state_fabric"]
        assert len(sf_arts) == 1


def test_discover_artifacts_excludes_test_files():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        artifacts = discover_artifacts(base)
        test_files = [a for a in artifacts if a["name"].startswith("test_")]
        assert len(test_files) == 0, "Test files should not appear as artifacts"


def test_extract_metadata_has_required_fields():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        artifacts = discover_artifacts(base)
        required_fields = [
            "artifact_id",
            "name",
            "path",
            "version",
            "source_type",
            "docstring",
            "public_functions",
            "function_count",
            "lines_of_code",
            "has_tests",
            "test_count",
        ]
        for art in artifacts:
            for field in required_fields:
                assert field in art, f"Missing field {field} in {art['name']}"


def test_build_index_has_summary():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        index = build_index(base)
        assert "summary" in index
        assert "total_artifacts" in index["summary"]
        assert index["summary"]["total_artifacts"] == 5


def test_build_index_has_metadata():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        index = build_index(base)
        assert "index_version" in index
        assert "generated_at" in index
        assert "generated_by" in index


def test_filter_by_source_type():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        index = build_index(base)
        epoch_only = filter_by_source_type(index, "epoch")
        assert len(epoch_only) == 2


def test_filter_by_has_tests():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        index = build_index(base)
        with_tests = filter_by_has_tests(index, True)
        without_tests = filter_by_has_tests(index, False)
        assert len(with_tests) + len(without_tests) == index["summary"]["total_artifacts"]


def test_find_artifact_by_name():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        index = build_index(base)
        results = find_artifact_by_name(index, "provider")
        assert len(results) >= 1
        assert any("provider" in r["name"] for r in results)


def test_get_untested_artifacts():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        index = build_index(base)
        untested = get_untested_artifacts(index)
        assert len(untested) >= 1
        for a in untested:
            assert a["has_tests"] is False


def test_get_artifact_health_report():
    with tempfile.TemporaryDirectory() as tmp:
        base = _create_test_structure(Path(tmp))
        index = build_index(base)
        report = get_artifact_health_report(index)
        assert "status" in report
        assert "health_score" in report
        assert report["health_score"] >= 0
        assert report["health_score"] <= 100


def test_empty_directory():
    with tempfile.TemporaryDirectory() as tmp:
        index = build_index(Path(tmp))
        assert index["summary"]["total_artifacts"] == 0
        report = get_artifact_health_report(index)
        assert report["status"] == "EMPTY"


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
    print(f"\n{'=' * 60}")
    print(f"R0+ Artifact Indexer Tests: {passed}/{passed + failed} PASS")
    if failed:
        sys.exit(1)
