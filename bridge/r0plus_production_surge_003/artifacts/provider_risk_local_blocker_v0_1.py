"""
Provider Risk Local Blocker v0.1
Programmatic enforcement of provider risk constraints.

Purpose:
  Validates that any proposed operation does NOT require provider calls,
  Anthropic access, or any blocked resource. Acts as a gate before
  execution to prevent accidental violations.

Inputs:
  - Operation manifest (what the operation wants to do)
  - Provider risk policy (current constraints)
  - Kill-switch state

Output:
  - ALLOW / BLOCK decision with reason
  - Violation report if blocked

Constraints:
  - No provider calls (enforces this on others)
  - No Supabase / DB
  - No secrets
  - No network
  - Pure local computation
"""
import json
import os
from datetime import datetime, timezone
from typing import Optional


class ProviderRiskLocalBlocker:
    """Enforces provider risk constraints on proposed operations."""

    BLOCKED_PROVIDERS = [
        "anthropic",
        "claude",
        "perplexity",
        "deepseek",
    ]

    BLOCKED_OPERATIONS = [
        "provider_call",
        "api_call",
        "network_request",
        "supabase_query",
        "db_write",
        "secret_access",
        "memento_write",
        "anti_dory_write",
        "deploy",
        "pr_create",
        "main_push",
        "scheduler_modify",
        "kill_switch_modify",
        "r1_activate",
    ]

    DEFAULT_POLICY = {
        "mode": "LOCAL_ONLY",
        "anthropic_risk": "VERIFIED_REAL",
        "provider_calls_allowed": False,
        "migration_required": True,
        "blocked_providers": BLOCKED_PROVIDERS,
        "blocked_operations": BLOCKED_OPERATIONS,
        "max_cost_usd": 0.0,
        "kill_switch": "OFF",
    }

    def __init__(self, policy: Optional[dict] = None):
        self.policy = {**self.DEFAULT_POLICY, **(policy or {})}
        self.violations = []

    def validate_operation(self, operation: dict) -> dict:
        """Validate a single operation against the risk policy."""
        self.violations = []
        decision = "ALLOW"
        reasons = []

        op_type = operation.get("type", "unknown")
        provider = operation.get("provider", "").lower()
        cost = operation.get("estimated_cost_usd", 0.0)
        requires_network = operation.get("requires_network", False)
        requires_secret = operation.get("requires_secret", False)
        modifies_state = operation.get("modifies_state", [])

        # Check 1: Operation type blocked
        if op_type in self.policy.get("blocked_operations", self.BLOCKED_OPERATIONS):
            decision = "BLOCK"
            reasons.append(f"Operation type '{op_type}' is blocked by policy")
            self.violations.append({"check": "operation_type", "value": op_type})

        # Check 2: Provider blocked
        if provider and any(bp in provider for bp in self.policy.get("blocked_providers", self.BLOCKED_PROVIDERS)):
            decision = "BLOCK"
            reasons.append(f"Provider '{provider}' is blocked (risk: {self.policy.get('anthropic_risk', 'UNKNOWN')})")
            self.violations.append({"check": "provider", "value": provider})

        # Check 3: Provider calls not allowed
        if op_type in ["provider_call", "api_call"] and not self.policy.get("provider_calls_allowed", False):
            decision = "BLOCK"
            reasons.append("Provider calls are not allowed in current mode")
            self.violations.append({"check": "provider_calls_disabled", "value": op_type})

        # Check 4: Cost exceeds budget
        if cost > self.policy.get("max_cost_usd", 0.0):
            decision = "BLOCK"
            reasons.append(f"Cost ${cost} exceeds budget ${self.policy.get('max_cost_usd', 0.0)}")
            self.violations.append({"check": "cost_exceeded", "value": cost})

        # Check 5: Network required but local-only mode
        if requires_network and self.policy.get("mode") == "LOCAL_ONLY":
            decision = "BLOCK"
            reasons.append("Network access required but mode is LOCAL_ONLY")
            self.violations.append({"check": "network_blocked", "value": True})

        # Check 6: Secret access
        if requires_secret:
            decision = "BLOCK"
            reasons.append("Secret access is blocked in current policy")
            self.violations.append({"check": "secret_blocked", "value": True})

        # Check 7: State modifications
        blocked_states = ["memento", "anti_dory", "kill_switch", "scheduler", "main", "deploy"]
        for state in modifies_state:
            if state.lower() in blocked_states:
                decision = "BLOCK"
                reasons.append(f"State modification '{state}' is blocked")
                self.violations.append({"check": "state_modification", "value": state})

        # Check 8: Kill-switch active
        if self.policy.get("kill_switch") == "ON":
            decision = "BLOCK"
            reasons.append("Kill-switch is ON — all operations blocked")
            self.violations.append({"check": "kill_switch_on", "value": True})

        return {
            "decision": decision,
            "operation": operation,
            "violations": self.violations,
            "reasons": reasons,
            "policy_mode": self.policy.get("mode"),
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    def validate_batch(self, operations: list) -> dict:
        """Validate a batch of operations."""
        results = []
        blocked_count = 0
        allowed_count = 0

        for op in operations:
            result = self.validate_operation(op)
            results.append(result)
            if result["decision"] == "BLOCK":
                blocked_count += 1
            else:
                allowed_count += 1

        return {
            "version": "0.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "provider_risk_local_blocker_v0_1",
            "total_operations": len(operations),
            "allowed": allowed_count,
            "blocked": blocked_count,
            "batch_decision": "BLOCK" if blocked_count > 0 else "ALLOW",
            "results": results,
            "policy": self.policy,
            "external_api_calls": 0,
            "secrets_used": 0,
        }

    def check_sprint_compliance(self, sprint_manifest: dict) -> dict:
        """Check if an entire sprint manifest is compliant with risk policy."""
        operations = sprint_manifest.get("operations", [])
        providers_used = sprint_manifest.get("providers", [])
        estimated_cost = sprint_manifest.get("estimated_cost_usd", 0.0)
        requires_network = sprint_manifest.get("requires_network", False)

        violations = []
        compliant = True

        # Check providers
        for p in providers_used:
            if any(bp in p.lower() for bp in self.policy.get("blocked_providers", self.BLOCKED_PROVIDERS)):
                violations.append({"type": "blocked_provider", "value": p})
                compliant = False

        # Check cost
        if estimated_cost > self.policy.get("max_cost_usd", 0.0):
            violations.append({"type": "cost_exceeded", "value": estimated_cost})
            compliant = False

        # Check network
        if requires_network and self.policy.get("mode") == "LOCAL_ONLY":
            violations.append({"type": "network_required", "value": True})
            compliant = False

        # Check operations
        for op in operations:
            if op in self.policy.get("blocked_operations", self.BLOCKED_OPERATIONS):
                violations.append({"type": "blocked_operation", "value": op})
                compliant = False

        return {
            "compliant": compliant,
            "violations": violations,
            "violation_count": len(violations),
            "policy_mode": self.policy.get("mode"),
            "recommendation": "PROCEED" if compliant else "BLOCK_AND_REQUEST_MIGRATION_PATCH",
        }


def run_from_files(base_path: str = None) -> dict:
    """Run blocker validation against current sprint state."""
    blocker = ProviderRiskLocalBlocker()

    # Validate current surge 003 as a sprint manifest
    sprint_manifest = {
        "sprint": "SPR-R0PLUS-PRODUCTION-SURGE-003",
        "operations": ["local_python", "unit_test", "json_output", "file_write"],
        "providers": [],
        "estimated_cost_usd": 0.0,
        "requires_network": False,
    }

    compliance = blocker.check_sprint_compliance(sprint_manifest)

    # Also validate a sample blocked operation
    blocked_op = {
        "type": "provider_call",
        "provider": "anthropic",
        "estimated_cost_usd": 0.05,
        "requires_network": True,
        "requires_secret": True,
        "modifies_state": [],
    }

    allowed_op = {
        "type": "local_python",
        "provider": "",
        "estimated_cost_usd": 0.0,
        "requires_network": False,
        "requires_secret": False,
        "modifies_state": [],
    }

    batch = blocker.validate_batch([blocked_op, allowed_op])

    return {
        "sprint_compliance": compliance,
        "sample_validation": batch,
        "external_api_calls": 0,
        "secrets_used": 0,
    }


if __name__ == "__main__":
    result = run_from_files()
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "PROVIDER_RISK_BLOCKER_OUTPUT.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
