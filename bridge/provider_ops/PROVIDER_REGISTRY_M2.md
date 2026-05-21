# Provider Registry M2 — Post-Migration State

**Version:** 1.1.0
**Updated:** 2026-05-21
**Sprint:** SPR-R0PLUS-ANTHROPIC-MIGRATION-PATCH-001

---

## Migration Applied

| Field | Before | After |
|---|---|---|
| Anthropic model | claude-sonnet-4-20250514 | **claude-sonnet-4-6** |
| Anthropic deprecated_models | 3 entries | 4 entries (+claude-sonnet-4-20250514) |
| Registry version | 1.0.0 | 1.1.0 |
| Migration guard eol_overrides | anthropic: 2026-06-15 | {} (cleared) |
| T1 Decision | — | APPROVE |

---

## Provider Status

| Provider | Status | Model | Endpoint |
|---|---|---|---|
| OpenAI | ALLOWED | gpt-4o-mini | api.openai.com |
| **Anthropic** | **ALLOWED** | **claude-sonnet-4-6** | api.anthropic.com |
| Google | ALLOWED | gemini-2.0-flash | generativelanguage.googleapis.com |
| xAI | ALLOWED | grok-3-mini-fast | api.x.ai |
| Perplexity | BLOCKED_403 | — | — |
| DeepSeek | KEY_REQUIRED | — | — |

---

## Policies (Unchanged)

| Policy | Value |
|---|---|
| auto_fallback | false |
| auto_replacement | false |
| unknown_provider_default | DENY |
| unknown_model_default | DENY |
| deprecated_model_default | DENY |

---

## Budget (Unchanged)

| Constraint | Value |
|---|---|
| max_usd_per_day | $0.05 |
| max_usd_per_cycle | $0.03 |
| max_calls_per_provider_per_cycle | 1 |
| retries | 0 |

---

## Deprecated Models (All DENY)

| Provider | Deprecated Model |
|---|---|
| OpenAI | gpt-3.5-turbo |
| OpenAI | gpt-4-0314 |
| OpenAI | gpt-4-0613 |
| **Anthropic** | **claude-sonnet-4-20250514** |
| Anthropic | claude-3-haiku-20240307 |
| Anthropic | claude-3-5-haiku-20241022 |
| Anthropic | claude-3-opus-20240229 |
| Google | gemini-1.0-pro |
| Google | gemini-1.5-flash |
| Google | gemini-2.0-flash-lite |
| xAI | grok-beta |
| xAI | grok-1 |

---

## Tests

| Suite | Tests | Result |
|---|---|---|
| test_provider_registry.py | 14/14 | PASS |
| test_provider_migration_guard.py | 12/12 | PASS |

---

## Functions Available

### provider_registry.py (7 functions)

1. `load_provider_registry()` — Load registry JSON
2. `validate_provider_allowed(provider_id, model_id)` — Validate provider+model
3. `reject_blocked_provider(provider_id)` — Check if provider is blocked
4. `reject_deprecated_model(model_id)` — Check if model is deprecated
5. `get_allowed_m2_providers()` — List allowed providers for M2 cycles
6. `assert_no_provider_auto_replacement()` — Enforce no auto-replacement
7. `estimate_budget_for_cycle()` — Estimate max budget

### provider_migration_guard.py (8 functions)

1. `load_provider_registry()` — Load registry
2. `detect_provider_eol_risk()` — Detect EOL risks from overrides
3. `mark_model_migration_candidate()` — Create migration candidate record
4. `block_auto_replacement()` — Verify auto-replacement is blocked
5. `require_t1_for_model_change()` — Enforce T1 approval for changes
6. `produce_migration_options()` — Generate options for T1
7. `validate_current_model_allowed_until_t1_decision()` — Check current model status
8. `export_provider_migration_snapshot()` — Export full snapshot

### provider_fallback_verifier_v0_1.py (7 functions)

1. `load_provider_registry()` — Load registry
2. `verify_fallback_chain()` — Verify fallback chain exists
3. `verify_no_single_point_of_failure()` — Check provider diversity
4. `verify_deprecated_model_blocked()` — Confirm deprecated models are denied
5. `verify_auto_replacement_blocked()` — Confirm no auto-replacement
6. `verify_t1_required_for_changes()` — Confirm T1 enforcement
7. `run_full_verification()` — Run all verifications
