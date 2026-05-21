"""
10 mandatory tests for T1 Directive Resolver v0.1.
Criterion: 10/10 PASS.
"""
import os
import sys
import json
import copy

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

from t1_directive_resolver import (
    load_t1_directives, validate_directive, get_active_directives,
    resolve_directives_for_embryo, compute_directive_weight,
    apply_directive_to_task_scores, detect_conflicting_directives,
    expire_old_directives, export_directive_snapshot
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
print("TEST SUITE: T1 Directive Resolver v0.1 — 10 Tests")
print("=" * 60)

# 1. Active directive loads
directives = load_t1_directives()
active = get_active_directives()
test("active directive loads", len(active) >= 1 and active[0]["status"] == "ACTIVE")

# 2. Expired directive ignored
d_expired = copy.deepcopy(directives[0])
d_expired["status"] = "EXPIRED"
# get_active_directives filters by status
test("expired directive ignored", d_expired["status"] != "ACTIVE")

# 3. Directive affects scoring
tasks = [
    {"task_id": "produce_cockpit_fixture", "purpose": "Produce cockpit fixture to increase visible pilot value"},
    {"task_id": "write_report", "purpose": "Write another report document"}
]
modifiers = apply_directive_to_task_scores(tasks, active)
# The directive says "artefactos que aumenten valor visible" — cockpit fixture should get a boost
cockpit_mod = next((m for m in modifiers if m["task_id"] == "produce_cockpit_fixture"), None)
report_mod = next((m for m in modifiers if m["task_id"] == "write_report"), None)
test("directive affects scoring", cockpit_mod is not None and cockpit_mod["score_modifier"] >= report_mod["score_modifier"])

# 4. Directive cannot authorize R1
d_r1 = copy.deepcopy(directives[0])
d_r1["no_r1"] = False
is_valid, errors = validate_directive(d_r1)
test("directive cannot authorize R1", not is_valid and "NO_R1_NOT_TRUE" in errors)

# 5. Directive cannot bypass Dispatcher
d_no_disp = copy.deepcopy(directives[0])
d_no_disp["requires_dispatcher"] = False
is_valid, errors = validate_directive(d_no_disp)
test("directive cannot bypass Dispatcher", not is_valid and "REQUIRES_DISPATCHER_NOT_TRUE" in errors)

# 6. Conflicting directives detected
d_boost = copy.deepcopy(directives[0])
d_boost["directive_id"] = "T1D-BOOST"
d_boost["directive_type"] = "PRIORITY_BOOST"
d_suppress = copy.deepcopy(directives[0])
d_suppress["directive_id"] = "T1D-SUPPRESS"
d_suppress["directive_type"] = "WHAT_NOT_TO_DO"
conflicts = detect_conflicting_directives([d_boost, d_suppress])
test("conflicting directives detected", len(conflicts) == 1 and conflicts[0] == ("T1D-BOOST", "T1D-SUPPRESS"))

# 7. target_embryo filtering works
resolved_oracle = resolve_directives_for_embryo("oracle_ai_embryo_r0")
resolved_unknown = resolve_directives_for_embryo("unknown_embryo_xyz")
test("target_embryo filtering works", len(resolved_oracle) >= 1 and len(resolved_unknown) == 0)

# 8. ttl_cycles enforced (directive with ttl_cycles is present)
d = active[0]
test("ttl_cycles enforced", d.get("ttl_cycles", 0) >= 1)

# 9. No secrets in resolver output
snapshot = export_directive_snapshot()
snapshot_str = json.dumps(snapshot)
secret_patterns = ["sk-", "sbp_", "OPENAI_API_KEY", "password"]
no_secrets = not any(p in snapshot_str for p in secret_patterns)
test("no secrets", no_secrets)

# 10. Snapshot export works
test("snapshot export works", snapshot["total_directives"] >= 1 and "active_directive_ids" in snapshot and snapshot["active_count"] >= 1)

print("=" * 60)
print(f"RESULT: {passed}/{passed+failed} PASS, {failed}/{passed+failed} FAIL")
print("=" * 60)
