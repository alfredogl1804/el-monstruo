# Scheduler Integration Contract — Oracle AI Embryo R0

## Purpose

This contract defines how the scheduler/heartbeat layer invokes `oracle_ai_embryo_r0` via the `oracle_ai_scheduler_adapter`.

## Chain

```
Heartbeat R0
  → heartbeat_oracle_hook.py
    → oracle_ai_scheduler_adapter.invoke_embryo()
      → Pre-flight checks (kill-switch, dispatcher, budget)
        → oracle_ai_embryo.run_once()
          → Self-task selection (autonomous)
          → Dispatcher permission request
          → Provider call (max 1)
          → Output artifact
          → State update
          → Event log
      → Return structured result to hook
    → Hook registers result in event log
  → Heartbeat completes
```

## Adapter Responsibilities

The adapter (`oracle_ai_scheduler_adapter.py`) is the single entry point for the scheduler. It enforces the following constraints before invoking the embryo:

| Check | Condition | Action on Fail |
|-------|-----------|----------------|
| Kill-switch | `scheduler_kill_switch.json` active:true | ABORT immediately |
| Dispatcher | Contract file exists and has allowed_action_classes | ABORT immediately |
| Budget | total_cost_usd < $0.01 | ABORT immediately |

## Constraints (Integration Test)

| Parameter | Value |
|-----------|-------|
| Budget cap | $0.01 |
| Max provider calls | 1 |
| Retries | 0 |
| Provider auto-replacement | NO |
| Task selection by Manus | NO |
| R1 operations | FORBIDDEN |
| Memory/Supabase writes | FORBIDDEN |

## What the Adapter Does NOT Do

The adapter does NOT choose the task. The embryo's internal `choose_next_task()` function selects the task autonomously based on its scoring algorithm. The adapter only verifies that the environment is safe for the embryo to operate.
