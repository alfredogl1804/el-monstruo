# Loop Auditor — Índice de Documentación

**SPRINT:** SPR-LOOP-AUDITOR-001
**Estado:** DOCTRINE_CANDIDATE

Este directorio contiene la doctrina, contratos y schemas para el **Loop Auditor**, el segundo loop real del Monstruo, diseñado para validar los outputs del Oráculo de IAs bajo el principio *Proposer ≠ Evaluator*.

## Documentación
- `01_LOOP_AUDITOR_VISION.md`: Visión y principios (Proposer ≠ Evaluator).
- `02_AUDIT_CONTRACT.md`: Contrato de ejecución y límites de autonomía.
- `03_ORACLE_OUTPUT_AUDIT_CRITERIA.md`: Los 8 criterios obligatorios de auditoría.
- `04_F16_ANTI_SELF_AUDIT_RULES.md`: Reglas contra la auto-auditoría y validación de linaje.
- `05_AUDITOR_POLICY_BINDING_A0_A8.md`: Mapeo del Auditor a la Escalera de Autonomía.
- `06_E2E_SIMULATION_REPORT.md`: Reporte de la simulación end-to-end.
- `07_RESTORE_TEST.md`: 15 preguntas para validar la comprensión del modelo.

## Schemas
- `loop_auditor_contract.yaml`: Contrato técnico para el Dispatcher.
- `oracle_audit_result.schema.json`: Schema del resultado final.
- `oracle_audit_findings.schema.json`: Schema de los hallazgos estructurados.
- `auditor_gate_log.schema.json`: Schema del registro de validación por compuertas.
