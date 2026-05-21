# EPOCH 003 DECLARATION

**Effective Date:** 2026-05-21T00:55:00Z
**Authorization:** T1 (SPR-EPOCH003-PRODUCTION-ACCELERATOR-001)

## Declaracion
Se declara el inicio de la Epoch 003 del piloto `LIMITED_ACTIVE_R0`. 
Este es un LIVE PRODUCTIVE UPGRADE CONTROLADO. El piloto se mantiene vivo (`kill-switch: false`) mientras se actualizan sus capacidades.

## Capacidades Activas
1. **Dispatcher Hardened:** Validacion de invariantes y limites por proveedor.
2. **State Fabric v0.2:** Logging estructurado con single-writer contract.
3. **Provider Registry Guard v1.0:** Bloqueo estricto de modelos deprecados y providers no autorizados.
4. **Oracle v0.3:** Generacion de Sprints tecnicos con scoring (CANDIDATE_ONLY).
5. **Cockpit UI:** Generacion de fixtures para monitoreo local read-only.

## Restricciones Mantenidas
- NO_R1
- NO_SUPABASE_WRITES
- NO_MEMORY_WRITES
- NO_APP_VISION_MOD
- NO_PR_DEPLOY_MAIN
- Perplexity = BLOCKED_403
- DeepSeek = KEY_REQUIRED

El cron se mantiene en 2 ejecuciones por dia (06:23 y 18:23 UTC).
El presupuesto se mantiene en $0.05 USD / dia max.
