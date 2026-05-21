# LIVE UPGRADE DIFF REPORT (Epoch 1 → Epoch 2)

**Timestamp:** 2026-05-20TXX:XX:XXZ
**Sprint:** SPR-LIVE-UPGRADE-LIMITED-R0-EPOCH-002

## 1. Archivos Modificados

| Archivo | Cambio | Por qué | Riesgo | Rollback |
|---------|--------|---------|--------|----------|
| `bridge/reactor_limited_active_r0/run_cycle.py` | Se actualiza para usar `Dispatcher Hardened`, `Oracle v0.2` (con schemas YAML y llamadas a LLM), y `State Fabric Log v0.2`. | Habilitar las capacidades desarrolladas en el Accelerator. | **Medio**. Podría fallar si los schemas YAML no son parseables o si el LLM devuelve JSON inválido. | Revertir al script de Epoch 1 (`git checkout 4e0745e bridge/reactor_limited_active_r0/run_cycle.py`). |
| `bridge/reactor_limited_active_r0/LIMITED_ACTIVE_R0_POLICY.json` | Actualizado a Epoch 2. Se añaden `Dispatcher_Hardened`, `Oracle_v0_2`, `Auditor_Extended`, `State_Fabric_Log` a la chain. | Reflejar la nueva política declarada. | **Bajo**. Solo configuración. | Revertir al JSON de Epoch 1. |

## 2. Efecto Esperado
- El ciclo dejará de usar el fixture estático y usará llamadas reales a los 4 proveedores para generar ideas de aplicación (Oráculo v0.2).
- El Dispatcher validará los invariantes (No R1, No Supabase) localmente en Python antes de continuar.
- El log de eventos tendrá el formato estructurado v0.2.

## 3. Restricciones Mantenidas
- No se modificó el cron del host.
- No se modificó el `kill-switch` (sigue en `active: false` según Epoch 1).
- No se tocaron archivos fuera del scope del piloto.
