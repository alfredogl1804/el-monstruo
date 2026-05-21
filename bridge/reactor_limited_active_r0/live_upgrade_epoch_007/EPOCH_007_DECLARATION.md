# EPOCH 007 — T1 Feedback Loop Declaration

## Identity

| Field | Value |
|-------|-------|
| Epoch | 007 |
| Sprint | SPR-EPOCH007-T1-FEEDBACK-LOOP-R0PLUS-001 |
| Phase | R0+ (LIMITED_ACTIVE) |
| Declared | 2026-05-20T12:00:00Z |
| Operator | Hilo B (Manus Ejecutor Técnico) |
| T1 Authority | Alfredo Góngora |

## Mission Statement

Epoch 007 introduces the **T1 Feedback Loop** — the first mechanism by which T1 (Alfredo) can influence embryo behavior without modifying code. Through the T1 Directive Queue and Directive Resolver, human strategic intent is converted into scoring modifiers that guide autonomous task selection.

## New Capabilities Introduced

1. **T1 Directive Queue** — Structured JSON queue where T1 deposits strategic directives
2. **T1 Directive Resolver** — Converts directives into score modifiers for embryo task selection
3. **Oracle v0.4 (Directive-Aware)** — `choose_next_task()` now consults the Directive Resolver
4. **Auditor v0.4 (Directive-Aware)** — Same integration for the auditor half
5. **Third R0+ Artifact** — Directive-guided artifact production

## Active Directive

| ID | Type | Priority | Scope | Focus |
|----|------|----------|-------|-------|
| T1D-001 | STRATEGIC_GUIDANCE | 9/10 | ALL_EMBRYOS | Produce artifacts that increase visible pilot value and reduce Alfredo manual work |

## Hard Constraints (unchanged)

- 0 Supabase calls
- 0 Memory writes (Memento/Anti-Dory)
- 0 R1 operations
- 0 PRs, 0 merge to main, 0 force-push
- 0 secrets in logs
- Kill-switch always respected
- Dispatcher required for all actions

## Expected Outputs

1. EPOCH_007_CHAIN_LOG.jsonl — Full execution chain
2. EPOCH_007_ORACLE_OUTPUT.json — Oracle cycle output
3. EPOCH_007_AUDIT_REPORT.md — Auditor assessment
4. EPOCH_007_T1_REPORT.md — T1-facing summary
5. EPOCH_007_MEMORY_PALACE_SNAPSHOT.json — Memory state
6. EPOCH_007_DIRECTIVE_INFLUENCE_REPORT.md — How directives affected decisions
7. Third R0+ Artifact (TBD by Oracle recommendation)

## Success Criteria

- Oracle executes with directive influence visible in scoring
- Auditor validates Oracle output with grounding enforcement
- Directive influence is measurable and documented
- All tests pass (target: ~100+ tests)
- Cost < $0.01 for the epoch cycle
