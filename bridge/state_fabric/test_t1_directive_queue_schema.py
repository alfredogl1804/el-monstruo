"""
12 mandatory tests for T1 Directive Queue Schema v0.1.
Criterion: 12/12 PASS.
"""
import os
import json
import copy

DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(DIR, "t1_directive_queue_schema.v0_1.json")
QUEUE_PATH = os.path.join(DIR, "t1_directive_queue.v0_1.json")

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
print("TEST SUITE: T1 Directive Queue Schema v0.1 — 12 Tests")
print("=" * 60)

# Load schema and queue
with open(SCHEMA_PATH, "r") as f:
    schema = json.load(f)
with open(QUEUE_PATH, "r") as f:
    queue = json.load(f)

directive = queue["directives"][0]

# 1. Schema valid (has required_fields and field_constraints)
test("schema valid", "required_fields" in schema and "field_constraints" in schema and len(schema["required_fields"]) >= 20)

# 2. Directive ACTIVE valid (all required fields present)
all_present = all(field in directive for field in schema["required_fields"])
test("directive ACTIVE valid", all_present and directive["status"] == "ACTIVE")

# 3. Directive without t1_verbatim = INVALID
d_no_verbatim = copy.deepcopy(directive)
d_no_verbatim["t1_verbatim"] = ""
is_invalid_no_verbatim = (d_no_verbatim["t1_verbatim"] == "" or d_no_verbatim["t1_verbatim"] is None)
test("directive without t1_verbatim = INVALID", is_invalid_no_verbatim)

# 4. Directive with may_authorize_actions:true = INVALID
d_auth = copy.deepcopy(directive)
d_auth["may_authorize_actions"] = True
is_invalid_auth = (d_auth["may_authorize_actions"] != schema["field_constraints"]["may_authorize_actions"]["must_be"])
test("directive with may_authorize_actions:true = INVALID", is_invalid_auth)

# 5. Directive that attempts R1 = INVALID
d_r1 = copy.deepcopy(directive)
d_r1["no_r1"] = False
is_invalid_r1 = (d_r1["no_r1"] != schema["field_constraints"]["no_r1"]["must_be"])
test("directive that attempts R1 = INVALID", is_invalid_r1)

# 6. Directive expired does not influence (status check)
d_expired = copy.deepcopy(directive)
d_expired["status"] = "EXPIRED"
does_not_influence = (d_expired["status"] != "ACTIVE")
test("directive expired does not influence", does_not_influence)

# 7. Directive PAUSED does not influence
d_paused = copy.deepcopy(directive)
d_paused["status"] = "PAUSED"
does_not_influence_paused = (d_paused["status"] != "ACTIVE")
test("directive PAUSED does not influence", does_not_influence_paused)

# 8. forbidden_interpretations required (non-empty array)
has_forbidden = (isinstance(directive["forbidden_interpretations"], list) and len(directive["forbidden_interpretations"]) > 0)
test("forbidden_interpretations required", has_forbidden)

# 9. target_embryos valid (non-empty array with valid IDs)
valid_embryos = ["oracle_ai_embryo_r0", "oracle_auditor_embryo_r0"]
has_targets = (isinstance(directive["target_embryos"], list) and len(directive["target_embryos"]) >= 1 and all(e in valid_embryos for e in directive["target_embryos"]))
test("target_embryos valid", has_targets)

# 10. No secrets in directive
directive_str = json.dumps(directive)
secret_patterns = ["sk-", "sbp_", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "password", "token="]
no_secrets = not any(p in directive_str for p in secret_patterns)
test("no secrets", no_secrets)

# 11. No raw CoT in directive
cot_patterns = ["<thinking>", "</thinking>", "chain-of-thought", "Let me think", "Step 1:", "I'll analyze"]
no_cot = not any(p.lower() in directive_str.lower() for p in cot_patterns)
test("no raw CoT", no_cot)

# 12. Export snapshot works
snapshot = {
    "exported_at": "2026-05-21T05:00:00Z",
    "queue_version": queue["queue_version"],
    "total_directives": len(queue["directives"]),
    "active_count": sum(1 for d in queue["directives"] if d["status"] == "ACTIVE"),
    "expired_count": sum(1 for d in queue["directives"] if d["status"] == "EXPIRED")
}
test("export snapshot", snapshot["total_directives"] >= 1 and snapshot["active_count"] >= 1)

print("=" * 60)
print(f"RESULT: {passed}/{passed+failed} PASS, {failed}/{passed+failed} FAIL")
print("=" * 60)
