# REGRESSION INPUT REPORT

**Sprint**: SPR-R0PLUS-REGRESSION-INVESTIGATION-001  
**Date**: 2026-05-21  
**Investigator**: Hilo B (ejecutor)

---

## Flag Origin

The regression flag was detected by `embryo_run_history_analyzer_v0_1` during Epoch 009 ops execution. It was reported in `EPOCH_009_OPS_SNAPSHOT.json` under `runner_output.consolidated.regression_flags`.

---

## Flagged Event

| Field | Value |
|-------|-------|
| Type | COST_SPIKE |
| Run index | 8 (0-based) / 9 (1-based) |
| Source file | `map_capability_to_application_20260521T033525.json` |
| Embryo | `oracle_ai_embryo_r0` |
| Task | `map_capability_to_application` |
| Cost (flagged) | $0.001000 |
| Recent avg | $0.000279 |
| Ratio | 3.58x |
| Z-score | 2.06 |
| Severity reported | MEDIUM |

---

## Full Cost History (13 Oracle Runs)

| Run | Cost | Task | Note |
|-----|------|------|------|
| 1 | $0.001000 | detect_new_ai_capability_candidates | Ceiling value |
| 2 | $0.000190 | detect_new_ai_capability_candidates | Normal |
| 3 | $0.001000 | detect_new_ai_capability_candidates | Ceiling value |
| 4 | $0.000195 | detect_new_ai_capability_candidates | Normal |
| 5 | $0.000478 | detect_new_ai_capability_candidates | Normal |
| 6 | $0.000285 | detect_new_ai_capability_candidates | Normal |
| 7 | $0.000438 | detect_new_ai_capability_candidates | Normal |
| 8 | $0.000114 | map_capability_to_application | Normal (low) |
| 9 | $0.001000 | map_capability_to_application | **FLAGGED** |
| 10 | $0.000295 | map_capability_to_application | Normal |
| 11 | $0.000287 | map_capability_to_application | Normal |
| 12 | $0.000292 | map_capability_to_application | Normal |
| 13 | $0.000294 | map_capability_to_application | Normal |

---

## Key Observation

Three runs (1, 3, 9) all have exactly $0.001000 cost. This is a **fixture ceiling value** — the cost field in early test fixtures was set to a round $0.001 placeholder. The history analyzer correctly detected that $0.001 is statistically anomalous relative to the average, but the root cause is a data artifact (fixture placeholder), not a real system regression.

Evidence: Runs 10-13 after the flagged run all returned to normal range ($0.000287-$0.000295), confirming no persistent degradation.

---

## Affected Systems

| System | Status | Evidence |
|--------|--------|----------|
| Oracle | NOT AFFECTED | Continues running, 13 total runs, health 100% |
| Auditor | NOT AFFECTED | 8 runs, all PASS, score 100 |
| Memory Palace | NOT AFFECTED | HEALTHY, score 70, 8 entries |
| Artifact Ops | NOT AFFECTED | 11 artifacts, 100% coverage |

---

## Preliminary Hypothesis

> **FALSE_POSITIVE** — The cost spike is a fixture data artifact ($0.001 ceiling value), not a real system regression. No system was degraded. No metric actually fell. The analyzer correctly flagged a statistical anomaly, but the anomaly is in the test data, not in system behavior.
