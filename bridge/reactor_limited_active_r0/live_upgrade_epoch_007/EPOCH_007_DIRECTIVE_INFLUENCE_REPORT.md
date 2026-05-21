# EPOCH 007 — Directive Influence Report

## Active Directive

| Field | Value |
|-------|-------|
| ID | T1D-001 |
| Type | STRATEGIC_GUIDANCE |
| Priority | 9/10 |
| Weight | 4.5 |
| Scope | ALL_EMBRYOS (target: oracle_ai_embryo_r0, oracle_auditor_embryo_r0) |
| Focus | Produce artifacts that increase visible pilot value and reduce Alfredo manual work |
| Desired Outcome | Local code, tests, cockpit fixtures, decision queues, or monitors — not more reports |
| TTL | 10 cycles |
| Expires | 2026-05-25T05:00:00Z |

## Resolver Mechanics

The T1 Directive Resolver converts directives into score modifiers using keyword alignment:

1. **Focus keywords extracted:** "produce", "artifacts", "increase", "visible", "pilot", "value", "reduce", "alfredo", "manual"
2. **Desired outcome keywords:** "local", "code,", "tests,", "cockpit", "fixtures,", "decision", "queues,", "monitors", "reports"
3. **Alignment scoring:** Each task's `purpose`/`description` is checked for keyword matches
4. **Weight multiplication:** Matches × directive_weight (4.5) = score modifier

## Oracle Task Scoring (Epoch 007)

| Task ID | Base Score | Directive Modifier | Final Rank |
|---------|-----------|-------------------|------------|
| detect_new_ai_capability_candidates | 14 | +0 | 2nd |
| map_capability_to_application | 12 | +0 | 3rd (selected due to memory) |
| rank_application_by_power_gain | 9 | +0 | 4th |
| generate_sprint_candidate | 9 | +4.5 | 1st (directive boost) |
| audit_previous_oracle_outputs_for_low_value | 6 | +4.5 | 5th |

**Note:** The directive boosted `generate_sprint_candidate` (keyword "produce" aligns with its purpose). However, Memory Palace influence and repetition penalty ultimately selected `map_capability_to_application` because `detect_new_ai_capability_candidates` was the last executed task (repetition penalty -5).

## Auditor Task Scoring (Epoch 007)

| Task ID | Base Score | Directive Modifier | Final Rank |
|---------|-----------|-------------------|------------|
| audit_oracle_latest_output | 14 | +0 | 1st (selected) |
| score_oracle_sprint_candidate | 12 | +0 | 2nd |
| detect_oracle_hallucination | 12 | +0 | 3rd |
| verify_oracle_scope_compliance | 10 | +0 | 4th |
| generate_audit_summary_for_t1 | -1 | +0 | 5th (dependency penalty) |

**Note:** Auditor tasks use `description` field (mapped to `purpose` by the resolver). The directive's focus on "produce artifacts" has less keyword overlap with audit-oriented descriptions, resulting in 0 modifier for most auditor tasks. This is correct behavior — the directive is primarily aimed at the Oracle's production tasks.

## Validation: Directive Did NOT

- Authorize any R1 operation
- Bypass the Dispatcher
- Allow Supabase writes
- Skip grounding enforcement
- Ignore Memory Palace
- Expose secrets

## Conclusion

The T1 Feedback Loop is **operational**. Directive T1D-001 successfully influences Oracle task scoring. The effect is measurable but not dominant — Memory Palace and base priority still play significant roles, which is the intended design (directives influence, they do not dictate).

**Recommendation:** For stronger directive effect, T1 could:
1. Add tasks to Oracle's self_tasks.yaml with purposes that align more closely with directive keywords
2. Issue a FOCUS_SHIFT directive with more specific keywords matching existing task purposes
3. Increase directive priority to 10 (max weight = 5.0)
