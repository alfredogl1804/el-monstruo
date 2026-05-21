# Anthropic Migration Patch Report

**Sprint:** SPR-R0PLUS-ANTHROPIC-MIGRATION-PATCH-001
**Date:** 2026-05-21
**T1 Decision:** APPROVE
**Status:** MIGRATION_COMPLETE

---

## Summary

T1 approved migration of Anthropic provider from deprecated model `claude-sonnet-4-20250514` (retirement: 2026-06-15) to active model `claude-sonnet-4-6` (active until: 2027-02-17).

---

## Changes Applied

| File | Change |
|---|---|
| `provider_ops/provider_registry.json` | model: claude-sonnet-4-20250514 → claude-sonnet-4-6 |
| `provider_ops/provider_registry.json` | deprecated_models: +claude-sonnet-4-20250514 |
| `provider_ops/provider_registry.json` | version: 1.0.0 → 1.1.0 |
| `provider_ops/provider_registry.json` | migration_log: added T1 decision record |
| `provider_ops/provider_migration_guard.py` | eol_overrides: removed anthropic entry |
| `provider_ops/test_provider_registry.py` | Updated: 10 → 14 tests (added migration-specific) |
| `provider_ops/test_provider_migration_guard.py` | Updated: reflects post-migration state |
| `provider_ops/PROVIDER_REGISTRY_M2.md` | New: updated documentation |

---

## Verification

| Check | Result |
|---|---|
| Old model (claude-sonnet-4-20250514) DENY | PASS |
| New model (claude-sonnet-4-6) ALLOW | PASS |
| No auto-replacement | PASS |
| T1 decision recorded | PASS |
| Provider registry valid JSON | PASS |
| Migration guard PASS | PASS |
| No secrets in code | PASS |
| No provider calls made | PASS |
| test_provider_registry.py | 14/14 PASS |
| test_provider_migration_guard.py | 12/12 PASS |

---

## Before/After

| Metric | Before | After |
|---|---|---|
| Anthropic model | claude-sonnet-4-20250514 | claude-sonnet-4-6 |
| Anthropic status | ALLOWED (deprecated model) | ALLOWED (active model) |
| EOL risk | HIGH (25 days) | NONE |
| Provider health score | 75/100 | 95/100 |
| Days of active support | 0 (deprecated phase) | ~270 (until 2027-02-17) |

---

## Hard Rules Confirmation

| Rule | Status |
|---|---|
| No provider calls | CONFIRMED |
| No retries | CONFIRMED |
| No auto-replacement | CONFIRMED (T1 explicit approval) |
| No R1 | CONFIRMED |
| No main | CONFIRMED |
| No PR | CONFIRMED |
| No deploy | CONFIRMED |
| No Supabase | CONFIRMED |
| No DB | CONFIRMED |
| No secrets read | CONFIRMED |
| No Memento/Anti-Dory | CONFIRMED |
| No APP_VISION | CONFIRMED |
| No canon | CONFIRMED |
| No PRE-IA | CONFIRMED |
| Budget $0.00 | CONFIRMED |
