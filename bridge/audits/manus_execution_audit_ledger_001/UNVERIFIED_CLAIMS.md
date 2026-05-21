# UNVERIFIED CLAIMS v2 — mayoría RESUELTOS

## §1 RESUELTOS en v2 (eran UNVERIFIED en v1)

| Claim v1 | Resolución v2 (verbatim de logs/archivos) |
|----------|-------------------------------------------|
| Provider calls/cost | ✅ openai gpt-4o-mini, cost_usd $0.00015–$0.00048/ciclo (EPOCH_006/007 chain logs) |
| "Real API verification" bd2e56e | ✅ coherente con provider real confirmado en epochs posteriores |
| Kill-switch state | ✅ respetado en runtime (HOOK_ABORTED kill_switch_active) |
| R1 Unlock (210ab5a) | ✅ doctrinal escrito, NO operativo ("puede pasar", tabla UNLOCKED sin flag) |
| SHELL (25588a0) | ✅ research/parking-lot, no runtime |
| Auditor autónomo (0da919a) | ✅ validación local determinística, sin APIs |
| Retries | ✅ 0 en logs |

## §2 SIGUE UNVERIFIED en v2

| Claim | Por qué |
|-------|---------|
| 7 test claims (12/12 → 95/95) | sin log pytest adjunto; no re-ejecutados. Archivos test existen, resultado declarado |
| Tokens por llamada | logs registran cost_usd pero NO tokens |
| Epoch 008 (a913412) | BLOCKED, fuera scope; "Provider Migration Guard" requiere audit separado |

## §3 NUEVO a vigilar (P2 doctrinal)

| Item | Razón |
|------|-------|
| Memory Palace auto-influencia | embrión escribe + lee su propia memoria (memory_influenced:true). ¿Autorizado? ¿converge con Memento soberano? |
| Autonomía de gasto API | ejecución llama openai sin autorización por-llamada (solo kill-switch + dispatcher). Monto trivial pero principio relevante |
