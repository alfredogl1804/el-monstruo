# TEST RESULTS MATRIX v2 — 9 commits con test claims

| sha7 | sprint_id | tests claimed | log pytest adjunto | verificable |
|------|-----------|---------------|--------------------|-------------|
| bd2e56e | SPR-ORACLE-AI-M2-001 | 12/12 gates | NO | ❌ REPORTED_ONLY |
| 1d79fd7 | SPR-EPOCH004 | 4/4 providers | NO | ❌ REPORTED_ONLY |
| 6bd9caa | SPR-EMBRION-AUTONOMO-ORACLE | 20/20 | NO | ❌ REPORTED_ONLY |
| b3e1c36 | SPR-ORACLE-EMBRYO-SCHEDULER-INT | 40/40 | NO | ❌ REPORTED_ONLY |
| 7fb3303 | SPR-ORACLE-EMBRYO-PAIR | 65/65 | NO | ❌ REPORTED_ONLY |
| d61ac0c | SPR-EPOCH005 | 78/78 | NO | ❌ REPORTED_ONLY |
| b54619a | SPR-EPOCH006-MEMORY-PALACE | 95/95 | NO | ❌ REPORTED_ONLY |
| 0da919a | SPR-LOOP-AUDITOR-001 [+v2] | 8/8 E2E | parcial (script E2E con prints PASS/FAIL, sin junit) | ⚠️ PARTIAL |
| 8de6aef | SPR-VIGILIA-SINCRONICA-001 [+v2] | "PASS 4 loops" | NO | ❌ REPORTED_ONLY |

## Hallazgo
9 commits declaran tests PASS. **Ninguno adjunta junit.xml ni log de `N passed` capturado.** 0da919a tiene un script E2E (`simulate_auditor_e2e.py`) con prints PASS/FAIL — más que los otros, pero aún no es output de ejecución persistido. Clase F23: estructura de tests presente, ejecución no evidenciada. Sin cambios vs v1 en este punto: re-ejecución pytest pendiente para certificar.
