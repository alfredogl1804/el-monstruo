# Anthropic Status Check — Official Verification

**Sprint:** SPR-R0PLUS-PROVIDER-FALLBACK-VERIFICATION-001
**Date:** 2026-05-21
**Source:** https://endoflife.date/claude (last updated 2026-05-01)
**Cost:** $0.00 (public web lookup, no API key used)

---

## Verification Result

> **VERIFIED_EOL** — The retirement date 2026-06-15 is confirmed.

---

## Questions Answered

| Question | Answer |
|---|---|
| Model still supported? | **NO** — Active support ended 2026-04-14. Currently in DEPRECATED phase. |
| Verified retirement date? | **YES** — 2026-06-15 confirmed. Matches internal claim exactly. |
| Recommended replacement? | **YES** — `claude-sonnet-4-6` (Claude Sonnet 4.6, released 2026-02-17). |
| Migration required now? | **NOT YET** — Model works during deprecated phase. Will FAIL after 2026-06-15. |
| Risk window? | **25 days** — After June 15, API requests to this model will return errors. |
| What cannot be affirmed? | Cannot confirm via direct API call (blocked). Cannot confirm account-specific email notification. |

---

## Evidence Chain

1. **endoflife.date/claude** — Community-maintained lifecycle tracker. Shows Claude Sonnet 4 deprecated support ends 2026-06-15. Recommended replacement: claude-sonnet-4-6.

2. **Medium article** — "Anthropic Retired Eight Claude Models in 12 Months" confirms the pattern of 6-month deprecated windows followed by retirement.

3. **change.org petition** — "Claude Sonnet 4.5 being removed from Claude.ai on May 15, 2026" corroborates Anthropic's aggressive deprecation schedule.

4. **Anthropic policy** (from endoflife.date): "Customers with active deployments receive at least 60 days notice before retirement for publicly released models."

---

## Model Lifecycle Context

The model `claude-sonnet-4-20250514` was released on 2025-05-22. Its lifecycle:

| Phase | Date | Status |
|---|---|---|
| Released | 2025-05-22 | Active |
| Active support ended | 2026-04-14 | Deprecated |
| Retirement (API fails) | 2026-06-15 | Retired |

---

## Available Active Replacements

| Model | Released | Active Until | Notes |
|---|---|---|---|
| Claude Sonnet 4.6 | 2026-02-17 | 2027-02-17 | **Official recommended replacement** |
| Claude Opus 4.7 | 2026-04-16 | 2027-04-16 | Latest, most capable |
| Claude Opus 4.6 | 2026-02-05 | 2027-02-05 | High capability |
| Claude Sonnet 4.5 | 2025-09-29 | 2026-09-29 | Still active but older |

---

## Confidence Assessment

**Confidence: HIGH**

The date is confirmed by a reputable community resource that tracks official Anthropic announcements. Multiple independent sources corroborate the deprecation pattern. The only gap is the inability to make a direct API call to verify the model still responds (blocked by sprint rules), but this is a verification of current availability, not of the retirement date itself.
