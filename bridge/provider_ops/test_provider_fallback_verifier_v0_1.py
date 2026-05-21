"""
Tests for Provider Fallback Verifier v0.1
Minimum 12 tests required.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import provider_fallback_verifier_v0_1 as verifier

passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS [{passed + failed:02d}] {name}")
    else:
        failed += 1
        print(f"  FAIL [{passed + failed:02d}] {name}")

print("=" * 60)
print("Provider Fallback Verifier v0.1 Tests")
print("=" * 60)

# Test 01: Loads provider registry
result = verifier.run_verifier()
test("loads provider registry", result["registry_loaded"] is True)

# Test 02: Detects Anthropic as risk candidate if EOL reported
anthropic_risks = [r for r in result["risk_candidates"] if r["provider"] == "anthropic"]
test("detects Anthropic as risk candidate", len(anthropic_risks) > 0 and any("EOL_REPORTED" in f for f in anthropic_risks[0]["risk_flags"]))

# Test 03: Does NOT replace model automatically
test("no auto replacement", result["decision_pack"]["auto_replacement_attempted"] is False)

# Test 04: Requires T1 for model change
test("requires T1 for change", verifier.requires_t1_for_change() is True and result["decision_pack"]["requires_t1"] is True)

# Test 05: Blocks Perplexity
test("blocks Perplexity", verifier.is_provider_blocked("perplexity") is True)

# Test 06: Blocks DeepSeek
test("blocks DeepSeek", verifier.is_provider_blocked("deepseek") is True)

# Test 07: Blocks unknown provider
base_dir = Path(__file__).parents[2]
registry = verifier.load_provider_registry(base_dir)
test("blocks unknown provider", verifier.is_unknown_provider("unknown_provider_xyz", registry) is True)

# Test 08: Produces fallback candidates
test("produces fallback candidates", len(result["fallback_candidates"]) > 0 and all(c["requires_t1_approval"] for c in result["fallback_candidates"]))

# Test 09: Produces snapshot JSON valid
try:
    json_str = json.dumps(result, default=str)
    parsed = json.loads(json_str)
    test("produces valid JSON snapshot", parsed["artifact"] == "provider_fallback_verifier_v0_1")
except (json.JSONDecodeError, TypeError):
    test("produces valid JSON snapshot", False)

# Test 10: Does not read secrets
test("no secrets read", result["secrets_used"] == 0)

# Test 11: Does not call providers
test("no provider calls", result["provider_calls"] == 0 and result["external_api_calls"] == 0)

# Test 12: Does not touch scheduler/kill-switch
test("no scheduler/kill-switch touch", result["decision_pack"]["scheduler_modified"] is False and result["decision_pack"]["kill_switch_modified"] is False)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

if failed > 0:
    sys.exit(1)
