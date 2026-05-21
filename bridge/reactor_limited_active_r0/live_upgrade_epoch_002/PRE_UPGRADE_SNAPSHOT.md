# PRE-UPGRADE SNAPSHOT: LIMITED_ACTIVE_R0 (Epoch 1)

**Timestamp:** 2026-05-20TXX:XX:XXZ
**Sprint:** SPR-LIVE-UPGRADE-LIMITED-R0-EPOCH-002

## 1. Estado Base (Epoch 1)
- **Commit Actual:** `4e0745e` (Accelerator completado)
- **Kill-Switch:** `active: false` (Piloto vivo)
- **Scheduler State:** `ACTIVE` (Esperando cron 06:23 UTC)
- **Cycle Count:** 1 completado
- **Total Cost:** $0.007233 USD
- **Provider Usage:** OpenAI, Anthropic, Google, xAI (Todos SUCCESS)
- **Last Event ID:** 3 (en el log de activación)

## 2. Configuración Actual
- **Current Policy:** `LIMITED_ACTIVE_R0_POLICY.json` (Epoch 1)
- **Allowed Chain:** Heartbeat → Dispatcher → Oráculo shadow → Auditor → T1 report
- **Oráculo:** Usa fixture estático `oracle_shadow_fixture.json` o hardcoded fallback.
- **Dispatcher:** Básico (sin validación dura de invariantes Python).
- **Event Log:** Básico (sin contrato `event_log_contract.v0_2.json`).

## 3. Blockers y Decisiones T1 Pendientes
- **Blockers:** Perplexity (403), DeepSeek (Key Required).
- **T1 Decisions:** Pack 003 pendiente de autorización explícita (D1, D2, D3, D4).

*Nota: Este snapshot congela el estado lógico del piloto antes de aplicar el upgrade a Epoch 2.*
