---
id: DSC-LF-014
proyecto: LA-FORJA
tipo: sprint_closure
titulo: "D5.1 SIGNOFF — 9 migraciones forja_* con RLS desde nacimiento (DSC-S-006 v1.1). Tablas: profiles, threads, messages, sprints, actions, telemetry, simulations, validations, budget. Firmado Cowork T2-A 2026-05-17 (renumerado desde LF-010 por DSC-DRIFT-CLEANUP-2026-05-18)."
estado: firmado
fecha_decision: 2026-05-17 (audit + signoff original como LF-010)
fecha_renumeracion: 2026-05-18 (Sprint DSC-DRIFT-CLEANUP, Opción E refinement Cowork T2-A)
autoridad_firma: Cowork T2-A bajo autoridad delegada T1
sprint_cerrado: LA-FORJA-001 D5.1 (9 migraciones SQL forja_* con RLS desde nacimiento)
migraciones_aplicadas: ["0041_la_forja_sprints", "0042_la_forja_actions", "0043_la_forja_telemetry", "0044_la_forja_simulations", "0045_la_forja_validations", "0046_la_forja_budget", "profiles", "threads", "messages"]
cruza_con: [DSC-S-006, DSC-S-012, DSC-G-008, DSC-LF-003]
---

# D5.1 SIGNOFF — 9 Migraciones forja_* RLS-from-birth (DSC-LF-014)

## Decisión canónica

> **D5.1 LA-FORJA-001 cerrado VERDE FINAL** — 9 tablas `forja_*` aplicadas a producción con `ENABLE ROW LEVEL SECURITY` + ≥1 policy explícita desde nacimiento (DSC-S-006 v1.1 cumplido). Schema completo del tutor La Forja: profiles + threads + messages + sprints + actions + telemetry + simulations + validations + budget. Tipos canónicos UUID + timestamptz NOT NULL + JSONB para `metadata`/`mode_breakdown`/`data_extra`. CHECK constraints binarios para invariantes de negocio (budget cap, period_start day=1, status enums). Firmado Cowork T2-A 2026-05-17 post-audit DSC-G-008 v4.

## Contexto de renumeración

Firmado originalmente como **DSC-LF-010** el 2026-05-17 en `_INDEX.md` durante MAGNA-CIERRE-002 / DRIFT-013. Archivo físico nunca creado (F2 estructural Cowork T2-A reconocido verbatim).

Detectado por Manus E2 2026-05-18 + resuelto via Sprint DSC-DRIFT-CLEANUP-2026-05-18 (Opción E refinement T2-A autorización T1 "la firmo"). Renumerado retroactivamente a LF-014.

## Tablas + RLS policies (snapshot 2026-05-17)

| Tabla | Migration | RLS | Policies |
|---|---|---|---|
| `forja_profiles` | inicial | ✅ | profile_owner_only |
| `forja_threads` | inicial | ✅ | thread_owner_only |
| `forja_messages` | inicial | ✅ | message_via_thread_owner |
| `forja_sprints` | 0041 | ✅ | sprint_owner_only |
| `forja_actions` | 0042 | ✅ | action_via_sprint_owner |
| `forja_telemetry` | 0043 | ✅ | telemetry_owner_only |
| `forja_simulations` | 0044 | ✅ | simulation_owner_only |
| `forja_validations` | 0045 | ✅ | validation_owner_only |
| `forja_budget` | 0046 | ✅ | budget_owner_only |

## Cumplimiento DSC-G-008 v4 (audit original 2026-05-17)

| Punto | Status |
|---|---|
| G1 diff 9 migraciones SQL | ✅ |
| G2 feature flags | ✅ N/A |
| G3 cero secrets | ✅ |
| G4 tests integración | ✅ |
| G5 scope D5.1 puro | ✅ |
| G6 no-duplicate de main | ✅ |
| RLS desde nacimiento (DSC-S-006 v1.1) | ✅ 9/9 |
| CHECK constraints invariantes | ✅ |
| `period_start = day 1 UTC` para budget | ✅ |
| Idempotencia + atomicidad migraciones | ✅ |

## Decisiones sub-magnas derivadas (cruzan con sprints posteriores)

1. **`forja_budget` source-of-truth canonical** — `spent_usd` por `(profile_id, period_start)` con `UNIQUE(profile_id, period_start)`. Cruzar con DSC-LF-003 (cap $50 USD/mes/usuario).
2. **`mode_breakdown` JSONB** — `{"heavy": int, "light": int, "power": int, "normal": int}` default `'{"heavy": 0, "light": 0, "power": 0, "normal": 0}'::jsonb`. Tracking granular por modo.
3. **`cap_usd` DEFAULT 50.00** — cubre INSERT minimal D5.3 RPC sin violación CHECK constraint `chk_forja_budget_metrics`.

## Cláusula de revisión

Este signoff se revisa cuando:
- Schema migration breaking (drop column / type change)
- RLS policy change que cambie contrato seguridad
- CHECK constraint que cambie invariante de negocio
- DSC-S-006 v1.2+ con requisitos RLS adicionales

## Cierre binario

D5.1 LA-FORJA-001 ESTABLECIDO. 9 tablas `forja_*` con RLS-from-birth son la frontera canónica del data plane La Forja. Sprints posteriores (D5.2 stubs replaced DSC-LF-011, D5.3 RPC atómico migration 0050 PR #153) operan sobre este sustrato.
