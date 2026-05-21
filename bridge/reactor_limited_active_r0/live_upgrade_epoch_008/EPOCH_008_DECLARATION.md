# EPOCH 008 DECLARATION

**Sprint:** SPR-EPOCH008-PROVIDER-MIGRATION-DIRECTIVE-CONFLICT-R0PLUS-001
**Date:** 2026-05-21
**Epoch:** 008
**Reactor:** R0+ (Limited Active)
**Status:** LIVE

---

## Objective

Epoch 008 introduces three major capabilities to the living pilot:

1. **Provider Migration Guard v0.1** — Detects provider model EOL risks, marks migration candidates, blocks auto-replacement, requires T1 for any model change.
2. **Multi-Directive Conflict Resolver v0.1** — Detects conflicts between multiple active T1 directives, resolves by explicit priority, validates safety constraints.
3. **Oracle/Auditor v0.5** — Multi-directive aware with conflict resolution. Uses winning directive set for scoring. Validates no directive authorizes prohibited actions.

---

## Directives Active

| ID | Priority | Type | Focus |
|---|---|---|---|
| T1D-001 | 9 | STRATEGIC_GUIDANCE | Produce artifacts that increase visible pilot value |
| T1D-002 | 10 | RISK_MITIGATION | Priorizar robustez sobre novedad |

**Conflict:** DETECTED (opposing intents: novelty vs robustness)
**Resolution:** T1D-002 wins (priority 10 > 9). T1D-001 suppressed.

---

## Provider Risk

| Provider | Model | EOL Date | Risk | Days Remaining |
|---|---|---|---|---|
| Anthropic | claude-sonnet-4-20250514 | 2026-06-15 | HIGH | 25 |

**Auto-replacement:** BLOCKED
**T1 Required:** YES

---

## Constraints

- R0+ only (no R1 operations)
- No Supabase/DB writes
- No Memory writes (except Memory Palace local)
- No PR/Deploy/Main push
- No provider auto-replacement
- Dispatcher required for all actions
- Kill-switch respected
