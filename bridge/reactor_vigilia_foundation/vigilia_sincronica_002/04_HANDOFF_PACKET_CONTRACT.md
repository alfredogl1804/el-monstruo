# Contrato de los Paquetes de Relevo (Handoff Packets)

**SPRINT:** SPR-VIGILIA-SINCRONICA-002
**Estado:** DOCTRINE_CANDIDATE

## 1. Propósito del Handoff Packet

El Handoff Packet es el único mecanismo de comunicación entre etapas de la cadena. Elimina la necesidad de que los loops se llamen entre sí (evitando mallas caóticas) y proporciona un contexto inmutable y auditable para el loop receptor.

## 2. Estructura Obligatoria

Todo Handoff Packet en esta cadena debe cumplir con el `handoff_packet.schema.json` y contener:

- `source_loop`: ID del loop que originó el contexto.
- `target_loop`: ID del loop que debe recibir el contexto.
- `artifact_refs`: Rutas a los archivos generados por el loop origen.
- `evidence_status`: Nivel de verificación de la evidencia (ej. `STATIC_CATALOG`).
- `forbidden_assumptions`: Lista explícita de asunciones que el loop receptor NO debe hacer (ej. "No asumir que las APIs están conectadas").
- `max_autonomy_level`: Nivel máximo permitido para el loop receptor.
- Banderas de control de riesgo:
  - `not_realtime_verified`: Booleano (true para esta cadena).
  - `no_m2_unlock`: Booleano (true para esta cadena).

## 3. Instancias de Handoff en la Cadena

### Handoff 1: Oráculo → Auditor
- **Objetivo:** Entregar el catálogo y el reporte al Auditor para su validación.
- **Artifact Refs:** `oraculo_capability_catalog_v0.json`, `oraculo_power_stacks_v0.md`.
- **Restricción Clave:** El Auditor debe saber que la evidencia es `STATIC_CATALOG`.

### Handoff 2: Auditor → Risk Classification
- **Objetivo:** Entregar el veredicto y los hallazgos a la etapa de riesgo.
- **Artifact Refs:** `audit_findings.json`, `auditor_gate_log.json`.
- **Restricción Clave:** `risk_classification_required: true`. No se permite mutar los outputs originales.

### Handoff 3: Risk Classification → Unified Face
- **Objetivo:** Entregar el resumen de riesgo y el estado de la cadena a la interfaz unificada.
- **Artifact Refs:** `capability_risk_overlay.v0_1.json`, etc.
- **Restricción Clave:** Indicar explícitamente los `pending_t1_decisions` y las opciones válidas a continuación.

## 4. Inmutabilidad

Los Handoff Packets se escriben en disco (o se mantienen en memoria del orquestador) y son de solo lectura para el loop receptor. Un loop receptor no puede modificar el Handoff Packet que recibió. Si necesita pasar información al siguiente loop, debe generar sus propios artefactos, y el Orquestador creará un nuevo Handoff Packet.
