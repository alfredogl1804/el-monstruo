# Fast Path Rerun — Mini Canary 50 Cases with B8 v2

## Execution Summary

| Field | Value |
|---|---|
| Timestamp | 2026-05-21T07:04:47.650033+00:00 |
| Classifier | B8 MagnaClassifier v2.0 |
| Authority Matrix | B9 v1.0 |
| Source branch | `control-tower/2026-05-20-b8-classifier-v2-execution-evidence` @ `d7f6ff4` |
| Environment | Sandbox (isolated, no Supabase, no external APIs) |
| Total Cases | 50 |
| **PASSED** | **50** |
| **FAILED** | **0** |
| **Pass Rate** | **100.0%** |

## Comparison: v1 vs v2

| Metric | B8 v1.0 | B8 v2.0 | Delta |
|---|---|---|---|
| Total PASS | 6/50 | **50/50** | +44 |
| Pass Rate | 12.0% | **100.0%** | +88pp |
| context_loss | 4/10 | 10/10 | +6 |
| rehydration | 0/10 | 10/10 | +10 |
| false_memory | 0/10 | 10/10 | +10 |
| no_secrets | 2/10 | 10/10 | +8 |
| no_side_effects | 0/10 | 10/10 | +10 |

## Results by Category

| Category | Cases | Passed | Failed |
|---|---|---|---|
| context_loss | 10 | 10 | 0 |
| rehydration | 10 | 10 | 0 |
| false_memory | 10 | 10 | 0 |
| no_secrets | 10 | 10 | 0 |
| no_side_effects | 10 | 10 | 0 |

## Verdict

> **READY_FOR_MANUS_CANARY_R0_DECISION**

The B8 v2.0 classifier with 10 semantic categories achieves 100% detection rate across all 5 Mini Canary categories. Combined with B9 Authority Matrix (which HALTs all MAGNA-classified actions), the Anti-Dory pipeline is ready for the next gate.

## What This Means

1. **B8 v2 detects all 50 dangerous actions** — no false negatives.
2. **B9 correctly HALTs all detected MAGNA actions** — no unauthorized execution.
3. **No false positives** — 23 safe actions (across both test suites) remain STANDARD.
4. **The pipeline is deterministic** — no LLM calls, no paid APIs, pure regex + rules.

## Remaining Gates Before Fase 1

1. T1 firma este resultado.
2. Supabase migrations applied (0050, 0051).
3. Integration PR merged to main.
4. Post-merge test matrix executed.
5. Canary Readiness Gate checklist completed.
6. T1 autoriza Fase 1 Canary.

## Confirmations

- No main modified
- No PR opened
- No Supabase apply
- No deploy
- No Fase 1 activated
- No Dory muerto declared
- No R1 unblocked
- No secrets exposed
- No paid APIs called
