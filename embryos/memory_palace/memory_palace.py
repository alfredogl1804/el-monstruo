"""
Memory Palace v0.1
Local, append-only memory system for the Oracle/Auditor bicéfalo pair.

Constraints:
- R0+ only: local JSON files, no external DB
- Append-only: entries are never physically deleted, only archived
- No secrets, no raw CoT, no Memento/Anti-Dory/Supabase
- No external memory writes
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

STATE_FILE = Path(__file__).parent / "memory_palace_state.json"
SCHEMA_FILE = Path(__file__).parent / "memory_palace_schema.json"

# Patterns that indicate secrets or raw CoT
SECRET_PATTERNS = [
    r"sk-[a-zA-Z0-9]{20,}",
    r"sbp_[a-zA-Z0-9]{20,}",
    r"ghp_[a-zA-Z0-9]{20,}",
    r"xai-[a-zA-Z0-9]{20,}",
    r"AIza[a-zA-Z0-9_-]{30,}",
    r"OPENAI_API_KEY",
    r"ANTHROPIC_API_KEY",
]

RAW_COT_PATTERNS = [
    r"<thinking>",
    r"</thinking>",
    r"<internal_monologue>",
    r"Let me think step by step",
]


def _check_for_secrets(text: str) -> bool:
    """Return True if text contains secret-looking patterns."""
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def _check_for_raw_cot(text: str) -> bool:
    """Return True if text contains raw chain-of-thought patterns."""
    for pattern in RAW_COT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def _validate_entry(entry: dict) -> tuple[bool, str]:
    """Validate a memory entry against constraints."""
    required_fields = [
        "memory_id", "timestamp", "source_embryo_id", "cycle_id",
        "task_id", "action_class", "artifact_refs", "claims_count",
        "grounding_score", "auditor_verdict", "value_score", "cost_usd",
        "lessons", "avoid_next_time", "next_best_action", "status"
    ]
    for field in required_fields:
        if field not in entry:
            return False, f"Missing required field: {field}"

    # Check for secrets in all string fields
    all_text = json.dumps(entry)
    if _check_for_secrets(all_text):
        return False, "Entry contains secret-looking patterns"
    if _check_for_raw_cot(all_text):
        return False, "Entry contains raw chain-of-thought"

    # Validate action_class
    valid_actions = ["A0_OBSERVE", "A1_ANALYZE", "A2_RECOMMEND", "A3_DRAFT"]
    if entry["action_class"] not in valid_actions:
        return False, f"Invalid action_class: {entry['action_class']}"

    # Validate status
    if entry["status"] not in ["active", "archived"]:
        return False, f"Invalid status: {entry['status']}"

    # Validate auditor_verdict
    if entry["auditor_verdict"] not in ["PASS", "PARTIAL", "FAIL", "PENDING"]:
        return False, f"Invalid auditor_verdict: {entry['auditor_verdict']}"

    return True, "OK"


def load_memory_palace(state_file: Optional[Path] = None) -> dict:
    """Load the Memory Palace state from disk."""
    path = state_file or STATE_FILE
    if path.exists():
        return json.loads(path.read_text())
    return {
        "version": "0.1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "entries": [],
        "stats": {
            "total_entries": 0,
            "total_archived": 0,
            "total_active": 0,
            "unique_embryos": [],
            "unique_tasks": [],
            "total_cost_usd": 0.0
        }
    }


def _save_state(state: dict, state_file: Optional[Path] = None):
    """Save state to disk."""
    path = state_file or STATE_FILE
    path.write_text(json.dumps(state, indent=2))


def _update_stats(state: dict):
    """Recalculate stats from entries."""
    entries = state["entries"]
    active = [e for e in entries if e["status"] == "active"]
    archived = [e for e in entries if e["status"] == "archived"]
    state["stats"] = {
        "total_entries": len(entries),
        "total_archived": len(archived),
        "total_active": len(active),
        "unique_embryos": list(set(e["source_embryo_id"] for e in entries)),
        "unique_tasks": list(set(e["task_id"] for e in entries)),
        "total_cost_usd": round(sum(e["cost_usd"] for e in entries), 6)
    }


def append_memory_entry(entry: dict, state_file: Optional[Path] = None) -> tuple[bool, str]:
    """Append a new memory entry. Returns (success, message)."""
    valid, msg = _validate_entry(entry)
    if not valid:
        return False, msg

    state = load_memory_palace(state_file)
    state["entries"].append(entry)
    _update_stats(state)
    _save_state(state, state_file)
    return True, f"Entry {entry['memory_id']} appended successfully"


def retrieve_recent_entries(n: int = 5, state_file: Optional[Path] = None) -> list:
    """Retrieve the N most recent active entries."""
    state = load_memory_palace(state_file)
    active = [e for e in state["entries"] if e["status"] == "active"]
    return sorted(active, key=lambda x: x["timestamp"], reverse=True)[:n]


def retrieve_by_embryo_id(embryo_id: str, state_file: Optional[Path] = None) -> list:
    """Retrieve all active entries for a specific embryo."""
    state = load_memory_palace(state_file)
    return [e for e in state["entries"]
            if e["source_embryo_id"] == embryo_id and e["status"] == "active"]


def retrieve_by_artifact_id(artifact_ref: str, state_file: Optional[Path] = None) -> list:
    """Retrieve all entries referencing a specific artifact."""
    state = load_memory_palace(state_file)
    return [e for e in state["entries"]
            if artifact_ref in e["artifact_refs"] and e["status"] == "active"]


def retrieve_lessons(state_file: Optional[Path] = None) -> list:
    """Retrieve all lessons from active entries."""
    state = load_memory_palace(state_file)
    lessons = []
    for e in state["entries"]:
        if e["status"] == "active" and e["lessons"]:
            for lesson in e["lessons"]:
                lessons.append({
                    "lesson": lesson,
                    "source_embryo": e["source_embryo_id"],
                    "task_id": e["task_id"],
                    "timestamp": e["timestamp"]
                })
    return lessons


def retrieve_low_value_patterns(threshold: float = 4.0, state_file: Optional[Path] = None) -> list:
    """Retrieve entries with value_score below threshold (low value patterns)."""
    state = load_memory_palace(state_file)
    return [e for e in state["entries"]
            if e["status"] == "active" and e["value_score"] < threshold]


def score_task_against_memory(task_id: str, embryo_id: str, state_file: Optional[Path] = None) -> dict:
    """Score a task against memory to determine if it should be penalized or boosted."""
    state = load_memory_palace(state_file)
    active = [e for e in state["entries"] if e["status"] == "active"]

    # Find previous executions of this task by this embryo
    prev_executions = [e for e in active
                       if e["task_id"] == task_id and e["source_embryo_id"] == embryo_id]

    if not prev_executions:
        return {
            "task_id": task_id,
            "repetition_count": 0,
            "avg_value_score": 0,
            "penalty": 0.0,
            "boost": 0.0,
            "recommendation": "NEW_TASK_NO_HISTORY"
        }

    repetition_count = len(prev_executions)
    avg_value = sum(e["value_score"] for e in prev_executions) / len(prev_executions)

    # Penalty for repeated low-value tasks
    penalty = 0.0
    if repetition_count >= 2 and avg_value < 5.0:
        penalty = min(5.0, repetition_count * 1.5)

    # Boost for high-value compounding tasks
    boost = 0.0
    if avg_value >= 7.0 and repetition_count <= 3:
        boost = min(3.0, avg_value * 0.3)

    recommendation = "PROCEED"
    if penalty >= 3.0:
        recommendation = "AVOID_REPEATED_LOW_VALUE"
    elif boost >= 2.0:
        recommendation = "COMPOUND_HIGH_VALUE"

    return {
        "task_id": task_id,
        "repetition_count": repetition_count,
        "avg_value_score": round(avg_value, 2),
        "penalty": round(penalty, 2),
        "boost": round(boost, 2),
        "recommendation": recommendation
    }


def prune_memory_if_needed(max_active: int = 100, state_file: Optional[Path] = None) -> int:
    """Archive oldest low-value entries if active count exceeds max. Returns count archived."""
    state = load_memory_palace(state_file)
    active = [e for e in state["entries"] if e["status"] == "active"]

    if len(active) <= max_active:
        return 0

    # Sort by value_score ascending, then by timestamp ascending (oldest first)
    candidates = sorted(active, key=lambda x: (x["value_score"], x["timestamp"]))
    to_archive = len(active) - max_active
    archived_count = 0

    for entry in candidates[:to_archive]:
        # Find and mark as archived (append-only: we modify status, not delete)
        for e in state["entries"]:
            if e["memory_id"] == entry["memory_id"]:
                e["status"] = "archived"
                archived_count += 1
                break

    _update_stats(state)
    _save_state(state, state_file)
    return archived_count


def export_memory_snapshot(state_file: Optional[Path] = None) -> dict:
    """Export a snapshot of the current Memory Palace state for reporting."""
    state = load_memory_palace(state_file)
    return {
        "snapshot_timestamp": datetime.now(timezone.utc).isoformat(),
        "version": state["version"],
        "stats": state["stats"],
        "recent_entries": retrieve_recent_entries(5, state_file),
        "lessons": retrieve_lessons(state_file),
        "low_value_patterns": retrieve_low_value_patterns(state_file=state_file)
    }
