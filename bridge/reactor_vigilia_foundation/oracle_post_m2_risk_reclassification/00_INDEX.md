# Índice: Reclasificación de Riesgo Post-M2

**SPRINT:** SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE
**Directorio:** `bridge/reactor_vigilia_foundation/oracle_post_m2_risk_reclassification/`

Este directorio contiene la reclasificación de riesgo de las capacidades del Oráculo, basándose en la evidencia empírica recolectada en el sprint M2 (`SPR-ORACLE-AI-M2-001`).

## Documentación
- `01_POST_M2_RISK_RECLASSIFICATION_VISION.md`: Visión y principio operativo (Verificar -> Reclasificar -> Automatizar).
- `02_M2_EVIDENCE_INPUTS.md`: Registro de los artefactos de entrada utilizados.
- `03_RISK_RECLASSIFICATION_RULES.md`: Reglas estrictas para elevar el riesgo (R0 a R1-R4).
- `04_PROVIDER_CORE_OPTIONAL_MATRIX.md`: Criterios para proponer la matriz Core vs Opcional.
- `05_CAPABILITY_RECLASSIFICATION_REPORT.md`: Reporte de reclasificación de capacidades individuales.
- `06_POWER_STACK_RECLASSIFICATION_REPORT.md`: Reporte de reclasificación de Power Stacks.
- `07_SPRINT_CANDIDATE_RECLASSIFICATION_REPORT.md`: Reporte de reclasificación de Sprint Candidates.
- `08_AUDITOR_RECHECK_REPORT.md`: Resultados de los 14 gates de validación.
- `09_T1_DECISION_PACK.md`: Paquete formal de decisiones pendientes para T1.
- `10_RESTORE_TEST.md`: 20 preguntas para validar la comprensión de una IA futura.
- `11_NEXT_DECISIONS_T1.md`: Resumen ejecutivo de decisiones T1.

## Schemas JSON
- `post_m2_capability_risk.schema.json`
- `post_m2_provider_risk.schema.json`
- `post_m2_power_stack_risk.schema.json`
- `post_m2_sprint_candidate_risk.schema.json`
- `post_m2_reclassification_manifest.schema.json`
- `post_m2_auditor_recheck.schema.json`
- `provider_core_optional.schema.json`
- `post_m2_t1_decision_pack.schema.json`

## Artefactos Generados
- `post_m2_reclassification_manifest.v0_1.json`
- `post_m2_capability_risk_overlay.v0_1.json`
- `post_m2_provider_risk_matrix.v0_1.json`
- `post_m2_power_stack_risk_overlay.v0_1.json`
- `post_m2_sprint_candidate_risk_overlay.v0_1.json`
- `provider_core_optional_matrix.v0_1.json`
- `post_m2_auditor_recheck_gate_log.v0_1.json`
- `post_m2_t1_decision_pack.v0_1.json`
- `unified_face_summary_post_m2_reclassification.v0_1.md`

## Scripts
- `scripts/run_post_m2_reclassification.py`: Orquestador de la reclasificación.
- `scripts/validate_post_m2_reclassification.py`: 14 gates de validación.
