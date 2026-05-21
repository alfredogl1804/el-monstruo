# Provider Risk Snapshot

**Sprint:** SPR-R0PLUS-PROVIDER-FALLBACK-VERIFICATION-001
**Date:** 2026-05-21

---

## Provider Registry Status

| Provider | Status | Model | Risk Flag | EOL Reported |
|---|---|---|---|---|
| Anthropic | ALLOWED | claude-sonnet-4-20250514 | YES | 2026-06-15 |
| OpenAI | ALLOWED | gpt-4o-mini | NO | — |
| Google | ALLOWED | gemini-2.0-flash | NO | — |
| xAI | ALLOWED | grok-3-mini-fast | NO | — |
| Perplexity | BLOCKED_403 | — | NO | — |
| DeepSeek | KEY_REQUIRED | — | NO | — |

---

## Anthropic Risk Detail

| Field | Value |
|---|---|
| Model | claude-sonnet-4-20250514 |
| Reported EOL | 2026-06-15 |
| Days remaining | 25 |
| Risk level (per guard) | HIGH |
| Auto-replacement | BLOCKED (policy) |
| Requires T1 | YES |
| EOL verified externally | **NO** |

---

## EOL Source Analysis

The date `2026-06-15` is **hardcoded** in `bridge/provider_ops/provider_migration_guard.py` at line 288:

```python
eol_overrides = {
    "anthropic": "2026-06-15"
}
```

This was introduced during Epoch 008 as a **hypothetical risk scenario** for testing the migration guard. There is **no evidence** that this date came from an official Anthropic announcement.

---

## Evidence Available

1. Internal `eol_overrides` dict in provider_migration_guard.py
2. Migration guard output: "25 days remaining"
3. Provider registry: model listed as ALLOWED

## Evidence Missing

1. Official Anthropic deprecation announcement
2. Anthropic API changelog entry
3. Anthropic status page confirmation
4. Any external source confirming 2026-06-15 as EOL
5. Model availability test (blocked by no-provider-calls rule)

---

## Verdict

> **UNVERIFIED_INTERNAL_CLAIM**

The EOL date is an internal assumption, not a verified fact. The migration guard correctly flags it, but T1 should not treat it as confirmed without external verification.
