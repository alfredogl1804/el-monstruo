"""
Tests for Provider Registry Guard v1.1
10 tests + 4 migration-specific tests = 14 tests.
Updated for SPR-R0PLUS-ANTHROPIC-MIGRATION-PATCH-001.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from provider_registry import (
    load_provider_registry,
    validate_provider_allowed,
    reject_blocked_provider,
    reject_deprecated_model,
    get_allowed_m2_providers,
    assert_no_provider_auto_replacement,
    estimate_budget_for_cycle,
)

PASS = 0
FAIL = 0


def test(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}")


def run_tests():
    global PASS, FAIL
    print("=" * 60)
    print("Provider Registry Guard Tests (v1.1 post-migration)")
    print("=" * 60)

    reg = load_provider_registry()

    # Test 1: 4 providers permitidos PASS
    allowed = get_allowed_m2_providers(reg)
    test("1. 4 providers permitidos PASS", len(allowed) == 4)

    # Test 2: Perplexity DENY
    test("2. Perplexity DENY", reject_blocked_provider("perplexity", reg) is True)

    # Test 3: DeepSeek DENY
    test("3. DeepSeek DENY", reject_blocked_provider("deepseek", reg) is True)

    # Test 4: Modelo deprecated DENY (old OpenAI model)
    ok, reason = validate_provider_allowed("openai", "gpt-3.5-turbo", reg)
    test("4. Modelo deprecated DENY (openai)", ok is False and "deprecated" in reason.lower())

    # Test 5: Provider desconocido DENY
    ok, reason = validate_provider_allowed("unknown_provider", "some-model", reg)
    test("5. Provider desconocido DENY", ok is False and "unknown" in reason.lower())

    # Test 6: Fallback automatico DENY
    test("6. Fallback automatico DENY", assert_no_provider_auto_replacement(reg) is True)

    # Test 7: Budget cap validado
    budget = estimate_budget_for_cycle(reg)
    test("7. Budget cap validado (max_usd_per_cycle=0.03)", budget["max_usd_per_cycle"] == 0.03)

    # Test 8: max_calls_per_provider_per_cycle = 1
    test("8. max_calls_per_provider_per_cycle = 1", budget["max_calls_per_provider"] == 1)

    # Test 9: retries = 0
    test("9. retries = 0", budget["retries"] == 0)

    # Test 10: Registry JSON valido
    try:
        with open(os.path.join(os.path.dirname(__file__), "provider_registry.json"), "r") as f:
            data = json.load(f)
        valid_json = "providers" in data and "policies" in data and "budget" in data
    except Exception:
        valid_json = False
    test("10. Registry JSON valido", valid_json)

    # === MIGRATION-SPECIFIC TESTS ===

    # Test 11: Old Anthropic model (claude-sonnet-4-20250514) is now DEPRECATED → DENY
    ok_old, reason_old = validate_provider_allowed("anthropic", "claude-sonnet-4-20250514", reg)
    test("11. OLD model claude-sonnet-4-20250514 DENY (deprecated)",
         ok_old is False and "deprecated" in reason_old.lower())

    # Test 12: New Anthropic model (claude-sonnet-4-6) is ALLOWED
    ok_new, reason_new = validate_provider_allowed("anthropic", "claude-sonnet-4-6", reg)
    test("12. NEW model claude-sonnet-4-6 ALLOWED", ok_new is True and reason_new == "ALLOWED")

    # Test 13: Registry version updated to 1.1.0
    test("13. Registry version 1.1.0", reg["version"] == "1.1.0")

    # Test 14: Migration log exists with T1 decision recorded
    migration_log = reg.get("migration_log", [])
    has_migration = any(
        entry.get("t1_decision") == "APPROVE" and "claude-sonnet-4-6" in entry.get("change", "")
        for entry in migration_log
    )
    test("14. T1 decision recorded in migration_log", has_migration)

    print("=" * 60)
    print(f"Results: {PASS} PASS, {FAIL} FAIL, {PASS + FAIL} total")
    print("=" * 60)

    return FAIL == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
