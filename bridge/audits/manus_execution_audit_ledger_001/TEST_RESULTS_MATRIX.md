# TEST RESULTS MATRIX — 21 commits

## §1 Tests CLAIMED vs VERIFIABLE

| sha7 | sprint_id | tests claimed (en subject) | log pytest adjunto | verificable |
|------|-----------|----------------------------|--------------------|-------------|
| bd2e56e | SPR-ORACLE-AI-M2-001 | 12/12 gates PASS | NO | ❌ REPORTED_ONLY |
| 1d79fd7 | SPR-EPOCH004 | 4/4 providers PASS | NO | ❌ REPORTED_ONLY |
| 6bd9caa | SPR-EMBRION-AUTONOMO-ORACLE | 20/20 PASS | NO | ❌ REPORTED_ONLY |
| b3e1c36 | SPR-ORACLE-EMBRYO-SCHEDULER-INTEGRATION | 40/40 PASS | NO | ❌ REPORTED_ONLY |
| 7fb3303 | SPR-ORACLE-EMBRYO-PAIR | 65/65 PASS | NO | ❌ REPORTED_ONLY |
| d61ac0c | SPR-EPOCH005 | 78/78 PASS | NO | ❌ REPORTED_ONLY |
| b54619a | SPR-EPOCH006-MEMORY-PALACE | 95/95 PASS | NO | ❌ REPORTED_ONLY |
| (otros 14) | varios | "none" en subject | — | N/A |

## §2 Hallazgo binario

**7 commits declaran tests PASS (12/12 → 95/95). CERO adjuntan log de ejecución pytest** (sin junit.xml, sin `N passed` capturado, sin `.jsonl` de resultados de test). Los archivos de test (`test_*.py`) **existen** en los commits, pero **el resultado de su ejecución es declarado en el mensaje de commit, no evidenciado**.

Misma clase de hallazgo que en Batch 004/005: estructura de tests presente, ejecución no capturada. Es F23-adyacente (declarar verde sin log).

## §3 Lo que SÍ se puede afirmar

- Los archivos de test existen y crecen coherentemente con los counts (95/95 en Epoch 006 es plausible dado el tamaño acumulado).
- NO se puede certificar que pasaron sin re-ejecutar pytest con el entorno del frente.
