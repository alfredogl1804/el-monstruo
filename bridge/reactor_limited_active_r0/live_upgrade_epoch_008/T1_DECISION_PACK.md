# T1 DECISION PACK — Epoch 008

**Generated:** 2026-05-21T05:45:00Z
**Sprint:** SPR-EPOCH008-PROVIDER-MIGRATION-DIRECTIVE-CONFLICT-R0PLUS-001
**Status:** AWAITING T1 INPUT

---

## Pending Decisions (Action Required)

### 1. Anthropic Model Migration

**Context:** Provider Migration Guard detected that `claude-sonnet-4-20250514` has a reported EOL date of 2026-06-15 (25 days remaining). The guard has marked this as a MIGRATION_CANDIDATE requiring explicit T1 decision.

**Current state:**
- Model is still ALLOWED and functional
- Auto-replacement is BLOCKED (by policy)
- No autonomous action will be taken without T1 decision

**Options (execute via T1 Decision Executor):**

```json
// Option A: Acknowledge and monitor
{
  "decision_type": "ACKNOWLEDGE_RISK",
  "target": "anthropic",
  "reason": "Will monitor. Decide at 14 days remaining."
}

// Option B: Approve migration now
{
  "decision_type": "APPROVE_MODEL_MIGRATION",
  "target": "anthropic",
  "reason": "Proactive migration before EOL",
  "params": {"provider": "anthropic", "new_model": "claude-sonnet-4-20250601"}
}

// Option C: Block provider until verified
{
  "decision_type": "BLOCK_PROVIDER",
  "target": "anthropic",
  "reason": "Block until new model is verified"
}

// Option D: Reject migration (keep current)
{
  "decision_type": "REJECT_MIGRATION",
  "target": "anthropic",
  "reason": "EOL date unverified. Keep current model."
}
```

**Recommendation:** Option A (ACKNOWLEDGE_RISK) for now. Verify EOL date externally. Decide at 14 days remaining.

---

### 2. Directive Conflict Policy

**Context:** T1D-001 (novelty/artifacts, priority 9) and T1D-002 (robustness/risk, priority 10) are in conflict. The Conflict Resolver correctly identifies opposing intents and resolves by priority (T1D-002 wins).

**Current state:**
- Both directives remain ACTIVE in queue
- T1D-001 is suppressed only during conflict resolution
- Priority-based resolution is working as designed

**Options:**

```json
// Option A: Accept current (no action needed)
// T1D-002 dominates. System is working correctly.

// Option B: Expire T1D-001
{
  "decision_type": "EXPIRE_DIRECTIVE",
  "target": "T1D-001",
  "reason": "Superseded by T1D-002"
}

// Option C: Create unified directive
{
  "decision_type": "CREATE_DIRECTIVE",
  "target": "new",
  "reason": "Merge novelty and robustness into single directive",
  "params": {
    "directive_type": "STRATEGIC_GUIDANCE",
    "priority": 10,
    "focus": "Produce robust artifacts that increase pilot value. Prioritize risk reduction when in conflict with novelty.",
    "desired_outcome": "Code, tests, guards, monitors — stability-first but value-producing"
  }
}
```

**Recommendation:** Option A (no action). The priority system is working correctly. Both directives provide useful signal.

---

## Pilot Health Summary

| Dimension | Score | Status |
|---|---|---|
| Tests passing | 120+ | GREEN |
| Cost efficiency | $0.000636/epoch | GREEN |
| Grounding (Oracle) | 6/10 | YELLOW |
| Grounding (Auditor) | 10/10 | GREEN |
| Memory Palace | 6 entries | GROWING |
| Provider diversity | 4 ALLOWED | GREEN |
| Provider risk | 1 HIGH (Anthropic) | YELLOW |
| Directive conflicts | 1 (resolved) | GREEN |
| Auto-replacement | BLOCKED | GREEN |

**Overall:** HEALTHY (80/100)

---

## Artifacts Delivered This Epoch

| # | Artifact | Type | Tests |
|---|---|---|---|
| 1 | Provider Migration Guard v0.1 | Safety guard | 12/12 |
| 2 | Multi-Directive Conflict Resolver v0.1 | Policy engine | 10/10 |
| 3 | Oracle/Auditor v0.5 | Embryo upgrade | 40/40 |
| 4 | T1 Decision Executor v0.1 | Action tool | 14/14 |

---

## Next Epoch Recommendations

1. **Verify Anthropic EOL externally** (search for official announcement)
2. **Oracle grounding improvement** — add provider-risk-oriented task to self-task queue
3. **Memory Palace growth** — target 10+ entries for meaningful pattern detection
4. **Consider T1D-003** — unified directive that eliminates conflict
5. **Cockpit integration** — connect Decision Executor to Cockpit Data Injector
