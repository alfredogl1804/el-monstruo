"""
14 mandatory tests for T1 Cockpit Data Injector v0.1.
Criterion: 14/14 PASS.
"""
import os
import sys
import json
import tempfile

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ARTIFACT_DIR)

from t1_cockpit_data_injector_v0_1 import (
    load_json_safe, count_files, get_latest_file,
    compute_pilot_health, build_embryo_summary,
    build_directive_summary, build_memory_summary,
    build_epoch_history, generate_cockpit_fixture,
    MEMORY_PALACE_PATH, DIRECTIVE_QUEUE_PATH, KILL_SWITCH_PATH,
    ORACLE_STATE_PATH, AUDITOR_STATE_PATH
)

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS [{passed:02d}] {name}")
    else:
        failed += 1
        print(f"  FAIL [{passed+failed:02d}] {name}")


print("=" * 60)
print("TEST SUITE: T1 Cockpit Data Injector v0.1 — 14 Tests")
print("=" * 60)

# 1. load_json_safe handles missing file
test("load_json_safe handles missing file", load_json_safe("/nonexistent/path.json") is None)

# 2. load_json_safe loads valid JSON
test("load_json_safe loads valid JSON", load_json_safe(MEMORY_PALACE_PATH) is not None)

# 3. count_files works
count = count_files(ARTIFACT_DIR, "*.py")
test("count_files works", count >= 2)

# 4. get_latest_file returns a file
latest = get_latest_file(ARTIFACT_DIR, "*.py")
test("get_latest_file returns file", latest is not None and os.path.exists(latest))

# 5. compute_pilot_health returns score and checks
score, checks = compute_pilot_health()
test("pilot_health returns score", 0 <= score <= 100 and len(checks) == 5)

# 6. pilot health score is reasonable (at least 40 for our system)
test("pilot health >= 40", score >= 40)

# 7. build_embryo_summary returns valid structure
oracle_summary = build_embryo_summary(ORACLE_STATE_PATH, "oracle_ai_embryo_r0")
test("embryo summary has required fields", all(k in oracle_summary for k in ["name", "status", "cycles", "cost_usd"]))

# 8. Oracle has cycles > 0
test("oracle has cycles", oracle_summary["cycles"] > 0)

# 9. build_directive_summary returns active count
ds = build_directive_summary()
test("directive summary has active", ds["active"] >= 1)

# 10. build_memory_summary returns entries
ms = build_memory_summary()
test("memory summary has entries", ms["total_entries"] >= 1)

# 11. build_epoch_history returns epochs
eh = build_epoch_history()
test("epoch history has entries", len(eh) >= 1)

# 12. generate_cockpit_fixture produces valid JSON file
with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
    tmp_path = tf.name
try:
    path, fixture = generate_cockpit_fixture(tmp_path)
    test("fixture file created", os.path.exists(path))
finally:
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

# 13. fixture has all required top-level keys
required_keys = ["cockpit_version", "generated_at", "generator", "pilot_health",
                 "embryos", "directives", "memory_palace", "epoch_history",
                 "outputs", "cost_summary"]
test("fixture has all keys", all(k in fixture for k in required_keys))

# 14. No secrets in fixture output
fixture_str = json.dumps(fixture)
secret_patterns = ["sk-", "sbp_", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "password"]
no_secrets = not any(p in fixture_str for p in secret_patterns)
test("no secrets in fixture", no_secrets)

print("=" * 60)
print(f"RESULT: {passed}/{passed+failed} PASS, {failed}/{passed+failed} FAIL")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
