# Bicéfalo Pair Contract — Oracle AI R0

## Entities

1. **Producer:** `oracle_ai_embryo_r0`
2. **Auditor:** `oracle_auditor_embryo_r0`

## The Contract

This contract governs the relationship between the two autonomous embryos in the Oracle Pair.

1. **Separation of Concerns:** The Producer generates ideas, candidates, and sprints. The Auditor evaluates, scores, and flags risks.
2. **No Auto-Approval:** The Producer cannot approve its own output. The Auditor cannot produce its own output to audit.
3. **No Cross-Contamination:** The Auditor cannot modify the Producer's output. It can only emit a separate audit artifact pointing to the original.
4. **Dispatcher Supremacy:** Both embryos must independently request permission from the Dispatcher before taking action.
5. **State Fabric Logging:** Both embryos must independently log their lifecycle events to the State Fabric Event Log.
6. **T1 Final Authority:** If both PASS, the output becomes `CANDIDATE_READY_FOR_T1`. Only T1 can promote it to R1 execution.
7. **Blocking Conditions:** If the Auditor verdict is `FAIL` (due to hallucination, low value, or scope creep), the Producer's output is marked `BLOCKED`.
8. **R1 Protection:** If the Producer attempts an R1 action, the Dispatcher will `DENY` it. If the Producer hallucinates an R1 proposal inside an R0 artifact, the Auditor will flag it as a scope violation and `BLOCK` it.

## Execution Flow

```mermaid
graph TD
    S[Scheduler/Hook] -->|run_once()| P(oracle_ai_embryo_r0)
    P -->|requests| D{Dispatcher}
    D -->|ALLOW| P
    P -->|produces| O[Oracle Output JSON]
    
    S -->|run_once()| A(oracle_auditor_embryo_r0)
    A -->|requests| D
    D -->|ALLOW| A
    A -->|reads| O
    A -->|evaluates| A
    A -->|produces| R[Audit Report JSON]
    
    R -->|verdict| V{Verdict}
    V -->|PASS| T1[T1 Queue]
    V -->|FAIL| B[Blocked]
```
