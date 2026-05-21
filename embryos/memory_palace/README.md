# Memory Palace v0.1

Local, append-only memory system for the Oracle/Auditor bicéfalo pair.

## Purpose

Allows embryos to:
1. Remember learnings from previous cycles
2. Avoid repeating low-value tasks
3. Improve autonomous task selection
4. Accumulate artifact history
5. Record claims, grounding, auditor verdicts, and real utility
6. Produce better R0+ artifacts using accumulated knowledge

## Constraints

- **R0+ only:** Local JSON files, no external DB
- **Append-only:** Entries are never physically deleted, only archived
- **No secrets:** Validated on every append
- **No raw CoT:** Validated on every append
- **No Memento/Anti-Dory/Supabase:** Strictly local
- **No external memory writes:** Everything stays in this directory

## API

| Function | Purpose |
|----------|---------|
| `load_memory_palace()` | Load state from disk |
| `append_memory_entry(entry)` | Add a new entry (validated) |
| `retrieve_recent_entries(n)` | Get N most recent active entries |
| `retrieve_by_embryo_id(id)` | Filter by embryo |
| `retrieve_by_artifact_id(ref)` | Filter by artifact reference |
| `retrieve_lessons()` | Extract all lessons |
| `retrieve_low_value_patterns()` | Find low-value entries |
| `score_task_against_memory(task, embryo)` | Score a task for repetition/value |
| `prune_memory_if_needed(max)` | Archive oldest low-value if over limit |
| `export_memory_snapshot()` | Export state for reporting |

## Usage

```python
from memory_palace import load_memory_palace, append_memory_entry, score_task_against_memory

# Score a task before choosing it
score = score_task_against_memory("detect_new_ai", "oracle_ai_embryo_r0")
if score["recommendation"] == "AVOID_REPEATED_LOW_VALUE":
    # Choose a different task
    pass

# After completing a cycle, record it
entry = { ... }  # See schema
append_memory_entry(entry)
```

## Tests

```bash
python3 embryos/memory_palace/test_memory_palace.py
```

Expected: 12/12 PASS
