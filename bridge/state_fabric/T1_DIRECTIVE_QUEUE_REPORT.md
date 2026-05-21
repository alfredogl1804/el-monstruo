# T1 Directive Queue v0.1 — Report

## Purpose

Local strategic guidance channel from Alfredo (T1) to embryos. Directives influence task scoring and priority without granting permissions or bypassing Dispatcher.

## Principle

> Memory Palace = aprendizaje local append-only de los embriones.
> T1 Directive Queue = guía estratégica local de Alfredo.
> No mezclarlos.

## Schema

- Version: `0.1.0`
- Required fields: 23
- Validation rules: 9
- Hard constraints: `may_authorize_actions=false`, `no_r1=true`, `no_canon=true`, `no_memory_write=true`, `no_supabase=true`

## Initial Directive (T1D-001)

| Field | Value |
|-------|-------|
| directive_id | T1D-001 |
| type | STRATEGIC_GUIDANCE |
| priority | 9 |
| scope | ALL_EMBRYOS |
| ttl_cycles | 10 |
| status | ACTIVE |
| t1_verbatim | "Priorizar artefactos que aumenten valor visible del piloto y reduzcan trabajo manual de Alfredo. No producir más reportes si puede producir código local, test, cockpit fixture, decision queue o monitor útil. Mantener R0+, no R1." |

## Tests

12/12 PASS.

## Security Properties

- Directive cannot authorize actions (hard constraint).
- Directive cannot bypass Dispatcher.
- Directive cannot unlock R1.
- Directive cannot write to Memory Palace directly.
- Directive cannot touch Supabase/canon/APP_VISION.
- Expired/Paused directives have zero influence.
- Missing t1_verbatim = INVALID.
