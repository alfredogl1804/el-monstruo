# Fallback Options Matrix

**Sprint:** SPR-R0PLUS-PROVIDER-FALLBACK-VERIFICATION-001
**Date:** 2026-05-21
**Model at risk:** claude-sonnet-4-20250514
**Retirement date:** 2026-06-15 (VERIFIED)
**Days remaining:** 25

---

## Options Summary

| Option | Name | Risk | Cost | Quality | Recommended? |
|---|---|---|---|---|---|
| A | KEEP_CURRENT_MONITOR | HIGH (fails Jun 15) | $0 | None | If T1 will decide by Jun 1 |
| B | MIGRATE_TO_NEW_ANTHROPIC_MODEL | LOW | LOW | POSITIVE | **YES (recommended)** |
| C | TEMPORARILY_REMOVE_ANTHROPIC | LOW | $0 | None for R0+ | If reducing dependency |
| D | REPLACE_WITH_EXISTING_PROVIDER | MEDIUM | Variable | Variable | If leaving Anthropic |
| E | REQUIRE_EXTERNAL_VERIFICATION | LOW | Minimal | None | Already verified — low value |

---

## Option A: KEEP_CURRENT_MONITOR

**Benefit:** Zero disruption. Model still works during deprecated phase. Buys time for testing replacement.

**Risk:** Model WILL fail on 2026-06-15. If not migrated by then, all Anthropic-dependent operations break.

**Required T1 Action:** Set calendar reminder for 2026-06-01 to force migration decision.

**Recommended if:** T1 wants to test replacement model before committing.

**Not recommended if:** T1 cannot guarantee attention before 2026-06-15.

---

## Option B: MIGRATE_TO_NEW_ANTHROPIC_MODEL (RECOMMENDED)

**Benefit:** Stays within Anthropic ecosystem. Official replacement (`claude-sonnet-4-6`) is newer, better, active until 2027-02-17. Gives 9 months of runway.

**Risk:** Requires T1 to approve model change. May have different behavior/pricing. Needs testing.

**Required T1 Action:** Approve model change from `claude-sonnet-4-20250514` to `claude-sonnet-4-6` in provider_registry.json.

**Implementation:** Update `model` field in registry. Update `eol_overrides` in migration guard. Run verification test.

**Recommended if:** T1 wants to stay with Anthropic and the official replacement is acceptable.

---

## Option C: TEMPORARILY_REMOVE_ANTHROPIC_FROM_R0PLUS

**Benefit:** Eliminates Anthropic risk entirely from R0+ operations.

**Risk:** Reduces available providers from 4 to 3.

**Required T1 Action:** Approve setting Anthropic status to SUSPENDED_PENDING_MIGRATION.

**Recommended if:** T1 wants a clean risk profile while deciding on replacement.

---

## Option D: REPLACE_WITH_EXISTING_ALLOWED_PROVIDER

**Benefit:** Uses already-configured provider as primary. No new setup needed.

**Risk:** Changes the default provider assumption.

**Required T1 Action:** Approve which existing provider becomes the Anthropic replacement.

**Candidates:**

| Provider | Model | Strength |
|---|---|---|
| OpenAI | gpt-4o-mini | Cost-effective, reliable |
| Google | gemini-2.0-flash | Fast, multimodal |
| xAI | grok-3-mini-fast | Low latency |

**Recommended if:** T1 wants to move away from Anthropic entirely.

---

## Option E: REQUIRE_EXTERNAL_VERIFICATION_BEFORE_DECISION

**Benefit:** Maximum caution. Direct API test confirms model availability.

**Risk:** Delays decision. External source already confirms EOL.

**Required T1 Action:** Authorize one diagnostic API call to Anthropic.

**Recommended if:** T1 wants absolute certainty.

**Not recommended if:** External source already confirms EOL (which it does).

---

## Recommendation

> **Option B: MIGRATE_TO_NEW_ANTHROPIC_MODEL**

Rationale: The EOL is verified. The official replacement (`claude-sonnet-4-6`) exists, is active, and has 9 months of support. Migration is a single field change in the registry. No code logic changes needed since R0+ makes zero provider calls. The change only matters when R1 operations begin.
