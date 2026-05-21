# ROLLBACK / FREEZE POLICY (Epoch 002)

**Timestamp:** 2026-05-20TXX:XX:XXZ
**Sprint:** SPR-LIVE-UPGRADE-LIMITED-R0-EPOCH-002

## 1. Freeze Triggers (Automáticos)
El piloto en Epoch 002 debe abortar y auto-congelarse (kill-switch `active: true`) inmediatamente si ocurre cualquiera de los siguientes eventos:
- Costo de un solo ciclo excede `$0.03`.
- Se detecta una llamada a un proveedor NO autorizado (ej. Perplexity o DeepSeek antes del unblock explícito).
- Intento de ejecución de código o shell (R1 violation).
- Intento de escritura en Supabase o archivos de memoria persistente (Memento/Anti-Dory).
- Exposición de un secreto (API Key) en un log o output público.
- Modificación de los archivos canon (`APP_VISION`, `PRE-IA`, etc.).
- El Auditor reporta un `FAIL` en cualquier check de invariantes.
- El Oráculo v0.2 produce una alucinación severa o output destructivo que escape los guardrails.

## 2. Procedimiento de Rollback (Manual por T1)
Si el piloto se congela, T1 puede ordenar un rollback a Epoch 1 ejecutando:
1. `git checkout 4e0745e bridge/reactor_limited_active_r0/LIMITED_ACTIVE_R0_POLICY.json`
2. Desactivar el runner de Epoch 002.
3. Reactivar el kill-switch (`active: false`) si se desea continuar el piloto en Epoch 1.

## 3. Estado Actual
- **Freeze Status:** NO ACTIVADO.
- El ciclo inmediato de Epoch 002 pasó todas las validaciones.
- La recomendación es **MANTENER EPOCH 2 ACTIVA** hasta el final natural de la ventana del piloto (48h).
