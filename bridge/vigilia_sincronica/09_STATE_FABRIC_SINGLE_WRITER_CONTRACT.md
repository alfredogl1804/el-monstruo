# Vigilia Sincrónica: State Fabric Single-Writer Contract

**Status:** DRAFT (Hardening)
**Sprint:** SPR-ACCELERATOR-WHILE-LIMITED-R0-RUNS-001

Este documento formaliza el contrato "Single-Writer" para Vigilia Sincrónica.

## 1. El Problema de la Mutación Distribuida
En una arquitectura multi-agente, si cada agente (Oráculo, Auditor, Dispatcher) puede mutar el estado global directamente, se producen condiciones de carrera, alucinaciones de estado y pérdida de auditabilidad.

## 2. La Solución: Event Sourcing + Single Reducer
1. **Event Sourcing:** El estado no se actualiza; se añaden eventos a un log inmutable (`event_log`).
2. **Single Reducer:** Un único componente determinista (el State Fabric Core) lee el `event_log` y reconstruye el `current_state` en memoria.

## 3. Reglas para Vigilia Sincrónica
- **Oráculo:** Genera propuestas de eventos (payloads). No escribe en el log.
- **Auditor:** Revisa las propuestas. No escribe en el log.
- **Dispatcher:** Si la propuesta pasa las reglas duras (no R1, no DB writes) y la auditoría, el Dispatcher firma la propuesta y la emite al `event_log`.
- **State Fabric Core:** Detecta el nuevo evento firmado, aplica la función reductora y actualiza el `current_state` expuesto a los agentes.

Este contrato garantiza que ninguna alucinación de un LLM pueda corromper el estado persistente sin dejar un rastro criptográfico (firma del Dispatcher) en el log de eventos.
