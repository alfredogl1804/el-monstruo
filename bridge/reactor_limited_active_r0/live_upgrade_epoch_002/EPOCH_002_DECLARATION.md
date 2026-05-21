# EPOCH 002 DECLARATION: Live Upgrade Controlado

**Timestamp:** 2026-05-20TXX:XX:XXZ
**Sprint:** SPR-LIVE-UPGRADE-LIMITED-R0-EPOCH-002

## 1. Definición de Epochs
- **Epoch 1:** Baseline original. Cadena M2 básica (Heartbeat → Dispatcher simple → Oráculo estático → Auditor → T1 Report).
- **Epoch 2:** Live Upgrade Controlado. Integra los resultados del Accelerator sin detener el piloto.

## 2. Cambios Permitidos (El Upgrade)
Para esta nueva epoch, el piloto `LIMITED_ACTIVE_R0` adoptará:
1. **Oráculo AI v0.2:** El Oráculo pasa de usar un fixture estático a realizar llamadas reales a los LLMs para generar y rankear Application Candidates, usando los schemas `v0_2`.
2. **Dispatcher Hardening:** El Dispatcher ahora aplicará las reglas duras (No R1, No DB writes, No Self-Approval) mediante código Python estricto antes de consultar al LLM.
3. **State Fabric Event Log:** El log de eventos usará el contrato endurecido `event_log_contract.v0_2.json` (Single-Writer, Monotonic ID, Dispatcher Signature).
4. **Auditor Compliance Ampliado:** El Auditor verificará el cumplimiento de los nuevos invariantes del State Fabric.

## 3. Cambios Estrictamente Prohibidos (Invariantes de Seguridad)
El upgrade a Epoch 2 **MANTIENE TODAS LAS REGLAS DURAS DEL PILOTO**:
- NO R1 (ejecución de código o shell real).
- NO escrituras en memoria (Memento/Anti-Dory) ni Supabase.
- NO modificaciones a APP_VISION, canon o PRE-IA.
- NO creación de PRs, deploys o modificaciones a `main`.
- NO extender el scheduler de forma permanente fuera de la ventana del piloto de 48h.
- NO usar Perplexity (403) ni DeepSeek (hasta unblock).
- NO ejecutar SHELL No-Hint runtime (solo lectura/reporting).

Cualquier violación a estas reglas durante la ejecución del ciclo inmediato provocará un **FREEZE AUTOMÁTICO** (kill-switch `active: true`).
