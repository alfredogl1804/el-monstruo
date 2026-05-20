# Índice — SPR-VIGILIA-SINCRONICA-002

**SPRINT:** SPR-VIGILIA-SINCRONICA-002
**Estado:** DOCTRINE_CANDIDATE

## 1. Documentación Core
- `01_VIGILIA_SINCRONICA_002_VISION.md` — Visión de la cadena local controlada.
- `02_REAL_LOOP_CHAIN_CONTRACT.md` — Contrato de la cadena de ejecución.
- `03_DISPATCHER_SEQUENCE_PROTOCOL.md` — Protocolo de secuencia del Dispatcher.
- `04_HANDOFF_PACKET_CONTRACT.md` — Contrato de los paquetes de relevo (Handoff).
- `05_UNIFIED_FACE_CONTRACT.md` — Contrato de la Unified Face.
- `06_E2E_CHAIN_SIMULATION_REPORT.md` — Reporte de la simulación E2E (10 steps, 12 gates).
- `07_RISK_CONTROLS.md` — Controles de riesgo para evitar runtime productivo.
- `08_RESTORE_TEST.md` — Test de 20 preguntas para validar comprensión.
- `09_NEXT_DECISIONS_T1.md` — Decisiones pendientes para T1.

## 2. Schemas JSON
- `real_loop_chain_manifest.schema.json`
- `handoff_packet.schema.json`
- `chain_step_result.schema.json`
- `unified_face_output.schema.json`
- `chain_validation_report.schema.json`

## 3. Artefactos Generados (v0.1)
- `real_loop_chain_manifest.v0_1.json`
- `handoff_oracle_to_auditor.v0_1.json`
- `handoff_auditor_to_risk.v0_1.json`
- `handoff_risk_to_unified_face.v0_1.json`
- `unified_face_summary.v0_1.md`
- `chain_event_log_delta.v0_1.jsonl`
- `chain_validation_report.v0_1.json`

## 4. Scripts (Simulación y Validación)
- `scripts/run_vigilia_chain_v0.py` — Orquestador de la cadena.
- `scripts/validate_vigilia_chain_v0.py` — Validador de los 12 gates.
