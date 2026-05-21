# Índice — Oracle Risk Classification

**SPRINT:** SPR-RISK-CLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

Este directorio contiene el contrato de clasificación de riesgo para las capacidades, power stacks y sprint candidates propuestos por el Oráculo de IAs. Su objetivo es cerrar el gap detectado por el Loop Auditor (FND-031) y establecer los cimientos de gobernanza antes de escalar a Vigilia Sincrónica real o conectar APIs externas (M2).

## Documentación
- `01_RISK_CLASSIFICATION_VISION.md` — Visión y principio rector: "Antes de aumentar potencia, aumentar clasificación".
- `02_CAPABILITY_RISK_RUBRIC.md` — Rúbrica para clasificar el riesgo individual de una capacidad (R0-R5).
- `03_POWER_STACK_RISK_DERIVATION.md` — Reglas para derivar el riesgo de un Power Stack completo.
- `04_SPRINT_CANDIDATE_RISK_RULES.md` — Reglas para derivar el nivel de autonomía requerido (A0-A8) de un Sprint Candidate.
- `05_EVIDENCE_STATUS_RULES.md` — Reglas estrictas sobre la afirmación de verificación en tiempo real.
- `06_AUDITOR_RECHECK_REPORT.md` — Reporte de revalidación del Auditor tras aplicar el overlay de riesgo.
- `07_EXTERNAL_RESTORE_TEST_EXECUTION.md` — Registro de la ejecución del Restore Test contra un modelo externo.
- `08_E2E_SIMULATION_REPORT.md` — Reporte de la simulación End-to-End del proceso de clasificación.
- `09_RESTORE_TEST.md` — Test de 15 preguntas para validar la comprensión de este sprint.

## Schemas
- `capability_risk.schema.json`
- `power_stack_risk.schema.json`
- `sprint_candidate_risk.schema.json`
- `risk_classification_overlay.schema.json`

## Artifacts (Overlays v0.1)
- `capability_risk_overlay.v0_1.json`
- `power_stack_risk_overlay.v0_1.json`
- `sprint_candidate_risk_overlay.v0_1.json`
- `oracle_catalog_risk_annotated.v0_1.json`
- `auditor_recheck_gate_log.json`
