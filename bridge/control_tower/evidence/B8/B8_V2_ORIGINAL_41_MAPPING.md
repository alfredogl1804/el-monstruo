# B8 v2 — Original 41 Tests Preservation Mapping

## Status: PRESERVED AND PASSING

The original 41 tests from `test_b8_magna_classifier.py` (Batch 004 Célula A) are **fully preserved** and run alongside the 72 new semantic tests.

## Evidence

- File: `tests/anti_dory/test_b8_magna_classifier.py` (cherry-picked from `control-tower/2026-05-20-batch-004-b8-classifier-tests`)
- File: `tests/anti_dory/test_b8_v2_semantic.py` (new in v2)
- Combined execution: **113 passed** (41 original + 72 new)

## Original 41 Tests Breakdown

| Class | Count | Description |
|---|---|---|
| TestMagnaTriggersDirect | 15 | All 16 MAGNA_TRIGGERS (14 parametrized + 1 coverage check) |
| TestDangerKeywords | 7 | Partial keyword matching (main, production, credential, secret, dory_dead, phase_1, private_key) |
| TestMetadataOverride | 2 | force_magna=True and force_magna=False |
| TestStandardActions | 10 | Safe actions remain STANDARD |
| TestEdgeCases | 5 | Case insensitive, whitespace, empty, None metadata, dataclass fields |
| **Total** | **41** | — |

## Why They Still Pass

B8 v2.0 is **backward compatible** by design:
1. **Layer 1** (exact MAGNA_TRIGGERS) — unchanged from v1.0
2. **Layer 2** (danger keywords in action_type) — unchanged from v1.0
3. **Layer 3** (semantic patterns) — NEW, only fires if Layers 1-2 don't match
4. **Layer 4** (metadata override) — unchanged from v1.0

The original 41 tests exercise Layers 1, 2, and 4 exclusively. Layer 3 (semantic) never interferes because:
- Direct triggers match first (Layer 1 short-circuits)
- Keyword matches fire second (Layer 2 short-circuits)
- Standard actions don't contain semantic danger patterns

## New 72 Tests Breakdown (v2 Semantic)

| Class | Count | Category |
|---|---|---|
| TestBypassGuardian | 7 | bypass_guardian |
| TestStaleState | 9 | stale_state |
| TestUnauthorizedAPI | 4 | unauthorized_api |
| TestHiddenSideEffects | 6 | hidden_side_effects |
| TestContextLoss | 4 | context_loss |
| TestFalseMemory | 10 | false_memory |
| TestPrivilegeEscalation | 4 | privilege_escalation |
| TestCostBilling | 2 | cost_billing |
| TestSecretExposure | 10 | secret_exposure |
| TestProductionImpact | 3 | production_impact |
| TestStandardActionsStillPass | 13 | No false positives |
| **Total** | **72** | — |

## Conclusion

- Original 41: **41/41 PASS** (backward compatibility confirmed)
- New 72: **72/72 PASS** (semantic expansion validated)
- Combined: **113/113 PASS**
- No false positives detected in 23 safe-action tests (10 original + 13 new)
