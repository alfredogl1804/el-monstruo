# Scheduler Report — SPR-REACTOR-SCHEDULER-R0-001

**Generated:** 2026-05-21T01:12:35.668296+00:00
**Status:** ACTIVE

## Current State

| Metric | Value |
|--------|-------|
| Total cycles | 1 |
| Successful | 1 |
| Failed | 0 |
| Consecutive failures | 0 |
| Last run | 2026-05-21T01:12:35.668017+00:00 |
| Last result | SUCCESS |
| Last decision | REQUEST_T1 |

## Last Run Details

| Field | Value |
|-------|-------|
| Timestamp | 2026-05-21T01:12:35.667998+00:00 |
| Exit code | 0 |
| Duration | 0.03s |
| Decision | REQUEST_T1 |
| Outcome | SUCCESS |

## Configuration

| Setting | Value |
|---------|-------|
| Frequency | Every 12h |
| Mode | audit-only / report-only |
| Budget per cycle | $0 (R0 local) |
| Max consecutive failures | 2 |
| Kill-switch | INACTIVE |

## Anti-Loop Protection

- Window: 12h
- Max 1 execution per window
- If 2 consecutive failures → PAUSED (requires T1)

## Kill-Switch

To stop the scheduler immediately, create or edit:
`scheduler/scheduler_kill_switch.json` with `{"active": true}`

To resume: set `{"active": false}` and reset `scheduler_state.json` status to "ACTIVE".
