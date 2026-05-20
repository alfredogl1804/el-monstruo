# Contrato del Loop Auditor

**SPRINT:** SPR-LOOP-AUDITOR-001
**Estado:** DOCTRINE_CANDIDATE

Este documento define el contrato operativo del Loop Auditor frente al Dispatcher y el State Fabric.

## Identidad del Loop
- **loop_id:** `loop_auditor`
- **role:** Validate work from other loops (específicamente `loop_oraculo_ias`)
- **owner:** `monstruo`
- **maturity_level:** `M1` (Catalogado / Validado en Simulación)

## Permisos y Restricciones (Policy Engine Binding)
- **max_autonomy_level:** `A3` (Puede proponer deltas de estado en forma de reportes, pero no ejecutar código ni tocar bases de datos).
- **allowed_read_paths:**
  - `bridge/doctrine_candidates/` (Para leer los outputs del Oráculo).
  - `bridge/reactor_vigilia_foundation/state_fabric/` (Para leer el `event_log`).
- **allowed_write_paths:**
  - `bridge/doctrine_candidates/audit_reports/` (Para escribir sus resultados).
- **allowed_event_types:**
  - `OBSERVED`
  - `AUDIT_COMPLETED`
- **forbidden_actions:**
  - `write_code` (Requiere A5)
  - `touch_supabase` (Requiere A7)
  - `modify_kernel` (Requiere A8)
  - `deploy` (Requiere A6)

## Flujo de Ejecución Esperado
1. El Dispatcher asigna el turno al `loop_auditor`.
2. El Auditor lee `oraculo_capability_catalog_v0.json` y `oraculo_power_stacks_v0.md`.
3. El Auditor ejecuta los 8 Criterios de Auditoría.
4. El Auditor solicita permiso al Dispatcher para escribir los artefactos de auditoría (acción: `create_state_fabric_draft`).
5. Si es permitido, el Auditor escribe los archivos en `bridge/doctrine_candidates/audit_reports/`.
6. El Auditor solicita permiso para registrar el evento `AUDIT_COMPLETED` en el State Fabric.
7. El Auditor finaliza su ciclo.
