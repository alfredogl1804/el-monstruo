"""
R0+ Artifact Indexer v0.1
Auto-discovers all R0+ artifacts across epochs and production surges.
Produces a consolidated index JSON for T1 visibility.

Usage:
    python3 r0plus_artifact_indexer_v0_1.py [--base-dir /path/to/bridge]

Output:
    Prints JSON index to stdout.
    Optionally writes to bridge/r0plus_production_surge_001/fixtures/ARTIFACT_INDEX.json

Constraints:
    - R0+ only: local file scan, no external APIs
    - Read-only: does not modify any existing files
    - No secrets, no Supabase, no memory writes
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def discover_artifacts(base_dir: Path) -> list[dict]:
    """Scan known artifact directories and discover all R0+ artifacts."""
    artifacts = []
    
    # Pattern 1: Epoch artifacts
    epoch_pattern = base_dir / "reactor_limited_active_r0" / "live_upgrade_epoch_*" / "artifacts"
    epoch_dirs = sorted(Path(base_dir / "reactor_limited_active_r0").glob("live_upgrade_epoch_*/artifacts")) if (base_dir / "reactor_limited_active_r0").exists() else []
    
    for artifact_dir in epoch_dirs:
        epoch_match = re.search(r"epoch_(\d+)", str(artifact_dir))
        epoch_num = int(epoch_match.group(1)) if epoch_match else 0
        
        for py_file in sorted(artifact_dir.glob("*.py")):
            if py_file.name.startswith("test_"):
                continue
            if py_file.name.startswith("__"):
                continue
            
            artifact = _extract_artifact_metadata(py_file, epoch_num, "epoch")
            artifacts.append(artifact)
    
    # Pattern 2: Production surge artifacts
    surge_dirs = sorted(Path(base_dir).glob("r0plus_production_surge_*/artifacts")) if base_dir.exists() else []
    
    for artifact_dir in surge_dirs:
        surge_match = re.search(r"surge_(\d+)", str(artifact_dir))
        surge_num = int(surge_match.group(1)) if surge_match else 0
        
        for py_file in sorted(artifact_dir.glob("*.py")):
            if py_file.name.startswith("test_"):
                continue
            if py_file.name.startswith("__"):
                continue
            
            artifact = _extract_artifact_metadata(py_file, surge_num, "surge")
            artifacts.append(artifact)
    
    # Pattern 3: Provider ops tools
    provider_ops_dir = base_dir / "provider_ops"
    if provider_ops_dir.exists():
        for py_file in sorted(provider_ops_dir.glob("*.py")):
            if py_file.name.startswith("test_"):
                continue
            if py_file.name.startswith("__"):
                continue
            
            artifact = _extract_artifact_metadata(py_file, 0, "provider_ops")
            artifacts.append(artifact)
    
    # Pattern 4: State fabric tools
    state_fabric_dir = base_dir / "state_fabric"
    if state_fabric_dir.exists():
        for py_file in sorted(state_fabric_dir.glob("t1_*.py")):
            if py_file.name.startswith("test_"):
                continue
            
            artifact = _extract_artifact_metadata(py_file, 0, "state_fabric")
            artifacts.append(artifact)
    
    return artifacts


def _extract_artifact_metadata(py_file: Path, source_num: int, source_type: str) -> dict:
    """Extract metadata from a Python artifact file."""
    content = py_file.read_text(encoding="utf-8")
    
    # Extract docstring
    docstring = ""
    doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if doc_match:
        docstring = doc_match.group(1).strip()[:200]
    
    # Extract version from filename
    version_match = re.search(r"v(\d+)_(\d+)", py_file.name)
    version = f"v{version_match.group(1)}.{version_match.group(2)}" if version_match else "v0.1"
    
    # Count functions
    functions = re.findall(r"^def (\w+)", content, re.MULTILINE)
    public_functions = [f for f in functions if not f.startswith("_")]
    
    # Find test file
    test_file = py_file.parent / f"test_{py_file.name}"
    has_tests = test_file.exists()
    test_count = 0
    if has_tests:
        test_content = test_file.read_text(encoding="utf-8")
        test_count = len(re.findall(r"^def test_", test_content, re.MULTILINE))
    
    # File stats
    stat = py_file.stat()
    lines = content.count("\n") + 1
    
    return {
        "artifact_id": f"ART-{source_type.upper()}-{source_num:03d}-{py_file.stem}",
        "name": py_file.name,
        "path": str(py_file),
        "relative_path": str(py_file.relative_to(py_file.parents[2])) if len(py_file.parents) > 2 else str(py_file),
        "version": version,
        "source_type": source_type,
        "source_num": source_num,
        "docstring": docstring,
        "public_functions": public_functions,
        "function_count": len(public_functions),
        "lines_of_code": lines,
        "has_tests": has_tests,
        "test_file": str(test_file) if has_tests else None,
        "test_count": test_count,
        "created_at": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "size_bytes": stat.st_size
    }


def build_index(base_dir: Path) -> dict:
    """Build the complete artifact index."""
    artifacts = discover_artifacts(base_dir)
    
    # Compute summary stats
    total_tests = sum(a["test_count"] for a in artifacts)
    total_lines = sum(a["lines_of_code"] for a in artifacts)
    with_tests = sum(1 for a in artifacts if a["has_tests"])
    
    source_types = {}
    for a in artifacts:
        st = a["source_type"]
        source_types[st] = source_types.get(st, 0) + 1
    
    return {
        "index_version": "0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "r0plus_artifact_indexer_v0_1",
        "base_dir": str(base_dir),
        "summary": {
            "total_artifacts": len(artifacts),
            "total_with_tests": with_tests,
            "total_without_tests": len(artifacts) - with_tests,
            "total_test_count": total_tests,
            "total_lines_of_code": total_lines,
            "source_type_distribution": source_types,
            "test_coverage_pct": round(with_tests / len(artifacts) * 100, 1) if artifacts else 0
        },
        "artifacts": artifacts
    }


def filter_by_source_type(index: dict, source_type: str) -> list[dict]:
    """Filter artifacts by source type."""
    return [a for a in index["artifacts"] if a["source_type"] == source_type]


def filter_by_has_tests(index: dict, has_tests: bool = True) -> list[dict]:
    """Filter artifacts by test presence."""
    return [a for a in index["artifacts"] if a["has_tests"] == has_tests]


def find_artifact_by_name(index: dict, name_pattern: str) -> list[dict]:
    """Find artifacts matching a name pattern (regex)."""
    pattern = re.compile(name_pattern, re.IGNORECASE)
    return [a for a in index["artifacts"] if pattern.search(a["name"])]


def get_untested_artifacts(index: dict) -> list[dict]:
    """Get all artifacts without tests — candidates for test writing."""
    return filter_by_has_tests(index, has_tests=False)


def get_artifact_health_report(index: dict) -> dict:
    """Generate a health report for the artifact ecosystem."""
    artifacts = index["artifacts"]
    if not artifacts:
        return {"status": "EMPTY", "artifacts": 0}
    
    untested = get_untested_artifacts(index)
    low_function_count = [a for a in artifacts if a["function_count"] < 2]
    
    health_score = 100
    issues = []
    
    # Deduct for untested
    if untested:
        deduction = min(30, len(untested) * 10)
        health_score -= deduction
        issues.append(f"{len(untested)} artifacts without tests (-{deduction})")
    
    # Deduct for low function count
    if low_function_count:
        deduction = min(10, len(low_function_count) * 3)
        health_score -= deduction
        issues.append(f"{len(low_function_count)} artifacts with < 2 public functions (-{deduction})")
    
    status = "HEALTHY" if health_score >= 80 else "DEGRADED" if health_score >= 50 else "CRITICAL"
    
    return {
        "status": status,
        "health_score": max(0, health_score),
        "total_artifacts": len(artifacts),
        "untested_count": len(untested),
        "issues": issues,
        "recommendations": [
            f"Write tests for: {a['name']}" for a in untested[:5]
        ]
    }


if __name__ == "__main__":
    import sys
    
    base_dir = Path(__file__).parents[1].parent  # bridge/
    if len(sys.argv) > 2 and sys.argv[1] == "--base-dir":
        base_dir = Path(sys.argv[2])
    
    index = build_index(base_dir)
    print(json.dumps(index, indent=2))
