# T1 Provider Fallback Decision Pack

**Sprint:** SPR-R0PLUS-PROVIDER-FALLBACK-VERIFICATION-001
**Date:** 2026-05-21
**Status:** READY_FOR_T1_DECISION

---

## Decision D1: Anthropic Status

| Option | Selected? |
|---|---|
| VERIFIED_SAFE | NO |
| **VERIFIED_EOL** | **YES** |
| UNVERIFIED_RISK | NO |
| BLOCKED_UNKNOWN | NO |

**Evidence:** endoflife.date confirms `claude-sonnet-4` deprecated support ends 2026-06-15. Active support already ended 2026-04-14. Official replacement: `claude-sonnet-4-6`.

**Confidence:** HIGH

---

## Decision D2: Recommended Action

| Option | Recommended? | Notes |
|---|---|---|
| KEEP_CURRENT_MONITOR | Alternative | Valid if T1 wants to test first (deadline: Jun 1) |
| **MIGRATE_NOW** | **YES** | To claude-sonnet-4-6 (active until 2027-02-17) |
| REMOVE_ANTHROPIC_TEMPORARILY | No | Unnecessary if migrating |
| WAIT_FOR_EXTERNAL_VERIFICATION | No | Already verified externally |

**Rationale:** EOL is verified. Official replacement exists. Migration is a single registry field change. No code logic changes needed. 25 days remaining is sufficient for orderly migration but not for indefinite delay.

---

## Decision D3: R0+ Next Step

| Option | Recommended? | Notes |
|---|---|---|
| **EXECUTE_PRODUCTION_SURGE_003** | **YES** | R0+ makes zero provider calls |
| PAUSE_PROVIDER_DEPENDENT_TASKS | No | No tasks depend on providers |
| RUN_ONE_MORE_ZERO_PROVIDER_SURGE | Equivalent | Same as above |
| BLOCKED | No | Nothing is blocked |

**Rationale:** R0+ operations make ZERO provider calls. The Anthropic risk does not affect R0+ execution. Production surges can continue safely regardless of provider status.

---

## Implementation (If D2=MIGRATE_NOW Approved)

```
File: bridge/provider_ops/provider_registry.json
Change: providers.anthropic.model
From:   "claude-sonnet-4-20250514"
To:     "claude-sonnet-4-6"

Additional:
1. Add "claude-sonnet-4-20250514" to providers.anthropic.deprecated_models
2. Remove "anthropic": "2026-06-15" from eol_overrides in migration guard
3. Run provider tests to confirm green
```

**Auto-execution:** NO (requires T1 approval)

---

## Timeline

| Date | Event |
|---|---|
| 2025-05-22 | claude-sonnet-4 released |
| 2026-04-14 | Active support ended (deprecated) |
| **2026-05-21** | **This verification (today)** |
| 2026-06-01 | Recommended decision deadline |
| 2026-06-15 | Model retirement (API fails) |

---

## T1 Actions Required

1. **Approve or reject D2 (MIGRATE_NOW)** — If approved, the registry update will be executed in the next sprint.
2. **Confirm D3 (EXECUTE_PRODUCTION_SURGE_003)** — R0+ continues regardless of D2 decision.
3. **Optional:** If T1 prefers KEEP_CURRENT_MONITOR, set a hard reminder for 2026-06-01.

---

## Safety Guarantees

- No model was changed in this sprint
- No provider was called
- No auto-replacement was attempted
- No secrets were read
- No state was modified
- All decisions require explicit T1 approval
