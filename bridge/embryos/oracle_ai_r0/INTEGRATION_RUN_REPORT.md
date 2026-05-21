# Integration Run Report — Oracle AI Embryo R0

## Sprint

`SPR-ORACLE-EMBRYO-SCHEDULER-INTEGRATION-R0-001`

## Chain Executed

```
heartbeat_oracle_hook.py --run-once
  → oracle_ai_scheduler_adapter.invoke_embryo()
    → Pre-flight checks: PASS (kill_switch=INACTIVE, dispatcher=AVAILABLE, budget=OK)
      → oracle_ai_embryo.run_once()
        → Task chosen: map_capability_to_application (class: A1_ANALYZE)
        → Dispatcher: ALLOW
        → Provider: OpenAI gpt-4o-mini
        → Cost: $0.000114
        → Output: outputs/map_capability_to_application_20260521T032340.json
      → Verdict: AUTONOMOUS_CYCLE_COMPLETE
    → Adapter verdict: AUTONOMOUS_CYCLE_COMPLETE
  → Hook verdict: AUTONOMOUS_CYCLE_COMPLETE
```

## Timing

| Metric | Value |
|--------|-------|
| Hook start | 2026-05-21T03:23:36.687797Z |
| Hook end | 2026-05-21T03:23:40.953509Z |
| Duration | 4.27s |

## Pre-Flight Checks

| Check | Result |
|-------|--------|
| Kill-switch (hook level) | INACTIVE |
| Kill-switch (adapter level) | INACTIVE |
| Dispatcher available | AVAILABLE |
| Budget headroom | OK (spent: $0.0003, cap: $0.01) |

## Embryo Autonomous Decision

The embryo chose `map_capability_to_application` (not `detect_new_ai_capability_candidates` which was executed in cycle 1). This demonstrates:

1. **Repetition penalty** working (last task penalized by -5)
2. **Autonomous task rotation** without human instruction
3. **Action class A1_ANALYZE** correctly identified and allowed by Dispatcher

## State After

```json
{
  "total_cycles": 2,
  "last_task_executed": "map_capability_to_application",
  "last_task_result": "SUCCESS",
  "total_cost_usd": 0.000304,
  "consecutive_failures": 0,
  "status": "IDLE"
}
```

## Event Log (Integration Run)

```
HOOK_STARTED → heartbeat_oracle_hook_r0
DISPATCHER_REQUEST → map_capability_to_application (A1_ANALYZE)
DISPATCHER_ALLOW → Action class A1_ANALYZE is in allowed list
EMBRYO_TASK_STARTED → map_capability_to_application
EMBRYO_TASK_COMPLETED → cost: $0.000114
HOOK_COMPLETED → adapter_verdict: AUTONOMOUS_CYCLE_COMPLETE
```

## Hard Rules Verification

| Rule | Status |
|------|--------|
| 0 Supabase calls | PASS |
| 0 memory writes | PASS |
| 0 R1 operations | PASS |
| 0 PR/deploy/main | PASS |
| 0 Perplexity/DeepSeek | PASS |
| Kill-switch respected | PASS |
| Budget under cap | PASS |
| Max 1 provider call | PASS |
| Retries = 0 | PASS |
| No provider auto-replacement | PASS |
| Task chosen autonomously | PASS |
| Dispatcher permission requested | PASS |

## Conclusion

The full integration chain (Heartbeat Hook → Adapter → Embryo) works end-to-end. The embryo operates autonomously within its contract, choosing its own tasks, requesting Dispatcher permission, and producing auditable output artifacts. Total cost for 2 autonomous cycles: $0.000304.
