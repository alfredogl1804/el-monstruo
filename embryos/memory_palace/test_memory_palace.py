"""Tests for Memory Palace v0.1 — 12 mandatory tests."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from memory_palace import (
    append_memory_entry,
    export_memory_snapshot,
    load_memory_palace,
    prune_memory_if_needed,
    retrieve_by_artifact_id,
    retrieve_by_embryo_id,
    retrieve_lessons,
    retrieve_low_value_patterns,
    score_task_against_memory,
)

PASS = 0
FAIL = 0


def test(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")


def make_entry(
    memory_id="MEM-OAI-001",
    task_id="detect_new_ai",
    embryo_id="oracle_ai_embryo_r0",
    value_score=7.0,
    status="active",
    lessons=None,
    avoid=None,
    cost=0.001,
    grounding=8.0,
    verdict="PASS",
):
    return {
        "memory_id": memory_id,
        "timestamp": "2026-05-21T04:00:00Z",
        "source_embryo_id": embryo_id,
        "cycle_id": 1,
        "task_id": task_id,
        "action_class": "A0_OBSERVE",
        "artifact_refs": ["provider_health_monitor_v0_1"],
        "claims_count": 5,
        "grounding_score": grounding,
        "auditor_verdict": verdict,
        "value_score": value_score,
        "cost_usd": cost,
        "lessons": lessons or ["Use real-time validation for release dates"],
        "avoid_next_time": avoid or ["Relying on training data for dates"],
        "next_best_action": "map_capability_to_application",
        "status": status,
    }


# Use temp files for isolation
def get_temp_state():
    tf = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    json.dump(
        {
            "version": "0.1.0",
            "created_at": "2026-05-21T04:00:00Z",
            "entries": [],
            "stats": {
                "total_entries": 0,
                "total_archived": 0,
                "total_active": 0,
                "unique_embryos": [],
                "unique_tasks": [],
                "total_cost_usd": 0.0,
            },
        },
        tf,
    )
    tf.close()
    return Path(tf.name)


print("=" * 60)
print("MEMORY PALACE v0.1 — TEST SUITE")
print("=" * 60)

# Test 1: Schema valid
schema_path = Path(__file__).parent / "memory_palace_schema.json"
schema = json.loads(schema_path.read_text())
test("1. Schema valid (has required fields)", "required" in schema and len(schema["required"]) == 16)

# Test 2: Append entry
sf = get_temp_state()
entry = make_entry()
ok, msg = append_memory_entry(entry, sf)
test("2. Append entry succeeds", ok and "appended" in msg)

# Test 3: Retrieve by embryo
results = retrieve_by_embryo_id("oracle_ai_embryo_r0", sf)
test("3. Retrieve by embryo returns entry", len(results) == 1 and results[0]["memory_id"] == "MEM-OAI-001")

# Test 4: Retrieve by artifact
results = retrieve_by_artifact_id("provider_health_monitor_v0_1", sf)
test("4. Retrieve by artifact returns entry", len(results) == 1)

# Test 5: Retrieve lessons
lessons = retrieve_lessons(sf)
test("5. Retrieve lessons returns lesson", len(lessons) == 1 and "real-time" in lessons[0]["lesson"])

# Test 6: Low value pattern detected
sf2 = get_temp_state()
low_entry = make_entry(memory_id="MEM-OAI-002", value_score=2.0)
append_memory_entry(low_entry, sf2)
patterns = retrieve_low_value_patterns(threshold=4.0, state_file=sf2)
test("6. Low value pattern detected", len(patterns) == 1 and patterns[0]["value_score"] == 2.0)

# Test 7: Task scoring changes by memory
sf3 = get_temp_state()
# Add 3 low-value repetitions
for i in range(3):
    e = make_entry(memory_id=f"MEM-OAI-{i + 10}", task_id="bad_task", value_score=3.0)
    append_memory_entry(e, sf3)
score = score_task_against_memory("bad_task", "oracle_ai_embryo_r0", sf3)
test(
    "7. Task scoring penalizes repeated low-value",
    score["penalty"] >= 3.0 and score["recommendation"] == "AVOID_REPEATED_LOW_VALUE",
)

# Test 8: No raw CoT permitted
sf4 = get_temp_state()
cot_entry = make_entry(memory_id="MEM-OAI-099")
cot_entry["lessons"] = ["<thinking>Let me think step by step</thinking>"]
ok, msg = append_memory_entry(cot_entry, sf4)
test("8. No raw CoT permitted (rejected)", not ok and "chain-of-thought" in msg)

# Test 9: No secret-looking strings permitted
sf5 = get_temp_state()
secret_entry = make_entry(memory_id="MEM-OAI-100")
secret_entry["next_best_action"] = "Use key sk-abcdefghijklmnopqrstuvwxyz1234"
ok, msg = append_memory_entry(secret_entry, sf5)
test("9. No secret-looking strings (rejected)", not ok and "secret" in msg)

# Test 10: Append-only enforcement (no delete, only archive)
sf6 = get_temp_state()
e1 = make_entry(memory_id="MEM-OAI-200", value_score=1.0)
append_memory_entry(e1, sf6)
state = load_memory_palace(sf6)
initial_count = len(state["entries"])
prune_memory_if_needed(max_active=0, state_file=sf6)
state_after = load_memory_palace(sf6)
test(
    "10. Append-only (prune archives, not deletes)",
    len(state_after["entries"]) == initial_count and state_after["entries"][0]["status"] == "archived",
)

# Test 11: Archive marker without physical delete
test(
    "11. Archive marker set correctly",
    state_after["entries"][0]["status"] == "archived" and state_after["stats"]["total_archived"] == 1,
)

# Test 12: Export snapshot
sf7 = get_temp_state()
append_memory_entry(make_entry(memory_id="MEM-OAI-300"), sf7)
snapshot = export_memory_snapshot(sf7)
test(
    "12. Export snapshot has required fields",
    "stats" in snapshot and "recent_entries" in snapshot and "lessons" in snapshot,
)

print(f"\n{'=' * 60}")
print(f"RESULT: {PASS}/12 PASS, {FAIL}/12 FAIL")
print(f"{'=' * 60}")
if FAIL > 0:
    sys.exit(1)
