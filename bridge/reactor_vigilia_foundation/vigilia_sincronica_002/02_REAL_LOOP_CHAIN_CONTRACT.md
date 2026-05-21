# Contrato de la Cadena de Ejecución (Real Loop Chain)

**SPRINT:** SPR-VIGILIA-SINCRONICA-002
**Estado:** DOCTRINE_CANDIDATE

## 1. Definición de la Cadena

Una "Cadena de Ejecución" (Loop Chain) es una secuencia determinística de invocaciones a loops finitos. A diferencia de un enjambre (swarm) o una malla libre (mesh), la cadena impone un orden estricto donde el output de un loop se convierte en el contexto del siguiente mediante un paquete de relevo (Handoff Packet).

## 2. Reglas Estructurales

1. **Sin invocación directa:** Ningún loop puede instanciar o invocar directamente a otro loop.
2. **Mediación del Orquestador:** Un script orquestador (`run_vigilia_chain_v0.py`) actúa como el "Rotor". Instancia un loop, espera su finalización, recolecta su output, prepara el Handoff Packet y se lo entrega al siguiente loop.
3. **Mediación del Dispatcher:** Cada loop, al ejecutar su lógica, debe solicitar permiso al `MinimalDispatcher` antes de proponer cualquier cambio de estado o escribir un artefacto.
4. **Estado Inmutable (Append-Only):** Los loops no modifican los artefactos de los loops anteriores. El State Fabric (Event Log) solo recibe eventos nuevos (append-only).

## 3. Secuencia de la Cadena V0.2

La cadena definida para este sprint consta de 4 etapas principales y 3 transiciones (handoffs):

| Etapa | Componente | Acción Principal | Output Principal |
|-------|------------|------------------|------------------|
| **Step 1** | `loop_oraculo_ias` | Lee catálogo estático, propone capacidades. | `oraculo_capability_catalog_v0.json` |
| **Handoff 1** | Orquestador | Empaqueta contexto para el Auditor. | `handoff_oracle_to_auditor.v0_1.json` |
| **Step 2** | `loop_auditor` | Valida outputs del Oráculo (10 gates). | `audit_findings.json`, `auditor_gate_log.json` |
| **Handoff 2** | Orquestador | Empaqueta contexto para Risk. | `handoff_auditor_to_risk.v0_1.json` |
| **Step 3** | `risk_classification` | Aplica overlay de riesgo R0/A1. | `capability_risk_overlay.v0_1.json` |
| **Handoff 3** | Orquestador | Empaqueta contexto para Unified Face. | `handoff_risk_to_unified_face.v0_1.json` |
| **Step 4** | `loop_unified_face` | Sintetiza el resultado para T1. | `unified_face_summary.v0_1.md` |

## 4. Contrato de Estado (State Fabric)

Durante la ejecución de la cadena, el Orquestador mantiene un `chain_event_log_delta.v0_1.jsonl` en memoria o en un archivo temporal de la cadena.

- Cada loop emite eventos (ej. `STATE_DELTA_PROPOSED`, `BLOCKER_DECLARED`).
- El Dispatcher autoriza y registra estos eventos en el delta.
- Al finalizar un loop exitosamente, el Orquestador inyecta un evento de finalización de etapa (ej. `ORACLE_CHAIN_STEP_COMPLETED`, `HANDOFF_READY`).

## 5. Criterios de Falla (Abort)

La cadena se aborta inmediatamente si:
1. El Dispatcher deniega una acción crítica de un loop.
2. Un loop lanza una excepción no controlada.
3. Un loop intenta modificar un artefacto previo destructivamente.
4. Se detecta una violación de las reglas de riesgo (ej. intento de conexión a API real).
