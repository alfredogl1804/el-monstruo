"""
Test Suite: Provider Risk Local Blocker v0.1
Sprint: SPR-R0PLUS-PRODUCTION-SURGE-003
13 tests.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from provider_risk_local_blocker_v0_1 import ProviderRiskLocalBlocker

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS [{passed:02d}] {name}")
    else:
        failed += 1
        print(f"  FAIL [{passed + failed:02d}] {name}")


print("=" * 60)
print("TEST SUITE: Provider Risk Local Blocker v0.1 — 13 Tests")
print("=" * 60)

# Setup
blocker = ProviderRiskLocalBlocker()

# 1. Local operation is ALLOWED
local_op = {"type": "local_python", "provider": "", "estimated_cost_usd": 0.0, "requires_network": False, "requires_secret": False, "modifies_state": []}
result = blocker.validate_operation(local_op)
test("01. local operation is ALLOWED", result["decision"] == "ALLOW")

# 2. Anthropic provider is BLOCKED
anthropic_op = {"type": "provider_call", "provider": "anthropic", "estimated_cost_usd": 0.05, "requires_network": True, "requires_secret": True, "modifies_state": []}
result = blocker.validate_operation(anthropic_op)
test("02. anthropic provider is BLOCKED", result["decision"] == "BLOCK")

# 3. Perplexity provider is BLOCKED
perp_op = {"type": "api_call", "provider": "perplexity", "estimated_cost_usd": 0.01, "requires_network": True, "requires_secret": False, "modifies_state": []}
result = blocker.validate_operation(perp_op)
test("03. perplexity provider is BLOCKED", result["decision"] == "BLOCK")

# 4. Network operation in LOCAL_ONLY is BLOCKED
net_op = {"type": "http_request", "provider": "", "estimated_cost_usd": 0.0, "requires_network": True, "requires_secret": False, "modifies_state": []}
result = blocker.validate_operation(net_op)
test("04. network operation in LOCAL_ONLY is BLOCKED", result["decision"] == "BLOCK")

# 5. Cost exceeding budget is BLOCKED
cost_op = {"type": "local_python", "provider": "", "estimated_cost_usd": 0.01, "requires_network": False, "requires_secret": False, "modifies_state": []}
result = blocker.validate_operation(cost_op)
test("05. cost exceeding budget is BLOCKED", result["decision"] == "BLOCK")

# 6. Secret access is BLOCKED
secret_op = {"type": "local_python", "provider": "", "estimated_cost_usd": 0.0, "requires_network": False, "requires_secret": True, "modifies_state": []}
result = blocker.validate_operation(secret_op)
test("06. secret access is BLOCKED", result["decision"] == "BLOCK")

# 7. State modification (memento) is BLOCKED
state_op = {"type": "local_python", "provider": "", "estimated_cost_usd": 0.0, "requires_network": False, "requires_secret": False, "modifies_state": ["memento"]}
result = blocker.validate_operation(state_op)
test("07. memento state modification is BLOCKED", result["decision"] == "BLOCK")

# 8. Kill-switch ON blocks everything
ks_blocker = ProviderRiskLocalBlocker({"kill_switch": "ON"})
result = ks_blocker.validate_operation(local_op)
test("08. kill-switch ON blocks everything", result["decision"] == "BLOCK")

# 9. Batch validation returns correct counts
batch = blocker.validate_batch([local_op, anthropic_op])
test("09. batch validation counts correct", batch["allowed"] == 1 and batch["blocked"] == 1)

# 10. Batch decision is BLOCK if any blocked
test("10. batch decision BLOCK if any blocked", batch["batch_decision"] == "BLOCK")

# 11. Sprint compliance check passes for local-only sprint
sprint = {"operations": ["local_python", "unit_test"], "providers": [], "estimated_cost_usd": 0.0, "requires_network": False}
compliance = blocker.check_sprint_compliance(sprint)
test("11. local-only sprint is compliant", compliance["compliant"] is True)

# 12. Sprint with anthropic fails compliance
bad_sprint = {"operations": ["provider_call"], "providers": ["anthropic"], "estimated_cost_usd": 0.05, "requires_network": True}
compliance2 = blocker.check_sprint_compliance(bad_sprint)
test("12. anthropic sprint fails compliance", compliance2["compliant"] is False)

# 13. No external API calls in output
test("13. no external API calls", batch["external_api_calls"] == 0)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
