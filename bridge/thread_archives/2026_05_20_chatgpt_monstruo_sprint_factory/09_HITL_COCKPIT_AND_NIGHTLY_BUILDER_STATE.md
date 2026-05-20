# 09 HITL COCKPIT AND NIGHTLY BUILDER STATE

**Estado:** EVIDENCE
**Fuente:** chat_context, assistant_synthesis

## HITL Cockpit
- **Estado Actual:** v0.3 implementado.
- **Ubicación:** Pushed en branch `supervised/SPR-HITL-COCKPIT-001-hitl-cockpit-mvp` (Commit `916e64a`).
- **Naturaleza:** Es un demo read-only local. **No** se debe asumir como un control plane productivo ni funcional para operaciones POST.

## Nightly Builder
- **R0 (Shadow Run):** Funcional y ejecutado (Night 0). Produjo 4 carriles de auditoría.
- **R1 (Patch Execution):** Actualmente bloqueado. Requiere firma explícita T1 para proceder.
- **Auditoría:** `anonymous` actúa como blocker preventivo ("insufficient evidence") según el auditor.
- **Especificaciones:**
  - `OPP-NB-021`: Contract spec.
  - `OPP-NB-023`: Drift report.
