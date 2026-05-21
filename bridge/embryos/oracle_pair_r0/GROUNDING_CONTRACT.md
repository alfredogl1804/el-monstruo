# Bicéfalo Pair Grounding Contract

## Objective
Enhance the R0 Autonomous Oracle Pair by enforcing strict factual grounding. The Oracle must self-assess the evidence status of its claims, and the Auditor must enforce these standards, blocking or flagging unverified factual claims.

## Claim Types and Evidence Status

When the Oracle produces an output containing claims, each claim must be classified and assigned an evidence status.

### Allowed Evidence Statuses:
1. `VERIFIED_LOCAL`: Verified against the Monstruo's local context or codebase.
2. `VERIFIED_PROVIDER`: Verified via a direct API call or provider documentation accessed during the cycle.
3. `NEEDS_REAL_TIME_CHECK`: A factual claim (date, capability, price) that the Oracle believes is true but cannot verify in R0.
4. `NO_SOURCE`: A claim made without any supporting source or evidence.
5. `HYPOTHESIS`: A logical deduction or proposed idea, not presented as a hard fact.
6. `CANDIDATE_ONLY`: A raw idea intended for further research, not for immediate execution.

## Grounding Rules

### Rule 1: The "Current Fact" Mandate
If the Oracle mentions **dates, models, current capabilities, availability, prices, endpoints, or current tools**, it MUST mark the claim as `NEEDS_REAL_TIME_CHECK` unless it possesses verifiable evidence (`VERIFIED_LOCAL` or `VERIFIED_PROVIDER`).

### Rule 2: The "No-Source Fact" Prohibition
It is strictly PROHIBITED to present a claim marked as `NO_SOURCE` or `HYPOTHESIS` as a current, verified fact.

### Rule 3: Auditor Enforcement
The Auditor must:
1. Parse the Oracle's output and extract all claims.
2. Detect any factual claims lacking a source.
3. Detect any current dates/capabilities not marked for verification.
4. **Penalize:** Lower the overall score if factual grounding is < 7/10.
5. **BLOCK:** Emit a `BLOCK` verdict if a critical factual claim lacks a source and is presented as fact.
6. **PARTIAL:** Emit a `PARTIAL` verdict if the output is useful but contains `NEEDS_REAL_TIME_CHECK` claims that must be verified by T1 before action.
7. **PASS:** Emit a `PASS` verdict ONLY if grounding is >= 8/10 and there are no P0 (critical) unverified factual claims.
