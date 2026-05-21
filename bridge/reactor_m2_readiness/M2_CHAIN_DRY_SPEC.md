# M2 Chain Dry Spec

Este documento define la cadena propuesta para la transición hacia M2 Readiness. **Esta es una especificación en seco (dry spec) y NO implica ejecución activa hasta la autorización explícita de T1.**

## Flujo de la Cadena Propuesta

1. **Heartbeat R0:** El latido inicial que verifica el estado del sistema, constraints y el kill-switch.
2. **Dispatcher:** Enruta el evento si el Heartbeat lo autoriza y el Policy Engine lo permite.
3. **preflight_check():** Validación estricta de constraints antes de invocar a cualquier proveedor externo.
4. **State Fabric event:** Registro del inicio de la cadena en `event_log.v0.jsonl`.
5. **Oráculo shadow / report-only:** Ejecución del Oráculo de IAs en modo sombra (sin side effects, solo generación de reportes).
6. **Auditor:** El loop auditor revisa las salidas del Oráculo contra los 15 Objetivos Maestros y constraints.
7. **T1 Decision:** La cadena se detiene y requiere una decisión de T1 para cualquier acción subsecuente (writes, R1+, etc.).

## Distinción de Modos de Ejecución

Es imperativo distinguir entre los diferentes modos en los que esta cadena puede operar, dependiendo de la decisión A1 del `T1_DECISION_PACK`:

- **Dry Spec:** La definición actual. No hay código ejecutándose automáticamente.
- **One-shot Probe:** Ejecución manual de 1 ciclo completo de la cadena (Heartbeat → Auditor) con el kill-switch temporalmente en `false`, retornando a `true` inmediatamente después.
- **Limited Active:** El scheduler cron (12h) está activo, pero la cadena está topada a R0 local (sin llamadas a APIs externas) o a un Oráculo shadow con presupuesto estrictamente limitado.
- **Permanent Scheduler:** El scheduler cron (12h) está activo y la cadena M2 completa se ejecuta autónomamente, sujeta a los límites de budget y provider readiness autorizados.
