# SPRINT DRAFT: SPR-ORACLE-006

**Title:** Provider Latency Optimization
**Status:** DRAFT (Unsigned, Not Executable)
**Source:** Oracle v0.4 (Value Score: 78, Risk Score: 40)

## Objective
Reduce cycle time by running provider calls concurrently using asyncio/aiohttp.

## Scope
Refactor the cycle runner to execute API calls to the 4 verified providers in parallel instead of sequentially.

## Allowed Files
- `bridge/reactor_limited_active_r0/run_cycle.py` (modification)
- `bridge/reactor_limited_active_r0/test_async_providers.py`

## Forbidden Files
- `main` branch files
- `APP_VISION.md`
- Any file outside `bridge/`

## Expected Artifacts
1. Updated `run_cycle.py` using `asyncio`.
2. Tests verifying concurrent execution.

## Tests
- `test_concurrent_providers`
- `test_timeout_handling`

## Gates
- Code review by Auditor loop.
- All tests must pass before integration.

## Rollback
- Revert `run_cycle.py` to synchronous version.

## T1 Decision Needed
- Approve the refactor to asyncio.

## No-Go List
- DO NOT exceed provider rate limits.
- DO NOT ignore errors from individual providers (must handle exceptions gracefully).

## Estimated Cost
$0.00 USD (Refactor only)

## Definition of Done
- Cycle runner refactored to use asyncio.
- Cycle execution time reduced by at least 40%.
