# REGRESSION INVESTIGATOR REPORT — Artifact Documentation

**Artifact**: `regression_investigator_v0_1.py`  
**Sprint**: SPR-R0PLUS-REGRESSION-INVESTIGATION-001  
**Date**: 2026-05-21

---

## Purpose

The Regression Investigator is a local Python artifact that analyzes regression flags produced by `embryo_run_history_analyzer_v0_1` and determines whether they represent real system regressions or false positives.

---

## Capabilities

The investigator differentiates five regression types: cost spikes (z-score anomaly detection with fixture ceiling awareness), task repetition (dominance threshold detection), grounding drops (score threshold analysis), audit failures (verdict analysis), and health drops (system-level degradation). It produces a structured JSON report with classification, severity, root cause candidate, confidence score, and recommended action.

---

## Interface

The `RegressionInvestigator` class accepts run history (list of run dicts), regression flags (list of flag dicts from history analyzer), and optional memory palace entries. The `investigate()` method returns a complete investigation report. The `run_from_files()` function provides a file-based entry point that reads directly from the repo structure.

---

## Tests

12 tests covering all required criteria — all PASS.

| # | Test | Status |
|---|------|--------|
| 1 | Loads valid run history | PASS |
| 2 | Handles missing/empty data | PASS |
| 3 | Detects false positive | PASS |
| 4 | Detects real regression | PASS |
| 5 | Detects cost spike | PASS |
| 6 | Detects grounding drop | PASS |
| 7 | Detects repeated task | PASS |
| 8 | Calculates baseline | PASS |
| 9 | Classifies severity | PASS |
| 10 | Produces valid JSON | PASS |
| 11 | No external API calls | PASS |
| 12 | No secrets | PASS |

---

## Constraints

No external API calls, no Supabase, no DB, no secrets, no network. Pure local computation. Does not modify any state.
