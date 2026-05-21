# Embrión Oráculo de IAs R0

El primer embrión autónomo real de El Monstruo.

## Identidad

| Campo | Valor |
|-------|-------|
| embryo_id | `oracle_ai_embryo_r0` |
| Tier | R0 (Shadow, non-productive) |
| Status | AUTONOMOUS_R0_SHADOW |
| Entry Point | `oracle_ai_embryo.py --run-once` |

## Qué lo hace autónomo

Este embrión cumple los 10 criterios de autonomía definidos por T1:

1. **Identidad propia** — `oracle_ai_embryo_r0`
2. **Estado propio** — `oracle_ai_state.json`
3. **Cola propia** — `oracle_ai_self_tasks.yaml` (5 tareas)
4. **Loop propio** — `run_once()` en `oracle_ai_embryo.py`
5. **Criterio de acción propio** — Scoring autónomo (priority + freshness + compounding - penalties)
6. **Dispatcher** — Pide permiso antes de cada acción
7. **Event log** — Escribe a `bridge/embryos/oracle_ai_r0/event_log.jsonl`
8. **Output propio** — Genera artefactos en `bridge/embryos/oracle_ai_r0/outputs/`
9. **Kill-switch** — Respeta `scheduler_kill_switch.json`
10. **Invocable sin prompt humano** — Compatible con scheduler/cron

## Invocación

```bash
cd /path/to/el-monstruo-bridge
python3 embryos/oracle_ai/oracle_ai_embryo.py --run-once
```

## Self-Tasks Disponibles

| # | Task ID | Action Class | Compounding |
|---|---------|-------------|-------------|
| 1 | detect_new_ai_capability_candidates | A0_OBSERVE | HIGH |
| 2 | map_capability_to_application | A1_ANALYZE | HIGH |
| 3 | rank_application_by_power_gain | A1_ANALYZE | MEDIUM |
| 4 | generate_sprint_candidate | A3_CREATE_NON_PRODUCTIVE_ARTIFACT | HIGH |
| 5 | audit_previous_oracle_outputs_for_low_value | A2_PREPARE_EVIDENCE | MEDIUM |

## Tests

```bash
python3 embryos/oracle_ai/test_oracle_ai_embryo.py
```

Criterio: 20/20 PASS.
