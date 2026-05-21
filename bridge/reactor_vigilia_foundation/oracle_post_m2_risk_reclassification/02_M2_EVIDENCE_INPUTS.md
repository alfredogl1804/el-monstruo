# Inputs de Evidencia M2

**SPRINT:** SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

Este documento registra los artefactos inmutables de sprints anteriores que actúan como fuente de verdad (inputs) para la reclasificación de riesgo.

## 1. Artefactos del Sprint M2 (`SPR-ORACLE-AI-M2-001`)
Ruta base: `bridge/reactor_vigilia_foundation/oracle_ai_m2/`

| Artefacto | Propósito en Reclasificación |
|-----------|------------------------------|
| `provider_access_status.v0_1.json` | Determina qué proveedores están vivos (`REALTIME_VERIFIED`) y cuáles bloqueados (`ACCESS_BLOCKED_*`). |
| `realtime_capability_catalog.v0_1.json` | Lista granular de todas las capacidades detectadas en tiempo real. |
| `oracle_catalog_m2_realtime_overlay.v0_1.json` | Mapeo de las capacidades estáticas (M1) a su estado empírico (M2). |
| `api_probe_log.redacted.v0_1.jsonl` | Evidencia de las llamadas de solo lectura realizadas. |
| `api_cost_ledger.v0_1.json` | Evidencia del costo incurrido, vital para determinar riesgo financiero. |
| `oracle_m2_validation_report.v0_1.json` | Garantiza que los inputs M2 son válidos y no contienen secretos. |
| `reclassification_inputs_for_next_sprint.v0_1.json` | Recomendaciones base de elevación generadas por M2. |

## 2. Artefactos del Sprint de Clasificación Estática (`SPR-RISK-CLASSIFICATION-001`)
Ruta base: `bridge/reactor_vigilia_foundation/oracle_risk_classification/`

| Artefacto | Propósito en Reclasificación |
|-----------|------------------------------|
| `capability_risk_overlay.v0_1.json` | Baseline de riesgo (todos en R0). |
| `power_stack_risk_overlay.v0_1.json` | Baseline de riesgo para stacks compuestos. |
| `sprint_candidate_risk_overlay.v0_1.json` | Baseline de riesgo para los sprints propuestos. |

## 3. Artefactos de Auditoría y Cadena
Rutas base: `bridge/reactor_vigilia_foundation/loop_auditor/` y `bridge/reactor_vigilia_foundation/vigilia_sincronica_002/chain_run_001/`

| Artefacto | Propósito en Reclasificación |
|-----------|------------------------------|
| `oracle_audit_result.schema.json` | Formato esperado para validaciones del auditor. |
| `chain_validation_report.v0_1.json` | Evidencia de que la cadena M1 operó correctamente antes de M2. |

## Validación de Integridad
El script `run_post_m2_reclassification.py` verificará la existencia y legibilidad de todos estos artefactos antes de comenzar. Si alguno falta o está corrupto, el proceso se detendrá con un error `BLOCKED_BY_MISSING_ARTIFACT`.
