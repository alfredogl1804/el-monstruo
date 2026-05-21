# SPRINT DRAFT: SPR-ORACLE-005

**Title:** Automated Code Reviewer Loop
**Status:** DRAFT (Unsigned, Not Executable)
**Source:** Oracle v0.4 (Value Score: 85, Risk Score: 10)

## Objective
Audit generated code before execution to ensure hard rules compliance, preventing accidental R1 or secret exposure during live cycles.

## Scope
Add a pre-execution AST parsing step in the dispatcher to analyze generated Python code for forbidden patterns (e.g., `os.system`, `subprocess`, external network calls).

## Allowed Files
- `bridge/policy_engine/ast_auditor.py`
- `bridge/policy_engine/test_ast_auditor.py`
- `bridge/policy_engine/dispatcher.py` (modification)

## Forbidden Files
- `main` branch files
- `APP_VISION.md`
- Any file outside `bridge/`

## Expected Artifacts
1. `ast_auditor.py` module.
2. Unit tests for AST auditor.
3. Updated `dispatcher.py` that calls the auditor.

## Tests
- `test_ast_auditor_blocks_os_system`
- `test_ast_auditor_allows_json`
- `test_ast_auditor_blocks_requests`

## Gates
- Code review by Auditor loop.
- All tests must pass before integration.

## Rollback
- Revert `dispatcher.py` to previous version.
- Delete `ast_auditor.py`.

## T1 Decision Needed
- Approve the AST parsing rules.

## No-Go List
- DO NOT execute untrusted code to test it.
- DO NOT use regex for code analysis (must use AST).

## Estimated Cost
$0.00 USD (Local execution)

## Definition of Done
- AST auditor created and tested.
- Dispatcher successfully blocks a mock malicious payload.
