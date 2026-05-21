# DECISION TABLE: Heartbeat R0

Durante el paso 2 (Evaluate), el latido evalúa el estado y selecciona exactamente **UNA** decisión permitida.

## Decisiones Permitidas

| Decisión | Significado |
|----------|-------------|
| `BLOCKED` | Hay un blocker P0 o faltan inputs críticos. El latido aborta. |
| `REQUEST_T1` | Se requiere intervención de Alfredo (T1) antes de proceder. |
| `NO_ACTION` | El estado es seguro, pero no hay nueva señal o trabajo R0 pendiente. |
| `RUN_AUDIT_ONLY_R0` | Ejecutar solo el loop auditor sobre artefactos existentes. |
| `RUN_ORACLE_CHAIN_R0` | Ejecutar la cadena Vigilia Sincrónica R0 completa (Oráculo local -> Auditor -> Risk -> Face). |

## Lógica de Selección (Cascada)

El latido evalúa las siguientes reglas en orden. La primera que aplique determina la decisión:

1. **P0 Blocker Check:**
   - *Si* existe un blocker P0 documentado en el State Fabric, *o* si Post-M2 Reclassification no tiene un reporte PASS:
   - *Entonces* decision = `BLOCKED`.

2. **T1 Pending Check:**
   - *Si* hay decisiones T1 pendientes (ej. en `post_m2_t1_decision_pack.v0_1.json`):
   - *Entonces* decision = `REQUEST_T1`.

3. **API Requirement Check:**
   - *Si* el trabajo pendiente requiere llamar APIs reales nuevas (M2 o superior):
   - *Entonces* decision = `REQUEST_T1`.

4. **Safe Work Check:**
   - *Si* existe una cadena R0 local segura ya aprobada (ej. Vigilia 002) y no se ha ejecutado recientemente:
   - *Entonces* decision = `RUN_ORACLE_CHAIN_R0` (o `RUN_AUDIT_ONLY_R0` si solo requiere auditoría).

5. **Default Fallback:**
   - *Si* todo está limpio pero no hay trabajo pendiente ni señal nueva:
   - *Entonces* decision = `NO_ACTION`.
