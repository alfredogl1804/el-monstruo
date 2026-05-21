# State Fabric Invariants

**Sprint:** SPR-ACCELERATOR-WHILE-LIMITED-R0-RUNS-001

## Single-Writer Contract
El State Fabric opera bajo el principio de "Single-Writer". Esto significa:
1. **Mutación Indirecta:** Ningún actor (Oráculo, Auditor, T1) puede mutar el `current_state` directamente.
2. **Event Log como Fuente de Verdad:** Todas las intenciones de cambio deben registrarse como un evento en el `event_log`.
3. **Reductor Determinista:** Solo una función reductora pura (el State Fabric Core) puede leer el `event_log` y calcular el nuevo `current_state`.

## Estructura del Evento
Cada evento debe cumplir con `event_log_contract.v0_2.json`:
- `event_id`: Monotónico incremental.
- `timestamp`: UTC ISO 8601.
- `actor`: Quien propone el cambio.
- `action`: La acción a realizar.
- `payload`: Datos de la acción.
- `dispatcher_signature`: Firma de aprobación del Dispatcher (requerida para que el reductor la procese).
