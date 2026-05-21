# Auditor Policy Binding (A0-A8)

**SPRINT:** SPR-LOOP-AUDITOR-001
**Estado:** DOCTRINE_CANDIDATE

Este documento mapea las capacidades del Loop Auditor a la Escalera de Autonomía (A0-A8).

## Nivel de Autonomía Máximo: A3

El Loop Auditor opera bajo el nivel de autonomía **A3** (Proponer deltas de estado persistentes, no ejecutables).

### Acciones Permitidas (A0-A3)
- **A0 (Observar):** Leer archivos en `bridge/doctrine_candidates/` y `bridge/reactor_vigilia_foundation/state_fabric/`.
- **A2 (Reportar):** Generar el `audit_report.md` y `e2e_simulation_report.md`.
- **A3 (Proponer Delta):** Escribir `audit_findings.json`, `auditor_gate_log.json`, y registrar el evento `AUDIT_COMPLETED` en el State Fabric (previa autorización del Dispatcher).

### Acciones Prohibidas (A4+)
- **A4 (Modificar Configuración):** No puede alterar la configuración del Oráculo ni de otros loops.
- **A5 (Escribir Código):** No puede modificar el código fuente del Oráculo ni de sí mismo.
- **A6 (Desplegar):** No puede desplegar servicios ni ejecutar simulaciones en entornos remotos.
- **A7 (Tocar Supabase):** No tiene acceso a la base de datos real.
- **A8 (Modificar Kernel):** No puede alterar el Policy Engine, el Dispatcher ni las reglas fundamentales del sistema.
