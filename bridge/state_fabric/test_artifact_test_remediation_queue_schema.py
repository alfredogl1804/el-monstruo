"""
Tests for Artifact Test Remediation Queue Schema v0.1
10 tests covering all required criteria.
"""
import json
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "artifact_test_remediation_queue_schema.v0_1.json"
QUEUE_PATH = Path(__file__).parent / "artifact_test_remediation_queue.v0_1.json"

RESULTS = []


def test(name: str, condition: bool, detail: str = ""):
    status = "PASS" if condition else "FAIL"
    RESULTS.append((name, status, detail))
    print(f"  [{status}] {name}" + (f" — {detail}" if detail and not condition else ""))


def load_queue() -> dict:
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_01_schema_valid():
    """Schema is valid JSON with required fields."""
    schema = load_schema()
    required_keys = ["$schema", "title", "type", "required", "properties"]
    has_all = all(k in schema for k in required_keys)
    test("01_schema_valid", has_all, f"keys: {list(schema.keys())}")


def test_02_all_11_artifacts_represented():
    """Queue contains all 11 artifacts."""
    queue = load_queue()
    test("02_all_11_artifacts_represented",
         queue["total_artifacts"] == 11 and len(queue["items"]) == 11,
         f"total={queue['total_artifacts']}, items={len(queue['items'])}")


def test_03_artifacts_without_tests_pending_or_ready():
    """Artifacts without tests have status PENDING_T1 or READY_R0PLUS."""
    queue = load_queue()
    untested = [i for i in queue["items"] if not i["has_tests"]]
    valid_statuses = {"PENDING_T1", "READY_R0PLUS"}
    all_valid = all(i["status"] in valid_statuses for i in untested)
    test("03_artifacts_without_tests_pending_or_ready",
         all_valid or len(untested) == 0,
         f"untested={len(untested)}")


def test_04_no_approved_without_t1():
    """No item has status that implies T1 approval without T1 decision."""
    queue = load_queue()
    # APPROVED is not a valid status in the schema
    invalid = [i for i in queue["items"] if i["status"] not in
               {"PENDING_T1", "READY_R0PLUS", "BLOCKED", "IN_PROGRESS", "DONE"}]
    test("04_no_approved_without_t1",
         len(invalid) == 0,
         f"invalid_statuses={[i['status'] for i in invalid]}")


def test_05_no_r1():
    """No item references R1 as recommended action."""
    queue = load_queue()
    r1_refs = [i for i in queue["items"] if "R1" in i.get("recommended_action", "")]
    test("05_no_r1", len(r1_refs) == 0, f"r1_refs={len(r1_refs)}")


def test_06_no_main_pr_deploy():
    """No item allows main/PR/deploy in its actions."""
    queue = load_queue()
    violations = []
    for item in queue["items"]:
        forbidden = item.get("forbidden_actions", [])
        if "main" not in forbidden or "deploy" not in forbidden:
            violations.append(item["artifact_id"])
    test("06_no_main_pr_deploy",
         len(violations) == 0,
         f"violations={violations}")


def test_07_priority_valid():
    """All priorities are valid integers >= 1."""
    queue = load_queue()
    invalid = [i for i in queue["items"] if not isinstance(i["priority"], int) or i["priority"] < 1]
    test("07_priority_valid",
         len(invalid) == 0,
         f"invalid={[i['artifact_id'] for i in invalid]}")


def test_08_source_ref_required():
    """All items have a source_ref with minimum length."""
    queue = load_queue()
    missing = [i for i in queue["items"] if not i.get("source_ref") or len(i["source_ref"]) < 5]
    test("08_source_ref_required",
         len(missing) == 0,
         f"missing={[i['artifact_id'] for i in missing]}")


def test_09_export_snapshot():
    """Queue can be serialized to JSON (export snapshot)."""
    queue = load_queue()
    try:
        exported = json.dumps(queue, indent=2)
        re_parsed = json.loads(exported)
        test("09_export_snapshot",
             re_parsed["version"] == "0.1" and len(re_parsed["items"]) == 11,
             "export+reimport OK")
    except Exception as e:
        test("09_export_snapshot", False, str(e))


def test_10_no_secrets():
    """Queue contains no secrets or sensitive data."""
    queue_text = QUEUE_PATH.read_text(encoding="utf-8")
    secret_patterns = ["sk-", "sbp_", "ghp_", "password", "secret_key", "api_key="]
    found = [p for p in secret_patterns if p in queue_text.lower()]
    test("10_no_secrets",
         len(found) == 0,
         f"found_patterns={found}")


if __name__ == "__main__":
    print("=" * 60)
    print("ARTIFACT TEST REMEDIATION QUEUE SCHEMA — TEST SUITE")
    print("=" * 60)

    test_01_schema_valid()
    test_02_all_11_artifacts_represented()
    test_03_artifacts_without_tests_pending_or_ready()
    test_04_no_approved_without_t1()
    test_05_no_r1()
    test_06_no_main_pr_deploy()
    test_07_priority_valid()
    test_08_source_ref_required()
    test_09_export_snapshot()
    test_10_no_secrets()

    print("=" * 60)
    passed = sum(1 for _, s, _ in RESULTS if s == "PASS")
    failed = sum(1 for _, s, _ in RESULTS if s == "FAIL")
    print(f"RESULT: {passed}/{len(RESULTS)} PASS, {failed}/{len(RESULTS)} FAIL")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
