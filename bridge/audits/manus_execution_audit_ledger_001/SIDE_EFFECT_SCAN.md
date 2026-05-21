# SIDE EFFECT SCAN — 21 commits

## §1 Side-effects verificables desde git

| Categoría | Hallazgo |
|-----------|----------|
| Escrituras a `main` | NINGUNA (0/21) |
| Escrituras a DB/Supabase | NINGUNA (0 `.sql`) |
| Escrituras a código productivo | NINGUNA (0 `kernel/` `apps/`) |
| Archivos de output generados | SÍ — `bridge/embryos/oracle_ai_r0/outputs/*.json` (≥12 archivos `detect_new_ai_capability_candidates_*` + `map_capability_to_application_*` con timestamps 20260521) |
| event_log.jsonl | 7 commits (b3e1c36→a913412) contienen event logs de ejecución autónoma |

## §2 Side-effect MAGNO no verificable desde git

**Ejecuciones autónomas de embriones produjeron outputs con timestamps reales (20260521T03-05).** Esto implica que los loops Oracle/Auditor **corrieron de verdad** y generaron archivos. Lo que NO es verificable desde git:

1. **¿Llamaron a APIs de proveedores reales?** `bd2e56e SPR-ORACLE-AI-M2-001` dice verbatim "Real API capability verification (4/6 REALTIME_VERIFIED)". Esto sugiere **llamadas reales a APIs externas con costo**. NO hay log de costo/tokens adjunto. → UNVERIFIED P1.
2. **¿Cuánto costó?** Ningún commit adjunta log de provider cost. → UNVERIFIED.
3. **¿Las ejecuciones autónomas tuvieron side-effects fuera del repo?** (escrituras externas, webhooks, etc.) No verificable desde git. → NEEDS_REVIEW.

## §3 Kill-switch state

El frente declara kill-switch en `heartbeat-scheduler-r0.yml` + "Heartbeat scheduler 12h with kill-switch" (`d58b179`). El **estado real del kill-switch** (ON/OFF en runtime) NO es verificable desde git — es estado runtime. → NEEDS_REVIEW.
