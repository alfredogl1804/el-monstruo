# LIVE UPGRADE DIFF REPORT (Epoch 002 -> Epoch 003)

**Sprint:** SPR-EPOCH003-PRODUCTION-ACCELERATOR-001 — Carril D

## Cambios en la Politica (`EPOCH_003_POLICY.json`)
1. **Epoch:** `2` -> `3`.
2. **Chain Components:**
   - Se agrega `Provider Registry Guard v1.0`.
   - `Oracle AI v0.2 Shadow` cambia a `Oracle AI v0.3 Productive Shadow`.
   - Se agrega `Cockpit Fixture Generation`.
3. **Hard Rules:**
   - Se agregan `NO_PROVIDER_AUTO_REPLACE`, `NO_PERPLEXITY`, `NO_DEEPSEEK`.
4. **Freeze Triggers:**
   - Se agregan `unauthorized_provider` y `oracle_severe_hallucination`.

## Cambios Arquitectonicos
1. **Provider Ops:** Se implemento un modulo Python `provider_registry.py` que centraliza la validacion de proveedores, modelos y politicas de reemplazo. Esto previene el drift de modelos de forma deterministica.
2. **Oraculo AI:** El prompt y esquema del Oraculo se actualizaron a v0.3. Ahora genera `sprint_candidates` accionables con scoring, dependencias y riesgos, en lugar de solo ideas abstractas.
3. **Cockpit UI:** Se creo una interfaz HTML estatica y read-only para que T1 pueda visualizar el estado del reactor sin interactuar con produccion.

## Impacto en el Ciclo Inmediato
El script de ejecucion del ciclo de Epoch 003 debera:
1. Validar los proveedores usando `provider_registry.py` antes de hacer llamadas.
2. Usar el nuevo prompt/esquema del Oraculo v0.3.
3. Generar un archivo `EPOCH_003_COCKPIT_FIXTURE.json` al final del ciclo para alimentar la UI.

El piloto se mantiene vivo (`kill-switch: false`) durante esta transicion.
