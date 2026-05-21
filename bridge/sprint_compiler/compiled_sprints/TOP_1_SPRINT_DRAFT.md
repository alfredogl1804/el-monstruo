# SPRINT DRAFT: SPR-ORACLE-004

**Title:** State Persistence Layer for Cross-Cycle Memory
**Status:** DRAFT (Unsigned, Not Executable)
**Source:** Oracle v0.4 (Value Score: 92, Risk Score: 30)

## Objective
Enable the reactor to remember context between cron executions using local JSON files, allowing multi-step reasoning across days without violating `NO_SUPABASE_WRITES`.

## Scope
Create a `state_fabric/memory` module that reads/writes to local JSON files. Integrate this module into the cycle runner to persist state.

## Allowed Files
- `bridge/state_fabric/memory.py`
- `bridge/state_fabric/test_memory.py`
- `bridge/reactor_limited_active_r0/run_cycle.py` (modification)

## Forbidden Files
- `main` branch files
- `APP_VISION.md`
- Any file outside `bridge/`

## Expected Artifacts
1. `memory.py` module.
2. Unit tests for memory module.
3. Updated `run_cycle.py` that utilizes memory.

## Tests
- `test_memory_read`
- `test_memory_write`
- `test_memory_limits` (ensure JSON doesn't grow indefinitely)

## Gates
- Code review by Auditor loop.
- All tests must pass before integration.

## Rollback
- Revert `run_cycle.py` to previous version.
- Delete `memory.py`.

## T1 Decision Needed
- Approve the creation of the memory module.
- Confirm local JSON is acceptable for persistence.

## No-Go List
- DO NOT connect to Supabase.
- DO NOT connect to any external database.
- DO NOT store secrets in memory.

## Estimated Cost
$0.01 USD

## Definition of Done
- Module created and tested.
- Cycle runner successfully reads/writes state across 2 consecutive executions.
