# EVENT LOG DEEP SCAN — contenido real de los logs (v2, lo que el v1 no leyó)

Lectura verbatim de los .jsonl de ejecución. Cero hits de dummy/sim/shadow/mock/retry (grep across 6 commits = 0). Logs viven en `bridge/embryos/...`. `output_path` apunta a `/home/ubuntu/el-monstruo-bridge/bridge/embryos/` (filesystem sandbox del ejecutor, dentro de bridge/).

## Por commit

| commit | event_log | hallazgo binario |
|--------|-----------|------------------|
| b3e1c36 | `oracle_ai_r0/event_log.jsonl` 1 línea | **DUMMY**: solo `{"event_type":"TEST_EVENT","payload":{"test":true}}`. Sin API, costo, escritura, retry |
| 7fb3303 | event_log 3l + `FIRST_PAIR_MISSION_LOG.jsonl` 8l | Primera ejecución REAL del par: `EMBRYO_TASK_COMPLETED ... cost_usd:0.000195` + `AUDITOR_TASK_COMPLETED cost_usd:0.000151`. Provider NO nombrado. Escribe JSON a filesystem bridge/. Kill-switch: 2 `HOOK_ABORTED kill_switch_active` |
| 4e5c90c | event_log 9l + auditor_event_log | 1 ciclo real `cost_usd:0.0002947` + **4** `HOOK_ABORTED kill_switch_active`. Provider NO nombrado |
| d61ac0c | event_log 21l + `EPOCH_005_CHAIN_LOG.jsonl` 4l | 3 ciclos (cost 0.000287/0.000295/0.000479), 6 HOOK_ABORTED. Chain: `ORACLE_RUN_ONCE action_class:A0_OBSERVE dispatcher:ALLOW grounding_level:6 claims_count:5` + `AUDITOR grounding_verdict:PASS`. Provider NO nombrado aún |
| **b54619a** | event_log 27l + `EPOCH_006_CHAIN_LOG.jsonl` 3l | **PRIMER PROVIDER REAL**: `"provider":"openai","model":"gpt-4o-mini","cost_usd":0.000285 ... memory_appended:true,memory_id:MEM-OAI-...`. Auditor igual openai. `MEMORY_PALACE_STATE total_entries:2`. 8 HOOK_ABORTED |
| **ea7080d** | event_log 33l + auditor 31l + `EPOCH_007_CHAIN_LOG.jsonl` 4l | openai gpt-4o-mini cost 0.000292; `directive_active:T1D-001`; **`memory_influenced:true`** (memoria retroalimenta) + `directive_influenced:true`; `GROUNDING_ENFORCEMENT score:10 verdict:PASS`. **10** HOOK_ABORTED |

## 5 preguntas binarias (solo lo literal en los logs)

1. **APIs externas:** SÍ — `openai gpt-4o-mini` nombrado literal solo en EPOCH_006/007 chain logs. Pre-006 registran `cost_usd` sin nombrar provider. **Costo siempre registrado** (rango $0.00015–$0.00048/ciclo). **Tokens NUNCA registrados.**
2. **Escritura externa:** filesystem dentro de `bridge/` + **Memory Palace** (`memory_appended:true`+`memory_id`, epochs 006/007). **NO webhook, NO DB/Supabase, NO HTTP saliente fuera, NO escritura fuera de bridge/.**
3. **Retry:** NO. Cero.
4. **Kill-switch:** SÍ consultado y respetado (`HOOK_ABORTED/AUDITOR_ABORTED reason:kill_switch_active`, 4→10 acumuladas). `dispatcher` además filtra por action_class.
5. **Real vs sim:** REAL. Único dummy = `TEST_EVENT` inicial (b3e1c36). Desde epoch 006: provider real + costo real + memoria real con feedback.
