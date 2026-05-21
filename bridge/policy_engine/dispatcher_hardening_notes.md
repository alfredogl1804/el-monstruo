# Dispatcher & State Fabric Hardening Notes

**Sprint:** SPR-ACCELERATOR-WHILE-LIMITED-R0-RUNS-001
**Status:** DRAFT (Hardening in progress)

## 1. Problema Actual
Vigilia Sincrónica depende de un `event_log` y un `dispatcher` para coordinar múltiples actores (Oráculo, Auditor, etc.). Sin embargo, la estructura actual carece de invariantes duros que prevengan que un actor escriba directamente en el estado o que el dispatcher apruebe acciones prohibidas (como R1) por alucinación.

## 2. Invariantes Duros a Implementar
1. **Single-Writer Principle:** Nadie puede mutar el `current_state` directamente. Todo debe pasar por el `event_log` append-only.
2. **Event Monotonicity:** Cada evento debe tener un `event_id` secuencial estricto.
3. **Hard-Coded Denials (No-Go):** El dispatcher debe rechazar inmediatamente (sin llamar al LLM) cualquier solicitud de:
   - R1 (shell, code execution)
   - Escritura en memoria persistente o Supabase
   - Modificación de APP_VISION o canon
   - Modificación de la política del piloto en curso
4. **No Self-Approval:** El dispatcher no puede aprobar sus propias acciones.
5. **Lineage Validation:** El Auditor no puede auditar su propio output.

## 3. Plan de Pruebas
Se crearán tests unitarios (`test_dispatcher_hardening.py` y `test_event_log_contract.py`) para asegurar que estas reglas se cumplen a nivel de código (Python), independientemente de lo que decida el LLM.
